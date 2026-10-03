"""Admission boundary checks for the two S5 units (wire-contract-s5.md 8.3).

The committed contracts remain in shadow until S5-pre and the signed delta close.
Tests inject a public copy to exercise the already wired rejection path.
"""
from copy import deepcopy

import pytest

from tests.test_wire_contract_s5_lean import document, s1, s16
from tests.test_norms_contract import FIXTURES as NORM_FIXTURES
from tests.test_norm_defaults_contract import FIXTURES as DEFAULT_FIXTURES
from ve.errors import VEError
from ve.norm_admission import _admit_norm_document_python
from ve.norm_defaults_route import admit_norm_defaults_document
from ve.wire_contract.engine import load


@pytest.mark.parametrize("unit,source,call,contract_module", [
    ("norms@0", s1, _admit_norm_document_python, "ve.norms_contract"),
    ("norm-defaults@0", s16, admit_norm_defaults_document, "ve.norm_defaults_contract"),
])
def test_admission_rejection_uses_the_first_contract_fault(monkeypatch, unit, source, call, contract_module):
    module = __import__(contract_module, fromlist=["_locked_contract"])
    contract = deepcopy(load(unit))
    contract["status"] = "public"
    monkeypatch.setattr(module, "_locked_contract", lambda: contract)
    environment, norms = source()
    before = deepcopy((environment, norms))
    with pytest.raises(VEError) as caught:
        call(environment, document(norms))
    error = caught.value
    assert (environment, norms) == before
    assert error.diagnostic == {
        "contract": unit, "revision": contract["revision"], "check": "4.2" if unit == "norms@0" else "w1/4.2",
        "phase": "rules" if unit == "norms@0" else "norms", "code": "NORMS_DUPLICATE_DECLARATION",
        "class": "DuplicateDeclaration", "path": "/norms/2/norm/name",
        "text": "DuplicateDeclaration: rule a0", "args": {"value": "a0"},
    }
    assert error.message == str(error) == error.diagnostic["text"]


@pytest.mark.parametrize("unit,source,call", [
    ("norms@0", s1, _admit_norm_document_python),
    ("norm-defaults@0", s16, admit_norm_defaults_document),
])
def test_shadow_admission_retains_legacy_error(unit, source, call):
    assert load(unit)["status"] == "shadow"
    environment, norms = source()
    with pytest.raises(VEError) as caught:
        call(environment, document(norms))
    assert caught.value.diagnostic is None
    assert str(caught.value) == "rule a0"


@pytest.mark.parametrize("unit,source,call,contract_module", [
    ("norms@0", s1, _admit_norm_document_python, "ve.norms_contract"),
    ("norm-defaults@0", s16, admit_norm_defaults_document, "ve.norm_defaults_contract"),
])
def test_admission_checks_units_before_the_diagnostic_handler(monkeypatch, unit, source, call, contract_module):
    module = __import__(contract_module, fromlist=["_locked_contract"])
    contract = deepcopy(load(unit))
    contract["status"] = "public"
    monkeypatch.setattr(module, "_locked_contract", lambda: contract)
    environment, norms = source()
    submitted = document(norms)
    submitted["units"][2].pop("span")
    with pytest.raises(VEError) as caught:
        call(environment, submitted)
    assert caught.value.diagnostic is None


@pytest.mark.parametrize("fixture,unit,source,call,contract_module,check,phase", [
    ("N3", "norms@0", NORM_FIXTURES, _admit_norm_document_python, "ve.norms_contract", "2.2", "profiles"),
    ("N7", "norms@0", NORM_FIXTURES, _admit_norm_document_python, "ve.norms_contract", "3.4", "rule-shape"),
    ("D10", "norm-defaults@0", DEFAULT_FIXTURES, admit_norm_defaults_document,
     "ve.norm_defaults_contract", "6.2", "fill"),
])
def test_spec_fixture_reaches_admission_record(monkeypatch, fixture, unit, source, call, contract_module,
                                               check, phase):
    module = __import__(contract_module, fromlist=["_locked_contract"])
    contract = deepcopy(load(unit))
    contract["status"] = "public"
    monkeypatch.setattr(module, "_locked_contract", lambda: contract)
    environment, norms = source[fixture][0]()
    with pytest.raises(VEError) as caught:
        call(environment, document(norms))
    assert caught.value.diagnostic["check"] == check
    assert caught.value.diagnostic["phase"] == phase
    assert caught.value.message == str(caught.value) == caught.value.diagnostic["text"]
