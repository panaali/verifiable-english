"""Batch 16f: the document mode's remaining groups are Lean answers, typed and bound.

Plain `norms@0` content is decided on the norms route, a `soft-norms@0` document on the soft route (its formulas, fences
and reading sets read in the soft route's `E″`), an environment the mode composes no route for gets the environment
mode's fault, and a distinguishing model's or a strict fence's fault gets the owning mode's located diagnostic. Every
answer is Python's retained path's public outcome; every new answer field is typed by the response schema and bound
to the request by the receiver (R8)."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from conformance import document_wrapper as dw
from tools.lean_first_diff import outcome
from ve import document as D
from ve.backends import relay
from ve.backends.lean_service import LeanService
from ve.backends.service_schema import Context, Invalid, ROWS
from ve.errors import CheckerUnavailable, VEError


@pytest.fixture(scope="module")
def service():
    with LeanService() as instance:
        yield instance


def _seed(name: str) -> dict:
    return deepcopy(dict(dw.seeds())[name])


def _text(document: dict) -> str:
    return dw.text_of(document)


def _both(service, document: dict):
    text = _text(document)
    return dw.python_answer(text), dw.lean_answers(service, [text])[0]


def _public(path: Path):
    """(Lean decides, the public check and render on the Lean path, the same on the retained path)."""
    raw = path.read_bytes()
    try:
        decided = D._lean_answer(raw, True) is not None
    except VEError:
        decided = True
    new = [outcome(lambda: D.check_document(path)), outcome(lambda: D.render_document(path))]
    with patch.object(D, "_lean_answer", return_value=None):
        old = [outcome(lambda: D.check_document(path)), outcome(lambda: D.render_document(path))]
    return decided, new, old


# ------------------------------------------------------------------------------- the groups Lean now decides

@pytest.mark.parametrize("name", ["soft-norms", "norms-content"])
def test_the_layer_seeds_are_decided_by_lean_with_the_retained_public_outcome(tmp_path, name):
    path = tmp_path / "document.ve.md"
    path.write_text(_text(_seed(name)))
    decided, new, old = _public(path)
    assert decided and new == old and "returned" in new[0], (new, old)


def test_soft_norms_alone_is_owned():
    """Batch 16e owned `soft-norms@0` only beneath `rights@0`; the soft route now composes it alone."""
    assert "soft-norms@0" in dw.OWNED
    text = _text(_seed("soft-norms"))
    row = D._lean_answer(text.encode(), True)
    kinds = {u["id"]: u["kind"] for u in row["units"]}
    assert kinds == {"rule": "norm", "fact": "asserted", "excepted": "asserted"}


def test_a_formula_over_a_decision_predicate_is_read_in_the_extended_environment(service):
    """`soft__excepted__share_rule` is declared only by the soft route's `E″`: Python's `formula_from_data(formula_env,
    ...)` reads it there, and so does Lean; without the soft profile both reject it with the same text."""
    document = _seed("soft-norms")
    python, answer = _both(service, document)
    assert dw.verdict(python, answer) == "agree" and answer["outcome"] == "ok", (python, answer)
    document["front"]["environment"]["profiles"].remove("soft-norms@0")
    document["front"]["units"][0]["content"]["norm"].pop("mode")
    document["front"]["units"][0]["content"]["norm"].pop("exception")
    document["front"]["units"][0]["meaning"] = "specified"
    python, answer = _both(service, document)
    assert dw.verdict(python, answer) == "agree" and answer["outcome"] == "error", (python, answer)
    assert "soft__excepted__share_rule" in answer["text"], answer


@pytest.mark.parametrize("fault", ["unregulated", "unknown parent", "quoted unregulated"])
def test_norm_faults_are_the_norms_route_s(service, fault):
    """A plain norm object's faults are the norms route's diagnostics (`checkNorms`: `checkQuoted` on a quoted norm,
    then the free norm document), with Python's text. Python's own `NormDocument` raised them as `InvalidInput`;
    Lean's code is its diagnostic class (DELTA.md, row 3)."""
    document = _seed("norms-content")
    units = document["front"]["units"]
    if fault == "unregulated":
        units[0]["content"]["norm"]["predicate"] = "consents"
    elif fault == "unknown parent":
        units[0]["content"]["norm"]["over"] = ["absent"]
    else:
        units[1]["content"]["norm"]["predicate"] = "consents"
    python, answer = _both(service, document)
    assert answer["outcome"] == "error" and answer["text"] == python["text"], (python, answer)
    assert answer["code"] in (python["code"], answer["text"].split(":")[0]), (python, answer)


