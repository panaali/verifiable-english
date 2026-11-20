# fsf-repair-f2-glossary-1119: REPORT

- Status: built; selected run done, its two failures fixed by regeneration and rerun green; full gate left to the chain.
- Merges at VE main f5553bc894 (merge commit 8ef8bdfdf1 on this branch; the final HEAD is this REPORT's commit).
- Change: five FSF legends (assessed, secured, residual_assessed, within_levels, frontier) quote their Glossary definition.
- Open items: none. Prompt-size counter reads-1119 not installed on main (see "Prompt size").
- DRI signature needed: none; no DELTA row (see "Trust, DELTA, size").

Row F2 of reviews/pathf-q3/flag-analysis-1119/compare-report.md (manage-agents): the FSF Glossary defines four
terms the case asks to be required (Critical Capability Assessments, Security Mitigations, Residual Risk Assessments,
Frontier AI Models), and the legends that carry them did not hold the definitions. LANGUAGE only: the legends of
`usecases/safety-framework/vocabulary.py` (written to `environment.d1.json`) gain the Glossary sentence, verbatim.

## Base

Branched at VE main d8758ce968; main merged at 3d6b459df4 and then f5553bc894 (infra commits only; `git diff
--name-only HEAD...main` named nothing under usecases/, tests/data/ or conformance/english-lean/). The
task's plan commit 7cbec4b340b8 is the local `origin/main` ref, not an ancestor of main; `usecases/safety-framework/`
vocabulary.py and environment.d1.json are identical at 7cbec4b340b8 and at d8758ce968, so the condition test fails
at both (checked at d8758ce968: 6 failed, 1 passed). The final merge commit is named in the builder's final reply.

## Delivered

| Task row | Predicate (legend) | Delivered |
|---|---|---|
| 1a | `assessed` | appended `critical capability assessments "determine a model's proximity to T/CCLs through the use of early warning evaluations and other sources of evidence" (Glossary)` |
| 1b | `secured` | appended `security mitigations "are safety measures we implement which are intended to prevent the unauthorized modification or exfiltration of model weights by unauthorized actors" (Glossary)` |
| 1c | `within_levels` (the legend that carried only the entry's last sentence) and `residual_assessed` (the legend of f7-rra's residual risk assessments, the B-L*/RRA answers) | appended `residual risk assessments are "the process of evaluating the level of risk that remains after all planned mitigation strategies have been implemented" (Glossary)` |
| 1d | `frontier` (OT9) | "(Glossary definition)" replaced by `(Glossary: Frontier AI Models "are trained on a large data set, display significant generality, are capable of performing a wide range of distinctive tasks and have high-impact capabilities. Frontier AI models' agentic and reasoning-based general capabilities near or exceed those of other Google models")`; still open term OT9 |
| 2 | condition test | `tests/test_fsf_repair_f2_glossary_1119.py` (new file, as the parallel-siblings note asks) |

Every sentence is on a predicate legend (description) the blocks use, never a header/citation run or a constant
table (CARRIER GUARD). Each is added in its own predicate entry, nothing appended at the end of a shared file.

Generated files: `environment.d1.json` (`python usecases/safety-framework/vocabulary.py`), `coverage.json`
(`build_document.py`; document_sha256 only), `results.json` (`run.py`; answers unchanged, 257/262 as before; the two
N1 certificate hashes only), `conformance/english-lean/lexicon-report.json` (`conformance/english_lean_lexicon.py`;
the FSF lexicon_id only) and `tests/data/route-cases.jsonl` (`docs/en-e3-norm/en-2b/route_fixtures.py --write`; the
`stale` fixture, which carries the FSF environment, only). None of these is in `tools/regen_generated.py` (its
`--list` names none of them); each was written by its own generator, as in 7227dfad90 (FSF fix-3 batch 3) and the
sibling's d1bbb7b3ae. The selected run found the last two stale (`test_every_corpus_environment_has_a_valid_selected_lexicon`,
`test_the_route_fixtures_are_recorded`); after regeneration both pass.
`regen_generated.py --check` reports only route-cases (no Lean build in this worktree) and checker-pins (no pinned
Rust binary here), both unrelated to this item.

