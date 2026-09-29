import VE.Rights.Correlate

/-! The direct semantics `ValueRight` (docs/spec/rights.md 4.3, 9.1) and its relation to
the elaboration (9.2).

`ValueRight` is soft-norms' `ValueSoft` read on the rights document's own rules, the line
nodes (guard with the holder conjunct, author carve-outs and the packed limitation) and
the norm units outside rights, with two changes and no bar node:

* the bar is a condition, `BarredX`, on the right-derived positive lines: it makes the
  line's subtree yield and stops the line selecting (the bar decides beneath it);
* the strict negative decision on a right-derived permission predicate `m` gains the
  disjunct `aimed_m` (`StrictDecidesR`), so step 2 blocks a default rule on `m` or a
  default `require` across the dual pair where `aimed_m` holds.

The recursion is on rules (`…X`, over `directNodes D`, the rules of `T″` without the
bars) because a line's exceptions may be rules outside rights; each `…R` on a line
instance is the `…X` of its node. `LiveX` is soft's `LiveD` on the node, which for a line
node is `LiveR` (`liveR_denote`). `correlate_faithful` is by unfolding: a bar node applies
exactly where `aimed_m` holds, has no children, and is a child of exactly the
right-derived positive nodes on `m`. -/
namespace VE.Rights
open VE.Norms (Regulated anyF atom tupleVal catalaValue)
open VE.SoftNorms (SoftNode SoftDoc LiveD StrictYieldsD StrictSelectsD StrictDecidesD BlockedD EligibleD
  DomWithD EffD AppliesSoftD YieldsSoftD SelectsSoftD DecidesSoftD ValueSoft OutweighsD childrenIn
  dualPerm dualOblig Incompatible Comparable higher act rk rankFuel rulesOn)
universe u

/-- The fuel of `T″`. -/
def fuelR (D : RightsDoc) : Nat := (correlate D).T.nodes.length

section Direct
variable (D : RightsDoc) (S : VE.Structure.{u}) (ρ : VE.Valuation S)

/-- Step 0 on a line instance: guard, holder guard, author carve-outs, the limitations in
scope, switches, and for a default line its exception. -/
def LiveR (N : Line) : Prop :=
  (ownGuard D N).denote S ρ ∧ ¬ (∃ U ∈ N.node.carveOuts, U.denote S ρ) ∧ ¬ (limPack D N).denote S ρ ∧
    ¬ (VE.SoftNorms.switchF (correlate D) (nodeOf D N)).denote S ρ ∧
    (N.node.mode = .default → ¬ (VE.SoftNorms.exceptedF (correlate D) (nodeOf D N)).denote S ρ)

/-- The bar on a line instance (rule reading). -/
def BarredR (N : Line) : Prop :=
  ruleReading D = true ∧ N.node.sign = true ∧ rightPermission D N.node.pred = true ∧ (aimedF D N.node.pred).denote S ρ

/-- Step 0 on a rule of `T″` without bars. -/
def LiveX (X : SoftNode) : Prop := LiveD (correlate D) S ρ X

/-- The bar on a rule: a right-derived positive line node on a right-derived permission predicate. -/
def BarredX (X : SoftNode) : Prop :=
  ruleReading D = true ∧ X.sign = true ∧ X ∈ lineNodes D ∧ rightPermission D X.pred = true ∧
    (aimedF D X.pred).denote S ρ

def StrictYieldsX : Nat → SoftNode → Prop
  | 0, X => X.mode = .strict ∧ LiveX D S ρ X
  | f + 1, X => (X.mode = .strict ∧ LiveX D S ρ X) ∨ BarredX D S ρ X ∨
      ∃ C ∈ childrenIn (directNodes D) X, StrictYieldsX f C

def StrictSelectsX (f : Nat) (X : SoftNode) : Prop :=
  X.mode = .strict ∧ LiveX D S ρ X ∧ ¬ BarredX D S ρ X ∧
    ¬ ∃ C ∈ childrenIn (directNodes D) X, StrictYieldsX D S ρ f C

