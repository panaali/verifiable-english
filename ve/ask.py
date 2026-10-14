"""`ve ask DOCUMENT QUESTION [--reading] [--json] [--evidence FILE]` (docs/spec/question-answering-PLAN.md 4.8, Q1.2,
Q2.5; docs/spec/question-answering.md 4.2, 8).

A question is one of the document's own sentences, asked. Lean reads it (`english.question`) in the document's
vocabulary; with `--reading` this module prints Lean's A0 line or Lean's refusal and stops. Otherwise it answers: it
builds the case of the document's route and the evidence the existing untrusted generators find, sends them to Lean's
`ask` mode, and prints Lean's lines. Lean re-reads the question, binds the case to the document's own bytes, checks
every piece of evidence, decides the lead of every reading and renders every line; this module writes no English of
its own and decides nothing (`tools/relay_lint.py`).

The routes, by the document's profiles (Lean's `routeOfDocument` decides; a case built for another route is refused
by Lean): `readings@1` documents are RD-3's enumerated route (its readings case, `readings_verdicts.Enumerated`),
`norms@0` documents under `norm-defaults@0` without a reading set are one choice on the norm-defaults route (the
choice generator `readings_verdicts._FilledChoiceDocument` over the document's own elaboration), and any other
`relational-fol@0` document is the plain adapter (the prover and the countermodel search over its assertions). Per
choice the generators propose a certificate of the question's formula, else a countermodel; a certificate of its
negation; a certificate of `⊥`, else a premise model; the conflict packages, else a witness. A countermodel whose
failure turns on filled gaps (Lean's `gaps` of the row) is flipped at those gaps (`_split_piece`), the split asked of
Lean in a second request. `--evidence FILE` adds recorded pieces (an object of pieces for a one-choice route, a list
of `{choice, ...}` entries on the readings route); Lean checks them as it checks every piece.

Exit codes: 0 an answer whose lead is not unknown (`--reading`: the question has one reading); 3 VE could not decide;
2 the question is not read (Lean's code, class and text); 4 `ResourceLimit`; 5 `CheckerUnavailable`.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path
import sys

from .errors import CheckerUnavailable, ResourceLimit, VEError
from .document import MAX_DOCUMENT_BYTES
from .filling_search import split as _split

OPERATION = "question.read"
ANSWER_OPERATION = "question.answer"
MODE = "ask"
EXIT_READ, EXIT_UNKNOWN, EXIT_NOT_READ, EXIT_LIMIT, EXIT_UNAVAILABLE = 0, 3, 2, 4, 5


def _shape() -> dict:
    """The answer's shapes, read from the schema generated from Lean's (`lean_service_schema/ask.json`), never
    copied here (build checklist 1)."""
    from .backends.service_schema import DIRECTORY
    return json.loads((DIRECTORY / "ask.json").read_text(encoding="utf-8"))["$defs"]


_DEFS = _shape()
LEADS = tuple(_DEFS["row"]["properties"]["lead"]["enum"])
REASONS = tuple(next(alt["enum"] for alt in _DEFS["reason"]["anyOf"] if "enum" in alt))
ANSWER_LEADS = tuple(_DEFS["answered"]["properties"]["lead"]["enum"])
SOURCE_FIELDS = {alt["properties"]["kind"]["const"]: set(alt["properties"]) - {"kind"}
                 for alt in _DEFS["source"]["anyOf"]}
ANSWERED_FIELDS = set(_DEFS["answered"]["properties"])
LINE_FIELDS = set(_DEFS["line"]["properties"])
ROW_FIELDS = set(_DEFS["row"]["properties"])
NAME_FIELDS = set(_DEFS["name"]["properties"])
MAX_RECORDED_DEPTH = 128


def environment(raw: bytes):
    """The environment a document's sentences are read in: its front matter's, built as the loader builds it."""
    from .document import _environment, base_environment, stored_identities
    meta, _, _ = stored_identities(raw)
    return _environment(base_environment(meta))


def read(raw: bytes, question: str) -> dict:
    """Lean's checked `english.question` answer for `question` over the document `raw`, or the refusal raised as
    the class Lean names (its answer as `lean_question`)."""
    from .backends.english_lean import read_question
    from .english import EnglishVocabulary
    env = environment(raw)
    return read_question(env, question, EnglishVocabulary(env, _defer_overlay_refusals=True), {})


def _answer(exc: Exception) -> dict | None:
    return getattr(exc, "lean_question", None) or getattr(exc, "lean_answer", None)


def _lines(answer: dict) -> list[str]:
    """Lean's text, its advice, then its rephrasings, one per line (a question VE does not read)."""
    text = answer["text"] if "advice" not in answer else f'{answer["text"]} {answer["advice"]["text"]}'
    return [text, *answer.get("rephrasings", ())]


