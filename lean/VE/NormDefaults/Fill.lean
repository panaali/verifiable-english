import VE.NormDefaults.Check
import VE.NormDefaults.Dag
import VE.Norms.Conflict

/-! The rule structure of `fill U` (docs/spec/norm-defaults.md 2.3 and 7):
`fill_conservative`, `fill_selects_author`, `fill_decides` and
`fill_local_conflict`.

`F_p` is the parent of every root on `p` and has no parent itself; no author rule
gains a child, so every author rule's `applies`, `yields` and `selects` is
unchanged (`fill_selects_author`). The only difference in fuel is absorbed by
`yields_stable`: in an acyclic precedence DAG a rule's subtree is decided within
as many steps as there are rules below it. `yields_iff_selects` is "a subtree
yields iff one of its rules selects" (the lowest applying rule selects). -/
namespace VE.NormDefaults
open VE.Norms VE.Route
universe u

theorem unsaidName_inj {a b : String} (h : unsaidName a = unsaidName b) : a = b :=
  String.ext (List.append_cancel_left (by
    rw [← String.data_append, ← String.data_append]; exact congrArg String.data h))

/-! ## The facts `WellFormedU` gives -/

structure UValid (U : UDoc) : Prop where
  wf : WellFormed U.D = true
  ok : CheckOK U.D
  valid : Valid U.D
  nodup : U.unspec.Nodup
  declared : ∀ p ∈ U.unspec, ∃ r ∈ U.D.T.regulated, r.name = p ∧ r.allowByDefault = false
  freshPred : ∀ p ∈ U.unspec, U.D.E.predicates (unsaidName p) = none
  freshRule : ∀ N ∈ U.D.T.nodes, N.name ∉ U.unspec.map fillName
  ruleNames : ∀ p ∈ U.unspec, ruleName (fillName p) = true
  fillNodup : (U.unspec.map fillName).Nodup
  count : U.D.T.nodes.length + U.unspec.length ≤ 256
  heightU : ∀ N ∈ U.D.T.nodes, N.pred ∈ U.unspec → height U.D.T (fuel U.D.T) N ≤ 15
  ast : (U.D.T.nodes.map ruleNodes).sum + fillGuardNodes U ≤ 10000

