"""order@0: frozen syntax/identity, evaluation, search, Farkas certificates, English, Lean."""
from __future__ import annotations

import copy
import json
import random
import subprocess

import pytest

from conformance import order as corpus
from conformance.order import environment
from test_lean_conformance import lean_executable  # noqa: F401  (fixture)
from ve import (FiniteModel, evaluate, find_countermodel, meaning_id, parse, parse_english,
                print_document, prove_entailment, check_entailment_certificate)
from ve.ast import (Add, Bottom, Const, Document, Eq, Forall, Le, Lt, Not, Num, Scale, Top, Unary,
                    check_formula, document_from_data, formula_from_data, formula_to_data)
from ve.english import render_english
from ve.entailment import _binding
from ve.environment import Environment
from ve.errors import (ResourceLimit, SyntaxError, TypeMismatch, UnknownSymbol, UnsupportedProfile,
                       VEError)
from ve.search import check_countermodel
from ve.wire import digest

ENV = environment()
N, M, ONE = Const("n"), Const("m"), Num(1)


def order_data(**vocabulary):
    data = copy.deepcopy(ENV.to_dict())
    data["vocabulary"].update(vocabulary)
    return data


# ------------------------------------------------------------- profile gate

def test_order_profile_and_identity_domain():
    assert ENV.order and not ENV.closure
    assert ENV.identity_version == "v0.1-order"
    assert ENV.to_dict()["profiles"] == ["order@0", "relational-fol@0"]


@pytest.mark.parametrize("profiles,revision", [
    (["closure@0", "order@0", "relational-fol@0"], "ve-v0.1-order-2026-09-22"),
    (["order@0", "closure@0", "relational-fol@0"], "ve-v0.1-order-2026-09-22"),
    (["relational-fol@0", "order@0"], "ve-v0.1-order-2026-09-22"),
    (["order@0", "relational-fol@0"], "ve-v0.1-order-2026-09-21"),
    (["order@0", "relational-fol@0"], "ve-v0.1-closure-2026-09-21"),
])
def test_profile_gate_rejects_other_lists(profiles, revision):
    data = ENV.to_dict()
    data.update(profiles=profiles, spec_revision=revision)
    with pytest.raises(UnsupportedProfile):
        Environment(data)


def test_int_sort_is_reserved():
    # `$int` is not an identifier: it cannot be declared, enumerated or quantified.
    with pytest.raises(VEError):
        Environment(order_data(sorts={"$int": {"description": "x"}, "item": {"description": "I"}}))
    with pytest.raises(UnknownSymbol):
        formula_from_data(ENV, ["forall", "$int", ["top"]])
    with pytest.raises(VEError):
        parse(ENV, "for every $int x0, (true).\n")
    # Outside order@0, `$int` is an undeclared sort and arithmetic is unsupported.
    v0 = {"language": "ve.core@0", "profile": "relational-fol@0", "spec_revision": "ve-v0-draft-2026-09-20",
          "vocabulary": {"sorts": {"item": {"description": "I"}},
                         "predicates": {"marked": {"arguments": ["$int"], "description": "M"}},
                         "constants": {}}}
    with pytest.raises(UnknownSymbol):
        Environment(v0)
    v0["vocabulary"]["predicates"] = {}
    with pytest.raises(UnsupportedProfile):
        formula_from_data(Environment(v0), ["lt", ["num", "1"], ["num", "2"]])
    # A domain for `$int` is never accepted in a model.
    model = FiniteModel.from_dict(ENV, _model()).to_dict()
    model["domains"]["$int"] = ["0"]
    with pytest.raises(VEError):
        FiniteModel.from_dict(ENV, model)


def test_typing_separates_objects_and_integers():
    for data in (["lt", ["const", "a"], ["num", "1"]], ["eq", ["const", "a"], ["const", "n"]],
                 ["unary", "marked", ["const", "a"]], ["binary", "value", ["const", "n"], ["const", "n"]],
                 ["lt", ["add", ["const", "a"], ["num", "1"]], ["num", "1"]],
                 ["forall", "item", ["lt", ["var", 0], ["num", "1"]]]):
        with pytest.raises(TypeMismatch):
            formula_from_data(ENV, data)


# ------------------------------------------------------ frozen canonical forms

