# AR-14: deltas

No operation returns or raises anything different. AR-14 re-layers Python's import table, deletes 33 layer
exceptions, moves 30 function-level imports to module level and makes `ve/__init__.py` resolve its public names
lazily. The corpus A/B over the nine corpora of the lean-first gate found 0 unlisted differences, and the two
recordings are byte-identical (`evidence/ab.json`). Lean and Rust are unchanged.

Rows 1 and 2 are the Python API's import behaviour, which the task (item 4) and the plan's AR-14 change list
("`ve/__init__.py` resolves names lazily", per D5) require. Row 3 is records unavailable on both sides with identical outputs, each listed in `evidence/ab-delta.json` with its
reason.

Not a delta: the first A/B, against the earlier merge base `e73ded83`, had three whole-UDHR pilot records that hit the
recorder's 600 s limit on one side only under load (PIPELINE-LIMITS L75); re-run alone on both sides with a 1,500 s
limit they answered identically (`evidence/pilot-rerun.json`). The final A/B, against `11de39bd`, has none.

| # | Delta | Before | After | Ruling | Test |
|---|---|---|---|---|---|
| 1 | What `import ve` loads | 35 `ve` modules, the English reader among them (193 ms median, `evidence/before.json`) | `ve` alone (1.2 ms median, `evidence/after.json`); a public name imports its module on first use, and `ve.<submodule>` still imports that submodule | R11 (D5) | `tests/test_package_facade.py::test_import_ve_loads_no_submodule`, `::test_every_public_name_is_its_modules_object`, `::test_submodules_and_unknown_names` |
| 2 | What `from ve import *` binds, and `dir(ve)` | The 83 public names and every submodule that importing them had loaded (`ast`, `parser`, `wire`, ...) | The 83 public names (`__all__`); submodules by `import ve.<name>` or `ve.<name>`. `ve.check` and `ve.evaluate` are the functions in both | R11 (D5) | `::test_every_public_name_is_its_modules_object` (star import), `::test_public_names_are_the_table`, `::test_names_shared_with_their_modules_stay_functions`, `::test_checker_build_does_not_depend_on_what_was_imported` |
| 3 | 15 `pilots/default` `document_check` records, one `translation-companions-with_source_word.ve.md` per constitution pilot run | The same pre-existing `CheckerUnavailable` (`ReadingsConstruction: ... KeyError`) | Identical, byte for byte | R7 | `uv run python -m tools.evidence ab ~/.cache/ve-ar14-ab2/base.jsonl ~/.cache/ve-ar14-ab2/head.jsonl ... --delta docs/arch/AR-14/evidence/ab-delta.json` (PASS, 0 unlisted) |
