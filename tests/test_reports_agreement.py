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
