# P0 integration: three-way conformance (2026-09-25)

Branch `expand/p0` = `ve-integration` + `expand/p0-py` + `expand/p0-lean`. Where the halves
disagreed, PLAN-EXPAND2.md (adopted) decided.

## Interface mismatches found and how they were resolved

| # | Mismatch | Plan basis | Resolution |
|---|---|---|---|
| 1 | Lean required `description` on a `$string` constant; Python/Rust made it optional | W5: `"finance": {"sort": "$string"}` | Lean: `sort` required, `description` optional (nonempty when present) |
| 2 | Lean admitted `$string` predicate arguments; Python/Rust rejected them | W5 stage 1: equality only | Lean rejects them (W5 may widen this with its flags) |
| 3 | Lean's order route rejected `$string` literals (case `order-with-literals`); Python/Rust accepted | 3.1: Background depends on env only; order is an allowed family | Order route admits literals: the unchanged numbers2 decoder runs on the vocabulary without literals, literals become constants of user sort `$string` (never in `sorts`), Background (`orderLiterals`) is regenerated, checked on models and bound in certificates; new theorems below |
| 4 | Python skipped prepending Background when the caller's premises already began with it; Lean always prepends, so the certificate bindings differed | 3.4: `Entails E_out (Background ++ premises Γ)` | Python always binds Background ++ premises; internal replays pass the already expanded list |
| 5 | closure+n-ary: Lean's runner rejects every case (gated until W4); Python/Rust evaluated it as closure | 3.3: closure+n-ary gated until W4 lands | Python and Rust reject at every checking site with Lean's diagnostic; the envelope gate still accepts the family (3.10(4)) |
| 6 | Rust reported a generic message for a wrong v0.2 `spec_revision`; Python/Lean name it | 3.3: Rust mirrors the envelope check with the same diagnostic | Rust: `Unsupported specification revision <r>` |
| 7 | Python had no label grammar (any nonempty string) and no bridge admission; Lean parses canonical labels and admits documents | 3.6: admission enforced by Python and Lean; same diagnostic | `ve/admission.py` mirrors `Admission.lean` rule for rule (labels, kinds, lemmas, reading sets, bridge/background leaves, diagnostics, report id); `Claim` labels must parse |
| 8 | No shared label or DAG case form across the three | 3.5, 3.6 tests | Lean `route` gains a `label` case kind; Rust gains `label` and `dependency-order` kinds (`rust/ve-core/src/route.rs`); Python `dependency_order_nodes` takes the shared wire form |

Admission graph edges bind exactly their premise nodes (Background enters as explicit
`background:<generator>` leaves); the `certificate` case and every Python entailment site bind
Background ++ premises. Both are as Lean had them; Python now matches both.

## Families and verdicts

`conformance/p0.py` writes six families; `tests/test_p0_three_way.py` runs each through Python,
Rust and `ve_conformance route` and requires the `expected` verdict from each:

| Family | Cases | Python | Lean | Rust |
|---|---|---|---|---|
| `elaborated-document` | 37 | 37 | 37 (search checked as the found model) | 32: FOL/closure all but stale certificates; order evaluation only; valid certificates as "no countermodel within bound 2" |
| `invalid-background-model` | 7 (2 pending: W5, W3) | 5 | 5 | 4 (order evaluation included) |
| `dependency-order` | 207 (200 generated) | all | all | all |
| `labels` | 52 | all | all | all |
| `admission` | 18 | all (same report ids) | all | out of scope (3.7) |
| `vacuity` | 7 | 7 (premise status) | 7 (certificate for Background ++ premises ⊢ ⊥, or a model) | 4 FOL: bounded search agrees |

`lean/VE/Route/examples/route-cases.json` (326 cases) is generated from the same families.

## New Lean theorem statements (for statement review)

All in `VE.Route.Background` (order route with literals):

- `orderLiteralPremise_denote`: an order literal premise holds iff the two constants share no value.
- `orderLiterals_sat_iff`: for duplicate-free literals, an order structure satisfies the generated
  premises iff distinct declared literals denote distinct values (`OrderLiteralsDistinct`).
- `orderLiteralsValid_sound`: the executable literal check on a finite order model implies
  `OrderLiteralsDistinct`.
- `order_string_route_entails_iff`: order entailment from literals ++ Γ iff consequence over
  string-admissible order structures (`OrderStringAdmissible` = admissible ∧ `OrderLiteralsDistinct`).
- `order_string_route_acceptance`: an accepted order certificate for literals ++ Γ ⊢ φ gives the
  entailment and φ in every string-admissible order structure satisfying Γ.
- `order_string_route_countermodel`: an admissible finite order model that passes the literal check
  and the countermodel check refutes both.

New definitions under review: `OrderLiteralsDistinct`, `OrderStringAdmissible` (the order form of
the stage-1 meaning of `$string`). No existing theorem statement changed.
