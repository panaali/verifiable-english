# ar-10b report: the route registry (AR-10)

No DRI signature is reserved. Every DELTA row cites a standing ruling (R6).

Plan: `docs/ARCHITECTURE-REVIEW-2026-10.md` 4.4 AR-10 at 6ae55ebb8 (copied verbatim into this branch, since main
lacked it), with 3 T1(c), section 2.1's P6 and F4 rows, `arch-dri-decisions.md` D8 (the registry carries modes and,
later, the null policy; deadlines stay in Python), and SYNTHESIS 2.2's last bullet and 4.2 (AR-10's registry is
first in the `Protocol.lean` / `service_schema.py` queue). Statement gate: the plan's change log records the
converged review of AR-10 and D8 (debate `design-arch-review`, round 2), and the DRI adopted it (section 5, D8). The
profile-gate half of AR-10 was ar-10a.

## Plan rows

| Row | Delivered | Where | Checked by |
|---|---|---|---|
| `lean/VE/Service/Registry.lean`: `RouteSpec`, `registry`, `modes_complete`, `registry_modes`, `registry_names_nodup`, as written | yes, verbatim; `decide` proves all three in about 3 s, so the `#guard` fallback is not needed. `Mode`, `Mode.name`, `Mode.ofName?` and `modes` move here from `Protocol.lean`, because the handshake (in `Protocol.lean`) reads `registry` | `lean/VE/Service/Registry.lean` | the three theorems (`VE/Audit.lean` `#print axioms`); mutants below |
| The handshake carries the modes from `registry`, its shape in `Schemas/Envelope.lean` | yes: `("modes", toJson (registry.map (·.mode.name)))`. The shape pins that list exactly (`const`, as for `codes`); before, it required a list containing each mode | `lean/VE/Service/Protocol.lean`, `lean/ResponseShape/Schemas/Envelope.lean` | `ResponseShape/Schemas.lean:97` `#guard` (the handshake fits its shape); `:96` now walks `registry` |
| `service_schema.MODES` comes from the handshake; the Python list is deleted (one owner) | yes: `MODES` is `envelope.json`'s `handshake.modes`, as `ve/limits.py` reads the limits; `check_handshake` refuses a live service stating any other list. The literal tuple is deleted | `ve/backends/service_schema.py` | `test_handshake` (live service = `MODES`), `test_lean_lists_are_the_rendered_enumerations` |
| Mode lists in `tests/lean_routes.py` and `tests/test_lean_service.py` | `test_lean_service.py` reads `MODES` (the handshake's). `tests/lean_routes.py` holds no mode list: it maps 13 retired one-shot executable names to modes. Those names are not Lean's, and about 20 test files use them, so the table stays, renamed `EXECUTABLES`, and a test checks each target is a handshake mode. `ROUTE_MODES`, a classification of row shapes, is also checked to be a subset of the handshake's modes | `tests/lean_routes.py`, `tests/test_lean_service.py` | `test_route_executable_aliases_name_handshake_modes` |
| `lean_service.DEADLINES` stays in Python (F4); a test checks its keys equal the handshake's modes | yes; fixtures: a mode with no deadline and a deadline key that is no mode each fail | `tests/test_lean_service.py` | `test_the_deadline_keys_are_the_handshakes_modes`; `test_handshake` (live handshake) |
| Fixture: a handshake golden | the golden is generated, not hand-kept: `envelope.json` pins every handshake member exactly (service, protocol, modes, codes, limits, handles), `regen_generated.py --check` holds it to the Lean rendering, and `test_handshake` compares the live service with it. A hand-written golden would be a second copy of the mode list | `ve/backends/lean_service_schema/envelope.json` | `test_handshake`, `test_every_schema_file_is_the_lean_rendering` |
| Fixture: a new `Mode` constructor without a registry entry fails to compile | yes: mutant 1 below (a named constructor with no `modes` entry fails `modes_complete`; with no name, `Mode.name` also fails) | `mutants.json` | `VE.Service.modes_complete` |
| Deleted: P6's modes; mode-name lists in tests | the `MODES` tuple and the test assertion that copied the list from `allOf` | | |
| Outcome: adding a mode edits Lean only, plus its deadline | the recipe (AGENTS.md steps 1 and 4) now registers a mode in `Registry.lean`; Python's only hand line for a new mode is its `DEADLINES` row (F4). Files spelling `"risk-eval"` in hand-written product code: 3 (`Protocol.lean`, `service_schema.py`, `lean_service.py`) to 2 (`Registry.lean`, `lean_service.py`); in the whole tree 23 to 22, the rest being evidence, recorded fixtures and generated files | | `git grep -l '"risk-eval"'` at the merge base and HEAD |
| Null policy in `RouteSpec` | not here: AR-12b, as the plan says | | |

Follow-on edits the move needed: `tools/repo_map.py` no longer counts the mode type's module as a route's
implementation; `tools/select_tests.py` and `tools/answer_cutoff.py` treat `Registry.lean` as request handling, like
`Protocol.lean`; `tools/lean_mode_deps.py` hashes it as a source; `tools/architecture_numbers.py` counts the modes from
`envelope.json` (its table label is unchanged, so `docs/ARCHITECTURE.md`'s numbers stay valid);
`tests/test_enum_domains.py` writes string lists as a `::` chain, because Lean elaborates a list literal of over 32
elements (the 37 modes) to nested `let`s that the `fits` tactic does not read.

Not in scope, noted for a later item: `lean_service.UNHANDLED_MODES = {"english", "risk-eval"}` mirrors Lean's
`expandCases`. D8 keeps the registry to modes and the null policy, so it stays.

## Seeded bugs

[`mutants.json`](mutants.json): 14 of 14 killed, each applied alone and restored.
- Lean, `lean/VE/Service/Registry.lean`:
  - a named constructor `bogus` with no `modes` entry fails `modes_complete`;
  - `metered` dropped from `modes` fails `modes_complete`;
  - `registry` with `.drop 1` fails `registry_modes`;
  - `registry` mapping every mode to `evaluate` fails `registry_modes` and `registry_names_nodup`;
  - two modes named `words` fails `registry_names_nodup`.
- Lean, `lean/VE/Service/Protocol.lean`: the handshake without its first mode fails the `#guard` at
  `ResponseShape/Schemas.lean:97`.
- Lean, `lean/ResponseShape/Schemas/Envelope.lean`: the mode list reversed fails the same `#guard`.
- Python, `ve/backends/service_schema.py`: `MODES` without its last mode fails
  `test_the_deadline_keys_are_the_handshakes_modes` and `test_lean_lists_are_the_rendered_enumerations`.
- Python, `ve/backends/lean_service.py`: no `metered` deadline fails `test_the_deadline_keys_are_the_handshakes_modes`.
- Python, `tools/architecture_numbers.py`: `test_measure_on_a_small_tree`.
- Python, `tools/answer_cutoff.py`: `test_request_handling_and_project_changes_select_every_service_user[lean/VE/Service/Registry.lean]`.
- Python, `tools/select_tests.py`: `test_service_modes_narrow_only_known_recorded_users`.
- Python, `tools/repo_map.py`: `test_known_routes_print_their_lean_module_and_relay` for three routes.
- Python, `tools/lean_mode_deps.py`: `test_compiled_mode_roots_cover_every_service_mode`, plus `--check` reports the
  file stale.

## Trust, size and evidence

- Trust (`tools/trust_map.py --check` on the synced HEAD, against b1f7ca7ad): K +0, S +0, untied V +6.
  `Registry.lean` +61 (`Mode`, `Mode.name`, `Mode.ofName?` and `modes` moved; `RouteSpec` new; `registry` tied by
  `registry_modes`), `Protocol.lean` −55. Signed by R6: the lines replace the deleted Python `MODES` list. Recorded
  with `--allow` in `docs/trust-baseline.json`. No R16 growth, so no FOLLOW-UPS ties row.
- Statements: no approved statement changes; `statements.txt` adds the three theorems, and existing entries change
  only their `-- uses` module (`@VE.Service.Registry`).
- Size: about 300 hand-written lines added and 120 deleted, including this report, DELTA and `mutants.json`. The
  55-line move is counted on both sides. The copied plan and the generated files are not counted.
- Tests:
  - Selected plan on the Mac runner (a54bd546b, 455 units): one failure, `test_every_field_keeps_its_domain[0]`,
    fixed in af9bbf7a4 (`tests/test_enum_domains.py`, 28 passed).
  - The selected plan of the final HEAD is listed under "Final selected run" below.
  - Also run: `relay_mutation_gate.py` (42 routes, 137,740 mutants, 0 failures), `regen_generated.py --write` after
    the sync, `trust_map.py --check`, `repo_map.py --check`, `lean/audit.py`, `check_lean_imports.py`,
    `rust_build.py --check`, and `gate_collection.py --check --prebuilt` (8 added, 0 removed, 0 stale, 0 malformed).
- Not run: the full gate (the chain runs it on the final HEAD).
- Pilot bytes: none expected; no answer, text or availability moves.
- Overlap: no in-flight branch edits the hand-written files here. Generated inventories (`Audit.lean`) are not
  overlaps (R12).
- Next: AR-12b adds `nulls` to `RouteSpec` and to the handshake; the modes ME-2, QT-A3, SC-1c, AP-4 and ME-12 register
  here (SYNTHESIS 4.2).

## Final selected run

(filled in below after the run on the final HEAD)

## Self-review against BUILDER-CHECKLIST

1. PASS: the handshake's modes are an exact, typed list. A fake service stating null, fewer, extra (`absent`),
   reordered, duplicated or retyped (`7`) modes is CheckerUnavailable at start
   (`test_bad_or_missing_handshake_is_unavailable`). The relay mutation gate passes.
2. PASS: plan rows table above; the deletion is in 0414d2d1c.
3. PASS: `mutants.json`, 14 of 14, at least one per changed file in Lean and Python.
4. PASS: `test_handshake` (live service = `MODES` = the deadline keys); `test_lean_lists_are_the_rendered_enumerations`;
   `regen_generated.py --check`. No Rust change.
5. PASS: the handshake answers no request, so its modes are a closed domain bound exactly by the schema. An
   undeclared mode (`absent`), a duplicate, an extra and a shifted order are each refused
   (`test_bad_or_missing_handshake_is_unavailable`).
6. PASS: synced with main (7ca77d87d) and regenerated; the chain runs the gate on the final HEAD.
7. PASS: DELTA row 1 cites R6.
8. PASS: DELTA states that no answer moves; the narrower handshake check is described there with its test.
9. PASS: the selected plan covered the failing enum test. A seeded change in `select_tests.py` is caught
   (`test_service_modes_narrow_only_known_recorded_users`), and `Registry.lean` selects every service user.
10. PASS: the three theorems as written; mutants 1 to 5 break them; no statement changed.
11. N.A.: no budget, limit or deadline value or code path changed; only the deadline table's keys are tested.
12. N.A.: no runtime work added; the theorems are decided at build time (about 3 s).
13. PASS: `gate_collection.py --check --prebuilt` reports 8 added, 0 removed, 0 stale, 0 malformed (no test removed).
