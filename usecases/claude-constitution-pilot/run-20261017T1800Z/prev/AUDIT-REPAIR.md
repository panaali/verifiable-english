# Audit repair, run 20261017T0600Z

Input: `AUDIT-20261016T1800Z-received.md` (20/20 sampled faithful plus 11/11 changed faithful, 30 units; no unit marked unfaithful or incomplete, so no covered status is kept "only because repaired"; none of the audited units is `claimed: false`). It lists two small faults "with no verdict change". Both are repaired.

| Fault (source) | Repair | Where |
|---|---|---|
| The document's `units[].meaning` left out each default candidate's exception term: u0036.s05 listed only `genuine_ambiguity`; u0156.s03 and u0263.s04.p2 said "specified" | `meaning` is now `{"open": ["genuine_ambiguity", "exception_to_asking_for_clarification"]}`, `{"open": ["exception_to_not_deceiving_about_system_prompt"]}` and `{"open": ["exception_to_complying_with_exploit_instruction"]}`. The exception terms are declared by `nd.py` (not in `translation-without-content.ve.md`, which has no candidate with content), so `nd.py` now sets the unit's meaning in the same step; a first try that wrote the meaning into `translation-without-content.ve.md` made probe s1 refuse that document ("invalid meaning status": an undeclared open term) and was reverted. `nd.py all` rebuilds `translation.ve.md` byte for byte (`cmp readings/nd-all.ve.md translation.ve.md`). Only these three fields differ from the previous run's translation; body, vocabulary, graph, contents, meaning ids, situations and admission texts are identical; `ve document check` passes (16 choices CONFLICT-FREE). | `nd.py`, `translation.ve.md`, `units.json` (`repair_20261017T0600Z`) |
| `audit_repair` of u0165.s01, s02, s04 to s07 omitted the 20261014T1800Z acceptance that `plan_repairs` cites | the closing sentence now lists the audits of 20261014T1800Z, 20261015T0600Z, 20261015T1800Z, 20261016T0600Z and 20261016T1800Z; u0165.s03 (rejected by 20261014T1800Z, repaired in 20261015T0600Z) lists 20261015T0600Z to 20261016T1800Z | `units.json` |

`changed_units` (3): u0036.s05, u0156.s03, u0263.s04.p2. They leave the audit-verified set until an audit has seen the repair (they were not in it before). **Audit-verified covered bytes: 2,319 plus 349 label bytes** (previous run 1,472 plus 349): added back are u0073.s05, u0062.s01, u0123.s01.p1 and u0123.s02.p1 (847 B), which the 20261016T1800Z audit accepted in the form they still have. Claimed bytes stay 2,951.

**Seeded fault (pilot script, no product code changed).** Claim: the three units' meanings list the exception terms. Planted: the previous run's `translation.ve.md` put back. Failing check: `repair_20261017T0600Z.py` stops with `AssertionError: u0036.s05`. Restored: the file is cmp-identical to `readings/nd-all.ve.md` and the script passes.

**Not repaired, and why.** (a) "Being helpful" and "The existential frontier" are labelled whole while "Being broadly safe" and "Safe behaviors" get presupposition units: the labels are true and no claim is lost. (b) The notes call u0173.s01 to s04 modality/belief while the ledger tags them `norms`: the tally is kept so that differences measure the language.

## Plan additions of this run (DRI SC2, AT2, AT3, ME1; X5; X2-X4)

| Plan item | State | What this run did |
|---|---|---|
| AT-0p (u0165.s01 to s07) | already in the plan's form (applied 20261014T1800Z; u0165.s03 per candidate since 20261015T0600Z; audited faithful five times) | `repair_20261017T0600Z.py` asserts the guard shape `( C_i(s) and knowingly_engages_i(c, s) ) or thinks_quite_likely_i(c, s)` and that no unary or unsplit term remains; the four probe kinds re-measured: SETTLED no, SETTLED no, UNDECIDED, UNDECIDED for all seven rules, the probe file byte-identical. `plan_repairs` lists the seven with `applied_in_this_run: false`. The English export still renders the nested guards but does not read them back |
| SC-M0 (scope tally) | regenerated | 150 governors, 352 units, 55,294 bytes; identical (only the note's run id differs). Tags only |
| AP-0 item 3 (act_workaround) | regenerated | 17 units, 2,502 bytes (M4); no act phrase changed, no `act_workaround_stale` |
| DRI X5 (claimed) | applied | every covered unit is `claimed: true`; none is `claimed: false` |
| DRI X2-X4 (1) sort `entity` noun | in place | the noun is "thing" ("things"), asserted |
| DRI X2-X4 (2) vocabulary change | none | `nd.py all` ran at this tag (twice); every fenced unit (u0248) parses unchanged; the only units that differ from the previous run are the three meanings (`vocabulary_change_check` in `metrics.json`) |
| DRI X2-X4 (3) Rust time limit | default `VE_RUST_TIMEOUT` kept | no query needed the cap (all 21 hard-constraint queries answered on the first run), so no `prlimit` run and no peak resident set to record |

Expected against measured, as in the previous run: the plan's "46 open terms (1800Z copy)" is 50 here (the 46 plus the three exception terms and the scope set's per-candidate terms); claimed bytes 2,951 as expected; `ve document check` passes.
