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


def test_speech_english_keeps_its_surface_owner():
    assert "ve.speech_english" in relay_lint.OWNED_SURFACES
    assert ROOT / "ve/speech_english.py" not in relay_lint.helpers(
        [ROOT / path for path in relay_lint.RELAYED])


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


def test_a_check_moved_into_its_own_module_is_still_linted(tmp_path, monkeypatch, classes):
    """lf-8 recheck B2: the reports relay's record checks moved into `ve/reports_preflight.py`,
    which no relayed-module list named. A module only relayed modules import is linted with them;
    one that other modules import too is not theirs alone."""
    package = tmp_path / "ve"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "errors.py").write_text("class VEError(ValueError):\n    pass\n")
    (package / "relayed.py").write_text("from .preflight import prepare\nfrom . import shared\n")
    (package / "preflight.py").write_text("from .errors import VEError\n\n\ndef prepare(rows):\n"
                                         "    raise VEError('InvalidInput: contexts must be a list')\n")
    (package / "shared.py").write_text("from .errors import VEError\n\n\ndef f():\n    raise VEError('own words')\n")
    (package / "other.py").write_text("import ve.shared\n")
    monkeypatch.setattr(relay_lint, "ROOT", tmp_path)
    monkeypatch.setattr(relay_lint, "RELAYED", ("ve/relayed.py",))
    assert relay_lint.helpers([package / "relayed.py"]) == [package / "preflight.py"]
    assert relay_lint.main([]) == 1
    (package / "other.py").write_text("from .preflight import prepare\nimport ve.shared\n")
    assert relay_lint.helpers([package / "relayed.py"]) == []


def test_the_english_admission_path_is_relayed_by_function(tmp_path, classes):
    """English E2 (spec 2.9): the admission functions of `ve/english.py` are relayed; the module's producer,
    renderer, statement reader and comparator are not. A text of the path's own is a finding, one outside the
    named functions is not, and a named function that is missing fails."""
    assert relay_lint.RELAYED_FUNCTIONS["ve/english.py"] and "ve/backends/english_lean.py" in relay_lint.RELAYED
    module = tmp_path / "english.py"
    module.write_text("def parse_english(env, source):\n    raise SyntaxError('own words')\n\n"
                      "def render_english(value, env):\n    raise SyntaxError('renderer words')\n")
    found = relay_lint.findings(module, classes, functions=("parse_english",))
    assert len(found) == 1 and ":2:" in found[0]
    assert relay_lint.findings(module, classes, functions=("render_english",))
    assert "not found" in relay_lint.findings(module, classes, functions=("parse_english_argument",))[0]


# The second rule (readings-defaults plan RD-2b, D12): no readings module builds a name of the unspecified completion.

@pytest.mark.parametrize("line, found", [
    ('name = "unsaid__" + predicate', True),
    ('name = f"unsaid--{rule}"', True),
    ('names = ("x", "a unsaid__p b")', True),
    ('"""Docstrings count: unsaid__p."""', True),
    ('hidden = ("unsaid__", "unsaid--")  # relay-lint: non-wording', False),
    ('hidden = ("unsaid__",)  # relay-lint: non-wording, really', True),
    ('label = "unsaid:pair:" + body', False),
    ('name = "unsaid_" + "_p"', False),
])
def test_seeded_readings_modules(tmp_path, line, found):
    module = tmp_path / "readings_x.py"
    module.write_text(f"def f(predicate, rule, body):\n    {line}\n")
    guards = []
    assert bool(relay_lint.reserved_literals(module, guards)) is found
    assert bool(guards) is (not found and "non-wording" in line)
    assert relay_lint.main([str(module)]) == (1 if found else 0)


def test_every_readings_module_is_read_by_the_reserved_rule():
    """The rule reads the glob, not a hand-kept list: every `ve/readings*.py` file, and nothing fewer."""
    modules = sorted(ROOT.glob(relay_lint.READINGS_GLOB))
    assert {p.name for p in modules} >= {"readings.py", "readings_route.py", "readings_s1.py",
                                          "readings_s2_english.py", "readings_s2_wording.py",
                                          "readings_verdicts.py", "readings_sup.py", "readings_english.py"}
    for path in modules:
        assert relay_lint.reserved_literals(path) == [], path

# The third rule (readings-defaults plan RD-8): the senses path never names Python's English reader.

@pytest.mark.parametrize("line, found", [
    ("from .english import parse_english", True),
    ("from .english import parse_english as read", True),
    ("from . import english\nx = english.parse_english", True),
    ("x = parse_english(env, text)", True),
    ("from .english import parse_english_argument", False),
    ('x = "parse_english"', False),
    ("x = read_fences(env, texts, packs)", False),
])
def test_seeded_senses_modules(tmp_path, line, found):
    module = tmp_path / "senses_x.py"
    module.write_text(f"{line}\n")
    assert bool(relay_lint.english_reads(module)) is found
    assert relay_lint.main([str(module)]) == (1 if found else 0)


@pytest.mark.parametrize("body, found", [
    ("if senses is not None:\n    return parse_english(env, text)\nreturn parse_english(env, text)\n", True),
    ("if senses is not None and surface:\n    from .english import parse_english\n", True),
    ("if senses is not None:\n    return senses.formulas[uid]\nreturn parse_english(env, text)\n", False),
    ("if other:\n    return parse_english(env, text)\n", False),
])
def test_seeded_senses_branches(tmp_path, body, found):
    module = tmp_path / "document_x.py"
    module.write_text("def f(env, text, senses, surface, uid, other):\n" + "".join(
        "    " + row + "\n" for row in body.splitlines()))
    assert bool(relay_lint.english_reads(module, branches_only=True)) is found


def test_the_senses_path_is_read_by_the_third_rule():
    """Every module of the senses path exists and passes; the document loader has a senses branch to read."""
    for name in relay_lint.PARSE_FREE:
        assert (ROOT / name).is_file(), name
        assert relay_lint.english_reads(ROOT / name) == [], name
    loader = (ROOT / relay_lint.SENSES_LOADER).read_text()
    assert "if senses is not None" in loader and "parse_english" in loader
    assert relay_lint.english_reads(ROOT / relay_lint.SENSES_LOADER, branches_only=True) == []
