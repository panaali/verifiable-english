# speed-tmrescore: rescore an unchanged tree from its last trust_mutants run

No DRI signature is needed: DELTA.md has no rows (tooling only), and trust is +0 (no Lean change).

Infra item speed-tmrescore (acting DRI dri-improve, 2026-10-21 07Z; PIPELINE-LIMITS L91). The tool is
`tools/trust_mutants.py --rescore PREV.json`. The tests are in `tests/test_trust_mutants.py`. Section 1's table
comes from `docs/speed/tmrescore/measure.py`, which reads committed evidence only (git history; D4). The seeded
bugs are in `mutants.json`, with their results in `mutants-evidence.json`.

## 1. Measure: consecutive sweeps of one item on identical Lean inputs (Oct 19-21)

`measure.py` reads every committed version of each item's evidence JSON on all refs, the checkpoint stashes
included. Each distinct blob counts as one run, in the order it was first committed. For each two consecutive runs
of one item, it diffs lean/ and the --test files between the two runs' `head`s. A run on uncommitted changes reads
as its `head`. ap-1b committed no evidence JSON (only its allow file), so its rows are the task's, as given.

| item | first | second | mutants run | identical inputs | second took (min) | note |
|---|---|---|---|---|---|---|
| ap-1b (given) | 1034a4de6, 01:38-03:56Z | 1034a4de6, 03:56-07:16Z | ~132 | y | ~200 | one allow entry added; ended 130 KILLED, 2 UNKNOWN (load 46) |
| ap-1b (given) | 1034a4de6, 03:56-07:16Z | 1034a4de6, from 07:16Z | ~132 | y | ~200 (running; as the last) | one more allow entry; a full rerun again |
| df-1ac | ccf71608f | 6bd8247b0 | 90 | n | 20 | 7 files differ |
| df-1ac | 6bd8247b0 | f484e28cc | 90 | n | 13 | 6 files differ |
| df-1ac | f484e28cc | 1ed5cc2a9 | 90 | n | 99 | 7 files differ |
| me-2 | 83fb411fa | f0988ac6a | 161 | n | 9 | 4 files differ |
| me-2 | f0988ac6a | 261596835 | 156 | n | 11 | 2 files differ |
| me-2 | 261596835 | 261596835 | 156 | y | 8 | same head; the allow file gained 2 entries (2 SURVIVOR -> ALLOWED) |
| me-2 | 261596835 | cfee74b09 | 156 | n | 21 | 10 files differ; base differs (synced with main) |
| me-9b | 6369f18b5 | 7c63292cb | 46 | n | 18 | 5 files differ |
| sc-1ad | 3eb6bb51a | c1903fd95 | 163 | n | 63 | 2 files differ |
| sc-1ad | c1903fd95 | a22ec823c | 163 | n | 55 | 2 files differ |
| sc-1ad | a22ec823c | fc0c533ea | 163 | n | 12 | 2 files differ |