theorem uvalid {U : UDoc} (h : WellFormedU U = true) : UValid U := by
  simp only [WellFormedU, Bool.and_eq_true] at h
  obtain ⟨⟨⟨hw, hd⟩, hr⟩, hl⟩ := h
  have hck := ((wellFormed_iff U.D).mp hw).1
  simp only [unspecDeclared, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.any_eq_true,
    beq_iff_eq, Bool.not_eq_true'] at hd
  simp only [reservedFree, Bool.and_eq_true, List.all_eq_true, beq_iff_eq, Bool.not_eq_true'] at hr
  simp only [limitsU, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, Bool.or_eq_true,
    Bool.not_eq_true', decide_eq_false_iff_not] at hl
  obtain ⟨hn, hdecl⟩ := hd
  obtain ⟨⟨⟨⟨_, _⟩, _⟩, hfp⟩, hfr⟩ := hr
  obtain ⟨⟨⟨⟨hrn, hfn⟩, hcount⟩, hh⟩, hast⟩ := hl
  refine ⟨hw, hck, valid_of_wellFormed _ hw, hn, fun p hp => ?_, hfp, fun N hN => ?_, hrn, hfn, hcount,
    fun N hN hp => ?_, hast⟩
  · obtain ⟨r, hr, hrn, hra⟩ := hdecl p hp
    exact ⟨r, hr, hrn, hra⟩
  · have := hfr N hN
    simpa using this
  · rcases hh N hN with h | h
    · exact absurd hp h
    · exact h

section Valid
variable {U : UDoc} (hu : UValid U)
include hu

theorem UValid.acyclic : DagAcyclic (precedenceNodes U.D.T) := (precedence_acyclic U.D hu.wf).1

theorem UValid.regulated_eq {r r' : Regulated} (hr : r ∈ U.D.T.regulated) (hr' : r' ∈ U.D.T.regulated)
    (e : r.name = r'.name) : r = r' := by
  obtain ⟨k, hk⟩ := mem_syms_index (hu.valid.regulated r hr)
  obtain ⟨k', hk'⟩ := mem_syms_index (hu.valid.regulated r' hr')
  have h₁ := find_regulated hu.valid hk
  have h₂ := find_regulated hu.valid hk'
  rw [← e] at h₂
  rw [h₁] at h₂
  exact Option.some.inj h₂

theorem UValid.names_nodup : (U.D.T.nodes.map Node.name).Nodup := hu.ok.2.2.2.2.2.2.1.2.1

theorem UValid.over_node {N : Node} (hN : N ∈ U.D.T.nodes) {m : String} (hm : m ∈ N.over) :
    ∃ M ∈ U.D.T.nodes, M.name = m ∧ M.pred = N.pred := by
  obtain ⟨M, hM, hp⟩ := hu.ok.2.2.2.2.2.2.2.1 N hN m hm
  exact ⟨M, List.mem_of_find?_eq_some hM, by simpa using List.find?_some hM, hp⟩

theorem UValid.over_fresh {N : Node} (hN : N ∈ U.D.T.nodes) {m : String} (hm : m ∈ N.over) :
    m ∉ U.unspec.map fillName := by
  obtain ⟨M, hM, rfl, _⟩ := hu.over_node hN hm
  exact hu.freshRule M hM

theorem UValid.node_regulated {N : Node} (hN : N ∈ U.D.T.nodes) : ∃ r ∈ U.D.T.regulated, r.name = N.pred := by
  obtain ⟨_, _, r, hr, _⟩ := hu.ok.2.2.2.2.2.2.1.1 N hN
  exact ⟨r, List.mem_of_find?_eq_some hr, by simpa using List.find?_some hr⟩

theorem UValid.declared_pred {r : Regulated} (hr : r ∈ U.D.T.regulated) :
    U.D.E.predicates r.name = some r.sorts := (hu.ok.2.2.1 r hr).1

/-- A declared predicate is not an unsaid name. -/
theorem UValid.not_unsaid {n : String} {ss : List String} (hn : U.D.E.predicates n = some ss) :
    n ∉ unsaidNames U := by
  intro h
  obtain ⟨p, hp, rfl⟩ := List.mem_map.mp h
  rw [hu.freshPred p hp] at hn
  cases hn

end Valid

theorem flatMap_congr_mem {α β : Type} {l : List α} {f g : α → List β} (h : ∀ x ∈ l, f x = g x) :
    l.flatMap f = l.flatMap g := by
  induction l with
  | nil => rfl
  | cons a l ih =>
    simp only [List.flatMap_cons, h a List.mem_cons_self, ih (fun x hx => h x (List.mem_cons_of_mem _ hx))]

/-! ## `fill` -/

@[simp] theorem fill_E (U : UDoc) : (fill U).E = fillEnv U := rfl
@[simp] theorem fill_lits (U : UDoc) : (fill U).lits = U.D.lits := rfl
@[simp] theorem fill_regulated (U : UDoc) : (fill U).T.regulated = U.D.T.regulated := rfl
@[simp] theorem fill_definitions (U : UDoc) : (fill U).T.definitions = U.D.T.definitions := rfl
theorem fill_nodes (U : UDoc) : (fill U).T.nodes = U.D.T.nodes.map (fillRoot U) ++ fillNodes U := rfl

theorem fillEnv_sorts (U : UDoc) : (fillEnv U).sorts = U.D.E.sorts := rfl
theorem fillEnv_constants (U : UDoc) : (fillEnv U).constants = U.D.E.constants := rfl

theorem fillEnv_off (U : UDoc) {n : String} (hn : n ∉ unsaidNames U) :
    (fillEnv U).predicates n = U.D.E.predicates n := by
  simp only [fillEnv]
  rw [show U.unspec.find? (fun p => unsaidName p == n) = none from
    List.find?_eq_none.mpr fun p hp he => hn (List.mem_map.mpr ⟨p, hp, by simpa using he⟩)]

theorem fillEnv_unsaid (U : UDoc) {p : String} (hp : p ∈ U.unspec) :
    (fillEnv U).predicates (unsaidName p) = some (sortsOf U.D p) := by
  simp only [fillEnv]
  cases hf : U.unspec.find? (fun q => unsaidName q == unsaidName p) with
  | none =>
    exact absurd hp fun hp => List.find?_eq_none.mp hf p hp (by simp)
  | some q =>
    have := unsaidName_inj (by simpa using List.find?_some hf)
    subst this
    rfl

/-- `fill_conservative`: without unspecified predicates `fill` is the identity and
there are no fill premises (the premises half is `fillPremises_nil`). -/
theorem fill_eq_self (U : UDoc) (h0 : U.unspec = []) : fill U = U.D := by
  obtain ⟨⟨E, lits, ⟨reg, defs, nodes⟩⟩, unspec⟩ := U
  simp only at h0
  subst h0
  have hroot : ∀ N : Node, fillRoot ⟨⟨E, lits, ⟨reg, defs, nodes⟩⟩, []⟩ N = N := fun N => by
    simp [fillRoot]
  have hf : fillRoot ⟨⟨E, lits, ⟨reg, defs, nodes⟩⟩, []⟩ = id := funext hroot
  have hnil : List.filter (fun r : Regulated => decide False) reg = [] := by simp
  simp only [fill, fillTree, fillNodes, fillEnv, List.find?_nil, List.not_mem_nil, hf, List.map_id, hnil,
    List.map_nil, List.append_nil]

@[simp] theorem fillRoot_name (U : UDoc) (N : Node) : (fillRoot U N).name = N.name := by
  unfold fillRoot; split <;> rfl
@[simp] theorem fillRoot_pred (U : UDoc) (N : Node) : (fillRoot U N).pred = N.pred := by
  unfold fillRoot; split <;> rfl
@[simp] theorem fillRoot_sign (U : UDoc) (N : Node) : (fillRoot U N).sign = N.sign := by
  unfold fillRoot; split <;> rfl
@[simp] theorem fillRoot_guard (U : UDoc) (N : Node) : (fillRoot U N).guard = N.guard := by
  unfold fillRoot; split <;> rfl
@[simp] theorem fillRoot_carveOuts (U : UDoc) (N : Node) : (fillRoot U N).carveOuts = N.carveOuts := by
  unfold fillRoot; split <;> rfl

theorem fillRoot_over (U : UDoc) (N : Node) :
    (N.pred ∈ U.unspec ∧ N.over = [] ∧ (fillRoot U N).over = [fillName N.pred]) ∨
      (¬ (N.pred ∈ U.unspec ∧ N.over = []) ∧ fillRoot U N = N) := by
  unfold fillRoot
  split
  · rename_i h; exact Or.inl ⟨h.1, h.2, rfl⟩
  · rename_i h; exact Or.inr ⟨h, rfl⟩

theorem mem_fillNodes {U : UDoc} {C : Node} :
    C ∈ fillNodes U ↔ ∃ r ∈ U.D.T.regulated, r.name ∈ U.unspec ∧ C = fillNode r := by
  simp only [fillNodes, List.mem_map, List.mem_filter, decide_eq_true_eq]
  constructor
  · rintro ⟨r, ⟨hr, hp⟩, rfl⟩; exact ⟨r, hr, hp, rfl⟩
  · rintro ⟨r, hr, hp, rfl⟩; exact ⟨r, ⟨hr, hp⟩, rfl⟩

theorem mem_fill_nodes {U : UDoc} {C : Node} :
    C ∈ (fill U).T.nodes ↔ (∃ C₀ ∈ U.D.T.nodes, C = fillRoot U C₀) ∨ C ∈ fillNodes U := by
  simp only [fill_nodes, List.mem_append, List.mem_map]
  constructor
  · rintro (⟨C₀, h, rfl⟩ | h)
    · exact Or.inl ⟨C₀, h, rfl⟩
    · exact Or.inr h
  · rintro (⟨C₀, h, rfl⟩ | h)
    · exact Or.inl ⟨C₀, h, rfl⟩
    · exact Or.inr h

theorem children_fillRoot (U : UDoc) (T : Tree) (N : Node) : children T (fillRoot U N) = children T N := by
  simp only [children, fillRoot_pred, fillRoot_name]

section Structure
variable {U : UDoc} (hu : UValid U)
include hu

/-- No author rule gains a child: an author rule's exceptions are the same in `T‴`. -/
theorem children_fill_author {N : Node} (hN : N ∈ U.D.T.nodes) :
    children (fill U).T N = children U.D.T N := by
  have hfresh := hu.freshRule N hN
  unfold children
  congr 1
  rw [fill_nodes, List.flatMap_append, List.flatMap_map]
  have h₂ : (fillNodes U).flatMap (fun C => if C.pred == N.pred then (C.over.filter (· == N.name)).map
      (fun _ => C) else []) = [] := by
    rw [List.flatMap_eq_nil_iff]
    intro C hC
    obtain ⟨r, _, _, rfl⟩ := mem_fillNodes.mp hC
    simp [fillNode]
  rw [h₂, List.append_nil]
  apply flatMap_congr_mem
  intro C _
  rcases fillRoot_over U C with ⟨hp, ho, ho'⟩ | ⟨_, he⟩
  · simp only [fillRoot_pred, ho', ho]
    have : (fillName C.pred == N.name) = false := by
      simp only [beq_eq_false_iff_ne]
      intro e
      exact hfresh (List.mem_map.mpr ⟨C.pred, hp, e⟩)
    simp [this]
  · rw [he]

theorem fill_node_author {C : Node} (hC : C ∈ U.D.T.nodes) : C.name ∉ U.unspec.map fillName :=
  hu.freshRule C hC

/-- The exceptions of `F_p` are the roots on `p`. -/
theorem mem_children_fillNode {r : Regulated} (hp : r.name ∈ U.unspec) {C : Node} :
    C ∈ children (fill U).T (fillNode r) ↔
      ∃ C₀ ∈ U.D.T.nodes, C = fillRoot U C₀ ∧ C₀.pred = r.name ∧ C₀.over = [] := by
  rw [mem_children_iff]
  simp only [fillNode]
  constructor
  · rintro ⟨hC, hpred, hover⟩
    rcases mem_fill_nodes.mp hC with ⟨C₀, hC₀, rfl⟩ | hC
    · rw [fillRoot_pred] at hpred
      rcases fillRoot_over U C₀ with ⟨_, ho, _⟩ | ⟨_, he⟩
      · exact ⟨C₀, hC₀, rfl, hpred, ho⟩
      · rw [he] at hover
        exact absurd (List.mem_map.mpr ⟨r.name, hp, rfl⟩) (hu.over_fresh hC₀ hover)
    · obtain ⟨r', _, _, rfl⟩ := mem_fillNodes.mp hC
      simp [fillNode] at hover
  · rintro ⟨C₀, hC₀, rfl, hpred, ho⟩
    refine ⟨mem_fill_nodes.mpr (Or.inl ⟨C₀, hC₀, rfl⟩), by rw [fillRoot_pred, hpred], ?_⟩
    rcases fillRoot_over U C₀ with ⟨_, _, ho'⟩ | ⟨hn, _⟩
    · rw [ho', hpred]; exact List.mem_singleton_self _
    · exact absurd ⟨hpred ▸ hp, ho⟩ hn

end Structure

/-! ## Fuel: a subtree is decided within the rules below it -/

open Classical in
/-- The number of rules below `N` in the precedence DAG (those with a path to `N`). -/
noncomputable def belowCount (T : Tree) (N : Node) : Nat :=
  (nodeNames (precedenceNodes T)).countP (fun x => decide (DepPath (precedenceNodes T) x N.name))

open Classical in
/-- The number of rules above `N` (those `N` has a path to). -/
noncomputable def aboveCount (T : Tree) (N : Node) : Nat :=
  (nodeNames (precedenceNodes T)).countP (fun x => decide (DepPath (precedenceNodes T) N.name x))

theorem nodeNames_precedence (T : Tree) : nodeNames (precedenceNodes T) = T.nodes.map Node.name := by
  simp [nodeNames, precedenceNodes]

/-- An exception points at the rule it takes precedence over. -/
theorem over_edge {T : Tree} {N M : Node} (hN : N ∈ T.nodes) (hM : M ∈ T.nodes) (hover : M.name ∈ N.over) :
    DepEdge (precedenceNodes T) N.name M.name := by
  refine ⟨⟨N.name, N.over⟩, List.mem_map.mpr ⟨N, hN, rfl⟩, rfl, ?_⟩
  rw [mem_deps]
  exact ⟨hover, by rw [nodeNames_precedence]; exact List.mem_map_of_mem hM⟩

theorem child_edge {T : Tree} {N C : Node} (hN : N ∈ T.nodes) (hC : C ∈ children T N) :
    DepEdge (precedenceNodes T) C.name N.name := by
  obtain ⟨hC, _, hover⟩ := mem_children_iff.mp hC
  exact over_edge hC hN hover

theorem belowCount_child {T : Tree} (hac : DagAcyclic (precedenceNodes T)) {N C : Node} (hN : N ∈ T.nodes)
    (hC : C ∈ children T N) : belowCount T C < belowCount T N := by
  classical
  have he := child_edge hN hC
  apply countP_lt_of
  · intro x _ hx
    simp only [decide_eq_true_eq] at hx ⊢
    exact .trans hx (.edge he)
  · refine ⟨C.name, ?_, by simpa using DepPath.edge he, by simpa using hac C.name⟩
    rw [nodeNames_precedence]; exact List.mem_map_of_mem (mem_children_iff.mp hC).1

theorem aboveCount_over {T : Tree} (hac : DagAcyclic (precedenceNodes T)) {N M : Node} (hN : N ∈ T.nodes)
    (hM : M ∈ T.nodes) (hover : M.name ∈ N.over) : aboveCount T M < aboveCount T N := by
  classical
  have he := over_edge hN hM hover
  apply countP_lt_of
  · intro x _ hx
    simp only [decide_eq_true_eq] at hx ⊢
    exact .trans (.edge he) hx
  · refine ⟨M.name, ?_, by simpa using DepPath.edge he, by simpa using hac M.name⟩
    rw [nodeNames_precedence]; exact List.mem_map_of_mem hM

theorem belowCount_lt {T : Tree} (hac : DagAcyclic (precedenceNodes T)) {N : Node} (hN : N ∈ T.nodes) :
    belowCount T N < T.nodes.length := by
  classical
  have hlen : (nodeNames (precedenceNodes T)).countP (fun _ => true) = T.nodes.length := by
    rw [List.countP_true, nodeNames_precedence, List.length_map]
  rw [← hlen]
  apply countP_lt_of
  · intros; rfl
  · exact ⟨N.name, by rw [nodeNames_precedence]; exact List.mem_map_of_mem hN, rfl, by simpa using hac N.name⟩

section Stable
variable {T : Tree} (hac : DagAcyclic (precedenceNodes T)) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
include hac

theorem yields_leaf {N : Node} (hN : N ∈ T.nodes) (h0 : belowCount T N = 0) :
    ∀ g, YieldsD T S ρ g N ↔ AppliesD S ρ N
  | 0 => Iff.rfl
  | g + 1 => by
    simp only [YieldsD]
    refine ⟨fun h => h.elim id fun ⟨C, hC, _⟩ => ?_, Or.inl⟩
    have := belowCount_child hac hN hC
    omega

theorem yields_stable : ∀ (f g : Nat) (N : Node), N ∈ T.nodes → belowCount T N ≤ f → belowCount T N ≤ g →
    (YieldsD T S ρ f N ↔ YieldsD T S ρ g N)
  | 0, g, N, hN, hf, _ => by
    rw [yields_leaf hac S ρ hN (by omega) g]; exact Iff.rfl
  | f + 1, 0, N, hN, _, hg => by
    rw [yields_leaf hac S ρ hN (by omega) (f + 1)]; exact Iff.rfl
  | f + 1, g + 1, N, hN, hf, hg => by
    simp only [YieldsD]
    apply or_congr_right
    constructor
    · rintro ⟨C, hC, hy⟩
      have := belowCount_child hac hN hC
      exact ⟨C, hC, (yields_stable f g C (mem_children_iff.mp hC).1 (by omega) (by omega)).mp hy⟩
    · rintro ⟨C, hC, hy⟩
      have := belowCount_child hac hN hC
      exact ⟨C, hC, (yields_stable f g C (mem_children_iff.mp hC).1 (by omega) (by omega)).mpr hy⟩

theorem selects_stable (f g : Nat) {N : Node} (hN : N ∈ T.nodes) (hf : belowCount T N ≤ f)
    (hg : belowCount T N ≤ g) : SelectsD T S ρ f N ↔ SelectsD T S ρ g N := by
  simp only [SelectsD]
  apply and_congr_right
  intro _
  apply not_congr
  constructor
  · rintro ⟨C, hC, hy⟩
    have := belowCount_child hac hN hC
    exact ⟨C, hC, (yields_stable hac S ρ f g C (mem_children_iff.mp hC).1 (by omega) (by omega)).mp hy⟩
  · rintro ⟨C, hC, hy⟩
    have := belowCount_child hac hN hC
    exact ⟨C, hC, (yields_stable hac S ρ f g C (mem_children_iff.mp hC).1 (by omega) (by omega)).mpr hy⟩

/-- At full fuel a subtree yields iff its root applies or an exception subtree yields. -/
theorem yields_fuel_unfold {N : Node} (hN : N ∈ T.nodes) :
    YieldsD T S ρ (fuel T) N ↔ AppliesD S ρ N ∨ ∃ C ∈ children T N, YieldsD T S ρ (fuel T) C := by
  have hlt := belowCount_lt hac hN
  obtain ⟨k, hk⟩ : ∃ k, fuel T = k + 1 := ⟨T.nodes.length - 1, by unfold fuel; omega⟩
  have hk' : T.nodes.length = k + 1 := hk
  rw [hk]
  simp only [YieldsD]
  apply or_congr_right
  constructor
  · rintro ⟨C, hC, hy⟩
    have := belowCount_child hac hN hC
    exact ⟨C, hC, (yields_stable hac S ρ k (k + 1) C (mem_children_iff.mp hC).1 (by omega)
      (by omega)).mp hy⟩
  · rintro ⟨C, hC, hy⟩
    have := belowCount_child hac hN hC
    exact ⟨C, hC, (yields_stable hac S ρ k (k + 1) C (mem_children_iff.mp hC).1 (by omega)
      (by omega)).mpr hy⟩

/-- The lowest applying rule of a yielding subtree selects. -/
theorem selects_of_yields : ∀ n (N : Node), N ∈ T.nodes → belowCount T N = n → YieldsD T S ρ (fuel T) N →
    ∃ M ∈ T.nodes, M.pred = N.pred ∧ SelectsD T S ρ (fuel T) M := by
  intro n
  induction n using Nat.strongRecOn with
  | ind n ih =>
    intro N hN hn hy
    by_cases hc : ∃ C ∈ children T N, YieldsD T S ρ (fuel T) C
    · obtain ⟨C, hC, hyC⟩ := hc
      obtain ⟨hCm, hCp, _⟩ := mem_children_iff.mp hC
      obtain ⟨M, hM, hMp, hs⟩ := ih _ (hn ▸ belowCount_child hac hN hC) C hCm rfl hyC
      exact ⟨M, hM, hMp.trans hCp, hs⟩
    · have ha := ((yields_fuel_unfold hac S ρ hN).mp hy).resolve_right hc
      exact ⟨N, hN, rfl, ha, hc⟩

/-- A yielding subtree lies below a yielding root. -/
theorem root_of_yields (hover : ∀ N ∈ T.nodes, ∀ m ∈ N.over, ∃ M ∈ T.nodes, M.name = m ∧ M.pred = N.pred) :
    ∀ n (N : Node), N ∈ T.nodes → aboveCount T N = n → YieldsD T S ρ (fuel T) N →
      ∃ C ∈ T.nodes, C.pred = N.pred ∧ C.over = [] ∧ YieldsD T S ρ (fuel T) C := by
  intro n
  induction n using Nat.strongRecOn with
  | ind n ih =>
    intro N hN hn hy
    cases ho : N.over with
    | nil => exact ⟨N, hN, rfl, ho, hy⟩
    | cons m ms =>
      obtain ⟨M, hM, hMn, hMp⟩ := hover N hN m (by rw [ho]; exact List.mem_cons_self)
      have hover' : M.name ∈ N.over := by rw [hMn, ho]; exact List.mem_cons_self
      have hNM : N ∈ children T M := mem_children_iff.mpr ⟨hN, hMp.symm, hover'⟩
      have hyM : YieldsD T S ρ (fuel T) M := (yields_fuel_unfold hac S ρ hM).mpr (Or.inr ⟨N, hNM, hy⟩)
      obtain ⟨C, hC, hCp, hCo, hyC⟩ := ih _ (hn ▸ aboveCount_over hac hN hM hover') M hM rfl hyM
      exact ⟨C, hC, hCp.trans hMp, hCo, hyC⟩

/-- `yields_iff_selects`: some root subtree on `p` yields iff some rule on `p` selects. -/
theorem yields_iff_selects
    (hover : ∀ N ∈ T.nodes, ∀ m ∈ N.over, ∃ M ∈ T.nodes, M.name = m ∧ M.pred = N.pred) (p : String) :
    (∃ C ∈ T.nodes, C.pred = p ∧ C.over = [] ∧ YieldsD T S ρ (fuel T) C) ↔
      ∃ N ∈ T.nodes, N.pred = p ∧ SelectsD T S ρ (fuel T) N := by
  constructor
  · rintro ⟨C, hC, rfl, _, hy⟩
    obtain ⟨M, hM, hMp, hs⟩ := selects_of_yields hac S ρ _ C hC rfl hy
    exact ⟨M, hM, hMp, hs⟩
  · rintro ⟨N, hN, rfl, hs⟩
    have hy : YieldsD T S ρ (fuel T) N := (yields_fuel_unfold hac S ρ hN).mpr (Or.inl hs.1)
    obtain ⟨C, hC, hCp, hCo, hyC⟩ := root_of_yields hac S ρ hover _ N hN rfl hy
    exact ⟨C, hC, hCp, hCo, hyC⟩

end Stable

theorem decides_either (T : Tree) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (p : String) :
    (DecidesD T S ρ p true ∨ DecidesD T S ρ p false) ↔
      ∃ N ∈ T.nodes, N.pred = p ∧ SelectsD T S ρ (fuel T) N := by
  simp only [DecidesD, rulesOn, List.mem_filter, beq_iff_eq]
  constructor
  · rintro (⟨N, ⟨hN, hp⟩, _, hs⟩ | ⟨N, ⟨hN, hp⟩, _, hs⟩) <;> exact ⟨N, hN, hp, hs⟩
  · rintro ⟨N, hN, hp, hs⟩
    cases hsg : N.sign
    · exact Or.inr ⟨N, ⟨hN, hp⟩, hsg, hs⟩
    · exact Or.inl ⟨N, ⟨hN, hp⟩, hsg, hs⟩

/-! ## Selection on `T‴` -/

theorem appliesD_fillRoot (U : UDoc) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (N : Node) :
    AppliesD S ρ (fillRoot U N) ↔ AppliesD S ρ N := by
  simp [AppliesD]

theorem yieldsD_fillRoot (U : UDoc) (T : Tree) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (f : Nat) (N : Node) :
    YieldsD T S ρ f (fillRoot U N) ↔ YieldsD T S ρ f N := by
  cases f <;> simp only [YieldsD, children_fillRoot, appliesD_fillRoot]

theorem selectsD_fillRoot (U : UDoc) (T : Tree) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (f : Nat) (N : Node) :
    SelectsD T S ρ f (fillRoot U N) ↔ SelectsD T S ρ f N := by
  simp only [SelectsD, children_fillRoot, appliesD_fillRoot]

theorem fuel_fill (U : UDoc) : fuel (fill U).T = fuel U.D.T + (fillNodes U).length := by
  simp [fuel, fill_nodes]

section Sel
variable {U : UDoc} (hu : UValid U) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
include hu

theorem yields_fill_author : ∀ (f : Nat) (N : Node), N ∈ U.D.T.nodes →
    (YieldsD (fill U).T S ρ f N ↔ YieldsD U.D.T S ρ f N)
  | 0, _, _ => Iff.rfl
  | f + 1, N, hN => by
    simp only [YieldsD]
    rw [children_fill_author hu hN]
    apply or_congr_right
    constructor
    · rintro ⟨C, hC, hy⟩
      exact ⟨C, hC, (yields_fill_author f C (mem_children_iff.mp hC).1).mp hy⟩
    · rintro ⟨C, hC, hy⟩
      exact ⟨C, hC, (yields_fill_author f C (mem_children_iff.mp hC).1).mpr hy⟩

/-- An author rule's subtree at the fuel of `T‴` is its subtree in `T`. -/
theorem yields_fill_fuel {N : Node} (hN : N ∈ U.D.T.nodes) :
    YieldsD (fill U).T S ρ (fuel (fill U).T) N ↔ YieldsD U.D.T S ρ (fuel U.D.T) N := by
  rw [yields_fill_author hu S ρ _ N hN]
  have := belowCount_lt hu.acyclic hN
  exact yields_stable hu.acyclic S ρ _ _ N hN (by rw [fuel_fill]; unfold fuel; omega) (by unfold fuel; omega)

theorem selects_fill_fuel {N : Node} (hN : N ∈ U.D.T.nodes) :
    SelectsD (fill U).T S ρ (fuel (fill U).T) N ↔ SelectsD U.D.T S ρ (fuel U.D.T) N := by
  simp only [SelectsD]
  rw [children_fill_author hu hN]
  apply and_congr_right
  intro _
  apply not_congr
  constructor
  · rintro ⟨C, hC, hy⟩
    exact ⟨C, hC, (yields_fill_fuel hu S ρ (mem_children_iff.mp hC).1).mp hy⟩
  · rintro ⟨C, hC, hy⟩
    exact ⟨C, hC, (yields_fill_fuel hu S ρ (mem_children_iff.mp hC).1).mpr hy⟩

theorem sortsOf_reg {r : Regulated} (hr : r ∈ U.D.T.regulated) : sortsOf U.D r.name = r.sorts := by
  unfold sortsOf
  cases hf : U.D.T.regulated.find? (·.name == r.name) with
  | none => exact absurd hf (by rw [List.find?_eq_none]; intro h; exact h r hr (by simp))
  | some r' =>
    have := hu.regulated_eq (List.mem_of_find?_eq_some hf) hr (by simpa using List.find?_some hf)
    subst this; rfl

/-- `F_p` selects exactly where the gap is filled "yes" and no author rule on `p` selects. -/
theorem selects_fillNode {r : Regulated} (hp : r.name ∈ U.unspec) :
    SelectsD (fill U).T S ρ (fuel (fill U).T) (fillNode r) ↔
      (atom (unsaidName r.name) r.sorts).denote S ρ ∧
        ¬ DecidesD U.D.T S ρ r.name true ∧ ¬ DecidesD U.D.T S ρ r.name false := by
  have hover : ∀ N ∈ U.D.T.nodes, ∀ m ∈ N.over, ∃ M ∈ U.D.T.nodes, M.name = m ∧ M.pred = N.pred :=
    fun N hN m hm => hu.over_node hN hm
  simp only [SelectsD, AppliesD, fillNode, List.not_mem_nil, false_and, exists_false, not_false_eq_true,
    and_true]
  apply and_congr_right
  intro _
  rw [← not_or, decides_either, ← yields_iff_selects hu.acyclic S ρ hover]
  apply not_congr
  constructor
  · rintro ⟨C, hC, hy⟩
    obtain ⟨C₀, hC₀, rfl, hpred, ho⟩ := (mem_children_fillNode hu hp).mp hC
    rw [yieldsD_fillRoot, yields_fill_fuel hu S ρ hC₀] at hy
    exact ⟨C₀, hC₀, hpred, ho, hy⟩
  · rintro ⟨C₀, hC₀, hpred, ho, hy⟩
    refine ⟨fillRoot U C₀, (mem_children_fillNode hu hp).mpr ⟨C₀, hC₀, rfl, hpred, ho⟩, ?_⟩
    rw [yieldsD_fillRoot, yields_fill_fuel hu S ρ hC₀]
    exact hy

omit hu in
theorem mem_rulesOn_fill {p : String} {N : Node} :
    N ∈ rulesOn (fill U).T p ↔ (∃ N₀ ∈ rulesOn U.D.T p, N = fillRoot U N₀) ∨
      (∃ r ∈ U.D.T.regulated, r.name = p ∧ p ∈ U.unspec ∧ N = fillNode r) := by
  simp only [rulesOn, List.mem_filter, beq_iff_eq, mem_fill_nodes, mem_fillNodes]
  constructor
  · rintro ⟨⟨N₀, hN₀, rfl⟩ | ⟨r, hr, hp, rfl⟩, hpred⟩
    · exact Or.inl ⟨N₀, ⟨hN₀, by simpa using hpred⟩, rfl⟩
    · exact Or.inr ⟨r, hr, hpred, hpred ▸ hp, rfl⟩
  · rintro (⟨N₀, ⟨hN₀, hpred⟩, rfl⟩ | ⟨r, hr, rfl, hp, rfl⟩)
    · exact ⟨Or.inl ⟨N₀, hN₀, rfl⟩, by simpa using hpred⟩
    · exact ⟨Or.inr ⟨r, hr, hp, rfl⟩, rfl⟩

theorem decidesD_fill (p : String) (sign : Bool) :
    DecidesD (fill U).T S ρ p sign ↔ DecidesD U.D.T S ρ p sign ∨
      (sign = true ∧ ∃ r ∈ U.D.T.regulated, r.name = p ∧ p ∈ U.unspec ∧
        SelectsD (fill U).T S ρ (fuel (fill U).T) (fillNode r)) := by
  simp only [DecidesD]
  constructor
  · rintro ⟨N, hN, hs, hsel⟩
    rcases mem_rulesOn_fill.mp hN with ⟨N₀, hN₀, rfl⟩ | ⟨r, hr, hrp, hp, rfl⟩
    · rw [selectsD_fillRoot, selects_fill_fuel hu S ρ (List.mem_filter.mp hN₀).1] at hsel
      exact Or.inl ⟨N₀, hN₀, by simpa using hs, hsel⟩
    · exact Or.inr ⟨hs.symm, r, hr, hrp, hp, hsel⟩
  · rintro (⟨N₀, hN₀, hs, hsel⟩ | ⟨rfl, r, hr, hrp, hp, hsel⟩)
    · refine ⟨fillRoot U N₀, mem_rulesOn_fill.mpr (Or.inl ⟨N₀, hN₀, rfl⟩), by simpa using hs, ?_⟩
      rw [selectsD_fillRoot, selects_fill_fuel hu S ρ (List.mem_filter.mp hN₀).1]
      exact hsel
    · exact ⟨fillNode r, mem_rulesOn_fill.mpr (Or.inr ⟨r, hr, hrp, hp, rfl⟩), rfl, hsel⟩

end Sel

/-- `fill_selects_author`: no author rule's selection changes; `fill` adds parents only. -/
theorem fill_selects_author (U : UDoc) (h : WellFormedU U = true) (N : Node) (hN : N ∈ U.D.T.nodes)
    (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    (selects (fill U).T (fuel (fill U).T) N).denote S ρ ↔ (selects U.D.T (fuel U.D.T) N).denote S ρ := by
  rw [selects_denote, selects_denote]
  exact selects_fill_fuel (uvalid h) S ρ hN

/-- `fill_decides`: the synthetic rule selects exactly where the author rules are
silent and the gap is filled "yes". -/
theorem fill_decides (U : UDoc) (h : WellFormedU U = true) (p : String) (hp : p ∈ U.unspec)
    (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    (DecidesD (fill U).T S ρ p true ↔ DecidesD U.D.T S ρ p true ∨
        ((atom (unsaidName p) (sortsOf U.D p)).denote S ρ ∧
          ¬ DecidesD U.D.T S ρ p true ∧ ¬ DecidesD U.D.T S ρ p false)) ∧
    (DecidesD (fill U).T S ρ p false ↔ DecidesD U.D.T S ρ p false) := by
  have hu := uvalid h
  obtain ⟨r, hr, rfl, _⟩ := hu.declared p hp
  refine ⟨?_, ?_⟩
  · rw [decidesD_fill hu S ρ, sortsOf_reg hu hr]
    apply or_congr_right
    constructor
    · rintro ⟨_, r', hr', hrn, _, hsel⟩
      have := hu.regulated_eq hr' hr hrn
      subst this
      exact (selects_fillNode hu S ρ hp).mp hsel
    · intro hx
      exact ⟨rfl, r, hr, rfl, hp, (selects_fillNode hu S ρ hp).mpr hx⟩
  · rw [decidesD_fill hu S ρ]
    simp

/-- `fill_local_conflict`: on `T‴` the local conflict target of every regulated
predicate is W1's. -/
theorem fill_local_conflict (U : UDoc) (h : WellFormedU U = true) (r : Regulated) (hr : r ∈ U.D.T.regulated)
    (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    ((pos (fill U).T r.name).denote S ρ ∧ (neg (fill U).T r.name).denote S ρ) ↔
      ((pos U.D.T r.name).denote S ρ ∧ (neg U.D.T r.name).denote S ρ) := by
  have hu := uvalid h
  simp only [pos, neg, decides_denote]
  rw [decidesD_fill hu S ρ r.name false, decidesD_fill hu S ρ r.name true]
  simp only [Bool.false_eq_true, false_and, or_false, true_and]
  constructor
  · rintro ⟨hP | ⟨r', hr', hrn, hp, hsel⟩, hN⟩
    · exact ⟨hP, hN⟩
    · have := hu.regulated_eq hr' hr hrn
      subst this
      exact absurd hN ((selects_fillNode hu S ρ hp).mp hsel).2.2
  · rintro ⟨hP, hN⟩
    exact ⟨Or.inl hP, hN⟩

end VE.NormDefaults
