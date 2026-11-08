# jt-3b REPORT: a judgments@0 document's authored fences and the report's lines

DRI signature needed: none. Every DELTA row cites a standing ruling or a DRI decision file that signs it
(docs/judgment-terms/jt-3b/DELTA.md). Size overrun accepted by the DRI: reviews/dri-decisions-20261108-jt-3b-size.md item 1.
Open residual (honest version, DRI sprint decision item 2): the structure is checked; whether a reader understands
the legend and status lines is unmeasured, a named open residual, never counted as semantic coverage. Bytes 0 (estimate;
nothing is claimed before a pilot audit).

Plan: docs/spec/judgment-terms-PLAN.md at 4d1da4e6f, "JT-3" (:594-631) and 2.4 (:246-263); spec docs/spec/judgment-terms.md
8.1, 8.4, 9.2 and 9.5. Statement gate: JT-3's statements were accepted for jt-3; this item adds one statement (`lines_fits`,
the encoder theorem of the new report member) and changes none.

## DRI decisions

- reviews/dri-decisions-20261102-jt-3.md: item 1 signs the opt-in refusal; item 2 moves the document placement here;
  item 3 sets the per-predicate rule.
- reviews/dri-decisions-20261105-jt-3b.md: item 1 signs `ve document check` going from CheckerUnavailable to Lean's
  answer on a judgments@0 document with an English fence (the relay's proposal names the environment Lean reads a fence
  in, without the document layers), with conditions (a)-(e); item 2 corrects the base of the verdict row.
- reviews/dri-decisions-20261108-jt-3b-size.md item 1: deliverable (2) stays in jt-3b, accepted up to about 850
  hand-written lines (REPORT and DELTA not counted); nothing moves to jt-3c.

## Deliverables

