"""The `acts@0` wire table in shadow (ap-1bf): the legacy validator still owns the verdict; the engines name the
member of 1.1 at and around each limit of `VE.Acts.Lexical`, the limits read from Lean and never copied."""

from copy import deepcopy
import json
import os
from pathlib import Path
import re
import subprocess

import pytest

from conformance.acts_contract import REGISTRY, acts_source
from conformance.wire_contract_engine import CLEAN, Fault, load, run
from conformance.wire_contract_faults import catalogue, catalogue_index
from conformance.wire_contract_faults_acts import EXAMPLES, at_count, at_limits, base, limits
from tests import lean_routes
from tests.subprocesses import HANG_TIMEOUT
from tools import nested_pytest
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


def engine_records(sources):
    """Each source's record in Python's engine and in Lean's (`None` when clean), as pairs."""
    python = [run(CONTRACT, {"environment": deepcopy(raw), "norms": deepcopy(norms)}, registry=REGISTRY)
              for raw, norms in sources]
    lean = lean_routes.diagnose("acts@0", [case(raw, norms) for raw, norms in sources])
    assert [row["status"] for row in lean] == ["ok"] * len(sources)
    return [(outcome.record if isinstance(outcome, Fault) else None, row.get("diagnostic"))
            for outcome, row in zip(python, lean)]


def test_a_source_without_norms_gives_one_record_in_both_engines():
    """F1 of ap-1bf's review: without `norms@0` both engines give one check, outcome and text, the profile
    row's, which Lean writes and Python relays."""
    raw, norms = base()
    raw["profiles"].remove("norms@0")
    [(python, lean)] = engine_records([(raw, norms)])
    assert python is not None and python == lean
    assert lean["check"] == "1.1d" and lean["text"] == str(legacy(raw, norms))


# The test files whose `acts@0` sources the recorded corpus holds (F2 of ap-1bf's review): `-k acts` selects this
# file and the unit's row of the s5 tests, and the corpus test itself is left out of its own run.
RECORDED_TESTS = ("tests/test_acts_contract.py", "tests/test_wire_contract_s5_lean.py")


def recorded_sources(output):
    """The `[test id, environment, norms]` rows `tests/contract_input_recorder.py` records for `acts@0` while the
    recorded test files run."""
    environment = nested_pytest.environment(os.environ, VE_CONTRACT_INPUTS=str(output), VE_CONTRACT_UNIT="acts@0",
                                            VE_NATIVE_PREBUILT="1", PYTHONPATH=str(ROOT))
    result = subprocess.run(nested_pytest.command(["-q", "-p", "tests.contract_input_recorder", "-p",
                                                   "no:cacheprovider", "-o", "addopts=", "-m", "not live", "-k",
                                                   "acts and not recorded_corpus", *RECORDED_TESTS]),
                            cwd=ROOT, env=environment, capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert result.returncode == 0, result.stdout[-4000:]
    return json.loads(output.read_text())


def test_the_recorded_corpus_gives_one_record_in_both_engines(tmp_path):
    """F2 of ap-1bf's review: every `acts@0` source the tests submit gives one record, or none, in both engines."""
    recorded = recorded_sources(tmp_path / "inputs.json")
    assert any("norms@0" not in raw["profiles"] for _, raw, _ in recorded)  # F1's source is recorded
    pairs = engine_records([(raw, norms) for _, raw, norms in recorded])
    assert sum(lean is not None for _, lean in pairs) > len(catalogue("acts@0"))
    assert [label for (label, _, _), (python, lean) in zip(recorded, pairs) if python != lean] == []


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
