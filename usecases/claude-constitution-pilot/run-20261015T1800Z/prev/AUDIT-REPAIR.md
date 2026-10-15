# Audit repair, run 20261015T0600Z

Input: `AUDIT-20261014T1800Z-received.md` (19/20 sampled faithful + 8/9 changed faithful, 25 units; u0165.s03 UNFAITHFUL, and three "small faults, no verdict change"). A unit the audit rejected keeps its covered status only because it is repaired here; none counts as audit-verified until re-audited.

| Unit | Audit finding | Repair | Status |
|---|---|---|---|
| u0165.s03 | The reading set split the case atoms into wide and narrow but not the attitude terms. `thinks_quite_likely_3` was the same belief alternative in both candidates, and its record (like that of `knowingly_engages_3`) still described the category with the unsplit phrase. So the narrow candidate never stated that thinking it quite likely that one is creating *any* cyberweapon triggers the ban; the candidates differed only when the probe set the knowing term true. | **Audit repair.** Each candidate has its own pair of binary open terms on (claude_instance, situation): `knowingly_engages_3_wide`, `thinks_quite_likely_3_wide` (category: “creating something that is a cyberweapon or malicious code and that could cause significant damage if deployed”) and `knowingly_engages_3_narrow`, `thinks_quite_likely_3_narrow` (category: “creating a cyberweapon or creating malicious code that could cause significant damage if deployed”). Wording, description and record of each term state its own candidate's category and attachment of “that could cause significant damage if deployed”. The guards keep the AT-0p shape per candidate: `( category(s) and knowingly(c, s) ) or thinks(c, s)`, c = var 1, s = var 0. `s03_scope.py` owns the terms and guards. The previous run's two shared terms are removed with every trace (vocabulary, open terms, stored relations, ledger, notes, probes, metrics; the trace check uses a pattern, because the new names start with the old ones). | READINGS |
| u0052.s01 | The record of `good_judgment` gave undeclared argument sorts (`action`, `context`). | **Small fault repaired.** The record is a pair of an instance of Claude and a situation (both declared sorts); the question stays what counts as good judgment. The rule and its guard are unchanged. | OPEN |
| u0126 | The ledger entry still listed `ethical_harm`, which `repair.py` removed from the document. | **Small fault repaired.** The entry lists no open term. The heading is still a label; its presupposition is not formalised. | LABELLED |
| u0173.s01 | Accepted only as correctly UNFORMALISED. | Note only: says that u0165.s03 has one pair of attitude terms per candidate. Still UNFORMALISED (modality/belief; “quite likely” is a quantity), not claimed. | UNFORMALISED |

## The plan repair AT-0p (attitudes plan, DRI AT2) at the start of this run

The plan text is the same as in the previous run, and that run already applied it in the plan's form: for hard constraint i = 1..7 the guard is `( C_i(s) and knowingly_engages_i(c, s) ) or thinks_quite_likely_i(c, s)`, with fourteen binary open terms on (claude_instance, situation), c = var 1, s = var 0, the case atoms explicit, and no unary `knowingly_<C>` / `thought_likely_<C>` terms left. This run **asserts that shape** (`repair_20261015T0600Z.py`, `check_at0p_shape`) and does not re-apply it; the audit of the previous run found it faithful for u0165.s01, s02 and s04 to s07 (and for u0165.s03 it found only the split above). The four probe kinds were measured again, per rule:

| Probe point | Plan expectation | Measured (7 of 7 rules) |
|---|---|---|
| case false, thinks-quite-likely true | SETTLED no | SETTLED no |
| case true, knowingly true | SETTLED no | SETTLED no |
| neither | UNDECIDED | UNDECIDED |
| case false, knowingly true | UNDECIDED | UNDECIDED |

Claimed bytes are unchanged at 2,951. Open terms: 50 (the previous run's 48, minus the two shared u0165.s03 terms, plus four). `ve document check`: premises `model`, route `superposed`, all 16 choices CONFLICT-FREE. The English round trip of the nested guard is still refused (`IdentityMetadataMismatch: block count`), as the previous run found; the repair is kept because the check passes (the plan's rule).

## Vocabulary change (DRI 2026-10-14 15:30Z, 1 and 2)

* (1) The carried sort `entity` is declared with the noun “thing” (plural “things”), never the reserved word “entity”. Only the noun changed; the sort's id, the constants and every formula are as before. The noun appears only in VE's own model descriptions, in no unit's text.
* (2) After the vocabulary changes (the four new terms, the two removed, the changed description of `cyberweapon_creation_permitted`, the noun), `nd.py all` was rerun and every existing unit compared with the previous run's: the only unit that differs is u0165.s03 (its list of open terms); the one fenced block (u0248) parses unchanged; sorts apart from the noun, constants, the graph and the document's body are identical (`metrics.json: vocabulary_change_check`).
* (3) Rust time limit: the default `VE_RUST_TIMEOUT` was kept unless a query ran under `prlimit --as=6442450944`; see the conclusion queries in `metrics.json` (`reruns` records the cap and the peak resident set of any capped run).

## Conflicts

VE reports none (CONFLICT-FREE in all 16 choices), so there is nothing to classify as a source conflict or a translation artefact.

## Audit-verified bytes

See `metrics.json`: the six hard constraints and u0123.s02.p1 that the audit accepted become audit-verified; u0052.s01 (record changed) and u0126 (ledger entry changed) are dropped until re-audited, and u0165.s03 is claimed but not audit-verified.
