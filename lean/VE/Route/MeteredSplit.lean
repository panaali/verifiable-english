-- ve-layer: 4 (states theorems on the metered runners of VE.Route.MeteredRun, which it imports)
import VE.Route.MeteredRun

/-! The `metered` mode's three runners (kb-4b; docs/kernel/kb-4b/REPORT.md).

`MeteredRun.runCase` answers every case as one of three runners does, chosen by the case's
environment (`runCase_split`):

* a frozen `ve.core@0` or `ve.core@0.1` envelope (`isLegacy`) by `runCaseLegacy`, which alone reads the
  frozen decoders (`Standalone.evaluableLegacy`);
* an environment whose deciding view reads `acts@0`, or lists a model-view profile the deciding view does not
  (`Standalone.readsApart`), by `runCaseActs`: today's runner, with the regulated extension read through
  `ActsHook.lexical` and the model view through `Standalone.modelEnvironment`;
* every other environment by `runCaseCurrent`, which references neither, nor any typing reduction: its validation
  is `validatedOver` of the deciding view with the regulated extension read through `ActsHook.plain`
  (`Standalone.evaluableCurrent`), and its model view is the deciding view (`Standalone.modelEnvironmentCurrent`).

The mode's entry (`runCaseReported`) dispatches the same way, and answers every case as before
(`runCaseReported_today`), so a held environment answers as the case with it in place does
(`reportedWith_prepare`, which `VE.Service.caseResultWith_entry` reads). -/

namespace VE.Service.Standalone
open Lean
open VE.Order.ProfileGate (bind_ok)

/-! #### `validated` before kb-4b

The frozen copy below is a proof helper: what "today's" `validated` means in `validated_today`. No product code reads
it. -/

namespace Today

/-- `Standalone.validated` as it was before kb-4b, verbatim. -/
def validated (environment : Json) (typing : Bool := false) : Except String Validated := do
  -- Typing only: other modes keep the gate's refusal of these statement profiles.
  let environment ← if typing then typingReduced environment else pure environment
  let view ← actsRead environment
  let e ← VE.Route.Gate.decodeEnvelope view
  for kind in ["sorts", "predicates", "constants"] do
    for (name, _) in ← VE.Bridge.fields (← e.vocabulary.getObjVal? kind) do
      if pythonReserved.contains name then
        throw s!"DuplicateDeclaration: Schema identifier '{name}' is reserved"
  let predicates ← VE.Bridge.fields (← e.vocabulary.getObjVal? "predicates")
  let mut v : Validated := { envelope := e, decodable := view }
  if e.profiles.contains "norms@0" &&
      predicates.any (fun (_, entry) => (entry.getObjVal? "regulated").isOk) then
    -- Check the regulated extension, then strip it: the family decoders see
    -- regulated predicates as ordinary ones.
    checkRegulated environment predicates
    v ← stripPredicates v.envelope v.decodable ["regulated"]
  checkDataFlagFields e.profiles predicates
  if typing && e.family == .closureNary then
    let (envelope, decodable) ← VE.Route.Typed.typingEnvironment v.envelope v.decodable
    v := { envelope, decodable }
  else if e.family == .closureNary && VE.Core.Layers.usesLayers v.decodable then
    -- The core decoder has neither layer: they are validated over the FOL
    -- projection by the FOL route's decoders, and the n-ary definitions over the
    -- core environment, as the core route does.
    let _ ← VE.Core.Layers.decodeLayered e.profiles v.decodable
    let layered := v.decodable
    v ← stripPredicates v.envelope v.decodable VE.Core.Layers.layerFields
    v := { v with layers := some layered }
  validateFamily v.envelope v.decodable
  pure v

end Today

/-- kb-4b moved `validated`'s body after the acts view into `validatedOver`, with the typing step passed in; every
mode that calls `validated` reads what it read before. -/
theorem validated_today (environment : Json) (typing : Bool) :
    validated environment typing = Today.validated environment typing := by
  cases typing <;> rfl

/-- The `regulated` check and the norms profile read the extension as before kb-4b (`regulatedOf_today`). -/
theorem checkRegulated_today (environment : Json) (predicates : List (String × Json)) :
    checkRegulated environment predicates = (do let _ ← regulatedOf environment predicates; pure ()) :=
  rfl

