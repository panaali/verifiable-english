# p1-path-hold-alert: a ready p1 row held behind a feed path hold for 30 min is reported to the decider

- Status: built and staged in `/home/seyran/code/manage-agents` as `tools-local/decider-ready-alert.py.new-pha`.
  INSTALL WAITS FOR DECIDER READ (section at the end). The new tests are in `tools-local/test_p1_ready_alert.py`, edited in
  place (backup `test_p1_ready_alert.py.bak-20261116-pha`). The test file picks the `.new-pha` copy while it exists and the
  live script once the install moves it into place.
- No DELTA rows (control-plane tooling; no VE trusted line). No DRI signature reserved. Trust +0.
- This VE branch holds only this report and its evidence. No VE product code (Lean, Python or Rust) changed.
- Tests: 10 of the 10 new `PathHold` tests fail on the installed script, and all 33 tests pass on the staged script
  (`run-live.log`, `run-staged.log`). The existing 23 tests pass on both. `test_decider_ready_alert.py` passes 9 of 9 on the
  staged script (`run-dra-staged.log`, run with `DRA_SCRIPT=<.new-pha>`).

SIZE: 67 product (decider-ready-alert.py +67/-11, docstring and comments included), 116 tests (test_p1_ready_alert.py +116/-1),
1 other hand-written file (this report; the diff, logs and seeded-bugs.json are records).

Row: p1-path-hold-alert (infra p1). Filed by the DRI decider 2026-11-16 12:35Z on orchestrator NOW(critical) 121946Z item 2;
task `prompts/task-p1-path-hold-alert.txt`.

## Deliverables

| # | Task line | Where (staged `decider-ready-alert.py.new-pha`) | Test (`test_p1_ready_alert.py`) |
|---|---|---|---|
| 1 | A ready row with priority <= 1 whose state starts "feed: path" or names a path in flight, held for >= 30 min, counts as not startable in `p1_unstartable()` | `PATH_HOLD`, `path_held`, `p1_unstartable` (returns `(row, age, hold text or None)`) | `PathHold.test_31_min_alerts_names_branch_and_stage`, `test_29_min_silent_30_min_alerts` |
| 1 | Age: from when the hold was first seen, or ready_t; say which in a code comment; no new state file unless dedup needs one | `ready_t`, falling back to `status_t` and then `created`. The reason is in the comment in `p1_unstartable`. No new state file | `test_29_min_silent_30_min_alerts` (29 min silent, 30 min alerts) |
| 1 | The existing `p1-unstartable-alert.sent` 4 h dedup applies | Held rows are written to the same file as not-startable rows, and nothing is written when the send fails | `test_second_pass_within_4h_silent_then_again`, `test_held_and_not_startable_one_message`, `test_failed_send_records_nothing` |
| 2 | The message line names the holding branch and its stage: "p1 ready but held: <id>, <owner>, <age>, path <p> in flight on <branch> (<stage>)" | `hold_text`, `holder_stage`, plus a "p1 ready but held: " part in `main` | `test_31_min_alerts_names_branch_and_stage` (merge train), `test_chain_stage_by_branch_link_or_row_id` (chain stage), `test_stage_unknown_without_holder_row` |
| 2 | Never silent: if the state cannot be parsed, the alert still goes out with the raw state text | `hold_text` returns `state[:200]` when `PATH_HOLD` does not match | `test_unparsed_hold_named_raw` |
| 3 | Rows held for any other "feed:" reason (DRI hold, waits for ..., account room) are unchanged | `path_held` only matches path holds | `test_other_feed_holds_unchanged` (DRI hold, waits for, account room, both capacity-hold texts) |
| 3 | p2 row with the same state does not alert | the existing `prio_le_1` check runs first | `test_p2_held_row_not_named` |
| - | Each new test fails on the installed script and passes on `.new-pha`; existing tests stay green on both | | `run-live.log`: FAILED (failures=6, errors=4), all in `PathHold`. `run-staged.log`: Ran 33, OK |

The task's negative cases (29 min, p2, DRI hold) would pass on the installed script, which never names a held row. So each
negative test also has a positive control: 30 min alerts, a p1 held row is named, and a path-held control row is named. That way
every new test fails on the installed script, as the task requires.

Readings I took (in each case the conservative or narrower option; I did not ask):
- **"Contains 'in flight on '" is narrowed to a path hold: `path <p> in flight on <branch>`.** feed-features.sh also writes
  the capacity holds "queue items in flight on VM1 1 >= 1 (...)" and "queue items in flight on <host>: live builders ...". These
  contain "in flight on " but are not path or serial holds, and task item 3 keeps other feed holds unchanged. A held row is one
  whose state starts with "feed: path" or matches `\bpath (\S+) in flight on ([^\s;()]+)`. That matches every path-hold
  writer: feed-features.sh lines 204, 205 and 208, queue-runner.sh line 32, and infra_feed.py line 416. Seeded bug S3 (the
  literal "in flight on " reading) fails `test_other_feed_holds_unchanged`.
- **Age is measured from `ready_t`, not from when the hold was first seen.** The backlog keeps no timestamp for when a row's
  state became a hold, because `backlog.py item_status` rewrites `state` on every seed pass. I did not add a state file, since
  dedup does not need one. The age can only be longer than the hold, so the alert fires no later than 30 min into the hold.
- **Holder lookup.** The holder is the row whose `links.branch` equals the branch (live: `kb-9` has `feature/kb-9`). If there is
  none, it is the row whose id is the branch without its `<kind>/` prefix. Among the holder rows, a state that starts with
  "chain stage " or "merge train" is preferred. Otherwise the first non-empty state is used (for example "chain not running; ..."),
  cut to 100 characters. If there is no holder row, or every holder state is empty, the stage is "stage unknown".
