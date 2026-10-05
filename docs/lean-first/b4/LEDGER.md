# Lean-first batch 4 (discourse): deletion ledger

Plan: `docs/LEAN-FIRST-PLAN.md` (draft 3), section 5.1 item 3 and section 5.2 row 4. Base `776a64d7`. Every
deleted Python or Rust decision site is mapped to the Lean check or answer that now owns it. Lean names are in
`lean/VE/Discourse/`.

## Deleted decision sites

| # | Deleted (base `ve/discourse.py` unless named) | Decided | Owner now |
|---|---|---|---|
| D1 | `rejection(lean, python_error)`: Python's diagnostic kept when Python rejected too | which text a rejected `@2` document shows | Lean's row, relayed (`rejection(lean)` → `_error_of`); `ve/document.py` `load_document` raises it before any Python check runs |
| D2 | `python_discourse` (block fields, `_LEAN_ONLY` abstentions, version, `definitions_version`, names, content names, documents, imports, refers, mentions, form/kind table `_FORM_KINDS`, target kinds, pins, overlaps, location targets in slot positions, groups) | every block-level acceptance check and its order | `Wire.decodeManifest`, `WellFormed.wellFormed` (`mentionsOk`, `formFits`, `pinOk`, `slotUnit`, `groupsOk`), `Admission.postOk`, `Admission.prepare` |
| D3 | `_anchors`, `_table`, `_array`, `_span`, `_no_null`, `_inside` | anchor tree, duplicates, limits, spans | `Wire.decodeManifest`, `WellFormed` anchor checks |
| D4 | `decode_block` and its helpers (`_fields`, `_string`, `_strings`, `_nat`, `_rows`, `_optional`, `_span_shape`) | the strict wire decode of a block (3.1), own and stored | `Wire.decodeManifest`, `Wire.decodeTables` |
| D5 | `check_stored_documents`, `_stored_identities`, `_stored_block`, `_chain` | stored document integrity, pins, `StaleTarget`, `ImportCycle`, nesting `ResourceLimit` | `Admission.integrityOk`, `Admission.postOk` (`dependencyOrder`, `depthOf`) |
| D6 | `_token_spans`, `_canonical_wording`, `_lex`, `_unit_tokens`, `_mention_words`, `_label_end`, `_fold`, `_fold_text`, `_segments` | token-boundary mention spans, discourse wording (4.1(4)), the lexer | `Grammar.lex`, `Grammar.toTokenSpans`, `Grammar.canonicalWording`, `Grammar.foldChar`, `Grammar.segments` |
| D7 | `reference_surfaces`, `_segment_lengths`, `_unrecorded` | slot discovery and coverage (`UnrecordedSlot`) | `Grammar.textSurfaces`, `WellFormed.coverageOk` (`uncoveredSurface`) |
| D8 | `_surface_fits`, `_accessible`, `_scope_texts`, `_innermost`, `_competing_quantifier`, `_infix`, `_spellings`, `_coordinations`, `_sort_phrases`, `_sort_noun` | `MentionNotSlot`, accessibility, competing quantifiers, ordinal coordinations | `Access.accCands`, `Access.surfaceOk`, `Access.bindsSort`, `Access.earlierPairs` |
| D9 | `_resolve_unit`, `_expanded`, `_target_key`, `_same_target` | resolution: `IllTypedTarget`, `UnresolvedReference`, `AmbiguousReference`, `InaccessibleTarget`, `ManifestMismatch: bound.*` | `Resolve.validate`, `WellFormed.boundOk` |
| D10 | `group_reading`, `_parse_one`, `_same_witness`, `_conjuncts`, `_contains_var` | group regeneration, `WitnessSplit`, `ManifestMismatch: groups.*`, `IndependentFragment` | `WellFormed.groupFormula`, `sharedWitness`, `groupsOk`; `Admission.postOk` |
| D11 | `_joint` | the joint set: compatible choices, `InvalidCompatibility`, the 64-choice budget | `Joint.compatibleChoices`, `WellFormed.jointOk`; the admission's `joint_choices` (`Run.jointFields`, added) |
| D12 | `joint_assertion` | the joint disjunction for the premise check | `Joint.joint`; the admission's `joint_formula` (added). Which readings may form a premise (all asserted with content) stays the premise rule of `ve/document.py` `_report` (batch 13b) |
| D13 | `check_joint_extensions` (called by `ve/document.py` `_report`) | the composition gate: lemma and report labels extend a compatible choice | `Admission.gateOk` over `gateChoices`, run by `admit2` (`jointGate`) |
| D14 | `validate_discourse`'s fallback joint recomputation and "Python's joint choices are over their budget" | joint set when Python's check failed | the admission's `admitted: UNKNOWN` and `joint` |
| D15 | `validate_discourse` `hints` / `report_discourse` `discourse_hints` | Python's disagreeing diagnostics beside an admission | none: dropped, DRI acceptance pending (DELTA V1) |
| D16 | `rust/ve-core/src/discourse.rs` `elaborated_document_case` and its `lib.rs` re-export, the `ve` CLI branch, and its test in `rust/ve-core/tests/conformance.rs` | a Rust re-check of Python's elaborated formulas (identities, premise search) | none needed: the Lean route decides; `ve conformance` refuses the family (`UnsupportedProfile`) |
| D17 | `rejection`'s Python wording of an abstention (`the Lean discourse route abstains (...)`) | the text of `NotImplemented` | Lean's text, under `UnsupportedProfile` (DELTA W4.1) |