def test_a_quoted_soft_norm_s_fault_keeps_the_retained_path(service):
    """A norm object outside the soft source (here under a quoted kind) is checked alone under `_rule_source(E″)`
    (`check_rule_batch`, Lean's `decodeSoftNorm`); a valid one is decided. Python's relay raises a rejected one with
    the soft route's contract code, which this mode's error row cannot hold, so the mode answers
    `CheckerUnavailable` with the soft route's text."""
    document = _seed("soft-norms")
    unit = document["front"]["units"][1]
    rule = {**document["front"]["units"][0]["content"]["norm"], "name": "said"}
    unit.update(kind=["attributed", "anthropic", "says", "norm"], content={"norm": rule})
    document["front"].pop("graph")
    python, answer = _both(service, document)
    assert answer["outcome"] == "ok" and dw.verdict(python, answer) == "agree", (python, answer)
    rule["predicate"] = "consents"
    python, answer = _both(service, document)
    assert python["outcome"] == "error" and python["code"].startswith("SOFT_"), python
    assert answer["code"] == "CheckerUnavailable" and python["text"] in answer["text"], (python, answer)


def test_a_soft_admission_fault_keeps_the_retained_path(service):
    """A claim graph the soft route rejects is raised with the soft route's contract code (`admit_soft_document`), so
    the mode answers `CheckerUnavailable` with the soft route's text."""
    document = _seed("soft-norms")
    document["front"]["graph"]["nodes"][0]["unit"] = "rule"
    python, answer = _both(service, document)
    assert python["outcome"] == "error" and python["code"].startswith("SOFT_"), python
    assert answer["code"] == "CheckerUnavailable" and python["text"] in answer["text"], (python, answer)


@pytest.mark.parametrize("fault", ["unregulated", "no decider"])
def test_a_soft_source_fault_keeps_the_retained_path(service, fault):
    """The soft relay adds the `diagnose` mode's diagnostic (and its contract code) to a soft source's rejection,
    which this mode's error row cannot hold: the mode answers `CheckerUnavailable` and Python's loader decides."""
    document = _seed("soft-norms")
    norm = document["front"]["units"][0]["content"]["norm"]
    if fault == "unregulated":
        norm["predicate"] = "consents"
    else:
        norm["exception"].pop("decided_by")
    python, answer = _both(service, document)
    assert python["outcome"] == "error" and answer["code"] == "CheckerUnavailable", (python, answer)
    assert "soft source the soft route rejects" in answer["text"] and python["text"] in answer["text"]


def test_norm_content_beside_a_block_keeps_the_retained_path(service):
    """The norms route reads no alternatives or risk block: norm content beside one is `CheckerUnavailable`."""
    document = _seed("alternatives-cells")
    norm = {"norm": {"name": "r", "predicate": "permitted", "sign": True, "guard": ["top"], "unless": [],
                     "over": []}}
    document["front"]["units"][0].update(kind="norm", content=norm)
    _, answer = _both(service, document)
    assert answer["code"] == "CheckerUnavailable" and "beside a block" in answer["text"], answer


# ------------------------------------------------------------------------- the answer's fields: typed, bound