# ---------------------------------------------------------------------------------------------------------------
# The cases of the routes (untrusted generators; Lean checks every piece)


def _strip(name):
    """A `<reading>` name as Lean reads it back: the sentence without the italics markers; "" for a reading the
    relay cannot word (Lean refuses an answer that would show it)."""
    if type(name) is not str:
        return ""
    return name[1:-1] if len(name) >= 2 and name.startswith("*") and name.endswith("*") else name


def _split_piece(countermodel: dict, gaps) -> dict | None:
    """The asked sentence's instance of the one flip search (`filling_search.split`, plan Q2.5): the countermodel's
    base situation with its own filling, under which the asked sentence fails, and that filling flipped at every gap
    its failure depends on (Lean's `gaps` of the row), under which it may hold. Lean checks both fillings on the
    same base (`splitOk_sound`)."""
    if not gaps or "filling" not in countermodel:
        return None
    return {"kind": "split", "model": countermodel["model"], **_split(countermodel["filling"], gaps)}


class _Readings:
    """RD-3's enumerated route: the readings case its relay builds for the question (`Enumerated.entailment`), each
    choice's evidence from the choice's own filled document, and the reading names of RD-3's `<reading>` slot."""

    route = "readings"

    def __init__(self, doc):
        from .readings_verdicts import Enumerated, context
        self.doc = doc
        self.context = context(doc)
        if not isinstance(self.context, Enumerated):
            raise CheckerUnavailable("CheckerUnavailable: ask answers a readings document on the enumerated route "
                                     "with at most 64 compatible readings")

    def case(self, ast, extra=None, generate=True):
        route = self.context
        if getattr(route, "choices", None) is None:
            # RD-3 counts the choices before checking a row. Send the case without generated evidence so
            # Lean owns the X5 ResourceLimit and its wording, as it does for every other replay refusal.
            return {"id": "readings-verdicts", "kind": "readings-verdicts", "environment": route.environment,
                    "document": route.document, "question": "query", "conclusion": ast, "evidence": []}
        route.premises()
        row = route.query_answer(ast)
        case = copy.deepcopy(route.requests[id(row)])
        entries = {json.dumps(e["choice"]): e for e in case["evidence"]}
        for choice in route.choices:
            key = json.dumps(route.choice_json(choice))
            entry = entries.setdefault(key, {"choice": route.choice_json(choice)})
            negation = route._choice(choice).certificate_case(["not", ast])
            if negation is not None:
                entry["negation"] = negation
        for entry in extra or ():
            entries.setdefault(json.dumps(entry["choice"]), {"choice": entry["choice"]}).update(
                {k: v for k, v in entry.items() if k != "choice"})
        case["evidence"] = list(entries.values())
        return case

    def splits(self, case, rows):
        """A split per refuted row whose countermodel's failure turns on gaps; True when one was added."""
        added = False
        gaps = {json.dumps(r["choice"]): r["gaps"] for r in rows if r["lead"] == "notNecessarily" and r["gaps"]}
        for entry in case["evidence"]:
            g = gaps.get(json.dumps(entry["choice"]))
            piece = _split_piece(entry["countermodel"], g) if g and "countermodel" in entry else None
            if piece is not None and "split" not in entry:
                entry["split"] = piece
                added = True
        return added

    def names(self):
        from .readings_route import Wording
        wording = Wording(self.doc)
        return [{"set": R.id, "index": i, "text": _strip(name)}
                for R in self.context.sets for i, name in enumerate(wording.reading_names(R.id))]


