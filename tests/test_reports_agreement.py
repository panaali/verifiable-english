"""Python and Lean agree on what a reports@0 document is, not only on what it elaborates to.

Each case is a reproducer from the attribution reviews (Astra, Fable), kept as a
class: the Python production layer (`ve/reports.py`) and the Lean route
(`ve_reports_route`) accept exactly the same documents, reject the rest with the
same section-8 diagnostic kind, and bind the same envelope when they accept.
"""
from __future__ import annotations

import copy

import pytest

from ve.environment import Environment
from ve.errors import VEError
from ve.reports import ReportsDocument

from test_reports_lean import (A1, CONTEXTS, E0, LANGUAGE, REVISION, U, assess, ast, doc, lean, neg,  # noqa: F401
                               report, run)

KEYS = ("environment_reports_id", "keys", "premises", "open_terms", "bridge_formulas",
        "content_ids", "envelope", "warnings")


def python(d, env):
    try:
        return ReportsDocument(Environment(env), d.get("contexts", []), d.get("assessments", []), d["units"],
                               bridges=d.get("bridges", []), scoped=d.get("scoped", []),
                               open_terms=d.get("open_terms", [])).elaborated()
    except VEError as exc:
        return exc


def diagnostic(text):
    return str(text).split(":")[0]


def agree(cases):
    """Every case: (document, environment, expected diagnostic kind, "shape", or None to accept)."""
    results = run([{"id": str(i), "kind": "reports-elaborate", "environment": env, "document": d}
                   for i, (d, env, _) in enumerate(cases)])
    for (d, env, expected), result in zip(cases, results, strict=True):
        py = python(d, env)
        if expected is None:
            assert result["status"] == "ok", result
            assert not isinstance(py, Exception), py
            assert {k: py[k] for k in KEYS} == {k: result[k] for k in KEYS}
        else:
            assert result["status"] == "error", (expected, result)
            assert isinstance(py, Exception), (expected, py)
            if expected != "shape":  # decoder shape errors are rejections with no section-8 text
                assert diagnostic(result["error"]) == diagnostic(py) == expected, (result["error"], str(py))


def definition_env():
    return {"language": LANGUAGE, "profiles": ["definitions@0", "relational-fol@0"], "spec_revision": REVISION,
            "vocabulary": {"sorts": {"system": {"description": "system"}},
                           "predicates": {"reviewed": {"arguments": ["system"], "description": "reviewed"},
                                          "safe": {"arguments": ["system"], "description": "safe",
                                                   "defined": {"arguments": ["system"],
                                                               "body": ["unary", "reviewed", ["var", 0]]}}},
                           "constants": {"service": {"sort": "system", "description": "service"}}}}


def package_doc(**extra):
    package = {"definition": {"environment": definition_env(), "content": ast(U("reviewed", "service"))}}
    d = doc(report("the_article", "says", "c3", package), report("the_article", "says", "c3", ast(U("safe", "service"))),
            **extra)
    d["units"][0]["kind"] = ["attributed", "the_article", "says", "definition"]
    return d


def norm_doc(**extra):
    quote_env = copy.deepcopy(E0())
    quote_env["profiles"] = ["norms@0", "relational-fol@0"]
    del quote_env["vocabulary"]["reports"]
    d = doc(report("the_article", "says", "c3", {"norm": {"environment": quote_env, "norms": []}}), **extra)
    d["units"][0]["kind"] = ["attributed", "the_article", "says", "norm"]
    return d


def bridge(unit, path=None, **extra):
    return {"id": "b1", "unit": unit, **({"path": path} if path else {}), "accepted_by": "reviewer_ann",
            "reason": [], **extra}


