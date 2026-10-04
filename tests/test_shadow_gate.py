"""Stage 3 days, the count and Gate 3: fixtures G1 to G21, T2 and T3 (docs/spec/mig3.md 8.4, 8.6).

On a commit history and run directories made for the test.  The days are
numbered 1 to 14 (2026-10-01 to 2026-10-14); unless a test says otherwise every
day is clean, no commit changes a classed path, every commit that needs a merge
run has a complete one, `day` is run after the day has ended and its runs have
finished, and no finding is open.
"""
from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import subprocess

import pytest

from tools import shadow_gate
from ve.backends.dispatch import DISPATCH_NAMES

ROOT = Path(__file__).resolve().parents[1]
CORPORA = shadow_gate.CORPUS_IDS
LATER = "2026-10-20T00:00:00Z"
DECODER = "lean/VE/Bridge.lean"


def day(k: int) -> str:
    return f"2026-10-{k:02d}" if k > 0 else "2026-09-30"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()


def write(repo: Path, files: dict[str, str]) -> None:
    for path, text in files.items():
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)


def commit(repo: Path, files: dict[str, str], message: str) -> str:
    write(repo, files)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def registry():
    return [{"id": name, "plan": name, "command": ["true"], "expected_exit": 0, "min_cases": 1,
             "min_compared": 1, "calibration": f"cal-{name}", "merge": name == "suite"} for name in CORPORA]


