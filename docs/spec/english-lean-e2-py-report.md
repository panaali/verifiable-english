# English Lean E2: Python preparation report

This worktree contains Python preparation for E2's admission relay. It does not flip
`english.admission`: the E2 Lean service, V6, overlay check, and required bounded
statement review have not landed. No Lean source or Rust source was changed. The
E2 spec gives Rust no implementation change in these Python work items.

## Completed

- `EnglishVocabulary` can defer its O1, O2, and O3 overlay raises while constructing
  the fallback lexicon for a future Lean admission call. Its default behavior still
  raises for all three; display-environment validation and suggested-entry consent
  still precede the selection.
- `parse_english_argument` includes the prover's status in its refusal text.
- The six new Python tests are pinned in `tools/gate-collection.json`.
- Three temporary bugs were tested and removed: restoring the O1 duplicate raise,
  restoring the O2 risk-wording raise, and restoring the O3 final-comparison raise.
  Each made its matching `test_overlay_refusals_can_be_deferred_for_lean_admission`
  case fail.
- `lake build` and `python lean/audit.py` passed. The first full pytest run had only
  the two collection-baseline failures caused by the new test IDs. Both gate tests
  and all six new tests passed after refreshing the baseline.

## Remaining E2 work

- E2.0 through E2.2: Lean service, boundary, V6, overlay check, and proofs.
- E2.3: Python admission and rendering relays, class/text transport, obligations,
  comparator, and the authority flip. The deferred producer option is not active on
  the admission path before Lean owns the refusals.
- E2.4: deletion ledger and relay lint.
- E2.5 and GE2: parity, reverse corpus, mutation replay, corpus A/B, latency, and
  signed delta dispositions. The bounded statement review was not run because this
  task prohibited model calls.

## Build checklist disposition

Numbers refer to `~/code/manage-agents/prompts/build-checklist.txt`. “Not done”
means the requirement is applicable to E2 but has not been established by this
Python preparation. “N/A” means this change does not touch that mechanism.

| Line | Status | Evidence or reason |
|---|---|---|
| 1 | Not done | E2's generated Lean diagnostic contract is still pending. |
| 2 | Not done | E2 three-way differential fuzz is a GE2 gate. |
| 3 | N/A | No text normalization changed. |
| 4 | Not done | E2 response validation and fuzz await the service response. |
| 5 | N/A | No JSON input decoder changed. |
| 6 | N/A | No verdict or budget operation changed. |
| 7 | N/A | No deadline handling changed. |
| 8 | N/A | No kind or owner fold changed. |
| 9 | Not done | E2 render/check corpus and constructor coverage remain. |
| 10 | Not done | The E2 single-admit relay is not implemented. |
| 11 | N/A | No parser for a programming language was added. |
| 12 | N/A | No state machine or ledger implementation changed. |
| 13 | Done | Three independently failing seeded bugs were removed. |
| 14 | Not done | The complete E2 gate's hermetic run remains to be established. |
| 15 | N/A | No identity preimage or certificate schema changed. |
| 16 | Done | The gate collection was regenerated with all six new IDs. |
| 17 | Not done | E2 statement diff and bounded review remain. |
| 18 | Not done | E2 Lean implementation fixtures and proofs remain. |
| 19 | N/A | No use-case formalisation changed. |
| 20 | Not done | E2 gate JSON and final evidence report remain. |
| 21 | Not done | E2 acceptance items have not been tagged AGENT/HUMAN/EXTERNAL. |
| 22 | Not done | Final clean-HEAD full gate and disk check remain after this report commit. |