def _units(doc):
    """The case's units: id, kind and content, a unit without content (exposition) without the field, as the front
    matter has it (Lean reads an absent content as none; the service's restricted JSON has no null)."""
    return [{"id": u["id"], "kind": u["kind"], **({"content": u["content"]} if u.get("content") is not None else {})}
            for u in doc["units"]]


class _Plain:
    """The plain adapter: the prover and the countermodel search over the document's asserted formulas."""

    route = "plain"

    def __init__(self, doc):
        self.doc = doc
        self.env = doc["environment"]
        self.units = _units(doc)

    def _premises(self):
        from .ast import formula_from_data
        return [formula_from_data(self.env, u["content"]) for u in self.units if u.get("content") is not None]

    def _certificate(self, conclusion):
        from .entailment import _binding, _validate_inputs, prove_entailment
        from .readings_verdicts import BUDGET
        premises = self._premises()
        proof = prove_entailment(self.env, premises, conclusion, max_steps=BUDGET["max_steps"])
        if proof.status != "Found":
            return None
        return {"certificate": {**proof.certificate,
                                **_binding(self.env, _validate_inputs(self.env, premises, conclusion), conclusion)}}

    def _model(self, conclusion):
        from .readings_verdicts import BUDGET
        from .search import find_countermodel
        found = find_countermodel(self.env, self._premises(), conclusion, max_domain_size=BUDGET["max_domain_size"],
                                  max_models=BUDGET["max_models"], max_evaluations=BUDGET["max_evaluations"])
        return None if found.status != "Found" else {"model": found.model.to_dict()}

    def case(self, ast, extra=None, generate=True):
        from .ast import Bottom, Not, formula_from_data
        phi = formula_from_data(self.env, ast)
        evidence = {}
        for key, piece in (("certificate", self._certificate(phi)), ("negation", self._certificate(Not(phi))),
                           ("unsat", self._certificate(Bottom()))):
            if piece is not None:
                evidence[key] = piece
        if "unsat" not in evidence:
            model = self._model(Bottom())
            if model is not None:
                evidence["model"] = model
        if "certificate" not in evidence:
            model = self._model(phi)
            if model is not None:
                evidence["countermodel"] = model
        evidence.update(extra or {})
        return {"environment": self.env.to_dict(), "document": {"units": self.units}, "conclusion": ast,
                "evidence": evidence}

    def splits(self, case, rows):
        return False

    def names(self):
        return []


def _zero_generator(doc):
    """RD-3's choice generator (`_FilledChoiceDocument`) over the document's own norm-defaults elaboration: one
    choice, no reading set. Lean's elaboration row gives `Fill_T`, the filled layers and the conflict targets."""
    from .ast import _Decoder
    from .norm_defaults import UnspecifiedDocument
    from .readings_verdicts import _FilledChoiceDocument, _FilledView

    class _Zero(_FilledChoiceDocument):
        def __init__(self):  # noqa: D401 - the attributes `_FilledChoiceDocument`'s generators read
            self.route, self.choice, self.side = None, (), None
            units = _units(doc)
            nd = UnspecifiedDocument(doc["environment"], [u["content"] for u in units
                                                           if u["kind"] == "norm" and u.get("content") is not None])
            self.elaboration = nd.elaboration
            self.base = nd.filled.base_environment()
            self.env = nd.filled.env
            self.source_env = doc["environment"]
            self.tables = [item["name"] for item in nd.elaboration["unsaid"]]
            self.fill = [f for _, f in nd.fill_premises]
            self.layers = [f for _, f in nd.filled.premises()]
            self.targets = [(t["target"], tuple(t["sorts"]), _Decoder().decode(t["ast"]))
                            for t in nd.elaboration["conflict_targets"]]
            self.assertions = [u["content"] for u in units if u["kind"] == "asserted" and u.get("content") is not None]
            self.view = _FilledView(self.source_env, self.env, self.fill, self.layers)
            self.units = units

    return _Zero()


