import VE.Bridge
import VE.WireContract.Table

/-! The wire contract engine (docs/spec/wire-contract.md 2 and 5.2).

`instances` expands a table over an input in the one order of spec 2.6: phases
in order, entries in order, the items of a group item-major, resolved includes
read against the value at their site or its view. `eval` decides one instance:
`none` when it holds, otherwise its finding (spec 2.4, 2.5, 2.7). `run` is the
finding of the first instance that does not hold. The theorems at the end say
that in Lean: a clean result means every instance holds, a finding is that of
an instance before which every instance holds, phases are whole-input, and the
result depends on the hooks only where they are reached.

The engine decides a diagnostic, never a verdict: no module on a verdict path
imports it (spec 7.3, checked by `tools/check_lean_imports.py`).
-/

namespace VE.WireContract
open Lean

inductive HookResult where
  | ok
  | fail (args : List (String × Json))

inductive ClassifierResult where
  | ok
  | fail (member : String) (args : List (String × Json))

/-- The hand-written predicates of a unit (2.5). Each receives the value its instance reads and the enclosing
    items, innermost first. For a name the unit does not define, `predicate` and `classifier` give `ok` and
    `view` gives the identity. -/
structure Hooks where
  predicate : String → Json → List Pointer → HookResult
  classifier : String → Json → List Pointer → ClassifierResult
  view : String → Json → Json

/-- How pointers under resolved includes map back to the submitted input (2.7). -/
structure Frame where
  ids : List String                    -- include ids, outermost first
  site : Pointer                       -- the sites of the enclosing includes without a view, concatenated
  viewSite : Option Pointer            -- the site of the enclosing include with a view
  recode : Option (String × String)    -- the outermost `as`

def Frame.top : Frame := ⟨[], [], none, none⟩

/-- The frame inside an include whose site is `p`: `ids` gains `id`; the outermost `recode` is kept; with a
    view and no view yet, `viewSite` becomes `site ++ p` and `site` restarts empty; otherwise `site` gains `p`. -/
def Frame.enter (f : Frame) (id : String) (p : Pointer) (view : Option String)
    (recode : Option (String × String)) : Frame :=
  let entersView := view.isSome && f.viewSite.isNone
  { ids := f.ids ++ [id]
    site := if entersView then [] else f.site ++ p
    viewSite := if entersView then some (f.site ++ p) else f.viewSite
    recode := f.recode.or recode }

structure Instance where
  phase : String
  check : Check
  root : Json                          -- the input, or the value under a scope
  items : List Pointer                 -- enclosing group items, innermost first
  earlier : List Pointer               -- the earlier items of the innermost group, in order
  frame : Frame

structure Finding where                -- a record (2.7) without `contract` and `revision`
  check : String
  phase : String
  code : String
  cls : String
  path : String
  text : String
  args : List (String × String)

/-! ## Values, pointers and patterns (2.1) -/

/-- An array index token: `0`, or digits without a leading zero. -/
def indexToken? (s : String) : Option Nat :=
  if s.isEmpty || !s.all Char.isDigit || (s.length > 1 && s.front == '0') then none
  else some (s.foldl (fun n c => n * 10 + (c.toNat - '0'.toNat)) 0)

/-- One pointer step from a value by a token. -/
def stepInto (v : Json) (s : String) : Option Json :=
  match v with
  | .obj _ => match v.getObjVal? s with
    | .ok w => some w
    | .error _ => none
  | .arr a => (indexToken? s).bind fun n => a[n]?
  | _ => none

/-- The members of an object in code point order of the keys, or the elements of an array with their indices. -/
def children (v : Json) : List (String × Json) :=
  match v with
  | .obj _ => match VE.Bridge.fields v with
    | .ok fs => fs
    | .error _ => []
  | .arr a => ((List.range a.size).zip a.toList).map fun (n, w) => (toString n, w)
  | _ => []

/-- The value at a pointer, or `none` when it is absent. -/
def resolvePointer (root : Json) (p : Pointer) : Option Json :=
  p.foldlM stepInto root

