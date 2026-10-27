import VE.Scope.Examples
import VE.Service.ScopeAdmission
import VE.Discourse.Joint
import VE.Readings.Companions

/-! Statement stub of scope spec section 11 (sc-5r: per choice over a reading set a governed unit owns,
docs/spec/scope.md). Evidence for the statement review, not product code: it lives under docs/, imports the tree on
`main` unchanged, and every proof is `sorry` (the build item sc-5rb proves them, spec 11.7).
Check it from `lean/` with `PATH=~/.elan/bin:$PATH lake env lean ../docs/spec/scope/SpecStubs_sc5r.lean`.

Section numbers in comments are the spec's. The fixtures of 11.6 are `#guard`s over the hard-constraint document of
`VE.Scope.Examples` (`hcDoc`, `parts`, `g1`), so every value 11.6 lists is computed here. -/

namespace VE.Scope
open Lean

/-! ## 11.2 Placeholders (8.1) -/

namespace Pinned

/-- sc-1ae's hypothesis (the DRI's fix (a), 2026-10-27): every JSON object, at any depth, is a well-formed tree. -/
inductive JsonWF : Json → Prop
  | null : JsonWF .null
  | bool (b : Bool) : JsonWF (.bool b)
  | num (n : JsonNumber) : JsonWF (.num n)
  | str (s : String) : JsonWF (.str s)
  | arr (xs : Array Json) : (∀ x ∈ xs, JsonWF x) → JsonWF (.arr xs)
  | obj (kvs : Std.TreeMap.Raw String Json) : kvs.WF → (∀ kv ∈ kvs.toList, JsonWF kv.2) → JsonWF (.obj kvs)

/-- Spec 4.2's `HasStr` (sc-1ae): a JSON string value occurs in a JSON value (object keys are not values). -/
inductive HasStr (s : String) : Json → Prop
  | str : HasStr s (.str s)
  | arr {xs : Array Json} {x : Json} : x ∈ xs → HasStr s x → HasStr s (.arr xs)
  | obj {j x : Json} {k : String} : j.getObjVal? k = .ok x → HasStr s x → HasStr s j

/-- sc-5rb's document mode: `checkDoc` (5.2) with `governSetsWith governFast` in place of `governFast`. -/
opaque checkDocSets : Json → Except String Json
/-- sc-5rb's `withUnits` (8.1), which also hands the chain GOVERN's `reading_sets`. -/
opaque withGoverned : Json → Json → Json

/-- Spec 4.2's `payload` (sc-1ae). -/
def payload : Effect → Json
  | .frame p => p
  | .reguard c => c
  | .carveOut c => c
  | _ => .null

end Pinned

/-! ## 11.2 The definitions -/

/-- lf-14d's limit on joint choices (`compatibleChoices … 64`) and the readings route's (`VE.Readings.maxChoices`). -/
def choiceLimit : Nat := 64

def setsJson (doc : Json) : List Json := match doc.getObjValD "reading_sets" with
  | .arr xs => xs.toList
  | _ => []
def setUnit (s : Json) : String := (s.getObjValD "unit").getStr?.toOption.getD ""
def setVersion (s : Json) : Nat := (s.getObjValD "version").getNat?.toOption.getD 0
def readingsJson (s : Json) : List Json := match s.getObjValD "readings" with
  | .arr xs => xs.toList
  | _ => []

/-- Neither a frontier reach nor a frontier fixed by a pick (5.7). -/
def layoutReach : Reach → Bool
  | .frontier | .fixed _ => false
  | _ => true

/-- 11.1: the units whose reading set is governed per choice. A unit of the document, written without content, with
    exactly one reading set, which holds a reading; some governor covers it; it is no governor's own unit; and no
    frontier or fixed reach covers it. -/
