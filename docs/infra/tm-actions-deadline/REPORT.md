# tm-actions-deadline: cloud-tm-job.sh passes trust_mutants exactly one --deadline, the earliest

- Status: INSTALLED in `/home/seyran/code/manage-agents` after the install read. The backup is `cloud-tm-job.sh.bak-20261117tad`
  (md5 `fd87fcd340ae03087a069339986910fb`). The live `cloud-tm-job.sh` (md5 `c292dcfc149a0590ed9bd3a2eeb91119`) is the staged
  `.new-tad`, and manage-agents' git recorded it, together with the new `tools-local/test_cloud_tm_deadline.py`
  (md5 `1729626f90e57f71cc5775a01802aa4e`), in snapshot `d7030438`. `installed-changes.diff` is the diff from the backup to the
  live file. The build report with the install commands is `manage-agents/tm-actions-deadline-build.final.md`.
- This VE branch holds only this report and its evidence. No VE product code (Lean, Python or Rust) changed. There are no
  DELTA rows and no DRI signature is reserved: this is control-plane tooling, not a trust-base change. Trust +0.
- Row: tm-actions-deadline (infra, SERVICE/PLACEMENT class). Decision: reviews/dri-decisions-20261117-tm-drain-vm1-idle.md
  item 2 (Part 0b); task file per reviews/dri-decisions-20261117-orch1156.md item 2.

SIZE: 17 product (cloud-tm-job.sh: 12 code, 5 header comment; 4 removed), 132 tests (test_cloud_tm_deadline.py, new),
~70 other hand-written lines (this report, seed_run.py).

## 1. The fix

The old loop turned `--budget S` into `--deadline T0+S` but also kept the caller's `--deadline T`. trust_mutants (argparse)
takes the last `--deadline` it is given, which was the caller's far one, so Actions parts ran into GitHub's 120-min cancel and
published nothing. The installed loop collects every `--deadline T` and `--budget S`, in both the `--x V` and `--x=V` forms, and
gives trust_mutants exactly one `--deadline`: the earliest of every caller T and T0+S. Other arguments keep their order.

- A lone `--budget` or a lone well-formed `--deadline` gives the same `--deadline` as before.
- A malformed bound refuses the job rather than being dropped: either a value that is not 1–12 digits (a decimal part is
  allowed) or a flag with no value. In that case `machine.txt` says why, `timings.tsv` gets the row `args 2 0`, DONE is 2,
  and trust_mutants does not run. The check runs before any build, which is the conservative reading.
- The script runs under bash in every launcher (`cloud-dispatch.sh`, `gha/ve-job.yml`, `gha-job.sh`), and `bash -n` passes.

## 2. Tests (failing first)

Run with `python3 -I tools-local/test_cloud_tm_deadline.py` in manage-agents (`CTJ=<file>` tests another copy). The test runs
the script's `run` mode with a stub uv that records trust_mutants' argv; `CLOUD_TM_START` pins T0.

| Case | Before install (`run-pre-install.log`) | Installed (`run-installed.log`) |
|---|---|---|
| 1 budget 600 + far deadline → T0+600 | FAIL | ok |
| 2 near deadline + large budget → near | FAIL | ok |
| 3 budget only | ok (unchanged) | ok |
| 4 deadline only | ok (unchanged) | ok |
| 5 two deadlines + budget → earliest, one flag | FAIL | ok |
| 6 `--budget abc` → refused, trust_mutants not called | FAIL | ok |
| 7 `=` forms, argument order kept | FAIL | ok |
| 8a/8b deadline with no value / bad value → refused | FAIL | ok |

## 3. Seeded bugs (shell, `cloud-tm-job.sh`)

All five were caught (`seeded-bugs.json`, `seeds.log`). `python3 -I seed_run.py` plants each one in a temporary copy of the
installed file and runs the test file on it:

- S1 picks the latest deadline instead of the earliest. Fails 1, 2, 5, 7.
- S2 passes every deadline instead of one. Fails 1, 2, 5, 7.
- S3 passes a malformed value through instead of refusing it. Fails 6, 8b.
- S4 counts the budget from `date` instead of T0. Fails 1, 2, 3, 5, 7.
- S5 ignores the `=` forms. Fails 7.

## 4. Dispatchers that build these arguments

- `tm-shard.sh:398-401` adds `--budget TM_PART_BUDGET` only when the caller passed neither flag, so it never sends both. It
  does not rely on the far deadline. The remaining gap belongs to row tm-shard-actions-120 and was not changed here: an Actions
  part whose caller passed only a far `--deadline` gets no part budget.
- `tm-nightly.sh:162` and `mac-pytest.sh` resumed parts send `--budget` and `--deadline` together and expect the earlier one to
  win, which the installed script now does. Neither relies on the far deadline.

## 5. Notes for the DRI

- In-flight jobs keep the copy they shipped with at dispatch. `tm-nightly-20261117T0600Z-p9-9ccbf3fd` (Actions) was dispatched
  with the old file, so its far deadline could still win.
- Behaviour changes:
  - A lone malformed `--deadline` now ends the job with DONE 2, where before trust_mutants exited 2 in `tm.rc`.
  - `--budget=S` now counts from the job start.
- This branch exists only to record the item. The pre-review [commits] check needs a commit, and the deliverables live in
  manage-agents.

## 6. Selected run

`mac-pytest.sh --select -- --base d2573fc9a0 --run` on 889aa83874 exited 0: 232 units, 0 failed, run on ve-cloud-2
(`selected-run.log`). This branch adds only docs, so the run covers main's tests on this tree.
No main-known-red test is involved.
