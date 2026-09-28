"""Experimental ve-document@2 source wrapper; never admits P0 evidence.

The exact reviewed metadata, source bytes and fence text are retained for the
new document identity.  Ambiguous reading choices remain pending until the
speech-act choice route exists.
"""
from __future__ import annotations

import hashlib
from itertools import takewhile
import json
from pathlib import Path

from .admission import _check_kind, token
from .document import _body, _meaning, _parts, SUPPORTS, MAX_DOCUMENT_BYTES
from .environment import Environment
from .errors import ResourceLimit, VEError
from .identity import source_id
from .openterms import validate_open_terms
from .readings import active_reading_sets, plan_choices, validate_narrowings, validate_reading_sets
from .speech_acts import (SpeechDocument, choice_kind_conflicts, content_kind_ok, effective_scope,
                          fixed_assertion_ids, formula_shape, latest_reading_sets, query_records,
                          _reading_choice)
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
    # Every reference is a name (or a version number) before it is resolved, with the
    # cores' diagnostic (`latest_reading_sets`, Lean's `readingStates`), in W2's sets too.
    if any(type(item.get("unit")) is not str or type(item.get("version")) is not int
           or item.get("status") not in ("open", "authored") for item in sets):
        raise VEError("InvalidInput: reading sets on the speech-acts route need their unit, version and status")
    # A formula candidate's structure as the Lean route reads it (`formula_shape`).
    for item in sets:
        for reading in item["readings"]:
            if type(reading) is dict and type(reading.get("content")) is list:
                formula_shape(reading["content"])
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
        if not token(item["id"]) or item["version"] < 1:
            raise VEError("invalid or duplicate reading set version")
        key = item["id"], item["version"]
        if key in seen:
            raise VEError("invalid or duplicate reading set version")
        if item["unit"] not in unit_ids:  # W2's and the cores' text for a dangling unit
            raise VEError("invalid reading set unit or status")
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
        # References to sibling candidates are collected below. Validate every
        # candidate id first, including candidates later in the list.
        if any(type(reading) is not dict or not token(reading.get("id"))
               for reading in item["readings"]):
            raise VEError("invalid reading")
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
                if not content_kind_ok(reading["kind"], next(iter(reading["content"]))):
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
        wordings = {}  # unit id -> its span's sentence, the one wording every check of the unit reads (3.2)
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
            if type(unit["support"]) is not str or unit["support"] not in SUPPORTS:
                raise VEError("invalid support")
            content = unit.get("content")
            if type(content) is dict and "fence" in content:
                if content["fence"] != uid or uid not in fences:
                    raise VEError("unit fence must match its id")
                if unit.get("surface") != "english":
                    raise VEError("speech fence needs English surface")
            wordings[uid] = wording.strip()
            self.units.append({**unit, "content": content,
                               **({"source": wordings[uid]} if kind in ("instruction", "question") else {}),
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
        latest = latest_reading_sets(sets)
        # 3.2: a signed choice is checked against the source sentence, its unit's span, in the inline and the
        # fenced form alike (a fence is the unit's content, which the choice replaces).  The core receives the
        # same wording for every chosen unit, whatever its original kind, so it checks the chosen command or
        # question against it as it does an unchosen one.
        for unit in self.units:
            chosen = latest.get(unit["id"])
            if chosen is not None and chosen["status"] == "authored":
                if choice_kind_conflicts(self.env, chosen["readings"][0]["kind"], wordings[unit["id"]]):
                    raise VEError("InvalidInput: choice kind")
                unit["source"] = wordings[unit["id"]]
        # 1.1: a fence is read under the effective scope, so a phrase or "you" an
        # authored binding supplies reads as if the block declared it.  The scope is
        # the document's own merge, so a fenced and an unfenced source agree.
        # A wording that names neither its query nor its reading set leaves them to the
        # document, which regenerates them at the unit (`_fence_context`).
        fenced = [u for u in self.units if type(u["content"]) is dict and "fence" in u["content"]]
        if fenced:
            from .speech_english import parse_speech
            scope = effective_scope(self.env, self.units, sets)
            for unit in fenced:
                text = fences[unit["id"]].strip()
                reading_set = latest.get(unit["id"])
                if reading_set is not None and reading_set["status"] == "authored":
                    continue
                effective_kind = unit["kind"]
                if effective_kind == "asserted":
                    from .ast import _to_data
                    from .speech_english import _sentence
                    parsed = _to_data(_sentence(self.env, text))
                    parsed_kind = "asserted"
                else:
                    parsed, parsed_kind = parse_speech(self.env, text, scope,
                                                       **self._fence_context(unit, text, sets))
                if parsed_kind != effective_kind:
                    raise VEError("fence kind disagrees with unit")
                unit["content"] = ({"ast": parsed} if parsed_kind == "asserted" else
                                   {"command" if parsed_kind == "instruction" else "question": parsed})
        self.document = SpeechDocument(self.env, self.units, meta.get("queries", []), reading_sets=sets)
        from .identity import meaning_id
        from .speech_acts import _formula
        from .norms import NormDocument, norm_meaning_id
        for unit in self.units:
            if "meaning_id" not in unit:
                continue
            uid = unit["id"]
            expected = self.document.meaning_ids.get(uid)
            if expected is None:
                effective = next(u for u in self.document._effective if u["id"] == uid)
                content = effective.get("content")
                if type(content) is dict and set(content) == {"ast"}:
                    expected = meaning_id(self.document.env, _formula(self.document.env, content["ast"]))
                elif type(content) is list:
                    expected = meaning_id(self.document.env, _formula(self.document.env, content))
                elif type(content) is dict and set(content) == {"norm"}:
                    expected = norm_meaning_id(self.document.env, NormDocument._decode(content))
            if unit["meaning_id"] != expected:
                raise VEError("unit meaning id does not match content")
        for unit in self.units:
            if unit.get("status") not in (None, _w2_status(unit, latest.get(unit["id"]))):
                raise VEError("unit status contradicts content, meaning, or active reading set")
        by_name = {term["name"]: term for term in self.open_terms}
        # 4.1(4) and 4.6: every reading question, asked or a candidate of a unit's
        # latest reading set (as it would be if chosen), carries its derived open term;
        # the core has already resolved the set and version it names.
        candidates = [q for item, q in self.document.candidate_questions if latest[item["unit"]] is item]
        for question in [*self.document.questions, *candidates]:
            if question.mode == "reading":
                expected = _expected_open_term(self.document, question)
                if by_name.get(expected["name"]) != expected:
                    raise VEError(f"InvalidInput: invalid question fields for {question.unit}")
        weights = meta.get("weights", [])
        if type(weights) is not list:
            raise VEError("invalid removable reading weights")
        self.identity_payload = {"metadata": {k: v for k, v in meta.items() if k != "weights"},
                                 "source": source_text, "fences": fences}
        # W2's payload in W2's own encoding (ve/document.py): its reading sets may
        # hold `null` for an unelaborated candidate, which canonical_json refuses.
        canonical_json({k: v for k, v in self.identity_payload.items() if k != "metadata"})
        self.document_id = hashlib.sha256(
            b"ve-document@2\n" + json.dumps(self.identity_payload, sort_keys=True, ensure_ascii=False,
                                             separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()
        self.source_id = source_id(source, self.env)
        self.reading_plan = plan_choices([r for r in active_reading_sets(sets) if r["status"] == "open"])
        self.answers = meta.get("answers", [])
        self.compliance = meta.get("compliance", [])
        self.answer_lines = self._answer_records()
        self.compliance_lines = self._compliance_records()

    def _fence_context(self, unit, text, sets):
        """What a fenced wording leaves to its document, regenerated at its unit as for an unfenced one.

        "Does it follow from these premises that P?" and "Prove that P using these
        premises." are about the one query record whose premises are the fixed
        asserted units before the unit and whose target is P (1.4): none or more
        than one is `QueryMismatch: <u>`.  "Which reading did you mean?" asks about
        the set version its unit's derived open term names (4.6); a unit without
        that meaning and declaration is `invalid question fields for <u>`.  The
        document built afterwards checks the result exactly as an unfenced unit.
        """
        from .speech_english import _sentence
        uid = unit["id"]
        if text == "Which reading did you mean?":
            name = f"intended-reading.{uid}"
            term = next((t for t in self.open_terms if t["name"] == name), None)
            effective = unit["meaning"]
            latest = latest_reading_sets(sets).get(uid)
            if latest is not None and latest["status"] == "authored":
                effective = _reading_choice(unit, latest)["meaning"]
            if effective != {"open": [name]} or term is None or len(term["arguments"]) != 1:
                raise VEError(f"InvalidInput: invalid question fields for {uid}")
            return {"reading_set": (term["arguments"][0], term["version"])}
        for prefix, suffix in (("Does it follow from these premises that ", "?"),
                               ("Prove that ", " using these premises.")):
            if text.startswith(prefix) and text.endswith(suffix):
                target = _sentence(self.env, text[len(prefix):-len(suffix)] + ".")
                before = takewhile(lambda other: other["id"] != uid, self.units)
                premises = fixed_assertion_ids(before, sets)
                ids = {q.id for q in query_records(self.env, self.metadata.get("queries", []))
                       if list(q.premises) == premises and q.target == target}
                if len(ids) != 1:
                    raise VEError(f"QueryMismatch: {uid}")
                return {"query": ids.pop()}
        return {}

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
            if "conditional" in record and type(record["conditional"]) is not bool:
                raise VEError("InvalidInput: conditional")
            if type(record["by"]) is not str or not token(record["by"]):
                raise VEError("InvalidInput: answer record")
            uid = record["question"]
            if type(uid) is not str:
                raise VEError("InvalidInput: answer record")
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
                    answer_token = answer["one"]
                elif question.mode == "which_all":
                    if type(answer) is not dict or set(answer) != {"all"} or type(answer["all"]) is not list:
                        raise VEError(f"AnswerOutsideDomain: {uid}, {answer}")
                    answer_token = tuple(answer["all"])
                else:
                    answer_token = answer
                if support == "certificate" and set(record["evidence"]) == {"certificate"}:
                    line = self.document.check_answer_certificate(
                        question, answer_token, record["evidence"]["certificate"],
                        conditional=record.get("conditional", False))
                elif support == "model" and set(record["evidence"]) == {"model"}:
                    line = self.document.evaluate_answer_model(
                        question, answer_token, record["evidence"]["model"])
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
            if (type(record) is not dict or set(record) != {"command", "evidence"} or type(record["command"]) is not str
                    or record["command"] not in by_id or type(record["evidence"]) is not dict):
                raise VEError("InvalidInput: compliance record")
            command = by_id[record["command"]]
            qid = self.document.query_of(command)
            if qid is None or set(record["evidence"]) != {"certificate"}:
                raise VEError(f"QueryMismatch: {command.unit}")
            # 5.3 and 5.4: a proof task's certificate line carries the status of Π_q, as a follows line does.
            line = self.document.check_consequence_certificate(qid, record["evidence"]["certificate"])
            lines.append({"command": command.unit, "status": "certificate", "query": qid,
                          "premises": line["premises"], "vacuous": line["vacuous"]})
        return lines

    def coverage(self):
        """Section 6's classes beside W2's own status table, reconciled per unit.

        The statuses are W2's inference (document.md: content and meaning, then
        the active reading set) and the classes the section 6 precedence; each
        is computed from the unit, and a unit whose pair breaks the fixed
        mapping CHECKED ↦ C, OPEN ↦ R/O/U, LABELLED ↦ L, UNFORMALISED ↦ U is an
        error, never a silent reclassification.
        """
        latest = latest_reading_sets(self.reading_sets)
        classes = {}
        statuses = {}
        for unit in self.units:
            length = unit["span"][1] - unit["span"][0]
            reading_set = latest.get(unit["id"])
            status = _w2_status(unit, reading_set)
            cls = _speech_class(unit, reading_set)
            if cls not in _RECONCILES[status]:
                raise VEError(f"coverage reconciliation: {unit['id']} is {status} but class {cls}")
            classes[cls] = classes.get(cls, 0) + length
            statuses[status] = statuses.get(status, 0) + length
        assert sum(classes.values()) == sum(statuses.values()) == len(self.source)
        return {"bytes_by_class": classes, "bytes_by_status": statuses,
                "residual": {"open_terms": len(self.open_terms),
                             "unresolved_sets": sum(r["status"] == "open" for r in latest.values())}}


_RECONCILES = {"CHECKED": {"C"}, "OPEN": {"R", "O", "U"}, "LABELLED": {"L"}, "UNFORMALISED": {"U"}}


def _meaning_status(meaning):
    return meaning if meaning == "specified" else next(iter(meaning))


def _w2_status(unit, reading_set):
    """W2's status inference (ve/document.py), unchanged: an active set decides, else content and meaning."""
    if reading_set is not None:
        return ("CHECKED" if reading_set["status"] == "authored"
                and all(c["kind"] == "asserted" and c["content"] is not None for c in reading_set["readings"])
                else "OPEN")
    status = _meaning_status(unit["meaning"])
    return ("CHECKED" if unit["content"] is not None and status == "specified" else
            "OPEN" if status == "open" else "UNFORMALISED" if status == "unformalised" else "LABELLED")


def _speech_class(unit, reading_set):
    """Section 6's precedence U, R, O, C, else L, over the unit and its latest reading set."""
    status = _meaning_status(unit["meaning"])
    if status == "unformalised":
        return "U"
    if reading_set is not None:
        if any(c["content"] is None for c in reading_set["readings"]):
            return "U"  # an unelaborated candidate (or an unelaborated signed choice)
        if reading_set["status"] == "open":
            return "R"
        # A signed choice W2 checks itself is C; one it stores under OPEN is R.
        return "C" if all(c["kind"] == "asserted" for c in reading_set["readings"]) else "R"
    if status == "open":
        return "O"
    return "C" if unit["content"] is not None and status == "specified" else "L"


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
