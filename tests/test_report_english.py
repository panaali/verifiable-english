"""The reports@0 English (attribution.md 2.1 to 2.4): the reviewed wordings, one grammar
for typed and rendered text, every derivation enumerated, bound to a manifest.

Reproducers from the reviews: Fable B (a formula content came back capitalised
mid-sentence, the sentence-initial holder was never capitalised, and `wants` /
`intends` were rendered "wants that S", outside 2.1) and Astra B (parsing compared
the text with an already-supplied object instead of parsing the grammar).
"""
from __future__ import annotations

import copy
import json

import pytest

from ve.environment import Environment
from ve.errors import VEError
from ve.report_english import (parse_rendered_report, parse_report_sentence, render_report_sentence,
                               render_report_unit)
from ve.reports import ReportsDocument

CONTEXTS = [{"id": "c1", "tense": "present", "description": "the constitution"},
            {"id": "c2", "tense": "past", "reference_time": "sept16", "description": "the policy statement"},
            {"id": "c3", "tense": "perfect", "description": "the record"}]
A1 = {"id": "a1", "context": "e1", "decided_by": "unresolved_decider", "necessary": [], "sufficient": [],
      "factors": ["review status"], "precedents": [], "jurisdiction": "news_desk", "version": 1}


def environment(**extra_constants):
    constants = {"anthropic": {"sort": "organisation", "description": "Anthropic", "verbalisation": "Anthropic"},
                 "article": {"sort": "text", "description": "the article", "verbalisation": "the article"},
                 "claude": {"sort": "model", "description": "Claude"},
                 "service": {"sort": "system", "description": "service"},
                 "e1": {"sort": "evidence", "description": "e1"}}
    constants.update(extra_constants)
    return Environment({
        "language": "ve.core@0.2", "profiles": ["relational-fol@0", "reports@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {
            "reports": {"holders": ["organisation", "text"], "evidence": "evidence"},
            "sorts": {s: {"description": s} for s in ("organisation", "text", "model", "system", "evidence")},
            "predicates": {"helpful": {"arguments": ["model"], "description": "helpful"},
                           "safe": {"arguments": ["system"], "description": "safe"},
                           "audits": {"arguments": ["organisation", "system"], "description": "audits"},
                           "publishes": {"arguments": ["organisation", "system"], "description": "publishes",
                                         "verbalisation": "{0} publishes {1}"}},
            "constants": constants}})


def U(p, c):
    return {"ast": ["unary", p, ["const", c]]}


def B(p, a, b):
    return {"ast": ["binary", p, ["const", a], ["const", b]]}


def report(holder, act, context, content, literal=None):
    return {"report": {"holder": holder, "act": act, "context": context, "literal": literal, "content": content}}


def assess(judgment, content):
    return {"assessment": {"judgment": judgment, "record": "a1", "content": content}}


SAFE = U("safe", "service")
NOT_SAFE = {"ast": ["not", SAFE["ast"]]}
BELIEF = report("anthropic", "believes", "c1", U("helpful", "claude"))


def kind_of(content):
    tag, value = next(iter(content.items()))
    if tag == "negated":
        return kind_of(value)
    if tag == "report":
        return ["attributed", value["holder"], value["act"], kind_of(value["content"])]
    if tag == "assessment":
        return ["hedged", "could" if value["judgment"] == "may" else "likely", kind_of(value["content"])]
    return "asserted"


def document(*contents, env=None):
    """3.3: a unit with an assessment node is `open`, listing generated names (here
    every generated assessment name of the document)."""
    from test_reports_lean import assessment_nodes
    units = [{"id": f"u{i}", "span": [i, i + 1], "kind": kind_of(c), "meaning": "specified",
              "support": "testimony", "content": c} for i, c in enumerate(contents, 1)]
    keys = {(n["judgment"], n["record"], json.dumps(n["content"], sort_keys=True))
            for u in units for n in assessment_nodes(u["content"])}
    generated = [f"reports__{j}__{k}" for j in ("may", "probably")
                 for k in range(1, 1 + sum(key[0] == j for key in keys))]
    for u in units:
        if assessment_nodes(u["content"]):
            u["meaning"] = {"open": generated}
    return ReportsDocument(env or environment(), CONTEXTS, [A1], units)


