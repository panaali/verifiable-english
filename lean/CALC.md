# `calc@0` Lean core (`lean/VE/Calc/*`)

Specification: [docs/spec/math-evidence.md](../docs/spec/math-evidence.md) §§2.1–2.5 and the ME-1 row
of [docs/spec/math-evidence-PLAN.md](../docs/spec/math-evidence-PLAN.md). The numbers the core uses
(exact decimals, printed numbers, the four rounding rules, the comparison phrases, `Verdict` and
`Outcome`) are `VE.Numbers` (§1, me-1a). foundation/me-1 was split by the trust budget into three
items (reviews/dri-decisions-20261017b.md #6): me-1a `VE.Numbers`, me-1b the files below, me-1c
`VE.Calc.Render` (the display-only English lines of §9 and §11.2). `lean/audit.py` audits every
theorem: no `sorry`, only `propext`, `Classical.choice` and `Quot.sound`.

The core registers no service mode and no command: nothing public reads it before ME-2.

## Files

| File | Contents |
|---|---|
| `Syntax.lean` | `Expr`, `Values`, the independent meaning `Denotes` (division needs a nonzero divisor), `Expr.names`, `Expr.subexprs`, `Claim` (`compare`, `within`, `rounds`), `Claim.exprs`, `Claim.Holds`, `Claim.Defined` |
| `Eval.lean` | the evaluator `Expr.eval`, the checker `Claim.decide`, `Claim.tieSensitive`, and the theorems tying them to the meaning |
| `Decls.lean` | declarations (`Source`: stated, defined, free, counted; `Counted`), their meaning `values` and `WellFormed`; the digit limit (`maxDigits`, `Small`) and the operational path (`Val`, `Expr.evalL`, `valuesL`, `firstFault`, `Claim.run`); the causes of an unknown (`Overflows`, `NameOverflows`, `ReadsExhausted`, `NameExhausted`); findings (`FindingKind`, `findingKind`) |
| `Examples.lean` | `#guard` fixtures and `example`s for every definition above (spec fixtures V-1, V-2, V-4, V-9, V-10, V-11, V-13, D-1, H-4, H-5, H-9, DL-1, DL-2, DL-4); the English-line fixtures come with `Render.lean` |

## The theorems, in plain words

* `Expr.eval_iff`: the evaluator returns `q` exactly when the expression means `q` (`eval_sound`,
  `Denotes.eval_complete`); so the meaning is a function (`Denotes.unique`).
* `Claim.decide_holds`, `Claim.decide_undefined`, `Claim.decide_fails`: the checker says `holds`
  exactly when the claim holds, `undefined` exactly when some expression has no value, and `fails`
  exactly when every expression has a value and the claim does not hold.
* `values_stated`, `values_free`, `values_counted`, `values_defined`, `values_missing`: in a
  well-formed list of declarations each name has the value its source gives, and an undeclared name
  has none.
* `valuesL_agrees`, `Expr.evalL_agrees`: the operational path agrees with the meaning wherever it
  gives a value or `undefined`.
* `Claim.run_decided`: when `run` decides, its verdict is `decide` on the declared values.
  `Claim.run_unknown`: when it is unknown, the reason is the digit limit and some value the claim reads
  is over it (`Overflows`), or the evaluation budget and the claim reads an exhausted counted value
  (`ReadsExhausted`). `Claim.run_complete`: without either cause, `run` decides.
* `findingKind_source_iff`: a finding is a source finding exactly when no software produced it and
  every one of its (at least one) span checks passed.

## Choices and limits

* The first faulty expression, in the claim's order (`Claim.exprs`), names `run`'s outcome
  (`firstFault`): an undefined left side before an overflowing right side gives `undefined`.
* The digit limit counts the decimal digits of the numerator and of the denominator separately:
  4,096 digits are allowed, 4,097 are not (`Examples.lean` checks limit − 1, limit and limit + 1).
* `values` and `valuesL` recompute a defined value each time it is read, so the cost of a chain of
  definitions that each read the previous one twice doubles per link (me-1 review C1). Nothing public
  calls them yet; ME-2 must memoize them and add a step-count test before it registers `calc`.