def start (root : Json) (items : List Pointer) : Base → Option (Pointer × Json)
  | .root => some ([], root)
  | .item n => items[n]?.bind fun p => (resolvePointer root p).map fun v => (p, v)

def walk : List Step → Pointer × Json → List (Pointer × Json)
  | [], x => [x]
  | .tok s :: rest, (p, v) => match stepInto v s with
    | some w => walk rest (p ++ [s], w)
    | none => []
  | .star :: rest, (p, v) => (children v).flatMap fun (s, w) => walk rest (p ++ [s], w)

/-- 2.1: every match of a pattern with its pointer, in order; an object's members in the order of
    `VE.Bridge.fields`. -/
def collect (root : Json) (items : List Pointer) (p : Pattern) : List (Pointer × Json) :=
  match start root items p.base with
  | some x => walk p.steps x
  | none => []

/-- 2.1: the one match of a pattern without `star`, or `none` when it is absent. -/
def resolve (root : Json) (items : List Pointer) (p : Pattern) : Option (Pointer × Json) :=
  (collect root items p).head?

/-- 2.1: the pointer formed from the base and the tokens, without looking at the value. -/
def concrete (items : List Pointer) (p : Pattern) : Pointer :=
  let base := match p.base with
    | .root => []
    | .item n => items[n]?.getD []
  base ++ p.steps.filterMap fun | .tok s => some s | .star => none

/-- Two values are equal when they have the same JSON type and content; the compact form of `Lean.Json`
    writes object members in key order, so equal values have equal compact forms and only they do. -/
def same (a b : Json) : Bool := a.compress == b.compress

def natJson (n : Nat) : Json := .num (JsonNumber.fromNat n)

def valueJson : Value → Json
  | .bool b => .bool b
  | .int n => natJson n
  | .str s => .str s

def Atom.admits : Atom → Json → Bool
  | .null, .null => true
  | .boolean, .bool _ => true
  | .integer, .num n => n.exponent == 0 && decide (0 ≤ n.mantissa)
  | .string, .str _ => true
  | .array, .arr _ => true
  | .object, .obj _ => true
  | _, _ => false

def TypeForm.admits : TypeForm → Json → Bool
  | .atom a, v => a.admits v
  | .arrayOf a, .arr xs => xs.all a.admits
  | .tuple parts, .arr xs =>
    xs.size == parts.length && (parts.zip xs.toList).all fun (a, x) => a.admits x
  | _, _ => false

/-- 2.3: a value of type `T`, one form or a list of forms any of which may match. -/
def hasType (t : List TypeForm) (v : Json) : Bool := t.any (·.admits v)

/-! ## Guards (2.3) -/

def Lit.holds (root : Json) (items : List Pointer) : Lit → Bool
  | .present p => (resolve root items p).isSome
  | .absent p => (resolve root items p).isNone
  | .equals p v => match resolve root items p with
    | some (_, w) => same w (valueJson v)
    | none => false
  | .differs p v => match resolve root items p with
    | some (_, w) => !same w (valueJson v)
    | none => true
  | .isType p t => match resolve root items p with
    | some (_, w) => hasType t w
    | none => false
  | .notType p t => match resolve root items p with
    | some (_, w) => !hasType t w
    | none => true

/-- 2.3: every literal of the guard holds. -/
def guardHolds (root : Json) (items : List Pointer) (g : List Lit) : Bool :=
  g.all (·.holds root items)

/-- Each element with the elements before it: `[a, b, c] ↦ [([], a), ([a], b), ([a, b], c)]`. -/
def withEarlier {α : Type} : List α → List (List α × α) :=
  go []
where
  go (before : List α) : List α → List (List α × α)
    | [] => []
    | x :: xs => (before, x) :: go (before ++ [x]) xs

/-! ## Expansion (2.6) -/

