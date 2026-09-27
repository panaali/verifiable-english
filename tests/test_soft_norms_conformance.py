"""Three-way checks against the acceptance fixtures in soft-norms.md §10."""
from __future__ import annotations

import json

import pytest

from ve.ast import formula_to_data
from ve.document import check_document
from ve.softnorms import SoftEnvironment, SoftNormDocument
from ve.soft_route import _run, admit_soft_document
from tests.test_soft_norms_lean import env, norm, should, ranks, values, obligation, permission


def fixtures():
    return [
        ("alpha-high", env(ranks(["a", "b"], "holistic")),
         [should("h", "x_required", True, rank="a"), should("l", "x_required", False, rank="b")],
         [], [True], [True]),
        ("alpha-low", env(ranks(["a", "b"], "holistic")),
         [should("h", "x_required", True, rank="a"), should("l", "x_required", False, rank="b")],
         ["soft__outweighs__b__a__x_permitted"], [False], [True]),
        ("beta", env(), [should("d", "x_required", True), norm("s", "x_permitted", False)],
         [], [False], [False]),
        ("gamma", env(perm="deny"), [should("d", "x_required", True)],
         [], [True], [False]),
        ("delta", env(), [should("a", "x_required", True), should("b", "x_permitted", False)],
         [], [True], [False]),
        ("epsilon", env(ranks(["ra", "rb", "rc", "rd"], "holistic")),
         [should("a", "x_required", True, rank="ra"),
          should("b", "x_required", False, rank="rb"),
          should("c", "x_required", True, rank="rc"),
          should("d", "x_required", False, rank="rd")],
         ["soft__outweighs__rb__ra__x_permitted", "soft__outweighs__rc__rb__x_permitted",
          "soft__outweighs__rd__rc__x_permitted"], [False], [True]),
        ("kappa", env(ranks(["ra", "rb", "rc"]), perm="deny"),
         [should("a", "x_required", True, rank="ra"),
          should("b", "x_permitted", False, rank="rb"),
          should("c", "x_permitted", True, rank="rc")], [], [True], [True]),
        ("lambda", env(ranks(["high", "low"])),
         [norm("s", "x_required", False), should("hi", "x_required", True, rank="high"),
          should("lo", "x_permitted", False, rank="low")], [], [False], [False]),
        ("mu-exception", env({"parties": ["user"], "outranking": {"mode": "strict"}}),
         [norm("h", "x_required", True),
          norm("e", "x_required", False, over=["h"], alterable=["user"])],
         [], [False], [True]),
        ("mu-switched", env({"parties": ["user"], "outranking": {"mode": "strict"}}),
         [norm("h", "x_required", True),
          norm("e", "x_required", False, over=["h"], alterable=["user"])],
         ["soft__off__e__user"], [True], [True]),
        ("upsilon", env(ranks(["high", "low"])),
         [should("m", "x_required", True, rank="high"),
          should("n", "x_required", False, rank="low", over=["m"]),
          should("k", "x_required", False, over=["n"])], [], [False], [True]),
        ("xi", env(), [norm("h", "x_required", True)], [], [True], [True]),
        ("omicron", env(), [should("a", "x_required", True), should("b", "x_required", True)],
         [], [True], [True]),
    ]


@pytest.mark.parametrize("name,raw,rules,decisions,required,permitted", fixtures(),
                         ids=[case[0] for case in fixtures()])
def test_python_lean_spec_fixture(name, raw, rules, decisions, required, permitted):
    soft = SoftNormDocument(SoftEnvironment(raw), rules)
    lean = _run({"id": name, "kind": "soft-elaborate", "environment": raw, "norms": rules})
    assert soft.extended_env.to_dict() == lean["environment_prime"]
    py_layers = [(label, formula_to_data(soft.extended_env, formula, _generated=True))
                 for label, formula in soft.elaborated.premises()]
    lean_layers = [(item["label"], item["ast"]) for item in lean["premises"]]
    assert py_layers == lean_layers
    py_soft = [(label, formula_to_data(soft.extended_env, formula, _generated=True))
               for label, formula in soft.extended_env.soft_premises]
    lean_soft = [(item["label"], item["ast"]) for item in lean["background"]
                 if item["generator"] == "soft"]
    assert py_soft == lean_soft
    python = {"environment_prime": soft.extended_env.to_dict(),
              "premises": [{"label": label, "ast": ast} for label, ast in py_layers]}
    for predicate, expected in (("x_required", required), ("x_permitted", permitted)):
        assert values(python, predicate, decisions) == expected
        assert values(lean, predicate, decisions) == expected


