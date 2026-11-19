# remote-dead-job-reaper: REPORT

**INSTALL WAITS FOR DECIDER READ.** Row `remote-dead-job-reaper`; decision
`inbox/dri/done/20261112T201959Z-orchestrator-4183924.md`. This item changes only manage-agents scripts. They are staged as
`*.new-remotew` drafts and are not installed. This directory holds the evidence: the staged diff, the test runs on the drafts
and on the installed code, the checksums and the design/review doc (`design-review.md`, a copy of
`manage-agents/reviews/remote-dead-job-reaper-20261119.md`). The VE product code is unchanged: no Lean, Python, Rust, relay,
schema or DELTA change.

## What was already installed
The uv-hardlink refinement (`-links 1`) and the hourly dead-dir archive pass went in on 11-16
(`cloud2-job.sh.bak-20261116T1532Z-c2rh`). The one open part of the row was the on-kill archive and mark.

## What the drafts add (`staged-changes.diff`)
- `cloud2-job.sh.new-remotew`
  - **Kill record.** Just before a job's scope is stopped (by `stop`, or by scoped's watcher when the caller's ssh is gone), the
    host writes `~/c2/killed/<unit>.<epoch>.rec`. The record lists the job's dirs, each with its inode: the processes' cwd,
    open files and environment refs, plus the gate's `~/jobs/gate-*` dir.
  - **Archive.** A dir named in a record, with the same path and inode, whose scope is no longer active, skips only the
    12-hour idle wait for archiving and marking. Every other `deadwhy`/`mark` check still applies: done, open refs, lock,
    inode and sha.
  - **Removal unchanged.** `reapone` still applies `young` and `afterm`. A killed dir is removed only at the first job start
    after it has been idle 12 h (the conservative option).
  - **Health line.** It now ends in `killed=<n>` (pending records). I checked every parser of that line
    (`cloud2-run.sh:185`, `remote-hosts.sh:64`, `tm-remote-parallel.sh:86,131`); none breaks on the extra field.
  - Records are pruned after 2 days.
- `cloud2-health.sh.new-remotew`: when a host reports `killed>0`, the archive pass starts once the last pass is 600 s old,
  instead of 3600 s.
- `tools-local/test_c2_reap.sh.new-remotew`: new cases (d). See Tests.

Still covered only by the hourly pass after 12 h idle: a gate.py killed by `gateinner`'s own `timeout`, OOM kills and host
reboots. None of these writes a kill record.

## Tests
Command (run from manage-agents):
`bash tools-local/test_c2_reap.sh.new-remotew <job script> c2-archive-dead.sh <health script>`

| run | result | log |
|---|---|---|
| drafts (`cloud2-job.sh.new-remotew`, `cloud2-health.sh.new-remotew`) | 57 ok, 0 FAIL, `PASS test_c2_reap` | `run-staged.log` |
| installed (`cloud2-job.sh`, `cloud2-health.sh`) | 45 ok, 12 FAIL (all of them new (d)/health cases), `FAILED test_c2_reap` | `run-installed.log` |
| `bash -n` job script and test, `zsh -n` health script | ok | - |

The cases the task asks for:
- **The on-kill archive+mark path writes the marker:** `(d1)`/`(d2) kill record` (the stop path and the caller-gone
  path) and `(d) not marked on kill` for `ve-gate-kill1`, `ve-gate-kill2` and `gate-t<pid>k2-*`. These fail on the
  installed code and pass on the drafts.
- **A uv-hardlinked .venv file (links > 1) is not a write after the marker:** the `(a) hardlinked` and
  `(d) hardlinked .venv` cases. They pass on both, since the `-links 1` fix was installed on 11-16. Seeded bug M5 shows
  they can fail.
- **Existing cases stay green:** all 45 pre-existing checks pass on both.

Run earlier on the drafts (design-review.md, Tests): the installed test (36 checks), `test_cloud2_runner.py` with the draft
health script, and `test_c2_seedpick`, `test_gate_one_per_host` and `test_tm_nightly_complete` against the draft
`cloud2-job.sh`. All pass.

## Seeded bugs (each in a copy of a draft; the drafts were not touched)
| id | file | bug | failing check in test_c2_reap.sh.new-remotew |
|---|---|---|---|
| M1 | cloud2-job.sh.new-remotew | scoped's watcher writes no kill record | (d2) kill record; (d) health killed=1 |
| M2 | cloud2-job.sh.new-remotew | the kill record matches on path only (inode ignored) | (d) recreated dir |
| M3 | cloud2-job.sh.new-remotew | a record whose scope is still active is accepted | (d) live-scope record applied |
| M4 | cloud2-health.sh.new-remotew | no 600 s interval for killed>0 | health: killed=2 calls ''; on-kill passes not spaced |
| M5 | cloud2-job.sh.new-remotew | `afterm` counts the ctime of multi-link files | (a) hardlinked ctime; (d) hardlinked .venv |
| M6 | cloud2-job.sh.new-remotew | `stop` writes no kill record | (d1) kill record |

