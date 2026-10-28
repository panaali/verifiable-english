# eff-sel11: the selector always runs the history-inventory lint when the list can go stale

- **Status:** done, and the selected tests pass (28 units on the Mac). No DRI signature is needed. The chain runs the full gate on the final HEAD.
- **What changed:** both selection paths of `tools/select_tests.py` (the map plan and `--impacted`) add `tests/test_history_tests.py`, with the reason `history inventory`, when a change can make `tests/history-dependent.json` stale.
- **Measured:** on today's main and map, the last 10 merged branches already selected the lint (10 of 10, on both paths), so the rule adds 0 tests to them. The two train catches it was meant to prevent (speed-trustmut, speed-vocabpar) also selected it already. Both failed because main was merged **after** the builder's last selected run. See "What this does not fix".
- **Open:** one follow-up for the DRI (below): check the inventory after every main merge. Trust +0, no Lean or Rust change, no user-visible change, no DELTA rows.

Folder: `docs/test-speed-b1/eff-sel11/` (the selector's existing docs folder is `docs/test-speed-b1/`).

## The change

`history_inventory(paths)` (`tools/select_tests.py:908`) returns the changed paths that can make the list stale:

| Trigger | Where it is decided |
|---|---|
| a Python file under `tests/`, at any depth, added, edited or deleted (`tests/conftest.py` too) | `path.endswith(".py") and path.startswith("tests/")` |
| `tests/history-dependent.json`, `tests/history-map.json`, `tools/history_tests.py`, `tools/git_words.py` | `history_tests.INPUTS` (`tools/history_tests.py:69`) |
| a Python file the list (`via` entries) or its map extract (`sites`) names, read from the tree at selection time | `history_tests.named_sources` (`tools/history_tests.py:1128`) |

- `named_sources` lives in `tools/history_tests.py` because that file owns the format of the list. It takes the file part of each `file:qualname` entry from each file that passes the lint's own validator (`validate_list`, `validate_extract`). A file that is missing, unreadable or malformed names nothing. The selector then falls back to the first two rows of the table and does not crash.
- **Map path:** `finish` (`:922`) adds the test next to the SMOKE rule. A full fallback is unchanged, since every unit is already selected. **`--impacted`** (`:1259`) adds it next to ALWAYS. Both plans now carry `history_inventory`, the list of trigger paths.
- **Documentation only** triggers nothing, because no row of the table matches it.
- **No plan gets narrower.** The rule only calls `sel.add` or unions a set. `test_what_the_history_list_names_only_adds_its_lint` checks this: with every changed module named, the plan equals the plan without the rule plus the lint, and every other field is the same.
- **SELECTOR_VERSION:** this is a hash of the file, so it changed by itself. No evidence file records it. `uv run python tools/regen_generated.py --write` ran once and changed nothing.

### A guard I had to change (please review)

`tests/test_history_tests.py::test_only_the_lint_reads_the_list` said that no gate, merge, **selection** or cache code may read the list, "so no run skips or reuses a test because of it". This task asks the selector to read the list, so the literal rule and the task conflict. The intent still holds, because the selector only ever adds the lint. So I:
- added `tools/select_tests.py` and `tests/test_select_tests.py` to the allowed readers;
- added `test_the_selector_reads_the_list_only_to_run_its_lint` (`tests/test_history_tests.py:328`). It checks that `history_tests` is used only inside `history_inventory`, and only through `named_sources` and `INPUTS`;
- relied on the property test above to show that nothing is narrowed.

The `tools/history_tests.py` docstring now says this.

`tests/test_select_tests.py` used to count every reason other than smoke or static as a map answer (`mapped_reasons` and the presence test). The new reason is plan-wide, like smoke, so both helpers now use `PLAN_WIDE = {"smoke", HISTORY_REASON}`. My first selected run caught this: 5 presence cases failed, and they are fixed in commit 3.

## Measurements

Commands: `uv run python docs/test-speed-b1/eff-sel11/measure.py` (18 min on the VM). Evidence: `measure.json`, measured on b4ce890ed (selector behaviour as now) with main d9cff5345.

- Each row is the branch's own diff, from its merge base with main's first parent to the branch head, as a builder's `--base $(git merge-base HEAD main)` sees it.
- "Before" is the same plan without the rule.
- "Triggers" is the number of paths that fire the rule.

| Item | Paths | Map before | Map after | Impacted before | Impacted after | Lint selected (both) | Triggers |
|---|---|---|---|---|---|---|---|
| sc-5r | 5 | 30 | 30 | 473 | 473 | yes | 1 |
| me-12n | 3 | 14 | 14 | 473 | 473 | yes | 0 |
| sc-1bb | 17 | 409 | 409 | 447 | 447 | yes | 1 |
| ap-1be | 28 | 388 | 388 | 473 | 473 | yes | 1 |
| eff-20261027-1 | 23 | 35 | 35 | 473 | 473 | yes | 5 |
| eff-20261026-1b | 11 | 26 | 26 | 473 | 473 | yes | 2 |
| me-5d | 13 | 377 | 377 | 473 | 473 | yes | 0 |
| jt-2 | 27 | 474 | 474 | 473 | 473 | yes | 2 |
| me-12ab | 14 | 386 | 386 | 444 | 444 | yes | 0 |
| df-1b | 15 | 282 | 282 | 473 | 473 | yes | 5 |

- 7 of the 10 diffs fire the rule, and all 10 already selected the lint through the map or the static graph. The change adds 0 tests to these plans.
- **The two catches,** planned the same way (`/tmp` probe; it is not in the repository):
  - speed-vocabpar: its pre-merge head `365f96f1a` selected 29 units, and `a285f75c` selected 120. Both already include the lint (`reads tests/history-dependent.json`).
  - speed-trustmut: `b58fc131^1` and `b58fc131` give a full plan.
- **The lint's own runtime:** `tests/test_history_tests.py` took 31.9 s on ve-mac-1 in the selected run (6 jobs), and 98.9 s in one VM run (`uv run pytest -q tests/test_history_tests.py`). A plan that adds it costs about 0.5 to 1.7 min. In practice this is nothing, because every measured plan already had it.

### What this does not fix: the two catches came from merging main after the last selected run

- **speed-vocabpar:** the last selected run ended at 22:12:57Z (`mac-pytest.jsonl` line 717). The merge of main 8a64ef81 (`a285f75cf`), which brought the `tools/cache_store.py` rename, was committed at 22:13:50Z. No selected run saw the merged tree.
- **speed-trustmut:** the last selected run was at 09:23Z, and the main merge `b58fc131` was at 09:49Z. The candidate also held ar-10b, which the branch never saw.

No selection rule can catch a staleness that appears after the last run. The inventory is a generated file (`regen_generated.py --owner tests/history-dependent.json` gives `history-tests`). **Recommended follow-up (merge train or builder prompt, not this item):** after any merge of main into a branch, run `uv run python tools/history_tests.py --check` (16 s), or `regen_generated.py --check`. Alternatively, rerun the selected tests after a main merge. This item leaves `tools/gate.py`, the merge train and the nightly run alone, as the task required.

**Not a trigger by design** (the task's negative case): a product module the list does not name yet that gains a git call. The lint still catches it in the gate.

## Seeded bugs (all Python; no Lean or Rust changed)

Each bug was planted, its test run, and the code restored. The scripts were `/tmp/eff-sel11-seeds*.py`.

| # | File | Bug | Failing test |
|---|---|---|---|
| S1 | tools/select_tests.py | drop the `tests/` Python trigger | `test_a_change_that_can_stale_the_history_list_runs_its_lint_impacted[tests/test_vacuity.py]` |
| S2 | tools/history_tests.py | drop `tools/git_words.py` from `INPUTS` | `...runs_its_lint_impacted[tools/git_words.py]` |
| S3 | tools/history_tests.py | `named_sources` skips the map extract | `test_the_history_list_and_its_map_extract_each_name_their_sources[both]`; also `test_a_module_only_the_map_extract_names_runs_the_lint` |
| S4 | tools/select_tests.py | `--impacted` does not add the lint | `...runs_its_lint_impacted[tests/test_vacuity.py]` |
| S5 | tools/select_tests.py | the map plan does not add the lint | `test_a_change_that_can_stale_the_history_list_runs_its_lint_with_a_map[tests/test_vacuity.py]` |
| S6 | tools/history_tests.py | `named_sources` catches only OSError, so a malformed list crashes | `test_the_history_list_and_its_map_extract_each_name_their_sources[list unreadable]` |
| S7 | tools/select_tests.py | drop the named-module trigger | `...runs_its_lint_impacted[tools/cache_store.py]` |
| S8 | tools/select_tests.py | a use of `history_tests` outside `history_inventory` | `tests/test_history_tests.py::test_the_selector_reads_the_list_only_to_run_its_lint` |
| S9 | tools/select_tests.py | the rule narrows the plan (drops ALWAYS when it fires) | `test_what_the_history_list_names_only_adds_its_lint` |

## Tests run

- **New tests** in `tests/test_select_tests.py`, one per trigger kind, both paths:
  - 9 trigger paths (an edit; for `tests/` also an added file in a new directory and a deleted test) × map and impacted;
  - the 2 negatives (docs, an unlisted module) × both paths;
  - 6 `named_sources` shapes;
  - map-extract-only naming;
  - the fallback without a readable list;
  - the only-adds property.
- **Selected tests:** `zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` selected 28 of 474 units.
  - 5 presence cases failed (fixed in commit 3), and `--maxfail 5` stopped 22 units from running.
  - Rerun: `mac-pytest.sh -- -q tests/test_select_tests.py <the 22 unrun files>` gave 975 passed, 98 subtests passed, exit 0, on HEAD 5d759f07.
  - Separately: `tools/test_layer_policy.py` OK; `tests/test_history_tests.py -k 'tree_passes or command_line_lint or reads_the_list'` 4 passed on the final code.
- `uv run python tools/regen_generated.py --write` ran once; nothing changed.
- **Not run:** the full gate (the chain runs it), and `trust_mutants`, lake and `lean/audit.py` (no Lean change).
- **Pre-existing reds:** none in this selection (`main-known-red.txt`).

## DRI rulings

No user-visible behaviour of VE changes, and this is test tooling only, so there are no DELTA rows and nothing to sign. Trust +0.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is read or relayed.
2. PASS: plan items 1–3 are delivered by `tools/select_tests.py:908/922/1259` and their tests are listed above; item 3 needs no evidence bump (`regen_generated.py --write` unchanged). Measurements are in `measure.json`. No new permanent report test.
3. PASS: seeded bugs S1–S9, each with its failing test (table above).
4. N.A.: no Python, Lean or Rust semantics changed.
5. N.A.: no relayed field.
6. N.A.: the gate is the chain's; evidence is saved in `measure.json` with its commit, not read live.
7. PASS: no DELTA row and no trust growth (this report, "DRI rulings").
8. PASS: no user-visible change; only the test plans of `tools/select_tests.py` change (`test_what_the_history_list_names_only_adds_its_lint`).
9. PASS: the selected run on this branch selected 28 of 474 units (not all), including `tests/test_history_tests.py` via this rule. Seed S5 is in that selection (`test_select_tests.py`).
10. N.A.: no Lean.
11. N.A.: no budgets or deadlines; the new tests use none.
12. N.A.: selection reads two small JSON files once per plan; no CPU path in VE changed.
13. N.A.: no test removed or renamed (`test_only_the_lint_reads_the_list` is edited, not renamed).

## FIXMAP
- `tools/select_tests.py`: the selector.
  - `HISTORY_TEST`, `HISTORY_REASON` `:81-82`
  - `history_inventory` `:908`
  - map path: `finish` `:922`, add at `:931`
  - `--impacted`: `impacted` `:1259`
  - plan key `history_inventory` `:976`, `:1266`
  - module docstring bullet
- `tools/history_tests.py`: owns the list's format. `INPUTS` `:69`, `named_sources` `:1128`, docstring line on the selector.
- `tests/test_select_tests.py`:
  - `PLAN_WIDE` `:1330` (used by `mapped_reasons` and the presence test)
  - history block from `:2259`: `HISTORY_TRIGGERS`, `HISTORY_NEUTRAL`, `history_changes`, the map-path tests `:2284/:2295`, fixture `lint_unreached` `:2304`, the impacted tests `:2313/:2320`, `named_sources` shapes `:2348`, map-extract only `:2353`, fallback `:2363`, only-adds `:2372`
- `tests/test_history_tests.py`: reader guard `test_only_the_lint_reads_the_list` `:317`; `test_the_selector_reads_the_list_only_to_run_its_lint` `:328`.
- `docs/TESTING.md`: the "History inventory" selection rule.
- `docs/test-speed-b1/eff-sel11/`: `measure.py` (the measurement), `measure.json` (saved evidence), this report.
- Regression tests:
  - `uv run pytest -q tests/test_select_tests.py -k 'history or presence_alike or mapped'`
  - `uv run pytest -q tests/test_history_tests.py -k 'reads_the_list or tree_passes or command_line_lint'`
- Generated files: none changed. If an input changes, run `uv run python tools/regen_generated.py --write` (`tests/history-dependent.json` is the `history-tests` entry).
- `trust_mutants`: not used (no Lean).
## END FIXMAP
