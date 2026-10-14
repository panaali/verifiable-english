DRI signature needed: the measured trust budget rises by 17 Lean V lines (10 in English policy, 7 in readings decoder); the existing R6 allowance does not cover it.

# JT cross-plan fixes — build report

## Delivered items and directives

| Item | Delivery | Commits | Evidence | Owner |
|---|---|---|---|---|
| X2: only accepted templates claim a head word | Python's author lint and Lean's English policy discard heads of rejected templates; the accepted one-word renderings remain selected. | `7080d6d04`, `0b4509c58`, `cf079be92`, `da5b9d5e8` | `test_rejected_binary_template_does_not_take_accepted_unary_wordings`, Lean `E2Examples` guards, English S3 comparison | AGENT |
| X3: refuse a constant's `verbalisation` with the v0 field diagnostic | The `readings@1` environment decoder now refuses the field before it can reach the Rust conformance comparison. The v0 differential fixture compares Python and Rust; the soft extension remains accepted. | `47d1aaf05` | `test_readings_constant_verbalisation_uses_v0_field_diagnostic`, `test_v0_constant_field_differential_python_rust`, `test_soft_constant_display_extension_still_admitted` | AGENT |
| X4: one committed rebuild command after profile or vocabulary edits | `tools/readings_s1_pilot.py --rebuild-reading-ids ... --out ...` recomputes candidate, model, and situation IDs; `--check-noop` detects stale IDs. [PILOTS.md](PILOTS.md) documents it. | `8b010f82d`, `01f61e887`, `a58daa228`, `8dc3ecb63` | `tests/test_readings_s1_pilot_rebuild.py` | AGENT |

All three behavior changes are signed by item-specific DRI decisions X2–X4 in `DRI-DECISIONS-PHASE2.md`; [DELTA.md](DELTA.md) records the visible outputs. No model calls or push were made.

## Verification

