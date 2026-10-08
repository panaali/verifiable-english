"""The `ve-document@1` wrapper: Python's `load_document` and `check_document` against the Lean service's
`document` mode (docs/LEAN-FIRST-PLAN.md, row 16a).

A document is held as `{"front": <front matter>, "body": <text>}`, so a fuzzer can mutate every front-matter node
and the body. `python_answer` and `lean_answers` give each implementation's answer on the document's text:
`{"outcome": "ok", "value": <projection>}` or `{"outcome": "error", "code", "text"}` (Python may also crash).
`verdict` compares two answers under the mode's contract:

* `agree`: the same projection (identities, every unit's span, status and parent, the whole coverage), or the
  same `(code, text)`;
* `fail-closed`: Lean answers `CheckerUnavailable` or `ResourceLimit` (it cannot decide, and says so), or Python
  does (its own checker could not decide);
* `environment`, `formula`, `admission`: both reject, and Python's rejection is another decoder's (`owner_of`):
  the text its `Environment` gives the embedded environment by itself (the envelope decoder, batch 12), or one
  raised inside `formula_from_data` (the formula decoder) or `admit_document` (W2 admission), whose texts are
  batch 13's (docs/LEAN-FIRST-PLAN.md 2.1; conformance/DIFFFUZZ.md DF-3 and DF-9). Only the outcome is compared;
* `differ`: anything else, a finding.

`seeds()` is the seed corpus: every `ve-document@1` text of the repository and generated documents that reach
each branch of the wrapper (MIXED parts, open terms, reading sets with models and versions, narrowings, weights,
lemmas, bridge, readings and narrowing labels in an admitted graph, a definitions environment), each with nonzero
residual counts somewhere.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FAIL_CLOSED = ("CheckerUnavailable", "ResourceLimit")
# `VE.Service.Document.ownedProfiles` (checked against the Lean mode by `tests/test_lean_document_wrapper.py`).
OWNED = frozenset({"alternatives@0", "data@0", "definitions@0", "documents@1", "norms@0", "relational-fol@0", "risk@0",
                   "time@0"})


def text_of(document) -> str:
    """The document text of `{"front", "body"}`: the front matter as `json.dumps` writes it, then the body. A
    mutant without a front matter is its body alone; a body that is not a string, or an input that is not such
    an object (a 2-fault mutant whose second fault no longer applies is `None`), is written as JSON."""
    if type(document) is not dict:
        return json.dumps(document, ensure_ascii=False)
    body = document.get("body", "")
    body = body if type(body) is str else json.dumps(body, ensure_ascii=False)
    if "front" not in document:
        return body
    return "---\n" + json.dumps(document["front"], ensure_ascii=False) + "\n---\n" + body


def split_text(text: str):
    """`{"front", "body"}` of a document text whose front matter decodes."""
    boundary = text.find("\n---\n", 4)
    return {"front": json.loads(text[4:boundary]), "body": text[boundary + 5:]}


def projection_of(units, coverage, document_id, source_id):
    return {"document_id": document_id, "source_id": source_id,
            "units": [[u["id"], list(u["span"]), u["status"], u.get("parent_id")] for u in units],
            "coverage": coverage}


def python_answer(text: str) -> dict:
    """Python's answer: its own path (`_load_document`, which `load_document` keeps for the documents the Lean mode
    cannot decide yet, batch 16b), then `check_document`'s wrapper: `_report`, which admits the claim graph and
    reports the coverage, for a document with a graph; `coverage` alone for one without (`_report` adds only the
    premise status there, which the wrapper does not compute). A VEError is an answer; any other exception is a
    crash."""
    from ve.document import _load_document, _report, coverage
    from ve.errors import VEError
    from ve.search import model_search_scope
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "document.ve.md"
        path.write_bytes(text.encode("utf-8"))
        try:
            with model_search_scope():
                doc = _load_document(path.read_bytes(), path, None)
                result = (_report(doc) if "graph" in doc["meta"] else
                          {"coverage": coverage(doc), "document_id": doc["document_id"], "source_id": doc["source_id"]})
        except VEError as exc:
            answer = {"outcome": "error", "code": exc.code, "text": exc.message}
            owner = owner_of(exc, text)
            if owner is not None:
                answer["owner"] = owner
            return answer
        except RecursionError as exc:
            return {"outcome": "crash", "code": "RecursionError", "text": str(exc)[:200]}
        except Exception as exc:  # noqa: BLE001 - only VEError may escape; the rest is the finding
            return {"outcome": "crash", "code": type(exc).__name__, "text": str(exc)[:200]}
    return {"outcome": "ok", "value": projection_of(doc["units"], result["coverage"], result["document_id"],
                                                     result["source_id"])}


def lean_answers(service, texts) -> list:
    """The Lean `document` mode's answers, one per text, through the service client (which checks every row
    against the mode's schema)."""
    entries = service.run_bound("document", [{"id": str(i), "document": t} for i, t in enumerate(texts)])
    out = []
    for entry in entries:
        row = entry["result"]
        if row.get("status") == "ok":
            out.append({"outcome": "ok", "value": projection_of(row["units"], row["coverage"], row["document_id"],
                                                                 row["source_id"])})
        else:
            out.append({"outcome": "error", "code": entry.get("code") or "InvalidInput", "text": row["error"]})
    return out


