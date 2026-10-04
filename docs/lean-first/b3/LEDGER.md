# Lean-first batch 3: deletion ledger

Plan: `docs/LEAN-FIRST-PLAN.md` (draft 3), section 5.1 item 3 and section 5.2 row 3 (Readings S1: `readings_route.validate`
relays Lean's row; delete `readings_s1.py`, `rust_check`, `readings.rs` and the rights calls). Base `776a64d7`
(`lean-first/b0` with the DRI's signatures). Lean work: none, as the row says. Every deleted Python decision site
is mapped to the Lean check or answer that owns it; nothing was dropped without an owner.

## Deleted decision sites

All `ve/readings_s1.py` unless named; Lean files are under `lean/VE/Readings/`.

| # | Deleted (base) | Decided | Owner now |
|---|---|---|---|
| D1 | `ve/readings_route.py` `validate`: Python's answer computed and compared with Lean's row byte for byte, `CheckerUnavailable` on any difference | whether the route answers at all | Lean's row, relayed (`Run.lean` `runCase`, `validateResult`); the route checks only that the row is bound to the request (`_bound`) |
| D2 | `answer` (the whole regenerated row: `content_bearing`, per-candidate `pending`, `owned`, `shared`, the order of keys, per-pair facts, the 4.5 refusals `each other reading needs a distinguishing model id`, `distinguishing model id does not match model`, `invalid situation`, `violates a generated premise`, `does not separate readings`) | the answer of `readings-validate` | `Run.lean` `validateResult`, `candidateJson`, `setPairs` |
| D3 | `Side.document_hash` with `_canonical_raw`, `_canonical_unit`, `_canonical_norm` | each candidate's chain document hash | `Run.lean` `documentHash` (`oneJson`) |
| D4 | `ve/readings_route.py` `rights_findings`: two rights-route calls (`rights-scope`, `rights-elaborate`) per candidate, 352 per UDHR load | the chain findings `limitationScope`, `noDistinction` | `Run.lean` `chainFindings` (Python never had an implementation; it asked the rights route) |
| D5 | `S1Environment`: `UnsupportedProfile: profiles must be a sorted unique array`, `UnsupportedProfile: readings@1 is required` | the profile gate of the route | `Wire.lean` 56–57 (`decodeEnvironment`) |
| D6 | `Document`: `InvalidInput: unit kind is required`, `authored reading needs one signed choice`; `_candidate`: `UnsupportedProfile: readings@1 bar candidate content is not implemented`, `InvalidInput: reading <s>:<r> has kind … and content of kind …`, the W1 decode of a norm on the norms chain | decoding the document | `Wire.lean` 223–268 (`decodeReading`, `decodeDocument`) |
| D7 | `Admission._admission_text` and `_abstention`, `_reserved`, `_duplicate`, `_fixed_duplicate_text`, `_item_names`, `_interface`, `_attachment`, `Content.needs`, `Document.interface_of`, `Document.free` | the checks of 4.1 in order (abstention, `rd-`/`ve__` names, duplicates, interface, single attachment, `free D`) | `Wire.lean` 450–546 (`admitReadings` and its checks) |
| D8 | `Side.chain_text`, `line_order_text`, `has_rights`; `_elaborate`'s `UnsupportedProfile: rights content requires rights@0`, `InvalidInput: invalid norm fields`, `check_soft_source`, `InvalidInput: ill-typed assertion` | each candidate's chain well-formedness | `Wire.lean` 424–446 (`chainText`), `Lines.lean` `linesOnce`, `Doc.lean` `sideWF` |
| D9 | `Admission.decode_situation`, `_probe`, `situation_wf`, `tables_for`, `Side.tables_typed`, `probe_typed`, `key_sorts`, `generates`, `key_text`, `SITUATION_FIELDS`, `_typed` | 4.5 step 1: a situation's shape, id, ownership (`situation … decides …, which reading … does not own`), typing | `Wire.lean` 378–419 (`decodeSituation`), `Separate.lean` `situationWF` |
| D10 | `Admission.pair_facts` (and `ResourceLimit: decision assignments`) | `separated`, the witness's and the other side's completions | `Run.lean` `pairFacts`, `Separate.lean` `separates` (`separates_sound`) |
| D11 | `Admission.decision_only`, `act_only`, `set_findings`, `decision_only_text` | the findings of 4.6 | `Run.lean` `setFindings`, `Separate.lean` `decisionOnly`, `actOnly`; the English reads Lean's finding (`readings_route._finding_pairs`) |
| D12 | `ve/readings_route.py` `rust_check`, `Side.evaluation_case`; `rust/ve-core/src/readings.rs` and the `readings-evaluate` case of `rust/ve/src/main.rs` | none: an untrusted replay whose values had to agree with Python's | nothing replaces it: Lean's `separates` is the check (plan row 3) |

`decode_key` no longer raises a content diagnostic: a key that does not decode is a construction failure
(`ValueError`), which the English reports as `CheckerUnavailable` (`readings_route._built`, rule 2: Lean
validates, Python constructs).

No consumer of a deleted symbol remains: `git grep` over `ve/`, `tests/`, `tools/` and `conformance/` at the head
finds no use of `answer`, `Admission`, `rights_findings`, `rust_check`, `evaluation_case`, `pair_facts`,
`decode_situation`, `set_findings`, `decision_only` (outside `readings_english.decision_only_sentence`),
`chain_text`, `document_hash(` or `readings_evaluate_case`. `tools/relay_lint.py` now covers
`ve/readings_route.py` and passes.

## Retained, named (unfinished duplication)

What is left of `ve/readings_s1.py` (896 of 1,470 lines) builds the admitted document for the English and for the
search. Four pieces of it repeat Lean logic; they decide no admission, verdict or finding, and are listed here as
unfinished, not as exceptions:

| Site | Lean counterpart | Why it stays | Removed by |
|---|---|---|---|
| `Document.attached` (with `Content.declared`, `uses`) | `Doc.lean` `attached` | `document.py` `_s1_attached` needs, before the route runs, which fixed units the lower route must leave out; the English needs `one D s i` | a Lean answer field naming the attached units (batch 16a's document mode, or an earlier small Lean change) |
| `Side.keyed_rules`, `gen_keys` | `Separate.lean` `genKeys` | the English names the rule behind a decision key; the search enumerates keys | the readings English moving to Lean (track E3) and the search's evaluation (below) |
| `force_twins` (`node_value`, `line_value`, `_right_header`, `_twin_*`), `content_acts`, `_act_key` | `forceTwins`, `contentActs`, `actKey` | which wording a pair gets (E14 for twins) and the act phrase of E16; Lean's row carries the findings but not the twins or the acts | Lean emitting the twins and acts beside the findings, or track E3 |
| `Side.valid`, `observe`, `_formulas`, `selectable`, `model`, `Decoded.side_valid`, `side_value`, `cells`, `assignments` | `Separate.lean` `sideValid`, `sideValue`, `cells`, `assignments` | the search for situations (rule 3's generator) evaluates candidates in Python; Lean checks every situation it records (`readings-validate`, `readings-separate`) | the rule-3 decision of batch 15b and question 10 (this is a third generator-internal duplicate, beside `eval.rs` and the provers' replay; batch 2 should measure it too) |

The differential test of the last row is `tests/test_readings_s1_differential.py::test_generated_sets_lean_answers`
(every situation the search finds is accepted by Lean, on 1,000 generated documents) and the shadow test beside it.

## Lines

`git diff --numstat 776a64d7 HEAD`:

- **Python `ve/`: 752 lines deleted, 201 added (net −551).** `readings_s1.py` 1,470 → 896 (−650, +76: the module
  docstring, `Decoded`); `readings_route.py` 465 → 488 (−101, +124: the binding check `_bound` and the
  construction guard `_built` are new); `document.py` ±1. The plan's estimate (~1,530) assumed the whole of
  `readings_s1.py` goes; the retained construction above is why it does not yet.
- **Rust: 75 lines deleted** (`readings.rs` 70, `lib.rs` 2, `main.rs` 3), 0 added.
- **Lean: 0 lines** (none planned).
- Tests: `test_readings_route_relay.py` +189 (new); the Lean and differential tests drop their Python comparisons
  (−82, +72). Tools: `lean_first_diff.py` +78/−7 (the readings corpus, `checked_by` as wording),
  `readings_s1_pilot.py`, `relay_lint.py`, `check_rust_deps.py` small. Docs: `composition-s1.md` 8.4 and 10.