- `lake build VE.EnglishGrammar.E2Examples`: passed all guards; the accepted `undermines` case was updated after a genuine failed guard.
- `lake build`: passed, 887 jobs.
- Focused regressions: 74 passed; the two legacy E2 response/report files: 64 passed.
- `tools/regen_generated.py --check`: first pass identified the new frozen hash, decoder pin, and 17-line trust allowance. The hash and pin were updated; final check: **pending**.
- `4a21bccb5` commits the generated Lean source and checker inventories. `f9fae7632` keeps the older RD-6b trust report tied to its saved reviewed revisions (D4); its targeted test passed.
- Selected test plan (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`): **pending**. Its first two runs found stale X2 expectations and an identity-inventory scope after X4 moved the existing digest call. Both were fixed; `tests/test_identity_lint.py` passed 107 tests.
- Full release gate: **not run by this builder**, as explicitly directed; the chain runs it on the committed final HEAD.
- Disk: 41 GB free before handoff. `git diff --check` and `tools/repo_map.py --check` passed.

Side-by-side CPU probes over the same pilot documents used the merge-base printer policy and this tree's policy with the same current checker. Constitution check/render was 405/329 ms at base and 320/270 ms here; UDHR was 8189/1186 ms and 7935/1331 ms. These are measurements, not timing assertions. `test_accepted_head_collection_scans_each_candidate_once` checks the head scan without a clock.

The S3 comparison was regenerated: 170 cases, 168 agreements, 2 dispositioned differences. The exact-text comparison records 158/163 agreement. The E2 gate result remains the historical result of its recorded commit; its report labels the refreshed S3 comparison separately.

## Seeded bugs

Each seed changed product code and failed a behavior test before restoration:

Python and Lean product code changed; Rust product code did not.

| Seed | File | Failing test and observed failure |
|---|---|---|
| Reinsert rejected template heads | `ve/printer.py` | `test_rejected_binary_template_does_not_take_accepted_unary_wordings`: the accepted renderings differed. |
| Bypass the constant display-field refusal | `lean/VE/Readings/Wire.lean` | `test_readings_constant_verbalisation_uses_v0_field_diagnostic`: `DID NOT RAISE VEError`. |
| Keep a stale candidate meaning ID | `tools/readings_s1_pilot.py` | `test_rebuild_updates_formula_candidate_meanings`: computed identity differed. |
| Keep stale model keys | `tools/readings_s1_pilot.py` | `test_rebuild_command_updates_every_set_after_environment_edit`: `DID NOT RAISE SystemExit`. |
| Keep stale situation keys | `tools/readings_s1_pilot.py` | `test_rebuild_updates_situation_keys_and_admission_references`: recomputed situation key differed. |

## Build-checklist audit

| Line | Disposition and evidence |
|---|---|
| 1. One contract | X3 calls Lean's existing `displayFields`; no diagnostic or limit table was copied. |
| 2. Differential fuzz | `test_v0_constant_field_differential_python_rust` checks the field refusal; the existing `tests/test_difffuzz.py` remains selected. No new cross-language answer contract was added. |
| 3. Normalization | No normalizer changed; the English S3 corpus remains selected. |
| 4. Untrusted output | No response field or relay was added; `tests/test_english_e2_responses.py` passed 64 tests after its genuine invalid-grammar fixture was updated. |
| 5. Malformed input | The readings constant field is rejected at Lean decoding; `tests/test_environment_field_types.py` and the X3 regression exercise field types. |
| 6. Three-valued verdicts | No budget or verdict logic changed; `tests/test_readings_budget_zero.py` is selected. |
| 7. Deadlines | No deadline or budget wrapper changed. |
| 8. Kind folds | No kind or owner fold changed. |
| 9. English | E2 guards, S3 cases, `test_rejected_binary_template_does_not_take_accepted_unary_wordings`, and Asimov round trips check the changed selection. |
| 10. Admission entry points | No new admission path; the new pilot command rewrites IDs for the ordinary document loader to check. |
| 11. Language parsing | The new decoder check uses Lean's JSON parser; no regex parser was added. |
| 12. State machines | No state machine or ledger code changed. |
| 13. Seeded mutants | Five restored seeds and their failing tests are listed above. |
| 14. Hermetic tests | The X3/X4 tests use fixtures and `tmp_path`, with no sleeps, network, or model calls. |
| 15. Identity | `test_rebuild_updates_formula_candidate_meanings`, the model and situation tests, and `tests/test_identity_lint.py` cover the moved site. |
| 16. Inventories | The grammar lock, frozen hash, Lean declarations, checker pin, trust classes, and assurance decoder pin were refreshed. |
| 17. Spec statements | `lean_statements.py` found no statement change; no theorem approval is required. |
| 18. Spec-stage theorems | No spec-stage theorem was added. |
| 19. Use-case formalisation | Only Asimov's accepted English wordings and pins changed; its rules and artifact tests were run. |
| 20. Reports | S3 and lexicon reports were regenerated from case rows; `test_committed_report_counts_are_derived_from_individual_records` checks the saved totals. The full gate was not run here. |
| 21. Acceptance owners | All X2–X4 deliveries are AGENT items in the table above; no HUMAN or EXTERNAL acceptance is claimed. |
| 22. Tests and gate | Iteration used focused regressions and the Mac selected-test wrapper. The user's explicit instruction reserves the full release gate for the chain on final HEAD. |
| 23. DRI rulings | [DELTA.md](DELTA.md) records the item-specific X2–X4 decisions and tests; the trust allowance still awaits a separate signature. |

## Self-review against BUILDER-CHECKLIST

1. N.A. — No new Lean answer shape or relay field; existing response mutation tests remain selected.
2. PASS — The X2–X4 delivery table and `git diff main...HEAD` review map every task row to tests.
3. PASS — The five seeded failures are listed above with their failing tests.
4. PASS — `test_v0_constant_field_differential_python_rust` and the S3 comparison exercise the changed input and English selection; valid soft input passes.
5. N.A. — No new response binding relation or relayed output field.
6. PASS — `lean/checkers.lock`, generated inventories, and `git log main..HEAD --no-merges` are reviewed on final HEAD; chain owns the full gate by explicit instruction.
7. PASS — DELTA.md cites DRI X2–X4 and the relevant regression tests; trust allowance: **pending**.
8. PASS — DELTA.md and the regenerated S3 case reports list the changed renderings and case counts.
9. PASS — `tools/select_tests.py --base $(git merge-base HEAD main)` selected 375/375 units, including the seeded regression.
10. N.A. — No theorem statement or response shape theorem changed; Lean E2 guards and statement inventory passed.
11. N.A. — No budget, limit, or deadline behavior changed.
12. PASS — The side-by-side pilot check/render CPU probe above and `test_accepted_head_collection_scans_each_candidate_once` check cost and scan count.
