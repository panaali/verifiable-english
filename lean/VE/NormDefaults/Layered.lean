import VE.NormDefaults.Report
import VE.NormDefaults.Explain
import VE.Rights.Wire

/-! The soft and rights branches of `norm-defaults@0` (docs/spec/norm-defaults.md 2.3 and
3.3): `fill` runs last, so the soft route checks `fill (soften T)` and the rights route
`fill (soften (correlate D))`.

The source is decoded by the route's own unchanged decoder with each `unspecified`
completion read as the placeholder `deny` (`placeholderJson`), then the reserved names and
the author limits of section 8 are checked on the softened tree (`checkAuthorN`, counting
the route's generated predicates) and `WellFormedU` is required. The route's extra base
premises `X` are soft's `Soft_T` with `Coh_T` regenerated on `fill U` (its selections read
unsaid atoms where guards mention unspecified predicates, 3.3) and, on the rights route,
the limitation premises; the base background is `Background_base(E‴) ++ X ++ Fill_T`, in
Python's generator order (soft, rights, norm-defaults).

Evidence on these routes is a base situation of the route's base vocabulary (decision and
rights-generated predicates included, no unsaid tables) with a separate `filling`; a
filling is admissible when `Fill_T` and `X` hold on the filled situation. Every case
replays against the regenerated document:

* `layeredElaborate`: the regenerated outputs of `fill U`, the labelled `X`, and the
  bindings packages use (`environment_id`, `document_hash`, `base_environment`);
* `replayConflictX`: certificates for every target of `fill U` over the base background
  give CONFLICT-FREE under every admissible filling (`layered_conflict_sound`); a filled
  witness gives CONFLICT (`layered_witness_sound`), with the English fields of the norms
  route (`conflictFields`);
* `replayStatusX`: `table3` and enumeration give SETTLED (`SettledAs`, over every filling
  `Fill_T` admits, so also over those `X` admits), two admissible fillings give
  UNDECIDED (`UndecidedAtX`); the row carries `statusFields`, as on the norms route;
* the report (`layeredSource`, `layered_report_sound`). -/
namespace VE.NormDefaults.Wire
open Lean
open VE.Norms VE.Route
open VE.Bridge (Entity fields strings)
open VE.SoftNorms (SoftDoc SoftNode soften)
universe u

/-! ## `Soft_T` on the filled tree -/

/-- The coherence premise of a colliding pair regenerated on `fill U` (Python
`UnspecifiedSoftDocument._install_soft_premises`): the selections of both rules in `T‴`,
expanded through `T‴`. -/
def cohPremiseU (U : UDoc) (D : SoftDoc) (M N : SoftNode) : VE.Formula :=
  let sel := fun (K : SoftNode) =>
    subst (fill U).T (size (fill U)) (selects (fill U).T (fuel (fill U).T) (VE.SoftNorms.primeNode D K))
  bindAll (VE.SoftNorms.actSorts D M) (.not (.and (sel M) (sel N)))

/-- `Soft_T = Exc_T ++ Coh_T` with `Coh_T` on `fill U`, labelled as the soft route labels it. -/
def softLabelledU (U : UDoc) (D : SoftDoc) : List (String × VE.Formula) :=
  (VE.SoftNorms.Wire.excLabels D).zip (VE.SoftNorms.excPremises D) ++
    (VE.SoftNorms.collidingPairs D).map (fun (M, N) => (VE.SoftNorms.Wire.cohLabel M N, cohPremiseU U D M N))

/-! ## The decoded source -/

/-- A soft or rights source under the profile: `U = (soften D, unspec)`, the labelled extra
base premises, the base situation vocabulary and the bindings of its packages. -/
structure LayeredU where
  route : String
  D : SoftDoc
  U : UDoc
  wfU : WellFormedU U = true
  labelled : List (String × VE.Formula)
  rightsCount : Nat
  sitVocab : VE.Bridge.Vocabulary
  sitValid : ∀ M : VE.FiniteModel Entity, M.Valid sitVocab.environment → M.Valid (envAt U.D 0)
  baseEnv : Json
  envId : String
  docHash : String

