# AR-17 build report: readings S2 regeneration removed

**First line for the DRI:** no DRI signature is needed. The one user-visible delta, W1 (the report's
`checked_by.python` text, 45 records), cites standing ruling R1 (DELTA.md gives the reason). No record changed
availability. No test was left unconverted. `batch_evidence.py --check` passes every section except `[gate]`,
because `evidence/gate.json` can only be saved after the chain's gate has run (see "After the gate").

## What the batch does (plan 4.4, AR-17)

1. **Relay, not regeneration** (`e0fe5d00`). `ve/readings_route.py` `elaborate` checks Lean's `readings-elaborate`
   row against the generated schema (`check_row("readings-route", ...)`), then binds it to the request (R8):
   - a refusal's restriction ids, and the choice it names after ` under ` (`_bind_refusal`);
   - the sets a finding names, the stale narrowings, the choices and the counts (`_bind_elaborated`,
     `_bind_counts`, `_bind_choice_list`);
   - on the superposed route, the units, the slot labels and the name map (`_bind_superposed`, `_bind_slot_label`,
     `_bind_names`).
   The route, the finding's cause, the vocabulary, the contents, the formulas, the qualified names and the sizes
   are relayed as Lean wrote them. The completion path (`_bind_completion_superposed`) now uses the same binders
   instead of its own copies. `elaborate`'s signature and return value are unchanged, and `ve/document.py` is
   not edited.
2. **Shape** (`0f4dc221`). Every field `elaborate` binds already had a type in
   `lean/ResponseShape/Schemas/ReadingsRoute.lean`, so no binding mark was missing. Only the shape's description
   changed: it now says the client binds the row and regenerates none of it. The schema, the declarations and the
   binding census were regenerated. `elaborateFields_fits` still builds and is still listed in
   `lean/ResponseShape/Audit.lean` (mutant M9).
3. **Deletions** (`e0fe5d00`, `cbad85b6`). The comparisons, and every function only they called (list below).
   Generators and the verdict path keep what they use: `choice_vocabulary`, `superposed_contents`,
   `superposed_document`, `choice_core`, `slot_label` and `CHECK_BUDGET_TEXT` in `readings_verdicts.py` and
   `readings_s2_wording.py`.
4. **Tests.** Each test of a deleted comparison was converted (list below). New fuzz tests are in
   `tests/test_readings_s2_answer.py`: every member of every genuine recorded S2 row is dropped, emptied, retyped,
   duplicated, reordered, pushed out of range or forged, one fault and two faults at a time. A fault in a member
   that names the request is `CheckerUnavailable`. A fault in a value Lean derives is relayed as the mutant row
   (or refused by the schema).
5. **Coordination.** lf-18 merged (`ve-green-lf-18`), and main was merged (`cedff2cd`, then `beb5c463`) before
   `tests/test_readings_s2_lean.py` was touched. No hand-written file of this batch is edited by an in-flight
   `lean-first/*`, `feature/*`, `infra/*` or `foundation/*` branch (`git diff --name-only main...<branch>`,
   19:55Z).

## Measured outcome (tool output)

- `git diff --shortstat beb5c463 43570b7e -- ve/`: 4 files changed, 157 insertions(+), 511 deletions(-).
  Over all `*.py`, tests included: 6 files, +424 −575.
- Functions deleted (AST of base and head):
  - `ve/readings_sup.py` (18): `compatible`, `choices`, `choices_checked`, `choice_text`, `choice_chain_text`,
    `route_refusal`, `unsatisfiable_ids`, `sup_ready`, `first_nonuniform`, `uniform_precedence`,
    `canonical_content`, `superposed_units`, `name_map`, `superposed_elaboration`, `choice_slot`, `disj`,
    `_decision_atom`, `_quiet_formula`.
  - `ve/readings_s1.py` (4): `Side.line_order_text`, `Side.has_rights`, `Side.chain_text`,
    `Side._checked_elaborate`.
  - `ve/readings_route.py` (1): `_message`.
  - That is 23 in all. 8 binders were added to `ve/readings_route.py`.
- Comparisons removed: 11. These are the S2 refusal (2 sites), route, finding, precedence, choices, vocabulary,
  units, names, slot and sizes.
- `raise CheckerUnavailable("ReadingsConformance: ...")` sites (AST): `ve/readings_route.py` 11 before, 0 after;
  all of `ve/` 41 before, 30 after. The other 30 are in `readings_verdicts.py`, `readings_components.py` and
  `readings_s2_wording.py`, which are outside this batch.
