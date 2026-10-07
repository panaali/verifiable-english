"""Source file reading and display projection for Lean's speech-source route.

The source decoder, identity, coverage, answer and compliance decisions live in
VE.SpeechActs.Source. Python only reads the file and displays its bound report.
"""
from __future__ import annotations

import json
from pathlib import Path

from .ast import _to_data, formula_from_data
from .backends.relay import decide_once
from .backends.speech_source import decide_source
from .document import _body, _parts, MAX_DOCUMENT_BYTES
from .environment import Environment
from .errors import CheckerUnavailable, ResourceLimit, VEError
from .readings import active_reading_sets, plan_choices
from .speech_acts import wording_text
from .speech_english import _sentence, parse_speech
from .speech_english import legend
from .vacuity import search_premise_status_witness


class SpeechSource:
    """A display projection constructed only after Lean accepts a W2 source."""

    def __init__(self, meta, source, fences):
        if type(source) is not bytes:
            raise VEError("document source is not UTF-8")  # relay-lint: file I/O
        try:
            text = source.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise VEError("document source is not UTF-8") from exc  # relay-lint: file I/O
        try:
            self.report = decide_source(meta, text, fences)
        except VEError as exc:
            if exc.message != "NotImplemented: fenced English content":
                raise
            resolved = _resolve_fences(meta, fences)
            self.report = decide_source(meta, text, fences, resolved_fences=resolved)
        else:
            resolved = None
        try:
            effective = {**meta["environment"], "speech_acts": self.report["scope"]}
            env = Environment(effective)
        except (VEError, KeyError, TypeError) as exc:
            raise CheckerUnavailable("CheckerUnavailable: Python could not construct Lean's effective speech scope") from exc
        evidence = _premise_evidence(meta, self.report, env)
        if evidence:
            self.report = decide_source(meta, text, fences, resolved_fences=resolved, premise_status=evidence)
        self.metadata = meta
        self.source = source
        self.fences = fences
        self.document_id = self.report["document_id"]
        self.source_id = self.report["source_id"]
        answer_indices = [i for i, row in enumerate(meta.get("answers", [])) if "nominate" not in row]
        self.answer_lines = [_display_record(row, evidence.get("answers", {}).get(str(i), {}))
                             for i, row in zip(answer_indices, self.report["answers"], strict=True)]
        self.compliance_lines = [_display_record(row, evidence.get("compliance", {}).get(str(i), {}))
                                 for i, row in enumerate(self.report["compliance"])]
        try:
            self.legend = legend(env)
            sets = meta.get("reading_sets", [])
            self.reading_plan = plan_choices([s for s in active_reading_sets(sets) if s["status"] == "open"])
        except (VEError, KeyError, TypeError, ValueError, IndexError) as exc:
            raise CheckerUnavailable("CheckerUnavailable: Python could not display Lean's accepted speech source") from exc

    def coverage(self):
        return self.report["coverage"]


def _display_record(row, status_evidence):
    """Project Lean's checked status with the Python generator's search detail."""
    result = {key: value for key, value in row.items()
              if key != "line" or row.get("status") == "gap" or "unit" in row}
    if "premises" in result:
        premise = result["premises"]
        if premise["status"] == "INCONSISTENT":
            result["premises"] = {**premise, "certificate": status_evidence["inconsistent"]}
        elif premise["status"] == "UNKNOWN":
            result["premises"] = {**premise, "budget": {"max_proof_steps": 10_000,
                "max_domain_size": 2, "max_models": 10_000, "max_evaluations": 100_000}}
    return result


