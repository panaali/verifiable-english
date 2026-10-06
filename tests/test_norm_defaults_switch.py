"""Batch 10b: Lean answers that the Python document and admission paths consume."""
from __future__ import annotations

from copy import deepcopy

import pytest

from tests.test_norm_defaults import csam, CSAM_RULE, csam_document
from ve import norm_defaults_route
from ve.document import check_document
from ve.errors import CheckerUnavailable
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


def test_document_reports_the_leans_grounding_and_gap(tmp_path):
    result = check_document(csam_document(tmp_path, "allow"))
    assert result["norm_defaults"]["report"] == {
        "csam_generation_permitted": ["completion: allow", "default reached: reachable",
                                      "UngroundedDefault: csam_generation_permitted"]}
