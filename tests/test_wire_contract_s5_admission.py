"""Admission boundary checks for the two S5 units in shadow (wire-contract-s5.md 2.6, 7.2, 8.3).

The committed contracts remain in shadow until S5-pre and the signed delta close. While a unit is in shadow its
contract module has no `public_rejection` and its route has no handler (7.2: both are the switch commit's), so
no output of the call depends on the contract (2.6): the call raises the legacy error as it is, and imports no
diagnostic module.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from subprocesses import HANG_TIMEOUT
from tests.test_norm_defaults_contract import FIXTURES as DEFAULT_FIXTURES
from tests.test_norms_contract import FIXTURES as NORM_FIXTURES
from tests.test_wire_contract_s5_lean import document, s1, s16
from ve import norm_defaults_contract, norms_contract
from ve.errors import VEError
from ve.norm_admission import _admit_norm_document_python
from ve.norm_defaults_route import admit_norm_defaults_document
from ve.wire_contract.engine import load

ROOT = Path(__file__).resolve().parents[1]
UNITS = {"norms@0": (norms_contract, _admit_norm_document_python, s1),
         "norm-defaults@0": (norm_defaults_contract, admit_norm_defaults_document, s16)}
DIAGNOSTIC_MODULES = ("ve.norms_contract", "ve.norm_defaults_contract", "ve.softnorms_contract", "ve.wire_contract")


@pytest.mark.parametrize("unit", sorted(UNITS))
def test_shadow_contract_module_has_no_public_boundary(unit):
    """Fable review B: `public_rejection` and the call site's handler belong to the switch commit (7.2)."""
    module = UNITS[unit][0]
    assert load(unit)["status"] == "shadow"
    assert not hasattr(module, "public_rejection")
    assert "public_rejection" not in Path(module.__file__).read_text()


@pytest.mark.parametrize("unit,fixture", [("norms@0", None), ("norms@0", "N3"), ("norms@0", "N7"),
                                          ("norm-defaults@0", None), ("norm-defaults@0", "D10")])
def test_shadow_admission_retains_legacy_error(unit, fixture):
    """S1 and S16, and the fixtures N3, N7 and D10, through the call: the error is the legacy validator's, with
    its type, code and text, and no record."""
    module, call, source = UNITS[unit]
    fixtures = NORM_FIXTURES if unit == "norms@0" else DEFAULT_FIXTURES
    environment, norms = source() if fixture is None else fixtures[fixture][0]()
    with pytest.raises(VEError) as legacy:
        module.legacy_validation(json.loads(json.dumps(environment)), json.loads(json.dumps(norms)))
    with pytest.raises(VEError) as caught:
        call(environment, document(norms))
    assert caught.value.diagnostic is None
    if unit == "norm-defaults@0":
        from ve.norm_defaults_route import run_cases
        (lean,) = run_cases([{"id": "admission", "kind": "admission", "environment": environment,
                             "document": document(norms)}])
        assert str(caught.value) == lean["error"]
    else:
        assert (type(caught.value), caught.value.code, str(caught.value)) == \
            (type(legacy.value), legacy.value.code, str(legacy.value))


PROBE = """
import json, sys
from ve.admission import admit_document
from ve.errors import VEError
outcomes = []
for environment, document in json.loads(sys.stdin.read()):
    try:
        admit_document(environment, document)
        outcomes.append("accepted")
    except VEError:
        outcomes.append("rejected")
print(json.dumps([outcomes, sorted(name for name in sys.modules if name.startswith(%r))]))
"""


def test_shadow_calls_import_no_diagnostic_module():
    """V2 (S7), and in shadow more: neither an accepted nor a rejected call imports a contract module or the
    engine. The accepted call is S7's, on `tests/test_norm_admission.py::source()`."""
    from tests.test_norm_admission import source
    env, accepted = source()
    cases = [[env.to_dict(), accepted]] + [[environment, document(norms)] for environment, norms in (s1(), s16())]
    expected = ["accepted", "rejected", "rejected"]
    probe = PROBE % ("ve.",)
    result = subprocess.run([sys.executable, "-c", probe], input=json.dumps(cases), cwd=ROOT, text=True,
                            capture_output=True, timeout=HANG_TIMEOUT, env={**os.environ, "PYTHONPATH": str(ROOT)})
    assert result.returncode == 0, result.stderr
    outcomes, modules = json.loads(result.stdout)
    assert outcomes == expected
    assert not [name for name in modules if any(name == m or name.startswith(m + ".") for m in DIAGNOSTIC_MODULES)]