FROZEN = {
    "[@n - 1] < -5.\n": (["lt", ["add", ["const", "n"], ["scale", "-1", ["num", "1"]]], ["num", "-5"]],
                         "c1bbf05d9931574fed374339a87f000e60ab8a267a2965a8df542359df75a35e"),
    "-@n <= [3 * @m].\n": (["le", ["scale", "-1", ["const", "n"]], ["scale", "3", ["const", "m"]]],
                           "4e1e1e5882638997bc7ec2df4c97d0c9a0e34543a0d3c1ab2d871e857dd09cc6"),
    "[1 + @n] is marked.\n": (["unary", "marked", ["add", ["num", "1"], ["const", "n"]]],
                              "d4efcd7935adbbf92ed321058c3c6b77fcc7c3db37ae81c74ef233997cae9ddc"),
    "for every item x0, (x0 value 0).\n": (["forall", "item", ["binary", "value", ["var", 0], ["num", "0"]]],
                                           "efd4a72ba9e9d13d1a10e728617b6a4a476fc2e0e10fb3a6fa04119e8a4ef2c6"),
}


def test_frozen_meaning_ids():
    assert ENV.environment_id == "7e80b4aecc1ca536da333085c1745ff4e4b9ecc3e0da0b645663e19e8b221419"
    for source, (data, identity) in FROZEN.items():
        formula = parse(ENV, source).formulas[0]
        assert formula_to_data(ENV, formula) == data
        assert meaning_id(ENV, formula) == identity
        assert print_document(ENV, Document((formula,))) == source


def test_sugar_is_frozen_not_normalised():
    # t - u is Add(t, Scale(-1, u)); -t is Scale(-1, t); -5 is a numeral.
    assert parse(ENV, "[@n - @m] < 0.\n").formulas[0] == Lt(Add(N, Scale(-1, M)), Num(0))
    assert parse(ENV, "[@n + -@m] < 0.\n").formulas[0] == Lt(Add(N, Scale(-1, M)), Num(0))
    assert parse(ENV, "-5 < -@n.\n").formulas[0] == Lt(Num(-5), Scale(-1, N))
    assert parse(ENV, "[-1 * 5] < 0.\n").formulas[0] == Lt(Scale(-1, Num(5)), Num(0))
    # Commuted or regrouped terms are different ASTs with different identities.
    a, b = Lt(Add(N, ONE), M), Lt(Add(ONE, N), M)
    assert meaning_id(ENV, a) != meaning_id(ENV, b)
    assert print_document(ENV, Document((a,))) == "[@n + 1] < @m.\n"


@pytest.mark.parametrize("text", ["007", "-0", "+5", "1.0", "", "--1", "1e3", "0x1"])
def test_non_canonical_numerals_rejected(text):
    with pytest.raises(VEError):
        formula_from_data(ENV, ["lt", ["num", text], ["num", "0"]])


def test_numeral_wire_values_are_strings_and_bounded():
    with pytest.raises(VEError):
        formula_from_data(ENV, ["lt", ["num", 5], ["num", "0"]])
    with pytest.raises(ResourceLimit):
        formula_from_data(ENV, ["lt", ["num", "1" * 41], ["num", "0"]])
    big = "9" * 40
    assert formula_from_data(ENV, ["lt", ["num", big], ["num", "0"]]).left == Num(int(big))
    for source in ("007 < 1.\n", "-0 < 1.\n", "[@n + 1 + 2] < 1.\n", "[@n * 2] < 1.\n", "@n < @a.\n"):
        with pytest.raises(VEError):
            parse(ENV, source)


def test_random_print_parse_roundtrip():
    rng = random.Random(7)
    for _ in range(400):
        formula = corpus.formula(rng, rng.randint(0, 3))
        text = print_document(ENV, Document((formula,)))
        assert parse(ENV, text).formulas[0] == formula
        assert formula_from_data(ENV, formula_to_data(ENV, formula)) == formula


# ------------------------------------------------------ evaluation and search

def _model():
    return {"complete": True, "domains": {"item": ["i1", "i2"]},
            "constants": {"n": "-7", "m": "3", "k": "0", "a": "i1", "b": "i2"},
            "relations": {"p": [["i1"]], "marked": [["3"]], "value": [["i1", "-7"], ["i2", "3"]],
                          "bounded": []}}


