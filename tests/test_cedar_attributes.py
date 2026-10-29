import json
import subprocess
import sys
from pathlib import Path

from ve.adapters.attributes import Value, attribute, compare, has
import pytest
from subprocesses import HANG_TIMEOUT
from ve.errors import VEError


def test_defined_value_keeps_missing_distinct_from_false():
    context = {"principal": {"active": False, "department": "finance"}}
    assert attribute(context, ("principal", "active")).defined
    assert attribute(context, ("principal", "active")).value is False
    assert has(context, ("principal", "active")) == Value(True, True)
    assert has(context, ("principal", "missing")) == Value(True, False)
    assert has(context, ("absent", "active")) == Value(False)
    assert has({"principal": False}, ("principal", "active")) == Value(False)
    assert has(context, ("principal",)) == Value(True, True)
    with pytest.raises(VEError, match="definedness"):
        bool(has(context, ("absent", "active")))
    assert compare(context, ("principal", "department"), "finance").value is True
    assert compare(context, ("principal", "missing"), "finance").defined is False
    assert compare(context, ("principal", "missing"), "finance", "!=").defined is False


def test_cedar_comparisons_preserve_value_types():
    assert compare({"v": False}, ("v",), 0) == Value(True, False)
    assert compare({"v": 1}, ("v",), True) == Value(True, False)
    assert compare({"v": [False]}, ("v",), [0]) == Value(True, False)
    assert compare({"v": {"a": False}}, ("v",), {"a": 0}) == Value(True, False)
    assert compare({"v": [1, 2]}, ("v",), [2, 1, 1]) == Value(True, True)


def test_usecase_claim_holds_on_its_model():
    # The named test of the agent-policy requirement register (apol-req) for
    # usecases/cedar-attributes: claim.ve checks and is true on model.json.
    case = Path(__file__).resolve().parents[1] / "usecases" / "cedar-attributes"
    run = subprocess.run([sys.executable, "-m", "ve", "evaluate", "--env", str(case / "environment.json"),
                          "--model", str(case / "model.json"), str(case / "claim.ve")],
                         capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert run.returncode == 0, run.stderr
    evaluation = json.loads(run.stdout)["evaluation"]
    assert (evaluation["status"], evaluation["value"]) == ("Satisfied", True)
