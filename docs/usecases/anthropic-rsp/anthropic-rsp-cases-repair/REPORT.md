# anthropic-rsp-cases-repair: an accounting line for the RSP case records

**Status:** built; target met; no DRI signature reserved.
**What changed:** `usecases/anthropic-rsp/accounting.d1.txt` gets one line for the case records, saying "nothing". The accounting tool `usecases/safetyfw_accounting.py` now reads a line for a collection unit (CASES or D2D3). The saved report is regenerated with the tool's own `--report`.
**Target:** exposure.py goes from 8 to 7 on FACTS/CASES. The `CASES <- CASES no-record` row is gone, and no other row is new (the table below).
**Open items:** none. No D2D3 line was added (deliverable 3).
**Gate:** the chain runs it on the final HEAD.

Ruling: orchestrator re-plan ruling 2026-11-14 item A3; decision reviews/dri-decisions-20261114-replan-ruling.md; diagnosis
reviews/facts-cases-diag-20261114.md section 1 (both in manage-agents).

## Deliverables

| # | task line | delivered | evidence |
|---|---|---|---|
| 1 | one accounting line for the case records, written by the file's own tool, true | the case-records line, "nothing", the last line of accounting.d1.txt; `--check` exits 0 | `uv run python usecases/safetyfw_accounting.py anthropic-rsp --source <pinned rsp-3.4.txt> --check --report docs/usecases/safetyfw/anthropic-rsp/accounting.json`, exit 0, "85 blocks, 164 unaccounted words in 36 blocks, 3 blocks with a loss {'1': 2, 'limit 9': 1}, 0 of 141 quotes unanchored" |
| 2 | the tool takes a collection-unit line | a fixed tuple `COLLECTIONS` of the two collection ids; one line each, after every block line, in the block form; reasons resolve as for a block, and the tag for words a rule text repeats is refused (a collection has no rule text) | main's tool on the new sidecar refuses line 86 as "not '<block id> ...'" (`python3 -I /tmp/accmain/safetyfw_accounting.py usecases/anthropic-rsp --check`, main's file); tests `test_a_collection_unit_has_one_line_after_the_blocks` (16 cases), `test_a_report_without_a_collection_line_has_no_collections_key`; the existing tool tests pass unchanged except `test_case_sidecar_passes_in_form`, which now lets collection ids follow the block ids |
| 3 | no D2D3 line | none added | `grep -c '^D2D3' usecases/anthropic-rsp/accounting.d1.txt` = 0 |
| (a) | test: the line exists and parses | `test_cases_accounting_line_exists_and_parses` | tests/test_rsp_fidelity_fix.py |
| (b) | test: every situation is in PLAN 5, or allow-listed with its reason | `test_every_case_situation_is_plan_text_or_an_allowed_transcription` | tests/test_rsp_fidelity_fix.py |
| (+) | test: the two transcribed source sentences | `test_transcribed_source_sentences_are_whole_quotes_the_rules_account_and_the_findings_carry` | tests/test_rsp_fidelity_fix.py |

## The case check (why "nothing" is true)

Command: a read-only Python probe over cases.json, PLAN.md and the pinned text
`~/code/manage-agents/pilots/anthropic-rsp/source/rsp-3.4.txt` (sha256 c7de7fe2f1f4…, 59,410 bytes, as PLAN 1 pins it). The
three tests above re-check each finding without the source text, which the repository does not hold.

