# Batch 14d decision ledger

| Former decision site | Single owner and caller | Regression |
|---|---|---|
| `ve/readings.py::coupled_choices` enumerated compatible complete choices | `VE.Service.ReadingsChoices.enumerate` and `compatible`; `plan_choices` relays the Lean plan | `test_coupled_plan_response_is_typed_and_bound`, `test_coupled_plan_refuses_unresolved_set` |
| `ve/readings.py::undetermined_units` grouped coupled reading labels | `VE.Service.ReadingsChoices.openUnit`; the Python helper remains only for independent sets | `test_coupled_over_budget_response_is_typed_and_bound` |
| `ve/readings.py::_check_readings_python` folded coupled and joint choice verdicts for the Lean-owned scope | `VE.Service.ReadingsChoices.check` checks each proposed certificate or countermodel, exact choice coverage, and the ALL/SOME/NONE/UNKNOWN fold; `_choice_verdict` relays the evidence | `test_complete_choice_verdict_is_lean_checked`, `test_coupled_choice_mutations_cannot_claim_a_verdict`, `test_joint_choice_mutations_cannot_claim_a_verdict` |
| `check_readings` routed coupled and joint choices to the Python fallback | `check_readings` routes all in-scope requests to the Lean-owned path; Python still proposes search evidence | `test_complete_choice_verdict_is_lean_checked` |

Discourse already obtains its joint choice list from Lean's discourse route. The new readings mode checks that every proposed row corresponds to exactly one choice in that request list. Python retains its verdict fold only for environments outside the Lean readings modes' recorded scope. No Rust product code changed.

The `readings-choices` response has a Lean source schema, an encoder theorem, and request binding for every plan index, count, unit and coupling label. The client rejects missing, extra, mistyped, empty and unbound rows. `x-reading-plan` awaits D1 classification in the architecture ADR; the pending keyword is tracked by `test_adr_relation_keywords` and `test_lean_shapes_are_classified`.