mutual
/-- 2.6: the instances of one entry, in order. -/
def expand (h : Hooks) (phase : String) (root : Json) (items earlier : List Pointer) (frame : Frame) :
    Entry → List Instance
  | .check c =>
    if guardHolds root items c.guard then [⟨phase, c, root, items, earlier, frame⟩] else []
  | .each _ over guard entries =>
    if guardHolds root items guard then
      (withEarlier ((collect root items over).map (·.1))).flatMap fun (before, p) =>
        expandAll h phase root (p :: items) before frame entries
    else []
  | .scope id loc view recode entries =>
    match resolve root items loc with
    | none => []
    | some (p, v) =>
      expandAll h phase (match view with | none => v | some name => h.view name v) [] []
        (frame.enter id p view recode) entries
/-- 2.6: the instances of each entry of a list, in list order. -/
def expandAll (h : Hooks) (phase : String) (root : Json) (items earlier : List Pointer) (frame : Frame) :
    List Entry → List Instance
  | [] => []
  | e :: es =>
    expand h phase root items earlier frame e ++ expandAll h phase root items earlier frame es
end
-- `lean/audit.py` reads the `end` of a `mutual` block as the end of the namespace; closing and
-- reopening the namespace here keeps its reading and Lean's the same.
end VE.WireContract

namespace VE.WireContract
open Lean

/-- 2.6: the table expanded over the input. -/
def instances (t : Table) (h : Hooks) (j : Json) : List Instance :=
  t.phases.flatMap fun p => expandAll h p.name j [] [] Frame.top p.entries

/-! ## Rendering (2.7) -/

/-- Lean's compact form escapes a line feed and a carriage return by letter; the record writes every
    character below U+0020 as `\u00xx` in lower case, as Lean already does for the others. -/
def lowerEscapes : List Char → List Char
  | '\\' :: 'n' :: rest => "\\u000a".toList ++ lowerEscapes rest
  | '\\' :: 'r' :: rest => "\\u000d".toList ++ lowerEscapes rest
  | '\\' :: c :: rest => '\\' :: c :: lowerEscapes rest
  | c :: rest => c :: lowerEscapes rest
  | [] => []

/-- The longest prefix of whole characters within 80 bytes in UTF-8, with `...` added, for a longer string. -/
def cut (s : String) : String :=
  if s.utf8ByteSize ≤ 80 then s
  else
    let kept := s.toList.foldl (fun (acc : String × Bool) c =>
      if acc.2 && (acc.1.push c).utf8ByteSize ≤ 80 then (acc.1.push c, true) else (acc.1, false)) ("", true)
    kept.1 ++ "..."

/-- The `json` renderer: compact JSON, keys in code point order, cut at 80 bytes. -/
def renderJson (v : Json) : String := cut (String.mk (lowerEscapes v.compress.toList))

def increasing : List String → Bool
  | a :: b :: rest => decide (a < b) && increasing (b :: rest)
  | _ => true

def strings? (v : Json) : Option (List String) :=
  match v with
  | .arr xs => xs.toList.mapM fun | .str s => some s | _ => none
  | _ => none

/-- 2.7: every renderer is total, and an absent value renders as the empty string. -/
def render (r : Renderer) : Option Json → String
  | none => ""
  | some v => match r, v with
    | .raw, .str s => s
    | .list, v => match strings? v with
      | some ss => ", ".intercalate (ss.mergeSort fun a b => !decide (b < a))
      | none => renderJson v
    | _, v => renderJson v

def escapeToken (s : String) : String := (s.replace "~" "~0").replace "/" "~1"

def pointerText (p : Pointer) : String := String.join (p.map fun s => "/" ++ escapeToken s)

/-- The first occurrence of each name. -/
def dedupNames (l : List (String × String)) : List (String × String) :=
  l.foldl (fun acc x => if acc.any (·.1 == x.1) then acc else acc ++ [x]) []

/-- 2.7: the finding of an instance that does not hold, reported for the check or member `id` with its code,
    class and template, at the local pointer `p`. -/
