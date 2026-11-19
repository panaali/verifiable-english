"""Module B of the use-case leak pair: it runs after tests/test_sysmodules_leak_a.py in the same process.

Module A imported usecases/eligibility's `run` and `translation` by bare name at collection. None of
those harness modules, nor A's use-case directory, may be left for this module's tests; the package
modules A's import loaded (`ve.*`, `tools.*`) must be left in place, never dropped and re-imported.

    uv run pytest -q -p no:xdist tests/test_sysmodules_leak_a.py tests/test_sysmodules_leak_b.py
"""
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
A_CASE = ROOT / "usecases" / "eligibility"


def _from_a_case(module):
    file = getattr(module, "__file__", None)
    return isinstance(file, str) and Path(file).resolve().is_relative_to(A_CASE)


def test_module_a_left_no_harness_module_and_no_use_case_directory():
    for name in ("translation", "run", "reference"):
        assert not _from_a_case(sys.modules.get(name)), f"{name} is still module A's {sys.modules[name]}"
    assert not [entry for entry in sys.path if entry and Path(entry).resolve() == A_CASE]


def test_package_modules_stay_loaded_and_bound_to_their_package():
    """Each submodule a package holds as an attribute is still that entry of `sys.modules`: none was
    dropped (a later import would load a second copy) while the use-case modules were cleared."""
    for package in ("ve", "ve.backends", "tools"):
        held = {name: value for name, value in vars(sys.modules[package]).items()
                if isinstance(value, types.ModuleType) and value.__name__ == f"{package}.{name}"}
        assert held, package
        for value in held.values():
            assert sys.modules.get(value.__name__) is value, value.__name__
