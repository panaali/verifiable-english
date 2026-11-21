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
the three new rows. Fixed in 50b131dd (5 passed). After cda87704 come this report and c67cf14f: a reflowed docstring and one expression split over two lines in
tools/regen_generated.py, with no behaviour change. After it, the affected tests passed again: `-k "environment_hash or keyed
or listing or gitattributes or unique or derived or route_fixtures"` gave 20 passed (/tmp/genc-final.log).

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

## Addendum: genconflict-hashcheck-1120, the masked-merge check on `--resolve`

Status: built; selected run exit 0; the chain's gate on the final HEAD is pending. Nothing is reserved for the DRI and
there is no DELTA row (merge tooling only). Trust: none (sweep `hashcheck-trust-mutants.json`: 0 definitions, exit 0).
Covers reviews/dri-decisions-20261120-genconflict-hashcheck.md item 1, the condition from
reviews/dri-decisions-20261120-adv1604.md item 1.

SIZE: 133 product, 172 tests, 117 other hand-written lines (`git diff --numstat main...HEAD`, added + removed:
tools/regen_generated.py 130+3; tests/test_regen_usecase_merge.py 170+2; docs/merge-tooling.md 3+1 and this addendum.
Left out as generated files or records: tests/history-dependent.json, hashcheck-mutants.json and
hashcheck-trust-mutants.json).

**The check (tools/regen_generated.py).** The new `Generated.masked` field holds (path, hash keys) pairs, and
`_usecase` fills it from one constant, `USECASE_HASHES`: results.json `certificate_sha256`, coverage.json
`document_sha256`, spans.json none. Another use case with the same shape is still one line, `_usecase(name)`.
In `resolve()`:
1. Before anything is written, `_masked_merges` takes base, ours and theirs of each masked file both sides changed.
   It reads the index stages :1/:2/:3 when the path is unmerged. When an earlier `--resolve --only lake-build --only
   checker-pins` already staged the path (the train's real order), it reads the merge base, HEAD and MERGE_HEAD.
   It masks the hash keys at any depth (`_mask`) and merges with the existing `merge_json` (one owner of the
   three-way rule). A key both sides changed differently raises Conflict: exit 2, "needs a person or the sync
   agent", no writer run, nothing written.
2. The resolve snapshots the index file and the work-tree bytes of the conflicted paths and of every generated file.
3. After the writers ran, `_check_masked` masks each regenerated file and compares it with the merge exactly (values
   compared through `_text`, so `true` is not `1`; object key order is ignored).
4. On the first difference it restores the snapshot (`_restore`: the index, which keeps the original conflict
   stages, the files, and the removal of generated files written since). It then exits 2 with
   `<path> at <key path>: the regenerated file differs from the three-way merge of its two sides outside its hash
   fields; the conflicted merge is restored (agent sync needed)`. MERGE_HEAD stays, so the train falls back to the
   agent sync as before.
5. On acceptance it prints `checked <path>: ...` once per file and goes on to the checks and staging unchanged.

Entries without `masked`, and resolves where none of the use case's files conflicted, take exactly the old path.

**spans.json.** It has no hash-only drift. Its one hash, `source_sha256`, is the constant `TEXT_SHA256` of the
pinned FSF text (build_document.py:36, :791), and it was identical at base, ours, theirs and the agent's commit in
f1, f2 and f7 (`git show <c>:usecases/safety-framework/spans.json | sha256sum`: 8de30da4 in all twelve). Its
non-hash content can change with the source: `master()` sets each unit's status from the measured document and
results.json (build_document.py:759-770). So the same check applies to it, with nothing masked.

**Tests (tests/test_regen_usecase_merge.py, section (v)).** All are hermetic: a scratch repository, a stub writer
(`VERDICT_STUB`, with goals that each carry a verdict and nested certificate hashes), no service.
* (a) `test_hash_only_drift_with_disjoint_goals_resolves_to_the_writers_output[False|True]`. Both sides change only
  the hashes, plus one goal each. Expect exit 0; a `checked` line for results, coverage and spans; fresh hashes; the
  four goals. `[True]` first runs a staging `--resolve`, as the train does.
* (b) `test_a_flipped_verdict_neither_side_changed_declines_and_keeps_the_conflict[False|True]`. The writer flips
  g1's verdict. Expect exit 2 naming `usecases/safety-framework/results.json at $.goals[0].verdict`. The writers ran
  but the checks did not. Status, unmerged list, `ls-files --stage` and the three files equal the state before the
  resolve, conflict markers included, and MERGE_HEAD is kept.
* (c) `test_a_verdict_both_sides_changed_differently_declines_before_the_writers`. Each side overrides g1's verdict
  in its own source file, so the sources merge cleanly. Expect exit 2 with `results.json: $.goals.g1.verdict: both
  sides changed it`, no writer run and the state unchanged.
* Also added: `test_the_use_case_entry_names_its_hash_fields`, and `test_masked_first_difference` (5 cases: a
  nested hash is masked; a nested value, a list length, an extra key and `true` vs `1` each differ).
* Changed: the old stub's coverage `units` was a count, which no three-way merge can produce when both sides add a
  case (both 2, merged tree 3). It is now the case list, so test (i) still exercises an acceptance.

On main's tools/regen_generated.py (copied in for the run, then restored;
`pytest tests/test_regen_usecase_merge.py -k "hash_only or flipped_verdict or ..."`, /tmp/ghc-main.log), all 11
failed:
* (b) and (c) failed with `assert 0 == 2`: main accepts the flipped verdict and the two-sided change.
* (a) failed with `AttributeError: 'Generated' object has no attribute 'masked'`. Main also exits 0 on this input;
  the test fails on main through the hash constant and the `checked` lines it asserts.
