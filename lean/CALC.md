# `calc@0` Lean core (`lean/VE/Calc/*`)

Specification: [docs/spec/math-evidence.md](../docs/spec/math-evidence.md) §§2.1–2.5 and the ME-1 row
of [docs/spec/math-evidence-PLAN.md](../docs/spec/math-evidence-PLAN.md). The numbers the core uses
(exact decimals, printed numbers, the four rounding rules, the comparison phrases, `Verdict` and
`Outcome`) are `VE.Numbers` (§1, me-1a). foundation/me-1 was split by the trust budget into three
items (reviews/dri-decisions-20261017b.md #6): me-1a `VE.Numbers`, me-1b the meaning and checker
(`Syntax`, `Eval`, `Decls`), me-1c `VE.Calc.Render` (the display-only English lines of §9 and §11.2).
With me-1c, ME-1 is complete. `lean/audit.py` audits every theorem: no `sorry`, only `propext`,
`Classical.choice` and `Quot.sound`.

The core registers no service mode and no command: nothing public reads it before ME-2.

## Files

| File | Contents |
|---|---|
| `Syntax.lean` | `Expr`, `Values`, the independent meaning `Denotes` (division needs a nonzero divisor), `Expr.names`, `Expr.subexprs`, `Claim` (`compare`, `within`, `rounds`), `Claim.exprs`, `Claim.Holds`, `Claim.Defined` |
| `Eval.lean` | the evaluator `Expr.eval`, the checker `Claim.decide`, `Claim.tieSensitive`, and the theorems tying them to the meaning |
| `Decls.lean` | declarations (`Source`: stated, defined, free, counted; `Counted`), their meaning `values` and `WellFormed`; the digit limit (`maxDigits`, `Small`) and the operational path (`Val`, `Expr.evalL`, `valuesL`, `firstFault`, `Claim.run`); the causes of an unknown (`Overflows`, `NameOverflows`, `ReadsExhausted`, `NameExhausted`); findings (`FindingKind`, `findingKind`) |
| `Render.lean` | `VE.Calc.English.renderClaim`: a claim's English line from the values' words and the fixed phrases (`VE.Numbers.Phrases`, §11.2), or `none`; one function per production of 11.2 (`renderAtom`, `renderTerm`, `renderExpr`), 11.2's form of value words (`valueWordsOk`, `reservedWords`, `phraseWords`), numerals and printed numbers in words (`exactWords`, `printedWords`, `placesPhrase`), one-pass template filling (`fill`) |
| `Examples.lean` | `#guard` fixtures and `example`s for every definition above (spec fixtures V-1, V-2, V-4, V-9, V-10, V-11, V-13, D-1, H-4, H-5, H-9, DL-1, DL-2, DL-4), and the English lines: each phrase, each rounding rule, every shape 11.2 refuses, and a read-back of every expression to depth 3 |

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

## The English lines (`Render.lean`)

`renderClaim` is display only: no verdict reads it, and it has no theorem. Its checks are the `#guard`s in
`Examples.lean`, including an exhaustive one: over every expression to depth 3 built from four atoms, a line
is written exactly when 11.2's grammar accepts the expression, and a reader of that grammar that returns every
parse reads the line back as that expression and nothing else. The theorem form of this (render, then parse,
gives the expression back) is ME-11's, whose engine then replaces this file's phrase table.

* A line is written only when 11.2 gives it one reading (me-1 review F1): an infix phrase ("minus",
  "divided by", "to the power") stands only at the top, with an atom on its left, and at most one phrase
  stands inside another. Anything else is `none`, and the display names the intermediate values instead.
* Value words must have 11.2's form: single-spaced words beginning with "the", not beginning with a phrase
  word, and containing no reserved word as a whole word ("the island" is fine, "the x is y" is not).
  Otherwise the line is `none`.
* A number is written as exact decimal digits with at most 40 places. A negative number has no numeral in VE
  text (the sign is a symbol), so a claim that needs one has no line. A printed number with negative places
  is "d times ten to the power k".
* The places are words from one to twenty ("one decimal place", "twelve decimal places") and numerals after
  that; zero places is "a whole number"; negative places are "a multiple of ten to the power k".
* Every rounding line names its rule: "with exact ties going up", "with exact ties going to the even digit",
  "rounded down", "rounded up".
* A phrase template is filled in one pass, so "{1}" inside value words stays as written. A comparison with
  no phrase in `VE.Numbers.Phrases` (equality with `swap` set) has no line. Lines begin with a capital and
  end with a full stop.
