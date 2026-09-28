"""W6a quantity document admission; early diagnostics for Lean `VE.Time.Document`.

The P0 admission input with every formula replaced by a `ve-quantity@1`
statement: unit `content`, reading-set readings and graph-node `quantity`.
Every statement is regenerated and admitted before erasure. Deductions carry a
`ve-quantity-certificate@1` bound to the annotated meaning ids of exactly their
premise nodes and the node. Provenance rules and diagnostics are the base
route's. The units-only layer generates no Background, so background leaves are
never admitted. Citations are bound by checked lemmas: a lemma's certificate
establishes its conclusion from exactly its transitive leaves, a `cite` leaf
states that conclusion, and the report must carry the lemma's leaves.
Lean (`ve_quantity`, case kind `document`) is the authority.
"""
from __future__ import annotations

from typing import NamedTuple

from .admission import (AdmissionError, GRAPH_REJECTED, _array, _check_kind, _compatible, _fields,
                        _nat, _quoted, _agent_matches, _tokens, parse_label, token)
from .errors import ResourceLimit, UnsupportedProfile, VEError
from .units import CERTIFICATE_FORMAT, check_quantity_certificate, elaborate_quantity, quantity_meaning_id
from .wire import canonical_json, digest


class _Unit(NamedTuple):
    id: str
    start: int
    stop: int
    kind: object
    content: object  # canonical Q formula (JSON) or None


class _Node(NamedTuple):
    name: str
    payload: dict  # canonical ve-quantity@1 object
    label: str
    unit: str | None
    premises: tuple | None
    certificate: object


def _q(env, payload):
    canonical, _ = elaborate_quantity(env, payload)
    return canonical


def _key(formula):
    return canonical_json(formula)


def _decode_unit(env, data):
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
    content = _q(env, data["content"])["formula"] if "content" in data else None
    return _Unit(uid, start, stop, kind, content)


def _decode_reading_set(env, data):
    _fields(data, ("id", "version", "readings"))
    rid = data["id"]
    if type(rid) is not str:
        raise VEError("expected a string")
    if not token(rid):
        raise VEError(f"invalid reading set id {rid}")
    version = _nat(data["version"])
    readings = [_q(env, r)["formula"] for r in _array(data["readings"])]
    if not 1 <= len(readings) <= 64:
        raise VEError("reading sets hold 1 to 64 readings")
    return rid, version, readings


def _decode_node(env, data):
    _fields(data, ("name", "quantity"), ("label", "unit", "premises", "certificate"))
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
    payload = _q(env, data["quantity"])
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
        _certificate(data["certificate"])
    return _Node(name, payload, label, unit, premises, data.get("certificate"))


def _certificate(certificate):
    if (type(certificate) is not dict or set(certificate) != {
            "format", "environment_id", "premise_meaning_ids", "conclusion_meaning_id", "core"}
            or certificate["format"] != CERTIFICATE_FORMAT):
        # A raw order certificate, or any other object, is not W6 evidence.
        raise VEError("Invalid quantity certificate")
    return certificate


class _Lemma(NamedTuple):
    name: str
    conclusion: dict  # canonical ve-quantity@1 object
    leaves: list  # [(canonical ve-quantity@1 object, label)]


def _decode_leaf(env, data):
    _fields(data, ("quantity", "label"))
    label = data["label"]
    if type(label) is not str:
        raise VEError("expected a string")
    parsed = parse_label(label)
    if parsed is None:
        raise AdmissionError(f"AdmissionError: invalid label {label}")
    if parsed.kind == "cite":
        raise AdmissionError("AdmissionError: lemma leaves must be transitive (no cite labels)")
    return _q(env, data["quantity"]), label


def _decode_lemma(env, data):
    """Lean `decodeLemma`: the certificate must establish the conclusion from
    exactly the leaves, in order, bound to their annotated meaning ids."""
    _fields(data, ("name", "conclusion", "leaves", "certificate"))
    name = data["name"]
    if type(name) is not str:
        raise VEError("expected a string")
    parsed = parse_label("cite:" + name)
    if parsed is None or parsed.kind != "cite":
        raise VEError(f"invalid lemma name {name}")
    conclusion = _q(env, data["conclusion"])
    leaves = [_decode_leaf(env, leaf) for leaf in _array(data["leaves"])]
    if len(leaves) > 1000:
        raise ResourceLimit("ResourceLimit: lemma leaves")
    certificate = _certificate(data["certificate"])
    try:
        valid = check_quantity_certificate(env, [p for p, _ in leaves], conclusion, certificate)
    except VEError:
        valid = False
    if not valid:
        raise AdmissionError(f"AdmissionError: lemma {name} is not established by its certificate")
    return _Lemma(name, conclusion, leaves)


def _disjunction(readings):
    result = readings[-1]
    for formula in reversed(readings[:-1]):
        result = ["or", formula, result]
    return result


class _Doc(NamedTuple):
    units: list
    lemmas: list
    open_terms: list
    reading_sets: list
    narrowings: list


def _asserted_unit(doc, uid, formula):
    return any(u.id == uid and u.kind == "asserted" and u.content is not None
               and _key(u.content) == _key(formula) for u in doc.units)


