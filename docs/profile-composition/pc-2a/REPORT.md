# pc-2a report: `ve document check` composes soft-norms@0 with norm-defaults@0 through the norm-defaults mode's own decoder

Status: built; REPORT_STATUS. No signature outstanding: DELTA's five DRI rows are signed (reviews/dri-decisions-20261103-pc-2a.md, -rows45.md), the rest cite R6 and R16.
HEAD: see the chain's gate-result.json. Base `90807e7f7`; main has since moved 135+ commits, and this branch has not merged it (see "Not done").
Changed: Lean's document mode answers this chain through `DocumentChain.layeredOf`, then `validateCompletions`; the retained Python loader no longer accepts it.
Open: size is 1,1xx hand-written lines against the ~600 line (over, not cut: "Size"); F2.2 compares what both commands report, not an entailment ("F2.2").
Next item: pc-2b (the soft chain with `readings@1` in the document mode).

## Plan rows

| Row (plan "PC-2a", spec 3.2 and 5.2) | Delivered | Where | Checked by |
|---|---|---|---|
| (1) `requestOf`, `layeredOf`: the mode's own `decodeLayered`, no second elaboration, no `chainCheck` | yes, **in lean/VE/Service/Document.lean, not DocumentChain.lean** (deviation 1) | namespace `VE.Service.DocumentChain` | `test_statements_equal_the_spec`; DocumentChainExamples guards |
| (2) PC-2 (1) `layeredOf_ids`, PC-2 (2) `layeredOf_entails` | yes, proved, equal to the spec's text | lean/VE/Service/DocumentChain.lean | `tools/check_pc2a_statements.py`: "4 statements equal the spec"; `python3 lean/audit.py`: PASS |
| PC-2 (3) "two entry points, one answer" | by construction, as the spec says; **no theorem** | | F2.1b from both entry points; F2.3 |
| (3) Refusal text; the soft branch calls `layeredOf` | yes; the remaining text is spec 4's row 4 | `environmentOf`, `check` | `test_f2_3_the_refusal_names_only_what_is_still_refused` |
| (4) F2.1 | yes | lean/VE/Service/DocumentChainExamples.lean, tests/test_document_chain.py | `test_f2_1_point_statuses`, `test_f2_1_an_exception_without_its_decision_is_no_situation_of_the_document` |
| (4) F2.1b | yes | same | `test_f2_1b_validate_completions_answers_from_both_entry_points`, `test_f2_1b_a_valid_completions_entry_is_accepted_from_both_entry_points` |
| (4) F2.2 | **partly** ("F2.2" below) | tests/test_document_chain.py | `test_f2_2_check_and_readings_report_the_same_premise_status` |
| (4) F2.3 | yes, under the DRI's reading of "byte-identical" (item 2) | tests/document_chain_corpus.py, tests/data/composition/pc2a/parity-base.json | `test_f2_3_every_answer_equals_the_retained_loaders` |
| (4) F2.4, DeepMind DF-c | the harness's: expected admitted; **not measured** | | |
| (5) Delete the Python branch | its acceptance, yes ("The deletion"); rd-9 rows added (D9) | ve/document/load.py, docs/spec/rd-9-relay-binding.md, tests/test_relay_binding_inventory.py | `test_the_retained_branch_accepts_nothing_of_this_chain`, `test_every_bound_field_mutant_is_unavailable[document-soft-defaults]` |

Plan and spec on main are the copies this report reads; line numbers differ from the task's (it cites 938e148cb): plan "PC-2a" is lines 784-823 here, spec 3.2 starts at 1577, its F2 table at 3099.

## Deviations

1. **`requestOf` and `layeredOf` stand in Document.lean.** `Document.check` calls `layeredOf`, and `DocumentChain.lean` must import Document for `Env` and `SourceUnit`: an import cycle. Moving those types would collide with qt-a4's edits to `Env` and `UnitContent`. Names, signatures and statements equal spec 3.2. Noted by the DRI (decision item 4(a)); PC-2b may move them once qt-a4 has merged.
2. **`layeredOf_ids`' hypothesis `hs` is unused.** `requestOf` makes a case only on the soft route (`layeredRoute` on `E.lower`), so the soft pack follows without it. The statement keeps it, as approved; PC-2c, which adds the rights document, is where it will be read.
3. **Rights.** `requestOf` makes no case for a rights document (`null`, refused by the decoder), so `layeredOf_entails` needs only `decodeSoftU_X_wellFormed`. `decodeRightsU_X_wellFormed` is PC-2c's, as the task says.

