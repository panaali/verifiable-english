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
from functools import lru_cache
import gzip
import json
from pathlib import Path
import re

import pytest

from conformance import document_wrapper as dw
from ve import document as D
from ve.backends import relay
from ve.backends.lean_service import CheckerUnavailable
from ve.errors import VEError

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


def test_null_content_is_absent_on_the_lean_path(tmp_path, monkeypatch):
    doc = deepcopy(GENERATED["plain"])
    doc["front"]["units"][2]["content"] = None
    path = write(tmp_path, dw.text_of(doc))
    expected = outcome(python_path(path))
    row = D._lean_answer(path.read_bytes(), True)
    assert row is not None and "content" not in row["units"][2]
    monkeypatch.setattr(D, "_load_document", lambda *a, **k: (_ for _ in ()).throw(AssertionError("retained path")))
    assert outcome(lambda: D.check_document(path)) == expected


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
    alternate = deepcopy(row)
    env = D.Environment(GENERATED["plain"]["front"]["environment"])
    alternate["units"][0]["content"] = ["top"]
    alternate["units"][0]["meaning_id"] = D.digest(
        f"ve-meaning-{env.identity_version}\n", {"environment_id": env.environment_id, "ast": ["top"]})
    monkeypatch.setattr(relay, "answer", lambda mode, case: (alternate, None))
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


# {name: (seed, edit of the seed's front matter)}: one fault per branch of the mode's Python-order namers
# (`Service.Document.vocabularyFault`, `formulaFault`, `graphFault`), each a class the 16b looprecheck1 found
# relayed with a generic Lean text (`object expected`, `String expected`, `array expected`, `invalid indexed
# formula`, `invalid signature: p`, a raw control character in a quoted name).
def _vocabulary(front):
    return front["environment"]["vocabulary"]


def _rename(table, old, new):
    table[new] = table.pop(old)


NAMED = {
    "constants not an object": ("plain", lambda f: _vocabulary(f).update(constants=7)),
    "predicates not an object": ("plain", lambda f: _vocabulary(f).update(predicates=[])),
    "sorts not an object": ("plain", lambda f: _vocabulary(f).update(sorts="person")),
    "description not a string": ("plain", lambda f: _vocabulary(f)["sorts"]["person"].update(description=7)),
    "description empty": ("plain", lambda f: _vocabulary(f)["predicates"]["senior"].update(description="")),
    "constant description not a string": ("plain", lambda f: _vocabulary(f)["constants"]["bob"].update(
        description=[])),
    "verbalisation empty": ("plain", lambda f: _vocabulary(f)["predicates"]["senior"].update(verbalisation="")),
    "arguments not an array": ("plain", lambda f: _vocabulary(f)["predicates"]["senior"].update(
        arguments="person")),
    "arguments empty": ("plain", lambda f: _vocabulary(f)["predicates"]["senior"].update(arguments=[])),
    "arguments too many": ("plain", lambda f: _vocabulary(f)["predicates"]["senior"].update(
        arguments=["person"] * 3)),
    "argument sort a number": ("plain", lambda f: _vocabulary(f)["predicates"]["senior"].update(arguments=[7])),
    "argument sort a list": ("plain", lambda f: _vocabulary(f)["predicates"]["senior"].update(arguments=[[]])),
    "argument sort with a tab": ("plain", lambda f: _vocabulary(f)["predicates"]["senior"].update(
        arguments=["p\terson"])),
    "constant sort a boolean": ("plain", lambda f: _vocabulary(f)["constants"]["bob"].update(sort=True)),
    "constant sort undeclared": ("plain", lambda f: _vocabulary(f)["constants"]["bob"].update(sort="PERSON")),
    "identifier upper case": ("plain", lambda f: _rename(_vocabulary(f)["sorts"], "person", "PERSON")),
    "identifier with a no-break space": ("plain", lambda f: _rename(_vocabulary(f)["constants"], "bob",
                                                                    "b\u00a0ob")),
    "identifier with a control character": ("plain", lambda f: _rename(_vocabulary(f)["predicates"], "senior",
                                                                       "senior\x1c")),
    "identifier reserved": ("plain", lambda f: _rename(_vocabulary(f)["constants"], "bob", "x1")),
    "identifier declared twice": ("plain", lambda f: _vocabulary(f)["constants"].update(
        senior={"sort": "person", "description": "Senior"})),
    "definition arguments not an array": ("definitions", lambda f: _vocabulary(f)["predicates"]["staff"][
        "defined"].update(arguments="person")),
    "definition arguments differ": ("definitions", lambda f: _vocabulary(f)["predicates"]["staff"][
        "defined"].update(arguments=["$string"])),
    "definition body not a tagged array": ("definitions", lambda f: _vocabulary(f)["predicates"]["staff"][
        "defined"].update(body=[])),
    "definition body variable index": ("definitions", lambda f: _vocabulary(f)["predicates"]["staff"][
        "defined"].update(body=["unary", "in_finance", ["var", "0"]])),
    "definition body unknown tag": ("definitions", lambda f: _vocabulary(f)["predicates"]["staff"][
        "defined"].update(body=["VAR", 0])),
    "content unknown tag": ("plain", lambda f: f["units"][1]["content"].update(
        ast=["unary", "senior", ["c  onst", "bob"]])),
    "content not a tagged array": ("plain", lambda f: f["units"][1]["content"].update(ast=["unary", "senior", 7])),
    "content predicate a number": ("plain", lambda f: f["units"][1]["content"].update(
        ast=["unary", 7, ["const", "bob"]])),
    "content constant with a carriage return": ("plain", lambda f: f["units"][1]["content"].update(
        ast=["unary", "senior", ["const", "bob\r"]])),
    "graph node unknown tag": ("graph-bridge", lambda f: f["graph"]["nodes"][0].update(
        ast=["unary\x1c", "in_finance", ["const", "alice"]])),
    "graph node predicate a number": ("graph-bridge", lambda f: f["graph"]["nodes"][0].update(
        ast=["unary", 7, ["const", "alice"]])),
    "graph node unknown constant": ("graph-bridge", lambda f: f["graph"]["nodes"][0].update(
        ast=["unary", "in_finance", ["const", "x"]])),
}


