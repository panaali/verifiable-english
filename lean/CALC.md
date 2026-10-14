# `calc@0` Lean core (ME-1)

The approved statements are in `docs/spec/math-evidence.md` §§1–2 and the
ME-1 row of `docs/spec/math-evidence-PLAN.md`. `VE.Numbers.Decimal` uses W6's
`VE.Time.Dec`; `VE.Numbers.Round` owns exact rounding and the four rules.
`VE.Calc.Syntax` states expression and claim meanings independently of the
evaluator, and `VE.Calc.Eval` proves their agreement. `VE.Calc.Decls` carries
the operational limit path and the independent overflow and exhaustion causes.

ME-1 does not register a service mode. That belongs to ME-2. Counted values
already have their final mathematical and operational constructors; ME-4 adds
the table computation. `VE.Calc.English.renderClaim` is display only; ME-11
adds reading and the round-trip theorem.

The `#guard` fixtures in `VE.Calc.Examples` cover the values and verdicts of
the plan's ME-1 list, including its negative controls. The Lean audit and the
repository statement inventory check that no theorem is admitted as an axiom.