## Source passages (pinned FSF 3.1 text, sha256 18e3375b...0c53946, `usecases/pinned_sources.json`)

Location: lines of the extracted text (`source/extract_text.py`, one page per line), Glossary pages.

- Line 18 (Glossary p. 18), "Critical Capability Assessments: determine a model’s proximity to T/CCLs through the
  use of early warning evaluations and other sources of evidence."
- Line 19 (p. 19), "Security Mitigations: are safety measures we implement which are intended to prevent the
  unauthorized modification or exfiltration of model weights by unauthorized actors."
- Line 20 (p. 20), "Residual Risk Assessment Residual Risk Assessments: the process of evaluating the level of risk
  that remains after all planned mitigation strategies have been implemented."
- Line 18 (p. 18), "Frontier AI Models or Models : are trained on a large data set, display significant generality,
  are capable of performing a wide range of distinctive tasks and have high-impact capabilities. Frontier AI models’
  agentic and reasoning-based general capabilities near or exceed those of other Google models."

Differences from the task's quoted spans: the source prints the apostrophes of "model’s" (1a) and "models’" (1d)
curly; the legends carry them plain, as the project's quote normalisation (`usecases/safetyfw_accounting.py` `norm`)
gives them and as the existing `safety_case` legend does. No word differs. For 1d the task quotes no span: the
Glossary entry's definition is two sentences (the third begins the checkpoint/version note, a different matter), and
both are carried; the final full stop of each quoted span is left out, as in the existing Glossary legends.

## Condition test

`tests/test_fsf_repair_f2_glossary_1119.py::test_the_legend_quotes_the_pinned_glossary_sentence[<predicate>]` reads
the pinned source (`tests/pinned_source.py`), normalises it with `norm`, takes the sentence(s) after the entry's label
in the Glossary (the label must occur once), and asserts the sentence stands in quotes, byte for byte, in the
committed legend. `test_the_extracted_sentences_are_whole_definitions` pins where each extraction ends;
`test_the_frontier_legend_no_longer_stands_in_for_the_definition` needs no source. At the base: 6 failed, 1 passed;
after: 7 passed.

## Seeded bugs (Python, `usecases/safety-framework/vocabulary.py`; environment.d1.json regenerated for each; all restored)

| # | Bug | Failing test |
|---|---|---|
| s1 | `assessed`: apostrophe left curly ("model’s") | `test_the_legend_quotes_the_pinned_glossary_sentence[assessed]` |
| s2 | `secured`: last word "actors" dropped | `...[secured]` |
| s3 | `residual_assessed`: the Glossary append removed | `...[residual_assessed]` |
| s4 | `frontier`: second definition sentence dropped | `...[frontier]` |
| s5 | `within_levels`: "planned" dropped | `...[within_levels]` |
| s6 | `frontier`: "(Glossary definition)" marker restored | `...[frontier]`, `test_the_frontier_legend_no_longer_stands_in_for_the_definition` |

No Lean or Rust product code changed.

## Trust, DELTA, size

- Trust +0: no Lean file changed; light lane (`light-lane.py check`: LIGHT, 118 changed lines, no trusted-core
  file), so no trust_mutants sweep.
- DELTA: none. No verdict, diagnostic or checker output changes (results.json answers unchanged); the item adds
  source text to five legends and removes nothing but the "(Glossary definition)" placeholder, which the definition
  replaces. The precedent 7227dfad90 (same kind of append) had no DELTA row.
- SIZE: 14 product (vocabulary.py), 83 tests, 162 other hand-written lines (this REPORT).

## Prompt size

The reads-1119 counter (R16 C5 dry-run) is not installed on VE main at this merge (no file under tools/, usecases/
or docs/ names it), so no dry-run was run; the decider re-checks at the counted read. The five legends grow by
955 bytes in total (assessed 161, secured 184, residual_assessed 163, within_levels 163, frontier 284); a prompt
carries only the legends of the predicates its block uses.

## Pilot bytes expected to move (estimate, nothing claimed before a pilot audit)

Row F2's analysts count 13 answers that clear on this row alone (CCA 10, SECM 2, RRA 1 alone; compare-report.md).

## Notes for the DRI

