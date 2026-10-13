# Audit repair, run 20261013T0600Z

Input: `AUDIT-20261012T1800Z-received.md` (17/20 sampled faithful + 5/12 changed faithful; u0165.s01–s07 UNFAITHFUL). A unit the audit rejected keeps its covered status (OPEN) only because it is repaired here; none counts as audit-verified.

| Unit | Audit finding | Repair | Status |
|---|---|---|---|
| u0165.s01 to u0165.s07 | The guard "case atom AND knowledge-or-likelihood" weakens applicability: u0173.s01 also covers actions Claude *thinks quite likely* to fall into the category, and that belief need not be correct (the saved probe returned UNDECIDED where the belief held but membership did not). | The guard is the source's two alternatives, in its own order, as one flat "either … or …" of two open terms of the rule's own category: `knowingly_<category>` ("Claude would be knowingly and intentionally doing what the bullet says"; includes the category) or `thought_likely_<category>` ("Claude thinks it quite likely that the action would be a case of what the bullet says"; belief, no membership needed). Both carry the category's own open factors plus "what counts as knowingly / intentionally" and "what counts as thinking it so / how likely is quite likely". Where neither holds the rule says nothing (completion unspecified): the unclear, uncertain and unknowing cases of u0173.s02 and u0173.s04 are neither forbidden nor permitted. | OPEN (unchanged status; content repaired) |
| u0173.s01 | Accepted only as correctly UNFORMALISED. | Note only: it says which open terms carry its two alternatives. Still UNFORMALISED (modality/belief; "quite likely" is a quantity), not claimed. | UNFORMALISED |

## Why a flat either/or
A first repair, `(case AND knowing-and-intentional) OR thought-likely`, checked and probed correctly, but VE's English export of the nested guard does not read back (`IdentityMetadataMismatch: block count`; every other rule of the translation reads back). A flat either/or of two atoms reads back for all seven rules (`english_round_trip` true) and is also the source's own sentence, so the category's former case atom (which only labelled the bullet) is not needed: each of the two new terms holds the bullet's words. This is a finding about the language, not the source: a rule with "A and B, or C" cannot be exported to English and read back; the translator had to move the conjunction into a named term.

## Consequences removed with the old design (every trace)
The previous run's single open term `restricted_action_knowing_or_quite_likely`, the seven category case atoms (vocabulary predicates, open terms, stored relations of the reading sets' models), the wording "the case atom" in each hard-constraint note, the regulated predicates' description sentence naming the case atom, the ledger fields `case_atoms`/`check`/`readings`/`where_the_text_is_silent` for u0165.s01–s07, the probe points of the earlier design (`unspecified-probe.json` is re-run, 6 points per constraint), and the counts in SUMMARY and metrics (33 → 39 open terms, counting the three exception terms of the reading sets). The repair history of each unit (`audit_repair`) records the earlier forms in past tense without naming the removed terms.

## Conflicts
VE reports none (CONFLICT-FREE in all 8 choices), so there is nothing to classify as a source conflict or a translation artefact.

## Audit-verified bytes
1,728 substantive (0.93%) + 349 label bytes. Newly verified from the 20261012T1800Z audit: u0036.s05, u0125.s04.p2, u0156.s03, u0263.s04.p2 (byte-identical here). Claimed but not audit-verified: 874 (the seven repaired constraints).