def test_evaluation_with_actual_integers():
    model = FiniteModel.from_dict(ENV, _model())
    assert model.to_dict()["constants"]["n"] == "-7"
    truths = ["@n < 0.\n", "[@n + 10] is marked.\n", "for every item x0, (there exists item x1, (x1 value [@m + [@n - @n]])).\n",
              "@a value @n.\n", "[-3 * @n] equals 21.\n", "not ([@m + 1] is marked).\n"]
    for source in truths:
        assert evaluate(ENV, parse(ENV, source), model, trace=False).value is True, source
    with pytest.raises(VEError):
        FiniteModel.from_dict(ENV, {**_model(), "constants": {**_model()["constants"], "n": "07"}})
    with pytest.raises(VEError):
        FiniteModel.from_dict(ENV, {**_model(), "constants": {**_model()["constants"], "n": -7}})


def test_countermodel_search_is_bounded_and_rechecked():
    premises = parse(ENV, "@n < 5.\n[@n + 1] is marked.\n").formulas
    found = find_countermodel(ENV, premises, parse(ENV, "@n < 3.\n").formulas[0])
    assert found.status == "Found"
    assert check_countermodel(ENV, premises, parse(ENV, "@n < 3.\n").formulas[0], found.model).valid
    # A valid consequence is never "refuted"; exhaustion is NotFound, not entailment.
    missing = find_countermodel(ENV, premises, parse(ENV, "[1 + @n] is marked.\n").formulas[0])
    assert missing.status == "NotFound"


# ---------------------------------------------------------------- certificates

def _prove(premises, conclusion):
    result = prove_entailment(ENV, premises, conclusion)
    assert result.status == "Found", result.to_dict()
    assert result.certificate["checker_version"] == "ve-order-farkas-checker@1"
    assert check_entailment_certificate(ENV, premises, conclusion, result.certificate).valid
    return result.certificate


def test_farkas_gcd_split_and_congruence_certificates():
    assert _prove([Lt(N, M)], Le(N, M))["trace"]["rule"] == "order-farkas@1"
    cuts = _prove([Eq(Scale(2, N), ONE)], Bottom())["trace"]
    assert cuts["rule"] == "order-farkas@1" and cuts["cuts"]
    assert _prove([Le(N, M), Le(M, Add(N, Num(0)))], Eq(N, M))["trace"]["rule"] == "order-neq@1"
    congruence = _prove([Unary("marked", Add(N, ONE))], Unary("marked", Add(ONE, N)))["trace"]
    assert congruence["rule"] == "order-split@1"
    _prove([Eq(Scale(3, N), Scale(2, M))], parse(ENV, "not (@n equals 1).\n").formulas[0])
    _prove([Forall("item", Unary("p", __import__("ve").Var(0)))], Unary("p", Const("a")))


def _check(premises, conclusion, trace):
    certificate = {**_binding(ENV, tuple(premises), conclusion), "trace": trace}
    return check_entailment_certificate(ENV, premises, conclusion, certificate)


def test_hazards_are_rejected():
    marked = [Unary("marked", Add(N, ONE))], Unary("marked", Add(ONE, N))
    assert not _check(*marked, {"rule": "close"}).valid
    two = [Eq(Scale(2, N), ONE)], Bottom()
    plain = {"rule": "order-farkas@1", "cuts": [], "literals": [[0, "1"], [0, "-1"]], "final_cuts": []}
    assert not _check(*two, plain).valid
    assert not _check([Lt(N, M)], Le(N, M), {"rule": "order-farkas@1", "cuts": [],
                                              "literals": [[0, "-1"], [1, "1"]], "final_cuts": []}).valid
    assert not _check([Le(N, M), Le(M, Add(N, Num(0)))], Eq(N, M), {"rule": "close"}).valid
    assert not _check([Le(N, M)], Lt(N, M), {"rule": "order-split@1", "formula": ["le", ["const", "a"], ["const", "n"]],
                                              "children": [{"rule": "close"}, {"rule": "close"}]}).valid
    assert _check([Lt(N, M)], Le(N, M), {"rule": "order-farkas@1", "cuts": [], "literals": [[0, "1"], [1, "1"]],
                                          "final_cuts": []}).valid


