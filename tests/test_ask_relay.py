"""The relay of Lean's `ask` answer (docs/spec/question-answering.md 8; build checklist 4, 5; DRI ruling R8).

Python checks two things of an answer, and decides nothing: (a) it is fully typed, by the schema generated from
Lean's shapes (`ve/backends/lean_service_schema/ask.json`, `service_schema.check_row`), and (b) it is bound to the
request (`ve.ask.answer_problem`): every row names a choice of the request's open sets, once; every line's
readings, witness, source and quote name what the request has; the text is the lines' text; the unused units are
the document's; the unchecked names are the request's; the identities are the request's. These tests take genuine
recorded answers of the three routes and retype, drop, empty, duplicate and rebind each field: each mutant must be
refused by (a) or (b), and the genuine answer accepted by both.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

from ve import ask
from ve.backends import service_schema

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("ask_fixtures", ROOT / "tools/ask_fixtures.py")
AF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AF)

RETYPES = [7, True, None, [], {}, "x", 1.5]
NULLABLE = {"reason", "witness", "source", "quote"}


def bound(ident):
    """A recorded answer with the request and the binding context the relay checks it against (`ask.binding`)."""
    from ve.document import load_document
    entry = AF.load(ident)
    path = ROOT / entry["path"]
    raw = path.read_bytes()
    lexicon, _ = ask._identities(raw, entry["question"], load_document(path))
    request = {"id": "ask", "document": raw.decode("utf-8"), "question": entry["question"], "lexicon": lexicon,
               "case": entry["case"], "names": entry["names"]}
    context, expected = ask.binding(path, raw, request)
    assert context["_route"] == entry["result"]["route"]
    return entry["result"], {**request, **context}, expected


@pytest.fixture(scope="module")
def answers():
    return {ident: bound(ident) for ident in ("G1", "G3", "U3", "U5", "A1")}


def refused(result, request, expected) -> bool:
    """Refused by the schema or by the binding."""
    row = {"id": "ask", "status": "ok", "result": result}
    try:
        service_schema.check_row("ask", row, {"id": "ask"}, 0)
    except service_schema.Invalid:
        return True
    return ask.answer_problem(result, request, expected) is not None


def paths(value, prefix=()):
    """Every path of a JSON value, leaves and containers alike."""
    yield prefix
    if isinstance(value, dict):
        for k, v in value.items():
            yield from paths(v, prefix + (k,))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from paths(v, prefix + (i,))


def setting(value, path, new):
    out = copy.deepcopy(value)
    target = out
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = new
    return out


def dropping(value, path):
    out = copy.deepcopy(value)
    target = out
    for key in path[:-1]:
        target = target[key]
    del target[path[-1]]
    return out


@pytest.mark.parametrize("ident", ["G1", "G3", "U3", "U5"])
def test_a_genuine_answer_is_accepted(answers, ident):
    result, request, expected = answers[ident]
    assert not refused(result, request, expected)


@pytest.mark.parametrize("ident", ["G1", "U3"])
def test_every_field_retyped_is_refused(answers, ident):
    """Each node of the answer replaced by each value of another type (a bool for an int, null for a value, a list
    or an object for a string, a float for an index): refused. Same-type changes are the rebinding test's; null in a
    nullable slot (a row's reason, a line's witness, source and quote) is a value of that slot's type."""
    result, request, expected = answers[ident]
    checked = 0
    for path in paths(result):
        if not path:
            continue
        old = result
        for key in path:
            old = old[key]
        for new in RETYPES:
            if type(new) is type(old):
                continue
            if path[-1] in NULLABLE and (new is None or (old is None and type(new) in (list, dict))):
                continue  # null fits the slot; a list or an object in place of null may be its type (`[]` is
                # the one choice of a one-choice route)
            mutant = setting(result, path, new)
            assert refused(mutant, request, expected), (ident, path, new)
            checked += 1
    assert checked > 100


@pytest.mark.parametrize("ident", ["G1", "U3"])
def test_every_field_dropped_is_refused(answers, ident):
    result, request, expected = answers[ident]
    for path in paths(result):
        if not path or isinstance(path[-1], int):
            continue
        assert refused(dropping(result, path), request, expected), (ident, path)


