"""Saved commits found again by their content: a commit id names one lineage, its tree and subject every copy.

The GitHub export rewrites every commit and keeps every tree and message, so a test that checks saved history saves
each commit's tree with its subject and finds it here, in HEAD's history; a saved commit id is a record, never a
revision handed to Git. A tree alone is not enough: a merge into `main` has the tree of the branch's last merge of
`main`, so the pair (tree, subject) names the commit.
"""
from __future__ import annotations

from functools import cache
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(*args: str) -> list[str]:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()


@cache
def _history(head: str) -> dict[tuple[str, str], list[str]]:
    found: dict[tuple[str, str], list[str]] = {}
    for line in git("log", head, "--format=%H %T %s"):
        commit, tree, subject = line.split(" ", 2)
        found.setdefault((tree, subject), []).append(commit)
    return found


def commit_of(tree: str, subject: str) -> str:
    """The one commit in HEAD's history with this tree and subject."""
    [head] = git("rev-parse", "HEAD")
    commits = _history(head).get((tree, subject), [])
    if len(commits) != 1:
        raise LookupError(f"{len(commits)} commits in HEAD's history have tree {tree} and subject {subject!r}")
    return commits[0]


def log(base: str, head: str, *options: str) -> list[tuple[str, str]]:
    """(tree, subject) of each commit of `base..head`, in `git log` order with `options`."""
    return [tuple(line.split(" ", 1)) for line in git("log", *options, "--format=%T %s", f"{base}..{head}")]
