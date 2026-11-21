# srccov-rl-openai-preparedness-1121: rule lines for PF's "translation omission" units

No DRI signature is needed and none is reserved; no DELTA row (section 5).

**Summary.** Status: built, and review F1 is fixed (section 7); the final gate is the chain's. Final commit: see `git log -1` on the branch (base `cebf4fd24f`).
Of the 104 in-scope units, 4 are KEPT and carried by one new rule line, `sr-sufficiency`: 4.2's lead-in "The SAG will make this determination based on:" and three of its four bullets. The fourth bullet, S0187 (quantifier-scope, out of scope), is quoted in the header and recorded as a loss in accounting.d1.txt. 100 are DROPPED, each with a reason below.
16 of the dropped units already had a drafted plain rule line. They are dropped only because Lean's limit of 64 regulated predicates is reached: D1 had 62 at main, and N2's probe adds one at run time.
No keyed answer moved. Open items: none. The predicate budget is under Notes for the DRI.

The /tmp log lines this report cites are copied into [evidence.md](evidence.md).

Map: `reviews/source-coverage-1119/` in manage-agents. I read:
- METHOD.md with the challenger amendments (4, 13 and 15c among them);
- openai-preparedness.md, rows-openai-preparedness*.tsv and the part-openai-preparedness-s8/s9.tsv tags;
- CHALLENGE.md, challenge2/RESULT.md, FEATURE-PAGE-CHALLENGE.md;
- the architect page's 'none: translation omission' row (fable-team/architect/srccov-features-20261120.md:17).

Scope: the units of the 12 named rows whose merged tag is exactly `none: translation omission`. That gives 104 units (`/tmp/pf_scope.tsv`, built from openai-preparedness.md's units table and the rows' `units` columns).

Sources and files:
- The pinned text is `pf-v2.txt`, sha256 `d2e3dd5b…` (`usecases/openai-preparedness/build_document.py:24-26`).
- Current main is `cebf4fd24f`.
- I opened no answers/, reports/, sealed-read, counted-read or diagnostic file, nor answer-key.json, cases.json, KEY-FREEZE.md or results.json beyond its regenerated diff.

## 0. Verify table (104 units)

Each unit was checked as follows:
- against the pinned text: offsets from units-openai-preparedness.tsv, read from `pf-v2.txt`;
- against current main:
  - every legend of environment.d1.json, after a check that its symbol is used by a rule or fact line (`pf_translation.parsed_rule` and the fact blocks);
  - the rule and fact lines;
  - the spans.json record of the unit's bytes;
  - the build's placements.