def governedSetUnits (D : SDoc) : List String :=
  (setUnits D.doc).eraseDups.filter fun u =>
    (unitIds D.doc).contains u && (contentOf D.doc u).isNull && (setUnits D.doc).count u == 1 &&
    ((setsJson D.doc).find? (setUnit · == u)).any (fun s => !(readingsJson s).isEmpty) &&
    D.governors.any (fun g => coversU D g u) &&
    D.governors.all (fun g => g.unit != u && (layoutReach g.reach || !coversU D g u))

def governedSets (D : SDoc) : List Json := (setsJson D.doc).filter fun s => (governedSetUnits D).contains (setUnit s)

/-- A governed set as lf-14d's enumeration reads it: its id, its version and its number of readings
    (`VE.Discourse.mem_allChoices`: the enumeration reads nothing else). -/
def shapeOf (s : Json) : VE.Route.Admission.ReadingSet := ⟨idOf s, setVersion s, (readingsJson s).map fun _ => .top⟩

def setShapes (D : SDoc) : List VE.Route.Admission.ReadingSet := (governedSets D).map shapeOf

/-- Every joint choice of the governed sets, lf-14d's product in lf-14d's order, within the limit. -/
def setChoices (D : SDoc) : Except String (List VE.Discourse.Choice) :=
  if VE.Discourse.productSize (setShapes D) > choiceLimit then .error "ResourceLimit: scope choices"
  else .ok (VE.Discourse.allChoices (setShapes D))

def pickOf (ch : VE.Discourse.Choice) (s : Json) : Option Nat :=
  (ch.find? (fun x => x.1 == idOf s && x.2.1 == setVersion s)).map (·.2.2)
def readingAt (s : Json) (i : Nat) : Json := (((readingsJson s)[i]?).map (·.getObjValD "content")).getD .null

/-- The document under one choice: each unit of `su` carries the content of its set's chosen reading, and the sets on
    the units of `su` leave `reading_sets`. -/
def atChoiceOn (su : List String) (doc : Json) (ch : VE.Discourse.Choice) : Json :=
  let sets := setsJson doc
  let units := (unitsOf doc).map fun u =>
    match sets.find? (fun s => su.contains (setUnit s) && setUnit s == idOf u) with
    | some s => u.setObjVal! "content" (((pickOf ch s).map (readingAt s)).getD .null)
    | none => u
  (doc.setObjVal! "units" (.arr units.toArray)).setObjVal! "reading_sets"
    (.arr (sets.filter fun s => !su.contains (setUnit s)).toArray)

def atChoice (D : SDoc) (ch : VE.Discourse.Choice) : SDoc :=
  { D with doc := atChoiceOn (governedSetUnits D) D.doc ch }

/-- `govern` under one joint choice of the governed sets: the sibling of 5.7's `governAt`, whose `pick` fixes a
    governor's reach and cannot carry a unit's reading. -/
def governChoice (D : SDoc) (ch : VE.Discourse.Choice) : Except String Json := govern (atChoice D ch)

/-- 11.5: a choice, named by each governed set's unit, set, version and chosen reading. -/
def choiceText (D : SDoc) (ch : VE.Discourse.Choice) : String :=
  ", ".intercalate ((governedSets D).filterMap fun s => (pickOf ch s).map fun i =>
    s!"{setUnit s} {idOf s}@{setVersion s}:{(((readingsJson s)[i]?).map idOf).getD ""}")

/-- 11.5: a fault under a choice names the choice; a resource limit is passed on as it is (UNKNOWN). -/
def choiceFault (D : SDoc) (ch : VE.Discourse.Choice) (e : String) : String :=
  if e.startsWith "ResourceLimit" then e else s!"ScopeChoice: {choiceText D ch}: {e}"

/-- 11.5: the first fault in lf-14d's order of the choices, as the document's own text when every choice has that
    fault (it does not depend on the choice), else named with its choice by `choiceFault`. -/
def faultOf (D : SDoc) (rs : List (VE.Discourse.Choice × Except String Json)) : Option String :=
  match rs.findSome? (fun (ch, r) => match r with | .error e => some (ch, e) | .ok _ => none) with
  | none => none
  | some (ch, e) =>
    some (if rs.all (fun (_, r) => match r with | .error e' => e' == e | .ok _ => false) then e else choiceFault D ch e)

