# et-7 build report: `alternatives@0` with the completion (events-time-causation ET-7, first part)

No DRI signature is reserved: every DELTA row cites a standing ruling or the DRI's decision file
([DELTA.md](DELTA.md)). Branch `feature/et-7`, synced with main `c2b1a7d4`. Next item: **et-7b** (the rest of
ET-7, below), then et-8 (the Asimov and ET-1 pilot on the completion).

## What was built

ET-7 is larger than one merge-sized item, so this item delivers its first coherent part, the document-level
answers, and names the per-alternative scenario values as et-7b (the size rule of the feature feed):

- `lean/VE/Alternatives/FillWire.lean` (new): `AltSourceU`, `decodeAltSourceU` with `decodeSourceU`'s two
  branches (SR-A2) and `decodeAltSourceU_conservative`; `AltConflictFreeU` over `BaseAdmissibleAltU`, the slot
  premises included (SR-A3), with `alt_conflict_freeU` and `alternativesU_wire_conflict_sound`;
  `alternativesU_wire_followable_sound` (FOLLOWABLE from a certificate over `backgroundBaseAltU A unspec ++ A.Γ`);
  `alternativesU_dilemma_witness_sound` exactly as spec 6.4 states it (with `hA : WellFormedAlt A`, SR-A1) and its
  wire form `alternativesU_wire_dilemma_sound`; packages bound to the complete environment and to `E‴_base`; the
  untrusted diagnosis `diagnoseU`: `UNSETTLED(<alternatives>)` before every branch but "no alternatives", listing an
  alternative only when a validated refilling of the cone of `clear°(r, a)` makes it clear (with the witness's
  validated filling, at which none is clear, two validated fillings that answer both ways), else today's procedure
  on the filled outcomes (`diagnoseIn (fill …)`).
- `lean/VE/Alternatives/Run.lean`: lists with `norm-defaults@0` go to `runCaseU` (`alt-elaborate`,
  `alt-environment`, `alt-conflict` with packages, `alt-followable`); other kinds are refused by name (et-7b);
  `admission` keeps today's path. `Validate.lean`'s diagnosis reads the outcomes of a given tree (`diagnoseIn`,
  `permittedIn`, `requiredIn`, `dutiesIn`; the old names are their wrappers); `Wire.regeneratedOn` and
  `Replay.decodePackageAt` are the shared bodies of `regenerated` and `decodePackage`.
- The refusal deleted (2.11): `lean/VE/Compose/Dispatch.lean` (with its proof: `TodayList`, `todayGate_sound`,
  `todayGate_complete`, `today_alternatives`, `today_risk`), `ve/profiles.py` (the mirror row), the route's own
  `Unsupported profile norm-defaults@0` (the route and the environment mode now decode with `decodeAltSourceU` under
  the profile). AR-10 has not landed, so the deletion is in `Dispatch.lean` (SYNTHESIS 4.2: AR-10 rebases).
- Response shape: `alternatives.json#/$defs/elaborate` gains the five fill fields, required exactly on the
  completion path (`fill_path`, decided by `NormDefaults.Wire.hasProfile`, `CaseDecider.altFillPath`); the other
  rows keep their shapes. The encoder theorem `ResponseShape.Encoders.Alternatives.runCaseReported_fits` stays the
  owner of the wire (R8), now through `runCaseU_fits`, `elaborateU_case_fits`, `conflictU_fits`,
  `followableU_fits`.
