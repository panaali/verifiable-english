# digest-main-line: each digest opens with main week vs the pace line (INSTALL READ)

Status: STAGED, INSTALL WAITS FOR DECIDER READ (nothing installed). Live inbox-wait.sh md5 at staging: 5254ae5e8426bd04ecd5891c590f170c (md5.txt).
HEAD: the last commit on infra/digest-main-line (this REPORT and its evidence; no VE product code changed).
Changed (outside this repo, staged only): inbox-wait.sh.new-dml (zsh -n clean), new tools-local/test_digest_main_line.py.
Open items: none. No DELTA rows: no Lean or trust-base change, and no VE product code changed.
DRI signature needed: none. The install read goes to the decider (`msg.sh dri`).

SIZE: 41 product (inbox-wait.sh +41/-3), 187 tests, about 160 other hand-written lines (this REPORT, seeded-run.py).

## What it does

Every digest the waiter hands over (the hourly one, the keepalive one and the one sent with a wake) now opens with one line, printed
directly above the digest-take text, and only when there is a digest to hand over:

    main week 50% (usage-watch.log 12:14Z) vs line 59.1% (PICK_MAIN_PACE via pick-claude-account.sh pace_line()) gap -9.1 pt

(the live reading at 12:14Z 11-17, from a dry call of the header function on the live files; at 05:24Z the line was 56.6, the "~57"
the orchestrator quoted).

- **W** is the last `main` line of usage-watch.log. The path comes from `PICK_USAGE_LOG` as in the picker (an existing env var, so no
  new one). Rows are read with the picker's own row rule from `live()`/`week_rise()`: `<HH:MMZ> main 5h=.. week=<n>` with n >= 0, in
  the last 400 kB of the log. The time printed is that line's own HH:MMZ.
- **L** is the picker's own `pace_line()` (PICK_MAIN_PACE), called with the picker's clock (`endgame.now()`). The function is not
  copied or written again: the header takes `def pace_line():` out of pick-claude-account.sh at run time, checks with `ast` that the
  extract is exactly one `def pace_line`, and runs it. The header names this source.
- **Either value unreadable**: `main week ? (<reason>)` (missing or unreadable log, no main line, no PICK_MAIN_PACE line, picker
  without pace_line). If the header takes over 30 s or its python fails, it prints `main week ? (header failed: no reading within 30 s)`.
  In every case the digest is still sent, and the text below the header is byte-identical to the old waiter's.
- No new loop, flag, service, state file or env var.

Why reuse works this way: no importable or callable function returns "main's last week %" or "the line now". The picker's parse
and `pace_line()` sit inside an inline `python3 -c` string in pick-claude-account.sh. burndown.py's `account_table()` renders a
markdown table (3-h window, with an ACCOUNTS.md fallback) and has no line. The NOW.md accounts table has no pace line. So L runs
the picker's own function source. The W parse is two lines that follow the picker's row filter field for field. The one difference
is that it keeps the log's first line when the file is under 400 kB: the picker drops `[1:]` even when it did not seek, which would
hide a lone main line.

## Tests (tools-local/test_digest_main_line.py, failing-first)

Everything runs in a scratch M, with the waiter's `M=` rewritten as in test_coord_diet.py's InboxWait. It uses live copies of
coord_diet.py, endgame.py and pick-claude-account.sh (its PICK_MAIN_PACE path rewritten to a fixture) and fixed clocks (CD_NOW,
ENDGAME_NOW).

| task test | test ids |
|---|---|
| (1) header with W, L, gap and both sources | test_1_header_has_week_line_gap_and_sources, test_2b_line_follows_the_picker_clock |
| (2) gap sign for W > L and W < L | test_2_gap_sign_above_and_below_the_line |
| (3) missing usage-watch.log: "main week ?" and the rest unchanged | test_3_missing_log_question_line_and_digest_unchanged; also 3b (no PICK_MAIN_PACE), 3c (picker without pace_line), 3d (log without a main line), 3e (header deadline expired, injected) |
| (4) body byte-identical below the header | test_4_body_byte_identical_below_header_{keepalive,hourly,wake}; opposite direction: test_4b_no_digest_no_header |

- Staged: `IW_SCRIPT=$M/inbox-wait.sh.new-dml python3 -I tools-local/test_digest_main_line.py`: 12 tests OK, rc=0 (run-staged.log).
- Live (failing-first): `python3 -I tools-local/test_digest_main_line.py`: 11 of 12 FAIL, rc=1 (run-live.log). The one that passes,
  test_4b, checks that the output does not change when there is no digest, so it passes on both waiters by design.
- Regression: `IW_SCRIPT=$M/inbox-wait.sh.new-dml python3 -I tools-local/test_coord_diet.py`: 29 tests OK in 100.9 s (its 5 InboxWait
  tests drive the staged waiter; run-coord-diet-staged.log).
- Selected run of this branch (once, on commit 00a158a77c): exit=0, 232 units recorded, 0 failed (selected-run.log).
- After install, the test's defaults switch over: IW = the installed inbox-wait.sh, and DML_OLD = inbox-wait.sh.bak-20261117-dml.
  The test refuses to compare against an "old" waiter that already carries the header.

## Seeded bugs (zsh + Python embedded in zsh; file /home/seyran/code/manage-agents/inbox-wait.sh.new-dml)

