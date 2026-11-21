# srccov-rl-eligibility-1121: REPORT

No DRI signature needed. DELTA.md rows 1-3 cite R3, trust is +0, and no row is reserved.

**Summary.** Ready for the gate. HEAD is rebased on main e331b45943. This item merges at the merge commit the chain makes on top of that.
Of the 57 units in the 14 rows tagged 'none: translation omission', 7 are KEPT and carried by new rule lines G1-G7 in usecases/eligibility/translation.py. The other 50 are DROPPED, each with its reason below.
No answer changes: 269/269 answers, 32/32 mutants, 7337/7337 model premises (evidence/results-delta.json). There are no FOLLOW-UPs.

Files: S1 = usecases/eligibility/source/uksi-2025-969-made.txt, S2 = …/wfp-print.txt, Sch4 = …/ukpga-1995-26-sch4.txt, S3 = …/uksi-2005-3360-reg2.txt, T = usecases/eligibility/translation.py. METHOD = reviews/source-coverage-1119/METHOD.md (manage-agents).

## Verify table (deliverable 0)

The in-scope set was computed from rows-eligibility.tsv (the 14 named rows), keeping each unit that part-eligibility-s4.tsv or -s5.tsv tags 'none: translation omission'. That gives 57 distinct units; several sit in two rows. The map gives "about 52", an upper figure.
The source is unchanged between the map's pin e53db4e8fc and main: `git diff --stat e53db4e8fc HEAD -- usecases/eligibility` lists only environment.json, results.json and translation.py, and no file under source/.
None of the 7 kept units was carried at main: grep of translation.py, environment.json and rules.json at cd6d457912 for each key phrase ("affect your other benefits", "usually paid into", "tax deducted", "2 payments", "more tax each month", "Winter Fuel Payment charge", "tax calculation", "opt out") found 0 hits. The earlier srccov-eligibility-1119 item carried S0005, S0015 and S0033 only.

Drop reasons used below:
- **MODAL**: the content is a permission, possibility, expectation, duty or instruction ("can", "could", "may", "should", "must", "need to", or an imperative). The document declares only documents@1, order@0, relational-fol@0 and time@0 (T:285), so carrying it would need a profile the document does not declare. A plain line would assert as fact what the source states as a modal; METHOD:71 keeps `modality` for that case.
- **DECISION**: a correct carry changes an existing decision rule. A separate line beside that rule's biconditional gives a wrong reading. That is a decision-path change, out of scope.
- **LEAD-IN**: the unit is an item, or its lead-in or referent is a unit outside this item's scope (a different tag or row). Under METHOD:65 (amendment 8a), the item's clause map must carry the lead-in, so a line for the item alone does not carry it.
- **SCOPE**: Sch4 beyond para. 1 and S3 reg. 2(1)-(3),(6) state other benefits' rules. S1 reg. 1(3) cites only Sch4 para. 1 (S1:34) and S3 reg. 2(4),(5) (S1:27). The WFP rules use none of their terms.
- **HEDGE**: "usually" qualifies the rule itself (quantifier-scope). A plain line would state more than the source says.
- **FURNITURE**: a contact-channel line. It is not a rule or fact. Its siblings S0451 and S0487 are recorded as page furniture at T:209-212.

