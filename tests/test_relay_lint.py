"""`tools/relay_lint.py`: a relayed module raises Lean's diagnostics, never its own."""
from __future__ import annotations

from pathlib import Path

import pytest

from tools import relay_lint

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def classes():
    return relay_lint.content_classes()


def test_every_relayed_module_exists_and_passes():
    assert relay_lint.RELAYED and all((ROOT / path).is_file() for path in relay_lint.RELAYED)
    assert relay_lint.main([]) == 0


def test_the_classes_come_from_python(classes):
    assert {"VEError", "UnknownSymbol", "SyntaxError", "AmbiguousDerivation", "AdmissionError",
            "ResourceLimit"} <= classes
    assert "CheckerUnavailable" not in classes and "AuthorityViolation" not in classes


@pytest.mark.parametrize("line, found", [
    ('raise UnknownSymbol("Unknown predicate p")', True),
    ('raise errors.TypeMismatch(f"bad {x}")', True),
    ('raise VEError("x: " + message)', True),
    ('raise ResourceLimit("{} cases".format(n))', True),
    ('raise AdmissionError(message="own words")', True),
    ('error = InvalidModel("InvalidModel(x): y", generator="x")', True),
    ('raise UnknownSymbol(message)', False),
    ('raise cls(row["error"])', False),
    ('raise InvalidModel(message, generator=generator)', False),
    ('raise CheckerUnavailable("CheckerUnavailable: the service is down")', False),
    ('raise AuthorityViolation("CheckerUnavailable: no adapter")', False),
    ('raise ValueError("not a diagnostic")', False),
])
def test_seeded_modules(tmp_path, classes, line, found):
    module = tmp_path / "relayed.py"
    module.write_text(f"def f(message, row, cls, generator, x, n):\n    {line}\n")
    assert bool(relay_lint.findings(module, classes)) is found
    assert relay_lint.main([str(module)]) == (1 if found else 0)


@pytest.mark.parametrize("line, found", [
    ('raise VEError("InvalidInput: the file is not UTF-8 text")  # relay-lint: file I/O', False),
    ('raise VEError(\n        f"InvalidInput: {x} is not UTF-8 text")  # relay-lint: file I/O', False),
    ('raise VEError("InvalidInput: own words")  # relay-lint: file', True),
    ('raise VEError("InvalidInput: own words")  # relay-lint: file I/O, really', True),
    ('raise VEError("InvalidInput: own words")\n    x = 1  # relay-lint: file I/O', True),
])
def test_only_a_marked_call_is_a_file_io_diagnostic(tmp_path, classes, line, found):
    module = tmp_path / "relayed.py"
    module.write_text(f"def f(x):\n    {line}\n")
    marked = []
    assert bool(relay_lint.findings(module, classes, marked)) is found
    assert len(marked) == (0 if found else 1)


def test_discourse_is_relayed_with_two_file_io_diagnostics(classes):
    assert "ve/discourse.py" in relay_lint.RELAYED
    marked = []
    assert relay_lint.findings(ROOT / "ve/discourse.py", classes, marked) == []
    assert len(marked) == 2


def test_a_missing_relayed_module_fails(tmp_path):
    assert relay_lint.main([str(tmp_path / "absent.py")]) == 1
