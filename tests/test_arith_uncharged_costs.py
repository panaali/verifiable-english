"""me-12nb: the uncharged-cost fixtures of spec 12.2 stay selected (DRI decision 2026-10-27 on me-12nb, its condition).

`docs/math-evidence/me-12nb/uncharged-costs.lean` is evidence outside Lake's targets, so `lake build` never runs its
`#guard`s; this test runs the file with `lake env lean`, so every Lean change selects it (it runs Lean) and so does an
edit of the file (it names it). Lean decides every answer: the guards are the file's, and Python only checks that
Lean accepts them and that each guard the decision keeps is still there. Its review F1 found the file run by nothing.
"""
import re
import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, ROOT, lean_build

FIXTURE = ROOT / "docs/math-evidence/me-12nb/uncharged-costs.lean"
IMPORT = "VE.Arith.BoundedExamples"

# The guards the decision keeps, each as a text its `#guard` line carries: the parameter read, the name lookup's count
# at its acceptance boundary (6,147 units, unchanged), the name lookup and the 65,537-bit countdown UNKNOWN at maxSteps.
GUARDS = {
    "parameter read": "decideBounded wide maxSteps",
    "name lookup count": "= some (true, 6147)",
    "name lookup exhaustion": "decideBounded dense maxSteps (.allFromTo (lit 1) (lit 1000)",
    "countdown": "decideBounded (sqChain 16) maxSteps",
}
UNKNOWN = ("parameter read", "name lookup exhaustion", "countdown")


def guard_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith("#guard ")]


def run_lean(lake: str, source) -> subprocess.CompletedProcess:
    return subprocess.run([lake, "env", "lean", str(source)], cwd=LEAN, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)


@pytest.fixture(scope="module")
def lake():
    found = shutil.which("lake")
    if found is None:
        pytest.skip("lake is not available")
    lean_build(IMPORT.split(".")[0])
    return found


def test_the_file_imports_a_built_module():
    assert FIXTURE.read_text().splitlines()[0] == f"import {IMPORT}"


def test_every_kept_guard_is_there():
    lines = guard_lines(FIXTURE.read_text())
    found = {name: [line for line in lines if text in line] for name, text in GUARDS.items()}
    assert {name: len(hits) for name, hits in found.items()} == {name: 1 for name in GUARDS}
    for name in UNKNOWN:
        assert found[name][0].endswith(" = none"), name
    assert len(lines) == len(GUARDS)


def test_lean_accepts_every_guard(lake):
    """Review F1: the four guards run, and Lean accepts each."""
    done = run_lean(lake, FIXTURE)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "error" not in done.stdout + done.stderr


def test_a_failing_guard_fails_the_run(lake, tmp_path):
    """The run above can fail: the name lookup's count off by one is refused (the slow guards are left out)."""
    text = FIXTURE.read_text()
    count = next(line for line in guard_lines(text) if GUARDS["name lookup count"] in line)
    kept = [line for line in text.splitlines() if not line.startswith("#guard ")]
    wrong = count.replace("6147", "6148")
    assert wrong != count
    source = tmp_path / "Wrong.lean"
    source.write_text("\n".join([*kept[:-1], wrong, kept[-1]]) + "\n")
    done = run_lean(lake, source)
    assert done.returncode != 0
    assert re.search(r"error: Expression\n.*6148.*\ndid not evaluate to `true`", done.stdout + done.stderr, re.S)
