# et-7b build report: scenario values for `alternatives@0` with the completion (ET-7, second part)

**DELTA row 1 SIGNED by the DRI 2026-10-19 (dri-decisions-20261019.md #1)** (`alt-validate` with `norm-defaults@0`
is now answered where et-7 refused it by name): an intended widening of the events/alternatives feature, on the
condition that the branch tests the new answers and the budget-cut UNKNOWN naming `MAX_UNSAID_ATOMS` (it does:
`tests/test_alternatives_fill.py`). Row 2 (trust) is R16.
Branch `feature/et-7b`, synced with main `cb033316a`. Next item: **et-8** (the Asimov and ET-1 pilot on the
completion).

## Review fix 1 (et-7b-review.final.md)

- **F1 (B), fixed in Lean.** When the budget cut the search for a filling of the scenario, every alternative was
  UNKNOWN `no filling`, without the budget the spec requires (spec C, "naming the budget when it was exhausted").
  The class is "an UNKNOWN that does not say why", so the reason now travels with the result instead of being
  guessed where it is shown: `fillingFor` returns `Except AltEvidence`, `budget` when the scenario leaves more unsaid
  atoms than the budget and `noFilling` only after every assignment was tried (theorem `fillingFor_error` proves
  both). `scenarioRowsU` carries it and `runValidateU` labels every alternative with it. Sweep: the search UNKNOWN
  (`settleU`'s `.search`) was the only other UNKNOWN whose text gave no reason; it now says the search found no two
  validated fillings that disagree. The budget text is the same for the cone and the filling search: "more than
  <n> unsaid atoms (MAX_UNSAID_ATOMS) would have to be searched".
- Regression tests: the review's probe (`test_a_scenario_whose_filling_search_the_budget_cuts_is_unknown_naming_the_budget`,
  budgets 0 and 1 cut, 2 settles); the review's 12/13-action example at the default budget
  (`test_the_default_budget_is_named_when_the_scenario_leaves_more_atoms_unsaid`); Lean `#guard`s for the filling
  search cut and for every UNKNOWN's text. Seeded bugs S7 to S9. The probe fails on `c96de3316` and passes now.
