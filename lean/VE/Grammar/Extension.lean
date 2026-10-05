import VE.Grammar.Meaning
import VE.Grammar.Reading

/-! Extensions (docs/spec/english-lean.md 2.11 and 5.7).

An embedding of `G` into `G2` carries derivations to derivations of the same sentence, keeps different
derivations different and keeps every successful meaning. Under it a sentence with one reading keeps
that reading or becomes visibly ambiguous (`extension_safe`); growth cannot hide an ambiguity
(`extension_keeps_many`). An injective map on rules that preserves both sides of each rule and its
action induces an embedding (`rule_map_embeds`).
-/

namespace VE.Grammar

section Embedding

variable {T K σ ρ α : Type} [Accepts K T]
variable {G G2 : Grammar K} {μ μ2 : Meaning T σ ρ α} {emb : Tree T → Tree T}
variable {st st2 : σ} {w : List T} {A : α} {c : Bool} {t u : Tree T}

/-- A map on trees that carries derivations of `G` to derivations of `G2` of the same sentence, keeps
different derivations different, and keeps every successful meaning: the value, the conclusion mark
and the successor state, from the same initial state. -/
structure Embeds (G G2 : Grammar K) (μ μ2 : Meaning T σ ρ α) (emb : Tree T → Tree T) : Prop where
  derives : ∀ w t, Derives G (.n G.start) w t → Derives G2 (.n G2.start) w (emb t)
  injective : ∀ w t u, Derives G (.n G.start) w t → Derives G (.n G.start) w u → emb t = emb u → t = u
  meaning : ∀ st w t x, Derives G (.n G.start) w t → μ st t = .ok x → μ2 st (emb t) = .ok x

theorem extension_safe : Embeds G G2 μ μ2 emb → OneReading G μ st w A c st2 →
    OneReading G2 μ2 st w A c st2 ∨
    ∃ t u, Derives G2 (.n G2.start) w t ∧ Derives G2 (.n G2.start) w u ∧ t ≠ u := by
  rintro he ⟨t, hd, _, hm⟩
  have hd2 := he.derives w t hd
  have hm2 := he.meaning st w t _ hd hm
  by_cases hall : ∀ u, Derives G2 (.n G2.start) w u → u = emb t
  · exact Or.inl ⟨emb t, hd2, hall, hm2⟩
  · right
    have : ∃ u, Derives G2 (.n G2.start) w u ∧ u ≠ emb t := by
      apply Classical.byContradiction
      intro hn
      exact hall (fun u hu => Classical.byContradiction (fun hne => hn ⟨u, hu, hne⟩))
    obtain ⟨u, hu, hne⟩ := this
    exact ⟨emb t, u, hd2, hu, fun e => hne e.symm⟩

theorem extension_keeps_many : Embeds G G2 μ μ2 emb →
    Derives G (.n G.start) w t → Derives G (.n G.start) w u → t ≠ u →
    Derives G2 (.n G2.start) w (emb t) ∧ Derives G2 (.n G2.start) w (emb u) ∧ emb t ≠ emb u :=
  fun he ht hu hne => ⟨he.derives w t ht, he.derives w u hu, fun e => hne (he.injective w t u ht hu e)⟩

end Embedding

/-- A map on rule indices and on nonterminals. -/
structure RuleMap where
  rule : Nat → Nat
  nt : Nat → Nat

def Sym.rename {K : Type} (nt : Nat → Nat) : Sym K → Sym K
  | .t a => .t a
  | .n A => .n (nt A)

mutual
/-- Renumbers the rule of every node. -/
def RuleMap.tree {T : Type} (e : RuleMap) : Tree T → Tree T
  | .leaf tok => .leaf tok
  | .node r kids => .node (e.rule r) (e.trees kids)
/-- Renumbers the rule of every node of every tree. -/
def RuleMap.trees {T : Type} (e : RuleMap) : List (Tree T) → List (Tree T)
  | [] => []
  | t :: ts => e.tree t :: e.trees ts
end
end VE.Grammar

namespace VE.Grammar

variable {T K σ ρ α : Type} [Accepts K T]
variable {G G2 : Grammar K} {S : Sig T} {acts acts2 : Array (Action S)} {e : RuleMap} {X : Sym K}
variable {t : Tree T}

