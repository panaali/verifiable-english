"""Lean-first batch 16b: `ve-document@1` documents are checked by the Lean `document` mode.

One test (or one parametrised group) per behaviour the switch claims: Lean decides every document it owns and
Python builds the document from its answer without its own loader; Lean's rejection is raised verbatim; an
answer Lean marks as undecided (`CheckerUnavailable`, `ResourceLimit`) and a text the mode cannot be sent take
Python's retained path; a failure of the service is never answered by Python; the answer is bound to the request
before anything is built from it; identities and checked content come from Lean; `load_document` does not admit
the claim graph while `check_document` does; and an admission route that rejects what Lean admitted is
`CheckerUnavailable`. The retained reasons are the rows of docs/lean-first/b16b/DELTA.md.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re

import pytest

from conformance import document_wrapper as dw
from ve import document as D
from ve.backends import relay
from ve.backends.lean_service import CheckerUnavailable
from ve.errors import VEError
from ve.search import model_search_scope

ROOT = Path(__file__).resolve().parents[1]
DELTA = ROOT / "docs/lean-first/b16b/DELTA.md"
GENERATED = dict(dw._generated())
# The generated seeds the Lean mode owns (everything but the fenced one), each with a nonzero residual somewhere.
OWNED = ["plain", "mixed", "open-terms", "reading-sets", "graph-bridge", "graph-readings", "definitions",
         "p0-envelope", "alternatives-cells", "alternatives-graph", "risk"]


def write(tmp_path, text, name="document.ve.md"):
    path = tmp_path / name
    path.write_bytes(text.encode("utf-8") if type(text) is str else text)
    return path


def outcome(call):
    try:
        with model_search_scope():
            return {"returned": json.loads(json.dumps(call(), default=str))}
    except (VEError, CheckerUnavailable) as exc:
        return {"raised": [type(exc).__name__, getattr(exc, "message", str(exc))]}


def python_path(path):
    """Python's retained path on a document: its own loader, then the report or the coverage."""
    def check():
        doc = D._load_document(path.read_bytes(), path, None)
        return D._report(doc)
    return check