class _NormDefaults:
    """A `norms@0` document under `norm-defaults@0` without a reading set: one choice, `[]`, on the norm-defaults
    route's own checkers."""

    route = "norm-defaults"

    def __init__(self, doc):
        self.doc = doc
        self.gen = _zero_generator(doc)

    def conflict_evidence(self, conflict):
        """The conflict proof or witness, before any query or model search."""
        gen = self.gen
        evidence = {"conflict": conflict}
        if len(conflict["packages"]) < len(gen.targets):
            witness = gen.witness_case()
            if witness is not None:
                found = dict(witness["witness"])
                filling = found.pop("filling")
                model = dict(found["model"])
                model["relations"] = {**model["relations"], **filling}
                evidence["witness"] = {"witness": {**found, "model": model}}
        return evidence

    def case(self, ast, extra=None, generate=True):
        gen = self.gen
        extra = dict(extra or {})
        if not generate:
            return {"environment": self.doc["environment"].to_dict(), "document": {"units": gen.units},
                    "conclusion": ast, "evidence": extra}
        conflict = extra.pop("conflict") if "conflict" in extra else {"packages": gen._packages()}
        evidence = self.conflict_evidence(conflict)
        for key, conclusion in (("certificate", ast), ("negation", ["not", ast]), ("unsat", None)):
            piece = gen.certificate_case(conclusion)
            if piece is not None:
                evidence[key] = piece
        if "unsat" not in evidence:
            model = gen.model_case(None)
            if model is not None:
                evidence["model"] = model
        if "certificate" not in evidence:
            model = gen.model_case(ast)
            if model is not None:
                evidence["countermodel"] = model
        evidence.update(extra)
        return {"environment": self.doc["environment"].to_dict(), "document": {"units": gen.units},
                "conclusion": ast, "evidence": evidence}

    def splits(self, case, rows):
        [row] = rows
        evidence = case["evidence"]
        if row["lead"] != "notNecessarily" or not row["gaps"] or "countermodel" not in evidence or "split" in evidence:
            return False
        piece = _split_piece(evidence["countermodel"], row["gaps"])
        if piece is None:
            return False
        evidence["split"] = piece
        return True

    def names(self):
        return []


def _builder(doc):
    """The generator of the document's route, by its profiles (Lean's `routeOfDocument`)."""
    profiles = set(doc["environment"].profiles)
    if "readings@1" in profiles:
        return _Readings(doc)
    if "norms@0" in profiles or "norm-defaults@0" in profiles:
        return _NormDefaults(doc)
    return _Plain(doc)


def _recorded_evidence(route: str, evidence, generate: bool):
    """Check only the container fields the Python generators read; Lean checks the pieces themselves.

    Recorded JSON is untrusted. Keep its route-specific outer shape separate from generated evidence so
    malformed containers cannot crash a generator before the request reaches Lean.
    """
    if evidence is None:
        return
    if route == "readings":
        if type(evidence) is not list or any(type(entry) is not dict or "choice" not in entry
                                                   for entry in evidence):
            raise VEError("InvalidInput: recorded readings evidence must be a list of entries with a choice")  # relay-lint: file I/O
    elif type(evidence) is not dict:
        raise VEError("InvalidInput: recorded evidence must be an object")  # relay-lint: file I/O
    if route == "norm-defaults" and generate and "conflict" in evidence:
        conflict = evidence["conflict"]
        if type(conflict) is not dict or type(conflict.get("packages")) is not dict:
            raise VEError("InvalidInput: recorded conflict evidence needs a packages object")  # relay-lint: file I/O
    pending = [(evidence, 0)]
    while pending:
        value, depth = pending.pop()
        if depth > MAX_RECORDED_DEPTH:
            raise VEError("InvalidInput: recorded evidence is too deeply nested")  # relay-lint: file I/O
        if type(value) is float and not math.isfinite(value):
            raise VEError("InvalidInput: recorded evidence contains a non-finite number")  # relay-lint: file I/O
        if type(value) is dict:
            pending.extend((child, depth + 1) for child in value.values())
        elif type(value) is list:
            pending.extend((child, depth + 1) for child in value)


# ---------------------------------------------------------------------------------------------------------------
# The relay: Lean's answer, typed by its schema and bound to the request


def _need(condition, message):
    if not condition:
        raise _Malformed(message)


class _Malformed(Exception):
    pass


def _str_list(value):
    return type(value) is list and all(type(x) is str for x in value)


