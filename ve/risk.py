"""Untrusted risk@0 declaration checks and Lean route transport.

The block check gives early shape diagnostics. It does not decide a policy or
regenerate decision tables; the risk route must redo both from raw JSON.
"""
from __future__ import annotations

import os
from pathlib import Path

from .environment import valid_identifier
from .errors import CheckerUnavailable, DuplicateDeclaration, ResourceLimit, UnknownSymbol, UnsupportedProfile, VEError
from .wire import canonical_json

_STAGE_LATER = frozenset({"chance_tag", "bands", "costs", "additive_loss"})
_REQUIRED = frozenset({"severity", "harm_classes", "unexamined"})
_OPTIONAL = frozenset({"always_possible", "combination", "alternative_kinds",
                       "required_alternatives", "quantity_kinds", "required_estimators",
                       "use_all_recorded"})
_KINDS = frozenset({"risk-elaborate", "risk-decision", "risk-conflict",
                    "risk-followable", "risk-audit", "risk-certificate", "admission"})
_BINARY = Path(__file__).resolve().parents[1] / "lean/.lake/build/bin/ve_risk_route"


def _identifier(value, path):
    if not valid_identifier(value) or "__" in value:
        raise VEError(f"InvalidInput: risk.{path}")
    return value


def _short_text(value, path):
    if type(value) is not str or not value or len(value.encode("utf-8")) > 64:
        raise VEError(f"InvalidInput: risk.{path}")
    return value


def _pair(value, path):
    if type(value) is not list or len(value) != 2 or any(type(x) is not str for x in value):
        raise VEError(f"InvalidInput: risk.{path}")
    return value