def _row(name: str):
    text = _text(_seed(name))
    raw = text.encode()
    row = D._lean_answer(raw, True)
    meta, source, _ = D._split(raw)
    return text, raw, row, meta, source, list(D._parts(meta["units"]))


def _leaves(value, path):
    yield path, value
    if type(value) is dict:
        for key, child in value.items():
            yield from _leaves(child, (*path, key))
    elif type(value) is list:
        for index, child in enumerate(value):
            yield from _leaves(child, (*path, index))


def _replace(row, path, value):
    changed = deepcopy(row)
    target = changed
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return changed


@pytest.mark.parametrize("name", ["soft-norms", "norms-content"])
def test_every_unit_field_is_typed_and_every_row_bound(name):
    text, raw, row, meta, source, declared = _row(name)
    case = Context({"id": "document", "document": text, "admit": True})
    schema = ROWS["document"][0]
    schema(row, case, {})
    retyped = 0
    for index, unit in enumerate(row["units"]):
        for path, value in _leaves(unit, ("units", index)):
            for wrong in ({7: True, True: 7}.get(value, 7) if type(value) in (int, bool) else 7, None, [], {}):
                if wrong == value and type(wrong) is type(value):
                    continue
                changed = _replace(row, path, wrong)
                retyped += 1
                try:
                    schema(changed, case, {})
                except Invalid:
                    continue
                with pytest.raises((ValueError, CheckerUnavailable), match="not bound|disagrees"):
                    D._bind_document_answer(source, meta, declared, changed)
    assert retyped >= 80


@pytest.mark.parametrize("name", ["soft-norms", "norms-content"])
def test_an_empty_extra_or_duplicated_unit_row_is_refused(name):
    text, raw, row, meta, source, declared = _row(name)
    for units in ([], row["units"] + [deepcopy(row["units"][0])], row["units"][:-1],
                  [row["units"][0]] + row["units"][:-1]):
        with pytest.raises(ValueError, match="disagrees"):
            D._bind_document_answer(source, meta, declared, {**row, "units": units})


@pytest.mark.parametrize("member", ["name", "predicate", "sign", "over", "mode", "exception"])
def test_a_forged_but_typed_soft_norm_is_refused_by_the_binding(member):
    text, raw, row, meta, source, declared = _row("soft-norms")
    forged = deepcopy(row)
    norm = forged["units"][0]["content"]["norm"]
    norm[member] = {"name": "forged", "predicate": "consents", "sign": False, "over": ["absent"], "mode": "strict",
                    "exception": {"decided_by": "forged", "sufficient": [], "necessary": [], "factors": []}}[member]
    try:
        ROWS["document"][0](forged, Context({"id": "document", "document": text, "admit": True}), {})
    except Invalid:
        return  # the canonical form's own type refuses it (a strict `mode` is omitted)
    with pytest.raises(ValueError, match="disagrees"):
        D._bind_document_answer(source, meta, declared, forged)


@pytest.mark.parametrize("path, value", [(("guard", 2, 1), 7), (("guard", 1), "in_finance"),
                                         (("unless",), [["top"]])], ids=["index", "predicate", "carve-out"])
def test_a_changed_rule_formula_is_refused_by_the_binding(path, value):
    """Lean's re-encoding of a rule it accepted is the rule as written: a changed guard or carve-out list, which the
    schema types, is not bound."""
    text, raw, row, meta, source, declared = _row("soft-norms")
    forged = deepcopy(row)
    target = forged["units"][0]["content"]["norm"]
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    ROWS["document"][0](forged, Context({"id": "document", "document": text, "admit": True}), {})
    with pytest.raises(ValueError, match="disagrees"):
        D._bind_document_answer(source, meta, declared, forged)


