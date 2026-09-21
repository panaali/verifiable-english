import json

from lark import Lark
import pytest

from test_cli import ENV, cli


@pytest.mark.parametrize("dialect", ["lark", "gbnf", "ebnf"])
def test_export_cli(dialect):
    result = cli("grammar", "--env", ENV, "--dialect", dialect, "--max-binder-depth", 1)
    assert result.returncode == 0, result.stdout + result.stderr
    if dialect == "lark":
        Lark(result.stdout).parse("true.\n")
    else:
        assert result.stdout.startswith("root ::= ")


def test_export_wrapper_and_spec_cli():
    result = cli("grammar", "--env", ENV, "--wrapper", "--max-binder-depth", 0)
    assert result.returncode == 0
    payload = json.dumps({"ve": "true.\n", "explanation": "Free text."})
    Lark(result.stdout).parse(payload)
    result = cli("grammar", "--env", ENV, "--spec", "--mode", "syntax")
    assert result.returncode == 0
    spec = json.loads(result.stdout)
    assert spec["json_schema"]["required"] == ["ve", "explanation"]
    Lark(spec["grammar"]).parse(payload)


def test_export_cli_invalid_bounds_and_budget():
    for flag, value, code in [("--max-binder-depth", -1, "InvalidInput"),
                              ("--max-rules", 1, "ResourceLimit")]:
        result = cli("grammar", "--env", ENV, flag, value)
        assert result.returncode == 2
        assert json.loads(result.stdout)["error"]["code"] == code