There are 3 identical-input reruns. The two completed ones took ~208 min, and ap-1b's third was still running at
07:16Z (~200 min more at the second's pace). That is at least 3 reruns, and they total far over 2 h, so the stop
rule does not apply. Every non-identical pair changed real inputs: an `Examples.lean` file (new checks) with its
`declarations.txt`, or a definition. A digest of the bytes correctly gives a full run for each of those.

With `--rescore`:
- me-2's rerun and ap-1b's second run (allow-only) build nothing.
- ap-1b's third run builds its 2 UNKNOWN mutants and one control build.

That is about 6.8 h of VM time on Oct 21 (ap-1b's two reruns and me-2's) down to one control build and two mutants.

## 2. Orchestrator lines (not applied here: /home/seyran/code/manage-agents is read only for this item)

1. BUILDER-CHECKLIST.md item 3, at the end of the R16 sub-bullet ("... Commit the evidence JSON and the allow
   file."), add: `After an allow-only edit or for UNKNOWNs, rerun with --rescore <the last evidence JSON>; a code
   change still needs a full run.` Add the same sentence at the end of prompts/build-checklist.txt line 13a.
2. Review prompt (where it tells reviewers to rerun trust_mutants on the HEAD): `Reviewers may run without
   --rescore (a full run on the HEAD) and compare with the committed evidence; a rescored evidence JSON marks each
   reused verdict "reused_from": <head> and records "rescore": {file, head, reused, rerun}.`
3. mac-pytest.sh does not pass the PREV file through. `--rescore` is not in its two-value list, so its value is sent
   unchanged. An absolute VM path does not exist on the runner. The tool then says "a full run, since it cannot be
   read (FileNotFoundError ...)" and runs everything: it fails safe, but it wastes the run. The change, in the
   `--trustmut` argument loop:
   - line 92: `case $a in --jobs|--json|--test|--allow|--rescore|--root|--base|--max-mutants|--build-timeout) v=${args[$((i+1))]}; two=1;;`
   - line 98: `--test|--allow|--rescore) rv=${v:A}; [[ $rv == $w/* ]] || run_local "trust_mutants $a $v is not in the worktree $w"; margs+=($a ${rv#$w/});;`

   PREV must also be in the snapshot: tracked, or untracked but not ignored, as a committed `docs/<batch>/trust-mutants.json` is.

   `--json` already comes back. Writing `--json` to the same path as `--rescore` is safe, since PREV is read before
   any build.

   Header comment line 7: `--test/--allow/--rescore paths must lie in the worktree`.

   A PREV written on the VM and rescored on the runner (or the other way) is reused only when lean/ holds the same
   files on both machines (`.lake` and `.cache` excepted). Otherwise the line says `its inputs differ (lean)`.

## 3. What was built (step 2)

**Inputs digest.** `inputs()` gives five sha256 digests, which every `--json` records as `inputs`:
- `tool`: the tool's own source and every module of this repository it has imported (`trust_map`,
  `lean_statements`, `audit`, `check_lean_imports`, `lake_outputs`, `lean_share`, ...).
- `lean`: every file of lean/ that `Scratch` copies, which is everything but `.lake` and `.cache`. That covers the
  sources, lakefile, lean-toolchain, lake-manifest and the compiled lists `plan` reads (`declarations.txt`,
  `statements.txt`), as well as any file an `include_str` could read. It also covers `tools/trust-classes.json`
  (trust_map's table) and `.gitignore` (which untracked files `changed_lines` sees).
- `tests`: the outside `--test` files.
- `base`: the resolved base commit, a commit id, which is immutable.
- `options`: `--deep` and the `--test` list, normalised (lean-relative inside lean/, root-relative outside).

Only file bytes are digested; uncommitted state is never compared by commit id. On this repository the digest
costs well under a second; `plan()` dominates a 13 s run with no mutants. Each mutant also records `raw_status`,
its status before `--allow`.

**`--rescore PREV.json`.**
- When PREV's `inputs` equal this run's and its mutant rows are this plan's (id, file, line, definition, operator,
  before, after), it reuses every KILLED, INVALID and SURVIVOR verdict, reading `raw_status` for an ALLOWED one.
- It reruns the UNKNOWN ones and the NOT RUN that now fit `--max-mutants`, then applies the current `--allow` to
  every mutant, reused or run.
- The control build, the probe install and the check hashes run only when a mutant runs, and only for the targets
  of the mutants that run.
- In the evidence, each reused mutant has `reused_from: <PREV head>`, and the JSON gains `rescore: {file, head,
  reused, rerun}`. The summary ends with `; N reused from <head> (identical inputs)`.
- Otherwise it does a full run and prints one line, `trust_mutants: --rescore PREV: a full run, since <why>`. The
  reasons are: no `inputs`, `its inputs differ (<parts>)`, its mutants not this tree's, or a file it cannot read.
  `rescore` then has `head: null`, `reused: 0` and `full_run: <why>`.
- The exit codes are unchanged. A mutant that runs keeps today's verdict rules (`run` is unchanged).

**One decision against the letter of the task: `--max-mutants` is not in the digest.** The task lists it among the
digested options, and also asks that a rescore run "the NOT RUN that now fit --max-mutants". Both cannot hold: with
the option in the digest, a different `--max-mutants` is a full run, and the NOT RUN of PREV never fit. The
limit picks which mutants run, never a verdict:
- `plan` never reads it.
- A mutant's build, control and check hashes come from its own targets.

So the digest leaves it out. A larger limit reuses the earlier mutants and runs only the new ones
(`test_rescore_runs_the_not_run_mutants_that_now_fit`). Mutants past the current limit are NOT RUN, as in a fresh
run with that limit. `--build-timeout` and `--jobs` are left out for the same reason: a timeout gives UNKNOWN, which
always reruns.

Real tree: `uv run python tools/trust_mutants.py --json a.json`, then the same with `--rescore a.json`, at this
branch. Both runs had 0 mutants, equal `inputs`, and `rescore {"reused": 0, "rerun": 0}`, in 13 s each.

## 4. Tests (step 3), on the tiny synthetic package

| Rule | Test |
|---|---|
| allow-only: 0 builds (a `lake` first on PATH that logs each call and fails is never called), SURVIVOR -> ALLOWED with `raw_status` SURVIVOR, every verdict `reused_from` PREV's head | `test_rescore_after_an_allow_only_edit_builds_nothing` |
| UNKNOWN reruns alone: rescored with `--build-timeout 0`, exactly PREV's UNKNOWN ids run (each past the limit, every KILLED kept); rescored again, only those run, and give PREV's verdicts back | `test_rescore_reruns_only_the_unknown_mutants` |
| one byte of a cone file, the lakefile, `statements.txt`, trust_map's table or an outside --test file, or another `--deep`, `--test` or base: PREV refused (`inputs differ`), the changed part named | `test_any_changed_input_gives_a_full_run[cone-file, lakefile, statements, trust-table, test-file, deep, test-option, base]` |
| one byte of the tool or a module it imports | `test_the_inputs_digest_the_tools_own_source` |
| an old JSON with no `inputs`, or an unreadable file: a full run, one line why, `reused` 0 | `test_rescore_of_an_old_or_unreadable_file_is_a_full_run[no-inputs, unreadable]` |
| evidence whose mutant rows differ, a status the tool never writes, a row with no `raw_status`: refused; an ALLOWED row is reused by its `raw_status` | `test_rescore_of_evidence_whose_mutants_differ_is_a_full_run` |
| a larger `--max-mutants` reuses the run ones and runs only M006, M007 | `test_rescore_runs_the_not_run_mutants_that_now_fit` |

`tests/test_trust_mutants.py`: 316 passed (whole file, VM, 8 min). The selected tests passed, except two
`test_history_tests.py` failures caused by a `git rev-parse` in the new test. That test now hashes a fixed base id;
`tools/history_tests.py --check` passes, and `test_history_tests.py` has 25 passed. `tools/gate_collection.py
--check --prebuilt`: 15 added, 0 removed, 0 refused, 0 stale, 0 malformed.

### Seeded bugs (Python: the only language changed)

`uv run python tools/mutants.py docs/speed/tmrescore/mutants.json` gives 10 of 10 killed
(`mutants-evidence.json`). The tool's sha256 was the same before and after (`f4a5301b...`, the final tool).

| Id | File | Bug | Failing test |
|---|---|---|---|
| RS1 | tools/trust_mutants.py | the control build runs when nothing runs | `test_rescore_after_an_allow_only_edit_builds_nothing` |
| RS2 | tools/trust_mutants.py | UNKNOWN reused | `test_rescore_reruns_only_the_unknown_mutants` |
| RS3 | tools/trust_mutants.py | an ALLOWED verdict reused as its status, not `raw_status` | `test_rescore_of_evidence_whose_mutants_differ_is_a_full_run` |
| RS4 | tools/trust_mutants.py | the lean digest reads `.lean` files only, without trust_map's table | `test_any_changed_input_gives_a_full_run[lakefile/statements/trust-table]` |
| RS5 | tools/trust_mutants.py | outside --test files not digested | `test_any_changed_input_gives_a_full_run[test-file]` |
| RS6 | tools/trust_mutants.py | `--deep` not digested | `test_any_changed_input_gives_a_full_run[deep]` |
| RS7 | tools/trust_mutants.py | the tool's source not digested | `test_the_inputs_digest_the_tools_own_source` |
| RS8 | tools/trust_mutants.py | evidence with no `inputs` not refused as such | `test_rescore_of_an_old_or_unreadable_file_is_a_full_run[no-inputs]` |
| RS9 | tools/trust_mutants.py | `reused_from` not written | `test_rescore_after_an_allow_only_edit_builds_nothing` |
| RS10 | tools/trust_mutants.py | a NOT RUN verdict reused | `test_rescore_runs_the_not_run_mutants_that_now_fit` |

## 5. Rules kept

- R2 (the merge train's full live gate) and R3 (the nightlies) are unchanged. No gate, train or nightly reads
  trust_mutants or its evidence (`git grep trust_mutants tools/gate.py` is empty).
- No Lean, `ve/` or `rust/` change; trust +0. DELTA.md has no rows.
- Size: the tool has +109/-18 lines and the tests +162/-3, which is over the task's ~250 by ~40. The tests are 8
  new functions, the end-to-end ones sharing two fixtures. `measure.py` (76) and the seeded-bug files are evidence.
- Sibling lesson (speed-trustmut F1, a proof failure counted as a kill): no verdict rule changed. Only a mutant's
  reuse is new, and a reused verdict is one the unchanged rules gave on byte-identical inputs.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; the tool reads its own evidence JSON (`previous` checks every field it reuses
   and refuses anything else: `test_rescore_of_evidence_whose_mutants_differ_is_a_full_run`).
2. PASS: steps 1-4 delivered (sections 1-4 above; commits on this branch). The one deviation (`--max-mutants`) is
   argued in section 3 and tested (`test_rescore_runs_the_not_run_mutants_that_now_fit`). No permanent report
   test (D4).
3. PASS: 10 of 10 seeded bugs killed (`docs/speed/tmrescore/mutants-evidence.json`). The R16 trust_mutants run is
   N.A. (no Lean change).
4. N.A.: no Python/Lean/Rust parity path changes.
5. N.A.: no relayed field. PREV's rows are bound to the plan by id, file, line, definition, operator, before and
   after (`test_rescore_of_evidence_whose_mutants_differ_is_a_full_run`).
6. PASS: main has not moved since the merge base (68f18dcdc); the chain runs the gate on the final HEAD. Section 1
   reads committed history only (`measure.py`).
7. PASS: DELTA.md has no rows and no reserved signature; trust +0.
8. PASS: no VE output changes (no `ve/`, `lean/`, `rust/` or `conformance/` file in `git diff main...HEAD`).
9. PASS: `tools/select_tests.py --base $(git merge-base HEAD main)` selects 25/460 units, `tests/test_trust_mutants.py`
   among them; RS1-RS10 fail there.
10. N.A.: no Lean statement or proof.
11. PASS: an UNKNOWN (timeout, budget) is never reused; it always reruns
    (`test_rescore_reruns_only_the_unknown_mutants`, RS2). The tests use no sleep and no fixed deadline: the
    expired limit is `--build-timeout 0`, as the existing timeout test does.
12. N.A.: no VE runtime path; the change removes rebuilds (section 1).
13. PASS: no test removed or renamed against main; `tools/gate_collection.py --check --prebuilt` reports 15 added,
    0 refused, 0 stale, 0 malformed.
