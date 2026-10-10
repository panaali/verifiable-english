"""RD-5's seeded bugs: plant each, run the test that should catch it, record the failure, restore the file.

    PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1 uv run --frozen python docs/readings-defaults/rd5/mutants.py

Writes `evidence/mutants.json`: per bug its file, the exact text replaced, the test, whether the test failed, the tail
of its output, and the file's SHA-256 before planting and after restoring (equal, so nothing planted remains).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = "usecases/udhr-pilot/run-20261010T1400Z"

MUTANTS = [
    {"name": "no-e24-for-plain-probe", "file": "ve/readings_route.py", "language": "Python",
     "behaviour": "a pair separated on a plain regulated predicate gets E24, not a CheckerUnavailable report",
     "old": 'if role not in ("obligation", "permission"):', "new": 'if role not in ("obligation", "permission", "plain"):',
     "test": "tests/test_readings_rd5_plain_probe.py::test_a_pair_probed_on_a_plain_predicate_gets_e24"},
    {"name": "e24-for-every-probe", "file": "ve/readings_route.py", "language": "Python",
     "behaviour": "a pair separated on a duty keeps E19",
     "old": 'if role not in ("obligation", "permission"):', "new": 'if role not in ("permission",):',
     "test": "tests/test_readings_rd5_plain_probe.py::test_a_pair_probed_on_a_duty_keeps_e19"},
    {"name": "main-frame-without-norm-defaults", "file": f"{RUN}/migrate.py", "language": "Python",
     "behaviour": "the main frame takes norm-defaults@0 beside readings@1, so Lean checks the document as a product",
     "old": 'ADDED_PROFILES = ("norm-defaults@0", "readings@1")', "new": 'ADDED_PROFILES = ("readings@1",)',
     "test": "tests/test_readings_rd5_udhr.py::test_the_migration_reproduces_the_committed_document"},
    {"name": "unknown-status-taken-as-an-answer", "file": f"{RUN}/witnesses.py", "language": "Python",
     "behaviour": "a witness's status is Lean's first answer that is not UNKNOWN",
     "old": '        if row["point_status"] != "UNKNOWN":', "new": '        if True:',
     "test": "tests/test_readings_rd5_udhr.py::test_one_sets_witnesses_replay_equal_in_its_component_and_alone"},
    {"name": "summary-share-before-for-after", "file": f"{RUN}/summary.py", "language": "Python",
     "behaviour": "SUMMARY.md states the saved after share",
     "old": "%) before, {after['share']['decided_bytes']} of {source} bytes",
     "new": "%) before, {before['share']['decided_bytes']} of {source} bytes",
     "test": "tests/test_readings_rd5_udhr.py::test_the_summary_is_rendered_from_the_saved_metrics"},
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(mutant):
    path = ROOT / mutant["file"]
    original = path.read_bytes()
    before = sha(path)
    text = original.decode()
    if text.count(mutant["old"]) != 1:
        raise SystemExit(f"mutants: {mutant['name']}: the text to replace is not in {mutant['file']} once")
    try:
        path.write_text(text.replace(mutant["old"], mutant["new"]))
        done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-x", mutant["test"]],
                              cwd=ROOT, capture_output=True, text=True, env={**os.environ, "VE_NATIVE_PREBUILT": "1"})
    finally:
        path.write_bytes(original)
    lines = [line for line in done.stdout.splitlines() if line.strip()]
    return {**mutant, "failed": done.returncode != 0, "exit": done.returncode, "output_tail": lines[-6:],
            "sha256_before": before, "sha256_restored": sha(path)}


def main():
    rows = [run(m) for m in MUTANTS]
    for r in rows:
        print(r["name"], "FAILED as expected" if r["failed"] else "NOT CAUGHT", r["sha256_before"] == r["sha256_restored"])
    out = ROOT / "docs/readings-defaults/rd5/evidence/mutants.json"
    out.write_text(json.dumps({"mutants": rows}, indent=1, ensure_ascii=False) + "\n")
    return 0 if all(r["failed"] and r["sha256_before"] == r["sha256_restored"] for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
