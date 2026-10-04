"""Untrusted risk@0 declaration checks and Lean route transport.

The block check mirrors the Lean decoder: `decode_block` is
`VE.Risk.Wire.decodeRiskBlock` and `check_block` is `VE.Risk.checkRiskBlock`,
in the same order and with the same texts (risk.md 4.1, 6), so a standalone
`Environment` and the route reject an environment alike. It does not decide a
policy or regenerate decision tables. Records, logs and every case are sent to
Lean unchanged: their diagnostics come from the route (risk.md 6, "Python only
dispatches").
"""
from __future__ import annotations

import os

from .environment import valid_identifier
from .errors import (CheckerUnavailable, DuplicateDeclaration, ResourceLimit, UnknownSymbol, UnsupportedProfile,
                     VEError)
from .wire import canonical_json

_STAGE_LATER = ("chance_tag", "bands", "costs", "additive_loss")
_FIELDS = ("severity", "harm_classes", "unexamined", "always_possible", "combination", "alternative_kinds",
           "required_alternatives", "quantity_kinds", "required_estimators", "use_all_recorded")
_REQUIRED = ("severity", "harm_classes", "unexamined")
_PROFILE_WORDS = ("avoidable", "unavoidable", "allows", "prevents")
_KINDS = frozenset({"risk-elaborate", "risk-decision", "risk-conflict",
                    "risk-followable", "risk-audit", "risk-certificate", "admission"})


def _err(field):
    return VEError(f"InvalidInput: risk.{field}")


def _str(value, field):
    if type(value) is not str:
        raise _err(field)
    return value


def _strings(value, field):
    if type(value) is not list or any(type(x) is not str for x in value):
        raise _err(field)
    return value


def _pairs(value, field):
    if type(value) is not list:
        raise _err(field)
    for row in value:
        if len(_strings(row, field)) != 2:
            raise _err(field)
    return [tuple(row) for row in value]


def _object_strings(value, field):
    if type(value) is not dict:
        raise _err(field)
    return [(key, _str(value[key], field)) for key in sorted(value)]


def _identifier(value):
    return valid_identifier(value) and "__" not in value


def _short(value):
    return 0 < len(value.encode("utf-8")) <= 64


def decode_block(raw):
    """`decodeRiskBlock`: shape only, in the Lean decoder's order."""
    if type(raw) is not dict:
        raise _err("block")
    for key in sorted(raw):
        if key in _STAGE_LATER:
            raise VEError(f"InvalidInput: risk.{key} (stage B or C not enabled)")
        if key not in _FIELDS:
            raise _err(key)
    for key in _REQUIRED:
        if key not in raw:
            raise _err(key)
    severity = raw["severity"]
    if type(severity) is not dict or set(severity) != {"sort", "classes", "more_severe", "unranked", "decided_by"}:
        raise _err("severity")
    sort = _str(severity["sort"], "severity")
    classes = _strings(severity["classes"], "severity")
    if not all(_identifier(name) for name in (sort, *classes)):
        raise _err("severity")
    _pairs(severity["more_severe"], "severity")
    _pairs(severity["unranked"], "severity")
    if not _short(_str(severity["decided_by"], "severity")):
        raise _err("severity")
    _pairs(raw["harm_classes"], "harm_classes")
    unexamined = raw["unexamined"]
    if unexamined != "possible":
        if (type(unexamined) is not dict or set(unexamined) != {"ruled_out_by"}
                or type(unexamined["ruled_out_by"]) is not str
                or unexamined["ruled_out_by"] != "chooser" and not _short(unexamined["ruled_out_by"])):
            raise _err("unexamined")
    if "always_possible" in raw:
        _strings(raw["always_possible"], "always_possible")
    if "combination" in raw and raw["combination"] not in ("latest", "hull", "intersection"):
        raise _err("combination")
    for name, value in _object_strings(raw.get("alternative_kinds", {}), "alternative_kinds"):
        if not _identifier(name) or not _short(value):
            raise _err("alternative_kinds")
    rows = raw.get("required_alternatives", [])
    if type(rows) is not list:
        raise _err("required_alternatives")
    for row in rows:
        if type(row) is not dict or set(row) != {"when", "require"}:
            raise _err("required_alternatives")
        _str(row["when"], "required_alternatives")
        _strings(row["require"], "required_alternatives")
    for name, _ in _object_strings(raw.get("quantity_kinds", {}), "quantity_kinds"):
        if not _identifier(name):
            raise _err("quantity_kinds")
    rows = raw.get("required_estimators", [])
    if type(rows) is not list:
        raise _err("required_estimators")
    for row in rows:
        if type(row) is not dict or set(row) != {"quantity_kind", "estimators"}:
            raise _err("required_estimators")
        _str(row["quantity_kind"], "required_estimators")
        _strings(row["estimators"], "required_estimators")
    if "use_all_recorded" in raw and type(raw["use_all_recorded"]) is not bool:
        raise _err("use_all_recorded")
    return raw


