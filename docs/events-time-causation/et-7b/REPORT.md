# et-7b build report: scenario values for `alternatives@0` with the completion (ET-7, second part)

**DRI signature needed: DELTA row 1** (`alt-validate` with `norm-defaults@0` is now answered where et-7 refused it
by name). This is the plan's ET-7 deliverable, but widening what is accepted is outside every standing ruling. The
feature-feed rules forbid citing SYNTHESIS.md as a signature, and et-7's review left that citation to the DRI (F4).
So the item stops at review-ready's [delta] check by design (L52) until the DRI signs the row. Row 2 (trust) is R16.
Branch `feature/et-7b`, synced with main `cb033316a`. Next item: **et-8** (the Asimov and ET-1 pilot on the
completion).

## What was built

- `lean/VE/NormDefaults/Evidence.lean` (SYNTHESIS O18: one three-valued evaluator, generalised there only):
  `coneValuesAt` (the cone's assignments for any formula at any valuation; `C = []` is plain Kleene), `agreed`, and
  `denote_of_coneValuesAt`; `coneValues`, `enumerateSettled` and `settled_of_enumeration` are now their instances,
  with unchanged values and statements.
- `lean/VE/Alternatives/FillWire.lean`: spec 6.4's `SettledF`, `UndecidedF`, `AltStatus`, `ScenarioRowU` (validity,
  typed chooser and action, a validated filling, the three soundness fields); `settleU` (Kleene, then enumeration of
  the cone of `clear°(r, a)` within the budget, then two validated refillings of the cone, else UNKNOWN, with its
  evidence label), `chooserRowsU`, `scenarioRowsU` (spec's `scenarioRowU`); `settledF_of_agreed`,
  `undecidedF_of_fillings`, and `admissibleAltU_of_fillValid` (now shared with the DILEMMA theorem).
- `lean/VE/Alternatives/Run.lean`: `runValidateU` replaces the by-name refusal of `alt-validate` under the profile:
  today's validation and its text, then per chooser each alternative's status, evidence and Lean's text
  (`chooserReportU`; UNSETTLED lists only alternatives with UNDECIDED evidence), bound to the complete environment;
  optional scenario `filling` and `max_unsaid_atoms` (`budgetOf`).
- Shape `alternatives.json#/$defs/validate_fill` and `chooser_fill` (statuses and evidence as enums, `sameLength` with
  `alternatives`), sharing `evaluation` with today's row; encoder theorem `validateU_fits`.
- Python: no product change. The relay passes rows as they are (`ve/alternatives.py`); every text is Lean's.
- Fixtures: `tests/test_alternatives_fill.py` (5 test functions, 8 test ids), `FillExamples.lean` `#guard`s (T12, T12b, budget 0, a
  malformed budget); 14 genuine cases in `tests/data/route-cases.jsonl`, 9 in `tests/data/relay-gate-cases.jsonl`.

## Plan rows (ET-7, plan 5; 2.10, 3.4; spec 5 and 6.4)

| Plan row | Delivered | Where |
|---|---|---|
| scenario values under the evidence contract (C) | yes | `settleU`; `test_t12_scenario_push_undecided_pull_not_clear`, `test_t12b_…`; S1–S3 |
| UNKNOWN naming the budget; a Kleene unknown alone is UNKNOWN | yes (`MAX_UNSAID_ATOMS`) | `test_t12b_…` (budget 0); `#guard` |
| no validated filling: UNKNOWN for every alternative (SR-A4) | yes (`no filling`) | `test_a_scenario_without_a_validated_filling_is_unknown` |
| `UNSETTLED` only for alternatives with UNDECIDED evidence | yes (scenario text; the DILEMMA diagnosis is et-7's) | `test_t12_scenario_…` |
| the runner's by-name refusal of the scenario check replaced | yes; `alt-certificate`, `admission`, CONFLICT witnesses keep et-7's refusals (not in the plan's list: et-7c) | `test_cases_outside_this_item_are_refused_with_the_profile` |
| Python relay and display | relay unchanged, display is Lean's text | `test_route_row_schemas.py`, relay gate |
| T12b | yes | Lean `#guard` and pytest |
| T12f, scenario half | yes: a slot violation and an `available` naming an action as chooser answer today's texts, no status | `test_t12f_scenario_half_invalid_scenarios_keep_todays_texts` |
| seeded bugs: UNDECIDED rendered clear; Kleene-unknown as UNDECIDED without fillings | yes | S1, S2 |

## Deviations

- O18 against SYNTHESIS 4.2's queue (`Evidence.lean`: WG-6 only): WG-6 has not started and no branch in flight edits
  the file; the alternative was a second evaluator, which O18 rejects. The change is the generalisation O18 names.
- `ScenarioRowU` is spec 6.4's; the evidence label is returned beside it (`AltEvidence`, untrusted), not a field.
- With the profile, a scenario reports statuses only: a CONFLICT found on a filled scenario is a CONFLICT witness,
  which stays refused under the profile (et-7c).
- et-7's F10 (the environment mode's fault skipped when `soft-norms@0` or `rights@0` is listed) is not fixed: this
  item does not change admission or the document mode; it stays its own follow-up. F11 is et-7's DELTA wording.

## Seeded bugs ([mutants.json](mutants.json))

All 16 were killed, and the file and pin were restored after each. S1–S6 ran on a rebuilt, temporarily pinned
`ve_service`, with `VE_NATIVE_PREBUILT=1`: without it the suite's own build stops first, at the `#guard`s, which also
kill S1–S3. M4 and M6–M9 are killed by proofs. That is the evidence for an S-class statement (checklist 10). M9 first
reordered `AltStatus`'s constructors and survived (order is unobservable); its recorded form drops a constructor.

| Id | Defn | Killed by |
|---|---|---|
| S1 | `statusLabel` (UNDECIDED shown clear) | `test_t12_scenario_push_undecided_pull_not_clear` |
| S2 | `settleU` (Kleene unknown → UNDECIDED, no fillings) | `test_t12b_kleene_unknown_is_settled_by_enumeration_and_unknown_without_budget` |
| S3 | `budgetOf` | the same, and `test_a_scenario_without_a_validated_filling_is_unknown` |
| S4–S6 | `runValidateU`, `chooserReportU`, `statusPhrase` | `test_t12_scenario_push_undecided_pull_not_clear` |
| M4, M5 | `agreed`, `coneValuesAt` | `agreed_all`; `NormDefaults/Examples.lean` `#guard`s |
| M6–M9 | `SettledF`, `UndecidedF`, `ScenarioRowU`, `AltStatus` | `settledF_of_agreed`, `undecidedF_of_fillings`, `settleU`, the build |
| R1–R3 | `chooser_fill`, `evaluation`, `validate_fill` | `test_route_row_schemas.py::test_genuine_route_answers_are_accepted_by_schema_and_lean` |
| P1 | `tools/layer_policy.py` (Python) | `tools/check_lean_imports.py` (the layer gate) |

## Trust, size, pilot bytes

- Trust: K +0, S +42, V +93 (135 lines, R16's cap 150), per declaration in DELTA row 2; `trust_map.py --check`
  passes; ties row in manage-agents FOLLOW-UPS.md "## et-7b".
- Size: 727 hand-written lines added (Lean 443, of which proofs and `#guard`s about 150; tests 96; side tables and
  pins 41; this report, DELTA and mutants 147), measured with `git diff --numstat` against the merge base, generated
  files, recorded cases and saved evidence excluded. That is above ~600 (the code alone is 580). The scenario half
  could not be split further: its rows, runner, shape and fixtures go together, and the remaining refusals are
  already cut to et-7c.
- Pilot bytes: 0 expected (plan estimate 0). It gives et-8 a status for each Asimov alternative. Nothing is claimed
  before a pilot audit.

## Tests run

- `tests/test_alternatives_fill.py` (35 passed); the selected tests (`mac-pytest.sh --select`, ve-mac-1, HEAD
  `73a944f7`): 361 units, 0 failed, none of main-known-red.txt.
- `tools/relay_mutation_gate.py --route service:alternatives`: 14,096 mutants, 0 failures (the new chooser names and
  alternatives use the paths today's scenario rows file under F4; statuses and evidence are enums bound by length).
- `lake build`; `python3 lean/audit.py` (551 sources, 6,338 theorems); `tools/regen_generated.py --check` (31
  entries); `tools/trust_map.py --check`; `tools/gate_collection.py --check --prebuilt` (8 added, 0 refused, stale or
  malformed). The full gate is the chain's, on the final HEAD.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: PASS. Relay gate (14,096 mutants, 0 failures); `validateU_fits`; `test_scenario_request_faults`.
2. Every deliverable: PASS. Plan-row table above; no Python copy of a Lean decision; no report test; lf-18's files
   (`ve/alternatives.py`, `Decl.lean`) untouched.
3. Tests can fail: PASS. 16 seeded bugs, [mutants.json](mutants.json).
4. Py/Lean/Rust agree: PASS. Plain sources keep today's path (`test_alternatives_three_way.py`, `test_asimov_laws.py`
   in the selected run); `NormDefaults/Examples.lean` `#guard`s unchanged; no Rust change.
5. R8 binding: PASS for statuses and evidence (enum, `sameLength`; R1–R3). Chooser and alternative names keep the F4
   class of today's scenario rows, because the model's domains are an object keyed by a sort.
6. Gate evidence matches HEAD: PASS. Synced with main `cb033316a` (73a944f7); the gate is the chain's.
7. No unsigned item: PASS except the one reserved row. `review-ready.py --delta-dri-needed` lists DELTA row 1, the
   reason the item stops (first line); row 2 cites R16 with its evidence.
8. Every user-visible change in DELTA: PASS. [evidence/delta.json](evidence/delta.json), 13 records.
9. Test selection: PASS. `select_tests.py --base $(git merge-base HEAD main)` selects 361 of 442 units, including
   `test_alternatives_fill.py` and `test_route_row_schemas.py`, the tests the seeded bugs break.
10. Statements say what is claimed: PASS. M6–M8 break the proofs; `ScenarioRowU` is spec 6.4's.
11. Budgets fail closed: PASS. `max_unsaid_atoms` 0 gives UNKNOWN (`MAX_UNSAID_ATOMS`, `no filling`); a larger value
    is capped (`test_t12b_…`); no sleep or deadline.
12. No CPU or memory regression: PASS. Plain sources run today's code. The search runs only under the profile, at
    most 2 × 2^12 validated refillings per alternative, and none beyond the budget (budget 0 skips it).
13. Test-removed trailers: PASS. `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed (no test
    removed; `test_cases_outside_this_item_are_refused_with_the_profile` keeps its name).
