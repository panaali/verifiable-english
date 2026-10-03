import Lean
import VE.Readings.Choice

/-! Facts about the names of the superposed document (docs/spec/composition-s2.md 1.4, 1.7).

A qualified name `rd-<k>-<n>` is reserved (`reservedName_qualify`), so it is never an author name; a rule name
of the chain has no `_`, so `ruleKey` and the decision predicate names built from it are injective
(`exceptedName_inj`, `offName_inj`), and the three families of decision predicate names, the bit predicates and
one another, are disjoint by their prefixes. `String.startsWith` compares through a loop private to
`Init.Data.String.Basic`; `unfold_substrEq_loop` rewrites with that loop's unfolding equation, which the kernel
checks like any other. -/
namespace VE.Readings
open Lean Meta Elab Tactic

/-- The private loop of `String.substrEq`. -/
def substrEqLoopName : Name :=
  .str (.str (.str (.num (.str (.str (.str (.str (.str .anonymous "_private") "Init") "Data") "String") "Basic") 0)
    "String") "substrEq") "loop"

/-- Rewrites the goal once with the unfolding equation of `String.substrEq`'s loop. -/
elab "unfold_substrEq_loop" : tactic => do
  let some eqn ← getUnfoldEqnFor? substrEqLoopName | throwError "no unfolding equation for substrEq's loop"
  liftMetaTactic fun g => do
    let e ← mkConstWithFreshMVarLevels eqn
    let r ← g.rewrite (← g.getType) e
    let g' ← g.replaceTargetEq r.eNew r.eqProof
    return g' :: r.mvarIds

theorem rd_startsWith (t : String) : ("rd-" ++ t).startsWith "rd-" = true := by
  let s : String := String.mk ('r' :: 'd' :: '-' :: t.data)
  have hd : ("rd-" ++ t) = s := by apply String.ext; simp [s, String.data_append]
  rw [hd]
  have hE : s.endPos = ⟨3 + String.utf8ByteSize.go t.data⟩ := by
    show (⟨String.utf8ByteSize.go ('r' :: 'd' :: '-' :: t.data)⟩ : String.Pos) = _
    have : 'r'.utf8Size = 1 := rfl
    have : 'd'.utf8Size = 1 := rfl
    have : '-'.utf8Size = 1 := rfl
    simp [String.utf8ByteSize.go]; omega
  have hn0 : s.next 0 = ⟨1⟩ := rfl
  have hn1 : s.next ⟨1⟩ = ⟨2⟩ := rfl
  have hn2 : s.next ⟨2⟩ = ⟨3⟩ := rfl
  have h0 : (0 : String.Pos) ≠ s.endPos := by rw [hE]; simp [String.Pos.ext_iff]; omega
  have h1 : (⟨1⟩ : String.Pos) ≠ s.endPos := by rw [hE]; simp [String.Pos.ext_iff]; omega
  have h2 : (⟨2⟩ : String.Pos) ≠ s.endPos := by rw [hE]; simp [String.Pos.ext_iff]; omega
  unfold String.startsWith
  have hl : "rd-".length = 3 := rfl
  have hz : ∀ p : String.Pos, ({ } : String.Pos) + p = p := fun p => by simp [String.Pos.ext_iff]
  simp only [String.toSubstring, Substring.take, hl, Substring.nextn, Substring.next, hz]
  simp only [h0, if_false, hn0, Nat.sub_zero, h1, hn1, h2, hn2]
  have hE3 : "rd-".endPos = ⟨3⟩ := rfl
  show Substring.beq _ _ = true
  simp only [Substring.beq, Substring.bsize, hE3, String.substrEq]
  have hle : 0 + 3 ≤ s.endPos.byteIdx := by rw [hE]; show 0 + 3 ≤ 3 + _; omega
  have h3 : Nat.sub 3 0 = 3 := rfl
  simp only [beq_self_eq_true, Bool.true_and, h3, decide_eq_true hle]
  have g0 : s.get { } = 'r' := rfl
  have g1 : s.get ⟨1⟩ = 'd' := rfl
  have g2 : s.get ⟨2⟩ = '-' := rfl
  have r0 : "rd-".get { } = 'r' := rfl
  have r1 : "rd-".get ⟨1⟩ = 'd' := rfl
  have r2 : "rd-".get ⟨2⟩ = '-' := rfl
  have p0 : ({ } : String.Pos) + 'r' = ⟨1⟩ := rfl
  have p1 : (⟨1⟩ : String.Pos) + 'd' = ⟨2⟩ := rfl
  have p2 : (⟨2⟩ : String.Pos) + '-' = ⟨3⟩ := rfl
  unfold_substrEq_loop
  simp only [show (0 : Nat) < 3 from by decide, dite_true, g0, r0, p0, beq_self_eq_true, Bool.true_and,
    show (3 : Nat) ≤ 3 from by decide, decide_true]
  unfold_substrEq_loop
  simp only [show (1 : Nat) < 3 from by decide, dite_true, g1, r1, p1, beq_self_eq_true, Bool.true_and]
  unfold_substrEq_loop
  simp only [show (2 : Nat) < 3 from by decide, dite_true, g2, r2, p2, beq_self_eq_true, Bool.true_and]
  unfold_substrEq_loop
  simp