| Task row | Delivered by | Test |
|---|---|---|
| (1) an authored fence of a judgments@0 document sends the bound names as `judgments`, mode `authoring` (`Env.boundNames`, set once in `check`, passed by `contentOf`; kept by `layeredIds` for a soft document's E″) | 6152ccace, ab084a640 | `UndeclaredExamples.lean` `refused` guards; `test_an_unbound_word_in_an_authored_fence_is_refused_with_lean_s_text`, `test_a_soft_document_s_fence_is_read_with_the_bound_names` |
| (1) translation fences unchanged | no code: the document mode reads every fence in `authoring` (`Document.lean` `contentOf`, the one `"mode"` it sends); no document path sends `translation` | n/a |
| (1) 9.5's refusal keeps its code `UndeclaredEvaluative` in the document's error | 6152ccace (`contentOf`'s `head`) | `refusal` guard; `REASONABLE` in `tests/test_judgments_document.py` (whole string) |
| (2) the report places jt-3's legend lines (with the decider) and neutral status lines, Lean's text (`JudgmentLines.legendLines`, `JudgmentLines.statusLine`; no second word function) | 6152ccace (`legendRows`, `statusRows`, `linesJson`, `encode`); `judgment_lines` in `ve document check` (`ve/document/report.py`) | `boundLines` guard, the three-term and `linesJson` guards (9159b939f, 43bf63d78); `test_the_report_places_lean_s_lines` |
| (3) the relay passes the field and the text and checks types and binding only (R8; Python holds no word list) | 6152ccace, 673097b48 (`_judgment_lines_bound`, schema `judgment_lines`) | `test_every_mutant_of_the_lines_is_refused`, `test_a_changed_word_of_the_text_is_lean_s`, `test_the_lines_are_there_exactly_under_the_profile` |
| (4) condition: unbound word refused by `ve document check`, Lean's text verbatim | 673097b48 | `test_an_unbound_word_in_an_authored_fence_is_refused_with_lean_s_text` |
| (4) condition: the same document without the profile byte-identical (J-λ) | 673097b48 | `test_without_the_profile_the_same_document_answers_byte_identically`; guard `refused (fenced plainProfiles …) == none` |
| (4) condition: a bound word answers as today | 673097b48 | `test_a_bound_word_answers_the_report_as_today` |
| (4) condition: per predicate, two predicates of one row, one bound, refuse the other | 673097b48 | `test_two_predicates_of_one_row_bind_one_by_one`; the two per-predicate guards |
| DRI 2026-11-05 (d): the judged and the plain document carry the same lexicon proposal | 673097b48 | `test_the_proposal_is_the_one_the_plain_document_carries` |
| Evaluator rule (every value once, charged against a limit) | the names are encoded once (`toJson J` in `check`) and charged with the vocabulary | `test_the_bound_names_are_charged_against_the_vocabulary_s_limit` |

Not delivered: none of the task's rows. The `judgment-line` mode stays jt-3c's (jt-3's REPORT, unchanged here).

Deviations: the judged-versus-twin tests of other items now set `judgment_lines` aside
(`tests/test_judgments_chain.py::verdict`, `tests/test_judgments_compose.py::test_ve_document_check_and_coverage_answer_as_the_twin`,
which also asserts the member is there exactly for `ve document check` under the profile), and
`tests/test_cardinality_lean.py::test_the_route_cases_answer_as_recorded` reads its own `cardinality-*` cases now that
route-cases.jsonl has two document cases of this item (4bca8a0e5). The assurance manifest pins Document.lean's new hash,
and the report's reviewed broad handler is now `_checked_report`, the same handler moved into a helper (a3e99912a).

## Seeded bugs

Each planted alone, the named check seen failing, the file restored (docs/judgment-terms/jt-3b/mutants.json):

| Id | File | Bug | Fails |
|---|---|---|---|
| L1 | lean/VE/Service/Document.lean (`contentOf`) | fences sent without `judgments` | UndeclaredExamples.lean:128, :131 |
| L2 | lean/VE/Service/Document.lean (`check`) | the names sent without `judgments@0` (J-λ) | UndeclaredExamples.lean:129 |
| L3 | lean/VE/Service/Document.lean (`legendRows`) | the legend line drops the decider | UndeclaredExamples.lean:148, :156 |
| P1 | ve/document/lean.py (`_lean_document`) | `judgment_lines` dropped from the report | `test_the_report_places_lean_s_lines` |
| P2 | ve/document/lean.py (`_judgment_lines_bound`) | any `judgment_lines` accepted | `test_every_mutant_of_the_lines_is_refused` (5 cases) |
| P3 | ve/document/lean.py (`_document_case`) | the proposal keeps the document layers (DRI (e)) | conditions (a), (b), (d): the three tests above |

Commands: `lake build VE.Service.UndeclaredExamples` (L1-L3: `error: VE/Service/UndeclaredExamples.lean:<line>:0: Expression`);
`uv run pytest -q tests/test_judgments_document.py -k …` and `tests/test_judgments_answer.py -k every_mutant_of_the_lines` (P1-P3).

R16 mutants per definition: docs/judgment-terms/jt-3b/trust-mutants.json, `uv run python tools/trust_mutants.py
--max-mutants 1000 --jobs 20 --build-timeout 3600 --test lean/VE/Service/UndeclaredExamples.lean --allow
docs/judgment-terms/jt-3b/trust-mutants-allow.json`, a full run at 43bf63d78 rescored with the final allow file:
exit 0, 193 KILLED, 0 SURVIVOR, 0 UNKNOWN, 24 INVALID, 17 ALLOWED of 234 over 10 definitions (225 reused from the full
run, identical inputs). Allowed: four `Option.toList` equivalents on line 1605 (`take 1`, `reverse.take 1`); four survivors
on main's `generated` line 1604 (lf-16f, unchanged here); nine ill-typed `list-empty` mutants in `check`, `statusRows`,
`linesJson` and `legendRows` that Lean refuses in the mutated definition itself. The three-term
and `linesJson` guards were added for the survivors of the first run (bound names, records, legend and status `take 1`).

## Trust

`uv run python tools/trust_map.py --check` (exit 0 after the allowance): K +0, S +0, untied V +42 of 150:
`VE/Service/Document.lean` +30, `ResponseShape/Schemas/Document.lean` +12. Allowance in docs/trust-baseline.json, "SIGNED by
standing ruling R16 (DRI-RULINGS.md), jt-3b, 2026-10-18" (94facd2e1); FOLLOW-UPS.md "## jt-3b" asks for the ties pass.

## Size

`git diff --numstat $(git merge-base HEAD main)`, generated files excluded: +765 -42 before this REPORT and mutants.json.
Product code about 130 (Document.lean +37/-6, Schemas/Encoders +20/-3, ve/document/lean.py +54/-12, report.py +7,
profiles.py +2/-1); tests 304 (test_judgments_document.py +201, test_judgments_answer.py +93, others +10); Lean guards 121;
recorded base answers 176. Accepted by reviews/dri-decisions-20261108-jt-3b-size.md item 1.

## Tests

- Selected tests (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`): the first run stopped at
  --maxfail with the trust budget, the trust ratchet and the assurance pins red (fixed in a3e99912a and 94facd2e1); the
  second stopped with five failures in the three twin and route tests above (fixed in 4bca8a0e5; the five ids rerun locally:
  5 passed). The 148 selected units neither run had reached ran on the Mac at 4bca8a0e5: 4957 passed, 4 skipped.
  `tests/test_assurance_manifest.py` 139 passed; the trust budget and ratchet ids 2 passed.
- `lake build` (1302 jobs) and `python3 lean/audit.py` (PASS: 775 files, 8609 theorems) on the final Lean.
- `uv run python tools/regen_generated.py --check`: 35 entries up to date. `tools/gate_collection.py --check --prebuilt`:
  18 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- Pre-existing failures on main: none met.
- Not rerun after the last commit (4bca8a0e5 changed only the three tests named above, which were rerun): the whole
  selection. The chain runs the full gate on the final HEAD.

Spec re-read:
- `judgments` in authoring only, translation only reports: spec 9.5 (docs/spec/judgment-terms.md:851-855).
- Profile-off identity: spec 8.1 (:731) and J-λ, the byte-identical test above.
- Legend and status texts and their order: plan 2.4 (PLAN :252-254, the declaration, factors and unit status rows), jt-3's
  `legendLines` and `statusLine`, used verbatim.

Evidence commits (`git log main..HEAD --no-merges`): 6152ccace, 673097b48, 96744e023, ab084a640, 161aaf0b4, 9159b939f,
43bf63d78, a3e99912a, 94facd2e1, 4bca8a0e5, and the commit of this report.

Next item: jt-5a (the constitution switch-on, after jt-4 and this item), then jt-5b.

## Self-review against BUILDER-CHECKLIST

1. PASS: `judgment_lines` is typed in document.json (`lines_fits`) and fuzzed: `test_every_mutant_of_the_lines_is_refused`.
2. PASS: every task row above with its commit and test; no Python copy of a Lean decision (the relay types the text only).
3. PASS: seeded bugs L1-L3, P1-P3; trust mutants 0 survivors (allow file with exact definitions and reasons).
4. PASS: base answers recorded (`tests/data/judgments-document-before-jt-3b.json`) and compared in the DELTA tests.
5. PASS: terms and units rebound, duplicated, emptied and extra: `rebind_lines` in `test_every_mutant_of_the_lines_is_refused`.
6. N.A. here: the chain runs the gate on the final HEAD; evidence commits are listed from `main..HEAD --no-merges`.
7. PASS: DELTA Ruling cells cite R2, R3, R16 or the signing decision files; trust growth recorded under R16.
8. PASS: DELTA rows for the document verdict, the CheckerUnavailable change, the text, the new member and the fault order.
9. PASS: the selection found the five tests this change broke (second run), all fixed.
10. PASS: `lines_fits` is about `linesJson`, the value `encode` writes; the build breaks under L3 at the guards.
11. PASS: the names are charged with the vocabulary: `test_the_bound_names_are_charged_against_the_vocabulary_s_limit`.
12. PASS: the names are encoded once per document (`check`), not once per fence; `statusRows` reads each unit view once.
13. PASS: no test removed or renamed; gate_collection 0 refused/stale/malformed.
14. PASS: both directions (refused unbound / answered bound / identical without the profile); spec re-read listed above.
15. PASS: no overclaim (the residual is named); no silent cut (the DRI ruled on the size); each new guard has a mutant
    that breaks it (trust-mutants.json); limits charged before work (item 11's test).
