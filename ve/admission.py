"""Claim labels and executable document admission on ve.core@0.2 (PLAN-EXPAND2 3.6).

This mirrors `lean/VE/Route/Admission.lean` rule for rule and diagnostic for
diagnostic, so Python and the Lean `route` subcommand admit the same documents
    and report the same labels. A quoted unit must be named through its bridge;
    an independent formula-equal leaf keeps its own declared provenance.
    Admission graph edges bind exactly their premise
nodes; Background enters only as explicit `background:<generator>` leaves whose
formulas are regenerated from the environment.
"""
from __future__ import annotations

import re
from typing import NamedTuple

from .ast import Or, formula_from_data, formula_to_data
from .background import HOOKS, background
from .environment import Environment
from .errors import ResourceLimit, UnsupportedProfile, VEError
from .identity import meaning_id
from .profiles import LANGUAGE, require_checker
from .wire import digest, require_fields

_TOKEN = re.compile(r"[A-Za-z0-9_.\-]+\Z", re.ASCII)
_NAT = re.compile(r"(0|[1-9][0-9]*)\Z", re.ASCII)
GENERATORS = tuple(HOOKS)
ATOMIC_KINDS = ("asserted", "norm", "definition", "question", "instruction", "example",
                "exposition", "analogy", "explanation", "meta")
ACTS = ("says", "promised", "believes", "intends", "expects", "denies")
MODALITIES = ("could", "likely", "generally", "typically", "effectively")
RELATIONS = ("because", "in order to", "prevents")
GRAPH_REJECTED = ("graph rejected: cycle, duplicate name, dangling premise, ill-typed claim or "
                  "invalid certificate")


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
                "readings": lambda: f"readings:{a[0]}@{a[1]}:{'all' if a[2] is None else a[2]}",
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
        if rest[1] == "all":
            return Label("readings", (parts[0], int(rest[0]), None))
        return Label("readings", (parts[0], int(rest[0]), int(rest[1]))) if _NAT.fullmatch(rest[1]) else None
    if s.startswith("narrowing:"):
        return Label("narrowing", (s[10:],)) if token(s[10:]) else None
    return None


def parse_label(s) -> Label | None:
    """Only canonical label strings parse: the label renders back to the input."""
    if type(s) is not str:
        return None
    label = _parse_raw(s)
    return label if label is not None and label.render() == s else None


def validate_label(s) -> str:
    if parse_label(s) is None:
        raise AdmissionError(f"AdmissionError: invalid label {s}")
    return s


# Kinds are kept in their wire form (a string or a tagged list); decoding only validates.
def _check_kind(data, depth=16):
    if depth == 0:
        raise ResourceLimit("ResourceLimit: kind depth exceeds 16")
    if type(data) is str:
        if data not in ATOMIC_KINDS:
            raise VEError(f"unknown kind {data}")
        return data
    if type(data) is not list:
        raise VEError("invalid kind")
    if len(data) == 4 and data[0] == "attributed" and type(data[1]) is str and type(data[2]) is str:
        if not (token(data[1]) and data[2] in ACTS):
            raise VEError("invalid attributed kind")
        _check_kind(data[3], depth - 1)
    elif len(data) == 3 and data[0] == "hedged" and type(data[1]) is str:
        if data[1] not in MODALITIES:
            raise VEError("invalid hedged kind")
        _check_kind(data[2], depth - 1)
    elif len(data) == 4 and data[0] == "causal" and type(data[1]) is str:
        if data[1] not in RELATIONS:
            raise VEError("invalid causal kind")
        _check_kind(data[2], depth - 1)
        _check_kind(data[3], depth - 1)
    elif len(data) == 2 and data[0] == "unformalised" and type(data[1]) is str:
        if not token(data[1]):
            raise VEError("invalid unformalised reason")
    else:
        raise VEError("invalid kind")
    return data


def _quoted(kind) -> bool:
    return type(kind) is list and kind[0] in ("attributed", "hedged")


