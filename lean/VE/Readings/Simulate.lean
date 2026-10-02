import VE.Readings.Choice

/-! A simulation of soft documents (docs/spec/composition-s2.md 1.4, 8.4: the proof of `superpose_faithful`).

`X` is the larger document (the superposed one), `Y` the smaller (a reading's), `f` maps every node of `Y` to a
node of `X`, and `S` and `S'` are structures on one carrier. When the soft blocks and the regulated predicates
agree, liveness agrees on the images, a node of `X` outside the image is never live, and every child of an image
that lies outside the image has its children among the children of an image sibling, then every regulated
predicate has the same value (`value_sim`). The last condition is what uniform precedence gives: an unchosen copy
of an interface rule yields only where the chosen copy does. The fuel of `Y`'s recursions is bounded by a rank
that decreases along `children` (`yields_stable`). -/
namespace VE.Readings
open VE.Norms (Regulated tupleVal)
open VE.SoftNorms (SoftNode SoftDoc children LiveD StrictYieldsD StrictSelectsD StrictDecidesD BlockedD EligibleD
  OutweighsD DomWithD EffD AppliesSoftD YieldsSoftD SelectsSoftD DecidesSoftD ValueSoft rulesOn fuel rankFuel
  Incompatible Comparable higher act rk dualPerm dualOblig mem_rulesOn)
universe u

/-! ## Fuel -/

section Stable
variable (D : SoftDoc) (S : VE.Structure.{u}) (ρ : VE.Valuation S)

theorem strictYields_mono : ∀ (k : Nat) (N : SoftNode), StrictYieldsD D S ρ k N → StrictYieldsD D S ρ (k + 1) N
  | 0, _, h => Or.inl h
  | k + 1, _, h => h.elim Or.inl (fun ⟨C, hC, hy⟩ => Or.inr ⟨C, hC, strictYields_mono k C hy⟩)

theorem yields_mono : ∀ (k : Nat) (N : SoftNode), YieldsSoftD D S ρ k N → YieldsSoftD D S ρ (k + 1) N
  | 0, _, h => Or.inl h
  | k + 1, _, h => h.elim Or.inl (fun ⟨C, hC, hy⟩ => Or.inr ⟨C, hC, yields_mono k C hy⟩)

theorem strictYields_mono_le {k k' : Nat} (hk : k ≤ k') (N : SoftNode) (h : StrictYieldsD D S ρ k N) :
    StrictYieldsD D S ρ k' N := by
  induction hk with
  | refl => exact h
  | step _ ih => exact strictYields_mono D S ρ _ N ih

theorem yields_mono_le {k k' : Nat} (hk : k ≤ k') (N : SoftNode) (h : YieldsSoftD D S ρ k N) :
    YieldsSoftD D S ρ k' N := by
  induction hk with
  | refl => exact h
  | step _ ih => exact yields_mono D S ρ _ N ih

/-- Along a rank that decreases from a node to its children, fuel past the rank changes nothing. -/
theorem strictYields_stable (r : SoftNode → Nat) (hr : ∀ N C, C ∈ children D N → r C < r N) :
    ∀ (k : Nat) (N : SoftNode), r N ≤ k → (StrictYieldsD D S ρ (k + 1) N ↔ StrictYieldsD D S ρ k N)
  | 0, N, _ => by
    constructor
    · rintro (h | ⟨C, hC, _⟩)
      · exact h
      · have := hr N C hC; omega
    · exact strictYields_mono D S ρ 0 N
  | k + 1, N, hN => by
    constructor
    · rintro (h | ⟨C, hC, hy⟩)
      · exact Or.inl h
      · exact Or.inr ⟨C, hC, (strictYields_stable r hr k C (by have := hr N C hC; omega)).mp hy⟩
    · exact strictYields_mono D S ρ (k + 1) N

theorem yields_stable (r : SoftNode → Nat) (hr : ∀ N C, C ∈ children D N → r C < r N) :
    ∀ (k : Nat) (N : SoftNode), r N ≤ k → (YieldsSoftD D S ρ (k + 1) N ↔ YieldsSoftD D S ρ k N)
  | 0, N, _ => by
    constructor
    · rintro (h | ⟨C, hC, _⟩)
      · exact h
      · have := hr N C hC; omega
    · exact yields_mono D S ρ 0 N
  | k + 1, N, hN => by
    constructor
    · rintro (h | ⟨C, hC, hy⟩)
      · exact Or.inl h
      · exact Or.inr ⟨C, hC, (yields_stable r hr k C (by have := hr N C hC; omega)).mp hy⟩
    · exact yields_mono D S ρ (k + 1) N

theorem strictYields_stable_le (r : SoftNode → Nat) (hr : ∀ N C, C ∈ children D N → r C < r N)
    {k k' : Nat} (N : SoftNode) (hk : r N ≤ k) (hk' : k ≤ k') :
    StrictYieldsD D S ρ k' N ↔ StrictYieldsD D S ρ k N := by
  induction hk' with
  | refl => exact Iff.rfl
  | step hle ih => exact (strictYields_stable D S ρ r hr _ N (Nat.le_trans hk hle)).trans ih

theorem yields_stable_le (r : SoftNode → Nat) (hr : ∀ N C, C ∈ children D N → r C < r N)
    {k k' : Nat} (N : SoftNode) (hk : r N ≤ k) (hk' : k ≤ k') :
    YieldsSoftD D S ρ k' N ↔ YieldsSoftD D S ρ k N := by
  induction hk' with
  | refl => exact Iff.rfl
  | step hle ih => exact (yields_stable D S ρ r hr _ N (Nat.le_trans hk hle)).trans ih

end Stable

/-! ## The simulation -/

theorem children_mem {D : SoftDoc} {N C : SoftNode} (h : C ∈ children D N) : C ∈ D.T.nodes :=
  (VE.SoftNorms.mem_childrenIn_iff.mp h).1

/-- The conditions of the simulation (see the module note). -/
structure Sim (X Y : SoftDoc) (f : SoftNode → SoftNode) (S : VE.Structure.{u}) (R' : String → List S.Carrier → Prop)
    (ρ : VE.Valuation S) : Prop where
  soft : X.soft = Y.soft
  regs : X.T.regulated = Y.T.regulated
  mem : ∀ N ∈ Y.T.nodes, f N ∈ X.T.nodes
  inj : ∀ N ∈ Y.T.nodes, ∀ N' ∈ Y.T.nodes, f N = f N' → N = N'
  pred : ∀ N ∈ Y.T.nodes, (f N).pred = N.pred
  sign : ∀ N ∈ Y.T.nodes, (f N).sign = N.sign
  mode : ∀ N ∈ Y.T.nodes, (f N).mode = N.mode
  rank : ∀ N ∈ Y.T.nodes, (f N).rank = N.rank
  live : ∀ N ∈ Y.T.nodes, LiveD X S ρ (f N) ↔ LiveD Y { S with relation := R' } ρ N
  dead : ∀ M ∈ X.T.nodes, (∀ N ∈ Y.T.nodes, f N ≠ M) → ¬ LiveD X S ρ M
  childFwd : ∀ N ∈ Y.T.nodes, ∀ C ∈ children Y N, f C ∈ children X (f N)
  childBack : ∀ N ∈ Y.T.nodes, ∀ C ∈ Y.T.nodes, f C ∈ children X (f N) → C ∈ children Y N
  sibling : ∀ N ∈ Y.T.nodes, ∀ C ∈ children X (f N), (∀ N' ∈ Y.T.nodes, f N' ≠ C) →
    ∃ N'' ∈ children Y N, ∀ G ∈ children X C, G ∈ children X (f N'')
  outweighs : ∀ M ∈ Y.T.nodes, ∀ N ∈ Y.T.nodes, Incompatible Y M N = true → M.mode = .default →
    N.mode = .default → Comparable Y M N = true →
    (OutweighsD X S ρ (act Y N) (rk N) (rk M) ↔ OutweighsD Y { S with relation := R' } ρ (act Y N) (rk N) (rk M)) ∧
    (OutweighsD X S ρ (act Y N) (rk M) (rk N) ↔ OutweighsD Y { S with relation := R' } ρ (act Y N) (rk M) (rk N))
  /-- A rank on `Y` decreasing along children, bounded by `Y`'s fuel. -/
  ranked : ∃ r : SoftNode → Nat, (∀ N C, C ∈ children Y N → r C < r N) ∧ ∀ N ∈ Y.T.nodes, r N ≤ fuel Y
  fuelLe : fuel Y ≤ fuel X

section Sim
variable {X Y : SoftDoc} {f : SoftNode → SoftNode} {S : VE.Structure.{u}} {R' : String → List S.Carrier → Prop}
  {ρ : VE.Valuation S} (hs : Sim X Y f S R' ρ)
include hs

theorem sim_strictYields : ∀ (k : Nat) (N : SoftNode), N ∈ Y.T.nodes →
    (StrictYieldsD X S ρ k (f N) ↔ StrictYieldsD Y { S with relation := R' } ρ k N)
  | 0, N, hN => by
    show ((f N).mode = .strict ∧ _) ↔ (N.mode = .strict ∧ _)
    rw [hs.mode N hN, hs.live N hN]
  | k + 1, N, hN => by
    show (((f N).mode = .strict ∧ _) ∨ _) ↔ ((N.mode = .strict ∧ _) ∨ _)
    rw [hs.mode N hN, hs.live N hN]
    apply or_congr_right
    constructor
    · rintro ⟨C, hC, hy⟩
      by_cases him : ∃ C' ∈ Y.T.nodes, f C' = C
      · obtain ⟨C', hC', rfl⟩ := him
        exact ⟨C', hs.childBack N hN C' hC' hC, (sim_strictYields k C' hC').mp hy⟩
      · have hext : ∀ N' ∈ Y.T.nodes, f N' ≠ C := fun N' hN' he => him ⟨N', hN', he⟩
        obtain ⟨N'', hN'', hsub⟩ := hs.sibling N hN C hC hext
        have hN''m := children_mem hN''
        refine ⟨N'', hN'', (sim_strictYields k N'' hN''m).mp ?_⟩
        cases k with
        | zero => exact absurd hy.2 (hs.dead C (children_mem hC) hext)
        | succ j =>
          rcases hy with hy | ⟨G, hG, hy⟩
          · exact absurd hy.2 (hs.dead C (children_mem hC) hext)
          · exact Or.inr ⟨G, hsub G hG, hy⟩
    · rintro ⟨C', hC', hy⟩
      exact ⟨f C', hs.childFwd N hN C' hC', (sim_strictYields k C' (children_mem hC')).mpr hy⟩

theorem sim_strictSelects (k : Nat) (N : SoftNode) (hN : N ∈ Y.T.nodes) :
    StrictSelectsD X S ρ k (f N) ↔ StrictSelectsD Y { S with relation := R' } ρ k N := by
  show ((f N).mode = .strict ∧ _ ∧ _) ↔ (N.mode = .strict ∧ _ ∧ _)
  rw [hs.mode N hN, hs.live N hN]
  apply and_congr_right; intro _; apply and_congr_right; intro _
  apply not_congr
  constructor
  · rintro ⟨C, hC, hy⟩
    by_cases him : ∃ C' ∈ Y.T.nodes, f C' = C
    · obtain ⟨C', hC', rfl⟩ := him
      exact ⟨C', hs.childBack N hN C' hC' hC, (sim_strictYields hs k C' hC').mp hy⟩
    · have hext : ∀ N' ∈ Y.T.nodes, f N' ≠ C := fun N' hN' he => him ⟨N', hN', he⟩
      obtain ⟨N'', hN'', hsub⟩ := hs.sibling N hN C hC hext
      refine ⟨N'', hN'', (sim_strictYields hs k N'' (children_mem hN'')).mp ?_⟩
      cases k with
      | zero => exact absurd hy.2 (hs.dead C (children_mem hC) hext)
      | succ j =>
        rcases hy with hy | ⟨G, hG, hy⟩
        · exact absurd hy.2 (hs.dead C (children_mem hC) hext)
        · exact Or.inr ⟨G, hsub G hG, hy⟩
  · rintro ⟨C', hC', hy⟩
    exact ⟨f C', hs.childFwd N hN C' hC', (sim_strictYields hs k C' (children_mem hC')).mpr hy⟩

theorem sim_dualPerm : dualPerm X = dualPerm Y := by
  funext r
  simp only [dualPerm, VE.SoftNorms.SoftDoc.base, VE.Norms.pairs, hs.regs]

theorem sim_dualOblig : dualOblig X = dualOblig Y := by
  funext r
  simp only [dualOblig, VE.SoftNorms.SoftDoc.base, VE.Norms.pairs, hs.regs]

theorem sim_act (N : SoftNode) (hN : N ∈ Y.T.nodes) : act X (f N) = act Y N := by
  simp only [act, VE.SoftNorms.actKey, hs.pred N hN, sim_dualPerm hs]

theorem sim_rk (N : SoftNode) (hN : N ∈ Y.T.nodes) : rk (f N) = rk N := by
  simp only [rk, hs.rank N hN]

theorem sim_higher (M N : SoftNode) (hM : M ∈ Y.T.nodes) (hN : N ∈ Y.T.nodes) :
    higher X (f M) (f N) = higher Y M N := by
  simp only [higher, hs.rank M hM, hs.rank N hN, hs.soft]

theorem sim_comparable (M N : SoftNode) (hM : M ∈ Y.T.nodes) (hN : N ∈ Y.T.nodes) :
    Comparable X (f M) (f N) = Comparable Y M N := by
  simp only [Comparable, sim_higher hs M N hM hN, sim_higher hs N M hN hM]

theorem sim_incompatible (M N : SoftNode) (hM : M ∈ Y.T.nodes) (hN : N ∈ Y.T.nodes) :
    Incompatible X (f M) (f N) = Incompatible Y M N := by
  simp only [Incompatible, hs.pred M hM, hs.pred N hN, hs.sign M hM, hs.sign N hN, sim_dualPerm hs]

theorem sim_rankFuel : rankFuel X = rankFuel Y := by
  simp only [rankFuel, hs.soft]

/-- Strict selection at `X`'s fuel is strict selection at `Y`'s. -/
theorem sim_strictSelects_fuel (N : SoftNode) (hN : N ∈ Y.T.nodes) :
    StrictSelectsD X S ρ (fuel X) (f N) ↔ StrictSelectsD Y { S with relation := R' } ρ (fuel Y) N := by
  rw [sim_strictSelects hs _ N hN]
  obtain ⟨r, hr, hb⟩ := hs.ranked
  show (_ ∧ _ ∧ ¬ _) ↔ (_ ∧ _ ∧ ¬ _)
  apply and_congr_right; intro _; apply and_congr_right; intro _
  apply not_congr
  exact exists_congr fun C => and_congr_right fun hC =>
    strictYields_stable_le Y { S with relation := R' } ρ r hr C (hb C (children_mem hC)) hs.fuelLe

theorem sim_strictDecides (p : String) (sign : Bool) :
    StrictDecidesD X S ρ p sign ↔ StrictDecidesD Y { S with relation := R' } ρ p sign := by
  constructor
  · rintro ⟨M, hM, hsg, hsel⟩
    have hMX := (mem_rulesOn.mp hM).1
    by_cases him : ∃ N ∈ Y.T.nodes, f N = M
    · obtain ⟨N, hN, rfl⟩ := him
      refine ⟨N, mem_rulesOn.mpr ⟨hN, ?_⟩, by rw [← hs.sign N hN]; exact hsg, (sim_strictSelects_fuel hs N hN).mp hsel⟩
      rw [← hs.pred N hN]; exact (mem_rulesOn.mp hM).2
    · exact absurd hsel.2.1 (hs.dead M hMX (fun N hN he => him ⟨N, hN, he⟩))
  · rintro ⟨N, hN, hsg, hsel⟩
    have hNY := (mem_rulesOn.mp hN).1
    refine ⟨f N, mem_rulesOn.mpr ⟨hs.mem N hNY, ?_⟩, by rw [hs.sign N hNY]; exact hsg,
      (sim_strictSelects_fuel hs N hNY).mpr hsel⟩
    rw [hs.pred N hNY]; exact (mem_rulesOn.mp hN).2

theorem sim_blocked (N : SoftNode) (hN : N ∈ Y.T.nodes) :
    BlockedD X S ρ (f N) ↔ BlockedD Y { S with relation := R' } ρ N := by
  simp only [BlockedD, hs.pred N hN, hs.sign N hN, sim_dualPerm hs, sim_dualOblig hs, sim_strictDecides hs]

theorem sim_eligible (N : SoftNode) (hN : N ∈ Y.T.nodes) :
    EligibleD X S ρ (f N) ↔ EligibleD Y { S with relation := R' } ρ N := by
  simp only [EligibleD, hs.mode N hN, hs.live N hN, sim_blocked hs N hN]

theorem sim_eligible_extra (M : SoftNode) (hM : M ∈ X.T.nodes) (hext : ∀ N ∈ Y.T.nodes, f N ≠ M) :
    ¬ EligibleD X S ρ M := fun h => hs.dead M hM hext h.2.1

omit hs in
theorem effD_eligible {D : SoftDoc} {T : VE.Structure.{u}} {σ : VE.Valuation T} :
    ∀ {g : Nat} {N : SoftNode}, EffD D T σ g N → EligibleD D T σ N
  | 0, _, h => h
  | _ + 1, _, h => h.1

theorem sim_domWith (effX : SoftNode → Prop) (effY : SoftNode → Prop)
    (hX : ∀ M, effX M → EligibleD X S ρ M) (he : ∀ M ∈ Y.T.nodes, effX (f M) ↔ effY M)
    (N : SoftNode) (hN : N ∈ Y.T.nodes) (hNd : N.mode = .default) :
    DomWithD X S ρ effX (f N) ↔ DomWithD Y { S with relation := R' } ρ effY N := by
  constructor
  · rintro ⟨M, hM, hinc, hmd, hcmp, hb⟩
    by_cases him : ∃ M' ∈ Y.T.nodes, f M' = M
    · obtain ⟨M', hM', rfl⟩ := him
      rw [sim_incompatible hs M' N hM' hN] at hinc
      rw [sim_comparable hs M' N hM' hN] at hcmp
      rw [hs.mode M' hM'] at hmd
      have ho := hs.outweighs M' hM' N hN hinc hmd hNd hcmp
      refine ⟨M', hM', hinc, hmd, hcmp, ?_⟩
      rw [sim_higher hs M' N hM' hN, sim_higher hs N M' hN hM', sim_act hs N hN, sim_rk hs N hN,
        sim_rk hs M' hM', hs.soft] at hb
      rcases hb with ⟨h1, h2, h3⟩ | ⟨h1, h2, h3, h4⟩
      · exact Or.inl ⟨h1, (he M' hM').mp h2, fun hh => fun ho' => h3 hh (ho.1.mpr ho')⟩
      · exact Or.inr ⟨h1, h2, (sim_eligible hs M' hM').mp h3, ho.2.mp h4⟩
    · exfalso
      have hext : ∀ N' ∈ Y.T.nodes, f N' ≠ M := fun N' hN' e => him ⟨N', hN', e⟩
      rcases hb with ⟨_, h2, _⟩ | ⟨_, _, h3, _⟩
      · exact sim_eligible_extra hs M hM hext (hX M h2)
      · exact sim_eligible_extra hs M hM hext h3
  · rintro ⟨M', hM', hinc, hmd, hcmp, hb⟩
    have ho := hs.outweighs M' hM' N hN hinc hmd hNd hcmp
    refine ⟨f M', hs.mem M' hM', by rw [sim_incompatible hs M' N hM' hN]; exact hinc,
      by rw [hs.mode M' hM']; exact hmd, by rw [sim_comparable hs M' N hM' hN]; exact hcmp, ?_⟩
    rw [sim_higher hs M' N hM' hN, sim_higher hs N M' hN hM', sim_act hs N hN, sim_rk hs N hN,
      sim_rk hs M' hM', hs.soft]
    rcases hb with ⟨h1, h2, h3⟩ | ⟨h1, h2, h3, h4⟩
    · exact Or.inl ⟨h1, (he M' hM').mpr h2, fun hh => fun ho' => h3 hh (ho.1.mp ho')⟩
    · exact Or.inr ⟨h1, h2, (sim_eligible hs M' hM').mpr h3, ho.2.mpr h4⟩

theorem sim_eff : ∀ (g : Nat) (N : SoftNode), N ∈ Y.T.nodes →
    (EffD X S ρ g (f N) ↔ EffD Y { S with relation := R' } ρ g N)
  | 0, N, hN => sim_eligible hs N hN
  | g + 1, N, hN => by
    simp only [EffD]
    rw [sim_eligible hs N hN]
    constructor
    · rintro ⟨he, hd⟩
      exact ⟨he, fun h => hd ((sim_domWith hs _ _ (fun M h => effD_eligible h)
        (fun M hM => sim_eff g M hM) N hN he.1).mpr h)⟩
    · rintro ⟨he, hd⟩
      exact ⟨he, fun h => hd ((sim_domWith hs _ _ (fun M h => effD_eligible h)
        (fun M hM => sim_eff g M hM) N hN he.1).mp h)⟩

theorem sim_applies (N : SoftNode) (hN : N ∈ Y.T.nodes) :
    AppliesSoftD X S ρ (f N) ↔ AppliesSoftD Y { S with relation := R' } ρ N := by
  unfold AppliesSoftD
  rw [hs.mode N hN]
  cases N.mode with
  | strict => exact hs.live N hN
  | default => rw [sim_rankFuel hs]; exact sim_eff hs _ N hN

theorem sim_applies_extra (M : SoftNode) (hM : M ∈ X.T.nodes) (hext : ∀ N ∈ Y.T.nodes, f N ≠ M) :
    ¬ AppliesSoftD X S ρ M := by
  unfold AppliesSoftD
  cases M.mode with
  | strict => exact hs.dead M hM hext
  | default => exact fun h => sim_eligible_extra hs M hM hext (effD_eligible h)

theorem sim_yields : ∀ (k : Nat) (N : SoftNode), N ∈ Y.T.nodes →
    (YieldsSoftD X S ρ k (f N) ↔ YieldsSoftD Y { S with relation := R' } ρ k N)
  | 0, N, hN => sim_applies hs N hN
  | k + 1, N, hN => by
    simp only [YieldsSoftD]
    rw [sim_applies hs N hN]
    apply or_congr_right
    constructor
    · rintro ⟨C, hC, hy⟩
      by_cases him : ∃ C' ∈ Y.T.nodes, f C' = C
      · obtain ⟨C', hC', rfl⟩ := him
        exact ⟨C', hs.childBack N hN C' hC' hC, (sim_yields k C' hC').mp hy⟩
      · have hext : ∀ N' ∈ Y.T.nodes, f N' ≠ C := fun N' hN' he => him ⟨N', hN', he⟩
        obtain ⟨N'', hN'', hsub⟩ := hs.sibling N hN C hC hext
        refine ⟨N'', hN'', (sim_yields k N'' (children_mem hN'')).mp ?_⟩
        cases k with
        | zero => exact absurd hy (sim_applies_extra hs C (children_mem hC) hext)
        | succ j =>
          rcases hy with hy | ⟨G, hG, hy⟩
          · exact absurd hy (sim_applies_extra hs C (children_mem hC) hext)
          · exact Or.inr ⟨G, hsub G hG, hy⟩
    · rintro ⟨C', hC', hy⟩
      exact ⟨f C', hs.childFwd N hN C' hC', (sim_yields k C' (children_mem hC')).mpr hy⟩

theorem sim_selects_fuel (N : SoftNode) (hN : N ∈ Y.T.nodes) :
    SelectsSoftD X S ρ (fuel X) (f N) ↔ SelectsSoftD Y { S with relation := R' } ρ (fuel Y) N := by
  obtain ⟨r, hr, hb⟩ := hs.ranked
  unfold SelectsSoftD
  rw [sim_applies hs N hN]
  apply and_congr_right; intro _
  apply not_congr
  constructor
  · rintro ⟨C, hC, hy⟩
    by_cases him : ∃ C' ∈ Y.T.nodes, f C' = C
    · obtain ⟨C', hC', rfl⟩ := him
      have hC'' := hs.childBack N hN C' hC' hC
      exact ⟨C', hC'', (yields_stable_le Y { S with relation := R' } ρ r hr C' (hb C' hC') hs.fuelLe).mp
        ((sim_yields hs _ C' hC').mp hy)⟩
    · have hext : ∀ N' ∈ Y.T.nodes, f N' ≠ C := fun N' hN' he => him ⟨N', hN', he⟩
      obtain ⟨N'', hN'', hsub⟩ := hs.sibling N hN C hC hext
      have hN''m := children_mem hN''
      refine ⟨N'', hN'', (yields_stable_le Y { S with relation := R' } ρ r hr N'' (hb N'' hN''m) hs.fuelLe).mp
        ((sim_yields hs _ N'' hN''m).mp ?_)⟩
      cases hk : fuel X with
      | zero => rw [hk] at hy; exact absurd hy (sim_applies_extra hs C (children_mem hC) hext)
      | succ j =>
        rw [hk] at hy
        rcases hy with hy | ⟨G, hG, hy⟩
        · exact absurd hy (sim_applies_extra hs C (children_mem hC) hext)
        · exact Or.inr ⟨G, hsub G hG, hy⟩
  · rintro ⟨C', hC', hy⟩
    have hC'm := children_mem hC'
    exact ⟨f C', hs.childFwd N hN C' hC', (sim_yields hs _ C' hC'm).mpr
      ((yields_stable_le Y { S with relation := R' } ρ r hr C' (hb C' hC'm) hs.fuelLe).mpr hy)⟩

theorem sim_decides (p : String) (sign : Bool) :
    DecidesSoftD X S ρ p sign ↔ DecidesSoftD Y { S with relation := R' } ρ p sign := by
  constructor
  · rintro ⟨M, hM, hsg, hsel⟩
    have hMX := (mem_rulesOn.mp hM).1
    by_cases him : ∃ N ∈ Y.T.nodes, f N = M
    · obtain ⟨N, hN, rfl⟩ := him
      refine ⟨N, mem_rulesOn.mpr ⟨hN, ?_⟩, by rw [← hs.sign N hN]; exact hsg, (sim_selects_fuel hs N hN).mp hsel⟩
      rw [← hs.pred N hN]; exact (mem_rulesOn.mp hM).2
    · exact absurd hsel.1 (sim_applies_extra hs M hMX (fun N hN he => him ⟨N, hN, he⟩))
  · rintro ⟨N, hN, hsg, hsel⟩
    have hNY := (mem_rulesOn.mp hN).1
    refine ⟨f N, mem_rulesOn.mpr ⟨hs.mem N hNY, ?_⟩, by rw [hs.sign N hNY]; exact hsg,
      (sim_selects_fuel hs N hNY).mpr hsel⟩
    rw [hs.pred N hNY]; exact (mem_rulesOn.mp hN).2

end Sim

/-- The simulation gives every regulated predicate the same value. The valuation is the tuple's own. -/
theorem value_sim {X Y : SoftDoc} {f : SoftNode → SoftNode} {S : VE.Structure.{u}}
    {R' : String → List S.Carrier → Prop} (r : Regulated) (vs : List S.Carrier)
    (hs : Sim X Y f S R' (tupleVal vs)) :
    ValueSoft X r S vs = ValueSoft Y r { S with relation := R' } vs := by
  unfold ValueSoft VE.Norms.catalaValue
  have h1 := sim_decides hs r.name true
  have h2 := sim_decides hs r.name false
  by_cases a : DecidesSoftD X S (tupleVal vs) r.name true <;>
    by_cases b : DecidesSoftD X S (tupleVal vs) r.name false <;> simp_all
end VE.Readings
