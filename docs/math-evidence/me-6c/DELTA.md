# me-6c delta: unit factors written `["sci", d, e]` in `ve-units@2`

**Public output: none.** No service mode, command or route reads `VE.Calc.Units` yet (ME-2's runner and QT-A7 will);
the rows below are the answers of its decoder, `VE.Calc.Units.decode`, which `lake build` (the `#guard`s of the
generated `lean/VE/Calc/UnitsExamples.lean`) and `tests/test_calc_units.py` print. No Python or Rust file changes.

Trust, re-measured with `uv run python tools/trust_map.py --check` on the final code: K +0, S +0, D +0, G +0, tied
+0, unclassified +0, trusted +0 (`decodeFactor` keeps its 8 lines). No allowance is recorded and no R16 ties-pass row
is needed. [`trust-mutants.json`](trust-mutants.json): `tools/trust_mutants.py --max-mutants 1000` on c565810ae, 3 of
3 mutants of `decodeFactor` killed, exit 0. [`mutants.json`](mutants.json): 5 hand mutants, 5 killed.

Every row is the approved spec's behaviour (6.2 "`factor`: <literal>", 11 "No `sci` exponent remains"), which the
DRI signed for this item. Test ids are `tests/test_calc_units.py::test_fixture[...]` unless named.

| # | Input (a unit's `factor`) | Before (me-6b) | After | Condition tests | Ruling |
|---|---|---|---|---|---|
| 1 | `["sci", d, e]`, positive, `\|e\| ≤ 64`, `d` at most 40 digits | `InvalidInput: units.<name>.factor must be a decimal string` | read; its value is `d × 10^e`, and the identity spells it as its shortest plain decimal (`["sci", "1", 3]` is `"1000"`) | (i) `[sci-physics-id]` and `[sci-physics-id-plain]` (one `environment_id`), `[sci-same-small]`, `[sci-same-large]`, `[sci-same-places]`, `[sci-same-nano]` (`ok true`), `[sci-same-other]` (`ok false`), `[sci-values]`/`[sci-values-plain]`, `[sci-h7c]`, `[sci-h7c-n]`, `[sci-h7-time]` (the same answers), `[sci-spelling*]` (6); (ii) `[sci-exponent-63]`, `[sci-exponent-64]`, `[sci-exponent-minus-63]`, `[sci-exponent-minus-64]` | SIGNED by the DRI 2026-10-27 (reviews/dri-decisions-20261027-featureplan-gates.md item 6) |
| 2 | `["sci", d, e]` with `\|e\| ≥ 65` | `... must be a decimal string` | `ResourceLimit: an exponent exceeds 64` (limit 5 of 3.2, checked before limit 6) | (ii) `[sci-exponent-65]`, `[sci-exponent-minus-65]`, `[sci-exponent-1000]`, `[sci-exponent-minus-1000]`, `[sci-exponent-first]` | SIGNED by the DRI 2026-10-27 (reviews/dri-decisions-20261027-featureplan-gates.md item 6) |
| 3 | `["sci", d, e]` of value zero or less | `... must be a decimal string` | `InvalidInput: units.<name>.factor must be more than zero` | (iii) `[sci-zero]`, `[sci-zero-places]`, `[sci-negative]`, `[sci-negative-small]`; accepted beside them: `[sci-positive-small]`, `[sci-exponent-minus-64]` | SIGNED by the DRI 2026-10-27 (reviews/dri-decisions-20261027-featureplan-gates.md item 6) |
| 4 | a malformed `sci` literal | `... must be a decimal string` | `d` over 40 digits: `ResourceLimit: Decimal literal exceeds 40 digits`; `e` not an integer: `InvalidInput: units.<name>.factor.2 must be an integer`; `d` not a decimal: `... must be a decimal`; `d` not a string, a missing or extra member, another tag: `... must be a literal` | `[sci-digits]` (and `[sci-digits-40]` read), `[sci-integer]`, `[sci-integer-text]`, `[sci-decimal]`, `[sci-number]`, `[sci-short]`, `[sci-long]`, `[sci-tag]` | SIGNED by the DRI 2026-10-27 (reviews/dri-decisions-20261027-featureplan-gates.md item 6) |
| 5 | a factor that is neither a string nor a list (`1`, `true`, `null`, `{}`), `[]`, 10,000 nested lists | `... must be a decimal string` | `InvalidInput: units.<name>.factor must be a literal` (6.2: "a non-literal factor"; a list is now a literal's form, so "decimal string" no longer names what is read) | `[refuse-number]`, `test_malformed_environment[malformed-units.meter_per_second.factor-*]` (6) | SIGNED by the DRI 2026-10-27 (reviews/dri-decisions-20261027-featureplan-gates.md item 6) |

Unchanged: every decimal-string factor (value, spelling, refusal text and order; `[refuse-*]`, `[factor-*]`, `[i2-*]`
pass as on main).
