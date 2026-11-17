# challenge-final-delivery: a finished challenge final reaches its row's addressee within 30 min

- Status: built and staged as `manage-agents/tools-local/decider-ready-alert.py.new-challew`. INSTALL WAITS FOR DECIDER READ
  (install-read message: `manage-agents/inbox/dri/20261117T211701Z-challenge-final-delivery-build-2888443.md`). Install steps: section 5.
- What changed: the existing periodic check (`decider-ready-alert.py`, run by `backlog-svc.sh` after each seed, no new loop) now
  also names any `*-challenge*.final.md` that is newer than its in-flight row's `status_t` when the row is still in flight 30 min
  later. It sends one `NOW(critical)` message to the row's addressee (orchestrator for Astra challenges, else dri), once.
- Open items: none. No DRI signature is reserved and there are no DELTA rows (control-plane tooling only; no Lean, VE trusted
  line or verdict rule changed; trust +0). This VE branch holds only this report and its evidence.

SIZE: 104 product (+93 -11 in the staged script, 30 of them docstring), 164 tests (+160 -4), about 150 other hand-written lines (this report).

## 1. Spec (row note, ruling `reviews/dri-ruling-record-void-astra-20261115.md` section F) and where each part is delivered

| Spec words | Delivered by | Test |
|---|---|---|
| "a *-challenge*.final.md" | `CF_GLOB = "*-challenge*.final.md"` over `$M` (where delegates write finals); empty files skipped | test_6_silent_cases (`build-x.final.md`, empty final) |
| "newer than its row's in-flight stamp" | stamp = `status_t` of a row whose status is `in-flight`; final mtime must be later | test_6 (`late-challenge`, `nostamp-challenge`), test_7 |
| "whose row is not done" | only rows still `in-flight` count (done/merged/dropped, and ready/blocked/review, are silent: section 3, choice 1) | test_6 |
| "after 30 min" | `CF_AFTER = 30 * 60` from the final's mtime; 29 min silent, 30 min named | test_1 |
| "msg to the row's addressee (orchestrator for Astra challenges)" | row `addressee` field (dri or orchestrator) wins; else orchestrator when "astra" is a word of the row id or file name; else dri, as one more part of the one dri message | test_1, test_2, test_3, test_4 |
| "once" | state `decider-ready-alert.sent`, key `cf:<id>` + `<final>@<status_t>`; a row sent in flight again whose new final lands alerts again | test_1, test_7 |
| "same periodic check as decider-ready-alert" / "no new loop" | code added to `decider-ready-alert.py`; `backlog-svc.sh` unchanged (line 14 already runs it after each seed) | Loop.test_backlog_svc_runs_alert_after_seed |
| failed send | a failed send records nothing for that addressee; the next pass retries; the other addressee's send is recorded | test_8, test_9 |
| "the existing cases stay green" | all 24 existing tests pass on the staged script; `test_p1_ready_alert.py` passes on it | `run-staged.log`, `run-p1-staged.log` |

How a final finds its row (`final_rows`): `links.final` is the file name, or `links.delegate` is its stem, or the stem (with or
without `dri-`) is a row id, alone or followed by `-<date>` / `-stopped-<date>` (`record-void-astra-challenge-1115` ->
`record-void-astra-challenge`). Every open, in-flight row a final belongs to is named: a delegate row the seeder closed
(`dri-X`, done) does not close the challenge row `X` (test_5_row_mapping). A final no row claims is not named (test_6, `orphan-astra-challenge-1115`).

## 2. Evidence (commands and output files in this directory)

- Failing first, on the installed script (the 2026-11-17 13:45Z notask-wait-alert install, identical to `.new-nta`):
  `DRA_SCRIPT=$PWD/tools-local/decider-ready-alert.py python3 -I tools-local/test_decider_ready_alert.py` -> `run-before.log`:
  `Ran 35 tests`, `FAILED (failures=7, errors=2)`. The 9 failing tests are all new ChallengeFinal tests (test_1, 2, 3, 4, 5, 7,
  8, 9, 10). The existing 24 pass. test_6 (silent cases) and test_fin_is_the_final_time also pass on the installed script, as
  they should: it sends nothing.
- On the staged script: `python3 -I tools-local/test_decider_ready_alert.py` (picks `.new-challew` first) -> `run-staged.log`: `Ran 35 tests`, `OK`.
- p1 suite on the staged script: `P1RUA_ALERT=$PWD/tools-local/decider-ready-alert.py.new-challew python3 -I tools-local/test_p1_ready_alert.py` -> `run-p1-staged.log`: `OK`.
- `python3 -m py_compile` on the staged file: clean.
- Live dry run (reads the live backlog, records nothing): `python3 -I tools-local/decider-ready-alert.py.new-challew --dry-run`
  -> `live-dry-run.log`. It holds one message, to the orchestrator, naming two live rows: `reader-proxy-astra-challenge` (final
  2026-11-16T10:58Z, row in flight since 10:44:16Z) and `replan-astra-challenge-1114` (final 2026-11-15T17:17Z, row in flight
  since 2026-11-14T22:52:16Z). These are real hits: both rows are still `in-flight` 34 h and 52 h after their finals. The
  decider gets nothing extra.
