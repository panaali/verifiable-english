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
        "vocabulary": {
            "reports": {"holders": ["person", "text"], "evidence": "evidence"},
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


def unit(content, uid="u1", kind=None, meaning="specified"):
    index = int(uid[1:])
    return {"id": uid, "span": [index, index + 1], "kind": kind or ["attributed", "article", "says", "asserted"],
            "meaning": meaning, "support": "testimony", "content": content}


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
                          [unit(node, kind=["hedged", "could", "asserted"], meaning={"open": ["reports__may__1"]})])
    assert doc.premises == [["unary", "reports__may__1", ["const", "e1"]]]
    assert doc.open_terms[0]["record"]["decided_by"] == "unresolved_decider"
    assert doc.open_terms[0]["record"]["factors"] == ["review status"]


def test_quoted_packages_validate_locally_without_outer_layer():
    local = environment().to_dict()
    del local["vocabulary"]["reports"]
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
    # The holder opens the sentence capitalised; the formula content stays lower case (2.1).
    assert rendered["text"] == "Article says that alice is safe."
    assert parse_rendered_report(doc, rendered) == report()
    with pytest.raises(VEError, match="ManifestMismatch"):
        parse_rendered_report(ReportsDocument(environment(), contexts("past"), [],
                                              [unit(report())]), rendered)
    with pytest.raises(VEError, match="claims that"):
        parse_rendered_report(doc, {**rendered, "text": "Article claims that alice is safe."})


def test_reject_unsupported_act_and_profile_composition():
    with pytest.raises(VEError, match="UnsupportedAct"):
        ReportsDocument(environment(), contexts(), [], [unit(report(act="promised"))])
    with pytest.raises(UnsupportedProfile, match="reports@0 with norms@0"):
        environment(["documents@1", "norms@0", "relational-fol@0", "reports@0"])


def test_w2_loader_checks_report_elaboration_without_graph_admission(tmp_path):
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
    assert result["coverage"]["bytes_by_status"] == {"CHECKED": len(source.encode())}
    assert result["reports"]["premises"] == [{"label": "report:u1",
        "ast": ["unary", "reports__says__1", ["const", "article"]]}]


def test_w2_report_graph_admitted_by_lean(tmp_path):
    env = environment().to_dict()
    source = "The article says that Alice is safe.\n"
    metadata = {"format": "ve-document@1", "environment": env, "contexts": contexts(),
                "units": [{"id": "u1", "span": [0, len(source.encode())],
                           "kind": ["attributed", "article", "says", "asserted"],
                           "meaning": "specified", "support": "testimony", "content": report()}],
                "graph": {"root": "R", "nodes": [{"name": "R", "label": "report:u1", "unit": "u1",
                                                 "ast": ["unary", "reports__says__1", ["const", "article"]]}]}}
    path = tmp_path / "admitted-report.md"
    path.write_text("---\n" + json.dumps(metadata) + "\n---\n" + source)
    result = check_document(path)
    assert result["status"] == "CHECKED"
    assert result["admission"]["admitted"] is True
    assert result["admission"]["envelope"] == result["reports"]["envelope"]


def test_w2_assessment_graph_stays_open_and_is_admitted(tmp_path):
    env = environment().to_dict()
    source = "According to the stated assessment, Alice may be safe.\n"
    assessment = {"id": "a1", "context": "e1", "decided_by": "unresolved_decider",
                  "necessary": [], "sufficient": [], "factors": [], "precedents": [],
                  "jurisdiction": "news_desk", "version": 1}
    content = {"assessment": {"judgment": "may", "record": "a1",
                              "content": {"ast": ["unary", "safe", ["const", "alice"]]}}}
    metadata = {"format": "ve-document@1", "environment": env, "contexts": contexts(),
                "assessments": [assessment],
                "units": [{"id": "u1", "span": [0, len(source.encode())],
                           "kind": ["hedged", "could", "asserted"],
                           "meaning": {"open": ["reports__may__1"]}, "support": "testimony",
                           "content": content}],
                "graph": {"root": "A", "nodes": [{"name": "A", "label": "assessment:u1", "unit": "u1",
                                                 "ast": ["unary", "reports__may__1", ["const", "e1"]]}]}}
    path = tmp_path / "assessment.md"
    path.write_text("---\n" + json.dumps(metadata) + "\n---\n" + source)
    result = check_document(path)
    assert result["status"] == "OPEN" and result["admission"]["admitted"] is True
    assert result["coverage"]["residual"]["open_terms"] == 1


