# fsf-repair-f2-glossary-1119: REPORT

No DRI-reserved signature; no DELTA row (see "DELTA" below).

Row F2 of reviews/pathf-q3/flag-analysis-1119/compare-report.md (manage-agents): the FSF Glossary defines four
terms the case asks to be required (Critical Capability Assessments, Security Mitigations, Residual Risk Assessments,
Frontier AI Models), and the legends that carry them did not hold the definitions. LANGUAGE only: the legends of
`usecases/safety-framework/vocabulary.py` (written to `environment.d1.json`) gain the Glossary sentence, verbatim.

## Base

Branched at VE main d8758ce968; main merged at 3d6b459df4 (four infra commits, none under usecases/ or tests/). The
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
N1 certificate hashes only). These three are not in `tools/regen_generated.py` (its `--list` names no
safety-framework file); each was written by its own generator, as in 7227dfad90 (FSF fix-3 batch 3).
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
- SIZE: 14 product (vocabulary.py), 83 tests, about 95 other hand-written lines (this REPORT).

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
