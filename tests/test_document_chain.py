"""PC-2a: `ve document check` composes soft-norms@0 with norm-defaults@0 through the norm-defaults mode's own decoder
(docs/spec/profile-composition.md 3.2 and 5.2). Lean decides every value here: the same fixtures are `#guard`s of
lean/VE/Service/DocumentChainExamples.lean, which read `DocumentChain.layeredOf` itself. F2.4, DeepMind probe DF-c, is
the harness's, and is not run here."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

from tests.document_chain_corpus import (CHAIN, NEVER, ROOT, SAVED, TOP, answers, chain_document, chain_front,
                                         conclusions_of, corpus, text)
from ve.backends.relay import answer
from ve.document import load_document
from ve.document.lean import _lean_only
from ve.document.load import _load, _load_document
from ve.errors import CheckerUnavailable, ResourceLimit, VEError
from ve.norm_defaults_route import run_cases

COMPLY, DENY = "u0073.s05", "u0125.s04.p2"
ROUTE = Path("document.ve.md")
REFUSAL = "CheckerUnavailable: soft-norms with readings, alternatives or risk needs its composed Lean route"
ANSWERED, WRITTEN = corpus()
SAVED_ANSWERS = json.loads(SAVED.read_text())


def document_mode(raw, admit=True):
    """The Lean `document` mode's row and error, the first entry point."""
    return answer("document", {"id": "document", "document": raw.decode(), "admit": admit})


def mode_case(kind, uid=COMPLY, **fields):
    """A `norm-defaults` case over the unit's document: the second entry point, as `requestOf` makes it."""
    front = chain_front(uid)
    return {"id": kind, "kind": kind, "environment": front["environment"],
            "norms": [front["units"][0]["content"]], **fields}


def situation(danger, excepted):
    row = [["c"]]
    return {"complete": True, "domains": {"claude_instance": ["c"]}, "constants": {},
            "relations": {"unsafe_to_comply": row if danger else [], "unethical_to_comply": [],
                          "against_guidelines": [], "soft__excepted__comply": row if excepted else []}}


FILLINGS = {"yes": {"unsaid__comply_required": [["c"]]}, "no": {"unsaid__comply_required": []}}


def status_case(model, method):
    return mode_case("norm-defaults-status", model=model, predicate="comply_required", tuple=["c"], method=method,
                     **FILLINGS)


def report_case(model):
    return mode_case("norm-defaults-report", witnesses={
        "comply_required": {"model": model, "filling": FILLINGS["yes"], "tuple": ["c"]}})


def test_f2_1_the_document_mode_admits_the_soft_default_rule(tmp_path):
    row, error = document_mode(chain_document(COMPLY))
    assert error is None
    assert [(u["id"], u["status"]) for u in row["units"]] == [(COMPLY, "CHECKED")]
    coverage = json.loads(answers(chain_document(COMPLY), tmp_path)["check"]["output"])["coverage"]
    assert coverage["residual"]["default_exceptions"] == 1
    assert coverage["soft_residual_labels"] == ["soft__excepted__comply"]


@pytest.mark.parametrize(("danger", "excepted", "method", "status"), [
    (False, False, "enumerate", "SETTLED yes"),
    (False, False, "table3", "SETTLED yes"),
    (True, True, "undecided", "UNDECIDED"),
    (False, False, "undecided", "UNKNOWN"),  # the other direction: no exception, so the fillings witness no gap
    (True, True, "enumerate", "UNKNOWN"),
])
def test_f2_1_point_statuses(danger, excepted, method, status):
    (row,) = run_cases([status_case(situation(danger, excepted), method)])
    assert row["point_status"] == status


def test_f2_1_an_exception_without_its_decision_is_no_situation_of_the_document():
    """The soft pack's exception premise binds a filling: refused without its decision, accepted with it."""
    refused, reached = run_cases([report_case(situation(True, False)), report_case(situation(True, True))])
    assert refused["error"] == "InvalidModel(soft): the model violates a background premise"
    assert reached["status"] == "ok"


