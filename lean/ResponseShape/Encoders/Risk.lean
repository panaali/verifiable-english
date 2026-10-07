import ResponseShape.Encoders.Alternatives

/-! The `risk` mode (`Risk.Run.runCaseReported`) against `risk.json#/row`. A case off the risk path
is the alternatives mode's. -/

namespace ResponseShape.Encoders.Risk
open Lean ResponseShape ResponseShape.Skeletons
open VE.Risk VE.Risk.Run

variable {req : Json}

/-- The alternatives mode's rows, off the risk path, are rows of this mode. -/
theorem of_alternatives {v : Json} (hp : usesRiskPath req = false) (h : Fits req Skeletons.alternatives v) :
    Fits req Skeletons.risk v :=
  Fits.onCaseE (by simpa [CaseCond.holds, CaseDecider.fn] using hp) h

theorem decision_fits (id : String) (j : Json) {w : Json} (hobj : j.getObjVal? "id" = .ok w)
    (hp : usesRiskPath j = true) (hK : j.getObjValD "kind" = .str "risk-decision") :
    OkFits j Skeletons.risk (runDecision id j) := by
  unfold runDecision
  okfits
  all_goals (try simp only [ok, VE.Route.Wire.ok, endpointJson, caseJson])
  all_goals fits

theorem conflict_fits (id : String) (j : Json) {w : Json} (hobj : j.getObjVal? "id" = .ok w)
    (hp : usesRiskPath j = true) (hK : j.getObjValD "kind" = .str "risk-conflict") :
    OkFits j Skeletons.risk (runConflict id j) := by
  unfold runConflict
  okfits
  all_goals (try simp only [ok, VE.Route.Wire.ok])
  all_goals fits

theorem followable_fits (id : String) (j : Json) {w : Json} (hobj : j.getObjVal? "id" = .ok w)
    (hp : usesRiskPath j = true) (hK : j.getObjValD "kind" = .str "risk-followable") :
    OkFits j Skeletons.risk (runFollowable id j) := by
  unfold runFollowable
  okfits
  all_goals (try simp only [ok, VE.Route.Wire.ok])
  all_goals fits

theorem audit_fits (id : String) (j : Json) {w : Json} (hobj : j.getObjVal? "id" = .ok w)
    (hp : usesRiskPath j = true) (hK : j.getObjValD "kind" = .str "risk-audit") :
    OkFits j Skeletons.risk (runAudit id j) := by
  unfold runAudit
  okfits
  all_goals (try simp only [ok, VE.Route.Wire.ok])
  all_goals fits

theorem certificate_fits (id : String) (j : Json) {w : Json} (hobj : j.getObjVal? "id" = .ok w)
    (hp : usesRiskPath j = true) (hK : j.getObjValD "kind" = .str "risk-certificate") :
    OkFits j Skeletons.risk (runCertificate id j) := by
  unfold runCertificate
  okfits
  all_goals (try simp only [ok, VE.Route.Wire.ok])
  all_goals fits

/-- Every Background premise label of the risk document is one of `risk.json#/$defs/risk_labels`. -/
theorem premiseLabels_mem (R : RiskDoc) : ∀ s ∈ riskPremiseLabels R,
    s ∈ ["risk:certain_possible", "risk:severity_closure", "risk:classes_distinct", "risk:order",
      "risk:class_functional", "risk:class"] := by
  intro s hs
  simp only [riskPremiseLabels, List.mem_cons, List.mem_append, List.mem_map] at hs
  rcases hs with rfl | rfl | ((⟨_, _, rfl⟩ | ⟨_, _, rfl⟩) | rfl | ⟨_, _, rfl⟩) <;> decide

theorem labelled_fits {R : RiskDoc} {p : String × VE.Formula} (h : p ∈ (riskPremiseLabels R).zip (riskPremises R)) :
    Fits req (.strIn ["risk:certain_possible", "risk:severity_closure", "risk:classes_distinct", "risk:order",
      "risk:class_functional", "risk:class"]) (.str p.1) :=
  Fits.strIn (premiseLabels_mem R _ (List.of_mem_zip h).1)

