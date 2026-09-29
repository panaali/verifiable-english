import VE.Risk.Severity

/-! The Background slot `risk`, `BaseAdmissibleRisk` and the policy checks
(docs/spec/risk.md 4.6, 4.7 and 7.2).

The slot contributes, in this order, `risk:certain_possible`,
`risk:severity_closure`, `risk:classes_distinct`, the full ground order table
`risk:order`, `risk:class_functional` (the formula W1 generates for a
`functional` flag) and the ground class facts `risk:class`. The policy's
conflict and followability checks are alt's, run on `toAlt R` with the risk
premises added to alt's base background. -/
namespace VE.Risk
open VE.Norms
open VE.Alternatives (AltDoc inlineTree BaseAdmissibleAlt backgroundBaseAlt backgroundValidAlt Avail
  FollowableIn allFollowable notFollowableF altConflictFreeCheck targetAccepted AltConflictFree)
universe u

/-! ## The slot premises (4.6) -/

/-- `∀a h. leads_to(a, h) → risk__might_lead_to(a, h)`. -/
def certainPossible (R : RiskDoc) : VE.Formula :=
  .all R.alt.action (.all R.alt.harm (.implies (.binary R.alt.leadsTo (.var 1) (.var 0))
    (.binary mightName (.var 1) (.var 0))))

/-- `∀s. s = c₁ ∨ … ∨ s = cₙ` over the fresh sort. -/
def severityClosure (R : RiskDoc) : VE.Formula :=
  .all R.sev (anyF (R.classes.map fun c => .eq (.var 0) (.const c)))

/-- The pairs `(cᵢ, cⱼ)` with `i < j`. -/
def lowerPairs : List String → List (String × String)
  | [] => []
  | c :: cs => cs.map (c, ·) ++ lowerPairs cs

def classesDistinct (R : RiskDoc) : List VE.Formula :=
  (lowerPairs R.classes).map fun (a, b) => .not (.eq (.const a) (.const b))

/-- The n² ground literals of the closed order. -/
def orderLiteral (R : RiskDoc) (p : String × String) : VE.Formula :=
  if (closure R).contains p then .binary moreSeverePred (.const p.1) (.const p.2)
  else .not (.binary moreSeverePred (.const p.1) (.const p.2))

def orderTable (R : RiskDoc) : List VE.Formula := (classPairs R).map (orderLiteral R)

/-- `∀h s s′. class(h, s) ∧ class(h, s′) → s = s′`. -/
def classFunctional (R : RiskDoc) : VE.Formula :=
  .all R.alt.harm (.all R.sev (.all R.sev (.implies
    (.and (.binary classPred (.var 2) (.var 1)) (.binary classPred (.var 2) (.var 0))) (.eq (.var 1) (.var 0)))))

def classFacts (R : RiskDoc) : List VE.Formula :=
  R.risk.harmClasses.map fun (h, c) => .binary classPred (.const h) (.const c)

def riskPremises (R : RiskDoc) : List VE.Formula :=
  certainPossible R :: severityClosure R :: (classesDistinct R ++ orderTable R ++ classFunctional R :: classFacts R)

/-- The labels of `riskPremises`, in the same order. -/
def riskPremiseLabels (R : RiskDoc) : List String :=
  "risk:certain_possible" :: "risk:severity_closure" ::
    ((classesDistinct R).map (fun _ => "risk:classes_distinct") ++ (orderTable R).map (fun _ => "risk:order") ++
      "risk:class_functional" :: (classFacts R).map (fun _ => "risk:class"))

def BaseAdmissibleRisk (R : RiskDoc) (B : VE.Structure.{u}) : Prop :=
  BaseAdmissibleAlt (toAlt R) B ∧ Sat B (riskPremises R)

def backgroundValidRisk {α : Type u} [DecidableEq α] (R : RiskDoc) (M : VE.FiniteModel α) : Bool :=
  backgroundValidAlt (toAlt R) M && (riskPremises R).all (fun p => p.eval M [])

def RiskConflictFree (R : RiskDoc) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleRisk R B → ConflictFree (inlineTree (toAlt R)) B

