import VE.Grammar.Derives

/-! Meanings (docs/spec/english-lean.md 2.7 and 5.5).

A signature gives semantic types and their values; an action maps the values of a rule's children to
the value of its left-hand side. The value of a tree carries its type, so it does not depend on the
type table `ty`; `Grammar.typed` checks that every rule's action fits both sides of the rule, and under
it every derivation has a value of the type of its symbol (`sem_total`).
-/

namespace VE.Grammar

/-- A signature over the token type `T`. -/
structure Sig (T : Type) where
  Ty : Type
  decEq : DecidableEq Ty
  Sem : Ty → Type
  tok : Ty
  leaf : T → Sem tok

variable {T K : Type}

/-- The arguments of an action: one value per type. -/
def Args (S : Sig T) : List S.Ty → Type
  | [] => Unit
  | τ :: τs => S.Sem τ × Args S τs

structure Action (S : Sig T) where
  args : List S.Ty
  out : S.Ty
  run : Args S args → S.Sem out

def symTy (S : Sig T) (ty : Nat → S.Ty) : Sym K → S.Ty
  | .t _ => S.tok
  | .n A => ty A

/-- Each rule's action exists and fits both sides of the rule: its argument types are the types of the
right-hand symbols and its result type is the type of the left-hand side, compared by `S.decEq`. -/
def Grammar.typed (G : Grammar K) (S : Sig T) (ty : Nat → S.Ty) (acts : Array (Action S)) : Bool :=
  G.rules.all fun R =>
    match acts[R.act]? with
    | some a =>
      @decide (a.args = R.rhs.map (symTy S ty)) (@instDecidableEqList _ S.decEq _ _) &&
      @decide (a.out = ty R.lhs) (S.decEq _ _)
    | none => false

/-- A value with its type. -/
abbrev Val (S : Sig T) := (τ : S.Ty) × S.Sem τ

/-- The values as arguments of the given types, when their types are exactly those. -/
def toArgs (S : Sig T) : (τs : List S.Ty) → List (Val S) → Option (Args S τs)
  | [], [] => some ()
  | τ :: τs, v :: vs =>
    match S.decEq v.1 τ with
    | isTrue h => (toArgs S τs vs).map fun xs => (cast (congrArg S.Sem h) v.2, xs)
    | isFalse _ => none
  | _, _ => none

mutual
def Tree.sem (G : Grammar K) (S : Sig T) (acts : Array (Action S)) : Tree T → Option (Val S)
  | .leaf tok => some ⟨S.tok, S.leaf tok⟩
  | .node r kids =>
      match G.rules[r]? with
      | some R =>
          match acts[R.act]? with
          | some a =>
              match semAll G S acts kids with
              | some vs => (toArgs S a.args vs).map fun xs => ⟨a.out, a.run xs⟩
              | none => none
          | none => none
      | none => none
def semAll (G : Grammar K) (S : Sig T) (acts : Array (Action S)) : List (Tree T) → Option (List (Val S))
  | [] => some []
  | t :: ts =>
      match t.sem G S acts, semAll G S acts ts with
      | some v, some vs => some (v :: vs)
      | _, _ => none
end
end VE.Grammar

namespace VE.Grammar

variable {T K : Type} [Accepts K T]
variable {G : Grammar K} {S : Sig T} {ty : Nat → S.Ty} {acts : Array (Action S)} {X : Sym K} {t : Tree T}

omit [Accepts K T] in
theorem typed_rule (h : G.typed S ty acts = true) {r : Nat} {R : Rule K} (hr : G.rules[r]? = some R) :
    ∃ a, acts[R.act]? = some a ∧ a.args = R.rhs.map (symTy S ty) ∧ a.out = ty R.lhs := by
  unfold Grammar.typed at h
  rw [Array.all_eq_true] at h
  obtain ⟨hlt, hR⟩ := Array.getElem?_eq_some_iff.mp hr
  have := h r hlt
  rw [hR] at this
  cases ha : acts[R.act]? with
  | none => simp [ha] at this
  | some a =>
    rw [ha] at this
    simp only [Bool.and_eq_true] at this
    exact ⟨a, rfl, @of_decide_eq_true _ (@instDecidableEqList _ S.decEq _ _) this.1,
      @of_decide_eq_true _ (S.decEq _ _) this.2⟩