def StrictYieldsR (f : Nat) (N : Line) : Prop := StrictYieldsX D S ρ f (nodeOf D N)
def StrictSelectsR (f : Nat) (N : Line) : Prop := StrictSelectsX D S ρ f (nodeOf D N)

/-- Strict decisions: a line, a rule outside rights, or (sign `false`) the bar. -/
def StrictDecidesR (p : String) (sign : Bool) : Prop :=
  (∃ N ∈ (linesOf D).map (·.2), N.node.pred = p ∧ N.node.sign = sign ∧ StrictSelectsR D S ρ (fuelR D) N) ∨
  (∃ M ∈ outsideRules D, M.pred = p ∧ M.sign = sign ∧ StrictSelectsX D S ρ (fuelR D) M) ∨
  (sign = false ∧ ruleReading D = true ∧ rightPermission D p = true ∧ (aimedF D p).denote S ρ)

def BlockedX (X : SoftNode) : Prop :=
  StrictDecidesR D S ρ X.pred true ∨ StrictDecidesR D S ρ X.pred false ∨
    (X.sign = true ∧ ∃ m, dualPerm (correlate D) X.pred = some m ∧ StrictDecidesR D S ρ m false) ∨
    (X.sign = false ∧ ∃ r, dualOblig (correlate D) X.pred = some r ∧ StrictDecidesR D S ρ r true)

def EligibleX (X : SoftNode) : Prop := X.mode = .default ∧ LiveX D S ρ X ∧ ¬ BlockedX D S ρ X

def DomWithX (eff : SoftNode → Prop) (X : SoftNode) : Prop :=
  ∃ M ∈ directNodes D, Incompatible (correlate D) M X = true ∧ M.mode = .default ∧
    Comparable (correlate D) M X = true ∧
    ((higher (correlate D) M X = true ∧ eff M ∧
        ((correlate D).soft.outranking = .holistic →
          ¬ OutweighsD (correlate D) S ρ (act (correlate D) X) (rk X) (rk M))) ∨
     ((correlate D).soft.outranking = .holistic ∧ higher (correlate D) X M = true ∧ EligibleX D S ρ M ∧
        OutweighsD (correlate D) S ρ (act (correlate D) X) (rk M) (rk X)))

def EffX : Nat → SoftNode → Prop
  | 0, X => EligibleX D S ρ X
  | g + 1, X => EligibleX D S ρ X ∧ ¬ DomWithX D S ρ (EffX g) X

def DominatedX (g : Nat) (X : SoftNode) : Prop := DomWithX D S ρ (EffX D S ρ g) X

def AppliesX (X : SoftNode) : Prop :=
  match X.mode with
  | .strict => LiveX D S ρ X
  | .default => EffX D S ρ (rankFuel (correlate D)) X

def YieldsX : Nat → SoftNode → Prop
  | 0, X => AppliesX D S ρ X
  | f + 1, X => AppliesX D S ρ X ∨ BarredX D S ρ X ∨ ∃ C ∈ childrenIn (directNodes D) X, YieldsX f C

def SelectsX (f : Nat) (X : SoftNode) : Prop :=
  AppliesX D S ρ X ∧ ¬ BarredX D S ρ X ∧ ¬ ∃ C ∈ childrenIn (directNodes D) X, YieldsX D S ρ f C

def BlockedR (N : Line) : Prop := BlockedX D S ρ (nodeOf D N)
def EligibleR (N : Line) : Prop := EligibleX D S ρ (nodeOf D N)
def EffR (g : Nat) (N : Line) : Prop := EffX D S ρ g (nodeOf D N)
def DominatedR (g : Nat) (N : Line) : Prop := DominatedX D S ρ g (nodeOf D N)
def AppliesR (N : Line) : Prop := AppliesX D S ρ (nodeOf D N)
def YieldsR (f : Nat) (N : Line) : Prop := YieldsX D S ρ f (nodeOf D N)
def SelectsR (f : Nat) (N : Line) : Prop := SelectsX D S ρ f (nodeOf D N)