/-- The answer from the per-choice answers `outs` (in lf-14d's order, `(ch₀, o₀)` the first): every unit outside the
    governed set units as `o₀` writes it, refused when another choice writes it otherwise; each governed set unit as
    written; each governed set's reading `i` with the content its unit has under the choices that pick `i`, refused
    when two of them differ. Equality is `VE.Readings.Wire.jeq`, the tree equality proved sound (`jeq_iff`). -/
def assemble (D : SDoc) (ch₀ : VE.Discourse.Choice) (o₀ : Json) (outs : List (VE.Discourse.Choice × Json)) :
    Except String Json := do
  let su := governedSetUnits D
  for (ch, o) in outs do
    for (x, x₀) in (unitsOf o).zip (unitsOf o₀) do
      unless su.contains (idOf x) || VE.Readings.Wire.jeq x x₀ do
        throw s!"ScopeReadings: {idOf x}: differs between choices {choiceText D ch₀} and {choiceText D ch}"
  let readingIn (s : Json) (i : Nat) : Except String Json :=
    match outs.filter (fun (ch, _) => pickOf ch s == some i) with
    | [] => pure (readingAt s i)
    | (c₁, o₁) :: rest => do
      for (c, o) in rest do
        unless VE.Readings.Wire.jeq (contentOf o (setUnit s)) (contentOf o₁ (setUnit s)) do
          throw s!"ScopeReadings: {setUnit s}: differs between choices {choiceText D c₁} and {choiceText D c}"
      pure (contentOf o₁ (setUnit s))
  let sets ← (setsJson D.doc).mapM fun s => do
    if su.contains (setUnit s) then
      let rs ← (readingsJson s).zipIdx.mapM fun (r, i) => do pure (r.setObjVal! "content" (← readingIn s i))
      pure (s.setObjVal! "readings" (.arr rs.toArray))
    else pure s
  let units := ((unitsOf o₀).zip (unitsOf D.doc)).map fun (x, y) => if su.contains (idOf y) then y else x
  pure ((D.doc.setObjVal! "units" (.arr units.toArray)).setObjVal! "reading_sets" (.arr sets.toArray))

/-- 11.2: GOVERN over the governed sets, with `gv` for `govern` (the run path passes `governFast`, 1.5.8). -/
def governSetsWith (gv : SDoc → Except String Json) (D : SDoc) : Except String Json := do
  if (governedSetUnits D).isEmpty then gv D else
  let cs ← setChoices D
  let rs := cs.map fun ch => (ch, gv (atChoice D ch))
  if let some e := faultOf D rs then throw e
  match rs.filterMap (fun (ch, r) => r.toOption.map (ch, ·)) with
  | [] => throw "ResourceLimit: scope choices"   -- never: every governed set holds a reading
  | outs@((ch₀, o₀) :: _) => assemble D ch₀ o₀ outs

def governSets (D : SDoc) : Except String Json := governSetsWith govern D

/-! ## 11.3 The statements -/

/-- `governAt_no_frontier`, restated: with no governed set, the answer is `govern`'s, byte for byte as a value. -/
theorem governSets_no_sets (D : SDoc) (h : governedSetUnits D = []) : governSets D = govern D := by sorry

/-- The run path answers as the statement (`governFast_eq` per choice). -/
theorem governSetsFast_eq (D : SDoc) : governSetsWith governFast D = governSets D := by sorry

/-- `governAt_preserves`, restated: all but `units`, `reading_sets` and the governed readings' `content` is kept. -/
theorem governSets_preserves (D : SDoc) (hw : Pinned.JsonWF D.doc) (out : Json) (ho : governSets D = .ok out) :
    (∀ k, k ≠ "units" → k ≠ "reading_sets" → out.getObjVal? k = D.doc.getObjVal? k) ∧
    (unitsOf out).map idOf = (unitsOf D.doc).map idOf ∧
    (∀ (i : Nat) (x y : Json), (unitsOf out)[i]? = some x → (unitsOf D.doc)[i]? = some y →
      (∀ k, k ≠ "content" → x.getObjVal? k = y.getObjVal? k) ∧ (idOf y ∈ governedSetUnits D → x = y)) ∧
    (setsJson out).length = (setsJson D.doc).length ∧
    ∀ (i : Nat) (x y : Json), (setsJson out)[i]? = some x → (setsJson D.doc)[i]? = some y →
      (setUnit y ∉ governedSetUnits D → x = y) ∧ (∀ k, k ≠ "readings" → x.getObjVal? k = y.getObjVal? k) ∧
      (readingsJson x).length = (readingsJson y).length ∧
      ∀ (n : Nat) (r r' : Json), (readingsJson x)[n]? = some r → (readingsJson y)[n]? = some r' →
        ∀ k, k ≠ "content" → r.getObjVal? k = r'.getObjVal? k := by sorry

/-- Per choice: every joint choice of the governed sets, read off the answer, is `govern` of that choice. -/
theorem governSets_every_choice (D : SDoc) (hw : Pinned.JsonWF D.doc) (hs : governedSetUnits D ≠ [])
    (out : Json) (ho : governSets D = .ok out) (cs : List VE.Discourse.Choice) (hcs : setChoices D = .ok cs)
    (ch : VE.Discourse.Choice) (hc : ch ∈ cs) :
    ∃ o, governChoice D ch = .ok o ∧ atChoiceOn (governedSetUnits D) out ch = o := by sorry

/-- `govern_strings`, per choice: no reading brings in a new symbol. -/
theorem governSets_strings (D : SDoc) (hw : Pinned.JsonWF D.doc) (out : Json) (ho : governSets D = .ok out)
    (s : String) (hs : Pinned.HasStr s out) :
    Pinned.HasStr s D.doc ∨ ∃ g ∈ D.governors, Pinned.HasStr s (Pinned.payload g.effect) := by sorry

/-- `scope_choices`, restated: the choices checked are lf-14d's joint choices over the governed sets. -/
theorem scope_set_choices (D : SDoc) (cs : List VE.Discourse.Choice) (hcs : setChoices D = .ok cs)
    (K : VE.Discourse.Manifest) (n : Nat) (cs' : List VE.Discourse.Choice)
    (hk : VE.Discourse.compatibleChoices K (setShapes D) n = .ok cs') :
    (∀ c ∈ cs', c ∈ cs) ∧ (K.constraints = [] → cs' = cs) := by sorry

/-- A fault under one choice refuses the document: it is admitted only when every choice is. -/
theorem governSets_choice_refused (D : SDoc) (hs : governedSetUnits D ≠ []) (cs : List VE.Discourse.Choice)
    (hcs : setChoices D = .ok cs) (ch : VE.Discourse.Choice) (hc : ch ∈ cs) (e : String)
    (he : governChoice D ch = .error e) : (governSets D).isOk = false := by sorry

/-- A fault every choice has is the document's own text, named with no choice (as `govern` would give it). -/
theorem faultOf_every (D : SDoc) (rs : List (VE.Discourse.Choice × Except String Json)) (hn : rs ≠ []) (e : String)
    (h : ∀ p ∈ rs, p.2 = .error e) : faultOf D rs = some e := by sorry

/-- A resource limit under a choice is passed on unchanged: UNKNOWN, never a refusal of that choice (9.4 item 4). -/
theorem choiceFault_limit (D : SDoc) (ch : VE.Discourse.Choice) (e : String) (h : e.startsWith "ResourceLimit" = true) :
    choiceFault D ch e = e := by sorry

/-- More joint choices than the limit: `ResourceLimit` (UNKNOWN), never a truncated product. -/
theorem governSets_limit (D : SDoc) (h : VE.Discourse.productSize (setShapes D) > choiceLimit) :
    governSets D = .error "ResourceLimit: scope choices" := by sorry

/-- `readings_refused`, restated for the document mode: a set this section does not govern is still refused. -/
theorem governSets_readings_refused (D : SDoc) (hw : Pinned.JsonWF D.doc) (g : Governor) (hg : g ∈ D.governors)
    (us : List String) (hc : covered D g.reach = .ok us) (u : String) (hu : u = g.unit ∨ u ∈ us)
    (hs : u ∈ setUnits D.doc) (hn : u ∉ governedSetUnits D) : (governSets D).isOk = false := by sorry

/-- `scope_admission` (5.2), restated: the chain checks GOVERN's units and reading sets. -/
theorem scope_admission_sets (front ans : Json) (h : Pinned.checkDocSets front = .ok ans)
    (hs : "scope@0" ∈ VE.Service.Document.profilesOf front) :
    ∃ D out a, decodeScope front = .ok D ∧ governSets D = .ok out ∧
      VE.Service.Document.checkCore (Pinned.withGoverned front out) = .ok a ∧ ans = foldGovernors D a := by sorry

end VE.Scope

/-! ## 11.6 Fixtures, computed -/

namespace VE.Scope.Examples
open Lean VE.Scope

def guardWide : Json := j "[\"and\", [\"or\", [\"unary\", \"creating_a_cyberweapon\", [\"var\", 1]], [\"unary\", \"creating_malicious_code\", [\"var\", 1]]], [\"unary\", \"could_cause_significant_damage_if_deployed\", [\"var\", 1]]]"
def guardNarrow : Json := j "[\"or\", [\"unary\", \"creating_a_cyberweapon\", [\"var\", 1]], [\"and\", [\"unary\", \"creating_malicious_code\", [\"var\", 1]], [\"unary\", \"could_cause_significant_damage_if_deployed\", [\"var\", 1]]]]"
def cyberPart (pred : String) (g : Json) (extra : List (String × Json) := []) : Json :=
  Json.mkObj [("part", Json.mkObj ([("name", Json.str "hc-cyberweapons"), ("predicate", Json.str pred), ("guard", g)] ++ extra))]
def reading (id : String) (content : Json) : Json :=
  Json.mkObj [("id", id), ("kind", "norm"), ("meaning_id", s!"m-{id}"), ("content", content),
    ("admission", Json.mkObj [("who", "translator"), ("why", "the clause attaches to both nouns or to one")])]
def rset (id unit : String) (rs : List Json) : Json :=
  Json.mkObj [("id", id), ("unit", unit), ("version", (1 : Nat)), ("status", "open"), ("readings", .arr rs.toArray)]
/-- u0165.s03's set as the pilot records it (two candidates, wide and narrow), each reading a part under the frame. -/
def s03set (wide narrow : Json) : Json := rset "scope-u0165-s03" "u0165.s03" [reading "wide" wide, reading "narrow" narrow]
def s03 : Json := s03set (cyberPart "cyberweapon_creation_permitted" guardWide) (cyberPart "cyberweapon_creation_permitted" guardNarrow)
/-- The hard-constraint document: the six other items' parts, u0165.s03 without content, and the given sets. -/
def setDoc (sets : List Json) (cs : List (String × Json) := without "u0165.s03" parts) : Json :=
  hcDoc cs [("reading_sets", .arr sets.toArray)]
def sets (doc : Json) (gs : List Governor) (ln : List (VE.Discourse.ContentName × String × String) := []) :
    Except String Json := do
  governSets (sdoc doc gs ln (← VE.Readings.Wire.decodeEnvironment envJ))
def readingContents (r : Except String Json) (u : String) : Option (List String) :=
  r.toOption.map fun o => (((setsJson o).find? (setUnit · == u)).map fun s =>
    (readingsJson s).map (·.getObjValD "content" |>.compress)).getD []
def wideNorm : String :=
  "{\"norm\":{\"guard\":[\"and\",[\"or\",[\"unary\",\"creating_a_cyberweapon\",[\"var\",1]],[\"unary\",\"creating_malicious_code\",[\"var\",1]]],[\"unary\",\"could_cause_significant_damage_if_deployed\",[\"var\",1]]],\"name\":\"hc-cyberweapons\",\"over\":[],\"predicate\":\"cyberweapon_creation_permitted\",\"sign\":false,\"unless\":[]}}"
def narrowNorm : String :=
  "{\"norm\":{\"guard\":[\"or\",[\"unary\",\"creating_a_cyberweapon\",[\"var\",1]],[\"and\",[\"unary\",\"creating_malicious_code\",[\"var\",1]],[\"unary\",\"could_cause_significant_damage_if_deployed\",[\"var\",1]]]],\"name\":\"hc-cyberweapons\",\"over\":[],\"predicate\":\"cyberweapon_creation_permitted\",\"sign\":false,\"unless\":[]}}"

/-- SR-1 with `g2`: the wide reading's rule, re-guarded by u0173.s01's condition (the F3 shape of 7.4). -/
def wideG2 : String :=
  "{\"norm\":{\"guard\":[\"or\",[\"and\",[\"and\",[\"or\",[\"unary\",\"creating_a_cyberweapon\",[\"var\",1]],[\"unary\",\"creating_malicious_code\",[\"var\",1]]],[\"unary\",\"could_cause_significant_damage_if_deployed\",[\"var\",1]]],{\"attitude\":{\"content\":[\"and\",[\"or\",[\"unary\",\"creating_a_cyberweapon\",[\"var\",1]],[\"unary\",\"creating_malicious_code\",[\"var\",1]]],[\"unary\",\"could_cause_significant_damage_if_deployed\",[\"var\",1]]],\"holder\":[\"var\",0],\"mode\":\"knows\"}}],{\"attitude\":{\"content\":[\"and\",[\"or\",[\"unary\",\"creating_a_cyberweapon\",[\"var\",1]],[\"unary\",\"creating_malicious_code\",[\"var\",1]]],[\"unary\",\"could_cause_significant_damage_if_deployed\",[\"var\",1]]],\"degree\":\"quite likely\",\"holder\":[\"var\",0],\"mode\":\"thinks\"}}],\"name\":\"hc-cyberweapons\",\"over\":[],\"predicate\":\"cyberweapon_creation_permitted\",\"sign\":false,\"unless\":[]}}"
/-- The narrow reading's rule is the one `govern` gives u0165.s03 when its part is written in place of the set. -/
def narrowG2 : Option String :=
  contentStr (gov (hcDoc ((without "u0165.s03" parts) ++ [("u0165.s03", cyberPart "cyberweapon_creation_permitted" guardNarrow)])) [g1, g2] hcNames) "u0165.s03"

-- SR-1: u0165.s03's set inside the hard-constraint list. Two choices, each conflict-free: the list is admitted; each
-- reading is composed as the unit would be; u0165.s03 stays as written; the other items are F1-g's
#guard (do pure (governedSetUnits (sdoc (setDoc [s03]) [g1] [] (← VE.Readings.Wire.decodeEnvironment envJ))) :
  Except String (List String)).toOption == some ["u0165.s03"]
#guard (do setChoices (sdoc (setDoc [s03]) [g1] [] (← VE.Readings.Wire.decodeEnvironment envJ))).toOption ==
  some [[("scope-u0165-s03", 1, 0)], [("scope-u0165-s03", 1, 1)]]
#guard readingContents (sets (setDoc [s03]) [g1]) "u0165.s03" == some [wideNorm, narrowNorm]
#guard contentStr (sets (setDoc [s03]) [g1]) "u0165.s03" == some "null"
#guard contentStr (sets (setDoc [s03]) [g1]) "u0165.s01" == contentStr (gov (hcDoc parts) [g1]) "u0165.s01" &&
  (contentStr (sets (setDoc [s03]) [g1]) "u0165.s01").isSome
-- the per-choice statement on SR-1: each choice read off the answer is `govern` of that choice
def perChoice (doc : Json) (gs : List Governor) : Except String Bool := do
  let D := sdoc doc gs [] (← VE.Readings.Wire.decodeEnvironment envJ)
  let out ← governSets D
  let cs ← setChoices D
  cs.allM fun ch => do pure (VE.Readings.Wire.jeq (atChoiceOn (governedSetUnits D) out ch) (← governChoice D ch))
#guard (perChoice (setDoc [s03]) [g1]).toOption == some true
-- with g2 (the re-guard over the list name) too: every reading is re-guarded, as the items are
#guard (readingContents (sets (setDoc [s03]) [g1, g2] hcNames) "u0165.s03") == (narrowG2.map fun n => [wideG2, n]) && narrowG2.isSome &&
  contentStr (sets (setDoc [s03]) [g1, g2] hcNames) "u0165.s01" == contentStr (gov (hcDoc parts) [g1, g2] hcNames) "u0165.s01"

-- SR-c: one choice conflicts (its reading writes `sign`, which the frame writes): refused, naming the unit and choice
#guard errorOf (sets (setDoc [s03set (cyberPart "cyberweapon_creation_permitted" guardWide)
    (cyberPart "cyberweapon_creation_permitted" guardNarrow [("sign", .bool false)])]) [g1]) ==
  "ScopeChoice: u0165.s03 scope-u0165-s03@1:narrow: ScopeConflict: u0165.s03: sign"
