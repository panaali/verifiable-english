# Audit repair, run 20261018T0600Z

Input: `AUDIT-20261017T1800Z-received.md` (xhigh): **28 of 28 verdicts FAITHFUL** (20 sampled plus 8 changed), no UNFAITHFUL or INCOMPLETE unit. No audited unit is `claimed: false`. So no unit needs repair, none leaves the covered statuses, and `changed_units` and `audit_repairs` are empty.

| Finding | Action |
|---|---|
| Small fault: u0156.s03's frame term `asked_to_keep_system_prompt_confidential` takes only the instance, while the words describe "a situation" and the rule ranges over (instance, user) | Carried, not repaired. The audit says no verdict changes. Giving the term a user or situation argument would add structure the sentence does not state; a frame over a situation is what the missing scope construct (`other:scope`, governor u0156.s01, reach `frontier`) would give. Recorded in `metrics.json` (`audit_rejected_units_and_repair_status.small_faults_not_repaired`) and here; the unit, its four readings and the open term are as the audit accepted them |
| Earlier small faults (whole-labelled headings; modality/belief wording of u0173.s01 to s04) | Still not rewritten: the labels are true and the tally is kept so that differences measure the language |

**Audit-verified covered bytes: 2,602 plus 349 label bytes** (previous run 2,159 plus 349). The four units repaired in the previous run and accepted by this audit (u0156.s03, u0165.s06, u0036.s05, u0263.s04.p2) count again because they are byte-identical here. Claimed bytes stay 2,951.

**Seeded faults (pilot scripts; no product code changed).** (1) Claim: the finished translation is the previous run's. Planted: one byte of an open-term name changed. Failing check: `finish_20261018T0600Z.py` stops with `AssertionError: {'translation.ve.md': False}`. (2) Claim: the in-frame candidates are guarded on the Claude instance. Planted: the guard of the first in-frame candidate bound to variable 0. Failing check: `repair_20261017T1800Z.py --check` stops with `AssertionError: strict-in-frame`. Both restored (cmp-identical to `prev/translation.ve.md`).

## Plan additions of this run (DRI SC2, AT2, AT3, ME1; X5; X2-X4)

| Plan item | State | What this run did |
|---|---|---|
| AT-0p (u0165.s01 to s07) | in the plan's form since 20261014T1800Z | shape asserted (`repair_20261017T1800Z.py --check`), content rebuilt by `nd.py all` (cmp-identical), four probe points per rule re-run: SETTLED no, SETTLED no, UNDECIDED, UNDECIDED for all seven (byte-identical `probes/unspecified-probe.json`); `plan_repairs` lists the seven units with `applied_in_this_run: false`; 51 open terms; claimed bytes 2,951 |
| SC-M0 scope tally | in place | `scope-tally.json` regenerated: 150 governors, 352 units, 55,294 bytes, identical to the previous run's apart from the note |
| AP-0 item 3 `act_workaround` | in place | tags copied from `evidence/m4-act-workaround.json`; every act phrase equals the evidence's; M4 = 17 units, 2,502 bytes (`act_workaround_m4`) |
| X5 (`claimed: false`) | none marked | claimed bytes = covered bytes = 2,951 |
| X2-X4 vocabulary | no vocabulary change | `nd.py all` rerun anyway; the one fenced unit (u0248) parses unchanged; the sort `entity` keeps the noun "thing"; Rust limit left at its default (no prlimit, no cap raised; all 21 queries answered on the first run) |
