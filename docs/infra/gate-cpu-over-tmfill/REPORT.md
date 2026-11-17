# gate-cpu-over-tmfill: CPUWeight 25 for the trust-mutant idle-fill scopes in iso.sh

INSTALL WAITS FOR DECIDER READ. No DRI signature is reserved and there are no DELTA rows: this is control-plane tooling in
`/home/seyran/code/manage-agents`, and no VE code, verdict or trusted line changed. Trust +0.

- Row: gate-cpu-over-tmfill (infra). Decision: `reviews/dri-decisions-20261117-gatecpu.md` item 1.
- Status: built and staged as `/home/seyran/code/manage-agents/iso.sh.new-gcpu` (md5 `40bbfc4558ea7a608bcaf7b4a4e879ae`;
  live base `iso.sh` md5 `493df1e17a9eb072cf436503171e1788`, `md5.txt`). Not installed. Install read sent:
  `inbox/dri/20261117T124311Z-builder-gate-cpu-over-tmfill-1243693.md`.
- This VE branch holds only this report and its evidence. No VE product code (Lean, Python or Rust) changed.

SIZE: 3 product (iso.sh: 2 comment lines plus 1 changed case line), 79 tests (`tools-local/test_iso_weight_tmfill.py`,
new), ~120 other hand-written lines (this report, `seeded-bugs.json`).

## 1. The change

`staged-changes.diff` (`diff -u iso.sh iso.sh.new-gcpu`): `tmidle-*|tm-drain-*` is appended to the existing weight-25 case
(`exp-*|eb-*|...|vs-*|svc-pilot|svc-pilot-*`), under a dated comment that cites the decision file. Nothing else changes.
`zsh -n iso.sh.new-gcpu` is clean (`syntax.log`).

## 2. Test

`tools-local/test_iso_weight_tmfill.py` (a copy is in `test_iso_weight_tmfill.py.copy`). Run it with
`python3 -I tools-local/test_iso_weight_tmfill.py`. The script under test is `$ISO_GCPU_FILE` when that is set, else
`iso.sh.new-gcpu` while it exists, else `iso.sh`. The test copies the script into a temp tree and rewrites the
manage-agents path to that tree, so the live CPU-PRIORITY-ITEMS, WORKER_NO_AUTOMEM and worktree manifest are not read.
A `systemd-run` stub on PATH prints its arguments. Assertions:

| name | CPUWeight |
|---|---|
| tmidle-20261117T0531Z-p1, tm-drain-vm1-idle | 25 |
| kb-4b, tm-esc-sc7-wordchar (an escape-fix chain, not idle fill) | 100 |
| merge-x | 1000 |
| exp-foo, vs-tm-nightly (existing weight-25 names kept) | 25 |

- Staged: 4 of 4 pass, rc=0 (`run-staged.log`).
- Live (`ISO_GCPU_FILE=.../iso.sh`): `test_idle_fill_scopes_weight_25` fails with `AssertionError: 100 != 25`, rc=1
  (`run-live.log`).

## 3. Seeded bugs (`seeded-bugs.json`, `seeds.log`; zsh, in `iso.sh.new-gcpu` applied to a temp copy; the staged file's md5 is unchanged afterwards)

- S1: drop `tmidle-*`. `test_idle_fill_scopes_weight_25` fails (100 != 25).
- S2: drop `tm-drain-*`. `test_idle_fill_scopes_weight_25` fails (100 != 25).
- S3: widen both patterns to `tm-*`. `test_chain_and_escape_fix_stay_100` fails (25 != 100) and
  `test_idle_fill_scopes_weight_25` fails, because `tmidle-` does not match `tm-*`.

## 4. Launcher check: who names tmidle-/tm-drain- and depends on that weight (`launchers.log`)

`grep -rlE 'tmidle-|tm-drain-'` over the manage-agents `*.sh`/`*.py` files (no .bak, archive or inbox) finds
`tm-nightly.sh`, `tools-local/test_tm_drain_vm1_idle.py` and `tools-local/test_cloud_tm_deadline.py`. No launcher calls
`iso.sh` with a tmidle- or tm-drain- name, and none reads the weight iso.sh gives those names. So none depends on it.
The same check found that the decision's premise does not hold:

1. **The tmidle-\* scopes do not go through iso.sh.** `tm-nightly.sh` lpart() (lines 87-89) starts
   `ve-tmidle-<stamp>-p<k>` with its own `systemd-run --user --scope ... -p CPUWeight=${TM_IDLE_WEIGHT:-10} -p CPUQuota=...`
   under `nice -n 19`. `test_tm_drain_vm1_idle.py:111` asserts `-p CPUWeight=10`. In the 11-17 journal those scopes have
   no iso.sh epoch suffix (`ve-tmidle-20261117T0531Z-p1.scope`) and start as `nice -n 19 ionice -c 2 -n 7 ...`, which is
   lpart's command. The only manage-agents file that names `ve-tmidle` is the live `tm-nightly.sh`, and it sets the
   weight on the same line. UNVERIFIED: the weight of the 03:18Z and 05:31Z runs, which ran before tm-nightly.sh's 07:55Z
   install. The iso.sh `tmidle-*` pattern changes nothing today. It applies only if a future launcher calls
   `iso.sh tmidle-...`.
