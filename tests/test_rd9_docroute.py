"""The small soft-chain document has the pilot probe's profiles, a soft rule and a claim graph."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from ve.document import _load_document, check_document, load_document
from ve.document.report import _report, _report_premise_context
from ve.errors import CheckerUnavailable, VEError
from ve.admission import admit_document
from ve.ast import Top, formula_to_data
from ve.identity import meaning_id
from ve.norm_defaults_route import admit_norm_defaults_document
from ve.norms import NormDocument
from ve.softnorms import SoftEnvironment, check_soft_source


FIXTURE = Path(__file__).parent / "data/rd9-docroute.ve.md"
THROUGH_FILL = "UnsupportedProfile: norm-defaults@0 documents are checked through fill (ve.norm_defaults)"
NEEDS_PROFILE = "UnsupportedProfile: unspecified completion requires norm-defaults@0"


def _front():
    raw = FIXTURE.read_bytes()
    head, body = raw[4:].split(b"\n---\n", 1)
    return json.loads(head), body


def _loaded(front, body):
    return _load_document(b"---\n" + json.dumps(front).encode() + b"\n---\n" + body,
                          FIXTURE, None)


def _without_profile(tmp_path):
    front, body = _front()
    front["environment"]["profiles"].remove("norm-defaults@0")
    path = tmp_path / "without-defaults.ve.md"
    path.write_bytes(b"---\n" + json.dumps(front).encode() + b"\n---\n" + body)
    return path


def _direct_case():
    front, _ = _front()
    lower = deepcopy(front["environment"])
    lower["profiles"].remove("readings@1")
    document = {
        "units": [
            {"id": "u1", "span": front["units"][0]["span"], "kind": "norm",
             "content": front["units"][0]["content"]},
            {"id": "u2", "span": front["units"][1]["span"], "kind": "asserted",
             "content": ["top"]},
        ],
        "graph": front["graph"], "lemmas": [], "open_terms": [], "reading_sets": [], "narrowings": [],
    }
    return SoftEnvironment(lower), document


def test_soft_chain_document_checks_the_filled_route():
    loaded = load_document(FIXTURE)
    assert loaded["norm_defaults"] is None  # The soft chain owns its fill.
    report = check_document(FIXTURE)
    env, document = _direct_case()
    admitted = admit_norm_defaults_document(env, document)
    assert report["admission"]["admitted"] is True
    assert report["admission"]["report"] == admitted["report"]
    assert report["admission"]["core_report_id"] == admitted["report_id"]


def test_filled_soft_premises_make_a_contradiction_vacuous():
    front, body = _front()
    norm = front["units"][0]["content"]["norm"]
    norm["mode"] = "strict"
    norm.pop("exception")
    denied = ["not", ["forall", "assistant", ["unary", "x_required", ["var", 0]]]]
    front["units"][1]["content"]["ast"] = denied
    front["graph"]["nodes"][0]["ast"] = denied
    answer = _report(_loaded(front, body))
    assert answer["admission"]["admitted"] is True
    assert answer["premises"]["status"] == "INCONSISTENT"
    assert answer["admission"]["vacuous"] is True


@pytest.mark.parametrize("status", ["authored", "open"])
def test_filled_soft_premises_exclude_norm_replaced_by_assertion_reading(status):
    front, body = _front()
    norm = front["units"][0]["content"]["norm"]
    norm["mode"] = "strict"
    norm.pop("exception")
    denied = ["not", ["forall", "assistant", ["unary", "x_required", ["var", 0]]]]
    front["units"][1]["content"]["ast"] = denied
    front["graph"]["nodes"][0]["ast"] = denied
    assert _report(_loaded(front, body))["premises"]["status"] == "INCONSISTENT"

    env = _loaded(front, body)["soft_document"].extended_env
    front["reading_sets"] = [{
        "id": "r", "unit": "u1", "version": 1, "status": status,
        **({"signature": "a"} if status == "authored" else {}),
        "readings": [{"id": "c", "kind": "asserted", "meaning_id": meaning_id(env, Top()),
                      "content": ["top"],
                      "admission": {"who": "a", "why": "a", "distinguishing_models": {}}}],
    }]
    answer = _report(_loaded(front, body))
    assert answer["premises"]["status"] == "model"
    assert answer["admission"]["vacuous"] is False


@pytest.mark.parametrize("label", ["layer:norms:x_permitted", "layer:norms:x_required",
                                         "unsaid:pair:x_required,x_permitted"])
def test_filled_graph_leaves_decode_in_the_filled_vocabulary(label):
    from ve.norm_defaults_route import run_case
    doc = load_document(FIXTURE)
    source = doc["environment"].to_dict()
    source["profiles"].remove("readings@1")
    row = run_case({"id": "fill", "kind": "norm-defaults-elaborate", "environment": source,
                    "norms": [doc["meta"]["units"][0]["content"]]})
    generated = {item["label"]: item["ast"] for item in row["premises"]}
    generated["unsaid:pair:x_required,x_permitted"] = row["fill"][0]["ast"]
    doc["meta"]["graph"] = {"root": "leaf", "nodes": [{"name": "leaf", "label": label,
                                                     "ast": generated[label]}]}
    assert _report(doc)["admission"]["admitted"] is True


def test_soft_fill_uses_every_lean_generated_premise_class():
    from conformance.norm_defaults_layered import fixtures
    from ve.norm_defaults_route import run_case
    kind, source, norms, _ = next((kind, env, rules, situations)
                                   for name, kind, env, rules, situations in fixtures()
                                   if name == "coherent")
    assert kind == "soft"
    from ve.softnorms import SoftEnvironment, SoftNormDocument
    environment = SoftEnvironment(source)
    compiled = [{"id": f"u{i}", "kind": "norm", "content": item}
                for i, item in enumerate(norms)]
    doc = {"environment": environment, "soft_document": SoftNormDocument(environment, norms),
           "rights_document": None, "meta": {"units": compiled},
           "units": compiled, "norms": None, "norm_defaults": None}
    row = run_case({"id": "fill", "kind": "norm-defaults-elaborate",
                    "environment": source, "norms": norms})
    assert row["soft"] and row["premises"]
    expected = [item["ast"] for field in ("background", "premises", "fill", "soft")
                for item in row[field]]
    env, fixed, _ = _report_premise_context(doc)
    assert fixed == expected
    assert "unsaid__y_permitted" in env.predicates
    assert "soft__excepted__must_x" in env.predicates


def test_soft_coherence_graph_leaf_uses_filled_vocabulary():
    from conformance.norm_defaults_layered import fixtures
    from ve.norm_defaults_route import run_case
    front, body = _front()
    _, kind, source, norms, _ = next(item for item in fixtures() if item[0] == "coherent")
    assert kind == "soft"
    row = run_case({"id": "fill", "kind": "norm-defaults-elaborate",
                    "environment": source, "norms": norms})
    coherence = next(item for item in row["soft"] if item["label"].startswith("soft:coherence:"))
    front["environment"] = source
    front["units"][0]["content"] = norms[0]
    front["units"][0]["span"] = [0, 12]
    front["units"].insert(1, {**front["units"][0], "id": "u1b", "span": [12, 24],
                               "content": norms[1]})
    front["graph"] = {"root": "coherence", "nodes": [
        {"name": "coherence", "label": coherence["label"], "ast": coherence["ast"]}]}
    answer = _report(_loaded(front, body))
    assert answer["admission"]["admitted"] is True


def test_soft_chain_without_readings_uses_the_filled_route():
    front, body = _front()
    front["environment"]["profiles"].remove("readings@1")
    answer = _report(_loaded(front, body))
    assert answer["admission"]["admitted"] is True
    assert answer["premises"]["status"] == "model"


@pytest.mark.parametrize("mixed", [False, True])
@pytest.mark.parametrize("omit_norm_content", [False, True])
def test_filled_soft_report_selects_compiled_units(mixed, omit_norm_content):
    front, body = _front()
    if omit_norm_content:
        front["units"][0].pop("content")
    if mixed:
        parts = [{**unit, "status": "LABELLED" if omit_norm_content and unit["id"] == "u1"
                  else "CHECKED"} for unit in front["units"]]
        front["units"] = [{"id": "parent", "span": [0, 38], "status": "MIXED", "parts": parts}]
    doc = _loaded(front, body)
    assert [unit["id"] for unit in doc["units"]] == ["u1", "u2"]
    assert _report(doc)["admission"]["admitted"] is True


def _wrapped(units):
    return [{"id": "p", "span": [0, 38], "status": "MIXED",
             "parts": [{**unit, "status": "CHECKED"} for unit in units]}]


def _soft_lines(coverage):
    return {key: coverage[key] for key in
            ("soft_status", "default_exceptions_by_decider", "soft_residual_labels", "soft_background_labels")}


@pytest.mark.parametrize("chain", ["filled", "plain"])
def test_mixed_container_keeps_soft_decisions(chain, tmp_path):
    # F7: the soft source reads a MIXED unit's parts, so wrapping the units keeps the decision predicate, the
    # default exception and the OPEN soft status, on the filled chain and on the plain soft chain Lean answers.
    answers = []
    for mixed in (False, True):
        front, body = _front()
        if chain == "plain":
            front["environment"]["profiles"].remove("norm-defaults@0")
            front["environment"]["vocabulary"]["predicates"]["x_permitted"]["regulated"]["default"] = "deny"
        if mixed:
            front["units"] = _wrapped(front["units"])
        doc = _loaded(front, body)
        path = tmp_path / f"{chain}-{mixed}.ve.md"
        path.write_bytes(b"---\n" + json.dumps(front).encode() + b"\n---\n" + body)
        answers.append((sorted(doc["soft_document"].extended_env.decision_names), _soft_lines(_report(doc)["coverage"]),
                        _soft_lines(check_document(path)["coverage"])))
    assert answers[1] == answers[0]
    assert answers[0][0] == ["soft__excepted__s"]
    assert answers[0][1]["soft_status"] == answers[0][2]["soft_status"] == "OPEN"
    assert answers[0][1]["default_exceptions_by_decider"] == {"unstated": 1}


def _unit(uid, start, end, kind, content, status=None):
    return {"id": uid, "span": [start, end], "kind": kind, "meaning": "specified", "support": "none",
            "content": content, **({"status": status} if status else {})}


_RULE = {"norm": {"name": "s"}}
_CHECKED = [_unit("u1", 0, 24, "norm", _RULE, "CHECKED"), _unit("u2", 24, 38, "asserted", ["top"], "CHECKED")]


def _mixed(parts, end=38):
    return {"id": "p", "span": [0, end], "status": "MIXED", "parts": parts}


@pytest.mark.parametrize("units, norms", [
    ([_unit("u1", 0, 24, "norm", _RULE), _unit("u2", 24, 38, "asserted", ["top"])], [_RULE]),
    ([_mixed(_CHECKED)], [_RULE]),
    ([_mixed(_CHECKED, 40)], [_RULE]),
    ([_mixed(_CHECKED[::-1]), _unit("u3", 38, 40, "norm", _RULE)], []),
    ([_unit("u1", 0, 24, "norm", _RULE), 1, _unit("u3", 24, 38, "norm", _RULE)], [_RULE]),
], ids=["flat", "mixed", "short-parent", "misplaced-part", "non-object"])
def test_soft_source_reads_mixed_parts(units, norms):
    # The units of `VE.Service.SoftSourceExamples`, whose `#guard`s check Lean's `softSourceNorms` on them.
    from ve.document.containers import _soft_contents
    assert _soft_contents(units) == norms


@pytest.mark.parametrize("with_readings", [False, True])
def test_filled_soft_source_instruction_declarations_match_lean_base(with_readings):
    front, body = _front()
    if not with_readings:
        front["environment"]["profiles"].remove("readings@1")
    vocabulary = front["environment"]["vocabulary"]
    vocabulary["soft"] = {"parties": ["operator"], "outranking": {"mode": "strict"}}
    vocabulary["predicates"]["q"] = {
        "arguments": ["assistant"], "description": "instruction", "instruction_of": "operator"}
    doc = _loaded(front, body)
    env, _, _ = _report_premise_context(doc)
    assert env.predicates["q"].description == "instruction"
    assert _report(doc)["admission"]["admitted"] is True


def test_filled_soft_layer_matches_ordinary_w1():
    # The frozen oracle proposes the ordinary W1 tree. Both answers are Lean's.
    from conformance import frozen_norm_defaults as oracle
    env, source = _direct_case()
    filled = oracle.UnspecifiedSoftDocument(env, [source["units"][0]["content"]])
    label, formula = next((name, ast) for name, ast in filled.filled.premises()
                          if name == "layer:norms:x_permitted")
    ast = formula_to_data(filled.filled.env, formula)
    assert "unsaid__x_permitted" in json.dumps(ast)
    source["graph"] = {"root": "layer", "nodes": [{"name": "layer", "ast": ast, "label": label}]}
    routed = admit_norm_defaults_document(env, source)
    ordinary_env = deepcopy(filled.filled.env.to_dict())
    ordinary_env["profiles"].remove("soft-norms@0")
    ordinary = deepcopy(source)
    ordinary["units"][0]["content"] = filled.filled.rules[0].to_dict()
    end = ordinary["units"][-1]["span"][1]
    ordinary["units"].append({"id": "generated", "span": [end, end + 1], "kind": "norm",
                              "content": filled.filled.rules[1].to_dict()})
    checked_w1 = admit_document(ordinary_env, ordinary)
    assert routed["admitted"] is checked_w1["admitted"] is True
    assert routed["report"] == checked_w1["report"]


def test_soft_admission_conditions_are_bound_to_the_source(monkeypatch):
    from ve import norm_defaults_route as route
    env, document = _direct_case()
    original = route.run_case
    for labels in (["soft:coherence:absent,absent"],
                   ["soft:coherence:absent,absent", "soft:coherence:absent,absent"]):
        def changed(case):
            row = original(case)
            if case["kind"] == "admission":
                row = {**row, "conditional_on": labels}
            return row
        monkeypatch.setattr(route, "run_case", changed)
        with pytest.raises(CheckerUnavailable, match="unbound condition"):
            admit_norm_defaults_document(env, document)
        monkeypatch.setattr(route, "run_case", original)

    def missing(case):
        row = original(case)
        if case["kind"] == "admission":
            row = {key: value for key, value in row.items() if key != "conditional_on"}
        return row
    monkeypatch.setattr(route, "run_case", missing)
    with pytest.raises(CheckerUnavailable, match="another filled route"):
        admit_norm_defaults_document(env, document)


def test_soft_admission_row_fields_are_typed():
    from ve import norm_defaults_route as route
    from ve.backends.service_schema import Invalid, check_row
    env, document = _direct_case()
    case = {"id": "admission", "kind": "admission", "environment": env.to_dict(), "document": document}
    row = route.run_case(case)
    check_row("norm-defaults", row, case, 0)
    for field in row:
        missing = {key: value for key, value in row.items() if key != field}
        wrong_type = {**row, field: 7}
        if field != "conditional_on":
            with pytest.raises(Invalid):
                check_row("norm-defaults", missing, case, 0)
        with pytest.raises(Invalid):
            check_row("norm-defaults", wrong_type, case, 0)


def test_soft_admission_elaborates_fill_once(monkeypatch):
    from ve import norm_defaults_route as route
    env, document = _direct_case()
    original = route.run_case
    called = []

    def counted(case):
        called.append(case["kind"])
        return original(case)

    monkeypatch.setattr(route, "run_case", counted)
    assert route.admit_norm_defaults_document(env, document)["admitted"] is True
    assert called == ["admission", "norm-defaults-elaborate"]


def test_unspecified_without_profile_keeps_its_own_refusal(tmp_path):
    with pytest.raises(VEError, match="^" + NEEDS_PROFILE + "$"):
        check_document(_without_profile(tmp_path))


def test_plain_soft_document_keeps_its_admission_route(tmp_path):
    front, body = _front()
    front["environment"]["profiles"].remove("norm-defaults@0")
    front["environment"]["vocabulary"]["predicates"]["x_permitted"]["regulated"]["default"] = "deny"
    path = tmp_path / "plain-soft.ve.md"
    path.write_bytes(b"---\n" + json.dumps(front).encode() + b"\n---\n" + body)
    assert check_document(path)["admission"]["admitted"] is True


def test_direct_soft_check_of_unfilled_tree_still_refuses():
    front, _ = _front()
    with pytest.raises(VEError, match="^" + THROUGH_FILL.replace("(", r"\(").replace(")", r"\)") + "$"):
        check_soft_source(front["environment"], [front["units"][0]["content"]])


def test_direct_w1_outcome_of_unfilled_soft_tree_still_refuses():
    front, _ = _front()
    document = NormDocument(SoftEnvironment(front["environment"]), [])
    with pytest.raises(VEError, match="^" + THROUGH_FILL.replace("(", r"\(").replace(")", r"\)") + "$"):
        document.outcome("x_required")
