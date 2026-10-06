# English Lean E2 Lean work report

Branch `english-lean-e2/lean`; local commits `f3147ce3`, `dfb426d1`, `56b96a2a`, `246ddf04`, `237e5c9f`, `61383f34`, `3084dadd` and this report commit. Nothing was pushed. Frozen Norms, SoftNorms and Route Lean source was not edited; `VE/Route/frozen-sources.sha256` changed only to record the changed English and audit files.

## Implemented

- E2 policy selection, V6 failure order, O1–O3 overlay checks, Unicode and token scanners, and the approved `policy_selection` proof.
- Guarded read, translate, grammar and candidate-check paths; service modes `english.read`, `english.grammar`, `english.check` and their `rfl` pins; E2 response data including obligations, spans, codes and advice.
- Boundary decoding for the staged profiles, norms defaults, soft norms and units; display environment identity binding.
- A temporary S2 projection at the one-shot executable boundary while the Python relay still consumes its old field set. The E2 service response retains the E2 fields and V6 order.

## Verification

- `PATH=~/.elan/bin:$PATH lake build`: passed, 759 jobs.
- `python3 lean/audit.py --write`: passed, 417 source files and 4,393 theorems; only `propext`, `Classical.choice` and `Quot.sound`.
- `python3 tools/check_english_s3_statements.py`: passed, 10 exact S3 statements.
- `python3 tools/check_english_e2_statements.py`: 10 of 12 exact E2 statements found; see open work below.
- `tests/test_english_lean_route.py`: 60 passed.
- The clean-HEAD gate on `237e5c9f` selected 11,159 Python tests: 10,990 passed, 162 failed and 7 skipped; Rust tests passed. The failures exposed stale service mode lists, generated assurance pins, the S3 fixture report and the declaration table. Those integration artifacts are repaired in `61383f34` and `3084dadd`. The gate is being repeated on this report commit; its outcome must be reported at handoff.
- Focused integration checks after repair: 597 passed, three failed before the last corrections; the three failures were generated assurance tables, new mode deadlines and malformed-response seeds. All ten targeted regression checks then passed. S3 fixture comparison: 200 cases, 198 agreements, two spec-disposed differences, zero unexplained.
- The declaration table now covers all new E2 declarations conservatively. The trust budget check already had two issues at starting commit `73257d6a`; its baseline has not been changed or given a fabricated DRI signature.
- `python3 tools/english_grammar_gen.py --check`, `python3 lean/VE/Route/frozen.py`, and `git diff --check`: passed.
- `python3 lean/audit.py` read-only check and `python3 tools/gate.py --workers 4` are required before handoff; record their final outcome with the gate result.

Three temporary mutations of `Policy.lean` each failed a committed `#guard` in `ProfileExamples.lean`, then were removed:

1. Kelvin folding `K → k` changed to `K → x`: `#guard pyLower "Kİ" == "ki\u0307"` failed (`/tmp/e2-mutant-Kelvin-fold.log`).
2. Hyphen continuation disabled: `#guard tokens "Audit-Case" == ["Audit-Case"]` failed (`/tmp/e2-mutant-hyphen-token.log`).
3. Word-boundary scan forced false: `#guard wordOccurs "foo" " foo bar"` failed (`/tmp/e2-mutant-word-boundary.log`).

## Open work

The approved `sensesRequest_policy` and `decode_encode` statements are not yet proved. The Lean tree has no `VE/Senses` implementation to which the first statement can attach. The general JSON codec roundtrip proof remains open; four concrete formula cases in the spec are not a proof for all formulas. No axiom or `sorry` was added to cover either gap. The E2.0 prepared grammar cache and deletion of `ve_english_route` remain coordinated with the Python relay migration. The response-shape schema currently checks the outer envelope but treats the inner result as opaque. The Python/Lean selection and overlay parity harness of E2.1 has not been built.

## Build checklist (`~/code/manage-agents/prompts/build-checklist.txt`)

| Line | Status | Evidence or reason |
| --- | --- | --- |
| 1. Generated diagnostics, limits, JSON table | Open | E2 code/class text remains in Lean functions rather than one cross-language generated table. |
| 2. Py/Lean/Rust differential fuzz | Open | Rust has no English parser, but Py/Lean selection and overlay differential mutation coverage is still required by the E2 plan. |
| 3. Shared normalization and Unicode fixtures | Open | Kelvin and dotted-I scanner guards exist; the full per-entry-point normalization matrix is absent. |
| 4. Untrusted output schema | Open | The outer response envelope has a generated schema; its inner E2 `result` remains opaque. |
| 5. Malformed JSON node replacement | Open | Boundary decoding exists; seven-shape/deep-node fuzz coverage was not added. |
| 6. Three-valued verdicts and budget zero | Open | The reader preserves `budget`, but every public budget-zero path has not been checked. |
| 7. Whole-operation deadlines | Not applicable | E2 Lean modes are pure computations; deadline ownership is in the relay migration. |
| 8. Kind and owner folds | Not applicable | No kind/owner fold changed in this Lean work item. |
| 9. English render/parse roundtrip | Open | S3 unique-reading fixtures pass, but the all-constructor roundtrip matrix is incomplete. |
| 10. One `admit()` entry path | Not applicable | CLI and Python entry-point migration is the separate E2 relay work item. |
| 11. No regex over real languages | Done | New Lean policy uses explicit character/token scanners; Lean compiled the source. |
| 12. State machine and ledger | Not applicable | No state-machine or ledger code changed. |
| 13. Seeded mutants | Done | Three distinct scanner mutations failed the three `#guard`s and were removed. |
| 14. Hermetic execution | Open | A clean-HEAD gate ran and exposed integration failures; the final clean-HEAD repeat is pending. |
| 15. Identity mutations | Open | Lexicon/display identity is bound; mutation coverage for every schema field is incomplete. |
| 16. Registered lists | Done | English grammar lock, frozen source inventory, audit manifest, statement inventories and service modes were regenerated or checked. |
| 17. Approved statement diff | Open | The E2 diff tool finds 10 exact statements and two missing proofs. |
| 18. Spec-stage fixtures and iff boundaries | Open | Existing S3 fixtures and new scanner guards pass; E2 fixture matrix is incomplete. |
| 19. Use-case formalisation | Not applicable | No use-case rule or answer key was changed. |
| 20. Regenerated report numbers | Open | First gate counts came from `/tmp/e2-gate-result.json`; no test yet regenerates every report number. Final gate JSON is pending. |
| 21. AGENT/HUMAN/EXTERNAL labels | Open | E2 plan acceptance labels have not been fully annotated. |
| 22. Commit, full gate, disk, report | Open | Source commits and this nonempty report exist; full gate on a clean HEAD is pending. Disk had 59 GB free. |