- Overlap: `feature/fsf-repair-f5-lowrisk-1119` also edits vocabulary.py and regenerates environment.d1.json,
  coverage.json and results.json. Different predicate entries; the generated files regenerate on rebase.
- `build_document.py` writes its built document `fsf.d1.ve.md` next to the stored source in
  `~/code/manage-agents/pilots/safety-framework/source/` (gitignored there); running it rewrote that local build.

## Next item

None: every deliverable of row F2 is delivered.

## Test runs (commands and logs)

- Condition test at the base: `environment.d1.json` restored from d8758ce968, `uv run pytest -q
  tests/test_fsf_repair_f2_glossary_1119.py`: "6 failed, 1 passed"; at HEAD: "7 passed".
- Seeded bugs: each run as `uv run pytest -q tests/test_fsf_repair_f2_glossary_1119.py [tests/test_safety_framework.py
  -k "glossary or legend or f20 or environment"]`; failing ids in the table above.
- Selected run (`mac-pytest.sh --select -- --base 3d6b459df4 --run`, VM, 3011 s, tree 0da522db66): 57 units,
  2 failed: `tests/test_english_lean_lexicon.py::test_every_corpus_environment_has_a_valid_selected_lexicon` and
  `tests/test_english_statement_blocks.py::test_the_route_fixtures_are_recorded`, both artifacts that hash the FSF
  environment and that this change made stale (not in main-known-red.txt). Regenerated (commit 7eb0068d96); the two
  ids rerun: "2 passed"; the consumers of the changed route row (`mac-pytest.sh -- -q
  tests/test_english_statement_blocks.py::test_each_route_fixture_through_the_service tests/test_route_row_schemas.py`,
  ve-mac-1, HEAD 7eb0068d clean): "33 passed".
- `tools/select_tests.py --base $(git merge-base HEAD main)` (plan only) selects 76 test files, not every unit,
  including `tests/test_fsf_repair_f2_glossary_1119.py`, `tests/test_safety_framework.py`,
  `tests/test_english_lean_lexicon.py` and `tests/test_english_statement_blocks.py`.

## Spec re-read

- Legend 1a against the pinned text line 18 and the task's 1a: same words; apostrophe normalised.
- Legend 1b against line 19 and 1b: same words.
- Legend 1c (both predicates) against line 20 and 1c: same words.
- Legend 1d against line 18: the entry's two definition sentences; apostrophe normalised.
- CARRIER GUARD (converge-AB.md section 0) against each carrier: all five are predicate legends used by blocks of
  rules.d1.ve (`grep` of each predicate's wording in rules.d1.ve: assessed 2, secured 2, frontier 1, within_levels 3;
  f7-rra uses residual_assessed).

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A., no relayed answer or schema changed.
2. Deliverables built, no rule broken: PASS, 1a-1d and 2 in "Delivered"; `test_the_legend_quotes_the_pinned_glossary_sentence[*]`.
3. Tests and gates can fail: PASS, seeded bugs s1-s6 and the base run (6 failed).
4. Python, Lean and Rust agree: N.A., no decision path changed; results.json answers unchanged (`run.py`: 257/262, as committed before).
5. R8 binding: N.A., no relay.
6. Gate evidence matches final HEAD: PASS, the full gate is the chain's on the final HEAD; the selected run's failures were regenerated and rerun (Test runs).
7. No unsigned item: PASS, no DELTA row, no SIGNED cell.
8. Every user-visible change in DELTA: PASS, the checker's outputs do not change (results.json verdicts unchanged); the legend text is the use case's own content, as in 7227dfad90.
9. Test selection finds the tests: PASS, `tools/select_tests.py` plan (Test runs); seeded bugs s1-s6 fail `tests/test_fsf_repair_f2_glossary_1119.py`, which it selects.
10. Lean statements: N.A., no Lean change.
11. Budgets fail closed: N.A., no evaluator or limit.
12. No CPU or memory regression: N.A., legend text only (955 bytes).
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS, accept side (7 passed at HEAD), refuse side (s1-s6, base run); citations in "Test runs"; "Spec re-read" above.
15. Overclaim, silent cut, checks can fail, limits: PASS, no deliverable cut; every new test broken by a seeded bug (s1-s6); limits N.A.