def _agent_matches(kind, agent) -> bool:
    return not (type(kind) is list and kind[0] == "attributed") or kind[1] == agent


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


def _tokens(value) -> list[str]:
    items = _array(value)
    if not all(type(x) is str for x in items):
        raise VEError("expected strings")
    if not all(map(token, items)):
        raise VEError("invalid name")
    return items


class _Unit(NamedTuple):
    id: str
    start: int
    stop: int
    kind: object
    content: object


class _Node(NamedTuple):
    name: str
    ast: object
    formula: object
    label: str
    unit: str | None
    premises: tuple | None
    certificate: object


def _decode_unit(env, data) -> _Unit:
    _fields(data, ("id", "span", "kind"), ("content",))
    uid = data["id"]
    if type(uid) is not str:
        raise VEError("expected a string")
    if not token(uid):
        raise VEError(f"invalid unit id {uid}")
    span = _array(data["span"])
    if len(span) != 2:
        raise VEError("invalid span")
    start, stop = _nat(span[0]), _nat(span[1])
    if start > stop:
        raise VEError("invalid span")
    kind = _check_kind(data["kind"])
    content = formula_from_data(env, data["content"]) if "content" in data else None
    return _Unit(uid, start, stop, kind, content)


def _decode_leaf(env, data):
    _fields(data, ("ast", "label"))
    label = data["label"]
    if type(label) is not str:
        raise VEError("expected a string")
    parsed = parse_label(label)
    if parsed is None:
        raise AdmissionError(f"AdmissionError: invalid label {label}")
    if parsed.kind == "cite":
        raise AdmissionError("AdmissionError: lemma leaves must be transitive (no cite labels)")
    formula = formula_from_data(env, data["ast"], _generated=parsed.kind == "background")
    return formula, label


def _decode_lemma(env, data):
    _fields(data, ("name", "conclusion", "leaves"))
    name = data["name"]
    if type(name) is not str:
        raise VEError("expected a string")
    parsed = parse_label("cite:" + name)
    if parsed is None or parsed.kind != "cite":
        raise VEError(f"invalid lemma name {name}")
    conclusion = formula_from_data(env, data["conclusion"])
    leaves = [_decode_leaf(env, leaf) for leaf in _array(data["leaves"])]
    if len(leaves) > 1000:
        raise ResourceLimit("ResourceLimit: lemma leaves")
    return name, conclusion, leaves


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


class _Doc(NamedTuple):
    units: list
    lemmas: list
    open_terms: list
    reading_sets: list
    narrowings: list
    background: tuple


def _decode_doc(env, data) -> _Doc:
    units = [_decode_unit(env, u) for u in _array(data["units"])]
    if len(units) > 10000:
        raise ResourceLimit("ResourceLimit: unit count")
    if len({u.id for u in units}) != len(units):
        raise VEError("duplicate unit id")
    if any(a.stop > b.start for a, b in zip(units, units[1:])):
        raise VEError("unit spans must be sorted and non-overlapping")
    optional = {key: _array(data[key]) if key in data else []
                for key in ("lemmas", "open_terms", "reading_sets", "narrowings")}
    lemmas = [_decode_lemma(env, m) for m in optional["lemmas"]]
    if len({m[0] for m in lemmas}) != len(lemmas):
        raise VEError("duplicate lemma")
    open_terms = _tokens(optional["open_terms"])
    reading_sets = [_decode_reading_set(env, r) for r in optional["reading_sets"]]
    if len({(r[0], r[1]) for r in reading_sets}) != len(reading_sets):
        raise VEError("duplicate reading set version")
    narrowings = _tokens(optional["narrowings"])
    return _Doc(units, lemmas, open_terms, reading_sets, narrowings,
                tuple((p.formula, p.generator) for p in background(env)))


