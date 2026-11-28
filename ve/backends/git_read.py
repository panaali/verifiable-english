"""Read-only git queries for the provenance block of an answer (ve/provenance.py): which commit a checkout is at,
whether its tracked files differ from it, and a file as a commit holds it. Only the backend starts processes
(tests/test_assurance_manifest.py); git here never decides an answer, it only names what the answer was made from."""
from __future__ import annotations

from pathlib import Path
import subprocess


def output(root: Path, *args: str) -> bytes | None:
    """The standard output of `git -C root ARGS` (a local read: no deadline, as the suite's hang guard asks of waits
    that only guard against a hang, tests/test_hang_guards.py); None when git is missing or fails."""
    try:
        done = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout if done.returncode == 0 else None
