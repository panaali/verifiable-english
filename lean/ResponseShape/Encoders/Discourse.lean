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

theorem encodeAdmission_fits (id : String) (res : Admitted)
    (hr : Fits req (.arr [] (skel% "discourse.json#/$defs/reference")) res.references) :
    OkFits req (skel% "discourse.json#/$defs/admission") (encodeAdmission id res) := by
  unfold encodeAdmission jointFields
  okfits
  simp only [VE.Route.Wire.ok, admittedJson, reportJson, claimJson]
  split <;> simp only [List.cons_append, List.nil_append, List.append_nil, choicesJson, jointJson]
  all_goals fits
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
       fits_from encodeAdmission_fits _ _ (admitDiscourse_references _ _ _ _ _ _ ‹_›) v hv)
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
