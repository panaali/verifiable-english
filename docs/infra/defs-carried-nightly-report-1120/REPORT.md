# defs-carried-nightly-report-1120: REPORT

INSTALL WAITS FOR DECIDER READ. No VE product change: the deliverable is a control-plane step (the nightly runner's
`defscarried` report). This file is the only VE change, the item's report, so the branch has a commit to review.
Nothing is reserved for the DRI; no DELTA row (no user-visible VE change).

## The step (control plane, `/home/seyran/code/manage-agents`)
- Staged runner: `nightly-verify.sh.new-defscarried` (md5 bebcfe42bd364114d25260de53d96f13, `zsh -n` OK). Installed
  copy (first version, md5 b3650023...) is untouched; the running loop still runs the pre-step code (started 2026-11-19).
- Once per nightly, after the gate record, alert, hold and coverage-map refresh, in a subshell whose status is ignored:
  build the known-case fixture from the live inventories (`tools/defs_carried_known.py --audit
  $M/reviews/defs-carried-1119 --repo $N` into a temp dir), then run `tools/defs_carried.py --root $N --doc <doc>
  --known <fixture> --json <tmp>` once per inventory, and write `$M/nightly-runs/defs-carried-<UTC stamp>.md` + `.json`:
  per document `carried <n> cases, not carried <n> cases (<n> cases of <n> inventory rows)`.
- A case carried in the latest earlier record and not carried now: one `DROPPED` line and one message
  `msg.sh orchestrator defs-carried-report "<doc>: <n> carried definitions dropped: <ids>"` (the hourly digest).
- Any failure (no inventory, tool, builder or venv; a fixture build, tool crash, timeout or unreadable report): one
  `defs-carried: not run: <why>` line. The nightly's exit code and outputs never change.
- Notes, evidence and install commands: `reviews/defs-carried-nightly-report-1120/NOTES.md` (control plane).

## Review findings (review of f20025e7, verdict FIX)
- **F1 (B), fixed.** The step used the committed fixture, which holds only the first audit's 11 rows files, so
  openai-preparedness (50 rows), anthropic-rsp-x (63) and safety-framework-x (46) were not checked. Now the fixture is
  built each night from the live inventories and passed with `--known`; the unit is named (a case = one (rule, term)
  pair of an inventory row; rows counted too). Regression tests: `test_a_fixture_built_from_live_inventories` (the
  builder gets `--audit $M/reviews/defs-carried-1119 --repo $N`, every tool run gets its `--known`, an inventory missing
  from the committed fixture is counted), `test_b_fixture_build_fails_one_not_run_line`. PROBE F1 on the staged copy:
  `336 64`, exit 0. The false text (header, NOTES, record line) is rewritten.
- **F2 (B), fixed.** Sender `defs-carried-nightly` matched coord_diet's `GUARD_SENDER_RX` ("nightly") and woke the
  orchestrator at once. Sender is now `defs-carried-report`: `urgent()` -> `(False, 'unmarked (defs-carried-report)')`.
  Regression test: `test_c_drop_message_goes_to_hourly_digest` runs the real `coord_diet.urgent()` on the message the
  step sent. PROBE F2 on the staged copy: exit 0.
- **Note C (latest earlier record untested)**: `test_c_compares_with_latest_earlier_record` added.
- **Note C (ids leaving the fixture reported as DROPPED)**: fixed; such a case is a "left the inventory" line, no
  message (`test_c_case_left_inventory_not_a_drop`).
- **Note C (15 x 900 s worst case)**: not changed; the step runs after every nightly output is written, so a slow step
  delays only the next loop check, not the nightly's result.

## Evidence (saved in `reviews/defs-carried-nightly-report-1120/`)
- `test-output.txt`: 11 tests; staged copy 11 pass; installed first version 9 fail; pre-step backup 11 fail.
- `dry-run-record.md/.json`: the staged step on the live inventories, VE at f20025e7 read-only: 15 documents, 0 not run,
  834 cases, carried 194, not carried 640 (anthropic-rsp 28 / 36 of 64 rows; openai-preparedness 0 / 336 of 50 rows).
- Install read sent to the DRI decider (`msg.sh dri`), with the backup, mv and restart commands of NOTES.md.

## Seeded bugs (each in a copy of `nightly-verify.sh.new-defscarried`, run with NV=<copy>; staged file never edited)
Language: zsh with an inline Python step (no VE Lean, Python or Rust product code changed). Full list: `mutants.json`.
- m6 `--known` dropped from the tool call -> `test_a_fixture_built_from_live_inventories` FAILS (and 7 more).
- m7 sender `defs-carried-nightly` -> `test_c_drop_message_goes_to_hourly_digest`, `test_c_drop_reported_and_digested` FAIL.
- m8 `reverse=True` removed from `earlier()` -> `test_c_compares_with_latest_earlier_record` FAILS.
- m9 `gone = sorted(was - ok)` -> `test_c_case_left_inventory_not_a_drop` FAILS.
- m10 builder-failure not-run line removed -> `test_b_fixture_build_fails_one_not_run_line` FAILS.
- m1 (`PASSING = ('CARRIED',)`) and m3 (`ok - was`) rerun on the new copy: caught.

SIZE: 58 product (staged runner lines changed this round; 145 against the pre-step runner), 130 tests, 147 other hand-written lines (NOTES.md, this REPORT).

## Notes for the DRI
- The fixture builder reads the audit pin 3d6b459df4 and the repair trees from `$N` (ve-nightly); a clone without them
  gives one not-run line, never a 0/0 report.
- Cases without a row id (repairs, UDHR D7 pairs) count as their own row in the rows figure.

## Self-review against BUILDER-CHECKLIST
1. Lean answers typed and contained: N.A. (no relay or Lean change).
2. Every deliverable built: PASS (step staged, tests, dry run, install read; `test_a_report_in_nightly_record`).
3. Tests can fail: PASS (m1-m10 in `mutants.json`; installed and backup runners fail the suite).
4. Python, Lean and Rust agree: N.A.
5. R8 binding: N.A.
6. Gate evidence matches final HEAD: PASS (the chain gates this HEAD; this commit changes only this report).
7. No unsigned item: PASS (no DELTA row, nothing reserved).
8. User-visible change in DELTA: N.A. (no VE user-visible change).
9. Test selection: N.A. (no VE code changed).
10. Lean statements: N.A.
11. Budgets fail closed: PASS (a timeout is a not-run line, never a carried or dropped verdict; `test_b_tool_crash_one_not_run_line`).
12. CPU or memory regression: PASS (outside the gate; about 29 s for the fixture plus the tool runs, after the nightly's outputs).
13. Removed or renamed tests: N.A. (none removed; control-plane tests only added).
14. Both directions, cited evidence: PASS (installed and staged runs in `test-output.txt`; probes F1 and F2 rerun).
15. The four FIX classes: PASS (behaviour tested for each finding: `test_a_fixture_built_from_live_inventories`,
    `test_c_drop_message_goes_to_hourly_digest`).
