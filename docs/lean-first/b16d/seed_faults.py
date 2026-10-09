"""Temporarily plant three batch 16d bugs and save the failing test results."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "ve/document.py"
CASES = [
    ("forged norm content accepted",
     '            require(same(unit["content"], authored["content"]))',
     '            pass  # seeded fault: norm content is not request-bound',
     "test_norm_content_is_bound_to_the_authored_node"),
    ("English fence lexicon omitted",
     '                case["lexicon"] = export(EnglishVocabulary(Environment(meta["environment"])))',
     '                pass  # seeded fault: no lexicon reaches the Lean English reader',
     "test_norm_defaults_readings_and_english_fence_are_decided_by_lean"),
    ("norm-defaults coverage omitted",
     '            answer["norm_defaults"] = {"gaps": gaps["gaps"], "findings": lines["findings"]}',
     '            pass  # seeded fault: the Lean report is dropped',
     "test_norm_defaults_coverage_uses_lean_report"),
]


def main() -> None:
    original = SOURCE.read_text()
    records = []
    for bug, before, after, test in CASES:
        assert original.count(before) == 1, bug
        try:
            SOURCE.write_text(original.replace(before, after, 1))
            env = {**os.environ, "VE_NATIVE_PREBUILT": "1", "UV_CACHE_DIR": "/tmp/uv-b16d-cache"}
            done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:xdist",
                                   f"tests/test_b16d_document.py::{test}"], cwd=ROOT,
                                  env=env, capture_output=True, text=True, check=False)
        finally:
            SOURCE.write_text(original)
        output = done.stdout + done.stderr
        if done.returncode == 0 or "1 failed" not in output:
            raise RuntimeError(f"seeded bug {bug} did not fail its test: {output[-1200:]}")
        records.append({"bug": bug, "test": test, "exit_code": done.returncode,
                        "failure_excerpt": output[-1800:]})
        print(f"{bug}: {test} failed as expected", flush=True)
    path = Path(__file__).resolve().parent / "evidence/mutants.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(records, indent=2) + "\n")


if __name__ == "__main__":
    main()
