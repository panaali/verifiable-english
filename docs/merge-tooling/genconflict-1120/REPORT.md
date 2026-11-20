# train-queue-genconflict-1120: regenerate files that carry hashes of a use-case environment

Nothing is reserved for the DRI. No DELTA row: this changes merge tooling only, not what any checker answers.

SIZE: 188 product, 479 tests, 209 other hand-written lines (`git diff --numstat 941208a1 HEAD`: product =
tools/regen_generated.py +177 and docs/en-e3-norm/en-2b/route_fixtures.py +11; tests = tests/test_regen_usecase_merge.py
+446 and tests/test_regen_generated.py +33; other = docs/merge-tooling.md +20, replay.py +169, and this report's
summary rows. Generated files and records left out: .gitattributes, docs/codemap/*, tests/history-dependent.json,
mutants.json, replay.txt, tests-on-main.txt and trust-mutants.json).

## What changed (tools/regen_generated.py)

Three entries now cover the four files the decision names (DRI decision 20261120 item 1), plus `spans.json`, which
`build_document.py` writes together with `coverage.json`:

| Entry | Files | Merge | Writer / check | Runs |
|---|---|---|---|---|
| `english-lexicon-report` | conformance/english-lean/lexicon-report.json | `derived` | `python -m conformance.english_lean_lexicon` / rewrite and compare; `service="write"`; fresh = tests/test_english_lean_lexicon.py::test_every_corpus_environment_has_a_valid_selected_lexicon | every write, check and resolve |
| `recorded-route-cases` | tests/data/route-cases.jsonl | `keyed-lines` | `route_fixtures.py --write` / `--check` (new flag); `service="write"`; fresh = tests/test_english_statement_blocks.py::test_the_route_fixtures_are_recorded | every write, check and resolve |
| `usecase-safety-framework` (`_usecase("safety-framework")`) | usecases/safety-framework/{results,coverage,spans}.json | `derived` | `run.py`, then `build_document.py` / their `--check`; `service="write"` | `on_conflict` only |

* **`derived` strategy** (task 1d). `merge_text(..., resolving)`: if only one side changed the file, that side is
  kept; if both sides made the same change, it is kept. If both sides changed it differently, the git driver
  (`--merge-driver`) writes git merge-file's text with conflict markers and exits 1. A plain `git merge` therefore
  stops on the file as it does today. `--resolve` (`resolving=True`) takes ours, and the writers then run on the
  merged tree.
* **`keyed-lines` strategy** (task 1b), in `merge_keyed_lines`. Recorded lines are grouped by key `(mode, case id)`:
  lines that share a key form one group, and a line with no id is a group of its own. Merge rules per group:
  * a group changed by one side takes that side;
  * the same change on both sides is taken once;
  * different changes on both sides raise `Conflict`. The driver exits 1, `--resolve` exits 2 with "needs a person"
    and writes nothing.

  Order: ours' lines keep their places, a group that theirs changed replaces ours' first line of that group, and
  theirs' new groups follow in theirs' order. All of these come before the english.statement block. A recorded line
  is never silently resolved to ours.

  **Deviation from the task text:** the english.statement block is merged as a `derived` file. A one-sided change
  is taken; a two-sided change stops the driver; `--resolve` takes ours, and the writer then rewrites the block.
  The task said "a merge takes ours" on the assumption that the entry could be `at_merge`. It cannot (next bullet).
  Taking ours in the driver would then leave a stale block after a plain `git merge`. That is the case 1d rules out,
  so I took the conservative choice.
* **`at_merge` is NOT set on `recorded-route-cases`.** `route_fixtures()` loads the rsp and fsf use-case environments
  (`use_case()` in tests/test_english_statement_blocks.py), and loading them starts ve_service. The repository's
  trap test caught this when the entry was not marked: tests/test_regen_generated.py::test_the_entries_that_import_the_client_only_never_start_the_service
  failed with `recorded-route-cases`. The task's "1 s, no service" measurement presumably ran with a warm service.
  `at_merge` entries must start no service (test_the_entries_refreshed_at_merge_are_tree_only_writers), so the
  entry has `service="write"` and no `at_merge`.
* **`on_conflict`** (task 1c). `on_demand(entries, only, conflicted)` decides whether the use case runs:
  * a plain `--write`, `--check` or `--names` drops it unless `--only` names it;
  * `--resolve` runs it when the conflicted set contains one of its files. The conflicted set is the unmerged paths
    plus `changed_on_both_sides`: the files where merge-base, HEAD and MERGE_HEAD all differ. The second part matters
    because merge-train's first step, `--resolve --only lake-build --only checker-pins`, resolves and stages every
    conflicted file, so the full `--resolve` after it sees no unmerged paths. test_a_use_case_conflict_runs_it_also_after_a_partial_resolve
    covers this;
  * a failing writer (for example no pinned FSF text) makes `--resolve` exit 1 (test_a_failed_use_case_writer_fails_the_resolve).

  `_usecase(name)` builds the entry, so another use case of the same shape is one line.
* `.gitattributes` was regenerated by its own entry (5 new lines). `route_fixtures.py` moved out of `NOT_REGENERATED`.
  `usecases/*/*.py` stays there with a note that a use case of `_usecase`'s shape is an entry.
* I found and fixed a defect in my first draft: main already has an entry named `route-cases`
  (lean/VE/Route/examples/route-cases.json), and my draft reused the name. New test test_entry_names_are_unique
  catches this; it failed with the first draft's name (mutants.json, last row).

No entry that was already in GENERATED changed behaviour: `merge_text` for `regenerate`, `union` and `json` runs the
same code, and `union` now goes through the `_merge_file` helper. Evidence: tests/test_regen_generated.py passes
unchanged apart from the invariants listed below (66 tests, `uv run pytest -q tests/test_regen_generated.py`).

## Tests

New file: tests/test_regen_usecase_merge.py, 21 tests. It is hermetic: scratch git repositories, with the writers
replaced by a small deterministic stub script that hashes the scratch environment the way the real writers do. It
needs no service. Invariants added in tests/test_regen_generated.py:
* test_entry_names_are_unique;
* test_the_environment_hash_files_are_regenerated_and_slow_ones_only_on_conflict;
* the `at_merge` invariant now also refuses `on_conflict`.

| Task item | Test |
|---|---|
| (i) both branches add an environment row, a recorded case with a new key, a changed english.statement fixture and a use-case case; `--resolve` exits 0; all five files are byte-identical to the writers run on the merged sources in a fresh directory | test_resolve_regenerates_environment_hash_conflicts_to_the_writers_output |
| (ii) the same recorded route case changed differently on both sides: exit 2, "needs a person", nothing written, MERGE_HEAD kept, no writer run | test_a_recorded_route_case_both_sides_changed_differently_declines |
| (ii) the same legend of the environment source changed on both sides: exit 2, and the source is the only file named | test_the_same_environment_legend_changed_on_both_sides_declines |
| (iii) the driver stops on a two-sided `derived` change and keeps a one-sided one; the attribute is `ve-generated` | test_the_driver_stops_on_a_derived_file_both_sides_changed, test_the_driver_takes_a_one_sided_change_of_a_derived_file, test_merge_text_of_a_derived_file[4 files] |
| keyed-lines merge, accept and refuse directions | test_keyed_lines_merge_by_mode_and_id, test_keyed_lines_refuse_a_group_both_sides_changed_differently[4], test_the_driver_merges_recorded_route_cases_by_key[driver on/off] |
| (iv) a plain --write, --check, --names or --resolve without a use-case conflict runs neither run.py nor build_document.py; `--only` runs them | test_plain_write_check_and_names_skip_the_use_case, test_a_resolve_without_a_use_case_conflict_skips_it |
| the two-step train resolve; a failed writer gives exit 1 | test_a_use_case_conflict_runs_it_also_after_a_partial_resolve, test_a_failed_use_case_writer_fails_the_resolve |
| route_fixtures.py --check | test_route_fixtures_check_fails_on_a_stale_block_and_passes_after_write |

**On main** (docs/merge-tooling/genconflict-1120/tests-on-main.txt: this branch's tests run against main's
tools/regen_generated.py and route_fixtures.py): 19 failed, 2 passed. For (i), main's `--resolve` returned
"conflicts outside the generated files (agent sync needed): conformance/english-lean/lexicon-report.json ...". The two
that pass on main are the controls of behaviour that must not change, because git's own merge also stops there:
* test_the_driver_stops_on_a_derived_file_both_sides_changed;
* test_the_driver_merges_recorded_route_cases_by_key[False].

**On the branch**: `uv run pytest -q tests/test_regen_generated.py tests/test_regen_usecase_merge.py -n 4` gives
86 passed (/tmp/genc-rg4.log), and the route_fixtures test added after that run passes too (1 passed, /tmp/genc-rf.log).
tests/test_merge_tooling_evidence.py: 5 passed after the doc table gained the three rows.
Selected run: see "Selected tests" below.

## Replay (task 3): docs/merge-tooling/genconflict-1120/replay.py, replay.txt

Method: for each pair, a scratch worktree (~/code/ve-genconflict-replay-1120, created from main and restored by
lean-prep; removed afterwards; never ve-integration) checks out the first commit. An overlay commit adds this
branch's tools/regen_generated.py, .gitattributes and route_fixtures.py. Then
`git merge --no-commit --no-ff <second>` runs with the repository's `ve-generated` driver, followed by the train's two
steps: `--resolve --only lake-build --only checker-pins`, then a plain `--resolve`. The five derived files are
compared with the agent sync's result commit. Tools at 407c7f2a; run at 2026-11-20T15:40Z on multi-agent-lab.

| Pair | git merge conflicted on | build+pins step | plain --resolve | lexicon-report | route-cases | results | coverage | spans |
|---|---|---|---|---|---|---|---|---|
| f1 228142ff + ef7ecd59 -> f02219f5 | the four files | exit 0, 3 s | exit 0, 1337 s (use case 422 s) | byte-equal | byte-equal | byte-equal | byte-equal | byte-equal |
| f2 61b159e4 + 727d1d21 -> 505ec3a5 | the four files | exit 0, 2 s | exit 0, 837 s (use case 368 s) | byte-equal | byte-equal | byte-equal | byte-equal | byte-equal |
| f7 23d551568 + 09bea097 -> f4df75c5 | the four files | exit 0, 2 s | exit 0, 664 s (use case 304 s) | byte-equal | byte-equal | byte-equal | byte-equal | byte-equal |

One other file differs from the agent's tree in each replay: tests/history-dependent.json. That comes from this
branch's own change. The overlaid regen_generated.py adds git calls (`_merge_file`, `changed_on_both_sides`) that the
history-tests writer lists. This branch commits the same regeneration (`history_tests.py --check` was rc=1 on the
branch before it, rc=0 on each agent commit).

An earlier replay with the first draft (tools 3a7ebb02, route cases still `at_merge`, the block taking ours in the
driver) also gave byte-equal results for all five files in all three pairs. In that draft git's merge conflicted on
three files, because the driver took ours on the route cases' block. The final rules stop on it, which is what the
train log shows.

## Plain --resolve time, before and after (task 1c)

replay.txt, last section: a clean merge of a one-line doc commit into main e9b129ed, then a plain `--resolve` with
each tool, on the loaded VM:

| Tool | Exit | Wall | Entries run | New entries |
|---|---|---|---|---|
| main's | 0 | 463 s | 38 | none |
| this branch's | 0 | 470 s | 40 | english-lexicon-report 3.7 s, recorded-route-cases 1.4 s (write + check) |

The use-case entry did not run. The growth that can be attributed to the change is 5.1 s, which matches the 7 s
wall difference. An earlier round on the first draft measured 400 s against 460 s. The per-entry log put that
difference in unrelated entries (kernel-closure check +33 s, history-tests +15 s): VM load, not this change.

## Use cases that fit `_usecase` (not registered)

Measured over the whole merge-train.log: 176 "generated-file resolve declined" lines.
* Use-case files named in them: safety-framework only (coverage.json 23, results.json 13; plus 3 source files and
  one REPORT.md).
* Other files in them: route-cases.jsonl 35, lexicon-report.json 23.
* Use cases with the same run.py / build_document.py / {results,coverage,spans}.json shape: `anthropic-rsp` and
  `openai-preparedness` (`ls usecases/*/`). Neither appears in a declined resolve, so neither is registered. Each
  would be one line, `_usecase("anthropic-rsp")`, once its build_document.py's pinned source is checked the same way.

## Seeded bugs (Python; no Lean or Rust changed): docs/merge-tooling/genconflict-1120/mutants.json

Eight mutants, all killed. Each was run with /tmp/genc-seed.py, which plants the bug, runs the named tests and
restores the file; `git diff` was clean afterwards.

| Behaviour | File | Failing test |
|---|---|---|
| the driver keeps ours on a two-sided `derived` change | tools/regen_generated.py | test_merge_text_of_a_derived_file, test_the_driver_stops_on_a_derived_file_both_sides_changed |
| a recorded group both sides changed is resolved to ours silently | tools/regen_generated.py | test_keyed_lines_refuse_a_group_both_sides_changed_differently, test_a_recorded_route_case_both_sides_changed_differently_declines |
| theirs' new recorded groups are dropped | tools/regen_generated.py | test_keyed_lines_merge_by_mode_and_id, test_resolve_regenerates_environment_hash_conflicts_to_the_writers_output |
| plain runs include the `on_conflict` use case | tools/regen_generated.py | test_plain_write_check_and_names_skip_the_use_case, test_a_resolve_without_a_use_case_conflict_skips_it |
| the conflict is forgotten after the partial resolve | tools/regen_generated.py | test_a_use_case_conflict_runs_it_also_after_a_partial_resolve |
| the use-case entry loses `on_conflict` | tools/regen_generated.py | test_the_environment_hash_files_are_regenerated_and_slow_ones_only_on_conflict |
| route_fixtures.py --check always passes | docs/en-e3-norm/en-2b/route_fixtures.py | test_route_fixtures_check_fails_on_a_stale_block_and_passes_after_write |
| two entries share a name | tools/regen_generated.py | test_entry_names_are_unique |

trust_mutants: light-lane said NOT (1090 changed lines). The sweep ran through `mac-pytest.sh --trustmut -- --base
941208a1`: 0 definitions, 0 mutants, exit 0 (trust-mutants.json). No Lean changed.

## Selected tests

`zsh mac-pytest.sh --select -- --base 941208a1 --run` on cda87704 (ran on ve-cloud-2, x86_64): exit 0 in 6893 s;
the changed test files ran first (tests/test_regen_usecase_merge.py exit 0, tests/test_regen_generated.py exit 0;
tests/test_merge_tooling_evidence.py exit 0); "recorded 663 units ...; 0 failed" (/tmp/genc-select2.log lines 77-81,
763-765). An earlier selected run on 407c7f2a stopped in its fast stage on
tests/test_merge_tooling_evidence.py::test_the_generated_file_table_names_every_entry: the doc's entry table lacked
the three new rows. Fixed in 50b131dd (5 passed). The commits after cda87704 add only this report.

## Notes for the DRI

* The task's "route_fixtures.py: 1 s, no service" is not right for a cold run: the writer starts ve_service, so
  the entry cannot be `at_merge`. Because of that, the block's two-sided change stops the driver (above). Effect: a
  plain `git merge` of two FSF siblings stops on route-cases.jsonl as well. This is the same set of four files the
  train log names, and `--resolve` settles it.
* The out-of-scope follow-on (specregen-resolve-fallback-1120) can rely on this: the spec regen's `git merge` stops
  on all of these files, and `--resolve` settles them when the pinned FSF text is present.
* A clean merge where one side changed results.json and the other changed only its environment still leaves
  results.json stale. That is unchanged from today: the use case runs only on a conflict, as the task asks.
  tests/test_safety_framework.py catches the stale file in the gate.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relayed answer or schema changed.
2. Deliverables built: PASS. 1a, 1b, 1c, 1d and 1e are the tables above; 2(i)-(iv) are the tests table; 3 is replay.txt; the out-of-scope items were not touched.
3. Tests can fail: PASS. mutants.json has 8 of 8 killed; tests-on-main.txt has 19 failing on main.
4. Python/Lean/Rust agree: N.A., no checker path changed. The replay byte-equality against the agent's commits stands in for the base-vs-head comparison here.
5. R8 binding: N.A., no relayed field.
6. Gate evidence on the final HEAD: PASS by process. The chain runs the gate on the committed final HEAD; replay.txt and tests-on-main.txt are saved records, not live diffs.
7. No unsigned item: PASS. No DELTA row and no trust growth (trust-mutants.json: 0 definitions).
8. Every user-visible change in DELTA: N.A. Only merge tooling changed; no checker output, code or text changed (the `ve` package is untouched: `git diff --stat 941208a1 HEAD -- ve lean rust` is empty).
9. Test selection: PASS. The selected run's plan includes tests/test_regen_usecase_merge.py and tests/test_regen_generated.py for this diff (/tmp/genc-select2.log).
10. Lean statements: N.A., no Lean.
11. Budgets fail closed: PASS. A failed or missing use-case writer exits 1 (test_a_failed_use_case_writer_fails_the_resolve). Subprocesses use HANG_TIMEOUT; no sleeps.
12. CPU/memory: PASS. Plain --resolve grew by 5.1 s of new entries (replay.txt timing); the use case runs only on a conflict (test_plain_write_check_and_names_skip_the_use_case).
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions: PASS. Each check is tested on both sides: derived one-sided vs two-sided, keyed accept vs refuse, on_conflict skip vs run, route_fixtures --check stale vs fresh.
15. Overclaim, silent cut, checks can fail, limits: PASS. The universal claims above cite a test or a record; the one deviation (block strictness, no at_merge) is stated with its cause; nothing was cut.