def test_w2_nested_bridge_needs_a_record(tmp_path):
    env = environment().to_dict()
    source = "The article says that Alice believes that Alice is safe.\n"
    inner = report(holder="alice", act="believes")
    outer = report(inner)
    metadata = {"format": "ve-document@1", "environment": env, "contexts": contexts(),
                "units": [{"id": "u1", "span": [0, len(source.encode())],
                           "kind": ["attributed", "article", "says",
                                    ["attributed", "alice", "believes", "asserted"]],
                           "meaning": "specified", "support": "testimony", "content": outer}],
                "bridges": [{"id": "b1", "unit": "u1", "path": "1",
                             "accepted_by": "reviewer", "reason": []}],
                "graph": {"root": "B", "nodes": [{"name": "B", "label": "bridge:accepts_at(alice,u1,1)",
                                                 "ast": ["unary", "safe", ["const", "alice"]]}]}}
    path = tmp_path / "bridge.md"
    path.write_text("---\n" + json.dumps(metadata) + "\n---\n" + source)
    result = check_document(path)
    assert result["admission"]["admitted"] is True
    # Loop recheck B: the nested leaf assumes safe(alice), yet the residual counted
    # only root `bridge:accepts(` labels (bridge_leaves 0, residual_total 0).
    assert result["admission"]["report"]["assumptions"][0]["label"] == "bridge:accepts_at(alice,u1,1)"
    residual = result["coverage"]["residual"]
    assert residual["bridges_nested"] == 1 and residual["bridge_leaves"] == 0
    assert result["coverage"]["residual_total"] == 1
    root = dict(metadata, units=[dict(metadata["units"][0], content=inner,
                                      kind=["attributed", "alice", "believes", "asserted"])],
                bridges=[], graph={"root": "B", "nodes": [{"name": "B", "label": "bridge:accepts(alice,u1)",
                                                           "ast": ["unary", "safe", ["const", "alice"]]}]})
    path.write_text("---\n" + json.dumps(root) + "\n---\n" + source)
    result = check_document(path)
    assert result["admission"]["admitted"] is True
    assert result["coverage"]["residual"]["bridge_leaves"] == 1 and result["coverage"]["residual"]["bridges_nested"] == 0
    del metadata["bridges"]
    path.write_text("---\n" + json.dumps(metadata) + "\n---\n" + source)
    with pytest.raises(VEError):
        check_document(path)


def write_report_document(tmp_path, pieces, name="doc.md", **front):
    """pieces: (source text, unit fields without id/span); units are u1, u2, ... in order."""
    units, cursor, source = [], 0, ""
    for index, (text, fields) in enumerate(pieces, 1):
        units.append({"id": f"u{index}", "span": [cursor, cursor + len(text.encode())], **fields})
        cursor += len(text.encode())
        source += text
    fences = "".join(f"```ve {f}\n{t}\n```\n" for f, t in front.pop("fences", {}).items())
    metadata = {"format": "ve-document@1", "environment": environment().to_dict(),
                "contexts": contexts(), "units": units, **front}
    path = tmp_path / name
    path.write_text("---\n" + json.dumps(metadata) + "\n---\n" + source + fences)
    return path


def reported(content=None, kind=None, meaning="specified"):
    return {"kind": kind or ["attributed", "article", "says", "asserted"], "meaning": meaning,
            "support": "testimony", "content": content or report()}


