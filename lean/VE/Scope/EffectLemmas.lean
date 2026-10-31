import VE.Scope.Govern
import VE.Readings.Strings

/-! Decoder and loop lemmas for spec 5.4's SC-2 statements (sc-2c): the base guard decoder's value does not depend on
    its node count or depth fuel; a scalar or term position `substOwn` leaves, for any guard that decodes as a formula;
    and a loop fails only with an error of its body. `Theorems.lean` states 5.4's theorems over them. -/

namespace VE.Scope
open Lean
open VE.Norms.Wire (budgetFormula budgetTerm)

/-! The base guard decoder -/

theorem budgetTerm_ok {k : Nat} {j : Json} {t : VE.Term} {c : Nat} (h : budgetTerm k j = .ok (t, c)) :
    VE.Bridge.decodeTerm j = .ok t ∧ c = k + 1 := by
  unfold budgetTerm at h
  cases hd : VE.Bridge.decodeTerm j with
  | error e => by_cases hk : k + 1 > VE.Limits.maxNodes <;> simp_all [bind, Except.bind, pure, Except.pure]
  | ok d =>
    by_cases hk : k + 1 > VE.Limits.maxNodes <;> simp [hk, hd, bind, Except.bind, pure, Except.pure] at h
    cases d <;> simp at h <;> (try split at h) <;> simp_all