- Trust (`tools/trust_map.py --check`, final code): K +0, S +0, trusted +0. PASS. No allowance was recorded.
- Hand-written additions (`git diff --numstat` against the merge base, generated files and `evidence/` excluded):
  473 lines of code, tests, Lean and mutants: `ve/` 156, tests 268, Lean 11, `mutants.json` 38. This batch's
  docs (`DELTA.md`, `DELTA.json`, `REPORT.md`, `evidence.toml`, `pilot_parts.py`) add about 325 more, about 800 in
  all. The product and test part is under the ~600 guideline; the docs take the total over it.

<!-- BEGIN GENERATED AR-17 NUMBERS -->
- Scope: `beb5c463..43570b7e --no-merges`, 5 commits: `43570b7e`, `cbad85b6`, `f71b6b25`, `0f4dc221`, `e0fe5d00`.
- Corpus A/B (`beb5c463` against `43570b7e`): 99857 records identical, 45 wording (the report's `checked_by`, DELTA W1), 0 unlisted; pilots: 55 readings part documents, readings 1137, rights 2500.
- Seeded mutants (tools/mutants.py): 9/9 killed.
<!-- END GENERATED AR-17 NUMBERS -->

## Tests converted (none deleted unconverted)

| Removed test ID | Replacement |
|---|---|
| `tests/test_readings_s2_python.py::test_uniform_precedence_catches_m8_leak_and_shape_rejects_m17` | `tests/test_readings_s2_answer.py::test_lean_refuses_the_shapes_python_did_not_superpose`, `tests/test_readings_s2_lean.py::test_m8_precedence_leak_forces_enumeration` |
| `tests/test_readings_s2_python.py::test_unsatisfiable_and_65_choice_boundary` | the MU, 65-choice and M17d `#guard`s (`choices`, `unsatText`, `routeRefusal`) in `lean/VE/Readings/Examples.lean` |
| `tests/test_readings_s2_lean.py::test_ruling5_diagnostic_names_the_choice` | the `choiceChainText` / `routeRefusal` `#guard` under `norms@0` and the `checkBudgetText` `#guard` in `lean/VE/Readings/Examples.lean` |
| `tests/test_readings_s2_lean.py::test_ruling5_over_budget_refuses_superposed_kinds` | the `checkedJson .superposed MB == "over 1024"` `#guard`; `tests/test_readings_s2_lean.py::test_ruling5_every_choice_document_checked` |
| assertions in `test_coupling_narrowing_and_stale_narrowing_match_m6_m17` on `choices` / `unsatisfiable_ids` | the M6, M17d and MU `#guard`s (the test keeps its `choice_core` assertions) |
| `test_superposition_gates_and_qualifies_without_mutating_sources` (`sup_ready`, `uniform_precedence` part) | `tests/test_readings_s2_answer.py::test_a_fixed_child_over_an_interface_rule_superposes` |

`tools/gate_collection.py --check --prebuilt` is run against the trailers in the evidence commit.

## Behaviour (4.1 item 2)

`docs/arch/AR-17/pilot_parts.py` records the pilots corpus narrowed to the readings part documents. These are the
UDHR pilots' `translation-part<n>`, any `udhr-part<n>`, and the constitution pilots' `readings/` documents except
`all-*` and `nd-all`. That is 55 documents; no whole-UDHR or whole-constitution run (L70). Its `compare` is
`lean_first_diff.compare` with that expectation. The other eight corpora (probe, conformance, readings,
discourse, the 1,000-document rights corpus, quantity, norm_defaults, document) were recorded with
`tools/lean_first_diff.py record --corpus <c>`, one corpus at a time, base then head, on a base worktree of
`beb5c463`. The recordings are kept outside the repository in `~/.cache/ve-ar17-ab/{base,head}-all.jsonl.gz`;
`evidence/ab.json` carries their SHA-256. Result: 0 availability changes, 0 unavailable on both sides, and
45 wording records (W1). Wall time of the pilot parts, recorded one side at a time with 6 workers: base 344 s,
head 326 s. This is indicative only, not a benchmark.

## Seeded bugs (`mutants.json`; `evidence/mutants.json` from `tools/mutants.py`: 9/9 killed)

| Id | Language, file | Behaviour | Failing test |
|---|---|---|---|
| M1 | Python, `ve/readings_route.py` | choices bound to the request | `test_one_fault_in_what_the_row_names_is_unavailable_and_a_derived_one_is_lean_s` |
| M2 | Python, `ve/readings_route.py` | a reading's unit at its position | same |
| M3 | Python, `ve/readings_route.py` | no reading's unit dropped | same |
| M4 | Python, `ve/readings_route.py` | `ReadingsUnsatisfiable` names the request's restrictions | `test_a_forged_refusal_naming_what_the_request_has_not_is_unavailable` |
| M5 | Python, `ve/readings_route.py` | stale narrowings are the request's | `test_one_fault_...` |
| M6 | Python, `ve/readings_route.py` | slot labels name the request's couplings and narrowings | `test_a_slot_label_naming_what_the_request_has_not_is_unavailable` |
| M7 | Python, `ve/readings_route.py` | name map names the open sets in order | `test_one_fault_...` |
| M8 | Python, `ve/readings_route.py` | a derived value is relayed unchanged | `test_genuine_answers_are_relayed_unchanged` |
| M9 | Lean, `lean/ResponseShape/Schemas/ReadingsRoute.lean` | the shape is tied to the encoder (`elaborateFields_fits`) | `lake build ResponseShape.Encoders.ReadingsRoute` fails |

No Rust code changed.

## Tests run

- Selected tests (`mac-pytest.sh --select -- --base beb5c463 --run`, on ve-mac-1, worktree at `43570b7e`): exit 0,
  0 failed, 1,952 s.
- `uv run pytest tests/test_readings_s2_{python,lean,answer}.py`: 34 passed.
- `tools/regen_generated.py --check`: clean after `--write`.
- No test of `main-known-red.txt` was hit.
- The full gate was not run by the builder: the chain runs it on the final HEAD.

## After the gate

The scope, the A/B and the gate must name the commit the chain gates. After the chain's gate of `<G>`, make one
report commit that changes only `docs/arch/AR-17/`:

    cp gate-result.json docs/arch/AR-17/evidence/gate.json
    uv run python -m tools.evidence scope --base main --head <G> --out docs/arch/AR-17/evidence/scope.json
    gunzip -k ~/.cache/ve-ar17-ab/*.gz
    uv run python docs/arch/AR-17/pilot_parts.py compare ~/.cache/ve-ar17-ab/base-all.jsonl \
        ~/.cache/ve-ar17-ab/head-all.jsonl --base-commit beb5c463026211d9e8be684884153565ca0026b9 \
        --head-commit <G> --out docs/arch/AR-17/evidence/ab.json --delta docs/arch/AR-17/DELTA.json
    uv run python -m tools.evidence report docs/arch/AR-17   # paste between the markers
    uv run python tools/batch_evidence.py --check docs/arch/AR-17 --report-commit HEAD

`<G>` differs from the recorded code `43570b7e` only under `docs/arch/AR-17/`.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: PASS. `test_one_fault_in_what_the_row_names_is_unavailable_and_a_derived_one_is_lean_s`
   and `test_two_faults_are_unavailable_when_one_is_in_what_the_row_names` retype every member (RETYPED) and drop
   or empty it. Only `CheckerUnavailable` or Lean's `VEError` escape.
2. Deliverables: PASS. Items 1 to 5 above, with their commits. No new Python copy of a Lean decision and no
   permanent report test. Overlap check: none.
3. Tests can fail: PASS. M1 to M9 are killed (`evidence/mutants.json`). M9 breaks the Lean build, not a hash.
4. Base against head: PASS. `evidence/ab.json`, 0 unlisted.
5. R8 binding: PASS. `test_a_forged_refusal_naming_what_the_request_has_not_is_unavailable`,
   `test_a_slot_label_naming_what_the_request_has_not_is_unavailable`, and the forge, duplicate and range faults
   of `test_one_fault_...`.
6. Gate evidence: N.A. for the builder. The chain gates the final HEAD; the scope comes from
   `tools.evidence scope` (the merge base); "After the gate" lists the re-save.
7. Unsigned items: PASS. W1 cites R1. Trust +0.
8. DELTA: PASS. The A/B difference (45 wording records) is W1; the other categories are none.
9. Test selection: PASS. The selected run included the three changed test files (first in the order).
10. Lean statements: PASS. M9 (a renamed field breaks `elaborateFields_fits`). No theorem statement changed.
11. Budgets: PASS. `checkedJson .superposed MB == "over 1024"` and `checkBudgetText` `#guard`s; an `over <n>`
    count is bound (`_bind_counts`).
12. CPU and memory: PASS. Work is only removed (no Python regeneration). Pilot parts head 326 s against base
    344 s, indicative.
13. Test-removed trailers: PASS. The evidence commit's final trailer block holds them;
    `tools/gate_collection.py --check --prebuilt` reports 0 refused, 0 stale and 0 malformed.
