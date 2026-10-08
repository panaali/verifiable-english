# Lean first batch 16a: document wrapper evidence

**Status: review fix 1 applied.** The first round below built a structural `document` mode that refused reading sets and every statement layer. The review (`lf-16a-review.final.md`, B1 to B4, C1 to C5) is fixed in the section *Review fix 1*: the mode now runs every `load_document` step and `check_document`'s wrapper (graph admission, coverage) for the profiles it owns, composes the alternatives and risk routes, and fails closed with `CheckerUnavailable` on what it cannot decide yet. The 16a plan lists no Python deletion; the Python changes of the fix round are bug fixes the comparison found, with no public outcome changed.

## First round: saved source scope

Range: `main..HEAD --no-merges`, captured at code HEAD `2c2a1b31a7aec4bbb508473086c88668de2e24e1` while `main` was `acee4ede1c932537e9f0057a906c6f1ac1dc041f`. The branch's original A/B base is `29773091b436c14653fb21099152ecff4403476c`. Main advanced afterward; all numbers below read this saved scope rather than a moving ref.

Source commits (saved): 2c2a1b31a7aec4bbb508473086c88668de2e24e1, 9da901f5450ba05b101ec99f9ab7302ce50c7c63, 2b5407b72d0409dd8c22f71ac23f96db9b1b83c0, 8d549d54082060c23eecf0be368ec9b33a2207ad, 8b18d28621f19c5bfc09df4bc6af966625c7fd65

- Total lines deleted: 255
- Lean lines added: 280
- Python lines deleted: 1 (service mode registration replacement; zero semantic duplicate lines)

These are cumulative per commit numstat counts, including generated schema, assurance, declaration and trust files. They are not a net diff and do not imply 255 lines of duplicate logic were removed.

## First round: gate evidence

- Full gate: passed; 11845 passed, 7 skipped; commit `2c2a1b31a7aec4bbb508473086c88668de2e24e1`, clean worktree, 0 failed. Rust: 37 passed.
- A/B identical: 94498 public outcomes across probe, conformance, readings, discourse, rights, quantity and pilots; zero differences and zero unlisted cases. Pilots identical: 303 documents. No DELTA or DRI signature is needed for these unchanged public outcomes.
- CI baseline: 352 entries, 0 new signatures; all baseline entries replayed, no unreviewed findings.
- Date seeds: 14 paired; 550 inherited signatures; 0 head-only. The 13 non-CI dates fail the absolute committed baseline, but each signature set is identical at the pinned base and head. This batch grows the baseline by zero; the inherited gaps remain a separate baseline triage item for the DRI.
- `tools/lean_statements.py`: 0 statements added, removed or changed. `lake build` and Lean audit passed inside the full gate.

## First round: failure sensitivity

Seeded mutants: 3 failed as expected. Each changed the Lean file, built `ve_service`, failed its targeted test, was removed, and the original source hash and build were restored:

- `span_partition`: removing the terminal byte partition check failed `test_gap_and_wrong_status_are_rejected`.
- `mixed_provenance`: dropping the MIXED parent id failed `test_mixed_parent_counts_parts_once`.
- `status_inference`: forcing CHECKED failed `test_utf8_partition_status_and_counts`.

## First round: ownership (superseded by Review fix 1)

The mode calls the existing Lean `VE.Discourse.Loader` for front matter, MIXED partitioning, meaning status and identities, and the existing Lean standalone environment and formula checkers for accepted cases. Its numeric response maps are closed to natural values in the generated client schema. The structural behavior is exercised by `tests/test_lean_document_wrapper.py`; the five `tests/test_b16a_evidence.py` checks read only the saved evidence files and report.

**AGENT completed:** structural mode, response schema and decoder inventory, clean gate, public A/B, CI and date seed differential checks, and three restored seeded failures. **AGENT unfinished:** Lean reading set composition, profile specific coverage and residual lines, status folds over nested statement layers, comprehensive malformed response and budget/deadline injection checks. **HUMAN deferred (DRI):** triage the 550 inherited date seed signatures and approve any future public deltas; no public delta was observed here. **EXTERNAL:** none.

The work is kept within the 16a Lean side: Python document check and display remain unchanged, as scheduled for 16b. Because the missing Lean branches are required by 16a, this report does not claim batch completion or authorize the 16b switch.

## Review fix 1

Every A and B finding of the review, and its C items, were fixed as classes; each failing example is a regression
test in `tests/test_lean_document_wrapper.py` (unless named otherwise).