SAFE = ["unary", "safe", ["const", "alice"]]


def test_author_assertions_travel_in_the_wire_form(tmp_path):
    """Astra B: an ordinary asserted unit (AST or fenced English) beside a report unit
    reached Lean as a bare AST list ("object expected")."""
    path = write_report_document(tmp_path, [
        ("The article says that Alice is safe.\n", reported()),
        ("Alice is safe.\n", {"kind": "asserted", "meaning": "specified", "support": "assumption",
                              "content": {"ast": SAFE}}),
        ("Alice is safe, again.\n", {"kind": "asserted", "meaning": "specified", "support": "assumption",
                                     "surface": "english", "content": {"fence": "u3"}})],
        fences={"u3": "Alice is safe."},
        graph={"root": "R", "nodes": [{"name": "R", "unit": "u2", "ast": SAFE}]})
    result = check_document(path)
    assert result["admission"]["admitted"] is True
    assert result["admission"]["envelope"] == result["reports"]["envelope"]
    assert result["coverage"]["bytes_by_status"]["CHECKED"] == result["coverage"]["source_bytes"]


def test_w2_units_are_decoded_as_lean_decodes_them():
    """The same class on the Python side: W2 content is `{"ast": φ}` closed over E,
    canonicalised, and never on a quoted kind."""
    plain = {"id": "u2", "span": [2, 3], "kind": "asserted", "meaning": "specified",
             "support": "assumption", "content": {"ast": SAFE}}
    doc = ReportsDocument(environment(), contexts(), [], [unit(report()), plain])
    assert doc.elaborated()["premises"] == [{"label": "report:u1",
                                             "ast": ["unary", "reports__says__1", ["const", "article"]]}]
    for bad in ({**plain, "content": SAFE}, {**plain, "content": {"ast": ["unary", "safe", ["var", 0]]}},
                {**plain, "kind": ["attributed", "article", "says", "asserted"]}):
        with pytest.raises(VEError):
            ReportsDocument(environment(), contexts(), [], [unit(report()), bad])


A1_RECORD = {"id": "a1", "context": "e1", "decided_by": "unresolved_decider", "necessary": [], "sufficient": [],
             "factors": [], "precedents": [], "jurisdiction": "news_desk", "version": 1}
MAY = {"assessment": {"judgment": "may", "record": "a1", "content": {"ast": SAFE}}}
GENUINE = {"name": "genuine", "arguments": ["person"], "decided_by": "unresolved_decider", "necessary": [],
           "sufficient": [], "factors": [], "precedents": [], "jurisdiction": "news_desk", "version": 1}


def test_open_content_is_open_coverage(tmp_path):
    """Astra A / Fable B: every report wrapper was forced CHECKED, so a report whose
    content carries an open term (a nested `may` assessment, a denied assessment, or a
    declared W2 open term) counted its whole span CHECKED, and an explicit OPEN status
    was rejected."""
    nested = reported(report(MAY), ["attributed", "article", "says", ["hedged", "could", "asserted"]],
                      {"open": ["reports__may__1"]})
    denied = reported({"negated": MAY}, ["hedged", "could", "asserted"], {"open": ["reports__may__1"]})
    declared = reported(meaning={"open": ["genuine"]})
    cases = [("The article says that, according to the stated assessment, alice may be safe.\n", nested),
             ("It is not the case that, according to the stated assessment, alice may be safe.\n", denied),
             ("The article says that alice is safe.\n", declared)]
    front = {"assessments": [A1_RECORD], "open_terms": [GENUINE]}
    for text, piece in cases:
        for explicit in ({}, {"status": "OPEN"}):
            result = check_document(write_report_document(tmp_path, [(text, {**piece, **explicit})], **front))
            assert result["coverage"]["bytes_by_status"] == {"OPEN": len(text.encode())}, result["coverage"]
        with pytest.raises(VEError, match="unit status contradicts"):
            check_document(write_report_document(tmp_path, [(text, {**piece, "status": "CHECKED"})], **front))
    # The graph-level status follows the units: an admitted document with an open unit is OPEN.
    graph = {"root": "R", "nodes": [{"name": "R", "label": "report:u1", "unit": "u1",
                                     "ast": ["unary", "reports__says__1", ["const", "article"]]}]}
    result = check_document(write_report_document(tmp_path, [cases[2]], graph=graph, **front))
    assert result["admission"]["admitted"] is True and result["status"] == "OPEN"
    with pytest.raises(VEError, match="meaning of u1"):
        check_document(write_report_document(tmp_path, [(cases[0][0], {**nested, "meaning": "specified"})], **front))


