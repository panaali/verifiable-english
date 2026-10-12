"""arch-AR-4 review F3: a saved scope (base, commits, changed files) was trusted as written, so a dropped
commit or a wrong base passed the batch's evidence check. `tools/batch_scope.py` recomputes it from git."""
from __future__ import annotations

import json
import subprocess

import pytest

from tools.batch_scope import git_scope, scope_problems


def _git(repo, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                           "-c", "core.editor=true", *args], cwd=repo, check=True, capture_output=True,
                          text=True).stdout.strip()


def _commit(repo, files):
    for name, text in files.items():
        (repo / name).write_text(text)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "c")
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def batch(tmp_path):
    """`main` with two commits, a batch branched from the first (two commits, a merge of main, a rename),
    and main's tip. Returns the repository, the batch's scope as git writes it, and main's commits."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    first = _commit(repo, {"a.py": "1", "old.py": "x"})
    _git(repo, "checkout", "-q", "-b", "batch")
    _commit(repo, {"b.py": "1"})
    _git(repo, "checkout", "-q", "main")
    tip = _commit(repo, {"m.py": "1"})
    _git(repo, "checkout", "-q", "batch")
    _git(repo, "merge", "-q", "--no-ff", "main", "-m", "sync")
    assert _git(repo, "merge-base", "HEAD", "main") == tip  # the synced batch's base is main's tip
    _git(repo, "mv", "old.py", "new.py")
    _git(repo, "commit", "-q", "-m", "rename: a subject with  two spaces")
    head = _git(repo, "rev-parse", "HEAD")
    base = _git(repo, "merge-base", "HEAD", "main")
    return repo, git_scope(base, head, repo), {"first": first, "tip": tip}


def test_a_scope_git_wrote_passes(batch):
    repo, scope, main = batch
    assert scope["base"] == main["tip"]
    assert [c["subject"] for c in scope["commits"]] == ["rename: a subject with  two spaces", "c"]
    assert scope["files"] == ["b.py", "new.py", "old.py"]  # the rename as a delete and an add; main's m.py is not
    assert scope_problems(json.loads(json.dumps(scope)), repo) == []


def _scope_mutants(scope, main):
    commits, files = scope["commits"], scope["files"]
    return {
        "a commit dropped": {**scope, "commits": commits[:-1]},
        "a commit added": {**scope, "commits": [*commits, {"hash": main["tip"], "subject": "c"}]},
        "commits reordered": {**scope, "commits": commits[::-1]},
        "a subject edited": {**scope, "commits": [{**commits[0], "subject": "other"}, *commits[1:]]},
        "no commits": {**scope, "commits": []},
        "a file dropped": {**scope, "files": files[:-1]},
        "a file added": {**scope, "files": [*files, "m.py"]},
        "files reordered": {**scope, "files": files[::-1]},
        "an older base": {**scope, "base": main["first"]},
        "a batch commit as base": {**scope, "base": commits[-1]["hash"]},
        "head as base": {**scope, "base": scope["head"]},
        "a short base": {**scope, "base": scope["base"][:12]},
        "a missing key": {k: v for k, v in scope.items() if k != "files"},
        "an extra key": {**scope, "extra": 1},
        **{f"{key} as {value!r}": {**scope, key: value} for key in scope
           for value in (7, True, None, [], {}, "")},
        "not a dict": [scope],
    }


def test_every_change_to_a_scope_is_a_problem_never_a_crash(batch):
    repo, scope, main = batch
    for name, mutant in _scope_mutants(scope, main).items():
        assert scope_problems(mutant, repo), name


def test_a_merged_batch_needs_only_an_ancestor_base(batch):
    """After the batch merges into main the merge base is its head: the saved base must then only be an
    ancestor of the head, and the commits and files still match git."""
    repo, scope, main = batch
    _git(repo, "checkout", "-q", "main")
    _git(repo, "merge", "-q", "--no-ff", "batch", "-m", "merge batch")
    assert scope_problems(scope, repo) == []
    assert scope_problems({**scope, "commits": scope["commits"][:-1]}, repo)
    assert scope_problems({**scope, "base": main["first"]}, repo)  # its commits are then not git's


def test_a_scope_collected_against_another_base_is_a_problem(batch):
    """Commits and files that match git for a wrong base (an older commit of main, or a commit of the batch)
    still fail: the base must be the merge base of the head and main."""
    repo, scope, main = batch
    for base in (main["first"], scope["commits"][-1]["hash"]):
        wrong = git_scope(base, scope["head"], repo)
        assert wrong != scope and scope_problems(wrong, repo), base
