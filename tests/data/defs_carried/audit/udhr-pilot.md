# udhr-pilot: definitions carried (shard 4, METHOD.md + challenger amendments)

Written 2026-11-19 by dri-defs-carried-s4-1119 (Opus 5.5). Analysis only; every row is a CANDIDATE.

**Pin and inputs.** Pin `3d6b459df4`, read with `git show`. No hash-pinned source: `usecases/pinned_sources.json` pins only FSF, RSP and PF, so the frozen source is the in-repo text at the pin (amendment 8), here the body prose of the translation file (the UDHR).
- VE text: `usecases/udhr-pilot/run-20261010T1400Z/translation.ve.md`, front matter (`units`, `environment`, `open_terms`). The front matter is one JSON line (line 2); the body is the source.
- Legends shown: the front-matter `environment.vocabulary` (8 predicates, 5 sorts, 0 constants) and the 53 `open_terms` entries (name + factors; they have no description field).
- Source: the body (UDHR Preamble and Articles 1-30), cited below as Article/paragraph.
- Keyed answers: none. `situations.py` and `witnesses.py` propose and re-check separating situations; neither keys an answer (their docstrings: "nothing here reads a verdict from Python"), so answers touched = `unknown`. Only their first 40 lines and a keyword grep were read.
- `reading_sets` (49) are VE text but neither carriers nor evidence (amendment 7). They were used for one thing only: to see which unit's reading uses which of the 8 predicates (u052, u112, u114 and u074's inline body), because no other part of the surface ties a predicate to a unit.
- Files actually read: translation.ve.md; situations.py (head + grep); witnesses.py (grep); a `git grep -l` of the pin for derived files. Not opened: SUMMARY.md, frozen-run.json, metrics.json, unmigrated.json, measure.py, migrate.py, summary.py, any answers/reports.

