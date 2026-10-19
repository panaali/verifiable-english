# Audit repair, run 20261019T1800Z

The audit of run 20261019T0600Z (`AUDIT-20261019T0600Z-received.md`) found 30 of 31 verdicts faithful (20 sampled, 11 changed) and rejected one unit.

| Unit | Verdict | Cause | Repair in this run |
|---|---|---|---|
| u0032.presupposition ("What constitutes genuine helpfulness") | UNFAITHFUL | its English "Some thing is helpful." drops "genuine" and "constitutes", so it is weaker than the heading | **Reverted to UNFORMALISED** (`other.discourse`), 38 B not claimed. The predicate `genuine_helpfulness`, its open term and its fence are removed from the document (`repair_20261019T1800Z.py`). The recorded claim is the trigger's `pre`, "Something constitutes genuine helpfulness." The merged wordings (ps-6r) do not help: there is no admitted wording for "constitutes genuine helpfulness" (TEMPLATE_SHAPE). `open_terms: [genuine_helpfulness]` stays on the entry as a ledger-only pointer, as on the other UNFORMALISED entries that name the term. |

Small faults of that audit, all carried or noted: "principal type of Claude" can also be read as "main type of Claude" (the sort noun stays: it is what removed the quoted-name fallback; no other admitted wording was found); u0156.s03's frame term and u0168.s01's guard (carried since earlier runs; the first needs cross-sentence scope as a construct, the second a typed attitude).

REMOVE EVERY TRACE: the open term count falls from 53 to 52; `genuine_helpfulness` is again a ledger-only name (4 names: appropriate_oversight, broad_safety, ethical_harm, genuine_helpfulness); its judgment-term class (judgment) is unchanged; the metrics' PS-0p step-5 text, the companion probe, the rendering and the premise-variant record no longer mention the unit as claimed. The only places that still quote "Some thing is helpful." are u0032's own note and audit record, as the rejected wording.

## Ledger-note repairs (status unchanged)
PS-0p step 3 told earlier runs to keep u0013, u0095, u0002 and u0235 UNFORMALISED with the note "relational-noun wording not admitted in VE English". That note is now false (ps-6r admits the wordings): u0013 is CHECKED (feature upgrade); u0095, u0002 and u0235 keep UNFORMALISED with the new reason `other:premise-check-budget`; u0083's note "waits for PS-6r" is replaced (the merged wording says "core value of …", the heading says "values"; not offered). u0002's recorded claim and its trigger's `pre` are made equal ("exactly one mission"; the claim said "a mission").
