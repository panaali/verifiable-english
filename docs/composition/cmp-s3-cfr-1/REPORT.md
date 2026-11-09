# cmp-s3-cfr-1: the right-clauses wire, the `clauses-elaborate` mode and the registration (cmp-s3b part 1)

Status: deliverables (1) to (5) built. 8.5's `decode_unstructured` and `elaborate_plain` are proved, with no `sorry`.
No DRI signature is reserved. Decisions read: reviews/dri-decisions-20261104-cmp-s3.md (Q1 A1, Q2),
dri-decisions-20261109-lp0801.md item 1, dri-decisions-20261109-l1-c-regrade-rights.md item 3,
dri-decisions-20261109-adv0838.md item 3, dri-decisions-20261109-adv0947.md item 1,
dri-decisions-20261031-spec-right-clauses.md item 2, and this item's own size rulings
(dri-decisions-20261109-cmp-s3-cfr-1-size.md item 1, plus the second question in "Size").

## Deliverables

| Task row | Delivered | Evidence |
|---|---|---|
| (1) Wire.lean (8.5): the decoder, `decode_unstructured`, `elaborate_plain` with the signed `hd` | yes. `decode_unstructured` is word for word; `elaborate_plain` has `(hd : PlainOnWire D)` after `hp` (Q1 A1) | lean/VE/RightClauses/Wire.lean; proofs in WireDecode.lean, WireName.lean, WireTheorems.lean |
| (2) the `clauses-elaborate` mode: input the document; output the plained document's canonical bytes and `clauseSlotLabelled` | yes: Registry, `runMode_clausesElaborate`, response shape, encoder theorem `runCaseReported_fits`, schema, deadline, relay-gate fixtures. `elided_bytes` is **not** emitted: no product code computes it yet (row cmp-s3a-cfr-3) | lean/VE/RightClauses/Run.lean; `tools/relay_mutation_gate.py --route service:clauses-elaborate`: 528 mutants, 0 failures |
| (3) `right-clauses@0` in the registered list, ve/profile_table.json regenerated | yes: `VE.Compose.environmentWrappers`. D29, D33, D41 and D52 keep their values (their rows are unchanged; tests/test_compose_dispatch.py) | ve/profile_table.json (+1 line) |
| (4) test_right_clauses_k1_service_identity | yes; it fails on main (no mode, no registration) | tests/test_right_clauses.py |
| (5) the profile-off regression as saved evidence (9.3) | yes | docs/composition/cmp-s3-cfr-1/profile-off.json, written by profile_off_evidence.py at the base commit 6db6ee16d; test_right_clauses_profile_off_regression |

Not delivered here (cmp-s3-cfr-1b): the relay, the Python differential, the remaining 9.1/9.2 fixtures, W1's budget
fixture and `clauseSlot_wellFormed`.

## The wire (readings made here; for the reviewer and cmp-s3-cfr-1b)

- **Document.** The rights route's array of units (rights 3.2). Spec 8.5 builds each entry's `unitSpan` "from its
  unit", but the rights wire has no unit span. So a unit under the profile may carry `span: [a, b]`, and
  `stripElided` drops it. A unit without one has `[0, 0)`, so a non-empty clause or elided span on it is refused
  (`ClauseSpan`). A malformed span is `InvalidInput: invalid unit span`, the one text section 7 does not list.
- **`total: null`.** The service's restricted JSON has no null; rights' `_wire` writes an optional null by omission.
  So a relation without `total` reads as `total: null`. An explicit null is read too, if one arrives.
- **Order (4.1 step 2, 7).** Units in document order. In each unit, every line object goes through `decodeLine` on
  the object without the three keys (this gives `<n>`), then `elided`, `clauses` (each clause in order) and
  `relation`; then rights' own `addUnit` runs on the unit without its span and keys. A line is therefore decoded
  twice, a constant factor.
- **What the proof changed in this item's code.** Members are rewritten with `Std.TreeMap.Raw.map` (`mapMember`)
  rather than `setObjVal!`, which keeps every other member and the tree's shape. `lineWith` rebuilds the `norm` and
  `liberty` objects, which the soft decoder reads through their member lists. A parsed object is its own
  rebuilding, so no answer moves: the K1 bytes and the 9.3 evidence are unchanged.
- **`NoClauseKeys`** quantifies over every `lines` member of every `right`/`right_lines` member of every unit. That
  is 8.5's "no line object has `clauses` or `relation`" for any JSON value, including one whose object tree holds a
  key twice.

## Seeded bugs (each planted alone, restored; test run on a build of the change)