def finding (i : Instance) (id code cls : String) (text : List Piece) (p : Pointer) (target : Option Json)
    (extra returned : List (String × Json)) : Finding :=
  let value : String → Option Json := fun name =>
    match name with
    | "value" => target
    | "key" => some (.str ((i.items.head?.bind List.getLast?).getD ""))
    | "index" => some (natJson i.earlier.length)
    | _ => match extra.lookup name with
      | some v => some v
      | none => match i.check.args.lookup name with
        | some loc => (resolve i.root i.items loc).map (·.2)
        | none => returned.lookup name
  let rendered := text.map fun
    | .lit s => s
    | .arg n r => render r (value n)
  let named := dedupNames (text.filterMap fun
    | .lit _ => none
    | .arg n r => some (n, render r (value n)))
  let (code, cls) := i.frame.recode.getD (code, cls)
  let (path, inner) : Pointer × List (String × String) := match i.frame.viewSite with
    | some site => (site, [("inner_path", pointerText (i.frame.site ++ p))])
    | none => (i.frame.site ++ p, [])
  { check := "/".intercalate (i.frame.ids ++ [id]), phase := i.phase, code := code, cls := cls,
    path := pointerText path, text := String.join rendered, args := named ++ inner }

/-! ## Declarative checks (2.4) -/

def keysOf? (v : Json) : Option (List String) :=
  match v with
  | .obj _ => some ((children v).map (·.1))
  | _ => none

def memberCount? (v : Json) : Option Nat :=
  match v with
  | .arr xs => some xs.size
  | .obj _ => some (children v).length
  | _ => none

def contains (s x : String) : Bool :=
  (List.range (s.length + 1)).any fun n => (s.drop n).startsWith x

def inRanges (rs : List (Nat × Nat)) (c : Char) : Bool :=
  rs.any fun (lo, hi) => lo ≤ c.toNat && c.toNat ≤ hi

/-- 2.4: a string is in a lexical class when every member present is satisfied. -/
def NameClass.admits (k : NameClass) (s : String) : Bool :=
  (match k.first with
    | none => true
    | some rs => match s.toList with
      | c :: _ => inRanges rs c
      | [] => false) &&
  (match k.rest with
    | none => true
    | some rs => (s.toList.drop 1).all (inRanges rs)) &&
  k.minBytes.all (· ≤ s.utf8ByteSize) &&
  k.maxBytes.all (s.utf8ByteSize ≤ ·) &&
  k.forbidPrefix.all (fun x => !s.startsWith x) &&
  k.forbidInfix.all (fun x => !contains s x) &&
  k.oneOf.all (·.contains s)

/-- 2.4: the extra arguments of a failing declarative check on the present target `v` at `p`, or `none` when
    it holds. `earlier` are the earlier items of the innermost group and `loc` the check's location. -/
def failsOn (root : Json) (items earlier : List Pointer) (loc : Pattern) (k : Kind) (p : Pointer) (v : Json) :
    Option (List (String × Json)) :=
  let bad (b : Bool) : Option (List (String × Json)) := if b then some [] else none
  match k with
  | .hasType t => bad (!hasType t v)
  | .exactKeys ks => bad (match keysOf? v with
    | some a => !(a.all ks.contains && ks.all a.contains)
    | none => true)
  | .keys req opt => bad (match keysOf? v with
    | some a => !(req.all a.contains && a.all fun x => req.contains x || opt.contains x)
    | none => true)
  | .const x => bad (!same v (valueJson x))
  | .oneOf xs => bad (!xs.any fun x => same v (valueJson x))
  | .maxItems n => match memberCount? v with
    | some m => if n < m then some [("count", natJson m), ("limit", natJson n)] else none
    | none => none
  | .maxBytes n => match v with
    | .str s => if n < s.utf8ByteSize then some [("count", natJson s.utf8ByteSize), ("limit", natJson n)]
      else none
    | _ => none
  | .name k false => bad (match v with
    | .str s => !k.admits s
    | _ => true)
  | .name k true => bad (!k.admits (p.getLast?.getD ""))
  | .sortedUnique => bad (match strings? v with
    | some ss => !increasing ss
    | none => false)
  | .uniqueSoFar => bad (earlier.any fun e => match resolve root (e :: items.drop 1) loc with
    | some (_, w) => same w v
    | none => false)
  | .declaredIn set => bad (!(collect root items set).any fun (_, w) => same v w)
  | .requiresMember key => bad (match keysOf? v with
    | some a => !a.contains key
    | none => false)
  | .requiresItem x => bad (match v with
    | .arr xs => !xs.any fun w => same w (valueJson x)
    | _ => false)
  | .excludesMember key => bad (match keysOf? v with
    | some a => a.contains key
    | none => false)
  | .excludesItem x => bad (match v with
    | .arr xs => xs.any fun w => same w (valueJson x)
    | _ => false)
  | .maxCount _ _ | .hook _ | .classifier _ _ => none

