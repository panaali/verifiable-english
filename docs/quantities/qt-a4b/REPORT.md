# qt-a4b REPORT

- Status: rows 1-3 delivered; rows 4-6 cut to qt-a4c at the size line (DRI 2026-11-08, reviews/dri-decisions-20261108-qt-a4b-bridge.md item 2). No DRI signature is outstanding.
- HEAD: the commit that adds this file, on feature/qt-a4b; base e9a6ec8d5 (the merge base with main).
- What changed: `ve document check` admits E2's chain list `[cardinality@0, norm-defaults@0, norms@0, readings@1, relational-fol@0]`, read as two projections with the counting units named as not certified; bridge leaves on a cardinality claim graph; open terms, reading sets and narrowings beside a counting unit.
- Open: qt-a4c (rows 4-6); qt-a4-pilot-list (`documents@1` beside the chain list, DRI 2026-11-05 item 5); et-4b's `events@0` (DRI 2026-11-05 item 6) lands with whichever of the two branches rebases second.
- Signatures: every DELTA row is signed (DRI 2026-11-05 items 1-4, DRI 2026-11-08 item 1, R2, R3, R16).

## Plan rows (task deliverables, in order)

| Row | Task text | Delivered | Commit | Tests |
|---|---|---|---|---|
| 1 | the gate fact as ruled, the decoder composing the three first-order profiles with cardinality's environment, a small part document listing the profiles with cardinality content admitted by `ve document check` (route case recorded), with its refusing side | yes, as the DRI ruled: the list is five members, with `relational-fol@0` (DRI 2026-11-05 item 1). The literal four-member list stays refused with `Missing profile relational-fol@0` | ee6a1fd24, 91b1f022f, f9778559b, 7347fa3e6 (route case `cardinality-chain-list`) | `tests/test_cardinality_lean.py::test_the_chain_list_is_admitted_and_each_content_kind_read_by_its_decoder`, `::test_the_gate_refuses_a_list_cardinality_does_not_compose_with` (10 cases), `::test_a_counting_unit_changes_neither_the_chain_s_premises_nor_its_verdict`, `::test_two_counting_units_that_contradict_are_named_not_certified`, `::test_render_says_what_the_chain_does_not_cover`; `tests/test_cardinality_answer.py::test_a_chain_list_row_is_bound_to_the_request`; `VE.Cardinality.gate_cardinality`, `VE.Cardinality.Wire.profileLists_projected`; guards in `lean/VE/Compose/Examples.lean` 673-700 |
| 2 | bridge leaves: labels on the graph's nodes (W6a's provenance rule's quoted half), a quoted leaf entering only through a bridge | yes (DRI 2026-11-08 item 1) | 9d2a9e3fc | `tests/test_cardinality_lean.py::test_a_quoted_unit_enters_only_through_a_bridge_naming_it`, `::test_a_deduction_is_no_bridge_and_the_report_id_covers_the_label`, `::test_the_cardinality_mode_has_no_units_so_it_refuses_a_label`; `tests/test_cardinality_answer.py::test_a_row_s_leaf_labels_are_bound_to_the_request_graph`; guards in `lean/VE/Service/CardinalityExamples.lean` 80-112 |
| 3 | `open_terms`, `reading_sets`, `narrowings` and `senses` beside `cardinality@0` | `open_terms`, `reading_sets` and `narrowings` under the chain list: accepted, and refused by name where the chain does not compose them. Under W6a's lists the three stay refused by name (`test_what_the_chain_does_not_compose_is_refused_by_name`). `senses` beside `cardinality@0` is not delivered: a document with `senses` is still read only by the senses route (`Service.Document.split`, unchanged). It goes to qt-a4c under the cut order of DRI 2026-11-05 item 5 | 7347fa3e6 | `tests/test_cardinality_lean.py::test_the_chain_reads_open_terms_reading_sets_and_narrowings_beside_a_counting_unit`, `::test_what_the_chain_does_not_compose_is_refused_by_name` |
| 4 | the premise set's status from Lean | not delivered: qt-a4c (DRI 2026-11-08 item 2; R9). `ve document check` still answers `premises: UNKNOWN` for a cardinality document (`tests/test_cardinality_lean.py::test_a_part_document_is_admitted_with_lean_s_report`, line 90) | | |
| 5 | a proved shape for the row's report | not delivered: qt-a4c (same ruling) | | |
| 6 | `tools/relay_mutation_gate.py`: a `cardinality` reader and a recorded `cardinality@0` document fixture | not delivered: qt-a4c (same ruling) | | |

