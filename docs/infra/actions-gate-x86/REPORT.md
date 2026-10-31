# actions-gate-x86: sharded x86 gate on Actions with the Lean build once

- **Status:** BUILT. The tool is installed inert: no flag is on and no caller uses it. The validation run and the switch are in the follow-up row `actions-gate-x86-switch` (blocked by this item), because shards can restore the build-once pack only after VE main carries `ve-job.yml` v3. No DRI signature is needed and there are no DELTA rows.
- **HEAD:** branch `infra/actions-gate-x86`, base `72920c53f`. VE files changed: `.github/workflows/ve-job.yml` and `tests/test_ci_workflow.py`.
- **What changed:** the VE workflow can give a gate shard the Lean build of its own dispatch's build job (`lean_from`). A build job's pack is checked but never uploaded (`lean_publish: false`). In manage-agents, `gha-arm-shard.sh --x86` gains the x86 gate-leg modes and the build-once step, and `gha/gate-job.sh` restores that pack and never rewrites pins on x86_64.
- **Open:** the validation run (gate-compare EQUAL against a full VM gate record of the same commit) and the train and chain-gate wiring. Both are in `actions-gate-x86-switch`.

## Row and note, item by item

Row `actions-gate-x86`: "Sharded x86 gate on Actions: build-once job + N gate.py --shard jobs + --merge-shards, for the train's x86 leg, the x86 nightly and chain gates (DRI ruling gha-gate-shard item 2)".

| Row or note item | Delivered by | Evidence |
|---|---|---|
| Dispatcher = gha-arm-gate.sh generalised (one job commit per shard, one push) | `gha-arm-shard.sh --x86`. The `--x86` flag itself came from nightly-x86-actions (below). This item adds the modes `leg-shadow`, `leg-blocking` and `leg-validate`. Shards still go in one push. | `test-x86leg.zsh` L1 "2 pushes: the build job alone, then the 2 shards" |
| N gate.py --shard jobs + --merge-shards | unchanged: the candidate's own `tools/gate.py --merge-shards`. A missing shard gives a FAILED record. | `test-armshard.zsh` D2, X2; `test-x86leg.zsh` L1 (real merge) |
| Lean build once per tree (artifact or shared-cache asset keyed by lean/ tree) | step 2b. If main's manifest has an exact Linux-x86_64 asset of `HEAD:lean`, no build runs. Otherwise one build job runs, and each shard's job.json names its run id and sha256. A shard downloads that run's artifact `lean-build` and nothing else. | `test-x86leg.zsh` L1, L2, L2b, L4 (six failure kinds), L9; `test-gatejob.zsh` G1-G4; VE tests `test_the_lean_from_check_*` and `test_job_json_*` |
| for the train's x86 leg and chain gates | modes `leg-*`: plain gate.py with no `authority`, flags `X86_SHARD_SHADOW` / `X86_SHARD_BLOCKING`, a full VM record as the reference, alert `x86-shard-alert.final.md` | `test-x86leg.zsh` L5, L6, L7 |
| for the x86 nightly | the nightly path is nightly-x86-actions' own (`validate` / `nightly`, authority, cold Lean). Here it gets an opt-in `--lean-once`, which never uses main's asset (the authority builds from source). | `test-x86leg.zsh` L9 |
| Validation: one run vs the VM gate of the same commit (gate-compare EQUAL), then switch | **not done here.** It needs v3 on VE main, and this builder does not push. Moved to `actions-gate-x86-switch` (budget 2 runs, stop rule, flag rows). | backlog row `actions-gate-x86-switch` |
| Ruling item 2: one merged record, missing shard = FAIL, R18, ACTIONS_MISMATCH/SUSPENDED -> VM, no new spend | unchanged merge and gates (exit 3 means not sent, and the caller falls back to the VM). No new runner type is used, so there is no new spend. A failed build job means the shards build cold: the run is slower and the verdict is the same. | `test-armshard.zsh` D2-D8, X2, X4; `test-x86leg.zsh` L4 |

## Design

- **Why the shards use a run artifact and not the release.** Per backlog `gha-wf2-gate-nopin`, gates may restore only main's assets, because a branch build is made by branch-controlled `uv sync` / `lake build`. The pack here is made by the gated commit's own build job, in the same dispatch, so it carries the same trust as each shard building it. The dispatcher binds it by two values:
  - the run id, from the **last** `run_url` line of the build result's `gha.txt`. The publish job appends that line after anything the job wrote.
  - the sha256, from the publish job's `lean-build-asset.json`, whose checks cover members, seal, size and the secret scan.

  The shards never read `lean-branch-cache`.