-- a reading that is an assertion under the frame: refused under its choice, never skipped
#guard errorOf (sets (setDoc [s03set (j "[\"top\"]") (cyberPart "cyberweapon_creation_permitted" guardNarrow)]) [g1]) ==
  "ScopeChoice: u0165.s03 scope-u0165-s03@1:wide: ScopeNotARule: u0165.s03"

-- SR-cap: two governed sets of 8 and 9 readings (72 joint choices): ResourceLimit, UNKNOWN; 8 and 8 (64) are checked
def wideSet (id unit : String) (n : Nat) : Json :=
  rset id unit ((List.range n).map fun i => reading s!"r{i}" (cyberPart "cyberweapon_creation_permitted" guardWide))
#guard errorOf (sets (setDoc [wideSet "s3" "u0165.s03" 8, wideSet "s5" "u0165.s05" 9] ((without "u0165.s05" parts).filter (·.1 != "u0165.s03"))) [g1]) ==
  "ResourceLimit: scope choices"
#guard errorOf (sets (setDoc [wideSet "s3" "u0165.s03" 8, wideSet "s5" "u0165.s05" 8] ((without "u0165.s05" parts).filter (·.1 != "u0165.s03"))) [g1]) ==
  "ok"

-- SR-u: a reading set on a unit no governor covers (u0166.s01) is returned unchanged, beside a governed set and alone
def u0166set : Json := rset "u0166-set" "u0166.s01" [reading "a" .null, reading "b" .null]
#guard (sets (setDoc [s03, u0166set]) [g1]).toOption.map (fun o =>
  ((setsJson o).find? (setUnit · == "u0166.s01")).map (VE.Readings.Wire.jeq u0166set)) == some (some true)
