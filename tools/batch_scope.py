"""A batch's scope, written and checked from git: its base, its head, its commits and the paths it changes.

The saved scope of a batch's evidence (`docs/<track>/<batch>/evidence/scope.json`) is never trusted as written:
`git_scope` writes it and `scope_problems` recomputes it from git, so a dropped commit, a wrong base or a missing
path fails the batch's evidence check (arch-AR-4 review F3).
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess

from tools.batch_evidence import changed_since

SCOPE = ("base", "head", "commits", "files")
FULL_ID = re.compile(r"[0-9a-f]{40}")


def _git_out(cwd: Path | None, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "--no-optional-locks", "-c", "core.quotePath=false", *args], cwd=cwd,
                          capture_output=True, text=True)


def git_scope(base: str, head: str, cwd: Path | None = None) -> dict:
    """A batch's scope as git records it: its commits `base..head` without merges (newest first, each
    `{"hash", "subject"}`) and the paths it changes (sorted; renames as delete and add). The one
    writer and the one checker (`scope_problems`) of every saved scope."""
    log = _git_out(cwd, "log", "--no-merges", "-z", "--format=%H %s", f"{base}..{head}")
    if log.returncode:
        raise ValueError(f"git log {base}..{head}: {log.stderr.strip()}")
    commits = [dict(zip(("hash", "subject"), entry.split(" ", 1))) for entry in log.stdout.split("\0") if entry]
    return {"base": base, "head": head, "commits": commits, "files": sorted(changed_since(base, head, cwd))}


def scope_problems(scope: object, cwd: Path | None = None, main: str = "main") -> list[str]:
    """Why a saved scope is not the batch's: exactly the fields `SCOPE`; `base` and `head` full
    commit ids; `base` the merge base of `head` and `main` (once `head` is merged into `main`, only an
    ancestor of it); and `commits` and `files` exactly `git_scope(base, head)`. A dropped, added,
    reordered or edited commit or path is a problem, and so is a malformed scope: never a pass."""
    if not isinstance(scope, dict) or set(scope) != set(SCOPE):
        return [f"the scope holds exactly {', '.join(SCOPE)}"]
    base, head = scope["base"], scope["head"]
    if not all(isinstance(rev, str) and FULL_ID.fullmatch(rev) for rev in (base, head)):
        return ["the scope's base and head are full commit ids"]
    if _git_out(cwd, "merge-base", "--is-ancestor", head, main).returncode == 0:
        if _git_out(cwd, "merge-base", "--is-ancestor", base, head).returncode != 0:
            return [f"the scope's base {base[:12]} is not an ancestor of its head {head[:12]}"]
    else:
        merged = _git_out(cwd, "merge-base", head, main)
        if merged.returncode or merged.stdout.strip() != base:
            return [f"the scope's base {base[:12]} is not the merge base of its head {head[:12]} and {main} "
                    f"({merged.stdout.strip()[:12] or merged.stderr.strip()})"]
    try:
        actual = git_scope(base, head, cwd)
    except (ValueError, subprocess.CalledProcessError) as exc:
        return [f"the scope's commits cannot be listed: {exc}"]
    return [f"the scope's {field} are not git's {base[:12]}..{head[:12]} ({len(actual[field])} there)"
            for field in ("commits", "files") if scope[field] != actual[field]]
