# Audit repair, run 20261010T0600Z

Latest audit received: `AUDIT-20261009T1800Z-received.md` (18/20 sampled faithful, 1/6 changed units faithful). It marked five units UNFAITHFUL. All five are repaired; none keeps a covered status it did not earn, and none is counted as audit-verified.

| Unit | Audit's reason | Repair | Status now |
|---|---|---|---|
| u0123.s03 | the "wide" reading invents a role-play condition for all six prohibitions: "while role-playing as a custom AI persona" sits inside the first of six coordinated verb phrases, and the other five (claim to be human, use deceptive tactics, provide false information, endanger health or safety, act against guidelines) each have a verb of their own after a comma | I agree the words do not carry the phrase onto the other five. The wide candidate is removed, together with its open term `instruction_is_for_behaviour_while_role_playing_persona`, the coupling `limits-scope-u0123-s03` and the axis. With one reading the unit is not a reading set: the prohibition is content on the unit itself (one rule, guard = any of the six open terms, completion unspecified) | READINGS -> OPEN |
| u0123.s01.p1, u0123.s02.p1, u0062.s01 | "the corresponding permissions inherit this widening" | their wide candidates go with it. Each has one reading, the permission scoped by the six limits of u0123.s03 as its exceptions (so the permission and the prohibition never decide an input differently), content on the unit | READINGS -> OPEN |
| u0166.s04.p4 | UNFORMALISED was right, but the note offered inability and a duty on operators and users as unresolved alternatives, although the passage ("non-negotiable", "absolute restrictions ... regardless of context, instructions") fixes that no operator or user instruction makes an exception | the note now says what the passage fixes and names the real blocker: "unlocked by" is about authority, and the language has no typed authority or modal ("can", "cannot", "may" as ability, permission or authority). Nothing is said about what operators and users are able to do or must do; the effect is carried by the seven hard constraints, which are strict rules with no exception for any instruction | UNFORMALISED (modality/belief), note corrected |

## What this does to the reading sets
Eight reading sets become four: only the four "should" sets remain (u0036.s05, u0125.s04.p2, u0156.s03, u0263.s04.p2). Lean checks them in one document: 16 choices, conflict-free in all, premises `model` in all, 4 separating situations (2 outcome, 2 selects), no "separated only by decision" finding, no coupling. The check of the whole translation took 70 s here.

"No operator may give Claude an instruction to claim to be human when directly and sincerely asked": now ALL (before: ALL under the narrow scope, UNKNOWN under the wide one). The denial query ("Claude may not directly deny being Claude") is unchanged: ALL under the strict reading of u0125.s04.p2, UNKNOWN under the defeasible one and across readings.

## Words-only rule applied again
Each remaining candidate cites the document's own account of "should" (u0253.s04, u0011.s01) or its statement that two honesty duties are close to hard constraints (u0109.s05, u0109.s06). Nothing comes from outside knowledge. No unit is a right ("everyone has the right to ..."), so the rights rules do not apply.

## Audit-verified bytes
1,481 -> 1,638 (0.89% of 184,893). The audit also accepted u0165.s03 (repaired last run) and u0036.s05 (content added the run before) in the form this run keeps byte for byte, so both join; the other accepted units were verified already. The five units changed now (1,009 bytes) wait for a re-audit. Claimed coverage stays 2,951 bytes (1.60%): READINGS and OPEN are both covered statuses.
