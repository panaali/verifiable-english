import VE.Acts.Read
import Std.Data.HashSet.Lemmas
import Std.Data.HashMap.Lemmas

/-! First occurrences and their places, by hashing (ap-parse-index).

`firsts` and `List.idxOf` compare each element with the ones before it, so numbering the nonterminals of a rule table
(`VE.Acts.closed`, `VE.Acts.build`) costs the square of its size: 9.5 s of CPU at 128 frames (REPORT). `firstsGo`
and `idxGo` give the same answers (`firstsGo_eq`, `idxGo_getD`) with one hash lookup per element. The act grammar's
`@[csimp]` lemmas use them, so compiled code runs them and every definition and statement stays as written.
-/

namespace VE.Acts
open Std

variable {α : Type} [DecidableEq α] [Hashable α]

/-- The first occurrences of `l`'s elements that are not in `seen`, in order. -/
def firstsGo (seen : HashSet α) : List α → List α
  | [] => []
  | x :: xs => if seen.contains x then firstsGo seen xs else x :: firstsGo (seen.insert x) xs

/-- Each element of `l` mapped to the place of its first occurrence, counted from `i`, unless `m` has it. -/
def idxGo : List α → Nat → HashMap α Nat → HashMap α Nat
  | [], _, m => m
  | x :: xs, i, m => idxGo xs (i + 1) (m.insertIfNew x i)

omit [Hashable α] in
theorem firsts_filter (p : α → Bool) : ∀ l : List α, firsts (l.filter p) = (firsts l).filter p
  | [] => rfl
  | x :: xs => by
    by_cases hx : p x = true
    · simp only [List.filter_cons, hx, if_true, firsts, firsts_filter p xs, List.filter_filter]
      congr 1
      exact List.filter_congr fun y _ => Bool.and_comm _ _
    · simp only [List.filter_cons, hx, if_false, firsts, firsts_filter p xs, Bool.false_eq_true, List.filter_filter]
      refine List.filter_congr fun y _ => ?_
      by_cases hy : p y = true
      · have : y ≠ x := fun h => hx (h ▸ hy)
        simp [hy, this]
      · simp [hy]

theorem firstsGo_eq : ∀ (seen : HashSet α) (l : List α), firstsGo seen l = firsts (l.filter (!seen.contains ·))
  | _, [] => rfl
  | seen, x :: xs => by
    unfold firstsGo
    by_cases hx : seen.contains x = true
    · simp only [hx, if_true, List.filter_cons, Bool.not_true, Bool.false_eq_true]
      exact firstsGo_eq seen xs
    · have hp : (!seen.contains x) = true := by cases h : seen.contains x; rfl; exact absurd h hx
      rw [if_neg hx, List.filter_cons_of_pos (p := fun z => !seen.contains z) hp, firstsGo_eq _ xs]
      simp only [firsts]
      rw [← firsts_filter, List.filter_filter]
      congr 2
      refine List.filter_congr fun y _ => ?_
      simp only [HashSet.contains_insert, Bool.not_or, ne_eq, decide_not]
      by_cases h : x = y
      · subst h; simp
      · have h' : ¬y = x := Ne.symm h
        simp [h, h']

theorem firstsGo_empty (l : List α) : firstsGo ∅ l = firsts l := by
  rw [firstsGo_eq]; simp only [HashSet.contains_empty, Bool.not_false]
  rw [List.filter_eq_self.mpr (fun _ _ => rfl)]

theorem idxGo_get? : ∀ (l : List α) (i : Nat) (m : HashMap α Nat) (y : α), (idxGo l i m)[y]? =
    match m[y]? with | some v => some v | none => if y ∈ l then some (i + l.idxOf y) else none
  | [], _, m, y => by rw [idxGo]; rcases m[y]? with _ | v <;> simp
  | x :: xs, i, m, y => by
    rw [idxGo, idxGo_get? xs (i + 1), HashMap.getElem?_insertIfNew]
    rcases hm : m[y]? with _ | v
    · by_cases hxy : x = y
      · subst hxy
        have : x ∉ m := fun h => by rw [HashMap.mem_iff_isSome_getElem?, hm] at h; exact Bool.noConfusion h
        rw [if_pos ⟨beq_self_eq_true x, this⟩, if_pos List.mem_cons_self]
        simp only [List.idxOf_cons, beq_self_eq_true, cond_true, Nat.add_zero]
      · have hb : (x == y) = false := by simpa using hxy
        simp only [hb, if_false, Bool.false_eq_true, false_and, List.mem_cons, Ne.symm hxy,
          false_or, List.idxOf_cons, cond_false]
        by_cases hy : y ∈ xs <;> simp only [hy, if_true, if_false]
        exact congrArg some (by omega)
    · have hy : y ∈ m := by simp [HashMap.mem_iff_isSome_getElem?, hm]
      by_cases hxy : x = y
      · subst hxy; simp [hy]
      · simp [hxy]

/-- The place of `y`'s first occurrence in `l`, and `l.length` when it does not occur: `l.idxOf y`. -/
theorem idxGo_getD (l : List α) (y : α) : (idxGo l 0 ∅).getD y l.length = l.idxOf y := by
  rw [HashMap.getD_eq_getD_getElem?, idxGo_get?]
  simp only [HashMap.getElem?_empty]
  by_cases h : y ∈ l
  · simp [h]
  · simp [h, List.idxOf_eq_length h]

end VE.Acts
