# me-3 REPORT: the relay of `calc@0` (math-evidence ME-3)

**Status:** built; no DRI signature is reserved. The final HEAD is the branch's last commit, `feature/me-3`.
**What changed:** `ve/calc.py` relays the `calc` mode, binds each answer to its request (R8) and shows Lean's lines and
exact values. `ve calc check FILE` is new. The binding of a follows row's `certificate` and `counterexample` (DRI
decision 2026-10-27 me-5d item 1, route (b)) is ready for me-5e. Python only, with no Lean or Rust changes. Trust +0. Bytes 0.
**Open:** me-5e puts the two fields on the wire (and in the display); `rests_on` and data handles are bound by the items
that put them on the wire (below).

## Statement gate

ME-S passed (manage-agents `math-evidence-p3ver2.final.md`: PASS). This item adds no Lean statement and changes no Lean
file (`git diff --name-only $(git merge-base HEAD main) -- lean rust` is empty).

## Plan rows and directives delivered

Base `9fde70698` (`git merge-base HEAD main`). Commits: `git log --oneline --no-merges main..HEAD`.

| Row or directive | Delivered | Where, checked by |
|---|---|---|
| `ve/calc.py` sends cases with `rows` from `ve/backends/relay.py` | yes, through `relay.decide` (the relay's raising form of `rows`: a refused case raises Lean's diagnostic verbatim) | `ve.calc.check` (`ve/calc.py:35`); `tests/test_calc_lean.py::test_check_shows_leans_rows`, `test_a_refused_case_is_leans_diagnostic` |
| binds every claim id … in the answer to the request | yes: one row per request claim, in order, each naming its claim's id | `ve.calc.answer_problem` (`ve/calc.py:163`, `_row_problem` `:128`); `tests/test_calc_answer.py::test_the_relay_alone_refuses_every_binding_fault` (each id rebound to every other request id and to an unasked one, two ids swapped, rows dropped, duplicated, swapped) |
| … value name … | yes for every value name an answer carries today and after me-5e: the follows row's `certificate` (each farkas goal's coefficient names) and `counterexample` (each pair's name), each a declared free value | `_step_problem` (`:79`), `_shown_problem` (`:103`); the tests of the decision's condition below. `rests_on` (where spec 3.4 also names values) is not on the wire: me-2c's spec gap |
| … data handle … | no data handle exists yet: ME-4 adds tables and handles and, as the plan says ("each later batch extending the binding for its kind"), their binding | — |
| each row's `kind` and kind fields as spec 3.4 lists them | yes: `kind` is the form of the request's check (`claim`, or `follows` for `["follows", …]`); a claim row has exactly `sides`, `display`, `tie`; a follows row has none of them, or exactly `certificate` and `counterexample` (me-5e); a certificate only on holds and a counterexample only on fails; a reason exactly on unknown; no finding (a standalone case); a reproduction exactly under a software convention. `consistent` and `identity` are not kinds on the wire yet (ME-8, ME-9 extend the binding) | `_row_problem`, `_FIELDS` (`:25`); `test_the_two_fields_come_together_and_only_on_a_follows_row`, `test_a_certificate_only_on_holds_and_a_counterexample_only_on_fails`, the binding-fault test |
| displays Lean's English lines and exact values | yes: per row its claim, kind, outcome (and Lean's reason), Lean's line, and a claim's exact sides, display and tie; the reproduction | `ve.calc.lines` (`:182`); `tests/test_calc_lean.py::test_check_shows_leans_rows` (R-1, R-2, V-9, R-3, R-4, the mixed case), `test_the_command_prints_leans_answer` |
| `ve calc check FILE` in `ve/__main__.py` | yes: exit 0 answered, 2 refused (Lean's diagnostic, or a file that is no JSON case), 4 a resource limit, 5 an unbound answer (`CheckerUnavailable`, never a verdict) | `ve.calc.main` (`:202`); `test_a_refused_case_is_leans_diagnostic` (exits 2, 4, 2), `test_a_file_that_is_no_json_case_is_invalid_input`, `test_an_unbound_answer_is_checker_unavailable` (exit 5) |
| `tests/test_calc_lean.py` | yes | 13 tests, including `test_a_malformed_case_reaches_only_leans_answer` (each member of R-3's case retyped, a lone surrogate, a 10k-deep list: only a bound answer or a `VEError`) |
| `tests/test_calc_answer.py`: each member dropped, emptied, retyped, duplicated, reordered, an index out of range, one and two faults at a time; every mutant `CheckerUnavailable` or changes nothing shown | yes, with the two value-change classes below left out | `test_mutants_never_pass_as_answers` (R-1, R-2, V-2, V-9, R-3, R-4, the mixed case): every fault and every pair of faults (a 10k-deep list alone) goes through the transport's decoder, the service's schema check and `ve.calc.read_answer`, the path `ve calc check` takes. "Out of range" is a row past the request's last claim (an answer of `calc` has no index field yet; ME-8's `refutation.output` will) |
| `tools/layer_policy.py` one row | yes: `calc` in layer 4 (tools), beside `words` | regenerated `.importlinter`; `docs/ARCHITECTURE-LAYERS.md` row 4 (`tools/test_layer_policy.py::test_documented_python_layers_match_policy`) |
| route cases recorded (append-only) | yes: one case appended (28), claim and follows rows with both follows outcomes, a `within` and a `rounds` claim, a stated value beside three free ones, under a software convention | `tests/data/route-cases.jsonl` last line; `tests/test_calc_service.py::test_route_cases_answer_their_rows` (EXPECTED row 28). The `calc` mode is not in `tests/route_case_recorder.py`'s modes, so it is appended as the case Lean answers |
| Generated: `.importlinter`, `tools/gate-collection.json` | `.importlinter` by `tools/regen_generated.py --write`; no collection file is committed (CLAUDE.md: the gate ties test ids to the commit) | `tools/gate_collection.py --check --prebuilt`: 59 added, 0 removed, 0 refused, 0 stale, 0 malformed |
| Seeded bug (plan): the binding check skips claim ids | yes, S1 below: the swapped claim ids are accepted and the test fails | `test_the_relay_alone_refuses_every_binding_fault[R-1]` |
| The decision's condition: a counterexample with a renamed (undeclared) value name and a certificate pair that is not one of the derivation's links are each refused, the true name and link accepted | yes, each on both sides | `test_each_counterexample_name_is_a_free_value` (renamed `q`, a claim id: refused; the true names, first and last, one name, none: accepted); `test_each_square_step_is_one_of_the_derivations_links` (`(r, s)` reversed, `(d, r)`, `(q, r)`: refused; `(s, r)`: accepted); `test_a_declared_value_that_is_not_free_is_refused` (stated `h` refused, free `d` accepted, in a counterexample and in a farkas goal); `test_a_link_of_another_derivation_is_refused`; `test_the_certificate_and_counterexample_are_rebound_nowhere` (every name rebound to every other request string) |
| DELTA: the binding under R8, citing the decision; no reserved signature | yes | `docs/math-evidence/me-3/DELTA.md` row 1 |

### How the binding splits with the schema

The service already checks each answer against the generated `calc.json` (`LeanService.exchange`), which also binds the
row count, each row's `claim` and `kind` (`x-zip`, `x-equals`, `x-case`) and ties sides, display and tie to the claim's
form. `ve.calc.answer_problem` checks each binding again, by itself, so the relay's own binding has a seeded bug that a
test catches (S1). It does not copy the schema's form tables (how many sides each claim form has, which forms have a
display): those stay with the generated schema alone, and the fuzz test goes through both. Its one schema value, the
exact-value pattern, is read from `calc.json` itself.