def _check_source(source, request, units):
    _need(type(source) is dict and type(source.get("kind")) is str and source["kind"] in SOURCE_FIELDS,
          "a cited source is not one of the sources")
    _need(source.keys() == SOURCE_FIELDS[source["kind"]] | {"kind"}, "a cited source has other fields")
    _need(all(type(source[k]) is str for k in SOURCE_FIELDS[source["kind"]]), "a cited source names a non-string")
    predicates = request["_predicates"]
    if source["kind"] == "unit":
        _need(source["unit"] in units, f"a cited unit {source['unit']!r} is not the document's")
    elif source["kind"] == "rules":
        _need(source["predicate"] in predicates, f"cited rules on {source['predicate']!r}, not a declared predicate")
    elif source["kind"] == "definition":
        _need(source["name"] in request["_definitions"],
              f"a cited definition {source['name']!r} is not the document's")
    elif source["kind"] in ("pair", "fill"):
        _need({source["required"], source["permission"]} <= predicates, "a cited pair names undeclared predicates")


def _check_choice(choice, request):
    """A choice of the request's open sets: every set once, a candidate it has; `[]` for a one-choice route."""
    sets = request["_sets"]
    _need(type(choice) is list and all(type(x) is list and len(x) == 2 and type(x[0]) is str and type(x[1]) is int
                                       and not isinstance(x[1], bool) for x in choice), "a choice is not a choice")
    _need([s for s, _ in choice] == list(sets), "a choice does not name every open set once, in order")
    _need(all(0 <= i < sets[s] for s, i in choice), "a choice names a reading the set does not have")


def answer_problem(result, request: dict, expected: dict) -> str | None:
    """Why `result` is not Lean's answer to `request` (fully typed and bound to it), or None. Bound: the identities
    are the request's; the route is the request's; the asked sentence and formula are `english.question`'s; every
    row names a choice of the request's open sets (`[]` without one), once; every gap a declared predicate and
    elements of the models the request's evidence holds; every line's frame is a registered
    frame, its readings are named in the request, its witness is a row's choice, its cited source a unit or a
    predicate of the request, its quote a unit of the document; the text is the lines' text; the unused units are
    the document's, once each; the unchecked names are the request's. Semantics (which lead, which citations) are
    Lean's, by its theorems (DRI ruling R8)."""
    try:
        _check_answer(result, request, expected)
    except _Malformed as exc:
        return str(exc)
    except (KeyError, TypeError, ValueError, AttributeError):
        return "the answer is not of its schema"
    return None


