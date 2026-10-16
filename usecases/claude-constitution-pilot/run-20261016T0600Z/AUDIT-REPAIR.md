# Audit repair, run 20261016T0600Z

Input: `AUDIT-20261015T1800Z-received.md` (20/20 sampled faithful plus 5/5 changed faithful, 25 units; no unit marked unfaithful or incomplete, so no covered status is kept "only because repaired"). It lists small faults "with no verdict change"; the earlier audit `AUDIT-20261015T0600Z-received.md` listed some of them too, and the 1800Z audit found them still unrepaired. This run repairs every one that is a false text. Nothing in the translation's content, meaning ids or verdicts moves.

| Fault (source) | Repair | Where |
|---|---|---|
| u0156.s03 and u0263.s04.p2: the admission text says the readings have no content and the stored model is empty (0600Z audit, unrepaired at 1800Z). The same sentence was in u0036.s05's set | `nd.py` `true_admission` replaces the two false sentences by the true ones (both candidates carry content that Lean checks; the separating situations are stored in the set's `situations`); for u0156.s03 the claim that the defeasible reading "is recorded here without content" is replaced by what the document holds (the strict rule with one unnamed exception, an open term; no completion beyond norm-defaults@0 `unspecified`). Six admissions in `translation.ve.md` change; nothing else in it does | `nd.py`, `translation.ve.md` |
| u0156.s03 ledger: `defeasible_reading_predicate` names a predicate that is not in the document | now `system_prompt_deception_permitted` with the open term `exception_to_not_deceiving_about_system_prompt` as the exception | `units.json` |
| u0156.s03 ledger: `where_the_text_is_silent` says nothing is left unsaid | strict candidate: nothing left unsaid; defeasible candidate: where the exception holds the rule says nothing, so UNDECIDED | `units.json` |
| u0156.s03 ledger: note and `audit_repair` describe the defeasible reading without content / in the duty form | both describe the candidate the document holds | `units.json` |
| found while repairing: the ledger `english` of the default candidate of u0036.s05, u0156.s03 and u0263.s04.p2 was an old wording ("should seek", "should avoid ...") that the document no longer holds | every candidate's `english` is the English `ve document render` shows for it ("... must ..., unless ..."); u0156.s03's strict candidate takes the rendered wording too | `units.json` |
| u0263.s04.p2 ledger: the case atom says the situation has been instructed | it is the instance of Claude that has been instructed (the term is binary on instance and situation) | `units.json` |
| u0123.s03 ledger: the case atoms say "the situation is an instruction ..." but the terms take an operator input | each now says "the operator input is an instruction ..." | `units.json` |
| u0165.s01 to s07 ledger: `audit_repair` ends "Not audited." beside `audit_verified: true` | the closing sentence records the audits that accepted the unit (20261015T0600Z, 20261015T1800Z) | `units.json` |

`changed_units` is `u0036.s05`, `u0123.s03`, `u0156.s03`, `u0263.s04.p2` (the document text of the three sets and the ledger text of u0123.s03), so the audit can re-verify them; u0165.s01 to s07 are not changed units (no guard, act or content moved). `plan_repairs` lists the seven AT-0p units with `applied_in_this_run: false`. Because they were repaired, the four changed units leave the audit-verified set: **audit-verified covered bytes 1,968 plus 349 label bytes** (previous run 2,602 plus 349); claimed bytes stay 2,951.

**Not repaired, and why.** (a) The audit's note that "Being helpful" and "The existential frontier" are labelled whole while "Being broadly safe" and "Safe behaviors" get presupposition units: the labels are true and no claim is lost, so no text was rewritten; left for a later run. (b) The audit's note that the notes call u0173.s01 to s04 modality/belief while the ledger tags them `norms`: the ledger's missing feature is `norms` with `modality/belief` as a further blocker; the tally is kept as it was, so that differences measure the language. `translation-without-content.ve.md` still carries the old sentence in its pending-candidate admissions, where it is true (that file is the input of `nd.py`, whose candidates have no content yet).

## Plan additions of this run (DRI SC2, AT2, AT3, ME1; X5; X2-X4)

| Plan item | State | What this run did |
|---|---|---|
| AT-0p (u0165.s01 to s07) | already in the plan's form (applied 20261014T1800Z; u0165.s03 per candidate since 20261015T0600Z; audited faithful three times) | `repair_20261016T0600Z.py` asserts the guard shape `( C_i(s) and knowingly_engages_i(c, s) ) or thinks_quite_likely_i(c, s)` (c = var 1, s = var 0, binary terms on (claude_instance, situation)) on the three carried documents and that no unary or unsplit term remains; the four probe kinds were re-measured: SETTLED no, SETTLED no, UNDECIDED, UNDECIDED for all seven rules, the probe file byte-identical. Listed in `plan_repairs` with `applied_in_this_run: false` |
| SC-M0 (scope tally) | regenerated | 150 governors, 352 units, 55,294 bytes; identical. Tags only; no unit changes status or content for it |
| AP-0 item 3 (act_workaround) | regenerated | 17 units, 2,502 bytes (M4); no act phrase changed, so no `act_workaround_stale`; evidence file cmp-identical to the one on `research/act-phrases-p1` |
| DRI X5 (claimed) | applied | every covered unit is `claimed: true`; none is `claimed: false` |
| DRI X2-X4 (1) sort `entity` noun | in place | the noun is "thing" ("things"), asserted |
| DRI X2-X4 (2) vocabulary change | no vocabulary changed | `nd.py all` ran twice at this tag; every fenced unit (u0248, the only fenced block) parses unchanged; no unit differs; only the six admission texts changed (listed in `metrics.json: vocabulary_change_check`) |
| DRI X2-X4 (3) Rust time limit | default `VE_RUST_TIMEOUT` kept | no query needed the cap, so no `prlimit` run and no peak resident set to record |

Differences from the plan's expectations, reported not hidden: the plan's "46 open terms (measured on the 1800Z copy)" is 50 here, the 46 plus the exception terms of the three force sets and the per-candidate scope terms of u0165.s03 (later runs' additions, outside AT-0p); claimed bytes are 2,951 as expected; `ve document check` passes.

## Conflicts

VE reports none (CONFLICT-FREE in all 16 choices), so there is nothing to classify as a source conflict or a translation artefact.

## Audit-verified bytes

1,968 covered plus 349 label bytes. Dropped because changed: u0036.s05 (68 B), u0123.s03 (351 B), u0156.s03 (100 B), u0263.s04.p2 (115 B). Nothing new is verified (the 25 units of the 1800Z audit were already verified, bar the four above). These are verdicts on unchanged text, not a fresh audit of this run.