def test_bridge_and_scoped_targets_agree(lean):
    """Fable B4: Python descended into a quoted package's statement and elaborated it
    over E, emitting a bridge formula that Lean rejects (BridgeKindMismatch)."""
    belief = report("anthropic", "believes", "c1", ast(U("helpful", "claude")))
    plain = {"id": "u9", "span": [40, 41], "kind": "asserted", "meaning": "specified", "support": "assumption",
             "content": ast(U("safe", "service"))}
    with_w2 = doc(report("the_article", "says", "c3", belief))
    with_w2["units"].append(plain)
    agree([
        (package_doc(bridges=[bridge("u1", "1")]), E0(), "BridgeKindMismatch"),
        (package_doc(bridges=[bridge("u1")]), E0(), "BridgeKindMismatch"),
        (norm_doc(bridges=[bridge("u1")]), E0(), "BridgeKindMismatch"),
        (package_doc(bridges=[bridge("u1", "1.1")]), E0(), "BridgeTarget"),
        (dict(with_w2, bridges=[bridge("u9")]), E0(), "BridgeTarget"),
        (dict(with_w2, bridges=[bridge("u1", "1", note="x")]), E0(), "shape"),
        (dict(with_w2, bridges=[bridge("u1", "1")]), E0(), None),
        (package_doc(scoped=[{"id": "s1", "payloads": [{"unit": "u1", "path": "1"}, "u2"],
                              "conclusion": ast(U("safe", "service"))}]), E0(), "ScopedEnvironment"),
        (package_doc(scoped=[{"id": "s1", "payloads": ["u1"], "conclusion": ast(U("safe", "service"))}]),
         E0(), "ScopedTarget"),
        (dict(with_w2, scoped=[{"id": "s1", "payloads": ["u9"], "conclusion": ast(U("safe", "service"))}]),
         E0(), "ScopedTarget"),
        (dict(with_w2, scoped=[{"id": "s1", "payloads": [], "conclusion": ast(U("safe", "service"))}]),
         E0(), "ScopedEnvironment"),
        (package_doc(scoped=[{"id": "s1", "payloads": ["u2"], "conclusion": ast(U("human", "claude"))}]),
         E0(), None),
        (package_doc(scoped=[{"id": "s1", "payloads": [{"unit": "u1", "path": "1"}],
                              "conclusion": ast(U("human", "claude"))}]), E0(), "ScopedEnvironment"),
        (package_doc(scoped=[{"id": "s1", "payloads": [{"unit": "u1", "path": "1"}],
                              "conclusion": ast(U("safe", "service"))}]), E0(), None),
    ])


def many_predicates(n):
    env = E0()
    for i in range(n - len(env["vocabulary"]["predicates"])):
        env["vocabulary"]["predicates"][f"p{i}"] = {"arguments": ["system"], "description": f"p{i}"}
    return env


def verbalised(words):
    env = E0()
    env["vocabulary"]["constants"]["anthropic"]["verbalisation"] = words
    return env