| unit | row(s) | verdict | reason |
|---|---|---|---|
| S0003 | 3 | DROPPED | MODAL ("may be cited as", S1:14). The commencement date also needs a constant with no value in the keyed fixture model (usecases/eligibility/run.py:286, fixture_model), which is a harness change. The vocabulary (T:285-289) has no sort for the instrument it names. |
| S0004 | 3 | DROPPED | S1:15, "extend to England and Wales only": legal extent is a fact about the instrument, and the vocabulary has no sort for it (T:285-289). Reading it as residence (R3) would be a misreading (map note). |
| S0060 | 6 | DROPPED | DECISION + LEAD-IN. S1:91 is the lead-in of reg. 4(6), and its item S0062 is dropped. |
| S0062 | 6 | DROPPED | DECISION. S1:93 "regulation 5(2) applies" disapplies reg. 4(5). Carrying it means changing R12's formula (T:484, which cites 5(1) only). A separate line `5(2) -> not excluded_no_claim` beside R12's biconditional would entail that a 5(2) person claimed or was paid without a claim. Its referent S0064 is also dropped. |
| S0064 | 7 | DROPPED | MODAL ("must pay", S1:96). It also has a cross-reference (IAA 1999 s.115(1)) and a dated decision event, and it feeds reg. 4(6)(b), so it is DECISION too. |
| S0065 | 7 | DROPPED | S1:97: an evidential standard ("are sufficient evidence"). Shard s4 tags it attribution-evaluation, so it waits for srccov-design-attributed-1119. |
| S0215 | 15 | DROPPED | SCOPE + LEAD-IN. Sch4:244 is an item of S0214 (row 10, outside this item). |
| S0225 | 15 | DROPPED | SCOPE + LEAD-IN. Sch4:254 is an item of S0224 (row 10). Shard s5 tags it temporal. |
| S0235 | 15 | DROPPED | SCOPE + LEAD-IN. Sch4:264 sits beside S0234 (row 10). It is a counterfactual ("would have been satisfied on the assumption"); shard s5 tags it condition. |
| S0245 | 15 | DROPPED | SCOPE + LEAD-IN. Sch4:274 is the lead-in of S0246-S0247 (S0246 is tagged cross-reference). |
| S0301 | 18 | DROPPED | SCOPE + LEAD-IN. Sch4:379 is the words an amendment instruction substitutes; its lead-in S0300 is tagged cross-reference. They are not a statement in force. |
| S0308 | 18 | DROPPED | SCOPE + LEAD-IN. Sch4:386 is an item of S0307 (tagged condition). |
| S0309 | 18 | DROPPED | SCOPE + LEAD-IN. Sch4:387 is an item of S0307 (tagged condition). |
| S0315 | 18 | DROPPED | SCOPE + LEAD-IN. Sch4:393 is the words an instruction substitutes (lead-in S0314, cross-reference). Shard s4 classes it change log. |
| S0323 | 18 | DROPPED | SCOPE + LEAD-IN. Sch4:406 is an item of S0322 (cross-reference, "there is substituted"). |
| S0325 | 18 | DROPPED | SCOPE + LEAD-IN. Sch4:409 is a counterfactual ("would have been so entitled if S had retired"); shard s5 tags it condition. |
| S0335 | 18 | DROPPED | SCOPE. Sch4:419 is a lead-in to amounts conditioned on a date ("dies after 5th April 2000"); shard s5 tags it temporal. |
| S0345 | 18 | DROPPED | SCOPE + LEAD-IN. Sch4:429 is "one-half of that increase", an amount; shard s5 tags it quantity. Its lead-in S0335 is dropped. |
| S0359 | 19 | DROPPED | SCOPE + LEAD-IN. S3:4 is an item of S0358 (tagged exception). |
| S0360 | 19 | DROPPED | SCOPE + LEAD-IN. S3:5 is an item of S0358. "satisfies the Secretary of State that he will apply" is attributed content (wait: srccov-design-attributed-1119). |
| S0362 | 19 | DROPPED | SCOPE + LEAD-IN. S3:7 is an item of S0361 (tagged exception). |
| S0363 | 19 | DROPPED | SCOPE + LEAD-IN. S3:8 is an item of S0361, with attributed content as in S0360. |
| S0371 | 19 | DROPPED | SCOPE + LEAD-IN. S3:16 is an item of S0369 (tagged definition). It is a deeming rule ("shall be disregarded for the purpose of determining"). |
| S0384 | 14 | DROPPED | MODAL. S2:16 "You may get calls…" is a possibility. Its sibling S0386 is recorded as page furniture (T:209-212). |
| S0385 | 14 | DROPPED | MODAL. S2:16 "this could be a scam" is a possibility; shard s4 tags it modality. |
| S0387 | 14 | DROPPED | MODAL. S2:18 "You could also get:" is the lead-in of S0388-S0390. |
| S0388 | 14 | DROPPED | MODAL + LEAD-IN (S0387). S2:19 is another scheme; "certain benefits" names no set. |
| S0389 | 14 | DROPPED | MODAL + LEAD-IN (S0387). S2:20 is another scheme; "low-income household" is undefined. |
| S0390 | 14 | DROPPED | MODAL + LEAD-IN (S0387). S2:21 is another scheme with a cross-reference ("the rules in your area"). |
| S0392 | 21 | DROPPED | LEAD-IN. S2:25 takes the lowest class of its items (METHOD:65 (b)), and its item S0395 is dropped. |
| S0395 | 14, 21 | DROPPED | DECISION. S2:29 is a ground of not being eligible. R13b (T:491) makes `entitled` a biconditional over S1 reg. 4 only. A separate line `no public funds -> not entitled` beside it would entail that such a person falls under one of the reg. 4 exclusions, which is a wrong reading. |
| S0406 | 22 | KEPT | S2:39. G1 `entitled(applicant) -> not affects_other_benefits(applicant)`. |
| S0408 | 22 | DROPPED | S2:41 "by either:" followed by two labels (S2:42-43). A line `recovered -> by tax code or by tax return` needs a value for which way, and the keyed model (run.py:286) does not hold it. Supplying one would invent a fact and change the harness. |
| S0424 | 22 | KEPT | S2:64, under the heading S2:60. G2 `jointly_claims_benefits ∧ entitled -> paid_into_usual_account`. "usually" is inside the account's description, not a hedge on the rule. |
| S0425 | 14, 22 | DROPPED | DECISION. S2:65 "(not as part of a joint claim)" restricts the R14/R15 amount rules (T:521 ff.) and introduces labels S2:66-68. |
| S0435 | 14, 23 | DROPPED | DECISION + MODAL. S2:88 "you need to claim if either…" is a condition on R12's input paid_without_claim (T:484, T:104) over a 12-benefit list (S2:76-87) outside the vocabulary. Shard s5 tags it condition. |
| S0436 | 23 | DROPPED | MODAL. S2:92 "You can claim… by:" is a permission; its labels carry start dates (S2:93-94). |
| S0438 | 23 | DROPPED | MODAL. S2:97 is an imperative ("Fill in… and send it"). |
| S0439 | 23 | DROPPED | MODAL. S2:103 "You can challenge a decision" is a permission. |
| S0443 | 24 | DROPPED | MODAL. S2:106 "You should get a letter" is an expectation and the lead-in of S0444. |
| S0444 | 24 | DROPPED | HEDGE + LEAD-IN (S0443). S2:108: "this is usually the same account". |
| S0445 | 14, 24 | DROPPED | MODAL. S2:109 is an imperative ("contact the Winter Fuel Payment Centre"); shard s5 tags it temporal. |
| S0452 | 25 | DROPPED | FURNITURE (S2:124, the Relay UK number). |
| S0453 | 25 | DROPPED | FURNITURE (S2:125, the BSL relay service). |
| S0461 | 26 | DROPPED | HEDGE. S2:142 "HMRC will usually collect…". |
| S0465 | 14, 26 | KEPT | S2:145 (second sentence). "This" is the tax-code change of the same line and of the heading S2:144. G3 `tax_code_changed -> tax_deducted_increases`. |
| S0467 | 26 | KEPT | S2:148, under the heading S2:147. G4 `two_payments_to_collect -> two_payments_through_tax_code`. |
| S0468 | 26 | KEPT | S2:148 (second sentence). G5 `two_payments_through_tax_code -> more_tax_each_month`. |
| S0472 | 26 | DROPPED | MODAL. S2:153 "You must include…" is a duty, and "each year you get it" is a cadence. |
| S0474 | 26 | KEPT | S2:154 (second sentence). "It" is the amount on the Self Assessment return (S2:43, "adding the amount to your Self Assessment tax return"). G6 `added_to_tax_return -> shown_as_wfp_charge ∧ in_tax_calculation`. |
| S0475 | 14, 26 | DROPPED | MODAL. S2:156 "You cannot pay back…" is an ability; shard s4 notes also:modality. |
| S0481 | 27 | DROPPED | MODAL. S2:164 "You can no longer opt of…" is a permission with a period. |
| S0483 | 27 | KEPT | S2:166. G7 `entitled ∧ not opted_out ∧ income > £35,000 -> amount > 0 ∧ recovered`. The `entitled` conjunct is the narrower reading ("you'll receive" presumes eligibility). |
| S0484 | 27 | DROPPED | MODAL. S2:168 "You can opt in again…" is a permission. |
| S0485 | 14, 27 | DROPPED | MODAL + LEAD-IN. S2:168 "you need to contact them": "them" is in S0484, which is dropped. Shard s5 tags it temporal. |
| S0488 | 27 | DROPPED | FURNITURE (S2:178, the same as S0452). |
| S0489 | 27 | DROPPED | FURNITURE (S2:179, the same as S0453). |