def rebinds(result):
    """Mutants that keep every type and name something the request does not have, or break a count."""
    out = {}
    r = result
    out["no row"] = setting(r, ("rows",), [])
    out["a repeated row"] = setting(r, ("rows",), r["rows"] + r["rows"][:1])
    out["a lead unknown to the shape"] = setting(r, ("lead",), "maybe")
    out["another route"] = setting(r, ("route",), "plain" if r["route"] != "plain" else "readings")
    out["another sentence"] = setting(r, ("sentence",), "every member is happy.")
    out["another formula"] = setting(r, ("ast",), ["unary", "verified", ["const", "bo"]])
    out["text not the lines'"] = setting(r, ("text",), r["text"][:-1])
    out["an unused unit not the document's"] = setting(r, ("unused",), r["unused"] + ["zz9"])
    out["an unused unit twice"] = setting(r, ("unused",), r["unused"] + r["unused"][:1]) if r["unused"] else None
    for key, value in r["identities"].items():
        # Build checklist 15: every identity field is bound; a changed one is another request's answer.
        out[f"another {key}"] = setting(r, ("identities", key), value[:-1] + ("0" if value[-1:] != "0" else "1"))
    for i, row in enumerate(r["rows"]):
        if row["choice"]:
            out[f"row {i}: a set the request lacks"] = setting(r, ("rows", i, "choice", 0, 0), "rs_zz")
            out[f"row {i}: a reading the set lacks"] = setting(r, ("rows", i, "choice", 0, 1), 99)
            out[f"row {i}: a set dropped"] = setting(r, ("rows", i, "choice"), row["choice"][1:])
        else:
            out[f"row {i}: a choice on a one-choice route"] = setting(r, ("rows", i, "choice"), [["rs_zz", 0]])
        out[f"row {i}: a reason without unknown"] = setting(r, ("rows", i, "reason"), "X4") \
            if row["lead"] != "unknown" else setting(r, ("rows", i, "reason"), None)
        out[f"row {i}: a cited unit not the document's"] = setting(
            r, ("rows", i, "cited"), row["cited"] + [{"kind": "unit", "unit": "zz9"}])
        out[f"row {i}: a cited act not declared"] = setting(
            r, ("rows", i, "cited"), row["cited"] + [{"kind": "rules", "predicate": "zz_act"}])
        out[f"row {i}: a gap of an undeclared act"] = setting(r, ("rows", i, "gaps"), [["zz_act", ["e0"], False]])
        if row["gaps"]:
            act, ids, value = row["gaps"][0]
            out[f"row {i}: a gap naming an element no model has"] = setting(
                r, ("rows", i, "gaps", 0), [act, ids[:-1] + ["zz_el"], value])
        if row["cited"]:
            out[f"row {i}: a source cited twice"] = setting(r, ("rows", i, "cited"), row["cited"] + row["cited"][:1])
    for i, line in enumerate(r["lines"]):
        if line["quote"] is not None:
            unit = line["quote"][0]
            out[f"line {i}: a quote not from its unit"] = setting(r, ("lines", i, "quote"), [unit, "zz not quoted"])
            out[f"line {i}: an empty quote"] = setting(r, ("lines", i, "quote"), [unit, ""])
        out[f"line {i}: a reading the request does not name"] = setting(r, ("lines", i, "readings"), [["rs_zz", 0]])
        out[f"line {i}: a witness no row has"] = setting(r, ("lines", i, "witness"), [["rs_zz", 0]])
        out[f"line {i}: a quote of a unit not the document's"] = setting(r, ("lines", i, "quote"), ["zz9", "x"])
        out[f"line {i}: a source not the document's"] = setting(r, ("lines", i, "source"), {"kind": "unit", "unit": "zz9"})
        out[f"line {i}: no text"] = setting(setting(r, ("lines", i, "text"), ""), ("text", i), "")
    out["an unchecked name the request lacks"] = setting(r, ("unchecked_names",), [{"set": "rs_zz", "index": 0, "text": "x"}])
    if r["unchecked_names"]:
        out["an unchecked name twice"] = setting(r, ("unchecked_names",), r["unchecked_names"] + r["unchecked_names"][:1])
    return {k: v for k, v in out.items() if v is not None}


