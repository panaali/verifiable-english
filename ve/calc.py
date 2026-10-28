"""Python relay of the `calc` service mode: a `ve-calc@0` case (math-evidence plan ME-3, spec 3.4).

Lean decides the case (`VE.Calc.Run.runCaseReported`): its refusal, its `meaning_id` and one row per claim, with the
outcome, the reason, the English line and the exact values. This module sends the case with `ve.backends.relay`,
checks what a relay checks (DRI ruling R8) and displays Lean's answer; it computes no outcome, value or wording.

The service checks the answer against `calc.json` (its schema, which also ties each row's sides, display and tie to
the request's claim form). `answer_problem` binds the answer to the request it answers: one row per request claim, in
order, each naming that claim's id, with the kind of its form and that kind's fields, and a reproduction exactly
under a software convention. A follows row's `certificate` and `counterexample` (spec 3.4's table; Lean's
`Run.shownJson`, put on the wire by me-5e, DRI decision 2026-10-27 me-5d item 1) are bound here too: every name in
them is a declared free value of the request, a counterexample's in declaration order and each once, and every
square step's (square, root) pair is one of that derivation's links. The relay never re-evaluates a certificate or a
point: Lean's row theorem (`Run.row_sound`) carries their meaning. Anything else is `CheckerUnavailable`.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

from .errors import CheckerUnavailable

MODE = "calc"
_COMMON = frozenset({"status", "claim", "claim_id", "kind", "outcome", "reason", "line", "finding", "reproduction"})
# Each kind's fields beyond the common ones (spec 3.4's table); a follows row carries none of them until me-5e.
_FIELDS = {"claim": (frozenset({"sides", "display", "tie"}),),
           "follows": (frozenset(), frozenset({"certificate", "counterexample"}))}
_OUTCOMES = frozenset({"holds", "fails", "undefined", "unknown"})
# An exact value, as the generated schema types it (`VE.Calc.Run.exact`).
_EXACT = re.compile(json.loads((Path(__file__).resolve().parent / "backends/lean_service_schema/calc.json")
                               .read_text())["$defs"]["exact"]["pattern"])


def check(case: dict) -> dict:
    """Lean's answer to `case`, bound to it; Lean's refusal of the case raises its diagnostic."""
    from .backends.relay import decide
    return read_answer(decide(MODE, [case])[0], case)


def read_answer(result, case: dict) -> dict:
    """`result`, after the binding check (`answer_problem`)."""
    problem = answer_problem(result, case)
    if problem is not None:
        raise CheckerUnavailable(f"CheckerUnavailable: Lean's calc answer is not bound to its request: {problem}")
    return result


def _exact(value) -> bool:
    return type(value) is str and _EXACT.fullmatch(value) is not None


def _request(case):
    """The request's claims as (id, check) and its free values' names in declaration order, or None when the case
    does not hold them in the form Lean decoded (then no answer is bound to it)."""
    if type(case) is not dict or type(case.get("claims")) is not list or type(case.get("values", [])) is not list:
        return None
    claims = [(c.get("id"), c.get("claim")) for c in case["claims"] if type(c) is dict]
    values = [v for v in case.get("values", []) if type(v) is dict]
    if len(claims) != len(case["claims"]) or len(values) != len(case.get("values", [])):
        return None
    return claims, [v.get("name") for v in values if v.get("free") is True]


def _form(check) -> str:
    """The kind of a request check: a derivation is written `["follows", conclusion, premise ids, links]`."""
    return "follows" if type(check) is list and check[:1] == ["follows"] else "claim"


def _links(check) -> list:
    return [tuple(link) for link in check[3]] if len(check) == 4 and type(check[3]) is list and all(
        type(link) is list for link in check[3]) else []


def _pair(item) -> bool:
    return type(item) is list and len(item) == 2 and type(item[0]) is str and _exact(item[1])


def _step_problem(step, free: list, links: list) -> str | None:
    if type(step) is not dict or len(step) != 1:
        return "a certificate step is not one farkas or square step"
    [(name, body)] = step.items()
    if name == "farkas" and type(body) is dict and set(body) == {"goal", "weights"}:
        goal, weights = body["goal"], body["weights"]
        if type(goal) is not dict or set(goal) != {"const", "coeffs", "strict"} or not _exact(goal["const"]) \
                or type(goal["strict"]) is not bool or type(goal["coeffs"]) is not list \
                or not all(_pair(c) for c in goal["coeffs"]):
            return "a farkas goal is not a fact"
        if any(c[0] not in free for c in goal["coeffs"]):
            return "a farkas goal names a value that is not a free value of the request"
        if type(weights) is not list or not weights or not all(_exact(w) for w in weights):
            return "a farkas step's weights are not exact values"
        return None
    if name == "square" and type(body) is dict and set(body) == {"square", "root", "a", "b"}:
        if not (_exact(body["a"]) and _exact(body["b"])):
            return "a square step's bounds are not exact values"
        if (body["square"], body["root"]) not in links:
            return "a square step's pair is not one of the derivation's links"
        return None
    return "a certificate step is not one farkas or square step"


def _shown_problem(row: dict, check, free: list) -> str | None:
    """Why a follows row's certificate and counterexample (spec 3.4) are not bound to the request, or None."""
    certificate, counterexample = row["certificate"], row["counterexample"]
    if (certificate is not None) != (row["outcome"] == "holds"):
        return "a certificate is not exactly on a holds row"
    if (counterexample is not None) != (row["outcome"] == "fails"):
        return "a counterexample is not exactly on a fails row"
    if certificate is not None:
        if type(certificate) is not list or not certificate:
            return "a certificate is not a list of steps"
        for step in certificate:
            if (problem := _step_problem(step, free, _links(check))) is not None:
                return problem
    if counterexample is not None:
        if type(counterexample) is not list or not all(_pair(p) for p in counterexample):
            return "a counterexample is not a list of [name, value] pairs"
        names = [p[0] for p in counterexample]
        if any(n not in free for n in names):
            return "a counterexample names a value that is not a free value of the request"
        order = [free.index(n) for n in names]
        if order != sorted(set(order)):
            return "a counterexample's names are not each once, in declaration order"
    return None


