import VE.Calc.TableExamples
import VE.Calc.Stats

/-! ME-7's fixtures (spec 13.2 and 13.3, plan ME-7): V-6, V-6r, S-5's statistical domains, a sign-flip p over 12
synthetic differences against a hand count, a binomial tail and a kappa, each on both sides of its boundary. -/

namespace VE.Calc.StatsExamples
open VE.Calc VE.Numbers

def milli (ks : List Int) : List Rat := ks.map fun (k : Int) => (Rat.ofInt k) / 1000
/-- V-6: the twelve printed differences of `paper/sections/10-appendices.md:97` (14B AWQ, P1 attacker). -/
def v6 : List Rat := milli [-100, -133, 94, -192, 21, 86, -57, 0, 61, -50, -246, -29]
def sv : Rat := (sampleVariance? v6).getD 0
def pv : Rat := (populationVariance? v6).getD 0
/-- The `D` in 0…199 whose `(D, 3)` the square root of `v` rounds to (ties up). -/
def rootsAt (v : Rat) : List Nat := (List.range 200).filter fun D => decide (SqrtRoundsTo .tiesUp ⟨D, 3⟩ v)

/-! V-6 (holds × 3) and V-6r (fails: the population variance's root rounds to 0.103 only). -/
#guard v6.sum = -109 / 200 ∧ (v6.map fun x => x * x).sum = 152053 / 1000000
#guard sampleVariance? v6 = some (1527611 / 132000000)
#guard rootsAt sv = [108] ∧ rootsAt (sv / 12) = [31] ∧ rootsAt (2593 ^ 2 / 1000 ^ 2 * sv / 12) = [81]
#guard populationVariance? v6 = some (1527611 / 144000000)
#guard rootsAt pv = [103] ∧ ¬ SqrtRoundsTo .tiesUp ⟨108, 3⟩ pv

/-! `SqrtRoundsTo` at an exact root on each rule's boundary: √(0.1085²) is a tie, 0.1085 itself. -/
def tie : Rat := (1085 / 10000) ^ 2
#guard [Rounding.tiesUp, .halfEven, .down, .up].map (fun r => [108, 109].map fun D =>
  decide (SqrtRoundsTo r ⟨D, 3⟩ tie)) = [[false, true], [true, false], [true, false], [false, true]]
#guard [Rounding.tiesUp, .halfEven, .down, .up].map (fun r => [108, 109].map fun D =>
  decide (SqrtRoundsTo r ⟨D, 3⟩ (tie + 1 / 10 ^ 12))) = [[false, true], [false, true], [true, false], [false, true]]
#guard [Rounding.tiesUp, .halfEven, .down, .up].map (fun r => [109, 110].map fun D =>
  decide (SqrtRoundsTo r ⟨D, 3⟩ ((1095 / 10000) ^ 2))) = [[false, true], [false, true], [true, false], [false, true]]
/-- Exact roots 0.1070 to 0.1090 in steps of 0.00005: every tie and both sides of it, against `RoundsTo` of the root. -/
def grid : List Rat := (List.range 41).map fun i => (2140 + i : Nat) / 20000
#guard [Rounding.tiesUp, .halfEven, .down, .up].all fun r => grid.all fun s => (List.range 5).all fun j =>
  decide (SqrtRoundsTo r ⟨106 + j, 3⟩ (s * s)) == decide (RoundsTo r ⟨106 + j, 3⟩ s)
#guard decide (SqrtRoundsTo .tiesUp ⟨0, 0⟩ 0) ∧ ¬ SqrtRoundsTo .tiesUp ⟨0, 1⟩ (-1 / 100)
#guard decide (rootGe 4 2) ∧ ¬ rootGe 4 (201 / 100) ∧ decide (rootGe 0 (-1)) ∧ decide (rootGe (-1) 0)
#guard decide (rootGt 4 (199 / 100)) ∧ ¬ rootGt 4 2 ∧ decide (rootGt 0 (-1)) ∧ ¬ rootGt 0 0
#guard decide (rootLe 4 2) ∧ ¬ rootLe 4 (199 / 100) ∧ ¬ rootLe 0 (-1) ∧ decide (rootLe 0 0)
#guard decide (rootLt 4 (201 / 100)) ∧ ¬ rootLt 4 2 ∧ ¬ rootLt 0 0 ∧ ¬ rootLt (-1) 0
#guard decide (rootEq 4 2) ∧ ¬ rootEq 4 (-2) ∧ ¬ rootEq 4 (201 / 100) ∧ decide (rootEq 0 0)

