import VE.Attribution.Scoped

/-! Spec 9.3, assessments (5.3): each assessment unit contributes one generated
open term on the evidence sort with its complete record; the judgment is not
factive, `may` and `probably` are independent, and inner and outer negation of
`probably` are different keys when both nodes occur. -/
namespace VE.Reports
open VE.Route (fol)
universe u

theorem unitOf_eq {D : ReportDoc} (hw : WF D) {u : Unit} (hu : u ∈ D.units) : unitOf D u.id = some u := by
  unfold unitOf
  cases hf : D.units.find? (·.id == u.id) with
  | none => exact absurd (by simp) (List.find?_eq_none.mp hf u hu)
  | some x =>
    have hx := List.mem_of_find?_eq_some hf
    have he : x.id = u.id := findEq hf
    rw [inj_of_nodup_map Unit.id D.units hw.ids x hx u hu he]

theorem assessment_open_term (D : ReportDoc) (h : WellFormedReports D = true) (u : Unit) (hu : u ∈ D.units)
    (j : Judgment) (a : String) (b : Content)
    (hc : u.content = .assessment j a b ∨ u.content = .negated (.assessment j a b)) :
    assessName D ⟨j, a, contentId D b⟩ ∈ openTerms D ∧
    (envReports D).predicates (assessName D ⟨j, a, contentId D b⟩) = some [D.evidence] ∧
    ∃ r, recordOf D a = some r ∧ r.decidedBy ≠ "" := by
  have hw := wf_of h
  have ho : Occurs D (.assessment j a b) := by
    rcases hc with hc | hc
    · exact ⟨u, hu, by rw [hc]; exact Content.mem_nodes_self _⟩
    · exact ⟨u, hu, by rw [hc]; exact operand_mem_negated⟩
  have hk := assess_key_mem ho
  refine ⟨List.mem_map_of_mem hk, envReports_pred_assess hw hk, ?_⟩
  have hn := nodeOk_of_occurs hw ho
  simp only [nodeOk, Option.isSome_iff_exists] at hn
  obtain ⟨r, hr⟩ := hn
  refine ⟨r, hr, fun he => ?_⟩
  have := hw.assess r (recordOf_mem hr).1
  simp only [assessmentOk, VE.Route.Admission.token, he, Bool.and_eq_true, Bool.not_eq_true'] at this
  exact absurd this.1.2.1.1 (by decide)

theorem assessment_not_factive (D : ReportDoc) (h : WellFormedReports D = true) (u : Unit) (hu : u ∈ D.units)
    (j : Judgment) (a : String) (q : VE.Formula)
    (hc : u.content = .assessment j a (.formula q))
    (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) (he : Expandable D S₀) (hn : ¬ q.denote S₀ []) :
    ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M ∧ ¬ q.denote (interp D M) [] := by
  have hq : q.WellFormed D.E [] := occurs_formula_wellFormed (wf_of h)
    ⟨u, hu, by rw [hc]; exact body_mem_assessment⟩
  obtain ⟨M, hM, hi⟩ := source_over_any_structure D h S₀ h₀ he
  refine ⟨M, hM, hi, fun hq' => hn ?_⟩
  rw [← hM]
  exact (old_formula_invariant D h M q hq).mp hq'

theorem may_probably_independent (D : ReportDoc) (h : WellFormedReports D = true) (a q : String) :
    assessName D ⟨.may, a, q⟩ ≠ assessName D ⟨.probably, a, q⟩ ∧
    ∀ (f : Judgment → Bool) (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E), Expandable D S₀ →
      (∀ j, ⟨j, a, q⟩ ∉ topAKeys D) →
      ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M ∧
        ∀ j v, M.S.domain D.evidence v → (M.A j a q v ↔ f j = true) := by
  refine ⟨fun he => ?_, fun f S₀ h₀ he hk => ?_⟩
  · have := congrArg String.data he
    simp [assessName, Judgment.name, String.data_append] at this
  · refine ⟨mkSource D (wf_of h) S₀ h₀ (fun _ _ => False) (fun k _ => f k.j = true), rfl,
      mkSource_intended D (wf_of h) S₀ h₀ he _ _, fun j v hv => ?_⟩
    constructor
    · rintro (ha | ⟨_, _, hf⟩)
      · exact absurd (assertedA_top ha) (hk j)
      · exact hf
    · intro hf
      exact Or.inr ⟨hk j, hv, hf⟩

/-- Both `probably` nodes occur, so both formula bodies are digested. -/
theorem probably_not_scopes_distinct (D : ReportDoc) (h : WellFormedReports D = true) (a : String)
    (q : VE.Formula)
    (ho : Occurs D (.assessment .probably a (.formula (.not q))))
    (ho' : Occurs D (.assessment .probably a (.formula q))) :
    canonicalObject D (.formula (.not q)) ≠ canonicalObject D (.formula q) ∧
    assessName D ⟨.probably, a, contentId D (.formula (.not q))⟩ ≠
      assessName D ⟨.probably, a, contentId D (.formula q)⟩ := by
  have hobj : canonicalObject D (.formula (.not q)) ≠ canonicalObject D (.formula q) :=
    fun he => not_ne_self q (canonicalObject_formula_inj he)
  refine ⟨hobj, fun hn => hobj ?_⟩
  have hk := assessName_inj (wf_of h) (assess_key_mem ho) (assess_key_mem ho') hn
  simp only [AssessKey.mk.injEq, true_and] at hk
  exact no_collision D h _ _ (occurs_sub ho body_mem_assessment) (occurs_sub ho' body_mem_assessment) hk

end VE.Reports
