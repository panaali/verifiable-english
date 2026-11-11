"""`ve document` errors are structured answers (item document-cli-structured-errors, reviews/dri-decisions-20261110-df-5b.md
item 2): a `VEError` gives `{status, error}` on stdout, exit 2 (4 for `ResourceLimit`), and no traceback;
`CheckerUnavailable` keeps its own answer and exit 5. Each case compares `error` with the exception the document
command raises by itself, so the code, the message and every quoted name are the command's own. A limit is known by its
class, never its code: a limit Lean reports through the relay is a `ResourceLimit` whose code is Lean's wire code
(`SOFT_RESOURCE_LIMIT`), and it too is exit 4 (review F1), on every command line that answers a `VEError`."""
import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

import ve.document.cli as document_cli
from ve.__main__ import EXIT_CHECKER_UNAVAILABLE, main
from ve.errors import CheckerUnavailable, ResourceLimit, UnsupportedProfile, VEError
from tests.document_chain_corpus import CHAIN, chain_front, text
from tests.subprocesses import HANG_TIMEOUT
from tests.test_document import unit, write_doc

ROOT = Path(__file__).resolve().parents[1]
WEIGHING = ROOT / "docs/defeasible/df-5b/fixtures/weighing.ve.md"


def plain(tmp_path):
    source = b"This holds.\n"
    return write_doc(tmp_path, source, [unit("a", 0, len(source), content={"ast": ["top"]})])


def nested(tmp_path):
    """A front matter nested past the JSON parser's depth: the document reader's `ResourceLimit`."""
    path = tmp_path / "deep.ve.md"
    path.write_bytes(b"---\n" + b"[" * 200_000 + b"]" * 200_000 + b"\n---\nText.\n")
    return path


def relayed_limit(tmp_path):
    """A soft-norms@0 document of 300 rules (no norm-defaults@0): Lean's soft-norms check refuses it at its rule
    limit, and the relay raises a `ResourceLimit` whose code is Lean's wire code `SOFT_RESOURCE_LIMIT` (review F1's
    probe)."""
    deny = "u0125.s04.p2"
    base = CHAIN["units"][deny]
    front = chain_front(deny, profiles=[p for p in CHAIN["profiles"] if p != "norm-defaults@0"])
    permitted = base["predicates"]["deny_being_claude_permitted"]
    front["environment"]["vocabulary"]["predicates"] = {
        f"deny{i}_permitted": {**permitted, "regulated": {**permitted["regulated"], "default": "allow",
                                                          "act": "{0} deny " + chr(97 + i)}} for i in range(7)}
    front["units"] = [{"id": f"u{i}", "span": [10 * i, 10 * i + 10], "kind": "norm", "meaning": "specified",
                       "support": "assumption",
                       "content": {"norm": {**base["rule"], "name": f"rule-{i}", "predicate": f"deny{i % 7}_permitted"}}}
                      for i in range(300)]
    path = tmp_path / "rules.ve.md"
    path.write_bytes(text(front, b"".join(f"Rule {i:03d}.\n".encode() for i in range(300))))
    return path


# (case, command, the document builder, extra arguments, the exception class, status, exit code)
CASES = [
    ("under", "readings", plain, ["--under", "s:0"], VEError, "InvalidInput", 2),
    ("weighing-check", "check", lambda _: WEIGHING, [], UnsupportedProfile, "InvalidInput", 2),
    ("weighing-readings", "readings", lambda _: WEIGHING, [], UnsupportedProfile, "InvalidInput", 2),
    ("limit-check", "check", nested, [], ResourceLimit, "ResourceLimit", 4),
    ("limit-readings", "readings", nested, [], ResourceLimit, "ResourceLimit", 4),
    ("relayed-limit-check", "check", relayed_limit, [], ResourceLimit, "ResourceLimit", 4),
    ("relayed-limit-readings", "readings", relayed_limit, [], ResourceLimit, "ResourceLimit", 4),
    ("relayed-limit-coverage", "coverage", relayed_limit, [], ResourceLimit, "ResourceLimit", 4),
]


@pytest.mark.parametrize("case, command, build, extra, raised, status, code", CASES, ids=[c[0] for c in CASES])
def test_document_errors_are_structured(tmp_path, capsys, case, command, build, extra, raised, status, code):
    argv = [command, str(build(tmp_path)), *extra]
    with pytest.raises(raised) as own:
        document_cli.main(argv)
    assert type(own.value) is raised
    if case.startswith("relayed"):  # Lean's wire code, not the class's: a code comparison misses this limit
        assert own.value.code == "SOFT_RESOURCE_LIMIT" != ResourceLimit.code
    capsys.readouterr()
    assert main(["document", *argv]) == code
    out, err = capsys.readouterr()
    record = json.loads(out)
    assert record == {"status": status, "error": own.value.to_dict()}
    assert (record["error"]["code"], record["error"]["message"]) == (own.value.code, own.value.message)
    assert "Traceback" not in out + err


