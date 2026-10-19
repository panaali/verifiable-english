# me-6 report: physical dimensions and `ve-units@2`

No DRI signature is needed: both DELTA rows cite R16. The rest of ME-6's plan row is named as **me-6b** below.

## Statement gate

ME-S passed its bounded re-checks (`math-evidence-p3ver1.final.md`, then `math-evidence-p3ver2.final.md`: PASS).
Where plan 3.5 and spec 6.1 differ, the spec governs (plan, line 47): 3.5 writes `hΓ` as
`(Γ n).isSome → (Γ n).get!.Normal` and the comparison as `Rel`; 6.1 has `Γ n = some d' → d'.Normal` and
`Comparison`. I proved 6.1's statements. A whitespace-normalised comparison of `lean/VE/Calc/Dimension.lean` with
6.1 finds every theorem identical (`Rescale.of_pos`, `of_mul`, `of_one`, `denotes_rescale`, `compare_invariant`,
`rounds_invariant`, `convert_by_factors`, `legacy_nominal`) and every definition identical except two ME-7 parts
that `Expr` cannot have yet: `commonDim` and `dimOf`'s statistics cases. No statement changed. The `Normal`
hypotheses of `of_mul`, `denotes_rescale`, `compare_invariant` and `rounds_invariant` turn out to be unneeded.
`Rescale.of_mul_any` proves the product rule for every dimension, but the reviewed statements are kept as written.

## Plan rows (ME-6, plan at 702ff7429)

| Plan line | Delivered by |
|---|---|
| New files `lean/VE/Calc/{Dimension,Units}.lean`, `tests/test_calc_dimensions.py` | 2ddca563d and later commits |
| Proves 3.5 | `Dimension.lean`, audited by `python3 lean/audit.py` (PASS) |
| Only decoder and owner of `ve-units@2`: base dimensions, `base_exponents`, exact positive `factor` | `VE.Calc.Units.decode`; `test_fixture[refuse-*]` and `[i2-*]` |
| QT-A7 consumes it and uses `convert_by_factors` | theorem `VE.Calc.convert_by_factors`; H-7c |
| Refuses affine and logarithmic units by name | `[refuse-celsius]`, `[refuse-fahrenheit]`, `[refuse-decibel]`, `[refuse-neper]` |
| `ve-units@1` tags nominal; identical declarations incompatible; identities unchanged | `legacyDim`, `legacy_nominal`; `[h7l]`, `[h7l-same]`, `[h7l-value]`, `[i2-legacy]` |
| `day` never a unit of a physical dimension and never converts | `[refuse-day]`; `[refuse-elapsed]` is the control |
| Fixture H-7 (time, dimensionless, `DimensionMismatch(length, time)`) | `[h7-time]`, `[h7-ratio]`, `[h7-sum]`, `[h7-dimof]` |
| Meters against kilometers converted by factors | `[h7c]`, `[h7c-n]`, `[h7c-value]` |
| A sum of a length and a time refused with both names | `[h7-sum]`, `[h7-difference]` |
| Two identically declared `ve-units@1` tags incompatible | `[h7l]`. W6a's `displayInjective` refuses byte-identical declarations, so the two tags differ only in currency |
| `day` given `base_exponents` refused | `[refuse-day]`: `CalendarTagNotUnit: day (durations use elapsed_day)` |
| I-2 | `[i2-text]`, `[i2-id]` (pinned `448c0851…`), `[i2-reordered]`, `[i2-raw]` ("Natural number expected"), `[i2-legacy]` |
| H-7u (13.3, 13.4) | `[h7u-lt]`, `[h7u-eq]`, `[h7u-rounds]`, `[h7u-rounds-3]`, `[h7u-values]` |
| Seeded bug: `dimOf` of `div` adds exponents | mutant `dimof-div`, which fails `test_fixture[h7-dimof]` |
| Bytes: 0 | nothing is claimed |

**Not delivered: me-6b** (cut at the size rule; measured 619 hand-written lines before docs). It covers these parts
of spec 6.2:
- the claim-level checks: the two sides of a comparison and the three of `within` share one dimension
  (`DimensionMismatch` on claims);