1. **Situations (49 records, the 38 credited among them).** 42 are verbatim PLAN text. All 42 are in PLAN 6's key rows,
   which PLAN 5's table lists by family. The other 7 are on the test's allow-list, each with its reason:
   - A-T1..A-T4 ("Tk crossed, no other threshold"): PLAN 5's case-facts sentence "The model has crossed the thresholds named
     (T0: none) and no others", for PLAN 6's row "A-Tk, k = 1 … 4".
   - T1, T2, T5: PLAN 6's row with "4×", "6×", "4.5×" written "4x", "6x", "4.5x". `quantities.cost_factor` holds the number
     (4, 6, 4.5), and the test checks it. Only T1 is credited; this matches rsp-summary.md ("33 of 38 verbatim … T1 differs
     only in 4x vs 4×").
   Situations are PLAN wording, so they hold no RSP source words.
2. **Two records do hold source words**, a correction to the diagnosis. K21 and T2 each have a `source_sentence` field
   (PLAN 12 item 15: "the full sentence is beside the case"). On the pinned text (NFKC):
   - Each is one whole sentence of the source. It starts after a sentence end and ends at one: K21 at byte offset 46278,
     after "General upleveling."; T2 at 18215.
   - Each is one whole sentence of a block header quote whose accounting line reads "nothing": T2 in `t4-suff`, K21 in
     `f26-effort`. The K21 sentence is also in `f26-need-not-delay`, whose line has its own entries.
   - Every content word of each sentence is in the legend of a predicate the record's findings set: K21's OT8 is
     `mitigation_evidence`; T2's OT15 and `scenario_2` are `full_substitution_at_competitive_cost` and `scenario_2`. The
     names come from run.py's `OT` and `SCENARIO_TERMS`.
   - The only raw miss is "signi", "cant" in K21. That is the PDF ligature "ﬁ" in cases.json, and the tool's `norm` folds it.
   So the records transcribe these two sentences whole, and each word of both is carried. The expected DRI question 1 ("a
   case transcribes source words, so 'nothing' would be false") does not arise, and none was sent.

## Exposure (exposure.py, before and after)

Command: `python3 -I ~/code/manage-agents/reviews/facts-cases-diag/exposure.py anthropic-rsp <sha>`. A sha is passed because
the main checkout at ~/code/verifiable-english has no HEAD commit, so the literal argument `HEAD` gives "VE files unreadable".
Verbatim outputs are saved beside this file: `exposure-before.txt` (main a84c072d76) and `exposure-after.txt` (b5c3625cba).
Counter sha256 1c7cc4f7 both times. The rows are listed by unit, record unit and kind; the detail column is in the files.

| unit | record unit | kind | main a84c072d76 | branch b5c3625cba |
|---|---|---|---|---|
| FACTS | highly-capable-t4 | loss | yes | yes |
| FACTS | s2-suff-third | mistag (2 entries) | yes | yes |
| FACTS | s2-suff-third | plan12 | yes | yes |
| FACTS | t4-suff | plan12 | yes | yes |
| FACTS | t4-only-if | plan12 | yes | yes |
| FACTS | s2-only-if-third | report | yes | yes |
| CASES | CASES | no-record | yes | **no** |
| D2D3 | D2D3 | no-record | yes | yes |
| | | **total on FACTS/CASES** | **8** | **7** |

The same counter's `omit_exposure` was also compared over every unit of the manifest, main against this REPORT's own
commit (section "Every unit" below), so this REPORT adds no record on any unit.

## Answers

None moved. `git diff --stat main -- usecases/anthropic-rsp/results.json coverage.json environment.d1.json cases.json` is
empty. run.py reads neither accounting.d1.txt nor safetyfw_accounting.py (`grep -n accounting usecases/anthropic-rsp/run.py`:
no hit), and no rule, fact or case text changed.

## Seeded bugs (each planted, the named test failed, then `git checkout` restored the file)

| # | file (language) | bug | failing test |
|---|---|---|---|
| a | usecases/anthropic-rsp/accounting.d1.txt (data) | the case-records line deleted | test_rsp_fidelity_fix.py::test_cases_accounting_line_exists_and_parses (`assert [] == [([], None)]`) |
| b | usecases/anthropic-rsp/cases.json (data) | K7's situation "a Risk Report is approved" + " by the Board" | test_rsp_fidelity_fix.py::test_every_case_situation_is_plan_text_or_an_allowed_transcription (`['K7'] == []`) |
| c | usecases/anthropic-rsp/accounting.d1.txt (data) | the line becomes `"the model has crossed"` with an empty reason tag | test_rsp_fidelity_fix.py::test_cases_accounting_line_exists_and_parses (unreadable entry) |
| d | usecases/safetyfw_accounting.py (Python) | the "follows every block line" check disabled | test_safetyfw_accounting.py::test_a_collection_unit_has_one_line_after_the_blocks[lines6-…follows every block line] |
| e | usecases/safetyfw_accounting.py (Python) | `restates` accepted on a collection | test_safetyfw_accounting.py::test_a_collection_unit_has_one_line_after_the_blocks[lines11-…restates it] |
| f | usecases/anthropic-rsp/cases.json (data) | T2's transcription cut after "within a factor of 5)." | test_rsp_fidelity_fix.py::test_transcribed_source_sentences_are_whole_quotes_the_rules_account_and_the_findings_carry (`('T2', [])`) |
| g | usecases/anthropic-rsp/cases.json (data) | K21's finding OT8 swapped for OT5 | the same test (`K21`) |

The tests also plant their own opposite directions: a changed situation, a wrong carried factor and a stale allowance in
(b); collection lines the tool must accept, and lines it must refuse, in the tool test. Only Python product code changed.
No Lean or Rust changed, so there are no Lean or Rust seeded bugs.

## Size, trust, DELTA

SIZE: 38 product, 158 tests, 1 other hand-written lines (`git diff --numstat a84c072d76`: usecases/safetyfw_accounting.py
+38/-5, tests +119 and +39/-1, accounting.d1.txt +1; the regenerated accounting.json +7 is tool output). This REPORT and the
two saved outputs are not counted. The planner's estimate was ~5-30 hand-written lines plus tests.
Trust: `uv run python tools/trust_map.py --check` reports "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0"
(PASS). No R6 or R16 record is needed.
DELTA: none (use-case files only; no ve/, lean/, rust/, run.py, key or PLAN change), so there is no DELTA.md.
Light lane: `light-lane.py check` printed "NOT 210 changed lines outside generated files > 150". There is no trust_mutants
sweep because no Lean changed (build checklist 13a covers trusted Lean only), and the task file asks for none.

## Tests run

- New and touched: `uv run pytest -q tests/test_safetyfw_accounting.py` (72 passed);
  `tests/test_rsp_fidelity_fix.py -k "accounting or omission_record"` (4 passed) and the three new tests (3 passed).
- Named unchanged tests: `tests/test_safetyfw_usecases.py -k "test_section_6_is_the_frozen_key or
  test_transcription_is_pinned"` (4 passed; not in the selection, because their inputs did not change).
  `test_regulated_predicates_stay_64_after_fix_3` and fix-4's and fix-4b's tests are in test_rsp_fidelity_fix.py, which is selected.
- Selected run: see "Final selected run" below.

## Notes for the DRI

- The diagnosis (section 1) and rsp-summary.md say the case records carry no RSP source words. Two of them, K21 and T2,
  carry one whole source sentence each (above). The line stays "nothing" because both are whole and fully carried. A third
  `source_sentence` field would fail the new test (c), which pins the field set.
- Test (b) checks against PLAN sections 5 and 6, not only section 5. The situations are the key rows of section 6, and
  cases.json's own source field calls them "PLAN.md section 5 case facts". A check against section 5 alone would match 0
  of 49.
- The read-only exposure.py needs a sha argument here (above), because `HEAD` resolves in the main checkout, which has no commit.