/-- One target's certificate is accepted over `Background_baseAlt ++ riskPremises`, or over alt's
backgrounds alone (fewer premises, 4.7). -/
def riskTargetAccepted (R : RiskDoc) (t : String × List String × VE.Formula) (c : VE.Tableau.Certificate) : Bool :=
  VE.Tableau.checkCertificate (envAt (inlineTree (toAlt R)) 0) (backgroundBaseAlt (toAlt R) ++ riskPremises R)
    (targetConclusion t) c || targetAccepted (toAlt R) t c

/-- Every W1 target of `inlineTree (toAlt R)` has an accepted certificate. -/
def riskConflictFreeCheck (R : RiskDoc) (certs : List (Option VE.Tableau.Certificate)) : Bool :=
  (targets (inlineTree (toAlt R))).length == certs.length &&
    ((targets (inlineTree (toAlt R))).zip certs).all (fun (t, c) => match c with
      | some c => riskTargetAccepted R t c
      | none => false)

theorem riskConflictFreeCheck_target {R : RiskDoc} {certs : List (Option VE.Tableau.Certificate)}
    (hc : riskConflictFreeCheck R certs = true) {t : String × List String × VE.Formula}
    (ht : t ∈ targets (inlineTree (toAlt R))) : ∃ c, riskTargetAccepted R t c = true := by
  simp only [riskConflictFreeCheck, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hc
  obtain ⟨hl, hall⟩ := hc
  obtain ⟨i, hi⟩ := List.mem_iff_getElem?.mp ht
  have hlt : i < (targets (inlineTree (toAlt R))).length := (List.getElem?_eq_some_iff.mp hi).1
  have hlt' : i < certs.length := hl ▸ hlt
  have hmem : (t, certs[i]) ∈ (targets (inlineTree (toAlt R))).zip certs := by
    apply List.mem_iff_getElem?.mpr
    refine ⟨i, ?_⟩
    rw [List.getElem?_zip_eq_some]
    exact ⟨hi, List.getElem?_eq_getElem hlt'⟩
  have := hall _ hmem
  cases hci : certs[i] with
  | none => rw [hci] at this; cases this
  | some c => rw [hci] at this; exact ⟨c, this⟩

theorem sat_riskBackground {R : RiskDoc} {B : VE.Structure.{u}} (hB : BaseAdmissibleRisk R B) :
    Sat B (backgroundBaseAlt (toAlt R) ++ riskPremises R) := by
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · exact VE.Alternatives.sat_backgroundBaseAlt hB.1 a ha
  · exact hB.2 a ha

/-! ## Policy checks (4.7) -/

/-- 4.7: accepted certificates for every W1 target (over `Background_baseAlt ++ riskPremises`, or
alt's backgrounds) give `RiskConflictFree`. -/
theorem risk_conflict_free (R : RiskDoc) (h : WellFormedRisk R = true) (certs : List (Option VE.Tableau.Certificate))
    (hc : riskConflictFreeCheck R certs = true) : RiskConflictFree.{u} R := by
  have hv := valid_of_wellFormed _ (VE.Alternatives.alternatives_wellFormed _ (risk_wellFormed_alt R h))
  intro B hB
  have cert : ∀ t ∈ targets (inlineTree (toAlt R)), ∀ vs, VE.TupleTyped B t.2.1 vs →
      ¬ t.2.2.denote B (tupleVal vs) := by
    intro t ht vs hvs
    obtain ⟨c, hcc⟩ := riskConflictFreeCheck_target hc ht
    have he : (targetConclusion t).denote B [] := by
      rcases Bool.or_eq_true_iff.mp hcc with hcc | hcc
      · exact VE.Tableau.checkCertificate_sound.{u} _ _ _ c hcc B hB.1.1.1 (sat_riskBackground hB)
      · rcases Bool.or_eq_true_iff.mp hcc with hcc | hcc
        · exact VE.Tableau.checkCertificate_sound.{u} _ _ _ c hcc B hB.1.1.1
            (VE.Alternatives.sat_backgroundBaseAlt hB.1)
        · exact VE.Tableau.checkCertificate_sound.{u} _ _ _ c hcc B hB.1.1.1 hB.1.1.2
    exact (bindAll_denote_nil B _ _).mp he vs hvs
  refine ⟨fun r hr vs hvs => ?_, fun pr hpr vs hvs => ?_⟩
  · exact cert (r.name, r.sorts, conflict (inlineTree (toAlt R)) r)
      (List.mem_append_left _ (List.mem_filterMap.mpr ⟨.reg r, hv.regulated r hr, rfl⟩)) vs hvs
  · exact cert (pr.req ++ "->" ++ pr.perm, pr.sorts, pairConflict (inlineTree (toAlt R)) pr)
      (List.mem_append_right _ (List.mem_map.mpr ⟨pr, hpr, rfl⟩)) vs hvs

/-- 4.7: conflict-freedom over alt's background alone (fewer premises) gives `RiskConflictFree`. -/
theorem alt_conflict_free_risk (R : RiskDoc) (h : WellFormedRisk R = true)
    (hc : AltConflictFree.{u} (toAlt R)) : RiskConflictFree.{u} R := by
  have _ := h
  intro B hB
  exact hc B hB.1

/-- 4.7: FOLLOWABLE over the risk premises, for every document expansion of every
`BaseAdmissibleRisk` structure satisfying `Γ_base`. -/
theorem risk_followable_sound (R : RiskDoc) (h : WellFormedRisk R = true) (hc : RiskConflictFree.{u} R)
    (c : VE.Tableau.Certificate)
    (ok : VE.Tableau.checkCertificate (envAt (inlineTree (toAlt R)) 0)
            (backgroundBaseAlt (toAlt R) ++ riskPremises R ++ R.Γ) (allFollowable (toAlt R)) c = true) :
    ∀ B : VE.Structure.{u}, BaseAdmissibleRisk R B → Sat B R.Γ →
      ∀ S, DocumentExpansion (inlineTree (toAlt R)) B S → FollowableIn (toAlt R) S := by
  have _ := hc
  intro B hB hΓ S hS
  have hden := VE.Tableau.checkCertificate_sound.{u} _ _ _ c ok B hB.1.1.1 (fun a ha => by
    rcases List.mem_append.mp ha with ha | ha
    · exact sat_riskBackground hB a ha
    · exact hΓ a ha)
  have hr := hS.1
  subst hr
  exact (VE.Alternatives.followable_denote_of
    (VE.Alternatives.altValid_of_wellFormed _ (risk_wellFormed_alt R h)) hS).mp hden

theorem baseAdmissibleRisk_of_valid {α : Type u} [DecidableEq α] (R : RiskDoc) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt (inlineTree (toAlt R)) 0)) (hb : backgroundValidRisk R M = true) :
    BaseAdmissibleRisk R M.asStructure := by
  simp only [backgroundValidRisk, Bool.and_eq_true, List.all_eq_true] at hb
  exact ⟨VE.Alternatives.baseAdmissibleAlt_of_valid _ M valid hb.1,
    fun a ha => (VE.eval_iff_denote M [] a).mp (hb.2 a ha)⟩

