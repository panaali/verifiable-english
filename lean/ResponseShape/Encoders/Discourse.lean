import ResponseShape.Encoders.Route

/-! The `discourse` mode (`Discourse.Run.runCaseReported`) against `discourse.json#/row`. A case off
the discourse path is the route mode's. -/

namespace ResponseShape.Encoders.Discourse
open Lean ResponseShape ResponseShape.Skeletons
open VE.Discourse VE.Discourse.Run

variable {req : Json}

/-- The route mode's rows, off the discourse path, are rows of this mode. -/
theorem of_route {v : Json} (hp : usesDiscoursePath req = false) (h : Fits req Skeletons.route v) :
    Fits req Skeletons.discourse v :=
  Fits.onCaseE (by simpa [CaseCond.holds, CaseDecider.fn] using hp) h

theorem references_fits (front : Json) (pending : List (String × String)) :
    Fits req (.arr [] (skel% "discourse.json#/$defs/reference")) (referencesJson front pending) := by
  unfold referencesJson
  fits

/-- Every admission's reference lines are `referencesJson`'s (or none, for a `@1` document). -/
theorem admitDiscourse_references (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (n : Nat) :
    OkP (fun res : Admitted => Fits req (.arr [] (skel% "discourse.json#/$defs/reference")) res.references)
      (admitDiscourse profiles environment rv j n) := by
  cases n <;> unfold admitDiscourse admitAt <;> simp only [] <;> okfits
  all_goals first
    | (apply OkP.map; intro a; exact Fits.arrOf (fun x hx => by simp at hx))
    | (unfold admit2; okfits; exact references_fits _ _)

/-! ### The verdicts and statuses of an admission

A reading-dependent verdict is `UNKNOWN (joint choices)` (`readingVerdicts`); a unit's status is a
loaded status word (`statusOf`): the loader gives each unit one (`Loader.compileUnit`,
`Loader.loadFront`) and every admission keeps them (`admitDiscourse_status`). -/

theorem readingVerdict_fits (res : Admitted) {p : String × String} (h : p ∈ readingVerdicts res) :
    Fits req (.strIn ["UNKNOWN (joint choices)"]) (.str p.2) := by
  unfold readingVerdicts at h
  split at h
  · split at h
    · simp only [List.mem_append, List.mem_map, List.mem_cons, List.not_mem_nil, or_false] at h
      rcases h with ⟨_, _, rfl⟩ | rfl <;> fits
    · cases h
  · cases h

abbrev statusWords : List String := ["CHECKED", "OPEN", "LABELLED", "UNFORMALISED"]

/-- The words a discourse document's loaded units carry (`DDoc.status`). -/
def StatusesOk (D : DDoc) : Prop := ∀ p ∈ D.status, p.2 ∈ statusWords

theorem loadedStatus_mem {D : DDoc} (hs : StatusesOk D) (u : String) : loadedStatus D u ∈ statusWords := by
  unfold loadedStatus
  split
  · exact hs _ (List.mem_of_find?_eq_some ‹_›)
  · split <;> decide

theorem statusOf_fits (res : Admitted) (hs : StatusesOk res.doc) (u : String) :
    Fits req (.strIn statusWords) (.str (statusOf res u)) := by
  unfold statusOf unitStatus
  refine Fits.strIn ?_
  split
  · decide
  split
  · decide
  · decide
  split
  · decide
  split <;> exact loadedStatus_mem hs _

theorem compileUnit_status (rv : VE.Route.Wire.RouteVocabulary) (ps : List String) (envId source : String)
    (openNames : List String) (cursor : Nat) (u : Json) :
    OkP (fun x : Loader.Unit₀ => x.status ∈ statusWords) (Loader.compileUnit rv ps envId source openNames cursor u) := by
  unfold Loader.compileUnit
  okfits
  all_goals dsimp only
  all_goals (repeat' split) <;> decide

theorem compileUnits_status (rv : VE.Route.Wire.RouteVocabulary) (ps : List String) (envId source : String)
    (openNames parents : List String) :
    ∀ (us : List Json) (cursor : Nat), OkP (fun xs : List Loader.Unit₀ => ∀ x ∈ xs, x.status ∈ statusWords)
      (Loader.compileUnits rv ps envId source openNames parents cursor us)
  | [], cursor => by
    unfold Loader.compileUnits
    split
    · exact OkP.ok (by simp)
    · exact OkP.error
  | u :: us, cursor => by
    unfold Loader.compileUnits
    okfits
    rename_i parts _ acc hfold rest hrest _
    intro x hx
    rcases List.mem_append.mp hx with hx | hx
    · refine OkP.foldlM (I := fun acc : List Loader.Unit₀ × Nat => ∀ x ∈ acc.1, x.status ∈ statusWords)
        (fun s p hs => ?_) parts ([], cursor) (by simp) acc hfold x hx
      refine OkP.bind fun y hy => ?_
      have := compileUnit_status rv ps envId source openNames s.2 p y hy
      refine OkP.ite (fun _ => OkP.throw_bind) (fun _ => OkP.bind fun _ _ => OkP.pure ?_)
      intro z hz
      rcases List.mem_append.mp hz with hz | hz
      · exact hs z hz
      · simp only [List.mem_cons, List.not_mem_nil, or_false] at hz; subst hz; exact this
    · exact compileUnits_status rv ps envId source openNames parents us _ rest hrest x hx

theorem loadFront_status (rv : VE.Route.Wire.RouteVocabulary) (ps : List String) (envId : String) (front : Json)
    (source : String) (fences : List (String × String)) :
    OkP (fun F : Loader.Front => ∀ p ∈ F.status, p.2 ∈ statusWords)
      (Loader.loadFront rv ps envId front source fences) := by
  unfold Loader.loadFront
  okfits
  all_goals
    intro p hp
    simp only [List.mem_map] at hp
    obtain ⟨x, hx, rfl⟩ := hp
    dsimp only
    split
    · split <;> decide
    · exact compileUnits_status _ _ _ _ _ _ _ _ _ ‹Loader.compileUnits _ _ _ _ _ _ _ _ = .ok _› x hx

theorem prepare_status (ps : List String) (env : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json) :
    OkP (fun P : Prepared => StatusesOk P.doc) (prepare ps env rv j) := by
  unfold prepare
  okfits
  exact loadFront_status _ _ _ _ _ _ _ ‹Loader.loadPayload _ _ _ _ = .ok _›

theorem admit2_status (ps : List String) (env : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (check : ByteArray → ImportOutcome) : OkP (fun res : Admitted => StatusesOk res.doc) (admit2 ps env rv j check) := by
  unfold admit2
  okfits
  all_goals exact prepare_status _ _ _ _ _ ‹prepare _ _ _ _ = .ok _›

/-- Every admission's units carry loaded status words (none, for a `@1` document). -/
theorem admitDiscourse_status (ps : List String) (env : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (n : Nat) : OkP (fun res : Admitted => StatusesOk res.doc) (admitDiscourse ps env rv j n) := by
  cases n <;> unfold admitDiscourse admitAt <;> simp only [] <;> okfits
  all_goals first
    | (apply OkP.map; intro a p hp; simp [lift1] at hp)
    | exact admit2_status _ _ _ _ _

theorem admitCore_kinds (ps : List String) (env : Json) (rv : VE.Route.Wire.RouteVocabulary) (D : DDoc)
    (front : Loader.Front) (envId : String) :
    OkP (fun C : CoreResult => Common.KindsRendered C.base.kinds) (admitCore ps env rv D front envId) := by
  unfold admitCore
  okfits
  all_goals exact Common.admitDocument_kinds _ _ _ _ _ ‹VE.Route.Admission.admitDocument _ _ _ _ = .ok _›

theorem admit2_kinds (ps : List String) (env : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (check : ByteArray → ImportOutcome) :
    OkP (fun res : Admitted => Common.KindsRendered res.base.kinds) (admit2 ps env rv j check) := by
  unfold admit2
  okfits
  all_goals exact admitCore_kinds _ _ _ _ _ _ _ ‹admitCore _ _ _ _ _ _ = .ok _›

theorem admit1_kinds (ps : List String) (env : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json) :
    OkP (fun res : VE.Route.Admission.Admitted => Common.KindsRendered res.kinds) (admit1 ps env rv j) := by
  unfold admit1
  okfits
  all_goals exact Common.admitDocument_kinds _ _ _ _

/-- Every admission's kinds are its units' rendered kinds (W2's, for a `@1` document). -/
theorem admitDiscourse_kinds (ps : List String) (env : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (n : Nat) : OkP (fun res : Admitted => Common.KindsRendered res.base.kinds) (admitDiscourse ps env rv j n) := by
  cases n <;> unfold admitDiscourse admitAt <;> simp only [] <;> okfits
  all_goals first
    | exact admit2_kinds _ _ _ _ _
    | exact OkP.mapOf (admit1_kinds _ _ _ _) (fun _ h => h)
    | exact OkP.mapOf (Common.admitDocument_kinds _ _ _ _) (fun _ h => h)

theorem encodeAdmission_fits (id : String) (res : Admitted)
    (hr : Fits req (.arr [] (skel% "discourse.json#/$defs/reference")) res.references)
    (hs : StatusesOk res.doc) (hk : Common.KindsRendered res.base.kinds) :
    OkFits req (skel% "discourse.json#/$defs/admission") (encodeAdmission id res) := by
  unfold encodeAdmission jointFields
  okfits
  simp only [VE.Route.Wire.ok, admittedJson, reportJson, claimJson]
  split <;> simp only [List.cons_append, List.nil_append, List.append_nil, choicesJson, jointJson]
  all_goals fits using statusOf_fits res hs, readingVerdict_fits res, Common.kind_fits hk
  all_goals first
    | exact Common.claimJson_fits _
    | exact hr
    | (apply Fits.mkObjExtra
       refine OkP.filterMapM ?_ _ ‹_›
       intro _
       okfits
       all_goals (intro _ hb; cases hb)
       all_goals fits)

theorem targetJson_fits (t : Target) :
    Fits req (skel% "discourse.json#/$defs/resolved_target") (targetJson t) := by
  unfold targetJson
  fits

theorem resolve_fits (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (id : String)
    (j : Json) : OkFits req (skel% "discourse.json#/$defs/resolve") (runResolve profiles environment rv id j) := by
  unfold runResolve
  okfits
  simp only [VE.Route.Wire.ok]
  fits using targetJson_fits
  all_goals try
    apply Fits.mkObjExtra
    refine OkP.mapM ?_ _ ‹_›
    intro _ _
    okfits
    all_goals fits

theorem joint_fits (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (id : String)
    (j : Json) : OkFits req (skel% "discourse.json#/$defs/joint") (runJoint profiles environment rv id j) := by
  unfold runJoint
  okfits
  all_goals simp only [VE.Route.Wire.ok]
  all_goals fits

theorem runCase_fits (j : Json) (hp : usesDiscoursePath j = true) : OkFits j Skeletons.discourse (runCase j) := by
  unfold runCase
  simp only []
  okfits
  all_goals read_kind
  all_goals (try contra)
  all_goals first
    | (intro v hv
       fits_from encodeAdmission_fits _ _ (admitDiscourse_references _ _ _ _ _ _ ‹_›)
         (admitDiscourse_status _ _ _ _ _ _ ‹_›) (admitDiscourse_kinds _ _ _ _ _ _ ‹_›) v hv)
    | (intro v hv; fits_from resolve_fits _ _ _ _ _ v hv)
    | (intro v hv; fits_from joint_fits _ _ _ _ _ v hv)
    | (simp only [VE.Route.Wire.ok]; fits)

theorem runCaseReported_fits (j : Json) : Fits j Skeletons.discourse (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j ‹_› _ ‹_›
    · fits
  · exact of_route (Bool.eq_false_iff.mpr ‹_›) (Route.runCaseReported_fits j)

end ResponseShape.Encoders.Discourse