ROWS = [
    (report("article", "says", "c1", SAFE), "The article says that service is safe."),
    (report("article", "says", "c2", SAFE), "The article said that service is safe."),
    (report("anthropic", "believes", "c2", U("helpful", "claude")), "Anthropic believed that claude is helpful."),
    (report("anthropic", "believes", "c3", U("helpful", "claude")), "Anthropic has believed that claude is helpful."),
    (report("anthropic", "wants", "c1", B("publishes", "anthropic", "service")), "Anthropic wants to publish service."),
    (report("article", "wants", "c1", B("audits", "anthropic", "service")),
     "The article wants anthropic to audit service."),
    (report("anthropic", "intends", "c2", B("audits", "anthropic", "service")), "Anthropic intended to audit service."),
    (report("anthropic", "believes", "c1", NOT_SAFE), "Anthropic believes that it is not the case that service is safe."),
    ({"negated": report("anthropic", "believes", "c1", SAFE)},
     "It is not the case that Anthropic believes that service is safe."),
    (report("article", "says", "c1", BELIEF), "The article says that Anthropic believes that claude is helpful."),
    (report("article", "says", "c1", {"negated": BELIEF}),
     "The article says that it is not the case that Anthropic believes that claude is helpful."),
    (report("article", "says", "c2", SAFE, literal="Service is safe."), 'The article said, "Service is safe.".'),
    (assess("may", SAFE), "According to the stated assessment, service may be safe."),
    (assess("probably", SAFE), "According to the stated assessment, service is probably safe."),
    (assess("may", NOT_SAFE),
     "According to the stated assessment, it may be that it is not the case that service is safe."),
    ({"negated": assess("may", SAFE)},
     "It is not the case that, according to the stated assessment, service may be safe."),
    (assess("probably", B("audits", "anthropic", "service")),
     "According to the stated assessment, it is probably the case that anthropic audits service."),
    (report("article", "says", "c1", assess("may", SAFE)),
     "The article says that according to the stated assessment, service may be safe."),
]


@pytest.mark.parametrize("content, text", ROWS, ids=[t for _, t in ROWS])
def test_every_wording_row_round_trips(content, text):
    doc = document(content)
    rendered = render_report_unit(doc, "u1")
    assert rendered["text"] == text
    parsed = parse_rendered_report(doc, rendered)
    assert doc.meaning_id(parsed) == doc.meaning_id(content)
    # Typed text passes through the same grammar: print(parse(s)) = s.
    assert render_report_sentence(doc, parse_report_sentence(doc, text, rendered["manifest"]))[0] == text


def test_synonyms_parse_to_the_canonical_wording():
    doc = document(report("article", "says", "c1", SAFE), assess("probably", SAFE))
    says = render_report_unit(doc, "u1")
    typed = parse_report_sentence(doc, "The article states that service is safe.", says["manifest"])
    assert doc.meaning_id(typed) == says["meaning_id"]
    probably = render_report_unit(doc, "u2")
    for text in ("According to the stated assessment, it is likely that service is safe.",
                 "According to the stated assessment, it is probably the case that service is safe."):
        assert doc.meaning_id(parse_report_sentence(doc, text, probably["manifest"])) == probably["meaning_id"]
    assert parse_report_sentence(doc, "The article stated that service is safe.",
                                 dict(says["manifest"], contexts=[CONTEXTS[1]]))["report"]["context"] == "c2"


def test_parsing_reads_the_grammar_not_a_supplied_object():
    """A sentence that no unit carries parses under a manifest of the document."""
    doc = document(report("article", "says", "c1", SAFE))
    manifest = render_report_unit(doc, "u1")["manifest"]
    node = parse_report_sentence(doc, "The article says that Anthropic believes that claude is helpful.",
                                 dict(manifest, contexts=[CONTEXTS[0], CONTEXTS[0]]))
    assert node == report("article", "says", "c1", report("anthropic", "believes", "c1", U("helpful", "claude")))


@pytest.mark.parametrize("text, message", [
    ("The article thinks that service is safe.", "thinks that"),
    ("The article claims that service is safe.", "claims that"),
    ("Anthropic plans to audit service.", "plans to"),
    ("Anthropic should audit service.", "should"),
    ("According to the stated assessment, service may not be safe.", "may not"),
    ("According to the stated assessment, service is probably not safe.", "probably not"),
    ("According to Anthropic, service is safe.", "labelled unit"),
    ("Anthropic believes that service is safe and the article says that service is safe.", "separate units"),
    ("Anthropic wants that service is safe.", "no reports wording"),
    ("Service is safe.", "no reports wording"),
])
def test_rejected_wordings_name_their_reason(text, message):
    doc = document(report("article", "says", "c1", SAFE))
    with pytest.raises(VEError, match=message):
        parse_report_sentence(doc, text, render_report_unit(doc, "u1")["manifest"])