omit [Accepts K T] in
theorem toArgs_some : ∀ (Xs : List (Sym K)) (vs : List (Val S)),
    (∀ i (h : i < Xs.length), ∃ v : S.Sem (symTy S ty Xs[i]), vs[i]? = some ⟨symTy S ty Xs[i], v⟩) → vs.length = Xs.length →
    ∃ xs, toArgs S (Xs.map (symTy S ty)) vs = some xs
  | [], [], _, _ => ⟨(), rfl⟩
  | [], _ :: _, _, h => by simp at h
  | _ :: _, [], _, h => by simp at h
  | X :: Xs, v :: vs, hv, hl => by
    obtain ⟨v0, hv0⟩ := hv 0 (by simp)
    simp at hv0
    subst hv0
    obtain ⟨xs, hxs⟩ := toArgs_some Xs vs (fun i h => by
      obtain ⟨u, hu⟩ := hv (i + 1) (by simp; omega)
      exact ⟨u, by simpa using hu⟩) (by simpa using hl)
    refine ⟨(v0, xs), ?_⟩
    simp only [List.map_cons, toArgs]
    split
    · rename_i h _
      simp [hxs]
    · rename_i h _
      exact absurd rfl h

mutual
theorem sem_total_of : ∀ (X : Sym K) (t : Tree T), t.derives G X = true → G.typed S ty acts = true →
    ∃ v : S.Sem (symTy S ty X), t.sem G S acts = some ⟨symTy S ty X, v⟩
  | .t _, .leaf tok, _, _ => ⟨S.leaf tok, by simp [Tree.sem, symTy]⟩
  | .n _, .leaf _, h, _ => by simp [Tree.derives] at h
  | .t _, .node _ _, h, _ => by simp [Tree.derives] at h
  | .n A, .node r kids, h, hT => by
    rw [derives_node] at h
    cases hr : G.rules[r]? with
    | none => simp [hr] at h
    | some R =>
      simp only [hr, Bool.and_eq_true, beq_iff_eq] at h
      obtain ⟨a, ha, hargs, hout⟩ := typed_rule hT hr
      obtain ⟨vs, hvs, hlen, hty⟩ := semAll_total_of R.rhs kids h.2 hT
      obtain ⟨xs, hxs⟩ := toArgs_some (S := S) (ty := ty) R.rhs vs hty hlen
      obtain ⟨args, out, run⟩ := a
      simp only at hargs hout
      subst hargs hout
      obtain ⟨hA, _⟩ := h
      subst hA
      refine ⟨run xs, ?_⟩
      simp [Tree.sem, hr, ha, hvs, hxs, symTy]
theorem semAll_total_of : ∀ (Xs : List (Sym K)) (kids : List (Tree T)), derivesAll G Xs kids = true →
    G.typed S ty acts = true →
    ∃ vs, semAll G S acts kids = some vs ∧ vs.length = Xs.length ∧
      ∀ i (h : i < Xs.length), ∃ v : S.Sem (symTy S ty Xs[i]), vs[i]? = some ⟨symTy S ty Xs[i], v⟩
  | [], [], _, _ => ⟨[], by simp [semAll]⟩
  | [], _ :: _, h, _ => by simp [derivesAll] at h
  | _ :: _, [], h, _ => by simp [derivesAll] at h
  | X :: Xs, k :: ks, h, hT => by
    rw [derivesAll_cons, Bool.and_eq_true] at h
    obtain ⟨v, hv⟩ := sem_total_of X k h.1 hT
    obtain ⟨vs, hvs, hlen, hty⟩ := semAll_total_of Xs ks h.2 hT
    refine ⟨⟨symTy S ty X, v⟩ :: vs, by simp [semAll, hv, hvs], by simp [hlen], ?_⟩
    intro i hi
    cases i with
    | zero => exact ⟨v, by simp⟩
    | succ i =>
      obtain ⟨u, hu⟩ := hty i (by simp at hi; omega)
      exact ⟨u, by simpa using hu⟩
end
end VE.Grammar

namespace VE.Grammar

variable {T K : Type} [Accepts K T]
variable {G : Grammar K} {S : Sig T} {ty : Nat → S.Ty} {acts : Array (Action S)} {X : Sym K} {t : Tree T}

theorem sem_total : G.typed S ty acts = true → t.derives G X = true →
    ∃ v : S.Sem (symTy S ty X), t.sem G S acts = some ⟨symTy S ty X, v⟩ :=
  fun hT h => sem_total_of X t h hT

end VE.Grammar
