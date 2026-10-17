"""Claim labels, unit kinds and executable document admission on ve.core@0.2 (PLAN-EXPAND2 3.6).

Lean decides admission under every authority (`lean/VE/Route/Admission.lean`
and the statement-layer routes, lean-first batch 13b); this module chooses the
route from the envelope and relays Lean's report or diagnostic. A quoted unit
must be named through its bridge; Background enters only as explicit
`background:<generator>` leaves whose formulas Lean regenerates.
"""
from __future__ import annotations

import re
from typing import NamedTuple

from .assurance import semantic_entry
from .ast import Or, decimal_text, decimal_value, formula_from_data
from .background import HOOKS, _DEPENDENCY_ENVIRONMENT
from .environment import Environment, listed_profiles
from .errors import ResourceLimit, VEError
from .profiles import LANGUAGE
from .wire import require_fields

_TOKEN = re.compile(r"[A-Za-z0-9_.\-]+\Z", re.ASCII)
_NAT = re.compile(r"(0|[1-9][0-9]*)\Z", re.ASCII)
GENERATORS = tuple(HOOKS)
ATOMIC_KINDS = ("asserted", "norm", "definition", "question", "instruction", "example",
                "exposition", "analogy", "explanation", "meta")
ACTS = ("says", "promised", "believes", "intends", "expects", "denies")
MODALITIES = ("could", "likely", "generally", "typically", "effectively")
RELATIONS = ("because", "in order to", "prevents")


class AdmissionError(VEError):
    code = "AdmissionError"


def token(value) -> bool:
    """Names inside kinds and labels: nonempty, at most 64 bytes, [A-Za-z0-9_.-]."""
    return type(value) is str and len(value.encode()) <= 64 and _TOKEN.fullmatch(value) is not None


class Label(NamedTuple):
    kind: str
    args: tuple

    def render(self) -> str:
        a = self.args
        return {"asserted": lambda: "asserted",
                "bridge": lambda: f"bridge:accepts({a[0]},{a[1]})",
                "background": lambda: f"background:{a[0]}",
                "cite": lambda: f"cite:{a[0]}/{a[1]}",
                "open": lambda: f"open:{a[0]}",
                "readings": lambda: (f"readings:{a[0]}@{decimal_text(a[1])}:"
                                     f"{'all' if a[2] is None else decimal_text(a[2])}"),
                "narrowing": lambda: f"narrowing:{a[0]}"}[self.kind]()


def _parse_raw(s: str) -> Label | None:
    if s == "asserted":
        return Label("asserted", ())
    if s.startswith("bridge:accepts(") and s.endswith(")"):
        parts = s[15:-1].split(",")
        return Label("bridge", tuple(parts)) if len(parts) == 2 and all(map(token, parts)) else None
    if s.startswith("background:"):
        return Label("background", (s[11:],)) if s[11:] in GENERATORS else None
    if s.startswith("cite:"):
        parts = s[5:].split("/")
        return Label("cite", tuple(parts)) if len(parts) == 2 and all(map(token, parts)) else None
    if s.startswith("open:"):
        return Label("open", (s[5:],)) if token(s[5:]) else None
    if s.startswith("readings:"):
        parts = s[9:].split("@")
        if len(parts) != 2:
            return None
        rest = parts[1].split(":")
        if len(rest) != 2 or not token(parts[0]) or not _NAT.fullmatch(rest[0]):
            return None
        # Lean's `String.toNat?`: an index of any length
        if rest[1] == "all":
            return Label("readings", (parts[0], decimal_value(rest[0]), None))
        return (Label("readings", (parts[0], decimal_value(rest[0]), decimal_value(rest[1])))
                if _NAT.fullmatch(rest[1]) else None)
    if s.startswith("narrowing:"):
        return Label("narrowing", (s[10:],)) if token(s[10:]) else None
    return None


@semantic_entry("label")
def parse_label(s) -> Label | None:
    """Only canonical label strings parse: the label renders back to the input."""
    if type(s) is not str:
        return None
    label = _parse_raw(s)
    return label if label is not None and label.render() == s else None


@semantic_entry("label")
def validate_label(s) -> str:
    """Check the public label grammar: Lean's `label` route decides under every authority."""
    from .backends.dispatch import owned
    from .backends.relay import decide
    from .backends.lean_service import CheckerUnavailable

    if type(s) is not str:
        raise AdmissionError(f"AdmissionError: invalid label {s}")
    case = {"id": "label", "kind": "label", "environment": _DEPENDENCY_ENVIRONMENT,
            "label": s}

    def lean():
        label = decide("route", [case])[0].get("label")
        if type(label) is not str or label != s:
            raise CheckerUnavailable("CheckerUnavailable: malformed Lean label result")
        return label

    return owned("label", lean)