class World:
    """A repository with one nightly commit per day and a runs directory."""

    def __init__(self, tmp_path: Path, extra: dict[int, list[dict]] | None = None):
        self.repo, self.runs = tmp_path / "repo", tmp_path / "runs"
        self.repo.mkdir()
        self.runs.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "test@example.com")
        git(self.repo, "config", "user.name", "Test")
        self.base = commit(self.repo, {
            "lean/checkers.lock": json.dumps({"ve_service": ["svc"], "rust_jsonl": ["rst"]}),
            "conformance/shadow/corpora.json": json.dumps(registry()),
            "conformance/shadow/wording.json": "[]", "conformance/shadow/triage.json": "[]",
            "conformance/shadow/changes.json": "[]",
            "ve/assurance-manifest.json": json.dumps({"lean_decoders": {"files": [{"file": DECODER}]}}),
            "ve/backends/dispatch.py": "def execute(*a, **k):\n    pass\n",
            "ve/parser.py": "from .backends.dispatch import execute\n\ndef parse():\n    return execute('parse', {}, None)\n",
            "ve/english.py": "", "ve/wire.py": "", "ve/printer.py": "",
            "lean/VE/Service/Graph.lean": "", DECODER: "", "tests/test_x.py": "", "docs/a.md": "",
        }, "base")
        self.nightly: dict[int, str] = {}
        self.extra: dict[int, list[str]] = {}
        for k in range(1, 15):
            for change in (extra or {}).get(k, ()):
                self.extra.setdefault(k, []).append(commit(self.repo, change["files"], change.get("message", "x")))
            self.nightly[k] = commit(self.repo, {f"docs/day-{k}.md": str(k)}, f"day {k}")
        self.serial = 0

    # --- runs ---------------------------------------------------------------------------
    def run(self, k: int, corpus: str, *, trigger="nightly", at=None, minute=5, ops=None, records=(),
            final=True, finished=True, seed=None, extra_ops=None, **meta):
        self.serial += 1
        name = f"{corpus}-{self.serial:04d}"
        directory = self.runs / name
        directory.mkdir()
        started = f"{day(k)}T{minute // 60:02d}:{minute % 60:02d}:{self.serial % 60:02d}Z"
        data = {"run": name, "corpus": corpus, "commit": at or self.nightly[k], "trigger": trigger,
                "started": started, "finished": f"{day(k)}T20:00:00Z" if finished else None,
                "exit": 0, "cases": 10, "builds": {"ve_service": "svc", "rust_jsonl": "rst"},
                "seed": seed if seed is not None else (int(day(k).replace("-", "")) if corpus == "fuzz-nightly" else None),
                "webapp_commit": None, "stderr_faults": 0, "clean": {"started": True, "finished": True}, **meta}
        (directory / "run.json").write_text(json.dumps(data))
        if ops is None:
            ops = {op: {"compared": 1} for op in (DISPATCH_NAMES if corpus == "suite" else ("evaluate",))}
        for op, counts in (extra_ops or {}).items():
            ops.setdefault(op, {}).update(counts)
        full = {}
        for op, counts in ops.items():
            cell = {name: 0 for name in ("compared", "agree", "recorded_only", "zero_tolerance",
                                         "completion_failures", "unavailable_other", "lean_only", "recorder_faults")}
            cell.update(counts)
            cell.setdefault("uncompared", {})
            full[op] = cell
        tally = {"run": name, "pid": 1, "nonce": "n", "started": started, "final": final, "calls": 1, "ops": full}
        (directory / "tally-1-n.json").write_text(json.dumps(tally))
        if records:
            (directory / "records-1-n.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
        (directory / "stderr.txt").write_text("")
        return directory

    def clean_day(self, k: int, skip=(), **changes):
        for corpus in CORPORA:
            if corpus not in skip:
                self.run(k, corpus, **changes.get(corpus, {}))

    def clean_days(self, days=range(1, 15), special=None):
        special = special or {}
        for k in days:
            if k in special:
                special[k](self)
            else:
                self.clean_day(k)

    def merge_runs(self, complete=True):
        for k, commits in self.extra.items():
            for c in commits:
                self.run(k - 1 if k > 1 else k, "suite", trigger="merge", at=c, minute=600,
                         **({} if complete else {"exit": 1}))

    # --- the tool -------------------------------------------------------------------------
    def tool(self, *args: str, now: str = LATER) -> tuple[int, str]:
        out = io.StringIO()
        with redirect_stdout(out):
            status = shadow_gate.main([*args, "--root", str(self.repo), "--runs", str(self.runs), "--now", now])
        return status, out.getvalue()

    def days(self, ks=range(1, 15)) -> dict[int, tuple[int, str]]:
        return {k: self.tool("day", day(k)) for k in ks}

    def gate(self, k=14) -> tuple[int, str]:
        return self.tool("gate", day(k))

    def set(self, name: str, data) -> None:
        (self.repo / "conformance/shadow" / name).write_text(json.dumps(data))

    def entry(self, k: int) -> dict:
        return json.loads((self.repo / f"conformance/shadow/ledger/{day(k)}.json").read_text())


def record(kind="divergence", op="evaluate", classes=("verdict",), digest="d" * 64, sides=None):
    row = {"kind": kind, "op": op, "input_digest": digest, "python": {"value": True}, "lean": {"value": False},
           "rust": None, "class": list(classes), "python_ms": 1.0, "backend_ms": 1.0, "run": None, "test": None,
           "input": None}
    if kind == "unavailable":
        row["sides"] = sides or ["backend"]
    return row


def count_of(text: str) -> int:
    line = next(line for line in text.splitlines() if line.startswith("The count of clean days in a row is "))
    return int(line.split(" is ")[1].split(",")[0])


def triage_entry(id_, cause, *, op="evaluate", kind="divergence", classes=("verdict",), digest="d" * 64,
                 fix=None, evidence="evidence", note="note", first_day=None):
    return {"id": id_, "first_day": first_day or day(1), "op": op, "kind": kind, "class": list(classes),
            "input_digest": digest, "cause": cause, "fix": fix, "evidence": evidence, "note": note}


def change(commit_, *files):
    lines = [{"path": path, "class": klass, "reason": f"{path}: {klass} for the test"} for path, klass in files]
    return {"commit": commit_, "class": "restart" if any(c == "restart" for _, c in files) else "no-restart",
            "reason": "test", "files": lines, "signed": "DRI"}


# --- 8.4 ---------------------------------------------------------------------------------

def test_g1_fourteen_clean_days_meet_the_gate(tmp_path):
    world = World(tmp_path)
    world.clean_days()
    assert all(status == 0 for status, _ in world.days().values())
    status, text = world.gate()
    assert status == 0 and count_of(text) == 14
    assert (f"Gate 3 is met on {day(14)} at commit {world.nightly[14]}: the 14 days from {day(1)} to {day(14)} "
            f"are clean, no restart event is among the commits after {world.nightly[1]} up to "
            f"{world.nightly[14]}, and every finding is closed.") in text
    assert "On 2026-10-07, every corpus ran in shadow at commit" in world.days([7])[7][1]


def test_g2_thirteen_days(tmp_path):
    world = World(tmp_path)
    world.clean_days(range(2, 15))
    world.days(range(2, 15))
    status, text = world.gate()
    assert status == 1 and count_of(text) == 13
    assert "the count is 13, and 14 are needed" in text


def test_g3_a_corpus_without_a_complete_run(tmp_path):
    world = World(tmp_path)
    world.clean_days(special={7: lambda w: w.clean_day(7, skip=("english",))})
    results = world.days()
    status, text = results[7]
    assert status == 1
    assert text.splitlines()[0] == f"{day(7)} is not a clean day: the corpus english has no complete run in the nightly."
    assert count_of(world.gate()[1]) == 7


def test_g4_a_zero_tolerance_record_in_a_merge_run(tmp_path):
    world = World(tmp_path, extra={7: [{"files": {"tests/test_x.py": "changed"}}]})
    world.clean_days()
    [merge_commit] = world.extra[7]
    world.run(6, "suite", trigger="merge", at=merge_commit, minute=600)
    world.run(7, "suite", trigger="merge", at=merge_commit, minute=60, records=[record()],
              extra_ops={"evaluate": {"zero_tolerance": 1}})
    results = world.days()
    assert results[7][0] == 1 and "1 compared calls differ in a zero-tolerance class" in results[7][1]
    assert count_of(world.gate()[1]) == 7


def test_g5_a_message_difference_does_not_cost_the_day(tmp_path):
    world = World(tmp_path)
    world.clean_days(special={7: lambda w: w.clean_day(7, baseline={
        "records": [record(classes=("diagnostic-message",))], "extra_ops": {"evaluate": {"recorded_only": 1}}})})
    assert world.days()[7][0] == 0
    assert count_of(world.gate()[1]) == 14


@pytest.mark.parametrize("sides,entry_cause,clean,met", [
    (["backend"], None, False, False),
    (["python"], "operational", True, True),
    (["backend", "python"], "operational", True, True),
    (["backend", "python"], None, True, False),
])
def test_g6_unavailable_calls(tmp_path, sides, entry_cause, clean, met):
    world = World(tmp_path)
    counts = {"completion_failures": 1} if sides == ["backend"] else {"unavailable_other": 1}
    world.clean_days(special={7: lambda w: w.clean_day(7, baseline={
        "records": [record("unavailable", classes=(), sides=sides)], "extra_ops": {"evaluate": counts}})})
    world.set("triage.json", [triage_entry("F1", entry_cause, kind="unavailable", classes=(), first_day=day(7))])
    assert (world.days()[7][0] == 0) is clean
    status, text = world.gate()
    if not clean:
        assert count_of(text) == 7
    elif met:
        assert status == 0
    else:
        assert status == 1 and "finding F1 is open" in text


@pytest.mark.parametrize("where,with_entry,expected", [("after", True, 9), ("before", True, 10), ("after", False, 9)])
def test_g7_an_adapter_fix_restarts_the_count(tmp_path, where, with_entry, expected):
    k = 6 if where == "after" else 5
    world = World(tmp_path, extra={k: [{"files": {"ve/parser.py": "# fixed\n"}}]})
    [fix] = world.extra[k]
    world.clean_days()
    world.merge_runs()
    world.set("triage.json", [triage_entry("F1", "adapter", fix=fix)])
    world.set("changes.json", [change(fix, ("ve/parser.py", "restart"))] if with_entry else [])
    world.days()
    status, text = world.gate()
    assert status == 1 and count_of(text) == expected
    assert f"The count went back to zero at commit {fix}: it fixes finding F1 (adapter)." in text
    assert (f"commit {fix} changes a classed path and is not classed" in text) is (not with_entry)


@pytest.mark.parametrize("path", ["lean/VE/Service/Graph.lean", "ve/parser.py", DECODER])
@pytest.mark.parametrize("klass", [None, "no-restart", "restart"])
def test_g8_changes_to_the_candidate_surface_are_classed(tmp_path, path, klass):
    world = World(tmp_path, extra={9: [{"files": {path: "changed\n"}}]})
    [changed] = world.extra[9]
    world.clean_days()
    world.merge_runs()
    world.set("changes.json", [] if klass is None else [change(changed, (path, klass))])
    world.days()
    status, text = world.gate()
    if klass is None:
        assert status == 1 and f"commit {changed} changes a classed path and is not classed" in text
    elif klass == "no-restart":
        assert status == 0
    else:
        assert count_of(text) == 6
        assert f"The count went back to zero at commit {changed}: the DRI classed {path} as a restart" in text


@pytest.mark.parametrize("path,klass", [("ve/wire.py", "restart"), ("ve/english.py", "no-restart")])
def test_g8a_g8b_changes_off_the_surface_are_classed_too(tmp_path, path, klass):
    world = World(tmp_path, extra={9: [{"files": {path: "fixed\n"}}]})
    [changed] = world.extra[9]
    world.clean_days()
    world.merge_runs()
    world.days()
    status, text = world.gate()
    assert status == 1 and f"commit {changed} changes a classed path and is not classed" in text
    world.set("changes.json", [change(changed, (path, klass))])
    status, text = world.gate()
    if klass == "restart":
        assert count_of(text) == 6
        assert f"the DRI classed {path} as a restart: {path}: restart for the test" in text
    else:
        assert status == 0
        assert f"classed change {changed} {path} (off the candidate surface): no-restart, {path}: no-restart" in text


def test_g8c_a_changes_entry_must_match_its_diff(tmp_path):
    world = World(tmp_path, extra={9: [{"files": {"ve/wire.py": "a\n", "ve/english.py": "b\n"}}]})
    [changed] = world.extra[9]
    world.set("changes.json", [change(changed, ("ve/wire.py", "restart"))])
    status, text = world.tool("--check")
    assert status == 2 and f"changes entry {changed} does not match its diff: ve/english.py" in text
    world.set("changes.json", [change(changed, ("ve/wire.py", "restart"), ("ve/english.py", "no-restart"),
                                      ("ve/printer.py", "no-restart"))])
    status, text = world.tool("--check")
    assert status == 2 and f"changes entry {changed} does not match its diff: ve/printer.py" in text


def test_g9_a_finding_without_a_cause_is_open(tmp_path):
    world = World(tmp_path)
    world.run(0, "baseline", at=world.base, records=[record()], extra_ops={"evaluate": {"zero_tolerance": 1}})
    world.clean_days()
    world.tool("day", day(0))
    world.days()
    world.set("triage.json", [triage_entry("F0", None, first_day=day(0))])
    status, text = world.gate()
    assert status == 1 and count_of(text) == 14 and "finding F0 is open" in text


def test_g10_a_python_fix_does_not_restart(tmp_path):
    world = World(tmp_path, extra={10: [{"files": {"ve/english.py": "fixed\n"}}]})
    [fix] = world.extra[10]
    world.clean_days()
    world.merge_runs()
    world.set("triage.json", [triage_entry("F1", "python", fix=fix, evidence="conformance/x.json")])
    world.set("changes.json", [change(fix, ("ve/english.py", "no-restart"))])
    world.days()
    status, text = world.gate()
    assert status == 0 and count_of(text) == 14


def test_g11_a_ledger_entry_must_follow_from_its_rows(tmp_path):
    world = World(tmp_path)
    world.clean_days()
    world.days()
    entry = world.entry(3)
    entry["runs"][0]["tally"]["evaluate"]["zero_tolerance"] = 1
    (world.repo / f"conformance/shadow/ledger/{day(3)}.json").write_text(json.dumps(entry))
    status, text = world.tool("--check")
    assert status == 2 and f"ledger entry {day(3)} does not match its runs: clean" in text


def test_g12_a_day_without_a_nightly(tmp_path):
    world = World(tmp_path)
    world.clean_days(special={7: lambda w: None})
    assert world.days()[7][0] == 1
    assert count_of(world.gate()[1]) == 7


def test_g13_an_operation_without_a_compared_call(tmp_path):
    world = World(tmp_path)
    ops = {op: {"compared": 1} for op in DISPATCH_NAMES if op != "distinguishing_model"}
    world.clean_days(special={7: lambda w: w.clean_day(7, suite={"ops": ops})})
    status, text = world.days()[7]
    assert status == 1
    assert f"{day(7)} is not a clean day: the operation distinguishing_model has no compared call in the nightly." in text
    assert world.entry(7)["covered"] is False


def test_g14_the_seed_of_another_day(tmp_path):
    world = World(tmp_path)
    world.clean_days(special={7: lambda w: w.clean_day(7, **{"fuzz-nightly": {"seed": 20261006}})})
    status, text = world.days()[7]
    assert status == 1 and "the seed is 20261006, not the seed of 2026-10-07" in text


def test_g15_a_manual_run_is_not_in_the_ledger(tmp_path):
    world = World(tmp_path)
    world.clean_days()
    world.run(7, "baseline", trigger="manual", minute=120, records=[record()],
              extra_ops={"evaluate": {"zero_tolerance": 1}})
    assert world.days()[7][0] == 0
    assert all(row["run"]["trigger"] == "nightly" for row in world.entry(7)["runs"])


def test_g16_a_ledger_commit_needs_nothing(tmp_path):
    world = World(tmp_path)
    ledger = commit(world.repo, {"conformance/shadow/ledger/2026-10-14.json": "{}"}, "ledger")
    history = shadow_gate.History(world.repo)
    assert not history.needs_merge_run(ledger) and not history.needs_classing(ledger)


@pytest.mark.parametrize("merge,covered", [(None, False), ("complete", True), ("incomplete", False)])
def test_g17_merge_coverage(tmp_path, merge, covered):
    world = World(tmp_path, extra={7: [{"files": {"tests/test_x.py": "changed\n"}}]})
    [changed] = world.extra[7]
    world.clean_days()
    if merge:
        world.run(6, "suite", trigger="merge", at=changed, minute=600, **({} if merge == "complete" else {"exit": 1}))
    results = world.days()
    assert world.entry(7)["covered"] is covered
    if not covered:
        assert f"the commit {changed} needs a merge run and has no complete one" in results[7][1]
        assert count_of(world.gate()[1]) == 7


def test_g18_a_day_is_certified_only_when_final(tmp_path):
    world = World(tmp_path)
    world.clean_day(7)
    late = world.run(7, "baseline", minute=900, finished=False)
    status, text = world.tool("day", day(7), now=f"{day(7)}T23:00:00Z")
    assert status == 2 and text.strip() == f"{day(7)} is not final: the day has not ended."
    status, text = world.tool("day", day(7), now=f"{day(8)}T01:00:00Z")
    assert status == 2 and text.strip() == f"{day(7)} is not final: the run {late.name} has not finished."
    assert not (world.repo / f"conformance/shadow/ledger/{day(7)}.json").exists()
    meta = json.loads((late / "run.json").read_text())
    meta["finished"] = f"{day(8)}T02:00:00Z"
    (late / "run.json").write_text(json.dumps(meta))
    world.tool("day", day(7), now=f"{day(8)}T03:00:00Z")
    assert world.entry(7)["written"] == f"{day(8)}T03:00:00Z"


@pytest.mark.parametrize("written", [f"{day(3)}T20:00:00Z", f"{day(4)}T00:30:00Z"])
def test_g19_an_entry_written_too_early(tmp_path, written):
    world = World(tmp_path)
    world.clean_day(3)
    for row in world.runs.iterdir():
        meta = json.loads((row / "run.json").read_text())
        meta["finished"] = f"{day(4)}T01:00:00Z"
        (row / "run.json").write_text(json.dumps(meta))
    world.tool("day", day(3))
    entry = world.entry(3)
    entry["written"] = written
    (world.repo / f"conformance/shadow/ledger/{day(3)}.json").write_text(json.dumps(entry))
    status, text = world.tool("--check")
    assert status == 2 and f"ledger entry {day(3)} does not match its runs: written" in text


def test_g20_a_second_nightly_at_a_later_commit(tmp_path):
    world = World(tmp_path, extra={8: [{"files": {"docs/later.md": "x"}}]})
    world.clean_days()
    [later] = world.extra[8]
    world.run(7, "baseline", at=later, minute=600, records=[record()], extra_ops={"evaluate": {"zero_tolerance": 1}})
    results = world.days()
    entry = world.entry(7)
    assert entry["nightly_commit"] == world.nightly[7] and entry["covered"] is True
    assert results[7][0] == 1 and entry["clean"] is False
    assert count_of(world.gate()[1]) == 7


@pytest.mark.parametrize("side,klass,expected", [("glue", "restart", 9), ("python", "no-restart", 14)])
def test_g21_a_spec_fix_restarts_as_its_side(tmp_path, side, klass, expected):
    path = "lean/VE/Service/Graph.lean" if side == "glue" else "ve/english.py"
    world = World(tmp_path, extra={6: [{"files": {path: "matched\n"}}]})
    [fix] = world.extra[6]
    world.clean_days()
    world.merge_runs()
    world.set("triage.json", [triage_entry("F1", "spec", fix={"commit": fix, "cause": side},
                                           note="docs/spec/x.md 2.1", evidence="tests/test_x.py")])
    world.set("changes.json", [change(fix, (path, klass))])
    world.days()
    assert count_of(world.gate()[1]) == expected


# --- 8.6 ---------------------------------------------------------------------------------

def test_t2_the_committed_tree_is_well_formed():
    out = io.StringIO()
    with redirect_stdout(out):
        status = shadow_gate.main(["--check", "--root", str(ROOT)])
    assert status == 0 and out.getvalue() == ""


WORDING_REJECTED = [("evaluate", ["status"]), ("parse", ["code"]), ("model_validation", ["generator"]),
                    ("evaluate", ["evaluations"]), ("graph", ["graph_id"]),
                    ("evaluate", ["explanation", "children", "kind"]),
                    ("evaluate", ["explanation", "bindings", "local_id"]), ("evaluate", ["explanation", "detail"]),
                    ("graph", ["composition", "message"]), ("bundle", ["proof"])]


def test_t3_malformed_files_are_named(tmp_path):
    world = World(tmp_path)
    corpora = [entry for entry in registry() if entry["id"] != "english"]
    world.set("corpora.json", corpora)
    status, text = world.tool("--check")
    assert status == 2 and "corpora entry english is missing: id" in text
    world.set("corpora.json", registry())
    world.set("triage.json", [triage_entry("F1", "unknown")])
    status, text = world.tool("--check")
    assert status == 2 and "triage entry F1 has an unknown cause: cause" in text
    world.set("triage.json", [])
    entry = change(world.nightly[3], )
    entry["class"] = "maybe"
    world.set("changes.json", [entry])
    status, text = world.tool("--check")
    assert status == 2 and f"changes entry {world.nightly[3]} does not match its diff: class" in text
    world.set("changes.json", [])
    for index, (op, path) in enumerate(WORDING_REJECTED):
        world.set("wording.json", [{"op": op, "path": path, "python": "a", "backend": "b", "reviewed": "r"}])
        status, text = world.tool("--check")
        assert status == 2, (op, path)
        assert f"wording entry 0 is not at an eligible location: {op} {json.dumps(path)}" in text
    for op, path in (("parse", ["message"]), ("graph", ["proof"])):
        world.set("wording.json", [{"op": op, "path": path, "python": "a", "backend": "b", "reviewed": "r"}])
        assert world.tool("--check") == (0, "")
