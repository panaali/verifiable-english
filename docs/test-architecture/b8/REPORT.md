# Test architecture batch 8: hermetic history tests

Batch 8 of `test-architecture-2026-10-14.md` section 4. Work started from `9f40783b` and was synced with main through `4ce477e18`. The changes stay within the row's five targets: the B11b and RD8 report checks, private Git fixture for the pre-commit hook tests, fixed pilot inputs for B16d, and the eager oracle import in `ve/norm_defaults_contract.py`.

## Delivery and checks

| Plan item | Commit | Delivery | Check |
|---|---|---|---|
| B11b saved evidence | `20a448129` | `production-numstat.json` saves the four source line counts; `report.py` renders from it. The historical DELTA now describes that source. | `test_batch_report_metrics_match_evidence`; `python3 docs/lean-first/b11b/report.py` |
| RD8 saved evidence | `20a448129` | The report commit's full hash is saved; the test checks that immutable object's ancestry without asking today's HEAD for the old branch's commit chain. | `test_review_fix_commit_chain_and_final_gate_target` |
| Pre-commit fixture repo | `5fd5fe93e`, `438df90b3` | A module fixture commits the source snapshot under `tmp_path_factory`; each probe uses a separate private index and object directory against that fixed HEAD. | `test_staging_history_is_private`; the full `test_precommit_hook.py` file |
| B16d pilot fixture repo | `5fd5fe93e`, `9284d2485` | The two original pilot blobs are committed under `tests/data/tarch-b8`, with SHA-256 checks. A private repository with two `pilot/*` branches feeds them through the original `pilot_documents` path. | `test_private_pilot_fixture_enumerates_saved_branches`, `test_coupled_pilot_reading_plan_matches_prior_path`, `test_labeled_pending_pilot_is_lean_decided` |
| Product import | `5fd5fe93e` | Loading `ve.norm_defaults_contract` no longer loads the Git-backed frozen oracle. Contract probes load it only when they use it. | `test_product_contract_import_does_not_load_git_oracle`; `test_norm_defaults_contract.py` |
| Import under the external harness | `cc599a6ff` | Both changed test modules import the hang guard as `tests.subprocesses`, so they also load outside pytest's path setup. | `test_test_modules_other_code_imports_load_outside_pytest` |
| Pilot corpus boundary | `20c65b006`, `fcb630f9d` | The saved bytes use `.ve.txt` fixture names and stay outside the global `.ve.md` seed scan; a direct integration test guards that boundary. | `test_saved_pilots_are_not_global_document_seeds`; `test_every_seed_document_agrees_with_python_or_fails_closed` |

The batch 8 code and evidence checks are AGENT items. The final-HEAD full release gate is EXTERNAL to this build, deferred to the chain after handoff; no HUMAN item remains.

The nightly full, live, no-reuse run is unchanged. B11b line counts, the exact RD8 historical chain and saved gate fields, hook decisions, and B16d Lean comparisons still have failing assertions. The RD8 test now names one content-addressed report commit instead of looking it up through today's moving HEAD. Current batch scope and evidence belong to the chain's batch gate and merge train under D4/R11; this report adds no permanent test of this batch's moving HEAD.

## Measured effect

The Mac baseline for the four existing files was **77 passed, 27.72 s pytest wall**, on `9f40783b`; first-run Lean setup was 407 s and end-to-end wall was 460.78 s. An intermediate edited run was **78 passed, 26.80 s pytest wall**. On the final code, the same four files were **80 passed, 27.61 s pytest wall** on ve-mac-1: three added tests and an observed **0.11 s (0.4%) faster** wall than the baseline. The final cached Lean setup was 2 s and the wrapper's end-to-end wall was 39 s. These are single runs; the pytest walls exclude setup and slot waits and show no material runtime change.

The plan counted 11 non-hermetic units. The four units changed here stop depending on moving HEAD or pilot refs, leaving 7 by the plan's section 2.5 inventory: `test_ar8_evidence`, `test_identity_lint`, and the five repository-listing units. The plan's “~5” was an estimate; those other units are outside batch 8. The frozen norm-defaults oracle remains available to explicit differential tests, but a product-module import no longer triggers its Git read.

## Seeded bugs

Each temporary fault was planted in a changed file, ran against its named test, and was removed. The first five ran together on ve-mac-1: **4 failed, 1 error**. The two stronger behavior probes ran together on the VM: **2 failed**. The import, corpus, and pilot-ref faults M8–M10 ran separately on the VM and each failed. The files were restored from byte-for-byte backups and `git status --short` showed only this report.