@pytest.mark.parametrize("ident", ["G1", "G3", "U3", "U5", "A1"])
def test_every_id_rebound_is_refused(answers, ident):
    result, request, expected = answers[ident]
    mutants = rebinds(result)
    assert len(mutants) > 15
    for name, mutant in mutants.items():
        assert refused(mutant, request, expected), (ident, name)


def test_the_relay_refuses_a_malformed_answer_from_the_service(monkeypatch):
    """The relay itself (`ve.ask._ask`) refuses an answer the binding refuses: CheckerUnavailable, never a lead."""
    from ve.backends import relay
    from ve.errors import CheckerUnavailable
    result, request, expected = bound("G1")
    wrong = setting(result, ("rows", 0, "cited"), [{"kind": "unit", "unit": "zz9"}])
    monkeypatch.setattr(relay, "decide_once", lambda mode, case: {"id": "ask", "status": "ok", "result": wrong})
    plain = {k: v for k, v in request.items() if not k.startswith("_")}
    context = {k: v for k, v in request.items() if k.startswith("_")}
    with pytest.raises(CheckerUnavailable, match="malformed"):
        ask._ask(plain, context, expected)


def _u3(edit):
    entry = copy.deepcopy(AF.load("U3"))
    edit(entry)
    return entry


@pytest.mark.parametrize("name, edit, match", [
    ("a name missing", lambda e: e["names"].pop(), "one per candidate"),
    ("a name extra", lambda e: e["names"].append({"set": "rs_u096", "index": 2, "text": "x"}), "one per candidate"),
    ("names out of order", lambda e: e["names"].reverse(), "one per candidate"),
    ("a name retyped", lambda e: e["names"][0].__setitem__("index", "0"), None),
    ("a name with another field", lambda e: e["names"][0].__setitem__("note", "x"), None),
    ("an asserted name that is not its reading", lambda e: e["names"][3].__setitem__(
        "text", "Every person is classified as \"has_the_right_to_form_and_join_trade_unions\""),
     "could not check the wording of a reading of sentence 10"),
    ("an evidence entry twice", lambda e: e["case"]["evidence"].append(e["case"]["evidence"][0]), "names no compatible"),
    ("an evidence entry for no compatible choice", lambda e: e["case"]["evidence"][0].__setitem__(
        "choice", [["rs_u087", 0], ["rs_u096", 7]]), "names no compatible"),
])
def test_lean_refuses_a_request_not_bound_to_its_document(name, edit, match):
    """Lean's own binding (`decodeNames`, `evidenceBound`): every name and evidence entry names a candidate or a
    compatible choice the document has, once; an asserted reading's name reads back to it."""
    from ve.errors import CheckerUnavailable, VEError
    with pytest.raises((VEError, CheckerUnavailable), match=match):
        AF.replay(_u3(edit))


def test_a_broken_split_is_not_a_split():
    """A split whose "false" filling is its "true" filling is not checked: the row is not "not settled"."""
    def edit(entry):
        for ev in entry["case"]["evidence"]:
            if "split" in ev:
                ev["split"]["false"] = ev["split"]["true"]
    entry = _u3(edit)
    assert any("split" in ev for ev in entry["case"]["evidence"])
    rows = AF.replay(entry)["rows"]
    assert all(row["lead"] != "notSettled" for row in rows)


def test_a_split_whose_fillings_differ_in_a_base_atom_is_not_a_split():
    """Plan Q2.2: a split is one base situation with two fillings of its gaps; a "false" filling that also changes a
    base atom (here `has_the_right_to_education` of the model's person) is not checked, so no row is not settled."""
    def edit(entry):
        for ev in entry["case"]["evidence"]:
            if "split" in ev:
                model = ev["split"]["model"]
                [person] = model["domains"]["person"]
                held = model["relations"]["has_the_right_to_education"]
                ev["split"]["false"]["has_the_right_to_education"] = [] if held else [[person]]
    entry = _u3(edit)
    rows = AF.replay(entry)["rows"]
    assert rows and all(row["lead"] != "notSettled" for row in rows)
    assert {row["lead"] for row in AF.replay(AF.load("U3"))["rows"]} >= {"notSettled"}


