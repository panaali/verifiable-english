"""Check the saved B2 map, mutations and fixed-merge shadow evidence."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import lean_mode_deps  # noqa: E402
import test_map  # noqa: E402
from shadow import check as check_shadow  # noqa: E402

EVIDENCE = ROOT / "docs/test-speed-b2/evidence"


def main() -> None:
    coverage = test_map.load(EVIDENCE / "coverage-map.json.gz")
    roots = lean_mode_deps.load()
    assert roots is not None and set(roots) == set(coverage["modes"])
    assert coverage["version"] == test_map.VERSION == 7
    assert len(coverage["tests"]) >= 300
    check_shadow(json.loads((EVIDENCE / "shadow.json").read_text()))
    mode_rows = json.loads((EVIDENCE / "mode-mutants.json").read_text())
    assert mode_rows["map_commit"] == coverage["commit"]
    assert len(mode_rows["mutants"]) >= 26
    assert len({row["mode"] for row in mode_rows["mutants"]}) == len(mode_rows["mutants"])
    for row in mode_rows["mutants"]:
        assert row["mode"] in roots and row["mutant_exit"] != 0
        assert row["root_change"] == "lean/" + roots[row["mode"]][0].replace(".", "/") + ".lean"
        assert row["selected_witness"] in coverage["tests"]
    mutants = json.loads((EVIDENCE / "mutants.json").read_text())["mutants"]
    assert len(mutants) >= 3
    assert all(row["mutant_exit"] and row["restored_exit"] == 0 for row in mutants)
    assert any(row["file"].endswith(".lean") for row in mutants)
    assert any(row["file"] == "ve/backends/lean_service.py" for row in mutants)
    print(f"B2 evidence: {len(coverage['tests'])} mapped units, {len(mode_rows['mutants'])} mode mutants, "
          f"{len(mutants)} behavior mutants, 10 fixed-merge shadow comparisons")


if __name__ == "__main__":
    main()
