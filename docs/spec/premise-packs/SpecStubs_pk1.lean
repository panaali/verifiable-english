import VE.NormDefaults.LayeredAdmission
import VE.Readings.SupExtra

/-! Statement stub of PK-1, premise packs (docs/spec/premise-packs.md). Evidence for the statement review, not
product code: it lives under docs/, imports the tree on `main` unchanged, and some proofs are `sorry` (the build item
pk-1 proves them in `lean/VE/NormDefaults/Packs.lean`). Check it from `lean/` with
`PATH=~/.elan/bin:$PATH lake env lean ../docs/spec/premise-packs/SpecStubs_pk1.lean`.

Section numbers in comments are the spec's. -/

namespace VE.NormDefaults.Packs
open Lean
open VE.Norms (envAt size Sat)
open VE.NormDefaults.Wire (LayeredU softLabelledU extraValid BaseAdmissibleX)
universe u

/-! ## 2.1 The data -/

/-- 2.1. -/
inductive PackKind
  | vocabulary
  | constraint
  deriving DecidableEq, Repr

/-- 2.1: object keys and array indices from the request root, as strings. -/
abbrev RequestPath := List String

/-- 2.1: what one provider regenerates from the decoded request. -/
structure Pack where
  id : String
  kind : PackKind
  decls : List (String × List String)
  consts : List (String × String)
  labelled : List (String × VE.Formula)
  origins : List (String × RequestPath)

/-- 2.2: the one order of `X`. -/
def packOrder : List String := ["soft", "rights", "weighing", "attitudes", "scales", "events"]

/-- 2.3: each reserved prefix with its owner. -/
def reservedPrefixes : List (String × String) :=
  [("soft", "soft__"), ("rights", "rights__"), ("norm-defaults", "unsaid__")]

/-- The fixtures' provider rows (attitudes AT-2, events ET-4 add theirs in their own batches). -/
def fixturePrefixes : List (String × String) := [("attitudes", "attitudes__"), ("events", "date__")]

/-- 2.3: an author name that begins with a reserved prefix. -/
def reserved (n : String) : Bool := reservedPrefixes.any (fun (_, x) => n.startsWith x)

def Pack.names (p : Pack) : List String := p.decls.map (·.1) ++ p.consts.map (·.1)

/-- 2.3: `n` begins with a prefix that `p`'s provider owns. -/
def ownPrefixIn (pre : List (String × String)) (p : Pack) (n : String) : Bool :=
  pre.any (fun (o, x) => o == p.id && n.startsWith x)

def ownPrefix : Pack → String → Bool := ownPrefixIn reservedPrefixes

/-! ## 2.4 Assembly -/

/-- The packs in `packOrder`, the first of each id. -/
def ordered (ps : List Pack) : List Pack := packOrder.filterMap (fun i => ps.find? (·.id == i))

def labelledX (qs : List Pack) : List (String × VE.Formula) := qs.flatMap (·.labelled)
def X (qs : List Pack) : List VE.Formula := (labelledX qs).map (·.2)
def names (qs : List Pack) : List String := qs.flatMap Pack.names

/-- One pack's labelled premises; `[]` when the pack is absent. -/
def packPremises (qs : List Pack) (i : String) : List (String × VE.Formula) :=
  ((qs.find? (·.id == i)).map (·.labelled)).getD []

/-- `E` with the generated predicates and constants; sorts unchanged. -/
def extendEnv (E : VE.Environment) (ds : List (String × List String)) (cs : List (String × String)) :
    VE.Environment :=
  { E with
    predicates := fun n => match ds.lookup n with | some ss => some ss | none => E.predicates n
    constants := fun n => match cs.lookup n with | some s => some s | none => E.constants n }

/-- The complete environment of the filled tree, layer symbols and `unsaid__` names included. -/
def fullEnv (U : UDoc) : VE.Environment := envAt (fill U) (size (fill U))

