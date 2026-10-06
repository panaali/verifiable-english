"""Bound transport for the Lean speech-source route.

The one-shot route is used for W2 until its response shape is part of the
persistent service.  The transport checks the producer's row structure and
binding; it does not recalculate a speech decision.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from ..errors import CheckerUnavailable
from ..wire import canonical_json
from .lean import NoAnswer, configured_timeout, read_rows, row_problem
from .relay import rejection

EXECUTABLE = Path(__file__).resolve().parents[2] / "lean/.lake/build/bin/ve_speech_acts_route"

# VE.SpeechActs.Source.report, beside VE.SpeechActs.Run.elaborated.  These are
# structural types only; the route is responsible for their values.
SOURCE_FIELDS = {
    "document_id": "string", "source_id": "string", "environment_id": "string",
    "scope": "object", "legend": "array<string>", "premises": "array<json>",
    "policy": "object", "rules": "array<object>", "commands": "array<object>", "dormant": "array<string>",
    "questions": "array<object>", "queries": "array<object>", "units": "array<object>",
    "coverage": "object", "answers": "array<object>", "nominations": "array<object>",
    "compliance": "array<object>", "status_text": "array<string>",
}


def decide_source(metadata: dict, source: str, fences: dict | None = None, *, executable=EXECUTABLE) -> dict:
    """Return Lean's W2 source report, or raise its coded diagnostic verbatim."""
    case = {"id": "speech-source", "kind": "speech-source",
            "document": {"metadata": metadata, "source": source, "fences": fences or {}}}
    try:
        proc = subprocess.run([str(executable), "-"], input=canonical_json([case]),
                              capture_output=True, timeout=configured_timeout(120.0))
        [row] = read_rows(proc.returncode, proc.stdout, [case], coded=True, restricted=True)
    except (OSError, subprocess.TimeoutExpired, NoAnswer) as exc:
        raise CheckerUnavailable(f"CheckerUnavailable: speech-source route returned no bound answer ({exc})") from exc
    if row["status"] == "error":
        if type(row.get("code")) is not str:
            raise CheckerUnavailable("CheckerUnavailable: speech-source route omitted its diagnostic code")
        raise rejection(row["code"], row["error"], generator=row.get("generator"))
    problem = row_problem(case, row, 0, SOURCE_FIELDS)
    if problem:
        raise CheckerUnavailable(f"CheckerUnavailable: speech-source route {problem}")
    if set(row) != {"id", "status", *SOURCE_FIELDS}:
        raise CheckerUnavailable("CheckerUnavailable: speech-source route returned unexpected fields")
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
    return row