| Finding | Fix | Commits |
|---|---|---|
| B1: reading sets, their status fold, profile-specific coverage and residual counts were refused | The mode runs W2's reading sets (`Loader.compileSets` in its Python mode, formulas through the `check` mode's typed decoder), the active-version status fold (`Loader.foldStatus`), narrowings, weights, lemmas and every residual line. An `alternatives@0` or `risk@0` document is composed from its block route: that route decodes the environment and admits the graph, and its coverage line (`Alternatives.Wire.coverage`) is relayed with a proof that it fits the row (`block_coverage_fits`, `cells_fits`). | 489080eb, 5afeee49, 44b1a7dc |
| B2: `ok` with coverage for nine documents Python rejects; the graph never validated | All nine checks, in Python's order and texts (asserted unit without content, unbound fence, couplings and completions gates, report metadata, weights, lemmas, dangling narrowings), and the claim graph's W2 admission and narrowing choices before any label is counted. | 489080eb |
| B3: valid documents rejected as InvalidInput | The profile gate runs before any environment decoder; a profile outside the owned set, a non-envelope block, a legacy language, a non-FOL family, a `@2` document, and front matter Python's JSON reads but the restricted reader does not (`null`, negatives, fractions, exponents, large numbers, duplicate keys, `NaN`, lone surrogates) are `CheckerUnavailable`. | 489080eb, 5afeee49 |
| B4: nothing compared the mode with Python | `conformance/document_wrapper.py` compares outcome, code, text and the whole projection; `tools/difffuzz.py` has a `document` surface in the CI run, with wrong-mode mutants that must be findings (`tests/test_difffuzz.py`); the seeds the mode owns must agree; the genuine service responses include the mode; budget 0 and a CPU deadline are tested. | b82aaac7, 2fce5544, 137a4dfb |
| C1: fault order | Explicit statuses after the fold, the unformalised reason before unformalised content, open terms before the unit list, MIXED parts interleaved with the unit loop, fences read left to right. | 489080eb |
| C2: a second metadata list | One table, `Loader.metadataKeys`, for both routes. | 489080eb |
| C3: report numbers outside the saved evidence | Every number below is read from `evidence/fix1/` by `tests/test_b16a_evidence.py`; line counts are the net diff, generated inventories counted apart. | this report |
| C4: `unresolved_reading_sets` always 0 | Counted from the reading sets (`test_residual_counts_are_nonzero_and_python_s`). | 489080eb |
| C5 and its class: Python crashes | A MIXED unit without an id, unhashable statuses, a malformed later reading and a non-object graph are diagnostics; texts naming `UnsupportedProfile:` or `ResourceLimit:` carry that code; block coverage no longer sends `null` contents. | b005dc8a, 04ea4dc3 |

### Fix 1: saved scope

Range: `192e496335c248d848fc1816f0b3b4fc6dd2fbcc..HEAD --no-merges`, captured at `8efa27f1dea862a36c7ad8d8526f79c1213e09ea`. Fix commits (saved): 8efa27f1dea862a36c7ad8d8526f79c1213e09ea, 5f71984f4aef2717e36935be19226331e743e50d, 137a4dfbb1c25ebb3da7b29ac88d9b759a2aeaa9, 9cffc4e322afec4907316b0342659375e1a07f2b, 2fce5544ae67822370cdead3aaf1cd61e306fd84, 44b1a7dced894d2c405d5197c271a647b55dd488, 04ea4dc3b1e1b792dc73a2b11b3b168d031c43a8, 5afeee499b9f14f63cc0a3f6a10ba0a40eee02fd, b82aaac789246efb1abe09c3363695fd83035517, b005dc8a848f5469e37092eb8112ea1efcc12133, 489080ebb815da3da3e77ec6dbfd43386bd42809

- Net lines: 2708 added, 440 deleted; source files (generated inventories and this report with its evidence excluded): 1625 added, 255 deleted
- Lean source lines added: 674
- Python lines deleted: 35 (bug fixes; no Python semantic duplicate is deleted in 16a)

The evidence below was measured at `2fce5544ae67822370cdead3aaf1cd61e306fd84`; the commits after it change only
conformance/document_wrapper.py, docs/lean-first/b16a/REPORT.md, docs/lean-first/b16a/evidence/fix1/ab.json, docs/lean-first/b16a/evidence/fix1/deep-document.json, docs/lean-first/b16a/evidence/fix1/difffuzz-ci.json, docs/lean-first/b16a/evidence/fix1/mutants.json, docs/lean-first/b16a/evidence/fix1/scope.json, tests/test_b16a_evidence.py, tools/difffuzz.py, tools/gate-collection.json, tools/trust-classes.json (layouts, the fuzz's profile label and CI sample, the report and its evidence).

### Fix 1: gate evidence

- Full suite at `6f3ec724`, run in the foreground in 7 parts (`-n 16`; the four tests over 10 minutes alone; the gate's nightly tests): 11906 passed, 6 skipped, 0 failed, of the gate's 11913 collected tests (the live model smoke test excluded, as the gate does). `lake build` and `lean/audit.py` passed (4682 theorems); Rust: 37 passed.
- A/B identical: 94588 public outcomes between the first round's head `192e4963` and `2fce5544`, zero differences and zero unlisted cases; pilots identical: 393 documents (the pilot branches grew since the first round).
- Difffuzz CI: 352 baseline entries, 0 new signatures, every entry replayed; the `document` surface ran 615 inputs.
- Deep document fuzz: 2 seeds at 10 times the CI sample, 50030 inputs, 0 new signatures.
- Fix seeded mutants: 9 failed as expected, each restored and the build hash re-checked: bridge_leaves_zero, no_status_fold, profile_gate_removed, unbound_fence_accepted, python_json_called_invalid, graph_not_admitted, block_line_dropped, mixed_parts_batched, python_unhashable_status.

### Fix 1: what the mode still refuses

Each of these is `CheckerUnavailable` naming its reason, never a verdict; each needs Lean logic its owning batch has
not delivered, so 16b must keep Python's path for it. AGENT, owner in parentheses:

- `reports@0`: its residual lines are Python's alone (`lean/REPORTS.md`, batch 8);
- `soft-norms@0` and `rights@0`: their documents are built by Python's decoders (batches 6 and 7);
- `norm-defaults@0` (batch 10), `readings@1` (batches 3 and 14), `speech-acts@0` (batch 11);
- the closure, n-ary and order families and quantity (`unit_schema`) environments: reading-set evaluation, open terms and admission there need batch 12's envelope decoders and batch 9's route composition;
- norm content and regulated predicates off a block (the norms route, batch 13), fenced English or strict content (the Lean surface parser, batch 13), distinguishing models the Lean model decoder refuses (batch 12);
- texts owned by other decoders are compared by outcome only: the environment decoder's (batch 12) and the formula decoder's and W2 admission's (batch 13), as conformance/DIFFFUZZ.md DF-3 and DF-9 record.

HUMAN (DRI): none new; no public delta was observed. EXTERNAL: none.