def test_well_formedness_boundaries_agree(lean):
    """Astra B: 256 author predicates plus one generated predicate was Lean `ok` and
    Python MAX_PREDICATES, so `WellFormedReports` missed 4.1 step 7. The class: every
    4.1 boundary is decided alike on both sides."""
    safe = ast(U("safe", "service"))
    says = report("the_article", "says", "c3", safe)
    a2 = dict(A1, id="a2")

    def with_context(**fields):
        return doc(says, contexts=[dict(CONTEXTS[2], **fields)])

    def with_record(**fields):
        record = {k: v for k, v in dict(A1, **fields).items() if v is not None}
        return doc(assess("may", safe), assessments=[record])

    deep = safe
    for _ in range(16):
        deep = report("the_article", "says", "c3", deep)
    kind_mismatch = doc(says)
    kind_mismatch["units"][0]["kind"] = ["attributed", "anthropic", "says", "asserted"]
    clash = doc(says)
    clash["units"].append({"id": "u1", "span": [5, 6], "kind": "asserted", "content": safe})
    agree([
        (doc(says), many_predicates(256), "ResourceLimit"),
        (doc(says), many_predicates(255), None),
        (doc(says, report("anthropic", "believes", "c1", safe)), many_predicates(255), "ResourceLimit"),
        (doc(report("the_article", "promised", "c3", safe)), E0(), "UnsupportedAct"),
        (doc(says), verbalised("the stated assessment"), "InvalidInput"),
        (doc(says), verbalised("The Stated Assessment"), "InvalidInput"),
        (doc(says), verbalised("the stated assessments"), None),
        (with_context(description=""), E0(), "InvalidInput"),
        (with_context(description="x" * 201), E0(), "ResourceLimit"),
        (with_context(reference_time="not a token"), E0(), "shape"),
        (with_context(tense="future"), E0(), "ContextTense"),
        (doc(says, contexts=CONTEXTS + [CONTEXTS[0]]), E0(), "DuplicateDeclaration"),
        (with_record(version=0), E0(), "InvalidInput"),
        (with_record(context="anthropic"), E0(), "UnknownSymbol"),
        (with_record(decided_by=None), E0(), "InvalidInput"),
        (with_record(necessary=[U("safe", "anthropic")]), E0(), "shape"),
        (with_record(jurisdiction="news desk"), E0(), "InvalidInput"),
        (with_record(factors=[""]), E0(), "InvalidInput"),
        (with_record(precedents=[""]), E0(), "InvalidInput"),
        (doc(assess("may", safe), assessments=[A1, A1]), E0(), "DuplicateDeclaration"),
        (doc(assess("may", safe, record="a9")), E0(), "UnknownAssessment"),
        (doc(assess("maybe", safe)), E0(), "shape"),
        (doc(assess("may", safe), assessments=[A1, a2]), E0(), None),
        (doc(report("service", "says", "c3", safe)), E0(), "HolderSort"),
        (doc(report("nobody", "says", "c3", safe)), E0(), "UnknownHolder"),
        (doc(report("the_article", "says", "c9", safe)), E0(), "UnknownContext"),
        (doc(report("the_article", "says", "c3", safe, literal="")), E0(), "InvalidInput"),
        (doc(report("the_article", "says", "c3", safe, literal="w" * 4097)), E0(), "ResourceLimit"),
        (doc(report("the_article", "says", "c3", safe, literal="w" * 4096)), E0(), None),
        (doc(report("the_article", "says", "c3", neg(safe))), E0(), "InvalidInput"),
        (doc(neg(neg(says))), E0(), "InvalidInput"),
        (doc(deep), E0(), "shape"),
        (kind_mismatch, E0(), "KindMismatch"),
        (clash, E0(), "shape"),
        (doc(says, bridges=[bridge("u1"), bridge("u1")]), E0(), "DuplicateDeclaration"),
        (doc(says, scoped=[{"id": "s1", "payloads": ["u1"], "conclusion": safe}] * 2), E0(), "DuplicateDeclaration"),
    ])


def test_w2_metadata_is_checked_and_bound_into_the_document(lean):
    """Astra B: spans, meaning and support were outside `document_id`, and the Lean
    wire accepted any meaning or support: a changed span, a nonexistent open term and
    a bogus support returned `ok` with the same envelope."""
    safe = ast(U("safe", "service"))
    says = report("the_article", "says", "c3", safe)
    may = assess("may", safe)
    base = doc(says, may, open_terms=["genuine"])

    def edited(index, **fields):
        d = copy.deepcopy(base)
        d["units"][index].update(fields)
        return d

    no_support = copy.deepcopy(base)
    del no_support["units"][0]["support"]
    plain = copy.deepcopy(base)
    plain["units"].append({"id": "u3", "span": [9, 10], "kind": "asserted", "content": safe})
    moved_plain = copy.deepcopy(plain)
    moved_plain["units"][2]["span"] = [9, 11]
    cases = [
        (base, E0(), None),
        (edited(0, meaning={"open": ["nonexistent"]}), E0(), "InvalidInput"),
        (edited(0, support="bogus"), E0(), "InvalidInput"),
        (edited(1, meaning="specified"), E0(), "InvalidInput"),
        (edited(1, meaning={"open": ["genuine"]}), E0(), "InvalidInput"),
        (edited(0, meaning={"contextual": "the desk"}), E0(), "InvalidInput"),
        (edited(0, meaning={"unformalised": "causation"}), E0(), "InvalidInput"),
        (edited(0, meaning={"open": []}), E0(), "InvalidInput"),
        (no_support, E0(), "shape"),
        (edited(0, span=[0, 2]), E0(), None),
        (edited(0, meaning={"open": ["genuine"]}), E0(), None),
        (edited(0, support="assumption"), E0(), None),
        (edited(1, meaning={"open": ["reports__may__1", "genuine"]}), E0(), None),
        (plain, E0(), None),
        (moved_plain, E0(), None),
    ]
    agree(cases)
    accepted = [d for d, _, expected in cases if expected is None]
    envelopes = [r["envelope"]["document_id"] for r in
                 run([{"id": str(i), "kind": "reports-elaborate", "environment": E0(), "document": d}
                      for i, d in enumerate(accepted)])]
    assert len(set(envelopes)) == len(accepted)
