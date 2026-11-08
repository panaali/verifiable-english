# CI-2 review fix

Status: F1 and F2 fixed and verified locally; no DRI signature reserved.
Code HEAD: `4785771af` (`feature/ci-2`); this report commit follows validation. Open: none.
Change: refusals reuse their original Lean translation outcome; comments state the delivered binding and entry point.

| Finding | Fix | Regression | Commit |
|---|---|---|---|
| F1 (B) | `translationOf` formats the existing outcome; `unreadOf` cannot start a second translation for a command condition or proof task. | `lean/VE/Commands/Read.lean` injected-outcome `#guard`; restoring the second translation made `lake build VE.Commands.Read` fail at line 150. `lean/VE/Commands/RunExamples.lean` formatter `#guard` checks the complete ordered refusal fields and wrapper agreement, after seven list truncation mutants survived the first sweep. | `ed1aca6ce`, `df1bfd43d` |
| F2 (A) | Schema and entry comments name only the delivered id/unit/wording binding and `english.command` caller. | `tests/test_commands_ci2_review.py::test_command_schema_and_entry_comments_name_only_delivered_bindings`; the supplied F2 probe failed before and passed after. | `b678a188d` |

Validation completed: `lake build` (1,279 jobs), `python3 lean/audit.py` (8,399 theorem declarations), `tools/regen_generated.py --check` (35 entries), `tools/trust_map.py --check` (K +0, S +0, V +147 under R16), and the F2 pytest regression plus the two assurance pin tests (3 passed). The trust mutant rescore records 10 killed, 0 survived, 0 unknown, with 3 carried kills and 7 rerun against the formatter guard. The source-identity lock advances `actions_version` 38 to 39 and the 12 affected senses hashes were recomputed from Lean answers; no verdict or diagnostic text changed. All 18 ask fixtures were regenerated and replayed against Lean. The first selected run covered 553 units; it found stale ask identities in five tests and a dotted-mode parser error in one test. Those six test cases passed after regeneration and the JSON prefix decoder fix (`6ced17a85`). The final selected run recorded 539 units and found one stale S3 comparator report: its 170 case identities still said version 38. The report was regenerated (`4785771af`), and `tests/test_english_lean_s3_compare.py::test_committed_report_counts_are_derived_from_individual_records` passed on rerun.

Pre-existing on main and untouched here: `tests/test_lean_service.py::test_the_sub_tick_deadline_tests_hold_on_a_fast_machine_and_need_the_response_check[checked]`, the `[response unchecked]` parameter of that test, and `tests/test_readings_defaults_rd8_report.py::test_review_fix_commit_chain_and_final_gate_target` (source: `/home/seyran/code/manage-agents/main-known-red.txt`). None failed in this selected run.
