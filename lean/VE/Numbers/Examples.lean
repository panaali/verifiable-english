import VE.Numbers.Phrases

/-! Fixtures for every `VE.Numbers` definition (me-1a). Each `#guard` fails the build when the definition it
exercises changes its answer. The rounding cases are spec fixtures V-1, V-8 and V-9 stated on `RoundsTo` and
`Rounding.round` directly; the Calc fixtures that reach them through claims come with `VE.Calc` (me-1b). -/

namespace VE.Numbers.Examples
open VE.Numbers

-- `decValue`: the exact value of a written decimal, its sign and its written places.
#guard decValue ⟨false, 0, [2, 9, 6]⟩ = 37 / 125
#guard decValue ⟨true, 2, [6, 7, 5]⟩ = -107 / 40
#guard decValue ⟨false, 17, []⟩ = 17
#guard decValue ⟨false, 0, [0, 5, 0]⟩ = 1 / 20

-- `tenPow`: positive, zero and negative powers.
#guard tenPow 3 = 1000
#guard tenPow 0 = 1
#guard tenPow (-2) = 1 / 100

-- `Printed`: the written places are kept ("0.050" is 50 at 3 places), and the scientific form moves them.
#guard Printed.ofDec ⟨false, 0, [2, 9, 6]⟩ = ⟨296, 3⟩
#guard Printed.ofDec ⟨false, 0, [0, 5, 0]⟩ = ⟨50, 3⟩
#guard Printed.ofDec ⟨true, 2, [6, 7, 5]⟩ = ⟨-2675, 3⟩
#guard Printed.sci ⟨false, 1, [5]⟩ (-8) = ⟨15, 9⟩
#guard Printed.sci ⟨false, 2, []⟩ 7 = ⟨2, -7⟩
#guard (Printed.mk 296 3).value = 37 / 125
#guard (Printed.mk 2 (-7)).value = 20000000
#guard (Printed.sci ⟨false, 1, [5]⟩ (-8)).value = 3 / 200000000

-- V-1: 176/594 is 0.2962…, so it rounds to 0.296 and not to 0.297 at three places.
#guard RoundsTo .tiesUp ⟨296, 3⟩ (176 / 594)
#guard ¬ RoundsTo .tiesUp ⟨297, 3⟩ (176 / 594)
#guard Rounding.round .tiesUp 3 (176 / 594) = 296
#guard tieAt 3 (176 / 594) = false

-- V-9: the exact value 2.675 is a tie that both declarable rules round to 2.68 (8 is even).
#guard tieAt 2 (107 / 40)
#guard Rounding.round .tiesUp 2 (107 / 40) = 268
#guard Rounding.round .halfEven 2 (107 / 40) = 268
#guard ¬ RoundsTo .tiesUp ⟨267, 2⟩ (107 / 40)
#guard ¬ RoundsTo .halfEven ⟨267, 2⟩ (107 / 40)

-- V-8: 0.0078125 at six places is a tie whose upper neighbour is odd: the rules differ.
#guard tieAt 6 (4 / 512)
#guard Rounding.round .tiesUp 6 (4 / 512) = 7813
#guard Rounding.round .halfEven 6 (4 / 512) = 7812
#guard RoundsTo .tiesUp ⟨7813, 6⟩ (4 / 512) ∧ ¬ RoundsTo .tiesUp ⟨7812, 6⟩ (4 / 512)
#guard RoundsTo .halfEven ⟨7812, 6⟩ (4 / 512) ∧ ¬ RoundsTo .halfEven ⟨7813, 6⟩ (4 / 512)

-- "Going up" is toward the larger number, also for negative values; half to even picks the even neighbour.
#guard Rounding.round .tiesUp 0 (-5 / 2) = -2
#guard Rounding.round .halfEven 0 (-5 / 2) = -2
#guard Rounding.round .tiesUp 0 (-7 / 2) = -3
#guard Rounding.round .halfEven 0 (-7 / 2) = -4
#guard RoundsTo .tiesUp ⟨-3, 0⟩ (-7 / 2) ∧ RoundsTo .halfEven ⟨-4, 0⟩ (-7 / 2)
#guard tieAt 0 (-5 / 2) ∧ tieAt 0 3 = false

