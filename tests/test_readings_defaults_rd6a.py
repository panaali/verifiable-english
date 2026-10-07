"""RD-6a (docs/spec/readings-defaults-PLAN.md): the premise of fixture X1 that Lean's `#guard`s cannot state.

X1 (lean/VE/Readings/SupExtraExamples.lean) shows that `superpose_all_extra` needs `hQw`: on S2a's K1 a carried
family over a layer symbol satisfies `Transfers` and gets its certificate accepted, yet the conclusion fails on both
readings. Its conflict-freedom hypothesis is that K1's slot is CONFLICT-FREE (`Q` holds of every admissible base,
so it excludes none). Conflict-freedom is not a Boolean `#guard`; here the Lean route certifies it, on the
superposed route, for the document of K1 (`rs1` = {strict, default} `no-deception` on `avoid_required`).
"""
from __future__ import annotations

from tests.test_readings_s2_document import DF, S, check_document, s2_document


def test_x1_k1_is_conflict_free_on_the_superposed_route(tmp_path):
    report = check_document(s2_document(tmp_path, [("set", "rs1", "u1", [S, DF])]))
    assert report["premises"]["route"] == "superposed"
    readings = report["readings"]
    assert readings["conflict"]["status"] == "CONFLICT-FREE", readings["conflict"]


def test_x1_premise_fails_when_k1_has_a_conflict(tmp_path):
    """The same check reports CONFLICT once K6's `never-avoid` is fixed beside the set (S2a M3), so the test above
    can fail."""
    from tests.test_readings_s2_document import NEVER_AVOID
    report = check_document(s2_document(tmp_path, [("set", "rs1", "u1", [S, DF]), ("fixed", "u0", NEVER_AVOID)]))
    assert report["readings"]["conflict"]["status"] != "CONFLICT-FREE"
