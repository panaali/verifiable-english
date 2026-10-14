# layer-research: `research/` is layer 5

DRI decision SC3 (`debates/plan-synthesis/DRI-DECISIONS-PHASE2.md`): add `research` to layer 5.

## Change

- `tools/layer_policy.py`: `APP_AREAS` names the top-level trees whose every path is layer 5
  (`ve_experiments`, `experiments`, `usecases`, `paper`, and now `research`); `source_layer` reads it.
- `tools/select_tests.py`: `KNOWN_AREAS` takes those trees from `APP_AREAS` instead of listing them
  again. Before, `research/` was neither layer 5 nor a known area, so any branch touching it ran every
  test.
- `tools/test_layer_policy.py::LayerSelectionTests::test_research_tree_is_layer_five_and_selects_its_readers`:
  a `.md`, `.py` and `.json` path under `research/` is layer 5, is not a full run, selects fewer than
  all tests, and every selected test beyond the smoke tests is there only because it names the path
  or a directory above it.

No generated file depends on these lines (`tools/gate-collection.json` lists `tests/` only, and the
layer ledgers are unchanged: `tools/check_python_layers.py` keeps its contract).

## Deltas

No user-visible delta: only the test selector and the layer table of tools change. No DRI ruling or
signature is needed.

## Seeded bugs (Python; the only language changed)

Each was planted, made the test above fail, and was removed; the outputs are in
`evidence/mutants.json`.

| Bug | File | Failing test | Failure |
|---|---|---|---|
| `research` dropped from `APP_AREAS` | `tools/layer_policy.py` | `tools/test_layer_policy.py::LayerSelectionTests::test_research_tree_is_layer_five_and_selects_its_readers` | full run for `research/layering/notes.md`; layer None |
| `research` dropped from `KNOWN_AREAS` | `tools/select_tests.py` | same | full run for `research/layering/notes.md` |
| a `research/` data change adds an unrelated test | `tools/select_tests.py` | same | `tests/test_english.py` selected with reason `research tree` |

## Tests run

- `tools/test_layer_policy.py` `LayerSelectionTests`: 36 passed.
- `tools/select_tests.py --base $(git merge-base HEAD main) --run`: 86 units, 0 failed (before the
  evidence commit).
- After the evidence commit the same selection is all 373 units. The cause predates this item: a
  module every test reaches through conftest holds the bare string `evidence`, which the static
  graph matches by name to every `docs/*/evidence/` directory, and this tree has no coverage map.
  The rerun (load average 100–250) stopped at `--maxfail` with 127 units passed and 3 load failures:
  `tests/test_agent_policy_rerun.py` (Lean `norms` CPU deadline of 5.56 s exceeded) and
  `tests/test_assist.py`, `tests/test_assist_invariants.py` (1 h unit timeout). Rerun alone, all
  pass: `test_agent_policy_rerun.py` + `tools/test_layer_policy.py` 43 passed; the two assist files
  128 passed, 1 skipped (P5 materials not available). The remaining 243 units are left to the
  chain's gate.
- Before that rerun, the worktree's Lean build failed to link: `VE/Readings/SupRun.c.o.export` was a
  736-byte empty object recorded as built (a compile killed under load). Deleting it and its
  trace let `lake build` finish; no Lean source changed.
- The first full gate was run by the chain on the committed HEAD (`gate-result.json` in the worktree).
  The first chain record (2026-10-13 13:33 UTC) was the placeholder a killed gate leaves: no commit,
  no stages, no failures; there was no failed test to rerun.
- The next chain gate on `49d75ddc3` built Lean and Rust and ran 15,081 selected pytest cases:
  14,988 passed, 92 skipped, and one failed. The failing historical RD-8 report test compared saved
  eight-character commit IDs to Git's `%h`, which now abbreviates those IDs to nine characters.
  It now reads full commit IDs and checks their saved prefixes and subjects. The RD-8 report file's
  nine tests passed after the fix. The pre-review check requires a passing gate on the final code.
- After that fix, `select_tests.py --base $(git merge-base HEAD main) --run` chose 22 units. Seventeen
  completed successfully; the five remaining integration units were still active after more than
  20 minutes under parallel load, so that selected run was stopped. The final full gate checks them.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is read or relayed; only the tools' layer table changes.
2. PASS: the one directive (SC3: `research` in layer 5; a test that a `research/` path is layer 5 and
   selects only research-related tests) is delivered by fc1ad2d34 and
   `test_research_tree_is_layer_five_and_selects_its_readers`; no generated file reads these lines;
   no Lean decision copied, no report test added.
3. PASS: three seeded bugs, each failing that test (`evidence/mutants.json`).
4. N.A.: no Python, Lean or Rust checker output changes.
5. N.A.: no relayed field is read.
6. PASS: the full gate runs on the committed final HEAD; `gate-result.json` records its target and
   result, and no gate evidence is committed.
7. PASS: no DELTA row (no user-visible change); no trust-budget growth.
8. PASS: no user-visible output changes; only `tools/` selection changes, so DELTA is none.
9. PASS: this is the item's own fix; `test_research_tree_is_layer_five_and_selects_its_readers`
   shows a `research/` path is not a full run and selects only its readers; seeded bug 3 shows an
   unrelated selected test is caught.
10. N.A.: no Lean statement or proof changes.
11. N.A.: no budget, limit or deadline changes.
12. N.A.: no checker code path changes; selection only shrinks for `research/` paths.