#guard (sets (hcDoc parts [("reading_sets", .arr #[u0166set])]) [g1]).toOption.map (VE.Readings.Wire.jeq ·
  ((gov (hcDoc parts [("reading_sets", .arr #[u0166set])]) [g1]).toOption.getD .null)) == some true

-- SR-0: no reading set: the answer is `govern`'s, as a value (F1-g's document, and F-id's)
#guard (sets (hcDoc parts) [g1]).toOption.map (VE.Readings.Wire.jeq · ((gov (hcDoc parts) [g1]).toOption.getD .null)) ==
  some true
#guard same (sets (hcDoc fourNorms [("title", "x")]) []) (hcDoc fourNorms [("title", "x")])

-- SR-g: still refused (F-rs's governor half): a set on the governor's own unit; a set on a governed unit that has content
#guard errorOf (sets (setDoc [s03, rset "lead" "u0164.s02" [reading "a" .null]]) [g1]) == "ScopeReadings: u0164.s02"
-- a carve-out written on u0165.s03 itself: the governor's own unit, though the frame covers it
#guard errorOf (sets (setDoc [s03]) [g1, ⟨"gX", "u0165.s03", carveT, .list "u0164.s02", seven⟩]) == "ScopeReadings: u0165.s03"
-- a fault every choice has is named with no choice: a frame recording six of the seven units (F-mm)
#guard errorOf (sets (setDoc [s03]) [{g1 with units := seven.take 6}]) == "ManifestMismatch: scope.governors.g1.units"
#guard errorOf (sets (hcDoc parts [("reading_sets", .arr #[s03])]) [g1]) == "ScopeReadings: u0165.s03"
-- F-rs itself is unchanged: `govern` refuses the set it governs per choice
#guard errorOf (gov (setDoc [s03]) [g1]) == "ScopeReadings: u0165.s03"

-- SR-dep: another unit's rule depends on the choice. r9 on u0166.s01 takes precedence over the rules named hc-2 and
-- hc-cyberweapons on its predicate; the narrow reading has another predicate, so r9's `over` differs: refused
def r9 : Json := j "{\"norm\": {\"name\": \"r9\", \"predicate\": \"cyberweapon_creation_permitted\", \"sign\": true, \"guard\": [\"top\"], \"unless\": [], \"over\": []}}"
def gPr : Governor := ⟨"gPr", "u0166.s01", .precedes, .rules ["hc-2", "hc-cyberweapons"], ["u0165.s02", "u0165.s03"]⟩
def depParts : List (String × Json) :=
  ((without "u0165.s03" parts).filter (·.1 != "u0165.s02")) ++
    [("u0165.s02", part "hc-2" "cyberweapon_creation_permitted" "a2"), ("u0166.s01", r9)]
#guard errorOf (sets (setDoc [s03set (cyberPart "cyberweapon_creation_permitted" guardWide)
    (cyberPart "other_permitted" guardNarrow)] depParts) [g1, gPr]) ==
  "ScopeReadings: u0166.s01: differs between choices u0165.s03 scope-u0165-s03@1:wide and u0165.s03 scope-u0165-s03@1:narrow"
-- with one predicate in both readings, r9's `over` is the same under both choices: admitted
#guard (sets (setDoc [s03] depParts) [g1, gPr]).toOption.map (fun o => contentOf o "u0166.s01" |>.compress) ==
  some "{\"norm\":{\"guard\":[\"top\"],\"name\":\"r9\",\"over\":[\"hc-2\",\"hc-cyberweapons\"],\"predicate\":\"cyberweapon_creation_permitted\",\"sign\":true,\"unless\":[]}}"

-- SR-lim: a decoder limit met under one choice is passed on unchanged: UNKNOWN, not a refusal of that choice. The
-- narrow reading's guard is 63 levels deep (it decodes, so its name is found); `gN`'s narrowing makes the composed
-- guard 64 deep, which the graph step's decoding of the composed rule meets
def notN : Nat → Json | 0 => j "[\"top\"]" | n + 1 => .arr #[.str "not", notN n]
#guard errorOf (sets (setDoc [s03set (cyberPart "cyberweapon_creation_permitted" guardWide)
    (cyberPart "cyberweapon_creation_permitted" (notN 63))] depParts) [g1, gN, gPr] hcNames) ==
  "ResourceLimit: formula depth exceeds 64"
#guard errorOf (sets (setDoc [s03set (cyberPart "cyberweapon_creation_permitted" guardWide)
    (cyberPart "cyberweapon_creation_permitted" (notN 62))] depParts) [g1, gN, gPr] hcNames) == "ok"

end VE.Scope.Examples
