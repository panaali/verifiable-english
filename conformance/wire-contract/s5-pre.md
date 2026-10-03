# S5-pre: the legacy verdict differences of `norms@0` and `norm-defaults@0` (open)

Status: open. This file records the measurement that S5-pre of
[wire-contract-s5.md](../../docs/spec/wire-contract-s5.md) 2.12 asks for; no
difference listed here is fixed yet, and each blocks its unit's switch. A fix
changes a verdict of a rejected or accepted input, which is a product decision
outside the wire work, made in Python first where Python's verdict changes.

## How it was measured

`python -m conformance.wire_contract_gate --unit <unit> --legacy-only` runs the
unit's Python legacy validator (`legacy_validation` of `ve/norms_contract.py` or
`ve/norm_defaults_contract.py`) and the unit's frozen Lean route
(`ve_norms_route` with `norms-elaborate`, `ve_norm_defaults_route` with
`norm-defaults-elaborate`) on every corpus case that Lean reads, and lists the
cases on which one rejects and the other accepts. It runs no engine, so it
needs no `ve_diagnose` entry for either unit. The corpus is the shadow gate's
(tiers 0, A, B, R and L) at revision 1 of each contract, on the branch
`wire-s5/py`.

## `norms@0`: 2,857 cases, two differences

| Case | Python | Lean route |
|---|---|---|
| `L:defined-layer`: a regulated rule's guard mentions a defined predicate whose body mentions the rule's own predicate, under `definitions@0` | accepts | `DependencyCycle: d, x_required` |
| `L:constant-verbalisation`: a constant with a `verbalisation` member | accepts | `fields do not match: expected [sort, description], got [description, sort, verbalisation]` |

The first is the fourth candidate of 2.12: Python's layer graph has regulated
nodes only (`ve/norms.py`, the layer order), Lean's stratum graph has regulated
and defined nodes. The second was not a candidate. Python's environment decoder
admits `verbalisation` on a constant; the norms route's environment decoder
does not.

## `norm-defaults@0`: 3,024 cases, six differences in three classes

| Case | Python | Lean route |
|---|---|---|
| `0:fill-premise` (fixture D11: unit 0's guard a balanced conjunction of 3,320 atoms) | `ResourceLimit: fill premise unsaid:pair:x_required,x_permitted` | accepts |
| `L:data-flag`: a `data@0` predicate with a `functional` flag | accepts | `UnsupportedProfile: norms route with data flags is not implemented` |
| `L:constant-verbalisation`, and three recorded inputs of `tests/test_norm_defaults.py` (`test_u1_claude_settled_no_and_sol_undecided`, `test_u1_variants_keep_the_unchanged_decoder_identity`) whose constants carry `verbalisation` | accepts | `fields do not match: expected [sort, description], got [description, sort, verbalisation]` |

The first two are the third and first candidates of 2.12. The third is the
class found under `norms@0`, reached here by inputs the tests already submit.

The second candidate of 2.12 (a document that the decoder accepts and that
`norms-elaborate` then rejects) has no case on either corpus.

## Found while aligning the two adapters' domain: a Python crash

An environment whose `profiles` is a number or a Boolean is inside the domain of
`norms@0` (2.2: an environment that does not decode is in the domain). Python's
environment decoder raises `TypeError` on it (`"speech-acts@0" in
data.get("profiles", [])`, `ve/environment.py:327`), not a `VEError`, so the
Python legacy validator neither accepts nor rejects, and the call
`admit_document` raises `TypeError`; the Lean route rejects, and `ve_diagnose`
reports 1.1. `ve/environment.py` is outside item 1's diff scope (7.2), so the
crash is recorded here, not fixed, and pinned by
`tests/test_wire_contract_s5_lean.py::test_both_adapters_share_one_domain`
(the expectation `crash`). The gate's corpus holds no such source: the gate's
Python column reads only a `VEError`. Under `norm-defaults@0` the same
environment lists no profile and is outside the domain.

## Class differences (recorded, not S5-pre's)

On the cases both validators reject, the Python class and the class that
`checker_error` gives the Lean route's text differ on 441 `norms@0` cases and on
365 `norm-defaults@0` cases. Most are Lean texts without a class prefix
(`SyntaxError / InvalidInput`, `UnboundVariable / InvalidInput`), and the two
recorded in 2.3 (`norms@0 is required` and `regulated predicate`). They are not
verdict differences; the contract keeps Python's classes (D3), and the measured
delta's `lean_route_changes` will report them once the Lean engine runs.

## Integrated three-way measurement

After merging the Python and Lean engines, the complete shadow gates ran over
2,857 `norms@0` and 3,024 `norm-defaults@0` cases. The stored gate and delta
reports are `norms@0-gate.json`, `norm-defaults@0-gate.json`, and their
`-delta.json` counterparts. Python has zero deferred cases, residuals, or
class differences for both units. The gates still fail for the verdict
differences above: the Lean engine disagrees with Python on the constant
`verbalisation` cases, and `norm-defaults@0` has no Lean first-fault witness
for check 6.3 because the Lean route accepts D11. The two switch gates cannot
pass until the product verdicts are reconciled and remeasured.