def test_a_fence_that_reads_as_two_formulas_is_not_the_cases_unit():
    """Plan Q2.2 (5.2 `UnitBound`): an English fence compiles to exactly one formula. The G document sent with its
    `g3` fence holding two sentences no longer binds the recorded case, whose `g3` is one formula."""
    from ve.backends import relay
    from ve.errors import CheckerUnavailable
    request = _request("G1")
    fence = "```ve g3\nAnn is verified.\n```"
    assert request["document"].count(fence) == 1
    request["document"] = request["document"].replace(fence, "```ve g3\nAnn is verified. Bo is verified.\n```")
    with pytest.raises(CheckerUnavailable, match="the case is not this document's"):
        relay.decide_once("ask", request)


def _deep(depth):
    value = []
    for _ in range(depth):
        value = [value]
    return value


def _request(ident):
    result, request, expected = bound(ident)
    return {k: v for k, v in request.items() if not k.startswith("_")}


def test_a_malformed_request_is_refused_never_answered():
    """Build checklist 5: each field of the request, and each field of its case, replaced by 7, true, null, [], {}
    or a 10,000-deep list: Lean refuses (a VE error, `CheckerUnavailable` or `ResourceLimit`), never an answer and
    never a crash of the relay."""
    from ve.backends import relay
    from ve.errors import CheckerUnavailable, ResourceLimit, VEError
    tried = 0
    for ident in ("G1", "U3", "A5"):
        request = _request(ident)
        slots = [(k,) for k in request] + [("case", k) for k in request["case"]]
        for path in slots:
            for new in (7, True, None, [], {}, _deep(10_000)):
                mutant = setting(request, path, new)
                if mutant == request:
                    continue
                empty = new in ([], {}) and type(new) is type(request["case"]["evidence"])
                if path == ("case", "evidence") and empty:
                    # No evidence, of the evidence's own type: Lean checks nothing, so it answers unknown: X2 where a
                    # conflict check is due (its packages are evidence too), else X4.
                    result = relay.decide_once("ask", mutant)["result"]
                    assert result["lead"] == "unknown" and {r["reason"] for r in result["rows"]} <= {"X2", "X4"}
                    continue
                with pytest.raises((VEError, CheckerUnavailable, ResourceLimit)):
                    row = relay.decide_once("ask", mutant)
                    assert row["result"]["status"] != "answered", (ident, path, new)
                    raise VEError(f"refused: {row['result']['status']}")
                tried += 1
    assert tried > 150


def test_the_deadline_bounds_the_whole_answer(monkeypatch):
    """Build checklist 7: the mode's CPU deadline covers the whole request (reading, binding, replay, rendering):
    injected near zero, U3's question is `CheckerUnavailable` naming the mode, never a lead or `ResourceLimit`."""
    from ve.backends import lean_service, relay
    from ve.errors import CheckerUnavailable, ResourceLimit
    monkeypatch.setitem(lean_service.DEADLINES, "ask", (1e-6, 1e-6))
    request = _request("U3")
    request["id"] = "ask-deadline"   # not a request the relay's memo holds
    with pytest.raises(CheckerUnavailable, match="mode ask used more than its deadline") as caught:
        relay.decide_once("ask", request)
    assert not isinstance(caught.value, ResourceLimit)


def _refused(question):
    """G1's request with another question, Lean's genuine result for it, and the identities it is bound to."""
    from ve.backends import relay
    from ve.backends.english_lean import export, identities
    from ve.english import EnglishVocabulary
    result, request, expected = bound("G1")
    plain = {k: v for k, v in request.items() if not k.startswith("_")}
    plain["question"] = question
    raw = plain["document"].encode("utf-8")
    words = EnglishVocabulary(ask.environment(raw), _defer_overlay_refusals=True)
    want = {**identities(ask.environment(raw), question, words, export(words)),
            "document_id": expected["document_id"]}
    context = {k: v for k, v in request.items() if k.startswith("_")}
    return plain, context, want, relay.decide_once("ask", plain)["result"]