/-- The base environment `X` is typed over: `envAt (fill U) 0` extended by every pack's names. -/
def envX (U : UDoc) (qs : List Pack) : VE.Environment :=
  extendEnv (envAt (fill U) 0) (qs.flatMap (·.decls)) (qs.flatMap (·.consts))

/-- The first `(pack, key)` whose key is already in `seen` or earlier in the list. -/
def firstRepeat (seen : List String) : List (String × String) → Option (String × String)
  | [] => none
  | (i, n) :: rest => if seen.contains n then some (i, n) else firstRepeat (n :: seen) rest

def declaredIn (E : VE.Environment) (n : String) : Bool := (E.predicates n).isSome || (E.constants n).isSome

/-- 2.4, over a prefix table and the environment the names must be fresh in; `used` counts the vocabulary `checkAuthorN` charged. -/
def assembleIn (pre : List (String × String)) (E : VE.Environment) (used : Nat) (ps : List Pack) :
    Except String (List Pack) := do
  if let some p := ps.find? (fun p => !packOrder.contains p.id) then
    throw s!"InvalidInput: unknown premise pack {p.id}"
  if let some i := packOrder.find? (fun i => ps.countP (·.id == i) > 1) then
    throw s!"InvalidInput: premise pack {i} is given twice"
  let qs := ordered ps
  if let some (i, l) := firstRepeat [] (qs.flatMap (fun p => p.labelled.map (fun a => (p.id, a.1)))) then
    throw s!"InvalidInput: premise label {l} of pack {i} is used twice"
  let named := qs.flatMap (fun p => p.names.map (fun n => (p.id, n)))
  if let some (i, n) := named.find? (fun (_, n) => declaredIn E n) then
    throw s!"InvalidInput: generated name {n} of pack {i} is already declared"
  if let some (i, n) := firstRepeat [] named then
    throw s!"InvalidInput: generated name {n} of pack {i} is declared twice"
  if let some p := qs.find? (fun p => !p.names.all (ownPrefixIn pre p)) then
    throw s!"InvalidInput: a generated name of pack {p.id} lacks its reserved prefix"
  if used + (names qs).length > 256 then throw "ResourceLimit: vocabulary size"
  pure qs

/-- 2.4. -/
def assemble (U : UDoc) (used : Nat) (ps : List Pack) : Except String (List Pack) :=
  assembleIn reservedPrefixes (fullEnv U) used ps

/-! ## 2.5 Theorems -/

theorem extendEnv_nil (E : VE.Environment) : extendEnv E [] [] = E := rfl

theorem envX_nil (U : UDoc) : envX U [] = envAt (fill U) 0 := rfl

/-- 2.5 (1). -/
theorem assemble_order {U : UDoc} {used : Nat} {ps qs : List Pack} (h : assemble U used ps = .ok qs) :
    qs = ordered ps ∧ qs.Perm ps ∧ (qs.map (·.id)).Sublist packOrder := sorry

/-- 2.5 (2). -/
theorem assemble_fresh {U : UDoc} {used : Nat} {ps qs : List Pack} (h : assemble U used ps = .ok qs) :
    ((labelledX qs).map (·.1)).Nodup ∧ (names qs).Nodup ∧
    (∀ p ∈ qs, ∀ n ∈ p.names, (fullEnv U).predicates n = none ∧ (fullEnv U).constants n = none ∧
      ownPrefix p n = true) ∧
    used + (names qs).length ≤ 256 := sorry

/-- 2.5 (3): each pack typed over the base environment and its own names gives `X` typed over `envX`. -/
theorem assemble_wellFormed {U : UDoc} {used : Nat} {ps qs : List Pack} (h : assemble U used ps = .ok qs)
    (hp : ∀ p ∈ ps, ∀ a ∈ p.labelled, a.2.WellFormed (extendEnv (envAt (fill U) 0) p.decls p.consts) []) :
    ∀ a ∈ X qs, a.WellFormed (envX U qs) [] := sorry