**Counts.**
- Units: 130. Rules (units with a VE meaning): 30, that is u074 (the one inline VE body: norm `no-compelled-association-membership` on `compel_association_membership_permitted`) and the 29 norm units whose meaning is `open` on named open terms. Skipped: 34 `meta`, 43 unformalised or attributed units, 3 norm units with an `unformalised` meaning (u019, u057, u058), and 20 `specified` norm units with no inline VE body (their content is only in reading sets).
- Terms: 66 declared (8 predicates, 5 sorts, 53 open terms). The 30 rules use 49 open-term occurrences (37 distinct open terms) and 1 predicate inline; 7 more predicates are reached only through reading sets.
- Larger than 40? No by rule count (30), but source-first was used anyway because only 6 rules hit a source definition. The other 24 rules and their open terms have NO SOURCE DEFINITION.
- Marker grep (amendment 2) on the body: 4 lines hit (109, 113, 139, 175). They gave 2 entries (D5, D6) and 2 were dismissed: 139 ("other means of social protection", not a definition) and 175 (Article 29(2), which states the rule itself). There are no bold lead-ins and no tables. A full read added D1-D4, D7 and D8. It also dismissed five rule-stating sentences: Article 2 second sentence (u020's own text), Article 13(2) "including his own", Article 24 "including reasonable limitation...", Article 25(1) "including food, clothing...", and Article 29(1) "the community in which alone...".
- Inventory: 8 entries (D1-D8).
- Verdicts on (rule, term) pairs: CARRIED 0; PARTIAL 1 (FRAGMENT 1); NOT CARRIED 9. One more term has NO SOURCE DEFINITION (reference out of source: D8). D5 and D6 hit no VE term.
- Candidate rows: P1 3, P2 0. One finding (D7) gets no row: see the notes.

**Source definitions inventory** (body of translation.ve.md).
- D1 (Article 2, sentence 1; kind 2, a list giving "distinction of any kind" its content): "Everyone is entitled to all the rights and freedoms set forth in this Declaration, without distinction of any kind, such as race, colour, sex, language, religion, political or other opinion, national or social origin, property, birth or other status."
- D2 (Article 7, sentence 2; kind 6, a reference inside the source): "any discrimination in violation of this Declaration". It resolves to D1.
- D3 (Article 14(1); kind 3, the named item that Article 14(2) cites as "This right"): "Everyone has the right to seek and to enjoy in other countries asylum from persecution."
- D4 (Article 16(3); kind 4, a definitional sentence): "The family is the natural and fundamental group unit of society and is entitled to protection by society and the State."
- D5 (Article 18; kind 1, "includes"): "Everyone has the right to freedom of thought, conscience and religion; this right includes freedom to change his religion or belief, and freedom, either alone or in community with others and in public or private, to manifest his religion or belief in teaching, practice, worship and observance."
- D6 (Article 19; kind 1, "includes"): "Everyone has the right to freedom of opinion and expression; this right includes freedom to hold opinions without interference and to seek, receive and impart information and ideas through any media and regardless of frontiers."
- D7 (Articles 2, 29(3) and 30; kind 3/6): "the rights and freedoms set forth in this Declaration" / "set forth herein". The target is the Declaration's own rights, Articles 3-27, which is the whole operative text.
- D8 (Articles 14(2) and 29(3)): "the purposes and principles of the United Nations". These are defined in the UN Charter, which is outside the frozen source: NO SOURCE DEFINITION (reference out of source).

| rule | term | source definition (quote, location) | carried? | where |
|---|---|---|---|---|
| u032 (Art 7 s1, open) | discrimination (open term) | D1 (Art 2 s1) | NOT CARRIED | The open-term factors "what counts as discrimination ; which distinctions are meant" pose the question and carry no content (helper 1/39). |
| u033a (Art 7 s2, open) | discrimination | D2 -> D1 | NOT CARRIED | as u032 |
| u033b (Art 7 s2, open) | discrimination ("such discrimination") | D2 -> D1 | NOT CARRIED | as u032 |
| u052 (Art 14(2), open) | asylum_right_covers_case ("This right") | D3 (Art 14(1)) | PARTIAL (FRAGMENT) | Predicate legend, with the citation "(Article 14, paragraph 1)" stripped: "The right to seek and to enjoy asylum may be invoked in the case of the prosecution" (helper 7/16). Clause map: "the right to seek and to enjoy" carried; "asylum" carried; "in other countries" missing; "from persecution" missing; "Everyone has" missing. |
| u052 | arises_from_acts_contrary_to_un, contrary_to_un_purposes_and_principles | D8 | NO SOURCE DEFINITION (reference out of source) | - |
| u052 | genuine, non_political_crime, arises_from_non_political_crime | none | NO SOURCE DEFINITION | - |
| u061 (Art 16(3), open) | protection_of_the_family ("family") | D4 | NOT CARRIED | Factors "what counts as protection of the family ; what society owes as distinct from the State" (helper 2/22). The `natural_group_unit` open term ("what counts as family") is used by no rule: u060, the first half of the sentence, is unformalised. |
| u100b (Art 26(2), open) | rights_and_freedoms_set_forth | D7 | NOT CARRIED | Factors "which items of the Declaration count as rights and freedoms" (a name only). |
| u112 (Art 29(3), open) | rights_and_freedoms_set_forth; exercise_of_declared_right | D7 | NOT CARRIED (2 pairs) | Legend "an exercise of a right or freedom set forth in this Declaration" (a name only). |
| u112 | contrary_to_un_purposes_and_principles, exercise_contrary_to_un | D8 | NO SOURCE DEFINITION (reference out of source) | - |
| u114 (Art 30, open) | rights_and_freedoms_set_forth; declaration_implies_destructive_right | D7 | NOT CARRIED (2 pairs) | Legend "...the destruction of any of the rights and freedoms set forth in it" (a name only). |
| u074 (Art 20(2)) | compel_association_membership_permitted; actor, person | none | NO SOURCE DEFINITION | - |
| 24 other open-meaning rules | their open terms (arbitrary, slavery, servitude, persecution, compulsory, merit, ...) | none | NO SOURCE DEFINITION | - |

**Candidate rows** (machine form: `rows-udhr-pilot.tsv`). Answers touched: `unknown` for every row (no keys).
- defs-udhr-pilot-1-1119 | P1 (FRAGMENT) | translation.ve.md front matter, `environment.vocabulary.predicates.asylum_right_covers_case.description` | append ' Article 14(1): "Everyone has the right to seek and to enjoy in other countries asylum from persecution."' (D3) | size 1 (the front matter is a single line; no file at the pin stores this document's environment id, see notes) | unknown.
- defs-udhr-pilot-2-1119 | P1 (NOT CARRIED; the open-term entry has no description field, so the planner must pick one: a new `description` key or a new factor) | translation.ve.md front matter, `open_terms[discrimination]` | append D1 verbatim | size 1 | unknown. Covers u032, u033a and u033b.
- defs-udhr-pilot-3-1119 | P1 (NOT CARRIED; same field question as row 2) | translation.ve.md front matter, `open_terms[protection_of_the_family]` | append D4 verbatim | size 1 | unknown. Covers u061.
- Total as one change: 1 changed line (all three appends are on front-matter line 2), plus whatever the planner's tool regenerates in the same line (reading-set `meaning_id`s, if they hash the environment).

**Notes.**
- D7 has no row. The definition is the whole of Articles 3-27, so no verbatim span fits a legend. Five pairs (u100b, u112 x2, u114 x2) stay NOT CARRIED. The planner decides whether to enumerate the rights, which would need a rule line or a list legend.
- D5 and D6 ("this right includes ...") are real definitions with no carrier. u066 and u070 are `specified` units with no inline VE body and only null reading contents. The "includes" clauses (u067, u068, u071a, u071b) are unformalised. A strict reader of those two rights gets no content from the VE surface at all, which is a coverage gap rather than a legend gap.
- Derived files: `git grep` of the pin finds no stored environment or manifest id for this document outside translation.ve.md. The reading-set model keys and `meaning_id`s inside the file may hash the environment. frozen-run.json (a forbidden input, not opened) may pin a document hash, and tests/test_readings_s1_pilot_rebuild.py names the file path. The planner should check both before sizing.
- Article 2 sentence 2 (u020) is the rule itself, so it was dismissed. Its open term `status_of_country_or_territory` lists the source's status list in its factors anyway.
