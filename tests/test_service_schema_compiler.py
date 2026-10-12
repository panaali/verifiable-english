"""The response schema compiler (`ve/backends/service_schema.py`): what it reads and when,
and that compiling on first use is safe from the service pool's threads.

* Importing the module reads no mode's schema; checking a mode reads only the files its
  `$ref`s can reach, so editing one mode's schema does not touch every importer.
* Many threads using a mode for the first time all get the finished validator: a
  rejected row raises `Invalid`, never `TypeError` from a cell still being compiled.
* A compile that fails leaves no half-built cell or fuel counter behind.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import threading

import pytest

from subprocesses import HANG_TIMEOUT
from ve.backends.service_schema import DIRECTORY, MODES, Compiler, Context, Invalid, SchemaError

ROOT = Path(__file__).resolve().parents[1]
THREADS = 8


def _refs(node: object):
    pending = [node]
    while pending:
        node = pending.pop()
        if isinstance(node, dict):
            if isinstance(node.get("$ref"), str):
                yield node["$ref"]
            pending.extend(node.values())
        elif isinstance(node, list):
            pending.extend(node)


def reachable_files(name: str) -> set[str]:
    """Every schema file a `$ref` chain from file `name` can name (an over-approximation)."""
    seen, pending = set(), [name]
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        for reference in _refs(json.loads((DIRECTORY / current).read_text())):
            pending.append(reference.partition("#")[0] or current)
    return seen


def test_mode_rows_compile_only_when_used():
    program = ("from ve.backends.service_schema import ROWS, _compiler\n"
               "assert not any(pointer == '/row' for _, pointer in _compiler._compiled)\n"
               "assert 'parse' in ROWS and 'not-a-mode' not in ROWS\n"
               "row = ROWS['parse']\n"
               "assert row is ROWS['parse']\n"
               "assert {name for name, pointer in _compiler._compiled if pointer == '/row'} "
               "== {'parse.json'}\n")
    subprocess.run([sys.executable, "-c", program], cwd=ROOT, check=True, timeout=HANG_TIMEOUT)


def test_import_reads_no_schema_and_a_mode_reads_only_what_it_reaches():
    program = '''
import json, sys
opened = []
sys.addaudithook(lambda event, args: opened.append(str(args[0])) if event == "open" else None)
from ve.backends import service_schema
from ve.backends.service_schema import DIRECTORY, MODES, Compiler, check_handshake, Invalid
directory = str(DIRECTORY) + "/"
def schema_reads():
    found = {path[len(directory):] for path in opened if path.startswith(directory) and path.endswith(".json")}
    opened.clear()
    return sorted(found)
reads = {"import": schema_reads()}
for mode in MODES:
    Compiler().ref(mode + ".json", "#/row")
    reads[mode] = schema_reads()
try:
    check_handshake(None)
except Invalid:
    pass
reads["handshake"] = schema_reads()
print(json.dumps(reads))
'''
    done = subprocess.run([sys.executable, "-c", program], cwd=ROOT, check=True, timeout=HANG_TIMEOUT,
                          capture_output=True, text=True)
    reads = json.loads(done.stdout.splitlines()[-1])
    # `ve.backends.lean_service` reads the handle bounds from the envelope, which every
    # response check uses; no mode's schema is read until that mode is checked.
    assert reads.pop("import") in ([], ["envelope.json"])
    assert set(reads.pop("handshake")) <= reachable_files("envelope.json")
    every = {path.name for path in DIRECTORY.glob("*.json")}
    for mode in MODES:
        assert f"{mode}.json" in reads[mode]
        assert set(reads[mode]) <= reachable_files(f"{mode}.json"), mode
    # Not vacuous: some mode reaches strictly fewer files than exist.
    assert any(set(reads[mode]) < every for mode in MODES)
    assert "norms.json" not in reads["parse"]


def test_threads_using_a_mode_for_the_first_time_get_the_finished_validator():
    compiler = Compiler()
    problems: list[str] = []

    def first_use(mode, barrier, cells):
        barrier.wait()
        try:
            cell = compiler.ref(f"{mode}.json", "#/row")
            cells.append(cell)
            cell[0](7, Context({}, 0), {})
            problems.append(f"{mode}: a number was accepted as a row")
        except Invalid:
            pass
        except Exception as exc:  # the finding: TypeError from an unfilled cell
            problems.append(f"{mode}: {type(exc).__name__}: {exc}")

    for mode in MODES:
        barrier, cells = threading.Barrier(THREADS), []
        threads = [threading.Thread(target=first_use, args=(mode, barrier, cells)) for _ in range(THREADS)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(HANG_TIMEOUT)
        assert len(cells) == THREADS and all(cell is cells[0] for cell in cells), mode
    assert problems == []
    assert sorted(compiler.counters.values()) == list(range(len(compiler.counters)))
    assert all(cell[0] is not None for cell in compiler._compiled.values())


def test_public_rows_are_safe_on_first_use_from_many_threads():
    """The review's probe, for every mode, through the module's shared `ROWS`."""
    program = f'''
import threading
from ve.backends import service_schema as s
for mode in s.MODES:
    barrier, found = threading.Barrier({THREADS}), []
    def use():
        barrier.wait()
        found.append(s.ROWS[mode][0])
    threads = [threading.Thread(target=use) for _ in range({THREADS})]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert len(found) == {THREADS} and None not in found, (mode, found.count(None))
'''
    subprocess.run([sys.executable, "-c", program], cwd=ROOT, check=True, timeout=HANG_TIMEOUT)


@pytest.mark.parametrize("schema", [
    {"row": {"$ref": "missing.json#/x"}},
    {"row": {"$ref": "#/nowhere"}},
    {"row": {"properties": {"a": {"$ref": "#/row"}, "b": {"x-unknown": 1}}}},
    {"row": {"anyOf": [{"$ref": "#/row"}, {"$ref": "../a.json#/row"}]}},
    {"row": {"x-tagged": {"t": [{"$ref": "#/row"}, {"x-unknown": 1}]}, "x-fuel": {"counter": "c", "limit": 2}}},
])
def test_a_failed_compile_leaves_no_half_built_cell(schema, tmp_path):
    (tmp_path / "a.json").write_text(json.dumps(schema))
    compiler = Compiler(tmp_path)
    for _ in range(2):  # the second attempt fails the same way, never returns an unfilled cell
        with pytest.raises(SchemaError):
            compiler.ref("a.json", "#/row")
        assert compiler._compiled == {} and compiler.counters == {}
