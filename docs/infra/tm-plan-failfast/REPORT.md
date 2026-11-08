# tm-plan-failfast: trust_mutants input refusals fail fast (build report)

Row tm-plan-failfast; DRI decision `reviews/dri-decisions-20261103-tm-plan-failfast.md` items 1-2 (both SIGNED there);
evidence `reviews/tm-plan-no-count-20261103.md`. All product changes are in `/home/seyran/code/manage-agents`, which is not
a git repository. Their diffs against the backups are saved in `live-changes.diff` (this folder). No file of this repo
outside this folder changed: no Lean, Python, Rust, generated file or DELTA row.

## What changed

1. `manage-agents/mac-pytest.sh` (installed by .new + `zsh -n` + backup `mac-pytest.sh.bak-20261103failfast` + `mv`;
   sha256 3e20a73c…). A `--trustmut` run first runs `uv run python tools/trust_mutants.py <args> --plan` in the worktree,
   with timeout 300 s (`timeout -k 10`). The run is skipped for a part run (`MAC_PYTEST_TM_PART` set), for `--merge`
   (which plans nothing; `--merge` with `--plan` is refused by the tool even when the merge itself would run), and when
   `TM_PLAN_FAILFAST.off` exists. The `--plan` args are the caller's without `--json`, `--jobs` or `--rescore`, in both
   the two-token and the `=` form, the same drop as tm-shard.sh. If `--plan` exits 2 with a message, mac-pytest prints
   "trust_mutants refuses its inputs, so every pool would too:" and the stderr (at most 40 lines, without uv `warning:`
   lines). It then logs `where=none rc 2` with the message and exits 2 before any pool is asked. The message is the first
   stderr line that is not `usage:`, indented, empty or a uv `warning:` line. If that line starts with `error:` it comes
   from uv itself (checked: `uv run --directory /nonexistent python -c 1` printed `error: No such file or directory
   (os error 2)` and exited 2), so the run is not refused: a uv failure on the VM says nothing about the Mac or Actions.
   Every other outcome routes exactly as before, after one "not a refusal" line on stderr. The check sits before the
   `MAC_PYTEST off` line, so no `run_local` path can reach a pool before it. That also places it before the cloud-reuse
   lookup, so a reuse hit now costs the plan's ~20 s first.
