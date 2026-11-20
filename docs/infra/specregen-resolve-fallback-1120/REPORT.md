# specregen-resolve-fallback-1120: the spec regen resolves generated-only conflicts

Status: BUILT; INSTALLED by the acting DRI after the install read (CURRENT-STATE 2026-11-20 21:18Z; backup merge-train.sh.bak-specregen-20261120T2117Z, sha256 e939d94a). Installed merge-train.sh sha256 = ba6957a8 = the staged script. Before the read the builder installed nothing (DRI 2026-11-10).
Staged: merge-train.sh.new-specregen (sha256 ba6957a800af14d0; zsh -n OK). The installed merge-train.sh is unchanged (sha256 e939d94ab371b749, the same at the start and at the end).
What changed: when specregen's plain `git merge` of a candidate stops ONLY on merge=ve-generated files, it now runs the main sync's own regen_merge (`tools/regen_generated.py --resolve`) instead of skipping. It keeps the result only if it is exactly branch + candidate with nothing left unmerged. Any other conflict, or a --resolve that does not finish, gives the same skip as before.
Open items: none. No DELTA row, nothing reserved for the DRI. No VE repo change: the VE branch has no commits beyond main 663be16252.
Challenger (Opus 5.5, one session): VERDICT FINDINGS, 0 A, 4 B, 2 C. The four B findings were fixed once, failing-first. The two C findings were answered (F5 in the replay, F6 with tests or a note).

SIZE: 39 product (added lines in merge-train.sh.new-specregen; 14 removed), 434 tests (tools-local/test_merge_train_specregen.py), 85 other hand-written lines (replay.zsh 60, seed.py 25) plus this report.

## The change (diff.txt, 93 lines of unified diff)

- `specregen` (merge-train.sh.new-specregen, the block after "merging the candidate"):
  - A clean merge: unchanged.
  - The merge stops and `allgen` is false (some unmerged path is not merge=ve-generated): unchanged, with the same abort, the same reason text and the same log line.
  - The merge stops and `allgen` is true: one log line `spec-regen resolve for <label>: ...`. It deliberately does not start with "spec regen of <label>", because stop-train.sh regenbase reads that prefix as the regen's start. Then `regen_merge $wt "spec regen"`. Files the resolve left untracked (not ignored) are removed, as brclosure does; the worktree's own untracked files stay.
  - The result is kept only if regen_merge returned 0, `HEAD^1 == h`, `HEAD^2 == c`, there is no `HEAD^3`, no `MERGE_HEAD` and `ls-files -u` is empty. Otherwise the regen is skipped with its reason, and the existing end-of-function restore (`merge --abort; reset --hard; checkout -f <branch>`) and the `HEAD == h` check apply.
