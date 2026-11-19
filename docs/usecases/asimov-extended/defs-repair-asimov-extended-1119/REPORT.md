# defs-repair-asimov-extended-1119: REPORT

- **Status:** all 6 P1 rows KEPT and carried. Nothing waits on a DRI signature. Trust +0. No DELTA row.
- **VE commit:** built on main `f5553bc894`. HEAD is the last commit on `feature/defs-repair-asimov-extended-1119`.
- **What changed:** four legends in `usecases/asimov-extended/environment.json` now carry source definitions E1, E2a, E2b and E3 word for word. The derived ids were regenerated with the project's tools. A new condition test: `tests/test_defs_repair_asimov_extended_1119.py`.
- **Carrier deviation:** rows 3, 5 and 6 named v2 predicates. Their legends are pinned identical to asimov-laws, so these rows are carried on the sort legend (`harm`, `action`) that their rules quantify over. Row 4 is the planner-decides row, and it shares row 3's carrier. Reason below.
- **Answers touched:** each row touches 51 of 51 keyed records (rows 1-2: the ext answers). Lean's answers on every record are unchanged (`test_rerun_records_equal_the_committed_results` passed).

## 0. Verify first (source at main `f5553bc894`: `usecases/asimov-extended/source.md`; no hash-pinned source, METHOD amendment 8)

| row id | KEPT / DROPPED | reason |
|---|---|---|
| defs-asimov-extended-1-1119 | KEPT | E3 is the list entry at `usecases/asimov-extended/source.md:31-33`, starting after "- " and ending at ";". At main the `less_severe_competitor` legend (`environment.json:283`) held only the name ("has a less severe worst case"). Rule 28 (`rules.ve:28`) uses the predicate. |
| defs-asimov-extended-2-1119 | KEPT | Same E3 span. The `beaten_by_a_candidate` legend (`environment.json:293`) held the name only. Rules 18, 19, 20 and 29 (`rules.ve:18-20,29`) use the predicate. |
| defs-asimov-extended-3-1119 | KEPT | E1 runs from the sentence starting "`base.ve` is v2's" (mid-line `source.md:9`) to the end of `source.md:12`. No legend carried it: `prevent_required` was "prevention". Rule 13 (`rules.ve:13`) says "might prevent that harm". |
| defs-asimov-extended-4-1119 | KEPT | Same E1 span. Rule 9 (`rules.ve:9`) says "that action might prevent that harm". No legend of Rule 9's terms carried E1. |
| defs-asimov-extended-5-1119 | KEPT | E2a is a whole sentence at `source.md:15`. `permitted` was "permission", and its default is only the config field `regulated.default: "allow"`. Rules 1, 2, 9, 11, 12, 13 and 19 say "may be performed". |
| defs-asimov-extended-6-1119 | KEPT | E2b is a whole sentence at `source.md:15-17`. `required` was "obligation". Rules 11 and 13 say "must be performed". |

Each row's audit quote was checked against the source at main by the new test's `source_span` (first and last words, normalised by `tests/omission_rule.py:42` `omit_norm`). All 6 matched on main. Evidence: `/tmp/defs-ae-main.log` from the run before the change. On that run the only failures were the legend assertion (test line 64) and the sort-noun test: 7 failed, 6 passed.

## 1. Carriers (`usecases/asimov-extended/environment.json`)

| row | carrier | text added (from source.md only) |
|---|---|---|
| 1 | `predicates.less_severe_competitor.description` (:283) | E3 is inserted after "as derived by addition rule 28;" and before the kept suffix " (authored, not Asimov's)" |
| 2 | `predicates.beaten_by_a_candidate.description` (:293) | E3, the same way, after "addition rule 29;" |
| 3, 4 | `sorts.harm.description` (:19) | "harm. " followed by E1 |
| 5, 6 | `sorts.action.description` (:16) | "action. " followed by E2a and E2b, which are contiguous in the source |

