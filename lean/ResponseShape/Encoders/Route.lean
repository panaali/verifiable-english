import ResponseShape.Encoders.Common

/-! The `route` mode (`Route.Run.runCaseReported`) against `route.json#/row`. -/

namespace ResponseShape.Encoders.Route
open Lean ResponseShape ResponseShape.Skeletons
open VE.Route VE.Route.Run

variable {req : Json}

/-- The answers a runner of the route returns (`route.json#/$defs/ok`): the row less its errors. -/
abbrev routeOk : Skel := skel% "route.json#/$defs/ok"

/-! Each runner answers for the kind it read (`KindRead`): the row's skeleton is the selection of
`route.json#/row` on the case's kind, so an answer of one kind given for a case of another, or a
field renamed in one kind's answer, fails. -/

/-- A Background answer: the case is a `background` case. -/
theorem runBackground_fits (id : String) (bg : List (VE.Formula × String))
    (hK : req.getObjValD "kind" = .str "background") :
    Fits req routeOk (Wire.runBackground id bg) := by
  unfold Wire.runBackground Wire.ok
  fits

theorem runDependencyOrder_fits (id : String) (j : Json) (hK : req.getObjValD "kind" = .str "dependency-order") :
    OkFits req routeOk (Wire.runDependencyOrder id j) := by
  unfold Wire.runDependencyOrder
  okfits
  all_goals (try simp only [Wire.ok])
  all_goals fits

/-- `kind_route`: through a runner given the kind it read, its tests of the kind substituted. -/
macro "kind_route" : tactic =>
  `(tactic|(okfits <;> kind_subst <;> (try simp only [Wire.ok]) <;> fits))

theorem runFol_fits (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (id kind : String)
    (j : Json) (hK : KindRead "evaluate" req kind) (hk : ¬ (kind == "background") = true) :
    OkFits req routeOk (Wire.runFol profiles environment rv id kind j) := by
  unfold Wire.runFol
  rcases hK with hK | ⟨hK, rfl⟩ <;> kind_route

theorem runClosure_fits (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (id kind : String)
    (j : Json) (hK : KindRead "evaluate" req kind) (hk : ¬ (kind == "background") = true) :
    OkFits req routeOk (Wire.runClosure profiles environment rv id kind j) := by
  unfold Wire.runClosure
  rcases hK with hK | ⟨hK, rfl⟩ <;> kind_route

theorem runOrder_fits (profiles : List String) (environment : Json) (rv : Wire.RouteOrderVocabulary)
    (id kind : String) (j : Json) (hK : KindRead "evaluate" req kind) :
    OkFits req routeOk (Wire.runOrder profiles environment rv id kind j) := by
  unfold Wire.runOrder
  rcases hK with hK | ⟨hK, rfl⟩ <;> kind_route

theorem coreWire_fits (profiles : List String) (environment : Json) (id kind : String) (j : Json)
    (hK : KindRead "evaluate" req kind) :
    OkFits req routeOk (VE.Core.Wire.run profiles environment id kind j) := by
  unfold VE.Core.Wire.run
  rcases hK with hK | ⟨hK, rfl⟩ <;> okfits <;> kind_subst <;> (try simp only [Wire.ok]) <;>
    first | with_reducible exact runBackground_fits _ _ ‹_› | fits

theorem coreLayers_fits (profiles : List String) (environment : Json) (id kind : String) (j : Json)
    (hK : KindRead "evaluate" req kind) :
    OkFits req routeOk (VE.Core.Layers.run profiles environment id kind j) := by
  unfold VE.Core.Layers.run
  okfits
  all_goals first
    | with_reducible exact coreWire_fits _ _ _ _ _ hK
    | skip
  all_goals rcases hK with hK | ⟨hK, rfl⟩
  all_goals kind_subst
  all_goals first
    | with_reducible exact runBackground_fits _ _ ‹_›
    | (unfold VE.Core.Layers.coreCertificate; okfits; all_goals (try simp only [Wire.ok]); all_goals fits)

theorem runBundle_fits (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (id : String)
    (j : Json) (hK : req.getObjValD "kind" = .str "bundle") :
    OkFits req routeOk (VE.Definitions.Bundle.runBundle profiles environment rv id j) := by
  unfold VE.Definitions.Bundle.runBundle
  okfits
  all_goals (try simp only [Wire.ok])
  all_goals fits

theorem runAdmit_fits (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (id : String)
    (j : Json) (hK : req.getObjValD "kind" = .str "admission") :
    OkFits req routeOk (runAdmit profiles environment rv id j) := by
  unfold runAdmit
  okfits
  all_goals (try simp only [Wire.ok])
  all_goals fits
  all_goals exact Common.claimJson_fits _

/-- `dispatch` on a case whose kind is the kind of `req` (`req` is the case itself, or a case the
runner answers through a rewrite of it). -/
theorem dispatch_fits (id : String) (environment : Json) (e : Gate.Envelope) (j : Json)
    (hread : ∀ kind, caseKind j = .ok kind → KindRead "evaluate" req kind) :
    OkFits req routeOk (dispatch id environment e j) := by
  unfold dispatch
  okfits
  all_goals
    have hK := hread _ ‹caseKind j = .ok _›
  all_goals first
    | with_reducible exact coreLayers_fits _ _ _ _ _ hK
    | with_reducible exact coreWire_fits _ _ _ _ _ hK
    | with_reducible exact runOrder_fits _ _ _ _ _ _ hK
    | with_reducible exact runClosure_fits _ _ _ _ _ _ hK ‹_›
    | with_reducible exact runFol_fits _ _ _ _ _ _ hK ‹_›
    | skip
  all_goals rcases hK with hK | ⟨hK, rfl⟩
  all_goals kind_subst
  all_goals (try simp only [Wire.ok])
  all_goals first
    | with_reducible exact runDependencyOrder_fits _ _ hK
    | with_reducible exact runBackground_fits _ _ hK
    | with_reducible exact runBundle_fits _ _ _ _ _ hK
    | with_reducible exact runAdmit_fits _ _ _ _ _ hK
    | fits

theorem runCase_fits_of (j : Json) (hread : ∀ kind, caseKind j = .ok kind → KindRead "evaluate" req kind) :
    OkFits req routeOk (runCase j) := by
  unfold runCase
  okfits
  exact dispatch_fits _ _ _ _ hread

theorem runCase_fits (j : Json) : OkFits j routeOk (runCase j) := by
  intro v hv
  unfold runCase at hv
  obtain ⟨_, hid, _⟩ := VE.Order.ProfileGate.bind_ok hv
  obtain ⟨_, hobj⟩ := Common.stringField_obj hid
  exact runCase_fits_of j (fun _ h => Common.caseKind_read hobj h) v (by unfold runCase; exact hv)

/-- A case with its environment rewritten (`setObjVal!`) is read as the same kind. -/
theorem caseKind_setObjVal {j : Json} (hj : CaseWF j) {w : Json} {k : String} (hobj : j.getObjVal? k = .ok w)
    (x : Json) : caseKind (j.setObjVal! "environment" x) = caseKind j := by
  cases j with
  | obj m =>
    unfold caseKind
    rw [getObjVal_setObjVal hj rfl (by decide)]
  | _ => simp [Json.getObjVal?] at hobj

theorem runCaseReported_fits (j : Json) : Fits j Skeletons.route (runCaseReported j) := by
  unfold runCaseReported
  split
  · have h := runCase_fits j _ ‹_›
    fits_from h
  · fits
    -- `valid` exactly beside a certificate case: the row's test of the case is the shape's.
    all_goals case_cond

end ResponseShape.Encoders.Route
