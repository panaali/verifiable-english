# me-6b report: `ve-units@2` (math-evidence spec 6.2)

No DRI signature is needed: the one DELTA row cites R16. The rest of ME-6's plan row, unit factors written
`["sci", d, e]`, is the next item **me-6c** (after ME-2's literal decoder).

## Statement gate

ME-S passed its bounded re-checks (`math-evidence-p3ver1.final.md`, then `math-evidence-p3ver2.final.md`: PASS).
me-6 proved every 3.5/6.1 statement in `lean/VE/Calc/Dimension.lean`; me-6b changes none and does not touch that
file. It adds its own theorems: `dimE_ok` (the decoder's `dimE` is `Expr.dimOf`), `unless_ok`, and
`checkClaim_invariant` (a claim the 6.2 checks admit has the same truth in every system of base units, from
`compare_invariant`, `rounds_invariant` and a range case proved the same way).

## Plan rows (ME-6 at beb5c4630; the me-6 report's me-6b list)

Built from `wip/me-6b` (b809ffcee) onto main; all fixtures are in the new `tests/test_calc_units.py` (me-6's
`test_calc_dimensions.py` is unchanged).

| Row | Delivered by (`test_fixture[...]` unless named) |
|---|---|
| `lean/VE/Calc/Units.lean`, the only decoder of `ve-units@2` | `decode`, `decodeV2` |
| Base dimensions, `base_exponents`, an exact positive factor | `[refuse-zero]`, `[refuse-negative]`, `[refuse-base]`, `[refuse-zero-exponent]`, `[i2-factor]`, `[h7c-value]` |
| Affine and logarithmic units refused by name | `[refuse-celsius]`, `[refuse-degree-celsius]`, `[refuse-fahrenheit]`, `[refuse-degree-fahrenheit]`, `[refuse-decibel]`, `[refuse-bel]`, `[refuse-neper]` |
| H-7d: `day` with `base_exponents` refused | `[refuse-day]`; `[refuse-elapsed]` admits `elapsed_day` |
| `ve-units@1` through W6a's frozen decoder; identities unchanged; tags nominal | `[i2-legacy]` (hashed as written; W6a's id `b4a20af9…`), `[h7l]`, `[h7l-same]`, `[h7l-value]` |
| I-2 pinned as in me-6's report | `[i2-id]`, `[i2-reordered]` (`448c0851…`), `[i2-text]`, `[i2-raw]` ("Natural number expected") |
| `DimensionMismatch` naming both dimensions | `[h7-sum]`, `[h7-difference]`, `[claim-compare-mismatch]`, `[claim-within-low]`, `[claim-within-high]` |
| Claim-level checks and `RoundingNeedsNumber` (new) | `checkClaim`, `unitOf`, `checkClaim_invariant`; `[claim-*]` (15) |
| H-7, H-7c, H-7u through the decoder | `[h7-*]`, `[h7c]`, `[h7c-n]`, `[h7u-values]` |
| Malformed input (checklist 5) | `test_malformed_environments_get_a_lean_answer`: each node of I-2 set to 7, true, null, [], {} or a 10,000-deep list |
| Factors written `["sci", d, e]` | **me-6c** |
| Bytes | 0; nothing claimed |

Choices the spec leaves open (in FOLLOW-UPS "## me-6b" for 6.2's next revision):
- `RoundingNeedsNumber`'s `<unit>` is the dimension's coherent unit (factor 1), else its first unit by name, else
  "unit of <dimension>" (`[claim-rounds-length]`, `[claim-rounds-no-coherent]`, `[claim-rounds-no-unit]`).
  `<words>` are the rounded expression's words, passed in by the caller (ME-2's runner).
- Diagnostic prose writes a name's underscores as spaces (`spoken`; 13.1: no symbol in a diagnostic; 6.2's example
  reads "one fringe width"). Refusals that quote a declared name (`AffineUnit: degree_fahrenheit`, `InvalidInput`
  paths) quote it as written.

