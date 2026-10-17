"""The answer-level cutoff (tools/answer_cutoff.py, tools/answer_replay.py) and the request records of
tools/test_map_recorder.py: an R1 experiment that tools/gate.py, the merge train and the nightlies never use.

The recorder tests run a child process under the recorder with this checkout as its root, as a
recorded test file would run, and send real cases to the built `ve_service`. The selection tests
use small maps, as tests/test_select_tests.py does.
"""
from __future__ import annotations

import argparse
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
# A locale whose text encoding is ASCII, neither coerced nor in UTF-8 mode: a file read or written without
# an explicit encoding fails on any other character.
ASCII = {"LC_ALL": "C", "PYTHONCOERCECLOCALE": "0", "PYTHONUTF8": "0"}


@pytest.fixture(scope="module")
def executable() -> Path:
    return lean_build("ve_service") / "ve_service"


def key(mode: str, text: str) -> str:
    return hashlib.sha256(f"{mode}\n{text}".encode()).hexdigest()


def record_child(tmp_path: Path, program: str, *, requests: bool = True, **environment: str) -> tuple[Path, Path]:
    """Run `program` in a child under the recorder, rooted at this checkout, as unit UNIT."""
    out, store = tmp_path / answer_cutoff.unit_directory(UNIT), tmp_path / "requests"
    out.mkdir()
    script = tmp_path / "child.py"
    script.write_text(START + textwrap.dedent(program))
    settings = {"PATH": os.environ["PATH"], "VE_TESTMAP_OUT": str(out), "VE_TESTMAP_ROOT": str(ROOT),
                "PYTHONPATH": str(ROOT), **environment}
    if requests:
        settings["VE_TESTMAP_REQUESTS"] = str(store)
    done = subprocess.run([sys.executable, str(script)], cwd=ROOT, env=nested_pytest.environment({}, **settings),
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert done.returncode == 0, done.stderr
    assert "Exception ignored" not in done.stderr, done.stderr  # no recorder hook failed, a fork's included
    return out, store


SEND = """
    import json
    from ve.backends.lean_service import LeanService
    cases = json.loads(open("conformance/evaluation.json").read())[:3]
    with LeanService() as service:
        service.run_bound("evaluate", cases)
        service.run_bound("evaluate", cases[:1])  # sent again: its records are written once
        service.run_bound("evaluate", [{"id": "a\\u2028b", "ast": [["top"]]}])
        service.exchange("evaluate", '[{"id":"x","ast":[["top"]]}]', 1)  # no texts: the recorder splits the array
"""


def sent_texts() -> list[str]:
    return [*(sent.text for sent in lean_service._encode([*EVALUATION, {"id": "a b", "ast": [["top"]]}])),
            '{"id":"x","ast":[["top"]]}']


def test_recorder_records_each_case_the_client_sent(tmp_path, executable):
    _, store = record_child(tmp_path, SEND, **ASCII)  # the case texts are written as UTF-8 in any locale
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
    for directory in (Path("units") / answer_cutoff.unit_directory(UNIT), Path("bodies"), Path("environments")):
        for path in (store / directory).glob("*.jsonl"):
            written = answer_cutoff.lines(path)
            assert written and len(written) == len(set(written)), path  # each record once per process


def test_request_records_leave_the_map_as_it_was(tmp_path, executable):
    """Request recording is opt-in, and the coverage records do not depend on it: a forked child and
    ve_service started outside the client (with a file of the checkout as its argument) included."""
    (tmp_path / "plain").mkdir()
    (tmp_path / "with").mkdir()
    program = SEND + f"""
    import os, subprocess
    subprocess.Popen([{SERVICE!r}, "README.md"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL).wait()
    pid = os.fork()
    if pid == 0:
        os._exit(0)
    os.waitpid(pid, 0)
"""
    plain, plain_store = record_child(tmp_path / "plain", program, requests=False)
    with_requests, _ = record_child(tmp_path / "with", program)
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
    # A request whose cases are not an array of texts, without texts and with texts that are not strings.
    ("from ve.backends.lean_service import LeanService\nwith LeanService() as service:\n    try:\n"
     "        service.exchange('evaluate', '{}', 1)\n    except Exception:\n        pass\n",
     "(ValueError: the request's cases do not split)"),
    ("from ve.backends.lean_service import LeanService\nwith LeanService() as service:\n    try:\n"
     "        service.exchange('evaluate', '[1]', 1, texts=[1])\n    except Exception:\n        pass\n",
     "(ValueError: the request's cases do not split)"),
])
def test_service_uses_the_record_cannot_replay_make_the_unit_unknown(tmp_path, executable, program, reason):
    _, store = record_child(tmp_path, program)
    entry = answer_cutoff.fold(store, [UNIT])["units"][UNIT]
    assert len(entry["unknown"]) == 1 and reason in entry["unknown"][0]
    assert entry["keys"] == []  # nothing of such a request is recorded as a case to replay


