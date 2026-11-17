# tm-sc7-rejudge: forward kill in tm-nightly classify + the sc-7 re-judge (row tm-sc7-rejudge)

Builder tm-sc7-rejudge (Opus 5.5), 2026-11-17. INSTALL READ class. DELTA: none (manage-agents tooling; no Lean, no
trust-base change; no row, no signature reserved). Decision: reviews/dri-decisions-20261116-tmlk.md item 3; plan
reviews/tm-nightly-lookups-20261116.md item 6.

**Install status (checked 2026-11-17 15:55Z): INSTALLED after the decider read.** manage-agents/tm-nightly.py md5 is
7f90506fb854841d7498a3c1447fb054 (= the staged tm-nightly.py.new-fk); the backup tm-nightly.py.bak-20261117T1236Z-fk md5
is 92d8c99045cf292089778783e5c5feb1 (= the file before). After install the forward-kill suite gives `Ran 12 tests ... OK`
on the installed file (forward-kill-tests.installed.log).

VE branch: no product change. This directory holds the item's report and evidence, so the branch records the item
(docs only); the code lives in manage-agents. Evidence here: installed-changes.diff (backup -> installed),
forward-kill-tests.{live,staged,installed}.log (live = before install: 12 failing), existing-suites.log, seeds.log,
forward-kills-ledger.jsonl (the ledger row), rejudge-record-extract.json (the 5 rows of the re-judge record; the full
record stays at its ledgered path, sha256 below), rejudge-run.log.

**Result: sc-7 re-judge 5/5 KILLED.** Record test-skip/forward-kills/20261117T1208Z-sc7-rejudge.json, sha256
5f59d51f7b21d734d09db097e1d4945183cec261e2e2929743b5baa2eecfce7f, head d2573fc9a0 (main; contains 496bf9af6b, the
merge of tm-esc-sc7-wordchar). Ledgered in test-skip/forward-kills.jsonl (the file the staged classify reads; the
installed one never reads it).

## Files

| file | md5 | what |
|---|---|---|
| tm-nightly.py (installed, unchanged) | 92d8c99045cf292089778783e5c5feb1 | the base of the draft |
| tm-nightly.py.new-fk (staged; `python3 -m py_compile` clean) | 7f90506fb854841d7498a3c1447fb054 | + forward kill (`diff tm-nightly.py tm-nightly.py.new-fk`: 60 lines added, 7 replaced) |
| tools-local/test_tm_nightly_forward_kill.py (new) | 8394b3e7a51615ed0b6e195f6d2bd3b3 | 12 tests |
| test-skip/forward-kills.jsonl (new ledger, 1 row) + test-skip/forward-kills/20261117T1208Z-sc7-rejudge.{json,log} | | the re-judge record and its run log |

## PART 1: the forward kill (tm-nightly.py.new-fk)

