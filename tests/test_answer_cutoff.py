"""The answer-level cutoff (tools/answer_cutoff.py, tools/answer_replay.py) and the request records of
tools/test_map_recorder.py: an R1 experiment that tools/gate.py, the merge train and the nightlies never use.

The recorder tests run a child process under the recorder with this checkout as its root, as a
recorded test file would run, and send real cases to the built `ve_service`. The selection tests
use small maps, as tests/test_select_tests.py does.
"""
from __future__ import annotations

import ast
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest

from lean_build import lean_build
from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import answer_cutoff  # noqa: E402
import answer_replay  # noqa: E402
from change_units import summarize  # noqa: E402
import nested_pytest  # noqa: E402
import select_tests  # noqa: E402
import source_graph  # noqa: E402
import test_map  # noqa: E402

from ve.backends import lean_service  # noqa: E402

SERVICE = "lean/.lake/build/bin/ve_service"
UNIT = "tests/test_demo.py"
EVALUATION = json.loads((ROOT / "conformance/evaluation.json").read_text())[:3]
START = (f"import sys\nsys.path.insert(0, {str(ROOT / 'tools')!r})\nimport test_map_recorder\n"
         "test_map_recorder.start()\nsys.path.pop(0)\n")


@pytest.fixture(scope="module")
def executable() -> Path:
    return lean_build("ve_service") / "ve_service"


def key(mode: str, text: str) -> str:
    return hashlib.sha256(f"{mode}\n{text}".encode()).hexdigest()


def record_child(tmp_path: Path, program: str, *, requests: bool = True) -> tuple[Path, Path]:
    """Run `program` in a child under the recorder, rooted at this checkout, as unit UNIT."""
    out, store = tmp_path / answer_cutoff.unit_directory(UNIT), tmp_path / "requests"
    out.mkdir()
    script = tmp_path / "child.py"
    script.write_text(START + textwrap.dedent(program))
    settings = {"PATH": os.environ["PATH"], "VE_TESTMAP_OUT": str(out), "VE_TESTMAP_ROOT": str(ROOT),
                "PYTHONPATH": str(ROOT)}
    if requests:
        settings["VE_TESTMAP_REQUESTS"] = str(store)
    subprocess.run([sys.executable, str(script)], cwd=ROOT, env=nested_pytest.environment({}, **settings),
                   check=True, timeout=HANG_TIMEOUT)
    return out, store


SEND = """
    import json
    from ve.backends.lean_service import LeanService
    cases = json.loads(open("conformance/evaluation.json").read())[:3]
    with LeanService() as service:
        service.run_bound("evaluate", cases)
        service.run_bound("evaluate", [{"id": "a\\u2028b", "ast": [["top"]]}])
"""


def sent_texts() -> list[str]:
    return [sent.text for sent in lean_service._encode([*EVALUATION, {"id": "a b", "ast": [["top"]]}])]


def test_recorder_records_each_case_the_client_sent(tmp_path, executable):
    _, store = record_child(tmp_path, SEND)
    index = answer_cutoff.fold(store, [UNIT])
    entry = index["units"][UNIT]
    assert {index["keys"][i] for i in entry["keys"]} == {key("evaluate", text) for text in sent_texts()}
    assert set(index["modes"]) == {"evaluate"}
    assert entry["pins"] == ["client"] and entry["unknown"] == [] and entry["timed"] is False
    written = tmp_path / "recording"
    written.mkdir()
    assert answer_cutoff.store_cases(store, index, written)[0] == len(sent_texts())
    stored = {row["k"]: row["c"] for row in answer_replay.read_jsonl(written / "cases.jsonl.gz")}
    # The exact text sent, a U+2028 inside a string included (a line separator only to str.splitlines).
    assert sorted(stored.values()) == sorted(sent_texts())
    handles = {answer_replay.handle_of(text) for text in stored.values()} - {None}
    environments = {row["d"]: row["t"] for row in answer_replay.read_jsonl(written / "environments.jsonl.gz")}
    assert handles and set(environments) == handles
    assert all(hashlib.sha256(text.encode()).hexdigest() == digest for digest, text in environments.items())


def test_request_records_leave_the_map_as_it_was(tmp_path, executable):
    """Request recording is opt-in, and the coverage records do not depend on it."""
    (tmp_path / "plain").mkdir()
    (tmp_path / "with").mkdir()
    plain, plain_store = record_child(tmp_path / "plain", SEND, requests=False)
    with_requests, _ = record_child(tmp_path / "with", SEND)
    assert not plain_store.exists()
    tracked = test_map.tracked_paths()
    edges = [test_map.read_unit(out, tracked) for out in (plain, with_requests)]
    assert edges[0]["f"] and edges[0] == edges[1]


