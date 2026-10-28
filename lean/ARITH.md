# `arith@0` Lean core (`lean/VE/Arith/*`)

Specification: [docs/spec/math-evidence.md](../docs/spec/math-evidence.md) §§12.1–12.3 and the ME-12 row of
[docs/spec/math-evidence-PLAN.md](../docs/spec/math-evidence-PLAN.md). `arith@0` states facts about whole numbers
and integers: "for every whole number n from 1 through 161, there is a prime p with n < p and p at most twice n".
ME-12 is split by the size rule: me-12a is the statement and its meaning; me-12aa adds the budgeted evaluator
(spec 12.2); me-12ab its monotonicity and completeness; me-12nb draft 5's charge (term nodes, calls and value sizes); me-12ac 12.5's deciding value and fixture M-6; me-12b the
wire, the runner, the rows and the mode (spec 12.5). Nothing public reads the core yet.
`lean/audit.py` audits every theorem: no `sorry`, only `propext`, `Classical.choice` and `Quot.sound`.

## Files

| File | Contents |
|---|---|
| `Syntax.lean` | `Term` (numerals, variables, sum, difference, product, calls, counts "the number of p from lo through hi such that …") and `Formula` (equals, less than, at most, divides, calls, not, and, or, if, quantifiers over all whole numbers or integers, and from lo through hi); `Def`, `Defs` (the definitions, in order) |
| `Holds.lean` | the meaning: `Term.value`, `Holds`, `Defs.env`, `Defs.Means` |
| `Defs.lean` | boundedness (`Formula.Bounded`); admission (`Defs.WellFormed`, `Formula.Scoped`) and the refusals the core decides, in the decoder's order (`caseRefusal`) |
| `Bounded.lean` | the budgeted evaluator: `Term.evalB` and `Formula.evalB` (one unit per node visit and each value's bit length), `maxSteps`, `decideBounded` and a statement's row `arithOutcome` |
| `BoundedExamples.lean` | the evaluation fixtures M-1, M-1b, M-2, M-3, M-4, M-4b, M-4x and M-5 at each budget boundary, one fixture per clause of the evaluator, and the chains B-1 to B-4 the budget stops |
| `CompleteExamples.lean` | each statement's work (the first budget that decides it) at, just under and just over it, every larger budget keeping the answer, and each hypothesis of completeness on its refusing side |
| `Examples.lean` | the prime vocabulary, Bertrand's postulate (`bertrand`, `IsPrime`, `bertrand_means_iff`), one example per clause of the meaning in both directions, the fixture statements M-1 to M-5 and the admission guards |

## The meaning, in plain words

A variable is a position: `var 0` is the value bound by the nearest quantifier (or a definition's first parameter),
`var 1` the one before it, and so on. A statement holds when `Holds` says so, and `Holds` reads no evaluator: "for
every whole number" ranges over 0, 1, 2, …; "for every integer i from lo through hi" over the integers from lo through
hi, none when hi is below lo; "the number of p from lo through hi such that φ" counts the values for which `Holds` of
φ is true (debate F4). A call reads the definition of that name made before it: each definition is read in the
meaning of the definitions above it (`Defs.env`), so no definition can call itself and the meaning needs no
termination argument. A term that names no definition, or calls one with the wrong number of arguments, has no value,
and a comparison of a term without a value does not hold. `Defs.Means D φ` is "φ holds over the definitions D".

## Boundedness and admission

A statement is bounded when it has no "for every whole number", "there is a whole number", "for every integer" or
"there is an integer" without a range, here or in any definition it calls. A bounded statement can be decided by trying each value of each range; an
unbounded one is stated, not decided, and is proved only by an import (ME-13).

## The budget

`decideBounded D limit φ` evaluates φ and returns its value and the units spent, or none (UNKNOWN). One unit is
charged per node visit, term and formula nodes alike (spec 12.2, draft 5); a call, of a function or a predicate, is
one visit plus its arguments' and its body's. Every value a term yields (a literal, a variable's value, a sum,
difference or product, a call's result, a count) is also charged its size, the bit length of its magnitude (`bits`),
and so is every value a range step binds. Connectives stop as soon as their left side decides, a
bounded quantifier stops at its first decisive value, and a visit is refused once the units spent reach the limit. The
budget is `maxSteps` = 1,000,000 by default and at most (W6's `VE.Time.maxEvaluations`). `arithOutcome` gives a
statement's row: holds or fails when the evaluator completes, "stated, not decided" for an unbounded statement before
any evaluation, and unknown (`limit .evaluations`) when the budget runs out. Budget 0 is always unknown. Because every value is charged its
bits, no value within budget n has more than n bits (`Term.evalB_bits`), and the work is linear in the units up to
big-number multiplication and division. N1 (`docs/math-evidence/me-12aa/REPORT.md`), a chain of definitions that each
call the one before twice, cost 1 unit under draft 4; it now costs 12,273 at ten levels and is unknown at 1,000,000
units at 24 (`BoundedExamples.lean`, B-1 and B-2, with F1's squaring chain B-3 and a reused large value B-4).

The decoder (me-12b) admits a case only when its definitions are well formed and every statement is scoped; it
refuses the first problem in this order: a name defined twice (`DuplicateName`), a variable no quantifier or parameter
binds (`UnscopedVariable`), a call of a name no definition of that kind has (`UnknownDefinition`), a call of the
definition itself or of a later one (`RecursiveDefinition`), a call with the wrong number of arguments
(`ArityMismatch`), and a count whose condition is unbounded (`UnboundedCount`). `caseRefusal` decides these over the
core's terms. `ShadowedVariable` needs the request's variable names, and each refusal's text names them, so both are
the wire's (me-12b).

## The theorems, in plain words

* `primeBody_iff`: VE's `prime` ("p is at least 2 and no whole number from 2 through p minus 1 divides p") holds of a
  whole number exactly when it is prime in the usual sense (`IsPrime`).
* `bertrand_means_iff`: Bertrand's postulate in VE (`bertrand`, fixture M-3) means "for every whole number n at least
  1 there is a prime p with n < p ≤ 2n". The proof unfolds definitions only; EX-1's import project rewrites with it.
* `Term.evalB_bits`: every value a term yields within budget n has at most n bits; `bits_add_le`, `bits_sub_le` and
  `bits_mul_le` bound the one value computed beyond the budget, whose charge is refused.
* `decideBounded_mono`: a larger budget never changes an answer; it only turns unknown into the answer.
* `decideBounded_covered` and `decideBounded_complete`: a bounded statement over well-formed definitions, with every
  variable bound, has an answer and a number of units fixed by the statement; every budget at least that number
  returns both. So it is decided once the budget covers its work.