theorem profileTree_today (modelEnv : Json) :
    profileTree modelEnv = (do
      let predicates ← VE.Bridge.fields (← (← modelEnv.getObjVal? "vocabulary").getObjVal? "predicates")
      if predicates.any (fun (_, entry) => (entry.getObjVal? "regulated").isOk) then
        return some ⟨← regulatedOf modelEnv predicates, [], []⟩
      pure none) :=
  rfl

/-- kb-4b step 2 (1): `validated` without typing is `validatedPlain`, which references no typing reduction. -/
theorem validated_plain (environment : Json) : validated environment false = validatedPlain environment := by
  rfl

/-- The non-frozen validation of the evaluation modes is today's: `validated` of the deciding view. -/
theorem evaluableActs_today (environment : Json) :
    evaluableActs environment = (do validated (← VE.Compose.decidingEnvironment environment)) := by
  simp only [evaluableActs, validated_plain]

/-- An environment from which `acts@0` is not read is its own acts view. -/
theorem actsRead_plain (environment : Json)
    (h : (VE.Norms.Wire.actsProfiles true environment).isEmpty = true) :
    actsRead environment = .ok environment := by
  simp [actsRead, h, pure, Except.pure]

/-- The plain hook reads the regulated extension of an environment from which `acts@0` is not read as
`regulatedOf` does. -/
theorem regulatedOfWith_plain (environment : Json)
    (h : (VE.Norms.Wire.actsProfiles true environment).isEmpty = true) :
    regulatedOfWith VE.Norms.Wire.ActsHook.plain environment = regulatedOf environment := by
  have h' : VE.Norms.Wire.actsProfiles true environment = [] := List.isEmpty_iff.mp h
  funext predicates
  simp [regulatedOf, regulatedOfWith, regulatedBy, VE.Norms.Wire.ActsHook.plain, h',
    VE.Norms.Wire.actsFixed, pure, Except.pure, bind, Except.bind,
    VE.Norms.Wire.canonicalActIn_without_acts [] [] (by simp)]

theorem profileTreeWith_plain (environment : Json)
    (h : (VE.Norms.Wire.actsProfiles true environment).isEmpty = true) :
    profileTreeWith VE.Norms.Wire.ActsHook.plain environment = profileTree environment := by
  simp only [profileTree, profileTreeWith, regulatedOfWith_plain environment h]

/-- On a view from which `acts@0` is not read, the current runner's validation is `validatedPlain`. -/
theorem validatedCurrent_eq (view : Json)
    (h : (VE.Norms.Wire.actsProfiles true view).isEmpty = true) :
    validatedCurrent view = validatedPlain view := by
  have hp : VE.Norms.Wire.ActsHook.plain.profiles true view = .ok [] := by
    simp [VE.Norms.Wire.ActsHook.plain, List.isEmpty_iff.mp h, pure, Except.pure]
  unfold validatedCurrent validatedPlain
  rw [hp, actsRead_plain view h, regulatedOfWith_plain view h]
  rfl

/-- A list of known profiles names none of the statement profiles typing reads apart. -/
theorem typingReduced_inert (v : Json)
    (h : ∀ p ∈ (VE.Route.Gate.profilesOf v).toOption.getD [], VE.Route.Gate.known p = true) :
    typingReduced v = .ok v := by
  have hc : ∀ p, VE.Route.Gate.known p = false → p ∉ (VE.Route.Gate.profilesOf v).toOption.getD [] := by
    intro p hp hm
    have := h p hm
    rw [hp] at this; cases this
  simp [typingReduced, hc "risk@0" (by decide), hc "reports@0" (by decide), hc "alternatives@0" (by decide),
    hc "speech-acts@0" (by decide), hc "rights@0" (by decide), hc "soft-norms@0" (by decide),
    hc "readings@1" (by decide), hc "norm-defaults@0" (by decide), pure, Except.pure, bind, Except.bind]