- Python: `ve.entailment.prove_alternatives_entailment`, the untrusted `alt-certificate` producer (PH6.4): it
  searches the list Lean binds (Background, slot premises, layer premises, then the case's premises) and Lean binds
  and replays it. `ve/alternatives.py` is unchanged: it relays rows as they are, and Lean writes every text.
- Fixtures: `tests/test_alternatives_fill.py`, `lean/VE/Alternatives/FillExamples.lean`,
  `tests/data/et7/et1-component.json` (ET-1's component, copied from the phase-1 evidence); 19 genuine cases in
  `tests/data/route-cases.jsonl`, 9 in `tests/data/relay-gate-cases.jsonl`.

## Plan rows (ET-7, plan 5; 2.10, 2.11, 3.4; fixtures)

| Plan row or directive | Delivered | Where (commit; test) |
|---|---|---|
| `lean/VE/Alternatives/FillWire.lean`: 3.4 as the spec states it | yes, except the scenario statements (`SettledF`, `UndecidedF`, `AltStatus`, `ScenarioRowU`), which are et-7b | 3b9fbbfe6; `lake build`, `python3 lean/audit.py` (Audit lists the five theorems) |
| the alternatives runner dispatches lists with `norm-defaults@0` to it | yes | 3b9fbbfe6; `tests/test_alternatives_fill.py` |
| the scenario's values under the evidence contract (clear / not clear when settled, UNDECIDED from two validated fillings, UNKNOWN otherwise) | **no: et-7b**. With the profile, `alt-validate` is refused by name, so no scenario value is shown without its evidence | `test_cases_outside_this_item_are_refused_with_the_profile` |
| `UNSETTLED` in the untrusted diagnosis, for alternatives with UNDECIDED evidence only | yes (for DILEMMA witnesses) | `test_t12_dilemma_with_unsettled_push`, `test_nd_u11_alternatives_part_every_alternative_unsettled`, `test_settled_dilemma_keeps_todays_classification_on_the_filled_outcomes`; M2, M3 |
| delete the two refusals (2.11), the one in `Dispatch.lean` serialised with AR-10 | yes (AR-10 not landed: deleted in `Dispatch.lean` with its proof) | 82f79351f; `tests/test_compose_dispatch.py`, `test_completion_environment_is_accepted_and_bound`; P2 |
| Python: relay and display the values | yes for the answers of this part: the route's rows are relayed unchanged and every text is Lean's; no Python display code was needed | `tests/test_route_row_schemas.py`, `tools/relay_mutation_gate.py --route service:alternatives` |
| the test asserting the refusals rewritten | yes: `tests/test_asimov_laws.py::test_permission_default_stays_allow_until_norm_defaults_combines_with_alternatives` (name kept: lean-first b5's saved evidence cites it) asserts the branch; `tests/test_asimov_extended.py` asserts the alternatives-only branch and risk's refusal; `tests/test_norm_defaults.py`, `tests/test_compose_dispatch.py` | e1aa3241c, 93ea1ee2d |
| a producer for `alt-certificate` (PH6.4), fixture ET-1's u0171.s03 certificate produced | yes | `test_alt_certificate_producer_on_the_et1_component`; P1 |
| T12 | yes | `test_t12_dilemma_with_unsettled_push`, `test_t12_followable_with_the_push_permission` |
| T12b | **no: et-7b** (Kleene unknown and enumeration are scenario values) | |
| T12c | yes: the decoder types Γ over the base vocabulary, so a premise naming `unsaid__permitted` is `InvalidInput: ill-typed premise g`; the statement keeps `hA` | `FillExamples.lean` `#guard` |
| T12d | yes, every branch with its text, except the `WellFormedU` failure: after `checkAuthor` and today's decoder no input reaches it (they check each of its conditions), so its text has no fixture | `FillExamples.lean` `#guard`s |
| T12e | yes | `test_t12e_conflict_free_needs_the_slot_premises`; M4 |
| T12f | witness half yes (a DILEMMA witness with push available to two agents gets today's validation text; a chooser of the action sort gets `InvalidInput: push is not in the agent domain`); scenario half **et-7b** | `test_t12f_an_invalid_witness_is_never_a_dilemma` |
| nd fixture u11's alternatives part | yes (k9: no rules, `permitted` unspecified, none clear, each UNDECIDED: `UNSETTLED(a, b, c)`) | `test_nd_u11_alternatives_part_every_alternative_unsettled` |
| seeded bugs: FOLLOWABLE without `fillPremises`; an UNDECIDED alternative rendered clear; UNDECIDED without two validated fillings; the producer's premise order | yes (M1, M2, M3, P1; the last two are on the UNSETTLED diagnosis, the scenario being et-7b) | [mutants.json](mutants.json) |
| Shared files: `Run.lean`, `Dispatch.lean`, `ve/profiles.py`, `ve/alternatives.py`, `ve/entailment.py`, `Audit.lean`, the response shape and its encoder theorem | all but `ve/alternatives.py` (no change needed) | |
| Generated: `alternatives.json`, gate collection, `checkers.lock` | regenerated with `tools/regen_generated.py --write` (the gate collection is no longer a committed file) | 84e3a6939, a84ddb2c1, 452128d59 |
| SYNTHESIS 2.8 and 4.2 | 4.2 followed (deleted in `Dispatch.lean`, AR-10 rebases); 2.8 concerns events@0 (no change here) | |
| DRI-DECISIONS-PHASE2 ET1-ET4 | none bears on ET-7 (premise-scale, the lint row kind, month and year offsets, ET-0's rerun) | |
| Overlap with lf-18 (`ve/alternatives.py`, `Decl.lean`) | neither file is touched; lf-18 had not merged at the sync | |

## Deviations from the spec's blocks

- Spec 6.4's wire theorems read the base units from `j.getObjValD "premises"`; the route's case field for them is
  `units` (`Replay.sourceOf`), so the theorems read `units`.
- `FollowableUReplay.followable`, `AltConflictReplayU.conflictFree` and `DilemmaDataU.dilemma` include
  `WellFormedU` (true on every source the profile decodes): the decoder's branch without the profile does not give
  it, and the theorems conclude it.
- On the wire, cases without `norm-defaults@0` keep today's runner and the environment mode keeps today's decoder,
  so an `unspecified` default without the profile keeps today's text
  (`InvalidInput: invalid regulated role or default for permitted`); the decoder's own no-profile text
  (`UnsupportedProfile: unspecified completion requires norm-defaults@0`, SR-A2) is checked at the decoder
  (`FillExamples.lean`). Sending those cases to the new decoder would have dropped the quoted predicate name (R1).
- Spec 5's UNSETTLED is "listing only alternatives with UNDECIDED evidence": here the evidence is the witness's
  validated filling (not clear) and a validated refilling of the cone of `clear°(r, a)` (clear), searched by Lean
  within `MAX_UNSAID_ATOMS`; nothing is claimed for it (G[R]).
- Statement gate: the statement review of ET-2's spec converged (FIX, round 3), its corrections are in draft 2
  (re-check PASS, `events-time-causation-p3ver1.final.md`), and the phase-2 check accepted the plan. The
  separate stub elaboration the spec names was not run (the stub is not in any worktree); `FillWire.lean` elaborates
  and proves the ET-7 statements it delivers, as stated except the two points above.

## Seeded bugs ([mutants.json](mutants.json))

Each was applied, the service rebuilt and pinned for the Lean ones, the named test run, and the file and pin
restored (`/tmp` runner; 52 min for the five Lean ones).

| Id | Language | File | Behaviour | Failing test |
|---|---|---|---|---|
| M1 | Lean | `lean/VE/Alternatives/FillWire.lean` | FOLLOWABLE's package bound without `Fill_T` | `test_t12_followable_with_the_push_permission` (UNKNOWN for FOLLOWABLE) |
| M2 | Lean | `lean/VE/Alternatives/FillWire.lean` | an UNDECIDED alternative rendered clear | `test_t12_dilemma_with_unsettled_push` (`clear: push`) |
| M3 | Lean | `lean/VE/Alternatives/FillWire.lean` | UNSETTLED without the second validated filling | `test_t12_dilemma_with_unsettled_push` (`UNSETTLED(push, pull)`) |
| M4 | Lean | `lean/VE/Alternatives/FillWire.lean` | conflict packages without the slot premises | `test_t12e_conflict_free_needs_the_slot_premises` (UNKNOWN for CONFLICT-FREE) |
| M5 | Lean | `lean/VE/Alternatives/FillWire.lean` | the decoder loses the unspecified predicates | `test_completion_environment_is_accepted_and_bound` (`[] == ['permitted']`) |
| P1 | Python | `ve/entailment.py` | the producer binds layer premises before slot premises | `test_alt_certificate_producer_on_the_et1_component` (Lean: stale certificate) |
| P2 | Python | `ve/profiles.py` | the deleted Python refusal restored | `tests/test_norm_defaults.py::test_unspecified_requires_the_profile_and_other_values_stay_invalid` |

Proof probes (checklist 10, copies compiled outside the tree): the FOLLOWABLE check over `backgroundBaseAlt`
(no `Fill_T`) breaks `alternativesU_wire_followable_sound`; DILEMMA on the unfilled `notFollowableF` breaks
`alternativesU_wire_dilemma_sound`.

## Trust

K +0, S +18, V +121 (139 lines, under R16's 150), per file and declaration in DELTA row 5, recorded with
`trust_map.py --allow` (signed by R16); `trust_map.py --check` passes. The ties pass row is in manage-agents
FOLLOW-UPS.md, "## et-7".

## Size

Hand-written changes outside generated files, copied documents and recorded fixtures: Lean 712 lines (FillWire
361, of which about 160 are proofs; the encoder theorems 93; Run 73; FillExamples 57; Validate 33; the shape 31;
Dispatch 22; Wire 17; Replay 13; Standalone 7; CaseDeciders 5), Python 30, tests 308. That is above the feed's
~600: the cut already moves the scenario values (the larger half of 6.4) to et-7b; what remains is one coherent
set (decoder, three verdicts with their theorems and their encoder proofs), and splitting the encoder theorems from
the rows they cover is not possible. `lean/VE/Compose/Examples.lean`'s 481 changed lines are its literal tables,
recomputed from the test's own functions.

## Pilot bytes

0 bytes expected from this item (plan estimate 0): it removes the Asimov case's modeling choice once et-8 switches
`permitted` to `unspecified` and runs on the completion. Nothing is claimed before a pilot audit.

## Tests run

- While iterating: `tests/test_alternatives_fill.py` (9 passed), and the affected files
  (`test_route_row_schemas`, `test_lean_service_schema`, `test_alternatives_three_way`, `test_asimov_laws`,
  `test_norm_defaults`, `test_compose_dispatch`, `test_profiles`, `test_environment_field_types`,
  `test_risk_fixtures`, `test_lean_handles`, `test_assurance_manifest`, `test_consolidation_tools`).
- The selected tests (`mac-pytest.sh --select`, ve-mac-1, HEAD 5b8cf450, 362 units): 3 failures, all from this
  branch and fixed in e1aa3241c, each rerun: `test_asimov_extended.py::…_with_risk_and_alternatives` (asserted the
  alternatives-only refusal), `test_lean_first_b5_delta.py::test_direct_entry_changes_are_recorded_with_dri_disposition`
  (b5's saved evidence names the Asimov test, so its name is kept), `test_consolidation_tools.py::test_committed_ledger_names_real_declarations`
  (plan rows 7 and 8b re-measured). No test of main-known-red.txt was hit.
- `tools/relay_mutation_gate.py --route service:alternatives`: 11,972 mutants, 0 failures. The new fixtures are the
  first with non-empty fill tables, rule lists and labels, so their mutants were filed under the route's existing
  allow classes, as the norm-defaults route files the same fields: B0 (empty or repeated `fill`, `inlined`,
  `reached`, `unsaid`, `unspecified`), F4 (rebinds of `conditional_on/*`, `inlined/*/norm/{name,predicate,over/*}`,
  `reached/*/{predicate,sorts/*}`, `unsaid/*/sorts/*`, `unspecified/*`), F10 (the `sorts` and `over` lists), F11
  (an empty rule name).
- `tools/regen_generated.py --check`, `tools/gate_collection.py --check --prebuilt` (0 refused, 0 stale),
  `tools/trust_map.py --check`, `tools/lean_statements.py --check`. The full gate is the chain's, on the final HEAD.
- Commit 93ea1ee2d's message has a `Test-removed:` line outside its trailer block; the test it names is collected
  again (its name was restored), and the collection check reads no trailer from it.

## et-7b (next item)

The scenario statements and rows of spec 6.4 (`SettledF`, `UndecidedF`, `AltStatus`, `ScenarioRowU` with its
validity, validated filling and soundness fields, `scenarioRowU`: Kleene by `kleene_sound`, enumeration of the
cone as `settled_of_enumeration`, two validated fillings as `undecided_witness_sound`, UNKNOWN naming the budget),
generalised in `NormDefaults/Evidence.lean` only (SYNTHESIS O18), `alt-validate` with the completion, T12b and
T12f's scenario half; then `alt-certificate`, `admission` and CONFLICT witnesses under the profile (refused by
name here).

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: PASS. `tools/relay_mutation_gate.py --route service:alternatives` (drop, empty,
   duplicate, retype incl. 10k-deep, rebind; 0 failures); `tests/test_route_row_schemas.py::test_route_answer_mutations_agree_with_lean`
   (found and fixed the `fill_path` disagreement on a non-string profile, a84ddb2c1).
2. Every deliverable built: PASS for this part, with the rest named et-7b under the feed's size rule (the plan-row
   table above); no Python copy of a Lean decision (the producer is an untrusted search; the Python gate row is
   deleted), no new report test, no in-flight file touched (lf-18's `ve/alternatives.py`, `Decl.lean`).
3. Tests can fail: PASS. Seeded bugs M1-M5 (Lean, each caught by a pytest test, not a build step) and P1-P2
   (Python), [mutants.json](mutants.json).
4. Py/Lean/Rust agree, valid inputs pass: PASS. Plain sources answer as before (`decodeAltSourceU_conservative`;
   `tests/test_alternatives_three_way.py`, `tests/test_asimov_laws.py` pass); the Python gate and Lean's agree on all
   65,536 lists (`tests/test_compose_dispatch.py::test_lean_literals`); no Rust change.
5. R8 binding: PASS for the fields Python relays: DILEMMA's `chooser` is `.equals /witness/chooser`, ids are echoed
   (relay gate rebind mutants refused); the fill fields are bound as the norm-defaults route binds them (F4/F10
   follow-ups, listed above); undeclared filling tables and wrong-sort choosers are refused
   (`test_t12f_an_invalid_witness_is_never_a_dilemma`).
6. Gate evidence matches HEAD: PASS. Synced with main c2b1a7d4 (452128d59); the chain runs the gate on the final HEAD.
7. No unsigned item: PASS. DELTA rows cite R1, R16 or the DRI's SYNTHESIS.md; no signature reserved.
8. Every user-visible change in DELTA: PASS. [evidence/delta.json](evidence/delta.json) lists each changed record,
   base and head; `admission` with the profile is listed unchanged.
9. Test selection: PASS. `tools/select_tests.py --base $(git merge-base HEAD main)` selects 362 units including
   `tests/test_alternatives_fill.py` and the three tests that failed (it caught them).
10. Lean statements say what is claimed: PASS. The two proof probes above break the build; the dilemma theorem is
    about `w.sc.M.withFill w.F`, the filling the row's `dilemma` checks.
11. Budgets fail closed: PASS. UNSETTLED is not claimed beyond `MAX_UNSAID_ATOMS` (a larger cone lists nothing:
    `unsettledAt`'s `C.length ≤ MAX_UNSAID_ATOMS`); no new deadline or rlimit; no sleep in the tests
    (`tests/test_hang_guards.py` passes in the selected run).
12. No CPU or memory regression: PASS. Plain sources run today's code unchanged; the new search runs only on
    completion witnesses and is bounded by 2^12 refillings per alternative.
13. Test-removed trailers: PASS. `tools/gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed
    (no test removed: the renamed test's name was restored).

## Review fix (manage-agents et-7-review.final.md, 2026-10-18)

Both B findings are fixed as classes; no A finding was raised; C findings F3 to F9 are not addressed here
(F7: the new DELTA rows' records are in [evidence/delta.json](evidence/delta.json); no permanent test reads it,
D4). No DRI signature is reserved: rows 4 to 6 cite R1, R2 and R16.

| Finding | Class removed | Fix | Regression tests | Commits |
|---|---|---|---|---|
| F1 (B) document path fell through to the norm-defaults route's field check | every reader that does not read the completion beside a composed block now refuses the pair by name with one Lean text, `VE.Compose.pendingWithDefaults` (DELTA row 6): the `document` mode (after the environment mode's own fault, never `CheckerUnavailable`), the norm-defaults mode (`NormDefaults.Run.runGated`, every kind, `runGated_fits`), and the alternatives decoder without the completion (`Alternatives.Wire.decodeAltSource`), which the English reader's boundary (`ve ask`, which had also lost `alternatives@0`) and the route's `admission` call | Lean only; Python relays as before | `tests/test_alternatives_fill.py`: `test_completion_documents_are_refused_by_name_on_every_entry_point` (PROBE F1 and its twins), `test_completion_cli_commands_print_the_named_refusal`, `test_the_document_mode_refuses_the_pair_after_the_environment_modes_faults`, `test_the_norm_defaults_route_refuses_a_composed_block_by_name`, `test_cases_outside_this_item_are_refused_with_the_profile`; `#guard`s in `Compose/Examples.lean`, `Alternatives/FillExamples.lean` | 4c9f941bc, 2e80a1300, adaf64688 |
| F2 (B) `FillExamples.lean` never compiled | a Lean module outside the default build: `tools/check_lean_imports.py` (the layer gate) reports any module outside the import closure of the lakefile's default targets, read with the reader checked against Lean's header parser; exceptions are only non-default executables' roots and `RUN_ONLY` scripts named with their runner. The six it found are built now: `VE.Alternatives.FillExamples`, `VE.NormDefaults.Examples` (the review's follow-up), `VE.Core.Checks`, `VE.TableauChecks` (from `VE.lean`), `VE.WireContract.Limits` and `.Names` (from `VE.WireContract.Diagnose`, as spec 7.3 keeps them internal) | | `tests/test_lean_default_build.py` (PROBE F2, the real tree, synthetic orphans, Lake globs, stale `RUN_ONLY`) | 85c4355b2, 7e55d4e42 |

Row 6's base texts were probed on main `c7fc6acac`'s built service (every entry point answered
`UnsupportedProfile: Unsupported profile norm-defaults@0`; the norm-defaults mode its field check). The probes:
PROBE F1 failed before the fix (`fields do not match: ...`) and passes after (`UnsupportedProfile: alternatives@0
with norm-defaults@0 is not implemented`); PROBE F2 failed before and passes after.

Trust: K +0, S +18, V +128 (146 lines, R16's cap 150): the fix adds V 7 (`runGated` 6, `decodeAltSource` 1), recorded
as its own allowance; `pendingWithDefaults` is G[R]. FOLLOW-UPS.md "## et-7" has the ties row for these lines.

Seeded bugs ([mutants.json](mutants.json); each Lean one on a rebuilt, temporarily pinned `ve_service`, file and pin
restored; run before the comment-only trims of adaf64688, same code):

| Id | Language | File | Behaviour | Killed by |
|---|---|---|---|---|
| M6 | Lean | `lean/VE/Service/Document.lean` | the document mode answers `CheckerUnavailable` again | `test_the_document_mode_refuses_the_pair_after_the_environment_modes_faults` |
| M7 | Lean | `lean/VE/NormDefaults/Run.lean` | the gate bypassed | the build: `runGated_fits` no longer proves |
| M7b | Lean | `lean/VE/NormDefaults/Run.lean` | the gate reads another field (proofs still hold) | `test_the_norm_defaults_route_refuses_a_composed_block_by_name`, `test_completion_cli_commands_print_the_named_refusal` |
| M8 | Lean | `lean/VE/Alternatives/Wire.lean` | the decoder's refusal deleted | `test_cases_outside_this_item_are_refused_with_the_profile`, `test_completion_documents_are_refused_by_name_on_every_entry_point[ask (the English reading)]` |
| M9 | Lean | `lean/VE/Alternatives/FillExamples.lean` | a wrong `#guard` | `lake build` (FillExamples is now in the default build) |
| P3 | Python | `tools/check_lean_imports.py` | imports not followed | `test_every_lean_source_is_built_by_the_default_build` |

Checks: `lake build` and `python3 lean/audit.py` pass (540 sources, 6,281 theorems); `tools/regen_generated.py
--check` passes (31 entries); `tools/trust_map.py --check` passes; `review-ready.py --delta-dri-needed`: no row.
