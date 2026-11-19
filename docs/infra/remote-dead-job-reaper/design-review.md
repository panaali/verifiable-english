# remote-dead-job-reaper: archive+mark on kill (2026-11-19)

Row: remote-dead-job-reaper. Decision: inbox/dri/done/20261112T201959Z-orchestrator-4183924.md (item 4: "a reaper (on kill and at
job start) on all remote hosts"). Status: **built and tested as drafts. NOT installed. INSTALL WAITS FOR DECIDER READ.**
DELTA: none (manage-agents tooling only; no VE repo, Lean or trust-base change). Nothing was killed, removed or copied on any host.

## What was already done (11-16, row c2-reap-hardlink, installed 11-16 15:32Z)
- The hardlink false positive: the "written after the marker" check counts a file's ctime only when it has ONE link
  (`-links 1`), so uv-hardlinked `.venv` files no longer keep dead dirs forever. This row's test now has a case for it in
  the archive path as well (see the tests below). It passes on the installed code too, because that fix is installed.
- The job-start sweep (reapsweep) and the hourly archive pass (c2-archive-dead.sh, started by cloud2-health.sh): a dir idle
  for 12 h is archived to the VM, verified and marked. The next job start removes it.

What was still open, and what this row adds: **nothing marked a killed job's dirs on the kill itself.** They waited 12 h and
then up to an hour more for a pass.

## Change (drafts `*.new-remotew`)
1. **cloud2-job.sh: kill records.** `killrec <unit>` runs just before a job's scope is stopped, in both kill paths:
   - scoped's stdin watcher (the caller's ssh went away: a chain timeout, a killed cloud2-run.sh);
   - `stop` (merge-train cancel).

   It reads the scope's processes from its cgroup and collects every reap-prefix dir they use: cwd, root, open fds and
   environment (TMPDIR or HOME of gate.py children). For a c2-gate unit it adds the gate's `~/jobs/gate-*` dir. It writes
   `~/c2/killed/<unit>.<epoch>.rec`: a line `unit <unit> <epoch>`, then `<dir> <inode>` for each dir. The file is written to a
   temporary name and then renamed, and only when at least one dir was found. Nothing is removed at this point.
2. **cloud2-job.sh: archive at once.** deadwhy, used by `deadlist`, `records` and `mark`, skips **only the 12-h idle check**
   when `killedrec` finds a kill record that meets all of these:
   - it names the dir with its current inode (a dir renamed or recreated after the kill does not count);
   - its unit's scope is no longer active.

   Every other check stands: no `done`, nothing open (openby), not already marked, plus mark's lock, same inode and tar sha.
   The marker ends in `(on kill: <unit>)`.
3. **cloud2-job.sh: health.** The `health` line ends in `killed=<n>`: dirs named by kill records younger than 12 h with the
   same inode and no marker or `done`. Every parser of the line strips at the next space, so the extra field changes none of
   them. I checked remote-hosts.sh, cloud2-run.sh, tm-remote-parallel.sh and cloud2-health.sh.
4. **cloud2-health.sh.** When the line reports `killed>0`, the archive pass starts once the last one is
   `C2_ARCHIVE_KILL_EVERY` (600) s old, instead of `C2_ARCHIVE_EVERY` (3600). A killed job's dirs are archived and marked
   about 2 to 10 min after the kill. All hosts in remote-hosts.sh rows are covered: the health loop probes each one.
5. **Removal is unchanged** (conservative choice). reapone still keeps any dir modified within 12 h. A killed dir is marked
   at once and removed at the first job start after 12 h idle. The job-start sweep drops kill records 2 days old.

Not covered, left to the 12-h pass as before:
- a gate.py killed by gateinner's own `timeout` (gateinner writes `done`; its `/tmp/ve-gate-*` dir has no kill record);
- an OOM kill;
- a host reboot.

c2-archive-dead.sh is unchanged: `deadlist` now also lists killed dirs.