No dropped unit needed definitions beside soft norms or a deadline inside a soft-norms document; eligibility is not a soft-norms document. S0065, S0360 and S0363 wait for srccov-design-attributed-1119.

## Units carried (deliverables 1-2)

- **Lines.** `guide_rules()` (T:558-584) returns G1-G7 for the applicant. `rules()` (T:590) puts them after the amount rules and before B1. Each rule's `source` is `S2:<line>, srccov-rl-eligibility-1121`. Each gloss is an English reading of the formula followed by the S2 sentence word for word.
- **Predicates.** GUIDE_PREDICATES (T:110-124) adds 12 base predicates with legends that quote S2 ("(S2: “…”)"). They are merged into FACT_PREDICATES, so the keyed model (run.py:294) gives each one an empty relation. No profile fact fixes them.
- **Unit record.** GUIDE_SENTENCES (T:128-136) maps rule -> (unit, S2 line, sentence). It is the document's record of which unit each line carries. The eligibility document has no spans.json; METHOD section 0 names T, rules.json and environment.json as its carriers.
- **Why no answer moves.** Each guide rule has `defines` [], so no staged step (run.py `Staged.premises_for`) reads it. Each holds when its guide predicates are false, which is how the keyed model sets them: 7337/7337 model premises are true (`usecases/eligibility/run.py` log /tmp/rl1121/run.log). The rules only add a new predicate in an antecedent, or a consequence of R16a and the amount rules (G7), so any old model extends with the guide predicates false. This is the argument for why answers hold; the run measures it below.
- **Modal strength per rule (build checklist 19).** G1-G7 come from S2 sentences in the plain future ("will", "'ll") or the present. None is deontic. G7's "you'll receive" is rendered as amount > GBP 0.00, the form probe P2 already uses (run.py:526).
- **Derived files**, all regenerated by their tools and never by hand:
  - `uv run python usecases/eligibility/run.py` rewrote environment.json, rules.json, results.json and RESULTS.md (7 min 14 s, exit 0; log /tmp/rl1121/run.log: "total": "269/269", "mutants_killed": "32/32", model_premises 7337 = model_premises_true).
  - `uv run python -m conformance.english_lean_seal` rewrote corpus-seal.json.
  - `uv run python -m conformance.english_lean_lexicon` rewrote lexicon-report.json (`{"valid": 43, "invalid": 0}`).
  - `uv run python tools/regen_generated.py --check` exits 0 after the rebase: "checked 43 entries" (/tmp/rl1121/regencheck2.log). Before the rebase, two entries (route-cases, checker-pins) failed only because this worktree had no Rust release binary (/tmp/rl1121/regencheck.log: "the Rust release binary is missing or not pinned").
  - tools/fidmech/manifests.py and tests/data/fidmech/wording-golden.json hold no eligibility entry (grep: 0 hits), so neither changes.

