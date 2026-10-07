"""Present replay budgets must never silently become the default."""
import json
from pathlib import Path

import pytest

from test_lean_service import service_executable  # noqa: F401
from ve import Environment
from ve.ast import Top
from ve.backends.relay import rows
from ve.entailment import prove_entailment
from ve.errors import VEError

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("invalid", [False, "0", [], {}])
def test_lean_certificate_rejects_present_malformed_budget(service_executable, invalid):
    environment = Environment.from_dict(json.loads((ROOT / "conformance/evaluation.json").read_text())[0]
                                        ["environment"])
    found = prove_entailment(environment, [Top()], Top())
    from ve.ast import formula_to_data
    case = {"id": "cert", "environment": environment.to_dict(),
            "premises": [formula_to_data(environment, Top())],
            "conclusion": formula_to_data(environment, Top()),
            "certificate": found.certificate, "max_steps": invalid}
    row = rows("check-certificate", [case], executable=service_executable)[0]
    assert row["status"] == "error"
    assert row["error"] == "InvalidInput: max_steps must be a nonnegative integer"


@pytest.mark.parametrize("invalid", [None, -1, 0.5])
def test_restricted_json_rejects_non_wire_budget_values(service_executable, invalid):
    environment = Environment.from_dict(json.loads((ROOT / "conformance/evaluation.json").read_text())[0]
                                        ["environment"])
    found = prove_entailment(environment, [Top()], Top())
    from ve.ast import formula_to_data
    case = {"id": "cert", "environment": environment.to_dict(),
            "premises": [formula_to_data(environment, Top())],
            "conclusion": formula_to_data(environment, Top()),
            "certificate": found.certificate, "max_steps": invalid}
    with pytest.raises(VEError) as raised:
        rows("check-certificate", [case], executable=service_executable)
    assert raised.value.code == "InvalidInput"


