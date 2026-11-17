# pick-main-rank1: rank-1 main rule, fix round 1 (holder pid through subshells)

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

## Install (picker read per call, no restart)

Check first that the live md5 is still `deb8c19d7a50f67e6613e0e62d8f5afc`, then:

```
cd /home/seyran/code/manage-agents
cp -p pick-claude-account.sh pick-claude-account.sh.bak-20261117-r1fix1
mv pick-claude-account.sh.new-r1 pick-claude-account.sh
```

## Notes not filed by the review (C1-C5), unchanged in this round

The review's C notes are left as they were. C3 (no test of the `cfhold` probe skipping the rule) and C2 (a mutant dropping
`w < PICK_CRIT_MAIN_WEEK` survives) are test gaps, not A or B findings.