def environment_error(text: str):
    """The message of Python's `Environment` rejecting the document's embedded environment by itself, or None
    (it accepts it, or the text has no readable embedded environment)."""
    from ve.environment import Environment
    from ve.errors import VEError
    try:
        front = json.loads(text[4:text.find("\n---\n", 4)])
        environment = front["environment"]
    except (ValueError, TypeError, KeyError, RecursionError):
        return None
    if type(environment) is not dict:
        return None
    try:
        Environment(deepcopy(environment))
    except VEError as exc:
        return exc.message
    except Exception:  # noqa: BLE001 - not a decoder answer; the document check reports it
        return None
    return None


# The decoders whose texts another batch owns (docs/LEAN-FIRST-PLAN.md 2.1, conformance/DIFFFUZZ.md): Python's
# function that raised, by the owner's name. `formula_from_data` is the formula decoder (DF-9, batch 13: the
# `check` mode's wording becomes the spec), `admit_document` the W2 admission route (DF-9, batch 13).
OWNERS = {"admit_document": "admission", "formula_from_data": "formula"}
OWNED_ELSEWHERE = ("environment", *OWNERS.values())


def owner_of(exc, text):
    """The other decoder whose text a Python rejection is (`environment`, `admission` or `formula`), or None
    for the wrapper's own rejection."""
    import traceback
    if environment_error(text) == exc.message:
        return "environment"
    names = [frame.name for frame in traceback.extract_tb(exc.__traceback__)]
    for name, owner in OWNERS.items():
        if name in names:
            return owner
    return None


def verdict(python, lean) -> str:
    """`agree`, `fail-closed`, `environment` or `differ` (see the module docstring)."""
    if python["outcome"] == "crash":
        return "differ"
    if lean["outcome"] == "error" and lean["code"] in FAIL_CLOSED:
        return "fail-closed"
    if python["outcome"] == "error" and python["code"] in FAIL_CLOSED:
        return "fail-closed"
    if python["outcome"] != lean["outcome"]:
        return "differ"
    if python["outcome"] == "ok":
        return "agree" if python["value"] == lean["value"] else "differ"
    if (python["code"], python["text"]) == (lean["code"], lean["text"]):
        return "agree"
    return python.get("owner", "differ")


def owned(document) -> bool:
    """Whether a document's environment is one the Lean mode owns: the envelope's four fields and the blocks of
    the routes it composes (`VE.Service.Document.envelopeKeys`), with profiles all `ownedProfiles`. The fuzzer
    counts findings by it."""
    environment = document.get("front", {}).get("environment") if type(document.get("front")) is dict else None
    if type(environment) is not dict:
        return False
    profiles = environment.get("profiles")
    if type(profiles) is not list or not set(profiles) <= OWNED:
        return False
    blocks = {"risk@0": {"alternatives", "risk"}, "alternatives@0": {"alternatives"}}
    allowed = {"language", "profiles", "spec_revision", "vocabulary"}
    allowed |= next((keys for profile, keys in blocks.items() if profile in profiles), set())
    return not set(environment) - allowed