**Why sort legends for rows 3-6 (row 4's planner choice, and the deviation for rows 3, 5 and 6).**
- The named carriers `prevent_required`, `harms_humanity`, `permitted` and `required` are v2 predicates.
- `tests/test_asimov_extended.py::test_the_environment_extends_v2_without_changing_it` asserts that every v2 predicate entry equals `usecases/asimov-laws/environment.json`'s. That is the use case's design rule (PLAN.md:28 (a); source.md:9, "The extension changes no rule, environment or manifest under `usecases/asimov-laws/`").
- Mutant M5 confirms the conflict: an append on `permitted` fails that test.
- Changing asimov-laws or relaxing that test is out of scope, and it would weaken an existing check.
- A new rule or fact line is excluded: it would change a rule formula.
- Rules 9 and 13 use only v2 predicates, so no non-v2 predicate legend of those rules exists.
- METHOD.md step 3 counts "a vocabulary legend … of a predicate, constant or sort **that rule uses**". The sorts `action` and `harm` are quantified by every rule in these rows (the test checks this word in each rule line).
- E2a and E2b are sentences about actions, so they go on sort `action`. E1 is about the harm an action "might prevent", so it goes on sort `harm`.
- A sort's noun is its name, not its description (`ve/printer.py:348-361`), so the rendered rules do not change. `test_every_rule_has_one_reading_in_plain_english` passes, and `test_a_sort_carrier_keeps_its_noun` pins this.
- Rows 3 and 4 share one carrier, and so do rows 5 and 6 (METHOD step 4: "Several rules sharing one carrier get one row").

**Not used.** The `risk` and `alternatives` blocks are config tables. They are not legends, and `alternatives` is pinned equal to v2's.

## 2. Derived files (regenerated with the project's tools only)

- `usecases/asimov-extended/rules.manifest.json` and `base.manifest.json`: `environment_id` and `document_hash` changed; `blocks` and `text_digest` stayed byte-equal. They were written with the document's own generator `asimov_extended_cases.render_manifest()`, in the file's existing format (`json.dumps(indent=2)+"\n"`). The script checked that the rendered text still equals `rules.ve` and `base.ve`.
- `conformance/english-lean/lexicon-report.json`: the asimov-extended `lexicon_id`. It was written by `uv run python -m conformance.english_lean_lexicon` (43 valid, 0 invalid). `LexiconFixtures.lean` is unchanged (`lean_fixtures()` equals the file). The file is outside the row's `derived_files`. The selected run found it: `test_every_corpus_environment_has_a_valid_selected_lexicon` failed before the regeneration and passed after (56 passed).
- `git grep` finds no file still holding the old `environment_id` (0dbd6881…), `document_hash` values or lexicon id.
- `uv run python tools/regen_generated.py --check` reports "checked 41 entries", with no stale file.
- No frozen-run.json or seal covers these files. asimov-extended has no run directory, and `corpus-seal.json` does not list it (`git grep` on the old hashes).

## 3. Condition test

`tests/test_defs_repair_asimov_extended_1119.py` (13 tests):
- per row: the source span, read from `source.md`, equals the audit quote, and that span occurs in the carrier legend (both normalised with `omit_norm`);
- per row: each dependent rule line exists and uses both the term phrase and the carrier;
- sort carriers keep their noun.

It fails on main (`/tmp/defs-ae-main.log`: 7 failed) and passes after (`/tmp/defs-ae-1.log`: 29 passed, together with the fast `tests/test_asimov_extended.py`). The Mac selected run picked it ("changed [...test_defs_repair_asimov_extended_1119.py]", exit 0).

## Tests run

- **Selected run** (`mac-pytest.sh --select`, HEAD d444f1c4): 37 units. The only failure was `tests/test_english_lean_lexicon.py::test_every_corpus_environment_has_a_valid_selected_lexicon` (stale derived id). It was regenerated, and that file then passed locally: 56 passed (`/tmp/defs-ae-lex.log`).
- **Final selected run** (after the lexicon regeneration and the docs commit): it ran on ve-cloud-2 and recorded "372 units for tree f81a7e5783 … 0 failed", exit=0 (`/tmp/defs-ae-select2.log`).
- **Records rerun:** `tests/test_asimov_extended.py::test_rerun_records_equal_the_committed_results` ran against the Lean service after a `lake build` (1478 jobs, ok). It passed in 168.82 s, not skipped (`/tmp/defs-ae-rerun.log`). So Lean's base, ext and permission-default answers on every record are unchanged.
- **Not run:** the nightly `test_rerun_document_*`, `test_rerun_mutant_*` and `test_rerun_sample_*`. Legends do not enter those formulas, but this is not verified. The full gate is left to the chain, as instructed.
- **Light lane:** "LIGHT 100 changed lines outside generated files <= 150 (5 files), no trusted-core file", so there was no trust_mutants sweep.

## Seeded bugs (`mutants.json`)

All 7 were planted in `usecases/asimov-extended/environment.json` (M1-M6) or `source.md` (M7). Each made a named test fail and was then restored with git checkout.
- M1 drops an E3 clause: row-1 test fails.
- M2 empties row 2's carrier: row-2 test fails.
- M3 changes E1's "13" to "12": rows 3 and 4 fail.
- M4 drops E2b's second clause: row 6 fails.
- M5 moves E2a onto `permitted`: `test_the_environment_extends_v2_without_changing_it` and row 5 fail.
- M6 adds a verbalisation to sort `harm`: `test_a_sort_carrier_keeps_its_noun` fails.
- M7 changes source drift "may" to "can": row 5 fails.

No Lean, Python or Rust product code changed, so there is no per-language product mutant.

## Trust and DELTA

- `uv run python tools/trust_map.py --check` against f5553bc894cf gives "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0", PASS.
- No DELTA.md. There is no verdict, diagnostic, refusal or acceptance change, only legend text in one use-case environment and the ids derived from it. The records rerun shows the answers are unchanged.

SIZE: 0 product, 82 tests, 8 other hand-written lines (environment.json legends), plus this REPORT and mutants.json. Generated: 4 manifest lines and 1 lexicon-report line.

Pilot bytes expected to move (estimate, nothing claimed): a definitions-carried read of asimov-extended should move rows 1-6 from NOT CARRIED to CARRIED. That is E1 for R9 and R13, E2a for 7 rules, E2b for 3 rules, and E3 for R18, R19, R20, R28 and R29.

Next item: none.

## Spec re-read

- The six quotes were checked against `reviews/defs-carried-1119/rows-asimov-extended.tsv` column `quote`, and against `source.md:9-12`, `:15-17` and `:31-33`. The test's `span == omit_norm(quote)` asserts this.
- The carrier rule ("legend … of a predicate, constant or sort that rule uses; never a header, comment or constant table") was checked against METHOD.md step 3 and against task deliverable 1.

## Notes for the DRI

- Rows 3, 5 and 6 are carried on sort legends, not on the predicates the rows name, because the v2 predicate legends are pinned. This keeps PLAN (a) and the v2-identity test intact.
- If the DRI prefers the predicate legends, the v2-identity rule of `tests/test_asimov_extended.py` has to be relaxed for descriptions first. That is a separate decision: it deletes part of a check.

## Notes

- P2 rows 7-9 (D1, D2 and D3 on `breaks_first_law`, `breaks_zeroth_law` and `ordered`) were not taken, as instructed. They are v2 predicates, so they would meet the same pin.
- The two E3 legends now read "…rule 28; the severity classes … author); (authored, not Asimov's)". The suffix moved after the inserted quote because a test requires derived legends to end with "(authored, not Asimov's)". No word was removed.
- I found no new candidates.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relay or schema changed.
2. Every required deliverable is built: PASS. All six rows are carried (`test_the_source_definition_is_carried_word_for_word[*]`). Derived files were regenerated (`regen_generated.py --check`; `test_english_lean_lexicon.py`).
3. Tests and gates can fail: PASS. M1-M7 in `mutants.json`. The condition test fails on main (`/tmp/defs-ae-main.log`).
4. Py/Lean/Rust agree, and valid inputs pass: PASS. `test_rerun_records_equal_the_committed_results` (Lean) and `test_the_independent_reading_gives_the_answer_key`.
5. R8 binding: N.A. No relay.
6. Gate evidence matches the final HEAD: N.A. The chain runs the gate on the final HEAD.
7. No unsigned item: PASS. No DELTA row; trust +0 (`trust_map.py --check`).
8. Every user-visible change is in DELTA: PASS. No verdict moved (`test_rerun_records_equal_the_committed_results`). Rendered text is unchanged (`test_every_rule_has_one_reading_in_plain_english`).
9. Test selection finds the tests: PASS. The selected run picked the new test, `test_asimov_extended.py` and `test_english_lean_lexicon.py`. The last one caught the stale lexicon id.
10. Lean statements: N.A. No Lean change.
11. Budgets and limits: N.A. No evaluator.
12. CPU and memory: N.A. Legend text only.
13. Test-removed trailers: N.A. No test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. The test fails on main and passes after. M5 checks the opposite direction (v2 predicates must stay unchanged). Evidence logs are cited above, and the spec re-read lines are above.
15. No overclaim / no silent cut / new checks can fail / limits: PASS. The nightly reruns are stated as not run. No deliverable was cut. M1-M7 cover the new checks. The limits class is N.A.
