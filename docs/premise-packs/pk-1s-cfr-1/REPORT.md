# pk-1s-cfr-1: spec 5's fixture file against the checked plan (REPORT)

Summary: READY FOR REVIEW. Spec 5's `PacksExamples.lean` row and the stub's section-5 comment now say where the
fixtures are built (A9′ in lean/ResponseShape/Encoders/NormDefaults.lean, no layer 2 to layer 4 import) and that
`PacksExamples.lean` is not in the checked plan; tests/test_pack_plan_covers_fixture_imports.py holds it (fails on the
base). Docs and test only; trust +0; pilot bytes 0. No DELTA row, no DRI signature reserved. Next item: none.

Source: DRI 2026-11-10, reviews/dri-decisions-20261110-lp0001.md Q2, applying reviews/dri-decisions-20261109-lp1801.md
item 1 (second-pass regrade #20, reviews/l1-c-regrade-norm-defaults-b-20261109.md). The plan is the code on main;
base ab406018f (`git merge-base HEAD main`). No plan section or statement gate applies.

## Deliverables (all AGENT)

| # | Row (task) | Delivered by |
|---|---|---|
| 1 | Spec 5's row for PacksExamples.lean says the built location (A9′ in the encoder file, no layer 2->4 import) | docs/spec/premise-packs.md:290: imports as built (`VE.NormDefaults.Packs`, `VE.Rights.Examples`, `VE.Defaults.Examples`, read from `lean/VE/NormDefaults/PacksExamples.lean:1-3`), imported by `PacksLegacyExamples.lean`, F1 in `PacksLegacyExamples.lean`, A9′ a `#guard` in `lean/ResponseShape/Encoders/NormDefaults.lean:73`; marked "not in the checked plan". Also :255 (spec 4) and :279 ("`planFiles` is this list without `PacksExamples.lean`") |
| 1 | The SpecStubs_pk1.lean section-5 comment says which files `planFiles` covers and that PacksExamples.lean is not in the checked plan | docs/spec/premise-packs/SpecStubs_pk1.lean:518-523 (the four files and the first provider; PacksExamples.lean holds no stub declaration, its fixtures being outside `stubDecls`'s namespaces). The smaller fix was chosen: `planFiles` is unchanged, so the stub's code is unchanged |
| 2 | test_pack_plan_covers_fixture_imports: every table file is in `planFiles` or marked in both table and comment; no planned import breaks tools/layer_policy.py; fails on main | tests/test_pack_plan_covers_fixture_imports.py: `test_every_table_file_is_planned_or_marked`, `test_planned_imports_respect_layers` (`lean_layer` of importer >= imported, for the Imports and Imported-by columns; an unresolved name fails), and the opposite direction `test_every_plan_file_is_a_table_row` |

**Fails on the base.** At commit 33476c9fb (the test alone on the base's spec and stub), `uv run pytest -q
tests/test_pack_plan_covers_fixture_imports.py` gave `2 failed`: "spec 5's row `lean/VE/NormDefaults/PacksExamples.lean`
(new) is not in planFiles and does not say 'not in the checked plan'" and "VE.NormDefaults.PacksExamples (layer 2)
imports ResponseShape.Schemas.NormDefaults (layer 4)". On HEAD: `3 passed`.

**Line references.** The comment grew by 4 lines, so `planFiles` moved from stub:534 to stub:538 and the check from
stub:603 to stub:607; spec 5 cites the new lines (`grep -n "^def planFiles\|^run_meta" ...SpecStubs_pk1.lean` gives
538 and 607). `uv run pytest -q tests/test_premise_packs_stub.py tests/test_pack_plan_covers_fixture_imports.py`:
`37 passed` (its stub:157, 163 references are above the edit). The stub is checked from tree 49a926ee7 (its header);
only a comment changed, so its elaboration is unaffected.

**Stays selected.** `uv run python tools/select_tests.py --paths docs/spec/premise-packs.md
docs/spec/premise-packs/SpecStubs_pk1.lean tools/layer_policy.py --static --explain --no-record` lists
`tests/test_pack_plan_covers_fixture_imports.py: imports tools/layer_policy.py (static); names docs/spec/premise-packs.md
(static); names docs/spec/premise-packs/SpecStubs_pk1.lean (static)`.

## Seeded bugs

Each planted, run with `uv run pytest -q tests/test_pack_plan_covers_fixture_imports.py`, seen to fail, restored
(`3 passed` afterwards). No Lean, Python or Rust product code changed (the stub is spec under docs/).

| # | File | Bug | Fails |
|---|---|---|---|
| M1 | docs/spec/premise-packs.md | the old PacksExamples.lean row restored (task) | `test_every_table_file_is_planned_or_marked`, `test_planned_imports_respect_layers` |
| M2 | docs/spec/premise-packs/SpecStubs_pk1.lean | the "each pk-1 file" comment restored (task) | `test_every_table_file_is_planned_or_marked` |
| M3 | docs/spec/premise-packs.md | the marked row's imports name `ResponseShape.Schemas.NormDefaults` again | `test_planned_imports_respect_layers` |
| M4 | docs/spec/premise-packs/SpecStubs_pk1.lean | a `planFiles` entry renamed `SupPacksX.lean` | `test_every_table_file_is_planned_or_marked`, `test_every_plan_file_is_a_table_row` |
| M5 | docs/spec/premise-packs.md | a planned row (`SupPacks.lean`) marked "not in the checked plan" | `test_every_table_file_is_planned_or_marked` |

## Trust, lane and size

`uv run python tools/trust_map.py --check`: `against ab406018fc0d: K +0, S +0, D +0, G +0, tied +0, unclassified +0,
trusted +0`, `PASS`. `light-lane.py check`: `LIGHT 102 changed lines outside generated files <= 150 (3 files), no
trusted-core file` (before the opposite-direction test and this report). No lean/ file, no generated file, no
trust_mutants sweep (LIGHT, and the task asks for no trust_mutants record). No regen, lake build or audit: no input
of a generated file and no Lean module changed.

Spec re-read: the row's imports against lean/VE/NormDefaults/PacksExamples.lean:1-3; A9′ against
lean/ResponseShape/Encoders/NormDefaults.lean:73-87; F1 against lean/VE/NormDefaults/PacksLegacyExamples.lean:68;
"no stub declaration" against `stubDecls` (stub:602-606, direct children of `VE.NormDefaults.Packs`/`VE.Readings`
only, so `VE.NormDefaults.Packs.Fixtures.*` is outside).

## Test runs

See the final selected run below (filled in after it ran on committed code).