| Bug | File | Fault | Test that failed |
|---|---|---|---|
| M1 | `docs/lean-first/b11b/report.py` | Swapped added and deleted line-count columns. | `test_batch_report_metrics_match_evidence` |
| M2 | `docs/readings-defaults/rd8/evidence.json` | Pointed the pinned report commit at an earlier review commit; the saved chain length was wrong. | `test_review_fix_commit_chain_and_final_gate_target` |
| M3 | `ve/norm_defaults_contract.py` | Restored an eager import of the Git-backed oracle. | `test_product_contract_import_does_not_load_git_oracle` |
| M4 | `tests/test_precommit_hook.py` | Switched staging back to the live worktree after its private index was set up. | `test_staging_history_is_private` |
| M5 | `tests/test_b16d_document.py` | Replaced the prior-path reading plan with a planted value. | `test_coupled_pilot_reading_plan_matches_prior_path` |
| M6 | `tests/test_precommit_hook.py` | Switched staging to the live worktree before setting up the index. | `test_staging_history_is_private` (setup error) |
| M7 | `tests/test_b16d_document.py` | Selected the other saved pilot blob. | `test_coupled_pilot_reading_plan_matches_prior_path` (digest assertion) |
| M8 | `tests/test_norm_defaults_contract.py` | Restored the bare hang-guard import after its fix. | `test_test_modules_other_code_imports_load_outside_pytest` |
| M9 | `tests/data/tarch-b8/nd-op.ve.txt` | Restored the `.ve.md` extension, adding the pilot to the global seed scan. | `test_saved_pilots_are_not_global_document_seeds` |
| M10 | `tests/test_b16d_document.py` | Put one fixture branch under `other/nd` so `pilot_documents` skipped it. | `test_private_pilot_fixture_enumerates_saved_branches` |

## Execution and limits

The comparable focused runs and the selected run use `mac-pytest.sh`; the two stronger mutant checks and their clean rerun used the VM. The first VM `lake build` hit a clang frontend crash on the generated `VE.Readings.Run:c.o`; a single-target retry passed, followed by a complete **888/888** `lake build` pass. `python3 tools/rust_build.py` passed and reported a binary pinned in `lean/checkers.lock`. The builder did not run `tools/gate.py`, as the task assigns that full gate to the chain on the final committed HEAD. Of the three entries in `main-known-red.txt`, the two sub-tick tests were fixed on main before this branch's final sync. RD8 is an explicit batch 8 target and is fixed here; no unrelated known-red test was edited.

The first selected plan chose 374/374 units because the cached map at `f98183bf` marked all 374 uncertain after 87 changed files. The first Mac snapshot found two integration failures: `test_test_modules_other_code_imports_load_outside_pytest` could not import the new bare hang-guard imports outside pytest, and `test_every_seed_document_agrees_with_python_or_fails_closed` saw two unintended pilot seeds. Commits `cc599a6ff`, `20c65b006`, and `fcb630f9d` fix and guard these cases. The failed tests and affected focused tests passed locally afterward. After syncing main's `ts-B2` selector changes, the corrected plan chose 375/375 units because there is no compatible coverage map yet. This is existing map availability, not an unlayered new directory. A second Mac run reached passing build, audit, Rust, and affected tests; it was stopped during the diff review when the plan's private pilot-repo requirement showed that `pilot_documents` needed to remain under test. Commit `9284d2485` restores that path. The final selected Mac run passed **375/375 units**, plus its Lean build, audit, Rust, and layer checks, with **zero failures**; wrapper wall was **2,249 s**. No full `tools/gate.py` run was made by the builder.

## Self-review against BUILDER-CHECKLIST

1. N.A. No Lean response or request decoder changes.
2. PASS — `git diff main...HEAD` review and the delivery table above cover each batch 8 row; `test_private_pilot_fixture_enumerates_saved_branches` checks the fixture-repo requirement.
3. PASS — `test_batch_report_metrics_match_evidence`, `test_review_fix_commit_chain_and_final_gate_target`, `test_product_contract_import_does_not_load_git_oracle`, `test_staging_history_is_private`, `test_coupled_pilot_reading_plan_matches_prior_path`, `test_test_modules_other_code_imports_load_outside_pytest`, `test_saved_pilots_are_not_global_document_seeds`, and `test_private_pilot_fixture_enumerates_saved_branches` failed under M1–M5 and M8–M10.
4. N.A. No Python, Lean, or Rust verdict implementation changes.
5. N.A. No relayed answer or request binding changes.
6. N.A. The user assigned the final-HEAD full gate to the chain; `git status --short` verifies the committed handoff.
7. PASS — `DELTA.md` records no user-visible change; `test_examples_are_clean_and_accepted` and `test_every_catalogue_fault_alone_gives_its_expected_record_in_python` check outcomes.
8. PASS — `DELTA.md`, `test_examples_are_clean_and_accepted`, and `test_every_catalogue_fault_alone_gives_its_expected_record_in_python` check unchanged public results.
9. PASS — `tools/select_tests.py --base $(git merge-base HEAD main) --json` and the selected Mac runs identify the stale then missing coverage map and select `test_test_modules_other_code_imports_load_outside_pytest` and `test_every_seed_document_agrees_with_python_or_fails_closed`.
10. N.A. No Lean statements, shapes, or proofs change.
11. N.A. No public budget, limit, or deadline logic changes.
12. PASS — before/after Mac wall measurements cover `test_b11b_report.py`, `test_readings_defaults_rd8_report.py`, `test_precommit_hook.py`, and `test_b16d_document.py`; no product algorithm changes.
