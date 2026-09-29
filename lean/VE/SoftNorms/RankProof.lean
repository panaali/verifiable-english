import VE.SoftNorms.Coherence

/-! Comparable default rules remain mutually exclusive after full layer substitution,
even in structures with undefined or ill-typed constants. The proof interprets
the substituted eligibility and dominance formulas directly, then repeats the
rank-fuel argument without an admissibility assumption. -/
namespace VE.SoftNorms
open VE.Norms
universe u

private def RawEligible (D : SoftDoc) (B : VE.Structure.{u}) (ρ : VE.Valuation B)
    (N : SoftNode) : Prop := (circ D (eligibleF D N)).denote B ρ

private def RawOutweighs (D : SoftDoc) (B : VE.Structure.{u}) (ρ : VE.Valuation B)
    (a L H : String) : Prop := (circ D (outweighsF D a L H)).denote B ρ

private def RawDom (D : SoftDoc) (B : VE.Structure.{u}) (ρ : VE.Valuation B)
    (eff : SoftNode → Prop) (N : SoftNode) : Prop :=
  ∃ M ∈ D.T.nodes, Incompatible D M N = true ∧ M.mode = .default ∧ Comparable D M N = true ∧
    ((higher D M N = true ∧ eff M ∧
        (D.soft.outranking = .holistic → ¬ RawOutweighs D B ρ (act D N) (rk N) (rk M))) ∨
     (D.soft.outranking = .holistic ∧ higher D N M = true ∧ RawEligible D B ρ M ∧
        RawOutweighs D B ρ (act D N) (rk M) (rk N)))

private def RawEff (D : SoftDoc) (B : VE.Structure.{u}) (ρ : VE.Valuation B) :
    Nat → SoftNode → Prop
  | 0, N => RawEligible D B ρ N
  | g + 1, N => RawEligible D B ρ N ∧ ¬ RawDom D B ρ (RawEff D B ρ g) N

theorem raw_dom_denote (D : SoftDoc) (B : VE.Structure.{u}) (ρ : VE.Valuation B)
    (eff : SoftNode → VE.Formula) (effP : SoftNode → Prop)
    (he : ∀ M, (circ D (eff M)).denote B ρ ↔ effP M) (N : SoftNode) :
    (circ D (domWith D eff N)).denote B ρ ↔ RawDom D B ρ effP N := by
  simp only [domWith, circ, subst, substWith_anyF, anyF_denote, List.mem_map, opponents,
    List.mem_filter, Bool.and_eq_true, beq_iff_eq, RawDom]
  constructor
  · rintro ⟨_, ⟨_, ⟨M, ⟨hM, ⟨hi, hd⟩, hc⟩, rfl⟩, rfl⟩, h⟩
    refine ⟨M, hM, hi, hd, hc, ?_⟩
    simp only [substWith, VE.Formula.denote] at h
    rcases h with h | h
    · left
      by_cases hh : higher D M N = true
      · simp only [hh, if_true] at h
        refine ⟨hh, (he M).mp h.1, fun hol => ?_⟩
        simpa [hol, circ, subst, substWith, VE.Formula.denote, RawOutweighs] using h.2
      · simp [hh, substWith, VE.Formula.denote] at h
    · right
      by_cases hh : D.soft.outranking = .holistic ∧ higher D N M = true
      · simp only [hh, and_self, if_true] at h
        exact ⟨hh.1, hh.2, h.1, h.2⟩
      · simp [hh, substWith, VE.Formula.denote] at h
  · rintro ⟨M, hM, hi, hd, hc, h⟩
    refine ⟨_, ⟨_, ⟨M, ⟨hM, ⟨hi, hd⟩, hc⟩, rfl⟩, rfl⟩, ?_⟩
    simp only [substWith, VE.Formula.denote]
    rcases h with ⟨hh, he', ho⟩ | ⟨hol, hh, hel, ho⟩
    · left
      simp only [hh, if_true]
      refine ⟨(he M).mpr he', ?_⟩
      by_cases hol : D.soft.outranking = .holistic
      · simp only [hol, if_true]; exact ho hol
      · simp [hol, substWith, VE.Formula.denote]
    · right
      simp only [hol, hh, and_self, if_true]
      exact ⟨hel, ho⟩

