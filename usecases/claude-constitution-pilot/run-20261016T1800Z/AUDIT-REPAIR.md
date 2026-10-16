# Audit repair, run 20261016T1800Z

Input: `AUDIT-20261016T0600Z-received.md` (20/20 sampled faithful plus 8/8 changed faithful, 28 units; no unit marked unfaithful or incomplete, so no covered status is kept "only because repaired"; none of the audited units is `claimed: false`). It lists small faults "with no verdict change". This run repairs every one that is a false text. Nothing in the translation (`translation.ve.md` is byte-identical to the previous run's), its meaning ids or its verdicts moves.

| Fault (source) | Repair | Where |
|---|---|---|
| u0062.s01 (9), u0123.s01.p1 (7), u0123.s02.p1 (10): the case atoms say "the situation is …" for terms whose argument is an operator input | every such atom now says "the operator input is …" (u0123.s02.p1's eleventh atom, `instruction_promote_own_products`, a pair of an operator and an input, was already worded so). | `units.json` |
| u0156.s03, u0263.s04.p2, u0036.s05: `open_terms` empty (or only genuine_ambiguity) though the default candidate carries an `exception_to_*` open term | the ledger lists `exception_to_not_deceiving_about_system_prompt`, `exception_to_complying_with_exploit_instruction`, `exception_to_asking_for_clarification` (the audit's "meaning specified" refers to these three entries; no ledger field of that name exists, the candidates' `meaning` fields were already true) | `units.json` |
| u0073.s05: `audit_repair` says "Counted as claimed, not audit-verified." though the unit was accepted four times | now "Counted as claimed; accepted FAITHFUL by the audits of 20261015T0600Z and 20261016T0600Z." | `units.json` |
| u0123.s03: `audit_verified: true` though the unit was dropped as changed | resolved the other way: the audit of 20261016T0600Z has since accepted the repaired form, which is unchanged here, so the flag is true and the unit is counted verified again | `units.json`, `metrics.json` |
| u0165.s01 to s07 | the closing sentence of `audit_repair` records the acceptance by 20261016T0600Z too (not a changed unit) | `units.json` |

`changed_units` (7): u0036.s05, u0062.s01, u0073.s05, u0123.s01.p1, u0123.s02.p1, u0156.s03, u0263.s04.p2. They leave the audit-verified set until an audit has seen the repair. **Audit-verified covered bytes: 1,472 plus 349 label bytes** (previous run 1,968 plus 349): dropped u0073.s05 234, u0062.s01 85, u0123.s01.p1 180, u0123.s02.p1 348 (847 B); added back u0123.s03 351 B. Claimed bytes stay 2,951. The three force sets (u0036.s05 68 B, u0156.s03 100 B, u0263.s04.p2 115 B) were not in the previous run's verified set (changed then) and are not now (changed again); the audit accepted them in their 0600Z form.

**Not repaired, and why.** (a) "Being helpful" and "The existential frontier" are labelled whole while "Being broadly safe" and "Safe behaviors" get presupposition units: the labels are true and no claim is lost; left for a later run. (b) The notes call u0173.s01 to s04 modality/belief while the ledger tags them `norms`: the ledger's missing feature is `norms` with `modality/belief` as a further blocker; the tally is kept as it was, so that differences measure the language.

## Plan additions of this run (DRI SC2, AT2, AT3, ME1; X5; X2-X4)

| Plan item | State | What this run did |
|---|---|---|
| AT-0p (u0165.s01 to s07) | already in the plan's form (applied 20261014T1800Z; u0165.s03 per candidate since 20261015T0600Z; audited faithful four times) | `repair_20261016T1800Z.py` asserts the guard shape `( C_i(s) and knowingly_engages_i(c, s) ) or thinks_quite_likely_i(c, s)` (c = var 1, s = var 0, binary terms on (claude_instance, situation)) on the three carried documents, no unary or unsplit term remains; the four probe kinds re-measured: SETTLED no, SETTLED no, UNDECIDED, UNDECIDED for all seven rules, the probe file byte-identical. Listed in `plan_repairs` with `applied_in_this_run: false`. The English export still renders the nested guards but does not read them back (all seven) |
| SC-M0 (scope tally) | regenerated | 150 governors, 352 units, 55,294 bytes; identical. Tags only |
| AP-0 item 3 (act_workaround) | regenerated | 17 units, 2,502 bytes (M4); no act phrase changed, no `act_workaround_stale` |
| DRI X5 (claimed) | applied | every covered unit is `claimed: true`; none is `claimed: false` |
| DRI X2-X4 (1) sort `entity` noun | in place | the noun is "thing" ("things"), asserted |
| DRI X2-X4 (2) vocabulary change | none | `nd.py all` ran at this tag; its result is byte-identical to the previous translation, so every fenced unit (u0248, the only fenced block) parses unchanged and no unit differs (`vocabulary_change_check` in `metrics.json`) |
| DRI X2-X4 (3) Rust time limit | default `VE_RUST_TIMEOUT` kept | no query needed the cap (all 21 answered on the first run), so no `prlimit` run and no peak resident set to record |

Differences from the plan's expectations, reported not hidden: the plan's "46 open terms (measured on the 1800Z copy)" is 50 here (the 46 plus the exception terms of the three force sets and the per-candidate terms of u0165.s03, which later runs added); claimed bytes are 2,951 as expected; `ve document check` passes.

## Conflicts

VE reports none (CONFLICT-FREE in all 16 choices), so there is nothing to classify as a source conflict or a translation artefact.