/-! The sign-flip p over 12 synthetic differences, nine +1 and three −1: the observed mean is 6/12, and a sign vector
reaches it exactly when it has at most 3 or at least 9 plus signs, 2 · (1 + 12 + 66 + 220) = 598 of 4,096 by hand. -/
def d12 : List Rat := List.replicate 9 1 ++ List.replicate 3 (-1)
#guard signFlipP d12 = 598 / 4096
#guard signFlipP [1, 1] = 1 / 2 ∧ signFlipP [1, -1] = 1 ∧ signFlipP [2, 1] = 1 / 2 ∧ signFlipP [-3] = 1
#guard absR (-2) = 2 ∧ absR 2 = 2 ∧ absR 0 = 0
#guard signs 2 = [[1, 1], [-1, 1], [1, -1], [-1, -1]] ∧ (signs 12).length = 4096
#guard [choose 12 0, choose 12 1, choose 12 2, choose 12 3, choose 3 5, choose 0 0] = [1, 12, 66, 220, 0, 1]

/-! The limit: 16 values, the most a decoded sign flip has, end within `Work.maxWork` (2¹⁶ vectors); one unit less
refuses. The charge counts value bits (12.2's unit): `(2¹⁶ + 2) · 72 · (1 + 2 · 1 + 32 + 3)` for sixteen 1s. -/
def d16 : List Rat := List.replicate 16 1
#guard signFlipWork d16 = 179311968 ∧ signFlipWork d16 ≤ Work.maxWork
#guard signFlipC Work.maxWork d16 = some (1 / 32768, 179311968) ∧ signFlipC 179311967 d16 = none
#guard signFlipC 120 [] = some (1, 120) ∧ signFlipC 119 [] = none ∧ signFlipC 0 d16 = none

/-! Large values the length-only charge (`n + 2ⁿ (n + 1)`: 1,114,128 and 53,260 units) admitted within `Work.maxWork`
and the bits refuse: sixteen 2,000-bit integers (the numerators' bits), and twelve 1,000-bit numerators over
2,000-bit odd denominators (the denominators' bits: their least common multiple has about 24,000). -/
def big16 : List Rat := (List.range 16).map fun i => ((2 ^ 1999 + i : Nat) : Rat)
def big12 : List Rat := (List.range 12).map fun i => ((2 ^ 999 : Nat) : Rat) / ((2 ^ 1999 + 2 * i + 1 : Nat) : Rat)
#guard signFlipWork big16 = 9612065232 ∧ signFlipC Work.maxWork big16 = none
#guard signFlipWork big12 = 11241469680 ∧ signFlipC Work.maxWork big12 = none
#guard ((signFlipC 11241469680 big12).map (·.2)) = some 11241469680 ∧ signFlipC 11241469679 big12 = none

/-! A binomial tail and S-5's unguarded values (the domain 0 ≤ p ≤ 1 is `Denotes.binom`'s, me-7b). -/
#guard binomialTail 10 8 (1 / 2) = 7 / 128 ∧ binomialTail 10 0 (1 / 3) = 1 ∧ binomialTail 10 11 (1 / 2) = 0
#guard binomialTail 10 8 0 = 0 ∧ binomialTail 10 8 1 = 1
#guard binomialTail 10 8 2 = 7424 ∧ binomialTail 1 1 2 = 2

/-! Cohen's kappa of a 2 × 2 table: po = 35/50, pe = (25 · 30 + 25 · 20)/50² = 1/2, κ = 2/5; undefined on an empty
table and when chance agreement is 1. -/
#guard kappa? [[20, 5], [10, 15]] = some (2 / 5) ∧ kappa? [[5, 0], [0, 5]] = some 1
#guard kappa? [[0, 0], [0, 0]] = none ∧ kappa? [[4, 0], [0, 0]] = none ∧ kappa? [[2, 1], [0, 0]] = some 0
-- A ragged table reads a missing cell as 0 (the decoder refuses it as `KappaTableNotSquare`, me-7b).
#guard kappa? [[2], [1, 1]] = some (1 / 2) ∧ kappa? [[1, 1], [2]] = some (-1 / 2)

/-! S-5 (J5): each statistic of a list is undefined below its shortest list, on both sides. -/
#guard [Stat.mean, .variance, .populationVariance, .signFlip].map (·.run []) = [none, none, none, none]
#guard [Stat.mean, .variance, .populationVariance, .signFlip].map (·.run [3]) = [some 3, none, some 0, some 1]
#guard [Stat.mean, .variance, .populationVariance, .signFlip].map (·.run [3, 5]) =
  [some 4, some 2, some 1, some (1 / 2)]
#guard [Stat.mean, .variance, .populationVariance, .signFlip].map Stat.minLength = [1, 2, 1, 1]
#guard signFlipP [] = 1

/-! ME-4's column aggregates over T-1: the 32B scores are 3 and 5; the one `false` row's score is 5; the absent score
of `.all` leaves both undefined. -/
open VE.Calc.TableExamples in
#guard [.variance "score", .populationVariance "score"].map (run (.isText "judge" "32B")) = ok [some 2, some 1] ∧
  [.variance "score", .populationVariance "score"].map (run (.isFalse "approved")) = ok [none, some 0] ∧
  [.variance "score", .populationVariance "score"].map (run .all) = ok [none, none]

end VE.Calc.StatsExamples
