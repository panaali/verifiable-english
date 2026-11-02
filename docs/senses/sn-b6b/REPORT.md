# sn-b6b REPORT (senses B6 carry-overs)

Status: built; selected tests pass (443 units, 0 failed); the full gate is the chain's. No DRI signature is reserved.
HEAD: the commit that adds this file (code final at `3802e1b1b`). Changed: `senses.read` answers carry the preamble
lines and the flip models (Lean, bound by the relay); `senses.project.json` types the projected environment;
`ve senses project`; i3 recorded as built, i4, i5. Open: the senses lock and the D17 hook rule are cut to
**sn-b6bb** (size line). Hand-written lines: about 730 plus this report, over the ~600 line (see Size).

## Plan rows (senses-PLAN.md B6 :836, :877-881, 6.8 i3-i5 :1069-1075) and the task's deliverables

Plan edit 1 (edits-senses.md, D7: senses runs as `ve_senses_route`, no profile) is the one this item builds under:
`senses.read` stays on `ve_senses_route`, so its new members are typed by the relay (Deviation 1).

| Deliverable | Delivered | Where | Test |
|---|---|---|---|
| (1) (a) preamble lines of the `senses.read` source answer, written by Lean, bound by the relay | yes: `preamble`, the source's sentences before the body as written (`lexSpans` slices); on a source request only (a fence request maps its lines in `fences`) | `lean/VE/Senses/Run.lean` `writtenLines`, `admittedIds`; `ve/backends/senses.py` `_preamble_problem` | `tests/test_senses_route.py::test_the_preamble_lines_are_the_sources_leading_sentences`, `::test_preamble_rebinding_is_refused` (8), `::test_a_preamble_line_lean_did_not_read_is_unavailable`; `#guard`s in `RunExamples.lean` |
| (2) (d) flip models as the plan defines them (2.6 step 7; spec 2.6), in Lean, `#guard`s on both sides | yes: one row per pair of each open unit (`distinguished` with the senses made true and both values, `undistinguished`, or `unknown` for a form outside the evaluator or an exhausted budget); evaluated by `VE.Route.Budget.evalF` under one `maxEvaluations` budget for the whole answer | `lean/VE/Senses/Flip.lean`; `Run.lean` `flipJson`; relay `_flips_problem` | `RunExamples.lean` flip guards (first valuation, exchanged only (s2's unit 0), neither, outside, exhausted, the exact budget boundary); `tests/test_senses_route.py::test_flip_models_are_leans` (7), `::test_flip_rebinding_is_refused` (14) |
| (3) typed projected environment; OPEN_ALLOWED and F7 removed; the relay keeps binding `environment_id` and the lexicon's | yes | `lean/ResponseShape/Schemas/SensesProject.lean` (`environment`, `sort`, `request_profile`); `tests/test_route_row_schemas.py`; `tools/relay-gate-allow.json` | `tests/test_senses_project.py::test_projection_answer_mutations_are_rejected` (every member of the environment), `::test_the_typed_environment_is_bound_to_the_request`, `tests/test_route_row_schemas.py::test_no_answer_object_is_left_open` |
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
2. **Flip models carry the valuation, not the full model wire form.** Plan 4.2 types `flipModel` as "the existing
   model wire form". A row gives the senses the valuation makes true (every other predicate false) and the two
   values; the model is over one entity per sort and one per constant the pair names (spec 2.6). Writing the full
   `FiniteModel` JSON for the readings route is left to the item that writes the reading set (sn-b7b), in Lean.
   Spec 2.6's order is followed where it and plan 2.6 differ: the exchanged valuation, not the complement.
3. **The typed environment is `copied` content** (`Shape.copied`): the client validates it in full; the encoder
   theorem `projectCaseReported_fits` keeps its statement (a request-derived environment cannot be proved closed).
   Entry content (sorts, predicates) that the schema types but does not bind is refused by the relay's
   `environment_id` binding; the gate lists it under B2 with that reason.
4. `review_status` is given for a one-pack request: Lean's `dictionary_id` of several packs names them together,
   and no pin names a combination (plan 2.7 pins a pack alone).

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

The task's fourth seeded bug (the lock check skipping a senses file) goes with the lock to sn-b6bb.

## Trust (R16)

`uv run python tools/trust_map.py --check` on the final HEAD: K +0, S +50, V +42 over `3b4e471f8`
(`VE/Senses/Flip.lean` +72, `VE/Senses/Run.lean` +20), within the allowance S +50, V +43 recorded with
`--signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), sn-b6b, 2026-10-18"` (the allowance's reason text says
Run.lean +21, measured before two dead lines were removed). Trust mutants
(`docs/senses/sn-b6b/trust-mutants.json`, run on `26c47969b` through mac-pytest `--trustmut`, exit 0): 166 killed,
0 survivors, 0 unknown, 43 invalid, 20 allowed (`trust-mutants-allow.json`: one equivalent `candidatePairs`
mutant and mutants that do not elaborate). The later commits change no trusted declaration (a G[R] shape, tests,
docs). FOLLOW-UPS.md "## sn-b6b" asks for the ties pass. Statements: `tools/lean_statements.py --check` 0 removed,
0 changed; `python3 lean/audit.py` PASS.

## Size

`git diff --numstat $(git merge-base HEAD main)` without generated files: about 730 lines added or changed, plus
this report. The first measurement, after (1)-(3), was about 480; the lock and hook were cut then. The rest of
the overrun is the R16 mutant fixtures (about 80 lines of `#guard`s that the first trust run's 45 survivors asked
for) and the CLI, i4 and i5 tests. The review decides under the size line; nothing further was added.

## Evidence

- Selected tests: `zsh mac-pytest.sh --select -- --base 3b4e471f8 --run`, run `sn-b6b-cb8b3c76-t615641`, 6 shards,
  443 units, 443 passed, exit 0 (tree c131982cc3, code as `3802e1b1b`).
- `uv run python tools/relay_mutation_gate.py --route service:senses.project --route ve_senses_route::senses.read`:
  1,653 mutants, 0 failures.
- `uv run python tools/gate_collection.py --check --prebuilt`: 35 added, 0 removed, 0 refused, 0 stale.
- `uv run python tools/relay_lint.py`: PASS ("4 senses module(s), no English reader"). `tools/repo_map.py --check`:
  PASS. `tools/regen_generated.py --write` run after the last Lean change.
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
7. PASS: DELTA rows cite R3, R3, R16 with their tests; no reserved signature.
8. PASS: DELTA lists the two added output members and the trust growth; `senses.project` answers unchanged on the fixtures (`::test_projection_answer_mutations_are_rejected`, genuine side).
9. PASS: `tools/select_tests.py --base 3b4e471f8` selects `tests/test_senses_route.py`, `tests/test_senses_project.py`, `tests/test_route_row_schemas.py`.
10. PASS: the encoder theorem is unchanged and still builds (`ResponseShape.Encoders.SensesProject`); `tools/lean_statements.py --check` 0 removed, 0 changed.
11. PASS: an exhausted flip budget is `unknown`, never a distinction (`RunExamples.lean` `atLimit` and `deep 21` guards); budget 0 tests of the route unchanged (`tests/test_senses_route.py::test_zero_budget_never_admits`).
12. PASS: one budget for all flip evaluations of an answer, at most 4 evaluations per pair and 28 pairs per unit; step-count guard at exactly `maxEvaluations` (`atLimit`).
13. PASS: no test removed (`tools/gate_collection.py --check --prebuilt`: 0 removed).
14. PASS: both directions for each new check (genuine accepted and each mutant refused in the tests of 5); every claim above names its command; spec re-read listed above.

FOLLOW-UP: sn-b6bb senses lock, its check and the D17 hook rule; senses.project fault details and senses_version binding