- **Workflow (VE, `.github/workflows/ve-job.yml`).**
  - The `run` job gains `actions: read`. Its token reaches one step only: `lean-from download` (`actions/download-artifact`, pinned, `run-id` from job.json, `continue-on-error`).
  - `lean-from check` hands over the pack only when it is one regular file named `lean-build-<HEAD:lean, 12>.tar.zst` with job.json's sha256. Anything else is written to `lean-from.txt` and the shard builds cold.
  - A malformed `lean_from` (wrong types, an extra key, an injection attempt) downloads nothing.
  - `lean_publish: false` gives asset status `checked` and no `gh` call.
- **gate-job.sh.** Before the restore, the pack's seal must name `HEAD:lean`. The restore is `ve-cache.sh restore --url file://… --sha256 …` with an empty manifest, so it never takes a seed from another tree. Only match `exact` counts; otherwise `lean/.lake/build` is removed. On x86_64 the pins are never rewritten, so the committed `lean/checkers.lock` is checked, as on the VM's x86 leg.
- **n.** On every x86 mode, n is at least 2: one shard of the whole gate would not fit the run job's 120 min.

## Coordination with nightly-x86-actions (concurrent writer of the same files)

The delegate `dri-nightly-x86-actions` was launched the same minute (16:59Z) and told to build the x86 dispatch from the same script. I messaged the orchestrator at 17:03Z (`inbox/orchestrator/20261031T170353Z-actions-gate-x86-390573.md`). That delegate installed `--x86` (nightly authority) at 17:06Z (`gate-job.sh`) and 17:15Z (`gha-arm-shard.sh`), before the message was read.

I dropped my first draft and layered my changes on their installed files:
- my mode names do not collide with theirs (their harness asserts that `--x86 shadow` is a usage error);
- before the `mv`, I compared the live file byte for byte with my saved base copy.

Their validation run (`gha-arm-shard.sh --x86 val1`) was running during the install. `mv` keeps the running instance's inode, and their harness passes against my files: `ARMSH_NEW=new-agx86 zsh test-harness/armshard/test-armshard.zsh` gave "38 ok, 0 FAIL".

manage-agents installs (17:33Z), backups `*.bak-20261030-actions-gate-x86`:
- `gha-arm-shard.sh` (+101 lines)
- `gha/gate-job.sh` (+40 lines)
- new `test-harness/x86gate/test-gatejob.zsh`
- new `test-harness/x86gate/test-x86leg.zsh`

## Tests run (commands and results)

- `uv run pytest -q tests/test_ci_workflow.py`: "88 passed". There were 66 before this item. New: the lean-from check (1 accept, 7 refuse), the job.json parse (accept, absent/null, 9 malformed), the job step hand-off, the `lean_publish` parse and the asset step, and 6 seeded structure rows (repository, artifact, may-fail, always, token removed, token moved).
- `zsh test-harness/x86gate/test-gatejob.zsh` on the installed file: "10 ok, 0 FAIL". On the pre-change file: "4 ok, 6 FAIL" (the 6 are the new behaviours).
- `zsh test-harness/x86gate/test-x86leg.zsh` on the installed file: "26 ok, 0 FAIL".
- `zsh test-harness/armshard/test-armshard.zsh` on the installed file: "38 ok, 0 FAIL" (arm D1-D12 and nightly X1-X6 unchanged).
- `uv run python tools/regen_generated.py --check`: rc 0, nothing stale.
- Selected tests: `zsh ~/code/manage-agents/mac-pytest.sh --select -- --base 72920c53f5de --run` selected 29 units (it names the changed files `.github/workflows/ve-job.yml` and `tests/test_ci_workflow.py`). Result: "recorded 29 units for tree 3b51d3b9f5; … 0 failed", and the summary line "ran LOCALLY (VM) because: no mac-pytest slot on ve-mac-1 within 600s …; exit=0; 3829s".
- Not run: any real Actions run (no push by this builder; validation is in the follow-up row) and the full gate (the chain runs it).

## Seeded bugs (each planted, its test failing, then restored)

