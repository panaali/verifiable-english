"""`ve document` errors are structured answers (item document-cli-structured-errors, reviews/dri-decisions-20261110-df-5b.md
item 2): a `VEError` gives `{status, error}` on stdout, exit 2 (4 for `ResourceLimit`), and no traceback;
`CheckerUnavailable` keeps its own answer and exit 5. Each case compares `error` with the exception the document
command raises by itself, so the code, the message and every quoted name are the command's own."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

import ve.document.cli as document_cli
from ve.__main__ import EXIT_CHECKER_UNAVAILABLE, main
from ve.errors import CheckerUnavailable, ResourceLimit, UnsupportedProfile, VEError
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


# (case, command, the document builder, extra arguments, the exception class, status, exit code)
CASES = [
    ("under", "readings", plain, ["--under", "s:0"], VEError, "InvalidInput", 2),
    ("weighing-check", "check", lambda _: WEIGHING, [], UnsupportedProfile, "InvalidInput", 2),
    ("weighing-readings", "readings", lambda _: WEIGHING, [], UnsupportedProfile, "InvalidInput", 2),
    ("limit-check", "check", nested, [], ResourceLimit, "ResourceLimit", 4),
    ("limit-readings", "readings", nested, [], ResourceLimit, "ResourceLimit", 4),
]


@pytest.mark.parametrize("case, command, build, extra, raised, status, code", CASES, ids=[c[0] for c in CASES])
def test_document_errors_are_structured(tmp_path, capsys, case, command, build, extra, raised, status, code):
    argv = [command, str(build(tmp_path)), *extra]
    with pytest.raises(raised) as own:
        document_cli.main(argv)
    assert type(own.value) is raised
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
