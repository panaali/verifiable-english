# fix-fsmonitor-gate: build report

**DRI signature needed (first line, BUILDER-CHECKLIST 7):** the fix closes the hole the Mac runner relies on. The runner's
`mac-gate-job.sh` (and `mac-run-full.sh`) rewrites `lean/checkers.lock` with its aarch64 pins and hides it with
`git update-index --assume-unchanged`. With this branch, `tools/gate.py` sees that edit, so **every Mac gate would fail
"worktree is dirty at gate start"**, including this branch's own Mac candidate leg (it is a native change: it touches
`tools/gate.py`). The runner-side fix (review F1) is ready and tested, but it is not live: the wrapper
`manage-agents/mac-gate-wrap.fix-fsmonitor-gate.py` and its test `manage-agents/mac-gate-wrap-test.py` (see "Mac runner").
The DRI lands it by moving the candidate over `mac-gate-wrap.py`. Those scripts live outside this branch, and other
jobs use them now.

Item: infra item fix-fsmonitor-gate (acting DRI 2026-10-15 12:40Z; FAST LANE). Branch `fix/fsmonitor-gate`, synced with
`main` at 1cbd5ed1e. Changes are in Python only: `tools/gate.py`, plus tests and a benchmark.

## The fix

`tools/gate.py` `source_identity` (runs at the gate's start and at its end):

1. `git rev-parse HEAD` (stage `commit`), as before.
2. `git status --porcelain --untracked-files=all` on the repository's index (stage `worktree status`), as before. Any
   output means dirty, and the check stops here. A staged change still counts as dirty, even when the file on disk is back
   to the commit's content, so the gate refuses every tree it refused before.
3. Only for a tree that step 2 calls clean: `GIT_INDEX_FILE=<gate scratch>/source-index git read-tree <the commit from step 1>`
   (stage `worktree index`), then the same status on that index (stage `worktree content`). A fresh index holds no stat
   data, so git compares the content of every tracked file. No fsmonitor answer, rewritten racy entry, `assume-unchanged`
   bit or `skip-worktree` bit can hide an edit. The index is read from the commit step 1 recorded, not from `HEAD` again.
   It is removed afterwards. The repository's own index is never written (`--no-optional-locks`; tested).

`GIT_INDEX_FILE` is listed in `STAGE_ENVIRONMENT["source identity"]`. `test_poisoned_ambient_environment_leaves_gate_result_unchanged`
checks that every command's environment is listed. The test that showed the gap,
`tests/test_gate_integrity.py::test_fsmonitor_hook_cannot_hide_edited_source`, is unchanged.

A first version used only the fresh index. That would have widened what the gate accepts: a tree whose index differs from
the commit while its files match it (a staged edit reverted on disk) would have counted as clean. Widening is never covered
by a standing ruling, so step 2 stays. `test_staged_change_stays_dirty_when_the_file_matches_the_commit` covers it (seeded
bug P6).

## Reproduction: 400 runs of the test's steps, 32 processes in parallel (VM, load about 50 on 32 CPUs)

| Code | Missed edits (`source_identity` said clean) |
|---|---|
| main's `tools/gate.py` (`git archive main tools`) | **31 of 400**, then **6 of 400** |
| this branch, fresh index only (first version, e3dd03c81) | 0 of 400, 0 of 400 |
| this branch, final code | **0 of 400**, **0 of 400** |

The earlier diagnosis (`verifyfix-fix-abbrev.final.md`) saw 17 and 20 of 400 on main. The script follows. Each run is its
own process, so `gate.ROOT` is per run. Run it as `python3 -I repro.py <checkout> 400 32 <runs dir>`:

```python
import contextlib, io, shutil, subprocess, sys, tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, sys.argv[1])
import tools.gate as gate

RUNS = Path(sys.argv[4])


def one(i):
    tmp = Path(tempfile.mkdtemp(prefix="fsm-", dir=RUNS))
    try:
        repo = tmp / "repo"
        repo.mkdir()
        env = gate.gate_environment(tmp / "scratch")
        identity = ["-c", "user.name=gate", "-c", "user.email=gate@example.invalid"]
        for args in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "init"]):
            subprocess.run(["git", *identity, *args], cwd=repo, env=env, check=True)
        (repo / "source.py").write_text("one\n")
        subprocess.run(["git", "add", "source.py"], cwd=repo, env=env, check=True)
        subprocess.run(["git", *identity, "commit", "-q", "-m", "source"], cwd=repo, env=env, check=True)
        hook = tmp / "fsmonitor"
        hook.write_text("#!/bin/sh\nprintf 'token\\0'\n")
        hook.chmod(0o755)
        subprocess.run(["git", "config", "core.fsmonitor", str(hook)], cwd=repo, env=env, check=True)
        subprocess.run(["git", "status", "--porcelain"], cwd=repo, env=env, check=True)
        (repo / "source.py").write_text("two\n")
        plain = subprocess.run(["git", "status", "--porcelain"], cwd=repo, env=env,
                               capture_output=True, text=True, check=True)
        assert plain.stdout == ""
        gate.ROOT = repo
        with contextlib.redirect_stdout(io.StringIO()):
            return gate.source_identity(env)[1]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    n, p = int(sys.argv[2]), int(sys.argv[3])
    with ProcessPoolExecutor(p) as pool:
        results = list(pool.map(one, range(n)))
    print(f"missed {results.count(False)} of {n} ({p} in parallel); detected {results.count(True)}")
```

## Added cost (one read of the tracked tree: 5,331 files, 400 MB)

Five calls each. Seconds per call, sorted. The gate calls the check twice: at its start and at its end.

| Machine | Fresh-index check, wall | Fresh-index check, CPU | Repository-index status alone (before), wall |
|---|---|---|---|
| VM (x86_64, 32 CPUs, load 48.5) | 1.39, 1.42, 1.52, 1.56, 1.85 | 1.42, 1.44, 1.55, 1.60, 1.86 | 0.02 to 0.03 |
| VM (load 57.8) | 2.79, 2.79, 3.07, 3.08, 3.11 | 1.98 to 2.13 | 0.07 to 0.31 |
| Mac ve-mac-1 (aarch64, 18 CPUs, load 28.0) | 0.72, 0.75, 0.77, 0.78, 0.80 | 0.70 to 0.72 | 0.01 |

That is about 3 to 6 s per gate on the VM and 1.5 s on the Mac, against a full gate of 2 to 4 hours. The new benchmark
`tools/bench/test_perf.py::test_gate_source_identity` records it in CPU seconds: a VM baseline of 2.502 for `fresh index`
and 0.063 for `repository index`. A later VM bench run measured 1.862 and 0.04. The benchmark refuses a dirty checkout,
which would stop at the first status.

On the Mac, the read-tree and status commands were timed directly, through a temporary pytest file run with
`mac-pytest.sh` and then deleted. The runner's checkout is never clean (see the next section), so `source_identity` there
stops at step 2.

## Mac runner (needs the DRI)

Probe output on ve-mac-1 (mac-pytest job checkout, 2026-10-15 13:38Z):

```
repository-index status: 'A  docs/fix-fsmonitor-gate/mutants.json\nA  tests/test_zz_tmp_fsm_cost.py\n'
fresh-index status:      ' M lean/checkers.lock\n?? docs/fix-fsmonitor-gate/mutants.json\n?? tests/test_zz_tmp_fsm_cost.py\n'
```

The repository-index status never shows `lean/checkers.lock` because of the `assume-unchanged` bit. The fresh index does.
In a gate job checkout everything else is clean, so `tools/gate.py` would stop with "worktree is dirty at gate start".

The design first proposed here does not work, and the review (F1) did not catch that. It added the pin file's blob to
the fresh index (`git update-index --cacheinfo`) after the read-tree. Status then reports the file as staged against
`HEAD`, so the gate still stops. Scratch repository, 2026-10-15 (also the runner test `test_cacheinfo_of_the_pins_is_not_enough`):

```
repository status (assume-unchanged): []
fresh index:                          [ M lean/checkers.lock]
fresh index + cacheinfo of the pins:  [M  lean/checkers.lock]
```

Runner-side fix (review F1), ready and tested but not live: `manage-agents/mac-gate-wrap.fix-fsmonitor-gate.py`. To land
it, the DRI signs DELTA row 2 and moves the file over `manage-agents/mac-gate-wrap.py`, which `mac-gate.sh` copies to the
runner for each gate. Nothing in this branch changes for it.

- The wrapper imports `tools.gate` as a module in every mode. The nightlies already do (`VE_GATE_RUN_CACHE_OFF=1`, on the
  Mac and the VM). If the import fails, it runs the gate by runpy as before.
- The hook is installed only when the job checkout marks `lean/checkers.lock` assume-unchanged (`git ls-files -v` tag
  `h`), as `mac-gate-job.sh` does after writing the pins. It is not installed with `VE_GATE_NO_RUNNER_PINS=1` (the VM
  nightlies). The wrapper hashes the file once, at its start.
- The hook wraps `gate.command` for the stage `worktree content` only (the fresh-index status). It drops exactly the line
  ` M lean/checkers.lock`, and only while the file still hashes to the blob taken at the start. Any other line still
  makes the tree dirty: an edit hidden by an index bit, an untracked file, a staged change or a deletion. So does any
  later change to the pin file, even back to the commit's content. The gate checks at its start and at its end.
- A gate.py without that stage never calls the hook. A hook that drifts from gate.py fails closed: the gate stops
  "worktree is dirty at gate start", and `mac-gate.sh` falls back to the VM gate (exit 3).
- The stage names and the fresh index the hook relies on are pinned in this branch by
  `tests/test_gate_integrity.py::test_clean_status_is_checked_again_on_a_fresh_index_of_the_commit`.

Runner test: `manage-agents/mac-gate-wrap-test.py`, run from this worktree. It tests the wrapper's hook against this
worktree's own `tools.gate.source_identity`, on a small repository shaped like a Mac gate job checkout:

```
cd <VE worktree> && GATE_WRAP=$M/mac-gate-wrap.fix-fsmonitor-gate.py \
  uv run pytest -q -p no:cacheprovider -p no:randomly --rootdir=$M $M/mac-gate-wrap-test.py
```

Results on the VM, 2026-10-15:

- Before, against the live `mac-gate-wrap.py`: 9 failed, 2 passed. The two that pass show the defect itself:
  `test_runner_pins_alone_make_the_gate_refuse_without_the_hook` and `test_cacheinfo_of_the_pins_is_not_enough`.
- After, against the candidate: 11 passed.
- `uv run python <candidate> --help` in this worktree prints gate.py's usage and exits 0 (import mode and argv).

Seeded bugs in the candidate hook (Python). Each was planted alone in a scratch copy, which was then deleted:

| Id | Behaviour | Mutation | Failing tests |
|---|---|---|---|
| W1 | a pin file changed after the start is dirty | hash check disabled | `test_hook_refuses_a_pin_file_changed_after_the_wrapper_started` (both) |
| W2 | only the pin line is dropped | every line dropped | `test_hook_still_refuses_any_other_change[hidden edit]`, `[deleted]` |
| W3 | gate.command strips its output, so a first line ` M` arrives as `M` | raw ` M <pin>` match | `test_hook_accepts_exactly_the_runner_pins`, `test_hook_passes_other_stages_through`, two more |
| W4 | no hook unless the checkout hides the pins | bit check disabled | `test_hook_is_not_installed_when_the_checkout_does_not_hide_the_pins` |

The untracked and staged cases are refused before the hook runs, by the repository-index status, so W2 cannot reach them.

The alternatives are worse. Committing the pins changes the gated commit. Not writing them fails the pin check. A git
clean filter for the pin file would hide content from status, which is the kind of hiding this branch closes.

Same class, every runner flow that runs `tools/gate.py` or uses `assume-unchanged` (grep of `manage-agents/*.sh`):

- `mac-gate-job.sh` `work` runs the gate after `assume-unchanged`. It is fixed by the candidate wrapper.
- `mac-gate-job.sh` `vwork`, `mac-run-full.sh` and `mac-pytest-job.sh` use `assume-unchanged` but run pytest only. They
  are not affected, as the review found.
- `chain-gate.sh`, `merge-train.sh` (x86 leg), `nightly-verify.sh` and `nightly-vm-verify.sh` run the gate on the VM.
  None of them uses `assume-unchanged`, `skip-worktree` or an fsmonitor hook.

Until the candidate is live, this branch's merge-train Mac leg will fail, and so would every Mac gate after the merge.

## Tests

- VM: `tests/test_gate_integrity.py`, 43 passed (synced tree).
- Mac: `mac-pytest.sh -- tests/test_gate_integrity.py`, all passed (plus the cost probe).
- Mac: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, 101 units, 0 failed, exit 0 (835 s; HEAD
  d44261e9 plus this report's files).
- VM: `tools/select_tests.py --base $(git merge-base HEAD main) --run --jobs 6` on HEAD 8d0024015 selected 118 units.
  112 finished, all exit 0, including `tests/test_gate_integrity.py`, `tests/test_gate.py` and
  `tests/test_bench_baselines.py`. My 3,500 s limit then stopped the run: the VM load was 50 to 68 on 32 CPUs. The 6
  unfinished units are covered by the Mac run above, and the chain reruns the selection on the final HEAD.
- VM: `uv run python tools/regen_generated.py --check`, 25 entries fresh. `lake build`, 931 jobs, OK.
  `tools/gate_collection.py --check --prebuilt`: 5 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- Not run: the full gate (FAST LANE: the chain and the merge train run it). `lean/audit.py` was not run because no Lean
  file changed.
- `main-known-red.txt`: none of its three tests is in this change's scope, and none was touched.

New tests, in `tests/test_gate_integrity.py`:

- `test_index_bits_cannot_hide_edited_source[--assume-unchanged]` and `[--skip-worktree]`.
- `test_source_identity_reports_clean_tree_and_leaves_index_alone`: (sha, False) on a clean tree and (sha, True) with an
  untracked file; the repository index's bytes and mtime are unchanged; no scratch index is left.
- `test_staged_change_stays_dirty_when_the_file_matches_the_commit`: no widening.
- `test_clean_status_is_checked_again_on_a_fresh_index_of_the_commit`: the stage order, `read-tree <recorded commit>`, the
  same status arguments, and the scratch `GIT_INDEX_FILE` on both fresh-index commands but not on the first status.

`test_gate_rejects_untracked_source_before_build` is unchanged: a dirty first status still stops after `worktree status`.

## Seeded bugs (Python, `tools/gate.py`; `docs/fix-fsmonitor-gate/mutants.json`)

Each was planted alone, its test run, then the file restored. All six were killed by an assertion failure (pytest exit 1).

| Id | Behaviour | Mutation | Failing test |
|---|---|---|---|
| P1 | the content status runs on the fresh index | `env=fresh` changed to `env=env` for `worktree content` | `test_index_bits_cannot_hide_edited_source` (both) |
| P2 | the fresh index is read from the recorded commit | `read-tree sha` changed to `read-tree HEAD` | `test_clean_status_is_checked_again_on_a_fresh_index_of_the_commit` |
| P3 | the fresh index is removed afterwards | `finally: pass` | `test_source_identity_reports_clean_tree_and_leaves_index_alone` |
| P4 | the repository's index is never written | `GIT_INDEX_FILE` set to `ROOT/.git/index` | `test_source_identity_reports_clean_tree_and_leaves_index_alone` |
| P5 | `GIT_INDEX_FILE` is a listed variable | its `STAGE_ENVIRONMENT` entry dropped | `test_poisoned_ambient_environment_leaves_gate_result_unchanged` |
| P6 | a repository-index change stays dirty | first status removed | `test_staged_change_stays_dirty_when_the_file_matches_the_commit` |

The reproduction is also a seeded check: main's code (that is, without the fresh index) misses 31 and 6 of 400.

## Build checklist (`prompts/build-checklist.txt`)

Lines 1 to 3, 5 and 8 to 12 do not apply: the change touches no diagnostics, parser, relay, verdict, English or ledger.
Line 17 to 19 and 21 do not apply either: no spec, theorem or use case is involved.

- 4: no relayed answer. The git output read is a byte string; any byte means dirty.
- 6: N.A., no verdicts. The check fails closed: a command failure raises and the gate fails.
- 7: N.A., no deadline.
- 13: seeded bugs P1 to P6.
- 14: the tests write only under `tmp_path` and use no sleeps or timeouts. The benchmark is in `tools/bench`, not the suite.
- 15: the read-tree is bound to the commit the gate records (P2).
- 16: `STAGE_ENVIRONMENT` is covered by the poisoned-environment test (P5).
- 20: every number here comes from the commands and logs named.
- 22: selected tests run; the full gate is left to the chain (FAST LANE).
- 23: see DELTA.md.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean or Rust answer is read. The gate reads git's porcelain output, and any output means dirty.
2. PASS: directive lines, each with its evidence:
   - fresh index in source_identity: commits e3dd03c81 and 1e5f7dd97, `test_clean_status_is_checked_again_on_a_fresh_index_of_the_commit`;
   - the repository index is never written: `test_source_identity_reports_clean_tree_and_leaves_index_alone`;
   - the test is kept as is: `git diff main...HEAD` removes no line of `test_fsmonitor_hook_cannot_hide_edited_source`;
   - cost measured on the VM and Mac: "Added cost" above and `tools/bench/test_perf.py::test_gate_source_identity`;
   - reproduction before and after: the table above.
   A grep of the diff finds no new Python copy of a Lean decision and no permanent report test.
3. PASS: seeded bugs P1 to P6 (`docs/fix-fsmonitor-gate/mutants.json`). All six are assertion failures, none a build or
   hash step.
4. PASS: valid inputs still pass. A clean tree is clean (`test_source_identity_reports_clean_tree_and_leaves_index_alone`),
   all 43 gate-integrity tests pass, and the Mac selected run is green. A clean Mac runner checkout is dirty by design.
   The runner fix that accepts exactly its pins is in "Mac runner" (review F1).
5. N.A.: no relayed field.
6. PASS: synced with main at 1cbd5ed1e. Selected tests ran on the Mac. The full gate is left to the chain and merge train
   (FAST LANE).
7. PASS: every DELTA row is signed by the item directive, or marked "DRI signature needed" (the Mac runner; also the first
   line of this report).
8. PASS: DELTA.md lists the dirty-check tightening, the Mac consequence, the two new log lines and the cost. The gate
   record's fields are unchanged (`test_poisoned_ambient_environment_leaves_gate_result_unchanged`).
9. PASS: `tools/select_tests.py --base $(git merge-base HEAD main)` selects 100 of 384 units, including
   `tests/test_gate_integrity.py`, the test that catches P1 to P6.
10. N.A.: no Lean statement.
11. N.A.: no budget. The check fails closed on a git error, as before.
12. PASS: CPU measured and recorded, about 2.5 CPU s per call on the VM and 0.7 on the Mac. The benchmark
    `tools/bench/test_perf.py::test_gate_source_identity` has its baseline stored.
13. PASS: no test removed or renamed. `tools/gate_collection.py --check --prebuilt` reports 0 refused, 0 stale and
    0 malformed.
