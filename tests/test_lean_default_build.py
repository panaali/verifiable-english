"""Every Lean source is compiled by the default `lake build` (et-7 review F2).

A module no default target imports has no object file until it is named, so the gate's build never elaborates
it and its `#guard`s cannot fail (`VE.Alternatives.FillExamples`, `VE.NormDefaults.Examples`).
`tools/check_lean_imports.py` reports such a module; the only modules outside the default build are the roots of
the lakefile's non-default executables and the scripts of `RUN_ONLY`, each run by the tool it names. The headers
are read by the reader that tests/test_lean_import_reader.py checks against Lean's own header parser.
"""
from __future__ import annotations

from pathlib import Path
import sys
import tomllib

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_lean_imports import imports, lake_globs, unbuilt_modules  # noqa: E402

UNBUILT = "Lean module no default target builds (import it from VE.lean, or name its runner in RUN_ONLY): "


def tree():
    paths = {".".join(p.relative_to(ROOT / "lean").with_suffix("").parts): p
             for p in (ROOT / "lean").rglob("*.lean") if ".lake" not in p.parts}
    return set(paths), {module: imports(path.read_text()) for module, path in paths.items()}


def test_every_lean_source_is_built_by_the_default_build():
    modules, read = tree()
    assert unbuilt_modules(modules, read, tomllib.loads((ROOT / "lean/lakefile.toml").read_text())) == []


def test_the_fixture_modules_the_review_named_are_imported_by_the_library():
    """PROBE F2 (`grep -rqx 'import VE.Alternatives.FillExamples' lean/VE lean/VE.lean`), and its main twin."""
    _, read = tree()
    assert {"VE.Alternatives.FillExamples", "VE.NormDefaults.Examples"} <= set(read["VE"])


LAKE = {"defaultTargets": ["Lib", "lib_exe"],
        "lean_lib": [{"name": "Lib"}, {"name": "Shapes", "globs": ["Shapes.*"]}],
        "lean_exe": [{"name": "lib_exe", "root": "Main"}, {"name": "bench", "root": "BenchMain"}]}
READ = {"Lib": ["Lib.A", "Init"], "Main": ["Lib"], "BenchMain": ["Lib", "Lib.Bench"]}


def test_a_module_no_default_target_imports_is_reported(tmp_path):
    modules = {"Lib", "Lib.A", "Lib.Orphan", "Main", "BenchMain", "Lib.Bench", "Shapes", "Shapes.X"}
    # The bench executable's root is built when named; a module only it imports is still unbuilt by default.
    assert unbuilt_modules(modules, READ, LAKE, run_only={}, root=tmp_path) == [
        UNBUILT + m for m in ("Lib.Bench", "Lib.Orphan", "Shapes", "Shapes.X")]
    shapes = {**LAKE, "defaultTargets": [*LAKE["defaultTargets"], "Shapes"]}
    assert unbuilt_modules(modules - {"Lib.Bench", "Lib.Orphan"}, READ, shapes, run_only={}, root=tmp_path) == []


def test_lake_globs_are_read_as_lake_reads_them_or_refused():
    lake = {"defaultTargets": ["A", "B", "C"], "lean_exe": [],
            "lean_lib": [{"name": "A", "globs": ["A.*"]}, {"name": "B", "globs": ["B.+"]},
                         {"name": "C", "roots": ["C", "D"]}]}
    assert lake_globs(lake) == ([("A", "andSubmodules"), ("B", "submodules"), ("C", "one"), ("D", "one")], set())
    modules = {"A", "A.X", "B", "B.Y", "C", "D"}
    assert unbuilt_modules(modules, {}, lake, run_only={}) == [UNBUILT + "B"]
    for glob in ("A.**", "A/*", "", 7, "A..B"):
        with pytest.raises(ValueError, match="cannot read"):
            lake_globs({"defaultTargets": ["A"], "lean_lib": [{"name": "A", "globs": [glob]}]})
    with pytest.raises(ValueError, match="neither a lean_lib nor a lean_exe"):
        lake_globs({"defaultTargets": ["missing"]})


def test_run_only_entries_must_be_current(tmp_path):
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools/run.py").write_text('run(["lake", "env", "lean", "--run", "Lib/Script.lean"])\n')
    modules = {"Lib", "Lib.A", "Main", "BenchMain", "Lib.Script"}
    run_only = {"Lib.Script": "tools/run.py"}
    assert unbuilt_modules(modules, READ, LAKE, run_only=run_only, root=tmp_path) == []
    stale = "stale RUN_ONLY entry: Lib.Script (run by tools/run.py)"
    # The script imported by the library, gone from the tree, or no longer run by its tool.
    assert unbuilt_modules(modules, {**READ, "Lib": ["Lib.A", "Lib.Script"]}, LAKE, run_only=run_only,
                           root=tmp_path) == [stale]
    assert unbuilt_modules(modules - {"Lib.Script"}, READ, LAKE, run_only=run_only, root=tmp_path) == [stale]
    (tmp_path / "tools/run.py").write_text("pass\n")
    assert unbuilt_modules(modules, READ, LAKE, run_only=run_only, root=tmp_path) == [stale]