def fuzzed(document) -> bool:
    """Whether the fuzzer mutates a seed: not a quantity (`unit_schema`) document, whose Python check runs the
    quantity route for every mutant while the Lean mode refuses its environment block before anything else
    (each such seed is still compared as it is, `tests/test_lean_document_wrapper.py`)."""
    environment = document["front"].get("environment")
    return not (type(environment) is dict and "unit_schema" in environment)


# ---------------------------------------------------------------- seeds

def _repository_documents():
    paths = sorted([*ROOT.glob("usecases/**/*.ve.md"), *ROOT.glob("tests/data/**/*.ve.md")])
    return [(str(path.relative_to(ROOT)), split_text(path.read_text())) for path in paths]


def _unit(uid, span, kind="exposition", meaning="specified", support="none", **extra):
    return {"id": uid, "span": list(span), "kind": kind, "meaning": meaning, "support": support, **extra}


def _generated():
    from conformance.p0 import VOCAB, envelope, environment
    from ve.ast import formula_from_data
    from ve.environment import Environment
    from ve.identity import meaning_id
    from ve.model import FiniteModel

    env_json = envelope(VOCAB)
    env = Environment(deepcopy(env_json))
    fin = ["unary", "in_finance", ["const", "alice"]]
    legal = ["unary", "in_legal", ["const", "alice"]]
    senior = ["unary", "senior", ["const", "bob"]]

    def mid(ast):
        return meaning_id(env, formula_from_data(env, ast))

    def model(finance, legal_):
        data = {"complete": True, "domains": {"person": ["a", "b"], "$string": ["f", "l"]},
                "constants": {"alice": "a", "bob": "b", "finance": "f", "legal": "l"},
                "relations": {"in_finance": [["a"]] if finance else [], "in_legal": [["a"]] if legal_ else [],
                              "senior": []}}
        return FiniteModel.from_dict(env, data).model_id, data

    def reading(rid, ast, others, kind="asserted"):
        return {"id": rid, "kind": kind, "meaning_id": mid(ast), "content": ast,
                "admission": {"who": "alice", "why": "the source allows it", "distinguishing_models": others}}

    out = []
    plain = "Café. Next one.\nMeta.\n"
    cut, cut2 = len("Café. ".encode()), len("Café. Next one.\n".encode())
    out.append(("plain", {"front": {"format": "ve-document@1", "environment": env_json, "units": [
        _unit("a", (0, cut), "asserted", support="assumption", content={"ast": fin}, meaning_id=mid(fin),
              status="CHECKED"),
        _unit("b", (cut, cut2), ["hedged", "likely", "asserted"], content={"ast": senior}),
        _unit("c", (cut2, len(plain.encode())), ["unformalised", "opaque"], {"unformalised": "opaque"},
              status="UNFORMALISED")]}, "body": plain}))
    mixed = "Alice works in finance, they say.\n"
    half = len("Alice works in finance".encode())
    out.append(("mixed", {"front": {"format": "ve-document@1", "environment": env_json, "units": [
        {"id": "whole", "span": [0, len(mixed)], "status": "MIXED", "parts": [
            _unit("p1", (0, half), "asserted", support="observation", content={"ast": fin}, status="CHECKED"),
            _unit("p2", (half, len(mixed)), ["unformalised", "hedge"], {"unformalised": "hedge"},
                  status="UNFORMALISED")]}]}, "body": mixed}))
    term = {"name": "seniority", "arguments": ["person"], "decided_by": "hr", "necessary": [senior],
            "sufficient": [], "factors": ["tenure"], "precedents": [], "jurisdiction": "company", "version": 1}
    opened = "Bob is senior enough.\nAside.\n"
    cut = len("Bob is senior enough.\n")
    out.append(("open-terms", {"front": {"format": "ve-document@1", "environment": env_json,
                                          "open_terms": [term, {**term, "name": "tenure", "necessary": []}],
                                          "units": [
        _unit("a", (0, cut), "explanation", {"open": ["seniority"]}, support="assumption", status="OPEN"),
        _unit("b", (cut, len(opened)), "meta", status="LABELLED")]}, "body": opened}))
    m1, d1 = model(True, False)
    m2, d2 = model(False, True)
    sets = [{"id": "s", "unit": "a", "version": 1, "status": "open", "readings": [
                reading("fin", fin, {"legal": m1}), reading("legal", legal, {"fin": m2})],
             "models": {m1: d1, m2: d2}, "rejected_history": []},
            {"id": "s", "unit": "a", "version": 2, "status": "open", "readings": [
                reading("fin", fin, {"legal": m1}), reading("legal", legal, {"fin": m1})],
             "models": {m1: d1}},
            {"id": "t", "unit": "b", "version": 1, "status": "authored", "signature": "alice",
             "readings": [reading("only", senior, {})]}]
    readings_body = "Alice works there.\nBob is senior.\nWeights.\n"
    c1, c2 = len("Alice works there.\n"), len("Alice works there.\nBob is senior.\n")
    out.append(("reading-sets", {"front": {
        "format": "ve-document@1", "environment": env_json, "units": [
            _unit("a", (0, c1), "asserted", status="OPEN"),
            _unit("b", (c1, c2), "asserted", status="CHECKED"),
            _unit("c", (c2, len(readings_body)), "meta", support="assumption")],
        "reading_sets": sets,
        "narrowings": [{"id": "n", "set": "s", "version": 2, "keeps": ["fin"], "by": "alice",
                        "reason_spans": ["c"]}],
        "weights": [{"set": "s", "by": "alice", "values": {"fin": 2, "legal": 1}}], "lemmas": []},
        "body": readings_body}))
    bridge_body = "Alice says she works in finance.\nAlice is in finance.\n"
    cut = len("Alice says she works in finance.\n")
    out.append(("graph-bridge", {"front": {
        "format": "ve-document@1", "environment": env_json, "units": [
            _unit("a", (0, cut), ["attributed", "alice", "says", "asserted"], support="testimony",
                  content={"ast": fin}),
            _unit("b", (cut, len(bridge_body)), "asserted", support="assumption", content={"ast": fin})],
        "graph": {"root": "claim", "nodes": [
            {"name": "claim", "ast": fin, "unit": "a", "label": "bridge:accepts(alice,a)"}]}},
        "body": bridge_body}))
    graph_sets = [{"id": "s", "unit": "a", "version": 1, "status": "open", "readings": [
        reading("fin", fin, {"legal": m1}), reading("legal", legal, {"fin": m2})], "models": {m1: d1, m2: d2}}]
    labels_body = "Alice works there.\nWhy.\n"
    cut = len("Alice works there.\n")
    out.append(("graph-readings", {"front": {
        "format": "ve-document@1", "environment": env_json, "units": [
            _unit("a", (0, cut), "asserted"), _unit("b", (cut, len(labels_body)), "explanation")],
        "reading_sets": graph_sets,
        "narrowings": [{"id": "n", "set": "s", "version": 1, "keeps": ["fin"], "by": "alice",
                        "reason_spans": ["b"]}],
        "graph": {"root": "claim", "nodes": [
            {"name": "claim", "ast": fin, "label": "readings:s@1:0"},
            {"name": "keep", "ast": ["top"], "label": "narrowing:n"}]}},
        "body": labels_body}))
    defs = deepcopy(env_json)
    defs["profiles"] = ["definitions@0", "relational-fol@0"]
    defs["vocabulary"]["predicates"]["staff"] = {
        "arguments": ["person"], "description": "is staff",
        "defined": {"arguments": ["person"], "body": ["or", ["unary", "in_finance", ["var", 0]],
                                                      ["unary", "in_legal", ["var", 0]]]}}
    staff = ["unary", "staff", ["const", "alice"]]
    out.append(("definitions", {"front": {"format": "ve-document@1", "environment": defs, "units": [
        _unit("a", (0, 13), "asserted", content={"ast": staff})]}, "body": "Alice staff.\n"}))
    out.append(("p0-envelope", {"front": {"format": "ve-document@1", "environment": environment(), "units": [
        _unit("a", (0, 3), "asserted", content={"ast": ["eq", ["const", "alpha"], ["const", "beta"]]})]},
        "body": "A=B"}))
    out += _block_seeds()
    fence_body = "Alice is in finance.\n```ve a\nAlice is in finance.\n```\n"
    out.append(("fence", {"front": {"format": "ve-document@1", "environment": env_json, "units": [
        _unit("a", (0, len("Alice is in finance.\n")), "asserted", content={"fence": "a"}, surface="strict")]},
        "body": fence_body}))
    return out


