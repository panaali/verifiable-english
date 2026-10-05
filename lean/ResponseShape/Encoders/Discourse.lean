import ResponseShape.Encoders.Route

/-! The `discourse` mode (`Discourse.Run.runCaseReported`) against `discourse.json#/row`. A case off
the discourse path is the route mode's. -/

namespace ResponseShape.Encoders.Discourse
open Lean ResponseShape ResponseShape.Skeletons
open VE.Discourse VE.Discourse.Run

theorem of_route {v : Json} (h : Fits Γ Skeletons.route v) : Fits Γ Skeletons.discourse v := by
  refine Fits.altSub ?_ h
  alt_sub

theorem references_fits (front : Json) (pending : List (String × String)) :
    Fits Γ (.arr [] (skel% "discourse.json#/$defs/reference")) (referencesJson front pending) := by
  unfold referencesJson
  fits

/-- Every admission's reference lines are `referencesJson`'s (or none, for a `@1` document). -/
theorem admitDiscourse_references (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (n : Nat) :
    OkP (fun res : Admitted => Fits Γ (.arr [] (skel% "discourse.json#/$defs/reference")) res.references)
      (admitDiscourse profiles environment rv j n) := by
  cases n <;> unfold admitDiscourse admitAt <;> simp only [] <;> okfits
  all_goals first
    | (apply OkP.map; intro a; exact Fits.arrOf (fun x hx => by simp at hx))
    | (unfold admit2; okfits; exact references_fits _ _)

theorem encodeAdmission_fits (id : String) (res : Admitted)
    (hr : Fits Γ (.arr [] (skel% "discourse.json#/$defs/reference")) res.references) :
    OkFits Γ (skel% "discourse.json#/$defs/admission") (encodeAdmission id res) := by
  unfold encodeAdmission
  okfits
  simp only [VE.Route.Wire.ok, admittedJson, reportJson, claimJson]
  fits
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
    Fits Γ (skel% "discourse.json#/$defs/resolved_target") (targetJson t) := by
  unfold targetJson
  fits

theorem resolve_fits (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (id : String)
    (j : Json) : OkFits Γ (skel% "discourse.json#/$defs/resolve") (runResolve profiles environment rv id j) := by
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
    (j : Json) : OkFits Γ (skel% "discourse.json#/$defs/joint") (runJoint profiles environment rv id j) := by
  unfold runJoint
  okfits
  all_goals simp only [VE.Route.Wire.ok]
  all_goals fits

theorem runCase_fits (j : Json) : OkFits Γ Skeletons.discourse (runCase j) := by
  unfold runCase
  simp only []
  okfits
  all_goals first
    | with_reducible exact OkP.of (Route.runCase_fits _) fun _ => of_route
    | (refine OkP.of (encodeAdmission_fits _ _ ?_) fun _ h => Fits.ofAlt (by alt_mem) h
       exact admitDiscourse_references _ _ _ _ _ _ ‹_›)
    | with_reducible exact OkP.of (resolve_fits _ _ _ _ _) fun _ h => Fits.ofAlt (by alt_mem) h
    | with_reducible exact OkP.of (joint_fits _ _ _ _ _) fun _ h => Fits.altSub (by alt_sub) h
    | (simp only [VE.Route.Wire.ok]; fits)

theorem runCaseReported_fits (j : Json) : Fits Γ Skeletons.discourse (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j _ ‹_›
    · fits
  · exact of_route (Route.runCaseReported_fits j)

end ResponseShape.Encoders.Discourse
