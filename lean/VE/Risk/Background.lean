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
def lowerPairs {α : Type} : List α → List (α × α)
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

/-! ## Conservativity (4.6) -/

/-- The old signature: `E_base` without the generated sort, the class constants, the generated
predicates, and any constant or predicate of the generated sort. -/
def oldEnvRisk (R : RiskDoc) : VE.Environment :=
  let E0 := envAt (inlineTree (toAlt R)) 0
  { sorts := R.E.sorts
    predicates := fun p => if p ∈ generatedPreds ∨ R.sev ∈ (E0.predicates p).getD [] then none else E0.predicates p
    constants := fun c => if c ∈ R.classes ∨ E0.constants c = some R.sev then none else E0.constants c }

/-- `¬(c = c′)` for harm constants `c`, `c′` with different classes. -/
def compatFacts (R : RiskDoc) : List VE.Formula :=
  ((lowerPairs R.risk.harmClasses).filter (fun (p, q) => p.2 != q.2)).map
    fun (p, q) => .not (.eq (.const p.1) (.const q.1))

/-- `B₀` embeds in `B` along `e`, preserving the old signature (carrier transport). -/
def ReductVia (R : RiskDoc) (B₀ B : VE.Structure.{u}) (e : B₀.Carrier → B.Carrier) : Prop :=
  Function.Injective e ∧
  (∀ s ∈ (oldEnvRisk R).sorts, ∀ v, B.domain s v ↔ ∃ v₀, v = e v₀ ∧ B₀.domain s v₀) ∧
  (∀ c, (oldEnvRisk R).constants c ≠ none → B.constant c = (B₀.constant c).map e) ∧
  (∀ p, (oldEnvRisk R).predicates p ≠ none → ∀ vs, B.relation p vs ↔ ∃ vs₀, vs = vs₀.map e ∧ B₀.relation p vs₀)

/-! ### Truth along an embedding -/

def binderSorts : VE.Formula → List String
  | .top | .bottom | .unary .. | .binary .. | .eq .. => []
  | .not a => binderSorts a
  | .and a b | .or a b | .implies a b => binderSorts a ++ binderSorts b
  | .all s a | .ex s a => s :: binderSorts a

def termConsts : VE.Term → List String
  | .var _ => []
  | .const c => [c]

def formulaConsts : VE.Formula → List String
  | .top | .bottom => []
  | .unary _ t => termConsts t
  | .binary _ t u | .eq t u => termConsts t ++ termConsts u
  | .not a | .all _ a | .ex _ a => formulaConsts a
  | .and a b | .or a b | .implies a b => formulaConsts a ++ formulaConsts b

theorem map_injective {α β : Type _} {e : α → β} (he : Function.Injective e) :
    ∀ {l m : List α}, l.map e = m.map e → l = m
  | [], [], _ => rfl
  | [], _ :: _, h | _ :: _, [], h => by simp at h
  | a :: l, b :: m, h => by
    simp only [List.map_cons, List.cons.injEq] at h
    rw [he h.1, map_injective he h.2]

theorem term_transport {B₀ B : VE.Structure.{u}} (e : B₀.Carrier → B.Carrier) (ρ : List B₀.Carrier) (t : VE.Term)
    (hc : ∀ c ∈ termConsts t, B.constant c = (B₀.constant c).map e) :
    t.denote B (ρ.map e) = (t.denote B₀ ρ).map e := by
  cases t with
  | var i => simp [VE.Term.denote]
  | const c => exact hc c (by simp [termConsts])

