# vs-ref-notrun-not-compared: report

**INSTALL WAITS FOR DECIDER READ.** The fix is a set of staged `.new-vsnr` files in `/home/seyran/code/manage-agents`.
Nothing is installed. No DELTA row and no signature are needed: no product code in this repository changed, and no DRI
ruling covers this item. This directory is the item's record in the VE repository: the report, the staged diff and the
evidence.

## The item

Task: reviews/dri-decisions-20261117-vs-p9-deadline.md. Fixture: tm-nightly-20261116T1607Z-p9-9ccbf3fd. Its VM reference
ran past the job's own `--deadline` and judged 0 of 31 mutants. Its 31 NOT RUN rows against the cloud's 5 KILLED were
counted as a CLOUD VERDICT MISMATCH, which was false.

- **(a)** `cloud-verdict-compare.py`: a mutant that one side did not judge (NOT RUN, or an UNKNOWN that ran out of time)
  is not compared. When no shared mutant is judged on both sides, the result is `NOT COMPARED`, exit 3.
  `verdict-sample.sh` then writes a "not run" row and calls `vdone notrun`.
- **(b)** The reference run drops the job's `--deadline` and `--budget` and gets its own `--budget ${VS_REF_BUDGET:-21600}`.
- **(c)** A partial or failed reference is renamed aside, and `findref` never returns a partial.

`staged-changes.diff` holds every staged file against its installed copy, plus the new test file.

## Review round 1 (vs-ref-notrun-not-compared-review.final.md)

### F1 (B): `cloud-late.py` read the new exit 3 as "the key is not exact"

**Class.** A caller of `cloud-verdict-compare.py` that decides on the exit code alone. Exit 3 now carries two outcomes:
- INVALID REFERENCE: the inputs differ.
- NOT COMPARED: no shared mutant was judged on both sides.

Exit 1 is also not proof of a verdict difference: a comparator that dies with a traceback exits 1 too. Before the fix,
`cloud-late.py`'s `cmd_local_done` read NOT COMPARED as a non-exact key, deleted the entry, removed `CLOUD_LATE_APPLY` and
sent the wrong alarm. It also read a crash as VERDICTS DIFFER, which turned the pool off.

**Structural fix** (`cloud-late.py.new-vsnr`, diff in `review-f1.diff`):
- **One table.** `OUTCOMES` maps each verdict line the comparator prints to an outcome name and the exit code that must
  come with it.
- **One classifier.** `outcome(rc, out)` returns an outcome name only when exactly one verdict line is present and the
  exit code matches it. Anything else is `failed`, meaning the comparison was not made.
- **Both callers use it.** `cmd_store` and `cmd_local_done` branch on the outcome names. NOT COMPARED and `failed` are
  logged as "not made" and turn nothing off.
- **Unchanged guards.** INVALID REFERENCE still means a non-exact key (flag off), and VERDICTS DIFFER still means POOL OFF.
- **Summary.** It is built from the same table's prefixes, with the verdict line first, so the 240-character cut cannot
  drop it. That also settles note F5.

The other callers that act on exit 3 already decide on the `^NOT COMPARED` line: `verdict-sample.sh` (`cmpv`, and its
ve-cloud-2 path, which acts only on exit 1) and `cloud-late.py` `cmd_store`. `actions-health.py` does not run the
comparator.

**PROBE F1** (`probe-f1.log`):
- **Before the fix, verbatim:** fails with `CLOUD_LATE_APPLY turned off`.
- **After the fix, verbatim:** cannot run. The probe loads the staged file with
  `importlib.util.spec_from_file_location`, which returns None for a `.new-vsnr` suffix (`AttributeError: 'NoneType'
  object has no attribute 'loader'`).
- **The fair rerun:** the same probe with only `loader=SourceFileLoader(...)` added. It fails with the staged
  `cloud-late.py.new-vsnr` hidden and passes with it in place. Once installed, the file's suffix is `.py` and the
  verbatim probe loads it.

