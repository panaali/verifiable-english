DRI signature needed: the measured trust budget rises by 18 Lean V lines against the merge base (English policy +15, readings decoder +3); the existing R6 allowance does not cover it. `python3 tools/trust_map.py --check` and therefore `tools/regen_generated.py --check` (entry `trust-tables`) fail until the DRI signs the allowance.

DRI waiver or main fix needed: the relay mutation gate's 29 remaining failures (graph, route, parse) are identical on main `f75082449`; see *Pre-review continuation (ready1)*.

# JT cross-plan fixes — build report

## Delivered items and directives

| Item | Delivery | Commits | Evidence | Owner |
|---|---|---|---|---|
| X2: only accepted templates claim a head word | The printer's lint reaches a fixed point: the templates that pass without heads claim theirs, and those that then reject each other give them up. The English producer (`ve/english.py`) reads only those claimed heads in its rescue, idiom and negation checks. Lean's policy (`PolicyCtx.of`) computes the same fixed point in one round, keeps each kept wording's codes, and reads each predicate's claimed head. | `7080d6d04`, `0b4509c58`, `cf079be92`, `da5b9d5e8`, `4e28a9ad7`, `4db4c7853`, `b26f68a69`, `8f000e4e5` | `test_rejected_binary_template_does_not_take_accepted_unary_wordings`, `test_templates_that_reject_each_other_give_up_their_shared_head`, `test_rejected_template_head_does_not_block_an_accepted_idiom`, Lean `E2Examples` guards (`Fpermits`, lx22c, reference agreement), English S3 comparison | AGENT |
| X3: refuse a constant's `verbalisation` with the v0 field diagnostic | The `readings@1` environment decoder refuses the field before it can reach the Rust conformance comparison. The v0 differential fixture compares Python and Rust; the soft extension remains accepted. | `47d1aaf05`, `9a07acb04` | `test_readings_constant_verbalisation_uses_v0_field_diagnostic`, `test_v0_constant_field_differential_python_rust`, `test_soft_constant_display_extension_still_admitted` | AGENT |
| X4: one committed rebuild command after profile or vocabulary edits | `tools/readings_s1_pilot.py --rebuild-reading-ids ... --out ...` recomputes candidate, model, and situation IDs; `--check-noop` detects stale IDs. [PILOTS.md](PILOTS.md) documents it. | `8b010f82d`, `01f61e887`, `a58daa228`, `8dc3ecb63` | `tests/test_readings_s1_pilot_rebuild.py` | AGENT |

All three behaviour changes are signed by the item-specific DRI decisions X2–X4 in `DRI-DECISIONS-PHASE2.md`; [DELTA.md](DELTA.md) records the visible outputs. No model calls or push were made.

### Second session: what changed and why

The first session's X2 fix left two gaps, both found by probing Python against Lean:

1. **The producer still read rejected heads.** `ve/english.py` took `_template_head` of every declared template in its rescue collision, idiom collision, `is`-head negation and suggested-head checks. Lean's policy (changed in `0b4509c58`) reads only accepted heads. For lx22c (`undermines` `{0} undermines {1}` beside `erodes` `{0} undermines the oversight role of {1}`), Python fell back while Lean accepted the wording, so Lean's V6 would have refused Python's own lexicon. `4e28a9ad7` makes the producer read the printer's claimed heads (`_NaturalVocabulary._heads`).
2. **Lean stopped one round early.** Python's printer loops until no candidate is rejected. Lean's `PolicyCtx.of` claimed the heads of everything that passed the head-free lint and stopped there, so wordings that rejected each other through a shared head kept it. `4db4c7853` added the drop round. `b26f68a69` notes that fewer heads only remove codes, so a single drop round already reaches Python's fixed point. It removes the recursion and stores the settled codes and each predicate's claimed head. That also replaces the per-pair head-table search that `0b4509c58` had added.

Two existing tests asserted the old behaviour that X2 reverses: a rejected template's head blocking an idiom, and two rejected templates' head taking a word from a sort noun. Each keeps its original setup with the new X2 result asserted. Each also gains a variant where an *accepted* head still blocks (`test_idioms_still_check_collisions_and_argument_direction[head]`, `test_template_head_and_identifier_collisions_across_all_categories`).

`5fbcd6c89` (first session) had edited `tests/test_readings_defaults_rd8_report.py`, whose `test_review_fix_commit_chain_and_final_gate_target` is listed in `main-known-red.txt`; `6036e2d56` reverts that edit (see *Pre-existing failures*). `f9fae7632` (first session) stays: the RD-6b report test compared the live tree with the trust baseline, which fails for any later trust change; it now reads the saved revisions, as the B12 report test does (D4), and `trust_map.py --check` in the gate still compares the live tree.

