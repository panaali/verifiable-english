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

end VE.SoftNorms
