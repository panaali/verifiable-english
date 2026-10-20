# me-6b report: `ve-units@2` (math-evidence spec 6.2)

No DRI signature is needed: the one DELTA row cites R16. The rest of ME-6's plan row, unit factors written
`["sci", d, e]`, is the next item **me-6c** (after ME-2's literal decoder).

## Statement gate

ME-S passed its bounded re-checks (`math-evidence-p3ver1.final.md`, then `math-evidence-p3ver2.final.md`: PASS).
me-6 proved every 3.5/6.1 statement in `lean/VE/Calc/Dimension.lean`; me-6b changes none of them and does not touch
that file. It adds three helper theorems of its own: `dimE_ok` (the decoder's `dimE` is `Expr.dimOf`),
`unless_ok`, and `checkClaim_invariant` (a claim the 6.2 checks admit has the same truth in every system of base
units, from `compare_invariant` and `rounds_invariant`, plus a range case proved the same way).

## Plan rows (ME-6, plan at beb5c4630; the me-6 report's "me-6b" list)

| Row | Delivered by |
|---|---|
| New file `lean/VE/Calc/Units.lean`, the only decoder of `ve-units@2` | `decode`, `decodeV2`; `tests/test_calc_units.py` (new; me-6's `test_calc_dimensions.py` unchanged) |
| Base dimensions, `base_exponents`, an exact positive factor | `decodeExponents`, `decodeFactor`; `test_fixture[refuse-zero]`, `[refuse-negative]`, `[refuse-base]`, `[refuse-zero-exponent]`, `[i2-factor]`, `[h7c-value]` |
| Affine and logarithmic units refused by name | `[refuse-celsius]`, `[refuse-degree-celsius]`, `[refuse-fahrenheit]`, `[refuse-degree-fahrenheit]`, `[refuse-decibel]`, `[refuse-bel]`, `[refuse-neper]` |
| H-7d: `day` with `base_exponents` refused | `[refuse-day]` (`CalendarTagNotUnit: day (durations use elapsed_day)`); `[refuse-elapsed]` admits `elapsed_day` |
| `ve-units@1` through W6a's frozen decoder, identities unchanged, tags nominal | `decodeLegacy`; `[i2-legacy]` (hashed as written; W6a's id `b4a20af9…`), `[h7l]`, `[h7l-same]`, `[h7l-value]` |
| I-2 pinned as in me-6's report | `[i2-id]`, `[i2-reordered]` (`448c0851…`), `[i2-text]`, `[i2-raw]` ("Natural number expected") |
| `DimensionMismatch` naming both dimensions | `mismatch`, `dimE`; `[h7-sum]`, `[h7-difference]`, `[claim-compare-mismatch]`, `[claim-within-*]` |
| Claim-level checks and `RoundingNeedsNumber` (new here) | `checkClaim`, `unitOf`; `[claim-*]` (13 fixtures), `checkClaim_invariant` |
| H-7, H-7c, H-7u through the decoder | `[h7-*]`, `[h7c]`, `[h7c-n]`, `[h7u-values]` |
| Malformed input (checklist 5) | `test_malformed_environments_get_a_lean_answer`: every node of I-2 replaced by 7, true, null, [], {} and a 10,000-deep list |
| Factors written `["sci", d, e]` | **me-6c** (needs ME-2's literal decoder) |
| Bytes | 0; nothing claimed |

Two choices the spec leaves open, recorded in FOLLOW-UPS "## me-6b" for 6.2's next revision:
- `RoundingNeedsNumber`'s `<unit>` is the dimension's coherent unit (factor 1), else its first unit by name, else
  "unit of <dimension>" (`[claim-rounds-length]`, `[claim-rounds-no-coherent]`, `[claim-rounds-no-unit]`).
  `<words>` are the rounded expression's words, which the caller passes in (ME-2's runner).
- Diagnostics write a name's underscores as spaces (`spoken`): 13.1 says no diagnostic contains a symbol, and 6.2's
  own example reads "one fringe width". Refusals that quote a declared name (`AffineUnit: degree_fahrenheit`, the
  `InvalidInput` paths) quote it as written.

Directives:
- ET3: me-6b adds no month or year unit, offset or conversion. 6.2 refuses only `day` by name, so a document unit
  named `month` decodes like any other unit; calendar offsets stay W6's.
- `lean/VE/Time/Wire.lean` is untouched (read through `decodeEnvironment`).
- me-5 is merged; me-6b touches no other file in `lean/VE/Calc/`. The registries `lean/VE.lean`,
  `lean/VE/Audit.lean` and `tools/trust-classes.json` are also changed by ap-1b, jt-2, me-9, sc-1ac, me-1 and
  arch-AR-1 (append-only; generated or union-merged under R12). No other hand-written file is shared.

## Trust (R16)

K +0, S +0, untied V +60 (`Units.lean`: D[V] 55, G[V] 5), per declaration in DELTA row 1. `trust_map.py --check`:
PASS. The allowance is recorded; FOLLOW-UPS "## me-6b" holds the ties-pass row. `dimE` is C (tied by `dimE_ok`);
`checkClaim`, `unitOf`, `spoken`, `dimWords`, `mismatch` and `UnitEnv.context` are G[R].

## Seeded bugs and mutants (Lean, the only language changed)

32 mutants in `lean/VE/Calc/Units.lean`, at least one per definition except the two structures (see
`mutants.json`, "not mutated"); all 32 killed. Six break `dimE_ok` or `checkClaim_invariant`; for them the proofs
were stubbed so that the tests alone catch them. One per claimed behaviour:

| Behaviour | Mutant | Failing tests |
|---|---|---|
| H-7d: `day` is refused | `unit-day` | `test_fixture[refuse-day]` |
| Affine and logarithmic names | `affine`, `logarithmic` | `[refuse-celsius]`, `[refuse-neper]` |
| A positive factor | `factor-pos` | `[refuse-zero]` |
| I-2: exponents hash as strings | `unit-exponent-string` | `[i2-text]`, `[i2-id]`, `[i2-reordered]`, `[i2-factor]` |
| `ve-units@1` through W6a, nominal | `decode`, `legacy-decoder` | `[i2-legacy]`, `[h7l]`, `[h7l-same]`, `[claim-rounds-legacy]` |
| `DimensionMismatch` names both | `mismatch` | `[h7-sum]`, `[claim-compare-mismatch]` and 6 more |
| Comparison and range checks | `claim-compare`, `claim-within-low`, `claim-within-high` | `[claim-compare-mismatch]`, `[claim-within-low]`, `[claim-within-high]` |
| `RoundingNeedsNumber` | `claim-rounds`, `unit-of-coherent`, `unit-of-none` | `[claim-rounds-*]` (6), `[claim-rounds-length]`, `[claim-rounds-no-unit]` |
| Units are values (H-7c) | `values` | `[h7c]`, `[h7c-n]`, `[h7c-value]`, `[h7l-value]` |

## Tests run

On bb4271567 (main dc10bdfb6 merged; inventories regenerated):
- `tests/test_calc_units.py`: 73 passed (72 when the mutants ran; `[refuse-digits-40]` was added after).
- `lake build`: PASS. `python3 lean/audit.py`: PASS. `regen_generated.py --check`: 32 entries.
  `trust_map.py --check`: PASS.
- `tools/gate_collection.py --check --prebuilt`: 72 added, 0 refused, 0 stale, 0 malformed.
- `select_tests.py` selects `tests/test_calc_units.py` and `test_calc_dimensions.py` among 81 files (not all).
- Selected tests on the test runner: SELECTED_RESULT.
- No test in `main-known-red.txt` is touched. The full gate is the chain's.

Size: SIZE hand-written lines over the merge base (generated files excluded; the side table and these docs counted).

## Pilot bytes

0 expected. Physics' `calc-dimension` 92 B (ME-P2) wait for ME-2, which runs these checks in the `calc` mode.

## Next item

me-6c (`sci` factors, after ME-2), me-9 (identities, after me-5); ME-P2 after ME-4.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no service mode, relay or Lean answer that Python reads; the test reads Lean's printed lines only.
2. PASS: every plan row is mapped in "Plan rows", with me-6c named. No Python copy of a Lean decision, no permanent
   report test, no hand-written file shared with an in-flight branch.
3. PASS: 32 of 32 mutants killed by named tests (`mutants.json`); empty or wrong environments fail
   (`test_malformed_environments_get_a_lean_answer`, `[refuse-*]`).
4. N.A.: `ve-units@2` has no Python or Rust implementation. Reordered keys: `[i2-reordered]`.
5. PASS: `test_malformed_environments_get_a_lean_answer` replaces each node of I-2; undeclared names and units are
   refused (`[h7-unknown]`, `[claim-rounds-unknown]`, `[context-unit]`, `[refuse-base]`).
6. PASS: synced with main dc10bdfb6; selected run on that tree; the full gate is the chain's on the final HEAD.
7. PASS: the DELTA row cites R16 with per-declaration lines; `trust_map.py --check` PASS; FOLLOW-UPS "## me-6b".
8. PASS: no public output changes (no mode, route, Python or Rust); DELTA says so.
9. PASS: `select_tests.py --base $(git merge-base HEAD main)` selects `tests/test_calc_units.py`, not every file.
10. PASS: 6.1's statements unchanged (Dimension.lean untouched); `claim-*` mutants break `checkClaim_invariant` and
    `dimE` breaks `dimE_ok` (the `proofs_stubbed` mutants). No `tools/check_*_statements.py` covers math-evidence.
11. N.A.: no budget or deadline; the digit limit of a factor is `[refuse-digits-40]` and `[refuse-digits]`; the test waits with
    `HANG_TIMEOUT` and has no sleep.
12. N.A.: nothing on a pilot or document path changes; no route is registered.
13. PASS: no test removed; `gate_collection.py --check --prebuilt`: 0 refused, stale or malformed.

Sibling lessons (me-9 review): F1 (a limit tested only on one side): the factor's digit limit comes from W6's
`parseDecimal` and is tested at 40 digits and at 41 (`[refuse-digits-40]`, `[refuse-digits]`). F2 (a result that skips
normalisation): `decodeExponents` builds every dimension with `insertExp` (`[normal]`; zero exponents are refused,
`[refuse-zero-exponent]`). F3 (a vacuous truth): `checkClaim_invariant` only states invariance; a claim whose sides
have no value stays undefined in both systems.
