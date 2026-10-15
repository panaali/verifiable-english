"""The one-shot English executable has a distinct root and preserves its wire bytes."""

import json
from pathlib import Path
import subprocess
import tomllib

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import lean_build


ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / "tests/data/english_run_root_cases.json").read_text())


def test_executable_roots_are_outside_library_modules():
    lakefile = tomllib.loads((ROOT / "lean/lakefile.toml").read_text())
    libraries = {entry["name"] for entry in lakefile["lean_lib"]}
    for executable in lakefile["lean_exe"]:
        module = executable.get("root", executable["name"])
        path = ROOT / "lean" / (module.replace(".", "/") + ".lean")
        assert path.is_file(), executable["name"]
        assert all(module != lib and not module.startswith(lib + ".") for lib in libraries), executable["name"]


def test_differential_harness_uses_executable_root():
    from conformance import english_lean

    lakefile = tomllib.loads((ROOT / "lean/lakefile.toml").read_text())
    [root] = [entry["root"] for entry in lakefile["lean_exe"] if entry["name"] == "ve_english_run"]
    assert english_lean.RUNNER == root + ".lean"


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
def test_english_runner_bytes_match_base(case, tmp_path):
    binary = lean_build("ve_english_run") / "ve_english_run"
    payload = case["input"].encode()
    if case["mode"] == "file":
        path = tmp_path / "english.json"
        path.write_bytes(payload)
        args, stdin = [str(binary), str(path)], None
    else:
        args, stdin = [str(binary)], payload
    result = subprocess.run(args, input=stdin, capture_output=True, timeout=HANG_TIMEOUT)
    assert (result.returncode, result.stdout, result.stderr) == (
        case["returncode"], case["stdout"].encode(), case["stderr"].encode())
