# kb-regen-closure-check: evidence

Saved command outputs cited by REPORT.md (copied from /tmp/kbrc-*.log).

## Seeded bugs (find/replace, as run)

```json
{
 "item": "kb-regen-closure-check",
 "note": "Python only (no Lean or Rust product code changed). Each seed was applied in the worktree at d649f241a by exact find/replace, the listed tests were run with uv run pytest -q (log: the seed<n>.log sections below), and the file was restored with git checkout; git status was clean after each.",
 "mutants": [
  {
   "id": "S1",
   "bug": "the kernel-closure entry's check is the old totals-only one (no --fresh)",
   "file": "tools/regen_generated.py",
   "find": "\"--check\", \"docs/kernel/closure-baseline.json\",\n                \"--fresh\", \"docs/kernel/closure-baseline.json\"),),",
   "replace": "\"--check\", \"docs/kernel/closure-baseline.json\"),),",
   "rc": 1,
   "test": "tests/test_regen_generated.py::test_a_stale_closure_row_with_equal_totals_is_stale_and_the_r12_write_rewrites_it",
   "log": "evidence.md, section seed1.log"
  },
  {
   "id": "S2",
   "bug": "--fresh compares only the path names and the kernel total, not the bytes",
   "file": "tools/kernel_closure.py",
   "find": "    if saved_text == render(result):",
   "replace": "    if [r.get(\"name\") for r in json.loads(saved_text).get(\"paths\", [])] == [r[\"name\"] for r in result[\"paths\"]] and json.loads(saved_text).get(\"kernel_lines\") == result[\"kernel_lines\"]:",
   "rc": 1,
   "test": "tests/test_regen_generated.py::test_a_stale_closure_row_with_equal_totals_is_stale_and_the_r12_write_rewrites_it; tests/test_kernel_closure.py::test_fresh_fails_on_any_byte_the_write_would_change_and_check_alone_does_not",
   "log": "evidence.md, section seed2.log"
  },
  {
   "id": "S3",
   "bug": "--out writes another layout than the one --fresh compares with (two owners of the bytes)",
   "file": "tools/kernel_closure.py",
   "find": "        args.out.write_text(render(result))",
   "replace": "        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + \"\\n\")",
   "rc": 1,
   "test": "tests/test_regen_generated.py::test_a_stale_closure_row_with_equal_totals_is_stale_and_the_r12_write_rewrites_it; tests/test_kernel_closure.py::test_fresh_fails_on_any_byte_the_write_would_change_and_check_alone_does_not",
   "log": "evidence.md, section seed3.log"
  },
  {
   "id": "S4",
   "bug": "the section-6 limits (--check) are skipped when --fresh is given",
   "file": "tools/kernel_closure.py",
   "find": "    if args.check:\n        saved",
   "replace": "    if args.check and not args.fresh:\n        saved",
   "rc": 1,
   "test": "tests/test_regen_generated.py::test_a_stale_closure_row_with_equal_totals_is_stale_and_the_r12_write_rewrites_it; tests/test_regen_generated.py::test_an_up_to_date_closure_baseline_is_not_stale_and_a_limit_still_fails_it; tests/test_kernel_closure.py::test_fresh_fails_on_any_byte_the_write_would_change_and_check_alone_does_not",
   "log": "evidence.md, section seed4.log"
  }
 ]
}
```

## seed1.log (FAILED lines and summary)

```
26:        failed, unchecked = R.check([entry])
27:>       assert (failed, unchecked) == (["kernel-closure"], [])
58:FAILED tests/test_regen_generated.py::test_a_stale_closure_row_with_equal_totals_is_stale_and_the_r12_write_rewrites_it
59:1 failed, 1 passed, 62 deselected in 0.63s
```

## seed2.log (FAILED lines and summary)

```
26:        failed, unchecked = R.check([entry])
27:>       assert (failed, unchecked) == (["kernel-closure"], [])
98:FAILED tests/test_regen_generated.py::test_a_stale_closure_row_with_equal_totals_is_stale_and_the_r12_write_rewrites_it
99:FAILED tests/test_kernel_closure.py::test_fresh_fails_on_any_byte_the_write_would_change_and_check_alone_does_not
100:2 failed, 1 passed, 62 deselected in 0.97s
```

## seed3.log (FAILED lines and summary)