| # | File | Bug | Test that fails |
|---|---|---|---|
| S1 | `.github/workflows/ve-job.yml` (lean-from check) | the sha256 is not compared | `tests/test_ci_workflow.py::test_the_lean_from_check_refuses_anything_else_and_the_shard_builds_cold[another sha256]` |
| S2 | `.github/workflows/ve-job.yml` (job commit) | `run_id` is not type-checked | `tests/test_ci_workflow.py::test_a_malformed_lean_from_is_said_and_downloads_nothing[int run]` |
| S2b | `.github/workflows/ve-job.yml` (job commit) | the `run_id` pattern is dropped | `…::test_a_malformed_lean_from_is_said_and_downloads_nothing[space]`, `[injection]` |
| S3 | `.github/workflows/ve-job.yml` (lean-build asset) | `lean_publish: false` still uploads | `tests/test_ci_workflow.py::test_a_pack_not_to_publish_is_checked_and_never_reaches_gh` |
| S4 | manage-agents `gha/gate-job.sh` | the seal's lean tree is not checked | `test-gatejob.zsh` G2 |
| S5 | manage-agents `gha/gate-job.sh` | pins are rewritten on x86_64 | `test-gatejob.zsh` G1 "x86_64: pins not rewritten" |
| S6 | manage-agents `gha-arm-shard.sh` | the first `run_url` line is taken (the job could write it) | `test-x86leg.zsh` L1 "each shard names lean_from run 4242", L2b, L9 |
| S7 | manage-agents `gha-arm-shard.sh` | an x86-essentials VM record is taken as the reference | `test-x86leg.zsh` L7 |
| S8 | manage-agents `gha-arm-shard.sh` | no n floor of 2 on x86 | `test-x86leg.zsh` L8 |

VE product code in Python, Lean or Rust: none changed. The VE change is the workflow (YAML with bash) and its test.

## DELTA and trust

No user-visible VE behaviour changes: the CLI, verdicts and diagnostics are untouched. No Lean changed and the trust budget does not grow. No DELTA rows.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer or relayed route is touched.
2. PASS: each row and note item is in the table above with its test. Validation and switch moved to `actions-gate-x86-switch` (filed, blocked by this item). There is no authority switch: no flag on, no caller. The files the in-flight nightly-x86-actions also edits are coordinated (section above).
3. PASS: seeded bugs S1-S8 above, each with its failing test. The comparator path (gate-compare against a VM record) is caught by L6 (DIFFERENT) and L7 (no reference).
4. N.A.: no Py/Lean/Rust decision path. Valid inputs still pass: `test_the_lean_from_check_hands_over_the_named_pack`, `test_job_json_names_the_build_run_and_its_sha256`, L1.
5. PASS (binding of job.json input): `test_a_malformed_lean_from_is_said_and_downloads_nothing` (extra key, wrong types, injection); L4 `othertree`/`norun` (a build result naming another tree or no run is refused).
6. PASS: the gate runs on the committed final HEAD (by the chain). Evidence lists none.
7. PASS: no DELTA rows, no reserved signature. "checked" status tested on error exits: `test_a_pack_not_to_publish_is_checked_and_never_reaches_gh` (refused pack stays refused).
8. N.A.: no user-visible change (CI workflow only).
9. PASS: the selected-tests run above selected `tests/test_ci_workflow.py` for the workflow change (29 units, 0 failed).
10. N.A.: no Lean.
11. PASS: the build job's deadline (`X86_LEAN_DEADLINE_MIN`), tested with 0 (L4 `skip`, L11). No sleeps in the VE tests; subprocesses use `HANG_TIMEOUT`.
12. N.A.: no checker code. The cost of the build-once step is one serial build job (≈ one cold lake build), in place of n parallel ones.
13. PASS: no test removed or renamed (SEEDED ids kept; new ids only).
14. PASS: both directions are tested for every new check (accept and refuse: lean-from check, job.json parse, `lean_publish`, seal, sha256, manifest hit or miss, flags on or off). Every claim above names its command.

Spec re-read:
- "build-once job + N gate.py --shard jobs + --merge-shards" against the backlog row title: steps 2b, 3 and 5.
- "one job commit per shard, one push" against the row note: the shards are one push. The build job is a separate push, because the shards need its run id.
- Ruling item 2 conditions against `reviews/dri-decisions-20261028-gha-gate-shard.md`: lines "one gate record built from all shards…", "R18…", "ACTIONS_MISMATCH / ACTIONS_SUSPENDED…", "within the Actions minutes already in use".
