# me-6cc report: a unit factor's shape comes before its limits

Status: done, no DRI signature reserved. Branch feature/me-6cc on main f58ef91bb.
Changed: `VE.Calc.Units.decodeFactor` reads limits 5 and 6 only on a string or a list starting with `"sci"`.
DELTA: 4 rows, each R2 with its one-sentence order rule. Trust: K +0, S +0, V +2, SIGNED by standing ruling R16.
Open: nothing. The full gate is the chain's, on the final HEAD; it was not run here.
Bytes 0. Next item: none for unit factors; ME-P2 with ME-4 reads them.

## Inputs

me-6c's review F1 (manage-agents `me-6c-review-ov.final.md`), read first. Statement gate: ME-S passed; no statement
changes, and no theorem is touched. `debates/plan-synthesis-2/edits-math-evidence.md`: this item implements none of its
five edits (AR-10 rows, durations, `hedged` labels, budgets, "about"); none concerns unit factors. Overlap: no local
branch under feature/, infra/, lean-first/ or foundation/ changes `Units.lean`, `UnitsExamples.lean` or
`tools/calc_units_fixtures.py` against main (`git diff --name-only main...<branch>` over each, no hit).

## Delivered

| Task line | Delivered by |
|---|---|
| (1) limit checks only on literal shapes; every other tag or object `must be a literal` at every depth; `limitFault` and its callers untouched | `decodeFactor` (`lean/VE/Calc/Units.lean:43`), the `shaped` guard; `lean/VE/Calc/Wire.lean` has no diff |
| (2) the five probes refused `must be a literal` | `[sci-shape-pow-65]`, `[sci-shape-lit-41]`, `[sci-shape-rounds-41]`, `[sci-shape-stated-41]`, `[sci-shape-nested]` |
| (2) literal neighbours unchanged | `[sci-exponent-64]` read; `[sci-exponent-65]` and `[refuse-digits]` (a 41-digit string) `ResourceLimit` |
| both sides of each check | under each limit, the same refusal: `[sci-shape-pow-64]`, `[sci-shape-lit-40]`, `[sci-shape-rounds-40]`, `[sci-shape-stated-40]`; a list starting with `sci`: `[sci-shape-sci-short-41]` keeps its limit, `[sci-shape-sci-long-65]` stays `must be a literal` (no limit reads a four-member list) |
| (3) seeded bugs | below, and [`mutants.json`](mutants.json) |
| (4) generated fixtures | table in `tests/calc_units_fixtures.py`, `lean/VE/Calc/UnitsExamples.lean` through `tools/calc_units_fixtures.py --write`; `tools/regen_generated.py --write` moved `lean/declarations.txt` |
| (4) manifest pin | `ve/assurance-manifest.json`: lines 224, sha256 `bfcd9e42c95c…`, `total_lines` 39779; `docs/spec/assurance-manifest.md` through `tools/assurance_manifest.py --write`; `--check` exits 0 |
| DELTA, one row per changed refusal, R2 | [`DELTA.md`](DELTA.md), 4 rows |

Choice left by the task: `["sci", <41 digits>]`, a short `sci` list, stays `ResourceLimit`, because the guard is the
task's `"sci" :: _`, as me-6c's DELTA row 4 lists. me-6c's DELTA rows 4-5 ("another tag: `must be a literal`") now
hold as written; that file is not edited.

Regen also rewrote `docs/codemap/*` from other merges (no input of this item, and `git log -- docs/codemap/INDEX.md`
shows no branch commits it); those changes were restored and are not in this diff.

## Seeded bugs (Lean, the only product language changed)