def validate_block(raw, sorts, predicates, constants, alt, units):
    """Validate the stage A block's declaration shape and return its identity bytes."""
    if type(raw) is not dict:
        raise VEError("InvalidInput: risk.block")
    for key in sorted(raw):
        if key in _STAGE_LATER:
            raise VEError(f"InvalidInput: risk.{key} (stage B or C not enabled)")
        if key not in _REQUIRED | _OPTIONAL:
            raise VEError(f"InvalidInput: risk.{key}")
    for key in sorted(_REQUIRED - raw.keys()):
        raise VEError(f"InvalidInput: risk.{key}")
    if alt["outcomes"] != "signed":
        raise VEError("RiskOutcomes: risk@0 requires outcomes signed")
    severity = raw["severity"]
    if type(severity) is not dict or set(severity) != {"sort", "classes", "more_severe", "unranked", "decided_by"}:
        raise VEError("InvalidInput: risk.severity")
    sort = _identifier(severity["sort"], "severity.sort")
    if sort in sorts:
        raise VEError(f"RiskSeverityNotFresh: {sort}")
    _short_text(severity["decided_by"], "severity.decided_by")
    classes = severity["classes"]
    if type(classes) is not list:
        raise VEError("InvalidInput: risk.severity.classes")
    if not 1 <= len(classes) <= 16:
        raise ResourceLimit("risk classes")
    seen = set()
    for name in classes:
        _identifier(name, "severity.classes")
        if name in seen:
            raise DuplicateDeclaration(f"risk class {name}")
        seen.add(name)
    for name in (*sorts, *predicates, *constants):
        if name.startswith("risk__") or name in seen:
            raise VEError(f"RiskReserved: {name}")
    edges = severity["more_severe"]
    unranked = severity["unranked"]
    if type(edges) is not list or type(unranked) is not list:
        raise VEError("InvalidInput: risk.severity order")
    graph = {name: set() for name in classes}
    for relation, rows in (("more_severe", edges), ("unranked", unranked)):
        for row in rows:
            left, right = _pair(row, f"severity.{relation}")
            for name in (left, right):
                if name not in seen:
                    raise UnknownSymbol(f"risk.severity {name}")
            if left == right:
                raise VEError(f"RiskUnrankedAgainstOrder: {left}, {right}" if relation == "unranked"
                              else f"DependencyCycle: {left}")
            if relation == "more_severe":
                graph[left].add(right)
    closure = {name: set() for name in classes}
    for root in classes:
        pending = list(graph[root])
        while pending:
            node = pending.pop()
            if node in closure[root]:
                continue
            closure[root].add(node)
            pending.extend(graph[node])
    cyclic = sorted(name for name in classes if name in closure[name])
    if cyclic:
        raise VEError("DependencyCycle: " + ", ".join(cyclic))
    for left, right in unranked:
        if right in closure[left] or left in closure[right]:
            raise VEError(f"RiskUnrankedAgainstOrder: {left}, {right}")
    harms = {name for name, decl in constants.items() if decl.sort == alt["harm"]}
    rows = raw["harm_classes"]
    if type(rows) is not list:
        raise VEError("InvalidInput: risk.harm_classes")
    classified = set()
    for row in rows:
        harm, klass = _pair(row, "harm_classes")
        if harm not in harms:
            raise UnknownSymbol(f"risk.harm_classes {harm}")
        if klass not in seen:
            raise UnknownSymbol(f"risk.harm_classes {klass}")
        if harm in classified:
            raise VEError(f"HarmTwoClasses: {harm}")
        classified.add(harm)
    if harms - classified:
        raise VEError(f"HarmUnclassified: {sorted(harms - classified)[0]}")
    unexamined = raw["unexamined"]
    if unexamined != "possible":
        if (type(unexamined) is not dict or set(unexamined) != {"ruled_out_by"}
                or not isinstance(unexamined["ruled_out_by"], str)):
            raise VEError("InvalidInput: risk.unexamined")
        _short_text(unexamined["ruled_out_by"], "unexamined")
    always = raw.get("always_possible", [])
    if type(always) is not list:
        raise VEError("InvalidInput: risk.always_possible")
    for klass in always:
        if klass not in seen:
            raise UnknownSymbol(f"risk.always_possible {klass}")
    if "combination" in raw and raw["combination"] not in ("latest", "hull", "intersection"):
        raise VEError("InvalidInput: risk.combination")
    for field in ("alternative_kinds", "quantity_kinds"):
        mapping = raw.get(field, {})
        if type(mapping) is not dict:
            raise VEError(f"InvalidInput: risk.{field}")
        for name, value in mapping.items():
            _identifier(name, field)
            if field == "alternative_kinds":
                _short_text(value, field)
            elif units is None or value not in units and value != "dimensionless":
                raise UnknownSymbol(f"risk.{field} {value}")
    requirements = raw.get("required_alternatives", [])
    if type(requirements) is not list:
        raise VEError("InvalidInput: risk.required_alternatives")
    for row in requirements:
        if type(row) is not dict or set(row) != {"when", "require"} or type(row["require"]) is not list:
            raise VEError("InvalidInput: risk.required_alternatives")
        for name in (row["when"], *row["require"]):
            if name not in raw.get("alternative_kinds", {}):
                raise UnknownSymbol(f"risk.required_alternatives {name}")
    requirements = raw.get("required_estimators", [])
    if type(requirements) is not list:
        raise VEError("InvalidInput: risk.required_estimators")
    for row in requirements:
        if type(row) is not dict or set(row) != {"quantity_kind", "estimators"} or type(row["estimators"]) is not list:
            raise VEError("InvalidInput: risk.required_estimators")
        if row["quantity_kind"] not in raw.get("quantity_kinds", {}):
            raise UnknownSymbol(f"risk.required_estimators {row['quantity_kind']}")
        for name in row["estimators"]:
            _short_text(name, "required_estimators")
    if type(raw.get("use_all_recorded", False)) is not bool:
        raise VEError("InvalidInput: risk.use_all_recorded")
    return canonical_json(raw)


def run_case(case: dict, *, binary: Path | None = None, timeout: int = 180) -> dict:
    """Send a raw case to Lean; an unavailable route is never a verdict."""
    if type(case) is not dict or case.get("kind") not in _KINDS or type(case.get("environment")) is not dict:
        raise VEError("InvalidInput: risk route case")
    from .environment import Environment
    env = Environment(case["environment"])
    if "risk@0" not in env.profiles:
        raise UnsupportedProfile("risk@0 is required")
    if os.environ.get("VE_AUTHORITY") == "python":
        raise CheckerUnavailable("risk@0 requires the Lean checker")
    executable = _BINARY if binary is None else Path(binary)
    if not executable.is_file():
        raise CheckerUnavailable("ve_risk_route is unavailable")
    from .backends.lean import run_alternatives_case
    return run_alternatives_case(executable, case, timeout=timeout)
