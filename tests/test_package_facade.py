"""`ve/__init__.py` resolves its public names lazily: `import ve` loads no submodule, each name is its module's."""
from __future__ import annotations

import importlib
import subprocess
import sys

import pytest

import ve
from tests.subprocesses import HANG_TIMEOUT


def fresh(code: str) -> str:
    """Run `code` in a new interpreter (nothing of `ve` loaded yet) and return its output."""
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True,
                          timeout=HANG_TIMEOUT).stdout


def test_import_ve_loads_no_submodule():
    loaded = fresh("import sys, ve; print(' '.join(sorted(m for m in sys.modules if m.split('.')[0] == 've')))")
    assert loaded.split() == ["ve"]


@pytest.mark.parametrize("name", ve.__all__)
def test_every_public_name_is_its_modules_object(name):
    module = importlib.import_module(f"ve.{ve._MODULE[name]}")
    assert getattr(ve, name) is getattr(module, name)
    namespace: dict = {}
    exec("from ve import *", namespace)
    assert namespace[name] is getattr(module, name)


def test_public_names_are_the_table():
    assert sorted(ve.__all__) == sorted(name for names in ve._EXPORTS.values() for name in names)
    assert len(ve.__all__) == len(set(ve.__all__))
    assert set(ve.__all__) <= set(dir(ve))


def test_names_shared_with_their_modules_stay_functions():
    # Importing ve.check or ve.evaluate first binds the module on the package; the names stay the functions.
    out = fresh("import ve.check, ve.evaluate, sys\nimport ve\nfrom ve import check, evaluate\n"
                "print(ve.check is sys.modules['ve.check'].check, ve.evaluate is sys.modules['ve.evaluate'].evaluate,"
                " check is ve.check, evaluate is ve.evaluate)")
    assert out.split() == ["True"] * 4


def test_a_shared_name_can_be_replaced_and_restored(monkeypatch):
    from ve.check import check
    replacement = object()
    monkeypatch.setattr(ve, "check", replacement)
    assert ve.check is replacement
    monkeypatch.undo()
    assert ve.check is check


def test_submodules_and_unknown_names():
    out = fresh("import ve; print(ve.wire.__name__, ve.english_grammar.__name__)")
    assert out.split() == ["ve.wire", "ve.english_grammar"]
    with pytest.raises(AttributeError, match="no attribute 'not_a_name'"):
        ve.not_a_name  # noqa: B018
    assert ve.__version__ == "0.1.0"


def test_checker_build_does_not_depend_on_what_was_imported():
    # The build fingerprint covers every surface record; the English reader's is there even when only
    # ve.argument is imported, as it was when `import ve` loaded everything.
    build = "from ve.argument import _checker_build; print(_checker_build())"
    assert fresh(build) == fresh("import ve.english\n" + build)
