# p1-ready-unstartable-alert: the decider is told when a p1 row is ready but nobody can start it

- Status: built, staged as `.new-p1rua` in `/home/seyran/code/manage-agents`, and INSTALLED by the decider after the install
  read (`inbox/dri/done/20261116T030645Z-infra-p1-ready-unstartable-alert-3398579.md`). The backups `*.bak-20261116-p1rua`
  are in place. The live alert fired at 03:11Z for fid-mech-b2 and lw-allowances-shared (`p1-unstartable-alert.sent`).
  No DELTA rows, no DRI signature reserved, trust +0.
- Fix round 1 (review F1, `manage-agents/p1-ready-unstartable-alert-review.final.md`): staged as `.new-p1rua2`
  (decider-ready-alert.py, test_p1_ready_alert.py, test_decider_ready_alert.py); INSTALL WAITS FOR DECIDER READ (see
  "Fix round 1" below). A launch link now counts as startable only when `backlog.py launch_spec` can start it.
- What changed: (1) `decider-ready-alert.py` also reports any p1 ready row that has been not startable (fix round 1: a launch
  link `backlog.py launch_spec` cannot start, or no launch link and no task file) for 30 min or more, whatever its owner. It reports each row at most once per 4 h. (2) `backlog.sh add`/`update` warns and
  logs when it leaves a row at p1 + ready without a task file or a "writer: <name> by <UTC>" note line. It never refuses.
- Tests: `tools-local/test_p1_ready_alert.py`: 10 of 14 fail on the installed code, and all 14 pass on the staged code.
  The existing tests also pass on the staged code.
- This VE branch holds only this report and its evidence. No VE product code (Lean, Python or Rust) changed.

SIZE: 131 product (decider-ready-alert.py +89/-20, backlog.py +42), 186 tests (test_p1_ready_alert.py 179 new,
test_decider_ready_alert.py +7/-3), 1 other hand-written file (this report; seeded-bugs.json is a record).

Row: p1-ready-unstartable-alert (infra p1). Decision `reviews/dri-decisions-20261116-adv0244.md` item 2 (ADV-20261116T0244-2);
orchestrator `inbox/dri/done/20261116T025503Z-orchestrator-3198539.md`; task `prompts/task-p1-ready-unstartable-alert.txt`.

## Deliverables

| # | Task line | Where (staged) | Test |
|---|---|---|---|
| 1 | Any p1 row that is ready and not startable for at least 30 min since ready_t gets ONE `msg.sh dri` "NOW(critical): p1 ready but not startable: <ids>, <owner>, <age>", whatever its owner. Deduped per row per 4 h | `tools-local/decider-ready-alert.py.new-p1rua`: `has_task_file`, `startable`, `p1_unstartable`, state `p1-unstartable-alert.sent` | `Alert.test_no_task_file_31_min_alerts_once`, `test_29_min_silent`, `test_task_file_or_launch_link_silent`, `test_task_link_to_missing_file_alerts`, `test_second_run_within_4h_silent_then_again`, `test_non_matching_rows_silent`, `test_p0_and_status_t_fallback`, `test_several_rows_one_message_with_decider_part`, `test_failed_send_retries` |
| 1 | Extend decider-ready-alert.py; no new service, flag or loop | It runs in the same svc-backlog pass after `backlog.py seed`. The message is the same `msg.sh dri decider-ready-alert` call, so both parts share one message per pass | `test_decider_ready_alert.py` `Loop` (staged copy) |
| 2 | `add`/`update` that leaves a row at priority 1 + ready, with no `--link task=<existing file>` and no note line "writer: <name> by <UTC>", prints a warning and records it. Never refused | `backlog.py.new-p1rua`: `WRITER_RE`, `p1_filing_gap`, `p1_filing_warn`. The warning goes to stderr. The record is one line in `backlog-p1-filing.log` next to BACKLOG.jsonl (UTC, id, command, reason) | `Filing.test_add_p1_ready_without_task_or_writer_warns`, `test_add_with_missing_task_file_warns`, `test_update_to_p1_ready_warns`, `test_task_file_or_writer_silent`, `test_writer_line_needs_a_time`. Every case asserts exit 0 (warn, not refuse) |
| - | Existing decider-ready-alert tests stay green | `tools-local/test_decider_ready_alert.py.new-p1rua` | 8 of 8 OK on the staged script (below) |

