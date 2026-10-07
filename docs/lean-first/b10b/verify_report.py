"""Verify batch 10b's compact evidence against the gate and A/B JSON outputs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
BASE = "7345e3ed"
CORPORA = {"core": 58482, "norm": 2020, "profiles": 35713, "pilots": 294}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", type=Path, required=True)
    parser.add_argument("--fuzzer", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, default=Path("/tmp"))
    args = parser.parse_args()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    gate = json.loads(args.gate.read_text())
    assert gate["status"] == "passed" and gate["commit_sha"] == head and not gate["dirty"]
    assert gate["counts"].get("failed", 0) == 0
    assert gate["counts"]["passed"] + gate["counts"]["skipped"] == gate["counts"]["selected"]
    counts = {}
    for name, expected in CORPORA.items():
        row = json.loads((args.evidence_dir / f"lf10b-{name}-compare.json").read_text())
        assert sum(row["records"].values()) == row["totals"] == {"same": expected}
        assert row["unavailable_both"] == {} and row["unlisted"] == 0 and row["differences"] == []
        counts[name] = expected
    fuzz = json.loads(args.fuzzer.read_text())
    assert fuzz["base_commit"].startswith(BASE) and fuzz["head_commit"] == head
    assert len(fuzz["seeds"]) == 14 and all(not seed["differences"] for seed in fuzz["seeds"])
    baseline = (ROOT / "conformance/difffuzz-baseline.json").read_bytes()
    assert fuzz["baseline_sha256"] == hashlib.sha256(baseline).hexdigest()
    lines = subprocess.check_output(["git", "diff", "--numstat", f"{BASE}..HEAD"], cwd=ROOT, text=True)
    python_deleted = lean_added = 0
    for row in lines.splitlines():
        added, deleted, path = row.split("\t")
        if path.startswith("ve/") and path.endswith(".py"):
            python_deleted += int(deleted)
        if path.startswith("lean/") and path.endswith(".lean"):
            lean_added += int(added)
    print(json.dumps({"head": head, "gate": gate["status"], "suite": gate["counts"],
                      "ab_same": counts, "date_seeds": len(fuzz["seeds"]),
                      "python_lines_deleted": python_deleted, "lean_lines_added": lean_added}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
