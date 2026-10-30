import VE.Arith.Deciding
import VE.Arith.Examples

/-! The fixtures of spec 12.5's `decidingValue`, each on its deciding and its undecided side, at and around the ends of
the range and the budget; and M-6 (13.3): VE's `prime` against `IsPrime` on 0 through 400. -/

namespace VE.Arith.Examples
open VE.Arith

/-- `IsPrime` as a Boolean: p is at least 2 and no d from 2 through p − 1 leaves remainder 0. -/
def isPrimeB (p : Nat) : Bool := 2 ≤ p && (List.range p).all fun d => d < 2 || p % d != 0

theorem isPrimeB_iff (p : Nat) : isPrimeB p = true ↔ IsPrime p := by
  simp only [isPrimeB, IsPrime, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.mem_range,
    Bool.or_eq_true, bne_iff_ne, ne_eq, Nat.dvd_iff_mod_eq_zero]
  exact and_congr_right fun _ => ⟨fun H d h2 hd => (H d hd).resolve_left (by omega),
    fun H d hd => (Nat.lt_or_ge d 2).elim Or.inl fun h2 => Or.inr (H d h2 hd)⟩

instance decIsPrime (p : Nat) : Decidable (IsPrime p) := decidable_of_iff _ (isPrimeB_iff p)

#guard [0, 1, 2, 3, 4, 397, 399, 400].map (decide <| IsPrime ·) = [false, false, true, true, false, true, false, false]

/-- `prime` over the definitions `D`, by the evaluator within the default budget. -/
def vePrime (D : Defs) (p : Nat) : Option Bool := (decideBounded D maxSteps (.call "prime" [.num p])).map (·.1)

/-- On 0 through `n` − 1: the values where `prime` over `D` agrees with `IsPrime`, and the primes among them. -/
def agreeCount (D : Defs) (n : Nat) : Nat × Nat :=
  (((List.range n).filter fun p => vePrime D p == some (decide (IsPrime p))).length,
    ((List.range n).filter (decide <| IsPrime ·)).length)

/-! M-6: VE's `prime` agrees with `IsPrime` at all 401 values from 0 through 400, 78 of them prime. A body that also
tries p itself ("from 2 through p") disagrees at each of the 78 primes. -/
#guard agreeCount primeDefs 401 = (401, 78)
#guard agreeCount [.pred "prime" 1 (.and (.le (.num 2) (.var 0))
    (.not (.exFromTo (.num 2) (.var 0) (.dvd (.var 0) (.var 1)))))] 401 = (323, 78)

/-- Whether the evaluator stops the statement's outermost bounded quantifier early: a failed "for every" or a true
"there is". -/
def stops (D : Defs) (l : Nat) (φ : Formula) : Bool := match φ, decideBounded D l φ with
  | .allFromTo .., some (false, _) | .exFromTo .., some (true, _) => true
  | _, _ => false

/-- At every budget from 0 through `n`, a deciding value exactly when the evaluator stops early. -/
def agreesUpTo (D : Defs) (φ : Formula) (n : Nat) : Bool :=
  (List.range (n + 1)).all fun l => (decidingValue D l φ).isSome == stops D l φ

def exPrime (lo hi : Term) : Formula := .exFromTo lo hi (.call "prime" [.var 0])

/-! M-5 fails at n = 1 ("fails at n = 1", 13.3): unknown below its 33 units, then 1. -/
#guard [32, 33, 34, maxSteps].map (decidingValue primeDefs · m5) = [none, some 1, some 1, some 1]

/-! The first witness, not the last (8 … 20 has 11, 13, 17 and 19), at the start of the range, at its end, alone in a
one-value range, and none when no value is prime. Range ends are terms, evaluated as the evaluator does. -/
#guard [exPrime (lit 8) (lit 20), exPrime (lit 2) (lit 20), exPrime (lit 14) (lit 17), exPrime (lit 7) (lit 7),
    exPrime (lit 8) (lit 8), exPrime (lit 8) (lit 10), exPrime (.add (lit 3) (lit 1)) (.mul (lit 2) (lit 4))].map
      (decidingValue primeDefs maxSteps) = [some 11, some 2, some 17, some 7, none, none, some 5]

/-! The first counterexample, not the last: 7 of 1 … 10 is the first above 6; at the end of the range (10), at its start
(3), none when every value passes (1 … 9), and over negative integers. -/
#guard [(1, 10, 6), (1, 10, 9), (1, 9, 9), (-3, 3, -2)].map (fun (a, b, c) =>
    decidingValue [] maxSteps (.allFromTo (lit a) (lit b) (.le (.var 0) (lit c)))) = [some 7, some 10, none, some (-1)]
#guard decidingValue [] maxSteps (.allFromTo (lit 3) (lit 10) (.le (lit 4) (.var 0))) = some 3
#guard decidingValue [] maxSteps (.exFromTo (lit (-3)) (lit 3) (.lt (.var 0) (lit 0))) = some (-3)

/-! None otherwise: an empty range (5 … 4) of either quantifier, a true "for every", a false "there is", and a
statement whose outermost node is no bounded quantifier, though one is inside it. -/
#guard [.allFromTo (lit 5) (lit 4) (.eq (lit 0) (lit 1)), .exFromTo (lit 5) (lit 4) (.eq (lit 0) (lit 0)), m1 161,
    exPrime (lit 24) (lit 28), .not (m5), .and m5 m5, .call "prime" [lit 7],
    .allNat (.le (lit 0) (.var 0))].map (decidingValue primeDefs maxSteps) = List.replicate 8 none

/-! The budget: a deciding value at exactly the budgets where the evaluator stops early, below and from each
statement's work on (M-5 33, 8 … 20 322, 1 … 10 84, M-1 to 4 324, 8 … 10 165). -/
#guard agreesUpTo primeDefs m5 40 && agreesUpTo primeDefs (exPrime (lit 8) (lit 20)) 330 &&
  agreesUpTo [] (.allFromTo (lit 1) (lit 10) (.le (.var 0) (lit 6))) 120 && agreesUpTo primeDefs (m1 4) 400 &&
  agreesUpTo primeDefs (exPrime (lit 8) (lit 10)) 200

/-! `decidingValue_of_fails` on M-5, and its converse fails: a "for every" that holds, or is unknown, has none. -/
#guard arithOutcome primeDefs 33 m5 = .decided .fails && (decidingValue primeDefs 33 m5).isSome
#guard arithOutcome primeDefs 32 m5 = .unknown (.limit .evaluations) && decidingValue primeDefs 32 m5 = none
#guard arithOutcome primeDefs maxSteps (m1 161) = .decided .holds && decidingValue primeDefs maxSteps (m1 161) = none

/-! For me-12b: an unbounded statement whose evaluation stops early at its first value still has a deciding value,
though its row is "stated, not decided"; the row must show the deciding value only on a decided outcome. -/
#guard let φ := .allFromTo (lit 1) (lit 3) (.and (.le (.var 0) (lit 0)) (.allNat (.le (lit 0) (.var 0))))
  arithOutcome [] maxSteps φ = .unknown .unboundedStatement && decidingValue [] maxSteps φ = some 1

/-- M-5's deciding value is its first counterexample in the meaning, by `decidingValue_all`. -/
example : ¬ Holds primeDefs.env [1] (exPrime (.add (.var 0) (.num 1)) (.sub (.mul (.num 2) (.var 0)) (.num 1))) :=
  have ⟨_, _, _, _, _, _, h, _⟩ := decidingValue_all primeDefs (by decide) (.num 1) (.num 161) _ (by decide) 33 1
    (by decide)
  h

end VE.Arith.Examples