/-- 2.5 (4): the empty pack list (JT-R2). -/
theorem assemble_nil (U : UDoc) (used : Nat) (hu : used ≤ 256) : assemble U used [] = .ok [] := by
  simp [assemble, assembleIn, ordered, packOrder, firstRepeat, names, Nat.not_lt.mpr hu]
  rfl

/-! ## 2.6 The legacy packs -/

/-- Soft's `Exc_T ++ Coh_T` on `fill U` (`Layered.lean:51–53`); its names are declared in `U` by `soften`. -/
def softPack (U : UDoc) (D : VE.SoftNorms.SoftDoc) : Pack := ⟨"soft", .constraint, [], [], softLabelledU U D, []⟩

/-- The rights limitation premises (`Layered.lean:120`); its names are declared in `U` by `correlate`. -/
def rightsPack (R : VE.Rights.RightsDoc) : Pack :=
  ⟨"rights", .constraint, [], [], VE.Rights.limPremisesLabelled R, []⟩

/-- The pack-id lists whose outputs and texts are today's. -/
def legacyIds : List (List String) := [[], ["soft"], ["soft", "rights"]]

/-- 2.6: the labels today's decoders build are distinct (proved in pk-1 from the checks they already run). -/
theorem softLabelledU_labels_nodup (U : UDoc) (D : VE.SoftNorms.SoftDoc)
    (hs : VE.SoftNorms.WellFormedSoft D = true) (hw : WellFormedU U = true) :
    ((softLabelledU U D).map (·.1)).Nodup := sorry

theorem legacy_labels_nodup (U : UDoc) (R : VE.Rights.RightsDoc)
    (hs : VE.SoftNorms.WellFormedSoft (VE.Rights.correlate R) = true) (hw : WellFormedU U = true) :
    ((softLabelledU U (VE.Rights.correlate R) ++ VE.Rights.limPremisesLabelled R).map (·.1)).Nodup := sorry

/-- 2.6 (5): assembly accepts today's soft source unchanged. -/
theorem assemble_legacy_soft (U : UDoc) (D : VE.SoftNorms.SoftDoc) (used : Nat) (hu : used ≤ 256)
    (hn : ((softLabelledU U D).map (·.1)).Nodup) :
    assemble U used [softPack U D] = .ok [softPack U D] := sorry

/-- 2.6 (5): and today's rights source, in today's order, whichever order the decoder lists them in. -/
theorem assemble_legacy_rights (U : UDoc) (R : VE.Rights.RightsDoc) (used : Nat) (hu : used ≤ 256)
    (hn : ((softLabelledU U (VE.Rights.correlate R) ++ VE.Rights.limPremisesLabelled R).map (·.1)).Nodup) :
    assemble U used [softPack U (VE.Rights.correlate R), rightsPack R] =
      .ok [softPack U (VE.Rights.correlate R), rightsPack R] ∧
    assemble U used [rightsPack R, softPack U (VE.Rights.correlate R)] =
      .ok [softPack U (VE.Rights.correlate R), rightsPack R] := sorry

/-- 2.6 (6): `X` is today's `L.labelled.map (·.2)` (`Layered.lean:72`, `:101`, `:121`). -/
theorem X_legacy (s r : Pack) : X [s, r] = (s.labelled ++ r.labelled).map (·.2) := by
  simp [X, labelledX]

/-- 2.6 (7): today's `"soft"` array and `filledX`'s soft prefix (`Layered.lean:150`, `:289`,
`LayeredAdmission.lean:105`) are the soft pack's premises. -/
theorem legacy_take (s r : List (String × VE.Formula)) :
    (s ++ r).take ((s ++ r).length - r.length) = s := by
  simp

/-- 2.6 (7): today's `"rights"` array (`Layered.lean:152`) is the rights pack's premises. -/
theorem legacy_drop (s r : List (String × VE.Formula)) :
    (s ++ r).drop ((s ++ r).length - r.length) = r := by
  simp

