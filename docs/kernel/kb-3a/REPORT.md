# kb-3a: the premise slot of the soft route on the wire (build report)

Status: built, every deliverable of the task and the acceptance addendum (T1 to T6); no DRI signature is needed (DELTA rows cite R8, R8, R16, R12).
Code: `ve-kb-3a` branch `feature/kb-3a`, final code at the merge of main `c9214a2608` (`346a885f9a`). After it come the records and one docs fix (`9ef8642183`, three rows of kernel-boundary.md).
What changed: `soft-norms` answers two new kinds, `slot-certificate` and `slot-conflict` (with or without `witness`). Each takes a list of base-vocabulary facts P and is proved sound for any P (`VE.Compose.SlotWire`). With P empty it is its soft twin (`slot_wire_empty`).
Open: one FOLLOW-UPS row, the R16 ties pass (`FOLLOW-UPS.md`). Not run by me: the full gate (the chain runs it on the final HEAD).
SIZE: 845 product, 776 tests, 549 other hand-written lines (`git diff --numstat main`: docs, records, registry and trust tables; generated files and the trust-mutants record excluded).

## Deliverables

| Task line | Where | Evidence |
|---|---|---|
| (1) `decodeFacts` over `envAt (soften src.D) 0`, raw items kept | `lean/VE/Compose/SlotWire.lean` (`b1d5068af4`) | `decodeFacts_ok` (well-formed over the base vocabulary, one formula per item, the request's own items); seeds T1, T3, T4 |
| (2) `replaySlotConflict`, `replaySlotWitness`, `replaySlotEntailment` | same | `slot_wire_empty`; seeds i, ii |
| (3) `slot_wire_conflict_sound`, `slot_wire_conflict_witness_sound`, `slot_wire_acceptance`, `slot_wire_empty` | same | `lake build` exit 0; `python3 lean/audit.py` PASS (876 files, 9990 theorems, standard axioms only) |
| (4) kinds `slot-certificate`, `slot-conflict` in `runSoftKind`; runCase theorems | `lean/VE/SoftNorms/Run.lean`, `lean/VE/SoftNorms/SlotSound.lean` (`998a6c01c7`) | `VE.SoftNorms.Run.slot_wire_certificate`, `slot_wire_conflict`; the `#guard`s of `lean/VE/SoftNorms/SlotExamples.lean` |
| (5) registry, closure baseline, ALLOWANCES | `tools/kernel-paths.json`, `docs/kernel/closure-baseline.json`, `docs/kernel/ALLOWANCES.md` (`511d869e78`, `fef61cd7b2`) | `uv run python tools/kernel_closure.py --check docs/kernel/closure-baseline.json --allowances docs/kernel/ALLOWANCES.md`: `PASS: kernel 9947 <= 9947` (+395, under the +400 stop line) |
| Python `facts=` on the two calls, schema `facts` typed and bound | `ve/soft_route.py` (`check_soft_conflict`, new `check_soft_certificate`, `bind_facts`, `bind_certificate`); `soft-norms.json` `slot_*` shapes | the claims below; `tests/test_relay_binding_inventory.py` routes `slot-certificate`, `slot-conflict`, `slot-conflict-witness` |
| Fixtures (a) to (d), T1 to T6 | `tests/test_slot_premises.py`, `lean/VE/SoftNorms/SlotExamples.lean`, `lean/ResponseShape/SlotExamples.lean` | the claims below |

The two new kinds return exactly the fields of `soft-certificate` and `soft-conflict` plus `facts`. No existing kind is touched: `slot_wire_empty` proves the slot replays equal the soft ones when `facts` is absent or `[]`, and Run.lean's soft branches are unchanged in the diff.

## Claims and their runs

Each row's verdict is the exact string its test asserts (`test_slot_report_claims_have_runs` checks this table).

| Fixture (a), `slot-conflict` with `facts: []`: the target has no certificate | `UNKNOWN` | `tests/test_slot_premises.py::test_fixture_a_is_conflict_free_only_with_the_fact` |
|---|---|---|
| Fixture (a), `slot-conflict` with the fact and its model | `CONFLICT-FREE` | `tests/test_slot_premises.py::test_fixture_a_is_conflict_free_only_with_the_fact` |
| Fixture (a), the excluded witness with `facts: []` | `CONFLICT` | `tests/test_slot_premises.py::test_fixture_a_a_witness_in_the_excluded_situation_is_refused` |
| Fixture (a), the excluded witness with the fact | `InvalidModel(facts): the model violates a fact` | `tests/test_slot_premises.py::test_fixture_a_a_witness_in_the_excluded_situation_is_refused` |
| `slot-certificate` of a claim that follows from the fact, relayed | `"valid": True` | `tests/test_slot_premises.py::test_a_slot_certificate_with_its_fact_is_valid` |
| (b) `slot-certificate` with `facts: []` on every recorded `soft-certificate` fixture | `{**soft, "facts": 0}` | `tests/test_slot_premises.py::test_slot_certificate_with_no_facts_is_soft_certificate_on_every_fixture` |
| A slot case without `facts` | `InvalidInput: a slot case needs a facts array` | `tests/test_slot_premises.py::test_slot_certificate_with_no_facts_is_soft_certificate_on_every_fixture` |
| Before: main refused every `slot-*` kind; a kind beside the two new ones still is | `UnsupportedProfile: case kind slot-bogus is not available on the soft-norms route` | `tests/test_slot_premises.py::test_an_unknown_slot_kind_is_refused_as_before` |
| (c), T1: a fact naming a regulated predicate, its permission or a layer symbol, on all three forms | `ill-typed or unbound formula` | `tests/test_slot_premises.py::test_slot_fact_cannot_discharge_rule` |
| T1: a fact naming a soft decision predicate | `soft__excepted__d is a soft decision predicate` | `tests/test_slot_premises.py::test_slot_fact_cannot_name_a_soft_decision_predicate` |
| T2: facts dropped, added or reordered against the certificate | `certificate is stale or bound to different inputs` | `tests/test_slot_premises.py::test_slot_binding_from_request_not_answer` |
| T2: an answer's `facts` not the number sent | `facts count is not the number of facts sent` | `tests/test_slot_premises.py::test_slot_binding_from_request_not_answer` |
| T3: `facts` not an array | `InvalidInput: facts must be an array` | `tests/test_slot_premises.py::test_slot_every_fact_item_decoded` |
| T4: a made-up constant or predicate, a wrong sort or arity | `ill-typed or unbound formula` | `tests/test_slot_premises.py::test_slot_fact_unknown_target_refused` |
| T5: facts [p(a), not p(a)] with a model | `InvalidModel(facts): the model violates a fact` | `tests/test_slot_premises.py::test_slot_inconsistent_facts_refused` |
| T5: non-empty facts with no model | `InvalidInput: facts need a facts_model: a base model of the background and the facts` | `tests/test_slot_premises.py::test_slot_inconsistent_facts_refused` |
| (d) `facts` retyped or rebound in the three answers | `not bound to the request` | `tests/test_slot_premises.py::test_facts_retyped_or_rebound_is_unavailable` |

The Lean twins of these rows are the `#guard`s of `lean/VE/SoftNorms/SlotExamples.lean` (fixture (a), T1, T3, T4, T5). Shape checks of every slot answer (accepted, and refused with a member added, dropped or retyped, or with `facts` shifted) are in `lean/ResponseShape/SlotExamples.lean`.

## T5: facts that cannot hold together

`ConflictFreeP X P` and the certificate premise list `backgroundP X P` hold vacuously when P cannot hold together with `Background_base′`. So a slot case with non-empty facts must send `facts_model`: a finite base model over `E′_base` in which `Background_base′` and every fact hold. Lean checks it with `backgroundValidP` before any replay (`factsModel`). Theorems: `factsModel_sat` (an accepted model gives a base structure admissible for P); `slot_wire_conflict_facts` and `slot_wire_entailment_facts` (every successful slot replay with `facts ≠ []` has `∃ B, BaseAdmissibleP X P B`, so its CONFLICT-FREE or `valid` is not vacuous). A witness answer already carries its own model, which must satisfy the facts (`slot_wire_conflict_witness_sound` concludes `BaseAdmissibleP X P M`). These lines count inside the +395.

## Seeded bugs

Full records: `docs/kernel/kb-3a/seeded-bugs.json`. Each was planted, run and restored with `git checkout`.

- (i) Lean, `lean/VE/Compose/SlotWire.lean`: P dropped from `SlotEntailmentReplay.valid`'s premise list. `lake build VE.Compose.SlotWire` fails: `slot_wire_acceptance` (SlotWire.lean:368).
- (ii) Lean, same file: the conflict check over `backgroundBase'` in place of `backgroundBaseP`. It fails to build: `slot_wire_conflict_sound` (SlotWire.lean:207) and `slot_wire_empty` (:418). The theorem catches it, so fixture (a) never runs.
- (iii) Python, `ve/soft_route.py`: facts sent under `premises`. `tests/test_slot_premises.py::test_fixture_a_is_conflict_free_only_with_the_fact` FAILED (`InvalidInput: a slot case needs a facts array`).
- T1 Lean: facts decoded over E′. `decodeFacts_ok` fails to build; with that proof `sorry`'d for the seed run only, `::test_slot_fact_cannot_discharge_rule` FAILED 3/3 and `#guard`s SlotExamples.lean:113, :115 fail.
- T2 Python: the count bound to the answer's own field. `::test_slot_binding_from_request_not_answer` FAILED (DID NOT RAISE).
- T3 Lean: undecodable items skipped. `decodeFacts_ok` fails; seed run: `::test_slot_every_fact_item_decoded` FAILED 5/5.
- T4 Lean: the decoder's refusal swallowed as no facts. `decodeFacts_ok` fails; seed run: `::test_slot_fact_unknown_target_refused` FAILED 4/4.
- T5 Lean: the facts-model check skipped. `factsModel_sat` fails (SlotWire.lean:134); seed run: `::test_slot_inconsistent_facts_refused` FAILED (`status ok`, `facts 2`).
- T6 docs: a claim row printing `CONFLICT FREE`. `::test_slot_report_claims_have_runs` FAILED (`AssertionError` naming the row and `CONFLICT FREE`); it also caught one real row while this report was written, removed (`array expected` is asserted through a parametrize argument, not in the test body).

## Trust and kernel

- Trusted Lean K +0, S +3, V +62 (`uv run python tools/trust_map.py --check`: `PASS`, `against 2114035c8ca0: K +0, S +3 ... trusted +65`), signed by R16 in `docs/trust-baseline.json`.
- Trust mutants, on the cloud runner (`mac-pytest.sh --trustmut`, both example files as `--test`, `--allow docs/kernel/kb-3a/trust-mutants-allow.json`):
  - First sweep: 52 SURVIVOR and 5 UNKNOWN.
  - The guards in `b73d022787` kill the rest: UNKNOWN and pair-conflict witnesses, every variant of the soft answers, the coherent-model and budget equalities with the soft twin, the batch decoder's `case_error`, a `soft-selected` row, the norms delegate, and a bogus kind.
  - Rescore: **261 KILLED, 0 SURVIVOR, 0 UNKNOWN, 21 ALLOWED, exit 0** (`docs/kernel/kb-3a/trust-mutants.json`).
  - What is allowed: `NoFacts` (5: a Prop no check can evaluate; one mutant Lean refuses to build); the `file` UNKNOWNs (3, killed in substance); single-element and implied-type list mutants (10, equivalent); the `admission` entry of `row` (outside this item, as kb-10a records).
- Kernel: `PASS: kernel 9947 <= 9947`, `PASS: verdict writers outside the kernel 56 <= 56`.

## Decisions taken (the conservative option, not asked)

- A slot kind requires `facts` (an absent key is refused, `needFacts`). `decodeFacts` still reads absent as `[]` as the task states, and `slot_wire_empty` covers both absent and `[]`. Only `runCase` refuses an absent key, so a slot case is never answered as if it were soft.
- Non-empty facts need `facts_model` (T5, above).
- A fact naming a soft decision predicate (`soft__excepted__*` and the like, in the base vocabulary) is refused. Its decider decides it (docs/spec/kernel-boundary.md 4.1).
- `check_soft_certificate` is a new relay. Main had no Python call for `soft-certificate`; the task's "two calls" are this one and `check_soft_conflict`.

## Spec re-read

- `decodeFacts` against the task's deliverable (1): base vocabulary `envAt (soften src.D) 0`; absent → `([], [])`; non-array refused.
- The replays against deliverable (2): certificate premise list `backgroundP src.D P ++ elaborate (soften src.D).T ++ premises`; the binding list `background′ ++ items ++ layer premises ++ premises` (SlotWire.lean `replaySlotEntailment`); packages bound to `backgroundBase′ ++ items` (`decodeSlotPackage`).
- Theorem statements against deliverable (3): `slot_wire_conflict_sound` concludes `decodeSoftSource ... = .ok res.src ∧ WellFormedSoft ∧ SlotWellFormed ∧ ConflictFreeP.{0}` (SlotWire.lean:201-204).
- Answer fields against deliverable (4): the soft fields plus `facts` (Run.lean `slotCertificateAnswer`, `slotConflictAnswer`, `slotWitnessAnswer`).
- The addendum's T1 to T6 against `reviews/dri-decisions-20261112-lp1701.md` item 5 as quoted in the task.

## What was run

- `lake build` (1444 jobs) and `python3 lean/audit.py` (PASS), once on the final Lean.
- `uv run python tools/regen_generated.py --write` after the main merge; `--check` exits 0.
- `uv run python tools/trust_map.py --check`, `tools/kernel_closure.py --check`: PASS.
- The trust-mutants sweep and rescore above.
- The selected tests on the committed tree `a3ee8d86db` (`MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, ran on ve-cloud-2, 8916 s): 541 units recorded, 1 failed, `tests/test_kernel_closure.py::test_the_records_quote_the_saved_measurement`. This branch had regenerated `docs/kernel/closure-baseline.json` after writing `docs/spec/kernel-boundary.md`'s table, so its `readingsRoute`, `discourse` and `document` rows still quoted main's figures. Each path reaches the soft-norms runner and grew by 187 lines. Fixed in `9ef8642183` (the three rows only); the failed id was rerun with `zsh mac-pytest.sh -- tests/test_kernel_closure.py::test_the_records_quote_the_saved_measurement`: 1 passed, exit 0 (ve-mac-1, HEAD 9ef86421, clean). The selection was not rerun (rule: failed ids only).
- Not run by me: the full release gate (the chain runs it on the final HEAD).

## Notes for the DRI

- Main moved 49 commits during the build. The only overlap was `tests/data/route-cases.jsonl` (main's file kept, the three slot cases added) and the generated code map (regenerated). Main changed no Lean.
- The trust-mutants record's base is the pre-merge merge base `2114035c8ca0`. Main changed no Lean, so the plan is the same against the new merge base.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: PASS. `tests/test_slot_premises.py::test_facts_retyped_or_rebound_is_unavailable` (deleted, 7, true, null, [], {}, 1.5, -1, lone surrogate, 10k-deep list, shifted) and `tests/test_relay_binding_inventory.py`.
2. Deliverables: PASS. The Deliverables table above; nothing cut.
3. Tests can fail: PASS. `docs/kernel/kb-3a/seeded-bugs.json` (i to iii, T1 to T6) and `trust-mutants.json` (exit 0).
4. Python, Lean and Rust agree: PASS for Python and Lean. The relay calls in `::test_fixture_a_is_conflict_free_only_with_the_fact` and `::test_a_slot_certificate_with_its_fact_is_valid` return Lean's direct answers. Rust: N.A. (not changed).
5. R8 binding: PASS. `::test_slot_binding_from_request_not_answer`, `::test_certificate_conditional_labels_are_bound`, `::test_slot_fact_unknown_target_refused`.
6. Gate evidence on the final HEAD: PASS. Synced with main (`346a885f9a`); the selected run is on the committed final code. The full gate is the chain's.
7. No unsigned item: PASS. DELTA rows cite R8, R8, R16, R12 (`docs/kernel/kb-3a/DELTA.md`).
8. User-visible changes in DELTA: PASS. Rows 1 (the kinds), 2 (each new refusal), 3 (trust), 4 (generated files).
9. Selection: PASS. `uv run python tools/select_tests.py --base $(git merge-base HEAD main)` lists `tests/test_slot_premises.py`, `tests/test_soft_norms_lean.py` and the harness tests.
10. Statements say what is claimed: PASS. Seeds i, ii, T1, T3, T4, T5 each break a named theorem's build.
11. Budgets: N.A. The slot kinds replay given certificates and search nothing. `budget` is quoted as unused, exactly as `soft-conflict` does; the Lean `#guard` "No facts: slot-conflict answers soft-conflict's answer" checks it.
12. CPU or memory: N.A. Existing kinds are unchanged (`slot_wire_empty`); the new kinds do one replay per target, as the soft kind does.
13. Test-removed: N.A. No test removed or renamed (`git diff main...HEAD -- tests/` has no removed `def test_`).
14. Both directions, cited evidence, spec re-read: PASS. Each refusal test also asserts the accepted twin (e.g. `::test_slot_inconsistent_facts_refused` answers each fact alone; `::test_slot_every_fact_item_decoded` accepts three facts). Spec re-read above.
15. No overclaim / no silent cut / checks can fail / limits charged: PASS. Universal words in this report cite a test or command. Nothing is cut. Seeds above. Limits: N.A. (the facts list is decoded by the route's own `decodeFormulas`, the same charge as `premises`).
