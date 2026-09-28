"""Reports preparation is untrusted; these tests cover its scope and identity."""
import json

import pytest

from ve.document import check_document
from ve.environment import Environment
from ve.errors import UnsupportedProfile, VEError
from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.reports import ReportsDocument
from ve.report_english import render_report_unit, parse_rendered_report


def environment(profiles=None):
    return Environment({
        "language": LANGUAGE,
        "profiles": profiles or ["documents@1", "relational-fol@0", "reports@0"],
        "spec_revision": SPEC_REVISION,
        "reports": {"holders": ["person", "text"], "evidence": "evidence"},
        "vocabulary": {
            "sorts": {s: {"description": s} for s in ("person", "text", "evidence")},
            "predicates": {"safe": {"arguments": ["person"], "description": "safe"}},
            "constants": {"article": {"sort": "text", "description": "article"},
                          "alice": {"sort": "person", "description": "Alice"},
                          "e1": {"sort": "evidence", "description": "evidence"}},
        },
    })


def contexts(tense="present"):
    return [{"id": "c1", "tense": tense, "reference_time": None, "description": "publication"}]


def report(inner=None, *, holder="article", act="says", literal=None):
    return {"report": {"holder": holder, "act": act, "context": "c1", "literal": literal,
                       "content": inner or {"ast": ["unary", "safe", ["const", "alice"]]}}}


def unit(content, uid="u1", kind=None):
    return {"id": uid, "kind": kind or ["attributed", "article", "says", "asserted"],
            "content": content}


def test_report_payload_does_not_become_an_author_premise():
    doc = ReportsDocument(environment(), contexts(), [], [unit(report())])
    assert doc.premises == [["unary", "reports__says__1", ["const", "article"]]]
    assert doc.search_payload()["untrusted"] is True
    assert doc.extended_environment.predicates["reports__says__1"].arguments == ("text",)
    assert "safe" in doc.extended_environment.predicates


def test_nested_and_negated_scope_and_context_binding():
    inner = report(holder="alice", act="believes")
    outer = report(inner)
    doc = ReportsDocument(environment(), contexts(), [], [
        unit(outer, kind=["attributed", "article", "says",
                          ["attributed", "alice", "believes", "asserted"]]),
        unit({"negated": inner}, "u2", ["attributed", "alice", "believes", "asserted"]),
    ])
    assert doc.premises[0] == ["unary", "reports__says__1", ["const", "article"]]
    assert doc.premises[1] == ["not", ["unary", "reports__believes__1", ["const", "alice"]]]
    changed = ReportsDocument(environment(), contexts("past"), [], [unit(report())])
    plain = ReportsDocument(environment(), contexts(), [], [unit(report())])
    assert changed.premises == plain.premises
    assert changed.document_id != plain.document_id


def test_assessment_is_open_and_has_a_separate_generated_atom():
    assessment = {"id": "a1", "context": "e1", "decided_by": "unresolved_decider",
                  "necessary": [], "sufficient": [], "factors": ["review status"],
                  "precedents": [], "jurisdiction": "news_desk", "version": 1}
    node = {"assessment": {"judgment": "may", "record": "a1",
                           "content": {"ast": ["unary", "safe", ["const", "alice"]]}}}
    doc = ReportsDocument(environment(), contexts(), [assessment],
                          [unit(node, kind=["hedged", "could", "asserted"])])
    assert doc.premises == [["unary", "reports__may__1", ["const", "e1"]]]
    assert doc.open_terms[0]["decided_by"] == "unresolved_decider"
    assert doc.open_terms[0]["factors"] == ["review status"]


def test_quoted_packages_validate_locally_without_outer_layer():
    local = environment().to_dict()
    del local["reports"]
    local["profiles"] = ["norms@0", "relational-fol@0"]
    quote = {"norm": {"environment": local, "norms": []}}
    doc = ReportsDocument(environment(), contexts(), [],
                          [unit(report(quote), kind=["attributed", "article", "says", "norm"])])
    assert doc.premises == [["unary", "reports__says__1", ["const", "article"]]]
    assert "norms@0" not in doc.extended_environment.profiles
    broken = json.loads(json.dumps(quote))
    broken["norm"]["environment"]["profiles"] = ["relational-fol@0"]
    with pytest.raises(VEError, match="quoted norm needs norms@0 locally"):
        ReportsDocument(environment(), contexts(), [],
                        [unit(report(broken), kind=["attributed", "article", "says", "norm"])])


def test_literal_and_paraphrase_have_distinct_keys():
    units = [unit(report(), "u1"), unit(report(literal="Alice is safe"), "u2")]
    doc = ReportsDocument(environment(), contexts(), [], units)
    assert doc.premises[0][1] != doc.premises[1][1]


def test_bound_review_wording_rejects_changed_context_and_text():
    doc = ReportsDocument(environment(), contexts(), [], [unit(report())])
    rendered = render_report_unit(doc, "u1")
    assert rendered["text"] == "article says that Alice is safe."
    assert parse_rendered_report(doc, rendered) == report()
    with pytest.raises(VEError, match="ManifestMismatch"):
        parse_rendered_report(ReportsDocument(environment(), contexts("past"), [],
                                              [unit(report())]), rendered)
    with pytest.raises(VEError, match="ManifestMismatch"):
        parse_rendered_report(doc, {**rendered, "text": "article claims that Alice is safe."})


def test_reject_unsupported_act_and_profile_composition():
    with pytest.raises(VEError, match="UnsupportedAct"):
        ReportsDocument(environment(), contexts(), [], [unit(report(act="promised"))])
    with pytest.raises(UnsupportedProfile, match="reports@0 with norms@0"):
        environment(["documents@1", "norms@0", "relational-fol@0", "reports@0"])


def test_w2_loader_keeps_reports_unverified(tmp_path):
    env = environment().to_dict()
    source = "The article says that Alice is safe.\n"
    metadata = {"format": "ve-document@1", "environment": env, "contexts": contexts(),
                "units": [{"id": "u1", "span": [0, len(source.encode())],
                           "kind": ["attributed", "article", "says", "asserted"],
                           "meaning": "specified", "support": "testimony",
                           "content": report()}]}
    path = tmp_path / "report.md"
    path.write_text("---\n" + json.dumps(metadata) + "\n---\n" + source)
    result = check_document(path)
    assert result["status"] == "UNVERIFIED"
    assert result["coverage"]["bytes_by_status"] == {"OPEN": len(source.encode())}
    assert result["reports"]["premises"] == [["unary", "reports__says__1", ["const", "article"]]]