/-- Truth is preserved along an injective embedding that preserves the domains of the binder sorts, the
constants and the relations a formula mentions. -/
theorem denote_transport {B₀ B : VE.Structure.{u}} (e : B₀.Carrier → B.Carrier) (he : Function.Injective e) :
    ∀ (φ : VE.Formula) (ρ : List B₀.Carrier),
      (∀ s ∈ binderSorts φ, ∀ v, B.domain s v ↔ ∃ v₀, v = e v₀ ∧ B₀.domain s v₀) →
      (∀ c ∈ formulaConsts φ, B.constant c = (B₀.constant c).map e) →
      (∀ p ∈ preds φ, ∀ vs, B.relation p vs ↔ ∃ vs₀, vs = vs₀.map e ∧ B₀.relation p vs₀) →
      (φ.denote B (ρ.map e) ↔ φ.denote B₀ ρ)
  | .top, _, _, _, _ | .bottom, _, _, _, _ => Iff.rfl
  | .unary p t, ρ, _, hc, hp => by
    simp only [VE.Formula.denote, term_transport e ρ t hc]
    have hr := hp p (by simp [preds])
    constructor
    · rintro ⟨v, hv, hrel⟩
      obtain ⟨v₀, hv₀, rfl⟩ := Option.map_eq_some_iff.mp hv
      obtain ⟨vs₀, hvs, h0⟩ := (hr [e v₀]).mp hrel
      have : vs₀ = [v₀] := map_injective he (by simpa using hvs.symm)
      subst this
      exact ⟨v₀, hv₀, h0⟩
    · rintro ⟨v₀, hv₀, h0⟩
      exact ⟨e v₀, by simp [hv₀], (hr [e v₀]).mpr ⟨[v₀], rfl, h0⟩⟩
  | .binary p t u, ρ, _, hc, hp => by
    simp only [VE.Formula.denote, term_transport e ρ t (fun c h => hc c (List.mem_append_left _ h)),
      term_transport e ρ u (fun c h => hc c (List.mem_append_right _ h))]
    have hr := hp p (by simp [preds])
    constructor
    · rintro ⟨v, w, hv, hw, hrel⟩
      obtain ⟨v₀, hv₀, rfl⟩ := Option.map_eq_some_iff.mp hv
      obtain ⟨w₀, hw₀, rfl⟩ := Option.map_eq_some_iff.mp hw
      obtain ⟨vs₀, hvs, h0⟩ := (hr [e v₀, e w₀]).mp hrel
      have : vs₀ = [v₀, w₀] := map_injective he (by simpa using hvs.symm)
      subst this
      exact ⟨v₀, w₀, hv₀, hw₀, h0⟩
    · rintro ⟨v₀, w₀, hv₀, hw₀, h0⟩
      exact ⟨e v₀, e w₀, by simp [hv₀], by simp [hw₀], (hr [e v₀, e w₀]).mpr ⟨[v₀, w₀], rfl, h0⟩⟩
  | .eq t u, ρ, _, hc, _ => by
    simp only [VE.Formula.denote, term_transport e ρ t (fun c h => hc c (List.mem_append_left _ h)),
      term_transport e ρ u (fun c h => hc c (List.mem_append_right _ h))]
    constructor
    · rintro ⟨v, hv, hw⟩
      obtain ⟨v₀, hv₀, rfl⟩ := Option.map_eq_some_iff.mp hv
      obtain ⟨w₀, hw₀, hew⟩ := Option.map_eq_some_iff.mp hw
      exact ⟨v₀, hv₀, by rw [hw₀, he hew]⟩
    · rintro ⟨v₀, hv₀, hw₀⟩
      exact ⟨e v₀, by simp [hv₀], by simp [hw₀]⟩
  | .not a, ρ, hs, hc, hp => not_congr (denote_transport e he a ρ hs hc hp)
  | .and a b, ρ, hs, hc, hp | .or a b, ρ, hs, hc, hp | .implies a b, ρ, hs, hc, hp => by
    have ia := denote_transport e he a ρ (fun s h => hs s (List.mem_append_left _ h))
      (fun c h => hc c (List.mem_append_left _ h)) (fun p h => hp p (List.mem_append_left _ h))
    have ib := denote_transport e he b ρ (fun s h => hs s (List.mem_append_right _ h))
      (fun c h => hc c (List.mem_append_right _ h)) (fun p h => hp p (List.mem_append_right _ h))
    first
    | exact and_congr ia ib
    | exact or_congr ia ib
    | exact imp_congr ia ib
  | .all s a, ρ, hs, hc, hp | .ex s a, ρ, hs, hc, hp => by
    have hd := hs s (List.mem_cons_self ..)
    have ih : ∀ v₀ : B₀.Carrier, (a.denote B ((v₀ :: ρ).map e) ↔ a.denote B₀ (v₀ :: ρ)) := fun v₀ =>
      denote_transport e he a (v₀ :: ρ) (fun s' h => hs s' (List.mem_cons_of_mem _ h)) hc hp
    simp only [VE.Formula.denote]
    first
    | constructor
      · intro h v₀ hv₀
        exact (ih v₀).mp (h (e v₀) ((hd (e v₀)).mpr ⟨v₀, rfl, hv₀⟩))
      · intro h v hv
        obtain ⟨v₀, rfl, hv₀⟩ := (hd v).mp hv
        exact (ih v₀).mpr (h v₀ hv₀)
    | constructor
      · rintro ⟨v, hv, ha⟩
        obtain ⟨v₀, rfl, hv₀⟩ := (hd v).mp hv
        exact ⟨v₀, hv₀, (ih v₀).mp ha⟩
      · rintro ⟨v₀, hv₀, ha⟩
        exact ⟨e v₀, (hd (e v₀)).mpr ⟨v₀, rfl, hv₀⟩, (ih v₀).mpr ha⟩

/-- A formula typed over the old signature mentions only old binder sorts, constants and predicates. -/
theorem wf_old_symbols {E : VE.Environment} :
    ∀ {φ : VE.Formula} {Γ : List String}, φ.WellFormed E Γ →
      (∀ s ∈ binderSorts φ, s ∈ E.sorts) ∧ (∀ c ∈ formulaConsts φ, E.constants c ≠ none) ∧
      (∀ p ∈ preds φ, E.predicates p ≠ none)
  | .top, _, _ | .bottom, _, _ => ⟨by simp [binderSorts], by simp [formulaConsts], by simp [preds]⟩
  | .unary p t, _, ⟨s, hp, ht⟩ => by
    refine ⟨by simp [binderSorts], fun c hc => ?_, fun q hq => ?_⟩
    · cases t with
      | var _ => simp [formulaConsts, termConsts] at hc
      | const c' =>
        simp [formulaConsts, termConsts] at hc; subst hc
        simp only [VE.Term.sortOf] at ht; rw [ht]; simp
    · simp only [preds, List.mem_singleton] at hq; subst hq; rw [hp]; simp
  | .binary p t u, _, ⟨s, r, hp, ht, hu⟩ => by
    refine ⟨by simp [binderSorts], fun c hc => ?_, fun q hq => ?_⟩
    · simp only [formulaConsts, List.mem_append] at hc
      rcases hc with hc | hc
      · cases t with
        | var _ => simp [termConsts] at hc
        | const c' => simp [termConsts] at hc; subst hc; simp only [VE.Term.sortOf] at ht; rw [ht]; simp
      · cases u with
        | var _ => simp [termConsts] at hc
        | const c' => simp [termConsts] at hc; subst hc; simp only [VE.Term.sortOf] at hu; rw [hu]; simp
    · simp only [preds, List.mem_singleton] at hq; subst hq; rw [hp]; simp
  | .eq t u, _, ⟨s, ht, hu⟩ => by
    refine ⟨by simp [binderSorts], fun c hc => ?_, by simp [preds]⟩
    simp only [formulaConsts, List.mem_append] at hc
    rcases hc with hc | hc
    · cases t with
      | var _ => simp [termConsts] at hc
      | const c' => simp [termConsts] at hc; subst hc; simp only [VE.Term.sortOf] at ht; rw [ht]; simp
    · cases u with
      | var _ => simp [termConsts] at hc
      | const c' => simp [termConsts] at hc; subst hc; simp only [VE.Term.sortOf] at hu; rw [hu]; simp
  | .not a, _, h => by
    have := wf_old_symbols (φ := a) h
    exact ⟨by simpa [binderSorts] using this.1, by simpa [formulaConsts] using this.2.1, by simpa [preds] using this.2.2⟩
  | .and a b, _, h | .or a b, _, h | .implies a b, _, h => by
    have ha := wf_old_symbols h.1
    have hb := wf_old_symbols h.2
    refine ⟨fun s hs => ?_, fun c hc => ?_, fun p hp => ?_⟩
    · rcases List.mem_append.mp hs with hs | hs
      · exact ha.1 s hs
      · exact hb.1 s hs
    · rcases List.mem_append.mp hc with hc | hc
      · exact ha.2.1 c hc
      · exact hb.2.1 c hc
    · rcases List.mem_append.mp hp with hp | hp
      · exact ha.2.2 p hp
      · exact hb.2.2 p hp
  | .all s a, _, h | .ex s a, _, h => by
    have ha := wf_old_symbols h.2
    refine ⟨fun s' hs => ?_, ha.2.1, ha.2.2⟩
    rcases List.mem_cons.mp hs with rfl | hs
    · exact h.1
    · exact ha.1 s' hs

