"""The fault catalogue and the oracle of the soft-norms gate (wire-contract.md 8.3), checked without Lean.

The full gate (`python -m conformance.wire_contract_gate`) runs both engines and both legacy validators;
these tests check, quickly, that the oracle is the catalogue's and not an engine's: each fault alone gives
its hand-written check and path in the Python engine, positions order as section 2.6 and section 6 say,
footprints keep interacting faults apart, and a combination is judged by its check, not only its code.
"""

import json
from pathlib import Path

import pytest

from conformance.wire_contract_gate import _applied
from conformance.wire_contract_faults import (UNREACHED, catalogue, expected_first, expected_record,
                                              footprint, legacy_codes, overlaps, position)
from ve.softnorms_contract import REGISTRY
from ve.wire_contract.engine import Fault, load, run

CONTRACT = load("soft-norms@0")
FAULTS = {fault.name: fault for fault in catalogue()}
REPORT = Path(__file__).resolve().parents[1] / "conformance/wire-contract/soft-norms@0-gate.json"
FIELDS = ("contract", "revision", "check", "phase", "code", "class", "path")


def python(faults):
    outcome = run(CONTRACT, _applied(faults), registry=REGISTRY)
    assert isinstance(outcome, Fault)
    return {key: outcome.record[key] for key in FIELDS}


@pytest.mark.parametrize("name", sorted(FAULTS))
def test_each_fault_alone_gives_its_hand_written_record(name):
    fault = FAULTS[name]
    assert python([fault]) == expected_record(CONTRACT, fault)
    if name in legacy_codes():
        assert legacy_codes()[name] == expected_record(CONTRACT, fault)["code"]


def test_positions_follow_the_table_and_the_order_keys():
    pos = lambda name: position(CONTRACT, FAULTS[name])
    # Phase order, then item-major inside a group: rule 0's last field check before rule 1's first.
    assert pos("language") < pos("party-name") < pos("profile-unknown") < pos("r0-factors") < pos("r1-field")
    # Check-major across two groups over the same items: 2.1a on any predicate before 2.2a on any.
    assert pos("reserved-name-z") < pos("instruction-type")
    # Inside `rule_typing` (section 6): 5.8b on condition 0 comes before 5.8a on condition 1.
    assert pos("r0-condition") < pos("r0-necessary-budget")
    assert pos("r0-guard") < pos("r0-condition")


def test_footprints_keep_interacting_faults_apart():
    """Each pair here gave the gate a wrong expectation before footprints covered replaced values, reads
    and the shared document budget; the old code-only oracle could not see the first one at all."""
    prints = {name: footprint(fault) for name, fault in FAULTS.items()}
    for left, right in (("derived-depth", "derived-nodes"), ("outranking-field", "outranking-decider-type"),
                        ("vocabulary-limit", "stratification"), ("soft-over-hard", "long-decision-names"),
                        ("revision", "soft4-layers-strict-guard-4981")):
        assert overlaps(prints[left], prints[right]), (left, right)
    assert not overlaps(prints["language"], prints["r0-mode"])


def test_the_oracle_judges_the_check_not_only_the_code():
    """2.11 and 4.10 share the code SOFT_INVALID_DECIDER; the expected record names 2.11."""
    combo = (FAULTS["r0-decider-type"], FAULTS["outranking-decider-type"])
    first = expected_first(CONTRACT, combo)
    assert first.name == "outranking-decider-type"
    assert python(combo) == expected_record(CONTRACT, first)


def test_stored_gate_report_has_no_mismatch_and_explains_every_gap():
    report = json.loads(REPORT.read_text())
    assert report["revision"] == CONTRACT["revision"]
    assert report["mismatches"] == []
    assert report["residual"] == {"python": 0, "lean": 0}
    gaps = set(report["coverage_unmet"]["first"]) | set(report["coverage_unmet"]["masked"])
    assert gaps <= set(report["coverage_unmet_reasons"])
    assert set(UNREACHED) <= gaps
    assert report["oracle"].startswith("fault catalogue")
