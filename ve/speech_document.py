"""Experimental ve-document@2 source wrapper; never admits P0 evidence.

The exact reviewed metadata, source bytes and fence text are retained for the
new document identity.  Ambiguous reading choices remain pending until the
speech-act choice route exists.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .admission import _check_kind, token
from .document import _body, _meaning, _parts, SUPPORTS, MAX_DOCUMENT_BYTES
from .environment import Environment
from .errors import ResourceLimit, VEError
from .identity import source_id
from .openterms import validate_open_terms
from .readings import active_reading_sets, plan_choices, validate_narrowings, validate_reading_sets
from .speech_acts import SpeechDocument
from .wire import canonical_json

_ALLOWED_META = {"format", "environment", "units", "open_terms", "reading_sets", "narrowings",
                 "weights", "graph", "lemmas", "queries", "answers", "compliance"}


def _reading_sets(env, sets, unit_ids):
    """Validate W2 assertion sets fully and retain speech candidates structurally.

    A speech choice has no verdict here.  In particular we never use W2's
    assertion-disjunction shortcut for a command or question candidate.
    """
    if type(sets) is not list:
        raise VEError("reading_sets must be a list")
    if any(type(item) is not dict or type(item.get("readings")) is not list for item in sets):
        raise VEError("invalid reading set")
    ordinary = [r for r in sets if all(c.get("kind") == "asserted" and
                (c.get("content") is None or type(c["content"]) is list)
                for c in r["readings"] if type(c) is dict)
                and all(type(c) is dict for c in r["readings"])]
    validate_reading_sets(env, ordinary, unit_ids)
    seen = {(r["id"], r["version"]) for r in ordinary}
    owners = {r["id"]: r["unit"] for r in ordinary}
    units = {r["unit"]: r["id"] for r in ordinary}
    for item in sets:
        if item in ordinary:
            continue
        if (type(item) is not dict or not {"id", "unit", "version", "status", "readings"} <= set(item)
                or set(item) - {"id", "unit", "version", "status", "readings", "signature",
                                "rejected_history", "models"}):
            raise VEError("invalid reading set")
        key = item["id"], item["version"]
        if (not token(item["id"]) or type(item["version"]) is not int or item["version"] < 1
                or key in seen or item["unit"] not in unit_ids or item["status"] not in ("open", "authored")):
            raise VEError("invalid or duplicate reading set version")
        if (item["id"] in owners and owners[item["id"]] != item["unit"]
                or item["unit"] in units and units[item["unit"]] != item["id"]):
            raise VEError("one reading set per source unit; versions must keep their unit")
        seen.add(key)
        owners[item["id"]] = item["unit"]
        units[item["unit"]] = item["id"]
        if type(item["readings"]) is not list or not 1 <= len(item["readings"]) <= 64:
            raise VEError("reading sets hold 1 to 64 readings")
        if any(type(reading) is not dict for reading in item["readings"]):
            raise VEError("invalid reading")
        if item["status"] == "authored" and (len(item["readings"]) != 1 or not token(item.get("signature"))):
            raise VEError("authored reading needs one signed choice")
        if item["status"] == "open" and "signature" in item:
            raise VEError("open reading set cannot have an author signature")
        ids = set()
        for reading in item["readings"]:
            if (type(reading) is not dict or set(reading) != {"id", "kind", "meaning_id", "content", "admission"}
                    or not token(reading["id"]) or reading["id"] in ids
                    or not token(reading["meaning_id"])):
                raise VEError("invalid reading")
            ids.add(reading["id"])
            if reading["kind"] != "binding":
                _check_kind(reading["kind"])
            if reading["content"] is not None and (type(reading["content"]) is not dict
                                                    or len(reading["content"]) != 1):
                raise VEError("invalid speech reading content")
            if reading["content"] is not None:
                tag = next(iter(reading["content"]))
                if tag not in {"ast", "norm", "command", "question", "binding"}:
                    raise VEError("invalid speech reading content")
                kind = reading["kind"]
                bare_kind = kind if type(kind) is str else kind[-1] if type(kind) is list else None
                if bare_kind != {"ast": "asserted", "norm": "norm", "command": "instruction",
                                 "question": "question", "binding": "binding"}[tag]:
                    raise VEError("invalid speech reading content")
            admission = reading["admission"]
            if (type(admission) is not dict or set(admission) != {"who", "why", "distinguishing_models"}
                    or not token(admission["who"]) or type(admission["why"]) is not str or not admission["why"]
                    or type(admission["distinguishing_models"]) is not dict):
                raise VEError("invalid reading admission")
            if (set(admission["distinguishing_models"]) !=
                    {other["id"] for other in item["readings"]} - {reading["id"]}):
                raise VEError("each other reading needs a distinguishing model id")
            if not all(token(v) for v in admission["distinguishing_models"].values()):
                raise VEError("invalid distinguishing model id")
        model_ids = {model_id for reading in item["readings"]
                     for model_id in reading["admission"]["distinguishing_models"].values()}
        if type(item.get("models", {})) is not dict or set(item.get("models", {})) != model_ids:
            raise VEError("distinguishing models must be supplied by id")
        if "rejected_history" in item and type(item["rejected_history"]) is not list:
            raise VEError("invalid rejected reading history")
    validate_narrowings([], sets, unit_ids)


def _expected_open_term(doc, question):
    if "addressee" not in doc.scope:
        raise VEError("UnboundSlot: you")
    set_id, version = question.reading_set
    by = doc.scope["addressee"]["constant"]
    wording = f"a candidate of {set_id} at version {version} by {by}"
    return {"name": f"intended-reading.{question.unit}", "arguments": [set_id],
            "version": version, "decided_by": by, "jurisdiction": doc.scope["task"],
            "necessary": [], "sufficient": [], "precedents": [],
            "factors": [f"necessary: at least one nomination of {wording}",
                        f"sufficient: exactly one nomination of {wording}"]}


class SpeechSource:
    def __init__(self, meta, source, fences):
        if type(meta) is not dict or meta.get("format") != "ve-document@2" or set(meta) - _ALLOWED_META:
            raise VEError("unsupported document format")
        if type(meta.get("environment")) is not dict:
            raise VEError("document needs an embedded environment")
        self.env = Environment(meta["environment"])
        if "speech-acts@0" not in self.env.profiles:
            raise VEError("UnsupportedProfile: speech-acts@0 required")
        if type(source) is not bytes or not source:
            raise VEError("document source is empty")
        try:
            source_text = source.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise VEError("document source is not UTF-8") from exc
        self.metadata = meta
        self.source = source
        self.fences = dict(fences)
        raw_units = meta.get("units")
        if type(raw_units) is not list or not raw_units:
            raise VEError("document needs units")
        self.units = []
        cursor = 0
        ids = set()
        for unit, parent in _parts(raw_units):
            if (type(unit) is not dict or not {"id", "span", "kind", "meaning", "support"} <= set(unit)
                    or set(unit) - {"id", "span", "kind", "meaning", "support", "content",
                                    "surface", "meaning_id", "status"}):
                raise VEError("invalid unit schema")
            uid, span = unit["id"], unit["span"]
            if (not token(uid) or uid in ids or type(span) is not list or len(span) != 2
                    or any(type(x) is not int for x in span) or span[0] != cursor
                    or span[1] <= cursor or span[1] > len(source)):
                raise VEError("unit spans must partition every source byte in order")
            ids.add(uid)
            cursor = span[1]
            try:
                wording = source[span[0]:span[1]].decode("utf-8")
            except UnicodeDecodeError as exc:
                raise VEError("unit span cuts a UTF-8 character") from exc
            kind = unit["kind"]
            if kind != "binding":
                _check_kind(kind)
            if unit["support"] not in SUPPORTS:
                raise VEError("invalid support")
            content = unit.get("content")
            if type(content) is dict and "fence" in content:
                if content["fence"] != uid or uid not in fences:
                    raise VEError("unit fence must match its id")
                if unit.get("surface") != "english":
                    raise VEError("speech fence needs English surface")
                from .speech_english import parse_speech
                parsed, parsed_kind = parse_speech(self.env, fences[uid].strip(),
                                                   self.env.to_dict()["speech_acts"])
                if parsed_kind != kind:
                    raise VEError("fence kind disagrees with unit")
                content = {"command" if kind == "instruction" else "question": parsed}
            self.units.append({**unit, "content": content,
                               **({"source": wording.strip()} if kind in ("instruction", "question") else {}),
                               **({"parent_id": parent} if parent is not None else {})})
        if cursor != len(source):
            raise VEError("unit spans do not partition all source bytes")
        self.open_terms = meta.get("open_terms", [])
        open_names = validate_open_terms(self.env, self.open_terms)
        for unit in self.units:
            _meaning(unit["meaning"], open_names)
        sets = meta.get("reading_sets", [])
        _reading_sets(self.env, sets, ids)
        self.reading_sets = sets
        self.narrowings = meta.get("narrowings", [])
        validate_narrowings(self.narrowings, sets, ids)
        pending = {r["unit"] for r in active_reading_sets(sets)}
        self.document = SpeechDocument(self.env, self.units, meta.get("queries", []), pending_units=pending)
        by_name = {term["name"]: term for term in self.open_terms}
        for question in self.document.questions:
            if question.mode == "reading":
                if question.reading_set not in {(r["id"], r["version"]) for r in sets}:
                    raise VEError(f"InvalidInput: invalid question fields for {question.unit}")
                expected = _expected_open_term(self.document, question)
                if by_name.get(expected["name"]) != expected:
                    raise VEError(f"InvalidInput: invalid question fields for {question.unit}")
        weights = meta.get("weights", [])
        if type(weights) is not list:
            raise VEError("invalid removable reading weights")
        self.identity_payload = {"metadata": {k: v for k, v in meta.items() if k != "weights"},
                                 "source": source_text, "fences": fences}
        self.document_id = hashlib.sha256(b"ve-document@2\n" + canonical_json(self.identity_payload)).hexdigest()
        self.source_id = source_id(source, self.env)
        self.reading_plan = plan_choices([r for r in active_reading_sets(sets) if r["status"] == "open"])
        self.answers = meta.get("answers", [])
        self.compliance = meta.get("compliance", [])
        self.answer_lines = self._answer_records()
        self.compliance_lines = self._compliance_records()

    def _answer_records(self):
        if type(self.answers) is not list:
            raise VEError("InvalidInput: answers")
        by_id = {q.unit: q for q in self.document.questions}
        lines = []
        for record in self.answers:
            if (type(record) is not dict or not {"question", "by", "support", "evidence"} <= set(record)
                    or set(record) - {"question", "by", "support", "evidence", "answer",
                                      "conditional", "judgment"}):
                raise VEError("InvalidInput: answer record")
            uid = record["question"]
            if uid not in by_id or type(record["evidence"]) is not dict:
                raise VEError(f"AnswerMismatch: {uid}")
            question = by_id[uid]
            support = record["support"]
            if question.mode == "follows":
                if (record.get("judgment") not in ("follows", "gap") or
                        record.get("judgment") != "follows" or support != "certificate"
                        or set(record["evidence"]) != {"certificate"}):
                    raise VEError("InvalidInput: judgment")
                line = self.document.check_consequence_certificate(
                    question.query, record["evidence"]["certificate"])
            elif question.mode in ("polar", "which_one", "which_all"):
                if "answer" not in record or "judgment" in record:
                    raise VEError(f"AnswerMismatch: {uid}")
                answer = record["answer"]
                if question.mode == "which_one":
                    if type(answer) is not dict or set(answer) != {"one"}:
                        raise VEError(f"AnswerOutsideDomain: {uid}, {answer}")
                    token = answer["one"]
                elif question.mode == "which_all":
                    if type(answer) is not dict or set(answer) != {"all"} or type(answer["all"]) is not list:
                        raise VEError(f"AnswerOutsideDomain: {uid}, {answer}")
                    token = tuple(answer["all"])
                else:
                    token = answer
                if support == "certificate" and set(record["evidence"]) == {"certificate"}:
                    line = self.document.check_answer_certificate(
                        question, token, record["evidence"]["certificate"],
                        conditional=record.get("conditional", False))
                elif support == "model" and set(record["evidence"]) == {"model"}:
                    line = self.document.evaluate_answer_model(
                        question, token, record["evidence"]["model"])
                else:
                    raise VEError(f"AnswerMismatch: {uid}")
            else:
                raise VEError(f"NominationOutsideSet: {uid}")
            lines.append({"question": uid, **line})
        return lines

    def _compliance_records(self):
        if type(self.compliance) is not list:
            raise VEError("InvalidInput: compliance")
        by_id = {c.unit: c for c in self.document.commands}
        lines = []
        for record in self.compliance:
            if (type(record) is not dict or set(record) != {"command", "evidence"}
                    or record["command"] not in by_id or type(record["evidence"]) is not dict):
                raise VEError("InvalidInput: compliance record")
            command = by_id[record["command"]]
            qid = self.document.query_of(command)
            if qid is None or set(record["evidence"]) != {"certificate"}:
                raise VEError(f"QueryMismatch: {command.unit}")
            self.document.check_consequence_certificate(qid, record["evidence"]["certificate"])
            lines.append({"command": command.unit, "status": "certificate", "query": qid})
        return lines

    def coverage(self):
        classes = {}
        statuses = {}
        for unit in self.units:
            length = unit["span"][1] - unit["span"][0]
            meaning = unit["meaning"]
            cls = ("U" if type(meaning) is dict and "unformalised" in meaning else
                   "R" if unit["id"] in {r["unit"] for r in self.reading_sets} else
                   "O" if type(meaning) is dict and "open" in meaning else
                   "C" if unit["content"] is not None else "L")
            classes[cls] = classes.get(cls, 0) + length
            status = "OPEN" if cls in ("R", "O") else "UNFORMALISED" if cls == "U" else "CHECKED" if cls == "C" else "LABELLED"
            statuses[status] = statuses.get(status, 0) + length
        assert sum(classes.values()) == sum(statuses.values()) == len(self.source)
        return {"bytes_by_class": classes, "bytes_by_status": statuses,
                "residual": {"open_terms": len(self.open_terms),
                             "unresolved_sets": len(self.reading_sets)}}


def load_speech_document(path):
    raw = Path(path).read_bytes()
    if len(raw) > MAX_DOCUMENT_BYTES:
        raise ResourceLimit("document byte budget")
    if not raw.startswith(b"---\n"):
        raise VEError("ve-document@2 needs JSON front matter")
    boundary = raw.find(b"\n---\n", 4)
    if boundary < 0:
        raise VEError("unclosed JSON front matter")
    def unique_fields(pairs):
        result = {}
        for name, value in pairs:
            if name in result:
                raise ValueError("duplicate front-matter field")
            result[name] = value
        return result

    def integer(value):
        number = int(value)
        if not 0 <= number <= 2**53 - 1:
            raise ValueError("front-matter integer out of range")
        return number

    def invalid_number(_value):
        raise ValueError("unsupported front-matter number")

    try:
        meta = json.loads(raw[4:boundary].decode("utf-8"), object_pairs_hook=unique_fields,
                          parse_int=integer, parse_float=invalid_number, parse_constant=invalid_number)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise VEError("invalid JSON front matter") from exc
    source, fences = _body(raw[boundary + 5:])
    return SpeechSource(meta, source, fences)
