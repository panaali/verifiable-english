# Batch 13b deletion ledger

Base: `main` at `abc30811`. The core operations named in plan row 13b are Lean's under every authority:
`dispatch.LEAN_OWNED` lists them, `dispatch.SINGLE_OWNER` maps each to `lean`, and `dispatch.execute` refuses
them, so no caller can hand them a second implementation. Every deleted Python decision site is mapped to the
Lean check or answer that owns it, or to a retained fallback named in [DELTA.md](DELTA.md).

| Deleted Python decision site | Lean owner (caller) |
|---|---|
| `admission._admit_document_python`: envelope, family and definitions refusals, `_decode_doc`/`_decode_node` decoding, certificate binding prechecks, `_node_admitted`/`_leaf_admitted` label admission, `_diagnostic` texts, `_check_graph` claim graph and replay, cited-lemma leaves, `_compatible` reading choices, citation refusal, report and `report_id` | route `admission` (`VE.Route.Admission`, `runAdmission_sound`) and the norms route's admission (`VE.Norms.Run.runAdmission`, `runAdmission_sound`); caller `admission._admit_lean`, bound by `admission.bound_admission` |
| `admission._validate_label_python` (`AdmissionError: invalid label`) | route `label`; caller `admission.validate_label` |
| `norm_admission._admit_norm_document_python`: norms-profile and family refusals, norm-unit decoding, quoted-norm checks, layer-leaf admission, report and `report_id` | norms route `admission` (`VE.Norms.Run.runAdmission`); caller `norm_admission.admit_norm_document`, bound by `bound_admission` |
| `background._background_python` and the premise generators `_flag_premises`, `_profile_premises`, `_empty`, `_valid` (Background premises and their order) | route and norms `background` (`VE.Route.Background`, `Plain.run`); caller `background.background` over `lean_runner.background_environment` |
| `background._dependency_order_python` (`DependencyCycle`, order) | route `dependency-order`; caller `background.dependency_order` |
| `ast.check_formula`/`check_document` Python and Rust typing closures, `_typing_in_scope` | `check` mode (`Standalone.checkCase`, `check_iff_wellFormed`), its typing view extended to `readings@1`, `norm-defaults@0` and `risk@0` (`Standalone.typingReduced`) |
| `parser.parse_with_metadata` Python-authority branch (Python decides acceptance) | `parse` mode (`Standalone.reportedParse`, batch 13a's located diagnostics); Python constructs only after Lean accepts |
| `definitions.compile_definitions` Python-authority branch and the `validation.decided` arbitration (Python's text won when both rejected) | route `background` over the definitions (`Standalone.validated`, `checkDefinitions`); Lean's premises are the definitions (`definitions._compile_lean`) |
| `bundle.check_bundle` Python-authority branch and `validation.decided` | route `bundle` (`bundle_sound`) and `bundle` mode (`FamilyBundle`); `validation.construct_after_lean` builds the report only after Lean accepts |
| `validation.decided` (the legacy arbitration adapter) | deleted; no consumer |
| `norms.NormDocument.elaborate`/`premises`, `check_norm_entailment_certificate`, `check_conflict` Python-authority branches | `norms`/`family-norms` modes (`norms-elaborate`, `norms-certificate`, `norms-conflict`) |
| `entailment.check_entailment_certificate` Python-authority branch (the default replay) | certificate modes (`checkCertificate_sound*`, batch 13a's binding and step budget) |
| `argument.check_argument`, `readings.check_readings`, `vacuity.premise_status`, `equivalence.compare` Python-authority and shadow branches | `graph` and `readings` modes confirm the verdict; the small Python rules of premise status and compare read only Lean-checked replays and model checks (`dispatch.owned` pins their constituents to Lean) |
| `conformance.three_way`: Python's column for `admission`, `background`, `certificate`, `dependency-order` and `label` | `KIND_OPERATIONS`: those answers are Lean's own, never compared with Lean |

Retained, each named in [DELTA.md](DELTA.md) with its reason: the four stage-2c fallbacks of plan row 13b,
the scope gaps the inventory found while switching (statement-layer and W6 environments for parse, graph,
readings, norms and bundles; certificate replay over `norm-defaults@0` and `readings@1`), the prover's
internal replay (rule 3, lead decision of 2026-10-08), and the envelope routing refusal of a frozen v0/v0.1
envelope in `admission._admit_lean`.

`tools/inventory_lint.py` and `tools/semantic_inventory.py` no longer name a deleted body; `rg` finds no
consumer of `_admit_document_python`, `_admit_norm_document_python`, `_background_python`,
`_dependency_order_python`, `_validate_label_python`, `_check_graph` or `validation.decided`
(`test_no_consumer_of_a_deleted_decision_site`).
