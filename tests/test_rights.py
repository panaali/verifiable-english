"""Rights holder-side elaboration regressions."""
from __future__ import annotations

import pytest
import json

from tests.test_norms import environment, obligation, permission
from ve.document import check_document, render_document
from ve.soft_route import elaborate_soft_document
from ve.errors import VEError
from ve.rights import RightsEnvironment, correlate


def rights_env():
    raw = environment({
        "protect_required": obligation("deny", "protect_permitted",
                                        act="{0} protect {1}", args=("state", "person")),
        "protect_permitted": permission("allow", act="{0} protect {1}",
                                         args=("state", "person")),
        "person_may_act": permission("allow", act="{0} act", args=("person",)),
    }, sorts=("state", "person")).to_dict()
    raw["profiles"] = sorted({"relational-fol@0", "norms@0", "soft-norms@0", "rights@0"})
    raw["vocabulary"]["rights"] = {"holders": ["person"], "bearers": ["state"],
                                    "protected": [], "alters": {}}
    return raw


def claim(name="protect"):
    return {"kind": "claim", "holder_slot": None, "cites": {},
            "norm": {"name": name, "predicate": "protect_required", "sign": True,
                     "guard": ["top"], "unless": [], "over": []}}


def right(lines=None, guard=None):
    return {"right": {"name": "life", "holder": "person", "guard": guard or ["top"],
                      "lines": [claim()] if lines is None else lines}}


def test_profile_and_identity_bound_rights_block():
    raw = rights_env()
    env = RightsEnvironment(raw)
    assert env.to_dict() == raw
    changed = rights_env()
    changed["vocabulary"]["rights"]["bearers"].append("person")
    assert RightsEnvironment(changed).environment_id != env.environment_id
    raw["profiles"].remove("soft-norms@0")
    with pytest.raises(VEError, match="rights@0 requires soft-norms@0"):
        RightsEnvironment(raw)


def test_claim_is_one_soft_rule_and_limitation_is_one_pack():
    units = [right(), {"limitation": {"name": "l29", "scope": "all", "kinds": ["claim"],
                                    "decided_by": "unstated", "conditions": [
                                        {"name": "law", "role": "necessary", "decided_by": None,
                                         "verbalisation": "determined by law"}], "factors": []}}]
    doc = correlate(rights_env(), units)
    assert [rule.core.name for rule in doc.soft_document.rules] == ["protect"]
    assert doc.limitation_names == {("l29", "protect_permitted"): "rights__lim__1"}
    assert doc.condition_names == {("l29", "protect_permitted", "law"): "rights__cond__1"}
    assert len(doc.soft_document.rules[0].core.unless) == 1
    assert [label for label, _ in doc.limitation_premises] == [
        "rights:limitation:l29:protect_permitted:necessary:law"]


def test_right_requires_incident_and_claim_shape():
    with pytest.raises(VEError, match="RightWithoutIncident: life"):
        correlate(rights_env(), [right([])])
    invalid = claim()
    invalid["norm"]["predicate"] = "person_may_act"
    with pytest.raises(VEError, match="IncidentShape"):
        correlate(rights_env(), [right([invalid])])


def test_document_check_uses_correlated_soft_route(tmp_path):
    source = "Every person has a right to protection.\n"
    meta = {"format": "ve-document@1", "environment": rights_env(),
            "units": [{"id": "u1", "span": [0, len(source)], "kind": "right",
                       "meaning": "specified", "support": "none", "content": right()}]}
    path = tmp_path / "rights.ve.md"
    path.write_text("---\n" + json.dumps(meta) + "\n---\n" + source)
    result = check_document(path)
    assert result["rights"]["environment_id"]
    assert result["soft"]["soft_document_hash"]
    assert "Claim of right life" in render_document(path)


def test_rule_bar_elaborates_over_right_liberty():
    liberty = {"kind": "liberty", "holder_slot": None, "cites": {},
               "norm": {"name": "may-act", "predicate": "person_may_act", "sign": True,
                        "guard": ["top"], "unless": [], "over": []}}
    doc = correlate(rights_env(), [right([liberty]),
                                   {"bar": {"name": "b30", "reading": "rule",
                                            "decided_by": "unstated"}}])
    assert doc.bar_names == {"person_may_act": "rights__bar__1"}
    assert [r.core.name for r in doc.soft_document.rules] == ["may-act", "rights-bar-1"]
    assert doc.soft_document.rules[-1].core.over == ("may-act",)
    assert elaborate_soft_document(doc.soft_document)["status"] == "ok"
