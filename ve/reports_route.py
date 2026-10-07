"""Checked reports route."""
from __future__ import annotations

from .backends.relay import decide


def _without_null(value):
    # The frozen Lean JSON parser has no null; the reports wire uses absent
    # optional fields for literal, reference_time and package content.
    if type(value) is dict:
        return {k: _without_null(v) for k, v in value.items() if v is not None}
    if type(value) is list:
        return [_without_null(v) for v in value]
    return value


def _split_nulls(value, path, nulls):
    """`value` without JSON null, and each removed null's path in `nulls`: a member is
    dropped, a list item becomes `{}` so later indices stay. Lean restores them for its
    fault walk (`Preflight.restore`), which treats them as the pre-batch Python did."""
    if type(value) is dict:
        out = {}
        for key, item in value.items():
            if item is None:
                nulls.append(path + [key])
            else:
                out[key] = _split_nulls(item, path + [key], nulls)
        return out
    if type(value) in (list, tuple):
        out = []
        for index, item in enumerate(value):
            if item is None:
                nulls.append(path + [index])
                out.append({})
            else:
                out.append(_split_nulls(item, path + [index], nulls))
        return out
    return value


def run_case(kind, environment, document, **extra):
    """Lean's reports route row (service mode `reports`); a rejection raises Lean's diagnostic."""
    nulls = []
    document = _split_nulls(document, [], nulls)
    case = _without_null({"id": "document", "kind": kind,
                          "environment": environment, "document": document, **extra})
    if nulls:
        case["nulls"] = nulls
    return decide("reports", [case])[0]