theorem raw_eff_denote (D : SoftDoc) (B : VE.Structure.{u}) (ρ : VE.Valuation B) :
    ∀ (g : Nat) (N : SoftNode), (circ D (effF D g N)).denote B ρ ↔ RawEff D B ρ g N
  | 0, _ => Iff.rfl
  | g + 1, N => by
    change (RawEligible D B ρ N ∧ ¬ (circ D (domWith D (effF D g) N)).denote B ρ) ↔
      (RawEligible D B ρ N ∧ ¬ RawDom D B ρ (RawEff D B ρ g) N)
    exact and_congr Iff.rfl (not_congr (raw_dom_denote D B ρ _ _ (fun M => raw_eff_denote D B ρ g M) N))

theorem raw_dom_congr {D : SoftDoc} {B : VE.Structure.{u}} {ρ : VE.Valuation B}
    {eff eff' : SoftNode → Prop} (N : SoftNode)
    (h : ∀ M ∈ D.T.nodes, higher D M N = true → (eff M ↔ eff' M)) :
    RawDom D B ρ eff N ↔ RawDom D B ρ eff' N := by
  unfold RawDom
  constructor
  · rintro ⟨M, hM, hi, hd, hc, (⟨hh, he, ho⟩ | hB)⟩
    · exact ⟨M, hM, hi, hd, hc, Or.inl ⟨hh, (h M hM hh).mp he, ho⟩⟩
    · exact ⟨M, hM, hi, hd, hc, Or.inr hB⟩
  · rintro ⟨M, hM, hi, hd, hc, (⟨hh, he, ho⟩ | hB)⟩
    · exact ⟨M, hM, hi, hd, hc, Or.inl ⟨hh, (h M hM hh).mpr he, ho⟩⟩
    · exact ⟨M, hM, hi, hd, hc, Or.inr hB⟩

theorem raw_eff_stable {D : SoftDoc} {B : VE.Structure.{u}} {ρ : VE.Valuation B}
    (hv : RanksValid D.soft) : ∀ (k : Nat) (N : SoftNode), N ∈ D.T.nodes → rankHeight D N < k →
      ∀ a b, rankHeight D N < a → rankHeight D N < b →
        (RawEff D B ρ a N ↔ RawEff D B ρ b N)
  | 0, _, _, hk => absurd hk (Nat.not_lt_zero _)
  | k + 1, N, _, hk => by
    intro a b ha hb
    match a, b, ha, hb with
    | a + 1, b + 1, ha, hb =>
      simp only [RawEff]
      apply and_congr_right
      intro _
      apply not_congr
      apply raw_dom_congr
      intro M hM hh
      have hlt := rankHeight_lt_of_higher hv hh
      exact raw_eff_stable hv k M hM (by omega) a b (by omega) (by omega)

theorem raw_resolve_higher {D : SoftDoc} {B : VE.Structure.{u}} {ρ : VE.Valuation B}
    (hv : SoftValid D) {H L : SoftNode} (hH : H ∈ D.T.nodes) (hL : L ∈ D.T.nodes)
    (hHd : H.mode = .default) (hLd : L.mode = .default) (hi : Incompatible D H L = true)
    (hh : higher D H L = true) :
    ¬ (RawEff D B ρ (rankFuel D) H ∧ RawEff D B ρ (rankFuel D) L) := by
  rintro ⟨eH, eL⟩
  have hcHL : Comparable D H L = true := by simp [Comparable, hh]
  have hcLH : Comparable D L H = true := by simp [Comparable, hh]
  have hiLH : Incompatible D L H = true := by rw [incompatible_symm]; exact hi
  have hlt := rankHeight_lt_of_higher hv.ranks hh
  have hLf := rankHeight_lt_fuel D L
  have eHn : RawEff D B ρ D.soft.ranks.length H :=
    (raw_eff_stable hv.ranks (rankHeight D H + 1) H hH (by omega) _ _
      (by unfold rankFuel at hLf; omega) (rankHeight_lt_fuel D H)).mpr eH
  unfold rankFuel at eH eL
  simp only [RawEff] at eH eL
  by_cases ho : D.soft.outranking = .holistic ∧ RawOutweighs D B ρ (act D L) (rk L) (rk H)
  · apply eH.2
    refine ⟨L, hL, hiLH, hLd, hcLH, Or.inr ⟨ho.1, hh, eL.1, ?_⟩⟩
    rw [act_eq hv hi]
    exact ho.2
  · apply eL.2
    exact ⟨H, hH, hi, hHd, hcHL, Or.inl ⟨hh, eHn, fun hol hw => ho ⟨hol, hw⟩⟩⟩

theorem raw_selects_eff (D : SoftDoc) (B : VE.Structure.{u}) (ρ : VE.Valuation B)
    (N : SoftNode) (hd : N.mode = .default)
    (hs : (circ D (selects' D N)).denote B ρ) : RawEff D B ρ (rankFuel D) N := by
  have ha : (circ D (VE.Norms.applies (primeNode D N))).denote B ρ := hs.1
  simp [VE.Norms.applies, primeNode, derivedList, hd, circ, subst] at ha
  simp only [substWith, substWith_anyF, VE.Formula.denote, anyF_denote,
    List.mem_map, List.mem_append, List.mem_singleton] at ha
  have hnom (F : VE.Formula) (hF : F ∈ N.carveOuts ∨ F = derived D N) :
      ¬ (circ D F).denote B ρ := by
    intro hf
    exact ha.2 ⟨_, ⟨F, hF, rfl⟩, hf⟩
  have hg : (circ D N.guard).denote B ρ := ha.1
  have hc : ¬ (circ D (anyF N.carveOuts)).denote B ρ := by
    simp only [circ, subst, substWith_anyF, anyF_denote, List.mem_map]
    rintro ⟨_, ⟨F, hF, rfl⟩, hf⟩
    exact hnom F (Or.inl hF) hf
  have hderived := hnom (derived D N) (Or.inr rfl)
  simp only [derived, hd, circ, subst, substWith, VE.Formula.denote] at hderived
  change ¬ ((((circ D (exceptedF D N)).denote B ρ ∨ (circ D (switchF D N)).denote B ρ) ∨
    (circ D (blockedF D N)).denote B ρ) ∨
    (circ D (dominatedF D D.soft.ranks.length N)).denote B ρ) at hderived
  have hx : ¬ (circ D (exceptedF D N)).denote B ρ :=
    fun x => hderived (Or.inl (Or.inl (Or.inl x)))
  have hsw : ¬ (circ D (switchF D N)).denote B ρ :=
    fun x => hderived (Or.inl (Or.inl (Or.inr x)))
  have hblk : ¬ (circ D (blockedF D N)).denote B ρ :=
    fun x => hderived (Or.inl (Or.inr x))
  have hdom : ¬ (circ D (dominatedF D D.soft.ranks.length N)).denote B ρ :=
    fun x => hderived (Or.inr x)
  have he : RawEligible D B ρ N := by
    simp only [RawEligible, eligibleF, hd, liveF, liveStrictIn, circ, subst]
    simp only [if_true, substWith, VE.Formula.denote]
    exact ⟨⟨⟨⟨hg, hc⟩, hsw⟩, hx⟩, hblk⟩
  change RawEligible D B ρ N ∧ ¬ RawDom D B ρ (RawEff D B ρ D.soft.ranks.length) N
  refine ⟨he, ?_⟩
  intro h
  apply hdom
  exact (raw_dom_denote D B ρ (effF D D.soft.ranks.length)
    (RawEff D B ρ D.soft.ranks.length) (fun M => raw_eff_denote D B ρ _ M) N).mpr h

theorem coh_rank_valid_unconditional (D : SoftDoc) (h : WellFormedSoft D = true) (M N : SoftNode)
    (hc : (M, N) ∈ collidingPairs D) (hcmp : Comparable D M N = true)
    (B : VE.Structure.{u}) : (cohPremise D M N).denote B [] := by
  have hv := softValid_of_wellFormed D h
  obtain ⟨hM, hN, hMd, hNd, _, hi⟩ := mem_collidingPairs.mp hc
  rw [cohPremise, bindAll_denote_nil]
  intro vs _
  simp only [VE.Formula.denote]
  intro hs
  have eM := raw_selects_eff D B (tupleVal vs) M hMd hs.1
  have eN := raw_selects_eff D B (tupleVal vs) N hNd hs.2
  unfold Comparable at hcmp
  rcases Bool.or_eq_true_iff.mp hcmp with hh | hh
  · exact raw_resolve_higher hv hM hN hMd hNd hi hh ⟨eM, eN⟩
  · exact raw_resolve_higher hv hN hM hNd hMd (by rw [incompatible_symm]; exact hi) hh ⟨eN, eM⟩

end VE.SoftNorms
