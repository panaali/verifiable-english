"""The run cache (`tools/run_cache.py`): a stored run is used only while every input it is keyed on is unchanged.

The cached run here is a nested pytest run of one test in a scratch repository that uses each kind of keyed
input once: its own file, a module it imports, a module it imports by a computed name (only the read
recorder sees it), a data file it opens, a directory it lists, a program it starts, and the keyed files the
run cannot be seen reading (the Lean and Rust binaries, the Lean sources, `uv.lock`), its settings and its
environment. Changing any one of them must run it again, and an unchanged second call must not.
"""
from __future__ import annotations

import gzip
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from subprocesses import HANG_TIMEOUT
from tools import nested_pytest, run_cache
from tools.gate import LEAN_BINARIES

ROOT = Path(__file__).resolve().parents[1]

CHECK = """import importlib, json, os, subprocess
from pathlib import Path
import helper
ROOT = Path(__file__).resolve().parents[1]
def test_tiny():
    dynamic = importlib.import_module("dynamic_" + "helper")
    data = json.loads((ROOT / "data.json").read_text())
    listed = sorted(path.name for path in (ROOT / "fixtures").iterdir())
    ran = subprocess.run([str(ROOT / "tool.sh")], capture_output=True, text=True, check=True).stdout
    Path(os.environ["VE_CONTRACT_INPUTS"]).write_text(json.dumps([helper.VALUE, dynamic.VALUE, data, listed, ran]))
"""


class Repository:
    def __init__(self, tmp_path, monkeypatch):
        self.root = root = tmp_path / "repository"
        files = {"checks/test_tiny.py": CHECK, "helper.py": "VALUE = 1\n", "dynamic_helper.py": "VALUE = 2\n",
                 "data.json": "[3]\n", "fixtures/one.txt": "", "tool.sh": "#!/bin/sh\necho 4\n",
                 "lean/lakefile.toml": "", "lean/VE.lean": "-- a module\n", "uv.lock": "version = 1\n",
                 "rust/target/release/ve": "rust binary",
                 **{f"lean/.lake/build/bin/{name}": "lean binary" for name in LEAN_BINARIES}}
        for name, text in files.items():
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text(text)
        (root / "tool.sh").chmod(0o755)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True, timeout=HANG_TIMEOUT)
        monkeypatch.setenv("VE_RUN_CACHE", str(tmp_path / "cache"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "xdg"))  # tools/source_graph.py's own cache
        self.output = tmp_path / "output.json"
        self.settings = {"units": ["tiny"]}
        self.environment = nested_pytest.environment(os.environ, PYTHONPATH=os.pathsep.join([str(ROOT), str(root)]))
        self.runs = 0

    def run(self, env):
        self.runs += 1
        return subprocess.run(nested_pytest.command(["-q", "-p", run_cache.PLUGIN, "-p", "no:cacheprovider",
                                                     "-o", "addopts=", "checks/test_tiny.py"]),
                              cwd=self.root, env={**env, "VE_CONTRACT_INPUTS": str(self.output)},
                              capture_output=True, text=True, timeout=HANG_TIMEOUT)

    def call(self, ok=lambda result: result.returncode == 0):
        self.output.unlink(missing_ok=True)
        result, status = run_cache.cached_run(self.output, starts=["checks/test_tiny.py"], settings=self.settings,
                                              environment=self.environment, run=self.run, ok=ok, root=self.root)
        assert result.returncode == 0, result.stdout + result.stderr
        return status, json.loads(self.output.read_text())

    def edit(self, name, text):
        (self.root / name).write_text(text)


@pytest.fixture
def repository(tmp_path, monkeypatch):
    return Repository(tmp_path, monkeypatch)


CHANGES = {
    "recorded test file": lambda r: r.edit("checks/test_tiny.py", CHECK + "# edited\n"),
    "imported module": lambda r: r.edit("helper.py", "VALUE = 10\n"),
    "module imported by a computed name": lambda r: r.edit("dynamic_helper.py", "VALUE = 20\n"),
    "data file opened": lambda r: r.edit("data.json", "[30]\n"),
    "directory listed": lambda r: r.edit("fixtures/two.txt", ""),
    "program started": lambda r: r.edit("tool.sh", "#!/bin/sh\necho 40\n"),
    "Lean binary": lambda r: r.edit("lean/.lake/build/bin/ve_service", "another lean binary"),
    "Rust binary": lambda r: r.edit("rust/target/release/ve", "another rust binary"),
    "Lean source": lambda r: r.edit("lean/VE.lean", "-- another module\n"),
    "new Lean source": lambda r: r.edit("lean/Other.lean", "-- a new module\n"),
    "lock": lambda r: r.edit("uv.lock", "version = 2\n"),
    "settings": lambda r: r.settings.update(units=["tiny", "other"]),
    "environment": lambda r: r.environment.update(VE_AUTHORITY="lean"),
}