# Kinds are kept in their wire form (a string or a tagged list); decoding only validates.
def _check_kind(data, depth=16, *, reports=False):
    if depth == 0:
        raise ResourceLimit("ResourceLimit: kind depth exceeds 16")
    if type(data) is str:
        if data not in ATOMIC_KINDS:
            raise VEError(f"unknown kind {data}")
        return data
    if type(data) is not list:
        raise VEError("invalid kind")
    if len(data) == 4 and data[0] == "attributed" and type(data[1]) is str and type(data[2]) is str:
        if not (token(data[1]) and data[2] in (ACTS + ("wants",) if reports else ACTS)):
            raise VEError("invalid attributed kind")
        _check_kind(data[3], depth - 1, reports=reports)
    elif len(data) == 3 and data[0] == "hedged" and type(data[1]) is str:
        if data[1] not in MODALITIES:
            raise VEError("invalid hedged kind")
        _check_kind(data[2], depth - 1, reports=reports)
    elif len(data) == 4 and data[0] == "causal" and type(data[1]) is str:
        if data[1] not in RELATIONS:
            raise VEError("invalid causal kind")
        _check_kind(data[2], depth - 1, reports=reports)
        _check_kind(data[3], depth - 1, reports=reports)
    elif len(data) == 2 and data[0] == "unformalised" and type(data[1]) is str:
        if not token(data[1]):
            raise VEError("invalid unformalised reason")
    else:
        raise VEError("invalid kind")
    return data


def _quoted(kind) -> bool:
    return type(kind) is list and kind[0] in ("attributed", "hedged")


def _fields(data, required, optional=(), path=""):
    require_fields(data, set(required) | {k for k in optional if type(data) is dict and k in data},
                   path=path)


def _nat(value) -> int:
    if type(value) is not int or isinstance(value, bool) or value < 0:
        raise VEError("expected a natural number")
    return value


def _array(value) -> list:
    if type(value) is not list:
        raise VEError("expected an array")
    return value


def _decode_reading_set(env, data):
    _fields(data, ("id", "version", "readings"))
    rid = data["id"]
    if type(rid) is not str:
        raise VEError("expected a string")
    if not token(rid):
        raise VEError(f"invalid reading set id {rid}")
    version = _nat(data["version"])
    readings = [formula_from_data(env, r) for r in _array(data["readings"])]
    if not 1 <= len(readings) <= 64:
        raise VEError("reading sets hold 1 to 64 readings")
    return rid, version, readings


def _disjunction(readings):
    result = readings[-1]
    for formula in reversed(readings[:-1]):
        result = Or(formula, result)
    return result


@semantic_entry("admission")
def admit_document(environment, document) -> dict:
    """Admit a document: Lean's admission routes decide under every authority (lean-first batch 13b).

    Returns the admitted report, its `ve-report-<identity>` id and the units'
    kinds rendered back (byte-identical to the input kinds), or raises Lean's
    diagnostic."""
    from .backends.dispatch import owned

    if (getattr(environment, "unit_schema", None) is not None or (
            type(environment) is dict and "unit_schema" in environment)) and "risk@0" not in (
            environment.profiles if type(environment) is Environment else listed_profiles(environment)):
        # W6: the Lean quantity route admits every annotated statement before erasure,
        # under every authority (Lean-first batch 9 deleted the Python copy). A risk
        # environment's W6 extension is the Lean risk route's, which admits it below.
        env = environment if type(environment) is Environment else Environment(environment)
        return _lean_quantity_admission(env, document)
    return owned("admission", lambda: _admit_lean(environment, document))


def _uses_norms(env, document) -> bool:
    """The norms route takes every input with a norm construct (11.4): a regulated
    declaration or norm content, as Lean `usesNormsPath` does."""
    return "norms@0" in env.profiles and (
        any(d.regulated is not None for d in env.predicates.values()) or
        (type(document) is dict and type(document.get("units")) is list and
         any(type(u) is dict and type(u.get("content")) is dict and "norm" in u["content"]
             for u in document["units"])))


def _admit_lean(environment, document) -> dict:
    """The Lean route that admits `document`, chosen by the envelope (routing, not a verdict)."""
    from .backends.relay import decide
    from .softnorms import SoftEnvironment
    if isinstance(environment, SoftEnvironment) or (type(environment) is dict and
            "soft-norms@0" in listed_profiles(environment)):
        from .soft_route import admit_soft_document
        return admit_soft_document(environment, document)
    env = environment if type(environment) is Environment else Environment(environment)
    if env.alternatives is not None:
        return _lean_block_admission(env, document)
    if "norm-defaults@0" in env.profiles:
        from .norm_defaults_route import admit_norm_defaults_document
        return admit_norm_defaults_document(env, document)
    if env.language != LANGUAGE:
        raise VEError("admission requires a ve.core@0.2 environment")
    case = {"id": "admission", "kind": "admission", "environment": env.to_dict(), "document": document}
    return bound_admission(env, document, decide("norms" if _uses_norms(env, document) else "route", [case])[0])