theorem packPremises_legacy (U : UDoc) (R : VE.Rights.RightsDoc) :
    packPremises [softPack U (VE.Rights.correlate R), rightsPack R] "soft" = softLabelledU U (VE.Rights.correlate R) ∧
    packPremises [softPack U (VE.Rights.correlate R), rightsPack R] "rights" = VE.Rights.limPremisesLabelled R := by
  simp [packPremises, softPack, rightsPack]

theorem packPremises_absent (qs : List Pack) (i : String) (h : ∀ p ∈ qs, p.id ≠ i) : packPremises qs i = [] := by
  simp only [packPremises]
  rw [List.find?_eq_none.mpr (fun p hp => by simpa using h p hp)]
  rfl

/-- 2.6 (DF5): soft is first in `X`, so `X` is soft's premises, then the other packs' (`R` in defeasible's
`DefaultsView`). -/
theorem X_soft_first {U : UDoc} {used : Nat} {ps qs : List Pack} (h : assemble U used ps = .ok qs) :
    X qs = (packPremises qs "soft").map (·.2) ++ X (qs.filter (·.id != "soft")) := sorry

/-! ## 2.7 Elaborate entries -/

def labelledJson (l : String) (a : VE.Formula) (origin : Option RequestPath) : Json :=
  Json.mkObj ([("label", .str l), ("ast", VE.SoftNorms.Wire.enc a)] ++
    match origin with | some o => [("origin", toJson o)] | none => [])

/-- One further pack's entry: its premises and its generated names, each with its origin. -/
def packEntry (p : Pack) : String × Json :=
  (p.id, Json.mkObj [
    ("premises", Json.arr (p.labelled.map (fun (l, a) => labelledJson l a (p.origins.lookup l))).toArray),
    ("names", Json.arr ((p.decls.map (fun (d : String × List String) => let (n, ss) := d; Json.mkObj [("name", .str n), ("arguments", toJson ss),
        ("origin", toJson ((p.origins.lookup n).getD []))])) ++
      (p.consts.map (fun (d : String × String) => let (n, s) := d; Json.mkObj [("name", .str n), ("sort", .str s),
        ("origin", toJson ((p.origins.lookup n).getD []))]))).toArray)])

/-- 2.7: the `"soft"` and `"rights"` arrays as today (`Layered.lean:150–153`), then one entry per further pack,
in `packOrder` (none on a legacy list, which holds only soft and rights). -/
def elaborateArrays (qs : List Pack) : List (String × Json) :=
  [("soft", Json.arr ((packPremises qs "soft").map (fun (l, a) => labelledJson l a none)).toArray),
   ("rights", Json.arr ((packPremises qs "rights").map (fun (l, a) => labelledJson l a none)).toArray)] ++
  (qs.filter (fun p => p.id != "soft" && p.id != "rights")).map packEntry

/-- 2.7 (7′): on a legacy list the arrays are today's expressions over `labelled` and `rightsCount`. -/
theorem elaborateArrays_legacy (s r : Pack) (hs : s.id = "soft") (hr : r.id = "rights") :
    elaborateArrays [s, r] =
      [("soft", Json.arr (((s.labelled ++ r.labelled).take ((s.labelled ++ r.labelled).length - r.labelled.length)).map
          (fun (l, a) => Json.mkObj [("label", .str l), ("ast", VE.SoftNorms.Wire.enc a)])).toArray),
       ("rights", Json.arr (((s.labelled ++ r.labelled).drop ((s.labelled ++ r.labelled).length - r.labelled.length)).map
          (fun (l, a) => Json.mkObj [("label", .str l), ("ast", VE.SoftNorms.Wire.enc a)])).toArray)] := sorry

/-! ## 2.8 Diagnostics -/

