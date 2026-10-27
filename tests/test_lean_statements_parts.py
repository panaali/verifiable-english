"""tools/lean_statements.py prints the statements in parts run at once (eff-20261027-1, PIPELINE-LIMITS L76).

* `statement_parts` cuts the sorted names into contiguous parts that cover every name once, in order.
* `print_statements` joins the parts' outputs in part order, whatever order the runs finish in; one failed part
  fails the dump with its label and its output; with one part it is the single run of before (`Statements` over
  `names.txt`, the same script and environment).

Hermetic: `run_lean` is replaced, or `lake` is a fake on PATH; no Lean runs.
"""
from __future__ import annotations

import os
from pathlib import Path
import sys
import threading

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lean_statements as L  # noqa: E402
from subprocesses import HANG_TIMEOUT  # noqa: E402


def _names(count: int) -> list[str]:
    return [f"VE.t{index:03d}" for index in range(count)]


def _entries(names: list[str]) -> str:
    return "".join(f"theorem {name}\n  {name} = {name}\n" for name in names)


def test_parts_are_contiguous_and_cover_every_name_once_in_order():
    for size in range(0, 30):
        names = _names(size)
        for count in range(1, 12):
            parts = L.statement_parts(names, count)
            assert [name for part in parts for name in part] == names, (size, count)
            assert len(parts) == max(1, min(count, size)), (size, count)
            if size:
                assert all(parts), (size, count)
                assert max(map(len, parts)) - min(map(len, parts)) <= 1, (size, count)


def test_the_part_count_is_the_constant_at_most_one_per_core(monkeypatch):
    for cores, expected in ((None, 1), (1, 1), (4, 4), (L.STATEMENT_PARTS, L.STATEMENT_PARTS),
                            (64, L.STATEMENT_PARTS)):
        monkeypatch.setattr(L.os, "cpu_count", lambda cores=cores: cores)
        assert L.statement_count() == expected


def test_one_part_is_the_single_run_of_before(tmp_path, monkeypatch):
    calls = []

    def run_lean(root, folder, script, label, env):
        calls.append((root, folder, script, label, env, Path(env["VE_STATEMENT_NAMES"]).read_text()))
        return _entries(_names(5))

    monkeypatch.setattr(L, "run_lean", run_lean)
    names = _names(5)
    assert L.print_statements(ROOT, tmp_path, names, 1) == _entries(names)
    assert calls == [(ROOT, tmp_path, L.SCRIPT, "Statements", {"VE_STATEMENT_NAMES": str(tmp_path / "names.txt")},
                      "\n".join(names) + "\n")]


def test_parts_run_the_same_script_and_are_joined_in_part_order(tmp_path, monkeypatch):
    """Each part waits for the next one to finish, so the runs finish in reverse order; the joined text is
    still in name order."""
    count = 4
    finished = [threading.Event() for _ in range(count + 1)]
    finished[count].set()
    seen = {}

    def run_lean(root, folder, script, label, env):
        index = int(label.removeprefix("Statements"))
        assert finished[index + 1].wait(HANG_TIMEOUT)
        assert script == L.SCRIPT and set(env) == {"VE_STATEMENT_NAMES"}
        assert Path(env["VE_STATEMENT_NAMES"]) == folder / f"names{index}.txt"
        part = [name for name in Path(env["VE_STATEMENT_NAMES"]).read_text().splitlines() if name]
        seen[index] = part
        finished[index].set()
        return _entries(part)

    monkeypatch.setattr(L, "run_lean", run_lean)
    names = _names(10)
    assert L.print_statements(ROOT, tmp_path, names, count) == _entries(names)
    assert [seen[index] for index in range(count)] == L.statement_parts(names, count)


FAKE_LAKE = """#!{python}
import os, sys
names = open(os.environ["VE_STATEMENT_NAMES"]).read().split()
if "{bad}" in names:
    sys.stderr.write("error: the part with {bad} failed\\n")
    sys.exit(3)
for name in names:
    print(f"theorem {{name}}\\n  {{name}} = {{name}}")
"""


def test_a_failed_part_fails_the_dump_with_its_label_and_output(tmp_path, monkeypatch):
    names = _names(12)
    bad = L.statement_parts(names, 4)[2][1]
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    (tmp_path / "lean").mkdir()
    lake = bin_ / "lake"
    lake.write_text(FAKE_LAKE.format(python=sys.executable, bad=bad))
    lake.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_}{os.pathsep}{os.environ['PATH']}")
    folder = tmp_path / "work"
    folder.mkdir()
    with pytest.raises(SystemExit) as failed:
        L.print_statements(tmp_path, folder, names, 4)
    assert "lake env lean failed on Statements2 (3)" in str(failed.value.code)
    assert f"the part with {bad} failed" in str(failed.value.code)
    good = [name for name in names if name != bad]
    assert L.print_statements(tmp_path, folder, good, 4) == _entries(good)
