# STOPPED — DRI signature needed for df-3's corrected `DVerdicts` statement

**Status: STOPPED at spec 7.4's `DVerdicts` / `d_rowsHold`; DRI approval of a corrected statement is needed.**
F2's shared Python request binding is fixed in this review round; F1 remains the statement approval stop.
F2's code and regressions are committed as `5a5992a86` on `feature/df-3`; merge base `0df9256dfe7d`.
The Lean fold, route, Python relay, English and fixtures are implemented and committed, but the approved structure is false for its claimed theorem.
The two user-visible rows D1 and D2 are signed by the DRI in `reviews/dri-decisions-20261028-df-3.md`; the statement change is not signed there.
No full gate ran (the user assigns it to the chain). The selected-test VM fallback was interrupted under sustained
runner overload after the Mac was unreachable; it is not counted as a pass.

## Review fix round (2026-10-28)

- F1: the executable statement probe still reports `DIFF DVerdicts` (16 OK, 1 DIFF). The approved structure permits
  arbitrary, empty, or false rows; no sound proof can establish `d_rowsHold` for all of them. DELTA row D3 explicitly
  reserves the item-specific DRI signature. A passing statement regression cannot be added until the DRI approves a
  sound replacement for spec 7.4; the comparator is the executable regression probe.
- F2: `ve/defaults.py::_situation` now binds the complete set of displayed filling tables to the request's
  unspecified regulated predicates, and checks every tuple's arity and declared sorts against the request model.
  `defaults-coherence`, `defaults-model`, and the DF-3 enumerated verdict route share this helper. The review's
  executable probe failed before the fix and passes after it. Regressions:
  `tests/test_defaults_readings.py::test_df_rho_every_forged_collision_field_is_refused` and
  `tests/test_defaults_answer.py::test_situation_filling_tables_and_tuples_are_bound`,
  `::test_situation_entities_of_every_sort`. The two focused files passed: **81 passed**. A seeded Python bug
  replacing the complete-table check with `if False` in a detached worktree made the missing-table assertion fail;
  that worktree was removed.
- Validation: `lake build` completed successfully (689 jobs) and `python3 lean/audit.py` passed (655 sources, 7,309
  theorem declarations) in the selected runner. The cached map selected **433 of 482** test units; the changed
  readings unit passed, and 9 recorded units had passed when the VM run was interrupted. The Mac runner was
  unreachable, and VM load averaged about 134 with 32 CPUs available. The initial VM fallback without a writable
  cached map was also interrupted after it began a fresh 482-unit map recording; neither run is a selected-test pass.
  The three tests listed in `main-known-red.txt` are pre-existing main failures and were not edited here.

## Statement counterexample and required decision

Spec 7.4 defines `DVerdicts` with `y : SDVerdicts` and three *unconstrained* lists: `dConflictRows`, `dQueryRows`,
and `bases`. It then claims `d_rowsHold (z)` for every such `z`. Take a valid `y` for DF-ρ, where the choice
`[(rs1,1),(rs2,1)]` has a checked default collision and its `DefaultCoherent` gate is false. Make a `DVerdicts` with
that `y` but with the choice's `dConflictRows` entry `.free`. This satisfies the stated structure constructor; it
does not satisfy `HoldsG (dSem N) [] .bottom c .free`, because `dSem.free c` requires `DefaultCoherent N c []`.
Even without DF-ρ, an empty `dConflictRows` list is allowed by the approved structure and cannot cover a
nonempty chosen set. Thus `d_rowsHold` is unprovable from the approved fields.

The implementation at `lean/VE/Readings/DefaultVerdicts.lean:134` makes `DVerdicts` carry each choice's checked
strict and default evidence plus a proof that the chosen choices are exactly those rows. The three lists are
computed projections. This supports `d_rowsHold` and all six wire theorems, but changes the approved structure
statement. The statement comparator reports **16 OK, 1 DIFF (`DVerdicts`)** for spec 7.4. A DRI decision must approve
this correction, or specify another sound statement, before this batch can be called delivered. A message through
`manage-agents/msg.sh dri df-3` was attempted but could not be written: the DRI inbox is read only in this sandbox.

## Plan rows and implementation already made

