import VE.Grammar.Basic

/-! Trees and derivations (docs/spec/english-lean.md 2.5 and 5.3).

A derivation is a tree that the checking function `Tree.derives` accepts. That function, the
matching of the instance and `Tree.yield` are the grammar relation; nothing else defines what the
derivations of a sentence are.
-/

namespace VE.Grammar

inductive Tree (T : Type) where
  | leaf (tok : T)
  | node (rule : Nat) (kids : List (Tree T))
  deriving Repr

mutual
/-- Decides equality of two trees; the type is nested, so the instance is written by hand. -/
def Tree.decEq {T : Type} [DecidableEq T] : (t u : Tree T) → Decidable (t = u)
  | .leaf a, .leaf b =>
      if h : a = b then isTrue (h ▸ rfl) else isFalse (fun e => by cases e; exact h rfl)
  | .leaf _, .node _ _ => isFalse (fun e => by cases e)
  | .node _ _, .leaf _ => isFalse (fun e => by cases e)
  | .node r ks, .node q us =>
      if h : r = q then
        match Tree.decEqList ks us with
        | isTrue e => isTrue (by subst h; subst e; rfl)
        | isFalse e => isFalse (fun x => by cases x; exact e rfl)
      else isFalse (fun e => by cases e; exact h rfl)
/-- Decides equality of two lists of trees. -/
def Tree.decEqList {T : Type} [DecidableEq T] : (ks us : List (Tree T)) → Decidable (ks = us)
  | [], [] => isTrue rfl
  | [], _ :: _ => isFalse (fun e => by cases e)
  | _ :: _, [] => isFalse (fun e => by cases e)
  | k :: ks, u :: us =>
      match Tree.decEq k u with
      | isTrue h =>
          match Tree.decEqList ks us with
          | isTrue e => isTrue (by subst h; subst e; rfl)
          | isFalse e => isFalse (fun x => by cases x; exact e rfl)
      | isFalse h => isFalse (fun x => by cases x; exact h rfl)
end
-- `lean/audit.py` reads the `end` of a `mutual` block as the end of the namespace; closing and
-- reopening the namespace here keeps its reading and Lean's the same.
end VE.Grammar

namespace VE.Grammar

instance {T : Type} [DecidableEq T] : DecidableEq (Tree T) := Tree.decEq

variable {T K : Type} [Accepts K T]

mutual
def Tree.yield : Tree T → List T
  | .leaf tok => [tok]
  | .node _ kids => yieldAll kids
def yieldAll : List (Tree T) → List T
  | [] => []
  | t :: ts => t.yield ++ yieldAll ts
end
end VE.Grammar

namespace VE.Grammar

variable {T K : Type} [Accepts K T]

mutual
/-- The grammar relation, as a checking function. -/
def Tree.derives (G : Grammar K) : Sym K → Tree T → Bool
  | .t a, .leaf tok => Accepts.accepts a tok
  | .n A, .node r kids =>
      match G.rules[r]? with
      | some R => R.lhs == A && derivesAll G R.rhs kids
      | none => false
  | _, _ => false
def derivesAll (G : Grammar K) : List (Sym K) → List (Tree T) → Bool
  | [], [] => true
  | X :: Xs, t :: ts => t.derives G X && derivesAll G Xs ts
  | _, _ => false
end
end VE.Grammar

namespace VE.Grammar

variable {T K : Type} [Accepts K T]

def Derives (G : Grammar K) (X : Sym K) (w : List T) (t : Tree T) : Prop :=
  t.derives G X = true ∧ t.yield = w

variable {G : Grammar K} {X : Sym K} {t : Tree T}

theorem yieldAll_nil : yieldAll ([] : List (Tree T)) = [] := by simp [yieldAll]

theorem yieldAll_cons {u : Tree T} {us : List (Tree T)} : yieldAll (u :: us) = u.yield ++ yieldAll us := by
  simp [yieldAll]