def _leaf_admitted(doc, node):
    label = parse_label(node.label)
    if label is None:
        return False
    kind, a = label
    formula = node.payload["formula"]
    if kind == "asserted":
        return node.unit is not None and _asserted_unit(doc, node.unit, formula)
    if kind == "bridge":
        return (node.unit in (None, a[1]) and
                any(u.id == a[1] and _quoted(u.kind) and u.content is not None
                    and _key(u.content) == _key(formula) and _agent_matches(u.kind, a[0])
                    for u in doc.units))
    if node.unit is not None:
        return False
    if kind == "cite":
        return any(m.name == f"{a[0]}/{a[1]}" and _key(m.conclusion["formula"]) == _key(formula)
                   for m in doc.lemmas)
    if kind == "open":
        return a[0] in doc.open_terms
    if kind == "readings":
        for rid, version, readings in doc.reading_sets:
            if rid == a[0] and version == a[1]:
                if a[2] is None and _key(_disjunction(readings)) == _key(formula):
                    return True
                if a[2] is not None and a[2] < len(readings) and _key(readings[a[2]]) == _key(formula):
                    return True
        return False
    if kind == "narrowing":
        return a[0] in doc.narrowings
    return False  # background: the units-only layer generates none


def _node_admitted(doc, node):
    if node.premises is not None:
        return node.label == "asserted" and (
            node.unit is None or _asserted_unit(doc, node.unit, node.payload["formula"]))
    return _leaf_admitted(doc, node)


def _diagnostic(doc, node):
    label = parse_label(node.label)
    bridge_naming = label.args[1] if label is not None and label.kind == "bridge" and node.premises is None else None
    unit = next((u for u in doc.units if u.id == node.unit), None) if node.unit is not None else None
    if unit is not None:
        if _quoted(unit.kind) and bridge_naming != unit.id:
            return f"AdmissionError: quoted content of unit {unit.id} is used without a bridge leaf"
        return f"AdmissionError: node {node.name} is not admitted under label {node.label}"
    if label is None:
        return f"AdmissionError: invalid label {node.label}"
    return f"AdmissionError: node {node.name} is not admitted under label {node.label}"


def _check_graph(env, nodes):
    """Lean `checkGraph`: nodes in submitted order; entries are
    (node, [(name, payload, label)] leaves)."""
    entries = {}
    for n in nodes:
        if n.name in entries:
            raise VEError(GRAPH_REJECTED)
        if n.premises is None:
            entries[n.name] = (n, [(n.name, n.payload, n.label)])
            continue
        if any(p not in entries for p in n.premises):
            raise VEError(GRAPH_REJECTED)
        children = [entries[p] for p in n.premises]
        try:
            valid = check_quantity_certificate(env, [c[0].payload for c in children], n.payload,
                                               n.certificate)
        except VEError:
            valid = False
        if not valid:
            raise VEError(GRAPH_REJECTED)
        entries[n.name] = (n, [a for c in children for a in c[1]])
    return entries


def _claim(env, name, payload, label):
    return {"name": name, "quantity": payload, "meaning_id": quantity_meaning_id(env, payload),
            **({} if label == "asserted" else {"label": label})}


def admit_quantity_document(env, document) -> dict:
    """Admit a quantity document or raise with Lean's diagnostic."""
    if "documents@1" not in env.profiles:
        raise UnsupportedProfile("quantity documents require documents@1")
    _fields(document, ("units", "graph"), ("lemmas", "open_terms", "reading_sets", "narrowings"))
    units = [_decode_unit(env, u) for u in _array(document["units"])]
    if len(units) > 10000:
        raise ResourceLimit("ResourceLimit: unit count")
    if len({u.id for u in units}) != len(units):
        raise VEError("duplicate unit id")
    if any(a.stop > b.start for a, b in zip(units, units[1:])):
        raise VEError("unit spans must be sorted and non-overlapping")
    optional = {key: _array(document[key]) if key in document else []
                for key in ("lemmas", "open_terms", "reading_sets", "narrowings")}
    lemmas = [_decode_lemma(env, m) for m in optional["lemmas"]]
    if len({m.name for m in lemmas}) != len(lemmas):
        raise VEError("duplicate lemma")
    open_terms = _tokens(optional["open_terms"])
    reading_sets = [_decode_reading_set(env, r) for r in optional["reading_sets"]]
    if len({(r[0], r[1]) for r in reading_sets}) != len(reading_sets):
        raise VEError("duplicate reading set version")
    narrowings = _tokens(optional["narrowings"])
    doc = _Doc(units, lemmas, open_terms, reading_sets, narrowings)
    graph = document["graph"]
    _fields(graph, ("root", "nodes"))
    if type(graph["root"]) is not str:
        raise VEError("expected a string")
    raw_nodes = _array(graph["nodes"])
    if len(raw_nodes) > 1000:
        raise ResourceLimit("ResourceLimit: graph node count")
    nodes = [_decode_node(env, n) for n in raw_nodes]
    for n in nodes:
        if not _node_admitted(doc, n):
            raise AdmissionError(_diagnostic(doc, n))
    entries = _check_graph(env, nodes)
    if graph["root"] not in entries:
        raise VEError(GRAPH_REJECTED)
    root, assumptions = entries[graph["root"]]
    for _, _, label in assumptions:
        parsed = parse_label(label)
        if parsed is None or parsed.kind != "cite":
            continue
        for lemma in (m for m in lemmas if m.name == f"{parsed.args[0]}/{parsed.args[1]}"):
            if not all(any(_key(y[1]["formula"]) == _key(p["formula"]) and y[2] == leaf_label
                           for y in assumptions) for p, leaf_label in lemma.leaves):
                raise AdmissionError("AdmissionError: a cited lemma's leaves are missing from the report")
    if not all(_compatible(a[2], b[2]) for a in assumptions for b in assumptions):
        raise AdmissionError("AdmissionError: incompatible reading choices")
    report = {"root": _claim(env, root.name, root.payload, root.label),
              "assumptions": [_claim(env, *a) for a in assumptions]}
    return {"admitted": True, "report": report,
            "report_id": digest(f"ve-report-{env.identity_version}\n",
                                {"environment_id": env.environment_id, "document": document,
                                 "report": report}),
            "kinds": [u.kind for u in units]}
