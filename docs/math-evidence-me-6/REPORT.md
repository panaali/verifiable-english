# me-6 report: physical dimensions (spec 6.1)

No DRI signature is needed: the one DELTA row cites R16. Part of ME-6's plan row is cut to **me-6b** under the size
rule. me-6b is built and kept on the local branch `wip/me-6b` (b809ffcee, not pushed).

## Statement gate

ME-S passed its bounded re-checks (`math-evidence-p3ver1.final.md`, then `math-evidence-p3ver2.final.md`: PASS).
Where plan 3.5 and spec 6.1 differ, the spec governs (plan, line 47). Plan 3.5 writes `hΓ` as
`(Γ n).isSome → (Γ n).get!.Normal` and the comparison as `Rel`. Spec 6.1 writes `Γ n = some d' → d'.Normal` and
`Comparison`. I proved 6.1's statements.

A whitespace-normalised comparison of `lean/VE/Calc/Dimension.lean` with 6.1 finds every theorem identical:
`Rescale.of_pos`, `of_mul`, `of_one`, `denotes_rescale`, `compare_invariant`, `rounds_invariant`,
`convert_by_factors` and `legacy_nominal`. Every definition is identical too, except two ME-7 parts that `Expr`
cannot have yet: `commonDim` and `dimOf`'s statistics cases. No statement changed.

The `Normal` hypotheses of `of_mul`, `denotes_rescale`, `compare_invariant` and `rounds_invariant` turn out to be
unneeded: `Rescale.of_mul_any` proves the product rule for every dimension. The statements are kept as reviewed.

## Plan rows (ME-6, plan at 702ff7429)

| Plan line | Delivered by |
|---|---|
| New files: `Dimension.lean` and `tests/test_calc_dimensions.py` | this branch |
| New file: `Units.lean` | me-6b |
| Proves 3.5 | `Dimension.lean`, audited (`python3 lean/audit.py`: PASS) |
| QT-A7 uses `convert_by_factors` | `VE.Calc.convert_by_factors`; `test_fixture[h7c]`, `[h7c-n]`, `[h7c-value]` |
| `ve-units@1` tags nominal, each its own base dimension | `legacyDim`, `legacy_nominal`; `[h7l]`, `[h7l-same]` |
| H-7: a time, dimensionless, and no dimension for D + T | `[h7-time]`, `[h7-ratio]`, `[h7-sum]`; also `[h7-difference]`, `[h7-ratio-sum]`, `[normal]` |
| Meters against kilometers, converted by factors | `[h7c]`, `[h7c-n]`, `[h7c-value]` |
| H-7u (13.3, 13.4: `compare_invariant` and `rounds_invariant` in both directions) | `[h7u-lt]`, `[h7u-eq]`, `[h7u-rounds]`, `[h7u-rounds-3]`, `[h7u-values]` |
| Seeded bug: `dimOf` of `div` adds exponents | mutant `dimof-div`, which fails `[h7-ratio]`, `[h7-ratio-sum]`, `[h7-frequency]` |
| Bytes: 0 | nothing claimed |

**me-6b** (next item). It is cut at the size rule: with the decoder this branch measured 863 hand-written lines.
It covers:
- `lean/VE/Calc/Units.lean`, the only decoder of `ve-units@2`: base dimensions, `base_exponents`, and an exact
  positive factor;
- the refusals by name (affine and logarithmic units, `day`, which is fixture H-7d);
- `ve-units@1` through W6a's frozen decoder, with identities unchanged;
- identity I-2, pinned as `448c0851…`;
- `DimensionMismatch` naming both dimensions;
- the claim-level checks and `RoundingNeedsNumber`;
- factors written `["sci", d, e]`, once ME-2's literal decoder exists.

`wip/me-6b` holds all of it except the claim checks, `RoundingNeedsNumber` and the `sci` factors, with 31 killed
mutants and its own REPORT. It needs a rebase onto me-6 after the merge.

Directives:
- `lean/VE/Time/Wire.lean` is untouched.
- No hand-written file of this branch is in another in-flight branch. The shared generated files fall under R12.
- ET3: me-6 adds no month or year unit, offset or conversion.

## Trust (R16)

K +0, S +55 (`Dimension.lean`), V +0. `trust_map.py --check`: PASS. The allowance is recorded and the FOLLOW-UPS
"## me-6" ties-pass row exists.

## Seeded bugs (Lean, the only language changed; all 15 in `mutants.json`)