```
26:        failed, unchecked = R.check([entry])
27:        assert (failed, unchecked) == (["kernel-closure"], [])
30:        assert "PASS: kernel" in out and "PASS: verdict writers" in out  # the section-6 limits still ran, and passed
32:        # R12: the train writes the entries whose check failed, with each entry's own writer.
33:        assert R.write([e for e in (entry,) if e.name in failed]) == []
125:FAILED tests/test_regen_generated.py::test_a_stale_closure_row_with_equal_totals_is_stale_and_the_r12_write_rewrites_it
126:FAILED tests/test_kernel_closure.py::test_fresh_fails_on_any_byte_the_write_would_change_and_check_alone_does_not
127:2 failed, 1 passed, 62 deselected in 1.08s
```

## seed4.log (FAILED lines and summary)

```
26:        failed, unchecked = R.check([entry])
27:        assert (failed, unchecked) == (["kernel-closure"], [])
30:>       assert "PASS: kernel" in out and "PASS: verdict writers" in out  # the section-6 limits still ran, and passed
90:FAILED tests/test_regen_generated.py::test_a_stale_closure_row_with_equal_totals_is_stale_and_the_r12_write_rewrites_it
91:FAILED tests/test_regen_generated.py::test_an_up_to_date_closure_baseline_is_not_stale_and_a_limit_still_fails_it
92:FAILED tests/test_kernel_closure.py::test_fresh_fails_on_any_byte_the_write_would_change_and_check_alone_does_not
93:3 failed, 62 deselected in 0.99s
```

## Timing tails

```
== /tmp/kbrc-old.log (last 4 lines)
under the frozen keys' answers: 16244, of them in the kernel: 9966
definitions that write a verdict token: 59, of them outside the kernel: 56 in 28 modules
PASS: kernel 9966 <= 9966
PASS: verdict writers outside the kernel 56 <= 56
== /tmp/kbrc-new.log (last 4 lines)
definitions that write a verdict token: 59, of them outside the kernel: 56 in 28 modules
PASS: kernel 9966 <= 9966
PASS: verdict writers outside the kernel 56 <= 56
STALE: docs/kernel/closure-baseline.json is not what --out writes now (path rows discourse, document); regenerate it: uv run python tools/regen_generated.py --write --only kernel-closure
== /tmp/kbrc-regencheck.log (last 4 lines)
PASS: kernel 9966 <= 9966
PASS: verdict writers outside the kernel 56 <= 56
PASS: docs/kernel/closure-baseline.json is what --out writes now
regen_generated: checked 1 entries
== /tmp/kbrc-old2.log (last 4 lines)
under the frozen keys' answers: 16244, of them in the kernel: 9966
definitions that write a verdict token: 59, of them outside the kernel: 56 in 28 modules
PASS: kernel 9966 <= 9966
PASS: verdict writers outside the kernel 56 <= 56
== /tmp/kbrc-new2.log (last 4 lines)
definitions that write a verdict token: 59, of them outside the kernel: 56 in 28 modules
PASS: kernel 9966 <= 9966
PASS: verdict writers outside the kernel 56 <= 56
PASS: docs/kernel/closure-baseline.json is what --out writes now
```

## Plan, iterating runs, main's stale baseline, regeneration

```
== select plan (/tmp/kbrc-plan.log lines 1-2)
472/634 test units (map 828449f6c0, 6.51 s)
changed: docs/kernel/closure-baseline.json, docs/spec/kernel-boundary.md, tests/test_kernel_closure.py, tests/test_regen_generated.py, tools/kernel_closure.py, tools/regen_generated.py
== iterating runs
-- /tmp/kbrc-1.log
1 failed, 4 passed, 62 deselected in 2.67s
-- /tmp/kbrc-2.log
1 passed in 0.94s
-- /tmp/kbrc-3.log
2 passed in 0.44s
== main's baseline under --fresh (/tmp/kbrc-new.log)
STALE: docs/kernel/closure-baseline.json is not what --out writes now (path rows discourse, document); regenerate it: uv run python tools/regen_generated.py --write --only kernel-closure
== regeneration (/tmp/kbrc-write.log)
signed total 9966 >= kernel 9966
PASS: verdict writers outside the kernel 56 <= 56
regen_generated: wrote 1 entries
cmp docs/kernel/closure-baseline.json /tmp/kbrc-m/a.json: identical (rc 0) at 75735543
```