| DF-3 row | Implementation | Evidence / status |
| --- | --- | --- |
| Lean `dSem` using RD-9 `foldG`, no second fold | `DefaultVerdicts.lean:19-53`; `choiceSoft`, `dSem`, `dSem_entails`, gate theorem | Builds and hand mutants L1-L3; **statement stop applies to the replay structure** |
| `DVerdicts`, replay, six wire theorems | `DefaultVerdicts.lean:134-430`, `replayVerdictsD`, `d_rowsHold`, `d_bases_sound`, `readings_wire_default_*` | Proved for the corrected dependent structure; spec 7.4 comparator DIFF above |
| Default member, DE8/DE12 or per-choice DE7 | `DefaultVerdicts.lean:442-505`, `ve/defaults_english.py`, `ve/readings_verdicts/enumerated.py` | DF-ν, DF-ρ, DF-τ and no-default tests in `test_defaults_readings.py` |
| One dispatch, shapes and encoder theorems | `lean/VE/Readings/Run.lean`, `lean/ResponseShape/Schemas/ReadingsRoute.lean`, `Encoders/ReadingsRoute.lean` | Lean build, `verdictsD_fits`; schema emitted by generator |
| Python relay/binding; flag reaches readings documents | `ve/readings_verdicts/{binding,choice,enumerated}.py`, `ve/document/cli.py` | 36 field forgeries, other-question/no-flag and flag refusal tests |
| Fixtures DF-ν, DF-ρ, F-DF2 | `lean/VE/Readings/DefaultVerdictsExamples.lean`, `tests/test_defaults_readings.py` | 69 focused tests pass with `test_defaults_lean.py`; English assertions included |
| Pilot P-2 on CE4 | `evidence/p2-ce4.json` | 3 enumerable sets, 16 choices each: strict SOME, default ALL, default conflict FREE; saved estimate only |
| Pilot translation / P-4 | Not measured | The plan conditions them on enumerable soft translations / UDHR availability; no `Dflt_T` transfer for `readings@1` |

The pilot's CE4 result estimates three additional ALL answers unless an exception applies, with no claim about the
constitution's superposed readings or about future pilot bytes. DF-4 remains the next item: defaults about facts and
English. The saved evidence compares to the baseline at `docs/research/evidence/defeasible/baseline/baseline.json`.

## Delta, trust, size, and seeded bugs

`DELTA.md` has D1 and D2 signed by the DRI and T1 signed by standing ruling R16. Binding checks follow R8.
`tools/trust_map.py --check` passes against the merge base: K +0, S +12, V +126, total +138 within R16's 150-line
cap. The R16 ties request is in `manage-agents/FOLLOW-UPS.md` under `## df-3` (written earlier in this build).
No Rust product code changed. The branch has 15 non-merge commits through `868e9118b` at report preparation.
Before this report and the assurance-pin fix, the hand-written change was approximately 1,780 added/deleted lines
excluding generated inventories and mutation JSON, above the 1,500-line target; the statement stop prevents an
approved size cut from being asserted here.

`mutants.json` and `evidence/mutants.out` record 16 Lean and 6 Python seeded bugs, all with a named failure. In
particular L3 removes the default coherence gate and DF-ρ's collision test fails; L7 shows the member despite a
strict conflict and DF-τ fails; P1 skips a choice's label binding and the forged-label test fails. The Python
missing-choice/dropped-row mutation P2 fails its binding test. L1-L16 cover each new trusted definition under R16.

The saved mechanical `trust_mutants` run is **not passing**. The committed `trust-mutants.json` records 30 KILLED,
381 SURVIVOR, 12 UNKNOWN, 12 INVALID, 0 NOT RUN, from 435 mechanical mutants. It did not execute the Python route
tests; no survivor is mislabeled equivalent and no allow file was invented. This is an additional review blocker.
The prescribed Mac runner was unreachable at the recorded attempt, and the DRI inbox message failed because that
directory is read only. The next fixer must run the mechanical gate to exit 0 after adding Lean-computed checks or
obtaining a ruling on evidence scope; `--rescore` can reuse only verdicts whose recorded inputs remain identical.

## Validation and limits

- `uv run pytest -q tests/test_defaults_readings.py tests/test_defaults_lean.py`: **69 passed** (local VM).
- `uv run pytest -q tests/test_assurance_manifest.py::test_decoder_files_are_pinned_whole tests/test_assurance_manifest.py::test_trusted_decoder_line_ranges_are_pinned`: **2 passed** after repinning the reviewed `Defaults/Wire.lean` file; `tools/assurance_manifest.py --write` regenerated its doc.
- `python3 lean/audit.py`: **PASS**, 655 sources and 7,309 named theorem declarations; standard axiom allowlist only.
- `uv run python tools/trust_map.py --check`: **PASS**, K +0, S +12, V +126.
- `uv run python tools/relay_lint.py`: **PASS**, including 18 readings and norm-defaults modules.
- `uv run python docs/defeasible/df-1ac/evidence/compare_statements.py lean/VE/Readings/DefaultVerdicts.lean 7.4`: **16 OK, 1 DIFF**, as explained above.
- `uv run python tools/regen_generated.py --check`: failed at the assurance pin; the two failing pin tests were repaired and pass. The complete check was not rerun after the statement stop.
- Selected-test runner: the Mac was unreachable; local fallback first hit read-only UV/test-selection/Lean build caches. With those redirected, it selected 433 of 482 units but again did not reach pytest because `manage-agents/gha-tests/gha-tests.log` is read only and the local cutoff tried its default Lean build cache. No selected-run pass is claimed.
- Full release gate, `gate_collection.py --check`, head-to-head base comparison, and `trust_mutants` exit-0 run: **not completed**. The user explicitly reserves the full gate for the chain on the final approved HEAD.

## Self-review against BUILDER-CHECKLIST