def test_open_lists_mix_declared_and_generated_terms(tmp_path):
    """Loop recheck B: the W2 loader accepted an open list only when it was all
    declared or all generated-shaped, so `["reports__may__1", "genuine"]` with
    `genuine` declared raised "invalid meaning status", though the reports layer
    and Lean accept every name that is declared or generated."""
    text = "According to the stated assessment, alice may be safe.\n"
    front = {"assessments": [A1_RECORD], "open_terms": [GENUINE]}
    piece = reported(MAY, ["hedged", "could", "asserted"], {"open": ["reports__may__1", "genuine"]})
    for order in (["reports__may__1", "genuine"], ["genuine", "reports__may__1"]):
        mixed = {**piece, "meaning": {"open": order}}
        result = check_document(write_report_document(tmp_path, [(text, mixed)], **front))
        assert result["coverage"]["bytes_by_status"] == {"OPEN": len(text.encode())}
    # Still rejected: a name neither declared nor generated-shaped, and a generated-shaped
    # name the document does not generate.
    with pytest.raises(VEError, match="invalid meaning status"):
        check_document(write_report_document(tmp_path, [(text, {**piece, "meaning": {
            "open": ["reports__may__1", "undeclared"]}})], **front))
    with pytest.raises(VEError, match="meaning of u1"):
        check_document(write_report_document(tmp_path, [(text, {**piece, "meaning": {
            "open": ["reports__may__1", "reports__may__2", "genuine"]}})], **front))


def test_report_documents_carry_the_premise_set_line(tmp_path):
    """Fable B: the reports path returned CHECKED from unit statuses alone, with no
    premise_status and no admission.vacuous (7.1 row 4), so a document whose signed
    report atoms are inconsistent reported CHECKED."""
    atom = ["unary", "reports__says__1", ["const", "article"]]
    graph = {"root": "R", "nodes": [{"name": "R", "label": "report:u1", "unit": "u1", "ast": atom}]}
    text = "The article says that alice is safe.\n"
    consistent = check_document(write_report_document(tmp_path, [(text, reported())], graph=graph))
    assert consistent["premises"]["status"] == "model"
    assert consistent["admission"]["vacuous"] is False and consistent["status"] == "CHECKED"
    denied = ("It is not the case that the article says that alice is safe.\n", reported({"negated": report()}))
    inconsistent = check_document(write_report_document(tmp_path, [(text, reported()), denied], graph=graph))
    assert inconsistent["premises"]["status"] == "INCONSISTENT"
    assert inconsistent["admission"]["vacuous"] is True and inconsistent["status"] == "UNVERIFIED"
    # Author assertions are part of Γ: a report beside an asserted contradiction is vacuous too.
    contradiction = ("Alice is not safe.\n", {"kind": "asserted", "meaning": "specified", "support": "assumption",
                                                "content": {"ast": ["and", SAFE, ["not", SAFE]]}})
    vacuous = check_document(write_report_document(tmp_path, [(text, reported()), contradiction], graph=graph))
    assert vacuous["premises"]["status"] == "INCONSISTENT" and vacuous["status"] == "UNVERIFIED"
    # Without a graph the line is still reported.
    assert check_document(write_report_document(tmp_path, [(text, reported()), denied]))["premises"]["status"] \
        == "INCONSISTENT"