def _check_answer(result, request, expected):
    from .backends.english_lean import QUESTION_VERSION
    from .backends.service_schema import same_json
    _need(type(result) is dict and result.keys() == ANSWERED_FIELDS, "the answer's fields are not an answer's")
    _need(result["status"] == "answered", "the answer's status is not answered")
    found = result["identities"]
    want = {**expected, "question_version": QUESTION_VERSION}
    _need(type(found) is dict and found.keys() == want.keys() and all(found[k] == want[k] for k in want),
          "the identities are not the request's")
    _need(result["route"] == request["_route"], "the answer's route is not the request's")
    reading = request["_reading"]
    _need(result["form"] == reading["form"] and result["sentence"] == reading["sentence"] and
          same_json(result["ast"], reading["ast"]) and same_json(result["spans"], reading["spans"]),
          "the asked sentence is not the question's reading")
    _need(result["lead"] in ANSWER_LEADS, "the lead is not a lead")
    units = request["_units"]
    names = {(n["set"], n["index"]): n for n in request["names"]}
    rows = result["rows"]
    _need(type(rows) is list and rows, "an answer has no row")
    choices = []
    for row in rows:
        _need(type(row) is dict and row.keys() == ROW_FIELDS, "a row's fields are not a row's")
        _check_choice(row["choice"], request)
        choices.append(json.dumps(row["choice"]))
        _need(row["lead"] in LEADS, "a row's lead is not a lead")
        _need(row["reason"] is None or row["reason"] in REASONS,
              "a row's reason is not a reason")
        _need((row["reason"] is None) == (row["lead"] != "unknown"), "a row's reason does not go with its lead")
        _need(type(row["cited"]) is list, "a row's citations are not a list")
        for source in row["cited"]:
            _check_source(source, request, units)
        _need(len({json.dumps(s, sort_keys=True) for s in row["cited"]}) == len(row["cited"]),
              "a row cites a source twice")
        _need(type(row["gaps"]) is list, "a row's gaps are not a list")
        for gap in row["gaps"]:
            _need(type(gap) is list and len(gap) == 3 and type(gap[0]) is str and _str_list(gap[1]) and
                  type(gap[2]) is bool and gap[0] in request["_predicates"], "a gap is not a predicate's tuple")
            _need(all(e in request["_elements"] for e in gap[1]),
                  "a gap names an element no model of the request's evidence has")
    _need(len(set(choices)) == len(choices), "two rows name one choice")
    expected_choices = ([e["choice"] for e in request["case"]["evidence"]]
                        if request["_route"] == "readings" else [[]])
    _need(set(choices) == {json.dumps(choice) for choice in expected_choices} and
          len(choices) == len(expected_choices), "the rows do not cover exactly the request's choices")
    lines = result["lines"]
    _need(type(lines) is list and lines, "an answer has no line")
    for line in lines:
        _need(type(line) is dict and line.keys() == LINE_FIELDS, "a line's fields are not a line's")
        _need(type(line["frame"]) is str, "a line's frame is not a string")
        _need(type(line["text"]) is str and line["text"], "a line has no text")
        _need(type(line["unchecked"]) is bool, "a line's mark is not a boolean")
        _need(type(line["readings"]) is list, "a line's readings are not a list")
        for reading_ in line["readings"]:
            _need(type(reading_) is list and len(reading_) == 2 and (reading_[0], reading_[1]) in names and
                  type(reading_[1]) is int and not isinstance(reading_[1], bool),
                  "a line names a reading the request does not name")
        if line["witness"] is not None:
            _need(json.dumps(line["witness"]) in choices, "a line's witness is not a row's choice")
        if line["source"] is not None:
            _check_source(line["source"], request, units)
        if line["quote"] is not None:
            _need(type(line["quote"]) is list and len(line["quote"]) == 2 and _str_list(line["quote"]) and
                  line["quote"][0] in units, "a line quotes a unit that is not the document's")
            _need(line["quote"][1] and line["quote"][1] in units[line["quote"][0]],
                  "a line's quote is not from its unit's text")
    _need(result["text"] == [line["text"] for line in lines], "the text is not the lines' text")
    _need(_str_list(result["unused"]) and all(u in units for u in result["unused"]) and
          len(set(result["unused"])) == len(result["unused"]), "the unused sentences are not the document's")
    _need(type(result["unchecked_names"]) is list, "the unchecked names are not a list")
    for n in result["unchecked_names"]:
        _need(type(n) is dict and n.keys() == NAME_FIELDS and
              names.get((n.get("set"), n.get("index"))) == n, "an unchecked name is not the request's")
    _need(len({(n["set"], n["index"]) for n in result["unchecked_names"]}) == len(result["unchecked_names"]),
          "an unchecked name is named twice")


def _context(request: dict, doc, raw: bytes, reading: dict, route: str) -> dict:
    """What the relay binds the answer to, beside the request: the document's units with their source text, its open
    sets with their sizes, its declared predicates, the elements of the models its evidence holds, the route and
    the reading."""
    from .document import front_matter
    meta, body = front_matter(raw)
    case = request["case"]
    reading_sets = (case.get("document") or {}).get("reading_sets") or []
    from .readings_s1 import active_sets
    sets = {}
    if route == "readings":
        active = {R["unit"]: R for R in active_sets(reading_sets)}
        for unit in case["document"]["units"]:
            R = active.get(unit["id"])
            if R is not None and R["status"] == "open":
                sets[R["id"]] = len(R["readings"])
    units = {u["id"]: body[u["span"][0]:u["span"][1]].decode("utf-8") for u in meta["units"]}
    return {"_units": units, "_sets": sets, "_predicates": set(doc["environment"].predicates),
            "_definitions": set(doc["environment"].definition_entries),
            "_elements": _elements(case.get("evidence"), set()), "_route": route, "_reading": reading}


def _elements(evidence, out: set) -> set:
    """The elements of every model in `evidence` (each `domains` map's lists): the ids a row's gaps may name."""
    pending = [evidence]
    while pending:
        value = pending.pop()
        if type(value) is dict:
            if type(value.get("domains")) is dict:
                out.update(e for elements in value["domains"].values() if type(elements) is list
                           for e in elements if type(e) is str)
            pending.extend(value.values())
        elif type(value) is list:
            pending.extend(value)
    return out


