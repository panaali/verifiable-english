"""me-6b: `ve-units@2` (math-evidence spec 6.2; fixtures H-7, H-7c, H-7d, H-7l, H-7u and I-2).

Lean decides every answer here: the fixture table is `tests/calc_units_fixtures.py`; `lake build` evaluates it as
the `#guard`s of `lean/VE/Calc/UnitsExamples.lean`, and one Lean file prints each answer here with that module's
helpers, so a failure names its fixture. Python only states the fixtures. Dimensions alone are
`tests/test_calc_dimensions.py`'s.
"""
import importlib.util
import json
import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from tests.calc_units_fixtures import BAD, FIXTURES, I2, MALFORMED, MALFORMED_ANSWERS, paths
from tests.lean_build import LEAN, ROOT, lean_build

HEADER = """import VE.Calc.UnitsExamples
open Lean VE.Calc VE.Calc.Units VE.Numbers VE.Calc.UnitsExamples

def line (key value : String) : IO Unit := IO.println (key ++ "\\t" ++ value)
"""


@pytest.fixture(scope="module")
def lean(tmp_path_factory):
    lake = shutil.which("lake")
    if lake is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    source = tmp_path_factory.mktemp("units") / "Units.lean"
    source.write_text(HEADER + "".join(f"#eval line {json.dumps(key)} ({expression})\n"
                                       for key, expression, _ in FIXTURES + MALFORMED))
    done = subprocess.run([lake, "env", "lean", str(source)], cwd=LEAN, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)
    assert done.returncode == 0, done.stdout + done.stderr
    return dict(row.split("\t", 1) for row in done.stdout.splitlines())


@pytest.mark.parametrize("key, expected", [pytest.param(key, expected, id=key) for key, _, expected in FIXTURES])
def test_fixture(lean, key, expected):
    assert lean[key] == expected


@pytest.mark.parametrize("key, expected", [pytest.param(key, expected, id=key) for key, _, expected in MALFORMED])
def test_malformed_environment(lean, key, expected):
    """Each malformed environment gets Lean's whole answer, its JSON path included (checklist item 5)."""
    assert lean[key] == expected


def test_the_malformed_table_covers_every_node():
    """One row per node of I-2 and replacement, and each path's answers are stated for that path."""
    assert [key for key, _, _ in MALFORMED] == list(dict.fromkeys(key for key, _, _ in MALFORMED))
    assert len(MALFORMED) == len(list(paths(I2))) * len(BAD)
    assert sorted(MALFORMED_ANSWERS, key=str) == sorted(paths(I2), key=str)
    # No units, a dimensionless unit and an exponent of 7 (twice).
    assert sum(expected.startswith("ok ") for _, _, expected in MALFORMED) == 4


def test_every_fixture_printed_once(lean):
    assert sorted(lean) == sorted(key for key, _, _ in FIXTURES + MALFORMED)


def test_the_lean_guards_are_the_fixture_table():
    """`lean/VE/Calc/UnitsExamples.lean` is the rendering of the table, and the Lean build evaluates it."""
    spec = importlib.util.spec_from_file_location("calc_units_fixtures_tool", ROOT / "tools/calc_units_fixtures.py")
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    assert generator.TARGET.read_text() == generator.render()
    assert "import VE.Calc.UnitsExamples" in (ROOT / "lean/VE.lean").read_text().splitlines()
    text = generator.TARGET.read_text()
    assert text.count("\n#guard (") == len(FIXTURES) + len(MALFORMED)
    for key, _, _ in FIXTURES + MALFORMED:
        assert f"-- {key}\n#guard (" in text