Readings I took (the conservative or narrower option each time; I did not ask):
- **Not startable = no task file AND no launch link.** SUPERSEDED by fix round 1 (review F1): `launch_spec` also rejects a
  launch link whose launcher needs a task file that is missing ("task file missing"), an unknown launcher, and a launcher
  without its arguments, so the alert now asks `launch_spec` itself whenever a row has a launch link (below). Original
  reading: this is the reason `backlog.py launch_spec` gives ("no task file and no
  launch link") and the one `INFRA-FEED-STATUS.md` showed for the incident rows. The task counts as present when any of
  these exists: the file `links.task` names, `prompts/task-<id>.txt`, or `prompts/dri-task-<id>.txt`. A `links.task` that
  names a missing file does not count. I rejected the other reading ("no task file OR no launch link"): it would alert on
  every feature row with a task file, because those start from FEATURE-QUEUE.tsv without a `links.launch`.
- **"priority 1" = priority <= 1.** This matches the existing decider-owned rule. `rsp-b-repair-1115`, one of the four
  incident rows, is stored as priority 0.
- **Age** is measured from `ready_t`, falling back to `status_t` and then `created`. A row with none of these is skipped,
  because its age is unknown.
- **One message per pass.** When a pass finds both a decider-owned ready row and a not-startable row, they go in one message
  joined by " | ". This keeps the existing one-message-per-pass behaviour and its tests. A failed send records neither part,
  so the next pass retries both.
- **Dedupe is per row id for 4 h**, regardless of `ready_t`. The task says "per row per 4 h".
- **The filing rule covers `add` and `update` only**, as the task names them. It does not cover `update-status`, or rows the
  seed flips to ready. Those are covered by the alert in deliverable 1 after 30 min.
- **The writer line** must be a line of the row's `note` matching `writer: <name> ... by YYYY-MM-DDTHH:MM[:SS]Z`
  (case-insensitive). A name without a time still warns (`test_writer_line_needs_a_time`).

## Test runs (2026-11-16 ~03:05Z, manage-agents, `python3 -I`)

| Run | Command | Result |
|---|---|---|
| New tests, staged | `python3 -I tools-local/test_p1_ready_alert.py` (defaults to the `.new-p1rua` copies) | `Ran 14 tests ... OK` (`run-staged.log`) |
| New tests, installed | `P1RUA_ALERT=tools-local/decider-ready-alert.py P1RUA_BACKLOG=backlog.py python3 -I tools-local/test_p1_ready_alert.py` | `FAILED (failures=9, errors=1)`: 10 of 14 fail. The 4 that pass are the silent cases (`run-live.log`) |
| Existing alert tests, staged script | `BACKLOG_SVC_SH=backlog-svc.sh python3 -I tools-local/test_decider_ready_alert.py.new-p1rua` | `OK` (8 tests) |
| Existing alert tests, installed | `python3 -I tools-local/test_decider_ready_alert.py` | `OK` |
| backlog.py tests, staged | `BL_SCRIPT=$PWD/backlog.py.new-p1rua python3 -I tools-local/test_backlog_{now,queue_gap,reject_not_done,seed_blocked}.py` | all exit 0: now `Ran 29 ... OK`, queue_gap `Ran 5 ... OK`, reject_not_done OK, seed_blocked OK |
| Selected VE tests, committed HEAD 267d312b0f | `MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` | exit 0: `8 units, 8 passed` (GitHub Actions, 2 shards) |
| Dry run on the live backlog | `python3 -I tools-local/decider-ready-alert.py.new-p1rua --dry-run` | `NOW(critical): p1 ready but not startable: fid-mech-b2, infra feed, 51h43m; lw-allowances-shared, infra feed, 8h43m. ...` Nothing was recorded (`p1-unstartable-alert.sent` absent) |

Change to an existing test: in `test_decider_ready_alert.py`, `test_non_matching_rows_silent` had a fixture row `feat`
(owner "feature planner", p1, ready, no task file, ready about 13 h earlier). Under the new rule that row must alert, so the
old assertion "silent" conflicts with deliverable 1. The staged copy gives `feat` a `links.launch`, which makes it startable.
The test still checks what it was written for: the decider-owned rule ignores another owner's row. The staged copy also
defaults `SCRIPT` to the staged `.new-p1rua` script (env `DRA_SCRIPT`). No test was removed or renamed.

## Seeded bugs

Each bug went into a temp copy of the staged file, and the test that should catch it was run against that copy
(`P1RUA_ALERT=` / `P1RUA_BACKLOG=`). The staged files were never edited. All 6 were caught; details are in `seeded-bugs.json`.

| # | Language / file | Bug | Failing test |
|---|---|---|---|
| S1 | Python `manage-agents/tools-local/decider-ready-alert.py.new-p1rua` | alerts at 28 min | `Alert.test_29_min_silent` |
| S2 | Python, same | `prompts/task-<id>.txt` not counted as a task file | `Alert.test_task_file_or_launch_link_silent` |
| S3 | Python, same | dedupe 3 h instead of 4 h | `Alert.test_second_run_within_4h_silent_then_again` |
| S4 | Python, same | only owner "infra feed" alerted | `Alert.test_no_task_file_31_min_alerts_once` |
| S5 | Python `manage-agents/backlog.py.new-p1rua` | filing check on `add` only | `Filing.test_update_to_p1_ready_warns` |
| S6 | Python, same | a writer line without "by <UTC>" accepted | `Filing.test_writer_line_needs_a_time` |

## Install (done by the decider; the commands as sent)

After install, `git diff --no-index --numstat <file>.bak-20261116-p1rua <file>` gives 89/20 (decider-ready-alert.py), 42/0
(backlog.py) and 7/3 (test_decider_ready_alert.py), the same counts as the staged diff. `python3 -I
tools-local/test_p1_ready_alert.py` on the installed files: `OK` (14 tests).


```
cd /home/seyran/code/manage-agents
cp -p backlog.py backlog.py.bak-20261116-p1rua
cp -p tools-local/decider-ready-alert.py tools-local/decider-ready-alert.py.bak-20261116-p1rua
cp -p tools-local/test_decider_ready_alert.py tools-local/test_decider_ready_alert.py.bak-20261116-p1rua
mv backlog.py.new-p1rua backlog.py
mv tools-local/decider-ready-alert.py.new-p1rua tools-local/decider-ready-alert.py
mv tools-local/test_decider_ready_alert.py.new-p1rua tools-local/test_decider_ready_alert.py
python3 -I tools-local/test_p1_ready_alert.py && python3 -I tools-local/test_decider_ready_alert.py
```
Restart: none. `backlog-svc.sh` starts a fresh `python3 -I` for `backlog.py` and `decider-ready-alert.py` on every pass.
The staged copies were taken from these bases (sha256 prefix): backlog.py `cbed2acf1ba8ee52`,
decider-ready-alert.py `b52e507bdacac787`, test_decider_ready_alert.py `cd1fb13a0a2d8c08`. If a live file no longer matches
its prefix, re-stage before the `mv`. `tools-local/test_p1_ready_alert.py` is new and already in place; it tests the staged
copies until they are moved in. `live-changes.diff` holds the full staged diff.

## Notes for the DRI

- On its first pass after install, the alert will report `fid-mech-b2` (ready about 52 h) and `lw-allowances-shared`
  (about 9 h). Both are p1 infra-feed rows with no task file and no launch link (dry run above). The four incident rows
  now have task files and do not match.
- `update-status <id> ready` on a p1 row does not trigger the filing warning, because the task names only `add`/`update`.
  The 30-min alert covers that case (for a row with a launch link, only since fix round 1: before it, a row with
  `launch=delegate` and no task file was never alerted, review F1).
- `backlog-p1-filing.log` and `p1-unstartable-alert.sent` grow by one line per event. Neither is rotated (both are small).

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relayed route, no VE code).
2. Every deliverable built: PASS. Deliverables table above, each row with its test (`test_p1_ready_alert.py`, 14 tests).
3. Tests can fail: PASS. Seeded bugs S1-S6 are all caught, and 10 of 14 new tests fail on the installed code (`run-live.log`).
4. Python/Lean/Rust agree: N.A. (ops script; no checker output).
5. R8 binding: N.A. (no Lean answer read).
6. Gate evidence matches HEAD: PASS. The chain gates the final HEAD. This branch adds docs only.
7. No unsigned item: PASS. No DELTA rows, no trust growth.
8. User-visible change in DELTA: N.A. (no VE user-visible output changes; the change is to ops scripts outside the repo).
9. Test selection: N.A. (docs-only diff in VE).
10. Lean statements: N.A. (no Lean).
11. Budgets and deadlines fail closed: PASS. The clock is injected (`DRA_NOW`), with no sleeps. The 30-min and 4-h bounds
    are tested from both sides (`test_29_min_silent` / `test_no_task_file_31_min_alerts_once`;
    `test_second_run_within_4h_silent_then_again`).