def coded(call):
    """The rejection of `call` as (code, message), the members `lean_first_diff` compares."""
    try:
        call()
    except (VEError, CheckerUnavailable) as exc:
        return getattr(exc, "code", type(exc).__name__), getattr(exc, "message", str(exc))
    return None


def _unprefixed(error):
    code, message = error
    return message.removeprefix(f"{code}: ")


@lru_cache(maxsize=1)
def _saved_document_cases():
    """Rebuild only the signed corpus entries; their seed and mutations are frozen in the gzip file."""
    from tools.difffuzz import apply_all
    corpus = json.loads(gzip.decompress((ROOT / "docs/lean-first/document-corpus.json.gz").read_bytes()))
    return {entry["id"]: dw.text_of(apply_all(corpus["seeds"][entry["seed"]], entry["mutations"]))
            for entry in corpus["entries"]}


def _delta_cases(klass):
    delta = json.loads((ROOT / "docs/lean-first/b16b/delta.json").read_text())
    return sorted({row["case"] for row in delta[klass]})


@pytest.mark.parametrize("case", _delta_cases("order"))
def test_signed_order_diagnostics_keep_python_names_and_specificity(tmp_path, case):
    """The historical order block is fixed at the current Lean head, including the unknown AST tag case."""
    path = write(tmp_path, _saved_document_cases()[case])
    lean, python = coded(lambda: D.check_document(path)), coded(python_path(path))
    assert lean is not None and python is not None
    assert lean[0] == python[0] and _unprefixed(lean) == _unprefixed(python), (case, lean, python)


@pytest.mark.parametrize("language", ["ve.core@٠.٢", "ve.core@0.2’", "v  e.core@0.2", "ve.core@0.3"])
@pytest.mark.parametrize("removed", [(), ("profiles",), ("spec_revision", "vocabulary")])
def test_unknown_language_uses_the_frozen_envelope_field_set(tmp_path, language, removed):
    doc = deepcopy(GENERATED["plain"])
    environment = doc["front"]["environment"]
    environment["language"] = language
    for key in removed:
        del environment[key]
    path = write(tmp_path, dw.text_of(doc))
    lean, python = coded(lambda: D.check_document(path)), coded(python_path(path))
    assert lean == python, (language, removed, lean, python)