- F2 to F7 (C) stay FOLLOW-UP as the review lists them. DELTA row 1 still waits for the DRI (above).

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
- Fixtures: `tests/test_alternatives_fill.py` (6 test functions, 10 test ids), `FillExamples.lean` `#guard`s (T12, T12b, budget 0, a
  malformed budget, the filling search cut, every UNKNOWN's text); 14 genuine cases in `tests/data/route-cases.jsonl`, 9 in `tests/data/relay-gate-cases.jsonl`.

## Plan rows (ET-7, plan 5; 2.10, 3.4; spec 5 and 6.4)

| Plan row | Delivered | Where |
|---|---|---|
| scenario values under the evidence contract (C) | yes | `settleU`; `test_t12_scenario_push_undecided_pull_not_clear`, `test_t12b_…`; S1–S3 |
| UNKNOWN naming the budget; a Kleene unknown alone is UNKNOWN | yes (`MAX_UNSAID_ATOMS`, for the cone and, since fix 1, for the filling search) | `test_t12b_…` (budget 0); `test_a_scenario_whose_filling_search_…`; `test_the_default_budget_is_named_…`; `#guard`s; `fillingFor_error` |
| no validated filling: UNKNOWN for every alternative (SR-A4) | yes (`MAX_UNSAID_ATOMS` when the budget cut the search, `no filling` only after every assignment was tried) | `test_a_scenario_whose_filling_search_…`; `fillingFor_error` |
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

All 19 were killed, and the file and pin were restored after each. S1–S7 ran on a rebuilt, temporarily pinned
`ve_service`, with `VE_NATIVE_PREBUILT=1`: without it the suite's own build stops first, at the `#guard`s, which also
kill S1–S3. M4 and M6–M9 are killed by proofs. That is the evidence for an S-class statement (checklist 10). M9 first
reordered `AltStatus`'s constructors and survived (order is unobservable); its recorded form drops a constructor.

| Id | Defn | Killed by |
|---|---|---|
| S1 | `statusLabel` (UNDECIDED shown clear) | `test_t12_scenario_push_undecided_pull_not_clear` |
| S2 | `settleU` (Kleene unknown → UNDECIDED, no fillings) | `test_t12b_kleene_unknown_is_settled_by_enumeration_and_unknown_without_budget` |
| S3 | `budgetOf` | the same, and `test_a_scenario_whose_filling_search_the_budget_cuts_is_unknown_naming_the_budget` |
| S4–S6 | `runValidateU`, `chooserReportU`, `statusPhrase` | `test_t12_scenario_push_undecided_pull_not_clear` |
| S7 | `runValidateU` (fix 1: the filling search's reason dropped, the reviewed bug) | `test_a_scenario_whose_filling_search_…`, `test_the_default_budget_is_named_…[13-expected1]` |
| S8 | `fillingFor` (fix 1: the budget cut forgotten) | `fillingFor_error` (the build) |
| S9 | `statusPhrase` (fix 1: the search UNKNOWN without its cause) | `FillExamples.lean` `#guard` (every UNKNOWN's text) |
| M4, M5 | `agreed`, `coneValuesAt` | `agreed_all`; `NormDefaults/Examples.lean` `#guard`s |
| M6–M9 | `SettledF`, `UndecidedF`, `ScenarioRowU`, `AltStatus` | `settledF_of_agreed`, `undecidedF_of_fillings`, `settleU`, the build |
| R1–R3 | `chooser_fill`, `evaluation`, `validate_fill` | `test_route_row_schemas.py::test_genuine_route_answers_are_accepted_by_schema_and_lean` |
| P1 | `tools/layer_policy.py` (Python) | `tools/check_lean_imports.py` (the layer gate) |

## Trust, size, pilot bytes

- Trust: K +0, S +42, V +94 (136 lines, R16's cap 150; fix 1 added `statusPhrase`'s line), per declaration in DELTA row 2; `trust_map.py --check`
  passes; ties row in manage-agents FOLLOW-UPS.md "## et-7b".
- Size: 727 hand-written lines added (Lean 443, of which proofs and `#guard`s about 150; tests 96; side tables and
  pins 41; this report, DELTA and mutants 147), measured with `git diff --numstat` against the merge base, generated
  files, recorded cases and saved evidence excluded. That is above ~600 (the code alone is 580). The scenario half
  could not be split further: its rows, runner, shape and fixtures go together, and the remaining refusals are
  already cut to et-7c.
- Pilot bytes: 0 expected (plan estimate 0). It gives et-8 a status for each Asimov alternative. Nothing is claimed
  before a pilot audit.

## Tests run

Fix 1 (HEAD `38e472161` plus the uncommitted report changes; Lean unchanged since):
- `tests/test_alternatives_fill.py` (37 passed); the selected tests (`mac-pytest.sh --select`, ve-mac-1): 357 units,
  0 failed, none of main-known-red.txt.
- `tools/relay_mutation_gate.py --route service:alternatives`: 14,096 mutants, 0 failures.
- `lake build`; `python3 lean/audit.py` (562 sources, 6,417 theorems); `tools/regen_generated.py --check` (31
  entries); `tools/trust_map.py --check`. The full gate is the chain's, on the final HEAD.

The build:
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
3. Tests can fail: PASS. 19 seeded bugs, [mutants.json](mutants.json).
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
11. Budgets fail closed: PASS. `max_unsaid_atoms` 0 gives UNKNOWN naming `MAX_UNSAID_ATOMS` wherever the budget cut a
    search (fix 1: also the search for a filling); a larger value is capped (`test_t12b_…`); no sleep or deadline.
12. No CPU or memory regression: PASS. Plain sources run today's code. The search runs only under the profile, at
    most 2 × 2^12 validated refillings per alternative, and none beyond the budget (budget 0 skips it).
13. Test-removed trailers: PASS. `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed (no test
    removed; `test_cases_outside_this_item_are_refused_with_the_profile` keeps its name).