theorem budgetTerm_val {k k' : Nat} {j : Json} {t t' : VE.Term} {c c' : Nat}
    (h : budgetTerm k j = .ok (t, c)) (h' : budgetTerm k' j = .ok (t', c')) : t = t' := by
  have := (budgetTerm_ok h).1; have := (budgetTerm_ok h').1; simp_all

/-- The decoded formula is the same whatever the node count or depth fuel, when both decodes succeed. -/
theorem budgetFormula_val : ∀ (n n' k k' : Nat) (j : Json) (φ ψ : VE.Formula) (c c' : Nat),
    budgetFormula n k j = .ok (φ, c) → budgetFormula n' k' j = .ok (ψ, c') → φ = ψ
  | 0, _, _, _, _, _, _, _, _, h, _ => by simp [budgetFormula, throw, throwThe, MonadExceptOf.throw] at h
  | _, 0, _, _, _, _, _, _, _, _, h => by simp [budgetFormula, throw, throwThe, MonadExceptOf.throw] at h
  | n + 1, n' + 1, k, k', j, φ, ψ, c, c', h, h' => by
    unfold budgetFormula at h h'
    cases j <;> simp only [Json.getArr?, bind, Except.bind, pure, Except.pure, throw, throwThe, MonadExceptOf.throw] at h h' <;>
      split at h <;> (try (simp at h; done)) <;> split at h' <;> (try (simp at h'; done))
    rename_i xs _ _
    split at h <;> rename_i heq <;> simp only [heq] at h' <;> (repeat' (first | split at h | split at h')) <;>
      simp_all
    all_goals (obtain ⟨rfl, -⟩ := h; obtain ⟨rfl, -⟩ := h'; congr 1 <;>
      first | (apply budgetTerm_val <;> assumption) | (apply budgetFormula_val <;> assumption))
theorem decodeBudgeted_ok {j : Json} {φ : VE.Formula} (h : VE.Norms.Wire.decodeBudgeted j = .ok φ) :
    ∃ c, budgetFormula VE.Limits.maxDepth 0 j = .ok (φ, c) := by
  unfold VE.Norms.Wire.decodeBudgeted at h
  cases hb : budgetFormula VE.Limits.maxDepth 0 j with
  | error e => simp [hb, Functor.map, Except.map] at h
  | ok p => simp [hb, Functor.map, Except.map] at h; exact ⟨p.2, by rw [← h]⟩

/-! `substOwn` at a position the decoder reads as a scalar or a term -/

/-- A scalar `substOwn` writes is the value as written, for any guard: `own` became a guard array, not a scalar. -/
theorem substOwn_scalar {g₁ : Json} (g₂ : Json) (hg : ∃ a, g₁ = .arr a) :
    ∀ (m : Nat) (x v : Json), (∀ a, v ≠ .arr a) → (∀ o, v ≠ .obj o) → substOwn g₁ m x = v → substOwn g₂ m x = v
  | 0, _, _, _, _, h => h
  | m + 1, x, v, ha, ho, h => by
    obtain ⟨a, rfl⟩ := hg
    cases x with
    | str s' =>
      by_cases hs : s' = "own"
      · simp only [substOwn, hs] at h; exact absurd h.symm (ha a)
      · simp_all [substOwn]
    | arr => simp only [substOwn] at h; exact absurd h.symm (ha _)
    | obj => simp only [substOwn] at h; exact absurd h.symm (ho _)
    | _ => simp_all [substOwn]

theorem substOwn_term {g₁ : Json} (g₂ : Json) (hg : ∃ a, g₁ = .arr a)
    (ht : ∀ t, VE.Bridge.decodeTerm g₁ ≠ .ok t) :
    ∀ (m : Nat) (x : Json) (t : VE.Term), VE.Bridge.decodeTerm (substOwn g₁ m x) = .ok t →
      substOwn g₂ m x = substOwn g₁ m x
  | 0, _, _, _ => rfl
  | m + 1, x, t, h => by
    cases x with
    | str s => by_cases hs : s = "own" <;> simp_all [substOwn, VE.Bridge.decodeTerm, Json.getArr?, bind, Except.bind]
    | arr xs =>
      rcases xs with ⟨l⟩
      rcases l with _ | ⟨y0, _ | ⟨y1, _ | ⟨y2, l⟩⟩⟩ <;>
        simp [substOwn, VE.Bridge.decodeTerm, Json.getArr?, bind, Except.bind, pure, Except.pure, throw, throwThe, MonadExceptOf.throw] at h ⊢
      split at h <;> rename_i heq <;> simp only [List.cons.injEq, and_true] at heq <;> try simp at h
      · rename_i i
        cases i <;> simp [Json.getNat?, throw, throwThe, MonadExceptOf.throw] at h
        rw [heq.1, heq.2]
        exact ⟨substOwn_scalar g₂ hg m y0 _ (by simp) (by simp) heq.1,
          substOwn_scalar g₂ hg m y1 _ (by simp) (by simp) heq.2⟩
      · rw [heq.1, heq.2]
        exact ⟨substOwn_scalar g₂ hg m y0 _ (by simp) (by simp) heq.1,
          substOwn_scalar g₂ hg m y1 _ (by simp) (by simp) heq.2⟩
    | obj => simp [substOwn, VE.Bridge.decodeTerm, Json.getArr?, bind, Except.bind] at h
    | _ => rfl

theorem substOwn_str {g : Json} (hg : ∃ a, g = .arr a) :
    ∀ (m : Nat) (x : Json) (s : String), substOwn g m x = .str s → x = .str s
  | 0, _, _, h => h
  | m + 1, x, s, h => by
    obtain ⟨a, rfl⟩ := hg
    cases x with
    | str s' => by_cases hs : s' = "own" <;> simp_all [substOwn]
    | arr => simp [substOwn] at h
    | obj => simp [substOwn] at h
    | _ => simp [substOwn] at h

theorem substOwn_str_self (g : Json) (s : String) (hs : s ≠ "own") : ∀ m, substOwn g m (.str s) = .str s
  | 0 => rfl
  | _ + 1 => by simp [substOwn, hs]

theorem budgetFormula_arr {n k : Nat} {j : Json} {r : VE.Formula × Nat} (h : budgetFormula n k j = .ok r) :
    ∃ a, j = .arr a := by
  cases n with
  | zero => simp [budgetFormula, throw, throwThe, MonadExceptOf.throw] at h
  | succ n =>
    unfold budgetFormula at h
    cases j <;> simp only [Json.getArr?, bind, Except.bind, pure, Except.pure, throw, throwThe,
      MonadExceptOf.throw] at h <;> first | exact ⟨_, rfl⟩ | (split at h <;> simp at h)

theorem budgetFormula_not_term {n k : Nat} {j : Json} {r : VE.Formula × Nat} (h : budgetFormula n k j = .ok r)
    (t : VE.Term) : VE.Bridge.decodeTerm j ≠ .ok t := by
  intro ht
  obtain ⟨⟨l⟩, rfl⟩ := budgetFormula_arr h
  cases n with
  | zero => simp [budgetFormula, throw, throwThe, MonadExceptOf.throw] at h
  | succ n =>
    unfold VE.Bridge.decodeTerm at ht
    simp only [Json.getArr?, bind, Except.bind, pure, Except.pure] at ht
    unfold budgetFormula at h
    simp only [Json.getArr?, bind, Except.bind, pure, Except.pure, throw, throwThe, MonadExceptOf.throw] at h
    split at ht <;> (try simp [throw, throwThe, MonadExceptOf.throw] at ht) <;> (split at h <;> simp at h)

theorem elt_str {g₁ : Json} (g₂ : Json) (hg : ∃ a, g₁ = .arr a) {m : Nat} {y : Json} {s : String}
    (hv : substOwn g₁ m y = .str s) : substOwn g₂ m y = substOwn g₁ m y := by
  rw [hv]; exact substOwn_scalar g₂ hg m y _ (by simp) (by simp) hv

theorem elt_term {g₁ : Json} (g₂ : Json) (hg : ∃ a, g₁ = .arr a) (ht : ∀ t, VE.Bridge.decodeTerm g₁ ≠ .ok t)
    {m k : Nat} {y : Json} {p : VE.Term × Nat} (hv : budgetTerm k (substOwn g₁ m y) = .ok p) :
    substOwn g₂ m y = substOwn g₁ m y :=
  substOwn_term g₂ hg ht m y p.1 (budgetTerm_ok hv).1

/-! Loops -/

/-- A loop over a list fails only with an error of its body. -/
theorem forIn_error {α : Type} (P : String → Prop) (f : α → PUnit.{1} → Except String (ForInStep PUnit.{1}))
    (hf : ∀ x e, f x PUnit.unit = .error e → P e) :
    ∀ (l : List α) (e : String), forIn l PUnit.unit f = .error e → P e
  | [], e, h => by simp [pure, Except.pure] at h
  | x :: l, e, h => by
    simp only [List.forIn_cons, bind, Except.bind] at h
    cases hx : f x PUnit.unit with
    | error e' => rw [hx] at h; cases h; exact hf x e hx
    | ok r => rw [hx] at h; cases r with
      | done => simp [pure, Except.pure] at h
      | yield => exact forIn_error P f hf l e h

theorem scopeOrder_prefix (a b c : String) :
    (toString "ScopeOrder: " ++ toString a ++ toString ": " ++ toString b ++ toString ", " ++ toString c).startsWith
      "ScopeOrder" = true := by
  have := VE.Readings.startsWith_append_ascii "ScopeOrder" (": " ++ a ++ ": " ++ b ++ ", " ++ c) (by decide)
  simpa only [toString, String.append_assoc] using this

end VE.Scope
