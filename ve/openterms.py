"""Reviewed open-term declarations for ve-document@1."""
from __future__ import annotations

from .admission import token
from .ast import formula_from_data
from .errors import VEError


def validate_open_terms(env, values):
    if type(values) is not list:
        raise VEError("open_terms must be a list")
    seen = set()
    for item in values:
        if type(item) is not dict or set(item) != {"name", "arguments", "decided_by", "necessary",
                                                   "sufficient", "factors", "precedents", "jurisdiction", "version"}:
            raise VEError("invalid open-term schema")
        name = item["name"]
        if not token(name) or name in seen:
            raise VEError("duplicate or invalid open term")
        seen.add(name)
        if (type(item["arguments"]) is not list or not all(token(x) for x in item["arguments"])
                or len(set(item["arguments"])) != len(item["arguments"])):
            raise VEError("invalid open-term arguments")
        if not token(item["decided_by"]) or not token(item["jurisdiction"]):
            raise VEError("open term needs a decision role and jurisdiction")
        if type(item["version"]) is not int or item["version"] < 1:
            raise VEError("invalid open-term version")
        for field in ("necessary", "sufficient"):
            if type(item[field]) is not list:
                raise VEError(f"{field} must be a list")
            for ast in item[field]:
                if env.unit_schema is not None:
                    # Conditions are annotated statements on the quantity route.
                    from .units import elaborate_quantity
                    elaborate_quantity(env, {"format": "ve-quantity@1", "formula": ast})
                else:
                    formula_from_data(env, ast)
        if (type(item["factors"]) is not list or not all(type(x) is str and x for x in item["factors"])
                or type(item["precedents"]) is not list or not all(type(x) is str and x for x in item["precedents"])):
            raise VEError("invalid open-term factors or precedents")
    return seen
