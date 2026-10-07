# Lean-first batch 5: deletion ledger

Base: `9aaf918d`. The owner of risk and alternatives acceptance is Lean. Python constructs and displays accepted data; Rust no longer evaluates risk cells.

| Deleted decision site | Decision | Lean owner and caller |
|---|---|---|
| `ve/environment.py::_alternatives_block` | Block fields, role names and sorts, wording, outcomes, performed and fulfilment checks, limits, first diagnostic | `VE.Alternatives.Wire.decodeBlock`, `checkBlock`, `decodeAltSource`; `Environment._decode` calls `decide("alternatives", alt-elaborate)` before constructing the container. `checkReservedWording` now covers the wording claim absent in Lean. |
| `ve/risk.py::decode_block`, `check_alt_reserved`, `check_block`, `check_route_declarations`, `validate_block` and helpers | Risk shape, severity order, classes, protected names, quantity tags, route eligibility, diagnostics | `VE.Risk.Wire.decodeRiskSource`, `decodeRiskBlock`, `checkRiskBlock`; `Environment._decode` calls `decide("risk", risk-elaborate)` before construction. `risk.run_case` transports raw cases. |
| `ve/alternatives.py::run_case` and `ve/risk.py::run_case` prechecks | Route kind, profile and input-shape rejection before Lean | The alternatives and risk service modes dispatch and reject the raw case; both Python functions now only transport it. |
| `ve/document.py::coverage` alternatives fold | Declared alternatives, counterfactual and proximate cells, table completion, unmapped obligations, residual counts | `VE.Alternatives.Wire.coverage` returned in `alt-elaborate` and `risk-elaborate`; Python copies `coverage.alternatives` and `coverage.residual`. The response shape is generated from `ResponseShape.Schemas.Alternatives`. |
| `ve/admission.py` alternatives-first and quantity-first branch on a risk environment | Which admission route checks a risk document | `VE.Risk.Run.runAdmission`; `admit_document` chooses risk before alternatives and quantity. |
| `rust/ve-profile/src/risk.rs`, exports and `ve conformance`'s `risk-condition`/`risk-cells` branches | Condition possible/certain and cell regeneration in a third language | `VE.Risk.Eval` and `VE.Risk.Run.runDecision`; Python's `ve.risk.run_case` calls Lean. The test of the Rust duplicate is removed; Lean's 10,000-case comparison with brute-force enumeration remains. |

The retained environment vocabulary and envelope checks, document wrapper logic, and quantity admission belong to later batches 12, 17 and 9. The risk and alternatives entry paths invoke their Lean route before those constructors continue. The `coverage_units` extension is internal to the document coverage call; its schema checks the section names, array/object shape and nonnegative integer residuals. Lean selects the rows and derives every count.

`rg` over `ve/`, `rust/`, `tests/` and `tools/` finds no consumer of the deleted `_alternatives_block`, risk validator symbols or Rust risk evaluator exports. The only remaining `risk-condition`/`risk-cells` strings are historical fixtures and prose; `ve conformance` no longer recognizes these untrusted differential-only kinds.