theorem yield_leaf {a : T} : (Tree.leaf a).yield = [a] := by simp [Tree.yield]

theorem yield_node {r : Nat} {ks : List (Tree T)} : (Tree.node r ks).yield = yieldAll ks := by
  simp [Tree.yield]

theorem derivesAll_nil_nil : derivesAll (T := T) G [] [] = true := by simp [derivesAll]

theorem derivesAll_cons {Y : Sym K} {Ys : List (Sym K)} {u : Tree T} {us : List (Tree T)} :
    derivesAll G (Y :: Ys) (u :: us) = (u.derives G Y && derivesAll G Ys us) := by
  simp [derivesAll]

theorem derivesAll_nil_cons {u : Tree T} {us : List (Tree T)} : derivesAll G [] (u :: us) = false := by
  simp [derivesAll]

theorem derivesAll_cons_nil {Y : Sym K} {Ys : List (Sym K)} : derivesAll (T := T) G (Y :: Ys) [] = false := by
  simp [derivesAll]

theorem derives_leaf {a : K} {x : T} : (Tree.leaf x).derives G (.t a) = Accepts.accepts a x := by
  simp [Tree.derives]

theorem derives_node {A r : Nat} {ks : List (Tree T)} :
    (Tree.node r ks).derives G (.n A) =
      match G.rules[r]? with
      | some R => (R.lhs == A && derivesAll G R.rhs ks)
      | none => false := by
  simp [Tree.derives]

theorem derives_leaf_n {A : Nat} {x : T} : (Tree.leaf x).derives G (.n A) = false := by
  simp [Tree.derives]

theorem derives_node_t {a : K} {r : Nat} {ks : List (Tree T)} : (Tree.node r ks).derives G (.t a) = false := by
  simp [Tree.derives]

theorem rule_wf_of_mem {R : Rule K} (hG : G.wf = true) {r : Nat} (hr : G.rules[r]? = some R) :
    Rule.wf G R = true := by
  simp only [Grammar.wf, Bool.and_eq_true, Array.all_eq_true] at hG
  have ⟨hlt, hR⟩ := Array.getElem?_eq_some_iff.mp hr
  have := hG.2 r hlt
  rwa [hR] at this

theorem rhs_ne_nil_of_mem {R : Rule K} (hG : G.wf = true) {r : Nat} (hr : G.rules[r]? = some R) :
    R.rhs ≠ [] := by
  have h := rule_wf_of_mem hG hr
  intro he
  simp [Rule.wf, he] at h

theorem yield_ne_nil_of (hG : G.wf = true) : ∀ (X : Sym K) (t : Tree T), t.derives G X = true → t.yield ≠ []
  | .t _, .leaf _, _ => by simp [Tree.yield]
  | .n _, .leaf _, h => by simp [Tree.derives] at h
  | .t _, .node _ _, h => by simp [Tree.derives] at h
  | .n A, .node r ks, h => by
    rw [derives_node] at h
    cases hr : G.rules[r]? with
    | none => simp [hr] at h
    | some R =>
      simp only [hr, Bool.and_eq_true] at h
      have hne := rhs_ne_nil_of_mem hG hr
      match hR : R.rhs, ks, h.2 with
      | [], _, _ => exact absurd hR hne
      | Y :: Ys, [], hk => simp [derivesAll] at hk
      | Y :: Ys, k :: ks, hk =>
        rw [derivesAll_cons, Bool.and_eq_true] at hk
        have := yield_ne_nil_of hG Y k hk.1
        rw [yield_node, yieldAll_cons]
        intro he
        exact this (List.append_eq_nil_iff.mp he).1

/-- No empty rule: a derivation covers at least one token. -/
theorem yield_ne_nil : G.wf = true → t.derives G X = true → t.yield ≠ [] :=
  fun hG h => yield_ne_nil_of hG X t h

end VE.Grammar