def LayeredU.X (L : LayeredU) : List VE.Formula := L.labelled.map (·.2)

/-- `Background_base(E‴) ++ X ++ Fill_T`. -/
def LayeredU.background (L : LayeredU) : List VE.Formula :=
  backgroundBase (fill L.U) ++ L.X ++ fillPremises L.U

/-- `E‴_base` JSON: the route's base environment JSON plus one `unsaid__p` per unspecified `p`. -/
def withUnsaid (U : UDoc) (base : Json) : Except String Json := do
  let vocab ← base.getObjVal? "vocabulary"
  let preds ← fields (← vocab.getObjVal? "predicates")
  let extra := U.unspec.map fun p => (unsaidName p, Json.mkObj [("arguments", toJson (sortsOf U.D p)),
    ("description", .str (unsaidDescription p))])
  pure (base.setObjVal! "vocabulary" (vocab.setObjVal! "predicates" (Json.mkObj (preds ++ extra))))

/-- The unspecified predicates of the softened tree, in its regulated order. -/
def unspecOf (environment : Json) (Dd : Doc) : List String :=
  (Dd.T.regulated.map Regulated.name).filter ((unspecifiedNames environment).contains ·)

/-- The soft branch: `soften` over the placeholder completions, then `fill`. -/
def decodeSoftU (environment norms : Json) : Except String LayeredU := do
  let env' ← placeholderJson environment
  let src ← VE.SoftNorms.Wire.decodeSoftSource env' norms
  let U : UDoc := ⟨soften src.D, unspecOf environment (soften src.D)⟩
  checkAuthorN environment (VE.SoftNorms.decisions src.D).length U
  if h : WellFormedU U = true then
    let profiles := profilesOf environment
    let baseEnv ← withUnsaid U (← VE.SoftNorms.Wire.basePrimeJson src.D env')
    let envId ← VE.Route.Wire.environmentId profiles (← canonicalEnvironmentJsonU environment)
    let docHash ← VE.SoftNorms.Wire.softDocumentHash profiles environment norms
    pure ⟨"soft-norms@0", src.D, U, h, softLabelledU U src.D, 0,
      VE.SoftNorms.Wire.primeModelVocabulary src.se src.D, VE.SoftNorms.Wire.primeModel_valid src,
      baseEnv, envId, docHash⟩
  else throw "InvalidInput: norm-defaults document is not well formed"

/-- The rights branch: `correlate` and `soften` over the placeholder completions, then `fill`;
the limitation premises stay in the base. -/
def decodeRightsU (environment document : Json) : Except String LayeredU := do
  let env' ← placeholderJson environment
  let src ← VE.Rights.Wire.decodeRightsSource env' document
  let D := VE.Rights.correlate src.D
  let U : UDoc := ⟨soften D, unspecOf environment (soften D)⟩
  checkAuthorN environment ((VE.Rights.genDecls src.D).length + (VE.SoftNorms.decisions D).length) U
  if h : WellFormedU U = true then
    if hg : VE.Rights.Wire.genFresh src.D = true then
      let profiles := profilesOf environment
      let baseEnv ← withUnsaid U (← VE.Rights.Wire.basePrimeJsonR src.D env')
      let envId ← VE.Route.Wire.environmentId profiles (← canonicalEnvironmentJsonU environment)
      let docHash ← VE.Rights.Wire.rightsDocumentHash profiles environment document
      let rights := VE.Rights.limPremisesLabelled src.D
      pure ⟨"rights@0", D, U, h, softLabelledU U D ++ rights, rights.length,
        VE.Rights.Wire.primeModelVocabularyR src.re src.D, (fun M h => VE.Rights.Wire.primeModelR_valid src M hg h),
        baseEnv, envId, docHash⟩
    else throw "InvalidInput: a rights-generated predicate is a layer symbol"
  else throw "InvalidInput: norm-defaults document is not well formed"

/-- The branch an environment under the profile takes, if it is soft or rights. -/
def layeredRoute (environment : Json) : Option String :=
  let ps := profilesOf environment
  if ps.contains "rights@0" then some "rights@0"
  else if ps.contains "soft-norms@0" then some "soft-norms@0"
  else none

/-- Decode a case's source on its branch: `norms` on the soft route, `document` on the
rights route, as those routes read them. -/
def decodeLayered (j : Json) : Except String LayeredU := do
  let environment ← j.getObjVal? "environment"
  match layeredRoute environment with
  | some "rights@0" => decodeRightsU environment (j.getObjValD "document")
  | some _ => decodeSoftU environment (j.getObjValD "norms")
  | none => throw "UnsupportedProfile: the layered norm-defaults branch needs soft-norms@0 or rights@0"

/-- The source JSON the bindings name: `norms` or `document`. -/
def sourceField (L : LayeredU) : String := if L.route == "rights@0" then "document" else "norms"

/-! ## Regenerated outputs -/

def layeredElaborate (L : LayeredU) : List (String × Json) :=
  regeneratedU L.U ++
  [("soft", Json.arr ((L.labelled.take (L.labelled.length - L.rightsCount)).map (fun (l, a) =>
      Json.mkObj [("label", .str l), ("ast", enc a)])).toArray),
   ("rights", Json.arr ((L.labelled.drop (L.labelled.length - L.rightsCount)).map (fun (l, a) =>
      Json.mkObj [("label", .str l), ("ast", enc a)])).toArray),
   ("environment_id", .str L.envId), ("document_hash", .str L.docHash),
   ("base_environment", L.baseEnv)]

/-! ## Admissibility with `X` -/

def ConflictFreeX (U : UDoc) (X : List VE.Formula) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleX U X B → ConflictFree (fill U) B

def UndecidedAtX (U : UDoc) (X : List VE.Formula) (B : VE.Structure.{u}) (r : Regulated)
    (vs : List B.Carrier) : Prop :=
  ∃ F₁ F₂ : FillTables U B,
    BaseAdmissibleX U X (withFill U B F₁) ∧ BaseAdmissibleX U X (withFill U B F₂) ∧
    (outcomeBase (fill U) r.name).denote (withFill U B F₁) (tupleVal vs) ∧
    ¬ (outcomeBase (fill U) r.name).denote (withFill U B F₂) (tupleVal vs)

/-- A certificate over the layered base background for `∀x̄. ¬φ` holds in every admissible
structure. -/
theorem layered_cert_sound (L : LayeredU) (ss : List String) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (ok : VE.Tableau.checkCertificate (envAt (fill L.U) 0) L.background (bindAll ss (.not φ)) c = true)
    (B : VE.Structure.{u}) (hB : BaseAdmissibleX L.U L.X B) (vs : List B.Carrier) (hvs : VE.TupleTyped B ss vs) :
    ¬ φ.denote B (tupleVal vs) := by
  have he := VE.Tableau.checkCertificate_sound.{u} _ _ _ c ok B hB.1.1.1 (fun a ha => by
    rcases List.mem_append.mp ha with ha | ha
    · rcases List.mem_append.mp ha with ha | ha
      · exact hB.1.1.2 a ha
      · exact hB.2 a ha
    · exact hB.1.2 a ha)
  exact (bindAll_denote_nil B _ _).mp he vs hvs

/-- A target of `fill U` true at a typed tuple of a structure contradicts `ConflictFree`
there. -/
theorem target_not_conflictFree (U : UDoc) (h : WellFormed (fill U) = true) (t : String × List String × VE.Formula)
    (ht : t ∈ targets (fill U)) (B : VE.Structure.{u}) (vs : List B.Carrier)
    (hvs : VE.TupleTyped B t.2.1 vs) (hw : t.2.2.denote B (tupleVal vs)) : ¬ ConflictFree (fill U) B := by
  have _ := h
  intro hcf
  rcases List.mem_append.mp ht with ht | ht
  · obtain ⟨q, hq, he⟩ := List.mem_filterMap.mp ht
    cases q with
    | defn _ => cases he
    | reg r =>
      simp only [Option.some.injEq] at he
      subst he
      exact hcf.1 r (mem_syms_reg hq) vs hvs hw
  · obtain ⟨pr, hpr, rfl⟩ := List.mem_map.mp ht
    exact hcf.2 pr hpr vs hvs hw

/-! ## Packages -/

/-- One target's package bound to the source (`environment_id`, the route's
`document_hash`, the target) and to `E‴_base`, the layered base background and the
target's conclusion. -/
def decodePackageX (L : LayeredU) (packages : Json) (t : String × List String × VE.Formula) :
    Option VE.Tableau.Certificate := Id.run do
  let some baseProfiles := (strings (L.baseEnv.getObjValD "profiles")).toOption | none
  let package := packages.getObjValD t.1
  unless package.getObjValD "environment_id" == .str L.envId &&
      package.getObjValD "document_hash" == .str L.docHash &&
      package.getObjValD "target" == .str t.1 do return none
  let some c := (VE.CertificateWire.decodeCertificate (package.getObjValD "certificate")).toOption | none
  match VE.Route.Wire.bindingOk baseProfiles L.baseEnv (L.background.map enc) (enc (targetConclusion t))
      c.environment_id c.premise_meaning_ids c.conclusion_meaning_id with
  | .ok () => some c
  | .error _ => none

def acceptedX (L : LayeredU) (packages : Json) (t : String × List String × VE.Formula) : Bool :=
  match decodePackageX L packages t with
  | some c => VE.Tableau.checkCertificate (envAt (fill L.U) 0) L.background (targetConclusion t) c
  | none => false

/-- CONFLICT-FREE: every target of `fill U` has an accepted certificate. -/
def conflictFreeX (L : LayeredU) (packages : Json) : Bool := (targets (fill L.U)).all (acceptedX L packages)

theorem layered_conflict_sound (L : LayeredU) (packages : Json) (h : conflictFreeX L packages = true) :
    ConflictFreeX.{u} L.U L.X := by
  intro B hB
  have hcert : ∀ t ∈ targets (fill L.U), ∀ vs : List B.Carrier, VE.TupleTyped B t.2.1 vs →
      ¬ t.2.2.denote B (tupleVal vs) := by
    intro t ht vs hvs
    have ha := List.all_eq_true.mp h t ht
    unfold acceptedX at ha
    split at ha
    · rename_i c _
      exact layered_cert_sound L t.2.1 t.2.2 c ha B hB vs hvs
    · cases ha
  have hv := valid_of_wellFormed _ (fill_wellFormed L.U L.wfU)
  refine ⟨fun r hr vs hvs => ?_, fun pr hpr vs hvs => ?_⟩
  · exact hcert _ (List.mem_append_left _ (List.mem_filterMap.mpr ⟨.reg r, hv.regulated r hr, rfl⟩)) vs hvs
  · exact hcert _ (List.mem_append_right _ (List.mem_map.mpr ⟨pr, hpr, rfl⟩)) vs hvs

/-- The first target without an accepted certificate, for the `detail` field. -/
def firstFailureX (L : LayeredU) (packages : Json) : Option String :=
  ((targets (fill L.U)).find? (fun t => !acceptedX L packages t)).map fun t =>
    if (decodePackageX L packages t).isSome then s!"invalid certificate for {t.1}"
    else s!"missing certificate for {t.1}"

/-! ## Situations and fillings -/

/-- A base situation of the route's base vocabulary; an `unsaid__` table is a filling. -/
def situationX (L : LayeredU) (m : Json) : Except String (SituationG L.U) := do
  if let .obj _ := m.getObjValD "relations" then
    for (n, _) in ← fields (m.getObjValD "relations") do
      if n.startsWith "unsaid__" then
        throw s!"InvalidModel(norm-defaults): {n} is a filling; supply it as a filling, not a table"
  let data ← VE.Bridge.decodeModelData L.sitVocab m
  if hv : data.valid L.sitVocab = true then
    if hb : backgroundValid L.U.D data.toModel = true then
      pure ⟨data.toModel, L.sitValid _ (VE.Bridge.modelData_valid data L.sitVocab hv), hb⟩
    else throw (VE.Route.Wire.invalidModel "literals")
  else throw "model is not semantically admissible"

/-- A typed tuple of `sorts` from entity ids. -/
def tupleOf (M : VE.FiniteModel Entity) (sorts : List String) (j : Json) :
    Except String {vs : List Entity // vs ∈ allTuples M sorts} := do
  let ids ← strings j
  let vs := sorts.zip ids
  if h : ids.length == sorts.length && VE.Bridge.tupleCheck M sorts vs then
    pure ⟨vs, (mem_allTuples M sorts vs).mpr
      ((VE.Bridge.tupleCheck_iff M _ _).mp (by simp only [Bool.and_eq_true] at h; exact h.2))⟩
  else throw "InvalidInput: tuple has the wrong length or sort"

/-- A filled situation: the situation, its `filling` and the check that the filling is
admissible (`Fill_T` and `X`); an inadmissible filling is `InvalidModel`, never evidence. -/
structure FilledX (L : LayeredU) where
  S : SituationG L.U
  F : FiniteFill L.U Entity
  fill_ok : fillValid L.U S.M F = true
  extra_ok : extraValid L.U L.X S.M F = true

def filledX (L : LayeredU) (w : Json) : Except String (FilledX L) := do
  let S ← situationX L (← w.getObjVal? "model")
  let F ← decodeFilling L.U S.M (w.getObjValD "filling")
  if hf : fillValid L.U S.M F = true then
    if hx : extraValid L.U L.X S.M F = true then pure ⟨S, F, hf, hx⟩
    else
      let soft := (L.labelled.take (L.labelled.length - L.rightsCount)).map (·.2)
      throw (VE.Route.Wire.invalidModel (if extraValid L.U soft S.M F then "rights" else "soft"))
  else throw (VE.Route.Wire.invalidModel "unsaid")

theorem FilledX.admissible {L : LayeredU} (w : FilledX L) :
    BaseAdmissibleX L.U L.X (withFill L.U w.S.M.asStructure (finFill w.S.M w.F)) :=
  admissibleX_of_fill L.U L.wfU L.X w.S.M w.S.valid w.S.background w.F w.fill_ok w.extra_ok

/-! ## CONFLICT witnesses -/

/-- A filled witness of a target: CONFLICT when the target is true at the tuple; with the
filled model, the target formula and the tuple (for `conflictFields`). -/
def witnessConflictX (L : LayeredU) (w : Json) :
    Except String (String × Option (PLift (¬ ConflictFreeX.{0} L.U L.X)) ×
      (VE.FiniteModel Entity × VE.Formula × List Entity)) := do
  let fw ← filledX L w
  let name ← VE.Bridge.stringField w "target"
  match hfind : (targets (fill L.U)).find? (·.1 == name) with
  | none => throw s!"InvalidInput: unknown conflict target {name}"
  | some t =>
    let ⟨vs, hvs⟩ ← tupleOf fw.S.M t.2.1 (← w.getObjVal? "tuple")
    if hw : t.2.2.eval (fw.S.M.withFill fw.F) (tupleVal vs) = true then
      pure (name, some ⟨fun hc => target_not_conflictFree L.U (fill_wellFormed L.U L.wfU) t
        (List.mem_of_find?_eq_some hfind) _ vs
        ((tupleTyped_relation fw.S.M.asStructure _ _ vs).mpr ((mem_allTuples fw.S.M _ vs).mp hvs))
        ((eval_withFill L.U fw.S.M fw.F _ _).mp hw) (hc _ fw.admissible)⟩, fw.S.M.withFill fw.F, t.2.2, vs)
    else pure (name, none, fw.S.M.withFill fw.F, t.2.2, vs)

/-! ## Statuses -/

structure StatusX (L : LayeredU) where
  S : SituationG L.U
  r : Regulated
  vs : List Entity
  typed : VE.TupleTyped S.M.asStructure r.sorts vs
  status : Status
  sound₁ : ∀ b, status = .settled b → SettledAs.{0} L.U S.M.asStructure r vs b
  sound₂ : status = .undecided → UndecidedAtX.{0} L.U L.X S.M.asStructure r vs

/-- The status of `p` at a tuple of a base situation, by `table3`, `enumerate`, or
`undecided` with admissible fillings `yes` and `no`. -/
def replayStatusX (L : LayeredU) (j : Json) : Except String (StatusX L) := do
  let S ← situationX L (← j.getObjVal? "model")
  let name ← VE.Bridge.stringField j "predicate"
  let method ← VE.Bridge.stringField j "method"
  match hfind : L.U.D.T.regulated.find? (·.name == name) with
  | none => throw s!"InvalidInput: unknown regulated predicate {name}"
  | some r =>
    let ⟨vs, hvs⟩ ← tupleOf S.M r.sorts (← j.getObjVal? "tuple")
    have hmem : r ∈ L.U.D.T.regulated := List.mem_of_find?_eq_some hfind
    have htyped : VE.TupleTyped S.M.asStructure r.sorts vs := (mem_allTuples S.M r.sorts vs).mp hvs
    let unknown : StatusX L := ⟨S, r, vs, htyped, .unknown, (fun _ h => by cases h), (fun h => by cases h)⟩
    if method == "table3" then
      match h3 : table3 L.U S.M r.name vs with
      | some b => pure ⟨S, r, vs, htyped, .settled b, (fun b' h => by
          cases h
          exact settled_of_table3 L.U L.wfU S.M S.valid S.background r hmem vs htyped b h3), (fun h => by cases h)⟩
      | none => pure unknown
    else if method == "enumerate" then
      match he : enumerateSettled L.U S.M r.name vs with
      | some b => pure ⟨S, r, vs, htyped, .settled b, (fun b' h => by
          cases h
          exact settled_of_enumeration L.U L.wfU S.M S.valid S.background r hmem vs htyped b he),
          (fun h => by cases h)⟩
      | none => pure unknown
    else if method == "undecided" then
      let F₁ ← decodeFilling L.U S.M (j.getObjValD "yes")
      let F₂ ← decodeFilling L.U S.M (j.getObjValD "no")
      if hc : fillValid L.U S.M F₁ = true ∧ fillValid L.U S.M F₂ = true ∧
          extraValid L.U L.X S.M F₁ = true ∧ extraValid L.U L.X S.M F₂ = true ∧
          (outcomeBase (fill L.U) r.name).eval (S.M.withFill F₁) (tupleVal vs) = true ∧
          (outcomeBase (fill L.U) r.name).eval (S.M.withFill F₂) (tupleVal vs) = false then
        pure ⟨S, r, vs, htyped, .undecided, (fun _ h => by cases h), fun _ =>
          ⟨finFill S.M F₁, finFill S.M F₂,
            admissibleX_of_fill L.U L.wfU L.X S.M S.valid S.background F₁ hc.1 hc.2.2.1,
            admissibleX_of_fill L.U L.wfU L.X S.M S.valid S.background F₂ hc.2.1 hc.2.2.2.1,
            (eval_withFill L.U S.M F₁ _ _).mp hc.2.2.2.2.1, fun hd => by
              have := (eval_withFill L.U S.M F₂ _ _).mpr hd
              rw [hc.2.2.2.2.2] at this
              cases this⟩⟩
      else pure unknown
    else throw s!"InvalidInput: unknown status method {method}"

/-! ## The report -/

/-- A supplied witness for `r`: a situation, its `filling` and the `tuple`. -/
def suppliedX (L : LayeredU) (witnesses : Json) (r : Regulated) :
    Except String (Option (PLift (ReachedSome L.U L.X r) × WitnessRow)) :=
  match witnesses.getObjVal? r.name with
  | .ok w => do
    let fw ← filledX L w
    let ⟨vs, hvs⟩ ← tupleOf fw.S.M r.sorts (← w.getObjVal? "tuple")
    if hr : (reachedF L.U r.name).eval (fw.S.M.withFill fw.F) (tupleVal vs) = true then
      pure (some (⟨reachedSome_of_fill L.U L.wfU L.X fw.S.M fw.S.valid fw.S.background r vs fw.F hvs
        fw.fill_ok fw.extra_ok hr⟩, witnessRow L.U (fw.S.M.withFill fw.F) vs))
    else pure none
  | .error _ => pure none

/-- The `reached:<p>` certificate over the layered base background. -/
def neverX (L : LayeredU) (packages : Json) (r : Regulated) : Option (PLift (NeverReached.{0} L.U L.X r)) :=
  match decodePackageX L packages (reachedTarget L.U r) with
  | some c =>
    if ok : VE.Tableau.checkCertificate (envAt (fill L.U) 0) L.background
        (targetConclusion (reachedTarget L.U r)) c = true then
      some ⟨fun B hB vs hvs => layered_cert_sound L r.sorts (reachedF L.U r.name) c ok B hB vs hvs⟩
    else none
  | none => none

def layeredSource (L : LayeredU) (packages : Json) : ReportSource :=
  { U := L.U, X := L.X, wfU := L.wfU, situation := situationX L, supplied := suppliedX L,
    never := neverX L packages }

theorem layered_report_sound (L : LayeredU) (packages : Json) (rep : ReportG (layeredSource L packages)) :
    ReportSound (layeredSource L packages) rep := report_sound _ rep

/-! ## Dispatch -/

/-- The `norm-defaults-*` kinds of a layered document that this branch answers itself, `none` for any other kind;
the dispatch of a choice's inner case under the readings completion (`Readings.Run.choiceInnerX`) uses it too, so both
answer each kind alike. The soft branch's `admission` and `norm-defaults-certificate` are dispatched before it, by
`NormDefaults.Admission.softCase` (`Run.runCase`). -/
def layeredCase (L : LayeredU) (id kind : String) (j : Json) : Except String (Option Json) := do
  let packages := j.getObjValD "packages"
  if kind == "norm-defaults-elaborate" then
    return some <| VE.Route.Wire.ok id (layeredElaborate L)
  if kind == "norm-defaults-conflict" && (j.getObjVal? "witness").toBool then
    let (target, w, M, φ, vs) ← witnessConflictX L (← j.getObjVal? "witness")
    return some <| VE.Route.Wire.ok id ([("verdict", .str (if w.isSome then "CONFLICT" else "UNKNOWN")),
      ("target", .str target), ("targets", toJson ((targets (fill L.U)).map (·.1)))] ++
      if w.isSome then conflictFields L.U M target φ vs else [])
  if kind == "norm-defaults-conflict" then
    let free := conflictFreeX L packages
    return some <| VE.Route.Wire.ok id ([("verdict", .str (if free then "CONFLICT-FREE" else "UNKNOWN")),
      ("targets", toJson ((targets (fill L.U)).map (·.1)))] ++
      match firstFailureX L packages with
      | some d => if free then [] else [("detail", .str d)]
      | none => [])
  if kind == "norm-defaults-status" then
    let d ← replayStatusX L j
    let fillings ← if d.status = .undecided then
        some <$> ((·, ·) <$> decodeFilling L.U d.S.M (j.getObjValD "yes") <*>
          decodeFilling L.U d.S.M (j.getObjValD "no"))
      else pure none
    return some <| VE.Route.Wire.ok id ([("point_status", .str d.status.label), ("predicate", .str d.r.name)] ++
      statusFields L.U d.S.M d.r.name d.vs (d.status != .undecided && d.status != .unknown) fillings)
  if kind == "norm-defaults-report" then
    let rep ← reportWith (layeredSource L packages) j
    return some <| VE.Route.Wire.ok id rep.toJson
  return none

/-- A `norm-defaults-*` case on the soft or rights branch. -/
def runLayered (id kind : String) (j : Json) : Except String Json := do
  let L ← decodeLayered j
  match ← layeredCase L id kind j with
  | some a => pure a
  | none => throw s!"UnsupportedProfile: case kind {kind} is not available on the {L.route} norm-defaults branch"

end VE.NormDefaults.Wire
