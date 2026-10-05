import ResponseShape.Encoders.Route

/-! The `norms` mode (`Norms.Run.runCaseReported`) against `norms.json#/row`. A case off the norms
path is the route mode's. -/

namespace ResponseShape.Encoders.Norms
open Lean ResponseShape ResponseShape.Skeletons
open VE.Norms VE.Norms.Run

variable {req : Json}

/-- A route row of the case, given off the norms path. -/
theorem of_route {v : Json} (hp : (usesNormsPath req || Plain.layered (req.getObjValD "environment")) = false)
    (h : Fits req Skeletons.route v) : Fits req Skeletons.norms v :=
  Fits.onCaseE (by simpa [CaseCond.holds, CaseDecider.fn] using hp) h

/-- On the norms path, a route row of the kind the runner read is a norms row: the norms selection
gives the route's shape for the kinds the plain runner answers. -/
theorem of_plain_route {v : Json} {kind : String} (hp : (usesNormsPath req || Plain.layered (req.getObjValD "environment")) = true)
    (hK : KindRead "evaluate" req kind) (hplain : Plain.isPlainKind kind = true) (h : Fits req Route.routeOk v) :
    Fits req Skeletons.norms v := by
  simp only [Plain.isPlainKind, Bool.or_eq_true, beq_iff_eq] at hplain
  rcases hK with hK | ⟨hK, rfl⟩
  · rcases hplain with ((rfl | rfl) | rfl) | rfl
    all_goals
      fits_invert h
      all_goals fits_from h
  · fits_invert h
    all_goals fits_from h

theorem admission_fits (id reportId : String) (res : Admission.Admitted) :
    Fits req (skel% "common.json#/$defs/admission") (encodeAdmitted id reportId res) := by
  unfold encodeAdmitted VE.Route.Wire.ok
  fits
  all_goals exact Common.claimJson_fits _

theorem certificate_fits (profiles : List String) (environment stripped : Json) (T : Tree)
    (extra : List VE.Formula) (id : String) (j : Json)
    (hp : (usesNormsPath req || Plain.layered (req.getObjValD "environment")) = true)
    (hK : req.getObjValD "kind" = .str "certificate") :
    OkFits req Skeletons.norms (Plain.certificate profiles environment stripped T extra id j) := by
  unfold Plain.certificate Plain.folCertificate Plain.closureCertificate Plain.orderCertificate
    VE.Core.Layers.coreCertificate
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals first
    | (with_reducible exact OkP.of (Route.runOrder_fits _ _ _ _ _ _ (KindRead.of_str hK)) (fun _ h => of_plain_route hp (KindRead.of_str hK) (by decide) h))
    | fits

/-- `Plain.run` answers through the route runner on the case with its environment rewritten,
which reads the same kind (`CaseWF`). -/
theorem plain_fits (j : Json) (hj : CaseWF j)
    (hp : (usesNormsPath j || Plain.layered (j.getObjValD "environment")) = true)
    (hplain : ∀ kind, VE.Route.Run.caseKind j = .ok kind → Plain.isPlainKind kind = true) :
    OkFits j Skeletons.norms (Plain.run j) := by
  unfold Plain.run
  okfits
  all_goals
    obtain ⟨_, hobj⟩ := Common.stringField_obj ‹VE.Bridge.stringField j "id" = .ok _›
    have hK := Common.caseKind_read hobj ‹VE.Route.Run.caseKind j = .ok _›
    have hpk := hplain _ ‹VE.Route.Run.caseKind j = .ok _›
  all_goals first
    | (rcases hK with hK | ⟨hK, rfl⟩ <;> kind_norm <;> exact certificate_fits _ _ _ _ _ _ _ hp hK)
    | (have hr := Route.runCase_fits_of (req := j) _ (fun _ h => Common.caseKind_read hobj
          (by rwa [Route.caseKind_setObjVal hj hobj] at h)) _ ‹VE.Route.Run.runCase _ = .ok _›
       exact of_plain_route hp hK hpk hr)
    | (rcases hK with hK | ⟨hK, rfl⟩ <;> kind_norm <;> (try simp only [VE.Route.Wire.ok]) <;> fits)

theorem runCase_fits (j : Json) (hj : CaseWF j)
    (hp : (usesNormsPath j || Plain.layered (j.getObjValD "environment")) = true) :
    OkFits j Skeletons.norms (runCase j) := by
  unfold runCase
  okfits
  all_goals
    obtain ⟨_, hobj⟩ := Common.stringField_obj ‹VE.Bridge.stringField j "id" = .ok _›
    have hK := Common.caseKind_read hobj ‹VE.Route.Run.caseKind j = .ok _›
  all_goals rcases hK with hK | ⟨hK, rfl⟩
  all_goals kind_subst
  all_goals first
    | (have hck := ‹VE.Route.Run.caseKind j = .ok _›
       exact plain_fits j hj hp (fun k hk => by
        rw [hck] at hk
        cases hk
        assumption))
    | skip
  all_goals kind_norm
  all_goals (try contradiction)
  all_goals (try simp only [VE.Route.Wire.ok, Flagged.regenerated, Wire.regenerated, List.map_cons, List.map_nil,
    String.reduceBEq])
  all_goals first
    | (unfold runAdmission; okfits; fits_from admission_fits _ _ _)
    | fits

theorem runCaseReported_fits (j : Json) (hj : CaseWF j) : Fits j Skeletons.norms (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j hj ‹_› _ ‹_›
    · fits
  · exact of_route (Bool.eq_false_iff.mpr ‹_›) (Route.runCaseReported_fits j)

end ResponseShape.Encoders.Norms