/-- The first premise of `X`, in `X` order, that `holds` rejects, with its pack id and label. -/
def firstFailing (qs : List Pack) (holds : VE.Formula → Bool) : Option (String × String) :=
  (qs.flatMap (fun p => p.labelled.map (fun a => (p.id, a)))).findSome? fun (i, l, a) =>
    if holds a then none else some (i, l)

/-- 2.8: `filledX`'s text when `X` fails: today's for a legacy list, pack and label otherwise. -/
def packFault (qs : List Pack) (holds : VE.Formula → Bool) : String :=
  match firstFailing qs holds with
  | some (i, l) =>
    if legacyIds.contains (qs.map (·.id)) then VE.Route.Wire.invalidModel i
    else VE.Route.Wire.invalidModel i ++ ": " ++ l
  | none => VE.Route.Wire.invalidModel "premises"

theorem firstFailing_some (qs : List Pack) (holds : VE.Formula → Bool) (h : (X qs).all holds = false) :
    (firstFailing qs holds).isSome := sorry

/-- 2.8 (8): on a legacy rights list the text is `Layered.lean:289–290`'s. -/
theorem packFault_legacy_rights (U : UDoc) (R : VE.Rights.RightsDoc) (M : VE.FiniteModel VE.Bridge.Entity)
    (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity)
    (hx : extraValid U (X [softPack U (VE.Rights.correlate R), rightsPack R]) M F = false) :
    packFault [softPack U (VE.Rights.correlate R), rightsPack R] (fun a => a.eval (M.withFill F) []) =
      VE.Route.Wire.invalidModel
        (if extraValid U ((softLabelledU U (VE.Rights.correlate R)).map (·.2)) M F then "rights" else "soft") := sorry

/-- 2.8 (8): on a legacy soft list it is `InvalidModel(soft)`. -/
theorem packFault_legacy_soft (U : UDoc) (D : VE.SoftNorms.SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity)
    (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity) (hx : extraValid U (X [softPack U D]) M F = false) :
    packFault [softPack U D] (fun a => a.eval (M.withFill F) []) = VE.Route.Wire.invalidModel "soft" := sorry

/-! ## 2.9 What PK-1 guarantees about witnesses -/

/-- 2.9: `X` without the premises under the labels in `drop`. -/
def xWithout (qs : List Pack) (drop : List String) : List VE.Formula :=
  ((labelledX qs).filter (fun a => !drop.contains a.1)).map (·.2)

/-- 2.9: the soft pack's coherence labels, from the colliding pairs (DF7's collision witness drops these). -/
def coherenceLabels (D : VE.SoftNorms.SoftDoc) : List String :=
  (VE.SoftNorms.collidingPairs D).map (fun (M, N) => VE.SoftNorms.Wire.cohLabel M N)

theorem xWithout_nil (qs : List Pack) : xWithout qs [] = X qs := by
  simp only [xWithout, X, List.contains_nil, Bool.not_false]
  rw [List.filter_eq_self.mpr (fun _ _ => rfl)]

theorem xWithout_sub (qs : List Pack) (drop : List String) : ∀ a ∈ xWithout qs drop, a ∈ X qs := by
  intro a ha
  simp only [xWithout, List.mem_map, List.mem_filter] at ha
  obtain ⟨b, ⟨hb, _⟩, rfl⟩ := ha
  exact List.mem_map.mpr ⟨b, hb, rfl⟩

/-- 2.9 (9): every filled situation the layered route accepts satisfies the whole `X`. -/
theorem filledX_whole (L : LayeredU) (w : Json) (fw : VE.NormDefaults.Wire.FilledX L)
    (_h : VE.NormDefaults.Wire.filledX L w = .ok fw) : extraValid L.U L.X fw.S.M fw.F = true := fw.extra_ok

/-! ## 2.10 Provider obligations -/

/-- `B` with the relations and constants replaced. -/
def expandBy (B : VE.Structure.{u}) (R : String → List B.Carrier → Prop) (k : String → Option B.Carrier) :
    VE.Structure.{u} := { B with relation := R, constant := k }

