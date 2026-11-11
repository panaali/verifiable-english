# norm-defaults-cfr-1: the norm-defaults mode's answers bound to their request (REPORT)

Summary: READY FOR REVIEW. A forged norm-defaults status row (tuple, repeated or absent rule) or certificate row
(premise count) is now `CheckerUnavailable`: the tuple and distinct rules in the Lean response schema, the rest in
`bind_answers` (ve/backends/lean_service.py). The manifest binds all 13 kinds the mode answers (new operation
`norm-defaults.route`). Status rules under `acts@0`/`rights@0`, left type-checked only here (DRI 2026-11-10),
are bound by norm-defaults-cfr-1b. Trust +0; one DELTA row (R16); no DRI signature reserved.

Source: regrade #3 (ND-FC2, grade A) in reviews/l1-c-regrade-norm-defaults-b-20261109.md; DRI 2026-11-10
reviews/dri-decisions-20261110-lp0001.md Q2 and reviews/dri-decisions-20261110-norm-defaults-cfr-1.md (scope of the
rule binding). The plan is the code on main; base de7fb9469 (`git merge-base HEAD main`); no plan section or gate.

## Deliverables (all AGENT)

| # | Task row | Delivered by |
|---|---|---|
| 1 | The manifest lists every kind the norm-defaults mode answers | ve/assurance-manifest.json: new lean-only operation `norm-defaults.route`, one `ve_service`/`norm-defaults` binding per kind (`norm-defaults-elaborate`, `-conflict`, `-status`, `-gaps`, `-report`, `-certificate`, `defaults-elaborate`, `-coherence`, `-certificate`, `-model`, `-zone`, `acts-elaborate`) with its declared response; `admission` stays the `admission` operation's binding. One accepted probe each: conformance/binding_probes.py `_norm_defaults_cases`. Tests: `test_the_manifest_lists_every_kind_the_mode_answers` (manifest kinds == the `kind` table of ve/backends/lean_service_schema/norm-defaults.json, rendered from Lean's ResponseShape) and tests/test_assurance_manifest.py `test_every_lean_binding_has_a_probe`, `test_every_lean_binding_routes_its_operation`, `test_every_real_answer_is_counted_and_indexed` |
| 2 | A status row naming a rule or entity absent from the request, or a certificate whose premise count differs from the premises it carries, is refused (CheckerUnavailable) by binding | Tuple and distinct rules: lean/ResponseShape/Schemas/NormDefaults.lean `status` (`.equals "/tuple"`, `.uniqueStrings`; skeletons ignore both, so no encoder theorem changes). Rules and premise count: `bind_answers` / `MODE_BINDINGS` / `_bind_norm_defaults`, run in `LeanService._roundtrip` after `check_response`, so a refusal is a `_Failure`: one retry, then `CheckerUnavailable`. Rules under `acts@0` or `rights@0`: bound by norm-defaults-cfr-1b (below) |
| 3 | `test_norm_defaults_response_binding`: forged rule, entity and premise count refused; genuine passes; manifest kinds | tests/test_norm_defaults_response_binding.py |

### What is bound (R8: Python binds, Lean decides)

- **Tuple** equals the case's `tuple` (`Wire.replayStatusIn` zips the request ids with the predicate's sorts after
  checking their number; `statusFields` returns them). Schema, so Lean's `ve_response_decode` agrees.
- **Rules** are distinct (schema) and each is the `name` of a `{"norm": ...}` unit of the case's `norms`
  (`_rule_names`). Under `acts@0` and `rights@0` Lean names rules the request does not carry; norm-defaults-cfr-1b
  binds them through the request source Lean echoes for each rule (`sources`; docs/premise-packs/norm-defaults-cfr-1b/).
  No Python copy of Lean's naming is kept (the first commit's `-a<k>` regex was deleted, self-review B1).
- **Premise count** is `len(certificate.premise_meaning_ids) - len(premises)`: `Wire.bindingOk`
  (lean/VE/Route/Wire.lean:553) refuses a certificate unless its ids are those of `background ++ fill ++ elaborate ++
  premises`, and the row counts `premisesU U []` (lean/VE/NormDefaults/Run.lean:281; the soft branch `premisesX`,
  Run.lean:130).
- **Not bound** (Lean's to choose): which request rules decide (an empty `rules` is a genuine answer: UNKNOWN, or a
  point its default settles), `differs`, and a request rule of another predicate (it exists in the request).

## First-commit comparison with main