An unallowed SURVIVOR at the nightly record's head H counts resolved (its own count `forward_killed`, never `allowed`) when
a row of test-skip/forward-kills.jsonl (`{"record", "head", "sha256"}`) names a trust_mutants record that holds its text
(file, definition, operator, before, after; never the id) as KILLED, and every one of these holds:
- the record file's sha256 is the ledger's, and the record's own `head` is the ledger's head H2 (a full 40-hex sha);
- H2 != H, H is an ancestor of H2, and H2 is an ancestor of `main` (git merge-base --is-ancestor in the classify worktree,
  a worktree of ~/code/verifiable-english: the merge train's main);
- every row of that text in the H2 record is KILLED (a text it also holds with another status resolves nothing), and the
  text is on exactly one row of the nightly record at H (two rows: which line H2 killed is not known, so nothing).
The survivor's nightly-survivors.jsonl row gets `forward_kill` {record, head, sha256, cite} and why_not_escape
"forward-kill: <record> @ <H2> (resolved)"; the nightly.jsonl row gets `forward_killed` (count) and `forward_kill` (one
entry per survivor: id, record, head, sha256, cite "forward-kill: <record> @ <H2>"). It files no tm-esc row and leaves
`unallowed_survivor`. `unresolved.SURVIVOR`, `complete` and `row_complete` (resume) subtract it. UNKNOWN rows are never
forward-killed.

Conservative choices taken (no DRI question, override 2): the sha256 and record-head checks, "all rows KILLED" at H2,
"text on one row" at H, a malformed ledger row or record is skipped (never an error, never a resolution), and a T1
escape stays an escape (its escapes.jsonl row, which the guard counts, and its tm-esc row; T1 ended 11-12, so this is
moot today).

### Tests (tools-local/test_tm_nightly_forward_kill.py)

Each refusal test also holds a control survivor that a valid record resolves in the same run, so each refusal is the
step's own decision. Commands: `TMN_PY=/tmp/tmfk/tm-nightly-fk.py nice -n 19 python3 -I -B tools-local/test_tm_nightly_forward_kill.py`
(the staged copy as .py) -> `Ran 12 tests ... OK`; the same without TMN_PY (live) -> `FAILED (failures=2, errors=10)`, all 12.

| task case | test | live | staged |
|---|---|---|---|
| (1) KILLED same text at H2 (descendant of H, ancestor of main): resolved, cited | Resolved.test_later_ancestor_of_main_kills_same_text (other id M42: ids renumber; cite, head, sha256 in nightly.jsonl and the survivor row; no tm-esc row) | FAIL | pass |
| (1) resume reads it as complete | Resolved.test_row_complete_subtracts_forward_killed | FAIL | pass |
| (2) H2 not an ancestor of main | Refused.test_h2_not_ancestor_of_main | FAIL | pass |
| (3) H2 older than H; H2 = H | Refused.test_h2_older_than_h; Refused.test_h2_equal_to_h | FAIL | pass |
| (4) same id, different text | Refused.test_same_id_other_text | FAIL | pass |
| (5) same text SURVIVOR at H2; KILLED + SURVIVOR rows | Refused.test_same_text_survived_at_h2; Refused.test_same_text_killed_and_survived_at_h2 | FAIL | pass |
| extras | Refused.test_sha256_mismatch, test_record_head_not_ledger_head, test_text_twice_at_h; Escape.test_t1_escape_stays_an_escape | FAIL | pass |

(6) the existing suites, each run with TMN_PY=staged copy and with the live file (logs /tmp/tmfk/<suite>.{staged,live}.log):
blame_prebase 3 OK, build_timeout 16 OK, complete 9 OK, escape_rows 15 OK, lookups 17 OK, split 11 OK, tests_allow 5 OK,
unknown_disposition 3 OK on both; restart_main 20 run, `FAILED (failures=1, errors=1)` on BOTH: test_pools_absent_routes_as_before
and test_remote_every_pool_refusing_no_vm_no_mac (MacPytestRemoteOnly: mac-pytest.sh tests, the 2 known pre-existing failures
named in reviews/dri-decisions-20261116-tmlk.md item 1; not this item's).

### Replay on the real record (scratch, no side effects)

`git clone --shared` of ~/code/verifiable-english at /tmp/tmfk/ve, detached at 9ccbf3fdf, `main` = d2573fc9a0; TEST_SKIP_DIR
a copy of forward-kills.jsonl, tm-esc.jsonl, t1-on, t1.jsonl; TM_NIGHTLY_NO_SIDE=1; classify of
test-skip/nightly/20261116T1607Z.json. Staged: forward_killed 5 (M798, M2490, M2762, M4698, M4970, each cited
"forward-kill: /home/seyran/code/manage-agents/test-skip/forward-kills/20261117T1208Z-sc7-rejudge.json @ d2573fc9a09365634c4f8aecc7d22130eb00b6c7"),
unresolved SURVIVOR 74. Live: unresolved SURVIVOR 79, the 5 listed unallowed. Nothing else differs (allowed 191/610 on both).
M252 (wordChar le-lt, a text on 3 rows at 9ccbf3fdf, 2 KILLED) is not forward-killed: the re-judge record does not
hold it, and its text is on more than one row at H.

## PART 2: the re-judge

The 5 sc-7 survivors at 9ccbf3fdf (item 6; record test-skip/nightly/20261116T1607Z.json): VE/Scope/Authoring.lean:26
VE.Scope.Pinned.wordChar, before `[0x115F, 0x1160, 0x2800, 0x3164, 0xFFA0]`. Their ids at main (trust_mutants `plan` at
d2573fc9a0, base 039d3dd51, classes trusted: 8719 planned; matched by full text, each text once): see the table.
Command (worktree /home/seyran/code/ve-tm-sc7-rejudge at main, clean): `zsh mac-pytest.sh --trustmut -- --base 039d3dd51...
--max-mutants 5000 --only M999,M3110,M3449,M5781,M6120 --test <the 64 paths tm-nightly.py tests gives at main, base
039d3dd51> --json /tmp/sc7rj/sc7-rejudge.json`, under wait-bg.sh. It ran on VM1 (TM_VM1_FIRST, --jobs 7, its own scope),
exit 0, 93 s: "5 KILLED, 0 SURVIVOR, 0 UNKNOWN, 0 INVALID, 0 ALLOWED, 0 NOT RUN"; lake mutant_builds 16 s (5): each was
built and judged fresh (no --resume, no --rescore; the record has no resumed_from/carried). GitHub Actions not used
(ACTIONS_FIRST absent).

| at 9ccbf3fdf | operator | after | id at main | verdict | killed by |
|---|---|---|---|---|---|
| M798 | list-empty | `[]` | M999 | KILLED | lean/VE/Scope/AuthoringExamples.lean:190 |
| M2490 | list-first | `(… .take 1)` | M3110 | KILLED | AuthoringExamples.lean:191 |
| M2762 | list-drop-last | `(… .dropLast)` | M3449 | KILLED | AuthoringExamples.lean:194 |
| M4698 | list-last | `(… .reverse.take 1)` | M5781 | KILLED | AuthoringExamples.lean:190 |
| M4970 | list-drop-first | `(… .drop 1)` | M6120 | KILLED | AuthoringExamples.lean:190 |

Record: test-skip/forward-kills/20261117T1208Z-sc7-rejudge.json, sha256 5f59d51f7b21d734d09db097e1d4945183cec261e2e2929743b5baa2eecfce7f.
The re-judge record is complete (5/5 judged) on Nov 17, before Nov 23, so ruling 1.4's "diagnostic, mutation coverage
open" wording is not needed for these 5. The 9ccbf3fdf nightly record itself stays not complete for other reasons
(replay: 2137 NOT RUN, 137 unallowed UNKNOWN, 74 other unallowed SURVIVOR); that is not this item's.

## Seeded bugs (Python; each planted in a /tmp copy of tm-nightly.py.new-fk, the 12 tests run, then the copy deleted)

| # | behaviour | mutation | failing test |
|---|---|---|---|
| 1 | H2 must be an ancestor of main | drop `or not is_ancestor(w, h2, "main")` | Refused.test_h2_not_ancestor_of_main |
| 2 | H must be an ancestor of H2 | drop `or not is_ancestor(w, head, h2)` | Refused.test_h2_older_than_h |
| 3 | H2 != H | drop `or h2 == head` | Refused.test_h2_equal_to_h |
| 4 | only an all-KILLED text resolves | `s == {"KILLED"}` -> `"KILLED" in s` | Refused.test_same_text_killed_and_survived_at_h2 |
| 5 | the ledger sha256 binds the record | drop the sha256 comparison | Refused.test_sha256_mismatch |
| 6 | resume reads forward kills as resolved | drop `- forward_killed` in row_complete | Resolved.test_row_complete_subtracts_forward_killed |
| 7 | a text on two rows at H resolves nothing | drop `n_text == 1` | Refused.test_text_twice_at_h |

Logs: /tmp/tmfk/seed-<name>.log (each `FAILED (failures=1)`). tm-nightly.py.new-fk is byte-identical to the copy the
tests passed on (`cmp` clean).

SIZE: 60 product (tm-nightly.py.new-fk, 11 of them docstring), 226 tests, 156 other hand-written lines (this report).

## INSTALL WAITS FOR DECIDER READ (done: installed 12:36Z, see Install status above)

The service (tm-nightly.sh) runs `python3 -I $M/tm-nightly.py <step>` fresh for each step (6 call sites), so no restart:
install between steps, when no `tm-nightly.py classify` is running (`pgrep -af 'tm-nightly.py classify'` empty). At
12:09Z the 20261117T0600Z run was sweeping parts (test-skip/nightly.log).

    cd /home/seyran/code/manage-agents
    md5sum tm-nightly.py tm-nightly.py.new-fk   # expect 92d8c99045cf292089778783e5c5feb1 and 7f90506fb854841d7498a3c1447fb054
    pgrep -af 'tm-nightly.py classify'          # expect nothing
    cp -p tm-nightly.py tm-nightly.py.bak-$(date -u +%Y%m%dT%H%MZ)-fk
    mv tm-nightly.py.new-fk tm-nightly.py
    nice -n 19 python3 -I -B tools-local/test_tm_nightly_forward_kill.py   # expect 12 OK

## Notes for the DRI

- After install, the next classify of a 9ccbf3fdf record resolves the 5 (replay above). The record still needs its NOT
  RUN, UNKNOWN and other 74 SURVIVORs settled before the base moves; the forward-kill row and ledger must be kept (once the
  base passes 9ccbf3fdf, the wordChar line is not planned again: item 6, second caveat).
- `light-lane.py check` printed "NOT no changes against d2573fc9" (the VE branch has no diff); the task file itself
  requires the trust_mutants record, so the run is the same either way. It was run after the sweep, not before.
- The ledger is append-only by hand; nothing writes it automatically. A row with a relative record path is read under
  test-skip/.

## Self-review against BUILDER-CHECKLIST

1. N.A. (no relayed Lean answer).
2. PASS: Part 1 (staged code + 12 tests), Part 2 (record + ledger + per-mutant table), message, install commands; each above.
3. PASS: seeded bugs 1-7, each failing one named test; all 12 tests fail on live.
4. PASS: replay of the live record, staged vs installed (only the 5 differ).
5. N.A. (no R8 binding).
6. N.A. (no VE change; HEAD = main; the chain gates it).
7. PASS: no DELTA row, no signature reserved (manage-agents tooling).
8. N.A. (no user-visible VE change).
9. N.A. (no VE file changed).
10. N.A. (no Lean).
11. N.A. (no budget or limit added).
12. N.A. (adds up to 2 git calls per ledger row per classify; one ledger row today).
13. N.A. (no test removed).
14. PASS: opposite directions (Resolved vs Refused, with a control in each refusal); each claim names its command/log.
15. PASS: no overclaim (the nightly record's own completion stated as open); no cut deliverable; every new check can fail (seeded bugs); limits N.A.