/-- The rule map is injective on the rules of `G`, and the image of each rule has the renamed sides
and the same action. -/
structure RuleMap.Ok (e : RuleMap) (G G2 : Grammar K) (acts acts2 : Array (Action S)) : Prop where
  start : e.nt G.start = G2.start
  injective : ∀ r r2, r < G.rules.size → r2 < G.rules.size → e.rule r = e.rule r2 → r = r2
  rules : ∀ r R, G.rules[r]? = some R → ∃ R2, G2.rules[e.rule r]? = some R2 ∧
    R2.lhs = e.nt R.lhs ∧ R2.rhs = R.rhs.map (Sym.rename e.nt) ∧ acts2[R2.act]? = acts[R.act]?

mutual
theorem rule_map_sem_of (he : e.Ok G G2 acts acts2) : ∀ (X : Sym K) (t : Tree T), t.derives G X = true →
    (e.tree t).derives G2 (X.rename e.nt) = true ∧ (e.tree t).yield = t.yield ∧
    (e.tree t).sem G2 S acts2 = t.sem G S acts
  | .t a, .leaf tok, h => by
    refine ⟨?_, ?_, ?_⟩
    · simpa [RuleMap.tree, Sym.rename, Tree.derives] using h
    · simp [RuleMap.tree]
    · simp [RuleMap.tree, Tree.sem]
  | .n _, .leaf _, h => by simp [Tree.derives] at h
  | .t _, .node _ _, h => by simp [Tree.derives] at h
  | .n A, .node r kids, h => by
    rw [derives_node] at h
    cases hr : G.rules[r]? with
    | none => simp [hr] at h
    | some R =>
      simp only [hr, Bool.and_eq_true, beq_iff_eq] at h
      obtain ⟨R2, hr2, hl2, hrhs2, ha2⟩ := he.rules r R hr
      obtain ⟨hd, hy, hs⟩ := rule_map_sems_of he R.rhs kids h.2
      refine ⟨?_, ?_, ?_⟩
      · simp only [RuleMap.tree, Sym.rename, derives_node, hr2, hl2, h.1, hrhs2, beq_self_eq_true,
          Bool.true_and]
        exact hd
      · simp only [RuleMap.tree, yield_node]; exact hy
      · simp only [RuleMap.tree, Tree.sem, hr2, hr, ha2]
        rw [hs]
theorem rule_map_sems_of (he : e.Ok G G2 acts acts2) : ∀ (Xs : List (Sym K)) (kids : List (Tree T)),
    derivesAll G Xs kids = true →
    derivesAll G2 (Xs.map (Sym.rename e.nt)) (e.trees kids) = true ∧ yieldAll (e.trees kids) = yieldAll kids ∧
    semAll G2 S acts2 (e.trees kids) = semAll G S acts kids
  | [], [], _ => by simp [RuleMap.trees, derivesAll, yieldAll, semAll]
  | [], _ :: _, h => by simp [derivesAll] at h
  | _ :: _, [], h => by simp [derivesAll] at h
  | X :: Xs, k :: ks, h => by
    rw [derivesAll_cons, Bool.and_eq_true] at h
    obtain ⟨hd1, hy1, hs1⟩ := rule_map_sem_of he X k h.1
    obtain ⟨hd2, hy2, hs2⟩ := rule_map_sems_of he Xs ks h.2
    refine ⟨?_, ?_, ?_⟩
    · simp only [List.map_cons, RuleMap.trees, derivesAll_cons, hd1, hd2, Bool.and_self]
    · simp only [RuleMap.trees, yieldAll_cons, hy1, hy2]
    · simp only [RuleMap.trees, semAll, hs1, hs2]
end
-- `lean/audit.py` reads the `end` of a `mutual` block as the end of the namespace; closing and
-- reopening the namespace here keeps its reading and Lean's the same.
end VE.Grammar

namespace VE.Grammar

variable {T K σ ρ α : Type} [Accepts K T]
variable {G G2 : Grammar K} {S : Sig T} {acts acts2 : Array (Action S)} {e : RuleMap} {X : Sym K}
variable {t : Tree T}

theorem rule_map_sem : e.Ok G G2 acts acts2 → t.derives G X = true →
    (e.tree t).derives G2 (X.rename e.nt) = true ∧ (e.tree t).yield = t.yield ∧
    (e.tree t).sem G2 S acts2 = t.sem G S acts :=
  fun he h => rule_map_sem_of he X t h