theorem reduct_denote {R : RiskDoc} {B₀ B : VE.Structure.{u}} {e : B₀.Carrier → B.Carrier}
    (hr : ReductVia R B₀ B e) {φ : VE.Formula} (hφ : φ.WellFormed (oldEnvRisk R) []) :
    φ.denote B [] ↔ φ.denote B₀ [] := by
  obtain ⟨hs, hc, hp⟩ := wf_old_symbols hφ
  exact denote_transport e hr.1 φ [] (fun s h => hr.2.1 s (hs s h)) (fun c h => hr.2.2.1 c (hc c h))
    (fun p h => hr.2.2.2 p (hp p h))

/-! ### The expansion -/

/-- A predicate of `E_risk` that is not generated and has no argument of the generated sort. -/
def PlainPred (R : RiskDoc) (p : String) : Prop :=
  p ∉ generatedPreds ∧ ∀ ss, (riskEnv R).predicates p = some ss → R.sev ∉ ss

/-- The expansion of 4.6: the old carrier plus one fresh element per class (named by the class);
`risk__might_lead_to` is `leads_to`, `risk__class` is `harm_classes` and `risk__more_severe` the closure.
A constant of the generated sort outside the classes denotes the first class. -/
def expand (R : RiskDoc) (B₀ : VE.Structure.{u}) : VE.Structure.{u} where
  Carrier := B₀.Carrier ⊕ String
  domain s v := match v with
    | .inl v₀ => s ≠ R.sev ∧ B₀.domain s v₀
    | .inr c => s = R.sev ∧ c ∈ R.classes
  constant c := if c ∈ R.classes then some (.inr c)
    else if R.E.constants c = some R.sev then some (.inr (R.classes.headD ""))
    else (B₀.constant c).map .inl
  relation p vs :=
    if p = mightName then ∃ a h, vs = [.inl a, .inl h] ∧ B₀.relation R.alt.leadsTo [a, h]
    else if p = classPred then
      ∃ h c, vs = [.inl h, .inr c] ∧ ∃ hc, (hc, c) ∈ R.risk.harmClasses ∧ B₀.constant hc = some h
    else if p = moreSeverePred then ∃ c c', vs = [.inr c, .inr c'] ∧ (c, c') ∈ closure R
    else PlainPred R p ∧ ∃ vs₀, vs = vs₀.map .inl ∧ B₀.relation p vs₀

section Expansion
variable {R : RiskDoc} {B₀ : VE.Structure.{u}}

theorem expand_domain_old {s : String} (hs : s ≠ R.sev) (v : (expand R B₀).Carrier) :
    (expand R B₀).domain s v ↔ ∃ v₀, v = Sum.inl v₀ ∧ B₀.domain s v₀ := by
  cases v with
  | inl v₀ => simp [expand, hs]
  | inr c => simp [expand, hs]

theorem expand_tupleTyped {ss : List String} (hs : ∀ s ∈ ss, s ≠ R.sev) :
    ∀ vs₀ : List B₀.Carrier, VE.TupleTyped (expand R B₀) ss (vs₀.map .inl) ↔ VE.TupleTyped B₀ ss vs₀ := by
  induction ss with
  | nil => intro vs₀; cases vs₀ <;> simp [VE.TupleTyped]
  | cons s ss ih =>
    intro vs₀
    cases vs₀ with
    | nil => simp [VE.TupleTyped]
    | cons v vs =>
      simp only [List.map_cons, VE.TupleTyped]
      rw [ih (fun s' h => hs s' (List.mem_cons_of_mem _ h)) vs]
      simp [expand, hs s (List.mem_cons_self ..)]

theorem expand_const_plain {c : String} (h1 : c ∉ R.classes) (h2 : R.E.constants c ≠ some R.sev) :
    (expand R B₀).constant c = (B₀.constant c).map .inl := by
  simp [expand, h1, h2]

theorem expand_relation_plain {p : String} (hp : PlainPred R p) (vs : List (expand R B₀).Carrier) :
    (expand R B₀).relation p vs ↔ ∃ vs₀, vs = vs₀.map .inl ∧ B₀.relation p vs₀ := by
  have h1 : p ≠ mightName := fun h => hp.1 (by simp [h, generatedPreds])
  have h2 : p ≠ classPred := fun h => hp.1 (by simp [h, generatedPreds])
  have h3 : p ≠ moreSeverePred := fun h => hp.1 (by simp [h, generatedPreds])
  simp only [expand, h1, h2, h3, if_false]
  exact ⟨fun h => h.2, fun h => ⟨hp, h⟩⟩

end Expansion

/-! ### Facts of a well-formed risk document used by the expansion -/

section Facts
variable {R : RiskDoc} (hv : RiskValid R)
include hv

theorem not_layer {n : String} (hn : n ∈ generatedPreds ++ riskWords) :
    n ∉ layerNames (inlineTree (toAlt R)).T := by
  intro hl
  simp only [layerNames, List.mem_map] at hl
  obtain ⟨q, hq, rfl⟩ := hl
  cases q with
  | reg r =>
    have : r ∈ (inlineTree (toAlt R)).T.regulated := mem_syms_reg hq
    exact hv.regulated r this hn
  | defn d =>
    have : d ∈ (inlineTree (toAlt R)).T.definitions := mem_syms_defn hq
    exact hv.definitions d this hn

theorem base_might : (envAt (inlineTree (toAlt R)) 0).predicates mightName = some [R.alt.action, R.alt.harm] := by
  rw [envAt_base (not_layer hv (by simp [generatedPreds]))]; exact riskEnv_might R

theorem base_class : (envAt (inlineTree (toAlt R)) 0).predicates classPred = some [R.alt.harm, R.sev] := by
  rw [envAt_base (not_layer hv (by simp [generatedPreds]))]; exact riskEnv_class R

theorem base_ms : (envAt (inlineTree (toAlt R)) 0).predicates moreSeverePred = some [R.sev, R.sev] := by
  rw [envAt_base (not_layer hv (by simp [generatedPreds]))]; exact riskEnv_ms R

theorem chooser_ne_sev : R.alt.chooser ≠ R.sev := fun h => hv.fresh (h ▸ hv.sorts.1)
theorem action_ne_sev : R.alt.action ≠ R.sev := fun h => hv.fresh (h ▸ hv.sorts.2.1)
theorem harm_ne_sev : R.alt.harm ≠ R.sev := fun h => hv.fresh (h ▸ hv.sorts.2.2)

theorem harm_const {h c : String} (hm : (h, c) ∈ R.risk.harmClasses) :
    (riskEnv R).constants h = some R.alt.harm ∧ h ∉ R.classes := by
  have := (hv.harmClasses _ hm).1
  have hnc : h ∉ R.classes := fun hc => by
    rw [(hv.classesFresh h hc).1] at this; cases this
  exact ⟨by simp [riskEnv, hnc, this], hnc⟩

/-- A role predicate is a plain base predicate over the chooser, action and harm sorts. -/
theorem role_plain {p : String} (hp : p ∈ VE.Alternatives.roleNames R.alt) :
    PlainPred R p ∧ ∃ ss, (envAt (inlineTree (toAlt R)) 0).predicates p = some ss ∧
      ∀ s ∈ ss, s = R.alt.chooser ∨ s = R.alt.action ∨ s = R.alt.harm := by
  have hav := VE.Alternatives.altValid_of_wellFormed _ hv.alt
  have hng : p ∉ generatedPreds := fun hg => hv.roles p hp (hv.reserved p (List.mem_append_left _ hg))
  have hrole : ∃ ss, (envAt (inlineTree (toAlt R)) 0).predicates p = some ss ∧
      ∀ s ∈ ss, s = R.alt.chooser ∨ s = R.alt.action ∨ s = R.alt.harm := by
    simp only [VE.Alternatives.roleNames, List.mem_append, List.mem_cons, List.not_mem_nil, or_false,
      Option.mem_toList] at hp
    rcases hp with (((h | h) | h) | h) | h
    · subst h; exact ⟨_, VE.Alternatives.base_available hav, by simp [toAlt]⟩
    · subst h; exact ⟨_, VE.Alternatives.base_leadsTo hav, by simp [toAlt]⟩
    · exact ⟨_, VE.Alternatives.base_inaction hav (Option.mem_def.mp h), by simp [toAlt]⟩
    · exact ⟨_, VE.Alternatives.base_taken hav (Option.mem_def.mp h), by simp [toAlt]⟩
    · exact ⟨_, VE.Alternatives.base_proximate hav (Option.mem_def.mp h), by simp [toAlt]⟩
  obtain ⟨ss, hss, hsorts⟩ := hrole
  refine ⟨⟨hng, fun ss' h' => ?_⟩, ss, hss, hsorts⟩
  have := envAt_sub _ _ _ _ hss
  change (riskEnv R).predicates p = some ss at this
  rw [this] at h'
  cases h'
  intro hin
  rcases hsorts _ hin with h | h | h
  · exact chooser_ne_sev hv h.symm
  · exact action_ne_sev hv h.symm
  · exact harm_ne_sev hv h.symm

end Facts

theorem mem_pairs {x y : String} : ∀ {l : List String}, (x, y) ∈ VE.Route.Background.pairs l → x ∈ l ∧ y ∈ l
  | [], h => by simp [VE.Route.Background.pairs] at h
  | a :: l, h => by
    simp only [VE.Route.Background.pairs, List.mem_append, List.mem_map, Prod.mk.injEq] at h
    rcases h with ⟨b, hb, rfl, rfl⟩ | h
    · exact ⟨List.mem_cons_self .., List.mem_cons_of_mem _ hb⟩
    · have := mem_pairs h
      exact ⟨List.mem_cons_of_mem _ this.1, List.mem_cons_of_mem _ this.2⟩

theorem mem_lowerPairs {α : Type} {x y : α} : ∀ {l : List α}, (x, y) ∈ lowerPairs l → x ∈ l ∧ y ∈ l
  | [], h => by simp [lowerPairs] at h
  | a :: l, h => by
    simp only [lowerPairs, List.mem_append, List.mem_map, Prod.mk.injEq] at h
    rcases h with ⟨b, hb, rfl, rfl⟩ | h
    · exact ⟨List.mem_cons_self .., List.mem_cons_of_mem _ hb⟩
    · have := mem_lowerPairs h
      exact ⟨List.mem_cons_of_mem _ this.1, List.mem_cons_of_mem _ this.2⟩

theorem lowerPairs_ne {α : Type} {x y : α} : ∀ {l : List α}, l.Nodup → (x, y) ∈ lowerPairs l → x ≠ y
  | [], _, h => by simp [lowerPairs] at h
  | a :: l, hn, h => by
    simp only [List.nodup_cons] at hn
    simp only [lowerPairs, List.mem_append, List.mem_map, Prod.mk.injEq] at h
    rcases h with ⟨b, hb, rfl, rfl⟩ | h
    · exact fun he => hn.1 (he ▸ hb)
    · exact lowerPairs_ne hn.2 h

theorem lowerPairs_of_ne {α : Type} {x y : α} : ∀ {l : List α}, x ∈ l → y ∈ l → x ≠ y →
    (x, y) ∈ lowerPairs l ∨ (y, x) ∈ lowerPairs l
  | [], hx, _, _ => by cases hx
  | a :: l, hx, hy, hne => by
    simp only [lowerPairs, List.mem_append, List.mem_map, Prod.mk.injEq]
    simp only [List.mem_cons] at hx hy
    rcases hx with hx | hx <;> rcases hy with hy | hy
    · exact absurd (hx.trans hy.symm) hne
    · exact Or.inl (Or.inl ⟨y, hy, hx.symm, rfl⟩)
    · exact Or.inr (Or.inl ⟨x, hx, hy.symm, rfl⟩)
    · rcases lowerPairs_of_ne hx hy hne with h | h
      · exact Or.inl (Or.inr h)
      · exact Or.inr (Or.inr h)

theorem fst_unique {x y y' : String} : ∀ {l : List (String × String)}, (l.map Prod.fst).Nodup →
    (x, y) ∈ l → (x, y') ∈ l → y = y'
  | [], _, h, _ => by cases h
  | a :: l, hn, h1, h2 => by
    simp only [List.map_cons, List.nodup_cons] at hn
    simp only [List.mem_cons] at h1 h2
    rcases h1 with h1 | h1 <;> rcases h2 with h2 | h2
    · rw [← h1] at h2; exact (Prod.mk.inj h2).2.symm
    · exact absurd (List.mem_map.mpr ⟨_, h2, by rw [← h1]⟩) hn.1
    · exact absurd (List.mem_map.mpr ⟨_, h1, by rw [← h2]⟩) hn.1
    · exact fst_unique hn.2 h1 h2

theorem compat_mem {R : RiskDoc} {h c h' c' : String} (h1 : (h, c) ∈ R.risk.harmClasses)
    (h2 : (h', c') ∈ R.risk.harmClasses) (hne : c ≠ c') :
    VE.Formula.not (.eq (.const h) (.const h')) ∈ compatFacts R ∨
      VE.Formula.not (.eq (.const h') (.const h)) ∈ compatFacts R := by
  have hpne : (h, c) ≠ (h', c') := fun he => hne (Prod.mk.injEq _ _ _ _ ▸ he).2
  unfold compatFacts
  rcases lowerPairs_of_ne h1 h2 hpne with hp | hp
  · left
    exact List.mem_map.mpr ⟨((h, c), (h', c')), List.mem_filter.mpr ⟨hp, by simpa using hne⟩, rfl⟩
  · right
    exact List.mem_map.mpr ⟨((h', c'), (h, c)), List.mem_filter.mpr ⟨hp, by simpa using Ne.symm hne⟩, rfl⟩

section Premises
variable {R : RiskDoc} {B : VE.Structure.{u}} (hB : BaseAdmissibleRisk R B)
include hB

theorem prem_mem {p : VE.Formula} (hp : p ∈ riskPremises R) : p.denote B [] := hB.2 p hp

theorem class_functional_of (h s s' : B.Carrier) (hh : B.domain R.alt.harm h) (hs : B.domain R.sev s)
    (hs' : B.domain R.sev s') (h1 : B.relation classPred [h, s]) (h2 : B.relation classPred [h, s']) : s = s' := by
  have := prem_mem hB (p := classFunctional R) (by simp [riskPremises])
  simp only [classFunctional, VE.Formula.denote, VE.Term.denote] at this
  have := this h hh s hs s' hs' ⟨⟨h, s, by simp, by simp, h1⟩, ⟨h, s', by simp, by simp, h2⟩⟩
  obtain ⟨x, hx1, hx2⟩ := this
  simp at hx1 hx2
  rw [hx1, hx2]

theorem sev_closed (s : B.Carrier) (hs : B.domain R.sev s) : ∃ c ∈ R.classes, B.constant c = some s := by
  have := prem_mem hB (p := severityClosure R) (by simp [riskPremises])
  simp only [severityClosure, VE.Formula.denote] at this
  have := (anyF_denote B [s] _).mp (this s hs)
  obtain ⟨φ, hφ, hd⟩ := this
  obtain ⟨c, hc, rfl⟩ := List.mem_map.mp hφ
  simp only [VE.Formula.denote, VE.Term.denote] at hd
  obtain ⟨x, hx1, hx2⟩ := hd
  simp at hx1
  subst hx1
  exact ⟨c, hc, hx2⟩

theorem order_of {c c' : String} (hc : c ∈ R.classes) (hc' : c' ∈ R.classes) {x y : B.Carrier}
    (hx : B.constant c = some x) (hy : B.constant c' = some y) :
    B.relation moreSeverePred [x, y] ↔ (c, c') ∈ closure R := by
  have hmem : orderLiteral R (c, c') ∈ riskPremises R := by
    simp only [riskPremises, List.mem_cons, List.mem_append]
    right; right; left; right
    exact List.mem_map.mpr ⟨(c, c'), List.mem_flatMap.mpr ⟨c, hc, List.mem_map.mpr ⟨c', hc', rfl⟩⟩, rfl⟩
  have := prem_mem hB hmem
  unfold orderLiteral at this
  split at this
  · rename_i hin
    simp only [VE.Formula.denote, VE.Term.denote, hx, hy, Option.some.injEq] at this
    obtain ⟨_, _, rfl, rfl, hr⟩ := this
    exact ⟨fun _ => by simpa using hin, fun _ => hr⟩
  · rename_i hin
    simp only [VE.Formula.denote, VE.Term.denote, hx, hy, Option.some.injEq] at this
    constructor
    · intro hr
      exact absurd ⟨x, y, rfl, rfl, hr⟩ this
    · intro hin'
      exact absurd (by simpa using hin') hin

end Premises

/-! ### The expansion satisfies the risk background -/

theorem inl_injective {α β : Type _} : Function.Injective (Sum.inl : α → α ⊕ β) := fun _ _ h => Sum.inl.inj h

section ExpansionProofs
variable {R : RiskDoc} {B₀ : VE.Structure.{u}} (hv : RiskValid R)
include hv

theorem headD_mem : R.classes.headD "" ∈ R.classes := by
  have := hv.nonempty
  cases hc : R.classes with
  | nil => exact absurd hc this
  | cons c cs => simp

theorem expand_admissible (hB₀ : BaseAdmissibleAlt (toAlt R) B₀) :
    (expand R B₀).Admissible (envAt (inlineTree (toAlt R)) 0) := by
  have hA := hB₀.1.1
  have hav := VE.Alternatives.altValid_of_wellFormed _ hv.alt
  refine ⟨fun c s hc => ?_, fun p vs hr => ?_⟩
  · have hc' : (riskEnv R).constants c = some s := hc
    by_cases hcl : c ∈ R.classes
    · simp only [riskEnv, hcl, if_true, Option.some.injEq] at hc'
      subst hc'
      exact ⟨.inr c, by simp [expand, hcl], by simp [expand, hcl]⟩
    · have hE : R.E.constants c = some s := by simpa [riskEnv, hcl] using hc'
      by_cases hs : s = R.sev
      · subst hs
        exact ⟨.inr (R.classes.headD ""), by simp [expand, hcl, hE], by show R.sev = R.sev ∧ _; exact ⟨rfl, headD_mem hv⟩⟩
      · obtain ⟨v₀, h1, h2⟩ := hA.1 c s hc
        have hne : R.E.constants c ≠ some R.sev := by rw [hE]; simpa using hs
        exact ⟨.inl v₀, by simp [expand_const_plain hcl hne, h1], by simp [expand, hs, h2]⟩
  · by_cases h1 : p = mightName
    · subst h1
      simp only [expand, if_true] at hr
      obtain ⟨a, h, rfl, hl⟩ := hr
      obtain ⟨ss, hss, ht⟩ := hA.2 _ _ hl
      have hlt : (envAt (inlineTree (toAlt R)) 0).predicates R.alt.leadsTo = some [R.alt.action, R.alt.harm] :=
        VE.Alternatives.base_leadsTo hav
      rw [hlt] at hss
      cases hss
      exact ⟨_, base_might hv, by simp [expand, VE.TupleTyped, action_ne_sev hv, harm_ne_sev hv, ht.1, ht.2.1]⟩
    by_cases h2 : p = classPred
    · subst h2
      simp only [expand, h1, if_false, if_true] at hr
      obtain ⟨h, c, rfl, hc, hm, hk⟩ := hr
      obtain ⟨hk', _⟩ := harm_const hv hm
      obtain ⟨v, hv1, hv2⟩ := hA.1 hc R.alt.harm hk'
      rw [hk] at hv1
      cases hv1
      exact ⟨_, base_class hv, by
        simp [expand, VE.TupleTyped, harm_ne_sev hv, hv2, (hv.harmClasses _ hm).2]⟩
    by_cases h3 : p = moreSeverePred
    · subst h3
      simp only [expand, h1, h2, if_false, if_true] at hr
      obtain ⟨c, c', rfl, hcl⟩ := hr
      have := hv.closureClasses _ hcl
      exact ⟨_, base_ms hv, by simp [expand, VE.TupleTyped, this.1, this.2]⟩
    · simp only [expand, h1, h2, h3, if_false] at hr
      obtain ⟨hp, vs₀, rfl, h0⟩ := hr
      obtain ⟨ss, hss, ht⟩ := hA.2 _ _ h0
      have hsub : (riskEnv R).predicates p = some ss := envAt_sub _ _ _ _ hss
      exact ⟨ss, hss, (expand_tupleTyped (fun s hs he => hp.2 ss hsub (he ▸ hs)) vs₀).mpr ht⟩

theorem expand_literals (hB₀ : BaseAdmissibleAlt (toAlt R) B₀) :
    Sat (expand R B₀) (backgroundBase (inlineTree (toAlt R))) := by
  intro a ha
  have h0 := hB₀.1.2 a ha
  simp only [backgroundBase, VE.Route.Background.literals, List.mem_map] at ha
  obtain ⟨⟨x, y⟩, hp, rfl⟩ := ha
  have hxy := mem_pairs hp
  simp only [VE.Route.sortStrings, List.mem_mergeSort] at hxy
  have hx := hv.lits x hxy.1
  have hy := hv.lits y hxy.2
  have := denote_transport (B := expand R B₀) Sum.inl inl_injective
    (VE.Route.Background.literalPremise (x, y)) []
    (by simp [VE.Route.Background.literalPremise, binderSorts])
    (by
      intro c hc
      simp only [VE.Route.Background.literalPremise, formulaConsts, termConsts, List.mem_append,
        List.mem_singleton] at hc
      rcases hc with rfl | rfl
      · exact expand_const_plain hx.2 hx.1
      · exact expand_const_plain hy.2 hy.1)
    (by simp [VE.Route.Background.literalPremise, preds])
  exact this.mpr h0

omit hv in
theorem altPremise_symbols {a : VE.Formula} (ha : a ∈ VE.Alternatives.altPremises (toAlt R)) :
    (∀ s ∈ binderSorts a, s = R.alt.chooser ∨ s = R.alt.action ∨ s = R.alt.harm) ∧
    formulaConsts a = [] ∧ ∀ p ∈ preds a, p ∈ VE.Alternatives.roleNames R.alt := by
  simp only [VE.Alternatives.altPremises, List.mem_cons, List.mem_append, VE.Alternatives.oneTakenPremise,
    VE.Alternatives.oneInactionPremise, VE.Alternatives.proximatePremise, Option.mem_toList,
    Option.map_eq_some_iff] at ha
  rcases ha with rfl | ((⟨p, hp, rfl⟩ | ⟨p, hp, rfl⟩) | ⟨p, hp, rfl⟩)
  · simp [VE.Alternatives.ownPremise, binderSorts, formulaConsts, termConsts, preds, VE.Alternatives.roleNames,
      toAlt]
  · have hp' : R.alt.taken = some p := hp
    simp [VE.Alternatives.oneOf, binderSorts, formulaConsts, termConsts, preds, VE.Alternatives.roleNames, toAlt, hp']
  · have hp' : R.alt.inaction = some p := hp
    simp [VE.Alternatives.oneOf, binderSorts, formulaConsts, termConsts, preds, VE.Alternatives.roleNames, toAlt, hp']
  · have hp' : R.alt.proximate = some p := hp
    simp [binderSorts, formulaConsts, termConsts, preds, VE.Alternatives.roleNames, toAlt, hp']

theorem expand_altPremises (hB₀ : BaseAdmissibleAlt (toAlt R) B₀) :
    Sat (expand R B₀) (VE.Alternatives.altPremises (toAlt R)) := by
  intro a ha
  obtain ⟨hs, hc, hp⟩ := altPremise_symbols ha
  have := denote_transport (B := expand R B₀) Sum.inl inl_injective a []
    (fun s h v => by
      apply expand_domain_old
      rcases hs s h with rfl | rfl | rfl
      · exact chooser_ne_sev hv
      · exact action_ne_sev hv
      · exact harm_ne_sev hv)
    (by rw [hc]; simp)
    (fun p h vs => expand_relation_plain (role_plain hv (hp p h)).1 vs)
  exact this.mpr (hB₀.2 a ha)

omit hv in
theorem expand_const_class {c : String} (hc : c ∈ R.classes) : (expand R B₀).constant c = some (.inr c) := by
  simp [expand, hc]

omit hv in
theorem expand_ms (x y : String) :
    (expand R B₀).relation moreSeverePred [.inr x, .inr y] ↔ (x, y) ∈ closure R := by
  simp only [expand, moreSeverePred, mightName, classPred]
  simp only [if_neg (by decide : ¬("risk__more_severe" = "risk__might_lead_to")),
    if_neg (by decide : ¬("risk__more_severe" = "risk__class")), if_true]
  constructor
  · rintro ⟨c, c', he, h⟩
    simp only [List.cons.injEq, Sum.inr.injEq, and_true] at he
    obtain ⟨rfl, rfl⟩ := he
    exact h
  · intro h
    exact ⟨x, y, rfl, h⟩

theorem expand_riskPremises (hB₀ : BaseAdmissibleAlt (toAlt R) B₀) (hc : Sat B₀ (compatFacts R)) :
    Sat (expand R B₀) (riskPremises R) := by
  have hA := hB₀.1.1
  have leads_plain := (role_plain hv (p := R.alt.leadsTo) (by simp [VE.Alternatives.roleNames])).1
  intro a ha
  simp only [riskPremises, List.mem_cons, List.mem_append] at ha
  rcases ha with rfl | rfl | ((ha | ha) | rfl | ha)
  · -- certain_possible
    simp only [certainPossible, VE.Formula.denote, VE.Term.denote]
    intro x _ y _ ⟨v, w, hv', hw', hl⟩
    simp only [List.getElem?_cons_succ, List.getElem?_cons_zero, Option.some.injEq] at hv' hw'
    subst hv' hw'
    obtain ⟨vs₀, hvs, h0⟩ := (expand_relation_plain leads_plain _).mp hl
    match vs₀, hvs with
    | [a₀, h₀], hvs =>
      simp only [List.map_cons, List.map_nil, List.cons.injEq, and_true] at hvs
      obtain ⟨rfl, rfl⟩ := hvs
      exact ⟨.inl a₀, .inl h₀, rfl, rfl, by simp only [expand, if_true]; exact ⟨a₀, h₀, rfl, h0⟩⟩
  · -- severity_closure
    simp only [severityClosure, VE.Formula.denote]
    intro v hv'
    cases v with
    | inl v₀ => simp [expand] at hv'
    | inr c =>
      simp only [expand] at hv'
      apply (anyF_denote _ _ _).mpr
      exact ⟨_, List.mem_map.mpr ⟨c, hv'.2, rfl⟩, by
        simp [VE.Formula.denote, VE.Term.denote, expand_const_class hv'.2]⟩
  · -- classes_distinct
    simp only [classesDistinct, List.mem_map] at ha
    obtain ⟨⟨x, y⟩, hp, rfl⟩ := ha
    have hne := lowerPairs_ne hv.nodup hp
    have hm := mem_lowerPairs hp
    simp only [VE.Formula.denote, VE.Term.denote, expand_const_class hm.1, expand_const_class hm.2]
    rintro ⟨w, h1, h2⟩
    cases h1
    exact hne (Sum.inr.inj (Option.some.inj h2)).symm
  · -- order
    simp only [orderTable, List.mem_map] at ha
    obtain ⟨⟨x, y⟩, hp, rfl⟩ := ha
    simp only [classPairs, List.mem_flatMap, List.mem_map, Prod.mk.injEq] at hp
    obtain ⟨x', hx, y', hy, rfl, rfl⟩ := hp
    unfold orderLiteral
    split
    · rename_i hin
      simp only [VE.Formula.denote, VE.Term.denote, expand_const_class hx, expand_const_class hy]
      exact ⟨_, _, rfl, rfl, (expand_ms x' y').mpr (by simpa using hin)⟩
    · rename_i hin
      simp only [VE.Formula.denote, VE.Term.denote, expand_const_class hx, expand_const_class hy]
      rintro ⟨_, _, h1, h2, hr⟩
      cases h1; cases h2
      exact hin (by simpa using (expand_ms x' y').mp hr)
  · -- class_functional
    simp only [classFunctional, VE.Formula.denote, VE.Term.denote]
    intro h _ s _ s' _ ⟨⟨v1, w1, e1, f1, r1⟩, ⟨v2, w2, e2, f2, r2⟩⟩
    simp only [List.getElem?_cons_succ, List.getElem?_cons_zero, Option.some.injEq] at e1 f1 e2 f2
    subst e1 f1 e2 f2
    simp only [expand, classPred, mightName, moreSeverePred] at r1 r2
    simp only [if_neg (by decide : ¬("risk__class" = "risk__might_lead_to")), if_true] at r1 r2
    obtain ⟨h1, c1, he1, hc1, hm1, hk1⟩ := r1
    obtain ⟨h2, c2, he2, hc2, hm2, hk2⟩ := r2
    simp only [List.cons.injEq, and_true] at he1 he2
    obtain ⟨rfl, rfl⟩ := he1
    obtain ⟨hh, rfl⟩ := he2
    cases hh
    refine ⟨.inr c1, rfl, ?_⟩
    by_cases hcc : c1 = c2
    · subst hcc; simp
    · exfalso
      rcases compat_mem hm1 hm2 hcc with hf | hf
      · have := hc _ hf
        simp only [VE.Formula.denote, VE.Term.denote] at this
        exact this ⟨h1, hk1, hk2⟩
      · have := hc _ hf
        simp only [VE.Formula.denote, VE.Term.denote] at this
        exact this ⟨h1, hk2, hk1⟩
  · -- class facts
    simp only [classFacts, List.mem_map] at ha
    obtain ⟨⟨h, c⟩, hm, rfl⟩ := ha
    obtain ⟨hk, hnc⟩ := harm_const hv hm
    obtain ⟨v₀, h1, _⟩ := hA.1 h R.alt.harm hk
    have hne : R.E.constants h ≠ some R.sev := by
      rw [(hv.harmClasses _ hm).1]; simpa using harm_ne_sev hv
    simp only [VE.Formula.denote, VE.Term.denote, expand_const_plain hnc hne, h1,
      expand_const_class (hv.harmClasses _ hm).2]
    refine ⟨.inl v₀, .inr c, rfl, rfl, ?_⟩
    simp only [expand, classPred, mightName]
    simp only [if_neg (by decide : ¬("risk__class" = "risk__might_lead_to")), if_true]
    exact ⟨v₀, c, rfl, h, hm, h1⟩

theorem expand_reduct : ReductVia R B₀ (expand R B₀) Sum.inl := by
  refine ⟨inl_injective, fun s hs v => expand_domain_old (fun he => hv.fresh (he ▸ hs)) v,
    fun c hc => ?_, fun p hp vs => ?_⟩
  · simp only [oldEnvRisk] at hc
    split at hc
    · exact absurd rfl hc
    · rename_i hcond
      have hcl : c ∉ R.classes := fun h => hcond (Or.inl h)
      apply expand_const_plain hcl
      intro he
      apply hcond
      right
      change (riskEnv R).constants c = some R.sev
      simp [riskEnv, hcl, he]
  · simp only [oldEnvRisk] at hp
    split at hp
    · exact absurd rfl hp
    · rename_i hcond
      apply expand_relation_plain
      refine ⟨fun h => hcond (Or.inl h), fun ss hss hin => hcond (Or.inr ?_)⟩
      cases h0 : (envAt (inlineTree (toAlt R)) 0).predicates p with
      | none => rw [h0] at hp; exact absurd rfl hp
      | some ss0 =>
        have := envAt_sub _ _ _ _ h0
        change (riskEnv R).predicates p = some ss0 at this
        rw [this] at hss
        cases hss
        simpa using hin

end ExpansionProofs

/-- 4.6: every structure satisfying alt's background and the compatibility facts expands, on the old carrier
plus one fresh element per class, to a `BaseAdmissibleRisk` structure whose old reduct is the given one
(`ReductVia` states the embedding). -/
theorem risk_expansion (R : RiskDoc) (h : WellFormedRisk R = true) (B₀ : VE.Structure.{u})
    (hB₀ : BaseAdmissibleAlt (toAlt R) B₀) (hc : Sat B₀ (compatFacts R)) :
    ∃ (B : VE.Structure.{u}) (e : B₀.Carrier → B.Carrier), BaseAdmissibleRisk R B ∧ ReductVia R B₀ B e := by
  have hv := riskValid_of_wellFormed R h
  exact ⟨expand R B₀, Sum.inl, ⟨⟨⟨expand_admissible hv hB₀, expand_literals hv hB₀⟩, expand_altPremises hv hB₀⟩,
    expand_riskPremises hv hB₀ hc⟩, expand_reduct hv⟩

/-- The compatibility facts hold in every `BaseAdmissibleRisk` structure. -/
theorem compat_sat {R : RiskDoc} (hv : RiskValid R) {B : VE.Structure.{u}} (hB : BaseAdmissibleRisk R B) :
    Sat B (compatFacts R) := by
  intro a ha
  simp only [compatFacts, List.mem_map, List.mem_filter] at ha
  obtain ⟨⟨⟨h, c⟩, ⟨h', c'⟩⟩, ⟨hp, hne⟩, rfl⟩ := ha
  simp only [bne_iff_ne, ne_eq] at hne
  have hm := mem_lowerPairs hp
  have hA := hB.1.1.1
  simp only [VE.Formula.denote, VE.Term.denote]
  rintro ⟨v, hk, hk'⟩
  have fact : ∀ {x y : String}, (x, y) ∈ R.risk.harmClasses → ∃ w, B.constant y = some w ∧
      B.domain R.sev w ∧ B.relation classPred [v, w] ∨ B.constant x ≠ some v := by
    intro x y hxy
    by_cases hx : B.constant x = some v
    · have hf := hB.2 _ (by
        simp only [riskPremises, List.mem_cons, List.mem_append]
        right; right; right; right
        exact List.mem_map.mpr ⟨(x, y), hxy, rfl⟩ : VE.Formula.binary classPred (.const x) (.const y) ∈ riskPremises R)
      simp only [VE.Formula.denote, VE.Term.denote, hx] at hf
      obtain ⟨x', w, hx', hw, hr⟩ := hf
      cases hx'
      have hcy : (envAt (inlineTree (toAlt R)) 0).constants y = some R.sev := by
        change (riskEnv R).constants y = some R.sev
        simp [riskEnv, (hv.harmClasses _ hxy).2]
      obtain ⟨w', hw', hd⟩ := hA.1 y R.sev hcy
      rw [hw] at hw'
      cases hw'
      exact ⟨w, Or.inl ⟨hw, hd, hr⟩⟩
    · exact ⟨v, Or.inr hx⟩
  obtain ⟨w, hw⟩ := fact hm.1
  obtain ⟨w', hw'⟩ := fact hm.2
  rcases hw with ⟨hw, hd, hr⟩ | hw
  · rcases hw' with ⟨hw', hd', hr'⟩ | hw'
    · have hcv : (envAt (inlineTree (toAlt R)) 0).constants h = some R.alt.harm := (harm_const hv hm.1).1
      obtain ⟨v', hv', hdv⟩ := hA.1 h R.alt.harm hcv
      rw [hk] at hv'
      cases hv'
      have := class_functional_of hB v w w' hdv hd hd' hr hr'
      subst this
      have hcm : c ∈ R.classes := (hv.harmClasses _ hm.1).2
      have hcm' : c' ∈ R.classes := (hv.harmClasses _ hm.2).2
      rcases lowerPairs_of_ne hcm hcm' hne with hl | hl
      · have := hB.2 (.not (.eq (.const c) (.const c'))) (by
          simp only [riskPremises, List.mem_cons, List.mem_append]
          right; right; left; left
          unfold classesDistinct
          exact List.mem_map.mpr ⟨(c, c'), hl, rfl⟩)
        exact this ⟨w, hw, hw'⟩
      · have := hB.2 (.not (.eq (.const c') (.const c))) (by
          simp only [riskPremises, List.mem_cons, List.mem_append]
          right; right; left; left
          unfold classesDistinct
          exact List.mem_map.mpr ⟨(c', c), hl, rfl⟩)
        exact this ⟨w, hw', hw⟩
    · exact hw' hk'
  · exact hw hk

/-- 4.6: over the old signature, the risk premises add exactly the compatibility facts. -/
theorem risk_conservative (R : RiskDoc) (h : WellFormedRisk R = true) (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (oldEnvRisk R) []) (hφ : φ.WellFormed (oldEnvRisk R) []) :
    (∀ B : VE.Structure.{u}, BaseAdmissibleRisk R B → Sat B Γ → φ.denote B []) ↔
    (∀ B : VE.Structure.{u}, BaseAdmissibleAlt (toAlt R) B → Sat B (compatFacts R) → Sat B Γ → φ.denote B []) := by
  have hv := riskValid_of_wellFormed R h
  constructor
  · intro hall B₀ hB₀ hc hs
    obtain ⟨B, e, hB, hr⟩ := risk_expansion R h B₀ hB₀ hc
    exact (reduct_denote hr hφ).mp (hall B hB (fun a ha => (reduct_denote hr (hΓ a ha)).mpr (hs a ha)))
  · intro hall B hB hs
    exact hall B hB.1 (compat_sat hv hB) hs

end VE.Risk