/-! ## The engine (5.2) -/

/-- 2.4, 2.5, 2.7: `none` when the instance holds, otherwise its finding. For a `hook` or `classifier` it calls
    `h` once; for every other kind it does not use `h`. -/
def eval (h : Hooks) (i : Instance) : Option Finding :=
  let c := i.check
  let target := resolve i.root i.items c.loc
  match c.kind with
  | .hook name => match h.predicate name i.root i.items with
    | .ok => none
    | .fail args => some (finding i c.id c.code c.cls c.text (concrete i.items c.loc) (target.map (·.2)) [] args)
  | .classifier name emits => match h.classifier name i.root i.items with
    | .ok => none
    | .fail member args => (emits.find? (·.id == member)).map fun m =>
      finding i m.id m.code m.cls m.text (concrete i.items c.loc) (target.map (·.2)) [] args
  | .maxCount pattern limit =>
    let n := (collect i.root i.items pattern).length
    if limit < n then
      some (finding i c.id c.code c.cls c.text (concrete i.items c.loc) (target.map (·.2))
        [("count", natJson n), ("limit", natJson limit)] [])
    else none
  | k => match target with
    | none => none
    | some (p, v) => (failsOn i.root i.items i.earlier c.loc k p v).map fun extra =>
      finding i c.id c.code c.cls c.text p (some v) extra []

def Holds (h : Hooks) (i : Instance) : Prop := eval h i = none

/-- The engine: the finding of the first instance that does not hold. -/
def run (t : Table) (h : Hooks) (j : Json) : Option Finding :=
  (instances t h j).findSome? (eval h)

/-- 2.7: the record of a finding, with the table's `contract` and `revision`. -/
def record (t : Table) (f : Finding) : Json :=
  Json.mkObj [("contract", .str t.contract), ("revision", natJson t.revision), ("check", .str f.check),
    ("phase", .str f.phase), ("code", .str f.code), ("class", .str f.cls), ("path", .str f.path),
    ("text", .str f.text), ("args", Json.mkObj (f.args.map fun (n, v) => (n, .str v)))]

/-! ## Registered names, for the build-time check of the hook modules (5.3) -/

mutual
def Entry.hookNames : Entry → List String
  | .check c => match c.kind with
    | .hook n => [n]
    | .classifier n _ => [n]
    | _ => []
  | .each _ _ _ entries => entriesHookNames entries
  | .scope _ _ view _ entries => view.toList ++ entriesHookNames entries
def entriesHookNames : List Entry → List String
  | [] => []
  | e :: es => e.hookNames ++ entriesHookNames es
end
-- `lean/audit.py` reads the `end` of a `mutual` block as the end of the namespace; closing and
-- reopening the namespace here keeps its reading and Lean's the same.
end VE.WireContract

namespace VE.WireContract
open Lean

/-- Every hook, classifier and view name that occurs in a table. -/
def Table.hookNames (t : Table) : List String :=
  t.phases.flatMap fun p => entriesHookNames p.entries

/-! ## The statements (5.3) -/

/-- The plan's first lemma: the engine reports nothing exactly when every instance holds. -/
theorem run_clean_iff (t : Table) (h : Hooks) (j : Json) :
    run t h j = none ↔ ∀ i ∈ instances t h j, eval h i = none := by
  unfold run
  exact List.findSome?_eq_none_iff

