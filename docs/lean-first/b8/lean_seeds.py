"""Build two temporary Lean defects and prove the reports tests reject them."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[3]
LEAN = ROOT / "lean"
LOCK = LEAN / "checkers.lock"
SERVICE = LEAN / ".lake/build/bin/ve_service"
OUT = ROOT / "docs/lean-first/b8/evidence/mutants.txt"
CASES = (
    ("status text", LEAN / "VE/Attribution/Run.lean",
     'reports ++ scopedLines ++ bridges ++ [s!"DOCUMENT: {status.render}"]', '[]',
     "tests/test_reports_status.py::test_nested_unformalised_kind_reaches_status_and_residual"),
    ("bridge diagnostics", LEAN / "VE/Attribution/Admission.lean",
     "let diagnosis := wires.findSome? (bridgeLeafDiagnostic D)",
     "let diagnosis : Option String := none",
     "tests/test_reports.py::test_w2_nested_bridge_needs_a_record"),
)


def build(env: dict[str, str]) -> None:
    result = subprocess.run(["lake", "build", "ve_service"], cwd=LEAN, env=env,
                            capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout[-2000:] + result.stderr[-2000:])


def main() -> None:
    original_lock = LOCK.read_text()
    originals = {path: path.read_text() for _, path, _, _, _ in CASES}
    environment = dict(os.environ, PATH=str(Path.home() / ".elan/bin") + ":" + os.environ["PATH"],
                       UV_CACHE_DIR="/tmp/ve-lf8-uv-cache", VE_NATIVE_PREBUILT="1")
    evidence = OUT.read_text().rstrip() + "\n\n"
    try:
        for name, path, old, replacement, test in CASES:
            if originals[path].count(old) != 1:
                raise RuntimeError(f"{name}: expected one insertion site")
            path.write_text(originals[path].replace(old, replacement))
            build(environment)
            lock = json.loads(original_lock)
            lock["ve_service"].append(hashlib.sha256(SERVICE.read_bytes()).hexdigest())
            LOCK.write_text(json.dumps(lock, indent=2) + "\n")
            result = subprocess.run(["uv", "run", "--frozen", "pytest", "-q", test], cwd=ROOT,
                                    env=environment, capture_output=True, text=True)
            if result.returncode == 0 or "FAILED" not in result.stdout:
                raise RuntimeError(f"{name}: test did not fail as expected: {result.stdout[-1000:]}")
            failures = [line for line in result.stdout.splitlines() if line.startswith("FAILED ")]
            evidence += f"{name}: exit={result.returncode}; test={test}\n" + "\n".join(failures) + "\n\n"
            path.write_text(originals[path])
            LOCK.write_text(original_lock)
    finally:
        for path, source in originals.items():
            path.write_text(source)
        LOCK.write_text(original_lock)
        build(environment)
    OUT.write_text(evidence.rstrip() + "\n")
    print("\n".join(evidence.splitlines()[-9:]))


if __name__ == "__main__":
    main()
