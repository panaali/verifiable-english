# Batch 16b deletion ledger

Base `8350e55f`. No Python decision site is deleted in this batch (DELTA.md, *Deviation*): each wrapper decision
below is Lean's for every document the `document` mode owns, and Python's copy is retained only for the mode's
`CheckerUnavailable` and `ResourceLimit` answers (DELTA.md, *Retained*). The `ve/` diff is the new caller
(`_lean_answer`, `_lean_document`, `_load`), the skips in `_report` and `coverage`, and `relay.answer`.

| Python decision or successful output (`ve/document.py`) | Owner for documents the mode owns | Python copy |
|---|---|---|
| `front_matter`, `_split`, `_body`: byte budget, front matter, format, metadata keys, couplings and completions gates, fences | `Service.Document.split` (`Loader.frontText`, `checkMetadata`, `bodyOf`) | retained: discourse `@2`, speech and norm-defaults loaders share it; the retained documents |
| `_load_document` unit loop: schema, ids, span partition, UTF-8 cuts, kinds, meaning, support, content, unformalised reason, meaning id, explicit status | `Service.Document.sourceUnit`, `unitsOf` | retained |
| `_parts`: MIXED partition and parents | `Loader.mixedParents`, `mixedOf`, `partOk` | retained (also used by speech and norm defaults) |
| open terms, reading sets, active-set status fold, couplings gate, lemmas, asserted-unit check, narrowings, weights | `Loader.openTermNames`, `compileSets`, `foldStatus`, `checkLemmas`, `narrowingIds`, `checkWeights` | retained |
| status inference and the explicit-status contradiction | `Loader.w2Status`, `Document.check` | retained |
| `_document_id`, `source_id`, unit `meaning_id` and canonical content | `Loader.documentId`, `Loader.sourceId`, `formulaOf` (rows' `content`, `meaning_id`) | retained (`stored_identities` for imports) |
| `coverage`: byte tables, residual counts, the alternatives/risk block line | `coverageJson`, `blockCoverage` | `coverage(doc)` returns Lean's for a Lean-built document; retained otherwise |
| `_report`: graph reading-label checks, `_check_narrowing_choices` | `Service.Document.admitGraph` (with `admit`) | skipped for a document Lean admitted; retained otherwise |
| `_report`: the claim graph's admission verdict | `Route.Run.dispatch` admission case inside the mode | Python asks `admit_document` for the report only (batch 13b's operation); a rejection there of what Lean admitted is `CheckerUnavailable` |

Not wrapper decisions, unchanged and not Lean's in this batch: the premise status (search, rule 3 and batch 15),
the reading plan's choice enumeration (`plan_choices`, batch 14d), rendering (display).