def _alternatives_environment():
    """An `alternatives@0` environment with regulated permission and obligation words and a complete outcome
    table (the alternatives profile tests' source)."""
    from ve.profiles import LANGUAGE, SPEC_REVISION

    def word(args, words):
        return {"arguments": args, "description": words, "verbalisation": words}
    predicates = {
        "available": word(["action", "robot"], "{0} is available to {1}"),
        "leads_to": word(["action", "harm"], "{0} leads to {1}"),
        "inaction": word(["action"], "{0} is inaction"), "taken": word(["action"], "{0} is taken"),
        "causes": word(["action", "harm"], "{0} causes {1}"),
        "permitted": {"arguments": ["action"], "description": "permission",
                      "regulated": {"role": "permission", "default": "deny", "act": "{0} be done"}},
        "required": {"arguments": ["action"], "description": "obligation",
                     "regulated": {"role": "obligation", "default": "deny", "act": "{0} be done",
                                   "permission": "permitted"}}}
    constants = {name: {"sort": sort, "description": name}
                 for name, sort in (("pull", "action"), ("wait", "action"), ("r", "robot"), ("h", "harm"))}
    block = {"chooser": "robot", "action": "action", "harm": "harm", "available": "available",
             "leads_to": "leads_to", "outcomes": {"complete_by": "case annotator"},
             "decided_by": "case annotator", "performed": {"permission": "permitted", "obligation": "required"},
             "inaction": "inaction", "taken": "taken", "proximate": "causes"}
    return {"language": LANGUAGE, "profiles": ["alternatives@0", "norms@0", "relational-fol@0"],
            "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": {name: {"description": name} for name in ("robot", "action", "harm")},
                           "predicates": predicates, "constants": constants},
            "alternatives": block}


