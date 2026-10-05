"""Lean-first batch 0: the triage of the differential fuzzer's disagreement groups
(`docs/lean-first/b0/df-triage.json`, docs/lean-first/b0/TRIAGE.md).

Every group DF-1 to DF-18 of the fuzzer's baseline is classed and carries its minimised
fixture. The Lean-accepts bugs the plan names (section 7.1) are run live here: each test
states today's discrepancy, so the batch that fixes Lean must change it (a fixed bug makes the
test fail until its expectation is flipped in that batch, with its DELTA.md entry)."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from tests import test_norms
from tests.test_environment_field_types import BIN, _block_matrix, _rights, lean_route_rows
from tests.test_p0_three_way import python_verdict
from ve import Environment
from ve.backends import relay
from ve.errors import VEError

ROOT = Path(__file__).resolve().parents[1]
TRIAGE = json.loads((ROOT / "docs/lean-first/b0/df-triage.json").read_text())
GROUPS = {group["id"]: group for group in TRIAGE["groups"]}
needs_service = pytest.mark.skipif(not (BIN / "ve_service").exists(), reason="Lean service has not been built")


def test_every_group_is_classed_with_its_fixture():
    assert list(GROUPS) == [f"DF-{i}" for i in range(1, 19)] + ["K1", "K2", "K3", "K4", "R1"]
    for group in TRIAGE["groups"]:
        assert group["class"] in TRIAGE["classes"] and group["batch"] and group["note"], group["id"]
        if group["id"].startswith("DF-"):
            fixture = group["fixture"]
            assert fixture["input"] and set(fixture["answers"]) == {"python", "lean", "rust"}, group["id"]
            assert group["entries"] >= 1


def test_the_lean_bugs_are_classed_as_lean_bugs():
    """Section 7.1's Lean-accepts bugs are class (i) or (iii), each with the batch it must precede
    (the duplicate `protected` entry, K2, is closed at the base)."""
    for name in ("DF-8", "DF-12", "K1"):
        assert GROUPS[name]["class"] in ("i", "iii"), name
    assert GROUPS["K2"]["class"] == "closed" and GROUPS["K2"]["batch"] == "7"
    assert GROUPS["DF-12"]["batch"].startswith("5")
    assert GROUPS["DF-8"]["batch"] == "12" and GROUPS["K1"]["batch"] == "12"


def _python(call):
    try:
        call()
    except VEError as exc:
        return exc.code, exc.message
    return "ok", ""


def test_df1_is_closed_at_the_base(monkeypatch):
    """DF-1 no longer reproduces: Python rejects a non-array `profiles` with Lean's diagnostic."""
    monkeypatch.setenv("VE_AUTHORITY", "python")
    fixture = GROUPS["DF-1"]["fixture"]
    lean = fixture["answers"]["lean"]
    assert _python(lambda: Environment(deepcopy(fixture["input"]["environment"]))) == (lean["code"], lean["text"])


@needs_service
def test_df8_dependency_order_accepts_a_misspelt_vocabulary_field(monkeypatch):
    """Lean's dependency-order route accepts an empty vocabulary that Python rejects."""
    monkeypatch.setenv("VE_AUTHORITY", "python")
    case = deepcopy(GROUPS["DF-8"]["accepts_fixture"]["input"])
    assert python_verdict(deepcopy(case))["status"] == "error"
    [row] = relay.decide("route", [case])
    assert row["status"] == "ok" and row["order"] == []


@needs_service
def test_df12_risk_route_accepts_an_nbsp_act_phrase(monkeypatch):
    monkeypatch.setenv("VE_AUTHORITY", "python")
    environment = GROUPS["DF-12"]["fixture"]["input"]
    code, message = _python(lambda: Environment(deepcopy(environment)))
    assert code == "InvalidInput" and "round-trip" in message
    assert lean_route_rows("risk", [deepcopy(environment)]) == [("ok", "")]


def _norms_environment(act):
    return {"language": test_norms.LANGUAGE, "profiles": ["norms@0", "relational-fol@0"],
            "spec_revision": test_norms.SPEC_REVISION,
            "vocabulary": {"sorts": {"act": {"description": "act"}}, "constants": {},
                           "predicates": {"permitted": test_norms.permission(act=act)}}}


@needs_service
def test_k1_lean_accepts_the_act_phrase_word_no(monkeypatch):
    monkeypatch.setenv("VE_AUTHORITY", "python")
    raw = _norms_environment("{0} be no longer done")
    assert _python(lambda: Environment(deepcopy(raw))) == ("InvalidInput", "InvalidInput: invalid act phrase for permitted")
    assert _python(lambda: Environment(_norms_environment("{0} be longer done"))) == ("ok", "")
    [row] = relay.decide("norms", [{"id": "k1", "kind": "background", "environment": raw}])
    assert row["status"] == "ok"


def test_k2_duplicate_protected_entries_are_rejected_by_both(monkeypatch):
    """K2 is closed at the base: Lean's rights route rejects a repeated `protected` name too;
    only the texts differ (a wording change for batch 7's list)."""
    from ve.rights import RightsEnvironment
    monkeypatch.setenv("VE_AUTHORITY", "python")
    case = {"build": RightsEnvironment, "row": {"kind": "rights-elaborate", "document": []}}
    differing = _block_matrix("ve_rights_route", case, _rights,
                              [("protected-duplicate", ("vocabulary", "rights", "protected"), ["person", "person"])])
    assert differing == [("protected-duplicate", ("InvalidInput", "protected"), ("InvalidInput", "protected person"))]


def test_the_triage_document_states_the_classes_of_the_data():
    """TRIAGE.md's table is the data's: one row per group, with its class and batch."""
    text = (ROOT / "docs/lean-first/b0/TRIAGE.md").read_text()
    rows = {}
    for line in text.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if line.startswith("| ") and cells[0] in GROUPS:
            rows[cells[0]] = (cells[1], cells[2])
    assert rows == {name: (group["class"], group["batch"]) for name, group in GROUPS.items()}
