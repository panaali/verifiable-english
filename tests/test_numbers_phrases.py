"""The existing English reader consumes the Lean-generated comparison rows."""
import json
import os
from pathlib import Path
import subprocess
import sys

from subprocesses import HANG_TIMEOUT
from ve import ast
from ve.english import _COMPARISONS
from tools import numbers_phrases

ROOT = Path(__file__).resolve().parents[1]


def test_the_committed_table_is_the_lean_generators_output():
    """Review F1 (me-1a): the committed rows are what `VE/Numbers/PhrasesMain.lean` prints now, checked by the
    generator itself, unmocked, so an edit of `orderPhrases` without `--write` fails the suite. elan's `lake` is
    the fallback when PATH has none."""
    env = {**os.environ, "PATH": os.environ.get("PATH", "") + os.pathsep + str(Path.home() / ".elan/bin")}
    done = subprocess.run([sys.executable, str(ROOT / "tools/numbers_phrases.py"), "--check"], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert done.returncode == 0, (done.stdout, done.stderr)


def test_comparison_rows_match_generated_table():
    path = ROOT / "ve/numbers_phrases.json"
    rows = json.loads(path.read_text())
    operators = {"eq": ast.Eq, "lt": ast.Lt, "le": ast.Le}
    assert _COMPARISONS == tuple(
        (row["text"], operators[row["rel"]], row["swap"]) for row in rows
    )
    assert len(rows) == 4
    assert len({row["text"] for row in rows}) == 4
    assert rows == [
        {"rel": "lt", "swap": False, "text": "{0} is less than {1}"},
        {"rel": "le", "swap": False, "text": "{0} is at most {1}"},
        {"rel": "lt", "swap": True, "text": "{0} is more than {1}"},
        {"rel": "le", "swap": True, "text": "{0} is at least {1}"},
    ]


def test_generator_writes_lean_output_and_check_refuses_any_other_file(tmp_path, monkeypatch):
    """`--write` stores exactly what the Lean generator printed; `--check` passes only on that file, and a
    generator failure is never a pass. The Lean run is replaced by its recorded output."""
    target = tmp_path / "numbers_phrases.json"
    printed = (ROOT / "ve/numbers_phrases.json").read_text()
    result = subprocess.CompletedProcess([], 0, stdout=printed.rstrip("\n"), stderr="")
    monkeypatch.setattr(numbers_phrases, "TARGET", target)
    monkeypatch.setattr(numbers_phrases.subprocess, "run", lambda *args, **kwargs: result)

    def run(flag):
        monkeypatch.setattr(sys, "argv", ["numbers_phrases.py", flag])
        return numbers_phrases.main()

    assert run("--check") == 1  # no file yet
    assert run("--write") == 0 and target.read_text() == printed
    assert run("--check") == 0
    target.write_text(printed.replace('"swap":true', '"swap":false', 1))
    assert run("--check") == 1
    target.write_text(printed.rstrip("\n"))
    assert run("--check") == 1
    target.write_text(printed)
    result.returncode = 1
    assert run("--check") == 1 and run("--write") == 1
    assert target.read_text() == printed