@pytest.mark.parametrize(("completions", "error_class", "text_"), [
    ({"comply_permitted": {"cites": ["absent"], "reason": "x"}}, VEError,
     "InvalidInput: completion grounding for comply_permitted cites an unknown unit"),
    ({"comply_required": {"cites": [COMPLY], "reason": "x"}}, VEError,
     "InvalidInput: completion of comply_required is unspecified and cites nothing"),
    ({"absent": {"cites": [COMPLY], "reason": "x"}}, VEError, "UnknownSymbol: regulated predicate absent"),
    (7, VEError, "InvalidInput: completions must be an object"),
])
def test_f2_1b_validate_completions_answers_from_both_entry_points(completions, error_class, text_):
    _, error = document_mode(chain_document(COMPLY, completions=completions))
    assert isinstance(error, error_class) and str(error) == text_
    (row,) = run_cases([mode_case("norm-defaults-report", unit_ids=[COMPLY], completions=completions)])
    assert row["error"] == text_


def test_f2_1b_a_valid_completions_entry_is_accepted_from_both_entry_points():
    completions = {"comply_permitted": {"cites": [COMPLY], "reason": "the rule"}}
    _, error = document_mode(chain_document(COMPLY, completions=completions))
    assert error is None
    (row,) = run_cases([mode_case("norm-defaults-report", unit_ids=[COMPLY], completions=completions)])
    assert row["status"] == "ok"


def test_f2_2_check_and_readings_report_the_same_premise_status(tmp_path):
    """What both commands report of the strict rule: the document has a model and nothing is vacuous. The readings
    query keeps its own lower route, which reads no soft rule (`_report_premise_context`); PC-2b's chain rows join it."""
    found = answers(chain_document(DENY), tmp_path, (TOP, NEVER))
    check = json.loads(found["check"]["output"])
    asked = [json.loads(found[f"readings --conclusion {json.dumps(c)}"]["output"]) for c in (TOP, NEVER)]
    assert check["premises"]["status"] == "model"
    assert [a["premises"]["status"] for a in asked] == ["model", "model"]
    assert [a["vacuous"] for a in asked] == [False, False]
    assert asked[0]["verdict"] == "ALL"
    assert check["soft"]["decision_predicates"] == []


def test_f2_2_a_strict_rule_contradicted_by_a_claim_is_inconsistent_in_check(tmp_path):
    """The check's premises read the strict rule on the filled tree: the opposite claim makes them inconsistent."""
    found = answers(ANSWERED[f"{DENY}#inconsistent"], tmp_path)
    assert json.loads(found["check"]["output"])["premises"]["status"] == "INCONSISTENT"


def _canonical(answer_):
    """An answer as F2.3 compares it: the JSON commands' values, a text command's bytes, and a refusal's code and text."""
    if "output" not in answer_:
        return answer_
    try:
        return json.dumps(json.loads(answer_["output"]), sort_keys=True, ensure_ascii=False)
    except ValueError:
        return answer_["output"]


def test_f2_3_the_corpus_is_every_document_of_tests_data_with_a_saved_answer():
    assert set(SAVED_ANSWERS) == {*ANSWERED, *WRITTEN}
    assert list(WRITTEN) == ["tests/data/rd9-docroute.ve.md"]


@pytest.mark.parametrize("name", sorted({*ANSWERED, *WRITTEN}))
def test_f2_3_every_answer_equals_the_retained_loaders(name, tmp_path):
    raw = {**ANSWERED, **WRITTEN}[name]
    found = answers(raw, tmp_path, conclusions_of(name))
    assert set(found) == set(SAVED_ANSWERS[name])
    for command, saved in SAVED_ANSWERS[name].items():
        assert _canonical(found[command]) == _canonical(saved), command


@pytest.mark.parametrize("name", sorted(ANSWERED))
def test_f2_3_lean_itself_answers_each_chain_document(name):
    """No row of the group takes the retained path: every answer is the mode's, a success or its own refusal."""
    _, error = document_mode(ANSWERED[name])
    assert not isinstance(error, CheckerUnavailable) or name == f"{COMPLY}#unknown-predicate", error


def test_f2_3_the_refusal_names_only_what_is_still_refused():
    (raw,) = WRITTEN.values()
    _, error = document_mode(raw)
    assert isinstance(error, CheckerUnavailable) and str(error) == REFUSAL
    assert "norm-defaults" not in REFUSAL