def test_document_check_to_python_route_to_lean(tmp_path):
    raw = env()
    rules = [should("a", "x_required", True), should("b", "x_permitted", False)]
    soft = SoftNormDocument(SoftEnvironment(raw), rules)
    coherence = dict(soft.extended_env.soft_premises)["soft:coherence:a,b"]
    ast = formula_to_data(soft.extended_env, coherence, _generated=True)
    units = [{"id": f"u{i}", "span": [2 * i, 2 * i + 2], "kind": "norm",
              "meaning": "specified", "support": "assumption", "content": rule}
             for i, rule in enumerate(rules)]
    graph = {"root": "leaf", "nodes": [{"name": "leaf", "ast": ast,
                                         "label": "soft:coherence:a,b"}]}
    meta = {"format": "ve-document@1", "environment": raw, "units": units, "graph": graph}
    path = tmp_path / "soft.ve.md"
    path.write_text("---\n" + json.dumps(meta) + "\n---\nA\nB\n")
    checked = check_document(path)
    admission = {"units": [{"id": u["id"], "span": u["span"], "kind": u["kind"],
                             "content": u["content"]} for u in units],
                 "graph": graph, "lemmas": [], "open_terms": [], "reading_sets": [],
                 "narrowings": []}
    python = admit_soft_document(soft.env, admission, soft_document=soft)
    lean = _run({"id": "admission", "kind": "admission", "environment": raw,
                 "document": admission})
    assert checked["admission"]["admitted"] is True
    assert checked["admission"]["conditional_on"] == ["soft:coherence:a,b"]
    assert checked["admission"]["report"] == python["report"] == lean["report"]
    assert checked["admission"]["core_report_id"] == python["report_id"] == lean["report_id"]
    assert checked["premises"]["status"] == "model"


def test_decision_finding_in_asserted_unit(tmp_path):
    raw = env()
    rule = should("a", "x_required", True)
    finding = ["exists", "assistant", ["unary", "soft__excepted__a", ["var", 0]]]
    units = [{"id": "u0", "span": [0, 2], "kind": "norm", "meaning": "specified",
              "support": "assumption", "content": rule},
             {"id": "u1", "span": [2, 4], "kind": "asserted", "meaning": "specified",
              "support": "assumption", "content": {"ast": finding}}]
    graph = {"root": "leaf", "nodes": [{"name": "leaf", "ast": finding, "unit": "u1"}]}
    meta = {"format": "ve-document@1", "environment": raw, "units": units, "graph": graph}
    path = tmp_path / "finding.ve.md"
    path.write_text("---\n" + json.dumps(meta) + "\n---\nA\nB\n")
    checked = check_document(path)
    assert checked["admission"]["admitted"] is True
    assert checked["admission"]["report"]["root"]["ast"] == finding


def test_nu_typed_acts_rho_conditions_and_tau_coherence():
    q = ["unary", "q", ["var", 0]]
    condition = {"decided_by": "assistant", "sufficient": [q],
                 "necessary": [q], "factors": []}
    extra = {"q": {"arguments": ["assistant"], "description": "q"},
             "y_required": obligation("deny", "y_permitted", act="{0} do y to {1}",
                                      args=("assistant", "user")),
             "y_permitted": permission("allow", act="{0} do y to {1}",
                                       args=("assistant", "user"))}
    raw = env(ranks(["h", "l"], "holistic"), extra=extra)
    rules = [should("xh", "x_required", True, rank="h", exception=condition),
             should("xl", "x_required", False, rank="l", exception=condition),
             should("yh", "y_required", True, rank="h"),
             should("yl", "y_required", False, rank="l")]
    soft = SoftNormDocument(SoftEnvironment(raw), rules)
    lean = _run({"id": "nu-rho", "kind": "soft-elaborate", "environment": raw, "norms": rules})
    assert soft.extended_env.to_dict() == lean["environment_prime"]
    assert [(l, formula_to_data(soft.extended_env, f, _generated=True))
            for l, f in soft.extended_env.soft_premises] == [
                (b["label"], b["ast"]) for b in lean["background"] if b["generator"] == "soft"]
    assert {d["name"]: d["arguments"] for d in lean["decisions"] if "outweighs" in d["name"]} == {
        "soft__outweighs__l__h__x_permitted": ["assistant"],
        "soft__outweighs__l__h__y_permitted": ["assistant", "user"]}
    assert [b["label"] for b in lean["background"] if b.get("label", "").startswith("soft:exception:")] == [
        "soft:exception:xh:sufficient:0", "soft:exception:xh:necessary:0",
        "soft:exception:xl:sufficient:0", "soft:exception:xl:necessary:0"]

    raw = env(extra={"q": extra["q"]})
    rules = [should(name, "x_required", sign, exception=condition)
             for name, sign in (("a", True), ("b", False), ("c", False))]
    soft = SoftNormDocument(SoftEnvironment(raw), rules)
    lean = _run({"id": "tau", "kind": "soft-elaborate", "environment": raw, "norms": rules})
    assert [label for label, _ in soft.coherence_premises] == [
        "soft:coherence:a,b", "soft:coherence:a,c"]
    assert [(l, formula_to_data(soft.extended_env, f, _generated=True))
            for l, f in soft.extended_env.soft_premises] == [
                (b["label"], b["ast"]) for b in lean["background"] if b["generator"] == "soft"]