def _ask(request: dict, bound: dict, expected: dict) -> dict:
    """Lean's `ask` answer, checked against the request (`answer_problem`); Lean's refusal is raised by the relay as
    the class its code names, with Lean's text."""
    from .backends import relay
    return read_answer(relay.decide_once(MODE, request), request, bound, expected)


def read_answer(row, request: dict, bound: dict, expected: dict) -> dict:
    """The answer of the service's `ask` row for `request`, checked against the request and what it is bound to
    (`binding`); Lean's refusal raised as the class its code names, with Lean's text; anything else is
    `CheckerUnavailable`."""
    if type(row) is not dict or row.keys() != {"id", "status", "result"} or row["status"] != "ok":
        raise CheckerUnavailable(f"CheckerUnavailable: the Lean answer is not an answer: {row!r}")
    result = row["result"]
    if type(result) is dict and result.get("status") != "answered":
        problem = refusal_problem(result, expected)
        if problem:
            raise CheckerUnavailable(f"CheckerUnavailable: the Lean answer is malformed: {problem}")
        from .backends.english_lean import ERROR_CLASSES
        cls = ERROR_CLASSES[result["class"]]
        raise cls(result["text"], operation=ANSWER_OPERATION, backend="lean") \
            if issubclass(cls, CheckerUnavailable) else cls(result["text"])
    problem = answer_problem(result, {**request, **bound}, expected)
    if problem:
        raise CheckerUnavailable(f"CheckerUnavailable: the Lean answer is malformed: {problem}")
    return result


def refusal_problem(result, expected: dict) -> str | None:
    """Why `result` is not Lean's refusal of the request's question, or None: its fields are the refusal's, its
    identities the request's, and its status, code and class a status of Lean's question contract other than `one`,
    a code of that status and Lean's class of the code (`ve/question/codes.json`, the contract Lean exports)."""
    from .backends.english_lean import (ERROR_CLASSES, QUESTION_CLASSES, QUESTION_STATUS_CODES, QUESTION_VERSION)
    if type(result) is not dict or result.keys() != set(_DEFS["refused"]["properties"]):
        return "the refusal's fields are not a refusal's"
    if result["identities"] != {**expected, "question_version": QUESTION_VERSION}:
        return "the identities are not the request's"
    status, code, cls = result["status"], result["code"], result["class"]
    if status == "one" or status not in QUESTION_STATUS_CODES or code not in QUESTION_STATUS_CODES[status]:
        return f"a {status!r} refusal with the code {code!r}"
    if cls != QUESTION_CLASSES.get(code) or cls not in ERROR_CLASSES:
        return f"the class {cls!r} is not Lean's class of {code!r}"
    if type(result["text"]) is not str or not result["text"]:
        return "the refusal has no text"
    return None


class Prepared:
    """A question's request to Lean's `ask`, what the relay binds the answer to, and the route's generator."""

    def __init__(self, request, bound, expected, builder):
        self.request, self.bound, self.expected, self.builder = request, bound, expected, builder

    def ask(self) -> dict:
        """Lean's answer, asked again with a split per countermodel whose failure turns on gaps."""
        result = _ask(self.request, self.bound, self.expected)
        if self.builder.splits(self.request["case"], result["rows"]):
            result = _ask(self.request, self.bound, self.expected)
        return result


def prepare(path, raw: bytes, question: str, evidence=None, generate: bool = True) -> Prepared:
    """The request for `question` over the document at `path` (its bytes `raw`): the question is read first
    (`read`), so a question VE does not read is refused there with Lean's text; then the route's case and evidence
    are generated."""
    from .document import load_document
    reading = read(raw, question)
    doc = load_document(path)
    builder = _builder(doc)
    _recorded_evidence(builder.route, evidence, generate)
    case = builder.case(reading["ast"], evidence) if generate else builder.case(reading["ast"], evidence, False)
    lexicon, expected = _identities(raw, question, doc)
    request = {"id": MODE, "document": raw.decode("utf-8"), "question": question, "lexicon": lexicon,
               "case": case, "names": builder.names()}
    return Prepared(request, _context(request, doc, raw, reading, builder.route), expected, builder)


