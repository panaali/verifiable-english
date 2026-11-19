INSTALL WAITS FOR DECIDER READ

# tm-cache-asset-pick: keep the cache asset the trust-mutant nightly's pinned head restores from (staged as lean-cache-publish.sh.new-tmcache)

Row tm-cache-asset-pick (guard trust-mutant-nightly; reviews/dri-decisions-20261117-tm-shard-actions-120.md item 3; task:
prompts/task-tm-cache-asset-pick.txt). This is an infra item in the PLACEMENT class (install read). The fix is staged as
`/home/seyran/code/manage-agents/lean-cache-publish.sh.new-tmcache` (`zsh -n` clean). The live file has not been replaced.
`cloud-dispatch.sh` is unchanged: no `.new` is staged for it. The tests are in
`/home/seyran/code/manage-agents/tools-local/test_tm_cache_asset_pick.py`. No VE product code was changed and there are no
DELTA rows: this branch carries only this evidence directory.

## Choice: (b), the publisher's keep set; not (a)
- **(a) cannot fix the measured case.** All 5 kept assets are *descendants* of the nightly head 9ccbf3fdf; none is an ancestor
  (`replay.txt`, the `merge-base --is-ancestor` lines). `lean-near.py` finds no ancestor asset with no K limit either:
  "no asset within 100000 lean trees (328 lean-tree changes in 615 main commits, none with a kept asset)" (`replay.txt`).
  So no pick rule over today's manifest can reach an asset of that head or of its ancestors.
- **The dispatcher already prefers the nearest ancestor.** Its pick order is exact tree, then base tree, then lean-near.py's
  nearest main ancestor within K=4, then main == base, then the newest. The nightly fell to "newest" because the publisher
  had deleted the head's asset. `lean-build-4acf8387e957` was uploaded 2026-11-12 05:26Z and deleted 2026-11-13 05:35Z by
  keep 5 (`replay.txt`, from logs/lean-cache-publish.log). The nightly kept resuming that head after the delete.