12. No CPU or memory regression: N.A. (one extra pass over the rows already loaded, plus at most 3 `isfile` calls per p1
    ready row).
13. Test-removed trailers: N.A. (no test removed or renamed; `test_non_matching_rows_silent` keeps its name).
14. Both directions, cited evidence, spec re-read: PASS. Each check is tested on both sides: alert vs silent (29/31 min,
    task file vs none, within vs after 4 h) and warn vs silent (`test_task_file_or_writer_silent`). Every claim cites a
    command in "Test runs". Spec re-read: "p1 ready but not startable: <ids>, <owner>, <age>", ">= 30 min since ready_t",
    "deduped per row per 4 h" and "whatever its owner" against `prompts/task-p1-ready-unstartable-alert.txt` (Task
    paragraph, DELIVER (1)); "writer: <name> by <UTC>" and "refuse is NOT wanted" against the same file, DELIVER (2).
15. Four classes: no overclaim, PASS (the readings and limits above are stated, including that `update-status` is not
    covered); no silent cut, PASS (both deliverables built); every new check can fail, PASS (S1-S6); limits charged
    before work, N.A. (no checker limits).

## Fix round 1 (review F1)

Review: `manage-agents/p1-ready-unstartable-alert-review.final.md` (one finding, F1 (B); notes C1-C6 not filed). The work is
staged as `.new-p1rua2` next to the installed files in `/home/seyran/code/manage-agents/tools-local/`; the full staged diff is
`fix1-changes.diff`. No VE product code (Lean, Python or Rust) changed; no DELTA rows; no DRI signature reserved.

