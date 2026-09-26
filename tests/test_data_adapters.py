from copy import deepcopy
import json

import pytest

from ve.__main__ import main
from ve.adapters import lookup, run, verify
from ve.errors import VEError


def test_recompute_and_reject_tampering():
    record = run("prefix@1", {"pattern": "report"}, ["report.pdf", "letter.pdf"])
    assert verify(record) == record
    assert lookup(record, "report.pdf") is True
    assert lookup(record, "letter.pdf") is False
    assert lookup(None, "report.pdf") is None
    with pytest.raises(VEError, match="outside"):
        lookup(record, "unlisted.pdf")
    for field, replacement in (("input_hashes", ["tampered"]),
                               ("table_hash", "tampered"), ("domain", ["letter.pdf"])):
        changed = deepcopy(record)
        changed[field] = replacement
        with pytest.raises(VEError, match="does not match"):
            verify(changed)


def test_glob_regex_and_error_rows():
    assert lookup(run("glob@1", {"pattern": "*.pdf"}, ["a.pdf"]), "a.pdf") is True
    assert lookup(run("regex@1", {"pattern": r"a[0-9]+"}, ["a42"]), "a42") is True
    error = run("regex@1", {"pattern": "["}, ["name"])
    assert error["rows"][0]["status"] == "error"
    with pytest.raises(VEError, match="invalid regex"):
        lookup(error, "name")


def test_adapter_cli(tmp_path, capsys):
    request = tmp_path / "request.json"
    request.write_text(json.dumps({"function": "prefix@1", "parameters": {"pattern": "a"},
                                   "domain": ["abc"]}))
    assert main(["adapter", "run", str(request)]) == 0
    record = json.loads(capsys.readouterr().out)
    request.write_text(json.dumps(record))
    assert main(["adapter", "run", "--verify", str(request)]) == 0