def test_integer_entailment_is_not_unknown_but_failure_is_inconclusive():
    result = prove_entailment(ENV, [Lt(N, Num(5))], Lt(N, Num(3)))
    assert result.status == "NotFound" and result.certificate is None


# -------------------------------------------------------------------- English

def test_english_comparisons_roundtrip_and_sugar():
    source = ("[@n + 1] < [-3 * -5].\n-@n <= [@n - 5].\nfor every item x0, (x0 value [2 * @n]).\n"
              "(@n < @m) and (@a value @m).\nnot (@m <= 3).\n[1 - @n] equals @k.\n")
    document = parse(ENV, source)
    text = render_english(document, ENV)
    assert "is less than" in text and "is at most" in text
    assert parse_english(ENV, text) == document
    assert parse_english(ENV, "M is at least 3.").formulas[0] == Le(Num(3), M)
    assert parse_english(ENV, "N is more than [m - 1].").formulas[0] == Lt(Add(M, Scale(-1, ONE)), N)


def test_english_at_least_is_never_a_counting_quantifier():
    for text in ("At least 3 items are p.", "At least two items value n.", "There are at least 3 items."):
        with pytest.raises(VEError):
            parse_english(ENV, text)


def _nested_additions(count):
    term = N
    for _ in range(count):
        term = Add(term, ONE)
    return term


def test_term_depth_is_budgeted_separately_and_round_trips():
    # 63 nested additions (term height 64) under Not(Le(t, 0)): the checker accepts
    # it, so the wire decoder must accept its serialization too.
    formula = Not(Le(_nested_additions(63), Num(0)))
    check_formula(ENV, formula)
    assert formula_from_data(ENV, formula_to_data(ENV, formula)) == formula
    assert document_from_data(ENV, [formula_to_data(ENV, formula)]).formulas == (formula,)
    # One more level exceeds the shared term budget in the checker and decoder alike.
    deeper = Not(Le(_nested_additions(64), Num(0)))
    with pytest.raises(ResourceLimit):
        check_formula(ENV, deeper)
    data = formula_to_data(ENV, formula)
    data[1][1] = ["add", data[1][1], ["num", "1"]]
    with pytest.raises(ResourceLimit):
        formula_from_data(ENV, data)
    # Formula depth and term depth are independent budgets.
    wrapped = formula
    for _ in range(62):
        wrapped = Not(wrapped)
    assert formula_from_data(ENV, formula_to_data(ENV, wrapped)) == wrapped


def test_english_integer_terms_round_trip_beyond_four_brackets():
    text = "[[[[[n + 1] + 1] + 1] + 1] + 1] is at most 0."
    document = parse_english(ENV, text)
    assert document.formulas == (Le(_nested_additions(5), Num(0)),)
    assert parse_english(ENV, render_english(document, ENV)) == document
    for count in (5, 20, 63):
        document = Document((Not(Le(_nested_additions(count), Num(0))),))
        assert parse_english(ENV, render_english(document, ENV)) == document
    with pytest.raises(ResourceLimit):
        parse_english(ENV, "[" * 64 + "n" + " + 1]" * 64 + " is at most 0.")
    with pytest.raises(VEError):
        parse_english(ENV, "[[n + 1] + 1 is at most 0.")


# ------------------------------------------------------------------------ Lean

def _invoke(executable, cases, command="order"):
    proc = subprocess.run([str(executable), command], input=json.dumps(cases), capture_output=True,
                          text=True, timeout=120)
    assert proc.returncode in (0, 1), proc.stderr
    return json.loads(proc.stdout)


def test_lean_order_route_gate(lean_executable):
    certificate = _prove([Lt(N, M)], Le(N, M))
    base = corpus.envelope("accepted", ENV, [Lt(N, M)], Le(N, M), certificate)
    cases = [base]
    for i, profiles in enumerate((["closure@0", "order@0", "relational-fol@0"], ["closure@0", "relational-fol@0"],
                                  ["relational-fol@0", "order@0"])):
        case = copy.deepcopy(base)
        case["id"] = f"rejected-{i}"
        case["environment"]["profiles"] = profiles
        cases.append(case)
    rows = _invoke(lean_executable, cases)
    assert rows[0]["valid"] is True
    assert all(row["valid"] is False and row["status"] == "error" for row in rows[1:])
    # The pre-existing certificate route still rejects every order envelope.
    old = _invoke(lean_executable, [base], "check-certificate")
    assert old[0]["valid"] is False and old[0]["error"] == "unsupported closure environment version/profiles"


