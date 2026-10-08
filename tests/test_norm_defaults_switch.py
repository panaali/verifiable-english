"""Batch 10b: Lean answers that the Python document and admission paths consume."""
from __future__ import annotations

from copy import deepcopy

import pytest

from tests.test_norm_defaults import csam, CSAM_RULE, csam_document
from ve import norm_defaults_route
from ve.document import check_document
from ve.errors import CheckerUnavailable, UnsupportedProfile
from ve.norm_defaults import UnspecifiedDocument


def test_filled_identity_is_bound_to_leans_elaboration(monkeypatch):
    document = UnspecifiedDocument(csam("unspecified"), [CSAM_RULE])
    assert document.filled.env.environment_id == document.elaboration["filled_environment_id"]
    assert document.fill_hash == document.elaboration["fill_hash"]
    assert document.document_hash == document.elaboration["document_hash"]
    original = norm_defaults_route.run_case

    def tampered(case):
        answer = deepcopy(original(case))
        answer["filled_environment_id"] = "0" * 64
        return answer

    monkeypatch.setattr(norm_defaults_route, "run_case", tampered)
    with pytest.raises(CheckerUnavailable, match="identity mismatch"):
        UnspecifiedDocument(csam("unspecified"), [CSAM_RULE])


def test_lean_accepts_constant_wording_and_refuses_a_repeated_profile():
    """The norm-defaults decoder accepts a constant's `verbalisation`, as Python does (DF-19), and
    setting the profile aside does not hide a repeated `norm-defaults@0` from the envelope gate."""
    environment = csam("unspecified").to_dict()
    assert "verbalisation" in environment["vocabulary"]["constants"]["claude"]
    case = {"id": "elaborate", "kind": "norm-defaults-elaborate", "environment": environment,
            "norms": [CSAM_RULE.to_dict()]}
    assert norm_defaults_route.run_case(case)["filled_environment_id"]
    repeated = deepcopy(environment)
    repeated["profiles"] = ["norm-defaults@0", *repeated["profiles"]]
    with pytest.raises(UnsupportedProfile, match="^UnsupportedProfile: profiles must be sorted and unique$"):
        norm_defaults_route.run_case({**case, "environment": repeated})


def test_document_reports_the_leans_grounding_and_gap(tmp_path):
    result = check_document(csam_document(tmp_path, "allow"))
    assert result["norm_defaults"]["report"] == {
        "csam_generation_permitted": ["completion: allow", "default reached: reachable",
                                      "UngroundedDefault: csam_generation_permitted"]}


def test_data_flags_are_admitted_and_every_supplied_model_must_satisfy_them():
    """English E2.6 (readability R01 to R16): Lean's norm-defaults route admits `data@0` flags as Python's base did;
    a status or report model that violates one (`tool` not total, or not functional) is `InvalidModel(flags)`."""
    import json
    from ve.environment import Environment
    from ve.errors import VEError
    from ve.norm_defaults import report
    from ve.norm_defaults_route import run_case, source_case
    from tests.test_assurance_manifest import ROOT
    raw = json.loads((ROOT / "usecases/agent-policy/environment.unspecified.json").read_text())
    assert raw["vocabulary"]["predicates"]["tool"]["functional"] and raw["vocabulary"]["predicates"]["tool"]["total"]
    rule = {"norm": {"name": "r1", "predicate": "permitted", "sign": True,
                     "guard": ["unary", "readonly", ["var", 0]], "unless": [], "over": []}}
    document = UnspecifiedDocument(Environment(raw), [rule])
    situation = document.situation_environment()
    strings = [c for c, d in raw["vocabulary"]["constants"].items() if d["sort"] == "$string"]

    def model(tool):
        domains = {s: [] for s in situation.sorts}
        domains.update(action=["a"], directory=["workspace"], **{"$string": strings})
        relations = {p: [] for p in situation.predicates}
        relations.update(tool=tool, readonly=[["a"]])
        return {"complete": True, "domains": domains, "constants": {**{c: c for c in strings}, "workspace": "workspace"},
                "relations": relations}

    def status(tool):
        return run_case(source_case(document, "norm-defaults-status", model=model(tool), predicate="permitted",
                                    tuple=["a"], method="enumerate"))["point_status"]

    assert status([["a", "shell"]]) == "SETTLED yes"
    for tool in ([], [["a", "shell"], ["a", "web_fetch"]]):
        with pytest.raises(VEError, match=r"^InvalidModel\(flags\)"):
            status(tool)
        with pytest.raises(VEError, match=r"^InvalidModel\(flags\)"):
            report(document, model=model(tool))
    assert report(document, model=model([["a", "shell"]]))["report"]
