import Lean

/-! `p.isPrefixOf (p ++ t)` (8.3, `plain_wellFormed`: an error that starts with `ResourceLimit: `). Core Lean has
no lemma about `String.isPrefixOf`; its comparison loop is private to `Init.Data.String.Basic`, so
`pwf_unfold_substrEq_loop` rewrites with that loop's unfolding equation (the kernel checks it like any other), as
`VE.Readings.unfold_substrEq_loop` does; right clauses do not import `VE.Readings` (right-clauses.md 0). -/
namespace VE.RightClauses.PWF
open Lean Meta Elab Tactic

/-- The private loop of `String.substrEq`. -/
def substrEqLoopName : Name :=
  .str (.str (.str (.num (.str (.str (.str (.str (.str .anonymous "_private") "Init") "Data") "String") "Basic") 0)
    "String") "substrEq") "loop"

/-- Rewrites the goal once with the unfolding equation of `String.substrEq`'s loop. -/
elab "pwf_unfold_substrEq_loop" : tactic => do
  let some eqn ← getUnfoldEqnFor? substrEqLoopName | throwError "no unfolding equation for substrEq's loop"
  liftMetaTactic fun g => do
    let e ← mkConstWithFreshMVarLevels eqn
    let r ← g.rewrite (← g.getType) e
    let g' ← g.replaceTargetEq r.eNew r.eqProof
    return g' :: r.mvarIds

theorem size_append (l l' : List Char) :
    String.utf8ByteSize.go (l ++ l') = String.utf8ByteSize.go l + String.utf8ByteSize.go l' := by
  induction l with
  | nil => simp [String.utf8ByteSize.go]
  | cons c l ih => simp [String.utf8ByteSize.go, ih]; omega

local notation "sz" => String.utf8ByteSize.go

theorem byteIdx_add_char (i : String.Pos) (c : Char) : (i + c).byteIdx = i.byteIdx + c.utf8Size := rfl

theorem size_cons (c : Char) (l : List Char) : sz (c :: l) = c.utf8Size + sz l := by
  simp [String.utf8ByteSize.go]; omega

theorem getAux_lt : ∀ (l : List Char) (i o : String.Pos), o.byteIdx < i.byteIdx → String.utf8GetAux l i o = default
  | [], _, _, _ => rfl
  | d :: l, i, o, h => by
    simp only [String.utf8GetAux]
    rw [if_neg (by intro he; rw [he] at h; omega)]
    exact getAux_lt l _ o (by rw [byteIdx_add_char]; omega)

theorem getAux_append :
    ∀ (cs ds : List Char) (i o : String.Pos), o.byteIdx < i.byteIdx + sz cs →
      String.utf8GetAux (cs ++ ds) i o = String.utf8GetAux cs i o
  | [], ds, i, o, h => by
    simp only [String.utf8ByteSize.go, Nat.add_zero] at h
    rw [List.nil_append, getAux_lt ds i o h, getAux_lt [] i o h]
  | c :: cs, ds, i, o, h => by
    simp only [List.cons_append, String.utf8GetAux]
    split
    · rfl
    · apply getAux_append
      rw [byteIdx_add_char]; rw [size_cons] at h; omega

theorem getAux_at (A : List Char) (c : Char) (R : List Char) (i : Nat) :
    String.utf8GetAux (A ++ c :: R) ⟨i⟩ ⟨i + sz A⟩ = c := by
  induction A generalizing i with
  | nil => simp [String.utf8GetAux, String.utf8ByteSize.go]
  | cons a A ih =>
    have ha := Char.utf8Size_pos a
    simp only [List.cons_append, String.utf8GetAux]
    rw [if_neg (by simp [String.Pos.ext_iff, size_cons]; omega)]
    have := ih (i + a.utf8Size)
    rw [show i + sz (a :: A) = i + a.utf8Size + sz A by rw [size_cons]; omega]
    exact this

theorem get_append (p t : String) (o : String.Pos) (h : o.byteIdx < p.endPos.byteIdx) :
    (p ++ t).get o = p.get o := by
  obtain ⟨cs⟩ := p
  obtain ⟨ds⟩ := t
  exact getAux_append cs ds 0 o (by simpa [String.endPos, String.utf8ByteSize] using h)

theorem endPos_append (p t : String) : (p ++ t).endPos.byteIdx = p.endPos.byteIdx + t.endPos.byteIdx := by
  obtain ⟨cs⟩ := p; obtain ⟨ds⟩ := t
  show sz (cs ++ ds) = sz cs + sz ds
  exact size_append cs ds

theorem substrEq_prefix (p t : String) :
    ∀ (R A : List Char), p.data = A ++ R → String.substrEq p ⟨sz A⟩ (p ++ t) ⟨sz A⟩ (sz R) = true
  | [], A, hp => by
    have hpe : p.endPos.byteIdx = sz A := by
      obtain ⟨d⟩ := p; simp only [List.append_nil] at hp; subst hp; rfl
    unfold String.substrEq
    pwf_unfold_substrEq_loop
    simp only [String.utf8ByteSize.go, Nat.add_zero, hpe, Nat.le_refl, decide_true, endPos_append,
      Nat.le_add_right, Bool.true_and, Nat.lt_irrefl, dite_false]
  | c :: R, A, hp => by
    have ih := substrEq_prefix p t R (A ++ [c]) (by rw [hp]; simp)
    have hsA : sz (A ++ [c]) = sz A + c.utf8Size := by rw [size_append, size_cons]; simp [String.utf8ByteSize.go]
    have hpe : p.endPos.byteIdx = sz A + sz (c :: R) := by
      obtain ⟨d⟩ := p; simp only at hp; subst hp; exact size_append A (c :: R)
    have hc := Char.utf8Size_pos c
    have hcR : sz (c :: R) = c.utf8Size + sz R := size_cons c R
    unfold String.substrEq at ih ⊢
    simp only [Bool.and_eq_true, decide_eq_true_eq, endPos_append] at ih ⊢
    refine ⟨⟨by omega, by omega⟩, ?_⟩
    pwf_unfold_substrEq_loop
    rw [dif_pos (by show sz A < sz A + sz (c :: R); omega)]
    have g1 : p.get ⟨sz A⟩ = c := by
      obtain ⟨d⟩ := p; simp only at hp; subst hp
      have := getAux_at A c R 0
      simpa using this
    have g2 : (p ++ t).get ⟨sz A⟩ = c := by rw [get_append p t _ (by show sz A < _; omega)]; exact g1
    simp only [g1, g2, beq_self_eq_true, Bool.true_and]
    have e1 : (⟨sz A⟩ : String.Pos) + c = ⟨sz (A ++ [c])⟩ := by
      apply String.Pos.ext; rw [byteIdx_add_char, hsA]
    have e2 : (⟨sz A + sz (c :: R)⟩ : String.Pos) = ⟨sz (A ++ [c]) + sz R⟩ := by
      rw [hsA, hcR]; congr 1; omega
    rw [e1, e2]; exact ih.2

theorem isPrefixOf_append (p t : String) : p.isPrefixOf (p ++ t) = true := by
  have := substrEq_prefix p t p.data [] (by simp)
  simpa [String.isPrefixOf, String.endPos, String.utf8ByteSize, String.utf8ByteSize.go] using this

end VE.RightClauses.PWF
