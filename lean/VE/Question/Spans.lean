import VE.Question.Properties
import VE.EnglishGrammar.Run

/-! The emitted spans of a question answer in code points (spec 2.5, 5.1): the response converts both byte bounds
of `mapSpan` with `Run.codepointsBefore`, which is monotone and at most the question's length, so
`mapSpan_valid`'s ordered byte interval inside the question gives `start ≤ stop ≤ q.length` in code points. -/

namespace VE.Question
open VE.EnglishGrammar

/-- `codepointsBefore`'s step. -/
def cpStep (x : Nat) (acc : Nat × Nat) (c : Char) : Nat × Nat :=
  if acc.1 < x then (acc.1 + c.utf8Size, acc.2 + 1) else acc

theorem codepointsBefore_eq (s : String) (x : Nat) :
    VE.EnglishGrammar.Run.codepointsBefore s x = (s.toList.foldl (cpStep x) (0, 0)).2 := rfl

theorem cpStep_ge (x : Nat) (acc : Nat × Nat) (c : Char) : acc.2 ≤ (cpStep x acc c).2 := by
  unfold cpStep; split <;> simp

theorem cpStep_le (x : Nat) (acc : Nat × Nat) (c : Char) : (cpStep x acc c).2 ≤ acc.2 + 1 := by
  unfold cpStep; split <;> simp

theorem cp_stop (l : List Char) (x : Nat) (acc : Nat × Nat) (h : ¬ acc.1 < x) : l.foldl (cpStep x) acc = acc := by
  induction l with
  | nil => rfl
  | cons c l ih => simp only [List.foldl_cons, cpStep, h, if_false]; exact ih

theorem cp_ge (l : List Char) (x : Nat) (acc : Nat × Nat) : acc.2 ≤ (l.foldl (cpStep x) acc).2 := by
  induction l generalizing acc with
  | nil => exact Nat.le_refl _
  | cons c l ih => exact Nat.le_trans (cpStep_ge x acc c) (ih _)

theorem cp_le (l : List Char) (x : Nat) (acc : Nat × Nat) : (l.foldl (cpStep x) acc).2 ≤ acc.2 + l.length := by
  induction l generalizing acc with
  | nil => simp
  | cons c l ih =>
    simp only [List.foldl_cons, List.length_cons]
    have := ih (cpStep x acc c)
    have := cpStep_le x acc c
    omega

theorem cp_mono (l : List Char) (x y : Nat) (hxy : x ≤ y) (acc : Nat × Nat) :
    (l.foldl (cpStep x) acc).2 ≤ (l.foldl (cpStep y) acc).2 := by
  induction l generalizing acc with
  | nil => exact Nat.le_refl _
  | cons c l ih =>
    simp only [List.foldl_cons]
    by_cases hx : acc.1 < x
    · have hy : acc.1 < y := by omega
      simp only [cpStep, hx, hy, if_true]
      exact ih _
    · rw [show cpStep x acc c = acc by simp [cpStep, hx], cp_stop l x acc hx]
      exact Nat.le_trans (cpStep_ge y acc c) (cp_ge l y _)

theorem mapSpan_codepoints_valid :
  ∀ (auxs : List String) (q : String) (c : Candidate) (start stop : Nat),
    (∀ a ∈ auxs, (capitalise a).utf8ByteSize = a.utf8ByteSize) →
    c ∈ candidates auxs q → start ≤ stop → stop ≤ c.sentence.utf8ByteSize →
    let span := mapSpan c caseFrame.utf8ByteSize (start, stop)
    VE.EnglishGrammar.Run.codepointsBefore q span.1 ≤
      VE.EnglishGrammar.Run.codepointsBefore q span.2 ∧
    VE.EnglishGrammar.Run.codepointsBefore q span.2 ≤ q.length := by
  intro auxs q c start stop hcap hc hss hstop
  have ⟨h1, _⟩ := mapSpan_valid auxs q c start stop hcap hc hss hstop
  simp only [codepointsBefore_eq]
  refine ⟨cp_mono _ _ _ h1 _, ?_⟩
  have := cp_le q.toList (mapSpan c caseFrame.utf8ByteSize (start, stop)).2 (0, 0)
  simpa [String.length] using this

end VE.Question