/-- Some rule of the sign on `p` selects, or (sign `false`) the bar applies. -/
def DecidesR (p : String) (sign : Bool) : Prop :=
  (∃ X ∈ directNodes D, X.pred = p ∧ X.sign = sign ∧ SelectsX D S ρ (fuelR D) X) ∨
  (sign = false ∧ ruleReading D = true ∧ rightPermission D p = true ∧ (aimedF D p).denote S ρ)

end Direct

noncomputable def ValueRight (D : RightsDoc) (r : Regulated) (S : VE.Structure.{u}) (vs : List S.Carrier) :
    Option Bool :=
  catalaValue (DecidesR D S (tupleVal vs) r.name true) (DecidesR D S (tupleVal vs) r.name false) r.allowByDefault

/-! ## The nodes of `T″` -/

section Nodes
variable (D : RightsDoc)

theorem mem_correlate_nodes (X : SoftNode) :
    X ∈ (correlate D).T.nodes ↔ X ∈ directNodes D ∨ X ∈ barNodes D := by
  simp only [correlate, directNodes, lineNodes, List.mem_append]

theorem mem_barNodes (B : SoftNode) :
    B ∈ barNodes D ↔ ruleReading D = true ∧ ∃ m, rightPermission D m = true ∧ B = barNode D m := by
  unfold barNodes
  split
  · rename_i hr
    simp only [List.mem_map, mem_barPreds, hr, true_and]
    constructor
    · rintro ⟨m, hm, rfl⟩; exact ⟨m, hm, rfl⟩
    · rintro ⟨m, hm, rfl⟩; exact ⟨m, hm, rfl⟩
  · rename_i hr
    simp [hr]

theorem barNode_mem (hb : ruleReading D = true) {m : String} (hm : rightPermission D m = true) :
    barNode D m ∈ barNodes D := (mem_barNodes D _).mpr ⟨hb, m, hm, rfl⟩

theorem lineNode_mem {R : String} {N : Line} (hN : (R, N) ∈ linesOf D) : nodeOf D N ∈ lineNodes D :=
  List.mem_map.mpr ⟨(R, N), hN, rfl⟩

theorem lineNode_direct {R : String} {N : Line} (hN : (R, N) ∈ linesOf D) : nodeOf D N ∈ directNodes D :=
  List.mem_append_left _ (lineNode_mem D hN)

theorem lineNode_correlate {R : String} {N : Line} (hN : (R, N) ∈ linesOf D) :
    nodeOf D N ∈ (correlate D).T.nodes :=
  (mem_correlate_nodes D _).mpr (Or.inl (lineNode_direct D hN))

theorem bar_mode {B : SoftNode} (hB : B ∈ barNodes D) : B.mode = .strict := by
  obtain ⟨_, m, _, rfl⟩ := (mem_barNodes D B).mp hB
  rfl

theorem mem_children_correlate (X C' : SoftNode) :
    C' ∈ VE.SoftNorms.children (correlate D) X ↔
      C' ∈ childrenIn (directNodes D) X ∨ (C' ∈ barNodes D ∧ C'.pred = X.pred ∧ X.name ∈ C'.over) := by
  simp only [VE.SoftNorms.children, VE.SoftNorms.mem_childrenIn_iff, mem_correlate_nodes]
  constructor
  · rintro ⟨h | h, hp, ho⟩
    · exact Or.inl ⟨h, hp, ho⟩
    · exact Or.inr ⟨h, hp, ho⟩
  · rintro (⟨h, hp, ho⟩ | ⟨h, hp, ho⟩)
    · exact ⟨Or.inl h, hp, ho⟩
    · exact ⟨Or.inr h, hp, ho⟩

theorem mem_childrenIn_direct {X C' : SoftNode} (h : C' ∈ childrenIn (directNodes D) X) : C' ∈ directNodes D :=
  (VE.SoftNorms.mem_childrenIn_iff.mp h).1

end Nodes

section Bars
variable {D : RightsDoc} (hv : RightsValid D) (S : VE.Structure.{u}) (ρ : VE.Valuation S)