- `regen_merge <wt> [<caller>]`:
  - With no caller (the main sync, syncbranch; presync-lean-regen's library mode), every command and log line is exactly as before.
  - With a caller ("spec regen"):
    - every log line is tagged " (spec regen)", and the decline ends "spec regen skipped, no agent sync";
    - amerge (the allowances resolve) is not run, because allgen already excludes an ALLOWANCES.md conflict;
    - both --resolve steps run under `timeout ${CAND_REGEN_LEAN_TIMEOUT:-2700}`;
    - the Lean pre-build runs in the train's own scope rather than an `iso.sh integ-regen-*` scope.

Conservative choices (taken without asking, per the builder overrides):
- Refuse a resolved commit that is not exactly h + c, even though regen_merge exited 0.
- A timeout counts as a decline.
- No allowances resolve inside a spec regen.
- No flag file: the path only fires on a generated-only conflict, and every other path is byte-identical (tests b, e, f, g).

## Tests (step 2): tools-local/test_merge_train_specregen.py, test-output.txt

Command: `MT_SPECREGEN_SRC=<script> python3 -I tools-local/test_merge_train_specregen.py`. It uses throwaway git repos: a gen/report.json with merge=ve-generated and no driver installed, and a fake regen_generated.py that follows the real tool's exit contract. The functions are cut from the script and run under `zsh -f`. Nothing live is touched: the test asserts that the cut functions name no live path.

| test | .new-specregen | installed |
|---|---|---|
| (a) generated-only conflict -> resolved; spec = h + c with the regenerated file; specuse fast-forwards (the item stays in the stack) | ok | **FAIL** (rc 1, "conflicts outside the generated files") |
| (b) source conflict -> unchanged skip line, --resolve never runs | ok | ok |
| (c) --resolve exits 2 -> skip, branch restored, no commit object with parents (h, c) anywhere | ok | ok |
| (d) --resolve exits 0 but aborted the merge and staged its own tree -> the single-parent commit is refused | ok | ok |
| (e) clean merge -> spec as before, no resolve | ok | ok |
| (f) main sync regen_merge decline: same line, iso.sh scope, no timeout | ok | ok |
| (g) main sync regen_merge success: same line, iso.sh scope, amerge still tried, no timeout | ok | ok |
| (h) F2: untracked leftovers removed on decline and on success; the worktree's own untracked file kept | ok | FAIL (tests the new path) |
| (i) F1: timeout exit 124 -> skip, no commit | ok | FAIL (tests the new path) |
| (j) F6b: the stale-ve_service retry inside a spec regen keeps parents h, c; its lines are tagged | ok | FAIL (tests the new path) |

test-output.txt: .new-specregen "Ran 10 tests ... OK" exit=0; installed "FAILED (failures=4)" exit=1, with failures (a), (h), (i), (j). The task's own requirement holds: (a) fails on the installed script and passes on .new-specregen, and (b) and (c) pass on both.

Main sync in library mode: tools-local/test_allowances_shared.py sources merge-train.sh with MT_LIB and calls regen_merge with one argument. It gives 18/18 OK with LWAS_SFX=.new-specregen and 18/18 OK on the installed script (allowances-test-output.txt).

## Replay (step 3): replay.zsh, replay.txt (first version), replay-final.txt (final script)

The case is merge-train.log line 28823 (11-20 05:06Z): "spec regen of fsf-repair-f1-leveldefs-1119 skipped (the merge of ef7ecd59 conflicts outside the generated files)", on branch 2767a772. The agent sync later made f02219f5, which is 228142ff + ef7ecd59; 228142ff = 2767a772 + 9c9da90f, and 9c9da90f is an ancestor of ef7ecd59.

Setup:
- A scratch worktree ~/code/ve-specregen-replay-1120 (removed afterwards; never ve-integration) on 2767a772, plus an overlay commit of main 663be16252's regen_generated.py, .gitattributes and route_fixtures.py, as in the genconflict-1120 replay. Lean was restored with lean-prep.
- `specregen` and `specuse` were cut from .new-specregen. branchregen and cregen_probe are stubs: they are unchanged code, and this replay tests the merge step.
- It ran in its own iso.sh scope (specregen-replay-1120).

replay-final.txt (2026-11-20T20:51Z, script ba6957a8):
- `specregen rc=0 in 955 s`. The merge stopped on exactly the four files (lexicon-report.json, route-cases.jsonl, safety-framework coverage.json and results.json).
- spec parents = branch + ef7ecd59.
- lexicon-report.json, route-cases.jsonl, coverage.json, results.json and spans.json are each **byte-equal to the agent sync f02219f5**.
- specuse fast-forwarded the branch; the worktree was left with 0 dirty files and no MERGE_HEAD.
- The first version gave the same result in 1117 s (replay.txt).
- The only other differing path is tests/history-dependent.json (challenger F5). It is merge=ve-generated. The agent's tree has H0's copy (empty diff H0..agent), and the resolve regenerated it for the overlaid regen_generated.py's new git calls (`_merge_file`, `changed_on_both_sides`). That is a side effect of the replay's overlay; the genconflict-1120 REPORT records the same thing. Lines are in replay-final.txt.

Time (MEASURED in the replay; the cost on a live train is an ESTIMATE):
- In the replay, about 16-19 min of resolve runs while the candidate gates (about 35 min per gate). On success the item stacks instead of waiting for the candidate to publish and then taking an agent sync.
- The genconflict-1120 REPORT measured 171 min of sibling waits after 05:00Z on 11-20 from this skip. It is the upper bound this change can recover; nothing here measures it on a live train.
- The 113 "spec regen ... skipped (... conflicts outside the generated files)" lines in merge-train.log (grep -c, 21:08Z) are the population. Only the generated-only ones change.

## Challenger (step 4): challenge-prompt.txt, challenge-out.md

One fresh Opus 5.5 session (claude-opus-5-5, account from `PICK_AVOID=main pick-claude-account.sh`, 20:40Z-20:43Z, rc 0, read-only tools). VERDICT FINDINGS, no class A. Its answers to the three questions: Q1 no wrong tree through commit or specuse; Q2 no hidden conflict beyond what the main sync already accepts; Q3 identical for trains without a generated-only conflict.

| finding | answer | test (failing-first: failing-first.txt, on .new-specregen v1) |
|---|---|---|
| F1 [B] the new --resolve has no timeout, and the train waits on it synchronously | fixed: `timeout ${CAND_REGEN_LEAN_TIMEOUT:-2700}` on both steps; expiry = decline | (i), (a) |
| F2 [B] untracked files from --resolve stay in the worktree | fixed: snapshot before, remove new untracked after regen_merge | (h) |
| F3 [B] the iso.sh pre-build scope outlives a train stop and writes after the restore | fixed: in spec mode, the build runs in the train's own scope (as cregen_run already does), so stop-train's scope stop covers it | (a), (j) assert no iso.sh |
| F4 [B] success/progress lines untagged (counted as main-sync resolves) | fixed: every regen_merge line carries " (spec regen)" in spec mode; main sync byte-identical | (a), (d), (j); (f), (g) for the main sync |
| F5 [C] history-dependent.json differs in the replay | explained above (overlay artifact, ve-generated) | replay-final.txt |
| F6 [C] test gaps | (a) -> (h); (b) handshake -> (j); (c) amerge in spec mode -> now skipped, and (a)/(g) assert it; (e) a stop-train test mid-resolve: not added, F3 removes the separate scope; (f) -> (g). (d) "--resolve exits 0 and changes a non-conflicted source" is NOT guarded, see Notes | |

Failing-first: failing-first.txt shows that, on v1 before the fix, (a), (h) (both modes), (i) and (j) FAILED, while (b)-(g) passed. After the fix all 10 pass (test-output.txt).

## Seeded bugs: seed.py, seeded-bugs.txt

All of these are in merge-train.sh.new-specregen (zsh; the only product language changed). Each was applied to a scratch copy /tmp/mt-seed.sh, never to the staged file (its sha256 is unchanged, as seeded-bugs.txt shows).

| # | bug | failing test |
|---|---|---|
| M1 | no allgen gate (every conflict goes to --resolve) | test_b |
| M2 | no parents/unfinished check after --resolve exit 0 | test_d |
| M3 | specregen calls regen_merge without its caller | test_c (plus a, d, i, j) |
| M4 | the main sync's decline line tagged too | test_f |
| M5 | the old skip kept on a generated-only conflict | test_a (plus h, j) |
| M6 | no timeout | test_i, test_a |
| M7 | no untracked cleanup | test_h |
| M8 | iso.sh scope kept in spec mode | test_a, test_j |
| M9 | amerge still run in spec mode | test_a |
| M10 | success line untagged | test_a, test_d |

All 10 CAUGHT. An earlier M2 that disabled only one of the five OR'd conditions was not caught, because the HEAD^2 check still refused the commit; it was rewritten to disable the whole check.

## Pre-review gate fix (2026-11-20)

[commits] FAILED (0 commits ahead of 663be162). Fix: committed the saved record docs/infra/specregen-resolve-fallback-1120/ on
infra/specregen-resolve-fallback-1120, as earlier infra items did (actions-mismatch-scope-1120, backlog-unlaunchable-ready-1120):
this REPORT, diff.txt, the test file (test_merge_train_specregen.py.txt), test-output.txt, failing-first.txt, test-after-install.txt,
allowances-test-output.txt, replay.txt, replay-final.txt, replay.zsh.txt, challenge-prompt.txt, challenge-out.md, seed.py.txt,
seeded-bugs.txt, sha256.txt. Documentation only; no VE product code, no generated file, no DELTA row.
After the DRI's install: `zsh -n merge-train.sh` OK; test_merge_train_specregen.py 10/10 OK; test_allowances_shared.py 18/18 OK
(test-after-install.txt, installed sha256 ba6957a8).
Selected tests on the record commit ff6923ee70 (mac-pytest.sh --select): exit 0, 267 units, 0 failed (ve-cloud-2, 1373 s).

## Notes for the DRI

- F6(d) is not guarded: a `--resolve` that exits 0 having also changed a non-conflicted, non-generated file would give h + c parents and pass the check. The main sync has the same trust in --resolve today. The candidate's full R2 gate runs on S afterwards, and the tool's writers write GENERATED files only. A path-set check (every path where S differs from the pre-resolve stage-0 index must be merge=ve-generated) would close it; it is not filed (override 3: not a verdict defect).
- presync-watch-job.sh keeps its own copy of regen_merge ("KEEP IN STEP"). It was not changed: it is the main-sync presync, not the spec regen.
- The replay stubs branchregen and cregen_probe; the live path runs them after the resolve exactly as after a clean merge (unchanged code).
- measure.py-style counts: spec-regen declines now read "generated-file resolve (spec regen) declined in ...", so a `'resolve declined in ve-'` match does not count them as agent syncs.
- No FOLLOW-UP lines.

## Install commands (given for the decider read; applied by the acting DRI, 21:18Z)

Commands (after the read):
```
systemctl --user list-units --type=scope | grep merge-train          # must print nothing (no train running)
cd /home/seyran/code/manage-agents
cp merge-train.sh merge-train.sh.bak-specregen-$(date -u +%Y%m%dT%H%MZ)
mv merge-train.sh.new-specregen merge-train.sh
zsh -n merge-train.sh && python3 -I tools-local/test_merge_train_specregen.py && LWAS_SFX=.none python3 -I tools-local/test_allowances_shared.py
```
(After the mv, the test defaults to merge-train.sh, so all 10 must pass.)

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relayed Lean answer; control-plane zsh only).
2. Every deliverable built, no rule broken: PASS. The steps map to these deliverables: 1 diff.txt; 2 test file + test-output.txt; 3 replay.txt + replay-final.txt; 4 challenge-out.md + fixes; 5 install-read message + commands above; 6 CURRENT-STATE line. Nothing was installed and the installed sha256 is unchanged.
3. Tests and gates can fail: PASS. seeded-bugs.txt (10/10 CAUGHT); failing-first.txt; test_a FAILS on the installed script.
4. Python/Lean/Rust agree: N.A. (no checker path).
5. R8 binding: N.A.
6. Gate evidence matches final HEAD: PASS by process. The VE HEAD has no change; the chain gates it. The evidence files name the script sha256 (ba6957a8) they ran on.
7. No unsigned item: PASS (no DELTA row, nothing reserved).
8. DELTA: N.A. (no user-visible VE change).
9. Test selection: N.A. for VE (no VE diff). The new test lives in tools-local beside the other train tests.
10. Lean statements: N.A.
11. Budgets fail closed: PASS. The new --resolve runs under a timeout and expiry is a decline (test_i). The test uses no sleep: the timeout is a stub that exits 124.
12. CPU/memory: PASS. The new path runs only on a generated-only conflict and replaces a later agent sync. The Lean pre-build now runs in the train's scope, as cregen_run does. Measured 955 s in the replay.
13. Test-removed trailers: N.A. (no test removed).
14. Both directions, cited evidence, spec re-read: PASS.
    - Accept: (a), (e), (j). Refuse: (b), (c), (d), (i). Keep the main sync: (f), (g), allowances 18/18.
    - Spec re-read: "conflicts ONLY on files tools/regen_generated.py lists as GENERATED" against `.gitattributes` (generated from GENERATED; the four files are lines 62-65) and `allgen`. "--resolve exit != 0 keeps today's behaviour exactly" against test_c + test_i. "never commit a tree --resolve did not finish" against test_d.
15. Overclaim / silent cut / new check can fail / limits: PASS.
    - "unchanged" claims are backed by (b), (e), (f), (g) and the allowances test.
    - No deliverable was cut.
    - Every new check has a mutant (M1-M10).
    - The timeout is charged before the work starts (test_i).

CW MEASURED: see the final message.