@pytest.mark.parametrize("name", [COMPLY, DENY, "tests/data/rd9-docroute.ve.md#lower"])
def test_the_retained_branch_accepts_nothing_of_this_chain(name):
    with pytest.raises(CheckerUnavailable, match="answered only by Lean's document mode"):
        _load_document(ANSWERED[name], ROUTE, None)


def _reserved_name():
    front = chain_front(DENY)
    front["environment"]["vocabulary"]["predicates"]["unsaid__x"] = {"arguments": ["claude_instance"], "description": "x"}
    return text(front, CHAIN["units"][DENY]["body"].encode())


@pytest.mark.parametrize("command", ["coverage", "render", "readings"])
@pytest.mark.parametrize(("document", "refused", "says"), [
    # Lean refuses a null `completions` as outside its JSON reader, and a repeated profile as outside the gate.
    (lambda: chain_document(COMPLY, completions=None), "CheckerUnavailable", "answered only by Lean's document mode"),
    (lambda: text(chain_front(COMPLY, profiles=[*CHAIN["profiles"], "norm-defaults@0"]),
                  CHAIN["units"][COMPLY]["body"].encode()), "CheckerUnavailable", "answered only by Lean's document mode"),
    # The layered route's own refusals, which the retained loader did not read at load (rows45 item 5).
    (lambda: _many_rules(250), "ResourceLimit", "ResourceLimit: rules"),
    (_reserved_name, "VEError", "InvalidInput: reserved name unsaid__x"),
], ids=["null-completions", "repeated-profile", "limit", "reserved-name"])
def test_a_document_lean_refuses_is_refused_on_every_path(document, refused, says, command, tmp_path):
    """Each load-only command gets Lean's refusal of a document the retained loader accepted at load."""
    found = answers(document(), tmp_path, ())[command]
    assert found["refused"] == refused and says in found["text"]


def test_the_retained_branch_keeps_every_other_chain():
    """The opposite direction: `readings@1` beside the chain, the plain soft route and a discourse admission still load."""
    (with_readings,) = WRITTEN.values()
    assert _load_document(with_readings, ROUTE, None)["soft_document"] is not None
    plain = chain_front(DENY, profiles=[p for p in CHAIN["profiles"] if p != "norm-defaults@0"])
    plain["environment"]["vocabulary"]["predicates"]["deny_being_claude_permitted"]["regulated"]["default"] = "allow"
    assert _load_document(text(plain, CHAIN["units"][DENY]["body"].encode()), ROUTE, None)["soft_document"] is not None
    assert _load_document(chain_document(COMPLY), ROUTE, {})["soft_document"] is not None


@pytest.mark.parametrize(("profiles", "only"), [
    (CHAIN["profiles"], True),
    ([*CHAIN["profiles"], "readings@1"], False),
    ([p for p in CHAIN["profiles"] if p != "norm-defaults@0"], False),
    ([p for p in CHAIN["profiles"] if p != "soft-norms@0"], False),
])
def test_only_this_chain_keeps_lean_s_limit_as_its_answer(profiles, only):
    assert _lean_only(text(chain_front(COMPLY, profiles=profiles), b"x")) is only


def test_a_limit_stays_unknown_on_this_chain(monkeypatch):
    """A limit Lean reports is UNKNOWN, never a refusal of the retained path."""
    limit = ResourceLimit("ResourceLimit: the document mode's budget")
    monkeypatch.setattr("ve.backends.relay.answer", lambda mode, case: (None, limit))
    with pytest.raises(ResourceLimit, match="the document mode's budget"):
        _load(ROUTE, admit=False, raw=chain_document(COMPLY))


def _many_rules(count):
    """`count` strict rules, over seven unspecified permissions."""
    base = CHAIN["units"][DENY]
    front = chain_front(DENY)
    predicate = base["predicates"]["deny_being_claude_permitted"]
    predicates = {}
    units, body = [], b""
    for index in range(count):
        name = f"deny{index % 7}_permitted"
        predicates[name] = {**predicate, "regulated": {**predicate["regulated"],
                                                       "act": "{0} deny " + chr(97 + index % 7)}}
        line = f"Rule {index}.\n".encode()
        units.append({"id": f"u{index}", "span": [len(body), len(body) + len(line)], "kind": "norm",
                      "meaning": "specified", "support": "assumption",
                      "content": {"norm": {**base["rule"], "name": f"rule-{index}", "predicate": name}}})
        body += line
    front["environment"]["vocabulary"]["predicates"] = predicates
    front["units"] = units
    return text(front, body)