At the first commit ad53a4859, with `git show main:ve/backends/lean_service.py` in place of the branch's client:
`uv run pytest -q -p no:cacheprovider tests/test_norm_defaults_response_binding.py` gave
`17 failed, 1 passed` (evidence/on-main.txt: every forged row and the manifest test; the pass is the genuine-answer
test). The manifest test fails on main's manifest alone (kinds `["admission"]`). The final test added forgeries
after that run, so this evidence does not claim that every final test was run against main. On HEAD: "Test runs".

## Genuine answers

`PYTHONPATH=docs/premise-packs/norm-defaults-cfr-1/evidence NDLOG=<file> uv run pytest -q -p genuine_pairs -n 4`
over tests/test_defaults_answer.py, test_document_chain.py, test_events_route.py, test_norm_defaults_layered.py,
test_norm_defaults_relay_english.py, test_norm_defaults_soft_kinds.py, test_norm_defaults_switch.py,
test_norm_defaults_three_way.py, test_alternatives_fill.py, test_norm_defaults.py: `282 passed`; then
`uv run python docs/premise-packs/norm-defaults-cfr-1/evidence/genuine_pairs.py <file>` (this tree's `check_row` and
`_bind_norm_defaults` on each): 21,344 rows, **0 refused** (evidence/genuine-pairs.json: status 21,248 plain, 34
soft-norms, 7 rights document; certificates 19 plain, 32 soft-norms, 4 soft-norms with events). Not in that set, and
shown instead by `test_genuine_answers_pass`: a split act (`acts@0`) and a certificate with the case's own premise.

## Seeded bugs

Each planted, run, seen to fail, and restored (`git checkout`; Lean ones then rebuilt with
`lake build ve_response_decode` and `tools/response_schemas.py --check` clean). T = tests/test_norm_defaults_response_binding.py.

| # | File | Bug | Failing test |
|---|---|---|---|
| S1 | ve/backends/lean_service.py | `bind_answers` not called in `_roundtrip` | T::test_norm_defaults_response_binding[certificate-premises-one_more] (FAILED) |
| S2 | ve/backends/lean_service.py | rule check dropped (`names = None`) | T::test_norm_defaults_response_binding[status-rules-ghost] (FAILED) |
| S3 | ve/backends/lean_service.py | premise-count equality dropped | T::test_norm_defaults_response_binding[certificate-premises-one_more] (FAILED) |
| S4 | ve/backends/lean_service.py | count compared with `len(ids)` (case premises ignored) | T::test_genuine_answers_pass and [certificate-premise-premises-every_id] (ERROR in the `genuine` fixture: "malformed response (norm-defaults-certificate premises is not the count its certificate is bound to)") |
| S5 | ve/backends/lean_service.py | `GENERATED_RULE_PROFILES = ()` (rules bound on every profile) | T::test_genuine_answers_pass (ERROR: "malformed response (norm-defaults-status rules name 'art9', no rule of the request)") |
| S6 | lean/ResponseShape/Schemas/NormDefaults.lean | `.equals "/tuple"` removed | T::test_norm_defaults_response_binding[status-tuple-other_entity] (FAILED: DID NOT RAISE) |
| S7 | lean/ResponseShape/Schemas/NormDefaults.lean | `.uniqueStrings` removed | T::test_norm_defaults_response_binding[status-rules-duplicated] (FAILED) |
| S8 | ve/assurance-manifest.json | the `norm-defaults-gaps` binding removed | T::test_the_manifest_lists_every_kind_the_mode_answers (FAILED) |
| S9 | ve/backends/lean_service.py | missing or malformed `profiles` exempts rule names | T::test_status_rule_binding_without_generated_profile (4 FAILED before fix, 6 passed after) |
| S10 | lean/ResponseShape/Schemas/NormDefaults.lean | `.equals "/tuple"` removed and schema regenerated | T::test_status_tuple_schema_binds_request_without_service (FAILED: DID NOT RAISE; passed after restore) |
| S11 | conformance/binding_probes.py | `norm-defaults-gaps` probe removed | tests/test_assurance_manifest.py::test_every_lean_binding_has_a_probe (FAILED: missing key; passed after restore) |

S9–S11 are also recorded in `seeded-mutants.json`. S10 was run by invoking the test function directly to avoid a
native-build lock while the Lean schema was deliberately mutated; the final pytest run covers the restored source.

## Test runs

- Iterating: T (24 passed); tests/test_assurance_manifest.py probe tests with `VE_LEAN_PREBUILT=1` (`3 passed`);
  tests/test_lean_service.py `-k random_malformed` (`1 passed`).
- `uv run python tools/regen_generated.py --write`: rc 0, 38 entries; `lake build`: `Build completed successfully
  (1344 jobs)`; `python3 lean/audit.py`: PASS (812 files, 9106 theorems); `tools/gate_collection.py --check
  --prebuilt`: 36 added, 0 refused, 0 stale, 0 malformed.