1. PASS — `test_defaults_readings.py`'s genuine-answer and 36 forged-field cases; response shape `verdictsD_fits`.
2. N.A. — delivery is stopped by the false approved `DVerdicts` statement; the plan-row table above names the stop.
3. PASS — `mutants.json` / `evidence/mutants.out` show 22 hand mutants fail; the mechanical run remains an open blocker.
4. PASS — `test_without_the_request_asking_there_is_no_member` and `test_the_flag_elsewhere_is_rd9s_answer` preserve the unrequested RD-9 answer.
5. PASS — `test_df_nu_every_forged_field_is_refused` and `test_df_rho_every_forged_collision_field_is_refused` cover request binding.
6. N.A. — the user assigns the full gate to the chain, and this branch stopped at spec 7.4.
7. N.A. — the DRI must decide the corrected statement; D1/D2 are already signed in `DELTA.md`.
8. PASS — `DELTA.md` records D1/D2; no-flag identity and flag refusal tests delimit the delta.
9. PASS — `tools/select_tests.py --base $(git merge-base HEAD main)` selected 433/482 units; selected execution is not claimed.
10. N.A. — the spec 7.4 comparison is 16 OK / 1 DIFF; the counterexample above requires a decision.
11. PASS — `tests/test_defaults_lean.py::test_an_empty_budget_is_unknown` and DF-3 refusal tests.
12. N.A. — no comparative performance run before the statement stop; P-2 records counts, not timings.
13. N.A. — no test was removed or renamed; `git diff main...HEAD -- tests` adds tests and edits existing assertions.

## FIXMAP

`lean/VE/Readings/DefaultVerdicts.lean` — `dSem`:29, `DVerdicts`:134, `d_rowsHold`:219, `d_bases_sound`:231, `replayVerdictsD`:367, wire theorems:372-430, JSON/English:442-505; spec 3.5/7.4.
`lean/VE/Readings/DefaultVerdictsExamples.lean` — computed DF-ν, DF-ρ and F-DF2 guards.
`lean/VE/Readings/Run.lean` — verdict-kind dispatch to `runVerdictsD`.
`lean/VE/Defaults/Wire.lean` — shared `viewOn` and `collisionFields` used by default replay.
`lean/VE.lean` — imports the new readings modules.
`lean/VE/Audit.lean` — audit declarations for DF-3 theorems.
`lean/ResponseShape/Schemas/ReadingsRoute.lean` — typed default-member shape.
`lean/ResponseShape/Encoders/ReadingsRoute.lean` — default JSON and answer-fit theorems.
`lean/ResponseShape/Encoders/NormDefaults.lean` — shared collision encoder adjustment.
`lean/ResponseShape/Audit.lean` — shape audit additions.
`ve/readings_verdicts/binding.py` — `_check_default` request binding.
`ve/readings_verdicts/choice.py` — per-choice default evidence generation.
`ve/readings_verdicts/enumerated.py` — default request, answer and English relay.
`ve/defaults_english.py` — DE8/DE12/DE7 reading renderer.
`ve/document/cli.py` — flag reaches enumerable readings documents.
`tests/test_defaults_readings.py` — DF-ν/ρ/τ, no-default, English and fuzz cases.
`tests/test_defaults_lean.py` — retained refusal and budget boundaries.
`ve/assurance-manifest.json` — reviewed full-file pin for `Defaults/Wire.lean`.
`docs/spec/assurance-manifest.md` — generated from the manifest (`uv run python tools/assurance_manifest.py --write`).
`ve/backends/lean_service_schema/readings-route.json` — generated typed response schema.
`tools/trust-classes.json` — DF-3 declaration classifications.
`docs/trust-baseline.json` — R16 allowance.
`docs/test-architecture/binding-census.json` — generated binding census.
`docs/test-architecture/binding-census.md` — generated census document.
`lean/axioms.txt` — generated axiom inventory.
`lean/declarations.txt` — generated declaration inventory.
`lean/predicates.txt` — generated predicate inventory.
`lean/statements.txt` — generated statement inventory.
`lean/checkers.lock` — generated checker pins.
`docs/defeasible/df-3/DELTA.md` — signed deltas D1/D2 and R16 T1.
`docs/defeasible/df-3/mutants.json` — hand mutation plan (16 Lean, 6 Python).
`docs/defeasible/df-3/evidence/run_mutants.py` — hand mutation runner.
`docs/defeasible/df-3/evidence/mutants.out` — hand mutation failures.
`docs/defeasible/df-3/evidence/p2-ce4.json` — CE4 pilot counts.
`docs/defeasible/df-3/trust-mutants.json` — mechanical run that still fails.
`docs/defeasible/df-3/REPORT.md` — this statement stop and handoff.
Regressions: `uv run pytest -q tests/test_defaults_readings.py tests/test_defaults_lean.py`; `uv run pytest -q tests/test_assurance_manifest.py::test_decoder_files_are_pinned_whole tests/test_assurance_manifest.py::test_trusted_decoder_line_ranges_are_pinned`.
Generated inputs: `uv run python tools/regen_generated.py --write`; manifest document: `uv run python tools/assurance_manifest.py --write`.
Mechanical mutants: `zsh /home/seyran/code/manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --json docs/defeasible/df-3/trust-mutants.json` (existing JSON is failing, not an exit-0 certificate).
## END FIXMAP