def test_a_large_document_ends_within_the_layered_routes_own_limit():
    """The layered decoder charges a document once against `authorLimits`: rules and unspecified predicates, at most
    256. The soft route's own limit (256 rules) admits both documents; only the layered one tells them apart, and its
    refusal is `ResourceLimit`, never a verdict."""
    row, error = document_mode(_many_rules(249), admit=False)
    assert error is None and len(row["units"]) == 249
    _, error = document_mode(_many_rules(250), admit=False)
    assert isinstance(error, ResourceLimit) and str(error) == "ResourceLimit: rules"


def test_the_judgment_layer_composes_beside_this_chain():
    """`judgments@0` over a strict rule of this chain is read by PC-1's reader: the unit is OPEN, with its term's usage."""
    front = chain_front(DENY, profiles=sorted([*CHAIN["profiles"], "judgments@0"]))
    vocabulary = front["environment"]["vocabulary"]["predicates"]
    vocabulary["t"] = {"arguments": ["claude_instance"], "description": "a judgment"}
    front["units"][0]["meaning"] = {"open": ["t"]}
    front["units"][0]["content"]["norm"]["guard"] = ["unary", "t", ["var", 0]]
    front["open_terms"] = [{"name": "t", "arguments": ["claude_instance"], "decided_by": "unstated", "necessary": [],
                            "sufficient": [], "factors": [], "precedents": [], "jurisdiction": "document", "version": 1}]
    row, error = document_mode(text(front, CHAIN["units"][DENY]["body"].encode()))
    assert error is None
    assert row["units"][0]["status"] == "OPEN"
    assert row["judgments"]["used"] == [{"term": "t", "units": [DENY]}]


def test_the_judgment_layer_stays_apart_from_a_rule_with_exception_conditions():
    """The opposite direction: PC-1 reads no exception condition (pc-1x), so this rule keeps main's refusal."""
    front = chain_front(COMPLY, profiles=sorted([*CHAIN["profiles"], "judgments@0"]))
    _, error = document_mode(text(front, CHAIN["units"][COMPLY]["body"].encode()))
    assert isinstance(error, CheckerUnavailable)
    assert str(error) == "CheckerUnavailable: judgments@0 with soft-norms@0 needs its composed Lean route"


def _nodes(value, path=()):
    """Every JSON node's path under `value`."""
    yield path
    if type(value) is dict:
        for key, item in value.items():
            yield from _nodes(item, (*path, key))
    elif type(value) is list:
        for index, item in enumerate(value):
            yield from _nodes(item, (*path, index))


def _replaced(value, path, new):
    if not path:
        return new
    if type(value) is dict:
        return {key: _replaced(item, path[1:], new) if key == path[0] else item for key, item in value.items()}
    return [_replaced(item, path[1:], new) if index == path[0] else item for index, item in enumerate(value)]


@pytest.mark.parametrize("new", [7, True, None, [], {}, 1.5, "\ud800"], ids=repr)
def test_only_a_ve_error_escapes_a_malformed_node(new):
    """Every node of F2.1's front matter replaced, on the public entry: a refusal is a `VEError` or `CheckerUnavailable`,
    never another type."""
    body = CHAIN["units"][COMPLY]["body"].encode()
    front = chain_front(COMPLY)
    front["completions"] = {"comply_permitted": {"cites": [COMPLY], "reason": "the rule"}}
    for path in _nodes(front):
        if path:
            raw = text(_replaced(front, path, new), body)
            try:
                _load(ROUTE, admit=True, raw=raw)
            except (VEError, CheckerUnavailable):
                pass


def test_only_a_ve_error_escapes_a_deep_node():
    deep = "[" * 10000 + "]" * 10000
    raw = chain_document(COMPLY).replace(b'"guard": ["top"]', f'"guard": {deep}'.encode())
    with pytest.raises((VEError, CheckerUnavailable)):
        _load(ROUTE, admit=True, raw=raw)


def test_statements_equal_the_spec():
    sys.path.insert(0, str(ROOT / "tools"))
    from check_pc2a_statements import main
    assert main() == 0
