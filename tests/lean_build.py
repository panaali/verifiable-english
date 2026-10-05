"""The one way a test fixture builds named Lean targets.

`lean_build(*targets)` checks every name against `lean/lakefile.toml` (its `lean_lib` and
`lean_exe` entries, read with the TOML parser) before anything else, so a stale target fails
the fixture whether or not the gate prebuilt Lean (`VE_LEAN_PREBUILT`): a deleted executable
named by a fixture used to pass prebuilt runs and fail every local one with lake's
`unknown target`. With `VE_LEAN_PREBUILT` every named executable must exist; otherwise lake
builds them.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tomllib

from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean"
BIN = LEAN / ".lake/build/bin"


def lean_targets(lakefile: Path = LEAN / "lakefile.toml") -> dict[str, str]:
    """{target name: "lean_lib" or "lean_exe"} of the lakefile."""
    data = tomllib.loads(lakefile.read_text())
    return {entry["name"]: kind for kind in ("lean_lib", "lean_exe") for entry in data.get(kind, [])}


class UnknownTarget(AssertionError):
    """A fixture names a Lean target the lakefile does not declare."""


def check_targets(targets, lakefile: Path = LEAN / "lakefile.toml") -> dict[str, str]:
    known = lean_targets(lakefile)
    unknown = [t for t in targets if t not in known]
    if unknown:
        raise UnknownTarget(f"lean/lakefile.toml declares no target {', '.join(unknown)}")
    return {t: known[t] for t in targets}


def lean_build(*targets: str) -> Path:
    """Build `targets` (checked against the lakefile first) and return the bin directory.
    Without lake, existing executables are used as they are, and missing ones skip the test."""
    kinds = check_targets(targets)
    missing = [t for t, kind in kinds.items() if kind == "lean_exe" and not (BIN / t).is_file()]
    if os.environ.get("VE_LEAN_PREBUILT"):
        assert not missing, f"gate Lean build missing: {missing}"
        return BIN
    lake = shutil.which("lake")
    if lake is None:
        if missing:
            import pytest
            pytest.skip("lake is not available")
        return BIN
    build = subprocess.run([lake, "build", *targets], cwd=LEAN, capture_output=True, text=True,
                           timeout=HANG_TIMEOUT)
    assert build.returncode == 0, build.stdout + build.stderr
    return BIN