## F2.2: what is and is not shown

`ve document readings --conclusion` does not read soft rules: `_report_premise_context` says its query keeps "its own frozen lower-route identity", and on the strict rule it answers `NONE` for the rule's direct consequence (saved in parity-base.json, row `u0125.s04.p2`). `ve document check` does read them: the same rule with a contradicting claim is `INCONSISTENT` there (`test_f2_2_a_strict_rule_contradicted_by_a_claim_is_inconsistent_in_check`). So the two commands agree on the fixture's premise status and vacuity, which is what the test compares, **but they do not give one answer to whether the rule entails a conclusion, and with a contradicting claim they disagree**. This is the base's behaviour; F2.3 forbids changing it here. It is PC-2b's to close (`chainReadings`). The DRI has read this (decision item 4(b)).

## The deletion

`soft-norms@0` with `norm-defaults@0` and `readings@1` still reaches the retained path until PC-2b, so `check_soft_source` with its layers stays. What goes is the acceptance: `_load_document` now raises `CheckerUnavailable` before it builds the document, on this chain without `readings@1` when no discourse admission is held. Its checks above that point remain, so a soft-source refusal keeps the soft relay's code and diagnostic, which the mode's error row cannot hold (rows `#unknown-predicate`, `#wrong-meaning-id`, `#status-contradiction` of F2.3). So few lines are deleted: the diff of load.py is +5. A `ve-document@2` document keeps Python's path.

## Parity corpus (F2.3)

`tests/data` holds one document listing both profiles (`rd9-docroute.ve.md`, with `readings@1`, still on the retained path). The corpus is that document, its form without `readings@1`, and constitution fixtures: 17 rows.

- 8 rows were saved on the real base, with its own service, and are unchanged: `uv run python docs/profile-composition/pc-2a/check_saved_rows.py` prints "first saved at aa033da3d: 9 rows; 8 remain, 8 unchanged; trimmed ['rd9-docroute#no-norm-content']; added 9".
- 9 rows, and the `--assume-no-exception` answers of every row, were saved through the retained path with Lean bypassed, because the base's build is gone. **They are not base runs.** The method first reproduced the saved rows byte for byte (`record_base.py`: "saved rows reproduced"). The DRI accepted this (rows45 item 6).

Every answer is equal except the `coverage` object's key order (DELTA row 2).

## Seeded bugs

docs/profile-composition/pc-2a/mutants.json holds all 12 with file and test; each was applied, shown failing and restored.
- Lean (7), in lean/VE/Service/Document.lean. The task's bug, `layeredOf` with `packs := []`: DocumentChainExamples.lean:106 (F2.1's exception case), also :98 and :132; the proof of `layeredOf_ids` breaks too, so the theorems were set aside to reach the guards. L7 fails only at a proof (`layeredOf_soft`).
- Python (5), in ve/document/load.py and ve/document/lean.py. The task's bug, the deleted acceptance restored: `test_a_document_lean_refuses_is_refused_on_every_path` and `test_the_retained_branch_accepts_nothing_of_this_chain` fail.
- Rust: not changed.

## Trust

`uv run python tools/trust_map.py --check`: K +0, S +0, trusted +145 (Document.lean +36, DocumentChainExamples.lean +109), within R16's 150. The allowance is recorded in docs/trust-baseline.json; the FOLLOW-UPS row is "## pc-2a". The first 109 are fixture helpers counted only because the merge train classifies new modules; I left tools/trust-classes.json alone, since changing it would have forced a full mutant run.

Trust mutants: MUTANT_LINE The first full run took 8.1 h on the loaded VM (74 survivors, 10 unknown); `DocumentChainChecks.lean` killed the real gaps, in a check-only module so that killed verdicts carried over. The allow file lists every remaining survivor by (definition, operator) with its reason: fixture helpers, `wireJson`'s fuel, a cut of a list of at most one element, one refusal's text (`decodedEnvironment`), and mutants that do not compile. **Allow entries are per operator, not per line**, so a reviewer should read the JSON's rows, and the fuel entries rest on an argument (depth limits) plus one deep-node test, not on a proof.

## Numbers