/-- The plan's second lemma: a reported finding is that of an instance before which every instance holds. -/
theorem run_fault_first (t : Table) (h : Hooks) (j : Json) (d : Finding) :
    run t h j = some d ↔
      ∃ pre i post, instances t h j = pre ++ i :: post ∧ eval h i = some d ∧
        ∀ b ∈ pre, eval h b = none := by
  unfold run
  exact List.findSome?_eq_some_iff

/-- Phases are whole-input: a later phase is consulted only when the earlier phases report nothing. -/
theorem run_phase_major (t : Table) (ps qs : List Phase) (h : Hooks) (j : Json)
    (ht : t.phases = ps ++ qs) :
    run t h j = (run { t with phases := ps } h j).or (run { t with phases := qs } h j) := by
  simp only [run, instances, ht, List.flatMap_append, List.findSome?_append]

mutual
/-- Expansion reads the hooks only through their views. -/
theorem expand_views (h g : Hooks) (hv : h.view = g.view) (phase : String) (root : Json)
    (items earlier : List Pointer) (frame : Frame) :
    ∀ e, expand h phase root items earlier frame e = expand g phase root items earlier frame e
  | .check _ => by simp only [expand]
  | .each _ over guard entries => by
    simp only [expand, expandAll_views h g hv]
  | .scope id loc view recode entries => by
    simp only [expand, expandAll_views h g hv, hv]
/-- Expansion of a list reads the hooks only through their views. -/
theorem expandAll_views (h g : Hooks) (hv : h.view = g.view) (phase : String) (root : Json)
    (items earlier : List Pointer) (frame : Frame) :
    ∀ es, expandAll h phase root items earlier frame es = expandAll g phase root items earlier frame es
  | [] => by simp only [expandAll]
  | e :: es => by
    simp only [expandAll, expand_views h g hv phase root items earlier frame e,
      expandAll_views h g hv phase root items earlier frame es]
end
-- `lean/audit.py` reads the `end` of a `mutual` block as the end of the namespace; closing and
-- reopening the namespace here keeps its reading and Lean's the same.
end VE.WireContract

namespace VE.WireContract
open Lean

/-- The table expanded with two hook sets that have the same views is the same list. -/
theorem instances_views (t : Table) (h g : Hooks) (j : Json) (hv : h.view = g.view) :
    instances t h j = instances t g j := by
  simp only [instances, expandAll_views h g hv]

/-- The first finding of a list depends on a function only where it is reached. -/
theorem findSome_congr_reached {α β : Type} (f g : α → Option β) :
    ∀ l : List α, (∀ pre i post, l = pre ++ i :: post → (∀ b ∈ pre, f b = none) → f i = g i) →
      l.findSome? f = l.findSome? g
  | [], _ => rfl
  | a :: l, hr => by
    have ha : f a = g a := hr [] a l rfl (by simp)
    cases hfa : f a with
    | some x => simp [hfa, ← ha]
    | none =>
      have hga : g a = none := by rw [← ha, hfa]
      have hl : l.findSome? f = l.findSome? g := by
        apply findSome_congr_reached f g l
        intro pre i post hsplit hpre
        apply hr (a :: pre) i post (by simp [hsplit])
        intro b hb
        cases List.mem_cons.mp hb with
        | inl hab => rw [hab]; exact hfa
        | inr hb' => exact hpre b hb'
      simp [hfa, hga, hl]

/-- Claim (B) of 2.9: two hook sets with the same views, which agree on every instance that is reached,
    give the same result. Hooks after the first instance that does not hold are never consulted. -/
theorem run_congr_reached (t : Table) (h g : Hooks) (j : Json)
    (hv : ∀ name v, h.view name v = g.view name v)
    (hr : ∀ pre i post, instances t h j = pre ++ i :: post →
            (∀ b ∈ pre, eval h b = none) → eval h i = eval g i) :
    run t h j = run t g j := by
  have hview : h.view = g.view := funext fun name => funext fun v => hv name v
  unfold run
  rw [← instances_views t h g j hview]
  exact findSome_congr_reached (eval h) (eval g) _ hr

end VE.WireContract