- `RoundingNeedsNumber` (it needs `VE.Calc.English.renderExpr` public);
- factors written `["sci", d, e]`, once ME-2's literal decoder exists. Today a factor is a decimal string
  (W6's `parseDecimal`).

me-6b lands with or after ME-2, which decodes the case's `"unit"` field and calls `UnitEnv.context`.

Directives:
- `lean/VE/Time/Wire.lean` is untouched: `ve-units@2` is decoded in `Units.lean`.
- Overlap check: no hand-written file of this branch is in another in-flight branch. Shared generated files
  (Audit, statements, trust tables) fall under R12.
- ET3: me-6 adds no month or year unit, offset or conversion. `ve-units@2` has no built-in units; every unit is
  declared with an exact factor.

## Trust (R16)

K +0, S +55 (`Dimension.lean`), untied V +60 (`Units.lean`), trusted +115 ≤ 150. `trust_map.py --check`: PASS.
The allowance is recorded and the FOLLOW-UPS "## me-6" ties-pass row exists. `dimE` is C, tied to `Expr.dimOf` by
`dimE_ok`. The following are D[R], D[I] or G[R]: the refusals, the identity and the words, since dimensions only
refuse.

## Seeded bugs (Lean, the only language changed; full list in `mutants.json`)

| Behaviour | File | Mutation | Failing test |
|---|---|---|---|
| H-7: D/λ is dimensionless | `lean/VE/Calc/Dimension.lean` | `dimOf` of `div`: `x.mul y.inv` → `x.mul y` | `test_fixture[h7-dimof]` |
| H-7u: values rescale by their dimension | `lean/VE/Calc/Dimension.lean` | `Rescale.apply`: `q * ρ.of d` → `q / ρ.of d` | `test_fixture[h7u-values]` |
| H-7c: a unit's value is its factor | `lean/VE/Calc/Units.lean` | `UnitEnv.values` gives 1 | `test_fixture[h7c]`, `[h7c-n]`, `[h7c-value]` |
| H-7l: legacy tags stay nominal | `lean/VE/Calc/Dimension.lean` | `legacyDim` ignores the tag | `test_fixture[h7l]`, `[h7l-same]` |
| H-7d: `day` refused | `lean/VE/Calc/Units.lean` | checks `"days"` instead of `dayTag` | `test_fixture[refuse-day]` |
| I-2: exponents hash as decimal strings | `lean/VE/Calc/Units.lean` | `Json.str (toString k)` → `toJson k` | `test_fixture[i2-id]`, `[i2-reordered]`, `[i2-factor]` |
| A sum names both dimensions | `lean/VE/Calc/Units.lean` | `dimE` adds without the check | `test_fixture[h7-sum]`, `[h7-difference]`, `[h7l]` |

All 31 mutants (at least one per trusted definition, plus the D[R], G[R] and C ones) were killed by a named test
after every proof they break was replaced by `sorry`. Two mutants first survived, and each now has a fixture:
- `insert-zero`: a cancelled exponent was kept as 0. The fix is `[h7-ratio-sum]`: D/λ plus 1 must be
  dimensionless.
- `context`: a value without a unit was not dimensionless. The fix is `[h7-number]`.

The carrier types `PhysDim`, `UnitDef` and `UnitEnv` have no body to mutate: a field change fails to elaborate their
users. `Rescale`'s field is mutated (`0 <` → `0 ≤`) and caught by `test_a_change_of_units_has_positive_factors`.

## Tests run

- `tests/test_calc_dimensions.py`: 56 passed (Lean answers, read through `lake env lean`).
- `python3 lean/audit.py`: PASS.
- `uv run python tools/regen_generated.py --check`: 31 entries.
- `trust_map.py --check`: PASS.
- Selected tests on the Mac runner (`mac-pytest.sh --select`): see the last commit's message.
- The full gate is the chain's.

## Pilot bytes

0 expected. Physics' `calc-dimension` 92 B (ME-P2) become reachable once ME-2 registers `calc` and me-6b lands.

## Next item

me-6b (above), then me-5 (derivations) and me-9 (identities); ME-P2 after ME-4.
