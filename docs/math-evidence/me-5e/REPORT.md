# me-5e build report: follows evidence on the wire

Status: built on `feature/me-5e`; no DRI signature is reserved.
HEAD: the final local commit on this branch; no push or model call was made.
Change: Lean emits typed `certificate` and `counterexample` members from one `runShown` search; Python displays and binds them.
Open: the R16 ties pass is requested below; this sandbox cannot write `/home/seyran/code/manage-agents/FOLLOW-UPS.md`.
Next: me-4b after me-4, then ME-7. Pilot bytes expected: 0; no pilot audit claim.

## Statement gate and delivered rows

ME-S's bounded statement review passed (`math-evidence-p3ver2.final.md`). The original `runCaseReported_fits` statement has exactly the approved type from spec 3.4; only its proof and the two follows members change. `Check.run_sound`, `Run.row_sound`, and `runMode_calc` keep their statements. The plan and spec are on main at the pinned `32ffc3ec9` content. The DRI decision in `reviews/dri-decisions-20261027-me-5d.md` item 1 chose ME-3's relay route (b).

Implementation commit: `be86b26fd` (all source, tests and generated files); this report and its evidence form the second local commit. The scope base is `6f59c66d6` (`git merge-base`). The hand-written files had no overlap with any in-flight `lean-first/*`, `feature/*`, `infra/*` or `foundation/*` branch sharing main as a merge base.

| Plan row or decision | Delivery | Check |
|---|---|---|
| ME-5 follows `certificate` on holds, `counterexample` on fails | `Run.row` stores outcome and shown evidence from one `Check.runShown`; `rowJson` writes both members, with null on the other outcomes | R-3/R-4 whole-answer `#guard`s and outcome pairing guards in `RunExamples.lean`; `tests/test_calc_service.py::test_route_cases_answer_their_rows` |
| ME-5 response shape and encoder | `Schemas/Calc.lean` has typed pairs, facts, steps and outcome-specific row alternatives; the generator produced `calc.json`; `runCaseReported_fits` is re-proved | shape render `#guard`s, `lake build ResponseShape.Encoders.Calc`, `tests/test_calc_answer.py::test_mutants_never_pass_as_answers` |
| ME-3 binding and display | The relay requires both follows fields, binds names to request free values and square pairs to the derivation's links, and prints Lean's evidence; the relay gate uses `calc.read_answer` | `tests/test_calc_answer.py::test_each_counterexample_name_is_a_free_value`, `test_each_square_step_is_one_of_the_derivations_links`, `tests/test_calc_lean.py::test_check_shows_leans_rows`, `relay-mutants.json` |
| me-5d review F1 trust class | `Check.runShown` and `Derive.shown` reclassified C to D[V] | `tools/trust_map.py --check`; `trust-mutants.json` |
| `rests_on` | Kept off the wire under me-2c's recorded spec gap | no `rests_on` member in `calc.json` |

The true R-3 certificate and R-4 point equal spec 13.6 in genuine service answers and in the CLI display. The condition tests accept declared free names and an actual derivation link, and refuse an undeclared name, a non-free declared name, a reversed or foreign link, a missing member, and a certificate or point on the wrong outcome. Follows rows with an empty point are typed and accepted when no free value was read. Every nested member is retyped and rebound by the fuzz and relay mutation tests. No request value is re-evaluated in Python.

## Trust and mutation evidence

Final `tools/trust_map.py --check`: K +0, S +0, V +43 for this item, all in `VE/Calc/Run.lean`; the new Calc shape definitions are G[R]. The R16 allowance is in `docs/trust-baseline.json`. `trust-mutants.json` (rescore on the final classification) has 22 killed, 0 survivor, 0 unknown; `schema-mutants.json` (broad prior classification) has 155 killed, 0 survivor, 0 unknown across the wire and all six new shape definitions. The latter tests the shape render guards beyond R16's trusted selection. The relay gate's eight calc fixtures yielded 1,629 mutants: 1,619 refused, ten allowed typed and request-bound semantic variations, zero failures (`relay-mutants.json`, with the five new paths explained narrowly in `tools/relay-gate-allow.json`).

