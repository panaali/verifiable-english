# me-6c report: unit factors written `["sci", d, e]` in `ve-units@2`

Status: done, no DRI signature reserved. Branch feature/me-6c on main c2a0ee977. `VE.Calc.Units.decodeFactor` now reads a
factor as 3.1's literal (`Wire.literal`, with limits 5 and 6 of 3.2 from `Wire.exponentFault`/`literalFault`, the
calc case's own owners) and hashes it as its shortest plain decimal (spec 11). DELTA: 5 rows, all SIGNED by the DRI
2026-10-27 (item 6) with the decision's condition tests. Trust +0. Bytes 0. Next: me-4, then ME-P2.

## Statement gate and decision

ME-S passed (me-6b REPORT); no statement changes, no theorem touched (`dimE_ok`, `unless_ok`, `checkClaim_invariant`
build unchanged). The DRI decided this item on 2026-10-27 (manage-agents
`reviews/dri-decisions-20261027-featureplan-gates.md` item 6): accepting `sci` factors is the approved spec's text
(6.2 "`factor`: <literal>", 11 "No `sci` exponent remains").

## Plan rows delivered (ME-6's `sci` row; me-6b REPORT "Factors written `["sci", d, e]`: **me-6c**")

| Row / condition | Delivered by (`tests/test_calc_units.py::test_fixture[...]`; the `-- sci` `#guard` of `lean/VE/Calc/UnitsExamples.lean`) |
|---|---|
| `sci` literal read in unit factors | `decodeFactor` (`lean/VE/Calc/Units.lean:40`) calls `Wire.literal`, the one decoder of 3.1's literals; no second reader |
| Normalised to the shortest plain decimal before `environment_id` | `plain p` in the identity; `[sci-spelling*]` (6), `[sci-exponent-6*]`, `[sci-positive-small]`, `[sci-digits-40]` |
| (i) same `environment_id` and the same answers as the plain spelling | `[sci-physics-id]` = `[sci-physics-id-plain]` (`cb0ef65f…`: PHYSICS with four factors written `sci`), `[sci-same-small]`, `[sci-same-large]`, `[sci-same-places]`, `[sci-same-nano]` (`ok true`), `[sci-same-other]` (`ok false`, the negative control); answers `[sci-values]` = `[sci-values-plain]`, `[sci-h7c]`, `[sci-h7c-n]`, `[sci-h7-time]` as `[h7c]`, `[h7c-n]`, `[h7-time]` |
| (ii) `\|e\| = 64` accepted, 65 refused | `[sci-exponent-63]`, `[sci-exponent-64]`, `[sci-exponent-minus-63]`, `[sci-exponent-minus-64]` accepted; `[sci-exponent-65]`, `[sci-exponent-minus-65]`, `[sci-exponent-1000]`, `[sci-exponent-minus-1000]` refused `ResourceLimit: an exponent exceeds 64`; `[sci-exponent-first]` (limit 5 before 6) |
| (iii) zero or negative `sci` factor refused with `InvalidInput: units.<name>.factor` | `[sci-zero]`, `[sci-zero-places]`, `[sci-negative]`, `[sci-negative-small]` (`... must be more than zero`); the nearest accepted: `[sci-positive-small]` (0.001 × 10^-64), `[sci-exponent-minus-64]` |
| Each new check on both sides | digits: `[sci-digits]` (41) / `[sci-digits-40]`; exponent type: `[sci-integer]`, `[sci-integer-text]` / `[sci-spelling-exponent-zero]`; shape: `[sci-number]`, `[sci-short]`, `[sci-long]`, `[sci-tag]`, `[sci-decimal]` / `[sci-spelling]` |
| Bytes | 0; nothing claimed |

