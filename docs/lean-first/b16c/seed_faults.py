"""Plant each 16c boundary fault, prove its named test fails, then restore the source."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
CASES = [
    ("null treated as present", "ve/document.py",
     'has_content = authored.get("content") is not None',
     'has_content = "content" in authored',
     "tests/test_document_lean_switch.py::test_null_content_is_absent_on_the_lean_path"),
    ("forged checked formula accepted", "ve/document.py",
     'require(same(unit["content"], authored["content"]["ast"]))',
     'pass  # seeded fault: ignore the authored AST',
     "tests/test_document_lean_switch.py::test_identities_and_content_are_leans"),
    ("untyped checked formula", "ve/backends/lean_service_schema/document.json",
     '"content": {"$ref": "common.json#/$defs/generated_formula"}',
     '"content": true',
     "tests/test_document_lean_switch.py::test_document_schema_types_checked_content"),
]


def main() -> None:
    records = []
    for name, relative, before, after, test in CASES:
        path = ROOT / relative
        original = path.read_text()
        if original.count(before) != 1:
            raise RuntimeError(f"expected one mutation site for {name}")
        try:
            path.write_text(original.replace(before, after, 1))
            run = subprocess.run([sys.executable, "-m", "pytest", "-q", test], cwd=ROOT,
                                 capture_output=True, text=True, check=False)
        finally:
            path.write_text(original)
        output = run.stdout + run.stderr
        if run.returncode == 0 or "1 failed" not in output:
            raise RuntimeError(f"{name}: expected a test failure, got {run.returncode}: {output[-1000:]}")
        records.append({"bug": name, "file": relative, "test": test,
                        "exit_code": run.returncode, "failure_excerpt": output[-1200:]})
    evidence = ROOT / "docs/lean-first/b16c/evidence/mutants.json"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(json.dumps(records, indent=2) + "\n")
    print(f"{len(records)} seeded faults caught")


if __name__ == "__main__":
    main()