@pytest.mark.parametrize("change", CHANGES)
def test_changing_any_keyed_input_runs_again(repository, change):
    first = repository.call()
    assert first == ("miss", [1, 2, [3], ["one.txt"], "4\n"]) and repository.runs == 1
    assert repository.call() == ("hit", first[1]) and repository.runs == 1
    CHANGES[change](repository)
    status, output = repository.call()
    assert status == "miss" and repository.runs == 2, change
    # The new run's output is stored: the next call is a hit with it.
    assert repository.call() == ("hit", output) and repository.runs == 2


def test_the_observed_reads_are_keyed(repository):
    """What the read recorder saw is in the entry: a module imported by a computed name, the data file, the
    listed directory and the program, which the static closure does not hold."""
    repository.call()
    [path] = (Path(os.environ["VE_RUN_CACHE"])).glob("*.json.gz")
    with gzip.open(path, "rt") as handle:
        entry = json.load(handle)
    dynamic, static = entry["dynamic"], entry["static"]
    assert {"file:dynamic_helper.py", "file:data.json", "directory:fixtures", "program:tool.sh",
            "file:checks/test_tiny.py", "file:helper.py"} <= set(dynamic)
    assert "file:dynamic_helper.py" not in static and "file:helper.py" in static
    assert {f"program:lean/.lake/build/bin/{name}" for name in LEAN_BINARIES} | {
        "program:rust", "file:lean/VE.lean", "file:uv.lock", "python", "settings", "environment"} <= set(static)


def test_a_run_the_caller_does_not_accept_is_not_stored(repository):
    assert repository.call(ok=lambda result: False)[0] == "miss"
    assert repository.call()[0] == "miss" and repository.runs == 2
    assert repository.call()[0] == "hit" and repository.runs == 2


def test_a_run_without_the_read_recorder_is_not_stored(repository, monkeypatch):
    """With nothing recorded, no entry could be checked later."""
    plain = repository.run
    monkeypatch.setattr(repository, "run", lambda env: plain({k: v for k, v in env.items() if k != "VE_RECORD_READS"}))
    assert [repository.call()[0] for _ in range(2)] == ["miss", "miss"]


def test_the_cache_can_be_turned_off(repository, monkeypatch):
    monkeypatch.setenv("VE_RUN_CACHE", "off")
    assert [repository.call()[0] for _ in range(2)] == ["off", "off"] and repository.runs == 2


def test_the_checkout_path_and_the_runs_outputs_are_not_keyed(repository):
    """Worktrees share entries: a setting naming the checkout is keyed as `<root>`; what it names, by content.
    A setting naming a run's own output (a fresh temporary path each run) is not an input."""
    root = str(repository.root)
    settings = run_cache.run_settings(repository.root, {
        "VE_RUST_BINARY": f"{root}/rust/target/release/ve", "VE_CONTRACT_INPUTS": "/tmp/x", "PATH": "/bin",
        "VE_ENGLISH_COMPARATOR_DIR": "/tmp/ve-english-comparator-1", "VE_SHADOW_LOG": "/tmp/c/controller.jsonl"})
    assert settings == {"VE_RUST_BINARY": "<root>/rust/target/release/ve"}


def test_the_read_recorder_keeps_checkout_paths_only(monkeypatch):
    sys.path.insert(0, str(ROOT))
    from tests import read_recorder
    monkeypatch.setattr(read_recorder, "ROOT", str(ROOT))
    assert read_recorder.relative(ROOT / "ve/core.py") == "ve/core.py"
    assert read_recorder.relative(os.fsencode(ROOT / "ve/core.py")) == "ve/core.py"
    assert read_recorder.relative("ve/core.py", base=str(ROOT)) == "ve/core.py"
    for outside in ("/etc/passwd", 3, None, "", ROOT / ".venv/lib/x.py", ROOT / "ve/__pycache__/core.pyc",
                    ROOT / "lean/.lake/build/lib/VE.olean", ROOT / ".git/HEAD"):
        assert read_recorder.relative(outside) is None, outside
    # A program is kept wherever it is in the checkout, but the interpreter.
    assert read_recorder.relative(ROOT / "lean/.lake/build/bin/ve_service", None,
                                  read_recorder.PROGRAMS_SKIPPED) == "lean/.lake/build/bin/ve_service"
    assert read_recorder.relative(ROOT / ".venv/bin/python", None, read_recorder.PROGRAMS_SKIPPED) is None


def test_entries_live_in_the_git_common_directory(monkeypatch):
    """Shared by the checkout's worktrees; `VE_RUN_CACHE` moves the cache or turns it off."""
    monkeypatch.delenv("VE_RUN_CACHE", raising=False)
    common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=ROOT,
                            capture_output=True, text=True, check=True, timeout=HANG_TIMEOUT).stdout.strip()
    assert run_cache.cache_directory(ROOT) == Path(common) / "ve-run-cache"
    monkeypatch.setenv("VE_RUN_CACHE", "/somewhere")
    assert run_cache.cache_directory(ROOT) == Path("/somewhere")
    monkeypatch.setenv("VE_RUN_CACHE", "off")
    assert run_cache.cache_directory(ROOT) is None
