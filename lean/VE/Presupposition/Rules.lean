import VE.Presupposition.Reading
import VE.Norms.Elaborate
import VE.NormDefaults.Semantics
import VE.Discourse.Descriptions

/-! # Presuppositions at a rule act (docs/spec/presupposition.md 4.5)

`ruleGoal` is the goal of a trigger in a rule's act: for every tuple of the regulated
predicate's sorts, if the rule applies then `pre` holds. `conditionRule` adds a condition to
the guard of the rules named `n` and changes nothing else. Where every rule named `n` gives the
condition when it applies, conditioning changes no rule's decision (`rule_collapse_decides`); a
valid or certified goal gives that at every typed tuple (`rule_collapse_typed`,
`rule_collapse_certified`). -/
namespace VE.Presupposition
universe u

def ruleGoal (r : VE.Norms.Regulated) (N : VE.Norms.Node) (pre : VE.Formula) : VE.Formula :=
  VE.Norms.bindAll r.sorts (.implies (VE.Norms.applies N) pre)

def conditionNode (N : VE.Norms.Node) (c : VE.Formula) : VE.Norms.Node := { N with guard := .and N.guard c }

def conditionRule (T : VE.Norms.Tree) (n : String) (c : VE.Formula) : VE.Norms.Tree :=
  { T with nodes := T.nodes.map (fun M => if M.name == n then conditionNode M c else M) }