/-- A view the route gate admits names no field beyond the envelope's four, so no `unit_schema`. -/
theorem decodeEnvelope_no_unit_schema (view : Json) (e : VE.Route.Gate.Envelope)
    (h : VE.Route.Gate.decodeEnvelope view = .ok e) :
    (view.getObjVal? "unit_schema").isOk = false := by
  unfold VE.Route.Gate.decodeEnvelope at h
  obtain ⟨u, hx, _⟩ := bind_ok h
  obtain ⟨fs, hfs, hk⟩ := VE.Order.ProfileGate.exactFields_keys (by decide) hx
  cases hv : view.getObjVal? "unit_schema" with
  | error _ => rfl
  | ok w =>
    obtain ⟨fs', hfs', hmem⟩ := VE.Order.ProfileGate.getObjVal_mem hv
    rw [hfs] at hfs'
    cases hfs'
    have := hk _ hmem
    simp at this

/-- On an environment the current runner takes (`readsApart` false) and whose deciding view `view` the
route gate admits, `modelEnvironment` is that view: no statement profile it reads apart is listed, the
view has no `unit_schema`, and typing reduces nothing. -/
theorem modelEnvironment_current (environment view : Json) (e : VE.Route.Gate.Envelope)
    (hD : VE.Compose.decidingEnvironment environment = .ok view)
    (hdrop : modelViewDropped environment view = false)
    (he : VE.Route.Gate.decodeEnvelope view = .ok e) :
    modelEnvironment environment = modelEnvironmentCurrent environment := by
  obtain ⟨_, hpv, hallowed⟩ := VE.Route.Gate.decodeEnvelope_sound view e he
  have hknown : ∀ p ∈ e.profiles, VE.Route.Gate.known p = true := hallowed.2.1
  have hunit := decodeEnvelope_no_unit_schema view e he
  have htyping : typingReduced view = .ok view := typingReduced_inert view (by
    rw [hpv]; exact hknown)
  unfold modelEnvironment modelEnvironmentCurrent
  cases hps : VE.Route.Gate.profilesOf environment with
  | error m => simp [bind, Except.bind]
  | ok ps =>
    have hout : ∀ p ∈ modelViewProfiles, p ∉ ps := by
      intro p hp
      have hnk : VE.Route.Gate.known p = false := by
        simp [modelViewProfiles] at hp
        rcases hp with rfl | rfl | rfl | rfl <;> decide
      have hne : e.profiles.contains p = false := by
        cases hm : e.profiles.contains p with
        | false => rfl
        | true => have := hknown p (List.contains_iff_mem.mp hm); rw [hnk] at this; cases this
      simp only [modelViewDropped, hps, hpv, Except.toOption, Option.getD, List.any_eq_false] at hdrop
      have := hdrop p hp
      simp only [hne, Bool.not_false, Bool.and_true, Bool.not_eq_true] at this
      intro hm
      simp at this
      exact this hm
    simp [hD, hout "risk@0" (by decide), hout "alternatives@0" (by decide),
      hout "readings@1" (by decide), hout "norm-defaults@0" (by decide), hunit, htyping, bind, Except.bind,
      pure, Except.pure]

end VE.Service.Standalone

namespace VE.Route.MeteredRun
open Lean
open VE.Order.ProfileGate (bind_ok)
open VE.Service.Standalone

theorem prepare_legacy (environment : Json) (h : isLegacy environment = true) :
    prepare environment = prepareLegacy environment := by
  simp [prepare, prepareLegacy, evaluable, h]

theorem prepare_acts (environment : Json) (h : isLegacy environment = false) :
    prepare environment = prepareActs environment := by
  simp [prepare, prepareActs, evaluable, h]