def check_alt_reserved(raw):
    """Alt's `checkBlock` on `E_risk`: a profile word may not be the severity sort or a class."""
    names = {raw["severity"]["sort"], *raw["severity"]["classes"]}
    for word in _PROFILE_WORDS:
        if word in names:
            raise VEError(f"AlternativesReserved: {word}")


def check_block(raw, sorts, predicates, constants, alt, units):
    """`checkRiskBlock`: clauses 2 to 6 of risk.md 4.1 with the texts of 6."""
    from .background import dependency_order
    severity = raw["severity"]
    sort, classes = severity["sort"], severity["classes"]
    edges = [tuple(row) for row in severity["more_severe"]]
    unranked = [tuple(row) for row in severity["unranked"]]
    if sort in sorts:
        raise VEError(f"RiskSeverityNotFresh: {sort}")
    for name in (*sorted(sorts), *sorted(predicates), *sorted(constants)):
        if name.startswith("risk__") or name in classes:
            raise VEError(f"RiskReserved: {name}")
    if not 1 <= len(classes) <= 16:
        raise ResourceLimit("risk classes")
    seen = []
    for name in classes:
        if name in seen:
            raise DuplicateDeclaration(f"risk class {name}")
        seen.append(name)
    for pair in edges + unranked:
        for name in pair:
            if name not in classes:
                raise UnknownSymbol(f"risk.severity {name}")
    dependency_order({name: {b for a, b in edges if a == name} for name in classes})
    closure = {name: set() for name in classes}
    for root in classes:
        pending = [b for a, b in edges if a == root]
        while pending:
            node = pending.pop()
            if node not in closure[root]:
                closure[root].add(node)
                pending.extend(b for a, b in edges if a == node)
    for left, right in unranked:
        # A class is ranked against itself: "c harms and c harms are not ranked" is no declaration.
        if left == right or right in closure[left] or left in closure[right]:
            raise VEError(f"RiskUnrankedAgainstOrder: {left}, {right}")
    classified = []
    for harm, klass in raw["harm_classes"]:
        declaration = constants.get(harm)
        if declaration is None or declaration.sort != alt["harm"]:
            raise UnknownSymbol(f"risk.harm_classes {harm}")
        if klass not in classes:
            raise UnknownSymbol(f"risk.harm_classes {klass}")
        if harm in classified:
            raise VEError(f"HarmTwoClasses: {harm}")
        classified.append(harm)
    for harm in sorted(constants):
        if constants[harm].sort == alt["harm"] and harm not in classified:
            raise VEError(f"HarmUnclassified: {harm}")
    for klass in raw.get("always_possible", []):
        if klass not in classes:
            raise UnknownSymbol(f"risk.always_possible {klass}")
    kinds = raw.get("alternative_kinds", {})
    for row in raw.get("required_alternatives", []):
        for kind in (row["when"], *row["require"]):
            if kind not in kinds:
                raise UnknownSymbol(f"risk.required_alternatives {kind}")
    quantity_kinds = raw.get("quantity_kinds", {})
    for _, tag in sorted(quantity_kinds.items()):
        if tag != "dimensionless" and (units is None or tag not in units):
            raise UnknownSymbol(f"risk.quantity_kinds {tag}")
    for row in raw.get("required_estimators", []):
        if row["quantity_kind"] not in quantity_kinds:
            raise UnknownSymbol(f"risk.required_estimators {row['quantity_kind']}")
    if alt["outcomes"] != "signed":
        raise VEError("RiskOutcomes: risk@0 requires outcomes signed")


def check_route_declarations(predicates, constants):
    """`decodeRiskSource`'s refusals after the vocabulary: definitions, data flags, then `$string` literals."""
    if any(decl.defined is not None for decl in predicates.values()):
        raise UnsupportedProfile("risk route with definitions is not implemented")
    # Lean keeps a flag only when `functional` or `total` is true.
    if any(decl.functional or decl.total for decl in predicates.values()):
        raise UnsupportedProfile("risk route with data flags is not implemented")
    if any(decl.sort == "$string" for decl in constants.values()):
        raise UnsupportedProfile("risk route with $string literals is not implemented")


def validate_block(raw, sorts, predicates, constants, alt, units):
    """Validate the stage A block's declarations and return its identity bytes."""
    decode_block(raw)
    check_alt_reserved(raw)
    check_block(raw, sorts, predicates, constants, alt, units)
    return canonical_json(raw)


def run_case(case: dict, *, timeout: float | None = None) -> dict:
    """Send a raw case to the Lean risk route (service mode `risk`) unchanged and return its row,
    a rejection included; an unavailable route is never a verdict.

    Python decodes nothing of the environment, record or log first, so every
    diagnostic, including its order, is the route's (risk.md 6, 7.3).
    """
    if (type(case) is not dict or type(case.get("kind")) is not str
            or case["kind"] not in _KINDS or type(case.get("environment")) is not dict):
        raise VEError("InvalidInput: risk route case")
    if os.environ.get("VE_AUTHORITY") == "python":
        raise CheckerUnavailable("risk@0 requires the Lean checker")
    from .backends.relay import rows
    return rows("risk", [case], timeout=timeout)[0]