@pytest.mark.xfail(strict=True, reason="path pending lf-12: located Lean decoders will restore these paths")
@pytest.mark.parametrize("case", _delta_cases("verdict"))
def test_pending_lf12_document_paths(tmp_path, case):
    """Each signed path gap becomes an XPASS failure as soon as lf-12 fixes that case."""
    path = write(tmp_path, _saved_document_cases()[case])
    with pytest.raises(VEError) as lean:
        D.check_document(path)
    with pytest.raises(VEError) as python:
        python_path(path)()
    assert python.value.path, case
    assert lean.value.code == python.value.code
    assert lean.value.path == python.value.path


@pytest.mark.parametrize("name", sorted(NAMED))
def test_lean_names_a_rejection_as_python_did(tmp_path, name):
    """DRI rule 2(a)-(c) (16b looprecheck1): Lean's rejection keeps every name, value and the specificity of
    the diagnostic Python's own path gives the same document; here the texts agree but for the code prefix, which
    the relay always writes."""
    seed, edit = NAMED[name]
    doc = deepcopy(GENERATED[seed])
    edit(doc["front"])
    path = write(tmp_path, dw.text_of(doc))
    lean, python = coded(lambda: D.check_document(path)), coded(python_path(path))
    assert lean is not None and python is not None, (lean, python)
    assert lean[0] != "CheckerUnavailable" and lean[0] == python[0], (lean, python)
    assert _unprefixed(lean) == _unprefixed(python), (lean, python)


def test_lean_quotes_a_name_as_python_repr_does():
    """`TypingDiagnostic.pyRepr` against Python's `repr` (16b looprecheck1: `'in_legal\\r'` was shown with a raw
    carriage return): every Latin-1 character, the separator, format and private-use characters its table lists,
    and printable characters above Latin-1, each inside a constant name the check mode does not know. An
    unassigned code point (Python escapes it) is outside the table and not compared."""
    from ve.backends.relay import decide
    environment = GENERATED["plain"]["front"]["environment"]
    chars = [*range(0x100), 0x600, 0x61c, 0x180e, 0x1680, *range(0x2000, 0x2010), *range(0x2028, 0x2030),
             *range(0x205f, 0x2065), 0x3000, 0xe000, 0xf8ff, 0xfeff, 0xfff9, 0xf0000, 0x2019, 0x212a, 0x130, 0x1f600]
    wrong = []
    for c in chars:
        name = f"b{chr(c)}ob"
        with pytest.raises(VEError) as caught:
            decide("check", [{"id": "name", "environment": environment,
                              "ast": ["unary", "senior", ["const", name]]}])
        if caught.value.message != f"UnknownSymbol: Unknown constant {name!r}":
            wrong.append((hex(c), caught.value.message))
    assert not wrong


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
                                             "weights": [{"set": "s", "by": "a", "values": {"x": 1.5}}]}})
            .replace('"x": 1.5', '"x": NaN')),
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
    # looprecheck1: an extra residual line with the total raised to match was accepted.
    yield "forged residual line", edit(lambda r: (r["coverage"]["residual"].update(forged_line=7),
                                                  r["coverage"].update(residual_total=r["coverage"]["residual_total"] + 7)))


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


@pytest.mark.parametrize("name", ["plain", "alternatives-cells"])
@pytest.mark.parametrize("entry", ["check", "load"])
def test_forged_residual_line_with_balanced_total_is_unavailable(
        tmp_path, no_python_loader, monkeypatch, name, entry):
    path = write(tmp_path, dw.text_of(GENERATED[name]))
    row = D._lean_answer(path.read_bytes(), entry == "check")
    forged = deepcopy(row)
    forged["coverage"]["residual"]["forged_line"] = 7
    forged["coverage"]["residual_total"] += 7
    monkeypatch.setattr(relay, "answer", lambda mode, case: (forged, None))
    call = D.check_document if entry == "check" else D.load_document
    with pytest.raises(CheckerUnavailable, match="not bound to the document sent"):
        call(path)


RETYPES = (7, True, None, [], {}, "x")