Two kinds of drop come from limits, not from the map:
- **The predicate budget.** A rule line needs a regulated predicate for its act. Lean refuses an environment with more than 64 (`lean/VE/SoftNorms/Soften.lean:471`; the same limit is in `Norms/Plain.lean:45`, `Norms/Tree.lean:304` and `Norms/Wire.lean:284`). D1 had 62 at main. `run.py:728` (N2's persuasion probe) adds a query-only 65th when one more is declared. My first run with all 16 drafted blocks failed there: `ve.errors.ResourceLimit: ResourceLimit: regulated predicates` (`/tmp/pfwork/run.log` of that run). So one slot was free. I gave it to the block that carries the most units.
- **The FACTS inventory.** A descriptive (non-duty) sentence cannot get a fact line. `facts.d1.ve` is pinned to PLAN 4.1's inventory (`tests/test_pf_fidelity_fix.py:432`), and a premise block in rules.d1.ve must be named by a keyed item (`:450`).

| unit | row | verdict | reason (file:line) |
|---|---|---|---|
| S0002 | srccov-openai-preparedness-7-1119 | DROPPED | mission commitment: a duty on every situation to develop and deploy misstates "committed to safely developing" (needs a scope reading and a "safely" judgment, no PLAN 3.2 open term); its relative clause is a descriptive claim |
| S0004 | srccov-openai-preparedness-13-1119 | DROPPED | already carried at main: the legend of `existing_at_publication` (`usecases/openai-preparedness/pf_vocabulary.py:244`), used by a rule or fact line, quotes it word for word |
| S0011 | srccov-openai-preparedness-13-1119 | DROPPED | already carried at main: the legend of `research_review` (`usecases/openai-preparedness/pf_vocabulary.py:632`), used by a rule or fact line, quotes it word for word |
| S0013 | srccov-openai-preparedness-13-1119 | DROPPED | time or cadence ("constantly") inside a soft-norms document: waits for srccov-design-deadline-cadence-1119 |
| S0016 | srccov-openai-preparedness-13-1119 | DROPPED | a descriptive or background claim, not a duty: a fact line would change PLAN 4.1's FACTS inventory (`tests/test_pf_fidelity_fix.py:432`) or add a rules.d1.ve premise no keyed item names (`tests/test_pf_fidelity_fix.py:450`); a rule line would turn the claim into a duty |
| S0019 | srccov-openai-preparedness-7-1119 | DROPPED | "particular caution" has no PLAN 3.2 open term, and "in these areas" without the threshold condition would widen the F2 safeguard duties; purpose clause "In order to" |
| S0020 | srccov-openai-preparedness-7-1119 | DROPPED | lead-in (amendment 8) of S0021-S0029: no line carries its items (S0021 and S0027 wait on the predicate budget, S0022 (temporal) and S0024 (modality) are out of scope, the rest are dropped below), so no line can carry its force |
| S0021 | srccov-openai-preparedness-7-1119 | DROPPED | its rule line needs a new regulated predicate: Lean's soft-norms limit is 64 (`lean/VE/SoftNorms/Soften.lean:471`), D1 had 62 at main and N2's probe adds one at run time (`usecases/openai-preparedness/run.py:728`); the one free slot carries sr-sufficiency (4 units) |
| S0023 | srccov-openai-preparedness-13-1119 | DROPPED | purpose "designed to detect" about a design, not a duty: attributed, attitude or evaluative content waits for srccov-design-attributed-1119 |
| S0027 | srccov-openai-preparedness-7-1119 | DROPPED | its rule line needs a new regulated predicate: Lean's soft-norms limit is 64 (`lean/VE/SoftNorms/Soften.lean:471`), D1 had 62 at main and N2's probe adds one at run time (`usecases/openai-preparedness/run.py:728`); the one free slot carries sr-sufficiency (4 units) |
| S0028 | srccov-openai-preparedness-7-1119 | DROPPED | already carried at main: the legend of `existing_at_publication` (`usecases/openai-preparedness/pf_vocabulary.py:244`), used by a rule or fact line, quotes it word for word |
| S0029 | srccov-openai-preparedness-7-1119 | DROPPED | needs two lines of different force (Leadership "can approve or reject", a permission; SSC "provides oversight", a duty); a unit routes to one block (`usecases/openai-preparedness/build_document.py:383-387`), and p4-u31 also holds S0030 |
| S0030 | srccov-openai-preparedness-13-1119 | DROPPED | heading and lead-in of 1.1's rationale list (S0031-S0042), whose items are descriptive and dropped |
| S0031 | srccov-openai-preparedness-13-1119 | DROPPED | a descriptive or background claim, not a duty: a fact line would change PLAN 4.1's FACTS inventory (`tests/test_pf_fidelity_fix.py:432`) or add a rules.d1.ve premise no keyed item names (`tests/test_pf_fidelity_fix.py:450`); a rule line would turn the claim into a duty |
| S0032 | srccov-openai-preparedness-13-1119 | DROPPED | time or cadence ("Until now") inside a soft-norms document: waits for srccov-design-deadline-cadence-1119 |
| S0033 | srccov-openai-preparedness-13-1119 | DROPPED | time or cadence ("so far", "yet") inside a soft-norms document: waits for srccov-design-deadline-cadence-1119 |
| S0034 | srccov-openai-preparedness-13-1119 | DROPPED | time or cadence ("soon") inside a soft-norms document: waits for srccov-design-deadline-cadence-1119 |
| S0035 | srccov-openai-preparedness-8-1119,srccov-openai-preparedness-13-1119 | DROPPED | a descriptive or background claim, not a duty: a fact line would change PLAN 4.1's FACTS inventory (`tests/test_pf_fidelity_fix.py:432`) or add a rules.d1.ve premise no keyed item names (`tests/test_pf_fidelity_fix.py:450`); a rule line would turn the claim into a duty |
| S0036 | srccov-openai-preparedness-13-1119 | DROPPED | a descriptive or background claim, not a duty: a fact line would change PLAN 4.1's FACTS inventory (`tests/test_pf_fidelity_fix.py:432`) or add a rules.d1.ve premise no keyed item names (`tests/test_pf_fidelity_fix.py:450`); a rule line would turn the claim into a duty |
| S0037 | srccov-openai-preparedness-13-1119 | DROPPED | time or cadence ("Today") inside a soft-norms document: waits for srccov-design-deadline-cadence-1119 |
| S0038 | srccov-openai-preparedness-13-1119 | DROPPED | evaluation "it's important" and the consequence "As a result": attributed, attitude or evaluative content waits for srccov-design-attributed-1119 |
| S0039 | srccov-openai-preparedness-13-1119 | DROPPED | evaluation "makes it important": attributed, attitude or evaluative content waits for srccov-design-attributed-1119 |
| S0040 | srccov-openai-preparedness-13-1119 | DROPPED | evaluation "more important than ever": attributed, attitude or evaluative content waits for srccov-design-attributed-1119 |
| S0041 | srccov-openai-preparedness-13-1119 | DROPPED | attitude "built conviction": attributed, attitude or evaluative content waits for srccov-design-attributed-1119 |
| S0042 | srccov-openai-preparedness-13-1119 | DROPPED | time or cadence ("The past year") inside a soft-norms document: waits for srccov-design-deadline-cadence-1119 |
| S0043 | srccov-openai-preparedness-8-1119 | DROPPED | spans unit p5-u45 also holds the descriptive "This includes …" sentence (dropped); splitting the spans unit renumbers every later unit id (`usecases/openai-preparedness/build_document.py:282`, `:400`) |
| S0044 | srccov-openai-preparedness-8-1119 | DROPPED | its rule line needs a new regulated predicate: Lean's soft-norms limit is 64 (`lean/VE/SoftNorms/Soften.lean:471`), D1 had 62 at main and N2's probe adds one at run time (`usecases/openai-preparedness/run.py:728`); the one free slot carries sr-sufficiency (4 units) |
| S0051 | srccov-openai-preparedness-8-1119 | DROPPED | time or cadence ("periodically") inside a soft-norms document: waits for srccov-design-deadline-cadence-1119 |
| S0061 | srccov-openai-preparedness-13-1119 | DROPPED | spans unit p5-u61 also holds the sentence "Critical capabilities require safeguards even during the development …" and footnote 2; splitting the spans unit renumbers every later unit id (`usecases/openai-preparedness/build_document.py:282`, `:400`) |
| S0078 | srccov-openai-preparedness-9-1119 | DROPPED | its spans unit already holds placement rs1-contrib-cyb (`usecases/openai-preparedness/build_document.py:49`); the build refuses two translations in one unit (`usecases/openai-preparedness/build_document.py:386`) |
| S0086 | srccov-openai-preparedness-9-1119 | DROPPED | time or cadence ("by then", "at this earlier milestone") inside a soft-norms document: waits for srccov-design-deadline-cadence-1119 |
| S0091 | srccov-openai-preparedness-8-1119 | DROPPED | already carried at main: the legend of `research_review` (`usecases/openai-preparedness/pf_vocabulary.py:632`), used by a rule or fact line, quotes it word for word |
| S0092 | srccov-openai-preparedness-8-1119 | DROPPED | already carried at main: the legend of `research_review` (`usecases/openai-preparedness/pf_vocabulary.py:632`), used by a rule or fact line, quotes it word for word |
| S0094 | srccov-openai-preparedness-8-1119 | DROPPED | already carried at main: the legend of `research_review` (`usecases/openai-preparedness/pf_vocabulary.py:632`), used by a rule or fact line, quotes it word for word |
| S0098 | srccov-openai-preparedness-8-1119 | DROPPED | time or cadence ("As this category matures") inside a soft-norms document: waits for srccov-design-deadline-cadence-1119 |
| S0104 | srccov-openai-preparedness-13-1119 | DROPPED | a descriptive or background claim, not a duty: a fact line would change PLAN 4.1's FACTS inventory (`tests/test_pf_fidelity_fix.py:432`) or add a rules.d1.ve premise no keyed item names (`tests/test_pf_fidelity_fix.py:450`); a rule line would turn the claim into a duty |
| S0106 | srccov-openai-preparedness-13-1119 | DROPPED | a descriptive or background claim, not a duty: a fact line would change PLAN 4.1's FACTS inventory (`tests/test_pf_fidelity_fix.py:432`) or add a rules.d1.ve premise no keyed item names (`tests/test_pf_fidelity_fix.py:450`); a rule line would turn the claim into a duty |
| S0108 | srccov-openai-preparedness-13-1119 | DROPPED | time or cadence ("now") inside a soft-norms document: waits for srccov-design-deadline-cadence-1119 |
| S0109 | srccov-openai-preparedness-13-1119 | DROPPED | a descriptive or background claim, not a duty: a fact line would change PLAN 4.1's FACTS inventory (`tests/test_pf_fidelity_fix.py:432`) or add a rules.d1.ve premise no keyed item names (`tests/test_pf_fidelity_fix.py:450`); a rule line would turn the claim into a duty |
| S0110 | srccov-openai-preparedness-13-1119 | DROPPED | a descriptive or background claim, not a duty: a fact line would change PLAN 4.1's FACTS inventory (`tests/test_pf_fidelity_fix.py:432`) or add a rules.d1.ve premise no keyed item names (`tests/test_pf_fidelity_fix.py:450`); a rule line would turn the claim into a duty |
| S0111 | srccov-openai-preparedness-13-1119 | DROPPED | a descriptive or background claim, not a duty: a fact line would change PLAN 4.1's FACTS inventory (`tests/test_pf_fidelity_fix.py:432`) or add a rules.d1.ve premise no keyed item names (`tests/test_pf_fidelity_fix.py:450`); a rule line would turn the claim into a duty |
| S0112 | srccov-openai-preparedness-13-1119 | DROPPED | a descriptive or background claim, not a duty: a fact line would change PLAN 4.1's FACTS inventory (`tests/test_pf_fidelity_fix.py:432`) or add a rules.d1.ve premise no keyed item names (`tests/test_pf_fidelity_fix.py:450`); a rule line would turn the claim into a duty |
| S0113 | srccov-openai-preparedness-10-1119 | DROPPED | its rule line needs a new regulated predicate: Lean's soft-norms limit is 64 (`lean/VE/SoftNorms/Soften.lean:471`), D1 had 62 at main and N2's probe adds one at run time (`usecases/openai-preparedness/run.py:728`); the one free slot carries sr-sufficiency (4 units) |
| S0115 | srccov-openai-preparedness-8-1119,srccov-openai-preparedness-10-1119 | DROPPED | its rule line needs a new regulated predicate: Lean's soft-norms limit is 64 (`lean/VE/SoftNorms/Soften.lean:471`), D1 had 62 at main and N2's probe adds one at run time (`usecases/openai-preparedness/run.py:728`); the one free slot carries sr-sufficiency (4 units) |
| S0116 | srccov-openai-preparedness-10-1119 | DROPPED | an attributed norm (what the Model Spec prohibits) in the persuasion passage RS15 reads (`usecases/openai-preparedness/build_document.py:101`): attributed, attitude or evaluative content waits for srccov-design-attributed-1119 |
| S0117 | srccov-openai-preparedness-10-1119 | DROPPED | the persuasion passage RS15 reads (`usecases/openai-preparedness/build_document.py:101`): an "always" line would decide what RS15 leaves open: attributed, attitude or evaluative content waits for srccov-design-attributed-1119 |
| S0119 | srccov-openai-preparedness-13-1119 | DROPPED | a descriptive or background claim, not a duty: a fact line would change PLAN 4.1's FACTS inventory (`tests/test_pf_fidelity_fix.py:432`) or add a rules.d1.ve premise no keyed item names (`tests/test_pf_fidelity_fix.py:450`); a rule line would turn the claim into a duty |
| S0120 | srccov-openai-preparedness-13-1119 | DROPPED | spans unit p9-u132 also holds S0119 (descriptive, dropped); splitting the spans unit renumbers every later unit id (`usecases/openai-preparedness/build_document.py:282`, `:400`) |
| S0122 | srccov-openai-preparedness-11-1119 | DROPPED | "should be tailored": a should-rule is a default and must belong to a reading set (`usecases/openai-preparedness/stage0.py:176-178`); a new reading set is beyond a plain line |
| S0124 | srccov-openai-preparedness-11-1119 | DROPPED | its rule line needs a new regulated predicate: Lean's soft-norms limit is 64 (`lean/VE/SoftNorms/Soften.lean:471`), D1 had 62 at main and N2's probe adds one at run time (`usecases/openai-preparedness/run.py:728`); the one free slot carries sr-sufficiency (4 units) |
| S0125 | srccov-openai-preparedness-8-1119,srccov-openai-preparedness-11-1119 | DROPPED | its rule line needs a new regulated predicate: Lean's soft-norms limit is 64 (`lean/VE/SoftNorms/Soften.lean:471`), D1 had 62 at main and N2's probe adds one at run time (`usecases/openai-preparedness/run.py:728`); the one free slot carries sr-sufficiency (4 units) |
| S0126 | srccov-openai-preparedness-13-1119 | DROPPED | lead-in of 3.1's two evaluation forms (S0127-S0130: definitions) and a count "two"; its items are not carried here |
| S0131 | srccov-openai-preparedness-13-1119 | DROPPED | the example box of 3.1 ("An example of …", "our current evaluations"): an illustration; a rule line would make it a duty |
| S0132 | srccov-openai-preparedness-13-1119 | DROPPED | the example box of 3.1 ("An example of …", "our current evaluations"): an illustration; a rule line would make it a duty |
| S0133 | srccov-openai-preparedness-13-1119 | DROPPED | the example box of 3.1 ("An example of …", "our current evaluations"): an illustration; a rule line would make it a duty |
| S0145 | srccov-openai-preparedness-11-1119 | DROPPED | already carried at main: the legend of `reached` (`usecases/openai-preparedness/pf_vocabulary.py:189`), used by a rule or fact line, quotes it word for word |
| S0147 | srccov-openai-preparedness-11-1119 | DROPPED | lead-in of 3.3's next steps: S0148 is reading RS16 (`usecases/openai-preparedness/build_document.py:159`), S0149 is dropped (occupied unit) |
| S0149 | srccov-openai-preparedness-11-1119 | DROPPED | its spans unit already holds placement rs8-distilled (`usecases/openai-preparedness/build_document.py:62`); the build refuses two translations in one unit (`usecases/openai-preparedness/build_document.py:386`) |
| S0151 | srccov-openai-preparedness-11-1119 | DROPPED | evaluation "This is appropriate" (no duty or permission is granted): attributed, attitude or evaluative content waits for srccov-design-attributed-1119 |
| S0153 | srccov-openai-preparedness-13-1119 | DROPPED | no claim for a line to carry (navigation, table header, label, caption, pointer or heading); the repair is a record, not a rule line |
| S0155 | srccov-openai-preparedness-8-1119,srccov-openai-preparedness-12-1119 | DROPPED | its spans unit already holds placement f8-start (`usecases/openai-preparedness/build_document.py:67`); the build refuses two translations in one unit (`usecases/openai-preparedness/build_document.py:386`) |
| S0160 | srccov-openai-preparedness-12-1119 | DROPPED | already carried at main: the legend of `existing_at_publication` (`usecases/openai-preparedness/pf_vocabulary.py:244`), used by a rule or fact line, quotes it word for word |
| S0163 | srccov-openai-preparedness-12-1119 | DROPPED | its spans unit already holds placement f9-report (`usecases/openai-preparedness/build_document.py:68`); the build refuses two translations in one unit (`usecases/openai-preparedness/build_document.py:386`) |
| S0171 | srccov-openai-preparedness-12-1119 | KEPT | 4.2 lead-in and three of its four bullets (the fourth, S0187, is quoted and recorded as a loss): block sr-sufficiency (`usecases/openai-preparedness/rules.d1.ve:187-188`), act `sufficiency_basis` (`usecases/openai-preparedness/pf_vocabulary.py:775`) |
| S0172 | srccov-openai-preparedness-12-1119 | KEPT | 4.2 lead-in and three of its four bullets (the fourth, S0187, is quoted and recorded as a loss): block sr-sufficiency (`usecases/openai-preparedness/rules.d1.ve:187-188`), act `sufficiency_basis` (`usecases/openai-preparedness/pf_vocabulary.py:775`) |
| S0173 | srccov-openai-preparedness-12-1119 | KEPT | 4.2 lead-in and three of its four bullets (the fourth, S0187, is quoted and recorded as a loss): block sr-sufficiency (`usecases/openai-preparedness/rules.d1.ve:187-188`), act `sufficiency_basis` (`usecases/openai-preparedness/pf_vocabulary.py:775`) |
| S0174 | srccov-openai-preparedness-13-1119 | DROPPED | no claim for a line to carry (navigation, table header, label, caption, pointer or heading); the repair is a record, not a rule line |
| S0175 | srccov-openai-preparedness-13-1119 | DROPPED | already carried at main: the legend of `misuse_safeguards` (`usecases/openai-preparedness/pf_vocabulary.py:420`), used by a rule or fact line, quotes it word for word |
| S0177 | srccov-openai-preparedness-13-1119 | DROPPED | Table 3 "Potential claims" cell: a claim a safeguards case may establish, not a duty; Appendix C's own wording of the claim is in the `misuse_safeguards` / `alignment_safeguards` legends (`usecases/openai-preparedness/pf_vocabulary.py:420`, `:487`) |
| S0178 | srccov-openai-preparedness-13-1119 | DROPPED | no claim for a line to carry (navigation, table header, label, caption, pointer or heading); the repair is a record, not a rule line |
| S0179 | srccov-openai-preparedness-13-1119 | DROPPED | already carried at main: the legend of `alignment_safeguards` (`usecases/openai-preparedness/pf_vocabulary.py:487`), used by a rule or fact line, quotes it word for word |
| S0181 | srccov-openai-preparedness-13-1119 | DROPPED | already carried at main: the legend of `alignment_safeguards` (`usecases/openai-preparedness/pf_vocabulary.py:487`), used by a rule or fact line, quotes it word for word |
| S0182 | srccov-openai-preparedness-13-1119 | DROPPED | already carried at main: the legend of `alignment_safeguards` (`usecases/openai-preparedness/pf_vocabulary.py:487`), used by a rule or fact line, quotes it word for word |
| S0183 | srccov-openai-preparedness-13-1119 | DROPPED | Table 3 "Potential claims" cell: a claim a safeguards case may establish, not a duty; Appendix C's own wording of the claim is in the `misuse_safeguards` / `alignment_safeguards` legends (`usecases/openai-preparedness/pf_vocabulary.py:420`, `:487`) |
| S0184 | srccov-openai-preparedness-13-1119 | DROPPED | no claim for a line to carry (navigation, table header, label, caption, pointer or heading); the repair is a record, not a rule line |
| S0185 | srccov-openai-preparedness-13-1119 | DROPPED | no claim for a line to carry (navigation, table header, label, caption, pointer or heading); the repair is a record, not a rule line |
| S0186 | srccov-openai-preparedness-12-1119 | KEPT | 4.2 lead-in and three of its four bullets (the fourth, S0187, is quoted and recorded as a loss): block sr-sufficiency (`usecases/openai-preparedness/rules.d1.ve:187-188`), act `sufficiency_basis` (`usecases/openai-preparedness/pf_vocabulary.py:775`) |
| S0190 | srccov-openai-preparedness-23-1119 | DROPPED | lead-in of 4.2's decision points (S0191-S0192): no line carries its items (S0191 attitude, S0192 read through RS16; the following S0193 is modality), so no line can carry its force |
| S0191 | srccov-openai-preparedness-23-1119 | DROPPED | attitude "confident" in a "can" decision point: attributed, attitude or evaluative content waits for srccov-design-attributed-1119 |
| S0192 | srccov-openai-preparedness-23-1119 | DROPPED | 4.2's "SAG can …" decision points are options, which PF reads through a reading set for 3.3's list (RS16, `usecases/openai-preparedness/build_document.py:159`) |
| S0202 | srccov-openai-preparedness-25-1119 | DROPPED | "forecasted to reach" and the hedge "should be treated with extreme caution": attributed, attitude or evaluative content waits for srccov-design-attributed-1119 |
| S0205 | srccov-openai-preparedness-12-1119,srccov-openai-preparedness-25-1119 | DROPPED | its rule line needs a new regulated predicate: Lean's soft-norms limit is 64 (`lean/VE/SoftNorms/Soften.lean:471`), D1 had 62 at main and N2's probe adds one at run time (`usecases/openai-preparedness/run.py:728`); the one free slot carries sr-sufficiency (4 units) |
| S0210 | srccov-openai-preparedness-26-1119 | DROPPED | a descriptive or background claim, not a duty: a fact line would change PLAN 4.1's FACTS inventory (`tests/test_pf_fidelity_fix.py:432`) or add a rules.d1.ve premise no keyed item names (`tests/test_pf_fidelity_fix.py:450`); a rule line would turn the claim into a duty |
| S0222 | srccov-openai-preparedness-26-1119 | DROPPED | its rule line needs a new regulated predicate: Lean's soft-norms limit is 64 (`lean/VE/SoftNorms/Soften.lean:471`), D1 had 62 at main and N2's probe adds one at run time (`usecases/openai-preparedness/run.py:728`); the one free slot carries sr-sufficiency (4 units) |
| S0224 | srccov-openai-preparedness-26-1119 | DROPPED | "may opt" / "may choose": PF reads such "may" through a permission/might reading set (RS13, `usecases/openai-preparedness/build_document.py:177`) |
| S0226 | srccov-openai-preparedness-26-1119 | DROPPED | its rule line needs a new regulated predicate: Lean's soft-norms limit is 64 (`lean/VE/SoftNorms/Soften.lean:471`), D1 had 62 at main and N2's probe adds one at run time (`usecases/openai-preparedness/run.py:728`); the one free slot carries sr-sufficiency (4 units) |
| S0244 | srccov-openai-preparedness-28-1119 | DROPPED | its spans unit already holds placement rs15-threat-models (`usecases/openai-preparedness/build_document.py:102`); the build refuses two translations in one unit (`usecases/openai-preparedness/build_document.py:386`) |
| S0246 | srccov-openai-preparedness-28-1119 | DROPPED | change-log entry (history: "Provide more detail on"); the commitment it reports is 3.1's S0121, tagged modality (out of scope) |
| S0250 | srccov-openai-preparedness-28-1119 | DROPPED | intention "we are planning for" and "As we move toward" (change log): attributed, attitude or evaluative content waits for srccov-design-attributed-1119 |
| S0255 | srccov-openai-preparedness-13-1119 | DROPPED | already recorded at main: spans units p16-u267/u268 are LABELLED exposition (`usecases/openai-preparedness/build_document.py:124-125`) |
| S0256 | srccov-openai-preparedness-28-1119 | DROPPED | its rule line needs a new regulated predicate: Lean's soft-norms limit is 64 (`lean/VE/SoftNorms/Soften.lean:471`), D1 had 62 at main and N2's probe adds one at run time (`usecases/openai-preparedness/run.py:728`); the one free slot carries sr-sufficiency (4 units) |
| S0257 | srccov-openai-preparedness-28-1119 | DROPPED | "For covered launches" needs the `covered` guard, whose readers are pinned by ruling pf-split-units-20261115 (`tests/test_pf_fidelity_fix.py:523-527`); an unguarded line drops the condition |
| S0258 | srccov-openai-preparedness-27-1119 | DROPPED | its rule line needs a new regulated predicate: Lean's soft-norms limit is 64 (`lean/VE/SoftNorms/Soften.lean:471`), D1 had 62 at main and N2's probe adds one at run time (`usecases/openai-preparedness/run.py:728`); the one free slot carries sr-sufficiency (4 units) |
| S0259 | srccov-openai-preparedness-27-1119 | DROPPED | lead-in of Appendix B's SAG duties (S0260-S0263): no line carries its items (S0260 and S0263 wait on the predicate budget; S0261 (quantifier-scope) and S0262 are out of scope), so no line can carry its force |
| S0260 | srccov-openai-preparedness-27-1119 | DROPPED | its rule line needs a new regulated predicate: Lean's soft-norms limit is 64 (`lean/VE/SoftNorms/Soften.lean:471`), D1 had 62 at main and N2's probe adds one at run time (`usecases/openai-preparedness/run.py:728`); the one free slot carries sr-sufficiency (4 units) |
| S0263 | srccov-openai-preparedness-27-1119 | DROPPED | its rule line needs a new regulated predicate: Lean's soft-norms limit is 64 (`lean/VE/SoftNorms/Soften.lean:471`), D1 had 62 at main and N2's probe adds one at run time (`usecases/openai-preparedness/run.py:728`); the one free slot carries sr-sufficiency (4 units) |
| S0264 | srccov-openai-preparedness-27-1119 | DROPPED | its spans unit already holds placement rs7-without-sag (`usecases/openai-preparedness/build_document.py:95`); the build refuses two translations in one unit (`usecases/openai-preparedness/build_document.py:386`) |
| S0265 | srccov-openai-preparedness-8-1119,srccov-openai-preparedness-27-1119 | DROPPED | its rule line needs a new regulated predicate: Lean's soft-norms limit is 64 (`lean/VE/SoftNorms/Soften.lean:471`), D1 had 62 at main and N2's probe adds one at run time (`usecases/openai-preparedness/run.py:728`); the one free slot carries sr-sufficiency (4 units) |
| S0267 | srccov-openai-preparedness-27-1119 | DROPPED | "may opt" / "may choose": PF reads such "may" through a permission/might reading set (RS13, `usecases/openai-preparedness/build_document.py:177`) |
| S0269 | srccov-openai-preparedness-27-1119 | DROPPED | already carried at main: the legend of `chair_coordination` (`usecases/openai-preparedness/pf_vocabulary.py:747`), used by a rule or fact line, quotes it word for word |
| S0272 | srccov-openai-preparedness-27-1119 | DROPPED | already carried at main: the legend of `existing_at_publication` (`usecases/openai-preparedness/pf_vocabulary.py:244`), used by a rule or fact line, quotes it word for word |
| S0275 | srccov-openai-preparedness-13-1119 | DROPPED | no claim for a line to carry (navigation, table header, label, caption, pointer or heading); the repair is a record, not a rule line |
| S0276 | srccov-openai-preparedness-27-1119 | DROPPED | a descriptive or background claim, not a duty: a fact line would change PLAN 4.1's FACTS inventory (`tests/test_pf_fidelity_fix.py:432`) or add a rules.d1.ve premise no keyed item names (`tests/test_pf_fidelity_fix.py:450`); a rule line would turn the claim into a duty |
| S0277 | srccov-openai-preparedness-27-1119 | DROPPED | its rule line needs a new regulated predicate: Lean's soft-norms limit is 64 (`lean/VE/SoftNorms/Soften.lean:471`), D1 had 62 at main and N2's probe adds one at run time (`usecases/openai-preparedness/run.py:728`); the one free slot carries sr-sufficiency (4 units) |

Totals: 4 KEPT. 100 DROPPED, broken down as:
- 16: the predicate budget;
- 14: already carried at main in a used legend;
- 1: already recorded;
- 6: spans unit occupied by another placement;
- 3: a spans unit shared with a dropped sentence;
- 1: two forces;
- 10: time or cadence, waiting for srccov-design-deadline-cadence-1119;
- 11: attributed, attitude or evaluative content, waiting for srccov-design-attributed-1119;
- 13: descriptive claims (no fact line);
- 6: lead-ins (the rule follows the list);
- 6: no claim (headings, captions);
- 3: example box;
- 2: Table 3 claim cells;
- 8: a reading set, a pinned guard, a scope reading or a change-log entry.

No unit needed definitions beside soft norms, so none waits for srccov-design-defs-softnorms-1119.

**The rule for a lead-in** (METHOD amendment 8, review F1). A lead-in is carried only by a line that carries its items with the lead-in's force. An item that line does not carry (out of scope, or dropped) is quoted in the block's header and recorded as a `loss` in accounting.d1.txt, so the omission is visible. The six dropped lead-ins (S0020, S0030, S0126, S0147, S0190, S0259) have no line that carries their items. S0171 is carried, and its fourth item S0187 is quoted and recorded as `loss 1`. `test_a_carried_lead_in_accounts_for_every_item` checks this over all seven lead-ins, from the map's `lead-in:` notes saved in the test.

## 1. What is carried

- **Line** (`usecases/openai-preparedness/rules.d1.ve:187-188`):
  `## sr-sufficiency | always | 4.2: “The SAG will make this determination based on:” “The level of capability …” “The associated risks …” “The safeguards in place …” “The baseline risk from other deployments, …” (the fourth bullet is not carried: …)`
  `Rule 1. Every situation must have SAG base safeguard sufficiency on capability plus risks plus safeguards.`
  - The header quotes the lead-in and all four bullets, five source sentences. The line names three of the four grounds, and the note after the quotes says that the fourth bullet (S0187) is not carried.
  - VE parses the line as the unconditional duty of `sufficiency_basis`: `test_the_line_parses_to_the_act_with_no_condition`.
- **Legend** (`pf_vocabulary.py:775`, environment.d1.json): `4.2: ` followed by the four quotations the line carries (the lead-in and three bullets), word for word from `pf-v2.txt`. Nothing outside the quotations but the section label.
  - The legend does not quote S0187. The accounting tool counts a used legend's words as carried, so quoting it there would hide the loss. f13-results and fn5-indicator likewise quote their lost words in the header only.
  - The act is `{0} have SAG base safeguard sufficiency on capability plus risks plus safeguards`: 80 characters, the case's act form.
  - The act uses "plus" as the act of `safeguards_during_development` does (`pf_vocabulary.py:522`), because the act form allows no comma.
- **Routing.** Four placements (`build_document.py:108-111`) put spans units p11-u181 (S0171), p11-u182 (S0172), p11-u183 (S0173) and p12-u196 (S0186) on the block.
  - With no clause map claimed, each is a blocked rule: `blocked_rule: sr-sufficiency`, UNFORMALISED, `unmapped_clause`, waits `["AP"]`. That is the conservative status: no unit becomes CHECKED.
  - The Table 3 units between the lead-in and the third carried bullet are not part of the list and are not routed.
  - S0187's own record p12-u197 is unchanged: UNFORMALISED, `quantifier_scope`, routed to no block (`test_the_fourth_bullet_keeps_its_own_record`).
  - `git diff` of spans.json changes exactly these four records.
- **Readings.** `pf_translation.py:40-41` adds the block to `RS0_STATEMENTS`, since "The SAG will make" is a future-tense process statement (PLAN 3.1). Without N1 it carries no norm, like the other RS0 lines.
- **Accounting.** `accounting.d1.txt:94` reads `sr-sufficiency | omits: "The baseline risk from other deployments, … for those models" loss 1` (class 1, a dropped conjunct). The tool lists S0187's ten content words as unaccounted and finds each in that entry (`--check` exit 0). With `omits: nothing` it refuses the block: `test_the_accounting_tool_refuses_omits_nothing_for_the_block`.

## 2. Regenerated files (the case's own scripts only)

| script | files |
|---|---|
| `pf_vocabulary.py` | environment.d1.json |
| `build_document.py` | spans.json, coverage.json (status bytes unchanged: `{'LABELLED': 6467, 'UNFORMALISED': 51446, 'OPEN': 9335, 'CHECKED': 170}`) |
| `source/quote_evidence.py` | docs/usecases/openai-preparedness/openai-preparedness-fidelity-fix/quote-hashes.json |
| `safetyfw_accounting.py openai-preparedness --source … --check --report …` | docs/usecases/safetyfw/openai-preparedness/accounting.json (`--check` exit 0) |
| `measure.py` | gaps.json, units.json (AP 118 → 121 units, readings 87 → 84; README family table updated) |
| `stage0.py` | stage0.json (P7 regulated_predicates 62 → 63) |
| `run.py` | results.json: only `metrics.M5.regulated_predicates` 62 → 63 and `metrics.M10.rules` 91 → 92 |
| `python -m conformance.english_lean_lexicon` | lexicon-report.json (PF row: symbols 140 → 141) |
| `python -m conformance.english_lean_seal` | corpus-seal.json (environment.d1.json and pf_translation.py hashes) |

Not changed:
- `tools/fidmech/manifests.py` pins no PF file (grep);
- `tests/data/fidmech/**` are frozen copies that no tool regenerates (as in srccov-openai-preparedness-1119).

`uv run python tools/regen_generated.py --check` reports only `route-cases` and `checker-pins`:
- the Rust release binary is not built in this worktree: "checker-pins: the Rust release binary is missing or not pinned";
- the route-case generator calls the Rust countermodel search.

Neither touches a PF file.

## 3. Answers touched

- **Keyed answers: none.** I compared results.json before (copied to /tmp/pfwork/results.main.json) and after `run.py` (exit 0, 28 min). `comparison`, `items` and `mutants` are equal (`True True True`). The only changed paths are `/metrics/M5/regulated_predicates` 62 → 63 and `/metrics/M10/rules` 91 → 92.
- **Why nothing moved:**
  - A/B/K/G answers ask named predicates. `sufficiency_basis` is in none of their atom lists.
  - The C conflicts pair rules on one predicate, and the new predicate has one rule.
  - N3 counts only `f<N>-` blocks (`run.py:849`).
  - N2 reads persuasion safeguards.
- **Reader inputs a later read must re-pin to:**
  - rules.d1.ve sha256 `583ee110…fbe4` (after review F1; `9a5be7c8…4dbe` before it);
  - environment.d1.json `0c884cbc…d345`;
  - spans.json `4413e7eb…529a`;
  - pf_vocabulary.py `5d6b2f31…8e7b`.
- **FREEZE.** The item merges at the commit the merge train makes from this branch's final HEAD, after the orchestrator's Monday 2026-11-23 freeze unless it merges first. It touches no keyed answer. A read on the repaired text re-pins to the four files above.

## 4. Condition test and seeded bugs

`tests/test_srccov_rl_openai_preparedness_1121.py` (new; selected: "changed ['tests/test_srccov_rl_openai_preparedness_1121.py']" in the selected run) checks, for each kept unit:
- the line and its regulated act are in rules.d1.ve / environment.d1.json;
- the line parses to the act;
- its spans.json record routes to the block, and only these four do;
- its sentence is one whole quotation of the legend and the header;
- with the pinned source (`tests/pinned_source.py`), the quotation equals the text in the unit's byte span under `quote_evidence.plain`, and the build places exactly these units.
- (review F1) for each of the item's seven lead-ins: a block that carries it routes each item, or quotes it in the header with a `loss` entry; a lead-in is routed exactly when this REPORT keeps it; the check refuses five mutants; the accounting tool refuses `omits: nothing`; S0187's record is unchanged.

Results:
- On main's PF files (`git checkout main -- usecases/openai-preparedness`, run, restore): **17 failed** (/tmp/pfwork/cond-main.log).
- At HEAD: **17 passed** (/tmp/pfwork/cond.log).

### Seeded bugs

Each was planted, the test file run, then restored with `git checkout`. Only Python and VE data were changed; no Lean or Rust.

| # | language, file | bug | failing tests |
|---|---|---|---|
| S1 | VE data, `usecases/openai-preparedness/rules.d1.ve` | remove the new line (block sr-sufficiency) | 8 failed, e.g. `test_the_rule_line_is_in_the_carrier_the_reader_is_shown`, `test_the_build_places_exactly_these_units_on_the_block` (/tmp/pfwork/seed-S1.log) |
| S2 | Python, `usecases/openai-preparedness/build_document.py` | drop S0173's placement, rebuild spans | `test_the_unit_routes_to_the_line[S0173]`, `test_only_these_units_route_to_the_line`, `test_the_build_places_exactly_these_units_on_the_block` (seed-S2.log) |
| S3 | Python, `usecases/openai-preparedness/pf_vocabulary.py` | legend "advice" → "guidance", regenerate | `test_the_legend_and_header_quote_the_sentence_whole[S0173]`, `test_the_legend_quotes_exactly_the_four_sentences`, `test_the_legend_text_is_the_source_text_of_the_unit[S0173]` (seed-S3.log) |
| S4 | Python, `usecases/openai-preparedness/pf_translation.py` | drop the block from RS0_STATEMENTS | `test_the_rule_line_is_in_the_carrier_the_reader_is_shown` (seed-S4.log) |
| S5 (review F1) | VE data, `usecases/openai-preparedness/rules.d1.ve` and `accounting.d1.txt` | the files of commit d6b73703: header without the fourth bullet, `omits: nothing` | 6 failed: `test_a_carried_lead_in_accounts_for_every_item`, `..._by_its_source_text`, `test_the_accounting_tool_refuses_omits_nothing_for_the_block`, `test_the_legend_quotes_the_carried_sentences_and_the_header_adds_the_fourth_bullet`, `test_the_rule_line_is_in_the_carrier_the_reader_is_shown`, and the `no fourth bullet` mutant, whose bullet is already absent (/tmp/t1121_f1.log, copied into evidence.md) |

Trust mutants:
- the light lane said NOT ("331 changed lines outside generated files > 150");
- the sweep ran through `mac-pytest.sh --trustmut`: "0 definitions, 0 mutants … 0 KILLED, 0 SURVIVOR" (/tmp/pfwork/tm.log), since no Lean changed.

## 5. DELTA

No row. What changed is translation content: one rule line, one predicate with its legend, four records routed.
- Unchanged checker outputs:
  - no verdict, keyed answer, diagnostic text, response field or fault order changed (section 3);
  - Lean, VE's Python package and Rust are unchanged;
  - trust is +0, and the kernel line count stays.
- The four records keep their status (UNFORMALISED); this matches srccov-openai-preparedness-1119's reading that a record change with no verdict move is not a DELTA row.

## 6. Tests run

- **Selected run.** `mac-pytest.sh --select -- --base cebf4fd24f --run` ran on GitHub Actions in 3 shards, 298 units (/tmp/pfwork/select.log).
  - It had one failure: `tests/test_pf_fidelity_fix.py::test_regulated_predicates_stay_within_64 - assert 63 == 62`. That test pins the count, and each earlier act addition bumped it. I set it to 63 with a comment and tightened the bound to `63 <= 64 - 1` (N2's probe takes the 64th).
  - Rerun: that test plus the condition file, "18 passed" (/tmp/pfwork/rerun.log).
  - 47 slow files selected for weak reasons were deferred to the chain gate by the selector.
- `uv run python tools/gate_collection.py --check --prebuilt`: "17 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers". No test was removed.
- No test in main-known-red.txt was touched. The full gate is the chain's, on the final HEAD.

- **Fix round (review F1), on commit 560b05ea52:**
  - `mac-pytest.sh --select -- --base cebf4fd24f --run` ran on GitHub Actions in 3 shards (run `srccov-rl-openai-preparedness-1121-560b05ea-t235537`): 63 of 678 units, 25 + 20 + 18 passed, exit 0 (/tmp/f1-select.log).
    - It selected `test_srccov_rl_openai_preparedness_1121.py`, `test_safetyfw_accounting.py`, `test_pf_fidelity_fix.py` and `test_srccov_openai_preparedness_1119.py`.
    - The selector deferred `tests/test_gate_quarantine.py` (weak reason, over 120 s) to the chain gate.
  - The condition file alone: 26 passed; on d6b73703's two PF files, 6 failed (S5).
  - `lake build`: "Build completed successfully (1478 jobs)". `python3 lean/audit.py`: PASS (898 files), with no Lean change.
  - `gate_collection.py --check --prebuilt`: "26 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers".
  - Not run: the full gate (the chain's) and `run.py --check`, since `run.py` reads neither headers nor sidecars.

SIZE (fix round, `git diff --stat d6b73703`): rules.d1.ve 1 line changed, accounting.d1.txt 1, build_document.py comment +3 -1, README +4 -2, test file +174 -2, plus this REPORT and evidence.md.

SIZE (build): 22 product (pf_vocabulary.py 8, build_document.py 7, pf_translation.py 4, rules.d1.ve 2, accounting.d1.txt 1), 161 tests (new file 155, test_pf_fidelity_fix.py 6), README 8 plus this REPORT (other hand-written).

## 7. Review fix (F1)

F1 (B): the 4.2 list has four bullets, and the kept lead-in S0171 was carried without the fourth, S0187, while the records said `omits: nothing` and "its three bullets".
- **Fix** (the review's second option): S0171 stays KEPT. The block's header quotes S0187 and says that the line does not carry it. accounting.d1.txt records S0187 as `loss 1`. The REPORT, README, the comment in build_document.py and the test docstring now say three of four bullets.
  - Why not the first option, dropping the block: that frees the 63rd predicate slot. The 16 drafted lines' reason, "dropped only because the budget is reached", would then be false, and carrying another of them is new work outside this fix.
- **Class:** a carried lead-in that drops an item without a record. One rule for every lead-in, stated in section 0, and `test_a_carried_lead_in_accounts_for_every_item` checks it over all seven lead-ins of the scope.
  - The S0020, S0190 and S0259 rows now give the true cause: no line carries their items. An out-of-scope item no longer reads as the cause, since S0171 is carried with one.
  - The accounting tool enforces the record on its own: with S0187 in the header, `omits: nothing` leaves ten words unaccounted.
- **Probe F1:** exit 1 before the fix, exit 0 after it. `test_a_carried_lead_in_accounts_for_every_item` covers it, along with the mutant `no fourth bullet in the header`.
- **Regenerated:** `docs/usecases/safetyfw/openai-preparedness/accounting.json` (blocks with a loss 15 → 16, class 1 17 → 18, quotes 122 → 123; `--check` exit 0) and `quote-hashes.json`. These pass `--check` unchanged: `build_document.py`, `measure.py`, `stage0.py`, `english_lean_seal`, `tools/regen_generated.py` (exit 0), and the lexicon report (byte-identical).
  - `run.py` reads no block header and no sidecar (grep), so results.json is unchanged.
- **No DELTA row:** the change is translation records only. No verdict, answer, diagnostic or trust moves.
- Tests: see section 6, fix round.

## Notes for the DRI

1. **PF's D1 vocabulary is at its regulated-predicate budget.** It now has 63 regulated predicates, plus N2's query-only probe, which makes 64, Lean's limit.
   - Every further PF rule line with a new act needs either a Lean limit change or a vocabulary split, and both are beyond a plain line.
   - Plain lines are drafted for 16 units: S0021, S0027, S0044, S0113, S0115, S0124, S0125, S0205, S0222, S0226, S0256, S0258, S0260, S0263, S0265, S0277. Each act fits the act form (≤ 80 characters) and each legend is a verbatim quote. They were withdrawn only for the budget.
   - If the limit is raised, they are a ready row.
2. **Descriptive and background sentences have no fact-line route.** PF's FACTS inventory is pinned to PLAN 4.1, so the background, rationale and illustration sentences (row 13's 46 'none' units) cannot get a fact line without changing the key design.
   - The route that exists is the legend (needs_rule_line=no), as the DRI's 2026-11-20 FACTS-wide rows on `existing_at_publication` used.
3. `tests/test_pf_fidelity_fix.py` is outside this item's path list. Its one edited assertion pins the count that this change moves.
4. Observed: `run.py` took 28 min here (README says about ten).

## Spec re-read

- Placement and routing against `build_document.py:402-406`: a `rule` placement with no clause map and no open term becomes a `blocked_rule` record.
- The act form against `tests/test_pf_fidelity_fix.py:579-583`.
- RS0 against `pf_translation.py:33-34` (PLAN 3.1).
- Carrier rule against METHOD amendment 4: the legend's predicate is used by the block's line.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer, relay or schema is read or changed.
2. PASS: deliverables 0-4 are sections 0, 1-2, 3 and 4. The diff has no Python copy of a Lean decision and no permanent report test (the condition test reads the case's files, not batch numbers). Siblings share only corpus-seal.json and lexicon-report.json, both regenerated.
3. PASS: seeded bugs S1-S4 (section 4), each failing named tests; trust mutants 0/0 (tm.log).
4. N.A.: no Python, Lean or Rust checker path changed. The case's answers are equal base vs head (section 3).
5. N.A.: no relayed field is read or bound.
6. PASS: the chain runs the gate on the final HEAD; local main has not moved since base `cebf4fd24f`.
7. PASS: no DELTA row and no trust growth (section 5).
8. PASS: output diff listed in sections 2-3 (results.json metrics only; spans: 4 records).
9. PASS: the selected run included the new file ("changed ['tests/test_srccov_rl_openai_preparedness_1121.py']"), and `test_pf_fidelity_fix.py`, which the change broke, was selected and caught.
10. N.A.: no Lean statement or proof.
11. N.A.: no budget or deadline code; the Lean limit is respected, not changed.
12. N.A.: one rule more in PF's D1; no checker change.
13. PASS: `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed; nothing removed.
14. PASS: each claim cites its command or log. Opposite direction: `test_only_these_units_route_to_the_line` (no other unit routes) and main's 17 failures.
15. PASS:
    - no overclaim: "none" in section 3 rests on the results.json comparison;
    - no silent cut: dropped units are listed with reasons, and the budget seam is in Notes;
    - every new check can fail: S1-S4;
    - limits: N.A.
