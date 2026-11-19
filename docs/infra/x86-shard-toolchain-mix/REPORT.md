# x86-shard-toolchain-mix: one git on every shard of an x86 Actions leg

- Status: built and tested; VE change ready for review. Staged manage-agents file NOT installed: **INSTALL WAITS FOR DECIDER READ.**
- What changed: `.github/workflows/ve-job.yml` gets the run job's step `git`. It is the step of the installed
  `gha/ve-job-arm.yml` (row arm-shard-toolchain-mix) copied byte for byte. `tests/test_ci_workflow.py` covers it.
  `gha/ve-job.yml.new-x86pin` stages the same step for the fallback workflow.
- Open: the install read of the staged file, and the first x86 sharded leg after merge (its check is below).
- No DELTA rows: there is no Lean or trust-base change and no checker output changes. No DRI signature is reserved.

SIZE: 42 product (the workflow step and its comment; the staged gha copy repeats the same 41 lines plus one header line),
234 tests (176 in `tests/test_ci_workflow.py`, plus the 58-line manage-agents shell test), 1 other hand-written file (this
report). Counted with `git diff --numstat $(git merge-base HEAD main)..HEAD` and `wc -l`.

## Why

In `gha-arm/x86sh-nightly-a8b8c0fd-t539141` (11-13), shard s1 had git 2.56.1 and s2-s4 had 2.56.0. `tools/gate.py` records
`git --version` among its toolchains, and `tools/gate_shards.py` refuses a leg whose shards differ. Step 5b repaired that leg
because the split was 3/1. A 2/2 split has no majority and is refused. The x86 legs run the gated commit's own
`.github/workflows/ve-job.yml` (`gha-arm-shard.sh` line 232), or the staged `gha/ve-job.yml` when the commit has none. The
fix therefore goes in both files.

## Deliverables

| Deliverable | Where | Test |
|---|---|---|
| The git pin step, the same as the arm workflow's | `.github/workflows/ve-job.yml`, step `git` after `tools`, before `pinned sources` / `job`, no `if:` | `tests/test_ci_workflow.py::test_the_git_step_is_unconditional_between_tools_and_the_job`; manage-agents `test-harness/x86mix/test-gitpin-x86.zsh` ("it is the arm step, key for key and byte for byte") |
| Every shard of a mixed leg records the one pinned git, wherever gate.py's PATH (`/usr/bin:/bin`) looks | same step | `::test_every_shard_of_a_mixed_leg_records_the_one_pinned_git` (images 2.56.1, 2.56.0, 2.57.0) |
| A pin it cannot fetch, check or build keeps the runner's git, says `PIN FAILED`, raises a warning and exits 0 (the comparison is never loosened) | same step | `::test_a_pin_it_cannot_have_keeps_the_runner_git_and_says_so[other bytes, download fails, build fails]` |
| zlib headers are installed only when they are missing | same step | `::test_no_zlib_headers_installs_them_before_the_build` |
| The workflow's download rule takes the git source tarball only when it is kernel.org's `git-$GIT_PIN.tar.xz` and is checked by `sha256sum -c` against `GIT_SHA`, with both variables set once to literals | `tests/test_ci_workflow.py::check_downloads`, `literal` | `::test_ve_job_keeps_its_security_properties` (accept); `::test_each_rule_refuses_its_seeded_bug` rows `pin unchecked`, `pin check of another file`, `pin check warns only`, `pin sha set again`, `pin short sha`, `pin pin set again`, `pin over http`, `pin from another host` (refuse) |
| The staged fallback workflow with the same step | manage-agents `gha/ve-job.yml.new-x86pin` (not installed) | `test-harness/x86mix/test-gitpin-x86.zsh`: 14 ok / 0 FAIL on the staged pair; 2 ok / 12 FAIL on the installed pair (VE main and the live `gha/ve-job.yml`) |

## Seeded bugs

Each bug was planted in `.github/workflows/ve-job.yml`, the matching test failed, and the file was restored with `git checkout`.
The output is in `/tmp/x86mix-seed.log` (M1-M3) and `/tmp/x86mix-seed-m4b.log` (M4, rerun after the rows were renamed). The
command was `uv run pytest -q tests/test_ci_workflow.py` (M1-M3 with `-k 'git or security or every_workflow'`).

| # | Bug | Failing tests |
|---|---|---|
| M1 | the `/usr/bin/git` link removed (the pin is on `/usr/local/bin` only) | `test_every_shard_of_a_mixed_leg_records_the_one_pinned_git` |
| M2 | the runner's git is always taken as the pin (`if true`) | `test_every_shard_of_a_mixed_leg_records_the_one_pinned_git`, all 3 `test_a_pin_it_cannot_have_keeps_the_runner_git_and_says_so` cases |
| M3 | a failed pin fails the run (`exit 1` after the warning) | all 3 `test_a_pin_it_cannot_have_keeps_the_runner_git_and_says_so` cases |
| M4 | the sha256 check made advisory (`sha256sum -c - \|\| true`) | `test_ve_job_keeps_its_security_properties`, `test_every_workflow_keeps_the_trigger_and_secret_rules[.github/workflows/ve-job.yml]`, `test_a_new_workflow_file_keeps_the_common_rules`, `test_each_rule_refuses_its_seeded_bug[pin unchecked, pin check warns only, pin sha set again, pin short sha]` (7 failed, whole file; `/tmp/x86mix-seed-m4b.log`) |
| M5 | pin drift: `GIT_PIN=2.56.2` in a copy of the VE file and `GIT_SHA` changed in a copy of the staged file | `test-gitpin-x86.zsh`: "it is the arm step, key for key and byte for byte", "its GIT_PIN and GIT_SHA are the arm step's", "the arm harness passes on its git step" (8 ok / 6 FAIL) |

No Lean, Python product (`ve/`, `tools/`, `conformance/`) or Rust code changed. The product change is the workflow, which
is shell inside YAML.

## After merge (the decider's check)

The first x86 sharded leg after merge, `gha-arm/x86sh-*`, must have the same `toolchains.git` in every
`s*/gate-record.json`, and every `s*/gha.txt` must have a `git:` line:

```
for f in gha-arm/<that leg>/s*/gate-record.json; do python3 -I -c 'import json,sys; print(sys.argv[1], json.load(open(sys.argv[1]))["toolchains"]["git"])' $f; done
grep -h '^git:' gha-arm/<that leg>/s*/gha.txt
```

The pool was mixed on 11-13. The three most recent x86 legs (`x86sh-nightly-f2de63a4-t884901`,
`x86sh-nightly-f51d6831-t798946` and `x86sh-pinsrc2-da0822ae-da0822ae-t764559`) all recorded 2.56.1, so most shards now take
the no-cost path ("the runner's git is the pin").