## Tests (`tools-local/test_c2_reap.sh.new-remotew`, 57 checks; new cases (d))
`bash tools-local/test_c2_reap.sh.new-remotew cloud2-job.sh.new-remotew c2-archive-dead.sh cloud2-health.sh.new-remotew`

| run | result |
|---|---|
| new test on the drafts | **57 ok, PASS** |
| new test on the INSTALLED cloud2-job.sh + cloud2-health.sh | **45 ok, 12 FAIL** (every on-kill case; every earlier case passes) |
| installed test (tools-local/test_c2_reap.sh) on the drafts | PASS (36) |
| `C2H=cloud2-health.sh.new-remotew python3 -I tools-local/test_cloud2_runner.py` | all passed |
| `C2J=<draft> test_c2_seedpick.py`, `C2J=<draft> test_tm_nightly_complete.py`, `C2J_SCRIPT=<draft> test_gate_one_per_host.py` | PASS, OK, OK |
| `bash -n` cloud2-job.sh.new-remotew and the test; `zsh -n` cloud2-health.sh.new-remotew | ok |

The (d) cases use real transient user scopes. In each kill path the scope's processes hold a dir as cwd or as an open fd:
- (d1) `stop` records the cwd dir and the fd dir with their inodes. The cancelled gate dir gets `done`, so the rotation owns it.
- (d2) the caller's ssh goes away (a stand-in gateinner, real `gatework` and `scoped`). The watcher records the cwd dir and
  the gate's job dir, then stops the scope.
- `health` reports `killed=3` before the pass and `killed=0` after it.
- The archiver marks all three dirs, each only minutes old, with records on the VM side and the marker naming the unit.
- These are not marked or not exempt:
  - a young dir that no killed process used: not marked;
  - the done dir: not marked;
  - the same path recreated with another inode: "modified within 12 h";
  - a kill record whose scope is still active: does not apply.
- Removal is unchanged: the job-start sweep KEEPS the marked killed dirs ("modified within 12 h") and drops a 3-day-old kill
  record.
- A uv-hardlinked `.venv` file (links 2) linked after the marker is no write: `records` answers "already marked", not a
  re-archive.
- health: `killed=0` with a pass 700 s ago starts no pass. `killed=2` starts one, and a second probe right after starts none.

## Seeded bugs (each in a copy of a draft; drafts untouched)
| # | file | bug | failing check |
|---|---|---|---|
| M1 | cloud2-job.sh.new-remotew | scoped's watcher without killrec | (d2) kill record; (d) health killed=1 |
| M2 | cloud2-job.sh.new-remotew | killedrec matches the path only (inode ignored) | (d) recreated dir: marked or wrong reason |
| M3 | cloud2-job.sh.new-remotew | killedrec ignores an active scope | (d) live-scope record applied |
| M4 | cloud2-health.sh.new-remotew | no 600-s interval for killed>0 | health: killed=2 calls ''; on-kill passes not spaced |
| M5 | cloud2-job.sh.new-remotew | afterm counts ctime of multi-link files | (a) hardlinked ctime; (d) hardlinked .venv |
| M6 | cloud2-job.sh.new-remotew | `stop` without killrec | (d1) kill record |

## Orphan lean processes (read-only, 2026-11-19 ~12:00Z; nothing killed)
ve-cloud-2: two tm scopes whose tool is gone. In neither scope is there a `timeout` or `trust_mutants.py` process left: only
lake/lean children, each with its cwd in a trust-mutants dir:
- `c2-tm-ve-et-5b-28aa88dc-1313146.scope`:
  - active since 2026-11-11 14:36Z (about 7 d 15 h);
  - 4 procs: lake 1881292 + lean 1881327, lake 1888864 + lean 1888925;
  - cwd `/tmp/trust-mutants-gb0i1tq1/lean-{wra698du,rjgpa9ct}/lean`.
