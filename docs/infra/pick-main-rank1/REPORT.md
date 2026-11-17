# pick-main-rank1: rank-1 main rule, fix rounds 1 (holder pid through subshells) and 2 (every session of the row holds)

## Fix round 2 (review `manage-agents/pick-main-rank1-looprecheck1.final.md`: F1 and F-ready1 FIXED, F2 (B) new)

Fix round 1 is installed now: the live picker md5 is `aa89fe5b4eda1ea93c9afed5894e71c5`, the round-1 staged script. The round-2
fix is staged as `manage-agents/pick-claude-account.sh.new-r1` (md5 `b52321d8d0fa600cdacd6fb98c96b0bd`, `zsh -n` clean,
diff `fix2-picker.diff`). It needs an install read (below). No file of this repo outside this folder changed.

### F2 (B): a second session of the same rank-1 row was not recorded in the marker

**Class:** the marker recorded one holder per rank-1 row, but a row can be on main through several sessions
(`feature-pipeline.sh:110-112` and `infra-item.sh:331,335` run two per row, plus forked subshells of one caller). The
marker's state and the row's real use of main could drift apart in three ways:
- a second session of the row was let onto main without being recorded;
- when the recorded holder exited, the marker looked stale while the row was still on main, so the next rank-1 row got main;
- the give-back (`:377`) could remove a marker that another session of the row relied on. One case: session A takes the
  marker but will not pick main, session B of the row joins, then A gives back.

**Fix:** one reader and one writer of the marker (`r1read`, `r1write`), used by both the take and the give-back, both under
the marker lock.
- The marker is `<item> <pid>[:<n>] ...` and lists every live holder of the row; `<n>` counts the grants of one holder pid
  and is written only when it is over 1.
- Every grant adds its holder (`r1holder()`) or raises its count.
- A marker is stale only when none of its pids lives. Dead pids and bad tokens are dropped on the next write.
- A live marker of another row refuses, naming all of its live pids.
- The give-back now runs under the lock and takes back only the grants this call added (`r1made` is a count now). Other
  holders and earlier grants of the same holder stay.
- The rule-head comment (`:148`) states the list.

Only the picker and its tests read the marker (`grep` over manage-agents). A marker in the old one-pid format reads as a
one-holder list.

**Probe F2** (the review's command, verbatim, with `PICK_SCRIPT=<script>`; `fix2-run-tests.log`):
- live picker (round 1): exit 1;
- staged `.new-r1`: exit 0.

**Regression tests**, in `manage-agents/tools-local/test_pick_main5h_unknown.py` (`Rank1Main`; diff `fix2-tests.diff`):
- `test_same_row_second_session_keeps_main_after_first_exits`: the probe as a test. Two live callers of the row are both
  listed; after the first exits, another rank-1 row is refused (naming the second) until the second exits.
- `test_same_row_give_back_keeps_other_session`: the give-back race, made deterministic with a fifo in the `accounts.sh`
  fixture. A (with `PICK_AVOID`) takes the marker; B of the same row joins and picks main; A gives back. B stays listed and
  other rows stay out.
- `test_same_row_same_holder_counts_grants`: one holder pid granted twice, and one grant given back. The other grant stays.
- `test_same_row_marker_live_while_any_pid_lives`: a live pid after a dead pid and a junk token still refuses another row.
  Joining drops the dead pid and the junk; an all-dead marker is cleared.

The callers that `hold()` starts read their fifos with `read -t 120`, are killed in `addCleanup` and do not inherit the
test's output. So a failing assertion leaves no process behind.

**Results:**
- Staged: 30 of 30 OK.
- Live (round 1): the four `test_same_row_*` cases fail and the 26 others pass.
- `test_same_row_same_holder_counts_grants` fails on the live picker only on the marker format: sequential picks of one
  holder never gave back there. It guards the count against the seed `F2-giveback-drops-all-grants`.

**Seeded bugs** (`seeded-bugs.json`, `fix2-run-seeded.log`): four mutants of the staged script, each caught.
- join not listed (the old behaviour);
- the give-back drops the whole marker;
- stale judged by the first pid only;
- the give-back drops every grant of the holder.

**Other picker suites, live and staged** (`fix2-run-other-suites.log`):
- Results are identical on both scripts.
- `endgame` and `pick_mgmt` failed on both under this session's environment. Their env starts from `os.environ`, and this
  session exports `PICK_AVOID=main`, which holds main out. With the session's `PICK_*` unset, both pass on both scripts.
  This is an isolation gap in those tests, not in the picker, and it is not a finding of this review.
- `role_budget test_listed_item_goes_unlisted_waits` fails on both scripts, as in round 1 and the build round: pre-existing.
- Every other suite is OK.

**Repo checks:**
- No VE code changed in round 2.
- DELTA: none, so there are no Ruling cells.
- The selected run (`mac-pytest.sh --select`), `lake build` and `python3 lean/audit.py` are recorded below.
- `[gate]` is left to the merge train (R17).

### Install round 2 (picker read per call, no restart)

Check first that the live md5 is still `aa89fe5b4eda1ea93c9afed5894e71c5`. The test file is already updated in place; until
the install, its four `test_same_row_*` cases fail on the live picker.

```
cd /home/seyran/code/manage-agents
cp -p pick-claude-account.sh pick-claude-account.sh.bak-20261117-r1fix2
mv pick-claude-account.sh.new-r1 pick-claude-account.sh
```

Any live marker `pick-main-rank1` in the old one-pid format stays valid; it reads as a one-holder list.

## Fix round 1

Row pick-main-rank1; decision `reviews/dri-decisions-20261116-rsp-presync.md` item 6; review
`manage-agents/pick-main-rank1-review.final.md` (FIX: F1 (B), F-ready1 (B)). All product changes are in
`/home/seyran/code/manage-agents` (the account picker), outside this repository. This folder is the record of the fix round.
No file of this repo outside this folder changed: no Lean, Python, Rust, generated file or DELTA row.

## State found at the start of the round

The build round's staged `pick-claude-account.sh.new-r1` had already been installed as the live picker (backup
`pick-claude-account.sh.bak-20261117-r1`, live md5 `deb8c19d7a50f67e6613e0e62d8f5afc`). So F1 is live now. The fix is
staged again under the same name, `pick-claude-account.sh.new-r1` (md5 `aa89fe5b4eda1ea93c9afed5894e71c5`, `zsh -n`
clean). The row's task says INSTALL READ, so it was not moved over the live script.

