# fu-lf14c-f4 build report

**DRI confirmation asked (not a standing-ruling class):** DELTA rows 2 and 3. Both come from the task's
own directive ("the family view must carry defined predicates of any arity"; "passes with the right
premises"), and every new answer equals the retained Python reference's. Row 2 is an availability change:
`VEError: invalid indexed formula` becomes an answer. Row 3 is a verdict change outside R5: with an
unreferenced n-ary definition, an invalid certificate becomes valid and UNKNOWN becomes CONFLICT-FREE.
Neither appears in any corpus (A/B: 0 unlisted). Every other delta is signed (R16, R8, R12, R7).

Branch `infra/fu-lf14c-f4`, base `85b20fcba` (`git merge-base HEAD main`). Commits (`main..HEAD --no-merges`):
`7039f1510` (the fix and the comments), `2b8aff333` (trust allowance and decoder pins), `d0c5088eb`
(tests, A/B evidence, DELTA), and the commit that adds this report.

## Task items

| Item | Delivered | Commit and test |
|---|---|---|
| 1. F4: family norm documents over n-ary definitions | Carried, not refused. `VE.Norms.Family.firstOrder` also requires every definition to be one the FOL view carries (`firstOrderDefinition`: a head of at most two arguments, a first-order body). Any other document goes to the family's reader, whose Background (`VE.Core.Layers`) elaborates definitions of every arity. The family-norms Background rows are typed by `familyFormula`, generated from the Lean shape. | `7039f1510`; `tests/test_stage2_norms.py` |
| 1. The reviewer's probe as a regression test | `test_a_definition_over_a_ternary_predicate_has_its_premises`: the probe's environment, through `NormDocument.premises()` on the Lean authority; the premises equal the Python reference's. | `d0c5088eb` |
| 1. One 3-ary and one 4-ary case, through the public path | `test_nary_definitions_on_the_core_family_match_python[3/4 × body/head/unused]`: `premises`, `prove_norm_entailment`, `check_norm_entailment_certificate` (genuine, stale, empty) and `check_conflict` (proved, missing, no evidence) equal Python's; Lean ops and the `family-norms` mode are asserted. `test_the_family_background_carries_every_nary_definition[3/4]`, `test_nary_definitions_with_no_budget_are_unknown[3/4]`, `test_the_family_background_refuses_retyped_nary_rows`. | `d0c5088eb` |
| 1. Corpus A/B, 0 unlisted differences | `evidence/ab.json`: 94,749 records over the seven corpora lf-14c used; 94,738 identical, 11 identical unavailable (R7, `evidence/ab-delta.json`); **0 unlisted**. | `d0c5088eb` |
| 2. Stale `Layers.lean` comments | `lean/VE/Core/Layers.lean`: the module comment's `background` bullet (Background = the FOL projection's flags, every definition's core biconditional in the one order, then literals); the stray ` -/` and the blank lines around it; the `definitionPremises` docstring (the FOL projection drops every defined declaration, so `L.rv.definitions` is empty and every definition is in `L.nary`); the `completeModel` docstring (the projection adds no defined tables; every defined table is computed by the core evaluator under one budget). The `FamilyNorms.lean` comments now list the new dispatch reason too. | `7039f1510` |
| Trust (R16) | K +0, S +0, V +13 (`VE/Norms/Family.lean` +12, `VE/Core/Layers.lean` +1), itemised in DELTA row 1, re-measured on the final code; allowance in `docs/trust-baseline.json`; `trust_map.py --check` passes. | `2b8aff333` |
| Do not edit `lean/VE/Service/Document.lean`, `ve/document.py` | Not touched (`git diff main...HEAD --stat`). | — |
| Generated files through `tools/regen_generated.py` | `lean/declarations.txt`, `lean/checkers.lock`, `family-norms.json`, the binding census, `docs/spec/assurance-manifest.md`; `regen_generated.py --check`: 28 entries pass. The decoder pins in `ve/assurance-manifest.json` (reviewed by hand, as the inventory says) list `firstOrderDefinition`. | `7039f1510`, `2b8aff333` |

Why carrying them is correct: the family reader (`genericCase`) was already the route for n-ary guards,
and `VE.Core.Layers.decodeLayered` already elaborates, orders and checks every definition. Only the
dispatch test sent definition-bearing documents to the view that cannot hold them.

## Tests run

- Selected tests (`mac-pytest.sh --select`, merge base, on `7039f1510`; it ran on the VM): 334 units. It
  failed only `test_trust_ratchet.py::test_committed_budget_passes_its_check` (fixed by the R16 allowance)
  and `test_assurance_manifest.py::test_decoder_files_are_pinned_whole` / `test_trusted_decoder_line_ranges_are_pinned`
  (fixed by the reviewed pins). The selection was the whole map because `lean/checkers.lock` changed (known).
- After the fixes, a curated set on `d0c5088eb`: `test_stage2_norms`, `test_assurance_manifest`,
  `test_trust_ratchet`, `test_binding_census`, `test_lean_service_schema`, `test_response_schemas`,
  `test_route_row_schemas`, `test_b14c`, `test_norms`, `test_frozen_sources`,
  `test_relay_binding_inventory`, `test_shape_binding_mutants`: **705 passed**.
- `tools/relay_mutation_gate.py --route service:family-norms`: 11 fixtures, 2,428 mutants, 0 failures
  (`evidence/relay-family-norms.json`).
- `tools/gate_collection.py --check --prebuilt`: 12 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- No pre-existing failure from `main-known-red.txt` showed up in these runs.
- The full gate was not run (the chain runs it on the final HEAD).

## Seeded bugs (Lean; no Python or Rust product code changed)

Recorded in `evidence/mutants.json`. Each one was planted, made the named test fail, and was restored
(source, `lean/checkers.lock` and schema restored; the pins check afterwards):

1. `lean/VE/Norms/Family.lean`: `firstOrderDefinition` ignores the body, which brings the n-ary case
   back. `test_a_definition_over_a_ternary_predicate_has_its_premises` fails with `invalid indexed formula`,
   as do `[3-body]` and `[4-body]`.
2. `lean/VE/Norms/Family.lean`: `firstOrderDefinition` ignores the head's arity.
   `test_nary_definitions_on_the_core_family_match_python[3-unused]` and `[4-unused]` fail.
3. `lean/ResponseShape/Schemas/Norms.lean`: Background rows typed with `generated_formula` again, schema
   regenerated. All 9 new route tests fail, and so does `test_the_family_background_refuses_retyped_nary_rows`,
   with `unknown tag 'atom'`.

## FOLLOW-UPS rows (for the orchestrator to copy)

- **fu-lf14c-f4 ties pass (R16):** tie the 13 new untied V lines to existing theorems:
  `VE.Norms.Family.firstOrderDefinition` and the `firstOrder` conjunct (`lean/VE/Norms/Family.lean`, G[V])
  to the family-norms dispatch (`ResponseShape.Encoders.Family.familyNorms_fits` covers both branches), or
  prove that a document `firstOrder` accepts decodes over `FamilyNorms.folView` with every definition kept.
  Also the one-line growth of the `VE.Core.Layers.completeModel` docstring (D[V]).
- **Stale Python docstring:** `ve/norms.py` `_lean_route` still says "except the n-ary core definitions
  `family_in_scope` leaves out (lean-first batch 14c)". lf-14c removed that exclusion. Python file, left
  alone here so that this item changes no Python product code.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: PASS. `test_the_family_background_refuses_retyped_nary_rows` retypes the n-ary
   atom's name, argument list, a term and the tag, and drops the generator. `relay_mutation_gate.py --route service:family-norms`: 0 failures.
2. Deliverables and rules: PASS. See the task table above. Lean owns the dispatch. No Python copy, no new
   report test, `Document.lean` and `ve/document.py` untouched.
3. Tests can fail: PASS. Three Lean seeded bugs in `evidence/mutants.json`, each failing named tests.
4. Agreement and valid inputs: PASS. `test_nary_definitions_on_the_core_family_match_python` compares Lean
   with the Python reference on 3- and 4-argument predicates; `evidence/ab.json` has 0 unlisted. Rust does
   not answer norms.
5. R8 binding: PASS. No new field is read. The existing order, label, target and sorts bindings cover the
   rows (`test_non_first_order_elaboration_refuses_unbound_rows`), and the relay gate's rebind mutants pass.
6. Gate evidence on the final HEAD: PASS for A/B (`evidence/ab.json` head `2b8aff333`; later commits change
   only tests and docs). The full gate is the chain's.
7. No unsigned item: PASS. Rows 1 and 4 are signed (R16, R8/R12); A/B is R7. Rows 2 and 3 are named in
   this report's first line as asking for DRI confirmation.
8. Every user-visible change in DELTA: PASS. Base vs head on the six new documents (`invalid indexed
   formula` ×4; invalid/UNKNOWN ×2 on base) is DELTA rows 2 and 3; the corpora show no change.
9. Test selection: PASS with a known cause. Selection is the whole map because `lean/checkers.lock`
   changed. `tests/test_stage2_norms.py` was in it and ran first as a changed file.
10. Lean statements: N.A. No theorem was added or changed. `familyNorms_fits` still builds over the new
    dispatch.
11. Budgets fail closed: PASS. `test_nary_definitions_with_no_budget_are_unknown[3/4]`:
    `tableau_steps=0` gives UNKNOWN (500 gives CONFLICT-FREE), and `max_steps=0` gives ResourceLimit with no
    certificate.
12. No CPU regression: PASS. DELTA "Cost", 200 elaborations base vs head on the same host: wall
    0.38/0.39/0.38 s base, 0.34/0.30/0.41 s head. The new test is one pass over the predicates. No eager
    per-candidate call.
13. Test-removed trailers: N.A. No test removed or renamed (`gate_collection.py --check --prebuilt`: 0 removed).
