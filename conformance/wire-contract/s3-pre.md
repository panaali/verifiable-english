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

## Result: no verdict difference; a code difference

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

**Status: closed** (no reachable verdict difference).
