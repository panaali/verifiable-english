"""The `acts@0` wire table in shadow (ap-1bf): the legacy validator still owns the verdict; the engines name the
member of 1.1 at and around each limit of `VE.Acts.Lexical`, the limits read from Lean and never copied."""

from copy import deepcopy
import json
from pathlib import Path
import re

import pytest

from conformance.acts_contract import REGISTRY, acts_source
from conformance.wire_contract_engine import CLEAN, Fault, load, run
from conformance.wire_contract_faults import catalogue, catalogue_index
from conformance.wire_contract_faults_acts import EXAMPLES, at_count, at_limits, base, limits
from tests import lean_routes
from ve.errors import UnsupportedProfile, VEError
from ve.norms_contract import OUTSIDE, legacy_validation

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = load("acts@0")
UNIT_FILES = ("ve/wire_contract/acts@0.json", "conformance/acts_contract.py", "conformance/wire_contract_faults_acts.py",
              "lean/VE/WireContract/Hooks/Acts.lean", "tests/test_acts_contract.py")
# Lean is the oracle of the limits (`limits`) and the legacy validator's decoder.
pytestmark = pytest.mark.skipif(not lean_routes.SERVICE.exists(), reason="ve_service is not built")


def legacy(raw, norms):
    try:
        legacy_validation(deepcopy(raw), deepcopy(norms))
    except VEError as exc:
        return exc
    return None


def accepted():
    examples = [json.loads(p.read_text()) for p in sorted(EXAMPLES.glob("*.json"))]
    return [(e["environment"], e["norms"]) for e in examples] + [at_count()]


def case(raw, norms, kind="norms-elaborate"):
    return {"id": "c", "kind": kind, "environment": raw, "norms": norms}


def test_the_limits_are_leans_and_never_copied():
    numerals = re.compile(r"(?<![0-9])(" + "|".join(str(v) for v in limits().values()) + r")(?![0-9])")
    for relative in UNIT_FILES:
        assert not numerals.search((ROOT / relative).read_text()), relative


def test_the_limit_example_is_the_source_at_the_limits_and_the_catalogue_is_current():
    assert json.loads((EXAMPLES / "limit.json").read_text()) == dict(zip(("environment", "norms"), at_limits()))
    index = ROOT / "conformance/wire-contract/acts@0-catalogue.json"
    assert json.loads(index.read_text()) == catalogue_index("acts@0")


def test_the_sources_at_each_limit_are_accepted_and_clean_in_python():
    for raw, norms in accepted():
        assert legacy(raw, norms) is None
        assert run(CONTRACT, {"environment": raw, "norms": norms}, registry=REGISTRY) is CLEAN


def test_every_fault_gives_its_member_in_python_with_leans_text():
    for fault in catalogue("acts@0"):
        raw, norms = fault.source()
        error = legacy(raw, norms)
        outcome = run(CONTRACT, {"environment": raw, "norms": norms}, registry=REGISTRY)
        assert error is not None and isinstance(outcome, Fault), fault.name
        assert outcome.record["check"] == fault.check and outcome.record["text"] == str(error), fault.name


def test_every_fault_gives_its_record_in_lean_and_the_sources_at_each_limit_are_clean():
    from conformance.wire_contract_faults import expected_record
    faults = catalogue("acts@0")
    rows = lean_routes.diagnose("acts@0", [case(*f.source()) for f in faults] + [case(*s) for s in accepted()])
    for fault, row in zip(faults, rows):
        record = row["diagnostic"]
        assert row["outcome"] == "fault", fault.name
        assert {k: record[k] for k in expected_record(CONTRACT, fault)} == expected_record(CONTRACT, fault)
        assert record["text"] == str(legacy(*fault.source())), fault.name
    assert [row["outcome"] for row in rows[len(faults):]] == ["clean"] * len(accepted())


def test_the_adapters_read_acts_sources_of_the_norms_route_only():
    raw, norms = base()
    plain, defaults = deepcopy(raw), deepcopy(raw)
    plain["profiles"] = ["norms@0", "relational-fol@0"]
    defaults["profiles"] = ["acts@0", "norm-defaults@0", "norms@0", "relational-fol@0"]
    cases = [case(raw, norms), case(raw, norms, "norms-conflict"), case(plain, norms), case(defaults, norms),
             case(raw, norms, "norm-defaults-elaborate")]
    rows = lean_routes.diagnose("acts@0", cases)
    assert [row["status"] for row in rows] == ["ok", "ok", "error", "error", "error"]
    assert acts_source(cases[0]) == {"environment": raw, "norms": norms}
    for c, row in zip(cases[2:], rows[2:]):
        with pytest.raises(UnsupportedProfile) as raised:
            acts_source(c)
        assert str(raised.value) == row["error"]
    assert rows[2]["error"] == OUTSIDE
