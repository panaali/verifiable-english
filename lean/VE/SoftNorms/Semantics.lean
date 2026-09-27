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

end VE.SoftNorms
