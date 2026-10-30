# df-1bbb delta (DE5 cut)

| # | Change | Evidence | Ruling |
|---|---|---|---|
| 1 | The flag's strict answer gains `deciders` and `english` when `Dflt_T` is nonempty; a strict answer with no default premise stays as before. The names are Lean's `decidersOf`, bound to the request, and DE5/DE5·u renders them. | `tests/test_defaults_lean.py::test_de5_strict_decider_boundaries`, `tests/test_defaults_english.py::test_strict_basis_uses_lean_deciders` | SIGNED by standing ruling R3 (DRI-RULINGS.md) |
| 2 | `defaults-elaborate` and FOLLOWS `defaults-certificate` rows gain `deciders`, with no existing field removed or renamed. | `tests/test_defaults_answer.py::test_deciders_are_typed_and_bound_on_both_rows`, `lean/ResponseShape/DefaultsExamples.lean` DE5 `#guard` | SIGNED by standing ruling R3 (DRI-RULINGS.md) |
| 3 | Trusted Lean grows by four lines: `VE/Defaults/Wire.lean` +2, `ResponseShape/Schemas/NormDefaults.lean` +2; K +0, S +0. | `uv run python tools/trust_map.py --check` output in REPORT; `trust-mutants-final.json` (83 KILLED, 5 ALLOWED, none remaining) | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