Three hand-planted bugs were each applied alone and restored (`mutants.json`): nulling Lean's certificate failed the R-3 whole-answer guard; allowing a follows row without both fields failed `test_the_two_fields_come_together_and_only_on_a_follows_row`; hiding a certificate in Python failed `test_check_shows_leans_rows[20]`. The first is in Lean product code, the latter two in Python product code. No Rust product code changed.

The R16 ties pass should bind `Shown.matches`, `Run.row`, `Run.rowJson`, `Check.runShown`, and `Derive.shown` to the existing outcome, row and encoder theorems. Please add that request under `## me-5e` in `/home/seyran/code/manage-agents/FOLLOW-UPS.md`; the managed workspace allows writes only in this checkout and `/tmp`.

## Checks and scope

- `regen_generated.py --write` completed on the final Lean source; `lake build` passed 1,157 jobs; `python3 lean/audit.py` passed 666 source files and 7,343 named theorems. `tools/trust_map.py --check` passed.
- Focused calc tests: six CLI display cases, 31 genuine-answer and fuzz cases, 38 other relay cases, four service cases passed. The one relay fixture mistake found during iteration was fixed and its single test passed.
- Selected tests ran once through `mac-pytest.sh --select`; five IDs failed: three assurance manifest pins, one unclassified shape count, and one recorded calc answer using the old wire shape. The pins, trust classification and saved answers were updated; rerunning only those IDs passed (the last manifest total needed one further single-ID rerun). No full release gate was run; the chain runs it on committed final HEAD.
- No tests were removed or renamed. The old main-only failures in `main-known-red.txt` were not edited. The new checks use no sleep, model call, network or whole UDHR/constitution operation.
- Hand-written scope is under the approximately 600-line limit; generated schema, inventories, census and assurance view are produced by their tools. The changed route uses the existing one-call Lean evaluator and no Python or Rust verdict path.

## Self-review against BUILDER-CHECKLIST

1. **PASS** — `test_mutants_never_pass_as_answers`, `test_the_true_certificate_and_counterexample_are_bound`, and `relay-mutants.json` type and bind genuine calc answers and mutants.
2. **PASS** — the plan table above names each delivered row and check; `rests_on` is the me-2c gap.
3. **PASS** — `mutants.json`, `trust-mutants.json` and `schema-mutants.json` show checks fail under planted changes.
4. **PASS** — R-3/R-4 whole-answer guards and `test_route_cases_answer_their_rows` pin the Lean output; no Rust calc implementation exists.
5. **PASS** — `test_each_counterexample_name_is_a_free_value`, `test_each_square_step_is_one_of_the_derivations_links`, and `test_the_two_fields_come_together_and_only_on_a_follows_row` refuse unbound and missing members.
6. **PASS** — the final source was regenerated and built; selected tests ran on the worktree snapshot; the chain owns the final-HEAD gate.
7. **PASS** — DELTA rows cite R3, R8 and R16; the trust allowance is signed by R16.
8. **PASS** — DELTA lists both new wire members, their display and binding, and trusted growth; R-3/R-4 goldens pin the changed answers.
9. **PASS** — the selected test command found the assurance, trust classification and saved-answer dependencies; only the five failed IDs were rerun.
10. **PASS** — `lake build ResponseShape.Encoders.Calc` proves the unchanged `runCaseReported_fits` statement; the schema render and wire `#guard`s fail on altered members.
11. **N.A.** — the new fields add no budget or deadline; the existing `RunExamples` limit and unknown guards still build.
12. **PASS** — `Run.row` calls `runShown` once per follows row; `test_route_cases_answer_their_rows` covers growing and mixed rows without an extra search.
13. **PASS** — no test removal; `tests/test_calc_answer.py::test_the_two_fields_come_together_and_only_on_a_follows_row` is collected and passes.