Each applied alone to `lean/VE/Calc/Units.lean`, restored after. `lake build VE.Calc.UnitsExamples` failed on each at
the guard named. Pytest cannot name a row here, as its session hook stops at the failed build, so one Lean file
importing `VE.Calc.Units` only printed each row of the table that differs (the method of me-6c's `mutants.json`).
On the good code it printed nothing.

| Behaviour | Seeded bug | Guard | Rows that fail |
|---|---|---|---|
| a non-literal factor is `must be a literal` | `guard-dropped`: `if shaped then throw e` to `throw e` (main's code) | `sci` (UnitsExamples.lean:245) | `sci-shape-pow-65`, `sci-shape-lit-41`, `sci-shape-rounds-41`, `sci-shape-stated-41` |
| only a `sci` list is a literal list | `guard-every-list`: `.arr _ => true` | `sci` | `sci-shape-pow-65`, `sci-shape-lit-41`, `sci-shape-rounds-41` |
| a string keeps limit 6 | `str-left-out`: `.str _ => false` | `refuse` (UnitsExamples.lean:163) | `refuse-digits` |
| a short `sci` list keeps its limit | `guard-exact-sci`: `[.str "sci", _, _]` | `sci` | `sci-shape-sci-short-41` |

## Trust

`uv run python tools/trust_map.py --check`: "against 62d8329d4dd9: K +0, S +0, D +2, G +0, tied +0, unclassified +0,
trusted +2", "PASS: K, S and untied [V] within 62d8329d4dd9 and the allowances introduced since". The task expected
+0. The guard is one more line of `decodeFactor`, and the order rule one more doc line; packing them to reach +0 would
not make the trusted logic smaller, so the growth is recorded under R16: `docs/trust-baseline.json` V +2, FOLLOW-UPS.md
row under "## me-6cc" for the ties pass. No new definition; `decodeFactor` is the one changed.

[`trust-mutants.json`](trust-mutants.json): `mac-pytest.sh --trustmut -- --max-mutants 1000` on 3e82f060d,
"2 KILLED, 0 SURVIVOR, 0 UNKNOWN, 0 INVALID, 0 ALLOWED, 0 NOT RUN", exit 0: the two `bool-flip`s of the guard
(`Units.lean:44`). Later commits change no Lean file.

## Runs

- `lake build` once on the final Lean: "Build completed successfully (1161 jobs)".
- `python3 lean/audit.py`: "PASS: 670 source files; 7496 named theorem declarations audited".
- `uv run pytest -q tests/test_calc_units.py`: 203 passed.
- Selected tests, once (`mac-pytest.sh --select`, run me-6cc-aea2a6a3-t350413, 5 shards, 75 units): 73 units passed, 2
  failed, one test each: `test_regen_generated.py::test_assurance_manifest_merge_recomputes_the_decoder_total` and
  `test_assurance_manifest.py::test_trusted_decoder_line_ranges_are_pinned`, both on `total_lines` (39779 measured,
  39777 written), which I had not moved with the pin. Fixed; those two ids rerun: "2 passed".
- Not run: `tools/gate.py` (the chain runs it), a Rust or Python differential (neither changed), pilots (bytes 0).

Spec re-read: the refusal against `docs/spec/math-evidence.md:1646` ("a zero, negative or non-literal factor:
`InvalidInput: units.<name>.factor`"); the factor's form against `:1639`; limits 5 and 6 against 3.2, `:801`.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer; no route reads this decoder.
2. PASS: the table under Delivered; grep of the diff: no Python decision, no report test.
3. PASS: `mutants.json` (4 killed), `trust-mutants.json` (2 killed).
4. N.A. for Python and Rust (Lean only); base against head: seeded bug `guard-dropped` is main's code, 4 rows differ.
5. N.A.: no relayed field; a unit's names are unchanged.
6. PASS: on main f58ef91bb (`git log main -1`); the chain gates the final HEAD.
7. PASS: `DELTA.md` 4 rows R2; V +2 R16 in `docs/trust-baseline.json`, FOLLOW-UPS row "## me-6cc".
8. PASS: `DELTA.md`, the row set from `guard-dropped`; `[sci-shape-pow-65]` and the 3 others.
9. PASS: the selection ran `tests/test_calc_units.py` and caught `test_trusted_decoder_line_ranges_are_pinned`.
10. N.A.: no proof or statement changed; `lake build` and `lean/audit.py` pass.
11. PASS: limits 5 and 6 on literals stay `ResourceLimit`: `[sci-exponent-65]`, `[sci-digits]`, `[refuse-digits]`.
12. N.A.: one constant-time shape test per factor; no pilot reads this decoder.
13. N.A.: no test removed or renamed; 11 rows added to the table.
14. PASS: both sides in the Delivered table; each claim above quotes its command; spec re-read above.