2. **`ve-tm-drain-vm1-idle-1794873631` was a builder chain, not idle fill.** The journal shows it started 00:00:32Z as
   `zsh .../infra-item.sh tm-drain-vm1-idle infra/tm-drain-vm1-idle .../task-tm-drain-vm1-idle.txt` and ended 09:55Z.
   It is the chain of the item that built the idle fill. `tm-drain-vm1-idle` is the only BACKLOG id with either prefix.
   In iso.sh, `tm-drain-*` matches only the chains of items whose id starts with `tm-drain-`, and it would put them at
   weight 25. That contradicts the decision's own rule that chains stay at 100, the same class as `tm-esc-sc7-wordchar`.

Recommendation, sent with the install read: **do not install**. Close the row as "premise not confirmed: idle fill
already runs at CPUWeight 10 outside iso.sh". If the decider wants it anyway, install only `tmidle-*` (a harmless guard)
and drop `tm-drain-*`. I built the deliverable exactly as the task specified and left the choice to the decider read.

## 5. Install (only after the decider read)

```
cd /home/seyran/code/manage-agents && cp -p iso.sh iso.sh.bak-20261117-gcpu && mv iso.sh.new-gcpu iso.sh && zsh -n iso.sh && python3 -I tools-local/test_iso_weight_tmfill.py
```

iso.sh runs at each launch, so no service restart is needed. Scopes that are already running keep their weight. Revert:
`cp -p iso.sh.bak-20261117-gcpu iso.sh`.

## 6. Checks run

- Trust mutants: none to run. light-lane.py prints `NOT 277 changed lines outside generated files > 150 (10 files)`, from
  the evidence files only; no trusted-core file changed. `tools/trust_mutants.py --base d2573fc9 --plan` gives
  `"mutants": 0` (`trust-mutants-plan.log`).
- VE tests: the branch changes only `docs/infra/gate-cpu-over-tmfill/`. The selected run (mac-pytest.sh --select, on
  GitHub Actions, run gate-cpu-over-tmfill-42f065f9-t919464) passed: shard 1 had 6 units and 6 passed, shard 2 had 4
  units and 4 passed, exit 0. It deferred two weakly selected files to the chain gate (`selected-run.log`).
- main-known-red: no listed test is touched.

## Notes for the DRI

- The decision's measurement ("tmidle-* 0.5-2.1 cores at the gate's own weight 100") counts tmidle scopes that tm-nightly.sh
  started at CPUWeight 10 plus CPUQuota and nice 19 (section 4.1). Their CPU came from idle cores, which is the design of
  tm-drain-vm1-idle, not from a weight tie.
- What really sits at the gate's weight 100 on the VM is the other chains (fid-mech-b4, pf-f16, kb-4b and
  tm-esc-sc7-wordchar, about 1.4-1.8 cores each) and builder chains such as tm-drain-vm1-idle. That is a ranking between
  chains, outside this row.

## 7. Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relayed Lean answer changed.
2. Every deliverable built, no rule broken: PASS. iso.sh.new-gcpu (`syntax.log`), the test (`run-staged.log`,
   `run-live.log`), the seeded bug (`seeds.log`), the launcher grep (`launchers.log`) and the install read (inbox file
   above). Nothing installed.
3. Tests can fail: PASS. `run-live.log` fails on live; S1-S3 in `seeds.log`.
4. Python/Lean/Rust agree: N.A., none changed.
5. R8 binding: N.A., no binding changed.
6. Gate evidence matches the final HEAD: PASS by process. The chain gates the final HEAD; the evidence here comes from
   manage-agents runs on the staged file (md5 above).
7. No unsigned item: PASS. There are no DELTA rows and no reserved signature.
8. DELTA: N.A., no user-visible VE change.
9. Test selection: N.A., no VE code changed. The new test is a standalone manage-agents test.
10. Lean statements: N.A.
11. Budgets fail closed: N.A., no budget or deadline changed. The test's subprocess timeout is a hang guard, not an assert.
12. CPU/memory regression: PASS. The change only lowers weights for the two name patterns; the test asserts that the
    weights of kb-4b, tm-esc-sc7-wordchar and merge-x do not change.
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. Both directions: 25 for the new names, 100 and 1000 kept
    (`test_chain_and_escape_fix_stay_100`, `test_merge_train_1000`). Spec re-read: the case line against
    `reviews/dri-decisions-20261117-gatecpu.md` item 1 ("tmidle-* and tm-drain-* in the weight-25 list, the same case line
    as exp-*/vs-*"). Section 4 records where that premise fails.
15. No overclaim / no silent cut / every check can fail / limits: PASS. "No launcher depends" rests on the grep in
    `launchers.log`; nothing was cut; S1-S3 show each check failing; no limits are involved.
