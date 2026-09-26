"""Reading-set structure and conservative checking plans.

Only same-background assertion readings may use the disjunction shortcut.
Every other kind requires complete choice enumeration or stays UNKNOWN.
"""
from __future__ import annotations

from itertools import product

from .admission import _check_kind, token
from .ast import formula_from_data
from .errors import VEError


def validate_reading_sets(env, values, unit_ids):
    if type(values) is not list:
        raise VEError("reading_sets must be a list")
    seen = set()
    for item in values:
        required = {"id", "unit", "version", "status", "readings"}
        if type(item) is not dict or not required <= set(item) or set(item) - required - {"signature", "rejected_history"}:
            raise VEError("invalid reading set")
        key = (item["id"], item["version"])
        if not token(item["id"]) or type(item["version"]) is not int or item["version"] < 1 or key in seen:
            raise VEError("invalid or duplicate reading set version")
        seen.add(key)
        if item["unit"] not in unit_ids or item["status"] not in ("authored", "open"):
            raise VEError("invalid reading set unit or status")
        readings = item["readings"]
        if type(readings) is not list or not 1 <= len(readings) <= 64:
            raise VEError("reading sets hold 1 to 64 readings")
        if item["status"] == "authored" and (len(readings) != 1 or not token(item.get("signature"))):
            raise VEError("authored reading needs one signed choice")
        if item["status"] == "open" and "signature" in item:
            raise VEError("open reading set cannot have an author signature")
        ids = set()
        for reading in readings:
            if type(reading) is not dict or set(reading) != {"id", "kind", "meaning_id", "content", "admission"}:
                raise VEError("invalid reading")
            if not token(reading["id"]) or reading["id"] in ids:
                raise VEError("duplicate or invalid reading id")
            ids.add(reading["id"])
            _check_kind(reading["kind"])
            if not token(reading["meaning_id"]):
                raise VEError("invalid reading meaning id")
            if reading["content"] is not None:
                formula_from_data(env, reading["content"])
            admission = reading["admission"]
            if (type(admission) is not dict or set(admission) != {"who", "why", "distinguishing_models"}
                    or not token(admission["who"]) or type(admission["why"]) is not str
                    or not admission["why"] or type(admission["distinguishing_models"]) is not dict):
                raise VEError("invalid reading admission")
            if set(admission["distinguishing_models"]) != set(r["id"] for r in readings) - {reading["id"]}:
                raise VEError("each other reading needs a distinguishing model id")
            if not all(token(v) for v in admission["distinguishing_models"].values()):
                raise VEError("invalid distinguishing model id")
        if "rejected_history" in item and type(item["rejected_history"]) is not list:
            raise VEError("invalid rejected reading history")
    return seen


def validate_narrowings(values, reading_sets, unit_ids):
    if type(values) is not list:
        raise VEError("narrowings must be a list")
    ids = set()
    for item in values:
        if type(item) is not dict or set(item) != {"id", "set", "version", "keeps", "by", "reason_spans"}:
            raise VEError("invalid narrowing")
        if not token(item["id"]) or item["id"] in ids or not token(item["by"]):
            raise VEError("invalid narrowing id or author")
        ids.add(item["id"])
        ref = (item["set"], item["version"])
        if ref not in reading_sets:
            raise VEError("narrowing cites unknown reading set version")
        rs = next(r for r in reading_sets if (r["id"], r["version"]) == ref)
        choices = {r["id"] for r in rs["readings"]}
        if type(item["keeps"]) is not list or not item["keeps"] or not set(item["keeps"]) <= choices:
            raise VEError("narrowing must keep named readings")
        if type(item["reason_spans"]) is not list or not item["reason_spans"] or not set(item["reason_spans"]) <= unit_ids:
            raise VEError("narrowing needs cited source units")
    return ids


def plan_choices(sets, *, limit=64):
    """Return a sound checking route; no verdict is inferred by this planner."""
    if not sets:
        return {"route": "single", "choices": [{}]}
    if all(all(r["kind"] == "asserted" and r["content"] is not None for r in s["readings"])
           for s in sets):
        return {"route": "assertion-disjunction", "choices": None,
                "all": "one proof from per-unit disjunctions",
                "none": "one shared finite model satisfying every reading"}
    count = 1
    for s in sets:
        count *= len(s["readings"])
        if count > limit:
            return {"route": "UNKNOWN", "budget": {"max_choices": limit}, "choice_count": count}
    return {"route": "enumerate", "choices": [dict(zip((s["id"] for s in sets), c))
             for c in product(*(range(len(s["readings"])) for s in sets))]}