def test_a_soft_meaning_id_is_bound_to_the_extended_environment(monkeypatch, tmp_path):
    """Every content of a soft-norms document is bound to `E″` (`soft_document.extended_env`): its id over the
    document's own environment, or a changed one, is not bound to the document sent."""
    text, raw, row, meta, source, declared = _row("soft-norms")
    path = tmp_path / "document.ve.md"
    path.write_text(text)
    env = D._environment(meta["environment"])
    for index in range(len(row["units"])):
        unit = row["units"][index]
        for forged_id in (D.rights_meaning_id(env, unit["content"]),
                          hashlib.sha256(unit["meaning_id"].encode()).hexdigest()):
            assert forged_id != unit["meaning_id"]
            forged = deepcopy(row)
            forged["units"][index]["meaning_id"] = forged_id
            monkeypatch.setattr(relay, "answer", lambda *_, forged=forged: (forged, None))
            with pytest.raises(CheckerUnavailable, match="not bound to the document sent"):
                D.load_document(path)


# ------------------------------------------------------------------------------- the environment mode's faults

@pytest.mark.parametrize("change", ["renamed key", "missing language", "unknown profile", "unsorted profiles",
                                    "block without its profile"])
def test_an_environment_fault_is_the_environment_mode_s(service, change):
    document = _seed("plain")
    environment = document["front"]["environment"]
    if change == "renamed key":
        environment["PROFILES"] = environment.pop("profiles")
    elif change == "missing language":
        environment["l\tanguage"] = environment.pop("language")
    elif change == "unknown profile":
        environment["profiles"] = sorted([*environment["profiles"], "relational-fol@0’"])
    elif change == "unsorted profiles":
        environment["profiles"] = ["relational-fol@0", "NORMS@0"]
    else:
        environment["alternatives"] = {}
    python, answer = _both(service, document)
    assert answer["outcome"] == "error" and answer["code"] != "CheckerUnavailable", answer
    assert dw.verdict(python, answer) == "agree" and dw.environment_error(_text(document)) == answer["text"]


def test_a_soft_or_rights_environment_keeps_its_route_s_order(service):
    """Python's loader checks a soft source (`check_soft_source`) or a rights environment before `Environment`:
    the environment mode's fault is not the document's there, so the mode answers `CheckerUnavailable`."""
    document = _seed("soft-norms")
    document["front"]["environment"]["PROFILES"] = document["front"]["environment"]["profiles"]
    _, answer = _both(service, document)
    assert answer["code"] == "CheckerUnavailable", answer


# ------------------------------------------------------------------------------- located diagnostics

def _refused_model(document: dict, set_index: int, model_index: int, change):
    reading_set = document["front"]["reading_sets"][set_index]
    name = list(reading_set["models"])[model_index]
    change(reading_set["models"][name])
    return document


def _arity(model):
    model["relations"]["in_finance"] = [["a", "b"]]


def _null(model):
    model["relations"]["in_finance"] = None


@pytest.mark.parametrize("change", [_arity, _null], ids=["arity", "null"])
def test_a_refused_distinguishing_model_is_lean_s_located_diagnostic(service, change):
    document = _refused_model(_seed("reading-sets"), 1, 0, change)
    python, answer = _both(service, document)
    assert answer["code"] == "InvalidModel" and answer["path"].startswith("/relations/in_finance"), answer
    assert dw.verdict(python, answer) == "agree", (python, answer)


def test_two_refused_models_of_one_set_keep_the_retained_path(service):
    """A JSON object here has no authored order: with two refused models the first is not known, so the mode
    answers `CheckerUnavailable` (`locatedModel`)."""
    document = _refused_model(_seed("reading-sets"), 0, 0, _arity)
    document = _refused_model(document, 0, 1, _arity)
    _, answer = _both(service, document)
    assert answer["code"] == "CheckerUnavailable" and "distinguishing model" in answer["text"], answer


def _forged_error(monkeypatch, **located):
    """`relay.answer` with the error's location replaced (`path` or `span`)."""
    real = relay.answer

    def forged(mode, case):
        row, error = real(mode, case)
        for key, value in located.items():
            setattr(error, key, value)
        return row, error
    monkeypatch.setattr(relay, "answer", forged)