| Bug | Language, file | Fails |
|---|---|---|
| The decoder accepts a structured line with two relations (an array, first taken) | Lean, lean/VE/RightClauses/Wire.lean `decodeRelation` | tests/test_right_clauses.py::test_right_clauses_k_fixtures_service (`two-relations`) |
| Registration dropped (`environmentWrappers := ["readings@1"]`) | Lean, lean/VE/Compose/Dispatch.lean | tests/test_right_clauses.py::test_right_clauses_k1_service_identity (the environment is refused: `UnsupportedProfile`); also the `environmentProfiles` #guard of lean/VE/Compose/Examples.lean at build |
| Plained bytes changed for an unstructured document (`elided` kept in the plained line) | Lean, lean/VE/RightClauses/Wire.lean `plainLineJson` | tests/test_right_clauses.py::test_right_clauses_k1_service_identity (the bytes assertion, line 111) |
| No model reduction for `right-clauses@0` | Python, ve/profiles.py `MODEL_REDUCTIONS` | tests/test_model_environment.py::test_every_registered_profile_has_one_model_reduction (and ::test_the_oracle_reaches_every_profile_and_display_field) |
| No deadline for `clauses-elaborate` | Python, ve/backends/lean_service.py `DEADLINES` | tests/test_lean_service.py::test_the_deadline_keys_are_the_handshakes_modes |
| DELTA's negative test: a profile-off rights record changes (a rights refusal text edited) | Lean, lean/VE/Rights/Run.lean (frozen; planted for this run only and restored) | tests/test_right_clauses.py::test_right_clauses_profile_off_regression (the saved-digest assertion, line 184) |

Each was planted alone by /tmp's seed script: plant, `lake build ve_service`, run the named test with the build
pinned in a temporary lock, restore, rebuild. The Python ones needed no build. mutants.json lists them. One mutant per new trusted definition: trust mutants, below.

## Trust (R16)

`tools/trust_map.py`, base 6db6ee16d against this branch: trusted 61459 → 61593, which is +134 (K +0, S +16,
untied [V] +118). Untied [V] is Wire.lean's clause, relation and elided readers (`decodeSpan`, `decodeRole`,
`hasKeys`, `decodeClause`, `decodeRelation`, `decodeElided`, `decodeClauses`, `decodeRelationOpt`, `unitSpanOf`,
`rebuild`, `mapDoc`, `unitsOf`), Run.lean (G[V]) and Dispatch's `environmentWrappers`, `withoutClauses` and
`environmentRows`. S is `NoClauseKeys`, `NoReadingSets` and `PlainOnWire`. Tied D[V]: `decodeClauseDoc`,
`elaborateJson`, `stripElided` and `stripProfile` to the 8.5 theorems; `plainLineJson`, `lineWith`, `headKeys`,
`mapUnit`, `headStep`, `headUnit`, `headLine`, `unitBody`, `dropKeys`, `bodyLines`, `mapMember`, `mapArr`,
`members`, `bodyRight` and `jsonLineName` to the forward lemmas that state them against `plainSource`, `CLine` or
`lineName`. Proof modules are P. FOLLOW-UPS row: "## cmp-s3-cfr-1".

## Size

Exempt proof lines, measured with `git diff --numstat` against the merge base: WireDecode.lean 324, WireName.lean
161 and WireTheorems.lean 912, which is 1,397. That is past the ~800 trigger of
dri-decisions-20261109-cmp-s3-cfr-1-size.md item 1. The DRI accepted them as delivered: exempt, with no cut and no
compaction (reviews/dri-decisions-20261109-cmp-s3-cfr-1-proofsize.md item 1).

Counted hand-written lines:
- Product, about 410: Wire.lean 230, Run.lean 37, the response shape and encoder 50, Dispatch 21, Standalone 15,
  Registry/Protocol/RegistryExamples 17, Compose/Examples 4, VE.lean 5, Python 5.
- Tests, evidence and side tables: tests/test_right_clauses.py 202, other test and corpus edits 28, relay-gate rows
  and allow-list 23, the evidence script 20, tools/trust-classes.json 168.
- Docs: RIGHT-CLAUSES.md 23, this REPORT and DELTA.md.

Generated, not counted: statements.txt, predicates.txt, declarations.txt, Audit, the schemas, profile_table.json, the
binding answers and profile-off.json (the evidence script's output).

## Not changed

Rights/*, SoftNorms/*, Norms/*, Route/* and Plain.lean are untouched. No import of `VE.Readings`: the transitive
imports of Run.lean and the proof modules hold no `VE.Readings.*` or `VE.Scope.*` module. `route-cases.jsonl` has no
rows for the mode: it holds the case-kind route modes (`ROUTE_MODES`), and `clauses-elaborate` has no kinds, like
`words` and `english.command`. Its fixtures are tests/test_right_clauses.py and the relay-gate rows.

## Pilot bytes

None are expected from this item: no relay sends a document to the mode yet (cmp-s3-cfr-1b), and with the profile
off nothing changes. The UDHR figure of spec 9.3 is cmp-s3-cfr-1b's estimate.

## Next items

cmp-s3-cfr-1b (relay, differential, fixtures, W1, `clauseSlot_wellFormed`) and cmp-s3a-cfr-3 (`elided_bytes`).
