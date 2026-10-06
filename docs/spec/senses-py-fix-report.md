# Senses Python slice: implementation and verification

This report covers the non-Lean slice requested from [senses.md](senses.md) and
[senses-PLAN.md](senses-PLAN.md). The spec assigns sense parsing, selection,
projection, identity and diagnostics to Lean. It explicitly keeps the projected
environment on `relational-fol@0`, so there is no new Python profile. Neither
spec assigns a senses implementation to Rust.

## Acceptance and ownership

| Item | Class | Status and owner |
|---|---|---|
| B2 fixture pack and English wordings | AGENT | Done: `ve/senses/packs/fixtures@1.json`; the test pins the senses, glosses, wordings, letters and declared negative. |
| B2 byte transport | AGENT | Done: `load_pack` and `bundled_pack` preserve bytes for the Lean decoder. |
| B2 review provenance | AGENT | Done: the fixture starts unpinned; `review_status` accepts only a matching Lean-supplied dictionary identity and complete review record. |
| B2 Lean decoder, dictionary identity, and CLI diagnostics | EXTERNAL | Deferred to the Lean senses owner; excluded from this Python work. The B2 end-to-end gate therefore remains open. |
| B6/B7 senses service, relay, rendering and reading-set display | EXTERNAL | Deferred to the Lean senses service owner, then the Python integration owner. There is no service contract to relay yet. |
| B8 starter pack wording review and pins | HUMAN | Deferred to the pack reviewers. No pack is represented as reviewed here. |
| B8 use-case measurement and B10 report claims | EXTERNAL | Deferred until the Lean reader and service exist; owner: senses integration. |
| Rust senses implementation | EXTERNAL | Not applicable: neither senses specification assigns one. |

## Seeded bug checks

Each mutant was applied to changed code, run against its focused test, and
restored. Each run exited 1 with a failed test. The unmutated focused suite
passes.

| Mutant | Test that failed |
|---|---|
| `load_pack` returns empty bytes | `test_loader_preserves_untrusted_bytes_for_lean` |
| `review_status` ignores `dictionary_id` | `test_review_requires_matching_identity_and_complete_record` |
| The first `funny` wording becomes `{0} was funny` | `test_fixture_pack_matches_spec_wordings` |

## Build checklist applicability

The numbered items refer to `manage-agents/prompts/build-checklist.txt`.

| Line | Status | Evidence or reason |
|---|---|---|
| 1 | Not applicable | No diagnostic, limit or decoding contract is implemented in Python; Lean owns it. |
| 2 | Not applicable | No Py/Lean/Rust senses decision paths exist to compare. |
| 3 | Not applicable | No senses text normalizer or parser is added. |
| 4 | Not applicable | No Lean/Rust response or ledger is consumed by this slice; review pins fail closed. |
| 5 | Done | Malformed pack bytes pass unchanged to the future Lean decoder; invalid bundled names raise `VEError`. |
| 6 | Not applicable | No verdict operation is added. |
| 7 | Not applicable | No public bounded checker operation is added. |
| 8 | Not applicable | No kind or owner fold is added. |
| 9 | Not applicable | No English renderer or parser is added; fixture wordings are pinned as data. |
| 10 | Not applicable | No new admission entry point is added. |
| 11 | Done | The loader never parses a real language with a regex; JSON interpretation is left to Lean. |
| 12 | Not applicable | No state machine or ledger is added. |
| 13 | Done | Three seeded mutants each failed a focused test and were restored. |
| 14 | Done for this slice | Focused tests write only under `tmp_path`; bundled data is read-only. The full gate controls its own environment. |
| 15 | Done for this slice | Review status requires the exact Lean-supplied `dictionary_id`; the loader does not compute identities. |
| 16 | Done for this slice | `test_fixture_pack_matches_spec_wordings` enumerates every fixture sense and sort. |
| 17 | Done | No theorem statement changed; `tools/lean_statements.py --check` reports no additions, removals or changes. |
| 18 | Not applicable | Lean theorem stubs are outside the requested scope. |
| 19 | Not applicable | No use-case rule is formalized in this slice. |
| 20 | Not applicable | No measured semantic or three-way claim is made. |
| 21 | Done | The acceptance table tags every scoped item AGENT, HUMAN or EXTERNAL and names deferred owners. |
| 22 | Pending final gate | This non-empty report and the test collection are committed before the gate runs on clean HEAD. Its result is reported at handoff. |

## Verification

- `PATH=/home/seyran/.elan/bin:$PATH lake build` in `lean/`: passed.
- `PATH=/home/seyran/.elan/bin:$PATH python3 lean/audit.py`: passed; only the declared standard axiom allowlist.
- `PATH=/home/seyran/.elan/bin:$PATH python3 tools/lean_statements.py --check`: passed; no statement, predicate or declaration changes.
- Focused tests: `tests/test_senses_pack.py::test_fixture_pack_matches_spec_wordings`, `test_loader_preserves_untrusted_bytes_for_lean`, `test_generic_canonicalization_is_stable_without_pack_schema`, `test_fixture_pack_is_unreviewed`, `test_review_requires_matching_identity_and_complete_record`, and all `test_bundled_pack_rejects_path_escape` cases passed.
- Full offline gate: pending on clean HEAD after this report is committed.
