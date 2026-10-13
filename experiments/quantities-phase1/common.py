"""Shared paths and the one way phase-1 scripts run `ve` (quantities plan, phase 1).

Every `ve` run goes through `run_ve` or `ve_python`: a checkout of main with consistent builds (the 2026-10-13
0600Z pilot checkout; `ve-integration` has a stale `ve_service` build)
with its own interpreter, `-P` so this worktree's `ve/` is never imported, and an address-space limit of
6 GiB (`prlimit --as=6442450944`). Pilot inputs are read, never written.

That checkout moves (the pilot commits its runs to it), so `check_main` pins it: every tracked file outside the
pilot's own directory must equal main at `MAIN_PIN`, and nothing tracked may be modified in the working tree. Builds
are untracked, so `lean/checkers.lock` (tracked, pinned) is what ties them to the code.
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
# The next pilot run (2026-10-13 0600Z), read for what it changes in the units phase 1 measures.
CONSTITUTION_NEXT = PILOTS / "claude-constitution" / "run-20261013T0600Z"
UDHR_NEXT = PILOTS / "udhr" / "run-20261013T0600Z"
MAIN = Path("/home/seyran/code/ve-pilot-20261013T0600Z")
MAIN_PIN = "406736a47beb0b3dc27f035f67cd53b6a8eec8a0"
MAIN_PILOT_DIR = "usecases/claude-constitution-pilot/"
EVIDENCE = REPO / "docs" / "research" / "evidence" / "quantities"
MEMORY_LIMIT = "6442450944"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(MAIN), *args], check=True, capture_output=True, text=True).stdout.strip()


def main_head() -> str:
    return _git("rev-parse", "HEAD")


def check_main() -> dict:
    """Fail unless MAIN's code is main at MAIN_PIN: only the pilot's own directory may differ, and nothing tracked
    is modified."""
    changed = [p for p in _git("diff", "--name-only", MAIN_PIN, "HEAD").splitlines() if not p.startswith(MAIN_PILOT_DIR)]
    dirty = _git("status", "--porcelain", "--untracked-files=no")
    if changed or dirty:
        raise SystemExit(f"{MAIN} is not main at {MAIN_PIN}: changed {changed[:10]}, modified {dirty[:500]!r}")
    return {"head": main_head(), "pin": MAIN_PIN, "differs_from_pin_only_under": MAIN_PILOT_DIR,
            "checkers_lock_sha256": sha256(MAIN / "lean" / "checkers.lock")}


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
