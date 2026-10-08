import VE.NormDefaults.Replay

/-! The `norm-defaults-report` case (docs/spec/norm-defaults.md 3.2 and 5): the lines of
every regulated predicate, decided here from checked evidence.

* `completion: deny | allow | unspecified`, from the environment.
* `gaps:` (unspecified) or `default reached:` (deny, allow): `reachable` when a filled
  situation and typed tuple where no author rule decides is found and checked (a supplied
  base `model` is searched here, `reachedWitness`, as Python's `_reached_witness` searches
  it; otherwise a supplied filled `witnesses` entry from the untrusted small-model search is
  replayed); else `none` when the `reached:<p>` package's certificate for `∀x̄. ¬reached_p`
  is accepted; else `unknown`.
* `grounded: <unit ids>` or `UngroundedDefault: <p>`, from the `completions` block
  (`validateCompletions`, spec 5): the finding only for a deny or allow completion of a
  translation document that has a `default reached` witness and no citation
  (`grounding_ungrounded_iff`).
* `inherits_from: [q, …]`: the unspecified predicates in the static guard cone.

`normDefaults_wire_report_sound`: every `reachable` line has an admissible filled witness
(`ReachedSome`), every `none` line is never reached (`NeverReached`), and the finding is
exactly the spec's condition. The residual `gaps` lists the unspecified predicates with a
`reachable` line and `ungrounded_defaults` counts the findings (`ReportU.residual`). -/
namespace VE.NormDefaults.Wire
open Lean
open VE.Norms VE.Route
open VE.Bridge (Entity fields strings)
universe u

/-! ## The `completions` block (5) -/

/-- The cited unit ids of one grounding entry, if it has exactly the fields `cites` (a
non-empty list of distinct strings) and `reason` (a string that is not blank in Python's
`str.isspace` sense). -/
def groundingCites (item : Json) : Option (List String) := do
  let kvs ← (fields item).toOption
  guard (kvs.length == 2 && kvs.any (·.1 == "cites") && kvs.any (·.1 == "reason"))
  let cites ← (strings (item.getObjValD "cites")).toOption
  guard (!cites.isEmpty && cites.eraseDups.length == cites.length)
  match item.getObjValD "reason" with
  | .str reason => if reason.any (fun c => !VE.Norms.Wire.pyWhitespace c) then some cites else none
  | _ => none

