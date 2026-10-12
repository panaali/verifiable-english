"""Prove the readings-route response checks fail on seeded faults, then restore every source."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PARITY = "tests/test_lean_service_schema.py::test_readings_route_shape_agrees_with_lean_on_empty_names_and_repeated_over"
UNIQUE = "tests/test_lean_service_schema.py::test_unique_string_lists_refuse_duplicate_rule_names"
SHAPE = "lean/ResponseShape/Schemas/ReadingsRoute.lean"
CASES = [
    ("fill label can be empty", SHAPE,
     '("label", n [str, .minLength 1]), ("ast", ref "common.json#/$defs/generated_formula")',
     '("label", str), ("ast", ref "common.json#/$defs/generated_formula")', PARITY, True),
    ("conflict target can be empty", SHAPE,
     '("targets", n [arr, .items (n [str, .minLength 1])]),',
     '("targets", ref "common.json#/$defs/strings"),', PARITY, True),
    ("a repeated over name is accepted by Lean", SHAPE,
     '("over", n [ref "common.json#/$defs/strings", .uniqueStrings]),',
     '("over", ref "common.json#/$defs/strings"),', PARITY, True),
    ("a repeated over name is accepted by Python", "ve/backends/service_schema.py",
     'len(value) != len(set(value)):', 'False:', UNIQUE, False),
]


def run(command: list[str], *, cwd: Path = ROOT, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, check=False, timeout=1800)


def build(env: dict) -> None:
    done = run(["lake", "build", "ve_response_decode"], cwd=ROOT / "lean", env=env)
    if done.returncode:
        raise RuntimeError("Lean decoder build failed:\n" + (done.stdout + done.stderr)[-3000:])


def main() -> None:
    env = {**os.environ, "PATH": str(Path.home() / ".elan/bin") + os.pathsep + os.environ.get("PATH", ""),
           "UV_CACHE_DIR": "/tmp/uv-oom-cache", "XDG_CACHE_HOME": "/tmp/ve-oom-cache",
           "VE_LEAN_PREBUILT": "1", "VE_NATIVE_PREBUILT": "1"}
    records = []
    try:
        for name, relative, before, after, test, lean in CASES:
            path = ROOT / relative
            original = path.read_text()
            if original.count(before) != 1:
                raise RuntimeError(f"{name}: expected one mutation site, found {original.count(before)}")
            try:
                path.write_text(original.replace(before, after, 1))
                if lean:
                    build(env)
                done = run(["uv", "run", "pytest", "-q", "-p", "no:cacheprovider", test], env=env)
            finally:
                path.write_text(original)
            output = done.stdout + done.stderr
            if done.returncode == 0 or "1 failed" not in output:
                raise RuntimeError(f"{name}: expected one failing test:\n{output[-3000:]}")
            records.append({"bug": name, "file": relative, "test": test,
                            "exit_code": done.returncode, "failure_excerpt": output[-1000:]})
            print(f"caught: {name}", flush=True)
    finally:
        build(env)
    evidence = ROOT / "docs/oom-rootcause/evidence/relay-mutants.json"
    evidence.write_text(json.dumps(records, indent=2) + "\n")
    print(f"{len(records)} relay faults caught")


if __name__ == "__main__":
    main()
