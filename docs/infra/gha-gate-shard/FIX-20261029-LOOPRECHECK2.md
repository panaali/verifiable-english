# gha-gate-shard fix round, 2026-10-29

Status: F11 (B) fixed; F3 (C) class cases closed.
HEAD: code and core tests committed as `53895fbb2`; extra regressions as `839488568`.
Changed: shard merging now requires complete deselection, toolchain and retry identities.
Open items: none in the local merge validator. No DRI signature or DELTA row is needed.

## Findings

| Finding | Fix | Regression test ID | Commit |
|---|---|---|---|
| F11 (B) | Require deselected IDs to equal the plan's unselected complement on shard 1, and be empty on all other shards | `test_merge_refuses_selected_id_reported_as_deselected` | `53895fbb2` |
| F3 (C) | Reject null or malformed toolchain fields, an invalid quarantine day, overlapping active and expired lists, and retries expired on the recorded day | `test_merge_refuses_absent_identity_even_when_all_shards_agree`, `test_merge_refuses_shared_malformed_toolchain_identity`, `test_merge_refuses_toolchain_paths_without_a_version`, `test_merge_refuses_incomplete_retry_metadata`, `test_merge_refuses_retry_expired_on_recorded_day`, `test_merge_refuses_invalid_quarantine_day_or_active_expired_overlap`, `test_merge_refuses_retry_of_skipped_test` | `53895fbb2`, `839488568` |
| F5 (prior B) | Existing disabled or inactive retry refusal remains in force | `test_merge_refuses_retry_without_enabled_active_quarantine` | `e1f894f2b` |

The F11 executable probe failed before the code change and passed after it. Direct F3 probes for a null shared toolchain and an expired retry passed before the change and returned failed merge records afterward. The historical F5 probe passed after the change. The positive cases `test_merged_counts_and_collection_match_unsharded_fixture`, `test_merge_accepts_retry_of_active_quarantine_test`, `test_merge_accepts_retry_expiring_on_recorded_day`, and `test_gate_runs_full_collection_and_only_its_share` remain green. The F11 test exercises both a deselected ID from shard 1's share and one from a different shard.

## Bounded hunts

1. Tried absent identities, null and malformed toolchain values, collection mismatches, duplicate or missing shard numbers, and wrong ran IDs. Found the shared null toolchain form of F3 and fixed it. The other forms were already refused. The new toolchain test covers null, empty, wrong type and malformed path data.
2. Tried a selected ID reported as deselected, retry expiry before the recorded day, invalid day, active and expired overlap, a failed retry and a prohibited skip. Found F11 and the expiry/day forms of F3; fixed them. The other forms were already refused. Eleven additional bounded mutations returned failed records after the fix.

No form remains open from these hunts. The hunts ran locally; the runtime's agent delegation rule did not permit the subagent requested by the acting-DRI note.

## Validation

- Four seeded Python mutations disabled the deselection-set comparison, toolchain value check, retry-expiry check and skipped-test retry check in turn. Each made its named regression fail; each mutation was restored.
- Focused `tests/test_gate_shards.py`: 78 passed.
- `lake build`: passed, 1,135 jobs. `python3 lean/audit.py`: passed, 653 source files and 7,286 theorem declarations.
- Selected test plan: 102/102 mapped units passed, zero failures. The Mac runner's two test slots stayed occupied through two waits; the final run used the VM fallback with `UV_CACHE_DIR`, `XDG_CACHE_HOME`, `VE_LEAN_BUILDS` and `VE_TESTMAP_CACHE` under `/tmp` because home cache directories were read-only in this sandbox. The successful selected run finished with exit 0 and recorded tree `43b343f8a7`.
- The three tests in `main-known-red.txt` are pre-existing on main and were not edited or fixed here. The real Actions/R18 comparison remains an external item for the train owner.

No VE language, wire, Lean, Rust, verdict or trust-budget behavior changed. There are no DELTA rows or Ruling cells for this gate-only correction.
