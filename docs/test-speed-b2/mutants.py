"""Plant B2 bugs one at a time, run the rejecting test, and restore the source."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
from subprocesses import HANG_TIMEOUT  # noqa: E402

PY = str(ROOT / ".venv/bin/python")
PREAMBLE = 'import sys; sys.path[:0]=["tests","tools"]; import test_select_tests as t; '

CASES = [
    ("lean/ModeDeps.lean", "let rhs ← if mode == .document",
     "let rhs ← if mode == .rights then pure (mkConst ``VE.Norms.Run.runCaseReported) else if mode == .document",
     "tests/test_select_tests.py::test_compiled_mode_roots_regenerate_from_lean",
     PREAMBLE + "t.test_compiled_mode_roots_regenerate_from_lean()"),
    ("ve/backends/lean_service.py", '        sys.audit("ve.service.mode", mode)\n', "",
     "tests/test_select_tests.py::test_lean_service_emits_mode_before_dispatch",
     PREAMBLE + 'from _pytest.monkeypatch import MonkeyPatch; m=MonkeyPatch(); '
     't.test_lean_service_emits_mode_before_dispatch(m); m.undo()'),
    ("tools/test_map_recorder.py", '        elif event == "ve.service.mode":\n            _emit(["v", args[0]])\n', "",
     "tests/test_select_tests.py::test_recorder_tracks_each_service_request_mode",
     PREAMBLE + 'import pathlib,tempfile; t.test_recorder_tracks_each_service_request_mode('
     'pathlib.Path(tempfile.mkdtemp()))'),
    ("tools/select_tests.py", "        return matched | (users - known)\n",
     "        return users - known\n",
     "tests/test_select_tests.py::test_service_modes_narrow_only_known_recorded_users",
     PREAMBLE + 'import pathlib,tempfile; from _pytest.monkeypatch import MonkeyPatch; '
     'm=MonkeyPatch(); t.test_service_modes_narrow_only_known_recorded_users('
     'pathlib.Path(tempfile.mkdtemp()),m); m.undo()'),
]


def run(code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([PY, "-c", code], cwd=ROOT, text=True, capture_output=True,
                          env={**os.environ, "VE_NATIVE_PREBUILT": "1"}, timeout=HANG_TIMEOUT)


def main() -> None:
    records = []
    for name, old, mutant, test, code in CASES:
        path = ROOT / name
        original = path.read_text()
        if original.count(old) != 1:
            raise RuntimeError(f"seed anchor missing or ambiguous in {name}")
        clean = run(code)
        if clean.returncode:
            raise RuntimeError(f"clean test failed for {name}: {clean.stderr[-1000:]}")
        try:
            path.write_text(original.replace(old, mutant, 1))
            failed = run(code)
        finally:
            path.write_text(original)
        if failed.returncode == 0:
            raise RuntimeError(f"mutant was not caught: {name}")
        records.append({"file": name, "test": test, "seeded_bug": mutant.strip(),
                        "mutant_exit": failed.returncode, "restored_exit": clean.returncode,
                        "failure_excerpt": failed.stderr.splitlines()[-1] if failed.stderr else failed.stdout[-200:]})
    output = ROOT / "docs/test-speed-b2/evidence/mutants.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"schema": 1, "mutants": records}, indent=2) + "\n")
    print(f"{len(records)} seeded bugs caught; sources restored")


if __name__ == "__main__":
    main()