def _decode_node(env, data) -> _Node:
    _fields(data, ("name", "ast"), ("label", "unit", "premises", "certificate"))
    name = data["name"]
    if type(name) is not str:
        raise VEError("expected a string")
    label = "asserted"
    if "label" in data:
        if type(data["label"]) is not str:
            raise VEError("expected a string")
        if data["label"] == "asserted":
            raise VEError("non-canonical label: the default label asserted is omitted")
        label = data["label"]
    formula = formula_from_data(env, data["ast"], _generated=label.startswith("background:"))
    unit = data.get("unit")
    if "unit" in data and type(unit) is not str:
        raise VEError("expected a string")
    if ("premises" in data) != ("certificate" in data):
        raise VEError("premises and certificate come together")
    premises = None
    if "premises" in data:
        premises = tuple(_array(data["premises"]))
        if not all(type(p) is str for p in premises):
            raise VEError("expected strings")
    return _Node(name, data["ast"], formula, label, unit, premises, data.get("certificate"))


def _unit(doc, uid):
    return next((u for u in doc.units if u.id == uid), None)


def _asserted_unit(doc, uid, formula) -> bool:
    return any(u.id == uid and u.kind == "asserted" and u.content == formula for u in doc.units)


def _leaf_admitted(doc, node) -> bool:
    label = parse_label(node.label)
    if label is None:
        return False
    kind, a = label
    if kind == "asserted":
        return node.unit is not None and _asserted_unit(doc, node.unit, node.formula)
    if kind == "bridge":
        return (node.unit in (None, a[1]) and
                any(u.id == a[1] and _quoted(u.kind) and u.content == node.formula
                    and _agent_matches(u.kind, a[0]) for u in doc.units))
    if node.unit is not None:
        return False
    if kind == "background":
        return (node.formula, a[0]) in doc.background
    if kind == "cite":
        return any(m[0] == f"{a[0]}/{a[1]}" and m[1] == node.formula for m in doc.lemmas)
    if kind == "open":
        return a[0] in doc.open_terms
    if kind == "readings":
        for rid, version, readings in doc.reading_sets:
            if rid == a[0] and version == a[1]:
                if a[2] is None and _disjunction(readings) == node.formula:
                    return True
                if a[2] is not None and a[2] < len(readings) and readings[a[2]] == node.formula:
                    return True
        return False
    return a[0] in doc.narrowings  # narrowing


def _node_admitted(doc, node) -> bool:
    if node.premises is not None:
        return node.label == "asserted" and (node.unit is None or _asserted_unit(doc, node.unit, node.formula))
    return _leaf_admitted(doc, node)


def _diagnostic(doc, node) -> str:
    label = parse_label(node.label)
    bridge_naming = label.args[1] if label is not None and label.kind == "bridge" and node.premises is None else None
    unit = _unit(doc, node.unit) if node.unit is not None else None
    if unit is not None:
        if _quoted(unit.kind) and bridge_naming != unit.id:
            return f"AdmissionError: quoted content of unit {unit.id} is used without a bridge leaf"
        return f"AdmissionError: node {node.name} is not admitted under label {node.label}"
    if label is None:
        return f"AdmissionError: invalid label {node.label}"
    return f"AdmissionError: node {node.name} is not admitted under label {node.label}"


def _check_graph(env, nodes, root):
    """The unchanged claim-graph check (`VE.Graph.checkTableau`): unique names,
    submitted topological order, typed claims, replayed certificates."""
    from .entailment import check_entailment_certificate
    names = [n.name for n in nodes]
    rank = {name: names.index(name) for name in names}
    if len(set(names)) != len(names) or any(
            n.premises is not None and any(rank.get(p, len(names)) >= rank[n.name] for p in n.premises)
            for n in nodes):
        raise VEError(GRAPH_REJECTED)
    reports = {}
    for n in nodes:
        claim = (n.name, n.formula, n.label)
        if n.premises is None:
            reports[n.name] = (claim, [claim])
            continue
        children = [reports[p] for p in n.premises]
        checked = check_entailment_certificate(env, [c[0][1] for c in children], n.formula,
                                               n.certificate, _background=False,
                                               _generated_premises=[c[0][2].startswith("background:")
                                                                    for c in children])
        if not checked.valid:
            raise VEError(GRAPH_REJECTED)
        reports[n.name] = (claim, [a for c in children for a in c[1]])
    if root not in reports:
        raise VEError(GRAPH_REJECTED)
    return reports[root]


