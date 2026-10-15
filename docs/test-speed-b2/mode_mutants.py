"""Plant one wrong Lean dependency extraction per service mode and save proposed witnesses.

The source is restored after every trial, including a failed trial. Selection
witnesses use the recorded v7 map and the proposed, unactivated mode rule.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "tests")]
import lean_mode_deps  # noqa: E402
import select_tests  # noqa: E402
import source_graph  # noqa: E402
import test_map  # noqa: E402
from subprocesses import HANG_TIMEOUT  # noqa: E402

SOURCE = ROOT / "tools/lean_mode_deps.lean"
PROTOCOL = ROOT / "lean/VE/Service/Protocol.lean"
MAP = ROOT / "docs/test-speed-b2/evidence/coverage-map.json.gz"
OUTPUT = ROOT / "docs/test-speed-b2/evidence/mode-mutants.json"
ANCHOR = "let rhs ← if mode == .document"


def constructors() -> dict[str, str]:
    return {name: constructor for constructor, name in re.findall(
        r'\| \.(\w+) => "([^"]+)"', PROTOCOL.read_text())}


def main() -> None:
    source = SOURCE.read_text()
    assert source.count(ANCHOR) == 1
    roots = lean_mode_deps.load()
    assert roots is not None
    coverage = select_tests.Coverage(test_map.load(MAP))
    graph = source_graph.load(ROOT)
    names = constructors()
    rows = []
    for mode in sorted(roots):
        if mode == "document":  # its special branch is already covered in mutants.py
            continue
        constructor = names[mode]
        wrong = "VE.Rights.Run.runCaseReported" if "VE.Norms.Run" in roots[mode] else "VE.Norms.Run.runCaseReported"
        mutant = f"let rhs ← if mode == .{constructor} then pure (mkConst ``{wrong}) else if mode == .document"
        code = ("import sys;sys.path.insert(0,'tools');import lean_mode_deps as d;"
                f"assert d.generate()['modes'][{mode!r}] == {roots[mode]!r}")
        try:
            SOURCE.write_text(source.replace(ANCHOR, mutant, 1))
            trial = subprocess.run((sys.executable, "-c", code), cwd=ROOT, text=True,
                                   capture_output=True, env=os.environ, timeout=HANG_TIMEOUT)
        finally:
            SOURCE.write_text(source)
        if trial.returncode == 0:
            raise AssertionError(f"uncaught Lean mutant: {mode}")
        root = roots[mode][0]
        path = "lean/" + root.replace(".", "/") + ".lean"
        impact = select_tests.proposed_service_impact(coverage, graph, path)
        witnesses = coverage._names(coverage.modes[mode]) & impact
        if not witnesses:
            raise AssertionError(f"mode {mode} has no selected test witness for {path}")
        rows.append({"mode": mode, "file": SOURCE.relative_to(ROOT).as_posix(),
                     "root_change": path, "test": "tests/test_select_tests.py::test_compiled_mode_roots_regenerate_from_lean",
                     "mutant_exit": trial.returncode, "selected_witness": sorted(witnesses)[0]})
    assert len(rows) >= 26
    assert SOURCE.read_text() == source and lean_mode_deps.load() == roots
    OUTPUT.write_text(json.dumps({"schema": 1, "map_commit": coverage.commit, "mutants": rows}, indent=2) + "\n")
    print(f"{len(rows)} Lean mode mutants rejected; all sources restored and each root has a selected witness")


if __name__ == "__main__":
    main()