/-- 2.10 (1): a vocabulary pack's expansion step after `earlier`: every admissible base of the base and the earlier
packs expands, changing only `p`'s own names, to a typed structure that still is one and satisfies `p`'s premises. -/
def ExpandsOn (U : UDoc) (earlier : List Pack) (p : Pack) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleX U (X earlier) B →
    ∃ (R : String → List B.Carrier → Prop) (k : String → Option B.Carrier),
      (∀ n vs, n ∉ p.decls.map (·.1) → (R n vs ↔ B.relation n vs)) ∧
      (∀ n, n ∉ p.consts.map (·.1) → k n = B.constant n) ∧
      (∀ d ∈ p.decls, ∀ vs, R d.1 vs → VE.TupleTyped B d.2 vs) ∧
      (∀ c ∈ p.consts, ∃ e, k c.1 = some e ∧ B.domain c.2 e) ∧
      BaseAdmissibleX U (X earlier) (expandBy B R k) ∧ Sat (expandBy B R k) (p.labelled.map (·.2))

/-- 2.10 (5): every label and generated name has an origin, and nothing else does. -/
def OriginsExact (p : Pack) : Prop := p.origins.map (·.1) = p.labelled.map (·.1) ++ p.names

/-! ## 2.11 The kind table -/

/-- 2.11: one row of the layered route's kind table. -/
structure KindRow where
  kind : String
  pack : Option String
  run : LayeredU → String → Json → Except String Json

/-- 2.11: the row for `kind`, refused when the pack it needs is absent. -/
def dispatch (rows : List KindRow) (ids : List String) (L : LayeredU) (id kind : String) (j : Json) :
    Except String (Option Json) :=
  match rows.find? (·.kind == kind) with
  | none => pure none
  | some r =>
    match r.pack with
    | some i => if ids.contains i then some <$> r.run L id j
      else throw s!"UnsupportedProfile: case kind {kind} needs the {i} premise pack"
    | none => some <$> r.run L id j

/-- 2.11: today's four kinds (`Layered.lean:410–437`), as rows. -/
def legacyKinds : List String :=
  ["norm-defaults-elaborate", "norm-defaults-conflict", "norm-defaults-status", "norm-defaults-report"]

def legacyRows : List KindRow := legacyKinds.map fun k =>
  ⟨k, none, fun L id j => do
    match ← VE.NormDefaults.Wire.layeredCase L id k j with
    | some a => pure a
    | none => throw "unreachable"⟩

theorem dispatch_legacy (ids : List String) (L : LayeredU) (id kind : String) (j : Json) (hk : kind ∈ legacyKinds) :
    dispatch legacyRows ids L id kind j = VE.NormDefaults.Wire.layeredCase L id kind j := sorry

end VE.NormDefaults.Packs

/-! ## 2.12 `transfers_append` -/

namespace VE.Readings
universe u

/-- 2.12: carried families concatenate. -/
theorem transfers_append (D : Doc) (Q₁ Q₂ : List VE.Formula) (Q₁c Q₂c : Choice → List VE.Formula)
    (h₁ : Transfers.{u} D Q₁ Q₁c) (h₂ : Transfers.{u} D Q₂ Q₂c) :
    Transfers.{u} D (Q₁ ++ Q₂) (fun c => Q₁c c ++ Q₂c c) := by
  refine ⟨fun c hc a ha => ?_, fun c hc B hB he => ?_⟩
  · rcases List.mem_append.mp ha with ha | ha
    · exact h₁.1 c hc a ha
    · exact h₂.1 c hc a ha
  · rw [VE.Compose.sat_append, VE.Compose.sat_append]
    exact and_congr (h₁.2 c hc B hB he) (h₂.2 c hc B hB he)