* The helper tests failed with AttributeError.

On the branch: tests/test_regen_usecase_merge.py 32 passed (/tmp/ghc-t2.log). Selected run
`mac-pytest.sh --select -- --base 99f10440 --run` on aa68eef5: exit 0 in 6790 s (ve-cloud-2). The changed file ran
first (tests/test_regen_usecase_merge.py exit 0, 339 functions). tests/test_regen_generated.py,
test_history_tests.py and test_merge_tooling_evidence.py exit 0, with no FAILED line in the log (/tmp/ghc-sel-run.log).
Test selection picks the file for tools/regen_generated.py statically ("imports tools/regen_generated.py; names
tools/regen_generated.py": `select_tests.py --paths tools/regen_generated.py --explain`).

**Replay of f1 (228142ff + ef7ecd59 -> f02219f5).** The service and the pinned text (sha256 18e3375b...) are on this
host. replay.py ran with PAIRS cut to f1, using this branch's tool at aa68eef5, in a scratch worktree that was
removed afterwards. Output (2026-11-20T21:56Z, multi-agent-lab):

    git merge (driver installed): exit 1; conflicted: lexicon-report.json route-cases.jsonl coverage.json results.json
    --resolve --only lake-build --only checker-pins: exit 0, 48 s
    --resolve: exit 0, 1376 s; new entries: english-lexicon-report 4.0 s, recorded-route-cases 1.7 s, usecase-safety-framework 451.5 s
    all five files byte-equal to the agent's result; other files differing: tests/history-dependent.json (as before)

The check therefore accepted f1 on the train's real path (files staged by the first step, sides read from the
commits). Without the service, the same comparison on the stored blobs (base / ours / theirs / agent result, through
`_masked_json`, `merge_json` and `_first_difference`) accepts all three files of f1, f2 and f7.

**Seeded bugs (Python; no Lean or Rust changed): docs/merge-tooling/genconflict-1120/hashcheck-mutants.json.** Each
was planted in tools/regen_generated.py, the test file was run, and the file was restored. All 6 were killed:

| Behaviour broken | Killed by |
|---|---|
| mask only top-level hash keys | test_hash_only_drift_with_disjoint_goals_resolves_to_the_writers_output |
| skip the post-writer comparison | test_a_flipped_verdict_neither_side_changed_declines_and_keeps_the_conflict |
| swallow a two-sided masked conflict | test_a_verdict_both_sides_changed_differently_declines_before_the_writers |
| decline without restoring | test_a_flipped_verdict_neither_side_changed_declines_and_keeps_the_conflict |
| compare with `==` (`true == 1`) | test_masked_first_difference |
| forget files an earlier `--resolve --only` staged | test_a_flipped_verdict_...[True], test_hash_only_...[True] |

trust_mutants: light-lane said NOT (309 changed lines). `mac-pytest.sh --trustmut -- --base 99f10440`: 0
definitions, 0 mutants, exit 0 (hashcheck-trust-mutants.json).

### Notes for the DRI

* The check is stricter than hash-only. A derived count that both sides moved the same way, while the merged tree
  moves it further, now declines: for example, both sides add one goal and coverage's residual count goes 1 -> 2 on
  each side but 3 on the merged tree. That is the accepted condition read literally (the conservative option). f1,
  f2 and f7 have no such field and accept. A use case whose coverage carries such totals will go to the agent sync
  on those merges.
* Only files in the conflicted set are checked, as the condition says. A use-case file only one side changed is
  still taken from the writers unchecked when the entry runs.
* results.json also carries `document_hash`, `decision_record_id` and `environment_id` under `d2_d3`. They are not
  masked, because the condition names only `certificate_sha256` and `document_sha256`. If they drift with the
  environment, such a merge declines (none did in f1, f2 or f7).

## Addendum: specregen-reinstall-allregen-1121, every file of the use case checked

