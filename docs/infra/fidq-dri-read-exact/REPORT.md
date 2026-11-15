# fidq-dri-read-exact: a fidquote DRI read applies only when its fault files and the floor test files are byte-identical

- Status: built and staged; the decider installed both scripts (see "Install"). No DELTA rows, no DRI signature reserved,
  trust +0 (infra scripts in `manage-agents`, no VE product code, no Lean).
- Row: fidq-dri-read-exact (infra, critical path p2). Decision `reviews/dri-decisions-20261115-adv1035.md` item 1; ruling
  ADV-1 (`inbox/dri/done/20261115T103930Z-orchestrator-61674.md`); advisor `reviews/advisor/20261115T1035Z.md`.
- This VE branch holds only this report. All the work is in `/home/seyran/code/manage-agents`, which is not a git repository.

SIZE: 37 product (fidquote-gate.py +23/-1, merge-train.sh +14), 132 tests (test-dri-read.zsh 66, dri_read_driver.py 28,
test-fdre.zsh 38) plus a 3-line change to `test-harness/fidquote/run.sh`, 1 other hand-written file (this report).

## The change

| # | Deliverable | Where | Test |
|---|---|---|---|
| 1 | Failing test first: a commit after the read's commit edits a floor test file and leaves the fault lines byte-equal | `test-harness/fidquote/test-dri-read.zsh` cases `flooredit` (edits `tests/test_pf_fidelity_fix.py`) and `sfedit` (edits another FLOOR file) | the old gate FAILS 4 of 9 cases, the new gate passes 9 of 9 (runs below) |
| 2 | No regression: a candidate that differs from the named commit only outside the fault files and floor files still gets the read | same harness, cases `merge` (the branch merged onto a newer main) and `outside`, `faultfile-ok` | `ok` on both gates |
| 3 | `dri_read`: the named commit must still be an ancestor, AND `git diff --quiet <named> <candidate> -- <fault files + FLOOR files>` must succeed. A fault line whose file cannot be parsed (text before the first `:`/`::`, no `..` part) voids the whole read | `fidquote-gate.py.new-fdre`: `READ_FILE`, `read_files()`, `dri_read()` (lines 395-431) | cases `faultfile`, `unparsed`, `notanc`; `python3 -m py_compile` ok |
| 3 | `test-harness/fidquote` still passes on the copy | `test-harness/fidquote/run.sh` | 14 of 14 cases as expected |
| 4 | Archive at merge, never delete: `fidq-dri-reads/<label>.txt` -> `archive/fidq-dri-reads/<label>.txt.merged-<HHMMZ>` (a name already taken gets `-2`, `-3`, ...), logged with the merge commit; on both publish paths (single train and the `MQ_BATCH` member `qbmember_done`) | `merge-train.sh.new-fdre`: `fqarchive()` (line 887) and its two calls (lines 1414, 1541) | `PS_NEW=1 PS_NEW_SFX=.new-fdre zsh test-harness/ps1014/harness/test-fdre.zsh`: 8 passed, 0 failed; `zsh -n` ok |

Design choices (I took the conservative option each time and did not ask):
- The file set is the union of the read's fault files and every FLOOR test file. The FLOOR files are always included, even
  when no fault line names them.
- `git --literal-pathspecs diff --quiet --no-ext-diff --no-textconv` is used, so no pathspec magic, external diff or textconv
  can make different bytes compare equal.
- A read with no fault lines, a bad `decision:` file, a `branch:` that is not 40 hex digits, or a file part containing `..`
  returns nothing, so the gate fails closed.
- The PASS line names the number of byte-identical files ("3 files byte-identical there and here"), so a log reader can see
  that the exact-files rule applied.

## Test runs (2026-11-15; read = `fdre/openai-preparedness-facts-repair.txt`, the DRI's read of VE d97a090ad1)

`zsh test-harness/fidquote/test-dri-read.zsh <gate file>`. PASS means the read was applied.

Old code (the installed gate before fdre, `fidquote-gate.py.bak-20261115-fdre`): exit 1, **5 of 9 as expected (4 failed)**.
```
CASE flooredit: FAILED (expected FAIL, gate PASS; ... DRI read: 7 fault(s) accepted ... (branch d97a090ad161))
CASE sfedit: FAILED (expected FAIL, gate PASS; ...)
CASE faultfile: FAILED (expected FAIL, gate PASS; ... 1 fault(s) accepted by fdre-faultfile.txt ...)
CASE unparsed: FAILED (expected FAIL, gate PASS; ... 8 fault(s) accepted by fdre-unparsed.txt ...)
same, merge, outside, faultfile-ok, notanc: ok
```
New code (`fidquote-gate.py.new-fdre`): exit 0, **9 of 9 as expected (0 failed)**.
```
CASE same: ok (expected PASS, gate PASS; ... (branch d97a090ad161; 3 files byte-identical there and here))
CASE flooredit: ok (expected FAIL, gate FAIL; ... first fault: tests/test_pf_fidelity_fix.py:209: ...)
CASE sfedit: ok (expected FAIL, gate FAIL)     CASE merge: ok (expected PASS, gate PASS)
CASE outside: ok (expected PASS, gate PASS)    CASE faultfile: ok (expected FAIL, gate FAIL)
CASE faultfile-ok: ok (expected PASS, gate PASS; 4 files byte-identical)
CASE unparsed: ok (expected FAIL, gate FAIL)   CASE notanc: ok (expected FAIL, gate FAIL)
```
Harnesses on the staged copies:
- `zsh test-harness/fidquote/run.sh merge-train.sh.new-fdre`: `RESULT: 14 of 14 cases as expected (0 failed)`.
- `PS_NEW=1 PS_NEW_SFX=.new-fdre zsh test-harness/ps1014/harness/test-fdre.zsh`: `== merge-train fdre: 8 passed, 0 failed`.

