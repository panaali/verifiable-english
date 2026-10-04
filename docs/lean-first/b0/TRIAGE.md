# Lean-first batch 0: triage of the differential fuzzer's disagreements

Plan: `docs/LEAN-FIRST-PLAN.md` (draft 3, branch `design/lean-first`), section 5.2 row 0 and section 2.5.
Source: the fuzzer's reviewed baseline `conformance/difffuzz-baseline.json` on `infra/difffuzz` at `9d7b8ccc`
(not on `main`; format `ve-difffuzz-baseline@2`, 403 entries in 18 follow-up groups, DF-1 to DF-18; the plan
was written against the earlier 138-entry, 13-group baseline). The data, with one minimised input per group and
each implementation's recorded answer, is [`conformance/lean-first/df-triage.json`](../../../conformance/lean-first/df-triage.json);
`tests/test_lean_first_triage.py` checks that every group is classed and runs the Lean-accepts bugs live.

Classes (the plan's three, plus two for groups where Lean is not in question):

- **i**: the frozen contract fixes Python's behaviour, so Lean has a bug, fixed before that surface switches.
- **ii**: the contract is silent (or fixes Lean's answer) and Lean's answer is sound; the switch changes the
  answer, listed in that batch's `DELTA.md` and signed (an `availability` or `verdict` change needs one DRI
  signature each; `wording` and `order` lists are signed as a block).
- **iii**: the contract is silent and Lean is wrong, so Lean has a bug, fixed before that surface switches.
- **rust-only**: Lean and Python agree; only Rust differs, and Rust texts never reach a user (rule 4).
- **closed**: no longer reproduces at the batch base (`62a5c589`).

The batch column names the batch the group must be resolved before (class i and iii) or in (class ii).

| Group | Class | Batch | Entries | Finding and reasoning |
|---|---|---|---:|---|
| DF-1 | closed | 12 | 17 | Python raised TypeError on a non-array `profiles`; Lean and Rust give the P0 text. Closed at the batch base: fix/env-field-types is on main and Python now gives Lean's diagnostic (test_df1_is_closed_at_the_base). |
| DF-2 | ii | 13b, 15b | 6 | Python crashes (TypeError) on an array or object where a name or tag belongs; only VEError may escape (checklist 5), Lean's decoder rejects with a diagnostic. Lean is sound; a crash becoming Lean's rejection is an availability change, signed when the formula decoder (13b) and search (15b) switch. |
| DF-3 | ii | 12 | 85 | Nested vocabulary fields of the wrong JSON type: both reject with the same code; the texts differ (Lean's decoder type diagnostics). The env-profiles directive fixed Lean's texts for top-level fields; the contract is silent on nested ones. Wording change in batch 12's list. |
| DF-4 | rust-only | 15b | 8 | Lean and Python give the P0 contract's text; only Rust differs. No Lean action: Rust texts never reach a user (rule 4). |
| DF-5 | i | 12 | 19 | A non-string or unknown spec_revision: the frozen v0 contract fixes UnsupportedProfile (conformance/validation.json validation_000 class); Lean says InvalidInput or reports another field first. Lean bug, fixed before the environment surface switches. |
| DF-6 | i | 12 | 33 | Language and envelope versions: validation.json fixes UnsupportedProfile for an unknown language (validation_000); Lean's v0 runner says InvalidInput (`unsupported environment version`) or `fields do not match`. Lean bug, fixed before batch 12. |
| DF-7 | i | 12 | 56 | Model shape errors: validation.json fixes InvalidModel (validation_007 to validation_020); Lean's route and v0 runner say InvalidInput and read the formulas first. Lean bug, fixed before batch 12 switches model validation. |
| DF-8 | i | 12 | 5 | The dependency-order route does not decode the vocabulary: it accepts an envelope with a misspelt vocabulary field that the P0 envelope contract (exact fields) rejects, and Python rejects. Lean-accepts bug (section 7.1), fixed before batch 12; the Rust `DependencyCycle` code is rule 4. Live fixture: test_df8_dependency_order_accepts_a_misspelt_vocabulary_field. |
| DF-9 | i | 12, 13b | 118 | Nested decoder codes and order: validation.json fixes UnknownSymbol, TypeMismatch, UnboundVariable, DuplicateDeclaration and SyntaxError for v0 envelopes where Lean's v0 runner and route say InvalidInput. Lean bug where a frozen fixture fixes the code; on ve.core@0.2 inputs the contract is silent and the change is `order` (13b's list). |
| DF-10 | ii | 13b | 1 | A non-string label: labels.json fixes AdmissionError for invalid string labels only; for a non-string the contract is silent and Lean's InvalidInput (a type error) is sound. Code change, 13b's list. |
| DF-11 | ii | 13b | 1 | Admission with a malformed certificate trace: both reject; Python reports the admission label first, Lean the certificate's fields. Order change, 13b's list. |
| DF-12 | iii | 5 (also 9) | 1 | An NBSP in a regulated act phrase: Python rejects (the W6 round trip), Lean's risk route accepts an act phrase whose canonical form differs from its text. Contract silent on Unicode spaces; Lean is wrong (one normaliser, FINDING-CLASSES class 4). Lean-accepts bug, fixed before batch 5. Live fixture: test_df12_risk_route_accepts_an_nbsp_act_phrase. |
| DF-13 | ii | 5, 6, 7, 8, 10, 11 | 28 | Block routes: both reject; Lean reports the block-level diagnostic where Python reports the field or the missing profile. Order and code changes in each block's batch. |
| DF-14 | ii | 6 | 3 | Python's wire-contract engine accepts a JSON null that the restricted wire excludes and every Lean and Rust reader refuses. Lean is right; closed when batch 6 deletes the Python engine. |
| DF-15 | rust-only | 15b | 10 | Rust reads a request without its model as another operation; Lean rejects (`property not found`). Rule 4. |
| DF-16 | ii | 15b | 3 | Python's search and countermodel check accept an object for `premises`; Lean says `array expected`. Lean is sound; the change from an answer to a rejection is a verdict change, signed in 15b. |
| DF-17 | iii | 10a | 1 | The norm-defaults route refuses data flags (`not implemented`) on an environment Python accepts: a missing Lean feature, ported in 10a before 10b switches. |
| DF-18 | ii | 6 | 8 | Python's `Environment` is not the soft-norms decoder (`SoftEnvironment` is); Lean's soft route and Rust accept the soft block. Lean is sound; closed by batch 6's switch. |
| K1 | iii | 12 | – | Act-phrase word `no`: Python's reserved words include it (ve/environment.py RESERVED), Lean's copy does not (lean/VE/Norms/Wire.lean actReserved). DRI answer 6: Lean adopts Python's list as a signed change before the surface switches. Live fixture: test_k1_lean_accepts_the_act_phrase_word_no. |
| K2 | closed | 7 | – | Duplicate `protected` rights entries (ARCH-ROADMAP's Lean-accepts bug): closed at the batch base. Lean's rights route now rejects a repeated name, as Python's RightsEnvironment does; only the texts differ (`protected` against `protected person`), a wording change for batch 7's list. Live fixture: test_k2_duplicate_protected_entries_are_rejected_by_both. |
| K3 | i | 12 | – | = DF-8 (the dependency-order route accepts an envelope Python and the envelope contract reject). |
| K4 | iii | 5 | – | = DF-12 (the risk route accepts an NBSP act phrase). |
| R1 | ii | 3 | – | Readings S1: a disagreement between Lean's readings answer and Python's regeneration is CheckerUnavailable today (ve/readings_route.py); batch 3 relays Lean's row, so each such input becomes Lean's answer, an availability change signed per input. No disagreement is known: the UDHR pilot's whole-document call regenerated byte for byte (LEAN-FIRST-PLAN.md 3.5), and the pilots of the A/B corpus show none. The fixture is the existing test that a disagreement is CheckerUnavailable, which batch 3 must turn into a listed availability change. |

## What the triage found beyond the plan

- **K2 is closed.** The plan lists duplicate `protected` rights entries among Lean's acceptance bugs (section 7.1).
  At the batch base Lean's rights route rejects a repeated name as Python does (`InvalidInput: protected person`
  against Python's `InvalidInput: protected`); only the wording differs, for batch 7's list.
- **DF-1 is closed.** `fix/env-field-types` is on `main`; Python now gives the P0 text Lean and Rust give. The
  fuzzer's baseline still lists its 17 entries, so its next `--update-baseline` drops them (the fuzzer's own
  acceptance item, owner: orchestrator).
- **K1 (act-phrase `no`) is live.** Python rejects `{0} be no longer done`, Lean's norms route accepts it; DRI
  answer 6 has Lean adopt Python's list as a signed change before batch 12 switches the environment surface.
  Lean's identifier list (`lean/VE/Surface.lean`) lacks `no` too.
- **DF-8 is an empty vocabulary.** The minimised Lean-accepts input is a dependency-order request whose
  vocabulary is `{}`: Lean answers an empty order, Python and Rust reject the envelope.
- **Not triaged here:** groups the fuzzer does not cover (its "Not covered" list: duplicate keys, `max_count`,
  10,000-deep nesting, the discourse, rights and readings routes). The readings case is R1.
