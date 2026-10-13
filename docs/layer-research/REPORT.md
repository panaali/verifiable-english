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
- `tools/select_tests.py --base $(git merge-base HEAD main) --run`: 86 units, 0 failed.
- The full gate on the final HEAD: `evidence/gate.json`.