def _row_problem(row, claim, software: bool, free: list) -> str | None:
    claim_id, check = claim
    if type(row) is not dict or row.get("status") != "ok":
        return "a row is not an answered row"
    if row.get("claim") != claim_id or type(claim_id) is not str:
        return f"a row names {row.get('claim')!r} where the request has {claim_id!r}"
    kind = _form(check)
    if row.get("kind") != kind:
        return f"row {claim_id} is of kind {row.get('kind')!r} where the request's check is a {kind}"
    if not any(set(row) == _COMMON | fields for fields in _FIELDS[kind]):
        return f"row {claim_id} does not have the fields of a {kind} row"
    if row["outcome"] not in _OUTCOMES:
        return f"row {claim_id} has no outcome"
    if (row["reason"] is None) == (row["outcome"] == "unknown") or not (row["reason"] is None or (
            type(row["reason"]) is str and row["reason"])):
        return f"row {claim_id} does not have a reason exactly when it is unknown"
    if not (row["line"] is None or (type(row["line"]) is str and row["line"])):
        return f"row {claim_id}'s line is not text"
    if row["finding"] is not None:
        return f"row {claim_id} has a finding in a standalone case"
    if row["reproduction"] != ("unknown" if software else None):
        return f"row {claim_id}'s reproduction does not follow the case's software convention"
    if kind == "claim":
        if type(row["sides"]) is not list or not row["sides"] or not all(
                s is None or _exact(s) for s in row["sides"]):
            return f"row {claim_id}'s sides are not exact values"
        if not (row["display"] is None or (type(row["display"]) is str and row["display"])):
            return f"row {claim_id}'s display is not text"
        if not (row["tie"] is None or type(row["tie"]) is bool):
            return f"row {claim_id}'s tie is not a flag"
    elif "certificate" in row:
        return _shown_problem(row, check, free)
    return None


def answer_problem(result, case: dict) -> str | None:
    """Why Lean's `calc` result is not an answer to `case` (R8: its binding to the request), or None."""
    request = _request(case)
    if request is None:
        return "the request is not a case Lean decoded"
    claims, free = request
    if type(result) is not dict or set(result) != {"status", "meaning_id", "rows"} or result["status"] != "ok":
        return "the result's fields are not status, meaning_id and rows"
    if type(result["meaning_id"]) is not str or not result["meaning_id"]:
        return "the result has no meaning_id"
    rows = result["rows"]
    if type(rows) is not list or len(rows) != len(claims):
        return "the result does not have one row per request claim"
    for row, claim in zip(rows, claims):
        if (problem := _row_problem(row, claim, "software" in case, free)) is not None:
            return problem
    return None


def lines(result: dict) -> list[str]:
    """What `ve calc check` shows of a bound answer: per row, its claim and Lean's outcome (and reason), Lean's
    English line, and a claim's exact values, display and tie."""
    shown = [f"meaning_id {result['meaning_id']}"]
    for row in result["rows"]:
        shown.append(f"{row['claim']} {row['kind']} {row['outcome']}" +
                     (f" ({row['reason']})" if row["reason"] is not None else ""))
        if row["line"] is not None:
            shown.append(f"  {row['line']}")
        if row["kind"] == "claim":
            shown.append("  sides " + ", ".join("null" if s is None else s for s in row["sides"]))
            if row["display"] is not None:
                shown.append(f"  display {row['display']}")
            if row["tie"] is not None:
                shown.append(f"  tie {str(row['tie']).lower()}")
        if row["reproduction"] is not None:
            shown.append(f"  reproduction {row['reproduction']}")
    return shown


def main(argv: list[str]) -> int:
    """`ve calc check FILE`: Lean's answer to the `ve-calc@0` case in FILE. Exit 0 when Lean answered, 2 when it
    refused the case (its diagnostic), 4 at a resource limit; an unavailable checker is the caller's exit 5."""
    import argparse
    import sys
    from .errors import ResourceLimit, VEError
    from .limits import MAX_PACKAGE_BYTES
    from .wire import loads_json
    parser = argparse.ArgumentParser(prog="python -m ve calc")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="check a ve-calc@0 case").add_argument("file", help="ve-calc@0 JSON file")
    options = parser.parse_args(argv)
    try:
        if options.file == "-":
            data = sys.stdin.buffer.read(MAX_PACKAGE_BYTES + 1)
        else:
            with Path(options.file).open("rb") as stream:
                data = stream.read(MAX_PACKAGE_BYTES + 1)
        result = check(loads_json(data))
    except CheckerUnavailable:
        raise
    except (VEError, OSError) as exc:
        error = exc.to_dict() if isinstance(exc, VEError) else {"code": "InvalidInput", "message": str(exc)}
        print(json.dumps({"status": error["code"], "error": error}, ensure_ascii=False, indent=2))
        return 4 if isinstance(exc, ResourceLimit) else 2
    print("\n".join(lines(result)))
    return 0