The follows fields are not on the wire yet, and today's schema refuses them (`additionalProperties: false`). So their
fixtures (spec 13.6's R-3 certificate and R-4 counterexample, the values `lean/VE/Calc/RunExamples.lean` pins) go to the
relay's binding alone. me-5e adds them to the schema and to `ve.calc.lines`.

### Faults the fuzz test does not apply (R8: value changes, not binding)

- A member Lean may leave null set to null, or a null line set to text or a null tie set to a flag. Lean's line is null
  beyond 11.2's nesting rule, and a side, display or tie is null without a known value. Which of these holds is Lean's to
  say, carried by its encoder theorem. Every other retype of these members is applied.
- The exact `sides` list reordered. Swapping two of Lean's values is the same kind of change as replacing one.

## Seeded bugs (`docs/math-evidence/me-3/mutants.json`)

Each was applied alone, run against its test, and restored. Only Python product code changed.

| Id | File | Behaviour | Fails |
|---|---|---|---|
| S1 | `ve/calc.py` | each row names its claim's id (the plan's bug) | `tests/test_calc_answer.py::test_the_relay_alone_refuses_every_binding_fault[R-1]` |
| S2 | `ve/calc.py` | every counterexample name is a free value | `test_each_counterexample_name_is_a_free_value` (2 cases) |
| S3 | `ve/calc.py` | every square step is one of the derivation's links | `test_each_square_step_is_one_of_the_derivations_links` (3 cases) |
| S4 | `ve/calc.py` | the kind is the request check's form | `test_the_relay_alone_refuses_every_binding_fault[mixed]` |
| S5 | `ve/calc.py` | a reproduction exactly under a software convention | `test_the_relay_alone_refuses_every_binding_fault[V-9]` |
| S6 | `ve/calc.py` | a certificate only on a holds row | `test_a_certificate_only_on_holds_and_a_counterexample_only_on_fails` (2 cases) |
| S7 | `ve/calc.py` | the display keeps the order of Lean's sides | `tests/test_calc_lean.py::test_check_shows_leans_rows` (R-2, mixed) |

## Trust

`tools/trust_map.py --check` on the final code: K +0, S +0, D +0, G +0, trusted +0, PASS. No Lean is changed, so no
R16 allowance, FOLLOW-UPS row or trust mutants are needed.

## Tests run

- While iterating: `tests/test_calc_answer.py` (46 tests; the fuzz test takes about 110 s over 7 answers) and
  `tests/test_calc_lean.py` (13), `tests/test_calc_service.py -k route_cases_answer`, `tools/relay_lint.py` (PASS,
  with `ve/calc.py` added to `RELAYED`).
