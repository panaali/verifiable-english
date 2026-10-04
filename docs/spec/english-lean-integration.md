# English in Lean: integration checkpoint, 2026-10-04

Branch: `english-lean/integrate`. This checkpoint merges `english-lean/py` and `english-lean/lean` and reconciles the punctuation-adjacency ruling in the Python reference lexer. It is **not an admission cutover**. `english.admission` remains Python-authoritative, and the S2–S5 gates of [english-lean-PLAN.md](english-lean-PLAN.md) remain open. No frozen contract or existing Lean theorem statement changed.

## Changes and checks

- The gate collection contains the test IDs from both branches. The integration reference lexer now emits the same `punct(text, gluedBefore, gluedAfter)` shape as Lean. Its corpus has explicit adjacency values. The reference grammar conversion retains canonical comma, semicolon, colon, bracket and arithmetic spacing; disjoint spacing variants preserve derivation multiplicity. The rejection report records `coefficientNotNumeral` and the closed O1 ruling.
- The 20 spec lexer fixtures agree between Python and Lean on tokens, UTF-8 byte spans and rejection offsets. The 14 rejection probes are consistent, including the non-numeral coefficient. The English Lean focused suite passed: 103 tests. A fresh 1,020-text replay over all 17 S0 configurations found zero Python Earley versus reference-token verdict differences; it did not compare formulas or Lean meanings. The replay rewrote only timing fields of `tokens-report.json`, so those load-sensitive values were not committed.
- `lake build` passed (575 jobs) on the second run. The first run suffered a clang frontend crash while compiling generated C under concurrent load. `python3 lean/audit.py` passed: 302 source files, 3,093 named theorems, standard axioms only. The frozen-source and Lean layer checks passed. Free disk space was 65 GiB.
- Full pytest suite: `VE_NATIVE_PREBUILT=1 .venv/bin/python -m pytest -q -n 4` finished with 8,744 passed, 6 optional skips and no failures in 1:25:12. It ran against the committed code; this report received its final result afterward. No model calls were made.

## Review fixes (Astra and Fable reviews, 2026-10-04)

- **Lexicon validity, Python versus Lean** (Astra B1, B2). The Python reference of `Lexicon.valid` read each field as a dictionary, so a repeated entry escaped V1 and a negative without a positive crashed. It is now a condition-by-condition port of Lean's `Lexicon.failures` over the lexicon's lists, with a total `negativeTemplate`. `lean/VE/EnglishGrammar/LexiconFixtures.lean` is generated from `conformance/english-lean/lexicon.json` and the reference. It holds every corpus case (new review cases `r1`–`r9`) and one- and two-fault mutants of `LF`, each as a `#guard` on Lean's full failure set. `lake build` therefore checks Python against Lean on 159 lexicons. `tests/test_english_lean_lexicon.py` keeps the file current and checks that the mutants reach V1–V5. The Rust side has no lexicon check.
- **Numerals** (Astra B3). The reference lexer and the tree printer read and print decimals in blocks. Numerals and label indices up to the 10,000-character text limit lex as they do in Lean, regardless of Python's `int_max_str_digits`. The same boundary sources are fixtures on both sides.
- **Audit record** (Fable B1, Astra C). `lean/axioms.txt` was regenerated: 3,093 entries, including the 134 new theorems. `lean/audit.py` now fails when the record differs from its output, and `--write` regenerates it. `tests/test_lean_audit_record.py` checks the record against the theorem inventory without running Lean.

## Required work still open

S2 requires fixed-rule JSON with generation and locking, the English grammar/actions/meaning, `read`, the section 5.8 theorems, a service mode, and an end-to-end Python adapter. S3 requires the formula-level profile rules and conformance. S4 requires the specified 14 consecutive clean shadow days. S5 requires the authority change, renderer checks, and support-matrix parity. The reverse corpus, formula/witness comparison, and genuine Python/Lean/Rust three-way tests on the spec fixtures are absent. The worker reports' remaining S0 measurements (use-case and pilot lengths, unloaded wall-clock timing) are also absent. No one-reading, frozen-contract or axiom claim has been widened to cover these missing stages.

## Build checklist audit

The numbers refer to `~/code/manage-agents/prompts/build-checklist.txt`. “Not done” means the line applies to the requested admission integration and still needs evidence; partial checks are described where present.

| Line | Status | Evidence or remaining requirement |
|---|---|---|
| 1 | Not done | English diagnostics and limits have no single generated Python/Lean/Rust table. |
| 2 | Partial | Lexicon validity has a generated one- and two-fault Python/Lean differential (`LexiconFixtures.lean`). There is no English reader or Rust differential. |
| 3 | Not done | No shared normalization function across the new English reader and every entry point. |
| 4 | Not done | No English service response schema or response mutation fuzz. |
| 5 | Not done | No English service malformed-node sweep or reference-resolution proof. |
| 6 | Not done | Generic parser tests budget exhaustion, but every public English operation has not been tested at budget zero. |
| 7 | Not done | Whole-operation deadlines and injected callee delays are absent for the proposed service. |
| 8 | Not applicable | This integration adds no kind/owner folds. |
| 9 | Not done | No all-constructor render → Lean parse → AST gate. |
| 10 | Not done | The English entry points do not yet route through one Lean-authoritative `admit()`. |
| 11 | Not applicable | The integration adds no import/source-language parser to an admission path; the Lark-to-token converter is measurement-only and fails on unrecognised terminal patterns. |
| 12 | Not applicable | No state-machine or ledger code changes. |
| 13 | Not done | Engine cap mutants exist, but no seeded admission-gate mutants or genuine three-way fixture test. |
| 14 | Not done | No hermetic English service gate or cache-independent binary hash check. |
| 15 | Not done | English grammar and certificate identity fields are not implemented. |
| 16 | Not done | New test IDs are in the gate collection and new Lean sources in the frozen inventory; full profile/corpus/registry coverage remains unproved. |
| 17 | Not done | No script diffs section 5.8 Lean statements against approved text. No existing statement was changed here. |
| 18 | Not done | Generic theorems are proved and fixtures evaluated; section 5.8 English-stage obligations remain. |
| 19 | Not applicable | No use-case formalisation was added. |
| 20 | Not done | S1 report numbers are not regenerated from gate JSON by a test; no G2–G5 verified claims exist. |
| 21 | Not done | Acceptance items lack AGENT/HUMAN/EXTERNAL tags and deferred owners. |
| 22 | Not done | Commits, disk check and this report exist; a full gate on final HEAD in a clean worktree is still required. |