def test_under_without_conclusion_prints_no_traceback(tmp_path):
    """The reported case, as a caller runs it: a process, exit 2, the structured answer, nothing on stderr."""
    done = subprocess.run([sys.executable, "-m", "ve", "document", "readings", str(plain(tmp_path)),
                           "--under", "s:0"], capture_output=True, text=True, timeout=HANG_TIMEOUT, cwd=ROOT)
    assert done.returncode == 2
    assert json.loads(done.stdout) == {"status": "InvalidInput",
                                       "error": {"code": "InvalidInput", "message": "--under requires --conclusion"}}
    assert "Traceback" not in done.stderr


@pytest.mark.parametrize("command", ["check", "readings"])
def test_checker_unavailable_is_unchanged(tmp_path, capsys, monkeypatch, command):
    """`CheckerUnavailable` is no input diagnostic: `main`'s own answer, exit 5, as before this item."""
    failure = CheckerUnavailable("the Lean service is not running")

    def unavailable(*_):
        raise failure
    monkeypatch.setattr(document_cli, "check_document" if command == "check" else "load_document", unavailable)
    assert main(["document", command, str(plain(tmp_path))]) == EXIT_CHECKER_UNAVAILABLE == 5
    out, err = capsys.readouterr()
    assert json.loads(out) == {"status": "CheckerUnavailable", "error": failure.to_dict()}
    assert "Traceback" not in out + err


def wire_codes():
    """Every code a relayed rejection can carry, with its class: each class of the relay's table under its own name,
    and each wire code of Lean's generated contracts (`ve/wire_contract/*.json`, from `VE.WireContract.Tables`)."""
    from ve.backends.relay import CLASSES
    found = {(name, name) for name, cls in CLASSES.items() if issubclass(cls, VEError)}
    for contract in sorted((ROOT / "ve/wire_contract").glob("*@*.json")):
        found |= {(code, row["class"]) for code, row in json.loads(contract.read_text())["codes"].items()}
    return sorted(found)


def relayed(code, cls, message="ResourceLimit: rules"):
    """The exception the relay raises for a Lean rejection of class `cls` coded `code` (`relay._raised`, as run)."""
    from ve.backends.relay import _raised
    return _raised({"code": cls, "result": {"status": "error", "error": message, "code": code}})


WIRE = wire_codes()


def test_the_wire_codes_include_coded_limits():
    """The enumeration is not vacuous: it reaches limits whose code is not the class's, and non-limit codes."""
    assert {"SOFT_RESOURCE_LIMIT", "ACTS_RESOURCE_LIMIT"} <= {code for code, cls in WIRE if cls == "ResourceLimit"}
    assert {cls for _, cls in WIRE} > {"ResourceLimit", "InvalidInput"}


@pytest.mark.parametrize("code, cls", WIRE, ids=[f"{code}-{cls}" for code, cls in WIRE])
def test_every_relayed_code_gets_the_answer_of_its_class(code, cls):
    """`diagnostic_answer`, the one owner of the mapping: exit 4 and `ResourceLimit` exactly for Lean's limit class,
    whatever wire code it carries; else `InvalidInput`, exit 2; `error` is the exception's own `to_dict()`."""
    from ve.backends.relay import CLASSES
    from ve.errors import diagnostic_answer
    error = relayed(code, cls)
    assert error.code == code and type(error) is CLASSES[cls]
    limit = cls == "ResourceLimit"
    assert diagnostic_answer(error) == ({"status": "ResourceLimit" if limit else "InvalidInput",
                                         "error": error.to_dict()}, 4 if limit else 2)


def _env_and_source(tmp_path):
    env, source, pack = tmp_path / "env.json", tmp_path / "source.txt", tmp_path / "pack.json"
    env.write_text("{}")
    source.write_text("This holds.\n")
    pack.write_text("{}")
    return str(env), str(source), str(pack)


def _refusing_environment(monkeypatch, error):
    import ve.__main__ as cli

    class Refusing:
        def __init__(self, *_):
            raise error

        @staticmethod
        def from_json(*_):
            raise error
    monkeypatch.setattr(cli, "Environment", Refusing)