mutual
theorem rule_map_inj (he : e.Ok G G2 acts acts2) : ∀ (X Y : Sym K) (t u : Tree T), t.derives G X = true →
    u.derives G Y = true → e.tree t = e.tree u → t = u
  | _, _, .leaf a, .leaf b, _, _, h => by simpa [RuleMap.tree] using h
  | _, _, .leaf _, .node _ _, _, _, h => by simp [RuleMap.tree] at h
  | _, _, .node _ _, .leaf _, _, _, h => by simp [RuleMap.tree] at h
  | X, Y, .node r ks, .node q us, ht, hu, h => by
    match X, Y, ht, hu with
    | .n A, .n B, ht, hu =>
      obtain ⟨r1, ks1, R1, h1, hr1, _, hd1⟩ := derives_root (G := G) ht
      obtain ⟨q1, us1, Q1, h2, hq1, _, hd2⟩ := derives_root (G := G) hu
      simp only [Tree.node.injEq] at h1 h2
      obtain ⟨rfl, rfl⟩ := h1
      obtain ⟨rfl, rfl⟩ := h2
      simp only [RuleMap.tree, Tree.node.injEq] at h
      have hrq : r = q := he.injective r q (Array.getElem?_eq_some_iff.mp hr1).1
        (Array.getElem?_eq_some_iff.mp hq1).1 h.1
      subst hrq
      rw [hr1] at hq1
      cases hq1
      rw [rule_map_injs he R1.rhs ks us hd1 hd2 h.2]
    | .t _, _, ht, _ => simp [Tree.derives] at ht
    | .n _, .t _, _, hu => simp [Tree.derives] at hu
theorem rule_map_injs (he : e.Ok G G2 acts acts2) : ∀ (Xs : List (Sym K)) (ks us : List (Tree T)),
    derivesAll G Xs ks = true → derivesAll G Xs us = true → e.trees ks = e.trees us → ks = us
  | [], [], [], _, _, _ => rfl
  | [], _ :: _, _, h, _, _ => by simp [derivesAll] at h
  | [], [], _ :: _, _, h, _ => by simp [derivesAll] at h
  | _ :: _, [], _, h, _, _ => by simp [derivesAll] at h
  | _ :: _, _ :: _, [], _, h, _ => by simp [derivesAll] at h
  | X :: Xs, k :: ks, u :: us, h1, h2, h => by
    rw [derivesAll_cons, Bool.and_eq_true] at h1 h2
    simp only [RuleMap.trees, List.cons.injEq] at h
    rw [rule_map_inj he X X k u h1.1 h2.1 h.1, rule_map_injs he Xs ks us h1.2 h2.2 h.2]
end
-- `lean/audit.py` reads the `end` of a `mutual` block as the end of the namespace; closing and
-- reopening the namespace here keeps its reading and Lean's the same.
end VE.Grammar

namespace VE.Grammar

variable {T K σ ρ α : Type} [Accepts K T]
variable {G G2 : Grammar K} {S : Sig T} {acts acts2 : Array (Action S)} {e : RuleMap} {X : Sym K}
variable {t : Tree T}

/-- A rule map induces an embedding, for any way `k` of turning a tree's value into a meaning. -/
theorem rule_map_embeds (k : σ → Option (Val S) → Except ρ (α × Bool × σ)) :
    e.Ok G G2 acts acts2 →
    Embeds G G2 (fun st t => k st (t.sem G S acts)) (fun st t => k st (t.sem G2 S acts2)) e.tree := by
  intro he
  refine ⟨?_, ?_, ?_⟩
  · intro w t ⟨hd, hy⟩
    obtain ⟨hd2, hy2, _⟩ := rule_map_sem he hd
    refine ⟨?_, hy2.trans hy⟩
    simpa [Sym.rename, he.start] using hd2
  · intro w t u ⟨ht, _⟩ ⟨hu, _⟩ h
    exact rule_map_inj he _ _ t u ht hu h
  · intro st w t x ⟨hd, _⟩ hm
    obtain ⟨_, _, hs⟩ := rule_map_sem he hd
    show k st ((e.tree t).sem G2 S acts2) = .ok x
    rw [hs]
    exact hm

end VE.Grammar