## F1 (B): the holder pid named a forked subshell

**Class:** the holder pid recorded for the one-holder marker named a process that exits as soon as the pick returns. A
caller that picks inside a command substitution or a `( ... )` subshell makes the picker's `$PPID` a forked subshell:

- `run-codex.sh:138,160`: `acct=$(rcx_pick ...)`, with `rcx_pick` a function;
- `feature-pipeline.sh:144-145`, `converge.sh:44,49` and `action-assurance-leanrun.sh:11`: `$(until zsh pick...; done)`,
  in converge.sh inside `( ... ) &`.

So the marker named a dead pid, and the next rank-1 row cleared it as stale.

**Fix:** the fix is one function in the picker, so it covers every caller and no caller edits are needed. `r1holder()`
walks up from `$PPID` while the parent has the same `/proc/<pid>/cmdline`, because a forked subshell keeps the argv of the
shell it forked from. With no `/proc`, the result is `$PPID`, as before. Two places use the result: taking the marker
(`r1hold`) and giving it back. Before the fix the give-back compared with raw `PICK_R1_PID`; it now compares with
`r1holder()`, so both sides name the same holder. The walk stops at the first parent with a different argv. Taking a
parent whose argv happens to be the same only makes the holder live longer, which errs on the strict side for "one holder".
The comments at the `r1pid` line and at the rule head no longer say the holder is "the pid of the picker caller".

**Probe F1** (the review's command, unchanged, against `.new-r1`):
- before the fix (the installed script, copied to `.new-r1`): exit 1;
- after the fix: exit 0.

**Regression tests**, in `manage-agents/tools-local/test_pick_main5h_unknown.py` (`Rank1Main`; diff `fix1-tests.diff`).
Each case runs a zsh caller script in one of the sweep's shapes:
- `test_holder_is_the_caller_through_a_function_in_command_substitution` (the run-codex shape, i.e. the probe). The marker
  names the caller's `$$`; a second rank-1 row is refused while the caller lives and granted after it exits.
- `test_holder_is_the_caller_through_until_in_a_background_subshell` (the converge, feature-pipeline and
  action-assurance-leanrun shape).
- `test_holder_marker_given_back_through_a_subshell`: when main is admitted but held out, the marker is given back through
  a subshell.

**Results** (`fix1-run-tests.log`, `fix1-run-other-suites.log`):
- Staged: 26 of 26 OK.
- Installed (pre-fix): the two `test_holder_is_the_caller_*` cases fail. The give-back case passes there, because the old
  take and the old give-back used the same raw pid; it guards the fix's own change.
- Other picker suites, live and staged, each run with `PICK_SCRIPT`: identical results.
  - All OK: `ccloud_main88`, `endgame`, `pick_crit_fallback`, `pick_critical`, `pick_longroom`, `pick_main_rank`,
    `pick_mgmt`, `pick_prefer`, `pick_released_yield`, `pick_tell`, `pick_why`.
  - `role_budget` fails `test_listed_item_goes_unlisted_waits` on both scripts. This failure predates the row, and the
    build round reported it.

**Seeded bugs** (`seeded-bugs.json`, `fix1-run-seeded.log`): three mutants, each caught.
- No walk (the old behaviour).
- Give-back compares with the raw pid.
- The walk ignores the cmdline.

## F-ready1 (B): 0 commits ahead of the merge base

The product is outside this repository, so the build round committed nothing here. This folder (report, diffs, run logs,
seeded bugs) is now committed on `infra/pick-main-rank1`, following `docs/infra/tm-plan-failfast` and
`docs/infra/p1-ready-unstartable-alert`. Rerun of `review-ready.py` at 252004ef:
- `[commits]`, `[clean]`, `[mutants]`, `[relay]` and `[delta]`: PASS (`1 commits ahead of the merge base b00f97f5`).
- `[gate]`: FAIL, because no full gate was run. The task leaves the full gate to the merge train. The selected run of this
  round passed: GitHub Actions run `pick-main-rank1-252004ef-t878961`, 2 shards, 10 units, exit 0.
- `lake build` and `python3 lean/audit.py` pass; no Lean changed.

Install read sent: `manage-agents/inbox/dri/20261117T013930Z-pick-main-rank1-3202893.md`.

## Install round 1 (done: the live md5 is the round-1 staged script)

Check first that the live md5 is still `deb8c19d7a50f67e6613e0e62d8f5afc`, then:

```
cd /home/seyran/code/manage-agents
cp -p pick-claude-account.sh pick-claude-account.sh.bak-20261117-r1fix1
mv pick-claude-account.sh.new-r1 pick-claude-account.sh
```

## Notes not filed by the review (C1-C5), unchanged in this round

The review's C notes are left as they were. C3 (no test of the `cfhold` probe skipping the rule) and C2 (a mutant dropping
`w < PICK_CRIT_MAIN_WEEK` survives) are test gaps, not A or B findings.