No consumer of a deleted symbol remains: `git grep` over `ve/`, `tests/`, `tools/`, `conformance/`, `bench/`
and `usecases/` finds no use of the deleted names. The remaining mentions are prose in `docs/spec/discourse.md`
history sections and a comment in `lean/VE/Discourse/Grammar.lean` (DELTA, "Stale prose"), plus
`ve/risk.py`'s and `ve/rights.py`'s own, unrelated `decode_block`/`_decode_block`.

## Retained, named

| Site | Why it stays | Removed by |
|---|---|---|
| `ve/document.py` `base_environment` (moved from `ve/discourse.py`, its only caller's module) | the `@1` profile gate (`ve.discourse@1 requires ve-document@2`, as `Admission.admitAt` says for `@2`) and the stripping of `ve.discourse@1` before the frozen environment routes; on a `@2` document it runs only after Lean admitted, where a failure is `CheckerUnavailable` | batch 12 (environments and the profile gate) |
| `ve/discourse.py` `_error_of` | the route's rows carry no `code`; this is the prefix classification of a codeless row (like batch 0's retained `checker_error` branch), now with `NotImplemented` → `UnsupportedProfile` | batch 1 (the route becomes a service mode with a `code`) |
| `ve/discourse.py` `import_files`, `_import_names`, `_sibling`, `_embedded`, `is_discourse_text` | file I/O: the sibling files Lean receives as the case's `files`; format detection | — (relay I/O) |
| `ve/discourse.py` `lean_admission`'s two not-UTF-8 errors | rule 2's file I/O errors (bytes that cannot reach Lean); marked `# relay-lint: file I/O` and counted by `tools/relay_lint.py` | — |
| `ve/discourse.py` `_presentations` | display of Lean's resolved targets by their registered displays, gated by the English parser (build checklist 9) | E2/E3 (English to Lean) |
| `ve/discourse.py` `_JOINT_BUDGET` (64), `_MAX_NESTING` (4) | displayed beside an UNKNOWN joint set; how deep the file collector reads | batch 18 (one `VE/Limits.lean`, limits from the handshake) |
| `ve/document.py` `_report`'s joint-premise guard | the premise rule (only all-asserted readings with content form a premise), core premise status | batch 13b |

## Lines

Python (`ve/`, base to head, `git diff --shortstat 776a64d7 HEAD -- ve`): **1,279 lines deleted, 158 added**
(`ve/discourse.py` from 1,458 to 321 lines; the plan estimated about 1,190). `ve/document.py` is +35/−18, and
`base_environment` (17 lines) moved there. Rust: **110 lines deleted** (`discourse.rs` 78, its test 30, two
re-exports), 8 added (the refusal and its test). Lean: **+23/−7** in `VE/Discourse/Run.lean` (`choicesJson`,
`jointJson`, `jointFields`; `runJoint` reuses the first two), plus the `frozen-sources.sha256` line; no theorem
changed. Tooling: `tools/lean_first_diff.py` +42 (the discourse corpus), `tools/relay_lint.py` +22/−6 (the
discourse module and the file I/O marker), `docs/lean-first/b4/capture_discourse.py` and `cpu.py` (new).