- **(b) as built.** On every run, `lean-cache-publish.sh` first finds the head the nightly resumes:
  - It takes the newest `test-skip/nightly/<stamp>.json` and runs `tm-nightly.py resume <repo> <that record's base>`. This is
    the nightly's own rule (not complete, under 4 days old, head in the repo, not on the no-resume list).
  - It then finds that head's asset: `lean-near.py <repo> <head> <this platform's manifest> <quarantine> --k 4 --base <base>`.
    This is the same call `cloud-dispatch.sh` makes for that nightly's parts, which run with `sha` = head and `--base` = the
    nightly base.
  - That asset (the pin) is kept beside the newest KEEP. The release prune skips it, and manifest.json keeps its row and url
    past the 6-row cut. The local pack is pruned as before; the dispatcher pins by url.
  - KEEP is unchanged (5). The pin adds **one more** asset only when it is older than the newest 5, which is the case (b)
    needs. When it is already among them, the kept count stays the same (test (2), "among the newest 5").
- **No pin, so behaviour as today**, when any of these holds: there is no record; the record is complete, old or on the
  no-resume list; the head has no asset within K; the asset is quarantined; or any step fails (every failure returns with
  `pin=""`).

## Tests (tools-local/test_tm_cache_asset_pick.py; failing first)
The script under test runs on a synthetic repo, a private test-skip dir (`TEST_SKIP_DIR`), a private cache dir and an
in-process fake releases API on 127.0.0.1. Afterwards the test runs **the live cloud-dispatch.sh's own pick** on the
manifest that is left. It reads the heredoc from the file and runs it with lean-near.py, using the nightly's head and base.
- `python3 -I tools-local/test_tm_cache_asset_pick.py` (live): **FAILED: 16** (`run-live.log`). The live script deletes the
  head's asset, and the dispatcher then pins the newest (main's).
- `LCP=…/lean-cache-publish.sh.new-tmcache python3 -I tools-local/test_tm_cache_asset_pick.py`: **PASS: 0 failed, 26 ok**
  (`run-staged.log`).
- The cases:
  - **(1) Failing first.** The head's asset is the oldest of 6. Two forms are tested: the exact tree (n=0), and the nearest main
    ancestor within K (n=2, where the head's own tree has no asset). In both, the asset is kept on the release and in
    manifest.json with its url, and the dispatcher pins it. On the next main move, it is still kept and the oldest other
    asset is deleted.
  - **(2) No related asset gives today's behaviour.** The staged script must give the same exit, deletes, manifest names,
    dispatcher pick and kept count as the live script, and must pin nothing. Cases: every asset newer than the head (the
    measured shape); no record; a complete record; a record over 4 days old; a head on the no-resume list; the head's asset
    quarantined; and the head's asset already among the newest 5 (same deletes, 5 kept).
  - **(3) aarch64 `--pack`.** The arm asset is kept from manifest-aarch64.json. No x86 asset is deleted, and manifest.json is
    not written.
- **Existing harnesses on the staged file** (`harness-regression.txt`; temporary harness copies pointed at the `.new`):
  - test-armcache.zsh: 37 passed, 0 failed on both live and staged.
  - test-cloudplumb.zsh: 187 passed, 8 failed on both, with the same 8 FAIL lines. All 8 are cloud-overflow.sh pool-order
    cases that already fail on the live scripts; none is in its lean-cache-publish.sh section.
  - cloud-dispatch.sh has no `.new`, so its tests were not rerun. Case (1) runs its live pick.

## Seeded bugs (seed_run.py; seeds.log, seeded-bugs.json): 6 of 6 caught
Each seed was planted in a temporary copy of the staged file
`/home/seyran/code/manage-agents/lean-cache-publish.sh.new-tmcache` (shell, zsh with embedded Python):
- B1, the release prune ignores the pin: 14 tests fail.
- B2, the manifest's 6-row cut drops the pin: 4 fail ("(1) exact tree, next main: … still kept …").
- B3, the resume check is skipped: 3 fail ("(2) record complete …").
- B4, the quarantine is ignored: 1 fails ("(2) the head's asset quarantined …").
- B5, the platform suffix is ignored: 2 fail ("(3) --pack …").
- B6, only the exact tree is used (no near walk from the base): 7 fail ("(1) nearest ancestor within K …").

## Cost
The staged `pinof()` adds three steps on the real 2.97 MB record (`pin-cost.txt`, `/usr/bin/time`): 0.09 s, 0.13 s and
0.08 s, under 30 MB each. It runs once per publish run.

## Install (decider)
```
cd /home/seyran/code/manage-agents
md5sum lean-cache-publish.sh lean-cache-publish.sh.new-tmcache
#   e03c9a09748e9273c7eb014f0dbc2cbc  lean-cache-publish.sh            (live, unchanged since 2026-10-30)
#   4c8a3d9d39d7c0a04c6f1527e72065fd  lean-cache-publish.sh.new-tmcache
cp -p lean-cache-publish.sh lean-cache-publish.sh.bak-20261119tmcache
mv lean-cache-publish.sh.new-tmcache lean-cache-publish.sh
python3 -I tools-local/test_tm_cache_asset_pick.py     # expect: PASS: 0 failed
```
(sha256 of every file involved: `sha256.txt`; the diff, +32/−4: `staged-changes.diff`.)

## What the install does and does not do for the current record (a real seam, not a size cut)
- The nightly's current record (20261117T0600Z, head 9ccbf3fdf) **still has no asset after the install**. Its asset was
  deleted on Nov 13, and the staged script logs "the nightly's head 9ccbf3fdf … has no asset within 4 lean trees … none kept
  for it" (`replay.txt`). The fix keeps a pinned head's asset **from the next pin on**: a head whose asset still exists when
  the nightly first pins it, which is the normal case, because the nightly starts at main's tip and that asset is the newest.
- An asset for 9ccbf3fdf can come only from a Lean build of tree 4acf8387e957. That is a one-off operation: build, then an
  upload to the public release. It is outward-facing and outside this staged change, so it is listed for the decider under
  Notes. It is not done here.

SIZE: 32 product, 279 tests, 54 other hand-written lines (product: staged diff +32/−4, 12 of the 32 a header comment;
tests: test_tm_cache_asset_pick.py; other: seed_run.py; this report and the logs are generated or prose).

## Notes for the DRI
- **The current pin (9ccbf3fdf).** There are two ways to stop the per-part rebuild before that record completes. Both are
  decider/ops calls, and I took neither:
  - (i) A one-off asset for tree 4acf8387e957. `~/code/ve-tm-nightly-l1` is at 9ccbf3fdf and has a `lean/.lake/build` (57
    lib entries; not verified complete). It would need `lean_share.py publish` there (the seal and checks), then
    `cloud-secret-scan.py files <entry>` (the `--pack` path runs only the names scan), then a pack and
    `lean-cache-publish.sh --pack …/lean-build-4acf8387e957.tar.zst --main 9ccbf3fdf… --tree 4acf8387e957… --entry <entry>`.
    After the install, the staged keep holds it until the record completes.
  - (ii) Accept the rebuild until the record completes or the head is put on `test-skip/nightly-no-resume-heads`.
- **Harness reads.** In the existing harnesses (cloudplumb, armcache), the staged script reads the live `test-skip/nightly`
  record through `tm-nightly.py resume`. That record's head is not in their synthetic repos, so they pin nothing, and their
  results are identical on both scripts (`harness-regression.txt`). The new test sets `TEST_SKIP_DIR`.
- **Every publish run logs one line.** While a resumable record's head has no asset within K, every publish run logs "none
  kept for it". This is a visible trace, not an error.

## Self-review against BUILDER-CHECKLIST
1. N.A.: no Lean answer or relay.
2. PASS: the deliverables are built. The staged file, the failing-first test and the existing harnesses run on the `.new`
   (`run-staged.log`, `harness-regression.txt`). The one seam (no asset for the current 9ccbf3fdf record) is explained above.
3. PASS: tests can fail. `run-live.log` has FAILED: 16, and `seeds.log` shows 6 of 6 caught.
4. N.A.: no Python, Lean or Rust product code. Case (2) compares the staged script with the live one on valid inputs.
5. N.A.: no R8 binding.
6. PASS: the evidence comes from the final staged file (md5 4c8a3d9d…, `sha256.txt`). The file was not changed after the
   runs.
7. PASS: no unsigned item; no DELTA rows.
8. N.A.: no user-visible VE change.
9. N.A.: no VE code changed, so test selection is not affected.
10. N.A.: no Lean.
11. PASS: every failing step leaves `pin=""` (fail-safe: the prune works as today). See test (2): complete, old, no-resume,
    quarantined and unrelated.
12. PASS: 0.30 s and under 30 MB added per publish run (`pin-cost.txt`).
13. N.A.: no test was removed or renamed.
14. PASS: both directions are tested. The pin is kept in (1) and nothing is pinned in the 7 cases of (2). Each claim above
    cites its file.
15. PASS: no overclaim. Words such as "no pin" and "every failure" are backed by case (2) and seeds B3/B4. There is no silent
    cut (the seam is stated above), every new check has a seed that breaks it (B1–B6), and the limits are unchanged (KEEP 5;
    one more only in the (b) case).