@pytest.mark.parametrize("client, call", [("timeout=600", ""), ("", "timeout=600")], ids=["client", "call"])
def test_timeouts_and_data_reads_of_the_pins_are_recorded(tmp_path, executable, client, call):
    """A timeout given to the client, or to one call (tests/test_lean_service_schema.py and
    tests/test_route_row_schemas.py pass HANG_TIMEOUT on each), makes the request timed; a read of the pins
    outside the client's pin check is data."""
    _, store = record_child(tmp_path, f"""
        from pathlib import Path
        from ve.backends.lean_service import LeanService
        Path("lean/checkers.lock").read_text()
        with LeanService({client}) as service:
            service.run("evaluate", [{{"id": "a", "ast": [["top"]]}}], {call})
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
    assert index["units"][UNIT]["unknown"] == []  # starting a Python child is not starting ve_service


def test_a_process_that_ends_without_cleanup_keeps_its_records(tmp_path, executable):
    """Each record is on disk when it is written: a process that ends by os._exit (a forked worker, a killed
    test) loses none."""
    _, store = record_child(tmp_path, """
        import os
        from ve.backends.lean_service import LeanService
        service = LeanService()
        service.run("evaluate", [{"id": "a", "ast": [["top"]]}])
        os._exit(0)
    """)
    index = answer_cutoff.fold(store, [UNIT])
    assert len(index["keys"]) == 1 and index["units"][UNIT] == entry(0)
    (tmp_path / "recording").mkdir()
    assert answer_cutoff.store_cases(store, index, tmp_path / "recording") == (1, 0)


def test_the_cutoff_reads_and_writes_its_files_as_utf8_in_any_locale(tmp_path):
    """Record lines, stored cases and a unit's test code hold any text: they are UTF-8 whatever the locale's
    encoding (checked in a child whose locale is ASCII)."""
    program = textwrap.dedent(f"""
        import sys
        from pathlib import Path
        sys.path.insert(0, {str(ROOT / 'tools')!r})
        import answer_cutoff, answer_replay
        work = Path({str(tmp_path)!r})
        (work / "bodies").mkdir()
        (work / "bodies/1.jsonl").write_bytes('{{"k": "k0", "m": "evaluate", "c": "\u00e9"}}\\n'.encode())
        rows = answer_cutoff.read_store(work, "bodies", "k")
        assert rows == {{"k0": {{"k": "k0", "m": "evaluate", "c": "\u00e9"}}}}, rows
        answer_cutoff.write_store(rows, work / "cases.jsonl.gz")
        assert list(answer_replay.read_jsonl(work / "cases.jsonl.gz")) == list(rows.values())
        (work / "tests").mkdir()
        (work / "tests/test_x.py").write_bytes("# \u00e9\\ndef test():\\n    pass\\n".encode())

        class Graph:
            def closure(self, unit):
                return {{unit}}, set()

        assert answer_cutoff.randomised("tests/test_x.py", Graph(), work) is None
    """)
    script = tmp_path / "ascii_child.py"
    script.write_text(program, encoding="utf-8")  # source is UTF-8 in any locale; a command line is not
    done = subprocess.run([sys.executable, str(script)], env=nested_pytest.environment(
        {"PATH": os.environ["PATH"]}, PYTHONPATH=str(ROOT), **ASCII), capture_output=True, text=True,
        timeout=HANG_TIMEOUT)
    assert done.returncode == 0, done.stderr


def test_a_recording_without_requests_starts_a_child_with_its_own_environment(tmp_path):
    """The request variables are passed on only when they are set: without request recording, a Python child
    with an explicit environment starts as before."""
    _, store = record_child(tmp_path, """
        import os, subprocess, sys
        subprocess.run([sys.executable, "-c", "pass"], env={"PATH": os.environ["PATH"]}, check=True)
    """, requests=False)
    assert not store.exists()


def test_the_caller_is_code_under_the_root_and_not_beside_it(tmp_path):
    """`_caller` names the innermost frame of code under the root: a directory whose name only starts with
    the root's is not under it. Run in a child, so no recording of this test sees the recorder's state change."""
    root = tmp_path / "root"
    program = textwrap.dedent(f"""
        import sys
        sys.path.insert(0, {str(ROOT / 'tools')!r})
        import test_map_recorder as recorder
        recorder._state.update(root={str(root)!r}, own=set())

        def call(filename):
            namespace = {{"caller": recorder._caller}}
            exec(compile("def _spawn():\\n    return caller()\\n", filename, "exec"), namespace)
            return namespace["_spawn"]()

        print(call({str(root) + '-beside/ve/backends/lean_service.py'!r}))
        print(call({str(root / 've/backends/lean_service.py')!r}))
    """)
    shown = subprocess.run([sys.executable, "-c", program], capture_output=True, text=True, check=True,
                           timeout=HANG_TIMEOUT).stdout.splitlines()
    assert shown == ["None", "('ve/backends/lean_service.py', '_spawn')"]


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
    assert [row["k"] for row in answer_replay.read_jsonl(out / "cases.jsonl.gz")] == keys[:1]
    reasons = {unit: entry["unknown"] for unit, entry in index["units"].items()}
    assert reasons["tests/test_a.py"] == []
    assert "a case whose text or environment was not recorded" in reasons["tests/test_b.py"]
    assert reasons["tests/test_c.py"] == ["a case whose text or environment was not recorded"]


def test_folding_keeps_a_timed_request_and_reads_every_line_it_can(tmp_path):
    """A unit is timed when any of its requests was; a line that does not parse, wherever it is, and a record of
    no known kind make the unit unknown; the records of a unit not asked about are left out."""
    write_records(tmp_path, "tests/test_a.py", [["q", "evaluate", "k0", True], ["q", "evaluate", "k1", False]], [], [])
    write_records(tmp_path, "tests/test_b.py", ['["q", "eval', ["k", "client"]], [], [])
    odd = {"tests/test_c.py": ["z", "x"], "tests/test_d.py": [], "tests/test_e.py": 5}
    for unit, record in odd.items():
        write_records(tmp_path, unit, [record], [], [])
    write_records(tmp_path, "tests/test_gone.py", [["q", "evaluate", "k2", False]], [], [])
    index = answer_cutoff.fold(tmp_path, ["tests/test_a.py", "tests/test_b.py", *odd])
    assert index["keys"] == ["k0", "k1"] and set(index["units"]) == {"tests/test_a.py", "tests/test_b.py", *odd}
    assert index["units"]["tests/test_a.py"]["timed"] is True
    assert index["units"]["tests/test_b.py"] == entry(unknown=["a truncated request record"])
    assert all(index["units"][unit] == entry(pins=(), unknown=["an unreadable request record"]) for unit in odd)
    # A process killed mid-line leaves a store file whose only line does not parse: its cases are missing.
    for kind in ("bodies", "environments"):
        (tmp_path / kind / "0.jsonl").write_text('{"k": "k0", "m"\n')
    (tmp_path / "recording").mkdir()
    assert answer_cutoff.store_cases(tmp_path, index, tmp_path / "recording") == (0, 0)
    assert "a case whose text or environment was not recorded" in index["units"]["tests/test_a.py"]["unknown"]


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
    with pytest.raises(ValueError, match="modes"):
        answer_replay.diff(base, {**head, "partial": ["evaluate"]})
    for wrong in ({"version": answer_replay.VERSION - 1}, {"answers": [["same", "1"]]}):
        with pytest.raises(ValueError, match="not an answer replay"):
            answer_replay.diff(base, {**head, **wrong})
    # The digest is of the compact JSON as written, non-ASCII text as it is: saved replays stay comparable.
    assert answer_replay.answer_digest({"a": "\u00e9", "b": [1, 2]}) == hashlib.sha256(
        '{"a":"\u00e9","b":[1,2]}'.encode()).hexdigest()[:32]


def test_a_case_names_an_environment_only_by_a_string_handle_in_an_object():
    name = lean_service.HANDLE_KEY
    assert answer_replay.handle_of(json.dumps({"id": "a", name: "h"})) == "h"
    assert answer_replay.handle_of('{"%s\\u005f%s": "h"}' % tuple(name.split("_", 1))) == "h"  # as the service reads it
    for text in (json.dumps({name: 5}), json.dumps([name]), '{"%s": "h"' % name, '{"id": "a"}'):
        assert answer_replay.handle_of(text) is None, text
    # A result's position is left out only from an object result; an entry without one keeps its other members.
    assert answer_replay.unplaced({"index": 1, "result": "case_index"}) == {"result": "case_index"}
    assert answer_replay.unplaced({"index": 1, "digest": "d"}) == {"digest": "d"}


def test_batches_split_by_mode_count_and_inline_size(monkeypatch):
    """At most BATCH_CASES cases a request, and a new one before the inline texts, environments included,
    pass BATCH_BYTES; never an empty one."""
    monkeypatch.setattr(answer_replay, "BATCH_CASES", 3)
    monkeypatch.setattr(answer_replay, "BATCH_BYTES", 40)
    named = json.dumps({lean_service.HANDLE_KEY: "h"})  # 40 bytes more inline: its environment
    texts = {"a1": "x" * 10, "a2": "x" * 10, "a3": "x" * 25, "a4": "x" * 10, "a5": "x" * 5, "a6": "x",
             "b1": "x", "b2": "x", "b3": "x", "b4": "x", "c1": "x" * 5, "c2": named, "d1": named}
    cases = {key: (key[0], text) for key, text in texts.items()}
    assert answer_replay.batches(cases, {"h": "e" * 40}) == [
        ("a", ["a1", "a2"]), ("a", ["a3", "a4", "a5"]), ("a", ["a6"]), ("b", ["b1", "b2", "b3"]), ("b", ["b4"]),
        ("c", ["c1"]), ("c", ["c2"]), ("d", ["d1"])]


class Refusing:
    """A stand-in service that refuses every request of more than one case and answers each case alone by its
    text; alone, it refuses the texts in `refused` and raises for those in `raising`."""

    def __init__(self, raising: dict[str, Exception] | None = None, refused: frozenset[str] = frozenset()):
        self.raising, self.refused = raising or {}, refused
        self.requests: list[list[str]] = []

    def exchange(self, mode, line, count, *, timeout, texts):
        self.requests.append(texts)
        if len(texts) == 1 and texts[0] in self.raising:
            raise self.raising[texts[0]]
        if len(texts) > 1 or texts[0] in self.refused:
            return None, {"status": "error", "id": "n" * len(self.requests), "error": f"refused {len(texts)}"}
        return None, {"status": "ok", "id": "n" * 32,
                      "results": [{"index": 0, "result": {"status": "ok", "text": texts[0]}}]}


def test_a_refused_batch_is_asked_again_case_by_case():
    """Each case of a refused batch gets its own answer, the one it gets alone; a case refused or raising alone
    is answered by the refusal (but its nonce) or by the class of what was raised."""
    texts = ["a", "b", "c", "d", "e"]
    options = {"raising": {"c": lean_service.CheckerUnavailable("down"), "d": lean_service.ResourceLimit("long")},
               "refused": frozenset({"e"})}
    service = Refusing(**options)
    together = answer_replay.ask(service, "evaluate", texts)
    assert service.requests == [texts, *([text] for text in texts)]
    alone = [answer_replay.ask(Refusing(**options), "evaluate", [text])[0] for text in texts]
    assert together == alone and len(set(together)) == len(texts)
    assert together[:2] == [answer_replay.answer_digest({"result": {"status": "ok", "text": text}})
                            for text in ("a", "b")]
    assert together[2] == "raised: CheckerUnavailable" and together[3].startswith(answer_replay.UNREPLAYABLE)
    assert together[4] == answer_replay.answer_digest({"status": "error", "error": "refused 1"})
    raising = Refusing({"a": RuntimeError()})
    raising.exchange = lambda *args, **options: (_ for _ in ()).throw(RuntimeError())  # the batch raises too
    assert answer_replay.ask(raising, "evaluate", ["a", "b"]) == ["raised: RuntimeError"] * 2
    # A batch over the client's line limit is asked case by case too.
    limited = Refusing()
    plain = limited.exchange
    limited.exchange = lambda mode, line, count, *, timeout, texts: (
        (_ for _ in ()).throw(lean_service.ResourceLimit("long")) if len(texts) > 1
        else plain(mode, line, count, timeout=timeout, texts=texts))
    assert answer_replay.ask(limited, "evaluate", ["a", "b"]) == together[:2]


def recording(tmp_path: Path, edges: dict[str, dict], units: dict[str, dict], keys: list[str]) -> Path:
    """A recording directory: the map of `edges` and a request index of `units`."""
    directory = tmp_path / "recording"
    directory.mkdir()
    test_map.write_map(make_map(edges), directory / "map.json.gz")
    answer_replay.write_json({"version": answer_cutoff.VERSION, "commit": "0" * 40, "keys": keys,
                              "modes": ["evaluate"] * len(keys), "units": units, "service": "a" * 64,
                              "map": answer_replay.digest_file(directory / "map.json.gz")},
                             directory / "requests.json.gz")
    return directory


def unit_results(edges: dict[str, dict], failed: tuple[str, ...] = (), opaque: tuple[str, ...] = ()) -> dict:
    """What `test_map.record_units` returns for units with these edges."""
    return {test: {"f": {(test, "<module>")}, "r": set(e.get("r", ())), "d": set(), "x": set(e.get("x", ())),
                   "m": set(), "p": set(), "v": set(e.get("v", ())),
                   "opaque": ["python child without site"] if test in opaque else [],
                   "exit": 1 if test in failed else 0, "seconds": 1.0} for test, e in edges.items()}


def make_map(edges: dict[str, dict], failed: tuple[str, ...] = (), opaque: tuple[str, ...] = ()) -> dict:
    return test_map.build_map(unit_results(edges, failed, opaque), "0" * 40)


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


USERS = {"changed": {"x": [SERVICE]}, "same": {"x": [SERVICE]}, "timed": {"x": [SERVICE]}, "randomised": {"x": [SERVICE]},
         "unreadable": {"x": [SERVICE]}, "silent": {"x": [SERVICE]}, "failed": {"x": [SERVICE]},
         "drifted": {"x": [SERVICE]}, "pins": {"x": [SERVICE], "r": ["lean/checkers.lock", "tests/data/pins.json"]},
         "pin-data": {"x": [SERVICE], "r": ["lean/checkers.lock"]},
         "metered": {"x": ["lean/.lake/build/bin/ve_metered"]}, "other": {}}


def answers_selection(tmp_path: Path, path: str, *, pinned: bool = True) -> set[str]:
    """What a change to `path` selects through file_impact under the answers rule, the map USERS.

    `other` sent a changed case when it was recorded, but today's map has it start no ve_service."""
    index = {"keys": ["k0", "k1", "k2", "k3", "k4"], "units": {
        "changed": entry(0, 1), "same": entry(1), "timed": entry(2, timed=True),
        "unreadable": entry(3, unknown=["a request to another executable"]), "silent": entry(),
        "failed": entry(1), "drifted": entry(1), "pins": entry(1), "pin-data": entry(1, pins=("client", "data")),
        "other": entry(0), "randomised": entry(1)}}
    data = make_map(USERS, failed=("failed",))
    plain = select_tests.Coverage(data)
    graph = graph_of(tmp_path, {})
    for unit in USERS:  # each unit's file, which `randomised` reads (a unit it cannot read is unknown)
        (tmp_path / unit).write_text("from hypothesis import given\n" if unit == "randomised" else "def test():\n    pass\n")
    unknown = answer_cutoff.unknown_units(index, plain, graph, {"drifted"}, root=tmp_path)
    client_only = {unit for unit, row in index["units"].items() if row["pins"] == ["client"]}
    coverage = answer_cutoff.CutoffCoverage(select_tests.Coverage(data), client_only if pinned else set())
    rule, _ = answer_cutoff.answers_rule({"changed": ["k0"]}, index, set(unknown))
    selected: set[str] = set()
    with answer_cutoff.service_rule(rule):
        select_tests.file_impact(coverage, graph, set(USERS), lambda tests, _: selected.update(tests), path, False)
    return selected


def test_a_unit_that_read_an_answer_the_base_build_changed_is_unknown(tmp_path):
    """On another base build than the recording's, a test may send requests the recording lacks."""
    index = {"keys": ["k0", "k1"], "units": {"changed": entry(0), "same": entry(1)}}
    coverage = select_tests.Coverage(make_map({"changed": {"x": [SERVICE]}, "same": {"x": [SERVICE]}}))
    for unit in ("changed", "same"):
        (tmp_path / unit).write_text("def test():\n    pass\n")
    assert answer_cutoff.unknown_units(index, coverage, graph_of(tmp_path, {}), set(), root=tmp_path,
                                       stale=frozenset({"k0"})) == {
        "changed": "an answer it read changed between the recording's build and the base's"}


def test_answers_rule_selects_changed_and_unknown_users_only(tmp_path, monkeypatch):
    monkeypatch.setattr(select_tests, "lean_programs", lambda graph, path: {"ve_service", "ve_metered"})
    assert answers_selection(tmp_path, "lean/VE/Discourse/Run.lean") == {
        "changed", "timed", "unreadable", "silent", "failed", "drifted", "metered", "randomised"}


def test_a_unit_recorded_failing_or_opaque_is_unknown_with_its_status(tmp_path):
    coverage = select_tests.Coverage(make_map({unit: {"x": [SERVICE]} for unit in ("failed", "opaque", "both")},
                                              failed=("failed", "both"), opaque=("opaque", "both")))
    index = {"keys": ["k0"], "units": {unit: entry(0) for unit in ("failed", "opaque", "both")}}
    assert answer_cutoff.unknown_units(index, coverage, graph_of(tmp_path, {}), set(), root=tmp_path) == {
        "failed": "recorded with exit 1", "opaque": "recorded with exit 0 and opaque",
        "both": "recorded with exit 1 and opaque"}


# The service's request loop, batch budgets, handles and case splitting: one case per request cannot show them.
@pytest.mark.parametrize("path", ["lean/VE/Service/Protocol.lean", "lean/Serve.lean", "lean/VE/Json.lean",
                                  "lean/lakefile.toml"])
def test_request_handling_and_project_changes_select_every_service_user(tmp_path, monkeypatch, path):
    monkeypatch.setattr(select_tests, "lean_programs", lambda graph, path: {"ve_service"})
    assert answers_selection(tmp_path, path) == set(USERS) - {"metered", "other"}


def test_a_pin_change_selects_only_data_readers_when_the_new_build_is_pinned(tmp_path):
    assert answers_selection(tmp_path, "lean/checkers.lock") == {"pin-data"}
    assert answers_selection(tmp_path, "lean/checkers.lock", pinned=False) == {"pins", "pin-data"}


def test_the_pin_exemption_is_for_the_pins_only(tmp_path):
    """A unit whose only pin read was the client's still reads its other files: a change to one selects it."""
    assert answers_selection(tmp_path, "tests/data/pins.json") == {"pins"}


def test_pinned_reads_the_pins_of_the_tree_or_of_a_commit(tmp_path, monkeypatch):
    """Whether the new build is pinned decides the exemption above; an unreadable pin file admits nothing."""
    pins = json.loads(subprocess.run(["git", "show", f"HEAD:{answer_cutoff.PIN_FILE}"], cwd=ROOT, check=True,
                                     capture_output=True, text=True).stdout)["ve_service"]
    monkeypatch.chdir(tmp_path)  # a commit's pins are this checkout's, wherever the tool runs from
    assert answer_cutoff.pinned(pins[0], "HEAD") and not answer_cutoff.pinned("0" * 64, "HEAD")
    assert not answer_cutoff.pinned(pins[0], "0" * 40)  # no such commit
    monkeypatch.setattr(answer_cutoff, "ROOT", tmp_path)
    (tmp_path / "lean").mkdir()
    lock = tmp_path / answer_cutoff.PIN_FILE
    for text, admitted in ((json.dumps({"ve_service": ["b" * 64]}), True), (json.dumps({"ve_service": ["c" * 64]}), False),
                           (json.dumps({"rust_jsonl": ["b" * 64]}), False), ("{", False), ("[]", False)):
        lock.write_text(text)
        assert answer_cutoff.pinned("b" * 64, None) is admitted, text
    lock.unlink()
    assert answer_cutoff.pinned("b" * 64, None) is False


@pytest.mark.parametrize("source, reason", [
    ("from hypothesis import given\n", "uses hypothesis"),
    ("import random\n\ndef test():\n    random.choice([1, 2])\n", "calls random.choice"),
    ("import random\n\ndef test():\n    random.Random()\n", "calls random.Random"),
    ("from random import shuffle\n", "imports random's shuffle"),
    ("import uuid\n\ndef test():\n    uuid.uuid4()\n", "calls uuid.uuid4"),
    ("import hypothesis\n", "uses hypothesis"),
    ("import hypothesis.strategies as st\n", "uses hypothesis"),
    ("from hypothesis.strategies import integers\n", "uses hypothesis"),
    ("from uuid import uuid4\n", "imports uuid's uuid4"),
    ("from os import urandom\n", "imports os's urandom"),
    ("import secrets\n\ndef test():\n    secrets.token_hex()\n", "calls secrets.token_hex"),
])
def test_randomised_inputs_make_a_unit_unknown(tmp_path, source, reason):
    graph = graph_of(tmp_path, {"tests/test_x.py": source})
    assert reason in answer_cutoff.randomised("tests/test_x.py", graph, tmp_path)


def test_a_unit_that_does_not_parse_is_unknown(tmp_path):
    graph = graph_of(tmp_path, {"tests/test_x.py": "from helper import f\n", "tests/helper.py": "f = 1\n"})
    (tmp_path / "tests/helper.py").write_text("def f(:\n")  # changed since the graph was built
    assert answer_cutoff.randomised("tests/test_x.py", graph, tmp_path) == "tests/helper.py does not parse"


def test_seeded_randomness_is_not_unknown(tmp_path):
    graph = graph_of(tmp_path, {"tests/test_x.py": "import os, random, uuid\nfrom random import Random\nfrom uuid import UUID\n"
                                                    "\ndef test():\n    random.Random(7).choice([1])\n    random.Random(x=7)\n"
                                                    "    os.getpid()\n    uuid.UUID(int=1)\n"})
    assert answer_cutoff.randomised("tests/test_x.py", graph, tmp_path) is None


def test_property_tests_count_in_the_unit_and_its_helpers_but_not_in_another_test_file(tmp_path):
    """A helper's strategies run in the unit that imports it; another test file's property tests do not."""
    hypothesis = "from hypothesis import given\n"
    graph = graph_of(tmp_path, {"tests/test_x.py": "from helper import f\n", "tests/helper.py": hypothesis,
                                "tests/test_y.py": "from test_other import f\n", "tests/test_other.py": hypothesis})
    assert answer_cutoff.randomised("tests/test_x.py", graph, tmp_path) == "tests/helper.py uses hypothesis"
    assert answer_cutoff.randomised("tests/test_y.py", graph, tmp_path) is None


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


def test_select_runs_today_off_and_the_answers_rule_on_its_diff(monkeypatch):
    calls = []
    monkeypatch.setattr(select_tests, "select", lambda paths, **options: calls.append(("today", paths, options)) or {})
    monkeypatch.setattr(answer_cutoff, "select_answers",
                        lambda diff, paths, **options: calls.append((diff, paths, options)) or {})
    assert answer_cutoff.select("off", ["a"], base="HEAD") == answer_cutoff.select("answers=d/x.json", ["b"]) == {}
    assert calls == [("today", ["a"], {"base": "HEAD"}), (Path("d/x.json"), ["b"], {})]


def test_select_answers_takes_the_build_made_here_by_default(tmp_path, monkeypatch):
    directory = recording(tmp_path, {"u": {"x": [SERVICE]}}, {"u": entry(0)}, ["k0"])
    path = tmp_path / "diff.json"
    answer_replay.write_json({"version": answer_replay.VERSION, "recording_dir": str(directory),
                              "recording": answer_replay.digest_file(directory / "requests.json.gz"),
                              "base": "a" * 64, "head": "b" * 64, "cases": 1, "changed": []}, path)
    root = tmp_path / "root"
    (root / answer_cutoff.SERVICE).parent.mkdir(parents=True)
    (root / answer_cutoff.SERVICE).write_bytes(b"service")
    monkeypatch.setattr(answer_cutoff, "ROOT", root)
    with pytest.raises(ValueError, match=f"but the tests run {hashlib.sha256(b'service').hexdigest()[:16]}"):
        answer_cutoff.select_answers(path, [], base="HEAD", after=None)


def test_select_answers_refuses_a_diff_it_cannot_trust(tmp_path):
    directory = recording(tmp_path, {"u": {"x": [SERVICE]}}, {"u": entry(0)}, ["k0"])
    digest = answer_replay.digest_file(directory / "requests.json.gz")
    diff = {"version": answer_replay.VERSION, "recording": digest, "recording_dir": str(directory),
            "base": "a" * 64, "head": "b" * 64, "cases": 1, "changed": []}
    path = tmp_path / "diff.json"
    for wrong in ({"recording": "0" * 64}, {"version": answer_replay.VERSION - 1}):
        answer_replay.write_json({**diff, **wrong}, path)
        with pytest.raises(ValueError, match="not a replay diff"):
            answer_cutoff.select_answers(path, [], base="HEAD", after=None, build="b" * 64)
    answer_replay.write_json(diff, path)
    with pytest.raises(ValueError, match="but the tests run"):
        answer_cutoff.select_answers(path, [], base="HEAD", after=None, build="c" * 64)
    answer_replay.write_json({**diff, "base": "d" * 64}, path)
    with pytest.raises(ValueError, match="is not the recording's"):
        answer_cutoff.select_answers(path, [], base="HEAD", after=None, build="b" * 64)
    test_map.write_map(make_map({"v": {}}), directory / "map.json.gz")
    with pytest.raises(ValueError, match="its map was replaced"):
        answer_cutoff.select_answers(path, [], base="HEAD", after=None, build="b" * 64)
    index = answer_replay.read_json(directory / "requests.json.gz")
    answer_replay.write_json({**index, "commit": "1" * 40, "map": answer_replay.digest_file(directory / "map.json.gz")},
                             directory / "requests.json.gz")
    with pytest.raises(ValueError, match="name different commits"):
        answer_cutoff.load_recording(directory)
    answer_replay.write_json({**index, "version": answer_cutoff.VERSION + 1,
                              "map": answer_replay.digest_file(directory / "map.json.gz")}, directory / "requests.json.gz")
    with pytest.raises(ValueError, match="not a request recording"):
        answer_cutoff.load_recording(directory)


def replayable(tmp_path: Path) -> tuple[Path, dict]:
    """A recording directory of SEND's requests, and its request index."""
    _, store = record_child(tmp_path, SEND)
    index = answer_cutoff.fold(store, [UNIT])
    directory = tmp_path / "recording"
    directory.mkdir()
    answer_cutoff.store_cases(store, index, directory)
    answer_replay.write_json({**index, "version": answer_cutoff.VERSION}, directory / "requests.json.gz")
    return directory, index


def test_replay_answers_each_case_as_recorded_and_again_alike(tmp_path, executable):
    directory, index = replayable(tmp_path)
    first = answer_replay.replay(directory, executable, jobs=2)
    second = answer_replay.replay(directory, executable, jobs=1)
    assert set(first["answers"]) == {index["keys"][i] for i in index["units"][UNIT]["keys"]}
    assert not any(answer.startswith(("raised", "unreplayable")) for answer in first["answers"].values())
    assert answer_replay.diff(first, second)["changed"] == []
    partial = answer_replay.replay(directory, executable, jobs=1, modes={"evaluate"})
    assert partial == {**first, "partial": ["evaluate"]}
    with pytest.raises(ValueError, match="no case"):
        answer_replay.replay(directory, executable, modes={"rights"})
    with gzip.open(directory / "environments.jsonl.gz", "wt") as handle:
        handle.write("")
    lost = answer_replay.replay(directory, executable, jobs=1)["answers"]
    named = {key for key, (_, text) in answer_replay.load_cases(directory)[0].items()
             if answer_replay.handle_of(text) is not None}
    assert named and {key for key, answer in lost.items() if answer.startswith(answer_replay.UNREPLAYABLE)} == named
    assert {key: lost[key] for key in lost.keys() - named} == {key: first["answers"][key] for key in lost.keys() - named}
    with gzip.open(directory / "cases.jsonl.gz", "wt") as handle:
        handle.write("")
    with pytest.raises(ValueError, match="no case"):
        answer_replay.replay(directory, executable)


def test_a_replay_refuses_to_finish_without_every_answer(tmp_path, executable, monkeypatch):
    """A batch that was never asked leaves the replay short of an answer: it raises, never writes a partial one."""
    directory, _ = replayable(tmp_path)
    every = answer_replay.batches
    monkeypatch.setattr(answer_replay, "batches", lambda cases, environments: [
        (mode, keys[:-1]) for mode, keys in every(cases, environments)])
    with pytest.raises(RuntimeError, match="replayed [0-9]+ of"):
        answer_replay.replay(directory, executable, jobs=1)


@pytest.mark.filterwarnings("ignore::pytest.PytestUnhandledThreadExceptionWarning")
def test_a_replay_answers_only_from_the_build_it_hashed(tmp_path, executable, monkeypatch):
    """The replay's answers are those of the build it names: a service whose executable hashes otherwise
    (replaced after the replay hashed it) is refused, and the replay raises."""
    directory, _ = replayable(tmp_path)
    real, calls = lean_service.executable_sha256, []
    monkeypatch.setattr(lean_service, "executable_sha256",
                        lambda path: "0" * 64 if not calls.append(path) and len(calls) == 1 else real(path))
    with pytest.raises(RuntimeError, match="replayed 0 of"):
        answer_replay.replay(directory, executable, jobs=1)
    assert len(calls) > 1


def help_text(main, argv: list[str], monkeypatch, capsys) -> str:
    monkeypatch.setenv("COLUMNS", "500")
    monkeypatch.setattr(sys, "argv", ["tool", *argv, "--help"])
    with pytest.raises(SystemExit):
        main()
    return capsys.readouterr().out


def test_the_replay_command_line(tmp_path, monkeypatch, capsys):
    """`answer_replay.py replay` and `diff` read their arguments as documented, write their output (into a new
    directory too) and say what they wrote; a missing argument is a usage error."""
    seen = []
    monkeypatch.setattr(answer_replay, "replay", lambda recording, service, jobs: seen.append(
        (recording, service, jobs)) or replay_of({"k": "1"}))
    out = tmp_path / "new/deeper/answers.json.gz"
    for argv in (["replay", "rec", "--service", "svc", "--jobs", "2", "--output", str(out)],
                 ["replay", "rec", "--output", str(out)]):
        monkeypatch.setattr(sys, "argv", ["answer_replay.py", *argv])
        assert answer_replay.main() == 0
    assert seen == [(Path("rec"), Path("svc"), 2), (Path("rec"), lean_service.DEFAULT_EXECUTABLE, 4)]
    assert answer_replay.read_json(out) == replay_of({"k": "1"})
    assert capsys.readouterr().out == f"replayed 1 cases against {'a' * 16}: {out}\n" * 2
    base, head, changes = tmp_path / "base.json", tmp_path / "head.json", tmp_path / "new/diff/changes.json"
    answer_replay.write_json(replay_of({"k": "1", "j": "1"}), base)
    answer_replay.write_json(replay_of({"k": "2", "j": "1"}, service="b" * 64), head)
    monkeypatch.setattr(sys, "argv", ["answer_replay.py", "diff", str(base), str(head), "--output", str(changes)])
    assert answer_replay.main() == 0
    assert answer_replay.read_json(changes) == answer_replay.diff(replay_of({"k": "1", "j": "1"}),
                                                                  replay_of({"k": "2", "j": "1"}, service="b" * 64))
    assert capsys.readouterr().out == f"1 of 2 answers changed: {changes}\n"
    for argv in ([], ["replay", "rec"], ["replay", "--output", str(out)], ["diff", str(base), str(head)],
                 ["diff", str(base), "--output", str(out)]):
        monkeypatch.setattr(sys, "argv", ["answer_replay.py", *argv])
        with pytest.raises(SystemExit):
            answer_replay.main()
    capsys.readouterr()
    assert "\n".join(answer_replay.__doc__.splitlines()[5:7]) in help_text(answer_replay.main, [], monkeypatch, capsys)
    assert "replay a recording against one ve_service build" in help_text(answer_replay.main, [], monkeypatch, capsys)
    assert "the cases whose answers two replays disagree on" in help_text(answer_replay.main, [], monkeypatch, capsys)
    assert "service processes" in help_text(answer_replay.main, ["replay"], monkeypatch, capsys)


def test_the_cutoff_command_line(tmp_path, monkeypatch, capsys):
    """`answer_cutoff.py record` passes its arguments, with their defaults, to `record`; `diff` writes the
    changed answers of two replays of the recording it names, and with --recording-answers the recording
    build and the answers the base build changes (its stale answers)."""
    seen = []
    monkeypatch.setattr(answer_cutoff, "record", lambda args: seen.append(vars(args)) or 0)
    for argv in (["record", "--output", "o", "--jobs", "3", "--timeout", "7", "--work", "w", "--keep",
                  "--allow-dirty", "--no-build", "tests/test_a.py", "tests/test_b.py"], ["record", "--output", "o"]):
        monkeypatch.setattr(sys, "argv", ["answer_cutoff.py", *argv])
        assert answer_cutoff.main() == 0
    common = {"command": "record", "output": "o"}
    assert seen == [{**common, "jobs": 3, "timeout": 7.0, "work": "w", "keep": True, "allow_dirty": True,
                     "no_build": True, "units": ["tests/test_a.py", "tests/test_b.py"]},
                    {**common, "jobs": 8, "timeout": test_map.UNIT_TIMEOUT, "work": None, "keep": False,
                     "allow_dirty": False, "no_build": False, "units": []}]
    directory = recording(tmp_path, {"u": {"x": [SERVICE]}}, {"u": entry(0, 1)}, ["k0", "k1"])
    digest = answer_replay.digest_file(directory / "requests.json.gz")
    sides = {name: tmp_path / f"{name}.json" for name in ("own", "base", "head")}
    for name, answers in (("own", {"k0": "1", "k1": "1"}), ("base", {"k0": "1", "k1": "2"}),
                          ("head", {"k0": "3", "k1": "2"})):
        answer_replay.write_json(replay_of(answers, service=name[0] * 64, recording=digest), sides[name])
    out = tmp_path / "new/diff.json"
    arguments = ["diff", str(directory), str(sides["base"]), str(sides["head"]), "--output", str(out)]
    for extra in ([], ["--recording-answers", str(sides["own"])]):
        monkeypatch.setattr(sys, "argv", ["answer_cutoff.py", *arguments, *extra])
        assert answer_cutoff.main() == 0
        assert capsys.readouterr().out == f"1 of 2 answers changed: {out}\n"
    assert answer_replay.read_json(out) == {
        "version": answer_replay.VERSION, "recording": digest, "base": "b" * 64, "head": "h" * 64, "cases": 2,
        "changed": ["k0"], "recording_dir": str(directory.resolve()), "recording_build": "o" * 64, "stale": ["k1"]}
    (tmp_path / "other").mkdir()
    other = recording(tmp_path / "other", {"v": {}}, {}, [])
    monkeypatch.setattr(sys, "argv", ["answer_cutoff.py", "diff", str(other), *arguments[2:]])
    with pytest.raises(SystemExit, match="the replays are not of"):
        answer_cutoff.main()
    for argv in ([], ["record"], ["diff", str(directory), str(sides["base"]), str(sides["head"])]):
        monkeypatch.setattr(sys, "argv", ["answer_cutoff.py", *argv])
        with pytest.raises(SystemExit):
            answer_cutoff.main()
    capsys.readouterr()
    top = help_text(answer_cutoff.main, [], monkeypatch, capsys)
    assert "\n".join(answer_cutoff.__doc__.splitlines()[12:14]) in top
    assert "record every unit's coverage and ve_service requests" in top
    assert "the changed answers of two replays, for --cutoff answers=" in top
    record = help_text(answer_cutoff.main, ["record"], monkeypatch, capsys)
    for text in ("directory for the map, the index and the cases", "seconds per test file",
                 "directory for the per-unit records (default: a temporary one)", "keep the per-unit records",
                 "binaries are already built", "record only these units"):
        assert text in record, text
    assert "needed when the base build is another" in help_text(answer_cutoff.main, ["diff"], monkeypatch, capsys)


@pytest.mark.parametrize("tool", ["answer_replay", "answer_cutoff"])
def test_the_tools_run_as_scripts(tmp_path, tool):
    directory = recording(tmp_path, {"u": {"x": [SERVICE]}}, {"u": entry(0)}, ["k0"])
    digest = answer_replay.digest_file(directory / "requests.json.gz")
    base, head = tmp_path / "base.json", tmp_path / "head.json"
    answer_replay.write_json(replay_of({"k0": "1"}, recording=digest), base)
    answer_replay.write_json(replay_of({"k0": "2"}, recording=digest), head)
    arguments = [str(directory)] if tool == "answer_cutoff" else []
    done = subprocess.run([sys.executable, str(ROOT / f"tools/{tool}.py"), "diff", *arguments, str(base), str(head),
                           "--output", str(tmp_path / "diff.json")], cwd=tmp_path, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)
    assert done.returncode == 0, done.stderr
    assert answer_replay.read_json(tmp_path / "diff.json")["changed"] == ["k0"]


def test_record_writes_a_recording_select_answers_reads(tmp_path, monkeypatch, capsys):
    """`record` runs the units under request recording and writes the map, the index and the cases; inside
    another request recording it marks that recording's unit unknown; a tree it cannot record records nothing."""
    root = tmp_path / "root"
    (root / answer_cutoff.SERVICE).parent.mkdir(parents=True)
    (root / answer_cutoff.SERVICE).write_bytes(b"service")
    monkeypatch.setattr(answer_cutoff, "ROOT", root)
    text, calls = '{"id":"a"}', []

    def record_units(units, work, jobs, timeout):
        requests = Path(os.environ["VE_TESTMAP_REQUESTS"])
        calls.append((units, work, jobs, timeout, requests, os.environ.get("VE_TESTMAP_REQUESTS_UNIT")))
        write_records(requests, units[0], [["q", "evaluate", key("evaluate", text), False]],
                      [{"k": key("evaluate", text), "m": "evaluate", "c": text}], [])
        return unit_results({unit: {"x": [SERVICE]} for unit in units})

    monkeypatch.setattr(test_map, "clean_head", lambda args: "0" * 40)
    monkeypatch.setattr(test_map, "build_natives", lambda: calls.append("build"))
    monkeypatch.setattr(test_map, "units", lambda: ["tests/test_all.py"])
    monkeypatch.setattr(test_map, "record_units", record_units)
    outer, output, work = tmp_path / "outer", tmp_path / "out/recording", tmp_path / "work"

    def run(**options) -> int:
        return answer_cutoff.record(argparse.Namespace(**{
            "output": str(output), "work": None, "jobs": 3, "timeout": 7.0, "units": [], "no_build": True,
            "keep": False, "allow_dirty": False, **options}))

    nested = outer / "units" / answer_cutoff.unit_directory("tests/test_outer.py")
    monkeypatch.setenv("VE_TESTMAP_REQUESTS", str(outer))
    monkeypatch.setenv("VE_TESTMAP_REQUESTS_UNIT", nested.name)
    assert run(work=str(work), units=["tests/test_a.py"], no_build=False, keep=True) == 0
    assert calls == ["build", (["tests/test_a.py"], work / "units", 3, 7.0, work / "requests", None)]
    assert (work / "requests").is_dir()
    index, data = answer_cutoff.load_recording(output)
    assert data["commit"] == index["commit"] == "0" * 40 and index["service"] == hashlib.sha256(b"service").hexdigest()
    assert index["keys"] == [key("evaluate", text)] and index["units"] == {"tests/test_a.py": entry(0, pins=())}
    assert [row["c"] for row in answer_replay.read_jsonl(output / "cases.jsonl.gz")] == [text]
    assert capsys.readouterr().out == f"recorded 1 units, 1 distinct cases and 0 environments: {output}\n"
    # Again, into the same output, inside the same outer recording, with a temporary work directory.
    monkeypatch.setenv("VE_TESTMAP_REQUESTS", str(outer))
    monkeypatch.setenv("VE_TESTMAP_REQUESTS_UNIT", nested.name)
    assert run() == 0
    temporary = calls[-1][1].parent
    assert calls[-1][0] == ["tests/test_all.py"] and temporary.name.startswith("ve-cutoff-record-")
    assert not temporary.exists()
    assert answer_cutoff.fold(outer, ["tests/test_outer.py"])["units"]["tests/test_outer.py"]["unknown"] == [
        "a nested request recording"]
    # A request recording without a unit is not nested; with no service built, the index names none.
    monkeypatch.setenv("VE_TESTMAP_REQUESTS", str(outer))
    monkeypatch.delenv("VE_TESTMAP_REQUESTS_UNIT", raising=False)  # record popped it
    (root / answer_cutoff.SERVICE).unlink()
    assert run() == 0
    assert len(answer_cutoff.lines(next(nested.glob("*.jsonl")))) == 2
    assert answer_cutoff.load_recording(output)[0]["service"] is None
    assert "build" not in calls[1:]
    monkeypatch.delenv("VE_TESTMAP_REQUESTS")
    monkeypatch.setenv("VE_TESTMAP_REQUESTS_UNIT", nested.name)
    assert run() == 0 and len(answer_cutoff.lines(next(nested.glob("*.jsonl")))) == 2
    monkeypatch.setattr(test_map, "clean_head", lambda args: None)
    assert run(output=str(tmp_path / "dirty")) == 2 and not (tmp_path / "dirty").exists()


def test_the_hook_passes_its_rule_and_is_off_by_default(monkeypatch, capsys):
    """`select_tests.py --cutoff RULE` plans through answer_cutoff with that rule; without the flag,
    the plan is select_tests' own and answer_cutoff is not consulted."""
    calls = []
    plan = {"selected": [], "selected_count": 0, "full_count": 0, "full": False, "full_reasons": [], "map": None,
            "seconds": 0, "commands": [], "reasons": {}}
    monkeypatch.setattr(select_tests, "select", lambda paths, **options: calls.append(("plain", paths, options)) or plan)
    monkeypatch.setattr(answer_cutoff, "select", lambda rule, paths, **options: calls.append((rule, paths, options))
                        or plan)
    for argv in (["--paths", "README.md", "--json"], ["--paths", "README.md", "--json", "--cutoff", "answers=d.json"]):
        monkeypatch.setattr(sys, "argv", ["select_tests.py", *argv])
        assert select_tests.main() == 0
    options = {"full": False, "base": "HEAD", "after": None, "coverage": "auto", "assume_fresh": False}
    assert calls == [("plain", ["README.md"], options), ("answers=d.json", ["README.md"], options)]
    capsys.readouterr()
    assert "--cutoff RULE" in help_text(select_tests.main, [], monkeypatch, capsys)
    assert "narrow the ve_service users a Lean change selects" in help_text(select_tests.main, [], monkeypatch, capsys)


@pytest.mark.parametrize("rule", [None, "modes"])
def test_a_feedback_run_takes_the_r1_rule_and_nothing_else_does(monkeypatch, capsys, rule):
    """R1 is `select_tests.py --run`: a run that names no rule takes R1_RULE; a plan print, a --full run and a
    run that names its rule (`--cutoff off` included) do not."""
    calls = []
    plan = {"selected": [], "selected_count": 0, "full_count": 0, "full": False, "full_reasons": [], "map": None,
            "seconds": 0, "commands": [], "reasons": {}, "changed": [], "lean_build": False, "lean_cutoff": None}
    monkeypatch.setattr(answer_cutoff, "R1_RULE", rule)
    monkeypatch.setattr(select_tests, "select", lambda paths, **options: calls.append("plain") or plan)
    monkeypatch.setattr(answer_cutoff, "select", lambda chosen, paths, **options: calls.append(chosen) or plan)
    monkeypatch.setattr(select_tests, "run", lambda *args, **options: 0)
    for argv in (["--run"], [], ["--run", "--full"], ["--run", "--cutoff", "off"]):
        monkeypatch.setattr(sys, "argv", ["select_tests.py", "--paths", "README.md", "--json", *argv])
        assert select_tests.main() == 0
    assert calls == [rule or "plain", "plain", "plain", "off"]
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


def test_a_case_answers_alike_alone_and_in_a_batch(executable):
    """An error result carries its position in the request (`case_index`); the answer leaves it out, as it
    leaves out `index`, so a batch that one build answers and another refuses compares case by case."""
    deep = {"id": "deep", "environment": EVALUATION[0]["environment"], "ast": [["not"] * 300]}
    nested: object = [["top"]]
    for _ in range(300):
        nested = ["not", nested]
    deep["ast"] = [nested]
    texts = [lean_service._dumps(case) for case in (EVALUATION[1], deep)]
    with lean_service.LeanService(executable) as service:
        together = answer_replay.ask(service, "evaluate", texts)
        alone = [answer_replay.ask(service, "evaluate", [text])[0] for text in texts]
        response = answer_replay.send(service, "evaluate", texts)
    assert response["status"] == "ok" and response["results"][1]["result"]["case_index"] == 1
    assert together == alone
    entry = {"digest": "d", "index": 3, "result": {"case_index": 3, "error": "x", "status": "error"}}
    assert answer_replay.unplaced(entry) == {"digest": "d", "result": {"error": "x", "status": "error"}}


def test_a_case_named_by_handle_is_replayed_inline_as_the_client_resends_it(tmp_path, executable):
    """The inline form answers as the handle did, and leaves no state in the process to vary the next answer."""
    case = EVALUATION[0]
    [sent] = lean_service._encode([case])
    assert sent.digest is not None
    text = answer_replay.inline(sent.text, {sent.digest: sent.environment})
    assert json.loads(text) == json.loads(lean_service._dumps(case))
    with lean_service.LeanService(executable, handles=True) as handled, \
            lean_service.LeanService(executable, handles=False) as plain:
        answers = [[{k: v for k, v in answer_replay.unplaced(entry).items() if k != "digest"} for entry in entries]
                   for entries in (handled.run_bound("evaluate", [case]),
                                   answer_replay.send(plain, "evaluate", [text])["results"])]
    assert answers[0] == answers[1] and answers[0]


def test_answers_read_todays_map_and_count_the_recordings_staleness(tmp_path, monkeypatch):
    """Today's rules read the map R1 reads; only the requests come from the recording. A unit that ran code
    changed since the recording, and a service user the recording lacks, are unknown; with no map at all
    the plan is today's."""
    fresh, stale, unrecorded = ("tests/test_time_w6a.py", "tests/test_wire_contract_lean.py",
                                "tests/test_risk_integration.py")
    directory = recording(tmp_path, {fresh: {"x": [SERVICE]}, stale: {"x": [SERVICE]}},
                          {fresh: entry(0), stale: entry(1)}, ["k0", "k1"])
    path = tmp_path / "diff.json"
    answer_replay.write_json({"version": answer_replay.VERSION, "recording_dir": str(directory),
                              "recording": answer_replay.digest_file(directory / "requests.json.gz"),
                              "base": "a" * 64, "head": "b" * 64, "cases": 2, "changed": []}, path)
    today = select_tests.Coverage(make_map({unit: {"x": [SERVICE]} for unit in (fresh, stale, unrecorded)}))
    monkeypatch.setattr(select_tests, "uncertain_since", lambda coverage, *args: (
        {stale} if coverage is not today else set(), 1))
    seen = []
    # Today's selection gets the options as select_answers got them, its defaults included.
    passed = {"full": False, "base": "HEAD", "after": None, "assume_fresh": False}

    def plan(paths, *, coverage, **options):
        seen.append(coverage)
        assert options == passed
        return {"selected": sorted(select_tests.service_impact(coverage, None, "lean/VE/Rights/Run.lean"))}

    monkeypatch.setattr(select_tests, "select", plan)
    selected = answer_cutoff.select_answers(path, ["lean/VE/Rights/Run.lean"], base="HEAD", after=None,
                                            coverage=today, build="b" * 64)
    assert selected["selected"] == sorted([stale, unrecorded])
    assert set(seen[0].tests) == {fresh, stale, unrecorded}
    monkeypatch.setattr(select_tests, "select", lambda paths, **options: seen.append(options) or {"selected": ["everything"]})
    assert answer_cutoff.select_answers(path, [], base="HEAD", after=None, coverage=None, build="b" * 64) == {
        "selected": ["everything"],
        "cutoff": {"rule": "answers", "diff": str(path), "note": "no coverage map: today's selection"}}
    assert seen[-1] == {**passed, "coverage": None}


def test_the_pin_exemption_and_the_stale_answers_reach_the_plan(tmp_path, monkeypatch):
    """select_answers exempts from a pin change only the client-only pin readers whose recording is current,
    and only when the new build is pinned (read from the pins unless `head_pinned` says); the diff's stale
    answers make their readers unknown."""
    fresh, drifted, reader = "tests/test_time_w6a.py", "tests/test_wire_contract_lean.py", "tests/test_risk_integration.py"
    # Read the pins as data as well as through the client's check, and not at all when recorded.
    data_too, unrecorded = "tests/test_lean_build.py", "tests/test_nested_pytest.py"
    units = (fresh, drifted, reader, data_too, unrecorded)
    directory = recording(tmp_path, {unit: {"x": [SERVICE]} for unit in units},
                          {fresh: entry(0), drifted: entry(1), reader: entry(2), data_too: entry(0, pins=("client", "data")),
                           unrecorded: entry(0, pins=())}, ["k0", "k1", "k2"])
    path = tmp_path / "diff.json"
    answer_replay.write_json({"version": answer_replay.VERSION, "recording_dir": str(directory),
                              "recording": answer_replay.digest_file(directory / "requests.json.gz"),
                              "base": "c" * 64, "recording_build": "a" * 64, "stale": ["k2"],
                              "head": "b" * 64, "cases": 3, "changed": []}, path)
    today = select_tests.Coverage(make_map({unit: {"x": [SERVICE], "r": [answer_cutoff.PIN_FILE]} for unit in units}))
    monkeypatch.setattr(select_tests, "uncertain_since", lambda coverage, *args: ({drifted}, 1))
    monkeypatch.setattr(select_tests, "select", lambda paths, *, coverage, **options: {
        "pins": sorted(coverage.readers(answer_cutoff.PIN_FILE)),
        "service": sorted(select_tests.service_impact(coverage, None, "lean/VE/Rights/Run.lean"))})
    asked = []

    def plan(pins_admit: bool, head_pinned=None):
        asked.clear()
        monkeypatch.setattr(answer_cutoff, "pinned", lambda build, after: asked.append((build, after)) or pins_admit)
        return answer_cutoff.select_answers(path, [answer_cutoff.PIN_FILE], base="HEAD", after=None,
                                            coverage=today, build="b" * 64, head_pinned=head_pinned)

    exempt = plan(True)
    assert asked == [("b" * 64, None)] and exempt["cutoff"]["head_pinned"] is True
    # drifted: its recorded pin reads may be others now; data_too reads them as data too.
    assert exempt["pins"] == sorted([drifted, data_too, unrecorded])
    assert exempt["service"] == sorted([drifted, reader])
    assert exempt["cutoff"]["unknown"][reader] == "an answer it read changed between the recording's build and the base's"
    assert exempt["cutoff"]["request_handling"] == []
    assert plan(False)["pins"] == sorted(units) and asked == [("b" * 64, None)]
    assert plan(True, head_pinned=False)["pins"] == sorted(units) and asked == []
    assert plan(False, head_pinned=True)["pins"] == sorted([drifted, data_too, unrecorded])


def test_a_feedback_run_takes_the_modes_rule():
    """R1_RULE as the report activates it (docs/test-architecture/cutoff/REPORT.md): ts-B2's per-mode rule."""
    assert answer_cutoff.R1_RULE == "modes"


def test_r1_never_takes_the_answers_rule():
    """R1's rule is ts-B2's per-mode rule or none: the answers rule is opt-in until the DRI reads its measurement."""
    assert answer_cutoff.R1_RULE in (None, "modes")
