import VE.Readings.Wire
import VE.Order.ProfileGate
import VE.Discourse.Loader
import VE.Attribution.Content

/-! Readings that carry their own vocabulary (docs/spec/readings-defaults.md 1.9, 3, 4.1 step 0, 5 rows 6 to 13,
6.6's wire part; plan RD-4a).

A candidate may carry `"companion": {"environment": E, "open_terms": T}`: its content is written over `E`, and its
`meaning_id` is `companionMeaningId`, the existing identity over `E`'s `environment_id`. A set whose readings all
carry a companion is a companion set (`companionSets`; a set that mixes the two is refused). `splitCase` gives the
cases of a document: `main`, the document without its companion sets (their units stay, without content), then one
case per companion set in source order: the companions' environments merged (`mergeCompanions`), and the set's unit,
the set, the narrowings on it and its companions' open terms merged and validated against the merged frame
(`mergeOpenTerms`). A coupling that names a companion set beside another set is refused, so every reading set,
coupling and narrowing lands in exactly one case (`split_keeps_links`).

Declarations are compared by their JSON values (`jeq`, structural, `jeq_sound`), after each companion is brought to
one normal form (`normJ`: every object rebuilt in key order), so two declarations agree exactly when their canonical
bytes do. Lean's own `BEq Json` is compiled code with no definition a proof can unfold: in this section the `contains` of
`split_keeps_links` is read with `jeq`, a local instance. -/
namespace VE.Readings.Wire
open Lean
open Std.DTreeMap.Internal (Impl)

/-! ## Structural equality of JSON values -/

mutual
/-- Two JSON values are the same tree. Sound for `=` (`jeq_sound`) and reflexive (`jeq_refl`); objects with the same
    entries built in another order are different trees, so values are compared in `normJ`'s form. -/
def jeq : Json → Json → Bool
  | .null, .null => true
  | .bool a, .bool b => a == b
  | .num a, .num b => a.mantissa == b.mantissa && a.exponent == b.exponent
  | .str a, .str b => a == b
  | .arr ⟨a⟩, .arr ⟨b⟩ => jeqList a b
  | .obj ⟨⟨a⟩⟩, .obj ⟨⟨b⟩⟩ => jeqImpl a b
  | _, _ => false
def jeqList : List Json → List Json → Bool
  | [], [] => true
  | x :: xs, y :: ys => jeq x y && jeqList xs ys
  | _, _ => false
def jeqImpl : Impl String (fun _ => Json) → Impl String (fun _ => Json) → Bool
  | .leaf, .leaf => true
  | .inner s k v l r, .inner s' k' v' l' r' =>
    s == s' && k == k' && jeq v v' && jeqImpl l l' && jeqImpl r r'
  | _, _ => false
end

mutual
theorem jeq_sound : ∀ (a b : Json), jeq a b = true → a = b
  | .null, .null, _ => rfl
  | .bool a, .bool b, h => by simp only [jeq, beq_iff_eq] at h; rw [h]
  | .num ⟨m, e⟩, .num ⟨m', e'⟩, h => by
    simp only [jeq, Bool.and_eq_true, beq_iff_eq] at h
    obtain ⟨rfl, rfl⟩ := h
    rfl
  | .str a, .str b, h => by simp only [jeq, beq_iff_eq] at h; rw [h]
  | .arr ⟨a⟩, .arr ⟨b⟩, h => by rw [jeq] at h; rw [jeqList_sound a b h]
  | .obj ⟨⟨a⟩⟩, .obj ⟨⟨b⟩⟩, h => by rw [jeq] at h; rw [jeqImpl_sound a b h]
  | .null, .bool _, h | .null, .num _, h | .null, .str _, h | .null, .arr _, h | .null, .obj _, h
  | .bool _, .null, h | .bool _, .num _, h | .bool _, .str _, h | .bool _, .arr _, h | .bool _, .obj _, h
  | .num _, .null, h | .num _, .bool _, h | .num _, .str _, h | .num _, .arr _, h | .num _, .obj _, h
  | .str _, .null, h | .str _, .bool _, h | .str _, .num _, h | .str _, .arr _, h | .str _, .obj _, h
  | .arr _, .null, h | .arr _, .bool _, h | .arr _, .num _, h | .arr _, .str _, h | .arr _, .obj _, h
  | .obj _, .null, h | .obj _, .bool _, h | .obj _, .num _, h | .obj _, .str _, h | .obj _, .arr _, h => by
    simp [jeq] at h
theorem jeqList_sound : ∀ (a b : List Json), jeqList a b = true → a = b
  | [], [], _ => rfl
  | x :: xs, y :: ys, h => by
    rw [jeqList, Bool.and_eq_true] at h
    rw [jeq_sound x y h.1, jeqList_sound xs ys h.2]
  | [], _ :: _, h | _ :: _, [], h => by simp [jeqList] at h
theorem jeqImpl_sound : ∀ (a b : Impl String (fun _ => Json)), jeqImpl a b = true → a = b
  | .leaf, .leaf, _ => rfl
  | .inner s k v l r, .inner s' k' v' l' r', h => by
    rw [jeqImpl] at h
    simp only [Bool.and_eq_true, beq_iff_eq] at h
    obtain ⟨⟨⟨⟨rfl, rfl⟩, hv⟩, hl⟩, hr⟩ := h
    rw [jeq_sound v v' hv, jeqImpl_sound l l' hl, jeqImpl_sound r r' hr]
  | .leaf, .inner .., h | .inner .., .leaf, h => by simp [jeqImpl] at h
end

mutual
theorem jeq_refl : ∀ (a : Json), jeq a a = true
  | .null => rfl
  | .bool a => by simp [jeq]
  | .num ⟨m, e⟩ => by simp [jeq]
  | .str a => by simp [jeq]
  | .arr ⟨a⟩ => by rw [jeq]; exact jeqList_refl a
  | .obj ⟨⟨a⟩⟩ => by rw [jeq]; exact jeqImpl_refl a
theorem jeqList_refl : ∀ (a : List Json), jeqList a a = true
  | [] => rfl
  | x :: xs => by rw [jeqList, jeq_refl x, jeqList_refl xs]; rfl
theorem jeqImpl_refl : ∀ (a : Impl String (fun _ => Json)), jeqImpl a a = true
  | .leaf => rfl
  | .inner s k v l r => by rw [jeqImpl, jeq_refl v, jeqImpl_refl l, jeqImpl_refl r]; simp
end

theorem jeq_iff (a b : Json) : jeq a b = true ↔ a = b :=
  ⟨jeq_sound a b, fun h => h ▸ jeq_refl a⟩

/-! ## One normal form: every object rebuilt by inserting its entries in key order -/

mutual
/-- `j` with every object rebuilt from its entries in key order, so that values with the same entries are the same
    tree (`jeq` then decides their canonical bytes' equality). -/
def normJ : Json → Json
  | .arr ⟨a⟩ => .arr ⟨normList a⟩
  | .obj ⟨⟨t⟩⟩ => Json.mkObj (normImpl t)
  | j => j
def normList : List Json → List Json
  | [] => []
  | x :: xs => normJ x :: normList xs
def normImpl : Impl String (fun _ => Json) → List (String × Json)
  | .leaf => []
  | .inner _ k v l r => normImpl l ++ [(k, normJ v)] ++ normImpl r
end

section Companions
open Lean
/-- The array at `k`, `[]` when absent. -/
def arr (j : Json) (k : String) : List Json :=
  match j.getObjValD k with
  | .arr xs => xs.toList
  | _ => []

/-! ## Reading the document -/

/-- The entries of a JSON object, in its tree's order; none for another value. -/
def entries : Json → List (String × Json)
  | .obj kvs => kvs.toList
  | _ => []

def strOf : Json → String
  | .str s => s
  | _ => ""

/-- A set's id as written (`""` when it has none: such a set is refused by the decoder of its case). -/
def setIdOf (s : Json) : String := strOf (s.getObjValD "id")

/-- A reading carries its own vocabulary. -/
def carries (r : Json) : Bool :=
  match r.getObjVal? "companion" with
  | .ok _ => true
  | .error _ => false

/-- The strings of `l`, each at its first occurrence. -/
def firstStrs : List String → List String
  | [] => []
  | s :: rest => s :: (firstStrs rest).filter (· != s)

/-- The entries of `l`, each key at its first occurrence. -/
def firstKeys : List (String × Json) → List (String × Json)
  | [] => []
  | e :: rest => e :: (firstKeys rest).filter (·.1 != e.1)

def mixedText (s : String) : String :=
  s!"InvalidInput: reading set {s} mixes readings with and without their own vocabulary"

/-- Along the set ids `ids`, those whose readings (over every version written) all carry a companion; the first set
    that mixes the two is refused (5 row 6). -/
def companionIds (sets : List Json) : List String → Except String (List String)
  | [] => pure []
  | s :: rest =>
    let readings := (sets.filter (setIdOf · == s)).flatMap (arr · "readings")
    if readings.any carries && !readings.all carries then throw (mixedText s)
    else do
      let tail ← companionIds sets rest
      pure (if readings.any carries then s :: tail else tail)

/-! ## Merging the companions of one set -/

/-- `<set>` of a source named `<set>@<v>:<i>`. -/
def setOfSource (name : String) : String := (name.splitOn "@").headD name

/-- One declaration of one source added to the merge so far, `(name, source, declaration)`: a repeated name only with
    the same declaration (5 row 10). -/
def addDecl (acc : List (String × String × Json)) (src : String) (e : String × Json) :
    Except String (List (String × String × Json)) :=
  match acc.find? (·.1 == e.1) with
  | some (_, src0, d0) =>
    if jeq d0 e.2 then pure acc else throw s!"InvalidInput: readings {src0} and {src} declare {e.1} differently"
  | none => pure (acc ++ [(e.1, src, e.2)])

def addDecls (src : String) : List (String × String × Json) → List (String × Json) →
    Except String (List (String × String × Json))
  | acc, [] => pure acc
  | acc, e :: es => do addDecls src (← addDecl acc src e) es

/-- The declarations of category `k` (`sorts`, `constants` or `predicates`) united by name in reading order. -/
def mergeCategory (k : String) : List (String × String × Json) → List (String × Json) →
    Except String (List (String × String × Json))
  | acc, [] => pure acc
  | acc, src :: rest => do
    mergeCategory k (← addDecls src.1 acc (entries ((src.2.getObjValD "vocabulary").getObjValD k))) rest

def categories : List String := ["sorts", "constants", "predicates"]

/-- Every source agrees with the first on `key` (5 row 9, and every other key of the environment). -/
def sameOn (set : String) (first : Json) (sources : List (String × Json)) (read : Json → Json) (key : String) :
    Except String Unit := do
  for src in sources do
    unless jeq (read src.2) (read first) do throw s!"InvalidInput: the readings of {set} declare different {key}"

/-- The keys written by any source, other than `skip`, in key order. -/
def otherKeys (skip : List String) (objs : List Json) : List String :=
  VE.Route.sortStrings (firstStrs ((objs.flatMap (fun o => (entries o).map (·.1))).filter (!skip.contains ·)))

/-- `readings@1` added to a profile list (sorted, as the decoders require). -/
def withReadings (profiles : Json) : Json :=
  match VE.Bridge.strings profiles with
  | .ok ps => toJson (VE.Route.sortStrings (if ps.contains readingsProfile then ps else ps ++ [readingsProfile]))
  | .error _ => profiles

def objOf (decls : List (String × String × Json)) : Json := Json.mkObj (decls.map (fun x => (x.1, x.2.2)))

/-- `base` with the entries `ks` in place of its keys of the same names (each other key at its first occurrence). -/
def overlay (base : Json) (ks : List (String × Json)) : Json :=
  Json.mkObj (firstKeys ((entries base).filter (fun e => !(ks.map (·.1)).contains e.1)) ++ ks)

/-- The first source's environment with the merged declarations and `readings@1` added. -/
def mergedJson (e : Json) (sorts constants predicates : List (String × String × Json)) : Json :=
  overlay e [("profiles", withReadings (e.getObjValD "profiles")),
    ("vocabulary", overlay (e.getObjValD "vocabulary")
      [("constants", objOf constants), ("predicates", objOf predicates), ("sorts", objOf sorts)])]

/-- 5 row 9: every source's language, revision and profiles are the first's, and so is every other key of the
    environment and of its vocabulary but the three categories. -/
def sameText (first : String × Json) (sources : List (String × Json)) : Except String Unit := do
  let set := setOfSource first.1
  let envs := sources.map (·.2)
  for key in ["language", "spec_revision", "profiles"] ++
      otherKeys ["language", "spec_revision", "profiles", "vocabulary"] envs do
    sameOn set first.2 sources (·.getObjValD key) key
  for key in otherKeys categories (envs.map (·.getObjValD "vocabulary")) do
    sameOn set first.2 sources (fun e => (e.getObjValD "vocabulary").getObjValD key) key

/-- The merged environment of a set's companions (1.9). `sources` names each environment `<set>@<v>:<i>`. -/
def mergeCompanions (sources : List (String × Json)) : Except String Json := do
  let some first := sources.head? | throw invalidSet
  sameText first sources
  let sorts ← mergeCategory "sorts" [] sources
  let constants ← mergeCategory "constants" [] sources
  let predicates ← mergeCategory "predicates" [] sources
  pure (mergedJson first.2 sorts constants predicates)

def nameText (t : Json) : String :=
  match t.getObjValD "name" with
  | .str s => s
  | j => j.compress

/-- One open term of one source added to the merge so far, `(source, term)`: a repeated name only with the same
    entry (5 row 11). -/
def addTerm (acc : List (String × Json)) (src : String) (t : Json) : Except String (List (String × Json)) :=
  match acc.find? (fun x => jeq (x.2.getObjValD "name") (t.getObjValD "name")) with
  | some (src0, t0) =>
    if jeq t0 t then pure acc
    else throw s!"InvalidInput: readings {src0} and {src} declare open term {nameText t} differently"
  | none => pure (acc ++ [(src, t)])

def addTerms (src : String) : List (String × Json) → List Json → Except String (List (String × Json))
  | acc, [] => pure acc
  | acc, t :: ts => do addTerms src (← addTerm acc src t) ts

def mergeTerms : List (String × Json) → List (String × Json) → Except String (List (String × Json))
  | acc, [] => pure acc
  | acc, src :: rest => do mergeTerms (← addTerms src.1 acc (arr src.2 "open_terms")) rest

/-- The merged open terms of a set's companions (1.9, E4), each validated against the merged environment. -/
def mergeOpenTerms (sources : List (String × Json)) : Except String (List Json) := do
  let m ← mergeCompanions (sources.map (fun s => (s.1, s.2.getObjValD "environment")))
  let ts := (← mergeTerms [] sources).map (·.2)
  -- The merged frame through the frozen decoders (5 row 12), then each term's conditions typed in it (E4).
  let re ← decodeEnvironment m
  let _ ← VE.Discourse.Loader.openTermNames re.se.ne.rv (Json.arr ts.toArray) (python := true)
  pure ts

/-- The companion sets of a document: those whose every reading carries `companion`; a set mixing the two is
    refused (1.9). -/
def companionSets (document : Json) : Except String (List String) :=
  let sets := arr document "reading_sets"
  companionIds sets (firstStrs (sets.map setIdOf))

def softOrRights (companion : Json) : Bool :=
  match VE.Bridge.strings ((companion.getObjValD "environment").getObjValD "profiles") with
  | .ok ps => ps.contains "soft-norms@0" || ps.contains "rights@0"
  | .error _ => false

/-- A reading's identity over its own environment (3). -/
def companionMeaningId (companion content : Json) : Except String String := do
  let environment := companion.getObjValD "environment"
  let profiles ← VE.Bridge.strings (← environment.getObjVal? "profiles")
  -- The content's canonical AST: a formula's, or the W1 rule's (`rule.to_dict()`'s form, `encodeNode`).
  let ast ← match content with
    | .arr _ => pure (VE.Route.Wire.encodeFormula (← VE.Bridge.decodeFormula 64 content))
    | _ => pure (VE.Reports.encodeNode (← VE.Norms.Wire.decodeNorm (Json.mkObj [("norm", content.getObjValD "norm")])))
  VE.Route.Wire.meaningId profiles (← VE.Route.Wire.environmentId profiles environment) ast

def unsupportedCompanion : String :=
  "UnsupportedProfile: readings with their own vocabulary on the soft or rights chain are not implemented"

/-- The written versions of set `s`. -/
def setEntries (document : Json) (s : String) : List Json := (arr document "reading_sets").filter (setIdOf · == s)

/-- The narrowings on set `s`: they travel with it (A3). -/
def narrowingsOn (document : Json) (s : String) : List Json := (arr document "narrowings").filter (fun n => strOf (n.getObjValD "set") == s)

/-- Each reading of set `s` named `<set>@<v>:<i>`, over every version written. -/
def readingsOf (document : Json) (s : String) : List (String × Json) :=
  (setEntries document s).flatMap (fun e =>
    let v := match (e.getObjValD "version").getNat? with
      | .ok n => toString n
      | .error _ => (e.getObjValD "version").compress
    (arr e "readings").zipIdx.map (fun (r, i) => (s!"{s}@{v}:{i}", r)))

/-- The document of set `s`'s case: its unit as written, the units its narrowings cite (by id, without content, so
    that W2's citation check reads them), the set, its narrowings and its merged open terms. -/
def componentDoc (document : Json) (s : String) (ts : List Json) : Json :=
  let unitIds := (setEntries document s).map (fun e => strOf (e.getObjValD "unit"))
  let cited := (narrowingsOn document s).flatMap (fun n => (arr n "reason_spans").map strOf)
  let units := (arr document "units").filterMap (fun u =>
    let id := strOf (u.getObjValD "id")
    if unitIds.contains id then some u else if cited.contains id then some (Json.mkObj [("id", .str id)]) else none)
  Json.mkObj [("narrowings", .arr (narrowingsOn document s).toArray), ("open_terms", .arr ts.toArray),
    ("reading_sets", .arr (setEntries document s).toArray), ("units", .arr units.toArray)]

/-- 5 row 8: no companion on the soft or rights chain (D2). -/
def profileCheck (sources : List (String × Json)) : Except String Unit :=
  if sources.any (fun x => softOrRights (x.2.getObjValD "companion")) then throw unsupportedCompanion else pure ()

/-- 5 row 13: each reading with content records its `companionMeaningId`. -/
def meaningCheck (sources : List (String × Json)) : Except String Unit := do
  for x in sources do
    let content := x.2.getObjValD "content"
    unless content matches .null do
      let mid ← companionMeaningId (x.2.getObjValD "companion") content
      unless jeq (x.2.getObjValD "meaning_id") (.str mid) do throw "reading meaning id does not match content"

/-- The case of companion set `s` (5 rows 8 to 13, in order): its environment and its document. -/
def componentOf (document : Json) (s : String) : Except String (String × Json × Json) := do
  let sources := readingsOf document s
  profileCheck sources
  let companions := sources.map (fun x => (x.1, normJ (x.2.getObjValD "companion")))
  let m ← mergeCompanions (companions.map (fun c => (c.1, c.2.getObjValD "environment")))
  let ts ← mergeOpenTerms companions
  meaningCheck sources
  pure (s, m, componentDoc document s ts)

def componentsOf (document : Json) : List String → Except String (List (String × Json × Json))
  | [] => pure []
  | s :: rest => do
    let p ← componentOf document s
    pure (p :: (← componentsOf document rest))

/-- A unit of a companion set stays in the main case without its content. -/
def withoutContent (u : Json) : Json := Json.mkObj ((entries u).filter (·.1 != "content"))

/-- `base` with the arrays `repl` in place of its keys of the same names. -/
def withArrays (base : Json) (repl : List (String × List Json)) : Json :=
  overlay base (repl.map (fun x => (x.1, Json.arr x.2.toArray)))

/-- The main case's document: without the companion sets `cs` and their narrowings, their units without content. -/
def mainDoc (document : Json) (cs : List String) : Json :=
  let units := (cs.flatMap (setEntries document)).map (fun e => strOf (e.getObjValD "unit"))
  withArrays document [("couplings", arr document "couplings"),
    ("narrowings", (arr document "narrowings").filter (fun n => !cs.contains (strOf (n.getObjValD "set")))),
    ("reading_sets", (arr document "reading_sets").filter (fun s => !cs.contains (setIdOf s))),
    ("units", (arr document "units").map (fun u =>
      if units.contains (strOf (u.getObjValD "id")) then withoutContent u else u))]

/-- 5 row 7: a coupling that names a companion set beside another set. -/
def crossingText (cs : List String) (c : Json) : Option String :=
  let named := (arr c "sets").map (fun r => strOf (r.getObjValD "set"))
  match named.find? cs.contains with
  | some s => (named.find? (· != s)).map (fun s' =>
      s!"InvalidInput: coupling {strOf (c.getObjValD "id")} links {s} and {s'}, which do not share one vocabulary")
  | none => none

/-- The arrays the split rewrites, refused as their decoders refuse them. -/
def shapeText (document : Json) : Option String :=
  if !(document.getObjValD "units" matches .arr _) then some "InvalidInput: document must list units"
  else if !(document.getObjValD "couplings" matches .arr _ | .null) then some "invalid couplings"
  else if !(document.getObjValD "narrowings" matches .arr _ | .null) then some "narrowings must be a list"
  else none

/-- Every case of the split: `main`, then one per companion set in source order, each an environment and a
    document (1.9); refuses a coupling across components (E3, A3). -/
def splitCase (environment document : Json) : Except String (List (String × Json × Json)) := do
  let cs ← companionSets document
  if cs.isEmpty then pure [("main", environment, document)]
  else match shapeText document with
    | some t => throw t
    | none => match (arr document "couplings").findSome? (crossingText cs) with
      | some t => throw t
      | none => do pure (("main", environment, mainDoc document cs) :: (← componentsOf document cs))

/-! ## Lemmas -/

theorem bind_ok {ε α β : Type} {x : Except ε α} {f : α → Except ε β} {b : β}
    (h : (x >>= f) = .ok b) : ∃ a, x = .ok a ∧ f a = .ok b := by
  cases x with
  | error e => cases h
  | ok a => exact ⟨a, rfl, h⟩

theorem getObjValD_ok {j v : Json} {k : String} (h : j.getObjVal? k = .ok v) : j.getObjValD k = v := by
  simp [Json.getObjValD, h]
  rfl

theorem entries_mem {j d : Json} {n : String} (h : j.getObjVal? n = .ok d) : (n, d) ∈ entries j := by
  cases j with
  | obj kvs =>
    simp only [Json.getObjVal?] at h
    split at h
    · rename_i w hw
      cases h
      exact VE.Order.ProfileGate.impl_get_mem (t := kvs.inner.inner) hw
    · cases h
  | _ => simp [Json.getObjVal?] at h <;> cases h

theorem mkObj_get {l : List (String × Json)} {k : String} {v : Json} (hd : (l.map (·.1)).Nodup)
    (hm : (k, v) ∈ l) : (Json.mkObj l).getObjVal? k = .ok v := by
  have hp : l.Pairwise (fun a b => ¬ compare a.1 b.1 = .eq) := by
    have := List.pairwise_map.mp hd
    exact this.imp (fun hne heq => hne (Std.LawfulEqOrd.eq_of_compare heq))
  have := Std.TreeMap.Raw.getElem?_ofList_of_mem (cmp := compare) (k_eq := Std.ReflCmp.compare_self) hp hm
  simp only [Json.mkObj, Json.getObjVal?, Std.TreeMap.Raw.get?_eq_getElem?, this]
  rfl

theorem firstKeys_sub : ∀ (l : List (String × Json)), ∀ x ∈ firstKeys l, x ∈ l
  | [], _, h => by simp [firstKeys] at h
  | e :: rest, x, h => by
    simp only [firstKeys, List.mem_cons, List.mem_filter] at h
    rcases h with rfl | ⟨h, _⟩
    · exact List.mem_cons_self
    · exact List.mem_cons_of_mem _ (firstKeys_sub rest x h)

theorem firstKeys_nodup : ∀ (l : List (String × Json)), ((firstKeys l).map (·.1)).Nodup
  | [] => by simp [firstKeys]
  | e :: rest => by
    simp only [firstKeys, List.map_cons, List.nodup_cons]
    refine ⟨?_, ?_⟩
    · intro hm
      obtain ⟨x, hx, hxe⟩ := List.mem_map.mp hm
      simp only [List.mem_filter, bne_iff_ne, ne_eq] at hx
      exact hx.2 hxe
    · have := firstKeys_nodup rest
      exact (List.Nodup.sublist (List.Sublist.map _ List.filter_sublist) this)


/-- A merge so far: its names distinct. -/
def Distinct (acc : List (String × String × Json)) : Prop := (acc.map (·.1)).Nodup

theorem addDecl_spec {acc acc' : List (String × String × Json)} {src : String} {e : String × Json}
    (h : addDecl acc src e = .ok acc') (hd : Distinct acc) :
    Distinct acc' ∧ (∀ x ∈ acc, x ∈ acc') ∧ ∃ s, (e.1, s, e.2) ∈ acc' := by
  unfold addDecl at h
  split at h
  · rename_i n0 src0 d0 hf
    split at h
    · rename_i hj
      cases h
      have hm := List.mem_of_find?_eq_some hf
      have hn := List.find?_some hf
      simp only [beq_iff_eq] at hn
      subst hn
      rw [jeq_sound _ _ hj] at hm
      exact ⟨hd, fun _ hx => hx, _, hm⟩
    · cases h
  · rename_i hf
    cases h
    refine ⟨?_, fun x hx => List.mem_append_left _ hx, src, List.mem_append_right _ (List.mem_singleton_self _)⟩
    unfold Distinct
    rw [List.map_append, List.nodup_append]
    refine ⟨hd, by simp, ?_⟩
    intro a ha b hb hab
    simp only [List.map_cons, List.map_nil, List.mem_singleton] at hb
    obtain ⟨x, hx, hxa⟩ := List.mem_map.mp ha
    have := List.find?_eq_none.mp hf x hx
    simp only [beq_iff_eq] at this
    exact this (hxa.trans (hab.trans hb))

theorem addDecls_spec (src : String) : ∀ (acc acc' : List (String × String × Json)) (es : List (String × Json)),
    addDecls src acc es = .ok acc' → Distinct acc →
      Distinct acc' ∧ (∀ x ∈ acc, x ∈ acc') ∧ ∀ e ∈ es, ∃ s, (e.1, s, e.2) ∈ acc'
  | acc, acc', [], h, hd => by
    cases h
    exact ⟨hd, fun _ hx => hx, by simp⟩
  | acc, acc', e :: es, h, hd => by
    simp only [addDecls, bind, Except.bind] at h
    split at h
    · cases h
    · rename_i a ha
      obtain ⟨hd1, hs1, s1, hm1⟩ := addDecl_spec ha hd
      obtain ⟨hd2, hs2, hc2⟩ := addDecls_spec src a acc' es h hd1
      refine ⟨hd2, fun x hx => hs2 x (hs1 x hx), ?_⟩
      intro e' he'
      rcases List.mem_cons.mp he' with rfl | he'
      · exact ⟨s1, hs2 _ hm1⟩
      · exact hc2 e' he'

theorem addDecl_mono {acc acc' : List (String × String × Json)} {src : String} {e : String × Json}
    (h : addDecl acc src e = .ok acc') : ∀ x ∈ acc, x ∈ acc' := by
  unfold addDecl at h
  split at h
  · split at h
    · cases h; exact fun _ hx => hx
    · cases h
  · cases h; exact fun x hx => List.mem_append_left _ hx

theorem addDecls_mono (src : String) : ∀ (acc acc' : List (String × String × Json)) (es : List (String × Json)),
    addDecls src acc es = .ok acc' → ∀ x ∈ acc, x ∈ acc'
  | acc, acc', [], h => by cases h; exact fun _ hx => hx
  | acc, acc', e :: es, h => by
    simp only [addDecls, bind, Except.bind] at h
    split at h
    · cases h
    · rename_i a ha
      exact fun x hx => addDecls_mono src a acc' es h x (addDecl_mono ha x hx)

theorem mergeCategory_mono (k : String) : ∀ (acc acc' : List (String × String × Json)) (sources : List (String × Json)),
    mergeCategory k acc sources = .ok acc' → ∀ x ∈ acc, x ∈ acc'
  | acc, acc', [], h => by cases h; exact fun _ hx => hx
  | acc, acc', src :: rest, h => by
    simp only [mergeCategory, bind, Except.bind] at h
    split at h
    · cases h
    · rename_i a ha
      intro x hx
      exact mergeCategory_mono k a acc' rest h x (addDecls_mono src.1 acc a _ ha x hx)

theorem mergeCategory_spec (k : String) : ∀ (acc acc' : List (String × String × Json)) (sources : List (String × Json)),
    mergeCategory k acc sources = .ok acc' → Distinct acc →
      Distinct acc' ∧ ∀ src ∈ sources, ∀ e ∈ entries ((src.2.getObjValD "vocabulary").getObjValD k),
        ∃ s, (e.1, s, e.2) ∈ acc'
  | acc, acc', [], h, hd => by
    cases h
    exact ⟨hd, by simp⟩
  | acc, acc', src :: rest, h, hd => by
    simp only [mergeCategory, bind, Except.bind] at h
    split at h
    · cases h
    · rename_i a ha
      obtain ⟨hd1, hs1, hc1⟩ := addDecls_spec src.1 acc a _ ha hd
      have ⟨hd2, hc2⟩ := mergeCategory_spec k a acc' rest h hd1
      -- what `rest` adds keeps every entry of `a`
      have hkeep := mergeCategory_mono k a acc' rest h
      refine ⟨hd2, fun src' hsrc e he => ?_⟩
      rcases List.mem_cons.mp hsrc with rfl | hsrc
      · obtain ⟨s, hm⟩ := hc1 e he
        exact ⟨s, hkeep _ hm⟩
      · exact hc2 src' hsrc e he

theorem overlay_get {base : Json} {ks : List (String × Json)} {k : String} {v : Json} (hks : (ks.map (·.1)).Nodup)
    (hm : (k, v) ∈ ks) : (overlay base ks).getObjVal? k = .ok v := by
  apply mkObj_get _ (List.mem_append_right _ hm)
  rw [List.map_append, List.nodup_append]
  refine ⟨firstKeys_nodup _, hks, ?_⟩
  intro a ha b hb hab
  obtain ⟨x, hx, rfl⟩ := List.mem_map.mp ha
  have := (List.mem_filter.mp (firstKeys_sub _ x hx)).2
  simp only [Bool.not_eq_true'] at this
  have hin : (List.map (fun x => x.fst) ks).contains x.fst = true := List.contains_iff_mem.mpr (hab ▸ hb)
  rw [this] at hin
  cases hin

theorem objOf_get {acc : List (String × String × Json)} {n src : String} {d : Json} (hm : (n, src, d) ∈ acc)
    (hd : Distinct acc) : (objOf acc).getObjVal? n = .ok d := by
  apply mkObj_get _ (List.mem_map.mpr ⟨_, hm, rfl⟩)
  simpa [List.map_map, Distinct] using hd

theorem mergeCompanions_ok {sources : List (String × Json)} {m : Json} (h : mergeCompanions sources = .ok m) :
    ∃ first sorts constants predicates, mergeCategory "sorts" [] sources = .ok sorts ∧
      mergeCategory "constants" [] sources = .ok constants ∧ mergeCategory "predicates" [] sources = .ok predicates ∧
      m = mergedJson first sorts constants predicates := by
  unfold mergeCompanions at h
  split at h
  · obtain ⟨_, _, h⟩ := bind_ok h
    obtain ⟨s, hs, h⟩ := bind_ok h
    obtain ⟨c, hc, h⟩ := bind_ok h
    obtain ⟨p, hp, h⟩ := bind_ok h
    cases h
    exact ⟨_, s, c, p, hs, hc, hp, rfl⟩
  · cases h

theorem mergedJson_category (e : Json) (s c p : List (String × String × Json)) (k : String)
    (hk : k ∈ ["sorts", "constants", "predicates"]) :
    ((mergedJson e s c p).getObjValD "vocabulary").getObjValD k =
      objOf (if k = "sorts" then s else if k = "constants" then c else p) := by
  unfold mergedJson
  rw [getObjValD_ok (overlay_get (by simp) (List.mem_cons_of_mem _ (List.mem_singleton_self _)))]
  simp only [List.mem_cons, List.mem_nil_iff, or_false] at hk
  rcases hk with rfl | rfl | rfl <;> simp only [reduceIte, String.reduceEq] <;>
    exact getObjValD_ok (overlay_get (by simp) (by simp))

theorem mergeCompanions_extends (sources : List (String × Json)) (m : Json) (h : mergeCompanions sources = .ok m) :
  ∀ src ∈ sources, ∀ k ∈ ["sorts", "constants", "predicates"], ∀ (n : String) (d : Json),
    ((src.2.getObjValD "vocabulary").getObjValD k).getObjVal? n = .ok d →
      ((m.getObjValD "vocabulary").getObjValD k).getObjVal? n = .ok d := by
  obtain ⟨first, s, c, p, hs, hc, hp, rfl⟩ := mergeCompanions_ok h
  intro src hsrc k hk n d hd
  rw [mergedJson_category _ _ _ _ k hk]
  have cover : ∀ acc, mergeCategory k [] sources = .ok acc → (objOf acc).getObjVal? n = .ok d := fun acc ha => by
    obtain ⟨hdist, hcov⟩ := mergeCategory_spec k [] acc sources ha (by simp [Distinct])
    obtain ⟨_, hm⟩ := hcov src hsrc (n, d) (entries_mem hd)
    exact objOf_get hm hdist
  simp only [List.mem_cons, List.mem_nil_iff, or_false] at hk
  rcases hk with rfl | rfl | rfl <;> simp only [reduceIte, String.reduceEq] <;> exact cover _ ‹_›

theorem mergeCompanions_identical (sources : List (String × Json)) (m : Json) (h : mergeCompanions sources = .ok m) :
  ∀ src ∈ sources, ∀ src' ∈ sources, ∀ k ∈ ["sorts", "constants", "predicates"], ∀ (n : String) (d d' : Json),
    ((src.2.getObjValD "vocabulary").getObjValD k).getObjVal? n = .ok d →
      ((src'.2.getObjValD "vocabulary").getObjValD k).getObjVal? n = .ok d' → d = d' := by
  intro src hsrc src' hsrc' k hk n d d' hd hd'
  have h1 := mergeCompanions_extends sources m h src hsrc k hk n d hd
  rw [mergeCompanions_extends sources m h src' hsrc' k hk n d' hd'] at h1
  cases h1
  rfl

/-- The open terms merged so far have pairwise different names. -/
def TermsDistinct (acc : List (String × Json)) : Prop :=
  (acc.map (·.2)).Pairwise (fun a b => jeq (a.getObjValD "name") (b.getObjValD "name") = false)

theorem addTerm_spec {acc acc' : List (String × Json)} {src : String} {t : Json} (h : addTerm acc src t = .ok acc')
    (hd : TermsDistinct acc) : TermsDistinct acc' ∧ (∀ x ∈ acc, x ∈ acc') ∧ t ∈ acc'.map (·.2) := by
  unfold addTerm at h
  split at h
  · rename_i src0 t0 hf
    split at h
    · rename_i hj
      cases h
      have hm := List.mem_of_find?_eq_some hf
      rw [jeq_sound _ _ hj] at hm
      exact ⟨hd, fun _ hx => hx, List.mem_map.mpr ⟨_, hm, rfl⟩⟩
    · cases h
  · rename_i hf
    cases h
    refine ⟨?_, fun x hx => List.mem_append_left _ hx, by simp⟩
    unfold TermsDistinct
    rw [List.map_append, List.pairwise_append]
    refine ⟨hd, by simp, ?_⟩
    intro a ha b hb
    simp only [List.map_cons, List.map_nil, List.mem_singleton] at hb
    subst hb
    obtain ⟨x, hx, rfl⟩ := List.mem_map.mp ha
    have := List.find?_eq_none.mp hf x hx
    simpa using this

theorem addTerms_spec (src : String) : ∀ (acc acc' : List (String × Json)) (ts : List Json),
    addTerms src acc ts = .ok acc' → TermsDistinct acc →
      TermsDistinct acc' ∧ (∀ x ∈ acc, x ∈ acc') ∧ ∀ t ∈ ts, t ∈ acc'.map (·.2)
  | acc, acc', [], h, hd => by
    cases h
    exact ⟨hd, fun _ hx => hx, by simp⟩
  | acc, acc', t :: ts, h, hd => by
    simp only [addTerms, bind, Except.bind] at h
    split at h
    · cases h
    · rename_i a ha
      obtain ⟨hd1, hs1, hm1⟩ := addTerm_spec ha hd
      obtain ⟨hd2, hs2, hc2⟩ := addTerms_spec src a acc' ts h hd1
      refine ⟨hd2, fun x hx => hs2 x (hs1 x hx), ?_⟩
      intro t' ht'
      rcases List.mem_cons.mp ht' with rfl | ht'
      · obtain ⟨y, hy, hyt⟩ := List.mem_map.mp hm1
        exact List.mem_map.mpr ⟨y, hs2 y hy, hyt⟩
      · exact hc2 t' ht'

theorem mergeTerms_spec : ∀ (acc acc' : List (String × Json)) (sources : List (String × Json)),
    mergeTerms acc sources = .ok acc' → TermsDistinct acc →
      TermsDistinct acc' ∧ (∀ x ∈ acc, x ∈ acc') ∧ ∀ src ∈ sources, ∀ t ∈ arr src.2 "open_terms", t ∈ acc'.map (·.2)
  | acc, acc', [], h, hd => by
    cases h
    exact ⟨hd, fun _ hx => hx, by simp⟩
  | acc, acc', src :: rest, h, hd => by
    simp only [mergeTerms, bind, Except.bind] at h
    split at h
    · cases h
    · rename_i a ha
      obtain ⟨hd1, hs1, hc1⟩ := addTerms_spec src.1 acc a _ ha hd
      obtain ⟨hd2, hs2, hc2⟩ := mergeTerms_spec a acc' rest h hd1
      refine ⟨hd2, fun x hx => hs2 x (hs1 x hx), fun src' hsrc t ht => ?_⟩
      rcases List.mem_cons.mp hsrc with rfl | hsrc
      · obtain ⟨y, hy, hyt⟩ := List.mem_map.mp (hc1 t ht)
        exact List.mem_map.mpr ⟨y, hs2 y hy, hyt⟩
      · exact hc2 src' hsrc t ht

/-- In a list of pairwise differently named terms, two terms of one name are one term. -/
theorem same_name {l : List Json}
    (hp : l.Pairwise (fun a b => jeq (a.getObjValD "name") (b.getObjValD "name") = false)) :
    ∀ t ∈ l, ∀ t' ∈ l, t.getObjValD "name" = t'.getObjValD "name" → t = t' := by
  induction l with
  | nil => simp
  | cons x xs ih =>
    rw [List.pairwise_cons] at hp
    intro t ht t' ht' hn
    rcases List.mem_cons.mp ht with h1 | h1 <;> rcases List.mem_cons.mp ht' with h2 | h2
    · exact h1.trans h2.symm
    · subst h1
      have := hp.1 t' h2
      rw [hn, jeq_refl] at this
      cases this
    · subst h2
      have := hp.1 t h1
      rw [← hn, jeq_refl] at this
      cases this
    · exact ih hp.2 t h1 t' h2 hn

theorem mergeOpenTerms_ok {sources : List (String × Json)} {ts : List Json} (h : mergeOpenTerms sources = .ok ts) :
    ∃ acc, mergeTerms [] sources = .ok acc ∧ ts = acc.map (·.2) := by
  unfold mergeOpenTerms at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨acc, hacc, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  cases h
  exact ⟨acc, hacc, rfl⟩

theorem mergeOpenTerms_identical (sources : List (String × Json)) (ts : List Json)
    (h : mergeOpenTerms sources = .ok ts) :
  (∀ src ∈ sources, ∀ t ∈ arr src.2 "open_terms", t ∈ ts) ∧
  ∀ t ∈ ts, ∀ t' ∈ ts, t.getObjValD "name" = t'.getObjValD "name" → t = t' := by
  obtain ⟨acc, hacc, rfl⟩ := mergeOpenTerms_ok h
  obtain ⟨hd, _, hc⟩ := mergeTerms_spec [] acc sources hacc (by simp [TermsDistinct])
  exact ⟨hc, same_name hd⟩

/-! ### The split -/

theorem mkObj_absent {l : List (String × Json)} {k : String} (h : (l.map (·.1)).contains k = false) :
    (Json.mkObj l).getObjValD k = .null := by
  have := Std.TreeMap.Raw.getElem?_ofList_of_contains_eq_false (cmp := compare) h
  simp only [Json.mkObj, Json.getObjValD, Json.getObjVal?, Std.TreeMap.Raw.get?_eq_getElem?, this]
  rfl

theorem arr_of_get {j : Json} {k : String} {l : List Json} (h : j.getObjVal? k = .ok (Json.arr l.toArray)) :
    arr j k = l := by
  simp [arr, getObjValD_ok h]

theorem withArrays_arr {base : Json} {repl : List (String × List Json)} {k : String} {l : List Json}
    (hd : (repl.map (·.1)).Nodup) (hm : (k, l) ∈ repl) : arr (withArrays base repl) k = l := by
  apply arr_of_get
  apply overlay_get
  · simpa [List.map_map] using hd
  · exact List.mem_map.mpr ⟨(k, l), hm, rfl⟩

theorem mainDoc_arr (document : Json) (cs : List String) :
    arr (mainDoc document cs) "couplings" = arr document "couplings" ∧
    arr (mainDoc document cs) "narrowings" =
      (arr document "narrowings").filter (fun n => !cs.contains (strOf (n.getObjValD "set"))) ∧
    arr (mainDoc document cs) "reading_sets" = (arr document "reading_sets").filter (fun s => !cs.contains (setIdOf s)) := by
  refine ⟨?_, ?_, ?_⟩ <;> (unfold mainDoc; apply withArrays_arr (by simp) (by simp))

theorem componentDoc_arr (document : Json) (s : String) (ts : List Json) :
    arr (componentDoc document s ts) "couplings" = [] ∧
    arr (componentDoc document s ts) "narrowings" = narrowingsOn document s ∧
    arr (componentDoc document s ts) "reading_sets" = setEntries document s := by
  refine ⟨?_, ?_, ?_⟩
  · unfold componentDoc arr
    rw [mkObj_absent]
    simp
  · unfold componentDoc; exact arr_of_get (mkObj_get (by simp) (by simp))
  · unfold componentDoc; exact arr_of_get (mkObj_get (by simp) (by simp))

theorem componentOf_doc {document : Json} {s : String} {p : String × Json × Json} (h : componentOf document s = .ok p) :
    p.1 = s ∧ ∃ ts, p.2.2 = componentDoc document s ts := by
  unfold componentOf at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨ts, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  cases h
  exact ⟨rfl, ts, rfl⟩

theorem componentsOf_docs (document : Json) : ∀ (cs : List String) (comps : List (String × Json × Json)),
    componentsOf document cs = .ok comps →
      comps.map (·.1) = cs ∧ ∀ p ∈ comps, ∃ ts, p.2.2 = componentDoc document p.1 ts
  | [], comps, h => by cases h; simp
  | s :: rest, comps, h => by
    simp only [componentsOf, bind, Except.bind] at h
    split at h
    · cases h
    · rename_i p hp
      split at h
      · cases h
      · rename_i ps hps
        cases h
        obtain ⟨h1, ts, h2⟩ := componentOf_doc hp
        obtain ⟨h3, h4⟩ := componentsOf_docs document rest ps hps
        refine ⟨by simp [h1, h3], fun q hq => ?_⟩
        rcases List.mem_cons.mp hq with rfl | hq
        · exact ⟨ts, h1 ▸ h2⟩
        · exact h4 q hq

theorem firstStrs_nodup : ∀ (l : List String), (firstStrs l).Nodup
  | [] => List.nodup_nil
  | s :: rest => by
    simp only [firstStrs, List.nodup_cons, List.mem_filter, bne_self_eq_false]
    exact ⟨by simp, (firstStrs_nodup rest).sublist List.filter_sublist⟩

theorem companionIds_sublist (sets : List Json) : ∀ (ids cs : List String), companionIds sets ids = .ok cs → cs.Sublist ids
  | [], cs, h => by cases h; exact List.Sublist.slnil
  | s :: rest, cs, h => by
    simp only [companionIds] at h
    split at h
    · cases h
    · obtain ⟨tail, ht, h⟩ := bind_ok h
      cases h
      have := companionIds_sublist sets rest tail ht
      split
      · exact this.cons₂ s
      · exact this.cons s

theorem companionSets_nodup {document : Json} {cs : List String} (h : companionSets document = .ok cs) : cs.Nodup :=
  (firstStrs_nodup _).sublist (companionIds_sublist _ _ _ h)

theorem splitCase_parts {environment document : Json} {parts : List (String × Json × Json)}
    (h : splitCase environment document = .ok parts) :
    parts = [("main", environment, document)] ∨
      ∃ cs comps, companionSets document = .ok cs ∧ componentsOf document cs = .ok comps ∧
        parts = ("main", environment, mainDoc document cs) :: comps := by
  unfold splitCase at h
  obtain ⟨cs, hcs, h⟩ := bind_ok h
  split at h
  · cases h; exact Or.inl rfl
  · split at h
    · cases h
    · split at h
      · cases h
      · obtain ⟨comps, hc, h⟩ := bind_ok h
        cases h
        exact Or.inr ⟨cs, comps, hcs, hc, rfl⟩

/-- In this section a JSON value is found in a list by `jeq`: Lean's own `BEq Json` is compiled code with no definition a proof can unfold, so nothing can be
    proved of it. `split_keeps_links` reads `contains` with this instance. -/
local instance : BEq Json := ⟨jeq⟩

example : (inferInstance : BEq Json).beq = jeq := rfl

theorem jcontains_iff (l : List Json) (x : Json) : l.contains x = true ↔ x ∈ l := by
  rw [List.contains_iff_exists_mem_beq]
  exact ⟨fun ⟨y, hy, hxy⟩ => (jeq_sound x y hxy) ▸ hy, fun hx => ⟨x, hx, jeq_refl x⟩⟩

/-- An item `x` of `l` is in the main case when its set is not a companion set, else in that set's case. -/
theorem count_one (l : List Json) (f : Json → String) (cs : List String) (hcs : cs.Nodup) (k : String)
    (main : String × Json × Json) (comps : List (String × Json × Json))
    (hm : arr main.2.2 k = l.filter (fun y => !cs.contains (f y)))
    (hc : ∀ p ∈ comps, arr p.2.2 k = l.filter (fun y => f y == p.1)) (hn : comps.map (·.1) = cs) :
    ∀ x ∈ l, ((main :: comps).filter (fun p => (arr p.2.2 k).contains x)).length = 1 := by
  intro x hx
  have hcomps : comps.filter (fun p => (arr p.2.2 k).contains x) = comps.filter (fun p => f x == p.1) := by
    apply List.filter_congr
    intro p hp
    rw [hc p hp]
    apply Bool.eq_iff_iff.mpr
    rw [jcontains_iff, List.mem_filter]
    exact ⟨fun h => h.2, fun h => ⟨hx, h⟩⟩
  have hlen : (comps.filter (fun p => f x == p.1)).length = cs.count (f x) := by
    rw [← List.countP_eq_length_filter, ← hn, List.count, List.countP_map]
    congr 1
    funext p
    simp only [Function.comp]
    exact Bool.eq_iff_iff.mpr (by simp only [beq_iff_eq]; exact eq_comm)
  rw [List.filter_cons, hm]
  by_cases hin : f x ∈ cs
  · have hno : (l.filter (fun y => !cs.contains (f y))).contains x = false := by
      apply Bool.eq_false_iff.mpr
      rw [ne_eq, jcontains_iff, List.mem_filter]
      simp [hin]
    rw [hno]
    simp only [Bool.false_eq_true, reduceIte, hcomps, hlen]
    simp [hcs.count, hin]
  · have hyes : (l.filter (fun y => !cs.contains (f y))).contains x = true := by
      rw [jcontains_iff, List.mem_filter]
      simp [hx, hin]
    rw [hyes]
    simp [hcomps, hlen, hcs.count, hin]

/-- No reading set, coupling or narrowing is lost or duplicated by the split (A3). -/
theorem split_keeps_links (environment document : Json) (parts : List (String × Json × Json))
    (h : splitCase environment document = .ok parts) :
  ∀ k ∈ ["reading_sets", "couplings", "narrowings"], ∀ x ∈ arr document k,
    (parts.filter (fun p => (arr p.2.2 k).contains x)).length = 1 := by
  intro k hk x hx
  rcases splitCase_parts h with rfl | ⟨cs, comps, hcs, hc, rfl⟩
  · simp [(jcontains_iff _ x).mpr hx]
  have hnd := companionSets_nodup hcs
  obtain ⟨hn, hdocs⟩ := componentsOf_docs document cs comps hc
  obtain ⟨hmc, hmn, hmr⟩ := mainDoc_arr document cs
  simp only [List.mem_cons, List.mem_nil_iff, or_false] at hk
  rcases hk with rfl | rfl | rfl
  · refine count_one _ setIdOf cs hnd _ _ comps hmr (fun p hp => ?_) hn x hx
    obtain ⟨ts, hts⟩ := hdocs p hp
    rw [hts, (componentDoc_arr document p.1 ts).2.2]
    rfl
  · rw [List.filter_cons, hmc, (jcontains_iff _ x).mpr hx]
    have : comps.filter (fun p => (arr p.2.2 "couplings").contains x) = [] := by
      apply List.filter_eq_nil_iff.mpr
      intro p hp
      obtain ⟨ts, hts⟩ := hdocs p hp
      rw [hts, (componentDoc_arr document p.1 ts).1]
      simp
    simp [this]
  · refine count_one _ (fun n => strOf (n.getObjValD "set")) cs hnd _ _ comps hmn (fun p hp => ?_) hn x hx
    obtain ⟨ts, hts⟩ := hdocs p hp
    rw [hts, (componentDoc_arr document p.1 ts).2.1]
    rfl

end Companions
end VE.Readings.Wire
