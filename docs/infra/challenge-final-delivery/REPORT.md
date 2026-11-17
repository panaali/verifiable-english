# challenge-final-delivery: a finished challenge final reaches its row's addressee within 30 min

- Status: fix round 1 done; staged again as `manage-agents/tools-local/decider-ready-alert.py.new-challew` (sha256 `e7fa412c…`).
  INSTALL WAITS FOR DECIDER READ (install-read message: `manage-agents/inbox/dri/20261117T220056Z-challenge-final-delivery-fix1-3928954.md`;
  the 21:39Z install read was REJECTED: see `fix-round-1.md` section 3, its cause was my in-place edit).
- What changed in round 1: review F1 (every not-closed row with an in-flight stamp older than the final is named: review rows of
  the release gate, `dri-<x>` delegate rows, seeder and feed launches); review F2 (the suites test the live script after the install);
  the DRI note's state-file items (a state line in any shape never stops a pass; the script is tested under its live name).
- Open items: none. No DRI signature is reserved; no DELTA rows (control-plane tooling only; no Lean, VE trusted line or verdict
  rule changed; trust +0). This VE branch holds only this report, its evidence and two evidence scripts. Per-finding lines: `fix-round-1.md`.

SIZE (item, staged files against the live ones and the pre-item test backups): 203 product lines changed (+177 -26 in the
staged script, docstring included), 423 test lines (+407 -16 in two test files), about 300 other hand-written lines (this
report, `fix-round-1.md`, `dry_install.py`, `run_seeds.py`). Round 1 alone: script +87 -26, tests +243 -27 (`fix-round-1.diff`).

## 1. Spec (row note, ruling `reviews/dri-ruling-record-void-astra-20261115.md` section F) and where each part is delivered

