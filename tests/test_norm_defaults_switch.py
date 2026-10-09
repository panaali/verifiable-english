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


def _flagged_document():
    """The agent-policy document whose `tool` is a functional, total `data@0` flag, and a model of
    its base situation (with the `unsaid__` filling tables when `filled`) for a given `tool` table."""
    import json
    from ve.environment import Environment
    from tests.test_assurance_manifest import ROOT
    raw = json.loads((ROOT / "usecases/agent-policy/environment.unspecified.json").read_text())
    assert raw["vocabulary"]["predicates"]["tool"]["functional"] and raw["vocabulary"]["predicates"]["tool"]["total"]
    rule = {"norm": {"name": "r1", "predicate": "permitted", "sign": True,
                     "guard": ["unary", "readonly", ["var", 0]], "unless": [], "over": []}}
    document = UnspecifiedDocument(Environment(raw), [rule])
    situation = document.situation_environment()
    strings = [c for c, d in raw["vocabulary"]["constants"].items() if d["sort"] == "$string"]

    def model(tool, filled=False):
        domains = {s: [] for s in situation.sorts}
        domains.update(action=["a"], directory=["workspace"], **{"$string": strings})
        relations = {p: [] for p in situation.predicates}
        relations.update(tool=tool, readonly=[["a"]])
        if filled:
            relations.update({f"unsaid__{p}": [] for p in document.unspec})
        return {"complete": True, "domains": domains, "constants": {**{c: c for c in strings}, "workspace": "workspace"},
                "relations": relations}

    return document, model


# Every entry point of the norm-defaults route that reads a supplied model; each one admits
# `data@0` flags, so each must refuse a model that breaks one (Lean `Wire.admitModel`).
def _status(document, model, tool):
    from ve.norm_defaults_route import run_case, source_case
    return run_case(source_case(document, "norm-defaults-status", model=model(tool), predicate="permitted",
                                tuple=["a"], method="enumerate"))


def _report_model(document, model, tool):
    from ve.norm_defaults import report
    return report(document, model=model(tool))


def _report_witness(document, model, tool):
    from ve.norm_defaults import report
    return report(document, witnesses={"permitted": {"model": model(tool, filled=True), "tuple": ["a"]}})


def _conflict_witness(document, model, tool):
    from ve.norm_defaults_route import run_case, source_case
    target = document.elaboration["conflict_targets"][0]["target"]
    return run_case(source_case(document, "norm-defaults-conflict",
                                witness={"target": target, "model": model(tool, filled=True), "tuple": ["a"]}))


def _gaps_model(document, model, tool):
    from ve.norm_defaults_route import run_case, source_case
    return run_case(source_case(document, "norm-defaults-gaps", model=model(tool, filled=True),
                                predicate="permitted", tuple=["a"]))


MODEL_ENTRY_POINTS = [_status, _report_model, _report_witness, _conflict_witness, _gaps_model]
BROKEN_TOOL = {"not total": [], "not functional": [["a", "shell"], ["a", "web_fetch"]]}


def test_data_flags_are_admitted_and_every_supplied_model_must_satisfy_them():
    """English E2.6 (readability R01 to R16): Lean's norm-defaults route admits `data@0` flags as Python's base did."""
    document, model = _flagged_document()
    assert _status(document, model, [["a", "shell"]])["point_status"] == "SETTLED yes"
    assert _report_model(document, model, [["a", "shell"]])["report"]


@pytest.mark.parametrize("entry", MODEL_ENTRY_POINTS, ids=lambda f: f.__name__.lstrip("_"))
@pytest.mark.parametrize("broken", sorted(BROKEN_TOOL))
def test_every_supplied_model_that_breaks_a_flag_is_invalid_model_flags(entry, broken):
    """A status, report model, report witness, CONFLICT witness or `gaps: reachable` model that violates
    a flag (`tool` not total, or not functional) is `InvalidModel(flags)`, never a verdict; the same
    model with the flag kept is admitted. Removing the flag check from any one replay fails here
    (review e2-flip B: the witness and reached replays were untested)."""
    from ve.errors import VEError
    document, model = _flagged_document()
    entry(document, model, [["a", "shell"]])
    with pytest.raises(VEError, match=r"^InvalidModel\(flags\)"):
        entry(document, model, BROKEN_TOOL[broken])