/-- Two prepared environments with one validation, equal whenever it accepts, answer every case alike. -/
theorem runWith_congr (p p' : Prepared) (j : Json) (hc : p.checked = p'.checked)
    (hp : ∀ c, p.checked = .ok c → p = p') : runWith (.ok p) j = runWith (.ok p') j := by
  cases hpc : p.checked with
  | ok c => rw [hp c hpc]
  | error m =>
    have hpc' : p'.checked = .error m := hc ▸ hpc
    simp only [runWith, hpc, hpc', bind, Except.bind, pure, Except.pure]

/-- kb-4b: on an environment the current runner takes, it answers every case as today's runner. -/
theorem runWith_prepare_current (environment j : Json) (hl : isLegacy environment = false)
    (ha : readsApart environment = false) :
    runWith (.ok (prepare environment)) j = runWith (.ok (prepareCurrent environment)) j := by
  rw [prepare_acts environment hl]
  have hchk : evaluableActs environment = evaluableCurrent environment := by
    unfold evaluableActs evaluableCurrent
    cases hD : VE.Compose.decidingEnvironment environment with
    | error m => rfl
    | ok view =>
      simp only [readsApart, hD, Bool.or_eq_false_iff, Bool.not_eq_false'] at ha
      exact (validatedCurrent_eq view ha.1).symm
  apply runWith_congr _ _ j hchk
  intro c hc
  simp only [prepareActs, prepareCurrent, prepareOf] at hc ⊢
  rw [hchk] at hc ⊢
  congr 1
  apply Thunk.ext
  simp only [Thunk.get]
  -- the validation accepted: the deciding view and its envelope
  unfold evaluableCurrent at hc
  obtain ⟨view, hD, hv⟩ := bind_ok hc
  simp only [readsApart, hD, Bool.or_eq_false_iff, Bool.not_eq_false'] at ha
  unfold validatedCurrent at hv
  obtain ⟨_, _, hv⟩ := bind_ok hv
  unfold validatedOver at hv
  obtain ⟨e, he, _⟩ := bind_ok hv
  rw [modelEnvironment_current environment view e hD ha.2 he]
  unfold modelEnvironmentCurrent
  cases hps : VE.Route.Gate.profilesOf environment with
  | error m => simp [bind, Except.bind]
  | ok ps => simp [hD, bind, Except.bind, profileTreeWith_plain view ha.1]

theorem legacyCase_ok (j environment : Json) (h : j.getObjVal? "environment" = .ok environment) :
    legacyCase j = isLegacy environment := by simp [legacyCase, h]

theorem actsCase_ok (j environment : Json) (h : j.getObjVal? "environment" = .ok environment) :
    actsCase j = readsApart environment := by simp [actsCase, h]

/-- The runner of each arm answers a case of that arm as today's runner (`runWith` of `prepare`). -/
theorem runWith_split (j : Json) :
    runWith (prepare <$> j.getObjVal? "environment") j =
      if legacyCase j then runWith (prepareLegacy <$> j.getObjVal? "environment") j
      else if actsCase j then runWith (prepareActs <$> j.getObjVal? "environment") j
      else runWith (prepareCurrent <$> j.getObjVal? "environment") j := by
  cases henv : j.getObjVal? "environment" with
  | error m => simp [legacyCase, actsCase, henv, Functor.map, Except.map]
  | ok environment =>
    simp only [legacyCase_ok j environment henv, actsCase_ok j environment henv, Functor.map, Except.map]
    cases hl : isLegacy environment with
    | true => simp [prepare_legacy environment hl]
    | false =>
      cases ha : readsApart environment with
      | true => simp [prepare_acts environment hl]
      | false => simpa using runWith_prepare_current environment j hl ha

/-- kb-4b step 2 (2) and (3): the `metered` runner is the frozen-envelope runner on a frozen envelope, the acts
runner on an environment it reads apart, and the current runner on every other case, each answering exactly
as `runCase` does. -/
theorem runCase_split (j : Json) :
    runCase j = if legacyCase j then runCaseLegacy j else if actsCase j then runCaseActs j
      else runCaseCurrent j :=
  runWith_split j

/-- The mode's entry answers every case as before kb-4b: `reportedWith` of today's prepared environment. -/
theorem runCaseReported_today (j : Json) :
    runCaseReported j = reportedWith (prepare <$> j.getObjVal? "environment") j := by
  unfold reportedWith
  rw [runWith_split j]
  unfold runCaseReported runCaseReportedLegacy runCaseReportedActs runCaseReportedCurrent reportedWith
  cases legacyCase j <;> cases actsCase j <;> rfl

/-- A case answered with what its own environment decodes to is answered as it was sent. -/
theorem reportedWith_prepare (j environment : Json) (h : j.getObjVal? "environment" = .ok environment) :
    reportedWith (.ok (prepare environment)) j = runCaseReported j := by
  rw [runCaseReported_today]
  simp [h, Functor.map, Except.map]

end VE.Route.MeteredRun