SIZE: 33 product (decider-ready-alert.py +40/-7), 122 tests (test_p1_ready_alert.py +116/-7, test_decider_ready_alert.py
+6/-4), 0 other hand-written files besides this section (seeded-bugs.json, fix1-*.log, fix1-changes.diff are records).

| Finding | Class | Fix | Regression tests (`tools-local/test_p1_ready_alert.py.new-p1rua2`) |
|---|---|---|---|
| F1 (B) `startable()` counted any non-empty `links.launch` as startable, so a p1 ready `launch=delegate` / `infra-item` row with no task file never alerted while the infra feed listed it "task file missing" | The alert kept its own copy of "can this row be started" instead of reading the one owner, `backlog.py launch_spec` (the function `infra_feed.py` starts rows with). Every launch link launch_spec rejects was missed: a task-needing launcher with no (or a missing) task file, an unknown launcher (live backlog: `iso` x6, `continue-item` x1), a launcher without its arguments (`research-wave`, `design-item`, `research-refresh`) | `startable()`: a row with a launch link is startable iff `backlog.py launch_spec(r)` returns a spec. The alert loads that function from the backlog.py next to tools-local (hook `DRA_BACKLOG_PY`) with its `M` pointed at `DRA_M`. If it cannot be loaded, a launch link counts as not startable (alert, never silence) and one line says so. A row with no launch link keeps the task-text rule (startable iff it has a task file) | `LaunchLink.test_probe_f1_delegate_without_task_file_alerts` (PROBE F1 verbatim), `test_task_needing_launcher_without_task_file_alerts`, `test_unknown_launcher_alerts_even_with_task_file`, `test_launcher_without_arguments_alerts`, `test_startable_launch_links_silent`, `test_launch_spec_unavailable_alerts`; class test `LaunchSpecAgreement.test_alert_agrees_with_launch_spec`: 72 launch links (every launcher in `backlog.LAUNCH_HOW`, enumerated from backlog.py, plus `iso`, `continue-item`, `Delegate`; x no / one / three arguments; x no / existing / missing task file), the alert names exactly the rows launch_spec rejects |
| F1, third bullet: `p1_filing_gap` | No instance (the review says so): the filing rule checks `links.task` only, whatever the launch link | none needed | - |

Also from the review notes (not filed, cheap): C1 `Alert.test_exactly_30_min_alerts` (the 30:00 boundary alerts) and C2
`Filing.test_add_p0_ready_warns` (p0 is "priority 1" for the filing rule). C3-C6 are unchanged and stay as stated above.

Changed existing test: `test_decider_ready_alert.py` `test_non_matching_rows_silent` used `links={"launch": "delegate"}`
with no task file to make the other-owner row `feat` startable; under F1 that row is not startable (the infra feed could not
start it), so the staged copy uses `research-wave w1 VE/Research`, which launch_spec accepts without a task file. The test
still checks the same thing. Both test files default to the `.new-p1rua2` copy, then `.new-p1rua`, then the live file.

