"""RD-6b: 200 generated norms-chain documents, superposed versus the retained enumerated oracle."""
from __future__ import annotations

from tests.test_readings_nd_document import QUERY, as_document
from tests.test_readings_nd_lean import doc1, doc2, env1, env2
from ve.document import load_document
from ve.readings_verdicts import Enumerated, Superposed


def test_200_generated_documents_agree_on_both_routes(tmp_path):
    query2 = ["forall", "act", ["unary", "x_required", ["var", 0]]]
    for index in range(200):
        if index % 2 == 0:
            raw = env1()
            document, _ = doc1(raw, set_id=f"rs_{index + 1}", rule=f"must-help-{index + 1}")
            texts = {"u1": "Every agent must help each user.\n"}
            question = QUERY
        else:
            raw = env2()
            document, _ = doc2(raw)
            document["units"][0]["content"]["norm"]["name"] = f"no-x-{index + 1}"
            document["reading_sets"][0]["readings"][0]["content"]["norm"]["name"] = f"must-x-{index + 1}"
            texts = {"u0": "Nothing may be done.\n", "u2": "Every act must be done if it may be tried.\n"}
            question = query2
        loaded = load_document(as_document(tmp_path, raw, document, texts))
        row = loaded["readings_s2"]
        assert row["route"] == "superposed" and row["choices_checked"] == 2
        superposed = Superposed(loaded)
        enumerated_row = {**row, "route": "enumerated", "finding": {
            "text": "ReadingsNotSuperposable: " + document["reading_sets"][0]["id"],
            "cause": "the unspecified completion"}}
        enumerated = Enumerated({**loaded, "readings_s2": enumerated_row})
        assert superposed.conflict()["status"] == enumerated.conflict()["status"]
        assert superposed.entailment(question)["verdict"] == enumerated.entailment(question)["verdict"]