- Final selected run, on committed code (clean tree at 4de39e8fb):
  `MAC_PYTEST_NO_DEFER=1 zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base de7fb9469 --run`
  ran on the Claude cloud in 4 shards: `exit=0; 2463s`; shards 1-4 `127, 127, 128, 97 units passed`, 0 failed; the
  selection included T, tests/test_assurance_manifest.py and tests/test_lean_service.py. Nothing but this REPORT
  changed after it.

## Size, trust, pilot bytes

- Hand-written lines outside generated files: 564 added, 6 removed at the REPORT's commit (`git diff --numstat`
  against the base: product code 65, probes 45, tests 236, docs and evidence 216, Lean 2).
  ve/assurance-manifest.json (+281) is a
  generated-class file (.gitattributes `merge=ve-generated`; the task calls it generated) whose values are
  hand-reviewed; counted, the item is ~845. Over the task's ~200 estimate because the manifest needs a probe per
  binding and the fuzz covers each bound field (BUILDER-CHECKLIST 1, 5); the DRI decision above used size as a reason not to grow the item.
- Trust: `uv run python tools/trust_map.py --check`: `K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0`,
  PASS. No trusted Lean growth, so no trust-mutant sweep (build checklist 13a) and no FOLLOW-UPS row.
- Pilot bytes: 0 expected (a binding of relayed rows; no verdict, wording or coverage changes).

## Follow-ups

- norm-defaults-cfr-1b (filed by the DRI): Lean echoes each status rule's request source; rules bound under
  `acts@0` and `rights@0` (delivered there).
- FOLLOW-UP norm-defaults-cfr-1d: `norm-defaults-conflict` witness rows' `tuple`/`rules` and readings-route
  `norm-defaults-certificate` rows (mode `readings-route`, so `MODE_BINDINGS` does not see them) are not bound
  (self-review C1).

## Spec re-read

- "status rule or tuple names a rule or entity absent from the request" against the task file and
  reviews/l1-c-regrade-norm-defaults-b-20261109.md:115, narrowed by reviews/dri-decisions-20261110-norm-defaults-cfr-1.md item 1.
- "certificate premise count differs from the premises it carries" against lean/VE/NormDefaults/Run.lean:281 and
  lean/VE/Route/Wire.lean:553.
- "the manifest lists every kind the norm-defaults mode answers" against the schema `kind` table,
  lean/VE/NormDefaults/Run.lean:219-283 and lean/VE/Defaults/Route.lean:15.

## Self-review against BUILDER-CHECKLIST

SELF-REVIEW: 1 A, 5 B, 4 C; fixed 9 (A1 by the DRI's scope ruling and the rights/acts gap; B1 regex deleted; B2 schema;
B3 certificate with a premise; B4 evidence scope; B5 size stated; C2 `unknown` outcome; C3 DELTA; C4 top-level units
only; C1 named as norm-defaults-cfr-1d).

1. PASS: T::test_each_bound_field_deleted_or_retyped_is_no_answer (delete, 7, true, null, [], {}, 1.5, "\ud800").
2. PASS: deliverables table; no Python copy of a Lean decision (the regex is gone); no report test; no overlap with in-flight branches.
3. PASS: seeded bugs S1-S8, each with its failing test.
4. PASS: evidence/genuine-pairs.json (0 of 21,344 refused) and T::test_genuine_answers_pass.
5. PASS: T::test_norm_defaults_response_binding (absent, shifted, extra, duplicated, emptied tuple and rules).
6. PASS: gate runs on the committed HEAD by the chain; evidence is saved files, no live git.
7. PASS: DELTA row 1 cites R16; no signature reserved.
8. PASS: DELTA row 1 (the only availability change; genuine rows unchanged per evidence/genuine-pairs.json).
9. PASS: the selected run below includes T and tests/test_assurance_manifest.py.
10. N.A.: no theorem or proof changed (the schema edit is outside every skeleton).
11. N.A.: no budget or deadline; the binding walks each case's `norms` once (one pass per row).
12. N.A.: one set build per status row; no Lean call added.
13. PASS: no test removed; `gate_collection.py --check --prebuilt` 0 refused, 0 stale, 0 malformed.
14. PASS: opposite directions in T (genuine passes on four source shapes; forgeries refused); spec re-read above.
15. PASS: overclaim grep of REPORT/DELTA done (the rule gap is stated); no deliverable cut without the DRI's ruling; every new check has a mutant (S1-S8); no new limit.