def test_wordings_outside_the_table_are_not_printed():
    for bad in (report("anthropic", "intends", "c1", SAFE),  # an intention's subject is the holder
                report("anthropic", "wants", "c1", NOT_SAFE),  # no infinitival form
                report("anthropic", "believes", "c1", SAFE, literal="Service is safe.")):
        with pytest.raises(VEError, match="No reviewed wording"):
            render_report_unit(document(bad), "u1")


def test_manifest_mismatch():
    doc = document(report("article", "says", "c1", SAFE), assess("may", SAFE))
    rendered = render_report_unit(doc, "u1")
    past = ReportsDocument(environment(), [dict(CONTEXTS[0], tense="past")] + CONTEXTS[1:], [A1],
                           [{"id": "u1", "span": [1, 2], "kind": kind_of(ROWS[0][0]),
                             "meaning": "specified", "support": "testimony", "content": ROWS[0][0]}])
    with pytest.raises(VEError, match="ManifestMismatch"):
        parse_rendered_report(past, rendered)
    with pytest.raises(VEError, match="ManifestMismatch"):
        parse_rendered_report(doc, dict(rendered, manifest=dict(rendered["manifest"], environment_id="x")))
    with pytest.raises(VEError, match="ManifestMismatch"):
        parse_rendered_report(doc, dict(rendered, manifest=dict(rendered["manifest"], contexts=[CONTEXTS[1]])))
    with pytest.raises(VEError, match="ManifestMismatch"):
        parse_rendered_report(doc, dict(rendered, manifest=dict(rendered["manifest"], contexts=[])))
    assessed = render_report_unit(doc, "u2")
    changed = copy.deepcopy(assessed)
    changed["manifest"]["assessments"][0]["version"] = 2
    with pytest.raises(VEError, match="ManifestMismatch"):
        parse_rendered_report(doc, changed)
    with pytest.raises(VEError, match="ManifestMismatch"):
        parse_rendered_report(doc, dict(rendered, text="The article said that service is safe."))


def test_literal_manifest_binds_the_quoted_content_records():
    """Loop recheck B: a literal quotation's manifest stored its content without
    the context and assessment records inside it, so after the record changed the
    original text and manifest still parsed, to content with a different meaning,
    instead of ``ManifestMismatch`` (2.4)."""
    assessed = report("article", "says", "c2", assess("may", SAFE), literal="Service may be safe.")
    doc = document(assessed)
    rendered = render_report_unit(doc, "u1")
    assert rendered["text"] == 'The article said, "Service may be safe.".'
    assert rendered["manifest"]["contexts"] == [CONTEXTS[1]] and rendered["manifest"]["assessments"] == [A1]
    assert parse_rendered_report(doc, rendered) == assessed
    changed = ReportsDocument(environment(), CONTEXTS, [dict(A1, version=2)], [
        {"id": "u1", "span": [1, 2], "kind": kind_of(assessed), "meaning": {"open": ["reports__may__1"]},
         "support": "testimony", "content": assessed}])
    assert changed.meaning_id(assessed) != doc.meaning_id(assessed)
    with pytest.raises(VEError, match="ManifestMismatch"):
        parse_report_sentence(changed, rendered["text"], rendered["manifest"])
    with pytest.raises(VEError, match="ManifestMismatch"):
        parse_rendered_report(changed, rendered)
    # A manifest without the quoted content's record, or with another in its place.
    with pytest.raises(VEError, match="ManifestMismatch"):
        parse_rendered_report(doc, dict(rendered, manifest=dict(rendered["manifest"], assessments=[])))
    # The same class for a context inside the quotation: the verb's context is c2, the quoted belief's c1.
    quoted_belief = report("article", "says", "c2", BELIEF, literal="Anthropic believes it.")
    doc = document(quoted_belief)
    rendered = render_report_unit(doc, "u1")
    assert rendered["manifest"]["contexts"] == [CONTEXTS[1], CONTEXTS[0]]
    assert parse_rendered_report(doc, rendered) == quoted_belief
    past = ReportsDocument(environment(), [dict(CONTEXTS[0], tense="past")] + CONTEXTS[1:], [A1], [
        {"id": "u1", "span": [1, 2], "kind": kind_of(quoted_belief), "meaning": "specified",
         "support": "testimony", "content": quoted_belief}])
    assert past.meaning_id(quoted_belief) != doc.meaning_id(quoted_belief)
    with pytest.raises(VEError, match="ManifestMismatch"):
        parse_rendered_report(past, rendered)
    with pytest.raises(VEError, match="ManifestMismatch"):
        parse_rendered_report(doc, dict(rendered, manifest=dict(rendered["manifest"], contexts=[CONTEXTS[1]])))