## Verification

- `lake build`: passed, 887 jobs, on the final Lean sources. `python3 lean/audit.py`: PASS, 483 files, 5784 theorem declarations. `Read.lean`'s `overlayCheck_constants` stays a `rfl` (`PolicyCtx.of` drops the overlay's constant entries, which no table reads).
- `tools/regen_generated.py --check`: every entry passes except `trust-tables` (the unsigned allowance above). The grammar lock's `actions_version` is 30 (main 28).
- Selected test plan (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`): **exit 0, 375 units, 0 failed**, on the Mac runner at `03367e896`. The plan for `8f000e4e5`'s guard wrap and inventory refresh (`--base HEAD~1`, 43 units) ran on the loaded VM (load ~80): 42 passed and `tests/test_english_evidence.py` hit the per-file timeout; rerun alone on the Mac runner at `5ae5c9cc5`: 67 passed.
- Focused: `tests/test_english.py`, `tests/test_views.py`, X3/X4 tests, E2 responses and statements, S3 compare and copy, assurance manifest and Asimov: 479 passed.
- S3 comparison regenerated: 170 cases, 168 agreements, 2 dispositioned differences; exact-text 158/163.
- `git diff --check` and `tools/repo_map.py --check` passed.
- Full release gate: **not run by this builder**, as directed; the chain runs it on the committed final HEAD.

### CPU (GE2 item 9)

Compiled `ve_english_lean_bench --policy` at 256 predicates, least of five, base and head alternated ([policy-bench.json](policy-bench.json)): the evidence's environment 45 ms (base 62 ms); 16 mutually rejecting pairs 69 ms (base 60 ms, +15%). Both are inside the 100 ms budget and the plan's +20% rule. An intermediate version that recursed and searched the head table per pair cost 83 ms; the one-round fixed point and the claimed-head field removed that. First session's pilot probes (constitution, UDHR check/render) are unchanged in kind; Python's producer now does fewer head scans.

## Seeded bugs

Each seed changed product code and failed a behaviour test before restoration. Python and Lean product code changed; Rust product code did not.

| Seed | File | Failing test and observed failure |
|---|---|---|
| Reinsert rejected template heads (session 1) | `ve/printer.py` | `test_rejected_binary_template_does_not_take_accepted_unary_wordings`: the accepted renderings differed. |
| Producer reads every template's head again | `ve/english.py` | `test_rejected_template_head_does_not_block_an_accepted_idiom`: `{0} has the recorded relation "undermines" to {1}` ≠ `{0} undermines {1}`. |
| Printer loop never drops (`rejected = set()`) | `ve/printer.py` | `test_templates_that_reject_each_other_give_up_their_shared_head`: `{0} is classified as "open"` ≠ `{0} is fully permits`. |
| Lean skips the drop round (`if true then { c with settled }`) | `lean/VE/EnglishGrammar/Policy.lean` | `lake build VE.EnglishGrammar.E2Examples`: the `Fpermits` guards (lines 190–191 at `b26f68a69`, now 190–193) did not evaluate to `true`. |
| Lean idiom check reads every head (`let head := f.head`) | `lean/VE/EnglishGrammar/Policy.lean` | `lake build VE.EnglishGrammar.E2Examples`: the lx22c guard (line 183 at `b26f68a69`, now 183–184) and `policyEnvs.all agreesWithReference` (605, now 606) failed. |
| Bypass the constant display-field refusal (session 1) | `lean/VE/Readings/Wire.lean` | `test_readings_constant_verbalisation_uses_v0_field_diagnostic`: `DID NOT RAISE VEError`. |
| Keep a stale candidate meaning ID (session 1) | `tools/readings_s1_pilot.py` | `test_rebuild_updates_formula_candidate_meanings`: computed identity differed. |
| Keep stale model keys (session 1) | `tools/readings_s1_pilot.py` | `test_rebuild_command_updates_every_set_after_environment_edit`: `DID NOT RAISE SystemExit`. |
| Keep stale situation keys (session 1) | `tools/readings_s1_pilot.py` | `test_rebuild_updates_situation_keys_and_admission_references`: recomputed situation key differed. |

## Pre-existing failures

`tests/test_readings_defaults_rd8_report.py::test_review_fix_commit_chain_and_final_gate_target` is in `main-known-red.txt` (lf-14d, 4667e8de). This branch no longer edits it; it fails here as on main and belongs to its own fix item.

### Pre-review continuation (ready1)

The pre-review gate at `1fd825843` failed on two lines.

- **Gate.** The chain's full gate failed only in its coverage stage: `0b4509c58` had renamed `tests/test_asimov_extended.py::test_v2_files_are_unchanged`, so that ID left the collection. `97366773d` restores the name; the test still checks the refreshed X2 pins. `tools/gate_collection.py --check` on the final HEAD reports 12 added and 0 removed IDs against main.
- **Relay mutation gate.** At the old merge base `4667e8de` the same build reported 106 failures on `service:graph` and `service:readings-route`, identical to the branch (same mutant counts: 786 and 15728). Main has since filed the readings-route mutants (`f06911d83`, `bad2756f2`), so `352880cef` merges main (`f75082449`). Its only conflicts were the assurance manifest and its doc, both generated, and `tools/regen_generated.py --resolve --only assurance-manifest --only assurance-doc` resolved them. The merge also added a `ve_service` pin to `lean/checkers.lock` through its writer. `lake build` passed (890 jobs). Every `regen_generated --check` entry passes except `trust-tables`, which still reports the +18 V lines awaiting the DRI (the first line of this report).
  After the merge, `tools/relay_mutation_gate.py` reports **29 failures over 40 routes and 111457 mutants**. Plain main `f75082449`, built in a separate worktree, reports **the same 29 lines**. They are on `service:graph` (`background/*/ast` untyped and accepted, `background/*/label` empty), `service:route` (`background`, `generators`, `premises` empty/duplicate/rebind), `service:parse` (`error` empty, `span` drop), and seven allow-list paths that match nothing (B0/F4 `graph supporting_edges`, F4 `route error`, F10 `readings-route fill` and `units/*/content/norm/over`). None of these routes reads code this branch changes. Per the main-known-red rule they belong to their own fix item. They need a main fix or a DRI waiver for this item (`review-ready-allow.txt`). This branch does not edit the allow-list to hide them.
- Selected tests on the merged HEAD `352880cef` (Mac runner, `--base $(git merge-base HEAD main)`): **exit 0, 377 units, 0 failed**.

### Pre-review continuation (ready2)

The pre-review gate at `cb8636a01` failed only on the relay mutation gate, with the same 29 findings main has. No waiver was filed. This branch now takes the relay-only repair that premise-scale wrote and tarch-b8 copied, with the same hunks, so whichever branch merges second gets a clean merge:

- `a88897564` (cherry-pick of tarch-b8 `0ba241d9a` = premise-scale `8808fb359`): the graph schema types each Background leaf. The label is `background:<generator>` with one of Lean's generators, and the AST is `common.json#/$defs/generated_formula`. The B0/F4 allow-list paths for `supporting_edges` move to `background`. The `lean/declarations.txt` conflict was regenerated with `tools/regen_generated.py --write --only lean-statements`.
- `00449ff9a` (cherry-pick of tarch-b8 `3663dd1b4`, the relay part of premise-scale `b961596b5`): the parse diagnostic is typed `text` (non-empty). Route Background, generators and premise lists are filed under B0/F4, and the parse `span` drop under F5, with `test_parse_diagnostic_text_cannot_be_empty`.
- `db239d62c`: prunes the three F10 readings-route paths that match no mutant (`fill` for empty and duplicate, `units/*/content/norm/over` for duplicate), the same paths premise-scale prunes.
- `fbde7eee0`: `tests/test_relay_mutation_gate.py::test_graph_background_labels_and_formulas_are_typed` covers the graph Background typing in the suite (tarch-b8 review F4). A genuine answer is accepted. Its label emptied or rebound, its AST nulled or emptied, and its first AST node nulled or emptied are each refused.
- DELTA.md gains the two R8 rows (graph and parse).

Evidence: after `lake build` (890 jobs), `tools/relay_mutation_gate.py` reports **40 routes, 111457 mutants, 0 failures**. `tools/regen_generated.py --check` passes every entry except `trust-tables`, which still shows the same +18 V lines that await the DRI. `tests/test_relay_mutation_gate.py`: 20 passed. Selected tests at `fbde7eee0` (Mac runner, `--base $(git merge-base HEAD main)`): **exit 0, 377 units, 0 failed**.

Seeded bug (Lean, restored): in `lean/ResponseShape/Schemas/Graph.lean`, the Background `ast` shape was reverted to `n [arr, .minItems 1]`, rebuilt and regenerated with `tools/response_schemas.py --write`. `test_graph_background_labels_and_formulas_are_typed` then failed with `AssertionError: ('retype', (..., 'background', 0, 'ast', 0))`, `'accepted' == 'refused'`. Restored, regenerated (no diff), and the test passes.

## Build-checklist audit

| Line | Disposition and evidence |
|---|---|
| 1. One contract | X2: Lean's `PolicyCtx.of` and Python's printer compute the same fixed point; the producer reads the printer's table instead of recomputing heads. X3 calls Lean's existing `displayFields`. |
| 2. Differential fuzz | `test_v0_constant_field_differential_python_rust`; `E2Examples`' `policyEnvs.all agreesWithReference` now includes `Fpermits`; the S3 comparison checks Python against Lean on the spec fixtures. |
| 3. Normalization | No normalizer changed. |
| 4. Untrusted output | No response field or relay was added; `tests/test_english_e2_responses.py` passed. ready2: the graph Background leaves and the parse diagnostic are now typed by their Lean shapes; relay mutation gate 0 failures; `test_graph_background_labels_and_formulas_are_typed`. |
| 5. Malformed input | The readings constant field is rejected at Lean decoding; `tests/test_environment_field_types.py` and the X3 regression exercise field types. |
| 6. Three-valued verdicts | No budget or verdict logic changed. |
| 7. Deadlines | No deadline or budget wrapper changed. |
| 8. Kind folds | No kind or owner fold changed. |
| 9. English | E2 guards, S3 cases, the four X2 tests above and Asimov round trips check the changed selection. |
| 10. Admission entry points | No new admission path. |
| 11. Language parsing | The decoder check uses Lean's JSON parser; no regex parser was added. |
| 12. State machines | No state machine or ledger code changed. |
| 13. Seeded mutants | Nine restored seeds, at least one per changed language and behaviour, are listed above. |
| 14. Hermetic tests | New tests build environments in memory or under `tmp_path`; no sleeps, network or model calls. |
| 15. Identity | `tests/test_readings_s1_pilot_rebuild.py` and `tests/test_identity_lint.py` cover the X4 sites. |
| 16. Inventories | Grammar lock (30), frozen hashes, Lean declarations, checker pin (one new `ve_service` pin over the merge base), trust classes and assurance decoder pin refreshed by their tools. |
| 17. Spec statements | No theorem statement changed (`overlayCheck_constants` keeps its statement and its `rfl` proof). |
| 18. Spec-stage theorems | None added. |
| 19. Use-case formalisation | Only Asimov's accepted wordings and pins changed (session 1). |
| 20. Reports | S3 reports regenerated from case rows; `policy-bench.json` holds the CPU runs. |
| 21. Acceptance owners | All X2–X4 deliveries are AGENT items. |
| 22. Tests and gate | Selected tests and focused tests as above; the chain runs the full gate on final HEAD. |
| 23. DRI rulings | DELTA.md: X2–X4 signed by the item decisions; CPU within the relative rule; trust allowance awaits a DRI signature. |

## Self-review against BUILDER-CHECKLIST

1. PASS — No new relay field. ready2 tightens two existing shapes (graph Background, parse error) in Lean's `ResponseShape` and regenerates their JSON; relay mutation gate 0 failures over 40 routes; `test_graph_background_labels_and_formulas_are_typed`, `test_parse_diagnostic_text_cannot_be_empty`.
2. PASS — X2–X4 table above; `git diff $(git merge-base HEAD main)...HEAD` reviewed against the task; the known-red test edit was reverted (`6036e2d56`).
3. PASS — Nine seeds listed above, each with its failing test.
4. PASS — `E2Examples` `agreesWithReference` over `policyEnvs` incl. `Fpermits`; `test_rejected_template_head_does_not_block_an_accepted_idiom` matches Lean's lx22c guard; S3 comparison 168/170; valid accepted wordings still pass (`test_idioms_still_check_collisions_and_argument_direction`).
5. N.A. — No new response binding relation or relayed output field.
6. PASS — Checker pin, inventories and selected tests are from the final Lean sources (`03367e896`, then `8f000e4e5` for the wrapped guard); the chain runs the full gate on final HEAD.
7. PASS — The only unsigned item, the trust allowance, is the first line of this report and a DELTA row; the two ready2 relay rows are signed R8.
8. PASS — DELTA.md lists the producer, fixed-point, lx22c, sort-noun and CPU deltas.
9. PASS — `tools/select_tests.py --base $(git merge-base HEAD main)` selected 375/375 units, including the X2 tests and `E2Examples`.
10. PASS — No statement changed; `overlayCheck_constants` still proves by `rfl`; the one-round claim rests on head-monotone codes and is checked by the `Fpermits` guards.
11. N.A. — No budget, limit or deadline behaviour changed.
12. PASS — `policy-bench.json`: compiled V6 at 256 predicates 45/69 ms against base 62/60 ms, inside 100 ms and +20%.
