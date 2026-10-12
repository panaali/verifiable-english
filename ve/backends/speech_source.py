"""Bound transport for the Lean speech-source route.

The one-shot route is used for W2 until its response shape is part of the
persistent service.  The transport checks the producer's row structure and
binding; it does not recalculate a speech decision.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from ..errors import CheckerUnavailable
from ..environment import Environment
from .lean import row_problem, run_route_cases
from .relay import rejection
from .service_schema import Invalid, check_row
from ..wire import digest

EXECUTABLE = Path(__file__).resolve().parents[2] / "lean/.lake/build/bin/ve_speech_acts_route"

# VE.SpeechActs.Source.report, beside VE.SpeechActs.Run.elaborated.  These are
# structural types only; the route is responsible for their values.
SOURCE_FIELDS = {
    "document_id": "string", "source_id": "string", "environment_id": "string",
    "scope": "object", "legend": "array<string>", "premises": "array<json>",
    "policy": "object", "rules": "array<object>", "commands": "array<object>", "dormant": "array<string>",
    "questions": "array<object>", "queries": "array<object>", "units": "array<object>",
    "coverage": "object", "warnings": "array<string>", "answers": "array<object>", "nominations": "array<object>",
    "compliance": "array<object>", "status_text": "array<string>",
}


def _invalid(field: str) -> None:
    raise CheckerUnavailable(f"CheckerUnavailable: speech-source route returned invalid {field}")


def _source_units(metadata: dict) -> list[dict]:
    """Flatten the submitted source units in the same order as the report."""
    units = []
    pending = list(reversed(metadata.get("units", [])))
    while pending:
        unit = pending.pop()
        if "parts" in unit:
            pending.extend(reversed(unit["parts"]))
        else:
            units.append(unit)
    return units


def _latest_sets(metadata: dict) -> dict:
    latest = {}
    for item in metadata.get("reading_sets", []):
        old = latest.get(item["unit"])
        if old is None or item["version"] > old["version"]:
            latest[item["unit"]] = item
    return latest


def _bound_environment(metadata: dict, units: list[dict], latest: dict) -> Environment:
    """Regenerate the effective scope from authored binding units, never from the response."""
    base = Environment(metadata["environment"])
    scope = base.to_dict()["speech_acts"]
    seen = set()
    for unit in units:
        chosen = latest.get(unit["id"])
        kind, content = unit["kind"], unit.get("content")
        if chosen is not None:
            if chosen["status"] == "open":
                continue
            reading = chosen["readings"][0]
            kind, content = reading["kind"], reading["content"]
        if kind != "binding" or type(content) is not dict or type(content.get("binding")) is not dict:
            continue
        binding = content["binding"]
        if "task" in binding:
            key, actual = "task", binding["task"]
        elif "you" in binding:
            key, actual = "you", binding["you"]
        else:
            key, actual = binding["phrase"], binding["constant"]
        if key in seen:
            _invalid("scope")
        seen.add(key)
        if key == "task":
            if scope["task"] != actual:
                _invalid("scope")
        elif key == "you":
            if "addressee" in scope and scope["addressee"]["constant"] != actual:
                _invalid("scope")
            scope["addressee"] = {"sort": base.constants[actual].sort, "constant": actual}
        else:
            if key in scope.get("definites", {}) and scope["definites"][key] != actual:
                _invalid("scope")
            scope.setdefault("definites", {})[key] = actual
    return Environment({**metadata["environment"], "speech_acts": scope})


def _coverage_pair(unit: dict, chosen: dict | None) -> tuple[str, str]:
    """W2 status and section 6 class from the submitted unit and latest set."""
    meaning = unit["meaning"]
    word = meaning if type(meaning) is str else next(iter(meaning))
    if chosen is not None:
        asserted = all(reading["kind"] == "asserted" for reading in chosen["readings"])
        status = "CHECKED" if chosen["status"] == "authored" and asserted else "OPEN"
        cls = "U" if word == "unformalised" else "R" if status == "OPEN" else "C"
    else:
        content = unit.get("content") is not None
        status = ("CHECKED" if content and word == "specified" else "OPEN" if word == "open" else
                  "UNFORMALISED" if word == "unformalised" else "LABELLED")
        cls = ("U" if word == "unformalised" else "O" if word == "open" else
               "C" if content and word == "specified" else "L")
    return status, cls


def _premise_fields(item: dict, field: str) -> None:
    premise = item.get("premises")
    if type(premise) is not dict:
        _invalid(field)
    status = premise.get("status")
    if status == "model":
        if set(premise) != {"status", "model_id"} or type(premise["model_id"]) is not str or \
                item.get("vacuous") != "no":
            _invalid(field)
    elif status in {"INCONSISTENT", "UNKNOWN"}:
        if set(premise) != {"status"} or \
                item.get("vacuous") != ("yes" if status == "INCONSISTENT" else "unknown"):
            _invalid(field)
    else:
        _invalid(field)


def _records(row: dict, metadata: dict) -> None:
    """Check the report variants and their references against the submitted records.

    These are the shapes emitted by Source.recordJson, nominationLines and
    complianceJson. The order and owners come from the request, while the
    contents of a decision remain Lean's responsibility.
    """
    source_units = []
    pending = [(unit, None) for unit in reversed(metadata.get("units", []))]
    while pending:
        unit, parent = pending.pop()
        if "parts" in unit:
            pending.extend((part, unit["id"]) for part in reversed(unit["parts"]))
        else:
            source_units.append((unit["id"], unit["span"][1] - unit["span"][0], parent))
    if [(unit["id"], unit["bytes"], unit.get("parent")) for unit in row["units"]] != source_units:
        _invalid("units")
    unit_ids = {unit[0] for unit in source_units}
    if len(unit_ids) != len(source_units) or \
            any(question["unit"] not in unit_ids for question in row["questions"]) or \
            any(command["unit"] not in unit_ids for command in row["commands"]) or \
            len({q["unit"] for q in row["questions"]}) != len(row["questions"]) or \
            len({c["unit"] for c in row["commands"]}) != len(row["commands"]):
        _invalid("speech units")
    if [query["id"] for query in row["queries"]] != \
            [query["id"] for query in metadata.get("queries", [])]:
        _invalid("queries")
    questions = {q["unit"]: q for q in row["questions"]}
    commands = {c["unit"] for c in row["commands"]}
    queries = {q["id"] for q in row["queries"]}
    requested_answers = metadata.get("answers", [])
    ordinary = [a for a in requested_answers if "nominate" not in a]
    if len(row["answers"]) != len(ordinary):
        _invalid("answers")
    for answer, request in zip(row["answers"], ordinary, strict=True):
        if type(answer) is not dict or type(answer.get("question")) is not str or \
                answer["question"] != request["question"] or answer["question"] not in questions or \
                type(answer.get("line")) is not str or type(answer.get("status")) is not str:
            _invalid("answers")
        mode = questions[answer["question"]]["mode"]
        keys = set(answer)
        if mode == "follows":
            if keys not in ({"question", "query", "status", "evidence", "premises", "vacuous", "line"},
                            {"question", "query", "status", "line"}) or \
                    answer.get("query") != questions[answer["question"]]["query"] or \
                    answer["query"] not in queries or answer["status"] not in {"follows", "gap"} or \
                    (answer["status"] == "gap") != (keys == {"question", "query", "status", "line"}):
                _invalid("answers")
            if answer["status"] == "follows":
                if answer["evidence"] != "certificate":
                    _invalid("answers")
                _premise_fields(answer, "answers")
        elif mode in {"polar", "which_one", "which_all"}:
            evidence = answer.get("evidence")
            status = answer["status"]
            base = {"question", "status", "evidence", "line"}
            if evidence == "certificate":
                expected = base | {"premises", "vacuous"}
                if status in {"supported", "supported given presupposition"}:
                    expected |= {"answer", "assumptions"}
                elif status != "PRESUPPOSITION-FAILED":
                    _invalid("answers")
                _premise_fields(answer, "answers")
                if "assumptions" in expected and (type(answer.get("assumptions")) is not list or
                                                   any(type(x) is not str for x in answer["assumptions"])):
                    _invalid("answers")
            elif evidence == "model":
                if status not in {"evaluated", "PRESUPPOSITION-FAILED"}:
                    _invalid("answers")
                expected = base | {"model_id", "scope"}
                if status == "evaluated":
                    expected.add("answer")
                if type(answer.get("model_id")) is not str or answer.get("scope") != "this model only":
                    _invalid("answers")
            else:
                _invalid("answers")
            if keys != expected:
                _invalid("answers")
            if "answer" in answer:
                value = answer["answer"]
                if (mode == "polar" and value not in ("yes", "no")) or \
                        (mode == "which_one" and (type(value) is not dict or set(value) != {"one"} or
                                                  type(value["one"]) is not str)) or \
                        (mode == "which_all" and (type(value) is not dict or set(value) != {"all"} or
                                                  type(value["all"]) is not list or
                                                  any(type(x) is not str for x in value["all"]))):
                    _invalid("answers")
            elif answer["status"] != "PRESUPPOSITION-FAILED":
                _invalid("answers")
        else:
            _invalid("answers")

    reading = [q for q in row["questions"] if q["mode"] == "reading"]
    if len(row["nominations"]) != len(reading):
        _invalid("nominations")
    for nomination, question in zip(row["nominations"], reading, strict=True):
        if type(nomination) is not dict or set(nomination) not in \
                ({"question", "line"}, {"question", "line", "narrowing"}) or \
                nomination.get("question") != question["unit"] or type(nomination.get("line")) is not str:
            _invalid("nominations")
        if "narrowing" in nomination:
            n = nomination["narrowing"]
            if type(n) is not dict or set(n) != {"set", "version", "keeps", "by", "reason_spans", "support"} or \
                    n["set"] != question["set"] or type(n["version"]) is not int or \
                    n["version"] != question["version"] or type(n["keeps"]) is not list or \
                    len(n["keeps"]) != 1 or type(n["keeps"][0]) is not str or \
                    type(n["by"]) is not str or n["reason_spans"] != [question["unit"]] or \
                    n["support"] != "testimony":
                _invalid("nominations")

    if len(row["compliance"]) != len(metadata.get("compliance", [])):
        _invalid("compliance")
    for compliance, request in zip(row["compliance"], metadata.get("compliance", []), strict=True):
        if type(compliance) is not dict or compliance.get("command") != request["command"] or \
                compliance["command"] not in commands or type(compliance.get("line")) is not str:
            _invalid("compliance")
        if set(compliance) == {"command", "unit", "line"}:
            if type(compliance["unit"]) is not str or \
                    compliance["unit"] != request["evidence"].get("unit"):
                _invalid("compliance")
        elif set(compliance) == {"command", "query", "status", "premises", "vacuous", "line"}:
            if type(compliance["query"]) is not str or compliance["query"] not in queries or \
                    compliance["status"] != "certificate":
                _invalid("compliance")
            _premise_fields(compliance, "compliance")
        else:
            _invalid("compliance")


def decide_source(metadata: dict, source: str, fences: dict | None = None, *,
                  resolved_fences: dict | None = None, premise_status: dict | None = None,
                  executable=EXECUTABLE) -> dict:
    """Return Lean's W2 source report, or raise its coded diagnostic verbatim."""
    payload = {"metadata": metadata, "source": source, "fences": fences or {}}
    if resolved_fences is not None:
        payload["resolved_fences"] = resolved_fences
    case = {"id": "speech-source", "kind": "speech-source", "document": payload}
    if premise_status is not None:
        case["premise_status"] = premise_status
    [row] = run_route_cases(executable, "-", [case], coded=True, route_name="speech-source route")
    if row["status"] == "error":
        if type(row.get("code")) is not str:
            raise CheckerUnavailable("CheckerUnavailable: speech-source route omitted its diagnostic code")
        raise rejection(row["code"], row["error"], generator=row.get("generator"))
    problem = row_problem(case, row, 0, SOURCE_FIELDS)
    if problem:
        raise CheckerUnavailable(f"CheckerUnavailable: speech-source route {problem}")
    if set(row) != {"id", "status", *SOURCE_FIELDS}:
        raise CheckerUnavailable("CheckerUnavailable: speech-source route returned unexpected fields")
    elaboration = {key: row[key] for key in ("id", "status", "environment_id", "scope", "legend",
                                            "premises", "policy", "commands", "dormant", "questions", "queries")}
    try:
        check_row("speech-acts", elaboration, {"id": case["id"], "kind": "speech-elaborate"}, 0)
    except Invalid as exc:
        raise CheckerUnavailable(f"CheckerUnavailable: speech-source route returned an invalid elaboration ({exc})") from exc
    for field in ("document_id", "source_id", "environment_id"):
        value = row[field]
        if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            raise CheckerUnavailable(f"CheckerUnavailable: speech-source route returned an invalid {field}")
    # Source.Run uses Loader.identityMetadata and Loader.sourceId. Recompute
    # only these request identities; no speech decision is repeated here.
    try:
        identity_payload = {"metadata": {key: value for key, value in metadata.items() if key != "weights"},
                            "source": source, "fences": fences or {}}
        expected_document = digest("ve-document@2\n", identity_payload)
        profiles = metadata["environment"]["profiles"]
        if type(profiles) is not list or any(type(profile) is not str for profile in profiles):
            _invalid("source_id")
        version = "v0.2:" + ",".join(profiles)
        expected_source = hashlib.sha256((f"ve-source-{version}\n" + source).encode("utf-8")).hexdigest()
    except (KeyError, TypeError, ValueError) as exc:
        raise CheckerUnavailable("CheckerUnavailable: speech-source route could not bind its identities") from exc
    if row["document_id"] != expected_document:
        _invalid("document_id")
    if row["source_id"] != expected_source:
        _invalid("source_id")
    try:
        source_units = _source_units(metadata)
        latest = _latest_sets(metadata)
        bound_environment = _bound_environment(metadata, source_units, latest)
        if row["scope"] != bound_environment.to_dict()["speech_acts"]:
            _invalid("scope")
    except (KeyError, TypeError, ValueError, StopIteration, IndexError) as exc:
        raise CheckerUnavailable("CheckerUnavailable: speech-source route could not bind its environment") from exc
    if row["environment_id"] != bound_environment.environment_id:
        _invalid("environment_id")
    coverage = row["coverage"]
    if type(coverage) is not dict or set(coverage) != {"bytes_by_class", "bytes_by_status", "residual"}:
        raise CheckerUnavailable("CheckerUnavailable: speech-source route returned invalid coverage")
    for field in ("bytes_by_class", "bytes_by_status"):
        counts = coverage[field]
        if type(counts) is not dict or any(type(k) is not str or type(v) is not int or v < 0
                                           for k, v in counts.items()) or sum(counts.values()) != len(source.encode()):
            raise CheckerUnavailable(f"CheckerUnavailable: speech-source route returned invalid {field}")
    residual = coverage["residual"]
    if type(residual) is not dict or set(residual) != {"open_terms", "unresolved_sets"} or any(
            type(value) is not int or value < 0 for value in residual.values()):
        raise CheckerUnavailable("CheckerUnavailable: speech-source route returned invalid residual counts")
    units = row["units"]
    if any(type(unit) is not dict or not {"id", "bytes", "status", "class"} <= set(unit)
           or set(unit) - {"id", "bytes", "status", "class", "parent"}
           or type(unit["id"]) is not str or type(unit["bytes"]) is not int or unit["bytes"] < 0
           # Tuples, not sets: a status or class of an unhashable type must be refused, not raise TypeError.
           or unit["status"] not in ("CHECKED", "OPEN", "LABELLED", "UNFORMALISED")
           or unit["class"] not in ("C", "L", "O", "R", "U")
           or "parent" in unit and type(unit["parent"]) is not str for unit in units):
        raise CheckerUnavailable("CheckerUnavailable: speech-source route returned invalid units")
    if sum(unit["bytes"] for unit in units) != len(source.encode()):
        raise CheckerUnavailable("CheckerUnavailable: speech-source route returned invalid unit byte counts")
    if len(units) != len(source_units):
        _invalid("unit coverage")
    for reported, submitted in zip(units, source_units, strict=True):
        status, cls = _coverage_pair(submitted, latest.get(submitted["id"]))
        if reported["status"] != status or reported["class"] != cls:
            _invalid("unit coverage")
    for field, name in (("bytes_by_class", "class"), ("bytes_by_status", "status")):
        projected = {}
        for unit in units:
            projected[unit[name]] = projected.get(unit[name], 0) + unit["bytes"]
        if coverage[field] != projected:
            raise CheckerUnavailable(f"CheckerUnavailable: speech-source route returned inconsistent {field}")
    if coverage["residual"] != {"open_terms": len(metadata.get("open_terms", [])),
                                "unresolved_sets": sum(item["status"] == "open" for item in latest.values())}:
        _invalid("residual")
    if any(type(rule) is not dict or set(rule) != {"name", "predicate", "sign", "guard", "unless", "over"}
           or type(rule["name"]) is not str or type(rule["predicate"]) is not str
           or type(rule["sign"]) is not bool or type(rule["guard"]) is not list
           or type(rule["unless"]) is not list or type(rule["over"]) is not list
           for rule in row["rules"]):
        raise CheckerUnavailable("CheckerUnavailable: speech-source route returned invalid rules")
    _records(row, metadata)
    return row