/-- A validated grounding: the predicate and its citations, each a known unit. -/
abbrev Cited (unitIds : List String) := {e : String × List String // e.2 ≠ [] ∧ e.2.all unitIds.contains = true}

/-- The `completions` grounding block (spec 5, Python `validate_completions` and its texts):
each entry names a regulated predicate whose completion is deny or allow, cites existing
source units and gives a reason. Entries are read in key order. -/
def validateCompletions (U : UDoc) (block : Json) (unitIds : List String) :
    Except String (List (Cited unitIds)) := do
  let entries ← match block with
    | .obj _ => fields block
    | _ => throw "InvalidInput: completions must be an object"
  entries.mapM fun (p, item) => do
    match U.D.T.regulated.find? (·.name == p) with
    | none => throw s!"UnknownSymbol: regulated predicate {p}"
    | some r =>
      if completionOf U r = .unspecified then
        throw s!"InvalidInput: completion of {p} is unspecified and cites nothing"
      let bad := s!"InvalidInput: invalid completion grounding for {p}"
      match groundingCites item with
      | none => throw bad
      | some cites =>
        unless cites.all unitIds.contains do
          throw s!"InvalidInput: completion grounding for {p} cites an unknown unit"
        if h : cites ≠ [] ∧ cites.all unitIds.contains = true then pure ⟨(p, cites), h⟩ else throw bad

/-! ## Lines -/

inductive Reached | never | reachable | unknown
  deriving DecidableEq, Repr

def Reached.label : Reached → String
  | .never => "none"
  | .reachable => "reachable"
  | .unknown => "unknown"

inductive Grounding | none | grounded (cites : List String) | ungrounded
  deriving DecidableEq, Repr

/-- The grounding of `r` (3.2, 5): its citation if the block names it, else the finding
for a reached deny or allow completion of a translation document. -/
def groundingOf (U : UDoc) (r : Regulated) (cited : List (String × List String)) (translation reachable : Bool) :
    Grounding :=
  if completionOf U r = .unspecified then .none
  else match VE.Bridge.lookup cited r.name with
    | some cites => .grounded cites
    | none => if translation && reachable then .ungrounded else .none

theorem grounding_ungrounded_iff (U : UDoc) (r : Regulated) (cited : List (String × List String))
    (translation reachable : Bool) :
    groundingOf U r cited translation reachable = .ungrounded ↔
      completionOf U r ≠ .unspecified ∧ VE.Bridge.lookup cited r.name = none ∧ translation = true ∧
        reachable = true := by
  unfold groundingOf
  by_cases hc : completionOf U r = .unspecified
  · simp [hc]
  · simp only [hc, if_false, ne_eq, not_false_eq_true, true_and]
    cases hl : VE.Bridge.lookup cited r.name with
    | some cites => simp
    | none => cases translation <;> cases reachable <;> simp

def Grounding.line (p : String) : Grounding → List String
  | .none => []
  | .grounded cites => ["grounded: " ++ ", ".intercalate cites]
  | .ungrounded => [s!"UngroundedDefault: {p}"]

def completionLabel : Completion → String
  | .deny => "deny"
  | .allow => "allow"
  | .unspecified => "unspecified"

/-- The value a completion gives where no author rule decides (`Explain.value3_gap`). -/
def completedLabel : Completion → String
  | .deny => "no"
  | .allow => "yes"
  | .unspecified => "unsaid"

/-! ## The static cone (2.5) -/

/-- The predicates named in the guards and carve-outs of the rules on `p`. -/
def guardPredicates (U : UDoc) (p : String) : List String :=
  (U.D.T.nodes.filter (·.pred == p)).flatMap (fun N => (N.guard :: N.carveOuts).flatMap VE.Norms.preds)

/-- The regulated predicates reached from `pending` along guard edges (fuel: one step per
regulated predicate taken from the list). -/
def guardCone (U : UDoc) : Nat → List String → List String → List String
  | 0, _, seen => seen
  | _ + 1, [], seen => seen
  | k + 1, q :: rest, seen =>
    let next := ((guardPredicates U q).filter (fun x =>
      (U.D.T.regulated.any (·.name == x)) && !seen.contains x)).eraseDups
    guardCone U k (rest ++ next) (seen ++ next)

/-- `inherits_from` (Python `inherits_from`): the unspecified predicates in the guard cone
of `p`, without `p`, sorted. -/
def inheritsFrom (U : UDoc) (p : String) : List String :=
  sortBy (fun a b => decide (a < b))
    ((guardCone U (U.D.T.regulated.length + 2) [p] []).filter (fun q => q ∈ U.unspec && q != p))

/-! ## The witness search in a supplied situation (Python `_reached_witness`) -/

/-- True on the permission members of declared pairs, false elsewhere (Python
`canonical_filling`, Lean `canonicalFill`), as a finite filling. -/
def canonicalFinite (U : UDoc) (M : VE.FiniteModel Entity) : FiniteFill U Entity :=
  fun n => match U.unspec.find? (fun p => unsaidName p == n) with
    | some p => if (pairs U.D.T).any (fun pr => pr.perm == p) then allTuples M (sortsOf U.D p) else []
    | none => []

/-- The assignment true exactly on `A` of the atoms `C`, the canonical filling elsewhere
(Python `_extend`). -/
def extendFill (U : UDoc) (M : VE.FiniteModel Entity) (C A : List (String × List Entity)) :
    FiniteFill U Entity :=
  fun n => ((canonicalFinite U M n).filter (fun ws => !C.contains (n, ws))) ++
    (A.filter (·.1 == n)).map (·.2)

/-- Python's order on atoms: the predicate name, then the entity ids. -/
def atomKey (a : String × List Entity) : List String := a.1 :: a.2.map (·.2)

def sortAtoms (C : List (String × List Entity)) : List (String × List Entity) :=
  sortBy (fun a b => decide (atomKey a < atomKey b)) C

/-- The filling under which `p` is reached at `vs` (Python `_reached_witness` at one
tuple): the canonical filling where `reached_p` is Kleene-true with nothing filled;
otherwise the first assignment of the point's closed cone (at most `MAX_UNSAID_ATOMS`
atoms, in Python's order) under which every open `Fill_T` instance meeting the cone and
`reached_p` are Kleene-true, extended canonically. Untrusted: `reachedWitness` checks it. -/
def reachedAt (U : UDoc) (M : VE.FiniteModel Entity) (p : String) (vs : List Entity) :
    Option (FiniteFill U Entity) :=
  let φ := reachedF U p
  let ρ := tupleVal vs
  match (coneEval U M ρ φ).1 with
  | some true => some (canonicalFinite U M)
  | some false => none
  | none =>
    let C := sortAtoms (coneOf U M ρ φ)
    if C.length > MAX_UNSAID_ATOMS then none else
    let touching := (openInstances U M).filter (fun i => i.2.any C.contains)
    ((subsets C).find? (fun A =>
      touching.all (fun i => kleene M (coneAtomV U M C A) (tupleVal i.1.2) (fillBody U i.1.1) == some true) &&
        kleene M (coneAtomV U M C A) ρ φ == some true)).map (extendFill U M C)

/-- The route's extra base premises hold on the filled situation. -/
def extraValid (U : UDoc) (X : List VE.Formula) (M : VE.FiniteModel Entity) (F : FiniteFill U Entity) : Bool :=
  X.all (fun φ => φ.eval (M.withFill F) [])

/-- The first typed tuple, in Python's order, whose proposed filling is admissible (`Fill_T`
and the route's base premises `X`) and reaches `r` there. -/
def reachedWitness (U : UDoc) (X : List VE.Formula) (M : VE.FiniteModel Entity) (r : Regulated) :
    Option (List Entity × FiniteFill U Entity) :=
  (allTuples M r.sorts).findSome? fun vs => match reachedAt U M r.name vs with
    | some F => if fillValid U M F && extraValid U X M F && (reachedF U r.name).eval (M.withFill F) (tupleVal vs)
        then some (vs, F) else none
    | none => none

/-! ## Admissibility with the route's base premises -/

/-- Base admissibility on `fill U` with the route's extra base premises `X`: soft's `Soft_T`
(regenerated on `fill U`) and the rights limitation premises; `X = []` on the norms route. -/
def BaseAdmissibleX (U : UDoc) (X : List VE.Formula) (B : VE.Structure.{u}) : Prop :=
  BaseAdmissibleU U B ∧ Sat B X

/-- Some admissible filled base structure has a typed tuple where no author rule on `r`
decides: `gaps: reachable` (unspecified) or `default reached` (deny, allow). -/
def ReachedSome (U : UDoc) (X : List VE.Formula) (r : Regulated) : Prop :=
  ∃ B : VE.Structure.{0}, BaseAdmissibleX U X B ∧ ∃ vs : List B.Carrier, VE.TupleTyped B r.sorts vs ∧
    (reachedF U r.name).denote B (tupleVal vs)

/-- At every typed tuple of every admissible filled base structure some author rule on
`r` decides: `gaps: none`, and for deny or allow the completion is never used. -/
def NeverReached (U : UDoc) (X : List VE.Formula) (r : Regulated) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleX U X B → ∀ vs : List B.Carrier, VE.TupleTyped B r.sorts vs →
    ¬ (reachedF U r.name).denote B (tupleVal vs)

/-- A checked finite filling of a situation is admissible with the route's premises. -/
theorem admissibleX_of_fill (U : UDoc) (h : WellFormedU U = true) (X : List VE.Formula)
    (M : VE.FiniteModel Entity) (valid : M.Valid (envAt U.D 0)) (hb : backgroundValid U.D M = true)
    (F : FiniteFill U Entity) (hF : fillValid U M F = true) (hX : extraValid U X M F = true) :
    BaseAdmissibleX U X (withFill U M.asStructure (finFill M F)) :=
  ⟨admissible_of_fillValid U h M valid hb F hF, fun φ hφ =>
    (eval_withFill U M F φ []).mp (List.all_eq_true.mp hX φ hφ)⟩

/-- A checked filled situation reaches `r`. -/
theorem reachedSome_of_fill (U : UDoc) (h : WellFormedU U = true) (X : List VE.Formula)
    (M : VE.FiniteModel Entity) (valid : M.Valid (envAt U.D 0)) (hb : backgroundValid U.D M = true)
    (r : Regulated) (vs : List Entity) (F : FiniteFill U Entity) (typed : vs ∈ allTuples M r.sorts)
    (hF : fillValid U M F = true) (hX : extraValid U X M F = true)
    (hr : (reachedF U r.name).eval (M.withFill F) (tupleVal vs) = true) : ReachedSome U X r :=
  ⟨withFill U M.asStructure (finFill M F), admissibleX_of_fill U h X M valid hb F hF hX, vs,
    (tupleTyped_relation M.asStructure _ _ vs).mpr ((mem_allTuples M r.sorts vs).mp typed),
    (eval_withFill U M F _ _).mp hr⟩

/-- A replayed filled model (`ReachedData`) at which `reached_p` evaluates true reaches `p`. -/
theorem ReachedData.reachedSome {s : SourceU} (d : ReachedData s) (hr : d.reached = true) :
    ReachedSome s.U [] d.r :=
  ⟨d.M.asStructure, ⟨⟨baseAdmissible_of_valid (fill s.U) d.M d.valid d.background, fun φ hφ =>
      (VE.eval_iff_denote d.M [] φ).mp (List.all_eq_true.mp d.filled φ hφ)⟩, fun _ h => by cases h⟩,
    d.tuple, d.typed, (VE.eval_iff_denote d.M _ _).mp hr⟩

/-! ## The evidence a route supplies -/

/-- A base situation of the author vocabulary (no unsaid tables), Background-valid. -/
structure SituationG (U : UDoc) where
  M : VE.FiniteModel Entity
  valid : M.Valid (envAt U.D 0)
  background : backgroundValid U.D M = true

/-- The witness shown with a `reachable` line: the tuple's entity ids and every unsaid
table of the filled situation, rows sorted (Python `_witness_json`). -/
structure WitnessRow where
  tuple : Json
  filling : List (String × Json)

def WitnessRow.toJson (w : WitnessRow) : Json :=
  Json.mkObj [("tuple", w.tuple), ("filling", Json.mkObj w.filling)]

def witnessRow (U : UDoc) (M : VE.FiniteModel Entity) (vs : List Entity) : WitnessRow :=
  ⟨toJson (vs.map (·.2)), U.unspec.map fun p => (unsaidName p,
    toJson (sortBy (fun a b => decide (a < b)) ((M.relations (unsaidName p)).map (·.map (·.2)))))⟩

/-- What one route gives the report: its document `U`, its extra base premises `X`, how it
decodes a base situation, how it replays a supplied witness for `r` (`none` when the
`witnesses` object has no entry for `r` or the entry does not reach `r`), and how it replays
the `reached:<p>` certificate (`some` exactly when it is accepted). -/
structure ReportSource where
  U : UDoc
  X : List VE.Formula
  wfU : WellFormedU U = true
  situation : Json → Except String (SituationG U)
  supplied : Json → (r : Regulated) → Except String (Option (PLift (ReachedSome U X r) × WitnessRow))
  never : (r : Regulated) → Option (PLift (NeverReached.{0} U X r))

/-! ## One line -/

/-- The lines of one regulated predicate, with the facts its evidence establishes. -/
structure LineU (U : UDoc) (X : List VE.Formula) (cited : List (String × List String)) (translation : Bool) where
  r : Regulated
  reached : Reached
  witness : Option WitnessRow
  grounding : Grounding
  sound_reached : reached = .reachable → ReachedSome U X r
  sound_never : reached = .never → NeverReached.{0} U X r
  ground_eq : grounding = groundingOf U r cited translation (reached == .reachable)

def LineU.lines {U X cited translation} (l : LineU U X cited translation) : List String :=
  let c := completionOf U l.r
  [s!"completion: {completionLabel c}",
   (if c = .unspecified then "gaps: " else "default reached: ") ++ l.reached.label] ++
  l.grounding.line l.r.name ++
  (match inheritsFrom U l.r.name with
   | [] => []
   | qs => ["inherits_from: [" ++ ", ".intercalate qs ++ "]"])

def LineU.toJson {U X cited translation} (l : LineU U X cited translation) : Json :=
  Json.mkObj ([("predicate", .str l.r.name), ("completion", .str (completionLabel (completionOf U l.r))),
    ("reached", .str l.reached.label), ("lines", Lean.toJson l.lines),
    ("inherits_from", Lean.toJson (inheritsFrom U l.r.name))] ++
    (match l.witness with
     | some w => [("witness", w.toJson), ("value", .str (completedLabel (completionOf U l.r)))]
     | none => []))

/-- The situation's own witness search, checked. -/
def situationWitness (src : ReportSource) (S : SituationG src.U) (r : Regulated) :
    Option (PLift (ReachedSome src.U src.X r) × WitnessRow) :=
  match reachedWitness src.U src.X S.M r with
  | some (vs, F) =>
    if hc : vs ∈ allTuples S.M r.sorts ∧ fillValid src.U S.M F = true ∧ extraValid src.U src.X S.M F = true ∧
        (reachedF src.U r.name).eval (S.M.withFill F) (tupleVal vs) = true then
      some (⟨reachedSome_of_fill src.U src.wfU src.X S.M S.valid S.background r vs F hc.1 hc.2.1 hc.2.2.1
        hc.2.2.2⟩, witnessRow src.U (S.M.withFill F) vs)
    else none
  | none => none

/-- The evidence for one line, in Python `report`'s order: the situation's own witness
search, else a supplied witness; if neither reaches `r`, the `reached:<p>` certificate. -/
def lineFor (src : ReportSource) (witnesses : Json) (sit : Option (SituationG src.U))
    (cited : List (String × List String)) (translation : Bool) (r : Regulated) :
    Except String (LineU src.U src.X cited translation) := do
  let found ← match sit with
    | some S => pure (situationWitness src S r)
    | none => src.supplied witnesses r
  match found with
  | some (hs, w) =>
    pure ⟨r, .reachable, some w, groundingOf src.U r cited translation true, (fun _ => hs.down),
      (fun h => by cases h), rfl⟩
  | none =>
    match src.never r with
    | some hn =>
      pure ⟨r, .never, none, groundingOf src.U r cited translation false, (fun h => by cases h),
        (fun _ => hn.down), rfl⟩
    | none =>
      pure ⟨r, .unknown, none, groundingOf src.U r cited translation false, (fun h => by cases h),
        (fun h => by cases h), rfl⟩

/-! ## The report -/

structure ReportG (src : ReportSource) where
  unitIds : List String
  cited : List (Cited unitIds)
  translation : Bool
  lines : List (LineU src.U src.X (cited.map (·.1)) translation)

/-- The residual line `gaps` (3.2): the unspecified predicates with a reachable gap,
sorted, and the number of `UngroundedDefault` findings. -/
def ReportG.gaps {src} (rep : ReportG src) : List String :=
  sortBy (fun a b => decide (a < b)) ((rep.lines.filter (fun l =>
    completionOf src.U l.r = .unspecified && l.reached == .reachable)).map (·.r.name))

def ReportG.findings {src} (rep : ReportG src) : List String :=
  rep.lines.flatMap (fun l => if l.grounding = .ungrounded then l.grounding.line l.r.name else [])

def ReportG.toJson {src} (rep : ReportG src) : List (String × Json) :=
  [("report", Json.arr (rep.lines.map (·.toJson)).toArray),
   ("residual", Json.mkObj [("gaps", Lean.toJson rep.gaps),
     ("ungrounded_defaults", Lean.toJson rep.findings.length)]),
   ("findings", Lean.toJson rep.findings)]

/-- The report fields of a case: the `completions` block against `unit_ids`, an optional
base `model`, supplied `witnesses` (predicate → the route's witness) and `packages`
(`reached:<p>` → package), `translation` and an optional `predicates` restriction; lines in
the layer order of `fill U`. -/
def reportWith (src : ReportSource) (j : Json) : Except String (ReportG src) := do
  let translation ← match j.getObjValD "translation" with
    | .bool b => pure b
    | .null => pure false
    | _ => throw "InvalidInput: translation must be a boolean"
  let unitIds ← match j.getObjValD "unit_ids" with
    | .null => pure []
    | ids => match strings ids with
      | .ok xs => pure xs
      | .error _ => throw "InvalidInput: unit_ids must be a list of strings"
  let block := match j.getObjValD "completions" with
    | .null => Json.mkObj []
    | b => b
  let cited ← validateCompletions src.U block unitIds
  let sit ← match j.getObjValD "model" with
    | .null => pure none
    | m => some <$> src.situation m
  let only ← match j.getObjValD "predicates" with
    | .null => pure none
    | ps => match strings ps with
      | .ok xs => pure (some xs)
      | .error _ => throw "InvalidInput: predicates must be a list of strings"
  for field in ["witnesses", "packages"] do
    match j.getObjValD field with
    | .null | .obj _ => pure ()
    | _ => throw s!"InvalidInput: {field} must be an object"
  let order := (layerNames (fill src.U).T).filterMap (fun n =>
    if only.all (·.contains n) then src.U.D.T.regulated.find? (·.name == n) else none)
  let lines ← order.mapM (lineFor src (j.getObjValD "witnesses") sit (cited.map (·.1)) translation)
  pure ⟨unitIds, cited, translation, lines⟩

/-- What a report establishes, on every route: a `reachable` line has an admissible filled
witness, a `none` line is never reached under any admissible filling (for an unspecified
`p`: no gap; for deny or allow: the completion is never used), `UngroundedDefault` is
reported exactly for a reached, uncited deny or allow completion of a translation document,
and every citation names known units. -/
def ReportSound (src : ReportSource) (rep : ReportG src) : Prop :=
  (∀ l ∈ rep.lines, (l.reached = .reachable → ReachedSome src.U src.X l.r) ∧
    (l.reached = .never → NeverReached.{0} src.U src.X l.r) ∧
    (l.grounding = .ungrounded ↔ completionOf src.U l.r ≠ .unspecified ∧
      VE.Bridge.lookup (rep.cited.map (·.1)) l.r.name = none ∧ rep.translation = true ∧
      l.reached = .reachable)) ∧
  (∀ e ∈ rep.cited, e.1.2 ≠ [] ∧ ∀ u ∈ e.1.2, u ∈ rep.unitIds)

theorem report_sound (src : ReportSource) (rep : ReportG src) : ReportSound src rep := by
  refine ⟨fun l _ => ⟨l.sound_reached, l.sound_never, ?_⟩, fun e _ => ⟨e.2.1, fun u hu => ?_⟩⟩
  · rw [l.ground_eq, grounding_ungrounded_iff]
    cases l.reached <;> simp
  · have := List.all_eq_true.mp e.2.2 u hu
    simpa using this

/-! ## The norms route -/

/-- Decode a base situation of the norms route: an `unsaid__` table is a filling, never a
situation table (Python `UnspecifiedDocument.situation`, checked in name order first). -/
def situationFrom (s : SourceU) (m : Json) : Except String (SituationG s.U) := do
  if let .obj _ := m.getObjValD "relations" then
    for (n, _) in ← fields (m.getObjValD "relations") do
      if n.startsWith "unsaid__" then
        throw s!"InvalidModel(norm-defaults): {n} is a filling; supply it as a filling, not a table"
  let v := VE.Norms.Replay.baseModelVocabulary s.src.ne s.src.D
  let data ← VE.Bridge.decodeModelData v m
  if hv : data.valid v = true then
    if hb : backgroundValid s.U.D data.toModel = true then
      pure ⟨data.toModel, by
        rw [s.doc]
        exact VE.Norms.Replay.baseModel_valid s.src.ne s.src.D s.src.env _ (VE.Bridge.modelData_valid data v hv), hb⟩
    else throw (VE.Route.Wire.invalidModel "literals")
  else throw "model is not semantically admissible"

/-- A supplied filled model of `E‴_base` for `r` (the `witnesses` entry named `r`), replayed. -/
def suppliedWitness (s : SourceU) (witnesses : Json) (r : Regulated) :
    Except String (Option (PLift (ReachedSome s.U [] r) × WitnessRow)) :=
  match witnesses.getObjVal? r.name with
  | .ok w => do
    let d ← reachedFromU s (pure r.name) w
    if hd : d.r = r ∧ d.reached = true then
      pure (some (⟨hd.1 ▸ d.reachedSome hd.2⟩, witnessRow s.U d.M d.tuple))
    else pure none
  | .error _ => pure none

/-- The `reached:<p>` certificate over `Background_base(E‴) ++ Fill_T`, replayed. -/
def neverReached (s : SourceU) (environment norms packages : Json) (r : Regulated) :
    Option (PLift (NeverReached.{0} s.U [] r)) :=
  match decodePackageU s.U environment norms packages (reachedTarget s.U r) with
  | some c =>
    if ok : VE.Tableau.checkCertificate (envAt (fill s.U) 0) (baseBackgroundU s.U)
        (targetConclusion (reachedTarget s.U r)) c = true then
      some ⟨fun B hB vs hvs => normDefaults_wire_gaps_sound.{0} s.U r c ok B hB.1 vs hvs⟩
    else none
  | none => none

def normsSource (s : SourceU) (hs : s.profiled = true) (j : Json) : ReportSource :=
  { U := s.U, X := [], wfU := s.wfU hs, situation := situationFrom s, supplied := suppliedWitness s,
    never := neverReached s (j.getObjValD "environment") (j.getObjValD "norms") (j.getObjValD "packages") }

structure ReportU (j : Json) where
  s : SourceU
  decoded : decodeSourceU (j.getObjValD "environment") (j.getObjValD "norms") = .ok s
  profiled : s.profiled = true
  rep : ReportG (normsSource s profiled j)

/-- The norms-route report case: the source under the profile, then `reportWith`. -/
def reportFrom (j : Json) : Except String (ReportU j) :=
  match hs0 : decodeSourceU (j.getObjValD "environment") (j.getObjValD "norms") with
  | .error e => throw e
  | .ok s =>
    if hs : s.profiled = true then do
      let rep ← reportWith (normsSource s hs j) j
      pure ⟨s, hs0, hs, rep⟩
    else throw "UnsupportedProfile: norm-defaults@0 is required"

/-- `normDefaults_wire_report_sound`: the report of the document decoded from that very
input satisfies `ReportSound` with no extra base premises. -/
theorem normDefaults_wire_report_sound (j : Json) (rep : ReportU j) (_h : reportFrom j = .ok rep) :
    decodeSourceU (j.getObjValD "environment") (j.getObjValD "norms") = .ok rep.s ∧
      ReportSound (normsSource rep.s rep.profiled j) rep.rep :=
  ⟨rep.decoded, report_sound _ rep.rep⟩

end VE.NormDefaults.Wire