- `c2-tm-ve-kb-2a-b-5f7bfd94-1393688.scope`:
  - active since 2026-11-14 19:40Z (about 4 d 10 h);
  - 6 procs: lake 1688507 + lean 1688538, lake 1689795 + lean 1689826, lake 1692956 + lean 1692985;
  - cwd `/tmp/trust-mutants-534gqrn0/lean-{njkncq_7,441yb5zc,st0n_ckr}/lean`.

Also long-lived, though not lean: `c2b-kb-4b-132775-1794855104.scope`, active since 11-16 18:51Z, 2 `select_tests.py`
processes (builder lane, c2b-job.sh). The other active scopes are the three tm-nightly scopes started 11-19 07:30Z, each with
its live `timeout` and `trust_mutants.py`.

ve-cloud-3: paused since 11-13 (`#PAUSED` in remote-hosts.tsv). ssh times out, so nothing could be listed there.

Why they hold: tminner's `timeout -k 30` kills `trust_mutants.py` only. The lake/lean grandchildren stay in the scope, so the
scope stays active and their trust-mutants dirs stay "open". The reaper keeps those dirs, which is the safe answer. The on-kill
path does not apply either, because the scope is active.

## Install (for the decider)
1. Check that the live files are still at the base the drafts were made from (sha256, first 16 hex):
   - cloud2-job.sh: 9c50fd9763f29e9c
   - cloud2-health.sh: c752f05752caaa2d
   - tools-local/test_c2_reap.sh: f397a1f73ce5e702
2. Run:
```
cd /home/seyran/code/manage-agents; S=$(date -u +%Y%m%dT%H%MZ)
sha256sum cloud2-job.sh cloud2-health.sh tools-local/test_c2_reap.sh | cut -c1-16   # 9c50fd9763f29e9c c752f05752caaa2d f397a1f73ce5e702
bash tools-local/test_c2_reap.sh.new-remotew cloud2-job.sh.new-remotew c2-archive-dead.sh cloud2-health.sh.new-remotew | tail -1   # PASS test_c2_reap
cp -p cloud2-job.sh cloud2-job.sh.bak-$S-remotew && mv cloud2-job.sh.new-remotew cloud2-job.sh
cp -p cloud2-health.sh cloud2-health.sh.bak-$S-remotew && mv cloud2-health.sh.new-remotew cloud2-health.sh
cp -p tools-local/test_c2_reap.sh tools-local/test_c2_reap.sh.bak-$S-remotew && mv tools-local/test_c2_reap.sh.new-remotew tools-local/test_c2_reap.sh
# svc-cloud2-health reads its script once: restart it (find the scope running `zsh cloud2-health.sh loop` first)
systemctl --user list-units 've-svc-cloud2-health*' --no-legend      # -> ve-svc-cloud2-health-<n>.scope
systemctl --user stop ve-svc-cloud2-health-1795073246.scope   # the scope at 2026-11-19 (pid 61804); confirm with the line above
setsid nohup zsh /home/seyran/code/manage-agents/iso.sh svc-cloud2-health 256M -- zsh /home/seyran/code/manage-agents/cloud2-health.sh loop >> /home/seyran/code/manage-agents/svc-cloud2-health.log 2>&1 < /dev/null &
```
3. Notes on the install:
   - **How the new cloud2-job.sh reaches the hosts.** The next `cloud2-run.sh tm|sel|gate` to a host copies it there (syncjob
     sha check).
   - **Until then:** the old host script prints no `killed=` field, so the health loop keeps its hourly pass.
   - **Kill paths covered:** only jobs killed after the new host script is in place get kill records.
   - **Undo:** restore the two `.bak-*-remotew` files and restart svc-cloud2-health. Kill records left on a host are ignored
     by the old script, and markers already written stay valid.

## Cost
CW: `tools-local/delegate-cw.py` printed "own session not found (needs VE_STEP and CLAUDE_CONFIG_DIR from dri-delegate.sh, or a
transcript path)", so this session's CW is not measured. No Codex used.
