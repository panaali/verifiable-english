"""Saved retrospective shadow replay for ten merged items.

Write uses fixed merge commits and a recorded v7 map. Check reads only the
saved paths, map and full-gate JSON: it does not diff a moving HEAD.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import select_tests  # noqa: E402
import test_map  # noqa: E402

EVIDENCE = ROOT / "docs/test-speed-b2/evidence"
MAP = EVIDENCE / "coverage-map.json.gz"
OUTPUT = EVIDENCE / "shadow.json"
MERGES = (
    ("lf-6", "29773091", "docs/lean-first/b6/evidence/full-gate.json"),
    ("lf-7", "7345e3ed", "docs/lean-first/b7/evidence/full-gate.json"),
    ("lf-11a", "87900bdf", "docs/lean-first/b11a/evidence/full-gate.json"),
    ("lf-11b", "c7e2000d", "docs/lean-first/b11b/evidence/full-gate.json"),
    ("lf-12", "abc30811", "docs/lean-first/b12/evidence/gate.json"),
    ("lf-13b", "f1b719c7", "docs/lean-first/b13b/evidence/gate.json"),
    ("lf-15a", "c07377ed", "docs/lean-first/b15a/evidence/full-gate.json"),
    ("lf-16a", "8350e55f", "docs/lean-first/b16a/evidence/gate.json"),
    ("lf-16c", "c24aeab2", "docs/lean-first/b16c/evidence/gate.json"),
    ("lf-16d", "8cec935a", "docs/lean-first/b16d/evidence/gate.json"),
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(("git", *args), cwd=ROOT, text=True, capture_output=True,
                          check=True).stdout.strip()


def failures(data: dict) -> list[str]:
    return sorted({row["nodeid"].split("::", 1)[0] for row in data.get("failures", ())
                   if isinstance(row, dict) and isinstance(row.get("nodeid"), str)})


def write() -> dict:
    coverage = test_map.load(MAP)
    rows = []
    for label, short, gate_name in MERGES:
        merge = git("rev-parse", short)
        paths = git("diff", "--name-only", f"{merge}^1", merge).splitlines()
        changes = select_tests.read_changes(paths, base=f"{merge}^1", after=merge)
        plan = select_tests.select(changes=changes, base=coverage["commit"], coverage=coverage,
                                   assume_fresh=True)
        gate_path = ROOT / gate_name
        gate = json.loads(gate_path.read_text())
        if gate.get("status") != "passed" or not gate.get("counts", {}).get("collected"):
            raise ValueError(f"{gate_name} is not a passed full-suite gate")
        selected = sorted(plan["selected"])
        failed = failures(gate)
        rows.append({"item": label, "merge": merge, "paths": paths, "gate": gate_name,
                     "gate_sha256": digest(gate_path), "gate_commit": gate["commit_sha"],
                     "full_collected": gate["counts"]["collected"], "selected": selected,
                     "selected_count": len(selected), "full_count": plan["full_count"],
                     "full_failures": failed, "failures_outside_selection": sorted(set(failed) - set(selected))})
    return {"schema": 1, "method": "fixed-merge retrospective shadow with a fresh B2 v7 map",
            "map_sha256": digest(MAP), "map_commit": coverage["commit"], "merges": rows}


def check(data: dict) -> None:
    assert data["schema"] == 1 and len(data["merges"]) == 10
    assert data["map_sha256"] == digest(MAP)
    coverage = test_map.load(MAP)
    assert data["map_commit"] == coverage["commit"]
    assert len({row["merge"] for row in data["merges"]}) == 10
    for row in data["merges"]:
        gate_path = ROOT / row["gate"]
        gate = json.loads(gate_path.read_text())
        assert row["gate_sha256"] == digest(gate_path)
        assert row["gate_commit"] == gate["commit_sha"]
        assert gate["status"] == "passed"
        assert row["full_collected"] == gate["counts"]["collected"]
        assert row["full_failures"] == failures(gate)
        assert row["selected_count"] == len(row["selected"])
        assert row["full_count"] == len(coverage["tests"])
        assert row["failures_outside_selection"] == sorted(set(failures(gate)) - set(row["selected"]))
        assert not row["failures_outside_selection"], row["item"]
        assert row["paths"] == git("diff", "--name-only", f'{row["merge"]}^1', row["merge"]).splitlines()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        data = write()
        check(data)
        OUTPUT.write_text(json.dumps(data, indent=2) + "\n")
    else:
        check(json.loads(OUTPUT.read_text()))
    print("ten merged items: no saved full-suite failure outside selection")


if __name__ == "__main__":
    main()