@pytest.fixture
def no_python_loader(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("Python's own document loader ran on a document Lean owns")
    monkeypatch.setattr(D, "_load_document", refuse)


# ---------------------------------------------------------------- Lean decides what it owns

@pytest.mark.parametrize("name", OWNED)
def test_owned_documents_are_decided_by_lean(tmp_path, name, monkeypatch):
    path = write(tmp_path, dw.text_of(GENERATED[name]))
    expected = outcome(python_path(path)), outcome(lambda: D.coverage(D._load_document(path.read_bytes(), path, None)))
    assert D._lean_answer(path.read_bytes(), True) is not None
    monkeypatch.setattr(D, "_load_document", lambda *a, **k: (_ for _ in ()).throw(AssertionError("retained path")))
    head = outcome(lambda: D.check_document(path)), outcome(lambda: D.coverage(D.load_document(path)))
    assert head == expected
    assert "lean" in D.load_document(path)
    assert D.render_document(path)


def test_coverage_and_statuses_are_leans(tmp_path, no_python_loader, monkeypatch):
    path = write(tmp_path, dw.text_of(GENERATED["reading-sets"]))
    row = D._lean_answer(path.read_bytes(), False)
    doc = D.load_document(path)
    assert D.coverage(doc) == row["coverage"]
    assert [(u["id"], u["span"], u["status"]) for u in doc["units"]] == [
        (u["id"], u["span"], u["status"]) for u in row["units"]]
    # Lean owns the result, while the receiver checks its request-bound arithmetic.
    forged = deepcopy(row)
    forged["coverage"]["residual"]["assumptions"] = 99
    monkeypatch.setattr(relay, "answer", lambda mode, case: (forged, None))
    with pytest.raises(CheckerUnavailable, match="not bound to the document sent"):
        D.load_document(path)


def test_identities_and_content_are_leans(tmp_path, no_python_loader, monkeypatch):
    path = write(tmp_path, dw.text_of(GENERATED["plain"]))
    row = D._lean_answer(path.read_bytes(), False)
    forged = deepcopy(row)
    for field in ("document_id", "source_id"):
        mutant = deepcopy(row)
        mutant[field] = "a" * 64
        monkeypatch.setattr(relay, "answer", lambda mode, case, mutant=mutant: (mutant, None))
        with pytest.raises(CheckerUnavailable, match="not bound to the document sent"):
            D.load_document(path)
    forged["units"][0]["meaning_id"] = "c" * 64
    monkeypatch.setattr(relay, "answer", lambda mode, case: (forged, None))
    with pytest.raises(CheckerUnavailable, match="not bound to the document sent"):
        D.load_document(path)
    # Python's own computation of the same identities agrees with Lean's on the genuine answer.
    monkeypatch.undo()
    doc = D.load_document(path)
    assert doc["units"][0]["content"] == row["units"][0]["content"]
    python = D._load_document(path.read_bytes(), path, None)
    assert (python["document_id"], python["source_id"]) == (row["document_id"], row["source_id"])
    assert [(u["content"], u["meaning_id"]) for u in python["units"]] == [
        (u.get("content"), u.get("meaning_id")) for u in row["units"]]


# ---------------------------------------------------------------- Lean's rejection is final

def test_lean_rejections_are_raised_verbatim(tmp_path, no_python_loader):
    text = dw.text_of(GENERATED["plain"])
    gap = text.replace('"span": [0, 7]', '"span": [0, 6]')
    assert gap != text
    with pytest.raises(VEError) as caught:
        D.check_document(write(tmp_path, gap))
    assert caught.value.message == "unit spans must partition every source byte in order"
    # An environment fault: the text is the Lean decoder's own (Python's `Environment` words it otherwise).
    front = dw.split_text(text)
    del front["front"]["environment"]["vocabulary"]["sorts"]["person"]["description"]
    path = write(tmp_path, dw.text_of(front))
    with pytest.raises(VEError) as caught:
        D.load_document(path)
    assert caught.value.message == "fields do not match: expected [description], got []"
    assert getattr(caught.value, "backend_rejection", False) is True


# ---------------------------------------------------------------- undecided answers take the retained path

def _order_document():
    return next(doc for name, doc in dw.seeds() if "order@0" in json.dumps(doc["front"].get("environment")))


# {the mode's reason: (its row in DELTA.md, a document it answers so)}
RETAINED = {
    "fenced English or strict content needs the Lean surface parser": (
        "fenced English or strict content needs the Lean surface parser", lambda: dw.text_of(GENERATED["fence"])),
    "document checks under order@0 need its Lean profile route": (
        "document checks under {profile} need its Lean profile route", lambda: dw.text_of(_order_document())),
    "front matter outside the restricted JSON reader": (
        "front matter outside the restricted JSON reader", lambda: dw.text_of(
            {**GENERATED["plain"], "front": {**GENERATED["plain"]["front"],
                                             "weights": [{"set": "s", "by": "a", "values": {"x": 1.5}}]}})),
    "a document with senses is read by the Lean senses route": (
        "a document with senses is read by the Lean senses route", lambda: dw.text_of(
            {**GENERATED["plain"], "front": {**GENERATED["plain"]["front"], "senses": {}}})),
}


@pytest.mark.parametrize("reason", sorted(RETAINED))
def test_undecided_answers_take_the_retained_path(tmp_path, reason, monkeypatch):
    listed, build = RETAINED[reason]
    path = write(tmp_path, build())
    row, error = relay.answer("document", {"id": "d", "document": path.read_text(), "admit": True})
    assert isinstance(error, CheckerUnavailable) and reason in error.message
    assert f"| {listed} |" in DELTA.read_text(), "every retained reason is a row of the batch's DELTA.md"
    expected = outcome(python_path(path))
    calls = []
    original = D._load_document
    monkeypatch.setattr(D, "_load_document", lambda *a: calls.append(a) or original(*a))
    assert outcome(lambda: D.check_document(path)) == expected
    assert len(calls) == 1


def test_resource_limit_answer_takes_the_retained_path(tmp_path, monkeypatch):
    from ve.errors import ResourceLimit
    path = write(tmp_path, dw.text_of(GENERATED["plain"]))
    monkeypatch.setattr(relay, "answer", lambda mode, case: ({"id": "d", "status": "error", "error": "x"},
                                                             ResourceLimit("ResourceLimit: x")))
    assert D._lean_answer(path.read_bytes(), True) is None
    assert outcome(lambda: D.check_document(path)) == outcome(python_path(path))


def test_a_text_that_is_not_utf8_takes_the_retained_path(tmp_path, monkeypatch):
    text = dw.text_of(GENERATED["plain"]).encode("utf-8").replace("Café".encode(), b"Caf\xe9!")
    path = write(tmp_path, text)
    monkeypatch.setattr(relay, "answer", lambda *a: (_ for _ in ()).throw(AssertionError("sent")))
    assert D._lean_answer(path.read_bytes(), True) is None
    assert outcome(lambda: D.check_document(path)) == outcome(python_path(path))


def test_a_service_failure_is_never_answered_by_python(tmp_path, no_python_loader, monkeypatch):
    path = write(tmp_path, dw.text_of(GENERATED["plain"]))

    def down(self, mode, cases, **kwargs):
        raise CheckerUnavailable("CheckerUnavailable: ve_service: no answer within 1 s (mode document)")
    monkeypatch.setattr(type(relay._pool_for(None)), "run_bound", down)
    for call in (D.check_document, D.load_document, D.render_document):
        with pytest.raises(CheckerUnavailable, match="no answer within"):
            call(path)


# ---------------------------------------------------------------- the answer is bound to the request

def _mutants(row):
    def edit(change):
        copy = deepcopy(row)
        change(copy)
        return copy
    yield "source", edit(lambda r: r.update(source=r["source"] + "x"))
    yield "dropped unit", edit(lambda r: r["units"].pop())
    yield "duplicated unit", edit(lambda r: r["units"].append(deepcopy(r["units"][-1])))
    yield "renamed unit", edit(lambda r: r["units"][0].update(id="zz"))
    yield "reordered units", edit(lambda r: r["units"].reverse())
    yield "parent added", edit(lambda r: r["units"][0].update(parent_id="p"))
    yield "content dropped", edit(lambda r: (r["units"][0].pop("content"), r["units"][0].pop("meaning_id")))
    yield "meaning id dropped", edit(lambda r: r["units"][0].pop("meaning_id"))
    yield "content added", edit(lambda r: r["units"][-1].update(content=["top"], meaning_id="d" * 64))
    for field, replacement in (("span", [0, 1]), ("kind", "changed_kind"),
                               ("meaning", {"contextual": "changed"}), ("support", "changed_support")):
        yield field, edit(lambda r, field=field, replacement=replacement:
                          r["units"][0].update({field: replacement}))
    for field, replacement in (("source_bytes", 0), ("accounted_bytes", 0),
                               ("coverage_percent", 0), ("bytes_by_kind", {}),
                               ("bytes_by_status", {}), ("unformalised_reasons", {"fake": 1}),
                               ("residual_total", 99)):
        yield field, edit(lambda r, field=field, replacement=replacement:
                          r["coverage"].update({field: replacement}))
    yield "residual count", edit(lambda r: r["coverage"]["residual"].update(assumptions=99))
    yield "boolean count", edit(lambda r: r["coverage"].update(accounted_bytes=True))


def test_answers_not_bound_to_the_request_are_unavailable(tmp_path, no_python_loader, monkeypatch):
    path = write(tmp_path, dw.text_of(GENERATED["plain"]))
    row = D._lean_answer(path.read_bytes(), True)
    for name, mutant in _mutants(row):
        monkeypatch.setattr(relay, "answer", lambda mode, case, mutant=mutant: (mutant, None))
        try:
            D.check_document(path)
        except CheckerUnavailable as exc:
            assert "not bound to the document sent" in str(exc), name
        else:
            pytest.fail(f"accepted mutated {name}")


@pytest.mark.parametrize("name", ["alternatives-cells", "risk"])
def test_alternatives_coverage_is_bound_to_units_and_counts(tmp_path, no_python_loader, monkeypatch, name):
    path = write(tmp_path, dw.text_of(GENERATED[name]))
    row = D._lean_answer(path.read_bytes(), False)
    for change in (
            lambda r: r["coverage"]["residual"].update(alternatives_declared=0),
            lambda r: r["coverage"]["alternatives"]["alternatives_declared"][0].update(unit="unknown"),
            lambda r: r["coverage"]["alternatives"]["alternatives_declared"][0].update(support="none")):
        mutant = deepcopy(row)
        change(mutant)
        monkeypatch.setattr(relay, "answer", lambda mode, case, mutant=mutant: (mutant, None))
        with pytest.raises(CheckerUnavailable, match="not bound to the document sent"):
            D.load_document(path)


def test_a_document_lean_accepted_that_python_cannot_build_is_unavailable(tmp_path, no_python_loader,
                                                                           monkeypatch):
    path = write(tmp_path, dw.text_of(GENERATED["plain"]))
    monkeypatch.setattr(D, "Environment", lambda data: (_ for _ in ()).throw(VEError("no")))
    with pytest.raises(CheckerUnavailable, match="could not be built"):
        D.load_document(path)


# ---------------------------------------------------------------- load against check

def _unadmitted_graph():
    doc = deepcopy(GENERATED["graph-bridge"])
    del doc["front"]["graph"]["nodes"][0]["label"]
    doc["front"]["graph"]["nodes"][0]["ast"] = ["unary", "senior", ["const", "bob"]]
    return dw.text_of(doc)


def test_load_does_not_admit_the_graph_and_check_does(tmp_path, no_python_loader):
    path = write(tmp_path, _unadmitted_graph())
    assert D.load_document(path)["lean"]["admitted"] is False
    assert D.render_document(path)
    assert D.coverage(D.load_document(path))["residual"]["bridge_leaves"] == 0
    with pytest.raises(VEError) as caught:
        D.check_document(path)
    assert re.match(r"AdmissionError: ", caught.value.message)


def test_the_admission_route_rejecting_what_lean_admitted_is_unavailable(tmp_path, no_python_loader,
                                                                          monkeypatch):
    path = write(tmp_path, dw.text_of(GENERATED["graph-bridge"]))
    assert D.check_document(path)["admission"]["report"]
    monkeypatch.setattr(D, "admit_document", lambda env, document: (_ for _ in ()).throw(VEError("refused")))
    with pytest.raises(CheckerUnavailable, match="admission route rejects a claim graph Lean's document mode"):
        D.check_document(path)


def test_python_graph_checks_do_not_run_on_a_lean_admitted_document(tmp_path, no_python_loader, monkeypatch):
    path = write(tmp_path, dw.text_of(GENERATED["graph-readings"]))
    monkeypatch.setattr(D, "_check_narrowing_choices", lambda *a: (_ for _ in ()).throw(AssertionError("ran")))
    assert D.check_document(path)["admission"]["report"]


def test_definitions_graph_is_deferred_as_the_admission_route_defers_it(tmp_path):
    doc = deepcopy(GENERATED["definitions"])
    doc["front"]["graph"] = {"root": "claim", "nodes": [{"name": "claim", "ast": ["top"]}]}
    path = write(tmp_path, dw.text_of(doc))
    row, error = relay.answer("document", {"id": "d", "document": path.read_text(), "admit": True})
    assert isinstance(error, CheckerUnavailable) and "definitions is deferred" in error.message
    with pytest.raises(VEError, match="admission of documents with definitions is deferred"):
        D.check_document(path)


def test_the_cli_and_the_api_give_the_same_answer(tmp_path, capsys):
    for name, document in (("plain", GENERATED["plain"]), ("graph-bridge", GENERATED["graph-bridge"]),
                           ("order", _order_document())):
        path = write(tmp_path, dw.text_of(document), f"{name}.ve.md")
        assert D.main(["check", str(path)]) == 0
        assert json.loads(capsys.readouterr().out) == json.loads(json.dumps(D.check_document(path), default=str))
        assert D.main(["coverage", str(path)]) == 0
        assert json.loads(capsys.readouterr().out) == D.coverage(D.load_document(path))