/-- 2.12: one family per pack gives the family of `X`. -/
theorem transfers_X (D : Doc) (qs : List VE.NormDefaults.Packs.Pack)
    (Qc : VE.NormDefaults.Packs.Pack → Choice → List VE.Formula)
    (h : ∀ p ∈ qs, Transfers.{u} D (p.labelled.map (·.2)) (Qc p)) :
    Transfers.{u} D (VE.NormDefaults.Packs.X qs) (fun c => qs.flatMap (fun p => Qc p c)) := by
  induction qs with
  | nil => exact transfers_nil D
  | cons p ps ih =>
    have hX : VE.NormDefaults.Packs.X (p :: ps) =
        p.labelled.map (·.2) ++ VE.NormDefaults.Packs.X ps := by
      simp [VE.NormDefaults.Packs.X, VE.NormDefaults.Packs.labelledX]
    rw [hX]
    exact transfers_append D _ _ (Qc p) (fun c => ps.flatMap (fun p => Qc p c))
      (h p (List.mem_cons_self ..)) (ih (fun q hq => h q (List.mem_cons_of_mem _ hq)))

end VE.Readings

/-! ## 4 Acceptance fixtures (computed by `#guard`) -/

namespace VE.NormDefaults.Packs.Fixtures
open VE.NormDefaults.Packs

/-- An author environment: `person`, the predicate `helps`, and the author name `attitudes__knows__1` (fixture A4). -/
def E : VE.Environment :=
  ⟨["person"], fun n => if n == "helps" || n == "attitudes__knows__1" then some ["person"] else none, fun _ => none⟩

/-- The prefix table with the two provider rows the fixtures need. -/
def P : List (String × String) := reservedPrefixes ++ fixturePrefixes

def φ : VE.Formula := .top

def soft : Pack := ⟨"soft", .constraint, [], [],
  [("soft:exception:r1:sufficient:0", φ), ("soft:coherence:r1,r2", φ)], []⟩
def rights : Pack := ⟨"rights", .constraint, [], [], [("rights:limitation:l1:act:necessary:c1", φ)], []⟩
def weighing : Pack := ⟨"weighing", .constraint, [], [], [("weigh:strength:a:b:x_permitted", .bottom)], []⟩

def diag : Except String (List Pack) → String
  | .ok qs => "ok " ++ toString (qs.map (·.id)) ++ " " ++ toString ((labelledX qs).map (·.1))
  | .error e => e

-- A1: today's lists, in either order, give today's X order (soft, then rights).
#guard diag (assembleIn P E 3 [soft, rights]) ==
  "ok [soft, rights] [soft:exception:r1:sufficient:0, soft:coherence:r1,r2, rights:limitation:l1:act:necessary:c1]"
#guard diag (assembleIn P E 3 [rights, soft]) == diag (assembleIn P E 3 [soft, rights])
#guard diag (assembleIn P E 3 [weighing, soft]) ==
  "ok [soft, weighing] [soft:exception:r1:sufficient:0, soft:coherence:r1,r2, weigh:strength:a:b:x_permitted]"

-- A2: a repeated id.
#guard diag (assembleIn P E 3 [soft, rights, soft]) == "InvalidInput: premise pack soft is given twice"

-- A3: a repeated label, within one pack and across two.
#guard diag (assembleIn P E 3 [{ soft with labelled := soft.labelled ++ [("soft:coherence:r1,r2", φ)] }]) ==
  "InvalidInput: premise label soft:coherence:r1,r2 of pack soft is used twice"
#guard diag (assembleIn P E 3 [soft, { weighing with labelled := [("soft:coherence:r1,r2", φ)] }]) ==
  "InvalidInput: premise label soft:coherence:r1,r2 of pack weighing is used twice"

-- A4: a generated name that E declares, or that another pack declares.
def att (n : String) : Pack := ⟨"attitudes", .vocabulary, [(n, ["person"])], [], [], [(n, ["environment"])]⟩
def ev (n : String) : Pack := ⟨"events", .constraint, [], [(n, "person")], [], [(n, ["environment"])]⟩
#guard diag (assembleIn P E 3 [att "attitudes__knows__1"]) ==
  "InvalidInput: generated name attitudes__knows__1 of pack attitudes is already declared"