| Spec words | Delivered by | Test |
|---|---|---|
| "a *-challenge*.final.md" | `CF_GLOB = "*-challenge*.final.md"` over `$M` (where delegates write finals); empty files skipped | test_6_silent_cases (`build-x.final.md`, empty final) |
| "newer than its row's in-flight stamp" | `launch_t`: the latest of `status_t` when `status_cli` is `in-flight` (backlog.sh's write; the release gate and the seeder keep both) and the run start of backlog.py `row_run_t` (the delegate's `prompts/<name>.run.txt`, a `dri-<x>` row being its own delegate, else the feed's `infra-feed-state/<id>.json`); the final's mtime must be later | test_6 (`late-challenge`, `nostamp-challenge`, ready/blocked/review rows with no in-flight stamp), test_7, test_11 to test_16 |
| "whose row is not done" | any status but backlog.py `CLOSED` (merged, done, dropped), read from backlog.py; review, blocked and ready rows with a stamp are named | test_6 (closed rows), test_11, test_12, test_15, test_19 (the fallback equals `CLOSED`) |
| "after 30 min" | `CF_AFTER = 30 * 60` from the final's mtime; 29 min silent, 30 min named | test_1 |
| "msg to the row's addressee (orchestrator for Astra challenges)" | row `addressee` field (dri or orchestrator) wins; else orchestrator when "astra" is a word of the row id or file name; else dri, as one more part of the one dri message | test_1 to test_4, test_17 |
| "once" | state `decider-ready-alert.sent`, key `cf:<id>` + `<final>@<in-flight stamp>`; a row sent in flight again whose new final lands alerts again | test_1, test_7, test_16, Install.test_installed_under_live_name_with_live_state_file |
| "same periodic check as decider-ready-alert" / "no new loop" | code added to `decider-ready-alert.py`; `backlog-svc.sh` unchanged (line 14 already runs it after each seed) | Loop.test_backlog_svc_runs_alert_after_seed |
| failed send | a failed send records nothing for that addressee; the next pass retries; the other addressee's send is recorded | test_8, test_9 |
| "the existing cases stay green" | the 23 tests that existed before the item pass on the staged script; `test_p1_ready_alert.py` passes on it | `run-staged.log`, `run-p1-staged.log` |

How a final finds its row (`final_rows`): `links.final` is the file name, or `links.delegate` is its stem, or the stem (with or
without `dri-`) is a row id, alone or followed by `-<date>` / `-stopped-<date>` (`record-void-astra-challenge-1115` ->
`record-void-astra-challenge`). Every open row a final belongs to is named, once: a delegate row the seeder closed (`dri-X`,
done) does not close the challenge row `X` (test_5_row_mapping, test_18). A final no row claims is not named (test_6, `orphan-astra-challenge-1115`).

## 2. Evidence (commands and output files in this directory; all on the files with the sha256 in `fix-round-1.md`)

- Failing first, on the installed script (live, sha256 `ac8af596…`, the 13:45Z notask-wait-alert install):
  `DRA_SCRIPT=$PWD/tools-local/decider-ready-alert.py python3 -I tools-local/test_decider_ready_alert.py` -> `run-before.log`:
  `Ran 46 tests`, `FAILED (failures=17, errors=3)`. The 20 failing tests are all tests this item added. The 23 tests that
  existed before the item pass, and so do test_fin, test_6 (silence: the installed script sends nothing) and the picker test.
- Failing first for round 1, on the round-1 build (sha256 `08a69f50…`): `run-failing-first-round1.log`: `FAILED (failures=10,
  errors=1)`: test_11 to test_16, test_19, test_20 and the install test (`UnicodeDecodeError` on a non-UTF-8 state line stops
  the pass), plus test_1 and test_7 for the new `(<status>, in flight since ...)` wording.
- On the staged script: `python3 -I tools-local/test_decider_ready_alert.py` (`staged()` picks `.new-challew`, the only copy
  newer than the live file) -> `run-staged.log`: `Ran 46 tests`, `OK`.
- p1 suite on the staged script: `python3 -I tools-local/test_p1_ready_alert.py` -> `run-p1-staged.log`: `Ran 33 tests`, `OK`,
  `alert: .../decider-ready-alert.py.new-challew`.
- Dry install (section 5): `run-dry-install.log`: the picker picks the installed `decider-ready-alert.py`; 46/46 with no
  `DRA_SCRIPT`, 46/46 with `DRA_SCRIPT=<installed path>`, p1 33/33.
- The review's probes F1 and F2, run unchanged before and after the fix: `probes.log` (both rc 1 before, rc 0 after).
- Live dry run (reads the live backlog, records nothing): `python3 -I tools-local/decider-ready-alert.py.new-challew --dry-run`
  -> `live-dry-run.log`. One message, to the orchestrator, naming two live rows: `reader-proxy-astra-challenge` (final
  2026-11-16T10:58Z, row in flight since 10:44:16Z) and `replan-astra-challenge-1114` (final 2026-11-15T17:17Z, row in flight
  since 2026-11-14T22:52:16Z), the same two as round 1. No live row is held in review by the release gate today, so F1's
  wider rule names nothing more on the live backlog now. The decider gets nothing extra.
- Full diffs: `staged-changes.diff` (staged files against the live ones and the pre-item test backups), `fix-round-1.diff`
  (round 1 only).
- Selected VE tests, once on commit f431c325f4: `selected-run-fix1.log`: rc 0, 0 failed; lake build and `lean/audit.py` pass (no Lean changed).

## 3. Choices made inside the scope (recorded, not asked)

1. "In-flight stamp" is the latest launch the row has: its backlog.sh in-flight write (`status_t` when `status_cli` is
   `in-flight`; for a row from before `status_cli`, when its status is) and its run start as backlog.py `row_run_t` reads it.
   backlog.py stays the one owner of the run start and of `CLOSED`; the script loads them from it. A row with neither stamp
   (backlog.sh set it ready or blocked and no run started) is not named: it has no in-flight stamp to be newer than.
   Round 1 replaces round 0's choice ("only status in-flight rows"), which review F1 showed wrong: the release gate moves a
   challenge row to review when its final lands and keeps `status_t` and `status_cli`, and seeder and feed launches have no
   `status_t` at all.
2. "Not done" is "not closed" (backlog.py `CLOSED`). A blocked or ready row with a run start older than the final is named
   once; the message asks to close it or move it to blocked with the reason, and the once-only key stops repeats.
3. If backlog.py cannot be loaded, `status_t` is the only stamp and `CF_CLOSED_FALLBACK` is used; a test pins it to
   backlog.py `CLOSED` (test_19, test_20).
4. Addressees are limited to dri and orchestrator. A row `addressee` of `lead` (or anything else) falls back to the default
   rule. This script never messages the lead (test_4).
5. A final that no row claims, or whose suffix after a row id is not a date, is silent. No row is guessed (test_6).
6. Only top-level `$M/*-challenge*.final.md` files are scanned (the spec's glob). Review note F5: `-rechallenge`, `-chal` and
   fact-check finals are not matched; widening the glob is a spec change, left as a follow-up (`fix-round-1.md` section 5).
7. Errors in the new part print one line and give an empty list. They never stop the decider, p1 or no-task alerts of the
   same pass. State files are read by one reader (`state_lines`) that never raises: a line not in the state form (no tab,
   empty id, not UTF-8, a p1 time that is not a number) is skipped and named on one line (DRI note item 1).
8. The message is marked `NOW(critical): `. Unmarked mail to the orchestrator waits for its hourly digest (msg.sh header), so
   without the mark the message could not arrive within the 30 minutes the ruling sets.

## 4. Seeded bugs (Python only; `seeded-bugs.json`, runner `run_seeds.py`)

Each seed is a temp copy of the staged script (S20 and S21: of the test file) with one find/replace, run as
`DRA_SCRIPT=<copy> python3 -I <test copy>`. The staged files were never edited (the runner checks their sha256 before and
after). All 21 seeds were caught:

| Seed | Bug | Failing tests (first ones) |
|---|---|---|
| S1 | wait is 29 min, not 30 | test_1 |
| S2 | no once-only dedup | test_1, test_7, test_8, test_9, test_11 |
| S3 | Astra challenge goes to dri | test_1, test_3, test_10, test_11, test_14, test_17 |
| S4 | final older than the in-flight stamp counts | test_6, test_7, test_16 |
| S5 | closed rows count (round 0's S5 recorded F1's required behaviour as a bug and is replaced) | test_5, test_6, test_20 |
| S6 | failed send to one addressee still records it | test_8 |
| S7 | any suffix after a row id claims a final | test_6 |
| S8 | `dri-` prefix not stripped | test_2, test_3, test_5, test_13 |
| S9 | F1: the run start is not a stamp | test_12 to test_16 |
| S10 | F1: the earliest stamp wins | test_16 |
| S11 | F1: `status_t` counts whatever status backlog.sh wrote | test_6 |
| S12 | F1: a `dri-<x>` row is not its own delegate | test_12 |
| S13 | F1: only status in-flight rows count (round 0's rule) | test_11, test_12, test_15, test_16, test_20 |
| S14 | DRI note: a non-UTF-8 state line stops the pass | Install.test_installed_under_live_name_with_live_state_file |
| S15 | DRI note: skipped state lines are not named | Install.test_installed_under_live_name_with_live_state_file |
| S16 | the `CLOSED` fallback drifts from backlog.py | test_19 |
| S17 | F4: "astra" matched in the row id only | test_17 |
| S18 | F4: "astra" matched in the file name only | test_17 |
| S19 | F4: a row two links claim is named twice | test_18 |
| S20 | F2: the picker ignores mtimes | Install.test_staged_newer_copy_only_then_live_after_install |
| S21 | F2: the picker uses a fixed tag list (round 0's rule) | Install.test_staged_newer_copy_only_then_live_after_install |

No Lean, Rust or Python product code of this VE repo changed, so no seed applies there.

## 5. Install (decider; INSTALL WAITS FOR DECIDER READ)

```
cd /home/seyran/code/manage-agents/tools-local
cp -p decider-ready-alert.py decider-ready-alert.py.bak-20261117-challew
mv decider-ready-alert.py.new-challew decider-ready-alert.py
mv decider-ready-alert.py.new-nta decider-ready-alert.py.bak-20261117-nta-stale
```

Check before the mv (sha256 of the staged file this report describes): `e7fa412c1a4a…` (full value in `fix-round-1.md`).
No restart: `backlog-svc.sh` line 14 runs `python3 -I $M/tools-local/decider-ready-alert.py` as a new process on every pass.
The test files `tools-local/test_decider_ready_alert.py` and `test_p1_ready_alert.py` are already in place (no service runs
them); backups `*.bak-20261117-challew` (before the item) and `test_decider_ready_alert.py.bak-20261117-challew-r1` (round 1).
After the install both suites test the live script: `staged()` picks a `.new-<tag>` copy only while it is newer than the live
file, and the last line moves the stale `.new-nta` aside as well. This was run as a dry install, not in the live directory:
`python3 -I docs/infra/challenge-final-delivery/dry_install.py` copies the files to a temp directory, runs these four lines
there, and runs both suites, once with `DRA_SCRIPT=<installed path>` -> `run-dry-install.log`.
The first pass after the install sends one message to the orchestrator about the two rows in section 2. To skip it, close
those rows first if they are already answered.

## Notes for the DRI

- The 21:39Z install read: see `fix-round-1.md` section 3. The ValueError was my half-applied edit of `.new-challew`, not the
  state file. The DRI note's three fix items are done anyway (sections 2, 3 item 7 and 5).
- `delegate-cw.py` without arguments cannot find this session: `VE_STEP` is `infra-item:...`, not `dri-delegate:...`.
  Round 0 MEASURED: `0.34M CW, raw context 2.49M, 40 calls`, then `0.44M CW (ledger weights), raw context 3.60M, 51 calls`.
- Pre-existing red on main (`manage-agents/main-known-red.txt`): none of those tests was touched here.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relayed Lean answer is touched.
2. Every deliverable built: PASS. The spec table in section 1 maps each part to a test. The diff adds no Python copy of a Lean decision and no permanent report test; the run start and `CLOSED` are read from backlog.py, their one owner.
3. Tests can fail: PASS. `run-before.log` (20 new tests fail on the installed script), `run-failing-first-round1.log` (11 fail on the round-0 build), `probes.log` and `seeded-bugs.json` (21 of 21 seeds caught).
4. Py/Lean/Rust agree: N.A., no checker code changed.
5. R8 binding: N.A., no Lean answer is read.
6. Gate evidence matches final HEAD: PASS by process. The chain runs the gate on the committed HEAD; the selected run is in `fix-round-1.md` section 4.
7. No unsigned item: PASS. No DELTA row and no trust growth.
8. DELTA: N.A., no user-visible VE output changed.
9. Test selection: PASS. The branch changes only `docs/infra/challenge-final-delivery/*`.
10. Lean statements: N.A., no Lean.
11. Budgets and deadlines fail closed: PASS. Time comes from the injected `DRA_NOW` clock with no sleeps. The boundary is tested at 29 and 30 min (test_1).
12. CPU and memory: N.A. It adds one glob over `$M` per 10-min pass (about 30 files today) and one stat per named row.
13. Test-removed trailer: N.A., no test removed or renamed (test_6's review and blocked rows now carry `status_cli` and stay silent; the review/blocked rows WITH a stamp moved to test_11 and test_15).
14. Both directions and cited evidence: PASS. Alerts in test_1-5, 7, 10-18, 20; silence in test_6, test_16's first step and the 29-min and stale-final steps of test_1 and test_7.
15. No overclaim and no silent cut: PASS. Every universal word in this report is tied to a test. Nothing was cut; F5 is a recorded follow-up. Each new check has a seed (section 4).