2. Builder text: one clause, with no backticks, `$` or double quotes, in three places. It says: rerun
   `uv run python tools/lean_statements.py` and commit lean/declarations.txt after Lean edits, before `--trustmut`; and
   give each `--test` path its own `--test` flag, Lean files only. The three places are `fixloop.sh` tests_fix item (4),
   `infra-item.sh` tests_rule item (2) (the build round's trust_mutants step) and `prompts/build-checklist.txt` 13a
   (where a build is told its trust_mutants command). Each was installed by .new + `zsh -n` + backup `.bak-20261103failfast`
   + `mv`, and the two eval'd strings were evaluated with dummy variables to check the clause comes out whole.
3. Harnesses. `test-harness/trustmut/test-trustmut.zsh` gains 18 cases (section 8) and a pool stub (`$S/M/cloud-overflow.sh`,
   logs `cloud ...`, exit 3), and its uv stub sends `--plan` calls to `plancalls` (outcomes set by scen/planrc, planerr,
   planhang, plancrash). The uv stubs of `cloudplumb/test-cloudplumb.zsh`, `cloudplumb/test-tmoptout.zsh` and
   `maclast/test-maclast.zsh` answer `--plan` with exit 0 and log nothing; without that, 4, 12 and 3 of their cases
   counted the new `--plan` call as a local run, though the routing was the same.

## Results (commands and outputs)

- Probe on this worktree, pools off (`MAC_PYTEST=0 MAC_PYTEST_NOFALLBACK=1 CLOUD_POOL=0 MAC_PYTEST_LOG=/tmp/...`):
  - `--test tools/trust_mutants.py`: printed `--test: not a Lean file: [PosixPath('…/tools/trust_mutants.py')]`, exit 2,
    real 0.57 s.
  - `--test lean/VE/Kernel.lean lean/VE/X.lean`: printed `trust_mutants.py: error: unrecognized arguments:
    lean/VE/X.lean`, exit 2.
  - A valid run: the plan passed in ~20 s (real 20.07 s), then `NOT running locally (MAC_PYTEST_NOFALLBACK): MAC_PYTEST
    off`, the path it took before.
  - The 3 log lines parse as JSON.
- Harness counts, before -> after (passed/failed):
  - trustmut (`zsh test-trustmut.zsh`), old harness on the old script: 14/3. New harness on the old script: 19/16. New
    harness on the new script (`OLD=…bak-20261103failfast`): 32/3.
  - The 3 failures predate this item and fail the same on the old script: "no --jobs: none added", "--rescore: sent
    worktree-relative…", "--rescore= form…". Their expectations are older than L144's `--jobs $cap`.
  - cloudplumb (`MPT=<script> zsh test-cloudplumb.zsh`): 174/8 -> 174/8, the same 8 pre-existing failures.
  - tmoptout: 21/0 -> 21/0. maclast: 29/0 -> 29/0. ghatests: 12/1 -> 12/1 (its "old script ignores the flag (control)"
    case fails on both).
- Harnesses that read the builder texts, run on the installed files:
  - nomain 15/0, overlap 40/0.
  - fixloop-dead 10/4, and the same 4 with `FXL=fixloop.sh.bak-20261103failfast` (pre-existing).
  - leanwire: D1/D2 fail on both the installed and the backup fixloop (pre-existing).
  - The l52, builderab, review-codex-default and feed failures are in cases about BUILDER-CHECKLIST.md, the run_builder
    hook, Codex routing and the feed. These are files and paths this item did not touch; none of the cases reads a
    trust_mutants or TESTS text.

## Seeded bugs (zsh; `seeded-bugs.json`)

Each seed was applied to a copy of the installed `manage-agents/mac-pytest.sh` and run through the trustmut harness. All
six were caught, and every copy was deleted.

| Seed | Caught by |
|---|---|
| A: any nonzero exit counts as a refusal | "plan crash (a signal): routing unchanged", "plan exit 1 (an exception): routing unchanged" |
| B: `--rescore` kept in the `--plan` args | "one --plan in the worktree, --json/--jobs/--rescore dropped…". The first run missed it because the case used only the `=` form; the two-token forms were then added to the case args |
| C: the part-run guard removed | "a part run (MAC_PYTEST_TM_PART): no local --plan" |
| D: the kill-switch path misspelt | "kill switch TM_PLAN_FAILFAST.off…", plus 8 routing cases |
| E: uv's `error:` counted as a refusal | "plan exit 2 from uv itself (error: line): routing unchanged" |
| F: no `exit 2` after the refusal | "plan exit 2 with a message -> rc 2, no pool called", plus the argparse case |

## Spec re-read

- Item 1 against `reviews/dri-decisions-20261103-tm-plan-failfast.md:5`:
  - The plan runs locally before any pool.
  - Exit 2 with a message: print, exit 2, no Actions, Mac or VM.
  - Exit 0, 124, a crash, or exit 2 with no message route as today.
  - Part runs skip the check.
  - Kill switch `TM_PLAN_FAILFAST.off`.
  - Harness cases for all of these, and the condition case stays in the trustmut harness. All met.
  - One reading: a uv `error:` line is treated as "no message from trust_mutants", so the run routes as today.
- Item 2 against the same file `:9`: the clause is in fixloop.sh and in the build-round texts, Lean files only, with no
  backticks. Met.
- The task prompt `prompts/task-tm-plan-failfast.txt`: no cap, pool order or other flag changed (`live-changes.diff`);
  no push; no DELTA row; no signatures.

## DRI rulings / DELTA

No VE user-visible delta; the routing change is signed by the DRI decision cited above. No DELTA.md row.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no Lean answer or relay touched).
2. Every deliverable built, no rule broken: PASS. Deliverables (1)-(3) are all built (`live-changes.diff`). Live files
   went through .new + `zsh -n` + backup + `mv`; no cap, pool order or flag changed.
3. Tests and gates can fail: PASS. Six seeded bugs, each caught (`seeded-bugs.json`).
4. Python/Lean/Rust agree: N.A. (shell routing only).
5. R8 binding: N.A. (no binding touched).
6. Gate evidence matches the final HEAD: PASS. The chain gates the final HEAD; this commit adds only docs/infra files.
7. No unsigned item: PASS. Both items are SIGNED in the DRI decision; nothing is reserved.
8. Every user-visible change in DELTA: N.A. (no VE user-visible change).
9. Test selection still finds the tests: N.A. (no repo test or product file changed).
10. Lean statements say what is claimed: N.A. (no Lean).
11. Budgets and deadlines fail closed: PASS. A `--plan` timeout (124) routes as today: test-trustmut.zsh "plan timeout
    (124): routing unchanged".
12. No CPU or memory regression: PASS. The added cost is one `--plan` per non-part `--trustmut` run, measured at
    real 20.07 s in the probe above, as the DRI accepted (~20 s).
13. Test-removed trailers: N.A. (no test removed or renamed).
14. Both directions, cited evidence, spec re-read: PASS.
    - Refuse side: test-trustmut.zsh "plan exit 2 with a message…" and the argparse case.
    - Accept side: "plan exit 0", "no message", "uv warning", "uv error:", timeout, crash, exit 1, part run, `--merge`,
      plain pytest, `--select`.
    - Claims above cite their commands; the spec re-read is above.