**Regression tests** (`manage-agents/tools-local/test_vs_ref_notrun.py`, class `CloudLate`; `cloud-late.py` joins the
staged set the file copies):
- `test_local_done_not_compared_is_not_made`: the probe as a test.
- `test_local_done_input_difference_still_turns_the_flag_off`: INVALID REFERENCE keeps its meaning.
- `test_local_done_judged_difference_still_turns_pool_and_flag_off`: VERDICTS DIFFER keeps its meaning.
- `test_local_done_equal`
- `test_a_crashing_comparator_is_not_a_mismatch`: exit 1 with no verdict line is "not made", not POOL OFF.
- `test_summary_names_the_verdict_line_first`: note F5.
- `test_outcome_line_and_exit_code_fuzz`: every verdict line with every exit code from -1 to 6, two verdict lines, no
  verdict line, and a traceback.
- `test_every_comparator_verdict_line_is_in_the_outcome_table`: two-way. Every upper-case line the comparator prints is
  either in `OUTCOMES` or one of its three info lines, and every `OUTCOMES` prefix is a line it prints. A new verdict line
  in the comparator therefore fails this test until `cloud-late.py` classifies it.

**Results:**

| Run | Result | Log |
|---|---|---|
| `VSNR_SFX=.new-vsnr python3 -I tools-local/test_vs_ref_notrun.py` | 20/20 pass | `run-staged.log` |
| The same tests on the installed files | 15 failures, 2 errors | `run-installed.log` |
| `tools-local/test_cloud_late_apply.py`, `CLOUD_LATE_PY=cloud-late.py.new-vsnr` | 23 passed, 5 failed | `cloud-late-apply.log` |
| `tools-local/test_cloud_late_apply.py` on the installed `cloud-late.py` | the same 5 failed | `cloud-late-apply.log` |

On the installed files, 7 of the 8 `CloudLate` tests fail. `test_local_done_equal` passes there, as it should. The 5
`MacPytest` failures in `test_cloud_late_apply.py` are the same on both files. They are pre-existing: `mac-pytest.sh`
runs `--plan` on a fixture worktree that has no `tools/trust_mutants.py`. They do not touch `cloud-late.py`.

**Seeded bugs** (`seeded-bugs.json`): 5 bugs planted in `cloud-late.py.new-vsnr`. Each one failed at least one
`CloudLate` test, and each was restored byte-for-byte.

### Install (backup and mv; no service restart; review round 1 adds `cloud-late.py`)

```
cd /home/seyran/code/manage-agents
for f in actions-health.py cloud-verdict-compare.py verdict-sample.sh cloud-late.py test-harness/cloudplumb/test-advfix4.zsh; do
  cp -p $f $f.bak-20261117-vsnr && mv $f.new-vsnr $f
done
```

`cloud-late.py` runs as a fresh `python3 -I` for each call (from cloud-pull.sh and mac-pytest.sh), so nothing needs a
restart. Install `cloud-late.py` together with `cloud-verdict-compare.py`. Without it, the staged comparator's
NOT COMPARED exit would turn `CLOUD_LATE_APPLY` off (F1).

### F-ready1 (B): 0 commits ahead of the merge base

This directory is the item's commit: the report, the staged diff and the evidence.

### Notes (C, not filed)

- **F5** is fixed with F1 (the verdict line comes first in the summary).
- **F2, F3, F4 and F6** are left as the review recorded them.

## Testing in this repository

There is no product change here. The selected run, `lake build` and `lean/audit.py` ran once, on 8c6ed86508 (the
evidence commit; this report commit adds only their record). All three passed, and `selected-run.log` records them:
- **Selected run:** exit 0 on GitHub Actions, 2 shards, 10 of 10 units passed.
- **`lake build`:** 1478 jobs.
- **`lean/audit.py`:** PASS on 898 source files.