def test_lean_differential_corpus(lean_executable):
    report = corpus.run(lean_executable, scale=1.0, evaluations=120)
    assert report["disagreements"] == []
    assert report["certificates_replayed"] >= 500
    assert report["lean_accepted"] == report["python_accepted"] == report["certificates_replayed"]
    assert report["lean_rejected"] == report["python_rejected"] >= 1000
    assert report["lean_refutes"] == report["countermodels_checked"] > 0
    assert report["evaluation_agreements"] == report["evaluation_cases"] == 120


def test_lean_order_route_rejects_malformed_declarations(lean_executable):
    # Declaration objects, descriptions and display metadata are validated as in
    # Python even when the certificate bindings are recomputed for the bad input.
    certificate = _prove([Top()], Top())
    base = corpus.envelope("well-formed", ENV, [Top()], Top(), certificate)
    mutations = {
        "sort-not-object": lambda v: v["sorts"].__setitem__("item", "not a declaration object"),
        "empty-description": lambda v: v["sorts"]["item"].__setitem__("description", ""),
        "extra-sort-field": lambda v: v["sorts"]["item"].__setitem__("colour", "red"),
        "bad-sort-display": lambda v: v["sorts"]["item"].__setitem__("verbalisation", {"singular": "item"}),
        "empty-verbalisation": lambda v: v["predicates"]["p"].__setitem__("verbalisation", ""),
        "long-verbalisation": lambda v: v["predicates"]["p"].__setitem__("verbalisation", "x" * 257),
        "extra-predicate-field": lambda v: v["predicates"]["p"].__setitem__("note", "x"),
        "predicate-not-object": lambda v: v["predicates"].__setitem__("p", ["item"]),
        "empty-constant-display": lambda v: v["constants"]["a"].__setitem__("verbalisation", ""),
        "constant-no-description": lambda v: v["constants"]["a"].pop("description"),
    }
    cases = [base]
    for name, mutate in mutations.items():
        case = copy.deepcopy(base)
        case["id"] = name
        mutate(case["environment"]["vocabulary"])
        with pytest.raises(VEError):
            Environment(case["environment"])
        environment_id = digest("ve-environment-v0.1-order\n", case["environment"])
        meaning = lambda ast: digest("ve-meaning-v0.1-order\n", {"environment_id": environment_id, "ast": ast})
        case["certificate"] = {**case["certificate"], "environment_id": environment_id,
                               "premise_meaning_ids": [meaning(a) for a in case["premises"]],
                               "conclusion_meaning_id": meaning(case["conclusion"])}
        cases.append(case)
    rows = _invoke(lean_executable, cases)
    assert rows[0]["valid"] is True, rows[0]
    for row in rows[1:]:
        assert row["valid"] is False and row["status"] == "error", row

    display = copy.deepcopy(ENV.to_dict())
    display["vocabulary"]["constants"]["a"]["verbalisation"] = "the A"
    named = Environment(display)
    proof = prove_entailment(named, [Top()], Top())
    assert proof.status == "Found"
    accepted = corpus.envelope("constant-display", named, [Top()], Top(), proof.certificate)
    assert _invoke(lean_executable, [accepted])[0]["valid"] is True


def test_lean_order_term_depth_matches_python(lean_executable):
    formula = Not(Le(_nested_additions(63), Num(0)))
    certificate = _prove([formula], formula)
    accepted = corpus.envelope("depth-63", ENV, [formula], formula, certificate)
    rejected = copy.deepcopy(accepted)
    rejected["id"] = "depth-64"
    for ast in (*rejected["premises"], rejected["conclusion"]):
        ast[1][1] = ["add", ast[1][1], ["num", "1"]]
    with pytest.raises(ResourceLimit):
        document_from_data(ENV, rejected["premises"])
    rows = _invoke(lean_executable, [accepted, rejected])
    assert rows[0]["valid"] is True, rows[0]
    assert rows[1]["valid"] is False and "term depth" in rows[1]["error"], rows[1]