@pytest.mark.parametrize("program, reason", [
    ("import sys\nsys.audit('ve.service.mode', 'evaluate')\n", "was not raised by the client's exchange"),
    ("from ve.backends.lean_service import LeanService, CheckerUnavailable\n"
     "try:\n    LeanService('/nonexistent/ve_service').run('evaluate', [{'id': 'a', 'ast': [['top']]}])\n"
     "except CheckerUnavailable:\n    pass\n", "a request to another executable"),
    (f"import subprocess\nsubprocess.Popen([{SERVICE!r}], stdin=subprocess.DEVNULL, "
     "stdout=subprocess.DEVNULL).wait()\n", "started outside ve/backends/lean_service.py"),
])
def test_service_uses_the_record_cannot_replay_make_the_unit_unknown(tmp_path, executable, program, reason):
    _, store = record_child(tmp_path, program)
    unknown = answer_cutoff.fold(store, [UNIT])["units"][UNIT]["unknown"]
    assert len(unknown) == 1 and reason in unknown[0]


def test_timeouts_and_data_reads_of_the_pins_are_recorded(tmp_path, executable):
    _, store = record_child(tmp_path, """
        from pathlib import Path
        from ve.backends.lean_service import LeanService
        Path("lean/checkers.lock").read_text()
        with LeanService(timeout=600) as service:
            service.run("evaluate", [{"id": "a", "ast": [["top"]]}])
    """)
    entry = answer_cutoff.fold(store, [UNIT])["units"][UNIT]
    assert entry["timed"] is True and entry["pins"] == ["client", "data"]


def test_a_child_and_a_nested_recording_send_for_the_outer_unit(tmp_path, executable):
    """A Python child with an explicit environment, and a nested recording with its own output,
    still record their requests for the unit that started them."""
    nested = tmp_path / "nested-out"
    nested.mkdir()
    child = textwrap.dedent(f"""
        import sys
        sys.path.insert(0, {str(ROOT / 'tools')!r})
        import test_map_recorder
        test_map_recorder.start()
        from ve.backends.lean_service import LeanService
        with LeanService() as service:
            service.run("evaluate", [{{"id": "child", "ast": [["top"]]}}])
    """)
    (tmp_path / "grandchild.py").write_text(child)
    _, store = record_child(tmp_path, f"""
        import os, subprocess, sys
        env = {{"PATH": os.environ["PATH"], "PYTHONPATH": {str(ROOT)!r}, "VE_TESTMAP_ROOT": {str(ROOT)!r},
               "VE_TESTMAP_OUT": {str(nested)!r}}}
        subprocess.run([sys.executable, {str(tmp_path / 'grandchild.py')!r}], env=env, check=True)
    """)
    index = answer_cutoff.fold(store, [UNIT])
    assert {index["keys"][i] for i in index["units"][UNIT]["keys"]} == {
        key("evaluate", json.dumps({"id": "child", "ast": [["top"]]}, separators=(",", ":")))}
    assert sorted(path.name for path in (store / "units").iterdir()) == [answer_cutoff.unit_directory(UNIT)]


def write_records(store: Path, unit: str, records: list, bodies: list[dict], environments: list[dict]) -> None:
    for directory, rows in ((store / "units" / answer_cutoff.unit_directory(unit), records),
                            (store / "bodies", bodies), (store / "environments", environments)):
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / "1.jsonl").open("a") as handle:  # one process's file, as the recorder appends
            handle.write("".join((row if isinstance(row, str) else json.dumps(row, ensure_ascii=False)) + "\n"
                                 for row in rows))


