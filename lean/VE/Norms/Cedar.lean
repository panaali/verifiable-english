import VE.Norms.Elaborate

/-! The Cedar adapter's tree shape (docs/spec/norms.md section 8). The adapter
translates each permit into a positive rule and each forbid into a negative
rule taking precedence over every permit; there are no carve-outs and no
nesting among permits or among forbids. `cedar_decision`: on every structure
the completed outcome of a deny-by-default `permitted` is exactly "some permit
applies and no forbid applies" (Cedar's "forbid overrides"), and opposite
selections are impossible, so the intra-predicate conflict formula is
unsatisfiable. The condition translation table itself is Python only. -/
namespace VE.Norms
universe u

/-- The adapter's shape on predicate `p`. -/
structure CedarShape (T : Tree) (p : String) : Prop where
  names : (T.nodes.map Node.name).Nodup
  noCarve : ∀ N ∈ rulesOn T p, N.carveOuts = []
  permitsFlat : ∀ N ∈ rulesOn T p, N.sign = true → N.over = []
  forbidsOverPermits : ∀ N ∈ rulesOn T p, N.sign = false →
    ∀ M ∈ rulesOn T p, M.sign = true → M.name ∈ N.over
  forbidsOnlyOverPermits : ∀ N ∈ rulesOn T p, N.sign = false →
    ∀ m ∈ N.over, ∃ M ∈ rulesOn T p, M.sign = true ∧ M.name = m

theorem mem_rulesOn {T : Tree} {p : String} {N : Node} : N ∈ rulesOn T p ↔ N ∈ T.nodes ∧ N.pred = p := by
  simp [rulesOn]

section
variable {T : Tree} {p : String} (hs : CedarShape T p) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
include hs

theorem cedar_children_forbid {N : Node} (hN : N ∈ rulesOn T p) (hneg : N.sign = false) :
    children T N = [] := by
  apply List.eq_nil_iff_forall_not_mem.mpr
  intro C hC
  simp only [children, mem_sortBy, List.mem_filter, Bool.and_eq_true, beq_iff_eq,
    List.contains_iff_mem] at hC
  obtain ⟨hC, hp, hover⟩ := hC
  have hCp : C ∈ rulesOn T p := mem_rulesOn.mpr ⟨hC, hp.trans (mem_rulesOn.mp hN).2⟩
  cases hsC : C.sign
  · obtain ⟨M, hM, hMs, hMn⟩ := hs.forbidsOnlyOverPermits C hCp hsC N.name hover
    have hMN : M = N := by
      have h₁ := (mem_rulesOn.mp hM).1
      have h₂ := (mem_rulesOn.mp hN).1
      obtain ⟨i, hi⟩ := List.mem_iff_getElem?.mp h₁
      obtain ⟨j, hj⟩ := List.mem_iff_getElem?.mp h₂
      have hi' : (T.nodes.map Node.name)[i]? = some N.name := by simp [hi, hMn]
      have hj' : (T.nodes.map Node.name)[j]? = some N.name := by simp [hj]
      have := nodup_getElemOpt_inj hs.names hi' hj'
      subst this; rw [hi] at hj; exact Option.some.inj hj
    rw [hMN] at hMs; rw [hMs] at hneg; cases hneg
  · rw [hs.permitsFlat C hCp hsC] at hover; cases hover

theorem cedar_children_permit {N : Node} (hN : N ∈ rulesOn T p) (hpos : N.sign = true) (C : Node) :
    C ∈ children T N ↔ C ∈ rulesOn T p ∧ C.sign = false := by
  simp only [children, mem_sortBy, List.mem_filter, Bool.and_eq_true, beq_iff_eq,
    List.contains_iff_mem]
  have hNp := (mem_rulesOn.mp hN).2
  constructor
  · rintro ⟨hC, hp, hover⟩
    have hCp : C ∈ rulesOn T p := mem_rulesOn.mpr ⟨hC, hp.trans hNp⟩
    refine ⟨hCp, ?_⟩
    cases hsC : C.sign
    · rfl
    · rw [hs.permitsFlat C hCp hsC] at hover; cases hover
  · rintro ⟨hCp, hsC⟩
    obtain ⟨hC, hp⟩ := mem_rulesOn.mp hCp
    exact ⟨hC, hp.trans hNp.symm, hs.forbidsOverPermits C hCp hsC N hN hpos⟩

