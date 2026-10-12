"""A stale or incomplete batch gate cannot be reported as a pass."""
from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from tools.batch_evidence import REQUIRED_STAGES, git_scope, outside_report, problems, scope_problems

ROOT = Path(__file__).resolve().parents[1]
from tools.readings_batch_latency import make_case


HEAD = "a" * 40
GATE = {"commit_sha": HEAD, "dirty": False, "status": "passed", "stages": list(REQUIRED_STAGES),
        "counts": {"passed": 1, "rust_passed": 1}}
AB = {"head_commit": HEAD, "unlisted": 0, "unavailable_both": {},
      "records": {f"{name}/default": 1 for name in
                  ("probe", "conformance", "readings", "pilots", "discourse", "rights", "quantity")}}
LATENCY = {"head_commit": HEAD, "pass": True,
           "samples": {"readings": {"base_cpu_ms": 1, "head_cpu_ms": 1}}}


def test_complete_head_evidence_passes():
    errors = problems(HEAD, GATE, AB, LATENCY)
    assert errors == []


def test_latency_request_uses_the_public_readings_normalizer():
    # The raw corpus can carry explicit nulls; the public validator omits them
    # before Lean parses the request.
    item = {"environment": {"optional": None},
            "document": {"units": [{"id": "u", "kind": None}], "reading_sets": []}}
    assert make_case(item) == {"id": "readings-s1", "kind": "readings-validate",
                               "environment": {},
                               "document": {"units": [{"id": "u"}], "reading_sets": []}}


@pytest.mark.parametrize("which,change", [
    ("gate", {"commit_sha": "b" * 40}),
    ("gate", {"dirty": True}),
    ("gate", {"stages": list(REQUIRED_STAGES[:-1])}),
    ("comparison", {"head_commit": "b" * 40}),
    ("comparison", {"records": {"probe/default": 1}}),
    ("comparison", {"unavailable_both": {"readings/default": 1}}),
    ("latency", {"head_commit": "b" * 40}),
    ("latency", {"samples": {}}),
    ("latency", {"samples": {"readings": {"base_cpu_ms": 1, "head_cpu_ms": 1.21}}}),
])
def test_stale_or_incomplete_evidence_fails(which, change):
    values = {"gate": deepcopy(GATE), "comparison": deepcopy(AB), "latency": deepcopy(LATENCY)}
    values[which].update(change)
    assert problems(HEAD, values["gate"], values["comparison"], values["latency"])


# Follow-up of rd-6a-looprecheck1: a committed copy of the evidence comes in a report commit after the gated one,
# which may change nothing outside the report directory.

def test_a_report_commit_may_change_only_the_report_directory():
    assert outside_report(["docs/b/DELTA.md", "docs/b/gate-note.json"], "docs/b") == []
    assert outside_report(["docs/b/DELTA.md", "tools/x.py", "docs/bb/y"], "docs/b/") == [
        "a commit after the gate changes docs/bb/y, outside docs/b/",
        "a commit after the gate changes tools/x.py, outside docs/b/"]


def _git(repo, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                           *args], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()


def _commit(repo, files):
    for name, text in files.items():
        (repo / name).parent.mkdir(parents=True, exist_ok=True)
        (repo / name).write_text(text)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "c")
    return _git(repo, "rev-parse", "HEAD")


def _main(repo, tmp_path, gated, report):
    for name, value in (("gate", {**GATE, "commit_sha": gated}), ("ab", {**AB, "head_commit": gated}),
                        ("latency", {**LATENCY, "head_commit": gated})):
        (tmp_path / f"{name}.json").write_text(json.dumps(value))
    return subprocess.run([sys.executable, str(ROOT / "tools/batch_evidence.py"), gated, str(tmp_path / "gate.json"),
                           str(tmp_path / "ab.json"), str(tmp_path / "latency.json"), "--report-commit", report,
                           "--report-dir", "docs/b"], cwd=repo, capture_output=True, text=True)


def test_report_commit_check_reads_git(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    gated = _commit(repo, {"code.py": "1", "docs/b/DELTA.md": "a"})
    report = _commit(repo, {"docs/b/DELTA.md": "b", "docs/b/gate-note.json": "{}"})
    result = _main(repo, tmp_path, gated, report)
    assert result.returncode == 0, result.stdout
    assert f"report commit {report} changes only docs/b" in result.stdout
    code = _commit(repo, {"code.py": "2"})
    result = _main(repo, tmp_path, gated, code)
    assert result.returncode == 1
    assert "a commit after the gate changes code.py, outside docs/b/" in result.stdout
    # a rename out of the directory is a delete and an add, so the added path is caught
    _git(repo, "checkout", "-q", report)
    _git(repo, "mv", "docs/b/gate-note.json", "note.json")
    _git(repo, "commit", "-q", "-m", "mv")
    result = _main(repo, tmp_path, gated, _git(repo, "rev-parse", "HEAD"))
    assert result.returncode == 1 and "changes note.json" in result.stdout
    # the gated commit must be an ancestor of the report commit
    result = _main(repo, tmp_path, report, gated)
    assert result.returncode == 1 and "is not an ancestor" in result.stdout


# arch-AR-4 review F3: a saved scope (base, commits, changed files) was trusted as written, so a dropped commit
# or a wrong base passed the batch's evidence check. `scope_problems` recomputes it from git (`git_scope`).

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
    _git(repo, "-c", "core.editor=true", "merge", "-q", "--no-ff", "main", "-m", "sync")
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