- Full diff of the staged script and the test file: `staged-changes.diff`.

## 3. Choices made inside the scope (the conservative or narrower option, recorded, not asked)

1. "In-flight stamp" is read as the `status_t` of a row whose status is `in-flight`. A ready, blocked or review row has no
   in-flight stamp and is not named. An in-flight row with no `status_t` is also not named. Only 20 in-flight rows carry a
   `status_t` today. The rows without one were set by the seeder, which closes them itself when their delegate final lands.
2. Addressees are limited to dri and orchestrator. A row `addressee` of `lead` (or anything else) falls back to the default rule.
   This script never messages the lead (test_4).
3. A final that no row claims, or whose suffix after a row id is not a date, is silent. No row is guessed (test_6).
4. Only top-level `$M/*-challenge*.final.md` files are scanned. Delegates write their finals there. Files in `reviews/` are
   reviews, not delegate finals.
5. Errors in the new part print one line and give an empty list. They never stop the decider, p1 or no-task alerts of the
   same pass. The tests assert that no such line ("skipped") appears.
6. The message is marked `NOW(critical): `. Unmarked mail to the orchestrator waits for its hourly digest (msg.sh header), so
   without the mark the message could not arrive within the 30 minutes the ruling sets.

## 4. Seeded bugs (Python only; `seeded-bugs.json`)

Each seed was a temp copy of the staged script with one find/replace, run with
`DRA_SCRIPT=<copy> python3 -I tools-local/test_decider_ready_alert.py`. The staged file was never edited: its sha256 was the
same before and after the seed runs (`sha256sum -c`: OK). All 8 seeds were caught:

| Seed | Bug | Failing tests |
|---|---|---|
| S1 | wait is 29 min, not 30 | test_1 |
| S2 | no once-only dedup | test_1, test_7, test_8, test_9 |
| S3 | Astra challenge goes to dri | test_1, test_3, test_8, test_9, test_10 |
| S4 | final older than the in-flight stamp counts | test_6, test_7 |
| S5 | any open status has an in-flight stamp | test_6 |
| S6 | failed send to one addressee still records it | test_8 |
| S7 | any suffix after a row id claims a final | test_6 |
| S8 | `dri-` prefix not stripped | test_2, test_3, test_5 |

No Lean, Rust or Python of this VE repo changed, so no seed applies there.

## 5. Install (decider; INSTALL WAITS FOR DECIDER READ)

```
cd /home/seyran/code/manage-agents/tools-local
cp -p decider-ready-alert.py decider-ready-alert.py.bak-20261117-challew
mv decider-ready-alert.py.new-challew decider-ready-alert.py
```

No restart: `backlog-svc.sh` line 14 runs `python3 -I $M/tools-local/decider-ready-alert.py` as a new process on every pass.
The test file `tools-local/test_decider_ready_alert.py` was edited in place, because no service runs it. Its backup is
`test_decider_ready_alert.py.bak-20261117-challew`. After the mv the test picks the live script and passes; this was not run,
since the mv waits for the read.
The first pass after the install sends one message to the orchestrator about the two rows in section 2. To skip it, close
those rows first if they are already answered.

## Notes for the DRI

- `delegate-cw.py` without arguments cannot find this session: `VE_STEP` is `infra-item:...`, not `dri-delegate:...`. I ran it
  on this session's transcript instead. MEASURED: `0.34M CW (ledger weights), raw context 2.49M, 40 calls`. The value at the end is in the final.
- Pre-existing red on main (`manage-agents/main-known-red.txt`): none of those tests was touched here.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relayed Lean answer is touched.
2. Every deliverable built: PASS. The spec table in section 1 maps each part to a test. The diff adds no Python copy of a Lean decision and no permanent report test.
3. Tests can fail: PASS. `run-before.log` (9 new tests fail on the installed script) and `seeded-bugs.json` (8 of 8 seeds caught).
4. Py/Lean/Rust agree: N.A., no checker code changed.
5. R8 binding: N.A., no Lean answer is read.
6. Gate evidence matches final HEAD: PASS by process. The chain runs the gate on the committed HEAD, and the selected run is recorded in `selected-run.log`.
7. No unsigned item: PASS. No DELTA row and no trust growth.
8. DELTA: N.A., no user-visible VE output changed.
9. Test selection: PASS. The branch changes only `docs/infra/challenge-final-delivery/*` (`selected-run.log`).
10. Lean statements: N.A., no Lean.
11. Budgets and deadlines fail closed: PASS. Time comes from the injected `DRA_NOW` clock with no sleeps. The boundary is tested at 29 and 30 min (test_1).
12. CPU and memory: N.A. It adds one glob over `$M` per 10-min pass (about 30 files today).
13. Test-removed trailer: N.A., no test removed or renamed.
14. Both directions and cited evidence: PASS. Alerts are in test_1-5, 7 and 10; silence in test_6 and the 29-min/stale-final steps of test_1 and test_7. Every claim above cites its log.
15. No overclaim and no silent cut: PASS. Every universal word in this report is tied to a test. Nothing was cut. Each new check has a seed (section 4).
