# S3-pre: the inherited `norm-defaults@0` difference, run to ground

Step S3-pre of [wire-contract-PLAN.md](../../docs/spec/wire-contract-PLAN.md) (section 7) and the last row of the
continuation gate in [wire-contract.md](../../docs/spec/wire-contract.md) section 9. Run on 2026-10-02 on branch
`wire/lean`; `tests/test_wire_contract_soft_lean.py::test_s3_pre_norm_defaults_profile` repeats it.

## The difference

`ve/softnorms.py:97` lists `norm-defaults@0` among the profiles that phase 2 passes on to W1's decoding of the
stripped environment (`_INHERITED_PROFILES`). `lean/VE/SoftNorms/Phases.lean:36` (`inheritedProfiles`) and
soft-norms.md 2.3 do not. So for a source whose `profiles` contain `norm-defaults@0`, Python decodes the
vocabulary under `norm-defaults@0` and Lean without it. For every other source the two lists give the same
profiles.

## First result (2026-10-02, superseded by the re-run below): no verdict difference; a code difference

Every soft source whose `profiles` contain `norm-defaults@0` is rejected by both implementations:

- **Lean** rejects it at the latest at check 3.2: `norm-defaults@0` is not in `VE.Route.Gate.registry`, so
  `UnsupportedProfile: Unsupported profile norm-defaults@0` (code `SOFT_UNSUPPORTED_PROFILE`), unless an
  earlier check fails first.
- **Python** passes 3.2 (its registry, `ve/profiles.py:26`, has `norm-defaults@0`) and, once the whole table
  holds, rejects while building the document: `SoftNormDocument._init_soft` always calls
  `self.elaborated.premises()` (`ve/softnorms.py:752`), which calls `NormDocument._require_completion`
  (`ve/norms.py:294-299`): `UnsupportedProfile: norm-defaults@0 documents are checked through fill
  (ve.norm_defaults)`, code `SOFT_UNSUPPORTED_PROFILE`.

Neither implementation accepts such a source, so no verdict differs and nothing outside this work needs a fix.
The difference is diagnostic only, which is what the contract settles:

| Source (profiles add `norm-defaults@0` unless stated) | Python | Lean route and `ve_diagnose` |
|---|---|---|
| `multi_fault_base()` | `SOFT_UNSUPPORTED_PROFILE`, "... checked through fill ..." | `SOFT_UNSUPPORTED_PROFILE`, check 3.2, `Unsupported profile norm-defaults@0` |
| `env()` with no rules | the same | the same |
| `env()` with no regulated predicate | the same | the same |
| `env()` with `x_required`'s default `unspecified` | `SOFT_UNSUPPORTED_PROFILE`, "... checked through fill ..." | `SOFT_INVALID_INPUT`, check 2.3, `InvalidInput: invalid regulated role or default for x_required` |
| the last row without `norm-defaults@0` | `SOFT_INVALID_INPUT`, `UnsupportedProfile: unspecified completion requires norm-defaults@0` | `SOFT_INVALID_INPUT`, check 2.3, the same Lean text |

The fourth row is the one input found where the codes differ: Python's W1 decoding admits the `unspecified`
default under `norm-defaults@0` and the rejection comes later, while Lean's decoding, without that profile,
rejects at 2.3. The pilot's delta report (plan 5.1, step 4) lists it; the decision is the DRI's at step 5.
Removing `norm-defaults@0` from Python's `_INHERITED_PROFILES` would make the first failing check 2.3 in both,
but `ve/softnorms.py` is not edited in S0 to S3 (spec 7.2).

## Re-run after the wire review (2026-10-02): the registries differ more widely, and one verdict differs

The wire review (Fable A1) found the two engines disagreeing on the first row above: Python's engine reported
6.10c and Lean's 3.2, because the Python hooks used Python's lists (`_INHERITED_PROFILES` for 2.3 and
`profiles.BY_NAME` for 3.2). The hooks now use the Lean route's lists (`ve/softnorms_contract.py`,
`INHERITED_PROFILES` and `ROUTE_PROFILES`, compared with the Lean sources by
`tests/test_softnorms_contract.py::test_hook_lists_are_the_lean_route_lists`), so both engines report the
Lean column of the tables here.

Checking 3.2's registry found the difference is wider than `norm-defaults@0`. `ve/profiles.py` registers six
profiles that `VE.Route.Gate.registry` does not: `alternatives@0`, `norm-defaults@0`, `reports@0`,
`rights@0`, `risk@0` and `speech-acts@0`. The Lean route rejects a soft source that lists any of them at 3.2.
Python's legacy validator, on `env()` and on `multi_fault_base()` with the profile added, does this
(`tests/test_wire_contract_soft_lean.py::test_profiles_outside_the_lean_route_three_way` pins it):

| Profile added | Python `load_soft_document` | Lean route, both engines |
|---|---|---|
| `alternatives@0` | `SOFT_UNSUPPORTED_PROFILE`, `alternatives@0 with soft-norms@0` | 3.2 |
| `norm-defaults@0` | `SOFT_UNSUPPORTED_PROFILE`, "... checked through fill ..." | 3.2 |
| `reports@0` | `SOFT_UNSUPPORTED_PROFILE`, `reports@0 with norms@0 layers` | 3.2 |
| `rights@0` | **accepts** | 3.2 |
| `risk@0` | `SOFT_UNSUPPORTED_PROFILE`, `risk@0 requires alternatives@0` | 3.2 |
| `speech-acts@0` | `SOFT_INVALID_INPUT`, `Incorrect fields (missing=['speech_acts'], unknown=[])` | 3.2 |

`rights@0` is a reachable **verdict** difference between the legacy validators: Python accepts a soft source
with `rights@0` among its profiles (its registry requires `soft-norms@0` with it, `ve/profiles.py:91`), and the
Lean soft route rejects it. Neither validator may be edited in S0 to S3 (spec 7.2), and the contract cannot
follow both: it follows Lean (D3), so the Python engine reports 3.2 on a source that Python's legacy
validator accepts. The gate report lists the case under `legacy_verdict_differences`.

**Status: open.** The S3-pre row of the continuation gate (spec 9) requires that a reachable verdict
difference is fixed outside this work; the `rights@0` difference is not fixed, so the row is not closed.