def _document(command):
    def drive(tmp_path, monkeypatch, error):
        def refuse(*_, **__):
            raise error
        monkeypatch.setattr(document_cli, "check_document" if command == "check" else "load_document", refuse)
        return ["document", command, str(plain(tmp_path))]
    return drive


def _senses(tmp_path, monkeypatch, error):
    env, source, pack = _env_and_source(tmp_path)
    _refusing_environment(monkeypatch, error)
    return ["senses", "resolve", "--env", env, "--pack", pack, "--word", "w", "--gloss", "g", source]


def _final(tmp_path, monkeypatch, error):
    env, source, _ = _env_and_source(tmp_path)
    _refusing_environment(monkeypatch, error)
    return ["check", "--env", env, source]


def _acts(tmp_path, monkeypatch, error):
    import ve.acts

    def refuse(*_, **__):
        raise error
    monkeypatch.setattr(ve.acts, "readings", refuse)
    return ["acts", "readings", "{0} to seek asylum"]


# Each command line that answers a `VEError` with `{status, error}`: `ve document`, `ve senses resolve` and
# `propose-readings`, the final handler of `check`/`render`/`format`/..., and `ve acts readings`.
ENTRIES = {"document-check": _document("check"), "document-readings": _document("readings"), "senses": _senses,
           "final": _final, "acts": _acts}
CODED = [("SOFT_RESOURCE_LIMIT", "ResourceLimit"), ("ACTS_RESOURCE_LIMIT", "ResourceLimit"),
         ("SOFT_INVALID_INPUT", "InvalidInput"), ("ResourceLimit", "ResourceLimit")]


@pytest.mark.parametrize("code, cls", CODED, ids=[c for c, _ in CODED])
@pytest.mark.parametrize("entry", ENTRIES)
def test_every_command_line_answers_a_relayed_limit_by_its_class(tmp_path, capsys, monkeypatch, entry, code, cls):
    """Review F1 as a class: a relayed limit is exit 4 with status `ResourceLimit` on every command line that answers a
    `VEError`, though its code is Lean's wire code; a relayed non-limit stays exit 2."""
    assert (code, cls) in WIRE
    error = relayed(code, cls)
    argv = ENTRIES[entry](tmp_path, monkeypatch, error)
    limit = cls == "ResourceLimit"
    assert main(argv) == (4 if limit else 2)
    out, err = capsys.readouterr()
    assert json.loads(out) == {"status": "ResourceLimit" if limit else "InvalidInput", "error": error.to_dict()}
    assert "Traceback" not in out + err


def _class_code(node, classes, codes):
    """Whether `node` is a diagnostic class's code: its string (`"ResourceLimit"`) or `Class.code`, alone or listed."""
    if isinstance(node, ast.Constant):
        return node.value in codes
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return any(_class_code(e, classes, codes) for e in node.elts)
    return isinstance(node, ast.Attribute) and node.attr == "code" and isinstance(node.value, ast.Name) \
        and node.value.id in classes


def class_by_code(source):
    """The comparisons in `source` of an exception's `.code` with a diagnostic class's code: each asks the class of an
    exception by its code, which a relayed Lean rejection replaces with its wire code (review F1's class)."""
    import ve.errors
    classes = {name for name, value in vars(ve.errors).items() if isinstance(value, type)
               and issubclass(value, (VEError, CheckerUnavailable))}
    codes = {getattr(ve.errors, name).code for name in classes}
    found = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Compare):
            operands = [node.left, *node.comparators]
            if any(isinstance(o, ast.Attribute) and o.attr == "code" and not _class_code(o, classes, codes)
                   for o in operands) and any(_class_code(o, classes, codes) for o in operands):
                found.append(node.lineno)
    return found


def test_no_product_code_asks_an_exceptions_class_by_its_code():
    """The lint behind F1's class: `isinstance` (or `diagnostic_answer`), never `exc.code == "ResourceLimit"`."""
    found = {str(path.relative_to(ROOT)): lines for path in sorted((ROOT / "ve").rglob("*.py"))
             if (lines := class_by_code(path.read_text(encoding="utf-8")))}
    assert found == {}


@pytest.mark.parametrize("line", ['exc.code == "ResourceLimit"', "exc.code == ResourceLimit.code",
                                  'error.code in ("ResourceLimit", "InvalidModel")', '"InvalidInput" != exc.code',
                                  "self.error.code == CheckerUnavailable.code"])
def test_the_lint_sees_each_spelling(line):
    """The lint can fail: each spelling of the comparison it forbids is found."""
    assert class_by_code(f"if {line}:\n    pass\n") == [1]
    assert class_by_code("if isinstance(exc, ResourceLimit):\n    pass\n") == []