def test_folding_marks_truncated_and_unrecorded_cases_unknown(tmp_path):
    handle = "e" * 64
    texts = ['{"id":"a"}', json.dumps({"id": "b", lean_service.HANDLE_KEY: handle}), '{"id":"c"}']
    keys = [key("evaluate", text) for text in texts]
    write_records(tmp_path, "tests/test_a.py", [["q", "evaluate", keys[0], False]],
                  [{"k": keys[0], "m": "evaluate", "c": texts[0]}], [])
    write_records(tmp_path, "tests/test_b.py", [["q", "evaluate", keys[1], True], '["q", "eval'],
                  [{"k": keys[1], "m": "evaluate", "c": texts[1]}], [])  # its environment is missing
    write_records(tmp_path, "tests/test_c.py", [["q", "evaluate", keys[2], False]], [], [])  # no text
    index = answer_cutoff.fold(tmp_path, ["tests/test_a.py", "tests/test_b.py", "tests/test_c.py"])
    assert index["units"]["tests/test_b.py"]["timed"] is True
    assert index["units"]["tests/test_b.py"]["unknown"] == ["a truncated request record"]
    out = tmp_path / "recording"
    out.mkdir()
    assert answer_cutoff.store_cases(tmp_path, index, out) == (1, 0)
    reasons = {unit: entry["unknown"] for unit, entry in index["units"].items()}
    assert reasons["tests/test_a.py"] == []
    assert "a case whose text or environment was not recorded" in reasons["tests/test_b.py"]
    assert reasons["tests/test_c.py"] == ["a case whose text or environment was not recorded"]


def replay_of(answers: dict[str, str], service: str = "a" * 64, recording: str = "r" * 64) -> dict:
    return {"version": answer_replay.VERSION, "service": service, "recording": recording, "answers": answers}


def test_diff_finds_changed_missing_and_unreplayable_answers():
    base = replay_of({"same": "1", "changed": "1", "only-base": "1", "lost": "unreplayable: x"})
    head = replay_of({"same": "1", "changed": "2", "only-head": "1", "lost": "unreplayable: x"},
                     service="b" * 64)
    assert answer_replay.diff(base, head)["changed"] == ["changed", "lost", "only-base", "only-head"]
    assert answer_replay.diff(base, base)["changed"] == ["lost"]
    assert answer_replay.answer_digest({"a": 1}) != answer_replay.answer_digest({"a": True})
    assert answer_replay.answer_digest({"a": 1}) != answer_replay.answer_digest({"a": 1.0})
    with pytest.raises(ValueError, match="different recordings"):
        answer_replay.diff(base, replay_of(head["answers"], recording="s" * 64))
    with pytest.raises(ValueError, match="empty"):
        answer_replay.diff(base, replay_of({}))


def recording(tmp_path: Path, edges: dict[str, dict], units: dict[str, dict], keys: list[str]) -> Path:
    """A recording directory: the map of `edges` and a request index of `units`."""
    directory = tmp_path / "recording"
    directory.mkdir()
    test_map.write_map(make_map(edges), directory / "map.json.gz")
    answer_replay.write_json({"version": answer_cutoff.VERSION, "commit": "0" * 40, "keys": keys,
                              "modes": ["evaluate"] * len(keys), "units": units,
                              "map": answer_replay.digest_file(directory / "map.json.gz")},
                             directory / "requests.json.gz")
    return directory


def make_map(edges: dict[str, dict], failed: tuple[str, ...] = ()) -> dict:
    results = {test: {"f": {(test, "<module>")}, "r": set(e.get("r", ())), "d": set(), "x": set(e.get("x", ())),
                      "m": set(), "p": set(), "v": set(e.get("v", ())), "opaque": [],
                      "exit": 1 if test in failed else 0, "seconds": 1.0} for test, e in edges.items()}
    return test_map.build_map(results, "0" * 40)


def entry(*keys: int, timed=False, pins=("client",), unknown=()) -> dict:
    return {"keys": list(keys), "timed": timed, "pins": list(pins), "unknown": list(unknown)}


def graph_of(tmp_path: Path, tests: dict[str, str]) -> source_graph.Graph:
    """The static graph of `tests` alone, built as tests/test_select_tests.py's `make_graph` builds one."""
    for path, text in tests.items():
        (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / path).write_text(text)
    (tmp_path / "lean").mkdir(exist_ok=True)
    (tmp_path / "lean/lakefile.toml").write_text('[[lean_exe]]\nname = "ve_service"\nroot = "Serve"\n')
    summaries = {path: summarize(text, source_graph.module_name(path)[0], package=source_graph.module_name(path)[1])
                 for path, text in tests.items()}
    graph = source_graph.Graph(tmp_path, sorted(tests), summaries)
    graph.prepare_names()
    graph.build()
    return graph


USERS = {"changed": {"x": [SERVICE]}, "same": {"x": [SERVICE]}, "timed": {"x": [SERVICE]},
         "unreadable": {"x": [SERVICE]}, "silent": {"x": [SERVICE]}, "failed": {"x": [SERVICE]},
         "drifted": {"x": [SERVICE]}, "pins": {"x": [SERVICE], "r": ["lean/checkers.lock"]},
         "pin-data": {"x": [SERVICE], "r": ["lean/checkers.lock"]},
         "metered": {"x": ["lean/.lake/build/bin/ve_metered"]}, "other": {}}