Size: the hand-written files add 699 lines and delete 156 (`git diff --numstat $(git merge-base HEAD main)` over the files that `tools/regen_generated.py --owner` gives no generator, plus the hand pins in `ve/assurance-manifest.json` and `tools/trust-classes.json`), before this REPORT and DELTA. That is past the ~600 line, so rows 4-6 were cut, as DRI 2026-11-05 item 5 orders.

What the pilot's list still needs (DRI 2026-11-05 item 5): the translation pinned by tests/ce4.py lists `documents@1` with a claim graph over norm units, so a counting unit in the constitution's document needs `documents@1` beside the chain list, and a claim graph over mixed content (row qt-a4-pilot-list). This item does not claim the 29 units, and how many of them the chain list moves is unmeasured.

Pilot bytes: none claimed before a pilot audit. Estimate: up to the 29 counting units' bytes, once qt-a4-pilot-list lands and the next constitution pilot translates them.

Next item: qt-a4c (rows 4-6 and `senses`), then qt-a5 (row 2's bridge labels are in place).

## DRI conditions

- 2026-11-05 item 1: `gate_cardinality` restated (lean/statements.txt); the refusal test has the mixed list (`norms@0` with `order@0`), the chain list plus `documents@1`, `soft-norms@0` and `scope@0`; seeded bug L1 below; route case `cardinality-chain-list` appended, `cardinality-four-profiles` unchanged (`git diff main...HEAD -- tests/data/route-cases.jsonl` adds one line and deletes none).
- Item 2: `gate_judgments` and `gateOf_iff` keep their text (`git diff main...HEAD -- lean/statements.txt` changes only the `gate_cardinality` and `profileLists_projected` blocks and adds the new declarations); the list with `judgments@0` stays admitted (#guard at `lean/VE/Compose/Examples.lean:676-679`, and `listFault ("judgments@0" :: chainList) == none`); one projection, `projectedProfiles`, used by `projectW6` and `decodeEnvironment`; spec 4.1, 4.2 and 4.3 made true with a change-log line (docs/spec/quantities.md:746-750, 782, 784, 838-840).
- Item 3: two contradicting counting units are named, not certified (`test_two_counting_units_that_contradict_are_named_not_certified`); a counting unit changes neither the chain's premises nor its verdict (`test_a_counting_unit_changes_neither_the_chain_s_premises_nor_its_verdict`); each content kind is read by its decoder and the wrong kind is refused (`test_the_chain_list_is_admitted_and_each_content_kind_read_by_its_decoder`).
- Item 4: E2's one text pinned in `tests/test_cardinality_service.py`, `lean/VE/Cardinality/WireExamples.lean` and `lean/VE/Service/CardinalityExamples.lean`; a refusal by name wins over the list check (`[*CHAIN, "scope@0"]` and `[*CHAIN, "soft-norms@0"]` cases; #guard `Examples.lean:688`).
- Item 6 (`events@0`): not applicable on this branch. feature/et-4b is not on main (`git merge-base --is-ancestor feature/et-4b main` fails), so whichever branch rebases second adds it.
- 2026-11-08 item 1: the three named tests and the guards at `CardinalityExamples.lean` 80-110 are in the selection; the `bridgeAdmitted` mutants that drop the `quoted` test (L3) and the meaning-id test (L4) each fail a named guard.

## Seeded bugs (each planted alone, shown failing, restored)

| Id | Language | File | Bug | Fails |
|---|---|---|---|---|
| L1 | Lean | lean/VE/Cardinality/Wire.lean, lean/VE/Compose/Dispatch.lean | the gate admits a fifth profile: `chainProfiles ++ ["scope@0"]` added to `profileLists` and `scope@0` taken out of `cardinalityOthers` | proof `Dispatch.lean:1372` (`decide` refutes `"scope@0" ∈ cardinalityOthers`); with that step stubbed by `sorry`, the #guards `lean/VE/Compose/Examples.lean:688` and `:699` (`lake build VE.Compose.Examples`) |
| L2 | Lean | lean/VE/Service/Document.lean (`cardinalityReport`) | a node with no bridge label may be a quoted unit (`u.kind == .str "asserted"` dropped), so a quoted unit becomes a premise | #guard `lean/VE/Service/CardinalityExamples.lean:82` (`lake build VE.Service.CardinalityExamples`) |
| L3 | Lean | lean/VE/Service/Document.lean (`bridgeAdmitted`) | `k.quoted` dropped: a bridge may name an asserted unit | #guard `lean/VE/Service/CardinalityExamples.lean:99` |
| L4 | Lean | lean/VE/Service/Document.lean (`bridgeAdmitted`) | `m == n.adm.meaningId` dropped: a bridge may name a unit holding another statement | #guard `lean/VE/Service/CardinalityExamples.lean:99` |
| P1 | Python | ve/cardinality.py (`bind_document`) | the `leaf_labels` binding dropped | `tests/test_cardinality_answer.py::test_a_row_s_leaf_labels_are_bound_to_the_request_graph` |
| P2 | Python | ve/cardinality.py (`bind_composed`) | `not_certified` no longer bound to the request's counting units | `tests/test_cardinality_answer.py::test_a_chain_list_row_is_bound_to_the_request` (DID NOT RAISE CheckerUnavailable) |

Not planted: the task's "`premises` written by Python" belongs to row 4, which is cut (qt-a4c). No Rust code was changed.

Mutants per new trusted definition: `uv run python tools/trust_mutants.py` (on the Mac, `mac-pytest.sh --trustmut -- --max-mutants 1000`), docs/quantities/qt-a4b/trust-mutants.json: TRUST_RESULT. mutants.json lists the hand mutants above with their file and test.

## Trust

`uv run python tools/trust_map.py --check` on the final tree: PASS; K +0, S +1, V +115 (trusted +116) against e9a6ec8d5: `VE/Service/Document.lean` +87, `VE/Cardinality/Wire.lean` +14, `VE/Compose/Dispatch.lean` +8 (S +1, V +7), `ResponseShape/Schemas/Document.lean` +5, `VE/Compose/ProfilesMain.lean` +2. Allowed under R16 in docs/trust-baseline.json (commit 34d3afcfd); the ties pass is the FOLLOW-UPS.md row "## qt-a4b (2026-11-08)".

## Checks run

- `cd lean && lake build`: Build completed successfully (1311 jobs).
- `python3 lean/audit.py`: PASS, 780 source files, 8639 theorem declarations after `listFault_some`, only the allowed axioms.
- `uv run python tools/lean_statements.py`: removed 0, changed 0 (lean/declarations.txt current), rerun after `listFault_some` (8055 statements); `uv run python tools/regen_generated.py --write` then wrote the audit manifest (`lean/VE/Audit.lean`, `lean/axioms.txt`).
- `uv run python tools/regen_generated.py --check`: after the decoder pins and the trust allowance, the two remaining failures (`assurance-manifest`, `trust-tables`) were fixed by commits c268b93d8 and 34d3afcfd; `tests/test_assurance_manifest.py`: 139 passed.
- `uv run python tools/gate_collection.py --check --prebuilt`: 19 added, 4 refused. The 4 are parametrized ids of `test_the_gate_refuses_a_list_cardinality_does_not_compose_with` whose expected text changed (DELTA row 4); they get `Test-removed` trailers in the commit that adds this file.
- Selected tests (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, ve-mac-1, HEAD 34d3afcf plus this REPORT's drafts): 547 units, 3 failed (4 ids): `tests/test_cardinality_exercised.py` (2: `Wire.e2` used by no theorem), `tests/test_relay_binding_inventory.py::test_every_schema_field_is_classified[document-soft-defaults]` (`composed` unclassified), `tests/test_route_row_schemas.py::test_dropped_retyped_or_emptied_fields_are_rejected` (a dropped `composed` passes the schema). Fixed in 5c09b6f02 (the theorem `VE.Cardinality.listFault_some`; `composed` classified); the failed files then passed (`uv run pytest -q tests/test_cardinality_exercised.py tests/test_relay_binding_inventory.py::test_every_schema_field_is_classified tests/test_route_row_schemas.py::test_dropped_retyped_or_emptied_fields_are_rejected`: 18 passed).
- Not run: the full gate (the chain runs it on the final HEAD).

Spec re-read:
- the chain list and the two readings against docs/spec/quantities.md:745-750;
- E2's text against docs/spec/quantities.md:782 and `VE.Cardinality.Wire.e2`;
- E4's projection against docs/spec/quantities.md:784 and `Wire.projectedProfiles`;
- the bridge rule against `VE.Time.Document.LeafAdmitted` (`.bridge a u`: a quoted unit attributed to `a`, holding the node's formula);
- the five members and the refusals by name against reviews/dri-decisions-20261105-qt-a4b.md items 1, 2 and 4.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: PASS. `tests/test_route_row_schemas.py::test_dropped_retyped_or_emptied_fields_are_rejected`, `tests/test_relay_binding_inventory.py::test_every_schema_field_is_classified[document-soft-defaults]` (`composed` classified), `tests/test_cardinality_answer.py::test_a_chain_list_row_is_bound_to_the_request`.
2. Every deliverable built or moved by a ruling: PASS. The plan rows table above; rows 4-6 are cut by DRI 2026-11-08 item 2 and `senses` by the cut order of 2026-11-05 item 5. There is no Python copy of a Lean decision: `cardinality.is_chain_list` reads `CARDINALITY_CHAIN` from the generated `ve/profile_table.json` (`ve/profiles.py`).
3. Tests can fail: PASS. docs/quantities/qt-a4b/mutants.json (L1-L4, P1-P2, the theorem mutant) and trust-mutants.json.
4. Python and Lean agree: PASS. The route case `cardinality-chain-list`; `tests/test_cardinality_lean.py::test_the_chain_list_is_admitted_and_each_content_kind_read_by_its_decoder`. No Rust code changed.
5. R8 binding: PASS. `test_a_chain_list_row_is_bound_to_the_request` (empty, absent, duplicated and shifted names, a dropped or extra `composed`), `test_a_row_s_leaf_labels_are_bound_to_the_request_graph`.
6. Gate evidence on the final HEAD: N.A. The chain runs the full gate on the committed final HEAD.
7. No unsigned item: PASS. Every DELTA.md Ruling cell cites a DRI decision file or R2, R3 or R16.
8. Every user-visible change in DELTA: PASS. DELTA.md rows 1-8 (admission, statements, texts, fault order, `composed`, labels, `leaf_labels`) and row 9 (trust).
9. Selection finds the tests: PASS. The selected run (547 units) picked `tests/test_cardinality_exercised.py`, `tests/test_relay_binding_inventory.py` and `tests/test_route_row_schemas.py`, which failed on this branch's change and are fixed in 5c09b6f02.
10. Lean statements say what is claimed: PASS. `listFault_some` breaks when `listFault` answers `"BOGUS"` (mutants.json `list-fault-text`). `gate_cardinality` and `profileLists_projected` are restated as DRI 2026-11-05 items 1-2 sign.
11. Limits fail closed: PASS. `graphLabelled` counts the nodes before it reads a label (#guard `lean/VE/Service/CardinalityExamples.lean:110`); `tests/test_cardinality_lean.py::test_a_large_well_formed_graph_ends_within_its_limit`.
12. No CPU or memory regression: N.A. (not measured). Lists without `cardinality@0` take unchanged paths; the chain list is a new path, read once per projection; no pilot timing was run.
13. `Test-removed` trailers: PASS. The four changed parametrized ids carry trailers in the commit that adds this file; `tools/gate_collection.py --check --prebuilt` GATE_COLLECTION.
14. Both directions, cited evidence, spec re-read: PASS. Each refusal has its admitted side (the chain list admitted / refused lists; a bridge admitted / every other label refused; `composed` present / absent); the spec re-read list is above.
15. No overclaim: PASS. The REPORT does not claim the 29 units, and rows 4-6 and `senses` are marked not delivered. No silent cut: PASS, rows 4-6 confirmed by DRI 2026-11-08 item 2. Every new check can fail: PASS (mutants.json, with P1 and P2 past Lean). Limits charged before work: PASS (item 11).
