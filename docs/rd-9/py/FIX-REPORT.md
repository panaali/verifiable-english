# RD-9 Python branch handoff (2026-10-11)

## Delivered

- `ve/readings_english.py` accepts an optional, already rendered gap segment in E14 between the decision supposition and the two outcomes. With the default empty segment, the sentence is byte-identical to the base. The E14 parser gate accepts a sentence with one gap.
- `tests/test_rd9_gap_relay.py` covers the unchanged empty case, gap placement, source word and reading preservation, and the parser gate.
- No user-visible answer, verdict, field, diagnostic or limit changes on this HEAD. No standing-ruling signature is claimed for a future activation.
- No Lean or Rust source was changed. No model was called.

## Required integration still open

- SC-A's Lean `readings-validate` producer must add per-pair `gaps`. A temporary Python consumer of that required field was tested and removed: on this HEAD, `tests/test_readings_nd_document.py::test_fnd1_render_shows_the_situation_with_its_filled_gaps` fails because Lean's pair has no `gaps`. The existing test passes again after removal. The Python full-table `filled_gaps` computation remains until that producer lands; it is not presented as RD-9's final renderer.
- SC-4, SC-5 and SC-6's Lean route, verdict and layered rows are absent. The SC-8 document loader, relay and generator changes cannot be activated or checked against their source-bound fields yet. The current soft-completion refusal remains. SC-9 and SC-10/11 are not delivered here.
- The future gap-selection wording removes irrelevant gap sentences. R1 does not sign a loss of quoted information; that visible delta needs a DRI signature unless the DRI's item-specific SC-0 ruling signs it. The future soft-completion availability and `decided_units` field additions likewise need their item-specific signature or a standing ruling whose conditions and tests are met.

## Tests and seeded bugs

- `lake build`: PASS, 886 jobs. `python lean/audit.py`: PASS, 481 files and 5,252 declarations, standard axiom allowlist only.
- Focused `tests/test_rd9_gap_relay.py` and the existing F-ND1 render test: 4 passed after restoration. `tools/relay_lint.py`: PASS. `git diff --check`: PASS.
- The first selected run was interrupted after a long silent unit. A second run completed all 202 selected units with exit 0 for each, including the RD-9 tests and gate-integrity file. The selector then exited 1 while recording its test map under the read-only account cache; this is a cache-write failure, not a test failure.
- The full gate on `3a64383d` failed only three parametrizations of `test_interrupted_gate_cannot_record_pass`. They passed after the test harness also stubbed the unrelated Lake-output hash step, which needs a Lean binary absent from the gate's isolated home. The failed-test rerun reproduced the three failures before this fix; all three passed in an exact reproduction of the gate pytest environment afterward. A full gate on the fix commit remains due.
- Three temporary E14 mutants each failed a focused test and were removed: (1) omit the inserted gap; (2) use the default reading's value for outcome (1); (3) drop the quoted source word. The final focused tests passed after removal.
- The full release gate has not yet run on a final RD-9 Python implementation.

## Build checklist

The statuses below describe this committed preparatory slice. “Open” means it remains required for the requested complete RD-9 work.

| Line | Status | Evidence or reason |
|---|---|---|
| 1 | Not applicable | No diagnostic, limit or decoder table changed. |
| 2 | Not applicable | No Python/Lean/Rust decoding contract changed. |
| 3 | Not applicable | No normalizer or parser entry point changed. |
| 4 | Not applicable | No untrusted output is consumed by this slice. |
| 5 | Not applicable | No JSON input boundary changed. |
| 6 | Not applicable | No verdict operation changed. |
| 7 | Not applicable | No deadline or budget changed. |
| 8 | Not applicable | No kind or owner fold changed. |
| 9 | Done for this slice | The new E14 form passes `s1_gated` in `test_rd9_gap_relay.py`; full SC-8 rendering remains open. |
| 10 | Not applicable | No entry point changed. |
| 11 | Not applicable | No language syntax is parsed by a new heuristic. |
| 12 | Not applicable | No ledger or state machine changed. |
| 13 | Done | Three seeded E14 mutants each failed a focused test and were removed. |
| 14 | Done for this slice | The added tests use no clock, sleep, cache assumption or file write. |
| 15 | Not applicable | No identity field or certificate changed. |
| 16 | Done | `gate-collection.json` regenerated with `tools/regen_generated.py --write --only gate-collection`; three added IDs. |
| 17 | Not applicable | No Lean statement changed. |
| 18 | Not applicable | This is not a spec-stage theorem change. |
| 19 | Not applicable | No use-case translation changed. |
| 20 | Done for this slice | This report states tested facts and unrun work; it makes no coverage claim. |
| 21 | Open | SC-8/SC-9 acceptance items need AGENT/HUMAN/EXTERNAL tagging in their final evidence. |
| 22 | Open | All 202 selected test units passed, but selector cache recording failed in the read-only account home. A full gate on the fix commit remains due. Disk had 73 GB free before the first full gate. |
| 23 | Done for this slice | No active user-visible delta, so no standing ruling is claimed. Future deltas and signatures listed above. |

## Acceptance status

- AGENT: E14 gap-slot preparation and mutation checks done.
- AGENT: SC-A Python renderer, SC-8 loader/relay/generators and final gate open, dependent on the specified Lean output.
- HUMAN (DRI): signature for any visible delta not covered by a standing ruling, including gap selection if not already signed by the SC-0 item ruling; deferred to the DRI.
- EXTERNAL: none used; no model calls.