`python3 -I docs/infra/digest-main-line/seeded-run.py` makes each mutant in a /tmp copy and runs the one named test with IW_SCRIPT
pointing at it. Output is in seeded-run.log and seeded-bugs.json. All 7 are CAUGHT; the staged file was never edited (md5.txt).

| id | mutation | failing test |
|---|---|---|
| S1-gap-sign-flipped | gap L-W | test_2_gap_sign_above_and_below_the_line |
| S2-header-below-digest | header after the digest text | test_4_body_byte_identical_below_header_keepalive |
| S3-header-without-digest | header with no digest | test_4b_no_digest_no_header |
| S4-missing-log-reads-zero | missing log read as W=0 | test_3_missing_log_question_line_and_digest_unchanged |
| S5-first-main-line-not-last | first main line, not the last | test_1_header_has_week_line_gap_and_sources |
| S6-line-real-clock-not-picker-clock | wall clock, not endgame.now() | test_2b_line_follows_the_picker_clock |
| S7-expired-header-drops-line | no "?" line on expiry | test_3e_header_deadline_expired_still_sends_digest |

## INSTALL (waits for the decider's read)

    cd /home/seyran/code/manage-agents
    md5sum inbox-wait.sh            # must still be 5254ae5e8426bd04ecd5891c590f170c; otherwise re-stage
    cp -p inbox-wait.sh inbox-wait.sh.bak-20261117-dml
    mv inbox-wait.sh.new-dml inbox-wait.sh
    zsh -n inbox-wait.sh && python3 -I tools-local/test_digest_main_line.py && python3 -I tools-local/test_coord_diet.py

How the running waiter picks it up: the orchestrator starts `zsh inbox-wait.sh` fresh on every re-arm. It exits on each wake, digest
or keepalive, which is at most 50 min. A waiter that is already running keeps the file it opened: `mv` swaps the directory entry,
not the inode zsh is reading, and the waiter keeps no state between runs other than the inbox files. So no restart is needed: the
header starts with the next launch, at the orchestrator's next re-arm. Use `mv`, never `cp` over inbox-wait.sh: a `cp` rewrites the
inode a running zsh is still reading.

## Spec re-read

- Header text `main week <W>% (usage-watch.log <UTC of the line read>) vs line <L>% (<source>) gap <W-L:+.1f> pt`, checked against the
  task's TASK paragraph: exact, with W as the integer the log carries, L to 1 decimal, and source `PICK_MAIN_PACE via
  pick-claude-account.sh pace_line()`.
- "When either value cannot be read: main week ? (reason) and still send the digest": test_3, 3b, 3c, 3d, 3e.
- "No new loop, flag, service or state file": the diff (inbox-wait.diff) adds two shell functions and one string, and no file is written.

## Notes for the DRI

- The header goes right above the digest-take text in all three hand-over paths (hourly, keepalive, with a wake), not above the
  "== digest due" / "== keepalive" / wake-message lines. That way the waiter's output minus that one line is exactly the old
  output. A keepalive with nothing pending prints no header.
- The HH:MMZ is the log line's own time (the log carries no date). A stale log shows as an old time; the header adds no freshness
  rule of its own.
- Taking `pace_line()` out of the picker's text depends on the picker keeping `def pace_line():` at column 0 inside its python
  string. If that changes, the header shows `main week ? (pace line unreadable: ...)` (test_3c) and does not guess.
- No trust_mutants sweep and no light-lane check: no VE product code changed in this repo.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no Lean answer is relayed.
2. Every deliverable built, no rule broken: PASS. Staged file, test file, install read and final are all present; tests (1) to (4) map to the table above (run-staged.log).
3. Tests can fail: PASS. Live run fails 11 of 12 (run-live.log); 7 seeded bugs are CAUGHT (seeded-run.log).
4. Python, Lean and Rust agree: N.A., no cross-language checker.
5. R8 binding: N.A., no relayed binding.
6. Gate evidence matches the final HEAD: PASS for this item's evidence (md5.txt pins the staged files). The full gate is run by the chain on the final HEAD.
7. No unsigned item: PASS. No DELTA row is needed (no Lean or trust-base change), and none is reserved.
8. Every user-visible change in DELTA: N.A., this is an operations-tool change outside VE (the task says "No DELTA rows").
9. Test selection: PASS. Only docs/infra/digest-main-line/ changed in this repo; the selected run (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, ran on ve-cloud-2) exit=0: 232 units, 0 failed, 2665 s (selected-run.log).
10. Lean statements: N.A., no Lean.
11. Deadlines fail closed: PASS. The 30 s header cap gives a "?" line and still sends the digest, with expiry injected by a shim and no sleep: test_3e_header_deadline_expired_still_sends_digest.
12. No CPU or memory regression: PASS. One python3 call per digest hand-over, 0.070 s on the live files (header-timing.txt), reading at most 400 kB; the staged run takes 10.6 s for 12 waiter runs (run-staged.log).
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. Header vs no header (test_4 vs test_4b), value vs "?" (test_1 vs test_3*), and W above vs below L (test_2); spec re-read is above.
15. No overclaim, no silent cut, new checks can fail, limits charged first: PASS. The "byte-identical" claim is backed by test_4_* on three paths and test_3; nothing is cut; S1 to S7 above; the log read is capped at 400 kB before parsing.