## Seeded bugs (each planted in a copy, run against the test that should catch it, then removed)

| # | Language / file | Seeded bug | Catching test | Result |
|---|---|---|---|---|
| S1 | infra script, `fidquote-gate.py.new-fdre` `read_files` | FLOOR files dropped from the compared set (`files = set()`) | `test-dri-read.zsh` case `sfedit` | FAILED (gate PASS), 0 of 1 |
| S2 | same, `read_files` | a line with no parsable file is skipped (`continue`) instead of voiding the read | case `unparsed` | FAILED (gate PASS), 0 of 1 |
| S3 | same, `dri_read` | the diff compares the named commit with itself (`br, br`), not with the candidate | case `flooredit` | FAILED (gate PASS), 0 of 1 |
| S4a | infra script, `merge-train.sh.new-fdre` line 1541 (single-train publish) | the `fqarchive` call disabled (`: fqarchive`) | `test-fdre.zsh` P1 / P2 checks | 5 passed, 3 failed |
| S4b | same, line 1414 (`qbmember_done`, batched publish) | the `fqarchive` call disabled | `test-fdre.zsh` B1 | 7 passed, 1 failed (after the harness fix below) |

No VE product code changed in this branch (Python, Lean and Rust: none), so the review-ready [mutants] check has nothing to
seed in the VE tree. The seeds above cover the infra scripts that did change.

Harness fix found by S4b: B1 used to grep for the bare word `fqarchive` in `qbmember_done`, so a disabled call (`: fqarchive`)
still matched, and S4b survived (8 passed). B1 now requires a call statement (`^[ \t]+fqarchive([ \t;#]|$)`). After the fix
S4b fails B1 and the clean staged copy still passes 8 of 8. The harness before the fix is kept at
`/tmp/fdre-seeds/test-fdre.zsh.orig` for this session only.

## Install

As the task required, I installed nothing myself. I sent one message:
`zsh msg.sh dri fidq-dri-read-exact "NOW(critical): install read: fidquote-gate.py.new-fdre merge-train.sh.new-fdre, exact-files DRI read + archive at merge"`
(`inbox/dri/done/20261115T113339Z-fidq-dri-read-exact-852688.md`, 11:33Z).

**Already installed by the decider** at 11:36:17Z (that is the ctime of `fidquote-gate.py`, `merge-train.sh` and both
`.bak-20261115-fdre` backups). Each installed file is byte-identical to its staged copy (`cmp` clean):
`fidquote-gate.py` sha256 `ac904c00233525bb...` = `.new-fdre`; `merge-train.sh` sha256 `68244abb0731cccf...` = `.new-fdre`.
Backups: `fidquote-gate.py.bak-20261115-fdre` (`fc38d8f3d9a489d1...`), `merge-train.sh.bak-20261115-fdre`
(`d155029dfb868e94...`).

The install commands as specified, which match what was done; the same pattern, reversed, rolls it back:
```
cd /home/seyran/code/manage-agents
# no train mid-step on merge-train.sh: no running merge-train process, and nobody holds the merge lock
pgrep -af 'merge-train.sh'                                # must print nothing
flock -n merge-train.lock true && echo lock-free          # must print lock-free
cp -p fidquote-gate.py fidquote-gate.py.bak-20261115-fdre && cmp fidquote-gate.py fidquote-gate.py.bak-20261115-fdre
cp -p merge-train.sh  merge-train.sh.bak-20261115-fdre  && cmp merge-train.sh  merge-train.sh.bak-20261115-fdre
python3 -m py_compile fidquote-gate.py.new-fdre && zsh -n merge-train.sh.new-fdre
sha256sum fidquote-gate.py.new-fdre merge-train.sh.new-fdre   # expect ac904c00233525bb..., 68244abb0731cccf...
cp -p fidquote-gate.py.new-fdre fidquote-gate.py.tmp && mv fidquote-gate.py.tmp fidquote-gate.py
cp -p merge-train.sh.new-fdre  merge-train.sh.tmp  && mv merge-train.sh.tmp  merge-train.sh
```
`mv` replaces the file atomically. A zsh that already has `merge-train.sh` open keeps reading the old inode, so a train that
is mid-step finishes on the old script. That is why the check that no train is running comes before the `mv`.

## Notes for the DRI

1. Ruling ADV-1 ("no new fidq DRI reads until this merges") can be lifted now that the gate is installed. A read written
   from now on is accepted only for a candidate whose fault files and FLOOR test files equal the named commit byte for byte;
   any other candidate needs a fresh read.
2. The current read `fidq-dri-reads/openai-preparedness-facts-repair.txt` is now checked under the exact-files rule. A fix
   round on that item that touches `tests/test_pf_fidelity_fix.py` or another FLOOR file will need a fresh read.
3. Earlier rounds ended without a commit on this VE branch, so the pre-review gate failed [commits] (0 ahead). This report
   is that commit.

Digest: fidq-dri-read-exact: fidquote DRI reads now apply only when the fault files and FLOOR test files are byte-identical
to the read's commit (old gate 5/9, new 9/9; fidquote harness 14/14; merge-train archives each read at merge, 8/8);
installed by the decider at 11:36Z.

## Self-review against BUILDER-CHECKLIST

All 12 items concern VE product code (relays, Lean, schema binding, evidence tests, hang guards, DELTA, trust). This branch
changes no VE product code, only this report, so every item is N.A.; the infra changes are covered by the harness runs and
seeds above.
- 1-12: N.A. (no VE product, test, Lean, Rust or generated file changed; `git diff --stat main...HEAD` = this report only).
