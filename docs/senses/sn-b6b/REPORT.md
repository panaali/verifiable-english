# sn-b6b REPORT (senses B6 carry-overs)

Status: review round 1 fixed (F1-F3 B, F8 C); selected tests pass on `e990750c4` (429 units, 0 failed); trust
mutants 0 survivors. No DRI signature is reserved. HEAD: the commit that adds this report's last edit. Changed in the fix: the projected
environment's members come from one Lean table and are each bound to the request (F1, F2; both routes); a
distinguishing flip row writes its model in the existing model wire form (F3). Open: the senses lock and the D17
hook rule (**sn-b6bb**); review C notes F4, F6 (FOLLOW-UPS). Hand-written lines: see Size.

## Plan rows (senses-PLAN.md B6 :836, :877-881, 6.8 i3-i5 :1069-1075) and the task's deliverables

Plan edit 1 (edits-senses.md, D7: senses runs as `ve_senses_route`, no profile) is the one this item builds under:
`senses.read` stays on `ve_senses_route`, so its new members are typed by the relay (Deviation 1).

| Deliverable | Delivered | Where | Test |
|---|---|---|---|
| (1) (a) preamble lines of the `senses.read` source answer, written by Lean, bound by the relay | yes: `preamble`, the source's sentences before the body as written (`lexSpans` slices); on a source request only (a fence request maps its lines in `fences`) | `lean/VE/Senses/Run.lean` `writtenLines`, `admittedIds`; `ve/backends/senses.py` `_preamble_problem` | `tests/test_senses_route.py::test_the_preamble_lines_are_the_sources_leading_sentences`, `::test_preamble_rebinding_is_refused` (8), `::test_a_preamble_line_lean_did_not_read_is_unavailable`; `#guard`s in `RunExamples.lean` |
| (2) (d) flip models as the plan defines them (2.6 step 7; spec 2.6; plan 4.2 "the existing model wire form"), in Lean, `#guard`s on both sides | yes: one row per pair of each open unit (`distinguished` with the senses made true, both values and the model in the existing model wire form, `undistinguished`, or `unknown` for a form outside the evaluator, an exhausted budget or a model over `maxTuples`); the model is a table (`FlipModel`) whose relations the evaluator reads (`VE.Route.Budget.evalF` under one `maxEvaluations` budget for the whole answer), so its values are the formulas' truth in it (`flipValues_sound`) | `lean/VE/Senses/Flip.lean`; `Run.lean` `flipJson`, `flipModelJson`; relay `_flips_problem`, `_model_problem` | `RunExamples.lean` flip guards (first valuation, exchanged only (s2's unit 0) with its whole model, neither, outside, exhausted, the exact budget boundary, the tuple limit on both sides and at exactly `maxTuples`); `tests/test_senses_route.py::test_flip_models_are_leans` (7), `::test_a_flip_model_is_a_model_of_the_projection_that_separates_the_pair` (4), `::test_flip_rebinding_is_refused` (27) |
| (3) typed projected environment; OPEN_ALLOWED and F7 removed; the relay keeps binding `environment_id` and the lexicon's | yes: every copied member from one table of the members each profile adds (`profileMembers`, a guard per profile of `VE.Compose.profileTable`), each equal to the request's and present when it is; `senses.read` checks its reading's environment with the same generated shape (`check_projected_environment`) | `lean/ResponseShape/Schemas/SensesProject.lean` (`environment`, `sort`, `profileMembers`, `copiedAt`); `ve/backends/service_schema.py`; `tests/test_route_row_schemas.py`; `tools/relay-gate-allow.json` | `tests/test_senses_project.py::test_every_member_a_request_environment_carries_is_copied_and_bound` (11 families), `::test_a_forged_profile_list_with_recomputed_identities_is_refused`, `::test_a_readings_environment_is_bound_to_the_request` (6), `::test_projection_answer_mutations_are_rejected`, `::test_the_typed_environment_is_bound_to_the_request`, `tests/test_route_row_schemas.py::test_no_answer_object_is_left_open` |
| (4) i3 as built (decision 20261031 item 1) | yes: senses-PLAN 6.8's i3 row updated verbatim; no code change | `docs/spec/senses-PLAN.md` | `tests/test_senses_route.py::test_own_senses_need_no_pack` (both cases, `[]-none` included) |
| (4) i4 `review_status` of a pack whose bytes differ | yes, displayed by `ve senses check` and `ve senses project` from `ve.senses.review_status` with Lean's `dictionary_id` (one-pack requests) | `ve/senses/__init__.py` `pack_review`; `ve/__main__.py` | `tests/test_senses_project.py::test_i4_a_changed_pack_is_unreviewed_and_reads_the_same` |
| (4) i5 service killed mid-request | yes: `ve_service` killed on each attempt is `CheckerUnavailable` after its one retry; the one-shot runner killed mid-answer too | existing pool and runner | `tests/test_senses_project.py::test_i5_a_service_killed_mid_request_is_unavailable` |
| (5) `ve senses project` relaying Lean's answer verbatim | yes (exit 0 projection, 3 Lean's fault, 2 Lean's refusal text, 5 unavailable) | `ve/__main__.py` | `tests/test_senses_project.py::test_senses_project_cli_relays_leans_answer` |
| (6) `ve/senses/LOCK.json`, the lock check, the D17 hook rule | **no: cut to sn-b6bb** (task's cut order: lock and hook first) | | |
| optional R3 advice field for i3 | no (optional; Lean writes none) | | |
| evaluated once against a stated limit, with a large request fixture | yes: every flip evaluation of an answer charges one `maxEvaluations` (1,000,000) budget; the fixture at exactly the limit answers, one unit earlier spent is `unknown`, and a deeper one ends `unknown` | `Flip.lean` `flipsOf` | `RunExamples.lean` (`atLimit`, `deep 21`) |

## Deviations

1. **The new `senses.read` members are typed and bound by the relay's validator, not a response shape.**
   `senses.read` is not a `ve_service` mode (plan edit 1), so it has no schema file. SIGNED by the DRI:
   reviews/dri-decisions-20261102-sn-b6b.md item 1 (conditions (a)-(f) met: no open member; the two bindings;
   no Python recomputation; `tools/relay_mutation_gate.py --route ve_senses_route::senses.read` 0 failures and
   the fuzz tests in tests/test_senses_route.py; seeded bug S1; Lean `#guard`s on both sides). Follow-up
   `sn-read-shape` was filed by the DRI.
2. **Withdrawn in review round 1 (F3): a distinguishing row writes the model in the existing model wire form**
   (`model`: every sort of the projected environment with its entities, every constant with its entity, every
   predicate with its tuples), beside the senses it makes true and the two values. One entity per sort (named by
   the sort, which no constant's name is) and one per constant the pair names (spec 2.6); another constant is its
   sort's entity. Spec 2.6's order is followed where it and plan 2.6 differ: the exchanged valuation, not the
   complement. An ill-sorted atom is false in the model (typed candidates have none).
3. **The typed environment is `copied` content** (`Shape.copied`): the client validates it in full; the encoder
   theorem `projectCaseReported_fits` keeps its statement (a request-derived environment cannot be proved closed).
   Every member but the sorts and predicates is bound to the request's by equality. The sorts' and predicates'
   entries are typed, and bound only through the identities, which an answer can recompute: review C note F4,
   in FOLLOW-UPS.
4. `review_status` is given for a one-pack request: Lean's `dictionary_id` of several packs names them together,
   and no pin names a combination (plan 2.7 pins a pack alone).

## Review fixes (round 1: sn-b6b-review.final.md)

| Finding | Class removed | Fix | Regression tests |
|---|---|---|---|
| F1 (B) the typed environment refused genuine answers (`acts`, `reports`, `speech_acts`) | a closed schema hand-listing the members of request-derived content | one Lean table of the members each profile adds (`profileMembers`), a guard that every profile of `VE.Compose.profileTable` has a row, the schema generated from it; `senses.read` checks its reading's environment with the same generated shape | `tests/test_senses_project.py::test_every_member_a_request_environment_carries_is_copied_and_bound` (11 families, each copied member dropped and changed), `::test_a_readings_environment_is_bound_to_the_request` (6); probe F1 `ok` |
| F2 (B) `profiles` typed, not bound | a copied member typed but not bound | every copied member is `x-equals` the request's and present when it is (`copiedAt`), `profile` and `profiles` included; the wire projection keeps the request's profile list as written (`Projection.written`), so the binding holds for a document layer too (DELTA row 3) | `::test_a_forged_profile_list_with_recomputed_identities_is_refused`, `::test_every_member_…[judgments]`; probe F2 passes |
| F3 (B) flip rows were not the plan's flip models | a model given as its valuation, not as the model | `FlipModel`, a table in the existing model wire form, evaluated through its own relations (`flipValues_sound`), written as `model` by Lean (`flipModelJson`); the relay types it and binds its names (`_model_problem`); over `maxTuples` it is `unknown` | `tests/test_senses_route.py::test_a_flip_model_is_a_model_of_the_projection_that_separates_the_pair` (4: Lean's model mode reads it, the values hold in it), `::test_flip_rebinding_is_refused` (13 model cases), the model guards of `RunExamples.lean` |
| F5 (C) `evalF_sound`'s premise failed with empty relations | | closed by F3: the evaluator reads the model's relations (`flipValues_sound`) | `VE.Senses.flipValues_sound` |
| F8 (C) "the projection's the environment identity" | | one article (DELTA row 4) | `tests/test_senses_project.py::test_an_identity_problem_names_its_identity_once` (3) |
| F4, F6 (C) | | FOLLOW-UPS.md "## sn-b6b" | |

Main's known failures (`main-known-red.txt`) are not in this item's selection.

## Seeded bugs (docs/senses/sn-b6b/mutants.json)

| Id | File | Bug | Failing test or check |
|---|---|---|---|
| S1 | `ve/backends/senses.py` | a preamble line not in the source accepted | `tests/test_senses_route.py::test_preamble_rebinding_is_refused[absent]` |
| S2 | `ve/backends/senses.py` | the typed environment's `environment_id` binding disabled | `tests/test_senses_project.py::test_the_typed_environment_is_bound_to_the_request` (its identity case was added after this bug first survived) |
| S3 | `ve/backends/senses.py` | flip rows not bound to the pairs | `tests/test_senses_route.py::test_flip_rebinding_is_refused[shifted]` |
| S4 | `ve/__main__.py` | `ve senses project` always exits 0 | `tests/test_senses_project.py::test_senses_project_cli_relays_leans_answer` |
| S5 | `ve/senses/__init__.py` | every pack shown `reviewed` | `tests/test_senses_project.py::test_i4_a_changed_pack_is_unreviewed_and_reads_the_same` |
| L1 | `lean/VE/Senses/Flip.lean` | a flip model computed with one candidate swapped (no exchange) | `#guard`s `RunExamples.lean:205`, `:249` |
| L2 | `lean/VE/Senses/Flip.lean` | the second candidate evaluated as the first | `#guard`s `RunExamples.lean:98`, `:110`, `:151`, `:202`, `:205` |
| S6 | `ve/backends/senses.py` | the reading's environment not checked against the request (`check_projected_environment` skipped) | `tests/test_senses_project.py::test_a_readings_environment_is_bound_to_the_request` (6 of 6 fail) |
| S7 | `ve/backends/senses.py` | a flip model not bound (`_model_problem` skipped) | `tests/test_senses_route.py::test_flip_rebinding_is_refused` (12 of its 13 model cases fail; the 13th, `no-model`, fails the field check) |
| L3 | `lean/ResponseShape/Schemas/SensesProject.lean` | `acts@0`'s `acts` left out of `profileMembers` | `tests/test_senses_project.py::test_every_member_a_request_environment_carries_is_copied_and_bound[acts]` |
| L4 | `lean/ResponseShape/Schemas/SensesProject.lean` | `profiles` typed as strings, not bound | `::test_a_forged_profile_list_with_recomputed_identities_is_refused` and 8 families of `::test_every_member_…` |
| L5 | `lean/VE/Senses/Run.lean` | `Projection.written` gives the deciding profile list | `::test_every_member_a_request_environment_carries_is_copied_and_bound[judgments]` |
| L6 | `lean/VE/Senses/Flip.lean` | the flip model's relations all empty | 19 `#guard`s of `RunExamples.lean` (the build fails) |

The task's fourth seeded bug (the lock check skipping a senses file) goes with the lock to sn-b6bb.

## Trust (R16)

`uv run python tools/trust_map.py --check` on the final HEAD: K +0, S +91, V +52 over `3b4e471f8`, trusted +143
(`VE/Senses/Flip.lean` +113, `VE/Senses/Run.lean` +30; DELTA row 5), within R16's 150 and the allowance S +91,
V +52 recorded in `docs/trust-baseline.json` with "SIGNED by standing ruling R16 (DRI-RULINGS.md), sn-b6b,
2026-11-02" (this item's two allowance entries, re-measured in the review fix). Trust mutants
(`docs/senses/sn-b6b/trust-mutants.json`, run on `54d602eff` through mac-pytest `--trustmut --max-mutants 1000`,
exit 0): 291 killed, 0 survivors, 0 unknown, 87 invalid, 43 allowed (`trust-mutants-allow.json`: one equivalent
`candidatePairs` mutant, one equivalent `flipModelOf` order mutant, and mutants that do not elaborate). Two
earlier runs of the fix are kept: `trust-mutants-run1.json` (`a5443602f`: 13 survivors, 9 unknown) and
`trust-mutants-run2.json` (`46ed6cca5`: 2 survivors); each survivor was killed by a guard or allowed as
equivalent with its reason. The later commits change no Lean (tests and docs). FOLLOW-UPS.md "## sn-b6b" asks for
the ties pass; `flipValues_sound` now ties `flipPair`'s values to `evalF_sound`. Statements:
`tools/lean_statements.py --check` 0 changed; `python3 lean/audit.py` PASS.

## Size

Hand-written code and tests over `3b4e471f8` (`lean/VE/Senses/`, the schema module, `ve/`, `tests/`): 1,021 lines
added, 617 of them before the review. The fix round adds 479 lines and removes 85: Lean 244 added (the member
table and its guard, the flip model table, its soundness theorem and the guards the trust mutants asked for),
Python 49, tests 186 (the family sweep, the forged list, the reading environment, the model checks). The review accepted the earlier
overrun (F7); this round adds only what F1-F3 and their mutants need.

## Evidence

- Selected tests (review round 1): `zsh mac-pytest.sh --select -- --base 3b4e471f8 --run` on `e990750c4` (clean),
  ve-mac-1: 429 units recorded, 0 failed, exit 0; its plan ran `lake build` and `python3 lean/audit.py` (PASS). A
  first run on the fix's code commit failed one test, `tests/test_assurance_manifest.py::
  test_every_json_handling_lean_file_is_classified` (`Flip.lean` wrote JSON); the model's wire encoder moved to
  `Run.lean`, a pinned decoder file, and the test passes.
- `uv run python tools/relay_mutation_gate.py --route service:senses.project --route ve_senses_route::senses.read`
  on the fix: 1,653 mutants, 0 failures.
- `uv run python tools/gate_collection.py --check --prebuilt` on the fix: 73 added, 0 removed, 0 refused, 0 stale.
- `uv run python tools/relay_lint.py`: PASS ("4 senses module(s), no English reader"). `tools/repo_map.py --check`:
  PASS. `tools/regen_generated.py --check`: 35 entries current after the last Lean change.
- Not run: the full gate (the chain runs it on the final HEAD).
- Pilot bytes expected to move: 0 (no pilot document uses senses yet); nothing is claimed before a pilot audit.

## Spec re-read

- `preamble`: against senses-PLAN.md B6 ("the preamble lines") and the task ("each line is a line of the request's
  source"): each line is a sentence of the source, in order, as many as precede the body.
- `flips`: against senses-PLAN.md 2.6 step 7 and senses.md 2.6 "Flip models" (true exactly the senses `c` chooses
  and `d` does not; exchanged; else undistinguished; one entity per sort and constant; the existing evaluator);
  values checked against spec 8.7's s2 and n7 flip valuations (`RunExamples.lean` guards).
- Typed environment: against senses-PLAN.md D8 and 2.5 (the request's environment with sorts and predicates
  added; constants and the rest the request's).
- i3 row: decision 20261031 item 1, text copied verbatim. i4, i5: senses-PLAN.md 6.8.

## Next item

sn-b6bb (the senses lock `ve/senses/LOCK.json`, its check and the D17 hook rule; sn-b6 round-1 C notes F2 and
F3 (fault details of `senses.project`, `senses_version` bound by the lock), relay-gate F4 and F11 entries of
`senses.project`), then sn-b6c (byte spans, the 3.2 texts, glosses, `In this document, W means G.`).

## Self-review against BUILDER-CHECKLIST

1. PASS: every new member fuzzed (drop, retype, rebind): `tests/test_senses_route.py::test_genuine_response_field_mutations_are_rejected`, `::test_flip_rebinding_is_refused`, `tests/test_senses_project.py::test_projection_answer_mutations_are_rejected`; relay gate 0 failures.
2. PASS: every deliverable in the table above with its test or the cut to sn-b6bb; no Python copy of a Lean decision (`tools/relay_lint.py` PASS); overlap: only feature/ap-1bg touches nearby files (Common.lean, Environment.lean), neither edited here.
3. PASS: seeded bugs S1-S5, L1-L2 (mutants.json); trust mutants exit 0 (`docs/senses/sn-b6b/trust-mutants.json`).
4. PASS: genuine answers accepted on every fixture (`::test_flip_models_are_leans`, `::test_the_preamble_lines_are_the_sources_leading_sentences`); the S2 route comparison unchanged (`tests/test_senses_route.py::test_s2_outcomes_match_the_english_route`, in the selected run).
5. PASS: undeclared names, shifted values, extra, duplicated and empty rows refused: `::test_preamble_rebinding_is_refused`, `::test_flip_rebinding_is_refused`, `::test_the_typed_environment_is_bound_to_the_request`.
6. PASS: evidence regenerated on this branch at `main..HEAD` from the merge base `3b4e471f8`; the gate is the chain's on the final HEAD.
7. PASS: DELTA rows cite R3, R3, R3, R1, R16 with their tests; no reserved signature.
8. PASS: DELTA lists the added output members (the flip `model` included), the profile list written for a document layer, the relay's wording and the trust growth; genuine `senses.project` answers pass on every environment family (`::test_every_member_a_request_environment_carries_is_copied_and_bound`).
9. PASS: `tools/select_tests.py --base 3b4e471f8` selects `tests/test_senses_route.py`, `tests/test_senses_project.py`, `tests/test_route_row_schemas.py`.
10. PASS: the encoder theorem is unchanged and still builds (`ResponseShape.Encoders.SensesProject`); `tools/lean_statements.py --check` 0 removed, 0 changed.
11. PASS: an exhausted flip budget is `unknown`, never a distinction (`RunExamples.lean` `atLimit` and `deep 21` guards); budget 0 tests of the route unchanged (`tests/test_senses_route.py::test_zero_budget_never_admits`).
12. PASS: one budget for all flip evaluations of an answer, at most 4 evaluations per pair and 28 pairs per unit; step-count guard at exactly `maxEvaluations` (`atLimit`).
13. PASS: no test removed (`tools/gate_collection.py --check --prebuilt`: 0 removed).
14. PASS: both directions for each new check (genuine accepted and each mutant refused in the tests of 5); every claim above names its command; spec re-read listed above.

FOLLOW-UP: sn-b6bb senses lock, its check and the D17 hook rule; senses.project fault details and senses_version binding