def answers_selection(tmp_path: Path, path: str, *, pinned: bool = True) -> set[str]:
    """What a change to `path` selects through file_impact under the answers rule, the map USERS."""
    index = {"keys": ["k0", "k1", "k2", "k3", "k4"], "units": {
        "changed": entry(0, 1), "same": entry(1), "timed": entry(2, timed=True),
        "unreadable": entry(3, unknown=["a request to another executable"]), "silent": entry(),
        "failed": entry(1), "drifted": entry(1), "pins": entry(1), "pin-data": entry(1, pins=("client", "data"))}}
    data = make_map(USERS, failed=("failed",))
    plain = select_tests.Coverage(data)
    graph = graph_of(tmp_path, {})
    for unit in USERS:  # each unit's file, which `randomised` reads (a unit it cannot read is unknown)
        (tmp_path / unit).write_text("def test():\n    pass\n")
    unknown = answer_cutoff.unknown_units(index, plain, graph, {"drifted"}, root=tmp_path)
    client_only = {unit for unit, row in index["units"].items() if row["pins"] == ["client"]}
    coverage = answer_cutoff.CutoffCoverage(data, None, client_only if pinned else set())
    rule, _ = answer_cutoff.answers_rule({"changed": ["k0"]}, index, set(unknown))
    selected: set[str] = set()
    with answer_cutoff.service_rule(rule):
        select_tests.file_impact(coverage, graph, set(USERS), lambda tests, _: selected.update(tests), path, False)
    return selected


def test_answers_rule_selects_changed_and_unknown_users_only(tmp_path, monkeypatch):
    monkeypatch.setattr(select_tests, "lean_programs", lambda graph, path: {"ve_service", "ve_metered"})
    assert answers_selection(tmp_path, "lean/VE/Discourse/Run.lean") == {
        "changed", "timed", "unreadable", "silent", "failed", "drifted", "metered"}


# The service's request loop, batch budgets, handles and case splitting: one case per request cannot show them.
@pytest.mark.parametrize("path", ["lean/VE/Service/Protocol.lean", "lean/Serve.lean", "lean/VE/Json.lean",
                                  "lean/lakefile.toml"])
def test_request_handling_and_project_changes_select_every_service_user(tmp_path, monkeypatch, path):
    monkeypatch.setattr(select_tests, "lean_programs", lambda graph, path: {"ve_service"})
    assert answers_selection(tmp_path, path) == set(USERS) - {"metered", "other"}


def test_a_pin_change_selects_only_data_readers_when_the_new_build_is_pinned(tmp_path):
    assert answers_selection(tmp_path, "lean/checkers.lock") == {"pin-data"}
    assert answers_selection(tmp_path, "lean/checkers.lock", pinned=False) == {"pins", "pin-data"}


@pytest.mark.parametrize("source, reason", [
    ("from hypothesis import given\n", "uses hypothesis"),
    ("import random\n\ndef test():\n    random.choice([1, 2])\n", "calls random.choice"),
    ("import random\n\ndef test():\n    random.Random()\n", "calls random.Random"),
    ("from random import shuffle\n", "imports random's shuffle"),
    ("import uuid\n\ndef test():\n    uuid.uuid4()\n", "calls uuid.uuid4"),
])
def test_randomised_inputs_make_a_unit_unknown(tmp_path, source, reason):
    graph = graph_of(tmp_path, {"tests/test_x.py": source})
    assert reason in answer_cutoff.randomised("tests/test_x.py", graph, tmp_path)


def test_seeded_randomness_is_not_unknown(tmp_path):
    graph = graph_of(tmp_path, {"tests/test_x.py": "import os, random\n\ndef test():\n"
                                                    "    random.Random(7).choice([1])\n    os.getpid()\n"})
    assert answer_cutoff.randomised("tests/test_x.py", graph, tmp_path) is None


def test_service_rule_is_restored_after_a_failure():
    original = select_tests.service_impact
    with pytest.raises(RuntimeError), answer_cutoff.service_rule(lambda *args: set()):
        assert select_tests.service_impact is not original
        raise RuntimeError
    assert select_tests.service_impact is original