## Answers touched (deliverable 3)

No keyed answer or question changes status or verdict. evidence/results-delta.json (main cd6d457912's results.json against the regenerated one) has `answers_equal`, `staged_equal`, `mutants_equal`, `single_shot_status_and_certified_equal` and `summary_equal_except_model_premises` all true.
Every profile's premise set now includes G1-G7, so all 80 profiles (269 keyed answers) run under environment_id e7634ba7… (was 00315b75…), with lexicon_id 8307042b… (was a9d8e621…).
A later read pinned to the old environment_id, lexicon_id, rules.json or seal re-pins. The guide predicates are new terms; no existing legend changed.
No sealed-read, answers/, reports/ or counted-read file was opened. Statuses come only from the document's own entry point, run.py.

## Condition test (deliverable 4)

New file: tests/test_srccov_rl_eligibility_1121.py, 37 tests.
- For each kept unit:
  - the sentence is on its S2 line, read from the repo;
  - rules.json (the shown rule lines) has its rule; the gloss ends with the sentence (after `omit_norm`), `source` cites the S2 line, and the rule uses exactly the new predicates named for it;
  - GUIDE_SENTENCES routes the unit to that rule, line and sentence;
  - the record lists exactly the kept units.
- For each new predicate: its shown legend (environment.json) quotes S2 words that are in the source, and a kept rule uses it (METHOD amendment 4).
- The guide rules define nothing.
- The opposite direction: a gloss with the sentence cut off or one number changed fails the carry check. A legend quote with changed words, or without the "S2:" marker, fails the legend check.
- **Fails on main**: with main's usecases/eligibility checked out, "30 failed, 7 passed" (/tmp/rl1121/t-main.log). The 7 that pass are the source-line checks, which read only the unchanged source. On HEAD: "37 passed" (/tmp/rl1121/t-head.log).
- **Stays selected**: a probe commit that only appended a comment to translation.py selects it (evidence/selection-probe.txt).

## Seeded bugs (Python, usecases/eligibility/translation.py; mutants.json)

Script /tmp/rl1121/mutants.py, log /tmp/rl1121/mutants.log. For each mutant the script edited translation.py, rewrote environment.json and rules.json the way run.py writes them, ran the new test file, and restored with `git checkout`. `git status` was clean afterwards. All 6 were killed.

| id | behaviour | change | failing tests |
|---|---|---|---|
| M1 | a kept line exists (the task's seeded check: remove one new line) | G7 dropped from `guide_rules()` | `…has_its_rule_line_in_the_shown_rules[S0483]`, `…legend_quoting_the_source[opted_out]`, `…refuses_a_gloss_without_the_sentence`, `…define_nothing` |
| M2 | the line carries the sentence word for word | "£35,000" -> "£30,000" in G7's sentence | `…shown_rules[S0483]`, `…routes_to_its_rule[S0483]`, `…refuses_a_gloss…` |
| M3 | a legend quotes the source | opted_out's quote "opt out of" -> "opt in to" | `…legend_quoting_the_source[opted_out]`, `…refuses_words_not_in_the_source` |
| M4 | the rule uses its predicates | G2 without `jointly_claims_benefits` | `…shown_rules[S0424]`, `…legend_quoting_the_source[jointly_claims_benefits]` |
| M5 | no staged step reads a guide rule | `defines` = [entitled(applicant)] | `test_the_guide_rules_define_nothing` |
| M6 | the unit routes to its line | G1's line 39 -> 40 | `…shown_rules[S0406]`, `…routes_to_its_rule[S0406]` |

## Tests, trust, light lane

- Selected run on the pre-rebase HEAD 542d13d1e4 (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`) ran on GitHub Actions in 3 shards: 51 units, 51 passed, exit 0, 915 s (evidence/selected-run.txt). It deferred one slow file selected only for weak reasons, tests/test_relay_binding_inventory.py, to the chain gate.
- It included test_eligibility_wfp.py (with `test_recorded_summary` and the single-shot depth-cap test), test_srccov_eligibility_1119.py, test_defs_repair_eligibility_1119.py, test_english_lean_seal.py and test_english_lean_lexicon.py.
- tests/test_definitions_carried.py reads eligibility at its fixture's pinned trees by blob id (tools/defs_carried.py:1225-1227), so this change cannot affect it.
- The rebase onto e331b45943 brought only a sibling's REPORT, evidence and test (`git diff --stat cd6d457912 e331b45943`: 3 files), and no eligibility, seal or lexicon file. The selected run was not repeated; the chain gates the final HEAD.
- Light lane: `light-lane.py check` printed "NOT 1114 changed lines outside generated files > 150". The trust sweep `mac-pytest.sh --trustmut -- --json docs/infra/srccov-rl-eligibility-1121/evidence/trust-mutants.json` found "0 definitions, 0 mutants", exit 0, because no Lean changed.
- Trust: `uv run python tools/trust_map.py --check` reported "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0" and PASS (/tmp/rl1121/trustmap.log). Kernel lines are unchanged.
- Known-red tests on main (main-known-red.txt): none was touched.
- The full gate was not run here; the chain runs it on the final HEAD.

SIZE: 63 product (translation.py: 63 added, 2 changed), 165 tests, about 200 other hand-written lines (REPORT, DELTA). Generated: environment.json 72, rules.json 260, results.json 536, RESULTS.md 12, corpus-seal.json 4, lexicon-report.json 4, evidence 4 files.

## Spec re-read

- "write the rule (or fact) line(s) in the document's own declared profile … grounded word for word in the source": checked against the task's DELIVERABLES 1. G1-G7 use only relational-fol@0 connectives and the quantity comparisons already in the document (T:285). Each gloss ends with the S2 sentence, checked by `…has_its_rule_line_in_the_shown_rules[*]`.
- "a new predicate with a source-quoted legend in the same profile": each legend's quote is checked against S2 by `…legend_quoting_the_source[*]`.
- "update the document's span/record file so the unit routes to the new line": GUIDE_SENTENCES, checked by `…routes_to_its_rule[*]` and `…lists_exactly_the_kept_units`.
- METHOD amendment 4 (a legend counts only on a used symbol): checked by the predicate-use clause of `…legend_quoting_the_source[*]`.
- METHOD amendment 8a (lead-ins) and 14 (modality only when the deontic force is the content): applied in the verify table (LEAD-IN, MODAL).
- "An existing CHECKED answer that would change status or verdict stops that unit": none changes (evidence/results-delta.json).

## Notes for the DRI

- **S0395** (S2:29, people whose leave says they cannot claim public funds are not eligible) and **S0062/S0064** (S1 reg. 4(6)(b) and 5(2)) are real rules. Carrying them means changing R13b or R12, a decision-path change outside a "plain line" row. Today no profile has these facts, so no current answer is wrong.
- The contact lines S0452, S0453, S0488 and S0489, and the scam-warning sentences S0384 and S0385, read as page furniture like their recorded siblings (T:209-212). Recording them is outside this item. METHOD amendment 12 kept them from class 4 because they contain a number or a modal.
- S0003 (commencement date) could be carried by a fact line with a day constant if run.py's fixture_model gave that constant its value. That is a harness change, not taken here (the conservative option).
- In units-eligibility.tsv the `§` heading context for some S2 units is the wrong section (for example S0406 under "If you live in a care home"; at S2:39 it is under "3. How much you'll get"). I read the source file for context.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relay, schema or route changed (the diff is translation.py, the run's derived files, the seal, the lexicon, a test and docs).
2. Deliverables built, no rule broken: PASS. 0 is the verify table; 1 is G1-G7 and GUIDE_SENTENCES (commit "carry 7 guide sentences"); 2 is the regeneration (run.py, the seal, the lexicon; `regen_generated.py --check` exit 0); 3 is "Answers touched"; 4 is tests/test_srccov_rl_eligibility_1121.py. There is no permanent report test (D4); evidence is read from saved files.
3. Tests can fail: PASS, mutants M1-M6 (mutants.json, /tmp/rl1121/mutants.log), and "30 failed" on main (/tmp/rl1121/t-main.log).
4. Python, Lean and Rust agree: PASS. run.py: 269/269 documents admitted by Lean, 2352/2352 certificates accepted, 7337/7337 model premises true under Lean evaluation (/tmp/rl1121/run.log). No Lean or Rust code changed.
5. R8 binding: N.A., no field is read from a Lean answer.
6. Gate evidence matches the final HEAD: PASS. The branch is rebased on main e331b45943, and `regen_generated.py --check` exits 0 there. The chain gates the final HEAD.
7. No unsigned item: PASS. DELTA.md rows 1-3 cite R3, with tests named.
8. Every user-visible change in DELTA: PASS. results.json was diffed path by path (evidence/results-delta.json `changed_paths`: 10 path patterns, all in DELTA rows 2-3). The RESULTS.md step rows and the rules, legends and ids are rows 1-3.
9. Test selection finds the tests: PASS. A comment-only edit of translation.py selects the new test (evidence/selection-probe.txt).
10. Lean statements: N.A., no Lean change.
11. Budgets and deadlines: N.A., no limit or deadline code. The new tests have no sleeps or timeouts.
12. CPU and memory: N.A. Seven premises were added to a use-case run. run.py took 7 min 14 s against 6 min 2 s in srccov-eligibility-1119's run (wall time only, not a measure).
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. `test_the_carry_check_refuses_a_gloss_without_the_sentence` and `test_the_legend_check_refuses_words_not_in_the_source` test the refusal side, the claims cite /tmp/rl1121 logs or evidence files, and the spec re-read is above.
15. No overclaim, no silent cut, new checks can fail, limits: PASS. "No answer changes" is backed by evidence/results-delta.json and `test_recorded_summary`; "exactly the kept units" by `test_the_unit_record_lists_exactly_the_kept_units`. All 50 dropped units are named as dropped, not carried. Every new check has a mutant (M1-M6). No limit was added.