/-- 4.7: a typed chooser of a valid finite witness passing `backgroundValidRisk` and `Γ_base`, at
which `¬followable°` evaluates true, refutes the document-wide claim over `BaseAdmissibleRisk`. -/
theorem risk_dilemma_witness_sound {α : Type u} [DecidableEq α] (R : RiskDoc) (h : WellFormedRisk R = true)
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (inlineTree (toAlt R)) 0))
    (hb : backgroundValidRisk R M = true) (hΓ : R.Γ.all (fun p => p.eval M []) = true)
    (r : α) (typed : M.inDomain R.alt.chooser r)
    (hd : (notFollowableF (toAlt R)).eval M (tupleVal [r]) = true) :
    ¬ (∀ B : VE.Structure.{u}, BaseAdmissibleRisk R B → Sat B R.Γ → (allFollowable (toAlt R)).denote B []) := by
  have _ := h
  intro hall
  have hF := hall M.asStructure (baseAdmissibleRisk_of_valid R M valid hb)
    (fun a ha => (VE.eval_iff_denote M [] a).mp (List.all_eq_true.mp hΓ a ha))
  have hF' := (bindAll_denote_nil _ _ _).mp hF [r] ⟨typed, trivial⟩
  exact ((VE.eval_iff_denote M _ _).mp hd) hF'

end VE.Risk
