"""Module A of the use-case leak pair; tests/test_sysmodules_leak_b.py runs after it in the same process.

Like tests/test_eligibility_wfp.py, it puts a use case's directory on `sys.path` and imports that use
case's harness modules by bare name at module level, during collection. While its own tests run, those
modules and that directory are its own, and a sibling the harness imports lazily at call time resolves
from the same directory. tests/conftest.py (`harness_modules_stay_with_their_test_module`) keeps them
from reaching module B.

    uv run pytest -q -p no:xdist tests/test_sysmodules_leak_a.py tests/test_sysmodules_leak_b.py
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "usecases" / "eligibility"
sys.path.insert(0, str(HERE))

import run  # noqa: E402
import translation  # noqa: E402


def test_its_own_harness_modules_and_directory_are_in_place_while_its_tests_run():
    assert sys.modules["translation"] is translation is run.T
    assert sys.modules["run"] is run
    assert str(HERE) in sys.path


def test_a_sibling_the_harness_imports_lazily_at_call_time_comes_from_its_own_use_case():
    data = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
    case = data["cases"][0]
    model = run.fixture_model(case, data["defaults"])  # `import reference as R` inside the call
    assert model
    assert Path(sys.modules["reference"].__file__).resolve() == HERE / "reference.py"