def _premise_evidence(meta, report, env):
    """Offer the existing premise search's witnesses; Lean checks each one."""
    answers = meta.get("answers", [])
    compliance = meta.get("compliance", [])
    if not any(type(r) is dict and r.get("support") == "certificate" for r in answers) and not compliance:
        return {}
    by_question = {q["unit"]: q for q in report["questions"]}
    by_query = {q["id"]: q for q in report["queries"]}
    by_command = {r["command"]: r for r in report["compliance"]}
    cache = {}

    def propose(raw):
        key = json.dumps(raw, sort_keys=True)
        if key not in cache:
            premises = [formula_from_data(env, ast) for ast in raw]
            result = search_premise_status_witness(env, premises)
            if result["status"] == "model":
                wire = result["model"]
                wire["relations"] = {name: rows for name, rows in wire["relations"].items()
                                     if env.predicates[name].regulated is None}
                cache[key] = {"model": wire}
            elif result["status"] == "INCONSISTENT":
                cache[key] = {"inconsistent": result["certificate"]}
            else:
                cache[key] = None
        return cache[key]

    evidence = {"answers": {}, "compliance": {}}
    for index, record in enumerate(answers):
        if type(record) is not dict or record.get("support") != "certificate":
            continue
        question = by_question[record["question"]]
        if question["mode"] == "follows":
            raw = by_query[question["query"]]["premises"]
        else:
            raw = [*report["premises"], *([question["presupposition"]]
                                             if record.get("conditional") else [])]
        if (proposal := propose(raw)) is not None:
            evidence["answers"][str(index)] = proposal
    for index, record in enumerate(compliance):
        if type(record) is not dict or record.get("command") not in by_command:
            continue
        checked = by_command[record["command"]]
        if "query" not in checked:
            continue  # External evidence has no consequence certificate.
        raw = by_query[checked["query"]]["premises"]
        if (proposal := propose(raw)) is not None:
            evidence["compliance"][str(index)] = proposal
    return evidence if evidence["answers"] or evidence["compliance"] else {}


def _resolve_fences(meta, fences):
    """The current English owner's parse, submitted as input to Lean's speech core.

    Lean has already checked the source wrapper through the deferred-fence point.
    Its second call checks the resolved content against the speech types, meaning
    identities, source units, records, and coverage. E3 will move this parser to Lean.
    """
    units = [unit for unit, _ in _parts(meta["units"])]
    bindings = [unit for unit in units if unit.get("kind") == "binding"]
    scope = decide_once("speech-acts", {"id": "speech-scope", "kind": "speech-elaborate",
                                        "environment": meta["environment"],
                                        "document": {"units": bindings}})["scope"]
    try:
        env = Environment({**meta["environment"], "speech_acts": scope})
    except VEError as exc:
        raise CheckerUnavailable("CheckerUnavailable: Python could not construct Lean's effective speech scope") from exc
    latest = {}
    for reading_set in meta.get("reading_sets", []):
        uid = reading_set["unit"]
        if uid not in latest or reading_set["version"] > latest[uid]["version"]:
            latest[uid] = reading_set
    resolved = {}
    for unit in units:
        uid = unit["id"]
        if not (type(unit.get("content")) is dict and unit["content"].get("fence") == uid):
            continue
        if uid in latest and latest[uid]["status"] == "authored":
            continue
        wording = wording_text(fences[uid])
        if unit["kind"] == "asserted":
            parsed, kind = _to_data(_sentence(env, wording)), "asserted"
        else:
            context = {}
            if wording == "Which reading did you mean?":
                term = next((t for t in meta.get("open_terms", [])
                             if t.get("name") == f"intended-reading.{uid}"), None)
                if term is not None and len(term["arguments"]) == 1:
                    context["reading_set"] = (term["arguments"][0], term["version"])
            for prefix, suffix in (("Does it follow from these premises that ", "?"),
                                   ("Prove that ", " using these premises.")):
                if wording.startswith(prefix) and wording.endswith(suffix):
                    target = _to_data(_sentence(env, wording[len(prefix):-len(suffix)] + "."))
                    matches = [q["id"] for q in meta.get("queries", []) if q["target"]["ast"] == target]
                    if len(matches) == 1:
                        context["query"] = matches[0]
            parsed, kind = parse_speech(env, wording, scope, **context)
        resolved[uid] = {"ast" if kind == "asserted" else
                         "command" if kind == "instruction" else "question": parsed}
    return resolved


def load_speech_document(path):
    """Read a W2 file, preserving its front matter and source bytes for Lean."""
    raw = Path(path).read_bytes()
    if len(raw) > MAX_DOCUMENT_BYTES:
        raise ResourceLimit("document byte budget")  # relay-lint: file I/O
    if not raw.startswith(b"---\n"):
        raise VEError("ve-document@2 needs JSON front matter")  # relay-lint: file I/O
    boundary = raw.find(b"\n---\n", 4)
    if boundary < 0:
        raise VEError("unclosed JSON front matter")  # relay-lint: file I/O

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
        raise VEError("invalid JSON front matter") from exc  # relay-lint: file I/O
    source, fences = _body(raw[boundary + 5:])
    return SpeechSource(meta, source, fences)