def test_modes_rule_is_ts_b2s_per_mode_rule(monkeypatch):
    seen = []
    monkeypatch.setattr(select_tests, "select", lambda paths, **options: seen.append(select_tests.service_impact)
                        or {"selected": []})
    assert answer_cutoff.select("modes", ["lean/VE/Rights/Run.lean"])["cutoff"] == {"rule": "modes"}
    assert seen == [select_tests.proposed_service_impact]
    with pytest.raises(ValueError, match="unknown cutoff rule"):
        answer_cutoff.select("everything", [])


def test_select_answers_refuses_a_diff_it_cannot_trust(tmp_path):
    directory = recording(tmp_path, {"u": {"x": [SERVICE]}}, {"u": entry(0)}, ["k0"])
    digest = answer_replay.digest_file(directory / "requests.json.gz")
    diff = {"version": answer_replay.VERSION, "recording": digest, "recording_dir": str(directory),
            "base": "a" * 64, "head": "b" * 64, "cases": 1, "changed": []}
    path = tmp_path / "diff.json"
    answer_replay.write_json({**diff, "recording": "0" * 64}, path)
    with pytest.raises(ValueError, match="not a replay diff"):
        answer_cutoff.select_answers(path, [], base="HEAD", after=None, build="b" * 64)
    answer_replay.write_json(diff, path)
    with pytest.raises(ValueError, match="but the tests run"):
        answer_cutoff.select_answers(path, [], base="HEAD", after=None, build="c" * 64)
    test_map.write_map(make_map({"v": {}}), directory / "map.json.gz")
    with pytest.raises(ValueError, match="its map was replaced"):
        answer_cutoff.select_answers(path, [], base="HEAD", after=None, build="b" * 64)


def test_replay_answers_each_case_as_recorded_and_again_alike(tmp_path, executable):
    _, store = record_child(tmp_path, SEND)
    index = answer_cutoff.fold(store, [UNIT])
    directory = tmp_path / "recording"
    directory.mkdir()
    answer_cutoff.store_cases(store, index, directory)
    answer_replay.write_json({**index, "version": answer_cutoff.VERSION}, directory / "requests.json.gz")
    first = answer_replay.replay(directory, executable, jobs=2)
    second = answer_replay.replay(directory, executable, jobs=1)
    assert set(first["answers"]) == {index["keys"][i] for i in index["units"][UNIT]["keys"]}
    assert not any(answer.startswith(("raised", "unreplayable")) for answer in first["answers"].values())
    assert answer_replay.diff(first, second)["changed"] == []
    with gzip.open(directory / "cases.jsonl.gz", "wt") as handle:
        handle.write("")
    with pytest.raises(ValueError, match="no case"):
        answer_replay.replay(directory, executable)


def test_the_hook_passes_its_rule_and_is_off_by_default(monkeypatch, capsys):
    """`select_tests.py --cutoff RULE` plans through answer_cutoff with that rule; without the flag,
    the plan is select_tests' own and answer_cutoff is not consulted."""
    calls = []
    plan = {"selected": [], "selected_count": 0, "full_count": 0, "full": False, "full_reasons": [], "map": None,
            "seconds": 0, "commands": [], "reasons": {}}
    monkeypatch.setattr(select_tests, "select", lambda paths, **options: calls.append(("plain", paths)) or plan)
    monkeypatch.setattr(answer_cutoff, "select", lambda rule, paths, **options: calls.append((rule, paths)) or plan)
    for argv in (["--paths", "README.md", "--json"], ["--paths", "README.md", "--json", "--cutoff", "answers=d.json"]):
        monkeypatch.setattr(sys, "argv", ["select_tests.py", *argv])
        assert select_tests.main() == 0
    assert calls == [("plain", ["README.md"]), ("answers=d.json", ["README.md"])]
    capsys.readouterr()


def test_the_gate_and_the_maps_never_reach_the_cutoff():
    """R2 and R3 (tools/gate.py) and the map tools import neither cutoff module, so no gate, merge or
    nightly can depend on it; select_tests.py names it only in its opt-in --cutoff hook."""
    for path in ("tools/gate.py", "tools/gate_collection.py", "tools/test_map.py", "tools/test_map_recorder.py"):
        imported = {alias.name for node in ast.walk(ast.parse((ROOT / path).read_text()))
                    if isinstance(node, ast.Import | ast.ImportFrom)
                    for alias in (node.names if isinstance(node, ast.Import) else [ast.alias(node.module or "")])}
        assert not imported & {"answer_cutoff", "answer_replay"}, path
    hook = [node for node in ast.walk(ast.parse((ROOT / "tools/select_tests.py").read_text()))
            if isinstance(node, ast.Import) and any(alias.name == "answer_cutoff" for alias in node.names)]
    assert len(hook) == 1