Covers reviews/dri-decisions-20261121-adv0013.md item 1. No DELTA row; trust: none (light lane LIGHT, 97 lines, no
trusted-core file). Nothing is reserved for the DRI.

SIZE: 25 product, 72 tests, 70 other hand-written lines (this addendum; allregen-mutants.json is a record).

**The check.** `_masked_merges` now takes every `masked` file of the entries the resolve runs, conflicted or not.
An unmerged path is read from the index stages :1/:2/:3, as before. Every other path is read from the merge base,
HEAD and MERGE_HEAD. `merge_json` of the masked sides then gives the changed side for a one-sided file and base for
a file neither side touched. Before this change, a file git merged cleanly was taken from the writers unseen: for
example, results.json when only theirs changed it and the conflict was on spans.json. Now any difference declines
exactly as before: exit 2, `<path> at <key path>`, the snapshot restored (index, files, generated files written
since), MERGE_HEAD kept. Which entries run is unchanged: still a two-sided change of one of the entry's files, or
`--only`. Nothing else in tools/regen_generated.py changed.

**Tests (tests/test_regen_usecase_merge.py).** The verdict stub's spans.json is now one line and also names the
texts of document/*.txt, which only `document` reads. Two sides changing it differently therefore conflict in git
while the JSON still merges.
* `test_a_onesided_flip_of_a_results_file_only_theirs_changed_declines[False|True]` (the DRI condition test).
  Ours adds document/o.txt; theirs adds goal t. Only spans.json conflicts, and results/coverage changed on theirs
  only (both asserted). The writer flips g1. Expect exit 2 naming `results.json at $.goals[0].verdict`, the writers
  run but not the checks, and `_state` (status, unmerged list, `ls-files --stage`, the three files) equal to the
  state before the resolve. results.json must equal theirs, not the stub's output, and the conflict markers stay.
* `test_an_untouched_flip_of_a_results_file_neither_side_changed_declines[False|True]`. Each side adds its own
  document text. results.json is untouched, so its merge is base's, and the flip declines the same way.
* `test_one_sided_and_untouched_files_equal_to_their_merge_resolve[onesided|untouched]`. The same merges without a
  flip exit 0, with a `checked` line for each of the three files, and commit clean.
* hash_only, flipped_verdict and both-sides tests: unchanged and passing.

On main's tools/regen_generated.py (cebf4fd2, copied in and then restored): 6 failed, 32 passed. Both flip tests
fail with `assert 0 == 2`, because main accepts the flipped verdict. The control tests fail because main prints
`checked` for spans.json alone. On the branch: 38 passed. Selection picks the file for tools/regen_generated.py
alone (`select_tests.py --paths tools/regen_generated.py --explain`: "imports tools/regen_generated.py"). Selected
run on d641d04f: exit 0 (ve-cloud-2, 2520 s). Records are in
manage-agents/reviews/specregen-reinstall-allregen-1121/ (onesided-flip-on-main.txt, selected-run.log).

**Replay of f1 (228142ff + ef7ecd59 -> f02219f5)** with this branch's tool d641d04f and the service and pinned text
on this host (replay.py, PAIRS cut to f1, scratch worktree removed afterwards; 2026-11-21T02:10Z, multi-agent-lab):

    git merge (driver installed): exit 1; conflicted: lexicon-report.json route-cases.jsonl coverage.json results.json
    --resolve --only lake-build --only checker-pins: exit 0, 31 s
    --resolve: exit 0, 1014 s; new entries: english-lexicon-report 3.2 s, recorded-route-cases 1.4 s, usecase-safety-framework 297.6 s
    all five files byte-equal to the agent's result; other files differing: tests/history-dependent.json (as before)

spans.json, untouched in f1, is now checked against base and accepted.

**Seeded bugs (Python only, tools/regen_generated.py; allregen-mutants.json).** Each was killed:

| Behaviour broken | Killed by |
|---|---|
| check only conflicted files (main's filter put back) | the onesided_flip, untouched_flip and control tests (6) |
| read theirs from HEAD for a clean file | test_one_sided_and_untouched_files_equal_to_their_merge_resolve[onesided] (and hash_only[True]) |
| decline without restoring | the onesided_flip, untouched_flip and flipped_verdict tests (6) |

### Notes for the DRI

* This check is stricter than the conflicted-set check. Under `--resolve --only usecase-<name>` with none of its
  files changed by either side, any regenerated difference outside the hashes now declines, because the merge is
  base. That is the condition read literally (the conservative option). The train passes `--only` only for
  lake-build and checker-pins.
* The merge-train resolve copy is staged as manage-agents/merge-train.sh.new-allregen. It is a byte copy of
  merge-train.sh.bak-adv0013-specregen-20261121T0021Z (md5 adf140bb), because the installed file was still md5
  2b98c9a2. It is not installed; installing it waits for this item to be on VE main.