- Selected tests, once, on the Mac runner (`mac-pytest.sh --select`, HEAD `5d18d121`): one failure,
  `tools/test_layer_policy.py::test_documented_python_layers_match_policy`, because `docs/ARCHITECTURE-LAYERS.md` row 4
  did not list `calc`. Fixed in the next commit. The failed test passes on rerun (`uv run python tools/test_layer_policy.py`: OK).
- Not run, per the task: the full gate (the chain runs it on the final HEAD).

## Files shared with branches in flight

`tools/layer_policy.py` (also `feature/ap-1bd`) and `tests/data/route-cases.jsonl` (also `feature/qt-a3c`): one word in
the layer-4 row, and one appended line. The plan lists both as shared files of ME-3.

## Size

About 920 hand-written lines changed outside generated files (921 added, 3 removed). `.importlinter` is generated. Most of the lines are the
relay (228), the two test files (about 460) and this item's docs.

## Pilot bytes

0, as the plan says. The relay moves no byte of a pilot: the bytes come when ME-P1 runs ground calculations through it.

## Next item

me-5e: `certificate` and `counterexample` on the wire (Lean: `rowJson`'s follows members from `Check.runShown`, the
shape typed per outcome, `runCaseReported_fits` re-proved, R3 and R8 tests). In this relay, me-5e:

- tightens `_FIELDS["follows"]` to the one field set;
- adds the two fields to `ve.calc.lines`;
- moves the fixtures above from the relay-only tests into the fuzz test's genuine answers;
- registers `ve.calc.read_answer` as the `calc` route's reader in `tools/relay_mutation_gate.py`'s `SERVICE_READERS`.

Then me-4.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer is fully typed and contained: PASS. `tests/test_calc_answer.py::test_mutants_never_pass_as_answers`
   applies 7, 1.5, true, null, [], {}, "x", a lone surrogate and a 10k-deep list to each member, through the transport,
   the schema and the relay. `tests/test_calc_lean.py::test_a_malformed_case_reaches_only_leans_answer` feeds the request
   side the same values.
2. Every required deliverable is built, and no rule is broken: PASS. See the table above. No Python copy of a Lean decision:
   `answer_problem` binds and types only, and reads the exact pattern from `calc.json`. No report test was added.
3. Your tests and gates can fail: PASS. Seeded bugs S1–S7 (`mutants.json`), each failing a named test.
4. Python, Lean and Rust agree, and valid inputs still pass: PASS. Every route case answers as on main
   (`test_route_cases_answer_their_rows`). Each genuine answer is accepted (`test_mutants_never_pass_as_answers` asserts
   it first), and so are legitimately empty fields: a counterexample with no free value and a goal with no coefficients
   (`test_the_true_certificate_and_counterexample_are_bound`, `test_each_square_step_is_one_of_the_derivations_links`).
5. R8 binding: undeclared names are refused: PASS. An unasked claim id `c-unasked`, a renamed value `q`, a stated
   (non-free) `h`, an extra, a duplicated and a dropped row, and an empty row list are each refused
   (`test_the_relay_alone_refuses_every_binding_fault`, `test_each_counterexample_name_is_a_free_value`,
   `test_a_declared_value_that_is_not_free_is_refused`, the fuzz test's emptied `rows`).
6. Gate evidence matches the final HEAD: PASS for what this item runs. The chain runs the full gate on the final HEAD. The
   selected tests ran on `5d18d121`; only the layer doc changed after that, and its failed test was rerun.
7. No unsigned item is left: PASS. DELTA row 1 says "SIGNED by standing ruling R8" and cites the decision. The ruling cell
   was checked with `review-ready.py`'s `ruling_verdict`, which returned None (it passes). Each exit code is tested on
   each error exit: 2, 4 and 5 (`tests/test_calc_lean.py`).
8. Every user-visible change is in DELTA: PASS. The binding is DELTA row 1. No Lean answer changed (route cases as on
   main), and no fallback path exists.
9. Test selection still finds the tests your change can break: PASS. `tools/select_tests.py --base …` selects
   `tests/test_calc_answer.py` and `tests/test_calc_lean.py`, and the seeded layer-doc gap was found by the selected run.
10. Lean statements and proofs say what you claim: N.A., since no Lean changed.
11. Budgets, limits and deadlines fail closed: N.A. for budgets, since a `calc` case sends no budget. The service's limits
    are Lean's: a resource limit exits 4 (`test_a_refused_case_is_leans_diagnostic[14-4-…]`). The tests use no sleeps or
    literal timeouts, and the service runs with `HANG_TIMEOUT`.
12. No CPU or memory regression: N.A. Each case is one request to the existing service, with no new Lean path.
13. Every test you remove or rename has a `Test-removed` trailer: PASS. Nothing was removed, and
    `tools/gate_collection.py --check --prebuilt` reports 0 refused, 0 stale and 0 malformed.

Sibling lessons (me-2d review): each check here is tested on its accepting and its refusing side (F1's class). F2 and
F3 (wording and case of the words checks) do not apply, since this item words nothing.