theorem elaborate_fits (id : String) (src : Wire.RiskSource)
    (hcoverage : (CaseCond.path ["coverage_units"]).holds req = false) :
    Fits req (skel% "risk.json#/$defs/elaborate") (ok id (Wire.regenerated src)) := by
  unfold ok VE.Route.Wire.ok Wire.regenerated VE.Alternatives.Wire.encodeNode Wire.labelled
    VE.Norms.Wire.regenerated orWorseName lessWorstName
  simp only []
  fits using labelled_fits, Alternatives.labelled_fits

theorem elaborate_coverage_fits (id : String) (src : Wire.RiskSource)
    (environment units narrowings : Json)
    (hcoverage : (CaseCond.path ["coverage_units"]).holds req = true) :
    Fits req (skel% "risk.json#/$defs/elaborate")
      (ok id (Wire.regenerated src ++
        [("coverage", VE.Alternatives.Wire.coverage (toAlt src.R)
          environment units narrowings)])) := by
  unfold ok VE.Route.Wire.ok Wire.regenerated VE.Alternatives.Wire.encodeNode Wire.labelled
    VE.Norms.Wire.regenerated orWorseName lessWorstName VE.Alternatives.Wire.coverage
  simp only []
  fits using labelled_fits, Alternatives.labelled_fits
  case h_2 x completion item heq hx =>
    simp only [List.mem_flatMap, List.mem_filterMap] at hx
    rcases hx with ⟨action, _, harm, _, h⟩
    split at h <;> simp only [Option.some.injEq, reduceCtorEq] at h
    subst_vars
    fits
    -- The complete table's own cell, read from the declared outcomes decider.
    all_goals
      split at heq <;> simp only [Option.some.injEq, reduceCtorEq] at heq
      subst_vars
      fits

theorem elaborate_case_fits (id : String) (j : Json) {w : Json} (hobj : j.getObjVal? "id" = .ok w)
    (hp : usesRiskPath j = true) (hK : j.getObjValD "kind" = .str "risk-elaborate") :
    OkFits j Skeletons.risk (runElaborate id j) := by
  unfold runElaborate
  okfits
  split
  · fits_from elaborate_coverage_fits (req := j) id _ _ _ _
      (CaseCond.path_ok ‹j.getObjVal? "coverage_units" = .ok _›)
  · simp only [List.append_nil]
    fits_from elaborate_fits (req := j) id _
      (CaseCond.path_error hobj ‹j.getObjVal? "coverage_units" = .error _›)

/-- Every admission's kinds are its units' rendered kinds. -/
theorem admitDocument_kinds (environment document : Json) :
    OkP (fun res : Admission.Admitted => Common.KindsRendered res.kinds) (Admission.admitDocument environment document) := by
  unfold Admission.admitDocument
  okfits
  all_goals exact Common.kindsRendered_map _ _

theorem admission_fits (id reportId : String) (res : Admission.Admitted) (hk : Common.KindsRendered res.kinds) :
    Fits req (skel% "risk.json#/$defs/admission") (encodeAdmitted id reportId res) := by
  unfold encodeAdmitted ok VE.Route.Wire.ok
  fits using Common.kind_fits hk
  all_goals exact Common.claimJson_fits _

theorem runCase_fits (j : Json) (hp : usesRiskPath j = true) : OkFits j Skeletons.risk (runCase j) := by
  unfold runCase
  okfits
  all_goals read_kind
  all_goals first
    | (unfold runAdmission; okfits; fits_from admission_fits _ _ _ (admitDocument_kinds _ _ _ ‹Admission.admitDocument _ _ = .ok _›))
    | exact elaborate_case_fits _ _ ‹_› hp ‹_›
    | exact decision_fits _ _ ‹_› hp ‹_›
    | exact conflict_fits _ _ ‹_› hp ‹_›
    | exact followable_fits _ _ ‹_› hp ‹_›
    | exact audit_fits _ _ ‹_› hp ‹_›
    | exact certificate_fits _ _ ‹_› hp ‹_›

theorem runCaseReported_fits (j : Json) (hj : CaseWF j) : Fits j Skeletons.risk (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j ‹_› _ ‹_›
    · fits
  · exact of_alternatives (Bool.eq_false_iff.mpr ‹_›) (Alternatives.runCaseReported_fits j hj)

end ResponseShape.Encoders.Risk
