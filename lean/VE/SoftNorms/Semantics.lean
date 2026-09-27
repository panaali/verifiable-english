import VE.SoftNorms.Soften

/-! The direct semantics `ValueSoft` (docs/spec/soft-norms.md 4.2, 9.1) and its
relation to the elaboration (9.2).

`LiveD`, `StrictYieldsD`, …, `DecidesSoftD` are propositions defined on the soft
tree itself, independently of `soften`: step 0 (in force), step 1 (strict rules
decide, W1's recursion over strict rules), step 2 (blocking), step 3 (dominance
by rank with fuel `g`: higher opponents must be effective at `g`, lower
overriding opponents need only be eligible) and step 4 (W1's recursion with
`applies′`). `DomWithD` is the dominance body with the opponents' effectiveness
as a parameter, so `EffD`/`DominatedD` are the spec's mutual pair.

Every generated formula denotes its counterpart (`live_denote`,
`strictDecides_denote`, `blocked_denote`, `eff_denote`, `derived_denote`), and
`soften_faithful` follows by unfolding: W1's `Value` on `T′` is `ValueSoft`. -/
namespace VE.SoftNorms
open VE.Norms
universe u

section Direct
variable (D : SoftDoc) (S : VE.Structure.{u}) (ρ : VE.Valuation S)

def LiveD (N : SoftNode) : Prop :=
  N.guard.denote S ρ ∧ ¬ (∃ U ∈ N.carveOuts, U.denote S ρ) ∧ ¬ (switchF D N).denote S ρ ∧
    (N.mode = .default → ¬ (exceptedF D N).denote S ρ)

def StrictYieldsD : Nat → SoftNode → Prop
  | 0, N => N.mode = .strict ∧ LiveD D S ρ N
  | f + 1, N => (N.mode = .strict ∧ LiveD D S ρ N) ∨ ∃ C ∈ children D N, StrictYieldsD f C

def StrictSelectsD (f : Nat) (N : SoftNode) : Prop :=
  N.mode = .strict ∧ LiveD D S ρ N ∧ ¬ ∃ C ∈ children D N, StrictYieldsD D S ρ f C

def StrictDecidesD (p : String) (sign : Bool) : Prop :=
  ∃ N ∈ rulesOn D p, N.sign = sign ∧ StrictSelectsD D S ρ (fuel D) N

def BlockedD (N : SoftNode) : Prop :=
  StrictDecidesD D S ρ N.pred true ∨ StrictDecidesD D S ρ N.pred false ∨
    (N.sign = true ∧ ∃ m, dualPerm D N.pred = some m ∧ StrictDecidesD D S ρ m false) ∨
    (N.sign = false ∧ ∃ r, dualOblig D N.pred = some r ∧ StrictDecidesD D S ρ r true)

def EligibleD (N : SoftNode) : Prop := N.mode = .default ∧ LiveD D S ρ N ∧ ¬ BlockedD D S ρ N

def OutweighsD (a L H : String) : Prop := (atom (outweighsName a L H) (actSortsOf D a)).denote S ρ

/-- `M` dominates `N` for some opponent `M`, given the opponents' effectiveness `eff`. -/
def DomWithD (eff : SoftNode → Prop) (N : SoftNode) : Prop :=
  ∃ M ∈ D.T.nodes, Incompatible D M N = true ∧ M.mode = .default ∧ Comparable D M N = true ∧
    ((higher D M N = true ∧ eff M ∧
        (D.soft.outranking = .holistic → ¬ OutweighsD D S ρ (act D N) (rk N) (rk M))) ∨
     (D.soft.outranking = .holistic ∧ higher D N M = true ∧ EligibleD D S ρ M ∧
        OutweighsD D S ρ (act D N) (rk M) (rk N)))

def EffD : Nat → SoftNode → Prop
  | 0, N => EligibleD D S ρ N
  | g + 1, N => EligibleD D S ρ N ∧ ¬ DomWithD D S ρ (EffD g) N

def DominatedD (g : Nat) (N : SoftNode) : Prop := DomWithD D S ρ (EffD D S ρ g) N

def AppliesSoftD (N : SoftNode) : Prop :=
  match N.mode with
  | .strict => LiveD D S ρ N
  | .default => EffD D S ρ (rankFuel D) N

def YieldsSoftD : Nat → SoftNode → Prop
  | 0, N => AppliesSoftD D S ρ N
  | f + 1, N => AppliesSoftD D S ρ N ∨ ∃ C ∈ children D N, YieldsSoftD f C

def SelectsSoftD (f : Nat) (N : SoftNode) : Prop :=
  AppliesSoftD D S ρ N ∧ ¬ ∃ C ∈ children D N, YieldsSoftD D S ρ f C

def DecidesSoftD (p : String) (sign : Bool) : Prop :=
  ∃ N ∈ rulesOn D p, N.sign = sign ∧ SelectsSoftD D S ρ (fuel D) N

def DefaultDecidesD (p : String) (sign : Bool) : Prop :=
  ∃ N ∈ rulesOn D p, N.mode = .default ∧ N.sign = sign ∧ SelectsSoftD D S ρ (fuel D) N

end Direct

noncomputable def ValueSoft (D : SoftDoc) (r : Regulated) (S : VE.Structure.{u}) (vs : List S.Carrier) :
    Option Bool :=
  catalaValue (DecidesSoftD D S (tupleVal vs) r.name true) (DecidesSoftD D S (tupleVal vs) r.name false)
    r.allowByDefault

def IntendedSoftAt (D : SoftDoc) (r : Regulated) (S : VE.Structure.{u}) : Prop :=
  ∀ vs, VE.TupleTyped S r.sorts vs →
    ∃ b, ValueSoft D r (forget [r.name] S) vs = some b ∧ (S.relation r.name vs ↔ b = true)

def holdsSoft (D : SoftDoc) (S : VE.Structure.{u}) : Prop := ∀ r ∈ D.T.regulated, IntendedSoftAt D r S

/-! ## Denotation of the generated formulas -/

section Denote
variable (D : SoftDoc) (S : VE.Structure.{u}) (ρ : VE.Valuation S)

theorem liveStrictIn_denote (regs : List Regulated) (N : SoftNode) :
    (liveStrictIn regs N).denote S ρ ↔
      N.guard.denote S ρ ∧ ¬ (∃ U ∈ N.carveOuts, U.denote S ρ) ∧ ¬ (switchIn regs N).denote S ρ := by
  simp only [liveStrictIn, VE.Formula.denote, anyF_denote, and_assoc]

theorem live_denote (N : SoftNode) : (liveF D N).denote S ρ ↔ LiveD D S ρ N := by
  unfold liveF LiveD
  rw [VE.Formula.denote, liveStrictIn_denote]
  simp only [switchF, and_assoc]
  cases N.mode <;> simp [VE.Formula.denote]

theorem coreNode_name (N : SoftNode) : (coreNode N).name = N.name := rfl
theorem coreNode_pred (N : SoftNode) : (coreNode N).pred = N.pred := rfl
theorem coreNode_over (N : SoftNode) : (coreNode N).over = N.over := rfl
theorem coreNode_sign (N : SoftNode) : (coreNode N).sign = N.sign := rfl
theorem coreNode_mode (N : SoftNode) : (coreNode N).mode = N.mode := rfl

theorem liveStrict_core (N : SoftNode) :
    ((if (coreNode N).mode = .strict then liveStrictIn D.T.regulated (coreNode N) else .bottom).denote S ρ) ↔
      N.mode = .strict ∧ LiveD D S ρ N := by
  simp only [coreNode_mode]
  by_cases hm : N.mode = .strict
  · simp only [hm, if_true, liveStrictIn_denote, LiveD, true_and]
    have hsw : switchIn D.T.regulated (coreNode N) = switchF D N := by
      simp [switchIn, switchF, coreNode, hm, offName]
    rw [hsw]
    simp [coreNode, hm]
  · simp [hm, VE.Formula.denote]