#guard diag (assembleIn P E 3 [att "helps"]) == "InvalidInput: generated name helps of pack attitudes is already declared"
#guard diag (assembleIn P E 3 [att "shared__x", ev "shared__x"]) ==
  "InvalidInput: generated name shared__x of pack events is declared twice"
#guard diag (assembleIn P E 3 [att "shared__x"]) ==
  "InvalidInput: a generated name of pack attitudes lacks its reserved prefix"

-- A4′: fresh, prefixed names pass, in packOrder, and extend the environment.
#guard diag (assembleIn P E 3 [ev "date__d", att "attitudes__k__2", soft]) == "ok [soft, attitudes, events] [soft:exception:r1:sufficient:0, soft:coherence:r1,r2]"
#guard (extendEnv E [("attitudes__k__2", ["person"])] [("date__d", "person")]).predicates "attitudes__k__2" == some ["person"]
#guard (extendEnv E [("attitudes__k__2", ["person"])] [("date__d", "person")]).constants "date__d" == some "person"
#guard (extendEnv E [("attitudes__k__2", ["person"])] []).predicates "helps" == some ["person"]

-- A5: the empty pack list.
#guard diag (assembleIn P E 3 []) == "ok [] []"
#guard X [] = []

-- A6: an unknown id, and the vocabulary limit (the prefix rows of a provider are added by its batch).
#guard diag (assembleIn P E 3 [{ soft with id := "acts" }]) == "InvalidInput: unknown premise pack acts"
#guard diag (assembleIn P E 257 []) == "ResourceLimit: vocabulary size"
#guard diag (assembleIn P E 256 []) == "ok [] []"
#guard diag (assembleIn P E 255 [att "attitudes__k__2", ev "date__d"]) == "ResourceLimit: vocabulary size"

-- A7: diagnostics. Legacy lists keep today's text; a new combination names the pack and the label.
def holds (a : VE.Formula) : Bool := a != .bottom
#guard packFault [soft, rights] (fun a => a != φ) == "InvalidModel(soft): the model violates a background premise"
#guard packFault [soft, { rights with labelled := [("rights:limitation:l1:act:necessary:c1", .bottom)] }] holds ==
  "InvalidModel(rights): the model violates a background premise"
#guard packFault [soft, weighing] holds ==
  "InvalidModel(weighing): the model violates a background premise: weigh:strength:a:b:x_permitted"

-- A8: packPremises and the collision witness's X.
#guard (packPremises [soft, rights] "rights").map (·.1) == ["rights:limitation:l1:act:necessary:c1"]
#guard (packPremises [soft] "rights").isEmpty
#guard xWithout [soft, weighing] ["soft:coherence:r1,r2"] = [φ, .bottom]

-- A9: elaborate entries: today's two arrays on a legacy list; one more entry per further pack otherwise.
#guard (elaborateArrays [soft, rights]).map (·.1) == ["soft", "rights"]
#guard (elaborateArrays []).map (·.1) == ["soft", "rights"]
#guard (elaborateArrays [soft, weighing, ev "date__d"]).map (·.1) == ["soft", "rights", "weighing", "events"]
#guard ((elaborateArrays [soft, rights]).lookup "soft").map (·.compress) ==
  some "[{\"ast\":[\"top\"],\"label\":\"soft:exception:r1:sufficient:0\"},{\"ast\":[\"top\"],\"label\":\"soft:coherence:r1,r2\"}]"

-- The reserved prefixes are pairwise disjoint (no prefix begins another).
#guard reservedPrefixes.all fun (o, x) => reservedPrefixes.all fun (o', y) => o == o' || !x.startsWith y

end VE.NormDefaults.Packs.Fixtures
