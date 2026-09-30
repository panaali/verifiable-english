import VE.Rights.Projections

/-! The bar of Art. 30 under the rule reading (docs/spec/rights.md 4.7, 9.2), scoped to
`correlate`'s own output.

Where `aimed_m` holds: no right-derived positive line on `m` selects (the bar node is a
child of each and yields there), the bar decides `¬m` strictly, and every default node of
`T″` on `m`, of either sign, or `require`ing on `m`'s dual, is blocked (soft-norms 4.2
step 2), right-derived or outside rights. `bar_value`: when every positive rule on `m`
is right-derived, `m` is false there. What these do not cover is the composition
assumption of 4.7: a *strict* positive rule on `m` outside rights, or a strict obligation
on the act, that selects where the bar selects is a W1 conflict point of `T″′` and is
reported by the unchanged conflict check. -/
namespace VE.Rights
open VE.Norms (tupleVal)
open VE.SoftNorms (SoftNode SelectsSoftD StrictDecidesD ValueSoft)
universe u

theorem bar_blocks (D : RightsDoc) (h : WellFormedRights D = true) (hb : ruleReading D = true)
    (m : String) (hm : rightPermission D m = true) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (ha : (aimedF D m).denote S ρ) :
    (∀ RN ∈ linesOf D, RN.2.node.pred = m → RN.2.node.sign = true → ¬ SelectsRN D S ρ RN.2) ∧
    StrictDecidesD (correlate D) S ρ m false ∧
    (∀ M ∈ (correlate D).T.nodes, M.mode = .default →
       (M.pred = m ∨ (M.sign = true ∧ VE.SoftNorms.dualPerm (correlate D) M.pred = some m)) →
       ¬ SelectsSoftD (correlate D) S ρ (VE.SoftNorms.fuel (correlate D)) M) := by
  have hv := rightsValid_of_wellFormed D h
  have hB := barNode_mem D hb hm
  have hsd : StrictDecidesD (correlate D) S ρ m false :=
    ⟨barNode D m, VE.SoftNorms.mem_rulesOn.mpr ⟨(mem_correlate_nodes D _).mpr (Or.inr hB), rfl⟩, rfl,
      (strictSelects_bar hv S ρ hB _).mpr ha⟩
  refine ⟨fun RN hRN hp hs hsel => ?_, hsd, fun M _ hd hM hsel => ?_⟩
  · apply hsel.2
    refine ⟨barNode D m, (mem_children_correlate D _ _).mpr (Or.inr ⟨hB, ?_, ?_⟩),
      (yields_bar hv S ρ hB _).mpr ha⟩
    · show m = RN.2.node.pred
      exact hp.symm
    · simp only [barNode, posLineNames, List.mem_map, List.mem_filter, Bool.and_eq_true, beq_iff_eq]
      exact ⟨nodeOf D RN.2, ⟨lineNode_mem D (R := RN.1) hRN, hp, hs⟩, rfl⟩
  · apply VE.SoftNorms.default_not_blocked hd hsel
    rcases hM with hp | ⟨hs, hdu⟩
    · exact Or.inr (Or.inl (by rw [hp]; exact hsd))
    · exact Or.inr (Or.inr (Or.inl ⟨hs, m, hdu, hsd⟩))

theorem bar_value (D : RightsDoc) (h : WellFormedRights D = true) (hb : ruleReading D = true)
    (m : String) (hm : rightPermission D m = true)
    (honly : ∀ M ∈ (correlate D).T.nodes, M.pred = m → M.sign = true → ∃ RN ∈ linesOf D, nodeOf D RN.2 = M)
    (S : VE.Structure.{u}) (vs : List S.Carrier) (ha : (aimedF D m).denote S (tupleVal vs)) :
    ValueSoft (correlate D) (regOf D m) S vs = some false := by
  have hsv := VE.SoftNorms.softValid_of_wellFormed _ (correlate_wellFormed D h)
  obtain ⟨hlines, hsd, _⟩ := bar_blocks D h hb m hm S (tupleVal vs) ha
  apply valueSoft_of_decides D m S vs false
  · obtain ⟨M, hM, hs, hsel⟩ := hsd
    exact ⟨M, hM, hs, (VE.SoftNorms.selects_strict hsv _ M (VE.SoftNorms.mem_rulesOn.mp hM).1 hsel.1).mpr hsel⟩
  · rintro ⟨M, hM, hs, hsel⟩
    obtain ⟨hMc, hp⟩ := VE.SoftNorms.mem_rulesOn.mp hM
    obtain ⟨RN, hRN, rfl⟩ := honly M hMc hp hs
    exact hlines RN hRN hp hs hsel

end VE.Rights