/-- A qualified name is reserved: no author name is one. -/
theorem reservedName_qualify (k : Nat) (n : String) : reservedName (qualify k n) = true := by
  unfold reservedName qualify
  rw [String.append_assoc, String.append_assoc]
  exact rd_startsWith _

theorem qualify_ne {k : Nat} {n m : String} (h : reservedName m = false) : qualify k n ≠ m := by
  intro he
  have := reservedName_qualify k n
  rw [he, h] at this
  cases this

/-! ## `String.map` on characters -/

theorem pos_add_char (i : String.Pos) (c : Char) : (i + c).byteIdx = i.byteIdx + c.utf8Size := rfl

theorem utf8GetAux_append (A : List Char) (c : Char) (rest : List Char) :
    ∀ i : String.Pos, String.utf8GetAux (A ++ c :: rest) i ⟨i.byteIdx + String.utf8ByteSize.go A⟩ = c := by
  induction A with
  | nil => intro i; simp [String.utf8GetAux, String.utf8ByteSize.go]
  | cons a A ih =>
    intro i
    have ha := Char.utf8Size_pos a
    simp only [List.cons_append, String.utf8GetAux, String.utf8ByteSize.go]
    rw [if_neg (by simp [String.Pos.ext_iff]; omega)]
    have := ih (i + a)
    simp only [pos_add_char] at this
    rw [show i.byteIdx + (String.utf8ByteSize.go A + a.utf8Size) = i.byteIdx + a.utf8Size +
      String.utf8ByteSize.go A by omega]
    exact this

theorem utf8SetAux_append (c' : Char) (A : List Char) (c : Char) (rest : List Char) :
    ∀ i : String.Pos,
      String.utf8SetAux c' (A ++ c :: rest) i ⟨i.byteIdx + String.utf8ByteSize.go A⟩ = A ++ c' :: rest := by
  induction A with
  | nil => intro i; simp [String.utf8SetAux, String.utf8ByteSize.go]
  | cons a A ih =>
    intro i
    have ha := Char.utf8Size_pos a
    simp only [List.cons_append, String.utf8SetAux, String.utf8ByteSize.go]
    rw [if_neg (by simp [String.Pos.ext_iff]; omega)]
    have := ih (i + a)
    simp only [pos_add_char] at this
    rw [show i.byteIdx + (String.utf8ByteSize.go A + a.utf8Size) = i.byteIdx + a.utf8Size +
      String.utf8ByteSize.go A by omega]
    rw [this]

theorem utf8ByteSize_go_append (l l' : List Char) :
    String.utf8ByteSize.go (l ++ l') = String.utf8ByteSize.go l + String.utf8ByteSize.go l' := by
  induction l with
  | nil => simp [String.utf8ByteSize.go]
  | cons c l ih => simp [String.utf8ByteSize.go, ih]; omega

theorem mapAux_data (f : Char → Char) : ∀ (post A : List Char) (s : String),
    s.data = A ++ post → (String.mapAux f ⟨String.utf8ByteSize.go A⟩ s).data = A ++ post.map f
  | [], A, s, hs => by
    unfold String.mapAux
    rw [dif_pos]
    · simpa using hs
    · simp [String.atEnd, String.utf8ByteSize, hs]
  | c :: post, A, s, hs => by
    obtain ⟨l⟩ := s
    simp only at hs
    subst hs
    unfold String.mapAux
    have hc := Char.utf8Size_pos c
    rw [dif_neg]
    · have hg : String.get ⟨A ++ c :: post⟩ ⟨String.utf8ByteSize.go A⟩ = c := by
        have := utf8GetAux_append A c post 0
        simpa using this
      simp only [hg]
      have hset : String.set ⟨A ++ c :: post⟩ ⟨String.utf8ByteSize.go A⟩ (f c) = ⟨A ++ f c :: post⟩ := by
        have := utf8SetAux_append (f c) A c post 0
        simp only [String.set]
        simpa using this
      rw [hset]
      have hnext : String.next ⟨A ++ f c :: post⟩ ⟨String.utf8ByteSize.go A⟩ =
          ⟨String.utf8ByteSize.go (A ++ [f c])⟩ := by
        have := utf8GetAux_append A (f c) post 0
        simp only [String.next, String.get, String.Pos.ext_iff, pos_add_char]
        simp at this
        rw [this, utf8ByteSize_go_append]
        simp [String.utf8ByteSize.go]
      rw [hnext]
      have := mapAux_data f post (A ++ [f c]) ⟨A ++ f c :: post⟩ (by simp)
      rw [this]
      simp
    · simp only [String.atEnd, String.utf8ByteSize, utf8ByteSize_go_append, String.utf8ByteSize.go]
      simp; omega

theorem map_data (f : Char → Char) (s : String) : (s.map f).data = s.data.map f := by
  have := mapAux_data f s.data [] s (by simp)
  simpa [String.map, String.utf8ByteSize.go] using this

end VE.Readings
