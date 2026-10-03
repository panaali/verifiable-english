"""W2 FOL admission for documents containing active W1 norm units.

Norm content remains a norm object in the source document. The only admitted
layer leaves are the premises regenerated from the active units. Ordinary W2
claim checking, citation closure and report identity use the P0 machinery.
"""
from __future__ import annotations

from dataclasses import replace

from .assurance import semantic_entry
from . import admission as w2
from .environment import Environment
from .errors import ResourceLimit, UnsupportedProfile, VEError
from .identity import meaning_id
from .norms import NormDocument
from .wire import digest


def _check_quoted(env, content):
    """A quoted norm never contributes a layer, but it is still a norm object
    over this environment: every single-rule check applies. Its precedence
    edges name rules of the quoted source, so they are not resolved here."""
    rule = NormDocument._decode(content)
    NormDocument(env, [replace(rule, over=())])


@semantic_entry("admission")
def admit_norm_document(environment, document):
    """Admit a document containing norm units under the selected authority."""
    from .backends.dispatch import authority_for, execute
    if authority_for("norms_admission") == "python":
        return _admit_norm_document_python(environment, document)
    env = environment if type(environment) is Environment else Environment(environment)
    if env.alternatives is not None:
        from .admission import admit_document
        return admit_document(env, document)
    case = {"id": "admission", "kind": "admission", "environment": env.to_dict(), "document": document}

    def lean():
        from .backends.lean_runner import run
        from .errors import CheckerUnavailable
        row = run("norms", [case])[0]
        if set(row) != {"id", "status", "admitted", "report", "report_id", "kinds"} or row["admitted"] is not True:
            raise CheckerUnavailable("CheckerUnavailable: malformed Lean norms admission result")
        return {key: row[key] for key in ("admitted", "report", "report_id", "kinds")}

    return execute("norms_admission", case, lambda: _admit_norm_document_python(env, document), lean=lean)


def _admit_norm_document_python(environment, document):
    env = environment if type(environment) is Environment else Environment(environment)
    if env.alternatives is not None:
        from .admission import admit_document
        return admit_document(env, document)
    if "norms@0" not in env.profiles:
        raise UnsupportedProfile("norms@0 is required")
    if env.closure or env.order:
        raise UnsupportedProfile("norm document admission is FOL-only")
    w2._fields(document, ("units", "graph"), ("lemmas", "open_terms", "reading_sets", "narrowings"))
    raw_units = w2._array(document["units"])
    if len(raw_units) > 10000:
        raise ResourceLimit("ResourceLimit: unit count")
    units = []
    active = []
    quoted = []
    for raw in raw_units:
        if type(raw) is not dict:
            raise VEError("invalid unit")
        content = raw.get("content")
        if type(content) is dict and "norm" in content:
            w2._fields(raw, ("id", "span", "kind", "content"))
            uid = raw["id"]
            if not w2.token(uid):
                raise VEError(f"invalid unit id {uid}")
            span = w2._array(raw["span"])
            if len(span) != 2:
                raise VEError("invalid span")
            start, stop = (w2._nat(x) for x in span)
            if start > stop:
                raise VEError("invalid span")
            kind = w2._check_kind(raw["kind"])
            if kind == "norm":
                active.append(content)
            elif w2._quoted(kind):
                quoted.append(content)
            else:
                raise VEError("norm content requires a norm or quoted kind")
            units.append(w2._Unit(uid, start, stop, kind, content))
        else:
            units.append(w2._decode_unit(env, raw))
    if len({u.id for u in units}) != len(units):
        raise VEError("duplicate unit id")
    if any(a.stop > b.start for a, b in zip(units, units[1:])):
        raise VEError("unit spans must be sorted and non-overlapping")
    try:
        norms = NormDocument(env, active)
    except VEError as error:
        from .norms_contract import public_rejection
        raise public_rejection(env.to_dict(), active, error)
    for content in quoted:
        _check_quoted(env, content)
    # Let the existing W2 decoder validate every non-unit source component.
    other = {**document, "units": []}
    decoded = w2._decode_doc(env, other)
    doc = w2._Doc(units, decoded.lemmas, decoded.open_terms, decoded.reading_sets,
                  decoded.narrowings, decoded.background)
    layers = dict(norms.premises())

    graph = document["graph"]
    w2._fields(graph, ("root", "nodes"))
    if type(graph["root"]) is not str:
        raise VEError("expected a string")
    raw_nodes = w2._array(graph["nodes"])
    if len(raw_nodes) > 1000:
        raise ResourceLimit("ResourceLimit: graph node count")
    nodes = [w2._decode_node(env, n) for n in raw_nodes]
    by_name = {}
    for node in nodes:
        by_name.setdefault(node.name, node)
    for node in nodes:
        if node.premises is None:
            continue
        for p in node.premises:
            if p not in by_name:
                raise VEError(f"dangling premise {p}")
        cert = node.certificate
        expected = ([meaning_id(env, by_name[p].formula) for p in node.premises],
                    meaning_id(env, node.formula))
        if (type(cert) is not dict or cert.get("environment_id") != env.environment_id
                or (cert.get("premise_meaning_ids"), cert.get("conclusion_meaning_id")) != expected):
            raise VEError("certificate is stale or bound to different inputs")
    for node in nodes:
        if node.premises is None and node.label.startswith("layer:norms:"):
            if node.unit is not None or layers.get(node.label) != node.formula:
                raise w2.AdmissionError(f"AdmissionError: node {node.name} is not admitted under label {node.label}")
        elif not w2._node_admitted(doc, node):
            raise w2.AdmissionError(w2._diagnostic(doc, node))
    root, assumptions = w2._check_graph(env, nodes, graph["root"])
    for leaf in assumptions:
        label = w2.parse_label(leaf[2])
        if label is not None and label.kind == "cite":
            lemma = next(m for m in doc.lemmas if m[0] == f"{label.args[0]}/{label.args[1]}")
            if not all(any(y[1] == f and y[2] == lab for y in assumptions) for f, lab in lemma[2]):
                raise w2.AdmissionError("AdmissionError: a cited lemma's leaves are missing from the report")
    if not all(w2._compatible(a[2], b[2]) for a in assumptions for b in assumptions):
        raise w2.AdmissionError("AdmissionError: incompatible reading choices")
    report = {"root": w2._claim_json(env, root),
              "assumptions": [w2._claim_json(env, a) for a in assumptions]}
    payload = {"environment_id": env.environment_id, "document": document, "report": report}
    return {"admitted": True, "report": report,
            "report_id": digest(f"ve-report-{env.identity_version}\n", payload),
            "kinds": [u.kind for u in units]}