def test_literal_manifest_content_is_decoded():
    """Loop recheck B: the manifest's literal content was returned without the
    content decoder, so `{"ast": ["unary", "undeclared", ...]}` in its place parsed
    (`meaning_id` rejected it only afterwards), as did a quoted report by an unknown
    holder and a quoted assessment with an invalid judgment."""
    quoted = report("article", "says", "c2", SAFE, literal="Service is safe.")
    doc = document(quoted)
    rendered = render_report_unit(doc, "u1")
    text, manifest = rendered["text"], rendered["manifest"]
    assert parse_report_sentence(doc, text, manifest) == quoted

    def parse_with(literal, **records):
        return parse_report_sentence(doc, text, dict(manifest, literals=[literal], **records))

    with pytest.raises(VEError, match="undeclared"):
        parse_with({"ast": ["unary", "undeclared", ["const", "service"]]})
    for bad in ({"ast": ["unary", "safe", ["const", "claude"]]},  # ill-sorted
                {"ast": ["unary", "safe", ["var", 0]]}, None, [], "safe", {"ast": SAFE["ast"], "x": 1},
                {"norm": {}}, {"fence": "u1"}, {"negated": SAFE}):
        with pytest.raises(VEError):
            parse_with(bad)
    # Quoted reports and assessments whose records match the manifest but whose own
    # fields are not content of this document.
    contexts = [CONTEXTS[1], CONTEXTS[0]]
    for bad in (report("nobody", "believes", "c1", SAFE), report("claude", "believes", "c1", SAFE),
                report("anthropic", "pledges", "c1", SAFE),
                report("anthropic", "believes", "c1", {"ast": ["unary", "undeclared", ["const", "service"]]}),
                report("anthropic", "believes", "c1", SAFE, literal=""),
                {"report": {"holder": "anthropic", "act": "believes", "context": "c1", "content": SAFE, "x": 1}},
                {"report": "anthropic"}):
        with pytest.raises(VEError):
            parse_with(bad, contexts=contexts)
    for bad in (assess("certainly", SAFE), assess("may", {"ast": ["unary", "undeclared", ["const", "service"]]}),
                {"assessment": {"judgment": "may", "record": "a1"}}):
        with pytest.raises(VEError):
            parse_with(bad, assessments=[A1])
    # The depth bound of the content decoder holds for manifest-supplied content too.
    deep = SAFE
    for _ in range(16):
        deep = report("anthropic", "believes", "c1", deep)
    with pytest.raises(VEError, match="depth"):
        parse_with(deep, contexts=[CONTEXTS[1]] + [CONTEXTS[0]] * 16)
    # Valid quoted content still binds, and a malformed literals list is a mismatch.
    assert parse_with(BELIEF, contexts=contexts)["report"]["content"] == BELIEF
    for literals in ({"0": SAFE}, "x", 1):
        with pytest.raises(VEError, match="ManifestMismatch"):
            parse_report_sentence(doc, text, dict(manifest, literals=literals))


def test_two_derivations_are_rejected():
    """Two holders displayed alike: the sentence has two readings, so it is neither
    printed nor parsed."""
    env = environment(anthropic_labs={"sort": "organisation", "description": "Labs", "verbalisation": "Anthropic"})
    doc = document(report("anthropic", "says", "c1", SAFE), env=env)
    with pytest.raises(VEError, match="one-reading"):
        render_report_unit(doc, "u1")
    manifest = {"environment_id": env.environment_id, "profiles": list(env.profiles), "choices": [],
                "contexts": [CONTEXTS[0]], "assessments": [], "literals": []}
    with pytest.raises(VEError, match="2 readings"):
        parse_report_sentence(doc, "Anthropic says that service is safe.", manifest)