Each mutant was applied alone. Every proof it breaks was replaced by `sorry`, so that only the tests can catch it.
All 15 were killed.

| Behaviour | Mutation in `lean/VE/Calc/Dimension.lean` | Failing tests |
|---|---|---|
| H-7: D/λ is dimensionless (the plan's seeded bug) | `dimOf` of `div`: `x.mul y.inv` → `x.mul y` | `test_fixture[h7-ratio]`, `[h7-ratio-sum]`, `[h7-frequency]` |
| H-7: D + T has no dimension | `dimOf` of `add`: no equality check | `[h7-sum]`, `[h7-difference]`, `[h7l]` |
| H-7u: values rescale by their dimension's factor | `Rescale.apply`: `q * ρ.of d` → `q / ρ.of d` | `[h7u-values]` |
| H-7l: legacy tags stay nominal | `legacyDim` ignores the tag | `[h7l]`, `[h7l-same]` |
| A change of units has positive factors | `Rescale.pos`: `0 <` → `0 ≤` | `test_a_change_of_units_has_positive_factors` |

The other 10 mutants cover `Normal` (2), `one`, `insertExp` (2), `mul`, `inv`, `npow`, `zpowR` and `Rescale.of`.
On wip/me-6b, `insertExp`'s cancelled-exponent mutant first survived; fixture `[h7-ratio-sum]` was added for it.

## Tests run

On 7ee9738bf, after syncing main (b7613541c, qt-a2) with `regen_generated.py --resolve`:
- `tests/test_calc_dimensions.py`: 23 passed.
- Selected tests on the Mac runner (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`): 76 units,
  exit 0, 0 failed. They include `tests/test_calc_dimensions.py`, `test_hang_guards.py` and `test_trust_budget.py`.
- `lake build`: PASS.
- `python3 lean/audit.py`: PASS.
- `regen_generated.py --check`: 31 entries.
- `trust_map.py --check`: PASS.
- `tools/gate_collection.py --check --prebuilt`: 23 added, 0 refused, 0 stale, 0 malformed.
- No test in `main-known-red.txt` is touched.
- The full gate is the chain's.

Size: 518 hand-written lines over the merge base, generated files excluded and the side tables counted, before this
section.

## Pilot bytes

0 expected. Physics' `calc-dimension` 92 B (ME-P2) wait for me-6b and ME-2.

## Next item

me-6b, then me-5 (derivations) and me-9 (identities); ME-P2 after ME-4.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no service mode, relay or Lean answer that Python reads. Lean evaluations are read by the test only.
2. PASS: each plan row is mapped to a test in "Plan rows", with me-6b named. The diff has no Python copy of a Lean
   decision (the test only states fixtures), no permanent report test, and no file in another in-flight branch.
3. PASS: 15 of 15 mutants killed by named tests (`mutants.json`), including the plan's seeded bug
   (`test_fixture[h7-ratio]`). `test_a_change_of_units_has_positive_factors` must reject a factor of 0 and accept 1.
4. N.A.: dimensions have no Python or Rust implementation; Lean is the only one.
5. N.A.: no relayed answer to bind. Unknown names give no dimension (`test_fixture[h7-unknown]`).
6. PASS: synced with main at 7ee9738bf. The selected run is on that HEAD; the full gate is the chain's.
7. PASS: the DELTA row cites R16 with per-declaration lines; `trust_map.py --check` PASS; the FOLLOW-UPS "## me-6"
   row exists.
8. PASS: no public output changes, and DELTA says so. The one row is the trust growth.
9. PASS: `select_tests.py` selects `tests/test_calc_dimensions.py` (76 units, not all).
10. PASS: theorem statements match spec 6.1 verbatim (see the statement gate). With proofs intact, the mutants also
    break proofs: for example `dimof-div` breaks `Expr.eval_rescale`. No hypothesis was added. No
    `tools/check_*_statements.py` covers math-evidence.
11. N.A.: no budget, limit or deadline. The test waits with `HANG_TIMEOUT` and has no sleep
    (`tests/test_hang_guards.py` passed in the selected run).
12. N.A.: nothing on a pilot or document path changes; no route is registered.
13. PASS: no test removed; `gate_collection.py --check --prebuilt` reports 0 refused, stale or malformed trailers.

Sibling lesson (me-1c F1, raw-text comparison): N.A. here, because me-6 compares no words. In me-6b, unit and base
names are identifiers (`[a-z][a-z0-9_]*`), so case and punctuation variants are refused, not folded.