@pytest.mark.parametrize("path", ["/relations/absent", "/relations/in_finance/9", "/relations/in_finance/00",
                                  "relations", "/models", "/relations/in_finance/٠"])
def test_a_model_path_is_bound_to_a_member_of_a_model_of_the_document(monkeypatch, tmp_path, path):
    document = _refused_model(_seed("reading-sets"), 1, 0, _arity)
    target = tmp_path / "document.ve.md"
    target.write_text(_text(document))
    with pytest.raises(VEError) as raised:
        D.load_document(target)
    assert raised.value.path == "/relations/in_finance/0"
    _forged_error(monkeypatch, path=path)
    with pytest.raises(CheckerUnavailable, match="names no member of a distinguishing model"):
        D.load_document(target)


def test_a_strict_fence_s_syntax_error_has_the_parse_mode_s_span(service):
    python, answer = _both(service, _seed("fence"))
    assert answer["code"] == "SyntaxError" and answer["span"] == {"start": 0, "end": 1, "line": 1, "column": 1}
    assert dw.verdict(python, answer) == "agree", (python, answer)


@pytest.mark.parametrize("span", [(1, 1, 1, 1), (0, 1, 2, 1), (0, 1, 1, 2), (0, 99, 1, 1), (2, 1, 1, 3)])
def test_a_fence_span_is_bound_to_a_strict_fence_of_the_document(monkeypatch, tmp_path, span):
    from ve.errors import Span
    target = tmp_path / "document.ve.md"
    target.write_text(_text(_seed("fence")))
    _forged_error(monkeypatch, span=Span(*span))
    with pytest.raises(CheckerUnavailable, match="span is in no strict fence"):
        D.load_document(target)


def test_a_fence_span_without_a_strict_fence_is_unbound(monkeypatch, tmp_path):
    document = _seed("fence")
    document["front"]["units"][0]["surface"] = "english"
    target = tmp_path / "document.ve.md"
    target.write_text(_text(document))
    real = relay.answer

    def forged(mode, case):
        from ve.errors import Span, SyntaxError as VESyntaxError
        row, _ = real(mode, case)
        return row, VESyntaxError("SyntaxError: expected term", span=Span(0, 1, 1, 1))
    monkeypatch.setattr(relay, "answer", forged)
    with pytest.raises(CheckerUnavailable, match="span is in no strict fence"):
        D.load_document(target)


def test_the_located_error_rows_are_typed(service):
    """The response schema types a located row's `path` (a string) and `span` (four naturals): any other value is
    refused by the transport."""
    schema = ROWS["document"][0]
    case = Context({"id": "d", "document": "x"})
    schema({"id": "d", "status": "error", "error": "SyntaxError: x", "span": {"start": 0, "end": 1, "line": 1,
                                                                          "column": 1}}, case, {})
    schema({"id": "d", "status": "error", "error": "InvalidModel: x", "path": "/a"}, case, {})
    for bad in ({"start": True, "end": 1, "line": 1, "column": 1}, {"start": -1, "end": 1, "line": 1, "column": 1},
                {"start": 0, "end": 1, "line": 1}, {"start": 0, "end": 1, "line": 1, "column": 1, "x": 0},
                {"start": "0", "end": 1, "line": 1, "column": 1}, [0, 1, 1, 1], None):
        with pytest.raises(Invalid):
            schema({"id": "d", "status": "error", "error": "SyntaxError: x", "span": bad}, case, {})
    for bad in (7, True, None, [], {}):
        with pytest.raises(Invalid):
            schema({"id": "d", "status": "error", "error": "InvalidModel: x", "path": bad}, case, {})
    with pytest.raises(Invalid):
        schema({"id": "d", "status": "error", "error": "", "path": "/a", "span": {"start": 0, "end": 1, "line": 1,
                                                                                 "column": 1}}, case, {})