-- Rounding down and up, on both sides of zero and on an exact value.
#guard Rounding.round .down 1 (271 / 100) = 27 ∧ Rounding.round .up 1 (271 / 100) = 28
#guard Rounding.round .down 1 (-271 / 100) = -28 ∧ Rounding.round .up 1 (-271 / 100) = -27
#guard Rounding.round .down 1 (27 / 10) = 27 ∧ Rounding.round .up 1 (27 / 10) = 27
#guard RoundsTo .down ⟨27, 1⟩ (271 / 100) ∧ ¬ RoundsTo .down ⟨28, 1⟩ (271 / 100)
#guard RoundsTo .up ⟨28, 1⟩ (271 / 100) ∧ ¬ RoundsTo .up ⟨27, 1⟩ (271 / 100)
#guard RoundsTo .down ⟨27, 1⟩ (27 / 10) ∧ RoundsTo .up ⟨27, 1⟩ (27 / 10)

-- Negative places round to tens, hundreds, …: 1,250 at the hundreds is a tie.
#guard Rounding.round .tiesUp (-2) 1234 = 12
#guard Rounding.round .tiesUp (-2) 1250 = 13 ∧ Rounding.round .halfEven (-2) 1250 = 12
#guard RoundsTo .tiesUp ⟨13, -2⟩ 1250 ∧ RoundsTo .halfEven ⟨12, -2⟩ 1250

-- Outcomes and the fixed explanation of each unknown.
#guard UnknownReason.text 500 (.limit .evaluations) = "unknown: the budget of 500 evaluation steps ran out"
#guard UnknownReason.text 0 (.limit .digits) = "unknown: an exact value would have more than 4,096 digits"
#guard UnknownReason.text 0 .unboundedStatement = "stated, not decided: a quantifier has no bound"
#guard
  let reasons : List UnknownReason :=
    [.limit .digits, .limit .evaluations, .limit .derivationSteps, .limit .witnessPoints, .limit .polyTerms,
     .floatingPointNotModelled, .derivationInconclusive, .consistencyInconclusive, .identityNotShown,
     .unboundedStatement]
  let texts := reasons.map (UnknownReason.text 7)
  texts.eraseDups.length = 10 && (texts.take 9).all (·.startsWith "unknown: ")
#guard Outcome.decided .holds ≠ Outcome.unknown (.limit .digits)
#guard [Verdict.holds, .fails, .undefined].eraseDups.length = 3

-- Comparisons: each order phrase's meaning below, at and above the boundary, in the table's order.
-- `Rel.Holds` has no instance of its own; it is decided through `Comparison.Holds` with no swap.
#guard Comparison.Holds ⟨.eq, false⟩ 1 1 ∧ ¬ Comparison.Holds ⟨.eq, false⟩ 1 2
#guard Comparison.Holds ⟨.lt, false⟩ 1 2 ∧ ¬ Comparison.Holds ⟨.lt, false⟩ 1 1
#guard Comparison.Holds ⟨.le, false⟩ 1 1 ∧ ¬ Comparison.Holds ⟨.le, false⟩ 2 1
#guard Comparison.Holds ⟨.lt, true⟩ 3 2 ∧ ¬ Comparison.Holds ⟨.lt, false⟩ 3 2
#guard orderPhrases.map (·.1) =
  ["{0} is less than {1}", "{0} is at most {1}", "{0} is more than {1}", "{0} is at least {1}"]
#guard orderPhrases.map (fun (_, c) => (decide (c.Holds 1 2), decide (c.Holds 1 1), decide (c.Holds 2 1))) =
  [(true, false, false), (true, true, false), (false, false, true), (false, true, true)]
#guard equalsPhrase.1 = "{0} equals {1}" ∧ equalsPhrase.2.Holds 1 1 ∧ ¬ equalsPhrase.2.Holds 1 2
#guard withinPhrase = "{0} is from {1} through {2}"

-- Every unknown's text is the spec's table (section 1.5), word for word; N is the case's budget.
#guard [UnknownReason.limit .digits, .limit .evaluations, .limit .derivationSteps, .limit .witnessPoints,
    .limit .polyTerms, .floatingPointNotModelled, .derivationInconclusive, .consistencyInconclusive,
    .identityNotShown, .unboundedStatement].map (UnknownReason.text 25) =
  ["unknown: an exact value would have more than 4,096 digits",
   "unknown: the budget of 25 evaluation steps ran out",
   "unknown: the derivation search ran out of its 10,000 combination steps",
   "unknown: the consistency search tried its 4,096 candidate points",
   "unknown: a normal form would have more than 10,000 terms",
   "unknown: floating-point computation not modelled",
   "unknown: no certificate and no counterexample was found",
   "unknown: neither a witness nor an enclosure decides it",
   "unknown: the normal forms differ and no point where the sides differ was found",
   "stated, not decided: a quantifier has no bound"]

end VE.Numbers.Examples