Choices the spec leaves open: the refusal of a factor that is no literal now says "must be a literal" (was "must be a
decimal string", which a list factor makes untrue; DELTA row 5); a `sci` exponent beyond 64 is limit 5's
`ResourceLimit` text, as in a calc case. Not delivered: nothing of the item. The `sci` factor's plain spelling may be
longer than 40 digits (`[sci-exponent-64]`, 65 characters); spec 11 asks for the plain decimal and 3.2's digit limit
reads the written literal, so this is the spec's behaviour.

## Seeded bugs (Lean, the only product language changed)

`mutants.json`: each applied alone, `lake build VE.Calc.Units`, then a Lean file importing `VE.Calc.Units` only prints
every row of the table (the same rows the `#guard` families and `test_fixture[...]` check); restored.

| Behaviour | Seeded bug (file) | Failing rows / guard |
|---|---|---|
| (ii) the bound | `exponentFault`: `> 64` to `> 65` (`lean/VE/Calc/Wire.lean`, the bound's one owner) | `[sci-exponent-65]`, `[sci-exponent-minus-65]`, `[sci-exponent-first]`; guard `sci` |
| (ii) the bound read for factors | `decodeFactor`: `exponentFault j <|>` dropped (`lean/VE/Calc/Units.lean`) | `[sci-exponent-65]`, `[sci-exponent-minus-65]`, `[sci-exponent-±1000]`, `[sci-exponent-first]` |
| (i) normalisation | `decodeFactor`: a `sci` factor hashed as written (`Units.lean`) | `[sci-physics-id]`, `[sci-same-small]`, `[sci-same-large]`, `[sci-same-places]`, `[sci-same-nano]`, `[sci-spelling*]` and 6 more (17) |
| (iii) the sign check | `decodeFactor`: `unless 0 < p.value` dropped (`Units.lean`) | `[sci-zero]`, `[sci-zero-places]`, `[sci-negative]`, `[sci-negative-small]`, `[refuse-zero]`, `[refuse-negative]`, `[refuse-negative-below-one]` |
| limit 6 for `sci` | `decodeFactor`: digits read as for a string only (`Units.lean`) | `[sci-digits]` |

A first version of `[sci-exponent-1000]` used 10^30: with the exponent check dropped, Lean then builds 10^(10^30) and
the run hangs instead of failing, so the row reads 1000 (and -1000), which a missing check prints in milliseconds.

`trust-mutants.json` (`mac-pytest.sh --trustmut -- --max-mutants 1000`, c565810ae): `decodeFactor`, 3 mutants
(`lt-le`, `lt-eq`, `lit-plus` on the sign check), 3 KILLED, exit 0.

## Trust

`trust_map.py --check`: K +0, S +0, D +0, G +0, unclassified +0, trusted +0: PASS. `decodeFactor` keeps 8 lines; the
fixture definition `physicsSci` is classed T beside `physics` (`tools/trust-classes.json`). No allowance, no R16
row, so no FOLLOW-UPS ties-pass row. `ve/assurance-manifest.json` re-pins `Units.lean` (same 222 lines, new
sha256); `docs/spec/assurance-manifest.md` regenerated.

## Runs (final code)

- `uv run pytest -q tests/test_calc_units.py`: 191 passed (on 756e4320a; the later commits change one fixture row's
  exponent and side tables).
- `uv run python tools/regen_generated.py --write` once, then `--check`: 33 entries.
- `lake build` (1135 jobs) and `python3 lean/audit.py`: PASS.
- Selected tests (`mac-pytest.sh --select -- --base c2a0ee977 --run`, HEAD 4a313f87): 74 units, 0 failed;
  `tests/test_calc_units.py` and `tests/test_assurance_manifest.py` among them.
- `tools/gate_collection.py --check --prebuilt`: 41 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- No test of `main-known-red.txt` touched. The full gate is the chain's.

Size: about 230 hand-written lines over the merge base (`Units.lean` 16, `tests/calc_units_fixtures.py` 80, side
tables 3, these docs about 130); `UnitsExamples.lean`, `declarations.txt`, `assurance-manifest.md` and
`trust-mutants.json` are generated. Below the 800-line trial target because the item is complete; nothing is cut.

## Pilot bytes and next item

0 expected. Next: me-4 (tables and pinned data), then ME-P2 (physics unit tables, which can now write factors such as
`["sci", "1", -9]`); QT-A7 consumes the same decoder.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no service mode, relay or Lean answer that Python reads; the test reads Lean's printed lines.
2. PASS: the plan row and the decision's three conditions are mapped above to `test_fixture[sci-*]`; no Python copy
   of a Lean decision (the fixture table states answers only); no permanent report test; `Wire.lean` (also edited by
   feature/me-2d) is only read.
3. PASS: 5 of 5 hand mutants killed (`mutants.json`); `trust-mutants.json` 3 of 3 KILLED, exit 0.
4. N.A.: `ve-units@2` has no Python or Rust implementation; key order: `[i2-reordered]` unchanged.
5. PASS: `test_malformed_environment[malformed-units.meter_per_second.factor-*]` (7, true, null, [], {}, deep) and
   the malformed `sci` forms `[sci-number]`, `[sci-short]`, `[sci-long]`, `[sci-tag]`, `[sci-integer*]`.
6. PASS: branch on main c2a0ee977, no merge needed; selected run on the committed HEAD; the full gate is the chain's.
7. PASS: every DELTA row says SIGNED by the DRI 2026-10-27 with the decision file and its condition tests; trust +0.
8. PASS: DELTA lists every changed decoder answer (5 classes); public output none (no route reads the module).
9. PASS: `select_tests.py` selects 74 units including `tests/test_calc_units.py`, not all.
10. N.A.: no theorem or statement changed; `lean/statements.txt` unchanged by regen.
11. PASS: limit 5 tested at 63, 64, 65 and 1000 on both signs (`[sci-exponent-*]`); limit 6 at 40 and 41
    (`[sci-digits-40]`, `[sci-digits]`); no sleep or timeout added (the test keeps `HANG_TIMEOUT`).
12. N.A.: no pilot path changes; the huge-exponent row is refused before any power is computed (`[sci-exponent-1000]`).
13. PASS: no test removed (`sci-exponent-huge` was never on main); `gate_collection.py --check --prebuilt`: 0 refused,
    0 stale, 0 malformed.

Sibling lesson (me-12nb F1, unselected fixtures): every new fixture is a row of `tests/calc_units_fixtures.py`, so it
is both a `#guard` in the generated `lean/VE/Calc/UnitsExamples.lean` (imported by `lean/VE.lean`, built by
`lake build`) and a selected `test_fixture[...]` id; no standalone `.lean` file was added.

## FIXMAP
- `lean/VE/Calc/Units.lean`: `ve-units@2`'s only decoder; me-6c changed `decodeFactor` (line 40) only.
- `lean/VE/Calc/Wire.lean` (read only): `literal` (3.1 literals), `exponentFault` (limit 5), `literalFault` (limit 6), `plain` (spec 11 spelling).
- `tests/calc_units_fixtures.py`: the fixture table; me-6c rows are the `sci-*` keys (after `i2-legacy`), helpers
  `meter`, `spelled`, `same_id`, definitions `PHYSICS_SCI`/`physicsSci`, `PHYSICS_ID`; `refuse-number` and the
  malformed factor answer now say "must be a literal".
- `lean/VE/Calc/UnitsExamples.lean`: GENERATED from the table (`tools/calc_units_fixtures.py`); never hand-edit.
- `tools/trust-classes.json`: `VE.Calc.UnitsExamples.physicsSci` classed T.
- `ve/assurance-manifest.json`: `Units.lean` pin sha256 (update by hand when `Units.lean` changes; then
  `uv run python tools/assurance_manifest.py --write` via regen).
- `docs/math-evidence/me-6c/`: DELTA.md, REPORT.md, mutants.json, trust-mutants.json.
Spec map: 6.2 "`factor`: <literal>" and "zero, negative or non-literal factor" -> `decodeFactor` (Units.lean:40);
11 shortest plain decimal -> `Wire.plain` (Wire.lean:130), used at Units.lean:47; 3.2 limit 5 -> `Wire.exponentFault`
(Wire.lean:71); limit 6 -> `Wire.literalFault` (Wire.lean:81).
Regression tests: `uv run pytest -q tests/test_calc_units.py` (or `-k sci`); `cd lean && lake build VE.Calc.UnitsExamples`.
Regen after a table or Lean change: `uv run python tools/regen_generated.py --write`.
Trust mutants: `zsh /home/seyran/code/manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --json docs/math-evidence/me-6c/trust-mutants.json`.
## END FIXMAP
