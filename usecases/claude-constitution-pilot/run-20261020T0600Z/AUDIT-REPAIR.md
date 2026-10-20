# Audit repair, run 20261020T0600Z

The audit of run 20261019T1800Z (`AUDIT-20261019T1800Z-received.md`) found 31 of 31 verdicts faithful (20 sampled, 9 changed, 2 PS-0p class-B items) and **no unit unfaithful or incomplete**, so no covered status needed repair and no claimed byte was removed. Its "audit-verified covered bytes" now equal the claimed bytes (3,158 B: 2,794 B of covered units and 364 B of labels), because it accepted the 24 B of u0013 that the previous run had not seen.

It listed four faults "to fix before claiming (no verdict change)", all on units whose status does not depend on them:

| Unit | Fault | What this run did |
|---|---|---|
| u0235.presupposition ("Claude's nature") | a singular possessive takes for granted existence and uniqueness; the record and fence gave existence only | recorded claim, trigger `pre` and the expressible fence are the uniqueness form ("There is a first thing such that … a nature of claude … every second thing that is a nature of claude … the same as the first thing."); `evidence/owner-probe.json` shows it parses, renders and round-trips. The unit stays UNFORMALISED (`other:premise-check-budget`), 0 B |
| u0002.presupposition, u0095.presupposition | the fences' owner `anthropic` is the constant "Anthropic, as a type of principal"; the mission and the guidelines belong to the company | the expressible fences name a separate constant `anthropiccompany` of the sort thing (a lower-case one-word identifier is what the English admits: `anthropic_company` and `Anthropic` do not read as a name). Parses, renders and round-trips; stays UNFORMALISED, 0 B |
| u0013.presupposition | "of claude" is written in lower case | **not repairable**: `Invalid ASCII identifier: 'Claude'`; a constant must be a lower-case ASCII identifier. Recorded as a finding; the entry is untouched so its audit verdict stands |

REMOVE EVERY TRACE: the old existence-only fence and claim of u0235 survive only as `previous_presupposed_claim` and `expressible_with.previous_fence`; the old owner fences only as `expressible_with.previous_fence`; u0235's earlier audit-repair record (20261018T1800Z) is kept as `earlier_audit_repair`. The premise-variant evidence (`evidence/ps6r/premise-variants.json`) was measured with the old fences and is cited as history, not re-measured: the corrected fences are not added to any document.

Small faults carried unchanged: "principal type of Claude" can also be read as "main type of Claude"; u0156.s03's frame term and u0168.s01's guard (see `metrics.json`, `audit_rejected_units_and_repair_status.small_faults_not_repaired`).