def _compatible(x, y) -> bool:
    a, b = parse_label(x), parse_label(y)
    if a is None or b is None or a.kind != "readings" or b.kind != "readings" or a.args[0] != b.args[0]:
        return True
    return a.args[1] == b.args[1] and (a.args[2] is None or b.args[2] is None or a.args[2] == b.args[2])


def _claim_json(env, claim):
    name, formula, label = claim
    return {"name": name, "ast": formula_to_data(env, formula,
            _generated=label.startswith("background:")),
            **({} if label == "asserted" else {"label": label})}


def admit_document(environment, document) -> dict:
    """Admit a ve.core@0.2 document (FOL family) or raise with Lean's diagnostic.

    Returns the admitted report, its `ve-report-<identity>` id and the units'
    kinds rendered back (byte-identical to the input kinds)."""
    env = environment if type(environment) is Environment else Environment(environment)
    if env.language != LANGUAGE:
        raise VEError("admission requires a ve.core@0.2 environment")
    require_checker(env)
    if env.closure or env.order:
        raise UnsupportedProfile(f"admission on the {'order' if env.order else 'closure'} family is deferred")
    _fields(document, ("units", "graph"), ("lemmas", "open_terms", "reading_sets", "narrowings"))
    doc = _decode_doc(env, document)
    graph = document["graph"]
    _fields(graph, ("root", "nodes"))
    if type(graph["root"]) is not str:
        raise VEError("expected a string")
    raw_nodes = _array(graph["nodes"])
    if len(raw_nodes) > 1000:
        raise ResourceLimit("ResourceLimit: graph node count")
    nodes = [_decode_node(env, n) for n in raw_nodes]
    by_name = {}
    for n in nodes:
        by_name.setdefault(n.name, n)
    for n in nodes:  # certificate bindings, checked before admission (Lean `checkBindings`)
        if n.premises is None:
            continue
        for p in n.premises:
            if p not in by_name:
                raise VEError(f"dangling premise {p}")
        cert = n.certificate
        expected = ([meaning_id(env, by_name[p].formula,
                                _generated=by_name[p].label.startswith("background:"))
                     for p in n.premises], meaning_id(env, n.formula))
        if (type(cert) is not dict or cert.get("environment_id") != env.environment_id
                or (cert.get("premise_meaning_ids"), cert.get("conclusion_meaning_id")) != expected):
            raise VEError("certificate is stale or bound to different inputs")
    for n in nodes:
        if not _node_admitted(doc, n):
            raise AdmissionError(_diagnostic(doc, n))
    root, assumptions = _check_graph(env, nodes, graph["root"])
    for leaf in assumptions:
        label = parse_label(leaf[2])
        if label is not None and label.kind == "cite":
            lemma = next(m for m in doc.lemmas if m[0] == f"{label.args[0]}/{label.args[1]}")
            if not all(any(y[1] == f and y[2] == lab for y in assumptions) for f, lab in lemma[2]):
                raise AdmissionError("AdmissionError: a cited lemma's leaves are missing from the report")
    if not all(_compatible(a[2], b[2]) for a in assumptions for b in assumptions):
        raise AdmissionError("AdmissionError: incompatible reading choices")
    report = {"root": _claim_json(env, root), "assumptions": [_claim_json(env, a) for a in assumptions]}
    identity_payload = {"environment_id": env.environment_id, "document": document,
                        "report": report}
    return {"admitted": True, "report": report,
            "report_id": digest(f"ve-report-{env.identity_version}\n", identity_payload),
            "kinds": [u.kind for u in doc.units]}