- **A row that is both not startable and held is listed as not startable.** The feed checks paths only after the task file
  exists, so in practice the two cases do not overlap.
- **One message per pass.** The held part is a third " | " part of the same NOW(critical) message, after the decider-owned part
  and the not-startable part.

## Seeded bugs (Python; `seeded-bugs.json`, all CAUGHT)

All of these are in `manage-agents/tools-local/decider-ready-alert.py.new-pha`. Each was applied to a /tmp copy and run with
`P1RUA_ALERT=<copy>`. The staged file was never edited (sha256 `cf3a7f43...c856` before and after).

| Id | Bug | Failing tests |
|---|---|---|
| S1 | path hold never counted | all 10 `PathHold` tests |
| S2 | stage never looked up | `test_31_min_alerts_names_branch_and_stage`, `test_chain_stage_by_branch_link_or_row_id`, `test_other_feed_holds_unchanged` |
| S3 | any "in flight on" counts (capacity holds too) | `test_other_feed_holds_unchanged` |
| S4 | unparsed hold silenced | `test_unparsed_hold_named_raw` |
| S5 | held rows not recorded for dedup | `test_second_pass_within_4h_silent_then_again`, `test_held_and_not_startable_one_message` |
| S6 | held rows skip the 30 min wait | `test_29_min_silent_30_min_alerts` |
| S7 | priority not checked | `test_p2_held_row_not_named`, `Alert.test_non_matching_rows_silent` |
| S8 | chain-stage preference dropped | `test_chain_stage_by_branch_link_or_row_id` |

No Lean or Rust code changed, and no VE Python changed.

## Checks run

- `python3 -I tools-local/test_p1_ready_alert.py` with the staged script: Ran 33, OK. With
  `P1RUA_ALERT=tools-local/decider-ready-alert.py` (live): 10 failures/errors, all in `PathHold`. The other 23 pass.
- `DRA_SCRIPT=tools-local/decider-ready-alert.py.new-pha python3 -I tools-local/test_decider_ready_alert.py`: Ran 9, OK.
- `python3 -I tools-local/decider-ready-alert.py.new-pha --dry-run` on the live backlog printed nothing. No ready p1 row is
  path-held right now, and `rsp-b-repair-1115` is in flight. Nothing was recorded.
- Final selected run on committed HEAD a414db4c62 (clean tree, `MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select`): exit 0,
  5 units, 5 passed (GitHub Actions run p1-path-hold-alert-a414db4c-t835171, 2 shards). This branch adds only docs.
- Install read sent: `inbox/dri/20261116T133352Z-infra-p1-path-hold-alert-32524.md`.

## Notes for the DRI

- `test_decider_ready_alert.py` defaults to `.new-p1rua2`/`.new-p1rua`, which no longer exist, so it runs the live script. I
  ran it against `.new-pha` with `DRA_SCRIPT` and did not change its picker.
- The feed log's `WAIT <id>: path ...` lines could give a true first-seen time for a hold. I did not use them because ready_t
  is enough for the 30 min rule.

## INSTALL WAITS FOR DECIDER READ

- Live sha check before the install: `sha256sum tools-local/decider-ready-alert.py` must print
  `23b635ec45cc933c48f3e4e0ab6be7d30169b43062bb0462810b03bd31e2eb94` (the file the staged copy was built from). Staged:
  `cf3a7f43a3ac271021ae5d8d87c888a09004890f76385372eeaf4fbb1fd6c856  tools-local/decider-ready-alert.py.new-pha`.
- Install (in `/home/seyran/code/manage-agents`):
  `cp -p tools-local/decider-ready-alert.py tools-local/decider-ready-alert.py.bak-20261116-pha && mv tools-local/decider-ready-alert.py.new-pha tools-local/decider-ready-alert.py`
  then `python3 -I tools-local/test_p1_ready_alert.py` (33 OK on the live file).
- Scope: `ve-svc-backlog-*.scope` (`zsh backlog-svc.sh`). Line 14 of that script runs `python3 -I $M/tools-local/decider-ready-alert.py`
  as a new process on every pass, so nothing caches the module and no restart is needed. The next pass (within 600 s) uses the
  new file.
- Rollback: `mv tools-local/decider-ready-alert.py.bak-20261116-pha tools-local/decider-ready-alert.py`.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no Lean answer is read; control-plane script only).
2. Deliverables built, no rule broken: PASS. See the Deliverables table; each row has its test. No report test was added and
   no VE file outside `docs/infra/p1-path-hold-alert/` was touched.
3. Tests can fail: PASS. Seeded bugs S1-S8 are all CAUGHT (`seeded-bugs.json`), and the 10 new tests fail on the live script.
4. Python/Lean/Rust agree: N.A. (no checker code).
5. R8 binding: N.A. (no Lean answer).
6. Gate evidence matches final HEAD: PASS. The final selected run is on the committed HEAD, and the chain gate runs on it.
7. No unsigned item: PASS. DELTA none; no signature reserved.
8. Every user-visible change in DELTA: N.A. No VE output changed. The changed decider message text is documented above.
9. Test selection: PASS. Only docs changed. The selected run (5 units) exited 0.
10. Lean statements: N.A.
11. Budgets fail closed: PASS for the one relevant point: an unparsable hold still alerts (`test_unparsed_hold_named_raw`), and a
    row with no timestamp is skipped as before. The tests use an injected clock (`DRA_NOW`) and no sleeps.
12. CPU/memory regression: N.A. `holder_stage` is one scan of the backlog per held row, and held rows are few.
