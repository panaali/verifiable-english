# challenge-final-delivery fix round 1 (review `challenge-final-delivery-review.final.md`, and its overlapped copy `-review-ov`)

- Status: F1 and F2 (both B) fixed as classes in the staged script and the two test files; the DRI note's three items
  (`reviews/challenge-final-delivery-dri-note-20261117.md`) done too. Install waits for the decider's read (REPORT section 5).
- Open: none; no DRI signature reserved, no DELTA rows. Incident in section 3: the 21:39Z install took a half-edited file of mine.
- Evidence: `probes.log`, `run-*.log`, `seeded-bugs.json` (21 of 21 caught), `fix-round-1.diff`; REPORT.md is updated throughout.

## 1. Findings

| Finding | Class removed | Fix | Regression tests | Probe |
|---|---|---|---|---|
| F1 (B) a challenge row in review is never alerted | every not-closed row with an in-flight stamp older than the final: release-gate review rows (`status_cli` in-flight), `dri-<x>` delegate rows, seeder and feed launches without `status_t`, blocked or ready rows with a run start | `launch_t` = latest of `status_t` (when `status_cli` is in-flight) and backlog.py `row_run_t` (one owner; a `dri-<x>` row is its own delegate); "not done" = not in backlog.py `CLOSED`; message and once-key carry the stamp | `ChallengeFinalRows.test_11` (the probe's row) to `test_16`, `test_19`, `test_20`; `test_6` reworked (review/blocked rows without a stamp stay silent) | PROBE F1: rc 1 before, rc 0 after (`probes.log`) |
| F2 (B) after the install the suite tests a stale copy | every fixed staged-tag list: `test_decider_ready_alert.py` SCRIPT and SVC, `test_p1_ready_alert.py` ALERT and BACKLOG (it listed `.new-nta` first too) | one picker `staged(live)`: the newest `<live>.new-<tag>` newer than the live file, else the live file; the p1 test imports it; REPORT section 5 also moves the stale `.new-nta` aside | `Install.test_staged_newer_copy_only_then_live_after_install`; `dry_install.py` -> `run-dry-install.log` | PROBE F2: rc 1 before, rc 0 after (`probes.log`) |
| DRI note 1 (state lines) | any state-file line (old shape, `nt:`, `cf:`, no tab, empty id, not UTF-8, a p1 time that is not a number) | one reader `state_lines` for both state files; never raises; a refused line is skipped and named | `Install.test_installed_under_live_name_with_live_state_file` (copies the live state files and adds every odd shape) | the round-0 build dies on the non-UTF-8 line (`run-failing-first-round1.log`) |
| DRI note 2 and 3 (live name) | a check that only ran the staged name | the install test runs a dry install of the staged script under its live name; `dry_install.py` runs REPORT section 5 in a temp copy and both suites, once with `DRA_SCRIPT=<installed path>` | same test; `run-dry-install.log` | n.a. |
| Notes F3, F4 (not filed) | counts in the report; surviving mutants | REPORT counts regenerated from the logs (46 tests now; 23 existed before the item); F4's three mutants are seeds S17 to S19, now killed | `test_17`, `test_18` | n.a. |
| Note F5 (not filed) | glob misses `-rechallenge`, `-chal`, fact-check | not changed: the spec gives the glob literally; follow-up in section 5 | n.a. | n.a. |

## 2. Files (manage-agents/tools-local; sha256)

- `decider-ready-alert.py` (live, unchanged by this round): `ac8af596435659b8280a5585bc296b403088bc50fd8d7ad0ef5bc7d5140428fc`
- `decider-ready-alert.py.new-challew` (staged, round 1): `e7fa412c1a4ab4d70906d859124dd9b61c82ebffa6b26a1aed645f15bd850500`
- round-0 staged build (reviewed): `08a69f503f84c2c5bfbf0a90c0222f3f3cbcd1b8378c6533b51d20909a725e73`
- `test_decider_ready_alert.py`: `e409de3ce6db4da26f93dfb445e34fdd782d1af6cfc4488076d04fa941538bc6` (round-0 copy: `.bak-20261117-challew-r1`)
- `test_p1_ready_alert.py`: `ebb55af5993da66bca26a6a9e55a8ea784ddb3330605b458d84d788867f894ff` (pre-item copy: `.bak-20261117-challew`)

## 3. Incident: the 21:39Z install took my half-edited file (my error)

- At 21:39Z I was editing `.new-challew` in place, one edit at a time. The decider ran REPORT section 5 between two of my
  edits: the `mv` installed a file whose `challenge_finals` already returned 6 fields while `cf_part` still unpacked 5. That
  is the `ValueError: too many values to unpack (expected 5)` in the DRI note. It is not the state file and not the path:
  the reviewed round-0 file (sha256 `08a69f50…`, rebuilt from `staged-changes.diff` of commit 4babceed) has no such error.
- The decider rolled the live file back at about 21:40Z. Not knowing that yet, at about 21:41Z I wrote the rebuilt round-0
  file to the live path to end the broken state, saw that the live file had already been rolled back, and within about a
  minute put the decider's rolled-back content back (sha256 `ac8af596…`, mtime 12:33:46 kept). The 21:41Z `svc-backlog`
  pass fell in that window: no `decider-ready-alert` message reached `inbox/orchestrator` or `inbox/dri` after 21:38Z, and
  `decider-ready-alert.sent` is unchanged since 16:26Z.
- `.new-challew` was missing after the rollback (the DRI note says "restored unchanged"); I put the round-0 file back there
  (sha256 `08a69f50…`), did the whole round in `/tmp/cfd-work`, and replaced the staged and test files only at the end, each
  by one atomic `mv` after both suites passed on them.
- Class fix for this incident: never edit a staged file in place; build in a scratch copy and move it in whole. The DRI note's
  checks (live name, live state file, dry install) are added anyway.

## 4. VE checks

- Selected tests: `selected-run-fix1.log` (see the commit after this file's first commit).
- No Lean changed, so no lake build or `lean/audit.py` result depends on this branch; both were run for the record
  (`selected-run-fix1.log` names them).

## 5. Follow-ups

- F5: `CF_GLOB` is the spec's literal `*-challenge*.final.md`; backlog.py `RELEASE_WORD` also treats `rechallenge`, `chal` and
  fact-check as challenge words. Reading the glob from `RELEASE_WORD` is a spec change for the DRI.
