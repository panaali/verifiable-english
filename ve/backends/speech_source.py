"""Bound transport for the Lean speech-source route.

The one-shot route is used for W2 until its response shape is part of the
persistent service.  The transport checks the producer's row structure and
binding; it does not recalculate a speech decision.
"""
from __future__ import annotations

from pathlib import Path

from ..errors import CheckerUnavailable
from .lean import row_problem, run_route_cases
from .relay import rejection
from .service_schema import Invalid, check_row

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
           or unit["status"] not in {"CHECKED", "OPEN", "LABELLED", "UNFORMALISED"}
           or unit["class"] not in {"C", "L", "O", "R", "U"}
           or "parent" in unit and type(unit["parent"]) is not str for unit in units):
        raise CheckerUnavailable("CheckerUnavailable: speech-source route returned invalid units")
    if sum(unit["bytes"] for unit in units) != len(source.encode()):
        raise CheckerUnavailable("CheckerUnavailable: speech-source route returned invalid unit byte counts")
    for field, name in (("bytes_by_class", "class"), ("bytes_by_status", "status")):
        projected = {}
        for unit in units:
            projected[unit[name]] = projected.get(unit[name], 0) + unit["bytes"]
        if coverage[field] != projected:
            raise CheckerUnavailable(f"CheckerUnavailable: speech-source route returned inconsistent {field}")
    if any(type(rule) is not dict or set(rule) != {"name", "predicate", "sign", "guard", "unless", "over"}
           or type(rule["name"]) is not str or type(rule["predicate"]) is not str
           or type(rule["sign"]) is not bool or type(rule["guard"]) is not list
           or type(rule["unless"]) is not list or type(rule["over"]) is not list
           for rule in row["rules"]):
        raise CheckerUnavailable("CheckerUnavailable: speech-source route returned invalid rules")
    for field, owner in (("answers", "question"), ("nominations", "question"), ("compliance", "command")):
        if any(type(item.get(owner)) is not str or type(item.get("line")) is not str
               for item in row[field]):
            raise CheckerUnavailable(f"CheckerUnavailable: speech-source route returned invalid {field}")
    return row
