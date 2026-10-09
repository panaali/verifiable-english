"""Seed RD-4b regressions one at a time, run their tests, restore source, and save the failing results.

Usage: .venv/bin/python tools/readings_defaults_rd4b_mutants.py --out PATH
The command runs synchronously; it never leaves a mutant in the worktree, even when a test raises.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

from tools import nested_pytest


ROOT = Path(__file__).resolve().parents[1]
MUTANTS = [
    ("companion-route", "ve/readings_components.py", "return type(reading_sets) is list and any(",
     "return False and type(reading_sets) is list and any(",
     "tests/test_readings_components_document.py::test_fc1_check_three_components_conflict_free_with_a_model"),
    ("product-verdict", "ve/readings_components.py", 'return {**row["result"], "sentence": row["sentence"],',
     'return {**row["result"], "verdict": "ALL", "sentence": row["sentence"],',
     "tests/test_readings_components_document.py::test_fc17_all_is_gated_on_every_other_component"),
    ("response-unit-binding", "ve/readings_components.py", '_need(entry["units"] == checked_units)',
     '_need(set(entry["units"]) <= set(checked_units))',
     "tests/test_readings_components_lean.py::test_every_emptied_or_duplicated_row_list_is_refused"),
    ("english-conclusion-slot", "ve/readings_components.py", 'wordings[row["component"]].slots.conclusions.add(slot)',
     'pass  # seeded fault: the canonical conclusion is not passed to W7',
     "tests/test_readings_components_document.py::test_a_query_typed_in_one_component_is_all_with_e30"),
    ("split-citation-content", "ve/readings_components.py", 'shown["content"] = None',
     'shown["content"] = by_id[unit["id"]]["content"]',
     "tests/test_readings_components_document.py::test_fc11_a_narrowing_is_listed_under_its_component_only"),
]


def run(out: Path) -> None:
    results = []
    for name, relative, old, new, test in MUTANTS:
        path = ROOT / relative
        source = path.read_bytes()
        before = hashlib.sha256(source).hexdigest()
        text = source.decode()
        if text.count(old) != 1:
            raise RuntimeError(f"{name}: expected exactly one mutation site")
        path.write_text(text.replace(old, new, 1))
        try:
            cmd = nested_pytest.command(["-q", test, "--tb=short"])
            proc = subprocess.run(cmd, cwd=ROOT, env=nested_pytest.environment(os.environ),
                                  capture_output=True, text=True, check=False)
        finally:
            path.write_bytes(source)
        if hashlib.sha256(path.read_bytes()).hexdigest() != before:
            raise RuntimeError(f"{name}: source was not restored")
        output = proc.stdout + proc.stderr
        if proc.returncode == 0 or f"FAILED {test}" not in output:
            raise RuntimeError(f"{name}: its targeted test did not fail as expected:\n{output[-3000:]}")
        results.append({"name": name, "file": relative, "old": old, "new": new,
                        "test": test, "exit_code": proc.returncode,
                        "failed_id_present": True, "source_sha256_after_restore": before,
                        "failure_tail": output[-1800:]})
        print(f"{name}: {test} failed with exit {proc.returncode}; restored {relative}", flush=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"mutants": results}, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    run(parser.parse_args().out)