def test_document_schema_types_checked_content(tmp_path):
    from ve.backends.service_schema import ROWS, Context, Invalid
    path = write(tmp_path, dw.text_of(GENERATED["plain"]))
    row = D._lean_answer(path.read_bytes(), True)
    forged = deepcopy(row)
    forged["units"][0]["content"] = 7
    with pytest.raises(Invalid):
        ROWS["document"][0](forged, Context({"id": "document", "document": path.read_text(), "admit": True}), {})


def _structural_mutants(node, at=()):
    """Every one-fault structural mutant of a genuine answer (build checklist line 4): each member dropped, an
    extra member added to each object, each element of a list dropped or duplicated, and each value replaced by
    one of another JSON type (a boolean for a count included). Yields (path, mutate) with `mutate(copy)`."""
    def at_path(root, path):
        for key in path:
            root = root[key]
        return root
    if type(node) is dict:
        yield at + ("+forged",), lambda r: at_path(r, at).update(forged_line=7)
        for key in node:
            yield at + (key, "-"), lambda r, key=key: at_path(r, at).pop(key)
    if type(node) is list:
        for i in range(len(node)):
            yield at + (i, "-"), lambda r, i=i: at_path(r, at).pop(i)
            yield at + (i, "x2"), lambda r, i=i: at_path(r, at).insert(i, deepcopy(at_path(r, at)[i]))
    children = node.items() if type(node) is dict else enumerate(node) if type(node) is list else ()
    for key, child in children:
        for value in RETYPES:
            if type(value) is not type(child):
                yield at + (key, f"={value!r}"), lambda r, key=key, value=value: \
                    at_path(r, at).__setitem__(key, deepcopy(value))
        yield from _structural_mutants(child, at + (key,))


@pytest.mark.parametrize("name", ["plain", "mixed", "graph-bridge", "alternatives-cells", "risk"])
def test_every_structural_mutant_of_an_answer_is_refused(tmp_path, no_python_loader, monkeypatch, name):
    """The response schema and the binding together refuse every structural mutant of a genuine row: none may
    reach a document. The schema is the service's own row check (`service_schema.ROWS`), as `run_bound` applies
    it; a row it refuses never reaches the binding."""
    from ve.backends.service_schema import ROWS, Context, Invalid
    path = write(tmp_path, dw.text_of(GENERATED[name]))
    case = {"id": "document", "document": path.read_text(), "admit": True}
    row = D._lean_answer(path.read_bytes(), True)
    def rebalanced(mutant):
        """The mutant with its residual total made consistent again: the second fault of a forged count."""
        coverage = mutant.get("coverage") if type(mutant) is dict else None
        residual = coverage.get("residual") if type(coverage) is dict else None
        if type(residual) is dict and all(type(n) is int for n in residual.values()):
            mutant = deepcopy(mutant)
            mutant["coverage"]["residual_total"] = sum(residual.values())
        return mutant

    accepted, count = [], 0
    for where, mutate in _structural_mutants(row):
        once = deepcopy(row)
        mutate(once)
        for mutant in (once, rebalanced(once)):
            if json.dumps(mutant, sort_keys=True) == json.dumps(row, sort_keys=True):
                continue  # rebalancing restored the genuine row (compared as JSON: True is not 1)
            count += 1
            try:
                ROWS["document"][0](mutant, Context(case), {})
            except Invalid:
                continue
            monkeypatch.setattr(relay, "answer", lambda mode, case, mutant=mutant: (mutant, None))
            try:
                D.check_document(path)
            except CheckerUnavailable as exc:
                assert "the Lean document answer" in str(exc), where
            else:
                accepted.append(where)
    assert count > 200 and not accepted, accepted


@pytest.mark.parametrize("name", ["alternatives-cells", "risk"])
def test_alternatives_coverage_is_bound_to_units_and_counts(tmp_path, no_python_loader, monkeypatch, name):
    path = write(tmp_path, dw.text_of(GENERATED[name]))
    row = D._lean_answer(path.read_bytes(), False)
    for change in (
            lambda r: r["coverage"]["residual"].update(forged_line=7),
            lambda r: r["coverage"]["alternatives"].update(narrowings=[{"forged": 1}]),
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
