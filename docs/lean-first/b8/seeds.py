"""Temporarily seed three reports relay defects and record the targeted failures."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "ve/reports.py"
OUT = ROOT / "docs/lean-first/b8/evidence/mutants.txt"
CASES = (
    ("identity", 'self.document_id = self.envelope["document_id"]',
     'self.document_id = "0" * 64',
     "tests/test_reports.py::test_nested_and_negated_scope_and_context_binding"),
    ("status", 'return next(row["status"] for row in self._statuses["units"] if row["id"] == unit["id"])',
     'return "CHECKED"',
     "tests/test_reports_status.py::test_nested_unformalised_kind_reaches_status_and_residual"),
    ("residual", 'return self._statuses["residual_lines"]', 'return {}',
     "tests/test_reports.py::test_report_premises_are_in_the_residual"),
)


def main() -> None:
    original = SOURCE.read_text()
    evidence = []
    environment = dict(os.environ, UV_CACHE_DIR="/tmp/ve-lf8-uv-cache", VE_NATIVE_PREBUILT="1")
    try:
        for name, old, replacement, test in CASES:
            if original.count(old) != 1:
                raise RuntimeError(f"{name}: expected one insertion site")
            SOURCE.write_text(original.replace(old, replacement))
            try:
                result = subprocess.run(["uv", "run", "--frozen", "pytest", "-q", test],
                                        cwd=ROOT, env=environment, capture_output=True, text=True)
            finally:
                SOURCE.write_text(original)
            if result.returncode == 0 or "FAILED" not in result.stdout:
                raise RuntimeError(f"{name}: test did not fail as expected: {result.stdout[-1000:]}")
            failures = [line for line in result.stdout.splitlines() if line.startswith("FAILED ")]
            evidence.append(f"{name}: exit={result.returncode}; test={test}\n" + "\n".join(failures))
    finally:
        SOURCE.write_text(original)
    OUT.write_text("\n\n".join(evidence) + "\n")
    print(OUT.read_text(), end="")


if __name__ == "__main__":
    main()