theorem live_bar (m : String) : LiveD (correlate D) S ρ (barNode D m) ↔ (aimedF D m).denote S ρ := by
  simp [LiveD, barNode, VE.SoftNorms.switchF, VE.SoftNorms.switchIn, anyF, VE.Formula.denote]

include hv

theorem not_mem_children_bar {B : SoftNode} (hB : B ∈ barNodes D) (C' : SoftNode) :
    C' ∉ VE.SoftNorms.children (correlate D) B := by
  intro hC
  obtain ⟨hC, _, ho⟩ := VE.SoftNorms.mem_childrenIn_iff.mp hC
  exact hv.barOver C' hC B hB ho

theorem strictYields_bar {B : SoftNode} (hB : B ∈ barNodes D) (f : Nat) :
    StrictYieldsD (correlate D) S ρ f B ↔ (aimedF D B.pred).denote S ρ := by
  obtain ⟨_, m, _, rfl⟩ := (mem_barNodes D B).mp hB
  cases f with
  | zero => simp only [StrictYieldsD, live_bar S ρ m]; exact ⟨fun h => h.2, fun h => ⟨rfl, h⟩⟩
  | succ f =>
    simp only [StrictYieldsD, live_bar S ρ m]
    constructor
    · rintro (h | ⟨C', hC, _⟩)
      · exact h.2
      · exact absurd hC (not_mem_children_bar hv hB C')
    · intro h; exact Or.inl ⟨rfl, h⟩

theorem strictSelects_bar {B : SoftNode} (hB : B ∈ barNodes D) (f : Nat) :
    StrictSelectsD (correlate D) S ρ f B ↔ (aimedF D B.pred).denote S ρ := by
  obtain ⟨_, m, _, rfl⟩ := (mem_barNodes D B).mp hB
  simp only [StrictSelectsD, live_bar S ρ m]
  constructor
  · exact fun h => h.2.1
  · intro h
    exact ⟨rfl, h, fun ⟨C', hC, _⟩ => not_mem_children_bar hv hB C' hC⟩

omit hv in
theorem applies_bar {B : SoftNode} (hB : B ∈ barNodes D) :
    AppliesSoftD (correlate D) S ρ B ↔ (aimedF D B.pred).denote S ρ := by
  obtain ⟨_, m, _, rfl⟩ := (mem_barNodes D B).mp hB
  simp only [AppliesSoftD, barNode]
  exact live_bar S ρ m

theorem yields_bar {B : SoftNode} (hB : B ∈ barNodes D) (f : Nat) :
    YieldsSoftD (correlate D) S ρ f B ↔ (aimedF D B.pred).denote S ρ := by
  cases f with
  | zero => exact applies_bar S ρ hB
  | succ f =>
    simp only [YieldsSoftD, applies_bar S ρ hB]
    constructor
    · rintro (h | ⟨C', hC, _⟩)
      · exact h
      · exact absurd hC (not_mem_children_bar hv hB C')
    · exact Or.inl

theorem selects_bar {B : SoftNode} (hB : B ∈ barNodes D) (f : Nat) :
    SelectsSoftD (correlate D) S ρ f B ↔ (aimedF D B.pred).denote S ρ := by
  simp only [SelectsSoftD, applies_bar S ρ hB]
  exact ⟨fun h => h.1, fun h => ⟨h, fun ⟨C', hC, _⟩ => not_mem_children_bar hv hB C' hC⟩⟩

/-- A bar is a child of a rule of `T″` exactly when the rule is a right-derived positive line
node on a right-derived permission predicate (rule reading). -/
theorem exists_child_split {X : SoftNode} (hX : X ∈ directNodes D) (Y : SoftNode → Prop)
    (hY : ∀ B ∈ barNodes D, Y B ↔ (aimedF D B.pred).denote S ρ) :
    (∃ C' ∈ VE.SoftNorms.children (correlate D) X, Y C') ↔
      BarredX D S ρ X ∨ ∃ C' ∈ childrenIn (directNodes D) X, Y C' := by
  have hnames := (VE.SoftNorms.softValid_of_wellFormed _ hv.wfSoft).names
  constructor
  · rintro ⟨C', hC, hy⟩
    rcases (mem_children_correlate D X C').mp hC with hC | ⟨hB, hp, ho⟩
    · exact Or.inr ⟨C', hC, hy⟩
    · left
      obtain ⟨hr, m, hm, rfl⟩ := (mem_barNodes D _).mp hB
      simp only [barNode] at hp ho
      simp only [posLineNames, List.mem_map, List.mem_filter, Bool.and_eq_true, beq_iff_eq] at ho
      obtain ⟨Y', ⟨hY', hYp, hYs⟩, hYn⟩ := ho
      have hYc : Y' ∈ (correlate D).T.nodes :=
        (mem_correlate_nodes D _).mpr (Or.inl (List.mem_append_left _ hY'))
      have hXc : X ∈ (correlate D).T.nodes := (mem_correlate_nodes D _).mpr (Or.inl hX)
      have he : Y' = X := VE.SoftNorms.eq_of_key (fun N : SoftNode => N.name) hnames hYc hXc hYn
      subst he
      have hy' := (hY _ hB).mp hy
      simp only [barNode] at hy'
      rw [← hYp] at hm
      rw [← hYp] at hy'
      exact ⟨hr, hYs, hY', hm, hy'⟩
  · rintro (⟨hr, hs, hl, hm, ha⟩ | ⟨C', hC, hy⟩)
    · have hB := barNode_mem D hr hm
      refine ⟨barNode D X.pred, (mem_children_correlate D X _).mpr (Or.inr ⟨hB, rfl, ?_⟩), (hY _ hB).mpr ha⟩
      simp only [barNode, posLineNames, List.mem_map, List.mem_filter, Bool.and_eq_true, beq_iff_eq]
      exact ⟨X, ⟨hl, rfl, hs⟩, rfl⟩
    · exact ⟨C', (mem_children_correlate D X C').mpr (Or.inl hC), hy⟩

/-! ## Faithfulness, rule by rule -/

theorem strictYields_eq : ∀ (f : Nat) (X : SoftNode), X ∈ directNodes D →
    (StrictYieldsD (correlate D) S ρ f X ↔ StrictYieldsX D S ρ f X)
  | 0, X, _ => Iff.rfl
  | f + 1, X, hX => by
    simp only [StrictYieldsD, StrictYieldsX]
    rw [exists_child_split hv S ρ hX _ (fun B hB => strictYields_bar hv S ρ hB f)]
    apply or_congr_right
    apply or_congr_right
    constructor
    · rintro ⟨C', hC, hy⟩
      exact ⟨C', hC, (strictYields_eq f C' (mem_childrenIn_direct D hC)).mp hy⟩
    · rintro ⟨C', hC, hy⟩
      exact ⟨C', hC, (strictYields_eq f C' (mem_childrenIn_direct D hC)).mpr hy⟩

theorem strictSelects_eq (f : Nat) {X : SoftNode} (hX : X ∈ directNodes D) :
    StrictSelectsD (correlate D) S ρ f X ↔ StrictSelectsX D S ρ f X := by
  simp only [StrictSelectsD, StrictSelectsX]
  rw [exists_child_split hv S ρ hX _ (fun B hB => strictYields_bar hv S ρ hB f)]
  have : (∃ C' ∈ childrenIn (directNodes D) X, StrictYieldsD (correlate D) S ρ f C') ↔
      ∃ C' ∈ childrenIn (directNodes D) X, StrictYieldsX D S ρ f C' := by
    constructor
    · rintro ⟨C', hC, hy⟩
      exact ⟨C', hC, (strictYields_eq hv S ρ f C' (mem_childrenIn_direct D hC)).mp hy⟩
    · rintro ⟨C', hC, hy⟩
      exact ⟨C', hC, (strictYields_eq hv S ρ f C' (mem_childrenIn_direct D hC)).mpr hy⟩
  rw [this, not_or]
  rfl

theorem strictDecides_eq (p : String) (sign : Bool) :
    StrictDecidesD (correlate D) S ρ p sign ↔ StrictDecidesR D S ρ p sign := by
  unfold StrictDecidesD StrictDecidesR
  constructor
  · rintro ⟨X, hX, hs, hsel⟩
    obtain ⟨hX, hp⟩ := VE.SoftNorms.mem_rulesOn.mp hX
    rcases (mem_correlate_nodes D X).mp hX with hd | hb
    · have hsel' := (strictSelects_eq hv S ρ _ hd).mp hsel
      rcases List.mem_append.mp hd with hl | ho
      · left
        obtain ⟨⟨R, N⟩, hN, rfl⟩ := List.mem_map.mp hl
        exact ⟨N, List.mem_map.mpr ⟨(R, N), hN, rfl⟩, hp, hs, hsel'⟩
      · exact Or.inr (Or.inl ⟨X, ho, hp, hs, hsel'⟩)
    · have ha := (strictSelects_bar hv S ρ hb _).mp hsel
      obtain ⟨hr, m, hm, rfl⟩ := (mem_barNodes D X).mp hb
      simp only [barNode] at hp hs ha
      subst hp
      exact Or.inr (Or.inr ⟨hs.symm, hr, hm, ha⟩)
  · rintro (⟨N, hN, hp, hs, hsel⟩ | ⟨M, hM, hp, hs, hsel⟩ | ⟨rfl, hr, hm, ha⟩)
    · obtain ⟨⟨R, N'⟩, hN', rfl⟩ := List.mem_map.mp hN
      refine ⟨nodeOf D N', VE.SoftNorms.mem_rulesOn.mpr ⟨lineNode_correlate D hN', hp⟩, hs, ?_⟩
      exact (strictSelects_eq hv S ρ _ (lineNode_direct D hN')).mpr hsel
    · have hd : M ∈ directNodes D := List.mem_append_right _ hM
      exact ⟨M, VE.SoftNorms.mem_rulesOn.mpr ⟨(mem_correlate_nodes D M).mpr (Or.inl hd), hp⟩, hs,
        (strictSelects_eq hv S ρ _ hd).mpr hsel⟩
    · have hB := barNode_mem D hr hm
      exact ⟨barNode D p, VE.SoftNorms.mem_rulesOn.mpr ⟨(mem_correlate_nodes D _).mpr (Or.inr hB), rfl⟩, rfl,
        (strictSelects_bar hv S ρ hB _).mpr ha⟩

theorem blocked_eq (X : SoftNode) : BlockedD (correlate D) S ρ X ↔ BlockedX D S ρ X := by
  simp only [BlockedD, BlockedX, strictDecides_eq hv S ρ]

theorem eligible_eq (X : SoftNode) : EligibleD (correlate D) S ρ X ↔ EligibleX D S ρ X := by
  simp only [EligibleD, EligibleX, blocked_eq hv S ρ, LiveX]

theorem domWith_eq (eff : SoftNode → Prop) (eff' : SoftNode → Prop)
    (he : ∀ M ∈ directNodes D, eff M ↔ eff' M) (X : SoftNode) :
    DomWithD (correlate D) S ρ eff X ↔ DomWithX D S ρ eff' X := by
  unfold DomWithD DomWithX
  constructor
  · rintro ⟨M, hM, hi, hd, hc, h⟩
    have hMd : M ∈ directNodes D := by
      rcases (mem_correlate_nodes D M).mp hM with h | h
      · exact h
      · rw [bar_mode D h] at hd; cases hd
    refine ⟨M, hMd, hi, hd, hc, ?_⟩
    rcases h with ⟨hh, hef, ho⟩ | ⟨hol, hh, hel, ho⟩
    · exact Or.inl ⟨hh, (he M hMd).mp hef, ho⟩
    · exact Or.inr ⟨hol, hh, (eligible_eq hv S ρ M).mp hel, ho⟩
  · rintro ⟨M, hM, hi, hd, hc, h⟩
    refine ⟨M, (mem_correlate_nodes D M).mpr (Or.inl hM), hi, hd, hc, ?_⟩
    rcases h with ⟨hh, hef, ho⟩ | ⟨hol, hh, hel, ho⟩
    · exact Or.inl ⟨hh, (he M hM).mpr hef, ho⟩
    · exact Or.inr ⟨hol, hh, (eligible_eq hv S ρ M).mpr hel, ho⟩

theorem eff_eq : ∀ (g : Nat) (X : SoftNode), EffD (correlate D) S ρ g X ↔ EffX D S ρ g X
  | 0, X => eligible_eq hv S ρ X
  | g + 1, X => by
    simp only [EffD, EffX, eligible_eq hv S ρ]
    rw [domWith_eq hv S ρ _ (EffX D S ρ g) (fun M _ => eff_eq g M)]

theorem dominated_eq (g : Nat) (X : SoftNode) :
    VE.SoftNorms.DominatedD (correlate D) S ρ g X ↔ DominatedX D S ρ g X :=
  domWith_eq hv S ρ _ _ (fun M _ => eff_eq hv S ρ g M) X

theorem applies_eq (X : SoftNode) : AppliesSoftD (correlate D) S ρ X ↔ AppliesX D S ρ X := by
  unfold AppliesSoftD AppliesX
  cases X.mode
  · rfl
  · exact eff_eq hv S ρ _ X

theorem yields_eq : ∀ (f : Nat) (X : SoftNode), X ∈ directNodes D →
    (YieldsSoftD (correlate D) S ρ f X ↔ YieldsX D S ρ f X)
  | 0, X, _ => applies_eq hv S ρ X
  | f + 1, X, hX => by
    simp only [YieldsSoftD, YieldsX, applies_eq hv S ρ]
    rw [exists_child_split hv S ρ hX _ (fun B hB => yields_bar hv S ρ hB f)]
    apply or_congr_right
    apply or_congr_right
    constructor
    · rintro ⟨C', hC, hy⟩
      exact ⟨C', hC, (yields_eq f C' (mem_childrenIn_direct D hC)).mp hy⟩
    · rintro ⟨C', hC, hy⟩
      exact ⟨C', hC, (yields_eq f C' (mem_childrenIn_direct D hC)).mpr hy⟩

theorem selects_eq (f : Nat) {X : SoftNode} (hX : X ∈ directNodes D) :
    SelectsSoftD (correlate D) S ρ f X ↔ SelectsX D S ρ f X := by
  simp only [SelectsSoftD, SelectsX, applies_eq hv S ρ]
  rw [exists_child_split hv S ρ hX _ (fun B hB => yields_bar hv S ρ hB f)]
  have : (∃ C' ∈ childrenIn (directNodes D) X, YieldsSoftD (correlate D) S ρ f C') ↔
      ∃ C' ∈ childrenIn (directNodes D) X, YieldsX D S ρ f C' := by
    constructor
    · rintro ⟨C', hC, hy⟩
      exact ⟨C', hC, (yields_eq hv S ρ f C' (mem_childrenIn_direct D hC)).mp hy⟩
    · rintro ⟨C', hC, hy⟩
      exact ⟨C', hC, (yields_eq hv S ρ f C' (mem_childrenIn_direct D hC)).mpr hy⟩
  rw [this, not_or]

theorem decides_eq (p : String) (sign : Bool) :
    DecidesSoftD (correlate D) S ρ p sign ↔ DecidesR D S ρ p sign := by
  unfold DecidesSoftD DecidesR
  constructor
  · rintro ⟨X, hX, hs, hsel⟩
    obtain ⟨hX, hp⟩ := VE.SoftNorms.mem_rulesOn.mp hX
    rcases (mem_correlate_nodes D X).mp hX with hd | hb
    · exact Or.inl ⟨X, hd, hp, hs, (selects_eq hv S ρ _ hd).mp hsel⟩
    · have ha := (selects_bar hv S ρ hb _).mp hsel
      obtain ⟨hr, m, hm, rfl⟩ := (mem_barNodes D X).mp hb
      simp only [barNode] at hp hs ha
      subst hp
      exact Or.inr ⟨hs.symm, hr, hm, ha⟩
  · rintro (⟨X, hX, hp, hs, hsel⟩ | ⟨rfl, hr, hm, ha⟩)
    · exact ⟨X, VE.SoftNorms.mem_rulesOn.mpr ⟨(mem_correlate_nodes D X).mpr (Or.inl hX), hp⟩, hs,
        (selects_eq hv S ρ _ hX).mpr hsel⟩
    · have hB := barNode_mem D hr hm
      exact ⟨barNode D p, VE.SoftNorms.mem_rulesOn.mpr ⟨(mem_correlate_nodes D _).mpr (Or.inr hB), rfl⟩, rfl,
        (selects_bar hv S ρ hB _).mpr ha⟩

end Bars

/-! ## 9.2: the generated formulas denote their direct counterparts -/

theorem limPackList_denote (D : RightsDoc) (N : Line) (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    (∃ U ∈ limPackList D N, U.denote S ρ) ↔ (limPack D N).denote S ρ := by
  unfold limPackList
  split
  · rename_i h
    simp [limPack, h, anyF, VE.Formula.denote]
  · simp

theorem liveR_denote (D : RightsDoc) (N : Line) (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    (VE.SoftNorms.liveF (correlate D) (nodeOf D N)).denote S ρ ↔ LiveR D S ρ N := by
  rw [VE.SoftNorms.live_denote]
  unfold LiveD LiveR
  have hc : (∃ U ∈ (nodeOf D N).carveOuts, U.denote S ρ) ↔
      (∃ U ∈ N.node.carveOuts, U.denote S ρ) ∨ (limPack D N).denote S ρ := by
    rw [← limPackList_denote]
    simp only [nodeOf, List.mem_append]
    constructor
    · rintro ⟨U, hU | hU, h⟩
      · exact Or.inl ⟨U, hU, h⟩
      · exact Or.inr ⟨U, hU, h⟩
    · rintro (⟨U, hU, h⟩ | ⟨U, hU, h⟩)
      · exact ⟨U, Or.inl hU, h⟩
      · exact ⟨U, Or.inr hU, h⟩
  rw [hc, not_or]
  simp only [nodeOf, ownGuard, and_assoc]

theorem bar_denote (D : RightsDoc) (h : WellFormedRights D = true) (hb : ruleReading D = true) (m : String)
    (hm : rightPermission D m = true) (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    StrictSelectsD (correlate D) S ρ (fuelR D) (barNode D m) ↔ (aimedF D m).denote S ρ :=
  strictSelects_bar (rightsValid_of_wellFormed D h) S ρ (barNode_mem D hb hm) _

theorem strictDecidesR_denote (D : RightsDoc) (h : WellFormedRights D = true) (p : String) (sign : Bool)
    (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    StrictDecidesD (correlate D) S ρ p sign ↔ StrictDecidesR D S ρ p sign :=
  strictDecides_eq (rightsValid_of_wellFormed D h) S ρ p sign

/-- 4.3: `ValueSoft` on `T″` is `ValueRight` on `D`. -/
theorem correlate_faithful (D : RightsDoc) (h : WellFormedRights D = true) (r : Regulated)
    (_hr : r ∈ (correlate D).T.regulated) (S : VE.Structure.{u}) (vs : List S.Carrier) :
    ValueSoft (correlate D) r S vs = ValueRight D r S vs := by
  have hv := rightsValid_of_wellFormed D h
  unfold ValueSoft ValueRight
  rw [propext (decides_eq hv S (tupleVal vs) r.name true), propext (decides_eq hv S (tupleVal vs) r.name false)]

/-- W1's `Value` on `T″′` is `ValueSoft` on `T″` is `ValueRight` on `D`. -/
theorem correlate_value (D : RightsDoc) (h : WellFormedRights D = true) (r : Regulated)
    (hr : r ∈ (correlate D).T.regulated) (S : VE.Structure.{u}) (vs : List S.Carrier) :
    VE.Norms.Value (VE.SoftNorms.soften (correlate D)).T r S vs = ValueRight D r S vs :=
  (VE.SoftNorms.soften_faithful (correlate D) (correlate_wellFormed D h) r hr S vs).trans
    (correlate_faithful D h r hr S vs)

end VE.Rights