All are shell. No Lean, Python or Rust product code changed in VE.

## Orphan lean processes (ve-cloud-2, read only, nothing killed)
In both scopes `timeout` and `trust_mutants.py` are gone; only lake/lean remain.

| scope | active since | processes | holds |
|---|---|---|---|
| `c2-tm-ve-et-5b-28aa88dc-1313146` | 11-11 14:36Z | lake 1881292 / lean 1881327, lake 1888864 / lean 1888925 | `/tmp/trust-mutants-gb0i1tq1` |
| `c2-tm-ve-kb-2a-b-5f7bfd94-1393688` | 11-14 19:40Z | lake 1688507 / lean 1688538, lake 1689795 / lean 1689826, lake 1692956 / lean 1692985 | `/tmp/trust-mutants-534gqrn0` |

ve-cloud-3 is paused (its host row has been commented out since 11-13, and ssh times out), so nothing could be listed there.

## Install (waits for the decider's read)
The install read was sent: `inbox/dri/done/20261119T092749Z-dri-remote-dead-job-reaper-2351882.md`. Checksums of the installed
files and the drafts are in `SHA256SUMS`. The installed files still match on 11-19.
```
cd /home/seyran/code/manage-agents; S=$(date -u +%Y%m%dT%H%MZ)
sha256sum cloud2-job.sh cloud2-health.sh tools-local/test_c2_reap.sh | cut -c1-16   # 9c50fd9763f29e9c c752f05752caaa2d f397a1f73ce5e702
cp -p cloud2-job.sh cloud2-job.sh.bak-$S-remotew && mv cloud2-job.sh.new-remotew cloud2-job.sh
cp -p cloud2-health.sh cloud2-health.sh.bak-$S-remotew && mv cloud2-health.sh.new-remotew cloud2-health.sh
cp -p tools-local/test_c2_reap.sh tools-local/test_c2_reap.sh.bak-$S-remotew && mv tools-local/test_c2_reap.sh.new-remotew tools-local/test_c2_reap.sh
# svc-cloud2-health reads its script once: restart it (find the scope running `zsh cloud2-health.sh loop` first)
systemctl --user stop ve-svc-cloud2-health-1795073246.scope
setsid nohup zsh /home/seyran/code/manage-agents/iso.sh svc-cloud2-health 256M -- zsh /home/seyran/code/manage-agents/cloud2-health.sh loop >> /home/seyran/code/manage-agents/svc-cloud2-health.log 2>&1 < /dev/null &
```
The new `cloud2-job.sh` reaches each host with the next job sent there. Until then, the old host script prints no `killed=`
field and the hourly pass runs as before.

SIZE: 55 product, 53 tests, ~150 other hand-written lines (design-review.md), plus this report.

CW (MEASURED): not available. `python3 -I tools-local/delegate-cw.py` printed "delegate-cw: own session not found (needs
VE_STEP and CLAUDE_CONFIG_DIR from dri-delegate.sh, or a transcript path)".

DELTA: none. No Lean or trust-base change, and no user-visible checker delta.

## Notes for the DRI
- **Orphans keep their scopes alive.** `tminner`'s `timeout -k 30` kills only `trust_mutants.py`, so lake/lean children stay
  in the scope and it never stops. Stopping the scope after the tool exits (with a kill record first) would fix this, but it
  is new kill behaviour, so it is not in this item.
- **Earlier removal is possible.** A killed dir could be removed before 12 h, since the kill record proves the job is dead.
  The 12-hour rule was kept.
- The c2b builder-lane scopes (e.g. `c2b-kb-4b-132775-1794855104.scope`, two `select_tests.py` since 11-16) are outside
  this row.
- Review notes F1-F7 (all class C): a temp `.rec` file can be left if `killrec` is cut off mid-write; `kpend` can keep a
  host on the 10-minute pass for an unarchivable dir; the `c2-tm-*` watcher path is untested (same code);
  the `grep -oE` prefix can over-match (guarded by the inode check).

## Self-review against BUILDER-CHECKLIST
All 12 items are N.A.: VE has no Lean, Python, Rust, relay, schema, generated-file or DELTA change, and this commit adds
evidence under `docs/infra/` only. The seeded bugs M1-M6 above, each caught by `test_c2_reap.sh.new-remotew`, cover the
seeded-bug rule for the changed (shell) code.