- Size: `git diff --numstat $(git merge-base HEAD main)`, excluding generated files, the saved answers and verbatim plan files: SIZE_LINE. **Over the ~600 line.** I measured it late, after the code and tests existed, then trimmed it from about 1,070; the checks module grew it back. All five deliverables are required, so nothing was moved to a later item.
- Speed: `VE_NATIVE_PREBUILT=1 uv run python docs/profile-composition/pc-2a/cpu.py`, least of 7, wall time: document mode 0.0063 s (F2.1) and 0.0076 s (rd9 without `readings@1`), retained loader 0.0111 s and 0.0086 s. Measured on a loaded VM, and the loader figures include its relays; no CPU row is claimed. Not run on UDHR or constitution pilots (L70).
- Pilot bytes (estimate only; nothing is claimed before a pilot audit): DeepMind at most 551 B UNFORMALISED to OPEN (s22-adjusted 482 B, fn11 69 B), a measured ceiling from the task.

## Observations, not changed

- `table3` answers SETTLED yes on a model that breaks an exception premise, since `situationX` reads no `X` (mode `norm-defaults-status`, unsafe true, excepted false). `SettledAs` does not read `X`. Pre-existing; this is why F2.1's exception case reads `filledX`.
- A list with `norm-defaults@0` last, otherwise sorted, is accepted on both paths: the profile is set aside before the order is read. Pre-existing.

## Not done

- Main was not merged: base `90807e7f7`. qt-a4, ap-3db and others touch Document.lean, so the merge train's rebase may need work there.
- SELECTED_LINE

## Spec re-read

- `requestOf`, `layeredOf`, `layeredOf_ids`, `layeredOf_entails` against docs/spec/profile-composition.md 3.2, by `tools/check_pc2a_statements.py`.
- The soft branch ("`layeredOf`, then `Wire.validateCompletions` on `L.U`") against 3.2, line 1607.
- The refusal text against section 4's row 4, line 3000.
- F2.1 to F2.4 against 5.2, lines 3099-3103, and the plan's lines 809-818. Spec F2.1 is the plan's "Point statuses" row.
- The rd-9 rows against 3.2's D9 paragraph, lines 1736-1738.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: PASS. `test_every_bound_field_mutant_is_unavailable[document-soft-defaults]`, `test_only_a_ve_error_escapes_a_malformed_node`, `test_only_a_ve_error_escapes_a_deep_node`.
2. Deliverables and rules: PASS with the stated limits. "Plan rows" above; F2.2 partly and F2.4 the harness's; size over the line.
3. Tests and gates can fail: PASS. mutants.json; trust-mutants.json; the allow file.
4. Python, Lean and Rust agree: PASS for Python and Lean, `test_f2_3_every_answer_equals_the_retained_loaders`; Rust N.A., not changed.
5. R8 binding: PASS. `test_another_requests_genuine_answer_is_unavailable[document-soft-defaults]`, and the bound-field fuzz.
6. Gate evidence: N.A. here: the chain gates the final HEAD. Main not merged ("Not done").
7. No unsigned item: PASS. `review-ready.py --delta-dri-needed`: DELTA_CHECK.
8. Every user-visible change in DELTA: PASS. F2.3's corpus and `test_a_document_lean_refuses_is_refused_on_every_path`.
9. Test selection finds the tests: PASS. `tools/select_tests.py --base $(git merge-base HEAD main)` selects tests/test_document_chain.py and tests/test_relay_binding_inventory.py; seeded P1 fails tests in tests/test_document_chain.py.
10. Lean statements say what is claimed: PASS. `tools/check_pc2a_statements.py`; seeded L1 and L7 break the proofs.
11. Budgets and limits fail closed: PASS. `test_a_limit_stays_unknown_on_this_chain`, `test_a_large_document_ends_within_the_layered_routes_own_limit`.
12. No CPU or memory regression: PASS on small documents only, `docs/profile-composition/pc-2a/cpu.py`; pilots not run (L70).
13. Removed tests carry a trailer: PASS. One parameter dropped within the branch, trailer on 30ae52a1f; `tools/gate_collection.py --check` left to the chain's gate.
14. Both directions, cited evidence, spec re-read: PASS. Each refusal test has its accepted twin (F2.1b, `test_the_retained_branch_keeps_every_other_chain`); "Spec re-read" above.
