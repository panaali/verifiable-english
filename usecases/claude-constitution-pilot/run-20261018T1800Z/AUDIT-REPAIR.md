# Audit repair, run 20261018T1800Z

Input: `AUDIT-20261018T0600Z-received.md` (xhigh): **25 of 25 verdicts FAITHFUL** (20 sampled plus the 5 AT-0p units it checked as changed), no UNFAITHFUL or INCOMPLETE unit. No audited unit is `claimed: false`. So no unit needs repair, none leaves the covered statuses, and `audit_repairs` is empty.

| Finding of that audit | Action |
|---|---|
| Small fault (carried): u0156.s03's frame term takes only the instance of Claude, the words say "a situation" | Carried, not repaired (as before): a frame over a situation is what the missing scope construct (`other:scope`, governor u0156.s01, reach `frontier`) would give |
| Small fault (new): u0168.s01's guard `seemingly_compelling_argument_to_cross_line(s)` takes only the situation, so when one instance faces the argument every instance in s is obliged to remain firm (the extra duty is empty in English) | Carried, not repaired: no plan of this run directs it; binding the term to an agent is the typed-attitude feature beyond AT-0p. Recorded in `metrics.json` (`audit_rejected_units_and_repair_status.small_faults_not_repaired`) |

**Audit-verified covered bytes: 2,602 plus 349 label bytes** (unchanged). None of the 25 changed units of this run (QT-0p, PS-0p) was audited in its present form, so the 154 new claimed bytes (u0042.presupposition 38, u0043.s02.p1 15, u0043.s02.p2 75, u0245.presupposition 26) are claimed but not audit-verified.

## Plan additions of this run (DRI SC2, AT2, AT3, ME1; the merge of 2026-10-18; X2-X5)

| Plan item | State | What this run did |
|---|---|---|
| JT-0p (judgment terms, ledger only) | done | the class of every open term in `metrics.json` (`open_term_class`, 56 terms: judgment 20, classification 15, attitude 16, exception 4, proportion 1); phase 1's classes reproduced for every term unchanged since 20261012T1800Z; a one-line reason for each of the 21 terms new since the instrument (16 attitude terms, creating_a_cyberweapon, creating_malicious_code, could_cause_significant_damage_if_deployed, asked_to_keep_system_prompt_confidential, novel_entity); `judgment_terms` on every unit; 507 units / 88,996 B (phase 1: 507 / 88,989 B; three units differ, with reasons) |
| QT-0p (quantities; u0042.presupposition, u0043.s02) | applied; kept | content applied as written (sort `principal_type`, constants `anthropic`, `operators`, `users`, predicate `claude_principal_type`); CHECKED 38 B; u0043.s02 MIXED (15 B LABELLED, 75 B CHECKED); +128 B as expected; premises `model`; "Is there a fourth type of principal?" SETTLED no. Reported: the planned wording is refused by the lint (English shows a quoted name); the companion route's main premise check goes UNKNOWN (Lean-decided share 1.41% → 0.20%) |
| PS-0p steps 1, 2, 3 | applied | 10 titles lose `presupposed_claim`; u0055 note and audit list; u0254, u0268 notes; u0013, u0095, u0002, u0235 notes; u0286 offered and reverted (premise check UNKNOWN) |
| PS-0p step 4 | applied | `presupposition_triggers` on every unit (486 entries in 337 units); blocker `other:presupposition` on the 334 units whose carrier is unresolved |
| PS-0p step 5 (class B) | partly | u0245 offered (OPEN, +26 B, claimed only if the audit accepts it); u0032 offered and reverted (premise check UNKNOWN); u0069 (no admitted noun wording) and u0083 (needs "core value", waits for PS-6r) not offered |
| PS-0p step 6 | done | `presupposition-goals.json`: 2 "the user" occurrences (u0156.s03's act, 4 goals across its four candidates; u0123.s03, packed in a guard atom, 1 goal), 1 "the operator" (u0123.s02.p1, packed, 1 goal) and "its content" (u0156.s03, 4 goals); goals of one rule share its applicability but differ in row, so nothing is coupled |
| PS-0p step 7 | done | loads; 32 choices CONFLICT-FREE; carried probes byte-identical except the companion probe and one hard-constraint query (see SUMMARY) |
| AT-0p (u0165.s01-s07) | already in the plan's form since 20261014T1800Z | shape asserted (`repair_20261017T1800Z.py --check` and `update_ledger`); the four probe points per rule re-run and byte-identical (`probes/unspecified-probe.json`); 52 open terms (51 + novel_entity); claimed bytes were 2,951 before the plans above |
| SC-M0 scope tally | in place | `scope-tally.json`: 150 governors, 352 units, 55,294 B, identical to the previous run's; u0043.s02 is counted once (90 B) and both parts carry the tags |
| AP-0 item 3 `act_workaround` | in place | tags carried; every act phrase equals the evidence's; M4 = 17 units, 2,502 B |
| X5 (`claimed: false`) | none marked | claimed bytes = covered bytes = 3,105 |
| X2-X4 vocabulary | vocabulary changed | `nd.py all` rerun after QT-0p, for every PS-0p build and for the final document; `checkpoint.py` shows no existing predicate wording changed and u0248 parses to the same formula; the sort `entity` keeps the noun "thing"; Rust limit left at its default (no prlimit, no cap raised: the UNKNOWN premise checks are an evaluation budget, not a timeout) |