theorem mem_children_core (N C' : SoftNode) :
    C' ∈ childrenIn (D.T.nodes.map coreNode) (coreNode N) ↔ ∃ C ∈ children D N, C' = coreNode C :=
  mem_childrenIn_map coreNode coreNode_name coreNode_pred coreNode_over N C'

theorem strictYields_denote : ∀ (f : Nat) (N : SoftNode),
    (strictYieldsIn D.T.regulated (D.T.nodes.map coreNode) f (coreNode N)).denote S ρ ↔
      StrictYieldsD D S ρ f N
  | 0, N => by
    simp only [strictYieldsIn, VE.Formula.denote, anyF_denote, List.not_mem_nil, false_and,
      exists_false, or_false, StrictYieldsD]
    exact liveStrict_core D S ρ N
  | f + 1, N => by
    simp only [strictYieldsIn, VE.Formula.denote, anyF_denote, List.mem_map, StrictYieldsD]
    rw [liveStrict_core D S ρ N]
    apply or_congr_right
    constructor
    · rintro ⟨_, ⟨C', hC', rfl⟩, hy⟩
      obtain ⟨C, hC, rfl⟩ := (mem_children_core D N C').mp hC'
      exact ⟨C, hC, (strictYields_denote f C).mp hy⟩
    · rintro ⟨C, hC, hy⟩
      exact ⟨_, ⟨coreNode C, (mem_children_core D N _).mpr ⟨C, hC, rfl⟩, rfl⟩,
        (strictYields_denote f C).mpr hy⟩

theorem strictSelects_denote (f : Nat) (N : SoftNode) :
    (strictSelectsIn D.T.regulated (D.T.nodes.map coreNode) f (coreNode N)).denote S ρ ↔
      StrictSelectsD D S ρ f N := by
  have hchild : (∃ a ∈ (childrenIn (D.T.nodes.map coreNode) (coreNode N)).map
      (strictYieldsIn D.T.regulated (D.T.nodes.map coreNode) f), a.denote S ρ) ↔
      ∃ C ∈ children D N, StrictYieldsD D S ρ f C := by
    simp only [List.mem_map]
    constructor
    · rintro ⟨_, ⟨C', hC', rfl⟩, hy⟩
      obtain ⟨C, hC, rfl⟩ := (mem_children_core D N C').mp hC'
      exact ⟨C, hC, (strictYields_denote D S ρ f C).mp hy⟩
    · rintro ⟨C, hC, hy⟩
      exact ⟨_, ⟨coreNode C, (mem_children_core D N _).mpr ⟨C, hC, rfl⟩, rfl⟩,
        (strictYields_denote D S ρ f C).mpr hy⟩
  have hl := liveStrict_core D S ρ N
  unfold strictSelectsIn StrictSelectsD
  simp only [coreNode_mode] at hl ⊢
  by_cases hm : N.mode = .strict
  · simp only [hm, if_true] at hl ⊢
    rw [VE.Formula.denote, VE.Formula.denote, anyF_denote, hchild, hl]
    simp
  · simp [hm, VE.Formula.denote]

theorem strictDecides_denote (p : String) (sign : Bool) :
    (strictDecidesF D p sign).denote S ρ ↔ StrictDecidesD D S ρ p sign := by
  simp only [strictDecidesF, strictDecidesIn, anyF_denote, List.mem_map, List.mem_filter,
    List.length_map, StrictDecidesD, rulesOn, beq_iff_eq]
  constructor
  · rintro ⟨_, ⟨N', ⟨⟨hN', hp⟩, hs⟩, rfl⟩, h⟩
    obtain ⟨N, hN, rfl⟩ := hN'
    exact ⟨N, ⟨hN, hp⟩, hs, (strictSelects_denote D S ρ _ N).mp h⟩
  · rintro ⟨N, ⟨hN, hp⟩, hs, h⟩
    exact ⟨_, ⟨coreNode N, ⟨⟨⟨N, hN, rfl⟩, hp⟩, hs⟩, rfl⟩, (strictSelects_denote D S ρ _ N).mpr h⟩

theorem blocked_denote (N : SoftNode) : (blockedF D N).denote S ρ ↔ BlockedD D S ρ N := by
  unfold blockedF BlockedD strictPos strictNeg
  simp only [VE.Formula.denote, strictDecides_denote]
  cases hs : N.sign
  · cases hd : dualOblig D N.pred <;> simp [VE.Formula.denote, strictDecides_denote, or_assoc]
  · cases hd : dualPerm D N.pred <;> simp [VE.Formula.denote, strictDecides_denote, or_assoc]

theorem eligible_denote (N : SoftNode) : (eligibleF D N).denote S ρ ↔ EligibleD D S ρ N := by
  unfold eligibleF EligibleD
  cases hm : N.mode
  · simp [VE.Formula.denote]
  · simp [VE.Formula.denote, live_denote, blocked_denote]

theorem outweighs_denote (a L H : String) : (outweighsF D a L H).denote S ρ ↔ OutweighsD D S ρ a L H :=
  Iff.rfl

theorem domWith_denote (eff : SoftNode → VE.Formula) (effP : SoftNode → Prop)
    (he : ∀ M, (eff M).denote S ρ ↔ effP M) (N : SoftNode) :
    (domWith D eff N).denote S ρ ↔ DomWithD D S ρ effP N := by
  simp only [domWith, anyF_denote, List.mem_map, opponents, List.mem_filter, Bool.and_eq_true,
    beq_iff_eq, DomWithD]
  constructor
  · rintro ⟨_, ⟨M, ⟨hM, ⟨hi, hd⟩, hc⟩, rfl⟩, h⟩
    refine ⟨M, hM, hi, hd, hc, ?_⟩
    simp only [VE.Formula.denote] at h
    rcases h with h | h
    · left
      by_cases hh : higher D M N = true
      · simp only [hh, if_true, VE.Formula.denote] at h
        refine ⟨hh, (he M).mp h.1, fun hol => ?_⟩
        simpa [hol, VE.Formula.denote, outweighs_denote] using h.2
      · simp [hh, VE.Formula.denote] at h
    · right
      by_cases hh : D.soft.outranking = .holistic ∧ higher D N M = true
      · simp only [hh, and_self, if_true, VE.Formula.denote, eligible_denote] at h
        exact ⟨hh.1, hh.2, h.1, h.2⟩
      · simp only [hh, if_false, VE.Formula.denote] at h
  · rintro ⟨M, hM, hi, hd, hc, h⟩
    refine ⟨_, ⟨M, ⟨hM, ⟨hi, hd⟩, hc⟩, rfl⟩, ?_⟩
    simp only [VE.Formula.denote]
    rcases h with ⟨hh, he', ho⟩ | ⟨hol, hh, hel, ho⟩
    · left
      simp only [hh, if_true, VE.Formula.denote]
      refine ⟨(he M).mpr he', ?_⟩
      by_cases hol : D.soft.outranking = .holistic
      · simp only [hol, if_true, VE.Formula.denote]; exact ho hol
      · simp [hol, VE.Formula.denote]
    · right
      simp only [hol, hh, and_self, if_true, VE.Formula.denote, eligible_denote]
      exact ⟨hel, ho⟩

theorem eff_denote : ∀ (g : Nat) (N : SoftNode), (effF D g N).denote S ρ ↔ EffD D S ρ g N
  | 0, N => eligible_denote D S ρ N
  | g + 1, N => by
    simp only [effF, EffD, VE.Formula.denote, eligible_denote]
    rw [domWith_denote D S ρ (effF D g) (EffD D S ρ g) (fun M => eff_denote g M)]

theorem dominated_denote (g : Nat) (N : SoftNode) :
    (dominatedF D g N).denote S ρ ↔ DominatedD D S ρ g N :=
  domWith_denote D S ρ _ _ (fun M => eff_denote D S ρ g M) N

theorem derived_denote (N : SoftNode) :
    (VE.Norms.applies { N.toNode with carveOuts := N.carveOuts ++ derivedList D N }).denote S ρ ↔
      AppliesSoftD D S ρ N := by
  simp only [VE.Norms.applies, VE.Formula.denote, anyF_denote, List.mem_append]
  unfold AppliesSoftD derivedList
  cases hm : N.mode with
  | strict =>
    simp only [LiveD, hm]
    by_cases ha : N.alterable = []
    · have hsw : ¬ (switchF D N).denote S ρ := by
        simp [switchF, switchIn, ha, anyF, VE.Formula.denote]
      rw [if_pos ⟨trivial, ha⟩]
      simp only [List.not_mem_nil, or_false]
      constructor
      · rintro ⟨hg, hn⟩
        exact ⟨hg, fun ⟨U, hU, hd⟩ => hn ⟨U, hU, hd⟩, hsw, fun h => by cases h⟩
      · rintro ⟨hg, hu, _, _⟩
        exact ⟨hg, fun ⟨U, hU, hd⟩ => hu ⟨U, hU, hd⟩⟩
    · rw [if_neg (fun h => ha h.2)]
      simp only [List.mem_singleton, derived, hm]
      constructor
      · rintro ⟨hg, hn⟩
        exact ⟨hg, fun ⟨U, hU, hd⟩ => hn ⟨U, Or.inl hU, hd⟩, fun hs => hn ⟨_, Or.inr rfl, hs⟩,
          fun h => by cases h⟩
      · rintro ⟨hg, hu, hs, _⟩
        refine ⟨hg, ?_⟩
        rintro ⟨U, hU | rfl, hd⟩
        · exact hu ⟨U, hU, hd⟩
        · exact hs hd
  | default =>
    rw [if_neg (fun h => by cases h.1)]
    have hdom := dominated_denote D S ρ D.soft.ranks.length N
    have hblk := blocked_denote D S ρ N
    unfold DominatedD at hdom
    simp only [List.mem_singleton, derived, hm, rankFuel, EffD, EligibleD, LiveD]
    constructor
    · rintro ⟨hg, hn⟩
      refine ⟨⟨trivial, ⟨hg, fun ⟨U, hU, hd⟩ => hn ⟨U, Or.inl hU, hd⟩,
        fun hs => hn ⟨_, Or.inr rfl, Or.inl (Or.inl (Or.inr hs))⟩,
        fun _ he => hn ⟨_, Or.inr rfl, Or.inl (Or.inl (Or.inl he))⟩⟩,
        fun hb => hn ⟨_, Or.inr rfl, Or.inl (Or.inr (hblk.mpr hb))⟩⟩,
        fun hd => hn ⟨_, Or.inr rfl, Or.inr (hdom.mpr hd)⟩⟩
    · rintro ⟨⟨_, ⟨hg, hu, hs, he⟩, hb⟩, hd⟩
      refine ⟨hg, ?_⟩
      rintro ⟨U, hU | rfl, hx⟩
      · exact hu ⟨U, hU, hx⟩
      · simp only [VE.Formula.denote] at hx
        rcases hx with ((hx | hx) | hx) | hx
        · exact he trivial hx
        · exact hs hx
        · exact hb (hblk.mp hx)
        · exact hd (hdom.mp hx)

end Denote

/-! ## Faithfulness: W1's recursion on `T′` is the direct recursion -/

section Faithful
variable (D : SoftDoc) (S : VE.Structure.{u}) (ρ : VE.Valuation S)

theorem primeNode_name (N : SoftNode) : (primeNode D N).name = N.name := rfl
theorem primeNode_pred (N : SoftNode) : (primeNode D N).pred = N.pred := rfl
theorem primeNode_over (N : SoftNode) : (primeNode D N).over = N.over := rfl
theorem primeNode_sign (N : SoftNode) : (primeNode D N).sign = N.sign := rfl

theorem appliesD_prime (N : SoftNode) : AppliesD S ρ (primeNode D N) ↔ AppliesSoftD D S ρ N :=
  (applies_denote S ρ (primeNode D N)).symm.trans (derived_denote D S ρ N)

theorem mem_children_prime (N : SoftNode) (C' : Node) :
    C' ∈ VE.Norms.children (soften D).T (primeNode D N) ↔ ∃ C ∈ children D N, C' = primeNode D C :=
  mem_children_map (primeNode D) (primeNode_name D) (primeNode_pred D) (primeNode_over D) _ rfl N C'

theorem yieldsD_prime : ∀ (f : Nat) (N : SoftNode),
    YieldsD (soften D).T S ρ f (primeNode D N) ↔ YieldsSoftD D S ρ f N
  | 0, N => appliesD_prime D S ρ N
  | f + 1, N => by
    simp only [YieldsD, YieldsSoftD, appliesD_prime]
    apply or_congr_right
    constructor
    · rintro ⟨C', hC', hy⟩
      obtain ⟨C, hC, rfl⟩ := (mem_children_prime D N C').mp hC'
      exact ⟨C, hC, (yieldsD_prime f C).mp hy⟩
    · rintro ⟨C, hC, hy⟩
      exact ⟨primeNode D C, (mem_children_prime D N _).mpr ⟨C, hC, rfl⟩, (yieldsD_prime f C).mpr hy⟩

theorem selectsD_prime (f : Nat) (N : SoftNode) :
    SelectsD (soften D).T S ρ f (primeNode D N) ↔ SelectsSoftD D S ρ f N := by
  simp only [SelectsD, SelectsSoftD, appliesD_prime]
  apply and_congr_right
  intro _
  apply not_congr
  constructor
  · rintro ⟨C', hC', hy⟩
    obtain ⟨C, hC, rfl⟩ := (mem_children_prime D N C').mp hC'
    exact ⟨C, hC, (yieldsD_prime D S ρ f C).mp hy⟩
  · rintro ⟨C, hC, hy⟩
    exact ⟨primeNode D C, (mem_children_prime D N _).mpr ⟨C, hC, rfl⟩, (yieldsD_prime D S ρ f C).mpr hy⟩

theorem fuel_soften : VE.Norms.fuel (soften D).T = fuel D := by
  simp [VE.Norms.fuel, soften, fuel]

theorem mem_rulesOn_soften (p : String) (N' : Node) :
    N' ∈ VE.Norms.rulesOn (soften D).T p ↔ ∃ N ∈ rulesOn D p, N' = primeNode D N := by
  simp only [VE.Norms.rulesOn, rulesOn, soften, List.mem_filter, List.mem_map, beq_iff_eq]
  constructor
  · rintro ⟨⟨N, hN, rfl⟩, hp⟩
    exact ⟨N, ⟨hN, hp⟩, rfl⟩
  · rintro ⟨N, ⟨hN, hp⟩, rfl⟩
    exact ⟨⟨N, hN, rfl⟩, hp⟩

theorem decidesD_soften (p : String) (sign : Bool) :
    DecidesD (soften D).T S ρ p sign ↔ DecidesSoftD D S ρ p sign := by
  simp only [DecidesD, DecidesSoftD, fuel_soften]
  constructor
  · rintro ⟨N', hN', hs, h⟩
    obtain ⟨N, hN, rfl⟩ := (mem_rulesOn_soften D p N').mp hN'
    exact ⟨N, hN, hs, (selectsD_prime D S ρ _ N).mp h⟩
  · rintro ⟨N, hN, hs, h⟩
    exact ⟨primeNode D N, (mem_rulesOn_soften D p _).mpr ⟨N, hN, rfl⟩, hs, (selectsD_prime D S ρ _ N).mpr h⟩

end Faithful

/-- 5.1: W1's `Value` on `T′` is `ValueSoft` on `T`, on every structure and tuple. -/
theorem soften_faithful (D : SoftDoc) (_h : WellFormedSoft D = true) (r : Regulated) (_hr : r ∈ D.T.regulated)
    (S : VE.Structure.{u}) (vs : List S.Carrier) :
    VE.Norms.Value (soften D).T r S vs = ValueSoft D r S vs := by
  unfold VE.Norms.Value ValueSoft
  rw [propext (decidesD_soften D S (tupleVal vs) r.name true),
    propext (decidesD_soften D S (tupleVal vs) r.name false)]

theorem soft_intended_iff (D : SoftDoc) (h : WellFormedSoft D = true) (r : Regulated) (hr : r ∈ D.T.regulated)
    (S : VE.Structure.{u}) : VE.Norms.IntendedAt (soften D).T r S ↔ IntendedSoftAt D r S := by
  unfold VE.Norms.IntendedAt IntendedSoftAt
  simp only [soften_faithful D h r hr]

theorem soft_elaborate_iff (D : SoftDoc) (h : WellFormedSoft D = true) (S : VE.Structure.{u}) :
    Sat S (VE.Norms.elaborate (soften D).T) ↔ holdsSoft D S := by
  rw [Sat, elaborate_iff (soften D) (soften_wellFormed D h) S]
  exact ⟨fun hc r hr => (soft_intended_iff D h r hr S).mp (hc r hr),
    fun hs r hr => (soft_intended_iff D h r hr S).mpr (hs r hr)⟩

/-! ## Declarations under `SoftValid` -/

theorem find_key {α : Type} (key : α → String) : ∀ (l : List α), (l.map key).Nodup → ∀ x ∈ l,
    l.find? (fun y => key y == key x) = some x
  | [], _, _, h => by cases h
  | y :: ys, hn, x, hx => by
    rw [List.map_cons, List.nodup_cons] at hn
    obtain ⟨hy, hys⟩ := hn
    by_cases hk : key y = key x
    · have hxy : x = y := by
        rcases List.mem_cons.mp hx with rfl | hx'
        · rfl
        · exact absurd (hk ▸ List.mem_map_of_mem hx') hy
      subst hxy
      simp
    · have hx' : x ∈ ys := by
        rcases List.mem_cons.mp hx with rfl | h
        · exact absurd rfl hk
        · exact h
      rw [List.find?_cons_of_neg (by simpa using hk)]
      exact find_key key ys hys x hx'

theorem str_lt_or_gt (a b : String) (h : a ≠ b) : a < b ∨ b < a := by
  by_cases h1 : a < b
  · exact Or.inl h1
  · right
    exact Classical.byContradiction fun h2 =>
      h (String.le_antisymm (String.not_lt.mp h2) (String.not_lt.mp h1))

section Valid
variable {D : SoftDoc} (hv : SoftValid D)
include hv

theorem dualPerm_pair {pr : Pair} (hpr : pr ∈ pairs D.base.T) : dualPerm D pr.req = some pr.perm := by
  unfold dualPerm
  rw [find_key (·.req) _ hv.pairReq pr hpr]
  rfl

theorem dualOblig_pair {pr : Pair} (hpr : pr ∈ pairs D.base.T) : dualOblig D pr.perm = some pr.req := by
  unfold dualOblig
  rw [find_key (·.perm) _ hv.pairPerm pr hpr]
  rfl

theorem dualPerm_perm {pr : Pair} (hpr : pr ∈ pairs D.base.T) : dualPerm D pr.perm = none := by
  unfold dualPerm
  have : (pairs D.base.T).find? (·.req == pr.perm) = none := by
    rw [List.find?_eq_none]
    intro x hx he
    simp only [beq_iff_eq] at he
    exact hv.permNotReq pr hpr (he ▸ List.mem_map_of_mem hx)
  rw [this]
  rfl

omit hv in
theorem dualPerm_some {r m : String} (h : dualPerm D r = some m) :
    ∃ pr ∈ pairs D.base.T, pr.req = r ∧ pr.perm = m := by
  unfold dualPerm at h
  obtain ⟨pr, hf, rfl⟩ := Option.map_eq_some_iff.mp h
  exact ⟨pr, List.mem_of_find?_eq_some hf, by simpa using List.find?_some hf, rfl⟩

theorem act_eq {M N : SoftNode} (hi : Incompatible D M N = true) : act D M = act D N := by
  unfold Incompatible at hi
  simp only [Bool.or_eq_true, Bool.and_eq_true, beq_iff_eq, bne_iff_ne, ne_eq, Bool.not_eq_true'] at hi
  unfold act actKey
  rcases hi with (⟨hp, _⟩ | ⟨⟨_, _⟩, hd⟩) | ⟨⟨_, _⟩, hd⟩
  · rw [hp]
  · obtain ⟨pr, hpr, _, hm⟩ := dualPerm_some hd
    rw [hd, ← hm, dualPerm_perm hv hpr]
    rfl
  · obtain ⟨pr, hpr, _, hm⟩ := dualPerm_some hd
    rw [hd, ← hm, dualPerm_perm hv hpr]
    rfl

end Valid

theorem mem_rulesOn {D : SoftDoc} {p : String} {N : SoftNode} : N ∈ rulesOn D p ↔ N ∈ D.T.nodes ∧ N.pred = p := by
  simp [rulesOn]

theorem mem_rulesOnAct {D : SoftDoc} {a : String} {N : SoftNode} :
    N ∈ rulesOnAct D a ↔ N ∈ D.T.nodes ∧ act D N = a := by
  simp [rulesOnAct]

/-! ## Effectiveness, fuel and rank resolution -/

section Rank
variable {D : SoftDoc} {S : VE.Structure.{u}} {ρ : VE.Valuation S}

theorem effD_eligible : ∀ {g : Nat} {N : SoftNode}, EffD D S ρ g N → EligibleD D S ρ N
  | 0, _, h => h
  | _ + 1, _, h => h.1

theorem selectsSoft_eff {f : Nat} {N : SoftNode} (hd : N.mode = .default) (h : SelectsSoftD D S ρ f N) :
    EffD D S ρ (rankFuel D) N := by
  have h1 := h.1
  simp only [AppliesSoftD, hd] at h1
  exact h1

theorem domWith_congr {eff eff' : SoftNode → Prop} (N : SoftNode)
    (h : ∀ M ∈ D.T.nodes, higher D M N = true → (eff M ↔ eff' M)) :
    DomWithD D S ρ eff N ↔ DomWithD D S ρ eff' N := by
  unfold DomWithD
  constructor
  · rintro ⟨M, hM, hi, hd, hc, (⟨hh, he, ho⟩ | hB)⟩
    · exact ⟨M, hM, hi, hd, hc, Or.inl ⟨hh, (h M hM hh).mp he, ho⟩⟩
    · exact ⟨M, hM, hi, hd, hc, Or.inr hB⟩
  · rintro ⟨M, hM, hi, hd, hc, (⟨hh, he, ho⟩ | hB)⟩
    · exact ⟨M, hM, hi, hd, hc, Or.inl ⟨hh, (h M hM hh).mpr he, ho⟩⟩
    · exact ⟨M, hM, hi, hd, hc, Or.inr hB⟩

theorem eff_stable (hv : RanksValid D.soft) : ∀ (k : Nat) (N : SoftNode), N ∈ D.T.nodes → rankHeight D N < k →
    ∀ a b, rankHeight D N < a → rankHeight D N < b → (EffD D S ρ a N ↔ EffD D S ρ b N)
  | 0, _, _, hk => absurd hk (Nat.not_lt_zero _)
  | k + 1, N, _, hk => by
    intro a b ha hb
    match a, b, ha, hb with
    | a + 1, b + 1, ha, hb =>
      simp only [EffD]
      apply and_congr_right
      intro _
      apply not_congr
      apply domWith_congr
      intro M hM hh
      have hlt := rankHeight_lt_of_higher hv hh
      exact eff_stable hv k M hM (by omega) a b (by omega) (by omega)

/-- Fuel stability: for a well-formed document the rank recursion is stable at `rankFuel`. -/
theorem eff_fuel (D : SoftDoc) (h : WellFormedSoft D = true) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (N : SoftNode) (hN : N ∈ D.T.nodes) (g : Nat) (hg : rankHeight D N < g) :
    EffD D S ρ g N ↔ EffD D S ρ (rankFuel D) N :=
  eff_stable (softValid_of_wellFormed D h).ranks (rankHeight D N + 1) N hN (by omega) g (rankFuel D) hg
    (rankHeight_lt_fuel D N)

/-- A higher effective rule and a lower effective colliding rule cannot coexist. -/
theorem resolve_higher (hv : SoftValid D) {H L : SoftNode} (hH : H ∈ D.T.nodes) (hL : L ∈ D.T.nodes)
    (hHd : H.mode = .default) (hLd : L.mode = .default) (hi : Incompatible D H L = true)
    (hh : higher D H L = true) : ¬ (EffD D S ρ (rankFuel D) H ∧ EffD D S ρ (rankFuel D) L) := by
  rintro ⟨eH, eL⟩
  have hcHL : Comparable D H L = true := by simp [Comparable, hh]
  have hcLH : Comparable D L H = true := by simp [Comparable, hh]
  have hiLH : Incompatible D L H = true := by rw [incompatible_symm]; exact hi
  have hlt := rankHeight_lt_of_higher hv.ranks hh
  have hLf := rankHeight_lt_fuel D L
  have eHn : EffD D S ρ D.soft.ranks.length H :=
    (eff_stable hv.ranks (rankHeight D H + 1) H hH (by omega) _ _ (by unfold rankFuel at hLf; omega)
      (rankHeight_lt_fuel D H)).mpr eH
  unfold rankFuel at eH eL
  simp only [EffD] at eH eL
  by_cases ho : D.soft.outranking = .holistic ∧ OutweighsD D S ρ (act D L) (rk L) (rk H)
  · apply eH.2
    refine ⟨L, hL, hiLH, hLd, hcLH, Or.inr ⟨ho.1, hh, eL.1, ?_⟩⟩
    rw [act_eq hv hi]
    exact ho.2
  · apply eL.2
    exact ⟨H, hH, hi, hHd, hcHL, Or.inl ⟨hh, eHn, fun hol hw => ho ⟨hol, hw⟩⟩⟩

end Rank

/-- 4.2 step 3: comparable colliding defaults never both select. -/
theorem rank_resolves (D : SoftDoc) (h : WellFormedSoft D = true) (M N : SoftNode)
    (hc : (M, N) ∈ collidingPairs D) (hcmp : Comparable D M N = true) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) :
    ¬ (SelectsSoftD D S ρ (fuel D) M ∧ SelectsSoftD D S ρ (fuel D) N) := by
  have hv := softValid_of_wellFormed D h
  obtain ⟨hM, hN, hMd, hNd, _, hi⟩ := mem_collidingPairs.mp hc
  rintro ⟨sM, sN⟩
  have eM := selectsSoft_eff hMd sM
  have eN := selectsSoft_eff hNd sN
  unfold Comparable at hcmp
  rcases Bool.or_eq_true_iff.mp hcmp with hh | hh
  · exact resolve_higher hv hM hN hMd hNd hi hh ⟨eM, eN⟩
  · exact resolve_higher hv hN hM hNd hMd (by rw [incompatible_symm]; exact hi) hh ⟨eN, eM⟩

/-- 4.3: an eligible default guarantees an effective default on the same act, before author precedence. -/
theorem eligible_effective (D : SoftDoc) (h : WellFormedSoft D = true) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (a : String) (hex : ∃ N ∈ rulesOnAct D a, EligibleD D S ρ N) :
    ∃ N ∈ rulesOnAct D a, EffD D S ρ (rankFuel D) N := by
  have hv := softValid_of_wellFormed D h
  refine Classical.byContradiction fun hno => ?_
  have hno' : ∀ N ∈ rulesOnAct D a, ¬ EffD D S ρ (rankFuel D) N := fun N hN he => hno ⟨N, hN, he⟩
  have key : ∀ k (N : SoftNode), rankFuel D - rankHeight D N < k → N ∈ rulesOnAct D a →
      EligibleD D S ρ N → False := by
    intro k
    induction k with
    | zero => intro N hk; exact absurd hk (Nat.not_lt_zero _)
    | succ k ih =>
      intro N hk hN he
      have hN' := mem_rulesOnAct.mp hN
      apply hno' N hN
      unfold rankFuel
      refine ⟨he, fun hdom => ?_⟩
      obtain ⟨M, hM, hi, hMd, _, hcase⟩ := hdom
      have hMa : M ∈ rulesOnAct D a := mem_rulesOnAct.mpr ⟨hM, (act_eq hv hi).trans hN'.2⟩
      rcases hcase with ⟨hh, heM, _⟩ | ⟨_, hh, helM, _⟩
      · have hlt := rankHeight_lt_of_higher hv.ranks hh
        have hNf := rankHeight_lt_fuel D N
        apply hno' M hMa
        exact (eff_fuel D h S ρ M hM _ (by unfold rankFuel at hNf; omega)).mp heM
      · have hlt := rankHeight_lt_of_higher hv.ranks hh
        have hMf := rankHeight_lt_fuel D M
        exact ih M (by omega) hMa helM
  obtain ⟨N, hN, he⟩ := hex
  exact key _ N (Nat.lt_succ_self _) hN he

/-! ## Hard over soft -/

theorem default_not_blocked {D : SoftDoc} {S : VE.Structure.{u}} {ρ : VE.Valuation S} {f : Nat}
    {N : SoftNode} (hd : N.mode = .default) (h : SelectsSoftD D S ρ f N) : ¬ BlockedD D S ρ N :=
  (effD_eligible (selectsSoft_eff hd h)).2.2

/-- 4.2 step 2 as a theorem about `soften`: a strict decision silences every default on the
predicate, and a strict decision against a default's effect across the pair silences it. -/
theorem hard_over_soft (D : SoftDoc) (h : WellFormedSoft D = true) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) :
    (∀ p sign, StrictDecidesD D S ρ p sign → ¬ DefaultDecidesD D S ρ p true ∧ ¬ DefaultDecidesD D S ρ p false) ∧
    (∀ pr ∈ pairs (soften D).T, StrictDecidesD D S ρ pr.perm false → ¬ DefaultDecidesD D S ρ pr.req true) ∧
    (∀ pr ∈ pairs (soften D).T, StrictDecidesD D S ρ pr.req true → ¬ DefaultDecidesD D S ρ pr.perm false) := by
  have hv := softValid_of_wellFormed D h
  refine ⟨fun p sign hs => ?_, fun pr hpr hs => ?_, fun pr hpr hs => ?_⟩
  · have hb : ∀ s, ¬ DefaultDecidesD D S ρ p s := by
      rintro s ⟨N, hN, hd, _, hsel⟩
      apply default_not_blocked hd hsel
      obtain ⟨_, rfl⟩ := mem_rulesOn.mp hN
      cases sign
      · exact Or.inr (Or.inl hs)
      · exact Or.inl hs
    exact ⟨hb true, hb false⟩
  · rintro ⟨N, hN, hd, hsgn, hsel⟩
    apply default_not_blocked hd hsel
    refine Or.inr (Or.inr (Or.inl ⟨hsgn, pr.perm, ?_, hs⟩))
    obtain ⟨_, hp⟩ := mem_rulesOn.mp hN
    rw [hp]
    exact dualPerm_pair hv hpr
  · rintro ⟨N, hN, hd, hsgn, hsel⟩
    apply default_not_blocked hd hsel
    refine Or.inr (Or.inr (Or.inr ⟨hsgn, pr.req, ?_, hs⟩))
    obtain ⟨_, hp⟩ := mem_rulesOn.mp hN
    rw [hp]
    exact dualOblig_pair hv hpr

/-- `φ°`: outcome substitution to `E′_base` at the full prefix. -/
def circ (D : SoftDoc) (φ : VE.Formula) : VE.Formula := subst (soften D).T (size (soften D)) φ

theorem substWith_foldl_or (tbl : Table) : ∀ (l : List VE.Formula) (acc : VE.Formula),
    substWith tbl (l.foldl .or acc) = (l.map (substWith tbl)).foldl .or (substWith tbl acc)
  | [], _ => rfl
  | a :: l, acc => by
    simp only [List.foldl_cons, List.map_cons]
    rw [substWith_foldl_or tbl l]
    rfl

theorem substWith_anyF (tbl : Table) (l : List VE.Formula) :
    substWith tbl (anyF l) = anyF (l.map (substWith tbl)) :=
  substWith_foldl_or tbl l .bottom

/-- Syntactically: where a default rule selects on `T′` (after substitution), its
blocking formula is false. -/
theorem subst_selects_blocked (D : SoftDoc) (k : Nat) (N : SoftNode) (hd : N.mode = .default)
    (B : VE.Structure.{u}) (ρ : VE.Valuation B) :
    (subst (soften D).T k (selects' D N)).denote B ρ → ¬ (subst (soften D).T k (blockedF D N)).denote B ρ := by
  intro hs hb
  simp only [selects', VE.Norms.selects, VE.Norms.applies, subst, substWith, VE.Formula.denote,
    substWith_anyF, anyF_denote] at hs
  apply hs.1.2
  refine ⟨substWith (expTable (soften D).T k) (derived D N),
    List.mem_map_of_mem (by simp [primeNode, derivedList, hd]), ?_⟩
  simp only [derived, hd, substWith, VE.Formula.denote]
  exact Or.inl (Or.inr hb)

theorem circ_defaultDecides {D : SoftDoc} {p : String} {sign : Bool} {B : VE.Structure.{u}}
    {ρ : VE.Valuation B} (h : (circ D (defaultDecidesF D p sign)).denote B ρ) :
    ∃ N ∈ rulesOn D p, N.mode = .default ∧ N.sign = sign ∧ (circ D (selects' D N)).denote B ρ := by
  simp only [circ, subst, defaultDecidesF, substWith_anyF, anyF_denote, List.mem_map, List.mem_filter,
    beq_iff_eq] at h
  obtain ⟨_, ⟨_, ⟨N, ⟨⟨hN, hd⟩, hs⟩, rfl⟩, rfl⟩, h⟩ := h
  exact ⟨N, hN, hd, hs, h⟩

/-- Its base-formula corollary: no conflict point of `T′` has a strict rule on one side and a
default rule on the other, on one predicate or across a pair. -/
theorem hard_over_soft_base (D : SoftDoc) (h : WellFormedSoft D = true) (B : VE.Structure.{u})
    (vs : List B.Carrier) :
    (∀ r ∈ D.T.regulated,
      ¬ (VE.Formula.and (circ D (strictPos D r.name)) (circ D (defaultNeg D r.name))).denote B (tupleVal vs) ∧
      ¬ (VE.Formula.and (circ D (defaultPos D r.name)) (circ D (strictNeg D r.name))).denote B (tupleVal vs)) ∧
    (∀ pr ∈ pairs (soften D).T,
      ¬ (VE.Formula.and (circ D (defaultPos D pr.req)) (circ D (strictNeg D pr.perm))).denote B (tupleVal vs) ∧
      ¬ (VE.Formula.and (circ D (strictPos D pr.req)) (circ D (defaultNeg D pr.perm))).denote B (tupleVal vs)) := by
  have hv := softValid_of_wellFormed D h
  have blk : ∀ N : SoftNode, N.mode = .default → (circ D (selects' D N)).denote B (tupleVal vs) →
      ¬ (circ D (blockedF D N)).denote B (tupleVal vs) :=
    fun N hd hs => subst_selects_blocked D _ N hd B _ hs
  have unfoldB : ∀ N : SoftNode, (circ D (blockedF D N)).denote B (tupleVal vs) ↔
      (((circ D (strictPos D N.pred)).denote B (tupleVal vs) ∨ (circ D (strictNeg D N.pred)).denote B (tupleVal vs)) ∨
        (circ D (if N.sign then (match dualPerm D N.pred with
          | some m => strictNeg D m
          | none => .bottom) else .bottom)).denote B (tupleVal vs)) ∨
        (circ D (if N.sign then .bottom else (match dualOblig D N.pred with
          | some r => strictPos D r
          | none => .bottom))).denote B (tupleVal vs) := by
    intro N
    exact Iff.rfl
  refine ⟨fun r _ => ⟨?_, ?_⟩, fun pr hpr => ⟨?_, ?_⟩⟩
  · rintro ⟨hsp, hdn⟩
    obtain ⟨N, hN, hd, _, hs⟩ := circ_defaultDecides hdn
    apply blk N hd hs
    rw [unfoldB, (mem_rulesOn.mp hN).2]
    exact Or.inl (Or.inl (Or.inl hsp))
  · rintro ⟨hdp, hsn⟩
    obtain ⟨N, hN, hd, _, hs⟩ := circ_defaultDecides hdp
    apply blk N hd hs
    rw [unfoldB, (mem_rulesOn.mp hN).2]
    exact Or.inl (Or.inl (Or.inr hsn))
  · rintro ⟨hdp, hsn⟩
    obtain ⟨N, hN, hd, hsg, hs⟩ := circ_defaultDecides hdp
    apply blk N hd hs
    rw [unfoldB, (mem_rulesOn.mp hN).2, hsg, dualPerm_pair hv hpr]
    exact Or.inl (Or.inr hsn)
  · rintro ⟨hsp, hdn⟩
    obtain ⟨N, hN, hd, hsg, hs⟩ := circ_defaultDecides hdn
    apply blk N hd hs
    rw [unfoldB, (mem_rulesOn.mp hN).2, hsg, dualOblig_pair hv hpr]
    exact Or.inr hsp

/-! ## Predicates mentioned by generated formulas -/

theorem mem_preds_foldl_or : ∀ (l : List VE.Formula) (acc : VE.Formula) (q : String),
    q ∈ preds (l.foldl .or acc) ↔ q ∈ preds acc ∨ ∃ a ∈ l, q ∈ preds a
  | [], acc, q => by simp
  | a :: l, acc, q => by
    rw [List.foldl_cons, mem_preds_foldl_or l]
    simp only [preds, List.mem_append, List.mem_cons, exists_eq_or_imp]
    constructor
    · rintro ((h | h) | h)
      · exact Or.inl h
      · exact Or.inr (Or.inl h)
      · exact Or.inr (Or.inr h)
    · rintro (h | h | h)
      · exact Or.inl (Or.inl h)
      · exact Or.inl (Or.inr h)
      · exact Or.inr h

theorem mem_preds_anyF (l : List VE.Formula) (q : String) : q ∈ preds (anyF l) ↔ ∃ a ∈ l, q ∈ preds a := by
  rw [anyF, mem_preds_foldl_or]
  simp [preds]

theorem mem_preds_atom {q p : String} {ss : List String} (h : q ∈ preds (atom p ss)) : q = p := by
  unfold atom at h
  split at h <;> simp_all [preds]

/-- Truth depends only on the relations of the predicates a formula mentions. -/
theorem denote_congr_preds (S : VE.Structure.{u}) (R : String → List S.Carrier → Prop) :
    ∀ (φ : VE.Formula) (ρ : VE.Valuation S), (∀ q ∈ preds φ, ∀ vs, R q vs ↔ S.relation q vs) →
      (φ.denote { S with relation := R } ρ ↔ φ.denote S ρ)
  | .top, _, _ | .bottom, _, _ | .eq _ _, _, _ => Iff.rfl
  | .unary p t, ρ, h => by
    simp only [VE.Formula.denote, VE.Term.denote, h p (by simp [preds])]
  | .binary p t w, ρ, h => by
    simp only [VE.Formula.denote, VE.Term.denote, h p (by simp [preds])]
  | .not a, ρ, h => by
    simp only [VE.Formula.denote]; rw [denote_congr_preds S R a ρ h]
  | .and a b, ρ, h | .or a b, ρ, h | .implies a b, ρ, h => by
    simp only [VE.Formula.denote]
    rw [denote_congr_preds S R a ρ (fun q hq => h q (by simp [preds, hq])),
      denote_congr_preds S R b ρ (fun q hq => h q (by simp [preds, hq]))]
  | .all s a, ρ, h => by
    simp only [VE.Formula.denote]
    exact forall_congr' fun v => imp_congr_right fun _ => denote_congr_preds S R a (v :: ρ) h
  | .ex s a, ρ, h => by
    simp only [VE.Formula.denote]
    exact exists_congr fun v => and_congr_right fun _ => denote_congr_preds S R a (v :: ρ) h

theorem preds_declared {E : VE.Environment} {q : String} (φ : VE.Formula) :
    ∀ {Γ : List String}, φ.WellFormed E Γ → q ∈ preds φ → (E.predicates q).isSome := by
  induction φ with
  | top | bottom | eq _ _ => intro _ _ h; simp [preds] at h
  | unary p _ =>
    intro _ hw h
    obtain ⟨_, hp, _⟩ := hw
    simp only [preds, List.mem_singleton] at h; subst h; simp [hp]
  | binary p _ _ =>
    intro _ hw h
    obtain ⟨_, _, hp, _⟩ := hw
    simp only [preds, List.mem_singleton] at h; subst h; simp [hp]
  | not a ih => intro _ hw h; exact ih hw h
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    intro _ hw h
    simp only [preds, List.mem_append] at h
    rcases h with h | h
    · exact ia hw.1 h
    · exact ib hw.2 h
  | all _ a ih | ex _ a ih => intro _ hw h; exact ih hw.2 h

theorem preds_liveStrict (regs : List Regulated) (N : SoftNode) {q : String}
    (h : q ∈ preds (liveStrictIn regs N)) :
    q ∈ preds N.guard ∨ (∃ U ∈ N.carveOuts, q ∈ preds U) ∨ ∃ π ∈ N.alterable, q = offName N π := by
  simp only [liveStrictIn, preds, List.mem_append, mem_preds_anyF, switchIn, List.mem_map] at h
  rcases h with (h | h) | h
  · exact Or.inl h
  · exact Or.inr (Or.inl h)
  · obtain ⟨_, ⟨π, hπ, rfl⟩, hq⟩ := h
    exact Or.inr (Or.inr ⟨π, hπ, mem_preds_atom hq⟩)

theorem preds_strictYields (regs : List Regulated) (ns : List SoftNode) {q : String} :
    ∀ (f : Nat) (N : SoftNode), N ∈ ns → q ∈ preds (strictYieldsIn regs ns f N) →
      ∃ M ∈ ns, M.mode = .strict ∧ q ∈ preds (liveStrictIn regs M)
  | 0, N, hN, h => by
    simp only [strictYieldsIn, preds, List.mem_append, mem_preds_anyF, List.not_mem_nil,
      false_and, exists_false, or_false] at h
    split at h
    · exact ⟨N, hN, ‹_›, h⟩
    · simp [preds] at h
  | f + 1, N, hN, h => by
    simp only [strictYieldsIn, preds, List.mem_append, mem_preds_anyF, List.mem_map] at h
    rcases h with h | ⟨_, ⟨C, hC, rfl⟩, h⟩
    · split at h
      · exact ⟨N, hN, ‹_›, h⟩
      · simp [preds] at h
    · exact preds_strictYields regs ns f C (mem_childrenIn_iff.mp hC).1 h

theorem preds_strictDecides (regs : List Regulated) (ns : List SoftNode) (p : String) (sign : Bool)
    {q : String} (h : q ∈ preds (strictDecidesIn regs ns p sign)) :
    ∃ M ∈ ns, M.mode = .strict ∧ q ∈ preds (liveStrictIn regs M) := by
  simp only [strictDecidesIn, mem_preds_anyF, List.mem_map, List.mem_filter] at h
  obtain ⟨_, ⟨N, ⟨⟨hN, _⟩, _⟩, rfl⟩, h⟩ := h
  unfold strictSelectsIn at h
  split at h
  · simp only [preds, List.mem_append, mem_preds_anyF, List.mem_map] at h
    rcases h with h | ⟨_, ⟨C, hC, rfl⟩, h⟩
    · exact ⟨N, hN, ‹_›, h⟩
    · exact preds_strictYields regs ns _ C (mem_childrenIn_iff.mp hC).1 h
  · simp [preds] at h

theorem flatMap_disjoint {α β : Type} (g : α → List β) : ∀ (l : List α), (l.flatMap g).Nodup →
    ∀ a ∈ l, ∀ b ∈ l, a ≠ b → ∀ x ∈ g a, x ∉ g b
  | [], _, _, h, _, _, _, _, _, _ => by cases h
  | c :: cs, hn, a, ha, b, hb, hab, x, hxa, hxb => by
    rw [List.flatMap_cons, List.nodup_append] at hn
    obtain ⟨_, hcs, hdis⟩ := hn
    rcases List.mem_cons.mp ha with rfl | ha'
    · rcases List.mem_cons.mp hb with rfl | hb'
      · exact hab rfl
      · exact hdis x hxa x (List.mem_flatMap.mpr ⟨b, hb', hxb⟩) rfl
    · rcases List.mem_cons.mp hb with rfl | hb'
      · exact hdis x hxb x (List.mem_flatMap.mpr ⟨a, ha', hxa⟩) rfl
      · exact flatMap_disjoint g cs hcs a ha' b hb' hab x hxa hxb

theorem offNames_eq (D : SoftDoc) :
    (offDecisions D).map (·.1) = D.T.nodes.flatMap (fun N => N.alterable.map (offName N)) := by
  simp [offDecisions, List.map_flatMap, Function.comp_def]

theorem decisionNames_eq (D : SoftDoc) : decisionNames D =
    (exceptedDecisions D).map (·.1) ++ D.T.nodes.flatMap (fun N => N.alterable.map (offName N)) ++
      (outweighsDecisions D).map (·.1) := by
  simp only [decisionNames, decisions, List.map_append, offNames_eq]

theorem weighing_sub_decisions (D : SoftDoc) {q : String} (h : q ∈ weighingSyms D) : q ∈ decisionNames D := by
  rw [decisionNames_eq]
  simp only [weighingSyms, List.mem_append, List.mem_flatMap, List.mem_filter] at h ⊢
  rcases h with (h | ⟨N, ⟨hN, _⟩, h⟩) | h
  · exact Or.inl (Or.inl h)
  · exact Or.inl (Or.inr ⟨N, hN, h⟩)
  · exact Or.inr h

theorem strict_off_not_weighing {D : SoftDoc} (hv : SoftValid D) {N : SoftNode} (hN : N ∈ D.T.nodes)
    (hs : N.mode = .strict) {π : String} (hπ : π ∈ N.alterable) : offName N π ∉ weighingSyms D := by
  have hn := hv.decNodup
  rw [decisionNames_eq, List.nodup_append, List.nodup_append] at hn
  obtain ⟨⟨_, hoff, hdis1⟩, _, hdis2⟩ := hn
  have hq : offName N π ∈ D.T.nodes.flatMap (fun N => N.alterable.map (offName N)) :=
    List.mem_flatMap.mpr ⟨N, hN, List.mem_map_of_mem hπ⟩
  intro hw
  simp only [weighingSyms, List.mem_append, List.mem_flatMap, List.mem_filter, beq_iff_eq] at hw
  rcases hw with (h | ⟨M, ⟨hM, hMd⟩, h⟩) | h
  · exact hdis1 _ h _ hq rfl
  · exact flatMap_disjoint (fun N => N.alterable.map (offName N)) _ hoff N hN M hM
      (fun e => by rw [e, hMd] at hs; cases hs) _ (List.mem_map_of_mem hπ) h
  · exact hdis2 _ (List.mem_append_right _ hq) _ h rfl

/-! ## Weighing independence and cone independence -/

/-- Same `E`, literals, regulated and definitions, and the same nodes up to rank,
exception, `hard` and the switches of default rules; ranks, `outranks`, ties and the
flag may differ. -/
def sameStrictCore (D D₂ : SoftDoc) : Prop :=
  D₂.E = D.E ∧ D₂.lits = D.lits ∧ D₂.T.regulated = D.T.regulated ∧ D₂.T.definitions = D.T.definitions ∧
    D₂.T.nodes.map coreNode = D.T.nodes.map coreNode

/-- Local weighing independence: strict selection on `p` reads neither ranks, the flag,
`outweighs`, exceptions nor the switches of default rules. (i) syntactically; (ii) as a
function of the strict core; (iii) semantically, in the form of W1's `denote_relation_congr`. -/
theorem hard_never_weighed (D : SoftDoc) (h : WellFormedSoft D = true) (p : String) (sign : Bool) :
    (∀ q ∈ VE.Norms.preds (strictDecidesF D p sign), q ∉ weighingSyms D) ∧
    (∀ (D₂ : SoftDoc), sameStrictCore D D₂ → strictDecidesF D₂ p sign = strictDecidesF D p sign) ∧
    (∀ (S : VE.Structure.{u}) (R : String → List S.Carrier → Prop)
      (_hR : ∀ q vs, q ∉ weighingSyms D → (R q vs ↔ S.relation q vs)) (ρ : VE.Valuation S),
      StrictDecidesD D { S with relation := R } ρ p sign ↔ StrictDecidesD D S ρ p sign) := by
  have hv := softValid_of_wellFormed D h
  have hi : ∀ q ∈ VE.Norms.preds (strictDecidesF D p sign), q ∉ weighingSyms D := by
    intro q hq hw
    obtain ⟨M, hM, hMs, hq⟩ := preds_strictDecides _ _ p sign hq
    obtain ⟨N, hN, rfl⟩ := List.mem_map.mp hM
    have hNs : N.mode = .strict := hMs
    have hdecl : ∀ φ ∈ N.guard :: N.carveOuts, q ∈ preds φ → False := by
      intro φ hφ hqφ
      have := preds_declared φ (hv.typed N hN φ hφ) hqφ
      rw [hv.decFresh q (weighing_sub_decisions D hw)] at this
      cases this
    rcases preds_liveStrict _ _ hq with hg | ⟨U, hU, hqU⟩ | ⟨π, hπ, rfl⟩
    · exact hdecl N.guard List.mem_cons_self hg
    · exact hdecl U (List.mem_cons_of_mem _ hU) hqU
    · have hπ' : π ∈ N.alterable := by simpa [coreNode, hNs] using hπ
      exact strict_off_not_weighing hv hN hNs hπ' hw
  refine ⟨hi, fun D₂ ⟨_, _, hreg, _, hnodes⟩ => ?_, fun S R hR ρ => ?_⟩
  · simp only [strictDecidesF, hreg, hnodes]
  · rw [← strictDecides_denote, ← strictDecides_denote]
    exact denote_congr_preds S R _ ρ (fun q hq vs => hR q vs (hi q hq))

/-! ### The cone (7.4) -/

/-- The predicates of formulas `φs`, followed by the table entries of those predicates. -/
def predsWith (tbl : String → List String) (φs : List VE.Formula) : List String :=
  φs.flatMap preds ++ (φs.flatMap preds).flatMap tbl

/-- For each layer symbol placed before `k`: every predicate reachable from it through
guards and carve-outs of its rules (on `T′`, including the derived ones), definition bodies
and the layer symbols below it. -/
def coneTable (T : Tree) : Nat → String → List String
  | 0, _ => []
  | k + 1, n => match (syms T)[k]? with
    | some q => if n = q.name then predsWith (coneTable T k) (q.formulas T) else coneTable T k n
    | none => coneTable T k n

def rulesFormulas (T : Tree) (p : String) : List VE.Formula :=
  (VE.Norms.rulesOn T p).flatMap (fun N => N.guard :: N.carveOuts)

/-- The predicates of every declared condition of each `excepted_N` among `ps`. -/
def exceptionPreds (D : SoftDoc) (ps : List String) : List String :=
  D.T.nodes.flatMap (fun N => if ps.contains (exceptedName N) then
    ((N.exception.map (fun e => (e.sufficient ++ e.necessary).flatMap preds)).getD []) else [])

/-- `cone(p)` (7.4): the predicates reachable from the rules on `p` in `T′` through guards,
carve-outs (including derived ones), definition bodies and the rules of lower regulated
predicates, closed over the declared conditions of each `excepted_N` reached (the conditions
are over the base vocabulary of `E`, so one step closes it). -/
def cone (D : SoftDoc) (p : String) : List String :=
  let base := predsWith (coneTable (soften D).T (before (soften D) p)) (rulesFormulas (soften D).T p)
  base ++ exceptionPreds D base

theorem preds_inst : ∀ (σ : List VE.Term) (φ : VE.Formula), preds (inst σ φ) = preds φ
  | _, .top | _, .bottom | _, .unary _ _ | _, .binary _ _ _ | _, .eq _ _ => rfl
  | σ, .not a => preds_inst σ a
  | σ, .and a b | σ, .or a b | σ, .implies a b => by
    simp only [inst, preds, preds_inst σ a, preds_inst σ b]
  | σ, .all _ a | σ, .ex _ a => preds_inst _ a

theorem preds_substWith (tbl : Table) {q : String} : ∀ (φ : VE.Formula), q ∈ preds (substWith tbl φ) →
    q ∈ preds φ ∨ ∃ m ∈ preds φ, ∃ F, tbl m = some F ∧ q ∈ preds F
  | .top, h | .bottom, h | .eq _ _, h => by simp [substWith, preds] at h
  | .unary p t, h => by
    simp only [substWith] at h
    split at h
    · rename_i F hF
      rw [preds_inst] at h
      exact Or.inr ⟨p, by simp [preds], F, hF, h⟩
    · exact Or.inl h
  | .binary p t w, h => by
    simp only [substWith] at h
    split at h
    · rename_i F hF
      rw [preds_inst] at h
      exact Or.inr ⟨p, by simp [preds], F, hF, h⟩
    · exact Or.inl h
  | .not a, h => preds_substWith tbl a h
  | .and a b, h | .or a b, h | .implies a b, h => by
    simp only [substWith, preds, List.mem_append] at h ⊢
    rcases h with h | h
    · rcases preds_substWith tbl a h with h | ⟨m, hm, F, hF, hq⟩
      · exact Or.inl (Or.inl h)
      · exact Or.inr ⟨m, Or.inl hm, F, hF, hq⟩
    · rcases preds_substWith tbl b h with h | ⟨m, hm, F, hF, hq⟩
      · exact Or.inl (Or.inr h)
      · exact Or.inr ⟨m, Or.inr hm, F, hF, hq⟩
  | .all _ a, h | .ex _ a, h => preds_substWith tbl a h

theorem preds_yields (T : Tree) {p q : String} : ∀ (f : Nat) (N : Node), N ∈ T.nodes → N.pred = p →
    q ∈ preds (yields T f N) → q ∈ (rulesFormulas T p).flatMap preds
  | 0, N, hN, hp, h => by
    simp only [yields, preds, VE.Norms.applies, List.mem_append, mem_preds_anyF, List.not_mem_nil,
      false_and, exists_false, or_false] at h
    simp only [rulesFormulas, List.mem_flatMap, VE.Norms.rulesOn, List.mem_filter, beq_iff_eq, List.mem_cons]
    rcases h with h | ⟨U, hU, h⟩
    · exact ⟨N.guard, ⟨N, ⟨hN, hp⟩, Or.inl rfl⟩, h⟩
    · exact ⟨U, ⟨N, ⟨hN, hp⟩, Or.inr hU⟩, h⟩
  | f + 1, N, hN, hp, h => by
    simp only [yields, preds, VE.Norms.applies, List.mem_append, mem_preds_anyF, List.mem_map] at h
    rcases h with (h | ⟨U, hU, h⟩) | ⟨_, ⟨C, hC, rfl⟩, h⟩
    · simp only [rulesFormulas, List.mem_flatMap, VE.Norms.rulesOn, List.mem_filter, beq_iff_eq, List.mem_cons]
      exact ⟨N.guard, ⟨N, ⟨hN, hp⟩, Or.inl rfl⟩, h⟩
    · simp only [rulesFormulas, List.mem_flatMap, VE.Norms.rulesOn, List.mem_filter, beq_iff_eq, List.mem_cons]
      exact ⟨U, ⟨N, ⟨hN, hp⟩, Or.inr hU⟩, h⟩
    · obtain ⟨hC, hCp⟩ := VE.Norms.mem_children hC
      exact preds_yields T f C hC (hCp.trans hp) h

theorem preds_selects (T : Tree) {p q : String} (f : Nat) (N : Node) (hN : N ∈ T.nodes) (hp : N.pred = p)
    (h : q ∈ preds (VE.Norms.selects T f N)) : q ∈ (rulesFormulas T p).flatMap preds := by
  simp only [VE.Norms.selects, preds, VE.Norms.applies, List.mem_append, mem_preds_anyF, List.mem_map] at h
  simp only [rulesFormulas, List.mem_flatMap, VE.Norms.rulesOn, List.mem_filter, beq_iff_eq, List.mem_cons]
  rcases h with (h | ⟨U, hU, h⟩) | ⟨_, ⟨C, hC, rfl⟩, h⟩
  · exact ⟨N.guard, ⟨N, ⟨hN, hp⟩, Or.inl rfl⟩, h⟩
  · exact ⟨U, ⟨N, ⟨hN, hp⟩, Or.inr hU⟩, h⟩
  · obtain ⟨hC, hCp⟩ := VE.Norms.mem_children hC
    have := preds_yields T f C hC (hCp.trans hp) h
    simpa [rulesFormulas, VE.Norms.rulesOn] using this

theorem preds_meaning (T : Tree) (s : Sym) {q : String} (h : q ∈ preds (s.meaning T)) :
    q ∈ (s.formulas T).flatMap preds := by
  cases s with
  | defn d => simpa [Sym.meaning, Sym.formulas] using h
  | reg r =>
    have hout : q ∈ preds (VE.Norms.decides T r.name true) ∨ q ∈ preds (VE.Norms.decides T r.name false) := by
      simp only [Sym.meaning, outcome] at h
      split at h
      · exact Or.inr (by simpa [preds, neg] using h)
      · exact Or.inl (by simpa [pos] using h)
    have key : ∀ sign, q ∈ preds (VE.Norms.decides T r.name sign) → q ∈ (rulesFormulas T r.name).flatMap preds := by
      intro sign hq
      simp only [VE.Norms.decides, mem_preds_anyF, List.mem_map, List.mem_filter, VE.Norms.rulesOn,
        beq_iff_eq] at hq
      obtain ⟨_, ⟨N, ⟨⟨hN, hp⟩, _⟩, rfl⟩, hq⟩ := hq
      exact preds_selects T _ N hN hp hq
    have : q ∈ (rulesFormulas T r.name).flatMap preds := by
      rcases hout with h | h
      · exact key true h
      · exact key false h
    simpa [Sym.formulas, rulesFormulas] using this

theorem coneTable_at {D : Doc} (hv : Valid D) : ∀ (k j : Nat) (q : Sym), j < k →
    (syms D.T)[j]? = some q → coneTable D.T k q.name = predsWith (coneTable D.T j) (q.formulas D.T)
  | 0, _, _, h, _ => absurd h (Nat.not_lt_zero _)
  | k + 1, j, q, hj, hq => by
    cases hq' : (syms D.T)[k]? with
    | some q' =>
      simp only [coneTable, hq']
      by_cases he : q.name = q'.name
      · have := nodup_getElemOpt_inj hv.nodup (names_getElemOpt hq) (he ▸ names_getElemOpt hq')
        subst this
        rw [hq] at hq'
        cases hq'
        simp
      · simp only [he, if_false]
        rcases Nat.lt_succ_iff_lt_or_eq.mp hj with hj | rfl
        · exact coneTable_at hv k j q hj hq
        · rw [hq] at hq'; cases hq'; exact absurd rfl he
    | none =>
      simp only [coneTable, hq']
      rcases Nat.lt_succ_iff_lt_or_eq.mp hj with hj | rfl
      · exact coneTable_at hv k j q hj hq
      · rw [hq] at hq'; cases hq'

theorem expTable_cone {D : Doc} (hv : Valid D) (k : Nat) :
    ∀ n F, expTable D.T k n = some F → ∀ q ∈ preds F, q ∈ coneTable D.T k n := by
  induction k using Nat.strongRecOn with
  | ind k ih =>
    intro n F hF q hq
    obtain ⟨j, s, hj, hs, rfl, rfl⟩ := expTable_some D.T k n F hF
    rw [coneTable_at hv k j s hj hs, predsWith, List.mem_append]
    rcases preds_substWith _ _ hq with h | ⟨m, hm, F', hF', hq'⟩
    · exact Or.inl (preds_meaning D.T s h)
    · exact Or.inr (List.mem_flatMap.mpr ⟨m, preds_meaning D.T s hm, ih j hj m F' hF' q hq'⟩)

theorem preds_outcomeBase_cone (D : SoftDoc) (h : WellFormedSoft D = true) (p : String) {q : String}
    (hq : q ∈ preds (outcomeBase (soften D) p)) : q ∈ cone D p := by
  have hv := valid_of_wellFormed _ (soften_wellFormed D h)
  unfold outcomeBase at hq
  split at hq
  · rename_i r hr
    have hrn : r.name = p := by simpa using List.find?_some hr
    simp only [cone, List.mem_append]
    left
    rw [predsWith, List.mem_append]
    have hout : ∀ x ∈ preds (outcome (soften D).T r), x ∈ (rulesFormulas (soften D).T p).flatMap preds := by
      intro x hx
      have := preds_meaning (soften D).T (.reg r) hx
      simpa [Sym.formulas, rulesFormulas, hrn] using this
    rcases preds_substWith _ _ hq with h | ⟨m, hm, F, hF, hqF⟩
    · exact Or.inl (hout q h)
    · exact Or.inr (List.mem_flatMap.mpr ⟨m, hout m hm, expTable_cone hv _ m F hF q hqF⟩)
  · simp [preds] at hq

/-- The general non-mention lemma behind the two global claims. -/
theorem cone_independent (D : SoftDoc) (h : WellFormedSoft D = true) (p : String)
    (_hp : p ∈ VE.Norms.regulatedNames D.base.T) (Q : List String) (hQ : ∀ q ∈ cone D p, q ∉ Q)
    (B : VE.Structure.{u}) (R : String → List B.Carrier → Prop)
    (hR : ∀ q vs, q ∉ Q → (R q vs ↔ B.relation q vs)) (vs : List B.Carrier) :
    (outcomeBase (soften D) p).denote { B with relation := R } (tupleVal vs) ↔
      (outcomeBase (soften D) p).denote B (tupleVal vs) :=
  denote_congr_preds B R _ _ (fun q hq ws => hR q ws (hQ q (preds_outcomeBase_cone D h p hq)))

/-- Global weighing independence needs a decision-free cone; strictness or hardness alone
does not give it (fixture μ). -/
theorem hard_never_weighed_global (D : SoftDoc) (h : WellFormedSoft D = true) (p : String)
    (hp : p ∈ VE.Norms.regulatedNames D.base.T) (_hcone : ∀ q ∈ cone D p, q ∉ decisionNames D)
    (B : VE.Structure.{u}) (R : String → List B.Carrier → Prop)
    (hR : ∀ q vs, q ∉ decisionNames D → (R q vs ↔ B.relation q vs)) (vs : List B.Carrier) :
    (outcomeBase (soften D) p).denote { B with relation := R } (tupleVal vs) ↔
      (outcomeBase (soften D) p).denote B (tupleVal vs) :=
  cone_independent D h p hp (decisionNames D) _hcone B R hR vs

/-- 7.4: declared attribution only. -/
theorem authority_independent (D : SoftDoc) (h : WellFormedSoft D = true) (p : String)
    (hp : p ∈ VE.Norms.regulatedNames D.base.T) (π : String) (_hπ : π ∈ D.soft.parties)
    (hcone : ∀ q ∈ cone D p, q ∉ attributed D π) (B : VE.Structure.{u})
    (R : String → List B.Carrier → Prop) (hR : ∀ q vs, q ∉ attributed D π → (R q vs ↔ B.relation q vs))
    (vs : List B.Carrier) :
    (outcomeBase (soften D) p).denote { B with relation := R } (tupleVal vs) ↔
      (outcomeBase (soften D) p).denote B (tupleVal vs) :=
  cone_independent D h p hp (attributed D π) hcone B R hR vs

/-- 1.2: the closed `outranks` order is a strict partial order. -/
theorem rank_acyclic (D : SoftDoc) (h : WellFormedSoft D = true) :
    VE.Route.DagAcyclic (rankNodes D.soft) ∧
    (∀ a, outranksPlus D.soft a a = false) ∧
    (∀ a b c, outranksPlus D.soft a b = true → outranksPlus D.soft b c = true → outranksPlus D.soft a c = true) := by
  have hv := (softValid_of_wellFormed D h).ranks
  obtain ⟨_, _, _, _, hd⟩ := order_facts hv
  exact ⟨hd, outranksPlus_irrefl hv, fun _ _ _ h₁ h₂ => outranksPlus_trans hv h₁ h₂⟩

/-! ## Every default–default collision is at a colliding pair -/

theorem eq_of_key {α : Type} (key : α → String) : ∀ {l : List α}, (l.map key).Nodup → ∀ {x y : α},
    x ∈ l → y ∈ l → key x = key y → x = y
  | [], _, _, _, hx, _, _ => by cases hx
  | z :: zs, hn, x, y, hx, hy, he => by
    rw [List.map_cons, List.nodup_cons] at hn
    rcases List.mem_cons.mp hx with rfl | hx' <;> rcases List.mem_cons.mp hy with rfl | hy'
    · rfl
    · exact absurd (he ▸ List.mem_map_of_mem hy') hn.1
    · exact absurd (he.symm ▸ List.mem_map_of_mem hx') hn.1
    · exact eq_of_key key hn.2 hx' hy' he

theorem colliding_of {D : SoftDoc} (hv : SoftValid D) {M N : SoftNode} (hM : M ∈ D.T.nodes) (hN : N ∈ D.T.nodes)
    (hMd : M.mode = .default) (hNd : N.mode = .default) (hne : M ≠ N) (hi : Incompatible D M N = true) :
    (M, N) ∈ collidingPairs D ∨ (N, M) ∈ collidingPairs D := by
  have hname : M.name ≠ N.name := fun e => hne (eq_of_key (fun N : SoftNode => N.name) hv.names hM hN e)
  rcases str_lt_or_gt _ _ hname with hlt | hlt
  · exact Or.inl (mem_collidingPairs.mpr ⟨hM, hN, hMd, hNd, hlt, hi⟩)
  · exact Or.inr (mem_collidingPairs.mpr ⟨hN, hM, hNd, hMd, hlt, by rw [incompatible_symm]; exact hi⟩)

theorem comparable_false {D : SoftDoc} (h : WellFormedSoft D = true) {M N : SoftNode}
    (hc : (M, N) ∈ collidingPairs D) {S : VE.Structure.{u}} {ρ : VE.Valuation S}
    (hs : SelectsSoftD D S ρ (fuel D) M ∧ SelectsSoftD D S ρ (fuel D) N) : Comparable D M N = false := by
  cases hcmp : Comparable D M N
  · rfl
  · exact absurd hs (rank_resolves D h M N hc hcmp S ρ)

/-- 6.3: every default–default collision is at a colliding pair; such a pair is not comparable. -/
theorem weighing_points_complete (D : SoftDoc) (h : WellFormedSoft D = true) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) :
    (∀ p, DefaultDecidesD D S ρ p true → DefaultDecidesD D S ρ p false →
      ∃ M N, (M, N) ∈ collidingPairs D ∧ M.pred = p ∧ N.pred = p ∧
        SelectsSoftD D S ρ (fuel D) M ∧ SelectsSoftD D S ρ (fuel D) N ∧ Comparable D M N = false) ∧
    (∀ pr ∈ pairs (soften D).T, DefaultDecidesD D S ρ pr.req true → DefaultDecidesD D S ρ pr.perm false →
      ∃ M N, (M, N) ∈ collidingPairs D ∧
        ((M.pred = pr.req ∧ N.pred = pr.perm) ∨ (M.pred = pr.perm ∧ N.pred = pr.req)) ∧
        SelectsSoftD D S ρ (fuel D) M ∧ SelectsSoftD D S ρ (fuel D) N ∧ Comparable D M N = false) := by
  have hv := softValid_of_wellFormed D h
  refine ⟨fun p ⟨M, hM, hMd, hMs, sM⟩ ⟨N, hN, hNd, hNs, sN⟩ => ?_, fun pr hpr ⟨M, hM, hMd, hMs, sM⟩
    ⟨N, hN, hNd, hNs, sN⟩ => ?_⟩
  · obtain ⟨hM, hMp⟩ := mem_rulesOn.mp hM
    obtain ⟨hN, hNp⟩ := mem_rulesOn.mp hN
    have hne : M ≠ N := fun e => by rw [e, hNs] at hMs; cases hMs
    have hi : Incompatible D M N = true := by
      simp [Incompatible, hMp, hNp, hMs, hNs]
    rcases colliding_of hv hM hN hMd hNd hne hi with hc | hc
    · exact ⟨M, N, hc, hMp, hNp, sM, sN, comparable_false h hc ⟨sM, sN⟩⟩
    · exact ⟨N, M, hc, hNp, hMp, sN, sM, comparable_false h hc ⟨sN, sM⟩⟩
  · obtain ⟨hM, hMp⟩ := mem_rulesOn.mp hM
    obtain ⟨hN, hNp⟩ := mem_rulesOn.mp hN
    have hv' := valid_of_wellFormed _ (soften_wellFormed D h)
    have hrp := (hv'.pairs pr hpr).1
    have hne : M ≠ N := fun e => hrp (by rw [← hMp, ← hNp, e])
    have hi : Incompatible D M N = true := by
      have hd := dualPerm_pair hv (show pr ∈ pairs D.base.T from hpr)
      simp [Incompatible, hMp, hNp, hMs, hNs, hd]
    rcases colliding_of hv hM hN hMd hNd hne hi with hc | hc
    · exact ⟨M, N, hc, Or.inl ⟨hMp, hNp⟩, sM, sN, comparable_false h hc ⟨sM, sN⟩⟩
    · exact ⟨N, M, hc, Or.inr ⟨hNp, hMp⟩, sN, sM, comparable_false h hc ⟨sN, sM⟩⟩

end VE.SoftNorms