Directives: ET3: no month or year unit, offset or conversion is added (6.2 refuses only `day` by name, so a document
unit named `month` decodes like any unit; calendar offsets stay W6's). `lean/VE/Time/Wire.lean` is untouched. No
other file in `lean/VE/Calc/` is touched (me-5 and me-9 are merged). Shared registries (`lean/VE.lean`,
`lean/VE/Audit.lean`, `tools/trust-classes.json`, `ve/assurance-manifest.json`) are append-only and also changed by
in-flight items (ap-1b, jt-2, sc-1ac, me-1, arch-AR-1); generated ones are regenerated under R12, and
`trust-classes.json` keeps main's order with the one `Units.lean` block added.
`ve/assurance-manifest.json` pins `Units.lean` whole as a Lean decoder (`total_lines` 36,413).

## Trust (R16)

K +0, S +0, untied V +60 (`Units.lean`: D[V] 55, G[V] 5), per declaration in DELTA row 1; `trust_map.py --check`:
PASS; allowance recorded; FOLLOW-UPS "## me-6b" has the ties-pass row. `dimE` is C (tied by `dimE_ok`);
`checkClaim`, `unitOf`, `spoken`, `dimWords`, `mismatch` and `UnitEnv.context` are G[R].

## Seeded bugs and mutants (Lean, the only language changed)

32 mutants in `lean/VE/Calc/Units.lean`, at least one per definition except the two structures (`mutants.json`,
"not mutated"); all 32 killed. Six also break `dimE_ok` or `checkClaim_invariant` and were run with those proofs
stubbed, so that the tests alone catch them. One per claimed behaviour:

| Behaviour | Mutant | Failing tests (`test_fixture[...]`) |
|---|---|---|
| H-7d: `day` refused | `unit-day` | `[refuse-day]` |
| Affine and logarithmic names | `affine`, `logarithmic` | `[refuse-celsius]`, `[refuse-neper]` |
| A positive factor | `factor-pos` | `[refuse-zero]` |
| I-2: exponents hash as strings | `unit-exponent-string` | `[i2-text]`, `[i2-id]`, `[i2-reordered]`, `[i2-factor]` |
| `ve-units@1` through W6a, nominal | `decode`, `legacy-decoder` | `[i2-legacy]`, `[h7l]`, `[h7l-same]`, `[claim-rounds-legacy]` |
| `DimensionMismatch` names both | `mismatch` | `[h7-sum]`, `[claim-compare-mismatch]` and 6 more |
| Comparison and range checks | `claim-compare`, `claim-within-low`, `claim-within-high` | `[claim-compare-mismatch]`, `[claim-within-low]`, `[claim-within-high]` |
| `RoundingNeedsNumber` | `claim-rounds`, `unit-of-coherent`, `unit-of-none` | `[claim-rounds-*]` (6), `[claim-rounds-length]`, `[claim-rounds-no-unit]` |
| Units are values (H-7c) | `values` | `[h7c]`, `[h7c-n]`, `[h7c-value]`, `[h7l-value]` |

## Tests run

- Selected tests on the test runner (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`) on
  98967efb (main c5197da78 merged): 85 units, exit 0, 0 failed. The run before it, on d49bbe51, failed
  `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified` (Units.lean unpinned),
  fixed in 98967efb.
- After that run only fixtures were removed (`h7u-lt`, `h7u-eq` and `h7-dimof`, already covered by
  `test_calc_dimensions.py`), `docs/trust-baseline.json` was put back in main's order (same entries) and these
  docs changed: `tests/test_calc_units.py` reruns at 70 passed; `trust_map.py --check` PASS.
- `lake build`, `python3 lean/audit.py`, `regen_generated.py --check` (32 entries), `trust_map.py --check`: PASS.
- `tools/gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
- No test in `main-known-red.txt` is touched. The full gate is the chain's.

Size: about 700 hand-written lines over the merge base (generated files excluded; side tables, manifest pin, mutants
and these docs counted), over the ~600 guide: `Units.lean` 229, `tests/test_calc_units.py` 250, docs and evidence
about 165, side tables about 60. The decoder, its refusals and the claim checks are one coherent part (the task's
deliverables); the only further cut, the claim checks, would leave `RoundingNeedsNumber` undelivered.

## Pilot bytes and next item

0 expected; physics' `calc-dimension` 92 B (ME-P2) wait for ME-2, which runs these checks in the `calc` mode.
Next: me-6c (`sci` factors, after ME-2); ME-P2 after ME-4.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no service mode, relay or Lean answer that Python reads; the test reads Lean's printed lines.
2. PASS: each plan row is mapped above, me-6c named; no Python copy of a Lean decision, no permanent report test.
3. PASS: 32 of 32 mutants killed by named tests (`mutants.json`); `[refuse-*]` and the malformed test fail closed.
4. N.A.: `ve-units@2` has no Python or Rust implementation. Reordered keys: `[i2-reordered]`.
5. PASS: `test_malformed_environments_get_a_lean_answer`; undeclared names and units refused (`[h7-unknown]`,
   `[claim-rounds-unknown]`, `[context-unit]`, `[refuse-base]`).
6. PASS: synced with main c5197da78; selected run on 98967efb; the full gate is the chain's.
7. PASS: the DELTA row cites R16 with per-declaration lines; `trust_map.py --check` PASS; FOLLOW-UPS row.
8. PASS: no public output changes (no mode, route, Python or Rust); DELTA says so.
9. PASS: `select_tests.py` selects `tests/test_calc_units.py` among 81 files, not all.
10. PASS: 6.1's statements unchanged; the `claim-*` mutants break `checkClaim_invariant` and `dimE` breaks
    `dimE_ok` (`proofs_stubbed`). No `tools/check_*_statements.py` covers math-evidence.
11. N.A.: no budget or deadline; the factor's digit limit is tested at 40 and 41 (`[refuse-digits-40]`,
    `[refuse-digits]`); the test waits with `HANG_TIMEOUT`, no sleep.
12. N.A.: nothing on a pilot or document path changes.
13. PASS: no test removed (the three dropped fixtures were never committed to main);
    `gate_collection.py --check --prebuilt`: 0 refused, stale or malformed.

Sibling lessons (me-9 review): F1 (a limit tested on one side only): the digit limit is tested at 40 and 41. F2 (a
result that skips normalisation): every decoded dimension is built by `insertExp`, zero exponents refused
(`[normal]`, `[refuse-zero-exponent]`). F3 (a vacuous truth): `checkClaim_invariant` states invariance only.