def _block_seeds():
    """Documents over the composed blocks: alternatives cells (declared, counterfactual, proximate and assumed
    harm-free), a graph admitted on the alternatives route, and a `risk@0` environment."""
    from ve.alternatives import run_case
    alt = _alternatives_environment()
    atoms = [["binary", "available", ["const", "pull"], ["const", "r"]],
             ["not", ["binary", "leads_to", ["const", "pull"], ["const", "h"]]],
             ["binary", "causes", ["const", "pull"], ["const", "h"]]]
    units = [_unit(f"u{i}", (i, i + 1), "asserted", support="testimony", content={"ast": atom})
             for i, atom in enumerate(atoms)]
    out = [("alternatives-cells", {"front": {"format": "ve-document@1", "environment": alt, "units": units,
                                             "narrowings": []}, "body": "abc"})]
    premise = next(p for p in run_case({"id": "source", "kind": "alt-elaborate", "environment": alt,
                                        "norms": []})["alternatives"] if p["label"] == "alternatives:own")
    out.append(("alternatives-graph", {"front": {
        "format": "ve-document@1", "environment": alt,
        "units": [_unit("claim", (0, 1), "asserted", support="observation", content={"ast": ["top"]})],
        "graph": {"root": "slot", "nodes": [{"name": "slot", "label": premise["label"], "ast": premise["ast"]}]}},
        "body": "x"}))
    risk = deepcopy(alt)
    risk["profiles"] = ["alternatives@0", "norms@0", "relational-fol@0", "risk@0"]
    risk["vocabulary"]["constants"]["outage"] = {"sort": "harm", "description": "outage"}
    risk["alternatives"]["outcomes"] = "signed"
    risk["risk"] = {"severity": {"sort": "severity", "classes": ["severe", "minor"],
                                 "more_severe": [["severe", "minor"]], "unranked": [], "decided_by": "team"},
                    "harm_classes": [["outage", "severe"], ["h", "minor"]], "unexamined": "possible"}
    out.append(("risk", {"front": {"format": "ve-document@1", "environment": risk, "units": [
        _unit("a", (0, 1), "asserted", support="assumption", content={"ast": atoms[0]}),
        _unit("b", (1, 2), "asserted", content={"ast": ["binary", "leads_to", ["const", "wait"], ["const", "outage"]]}),
        _unit("c", (2, 3))]}, "body": "abc"}))
    return out


def seeds():
    """[(name, document)]: the repository's documents, then the generated ones."""
    return _repository_documents() + _generated()
