# English in Lean S3: Lean work-item fix report

## Implemented

- Added the `order@0` and `alternatives@0` fixed rows, the staged catalogue and ranks, lexical families for integer terms, attributes, properties and alternative guards, and their typed actions. `ProfileExamples.lean` checks verdicts, formulas, rejections, quoted names, grammar typing, row counts, parser steps, boundary JSON and profile combinations with `#guard`.
- Extended the English environment decoder and typed view for alternatives, risk, units and regulated predicates. The submitted environment remains the identity input. The frozen `Norms`, `SoftNorms` and `Route` implementation contracts were not edited.
- Added `admit`, its obligation computation and candidate check, and proved the ten new theorem statements of spec section 5.5. `tools/check_english_s3_statements.py` compares their source text against the approved statements; the thirteen S2 headline statements checked during this work item remained textually unchanged.
- Imported the profile fixtures into the default Lean build, audited every new named lemma, refreshed the source hash inventory, the English grammar lock and version, and the generated Lean declaration records. The source audit distinguishes the approved function name `admit` from the forbidden proof tactic; the pre-commit check uses that same rule.

## Seeded bug checks (all removed)

| Bug planted in changed code | Failing check |
|---|---|
| `conformance/english_lean_lexicon.py`: `_subject_first` returned `True` for every wording | `tests/test_english_lean_lexicon.py::test_lean_fixtures_are_generated_from_the_python_reference`: failed; exit 1 |
| `Actions.lean`: integer negation scaled by `+1` | `lake build VE.EnglishGrammar.ProfileExamples`: guards at lines 150, 151, 152 and 176 failed; exit 1 |
| `Rules.lean`: `fixedTable` omitted `order@0` rows | `lake build VE.EnglishGrammar.ProfileExamples`: order guards from line 150 onward failed; exit 1 |

Each mutation was restored before the final build. `rg` found no seed marker or mutated expression afterward.

## Boundaries of this work item

This is the Lean S3 implementation and its supporting inventories. The plan assigns the JSON source generator for the two new fixed tables to S3.0's Python implementer, the corpus comparison and report to S3.5, and the authority flip, V6, service modes and deletion ledger to E2. Those items and the human bounded statement re-check remain outside this commit series. No model calls or push were made.