PROBE F1 (the review's command): before the fix, on the installed script: `AssertionError: ''`. After, with the path pointed
at `tools-local/decider-ready-alert.py.new-p1rua2`: passes (`NOW(critical): p1 ready but not startable: dlg, infra feed, 2h00m.
...`). It is the regression test `LaunchLink.test_probe_f1_delegate_without_task_file_alerts`.

Test runs (2026-11-16, manage-agents/tools-local, `python3 -I`):

| Run | Result |
|---|---|
| `test_p1_ready_alert.py.new-p1rua2` on the staged alert | `Ran 23 tests ... OK` (`fix1-run-staged.log`) |
| `test_decider_ready_alert.py.new-p1rua2` on the staged alert | `Ran 8 tests ... OK` (`fix1-run-staged.log`) |
| `P1RUA_ALERT=tools-local/decider-ready-alert.py` (installed) `test_p1_ready_alert.py.new-p1rua2` | `FAILED (failures=4, errors=2)`: 6 of the 7 F1 tests fail; `test_startable_launch_links_silent` passes (silent case); C1/C2 pass (they guard mutants, not a bug of the installed code) (`fix1-run-live.log`) |
| `DRA_SCRIPT=...new-p1rua2` with the installed `test_decider_ready_alert.py` | `test_non_matching_rows_silent` FAILS: the old `feat` fixture (delegate, no task file) is the F1 case |
| Dry run of the staged alert on the live backlog | empty (the live p1 ready rows are deduped or startable); the only p1 ready row, `rsp-b-repair-1115`, is startable under both versions, so the install adds no alert today |

Seeded bugs S7-S13 (Python, temp copies of the staged files; all CAUGHT; `seeded-bugs.json`, `"round": "fix1"`):

| # | File | Bug | Failing test |
|---|---|---|---|
| S7 | decider-ready-alert.py.new-p1rua2 | any launch link is startable (the installed behaviour) | `LaunchLink.test_task_needing_launcher_without_task_file_alerts` |
| S8 | same | launch_spec unavailable counts as startable | `LaunchLink.test_launch_spec_unavailable_alerts` |
| S9 | same | `bl.M = M` dropped (task paths resolve in the live dir) | `LaunchLink.test_startable_launch_links_silent` |
| S10 | same | `< P1_AFTER` -> `<= P1_AFTER` (C1) | `Alert.test_exactly_30_min_alerts` |
| S11 | backlog.py (installed) | `p1_filing_gap` `<= 1` -> `== 1` (C2) | `Filing.test_add_p0_ready_warns` |
| S12 | decider-ready-alert.py.new-p1rua2 | a task file makes any launch-link row startable | `LaunchLink.test_unknown_launcher_alerts_even_with_task_file` |
| S13 | same | links containing "research" are startable without launch_spec | `LaunchSpecAgreement.test_alert_agrees_with_launch_spec` |

INSTALL WAITS FOR DECIDER READ. The bases of the staged copies (sha256 prefix): decider-ready-alert.py `a4a58c81b7dadab5`,
test_p1_ready_alert.py `ed72e0fa9dde278e`, test_decider_ready_alert.py `42170efad5ceaf93` (backlog.py is unchanged and is
read, not edited). If a live file no longer matches its prefix, re-stage before the `mv`.

```
cd /home/seyran/code/manage-agents/tools-local
cp -p decider-ready-alert.py decider-ready-alert.py.bak-20261116-p1rua2
cp -p test_p1_ready_alert.py test_p1_ready_alert.py.bak-20261116-p1rua2
cp -p test_decider_ready_alert.py test_decider_ready_alert.py.bak-20261116-p1rua2
mv decider-ready-alert.py.new-p1rua2 decider-ready-alert.py
mv test_p1_ready_alert.py.new-p1rua2 test_p1_ready_alert.py
mv test_decider_ready_alert.py.new-p1rua2 test_decider_ready_alert.py
cd .. && python3 -I tools-local/test_p1_ready_alert.py && python3 -I tools-local/test_decider_ready_alert.py
```
Restart: none (`backlog-svc.sh` starts a fresh `python3 -I tools-local/decider-ready-alert.py` every pass).

Install read sent: `inbox/dri/20261116T054740Z-infra-p1-ready-unstartable-alert-1618430.md`. Checks on this branch: selected
VE tests on 26e09c8240 exit 0 (GitHub Actions, 2 shards, 10 units passed; docs-only diff); `lake build` OK (1475 jobs);
`python3 lean/audit.py` PASS.
