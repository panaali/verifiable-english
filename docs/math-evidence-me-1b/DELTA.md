# me-1b delta: the `VE.Calc` meaning and checker

Base `05b85b631` (`git merge-base HEAD main`). me-1b is the second of the three items that replace
foundation/me-1 (reviews/dri-decisions-20261017b.md #6). It carries over me-1's `lean/VE/Calc/Syntax.lean`,
`Eval.lean` and `Decls.lean` (7b93539a4) unchanged and adds `lean/VE/Calc/Examples.lean`, which does not import
`VE.Calc.Render`: its `#guard` fixtures and `example`s exercise every new trusted definition. No Render file is in
this item (me-1c).

**Public output: none.** me-1b registers no service mode, command or route, and no Python or Rust file changes:
`Claim.run`, `Claim.decide` and the meanings are reached only by the Lean build and its fixtures. No diagnostic,
fault order, verdict or English line a user can see changes, so none of this is a row below.

## User-visible deltas

Trust growth, re-measured with `uv run python tools/trust_map.py --check` on the final code: K +0, S +107,
untied V +0, trusted +107 against `05b85b631f80` (`VE/Calc/Decls.lean` +70, `VE/Calc/Syntax.lean` +37,
`VE/Calc/Eval.lean` +0: its three definitions are C, checked by the proofs below). Recorded as one allowance
(S 107) in `docs/trust-baseline.json` with `trust_map.py --allow`; `trust_map.py --check` passes. R16's cap is
150 lines per item, none in K. The ties-pass row R16 asks for is in manage-agents FOLLOW-UPS.md, section
"## me-1b" (infra item ties-me-1b). Line numbers below are `lean/VE/Calc/Examples.lean`; the seeded bugs that
make these checks fail are in [`mutants.json`](mutants.json). The proofs `Expr.eval_iff`, `Claim.decide_holds`,
`Claim.decide_undefined`, `Claim.decide_fails`, `Claim.run_decided`, `Claim.run_unknown` and
`Claim.run_complete` compile and are audited (`python3 lean/audit.py --check`).

| # | File | Trusted lines (class, declaration: lines) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Calc/Syntax.lean` | +37: S 37 (`Expr` 10, `Values` 2, `Denotes` 10, `Claim` 6, `Claim.Holds` 6, `Claim.Defined` 3) | `example`s 188-224 state `Denotes` (subtraction's operand order, a nonzero divisor, an unknown name), `Claim.Holds` (`within` at both inclusive ends and just outside, a 27/200 rounding, a failing order) and `Claim.Defined` (a defined claim, a zero divisor) from their constructors; `Expr.eval_iff` and `Claim.decide_*` tie them to `Claim.decide`, which the spec-fixture `#guard`s 19-108 pin (V-1, V-2, V-4, V-9, V-10, D-1, H-4, H-5, H-9, DL-1, DL-2, DL-4, the reversed V-2 difference at 40, undefined operands at 103-108); `Expr`, `Values` and `Claim` are the types every check is written in and can fail only by not compiling; seeded bugs 1-3 | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
| 2 | `lean/VE/Calc/Decls.lean` | +70: S 70 (`Counted` 5, `Source` 6, `Decl` 4, `Decl.valueUnder` 7, `values` 3, `WellFormed` 6, `Small` 3, `Val` 4, `NameOverflows` 8, `Expr.Overflows` 4, `Claim.Overflows` 3, `NameExhausted` 7, `Expr.ReadsExhausted` 3, `Claim.ReadsExhausted` 3, `FindingKind` 4) | `#guard`s 148-178: every `Source` and `Counted` kind on both paths (`values`, `Decl.valueUnder`, `Claim.run`; review C4's free and counted sources), a later declaration shadowing an earlier one, an exhausted count read directly and through a definition; 124-145: `Small` at limit − 1, limit and limit + 1 in numerator, denominator and sign, on `Val.guard` and `Claim.run`, and the unknown's text that names the limit (129); 110-122: V-11 and the fault order; 180-184: V-13 (`FindingKind`); `example`s 229-255 (`WellFormed`, and three lists that break each of its conditions), 262-298 (`Claim.Overflows`, `Expr.Overflows`, `NameOverflows` through `.here` and `.dep`, `Claim.ReadsExhausted`, `Expr.ReadsExhausted`, `NameExhausted` through `.here` and `.dep`, and a claim with neither cause); `Claim.run_decided`, `run_unknown` and `run_complete` tie the causes to `Claim.run`; seeded bugs 5-10 | SIGNED by standing ruling R16 (DRI-RULINGS.md) |

`lean/VE/Calc/Eval.lean` adds no trusted line (`Expr.eval`, `Claim.decide` and `Claim.tieSensitive` are C), so it
has no row; its seeded bug 4 (`tieSensitive` at 54-61) is in `mutants.json`.