def bind_report(document, report) -> None:
    """Bind an admission report to the request graph: its root is the graph's root claim and its
    assumptions are exactly the ordered unfolding of the root (ClaimGraph.lean `Unfolds`): a leaf
    gives itself, a deduction the unfoldings of its premises in order, so a shared or repeated
    premise is listed once per use. A claim is a node's name, AST and label as the node states
    them. Every admission relay calls this one binder; anything else raises ValueError."""
    from .backends.service_schema import same_json
    fields = ("name", "ast", "label")
    graph = document["graph"]
    nodes = {}
    for node in graph["nodes"]:
        if type(node) is not dict or type(node["name"]) is not str or node["name"] in nodes:
            raise ValueError("graph node")
        nodes[node["name"]] = node

    def same_claim(claim, node):
        return type(claim) is dict and set(claim) == {key for key in fields if key in node} and all(
            same_json(claim[key], node[key]) for key in claim)

    # Leaf counts first, so an unfolding of another size is refused before it is walked.
    counts, expanding, stack = {}, set(), [(graph["root"], False)]
    while stack:
        name, expanded = stack.pop()
        premises = nodes[name].get("premises")
        if expanded:
            counts[name] = sum(counts[premise] for premise in premises)
            expanding.discard(name)
        elif name in expanding:
            raise ValueError("cyclic graph")
        elif name not in counts and premises is None:
            counts[name] = 1
        elif name not in counts:
            expanding.add(name)
            stack.append((name, True))
            stack.extend((premise, False) for premise in reversed(premises))
    assumptions = report["assumptions"]
    if (not same_claim(report["root"], nodes[graph["root"]]) or type(assumptions) is not list or
            len(assumptions) != counts[graph["root"]]):
        raise ValueError("report root or assumption count")
    position, stack = 0, [graph["root"]]
    while stack:
        name = stack.pop()
        if "premises" in nodes[name]:
            stack.extend(premise for premise in reversed(nodes[name]["premises"]) if counts[premise])
        elif not same_claim(assumptions[position], nodes[name]):
            raise ValueError("report assumption")
        else:
            position += 1


def bound_admission(env, document, row) -> dict:
    """Lean's admission row, bound to the request: the units' kinds rendered back are the request's,
    each reported claim is a graph node with the same name, AST and label, the report's root is
    the graph's root, and `report_id` is the identity of exactly this report over the environment
    and document sent (the wire digest, rule 5), so no field of the report can change unseen.
    Anything else is CheckerUnavailable: Lean's answer is relayed, never repaired."""
    from .backends.lean_service import CheckerUnavailable
    from .backends.service_schema import same_json
    from .wire import digest
    if set(row) != {"id", "status", "admitted", "report", "report_id", "kinds"} or row["admitted"] is not True:
        raise CheckerUnavailable("CheckerUnavailable: malformed Lean admission result")
    units = document.get("units") if type(document) is dict else None
    report = row["report"]
    try:
        bind_report(document, report)
        bound = True
    except (KeyError, TypeError, ValueError, IndexError):
        bound = False
    try:
        expected = digest(f"ve-report-{env.identity_version}\n",
                          {"environment_id": env.environment_id, "document": document, "report": report})
    except (VEError, TypeError, ValueError):
        expected = None
    if (type(units) is not list or row["kinds"] != [u.get("kind") if type(u) is dict else None for u in units]
            or not bound or row["report_id"] != expected):
        raise CheckerUnavailable("CheckerUnavailable: the Lean admission answer is not bound to the request")
    return {key: row[key] for key in ("admitted", "report", "report_id", "kinds")}


def _lean_block_admission(env, document) -> dict:
    from .backends.relay import decide
    case = {"id": "admission", "kind": "admission", "environment": env.to_dict(),
            "document": document}
    row = decide("risk" if env.risk is not None else "alternatives", [case])[0]
    return {key: row[key] for key in ("admitted", "report", "report_id", "kinds",
                                      "conditional_on")}


def _lean_quantity_admission(env, document) -> dict:
    """W6 quantity admission by the Lean quantity route (service mode `quantity`, case kind
    `document`); a rejection raises Lean's diagnostic."""
    from .backends.relay import decide
    [row] = decide("quantity", [{"id": "admission", "kind": "document",
                                 "environment": env.to_dict(), "document": document}])
    return {key: row[key] for key in ("admitted", "report", "report_id", "kinds")}