@pytest.mark.parametrize("name,raw,rules,diagnostic", [
    ("pi", env(), [should("a", "x_required", True,
                         exception={"decided_by": None, "sufficient": [],
                                    "necessary": [], "factors": []})],
     "MissingExceptionDecider: rule a"),
    ("sigma-switch", env({"parties": ["user"], "outranking": {"mode": "strict"}}),
     [norm("a", "x_required", True, hard=True, alterable=["user"])],
     "HardConstraintAltered: rule a"),
    ("sigma-default", env(), [should("a", "x_required", True, hard=True)],
     "HardConstraintAltered: rule a"),
    ("theta-tie", env({"ranks": ["a", "b"], "outranks": [["a", "b"]],
                       "ties": [["a", "b"]], "outranking": {"mode": "strict"}}), [],
     "TieAgainstOrder: a, b"),
    ("theta-rank-cycle", env({"ranks": ["a", "b", "c"],
                              "outranks": [["a", "b"], ["b", "c"], ["c", "a"]],
                              "outranking": {"mode": "strict"}}), [],
     "DependencyCycle: a, b, c"),
    ("theta-dual-guard", env(), [norm("s", "x_permitted", False,
                                     guard=("not", ["unary", "x_required", ["var", 0]])),
                                  should("d", "x_required", True)],
     "DependencyCycle: x_permitted, x_required"),
], ids=lambda x: x if type(x) is str else None)
def test_python_lean_spec_diagnostics(name, raw, rules, diagnostic):
    with pytest.raises(Exception, match=diagnostic):
        SoftNormDocument(SoftEnvironment(raw), rules)
    # The Lean input parser's restricted JSON has no null spelling. Omission
    # is the canonical inherited-decider spelling on that side of the route.
    canonical = [{"norm": {**rule["norm"], "exception": {
        k: v for k, v in rule["norm"]["exception"].items() if k != "decided_by" or v is not None}}}
        if type(rule["norm"].get("exception")) is dict else rule for rule in rules]
    with pytest.raises(Exception, match=diagnostic):
        _run({"id": name, "kind": "soft-elaborate", "environment": raw, "norms": canonical})


def test_inherited_null_decider_is_admitted_by_python_route():
    raw = env({"exception_decider": "assistant", "outranking": {"mode": "strict"}})
    rule = should("a", "x_required", True,
                  exception={"decided_by": None, "sufficient": [],
                             "necessary": [], "factors": []})
    soft = SoftNormDocument(SoftEnvironment(raw), [rule])
    assert "decided_by" not in soft.rules[0].to_dict()["norm"]["exception"]
    layer = dict(soft.elaborated.premises())["layer:norms:x_required"]
    ast = formula_to_data(soft.extended_env, layer, _generated=True)
    document = {"units": [{"id": "u", "span": [0, 1], "kind": "norm", "content": rule}],
                "graph": {"root": "leaf", "nodes": [{"name": "leaf", "ast": ast,
                                                      "label": "layer:norms:x_required"}]}}
    assert admit_soft_document(soft.env, document)["admitted"] is True