def _identities(raw: bytes, question: str, doc) -> tuple[dict, dict]:
    """The document's exported lexicon, and the identities an answer to `question` over it carries."""
    from .backends.english_lean import export, identities
    from .english import EnglishVocabulary
    env = environment(raw)
    words = EnglishVocabulary(env, _defer_overlay_refusals=True)
    lexicon = export(words)
    return lexicon, {**identities(env, question, words, lexicon), "document_id": doc["document_id"]}


def binding(path, raw: bytes, request: dict) -> tuple[dict, dict]:
    """What Lean's answer to `request` is bound to, as `prepare` binds it: the relay's context and the identities;
    `path` holds the request's document, `raw` its bytes. The relay mutation gate reads a mutated answer with it."""
    from .document import load_document
    doc = load_document(path)
    reading = read(raw, request["question"])
    return (_context(request, doc, raw, reading, _builder(doc).route),
            _identities(raw, request["question"], doc)[1])


def answer(path, raw: bytes, question: str, evidence=None) -> dict:
    """Lean's answer to `question` over the document at `path`, Lean's refusal raised as its class."""
    return prepare(path, raw, question, evidence).ask()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ve ask",
        description="Answer a yes-or-no question about a document, in Lean's words, from Lean's checked answer.")
    parser.add_argument("document", help="ve-document file")
    parser.add_argument("question", help="the question, ending with its only question mark")
    parser.add_argument("--reading", action="store_true", help="print only the sentence the question is read as")
    parser.add_argument("--json", action="store_true", help="print Lean's whole result with the honesty fields")
    parser.add_argument("--evidence", help="recorded evidence pieces to add (Lean checks them as every piece)")
    options = parser.parse_args(argv)
    from .assurance import operation
    name = OPERATION if options.reading else ANSWER_OPERATION
    honesty = {"operation": name, "assurance": operation(name)["assurance"]["current"], "intent": "unconfirmed",
               "proof": "not_checked" if options.reading else "lean_checked",
               "answer": "not_asked" if options.reading else "lean"}

    def emit(result: dict | None, error: dict | None = None) -> None:
        if options.json:
            fields = {**honesty, **({"proof": "not_checked", "answer": "no_answer"} if error is not None else {})}
            if error is None and result is not None and options.evidence and not options.reading:
                fields["evidence"] = "recorded"
            print(json.dumps({**fields, **({"result": result} if result is not None else {}),
                              **({"error": error} if error is not None else {})}, ensure_ascii=False, indent=2))
        elif result is not None:
            print("\n".join(result["text"] if result.get("status") == "answered" else _lines(result)))
        else:
            print(error["message"], file=sys.stderr)

    try:
        path = Path(options.document)
        with path.open("rb") as stream:
            raw = stream.read(MAX_DOCUMENT_BYTES + 1)
        if len(raw) > MAX_DOCUMENT_BYTES:
            raise ResourceLimit(f"ResourceLimit: {options.document!r} exceeds {MAX_DOCUMENT_BYTES} bytes")  # relay-lint: file I/O
        if options.reading:
            result = read(raw, options.question)
        else:
            evidence = None
            if options.evidence:
                try:
                    evidence = json.loads(Path(options.evidence).read_text(encoding="utf-8"))
                except RecursionError as exc:
                    raise VEError("InvalidInput: recorded evidence is too deeply nested") from exc  # relay-lint: file I/O
                if evidence is None:
                    raise VEError("InvalidInput: recorded evidence cannot be null")  # relay-lint: file I/O
            result = answer(path, raw, options.question, evidence)
    except CheckerUnavailable as exc:
        emit(_answer(exc), {"class": "CheckerUnavailable", "message": str(exc)})
        return EXIT_UNAVAILABLE
    except ResourceLimit as exc:
        emit(_answer(exc), {"class": "ResourceLimit", "message": str(exc)})
        return EXIT_LIMIT
    except (VEError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        emit(_answer(exc), {"class": type(exc).__name__, "message": str(exc)})
        return EXIT_NOT_READ
    emit(result)
    if options.reading:
        return EXIT_READ
    return EXIT_UNKNOWN if result["lead"] == "unknown" else EXIT_READ