def test_leans_refusal_is_raised_with_its_class_and_text(monkeypatch):
    """A question Lean does not read with one meaning: `ask`'s refusal, bound to Lean's question contract
    (`refusal_problem`), is raised as Lean's class with Lean's text; a refusal whose status, code, class, fields or
    identities are not Lean's is CheckerUnavailable."""
    from ve.backends import relay
    from ve.errors import CheckerUnavailable, SyntaxError as VESyntaxError
    plain, context, want, result = _refused("Is a member eligible?")
    assert result["status"] == "indefinite" and result["code"] == "IndefiniteQuestion"
    assert ask.refusal_problem(result, want) is None
    with pytest.raises(VESyntaxError) as raised:
        ask._ask(plain, context, want)
    assert str(raised.value) == result["text"]
    mutants = {"status one": setting(result, ("status",), "one"),
               "another status": setting(result, ("status",), "none"),
               "another code": setting(result, ("code",), "QuestionForm"),
               "another class": setting(result, ("class",), "CheckerUnavailable"),
               "no text": setting(result, ("text",), ""),
               "another identity": setting(result, ("identities", "document_id"), "0" * 64),
               "a field more": {**result, "span": [0, 1]},
               "a field less": {k: v for k, v in result.items() if k != "code"}}
    for name, mutant in mutants.items():
        assert ask.refusal_problem(mutant, want), name
        monkeypatch.setattr(relay, "decide_once", lambda mode, case, m=mutant: {"id": "ask", "status": "ok",
                                                                                "result": m})
        with pytest.raises(CheckerUnavailable, match="malformed"):
            ask._ask(plain, context, want)


def test_the_schema_is_generated_and_types_every_field():
    """`ask.json` has no untyped result: every property of the answered and refused results names a type, a const,
    an enum or a reference (the generated file, `tools/response_schemas.py`)."""
    schema = json.loads((ROOT / "ve/backends/lean_service_schema/ask.json").read_text())

    def typed(node):
        return isinstance(node, dict) and any(k in node for k in ("type", "const", "enum", "$ref", "anyOf", "allOf"))
    for name in ("answered", "refused", "line", "row", "name", "identities"):
        props = schema["$defs"][name]["properties"]
        assert props and all(typed(v) for v in props.values()), name
        assert schema["$defs"][name]["additionalProperties"] is False, name
    ok = schema["row"]["anyOf"][-1]["properties"]["result"]
    assert ok is not True and typed(ok)


def test_the_rows_id_is_typed_and_bound_to_the_case():
    """The row's `id` (Lean's `caseReported`): an answer's is the case's string `id` (`x-equals`), an error row
    echoes the case's `id` value (`x-echo`) and has a non-empty error text; any other `id` is refused by the schema
    before the binding runs."""
    result, _, _ = bound("G1")

    def ok(row, case):
        try:
            service_schema.check_row("ask", row, case, 0)
        except service_schema.Invalid:
            return False
        return True
    assert ok({"id": "ask", "status": "ok", "result": result}, {"id": "ask"})
    for other in ("other", 7, None, ["ask"]):
        assert not ok({"id": other, "status": "ok", "result": result}, {"id": "ask"}), other
    assert ok({"id": 7, "status": "error", "error": "InvalidInput: id"}, {"id": 7})
    assert ok({"id": None, "status": "error", "error": "InvalidInput: id"}, {})
    assert not ok({"id": "ask", "status": "error", "error": "InvalidInput: id"}, {"id": "other"})
    assert not ok({"id": "ask", "status": "error", "error": ""}, {"id": "ask"})


def test_each_binding_has_its_rebound_mutant(answers):
    """The conditional mutants of `rebinds` occur on the fixtures: a source cited twice, a quote not from its unit
    or empty, an unchecked name twice."""
    names = set().union(*(rebinds(answers[ident][0]) for ident in ("G1", "U3")))
    for wanted in ("a source cited twice", "a quote not from its unit", "an empty quote", "an unchecked name twice"):
        assert any(wanted in name for name in names), wanted
