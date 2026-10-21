# `arith@0` Lean core (`lean/VE/Arith/*`)

Specification: [docs/spec/math-evidence.md](../docs/spec/math-evidence.md) §§12.1–12.3 and the ME-12 row of
[docs/spec/math-evidence-PLAN.md](../docs/spec/math-evidence-PLAN.md). `arith@0` states facts about whole numbers
and integers: "for every whole number n from 1 through 161, there is a prime p with n < p and p at most twice n".
ME-12 is split by the size rule: me-12a (this core) is the statement and its meaning; me-12aa adds the budgeted
evaluator; me-12b the wire, the runner, the rows and the mode (spec 12.5). Nothing public reads the core yet.
`lean/audit.py` audits every theorem: no `sorry`, only `propext`, `Classical.choice` and `Quot.sound`.

## Files

| File | Contents |
|---|---|
| `Syntax.lean` | `Term` (numerals, variables, sum, difference, product, calls, counts "the number of p from lo through hi such that …") and `Formula` (equals, less than, at most, divides, calls, not, and, or, if, quantifiers over all whole numbers or integers, and from lo through hi); `Def`, `Defs` (the definitions, in order) |
| `Holds.lean` | the meaning: `Term.value`, `Holds`, `Defs.env`, `Defs.Means` |
| `Defs.lean` | boundedness (`Formula.Bounded`); admission (`Defs.WellFormed`, `Formula.Scoped`) and the refusals the core decides, in the decoder's order (`caseRefusal`) |
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
"there is an integer" without a range, here or in any definition it calls. A bounded statement can be decided by trying each value of each range (me-12aa); an
unbounded one is stated, not decided, and is proved only by an import (ME-13).

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
