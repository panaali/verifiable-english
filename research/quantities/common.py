"""Shared paths and the one way phase-1 scripts run `ve` (quantities plan, phase 1).

Every `ve` run goes through `run_ve` or `ve_python`: a checkout of main with consistent builds (the 2026-10-13
0600Z pilot checkout at main 406736a4; `ve-integration` has a stale `ve_service` build)
with its own interpreter, `-P` so this worktree's `ve/` is never imported, and an address-space limit of
6 GiB (`prlimit --as=6442450944`). Pilot inputs are read, never written.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PILOTS = Path("/home/seyran/code/manage-agents/pilots")
CONSTITUTION_RUN = PILOTS / "claude-constitution" / "run-20261012T1800Z"
UDHR_RUN = PILOTS / "udhr" / "run-20261012T1800Z"
MAIN = Path("/home/seyran/code/ve-pilot-20261013T0600Z")
EVIDENCE = REPO / "docs" / "research" / "evidence" / "quantities"
MEMORY_LIMIT = "6442450944"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main_head() -> str:
    return subprocess.run(["git", "-C", str(MAIN), "rev-parse", "HEAD"], check=True, capture_output=True,
                          text=True).stdout.strip()


def _env() -> dict:
    # VE_RUST_TIMEOUT is a hang guard only (Rust's work limits are its evaluation budgets): the machine runs other
    # sessions, and the 5 s default fails searches under load (seen once at load average 62).
    return {**os.environ, "VE_NATIVE_PREBUILT": "1", "VE_RUST_TIMEOUT": "600",
            "PATH": f"{Path.home() / '.elan' / 'bin'}:{os.environ.get('PATH', '')}"}


def ve_python(args: list[str], stdin: str | None = None) -> subprocess.CompletedProcess:
    """Run main's interpreter (with main's `ve` importable) under the memory limit, from main's checkout."""
    command = ["prlimit", f"--as={MEMORY_LIMIT}", str(MAIN / ".venv" / "bin" / "python"), "-P", *args]
    return subprocess.run(command, cwd=MAIN, env=_env(), input=stdin, capture_output=True, text=True)


def run_ve(args: list[str]) -> subprocess.CompletedProcess:
    """`python -m ve <args>` on main, under the memory limit."""
    return ve_python(["-m", "ve", *args])


def split_document(path: Path) -> tuple[dict, bytes]:
    """The front matter of a `ve-document@1` file and its body bytes."""
    data = path.read_bytes()
    assert data.startswith(b"---\n"), path
    front, body = data[4:].split(b"\n---\n", 1)
    return json.loads(front), body


def write_document(path: Path, meta: dict, body: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False, indent=1).encode() + b"\n---\n" + body)


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