theorem cedar_applies {N : Node} (hN : N ∈ rulesOn T p) : AppliesD S ρ N ↔ N.guard.denote S ρ := by
  simp [AppliesD, hs.noCarve N hN]

theorem cedar_yields_forbid {N : Node} (hN : N ∈ rulesOn T p) (hneg : N.sign = false) :
    ∀ f, YieldsD T S ρ f N ↔ N.guard.denote S ρ
  | 0 => cedar_applies hs S ρ hN
  | f + 1 => by
    simp only [YieldsD, cedar_children_forbid hs hN hneg, List.not_mem_nil, false_and, exists_false,
      or_false]
    exact cedar_applies hs S ρ hN

end

/-- `cedar_decision`: the adapter's decision is `permit and not forbid`, and the
two sides never both decide. -/
theorem cedar_decision {T : Tree} (r : Regulated) (hd : r.allowByDefault = false) (hs : CedarShape T r.name)
    (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    ((outcome T r).denote S ρ ↔
      (∃ N ∈ rulesOn T r.name, N.sign = true ∧ N.guard.denote S ρ) ∧
        ¬ ∃ N ∈ rulesOn T r.name, N.sign = false ∧ N.guard.denote S ρ) ∧
    ¬ ((pos T r.name).denote S ρ ∧ (neg T r.name).denote S ρ) := by
  have hforbid : ∀ N ∈ rulesOn T r.name, N.sign = false →
      (SelectsD T S ρ (fuel T) N ↔ N.guard.denote S ρ) := by
    intro N hN hneg
    simp only [SelectsD, cedar_children_forbid hs hN hneg, List.not_mem_nil, false_and,
      exists_false, not_false_eq_true, and_true]
    exact cedar_applies hs S ρ hN
  have hpermit : ∀ N ∈ rulesOn T r.name, N.sign = true →
      (SelectsD T S ρ (fuel T) N ↔
        N.guard.denote S ρ ∧ ¬ ∃ M ∈ rulesOn T r.name, M.sign = false ∧ M.guard.denote S ρ) := by
    intro N hN hpos
    simp only [SelectsD, cedar_applies hs S ρ hN]
    apply and_congr_right
    intro _
    apply not_congr
    constructor
    · rintro ⟨C, hC, hy⟩
      obtain ⟨hCp, hsC⟩ := (cedar_children_permit hs hN hpos C).mp hC
      exact ⟨C, hCp, hsC, (cedar_yields_forbid hs S ρ hCp hsC _).mp hy⟩
    · rintro ⟨C, hCp, hsC, hg⟩
      exact ⟨C, (cedar_children_permit hs hN hpos C).mpr ⟨hCp, hsC⟩,
        (cedar_yields_forbid hs S ρ hCp hsC _).mpr hg⟩
  have hP : (pos T r.name).denote S ρ ↔
      (∃ N ∈ rulesOn T r.name, N.sign = true ∧ N.guard.denote S ρ) ∧
        ¬ ∃ N ∈ rulesOn T r.name, N.sign = false ∧ N.guard.denote S ρ := by
    rw [pos, decides_denote]
    constructor
    · rintro ⟨N, hN, hsN, hsel⟩
      obtain ⟨hg, hno⟩ := (hpermit N hN hsN).mp hsel
      exact ⟨⟨N, hN, hsN, hg⟩, hno⟩
    · rintro ⟨⟨N, hN, hsN, hg⟩, hno⟩
      exact ⟨N, hN, hsN, (hpermit N hN hsN).mpr ⟨hg, hno⟩⟩
  have hN : (neg T r.name).denote S ρ ↔ ∃ N ∈ rulesOn T r.name, N.sign = false ∧ N.guard.denote S ρ := by
    rw [neg, decides_denote]
    constructor
    · rintro ⟨N, hN, hsN, hsel⟩; exact ⟨N, hN, hsN, (hforbid N hN hsN).mp hsel⟩
    · rintro ⟨N, hN, hsN, hg⟩; exact ⟨N, hN, hsN, (hforbid N hN hsN).mpr hg⟩
  refine ⟨?_, fun ⟨hp, hn⟩ => (hP.mp hp).2 (hN.mp hn)⟩
  rw [outcome_denote, hd]
  exact hP

end VE.Norms
