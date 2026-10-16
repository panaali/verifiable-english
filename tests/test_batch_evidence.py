"""A stale or incomplete batch gate cannot be reported as a pass."""
from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from tools import gate_collection
from tools.batch_evidence import REQUIRED_STAGES, outside_report, problems

ROOT = Path(__file__).resolve().parents[1]
from tools.readings_batch_latency import make_case
from subprocesses import HANG_TIMEOUT


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


def test_only_identical_listed_unavailable_is_signed():
    row = {"corpus": "pilots", "authority": "default", "case": "p", "op": "document_check",
           "class": "unavailable", "base": {"timeout": HANG_TIMEOUT}, "head": {"timeout": HANG_TIMEOUT},
           "listed": True}
    ab = {**AB, "unavailable_both": {"pilots/default": 1}, "differences": [row]}
    errors = problems(HEAD, GATE, ab, LATENCY)
    assert errors == []
    for changed in ({"listed": False}, {"head": {"timeout": HANG_TIMEOUT + 1}},
                    {"base": {"exit": 0}}, {"case": "p2", "class": "verdict"}):
        bad = deepcopy(ab)
        bad["differences"][0].update(changed)
        errors = problems(HEAD, GATE, bad, LATENCY)
        assert errors


def test_identical_listed_unavailability_is_signed_by_r7():
    comparison = deepcopy(AB)
    comparison["unavailable_both"] = {"pilots/default": 1}
    comparison["differences"] = [{"corpus": "pilots", "authority": "default", "class": "unavailable",
                                  "listed": True, "base": {"timeout": 600}, "head": {"timeout": 600}}]
    errors = problems(HEAD, GATE, comparison, LATENCY)
    assert errors == []
    comparison["differences"][0]["head"] = {"timeout": 601}
    errors = problems(HEAD, GATE, comparison, LATENCY)
    assert errors
    comparison["differences"][0]["head"] = {"timeout": 600}
    comparison["differences"][0]["listed"] = False
    errors = problems(HEAD, GATE, comparison, LATENCY)
    assert errors


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


def _main(repo, tmp_path, gated, report, gate_data=None):
    for name, value in (("gate", {**GATE, "commit_sha": gated, **(gate_data or {})}),
                        ("ab", {**AB, "head_commit": gated}),
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


def test_f2_batch_evidence_checks_the_gate_note_when_present(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    gated = _commit(repo, {"code.py": "1"})
    ids = ["tests/a.py::test_a"]
    gate_data = {"tree_sha": _git(repo, "rev-parse", f"{gated}^{{tree}}"),
                 "collection": {"collected_zlib": gate_collection.encode_ids(ids)}}
    gate_collection.write_record(gated, ids, result={**GATE, "commit_sha": gated, **gate_data}, cwd=repo)
    assert _main(repo, tmp_path, gated, gated, gate_data).returncode == 0
    result = _main(repo, tmp_path, gated, gated)
    assert result.returncode == 1 and "gate evidence differs from its git note" in result.stdout


@pytest.mark.parametrize("note_kind", ["unparseable", "wrong commit", "wrong tree",
                                      "invalid collection", "base only"])
def test_f3_present_invalid_gate_note_fails_closed(tmp_path, note_kind):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    gated = _commit(repo, {"code.py": "1"})
    tree = _git(repo, "rev-parse", f"{gated}^{{tree}}")
    record = json.loads(gate_collection.record_text(gated, tree, ["tests/a.py::test_a"],
                                                    {"status": "passed"}))
    if note_kind == "unparseable":
        note = "malformed gate note"  # The review's executable F3 probe.
    else:
        if note_kind == "wrong commit":
            record["commit_sha"] = "b" * 40
        elif note_kind == "wrong tree":
            record["tree_sha"] = "b" * 40
        elif note_kind == "invalid collection":
            record["collection"]["collected_zlib"] = "***"
        elif note_kind == "base only":
            del record["status"]
        note = json.dumps(record)
    _git(repo, "notes", f"--ref={gate_collection.NOTES_REF}", "add", "-m", note, gated)
    result = _main(repo, tmp_path, gated, gated)
    assert result.returncode == 1, result.stdout
    assert "gate note" in result.stdout