theorem condition_applies (N : VE.Norms.Node) (c : VE.Formula) (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    (VE.Norms.applies (conditionNode N c)).denote S ρ ↔ (VE.Norms.applies N).denote S ρ ∧ c.denote S ρ :=
  ⟨fun ⟨⟨g, hc⟩, n⟩ => ⟨⟨g, n⟩, hc⟩, fun ⟨⟨g, n⟩, hc⟩ => ⟨⟨g, hc⟩, n⟩⟩

theorem conditionRule_shape (T : VE.Norms.Tree) (n : String) (c : VE.Formula) :
    (conditionRule T n c).regulated = T.regulated ∧ (conditionRule T n c).definitions = T.definitions ∧
    (conditionRule T n c).nodes.map (fun M => (M.name, M.pred, M.sign, M.carveOuts, M.over)) =
      T.nodes.map (fun M => (M.name, M.pred, M.sign, M.carveOuts, M.over)) := by
  refine ⟨rfl, rfl, ?_⟩
  simp only [conditionRule, List.map_map]
  apply List.map_congr_left
  intro M _
  simp only [Function.comp]
  split <;> rfl

section Map
variable {T T' : VE.Norms.Tree} {g : VE.Norms.Node → VE.Norms.Node} {S : VE.Structure.{u}} {ρ : VE.Valuation S}

/-- A map of the nodes that keeps names, predicates and precedence keeps which exceptions yield. -/
theorem exists_child_map (hT : T'.nodes = T.nodes.map g) (hn : ∀ M, (g M).name = M.name)
    (hp : ∀ M, (g M).pred = M.pred) (ho : ∀ M, (g M).over = M.over) (f : Nat) (N : VE.Norms.Node)
    (ih : ∀ C ∈ T.nodes, VE.Norms.YieldsD T' S ρ f (g C) ↔ VE.Norms.YieldsD T S ρ f C) :
    (∃ C ∈ VE.Norms.children T' (g N), VE.Norms.YieldsD T' S ρ f C) ↔
      ∃ C ∈ VE.Norms.children T N, VE.Norms.YieldsD T S ρ f C := by
  constructor
  · rintro ⟨C', hC', hy⟩
    obtain ⟨hm, hpc, hoc⟩ := VE.Norms.mem_children_iff.mp hC'
    rw [hT] at hm
    obtain ⟨C, hC, rfl⟩ := List.mem_map.mp hm
    rw [hp, hp] at hpc
    rw [hn, ho] at hoc
    exact ⟨C, VE.Norms.mem_children_iff.mpr ⟨hC, hpc, hoc⟩, (ih C hC).mp hy⟩
  · rintro ⟨C, hC', hy⟩
    obtain ⟨hC, hpc, hoc⟩ := VE.Norms.mem_children_iff.mp hC'
    refine ⟨g C, VE.Norms.mem_children_iff.mpr ⟨hT ▸ List.mem_map_of_mem hC, ?_, ?_⟩, (ih C hC).mpr hy⟩
    · rw [hp, hp, hpc]
    · rw [hn, ho]; exact hoc

/-- And if each node's applying is kept too, so is what each subtree yields. -/
theorem yieldsD_map (hT : T'.nodes = T.nodes.map g) (hn : ∀ M, (g M).name = M.name)
    (hp : ∀ M, (g M).pred = M.pred) (ho : ∀ M, (g M).over = M.over)
    (ha : ∀ M ∈ T.nodes, VE.Norms.AppliesD S ρ (g M) ↔ VE.Norms.AppliesD S ρ M) :
    ∀ (f : Nat) (N : VE.Norms.Node), N ∈ T.nodes →
      (VE.Norms.YieldsD T' S ρ f (g N) ↔ VE.Norms.YieldsD T S ρ f N)
  | 0, N, hN => ha N hN
  | f + 1, N, hN => or_congr (ha N hN) (exists_child_map hT hn hp ho f N
      fun C hC => yieldsD_map hT hn hp ho ha f C hC)

/-- And so is what each predicate's rules decide. -/
theorem decidesD_map (hT : T'.nodes = T.nodes.map g) (hn : ∀ M, (g M).name = M.name)
    (hp : ∀ M, (g M).pred = M.pred) (hs : ∀ M, (g M).sign = M.sign) (ho : ∀ M, (g M).over = M.over)
    (ha : ∀ M ∈ T.nodes, VE.Norms.AppliesD S ρ (g M) ↔ VE.Norms.AppliesD S ρ M)
    (p : String) (sign : Bool) :
    VE.Norms.DecidesD T' S ρ p sign ↔ VE.Norms.DecidesD T S ρ p sign := by
  have hfuel : VE.Norms.fuel T' = VE.Norms.fuel T := by simp [VE.Norms.fuel, hT]
  have hsel : ∀ N ∈ T.nodes, VE.Norms.SelectsD T' S ρ (VE.Norms.fuel T') (g N) ↔
      VE.Norms.SelectsD T S ρ (VE.Norms.fuel T) N := fun N hN => by
    rw [hfuel]
    exact and_congr (ha N hN) (not_congr (exists_child_map hT hn hp ho _ N
      fun C hC => yieldsD_map hT hn hp ho ha _ C hC))
  constructor
  · rintro ⟨N', hN', hsign, hy⟩
    obtain ⟨hm, hpN⟩ := List.mem_filter.mp hN'
    rw [hT] at hm
    obtain ⟨N, hN, rfl⟩ := List.mem_map.mp hm
    rw [hp] at hpN
    exact ⟨N, List.mem_filter.mpr ⟨hN, hpN⟩, hs N ▸ hsign, (hsel N hN).mp hy⟩
  · rintro ⟨N, hN', hsign, hy⟩
    obtain ⟨hN, hpN⟩ := List.mem_filter.mp hN'
    exact ⟨g N, List.mem_filter.mpr ⟨hT ▸ List.mem_map_of_mem hN, by rw [hp]; exact hpN⟩,
      (hs N).trans hsign, (hsel N hN).mpr hy⟩

end Map

theorem rule_collapse_decides (T : VE.Norms.Tree) (n : String) (c : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (h : ∀ M ∈ T.nodes, M.name = n → (VE.Norms.applies M).denote S ρ → c.denote S ρ)
    (p : String) (sign : Bool) :
    (VE.Norms.decides (conditionRule T n c) p sign).denote S ρ ↔ (VE.Norms.decides T p sign).denote S ρ := by
  rw [VE.Norms.decides_denote, VE.Norms.decides_denote]
  refine decidesD_map (g := fun M => if M.name == n then conditionNode M c else M) rfl
    (fun M => by dsimp only; split <;> rfl) (fun M => by dsimp only; split <;> rfl)
    (fun M => by dsimp only; split <;> rfl) (fun M => by dsimp only; split <;> rfl) ?_ p sign
  intro M hM
  rw [← VE.Norms.applies_denote, ← VE.Norms.applies_denote]
  dsimp only
  split
  · rename_i hn
    exact (condition_applies M c S ρ).trans
      (and_iff_left_of_imp (h M hM (by simpa using hn)))
  · exact Iff.rfl

theorem rule_collapse_typed (T : VE.Norms.Tree) (r : VE.Norms.Regulated) (N : VE.Norms.Node) (pre : VE.Formula)
    (S : VE.Structure.{u}) (hname : ∀ M ∈ T.nodes, M.name = N.name → M = N)
    (hgoal : (ruleGoal r N pre).denote S []) (vs : List S.Carrier) (hvs : VE.TupleTyped S r.sorts vs)
    (p : String) (sign : Bool) :
    (VE.Norms.decides (conditionRule T N.name pre) p sign).denote S (VE.Norms.tupleVal vs) ↔
      (VE.Norms.decides T p sign).denote S (VE.Norms.tupleVal vs) :=
  rule_collapse_decides T N.name pre S _ (fun M hM hn => by
    rw [hname M hM hn]
    exact (VE.Norms.bindAll_denote_nil S r.sorts _).mp hgoal vs hvs) p sign

theorem rule_collapse_certified (E : VE.Environment) (prem : List VE.Formula) (T : VE.Norms.Tree)
    (r : VE.Norms.Regulated) (N : VE.Norms.Node) (pre : VE.Formula) (cert : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate E prem (ruleGoal r N pre) cert = true)
    (hname : ∀ M ∈ T.nodes, M.name = N.name → M = N)
    (S : VE.Structure.{u}) (hS : S.Admissible E) (hprem : VE.Norms.Sat S prem)
    (vs : List S.Carrier) (hvs : VE.TupleTyped S r.sorts vs) (p : String) (sign : Bool) :
    (VE.Norms.decides (conditionRule T N.name pre) p sign).denote S (VE.Norms.tupleVal vs) ↔
      (VE.Norms.decides T p sign).denote S (VE.Norms.tupleVal vs) :=
  rule_collapse_typed T r N pre S hname (VE.Tableau.checkCertificate_sound.{u} E prem _ cert acc S hS hprem)
    vs hvs p sign

theorem conditioned_contributes_nothing (T : VE.Norms.Tree) (f : Nat) (N : VE.Norms.Node) (c : VE.Formula)
    (S : VE.Structure.{u}) (ρ : VE.Valuation S) (h : ¬ c.denote S ρ) :
    ¬ (VE.Norms.selects T f (conditionNode N c)).denote S ρ :=
  fun hs => h ((condition_applies N c S ρ).mp hs.1).2

theorem unsaid_iff (P N : Prop) : VE.NormDefaults.value3 P N .unspecified = .unsaid ↔ ¬ P ∧ ¬ N := by
  by_cases hP : P <;> by_cases hN : N <;> simp [VE.NormDefaults.value3, hP, hN]

theorem source_identity_entails (E : VE.Environment) (pre : VE.Formula) (hpre : pre.WellFormed E [])
    (S : VE.Structure.{u}) (h : pre.denote S []) (r : VE.Norms.Regulated) (N : VE.Norms.Node) :
    (ruleGoal r N pre).denote S [] :=
  (VE.Norms.bindAll_denote_nil S r.sorts _).mpr fun _ _ _ =>
    (VE.Discourse.denote_prefix pre [] _ _ hpre (by simp)).mp h

end VE.Presupposition
