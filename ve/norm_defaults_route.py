"""Python entry points for the `ve_norm_defaults_route` Lean executable
(docs/spec/norm-defaults.md 3, 6 and 8).

Python builds `fill U`, `Fill_T` and the evidence; Lean regenerates `fill U`
from the same source and replays every piece of evidence. `check_regenerated`
compares Lean's `norm-defaults-elaborate` row with Python's regeneration byte
for byte, and `admit_norm_defaults_document` is W1's admission on `fill U`
(Lean `Admission.admitDocument`).
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from .assurance import semantic_entry
from .backends.lean import run_norm_defaults_cases
from . import admission as w2
from .ast import _to_data, formula_to_data
from .background import background
from .environment import Environment
from .errors import ResourceLimit, UnsupportedProfile, VEError
from .identity import meaning_id
from .norms import NormDocument
from .wire import digest
from . import norm_defaults as nd

LEAN_ROUTE = Path(__file__).resolve().parents[1] / "lean/.lake/build/bin/ve_norm_defaults_route"


def run_cases(cases, executable=LEAN_ROUTE, *, timeout=None):
    """Every case through one process; rows in case order (errors are rows)."""
    return run_norm_defaults_cases(executable, cases, timeout=timeout)


def run_case(case, executable=LEAN_ROUTE):
    row = run_cases([case], executable)[0]
    if row["status"] == "error":
        raise VEError(row["error"])
    return row


def source_case(document, kind, **fields):
    """A case over `document`'s source environment and author norm objects."""
    return {"id": kind, "kind": kind, "environment": document.env.to_dict(),
            "norms": [rule.to_dict() for rule in document.author.rules], **fields}


def regeneration(document):
    """Python's outputs of `fill U`, in the fields and order of Lean `Wire.regeneratedU`."""
    filled, env = document.filled, document.filled.env
    base = filled.base_environment()
    regulated = sorted(p for p, d in document.env.predicates.items() if d.regulated is not None)
    return {
        "order": list(filled.order),
        "background": [{"generator": p.generator, "ast": formula_to_data(env, p.formula, _generated=True)}
                       for p in background(env)],
        "premises": [{"label": label, "ast": formula_to_data(env, formula, _generated=True)}
                     for label, formula in filled.premises()],
        "conflict_targets": [{"target": name, "sorts": list(sorts), "ast": _to_data(formula)}
                             for name, sorts, formula in filled.conflict_targets()],
        "fill": [{"generator": "fill", "ast": formula_to_data(base, formula, _generated=True)}
                 for _, formula in document.fill_premises],
        "unspecified": list(document.unspec),
        "unsaid": [{"name": nd.unsaid_name(p), "sorts": list(document.env.predicates[p].arguments)}
                   for p in document.unspec],
        "reached": [{"predicate": p, "sorts": list(document.env.predicates[p].arguments),
                     "ast": _to_data(document.reached(p))} for p in regulated],
    }


def check_regenerated(document, row):
    """Compare every output of Lean's `norm-defaults-elaborate` row with Python's."""
    for field, value in regeneration(document).items():
        if row.get(field) != value:
            raise VEError(f"norm-defaults route regeneration mismatch: {field}")
    return row


def elaborate(document, executable=LEAN_ROUTE):
    """Lean's regeneration of `fill U`, checked against Python's before any use."""
    return check_regenerated(document, run_case(source_case(document, "norm-defaults-elaborate"),
                                                executable))


# Entailment over `fill U` (Lean `Wire.replayEntailmentU`).

def _filled_premises(document, premises):
    """`Background(E‴) ++ Fill_T ++ T‴ ++ Γ`, with the generated flag of each."""
    env = document.filled.env
    generated = [p.formula for p in background(env)]
    regenerated = [f for _, f in document.fill_premises] + [f for _, f in document.filled.premises()]
    return ([(f, True) for f in generated] + [(f, True) for f in regenerated]
            + [(f, False) for f in premises])


def _source_binding(document, premises, conclusion):
    """The binding Lean checks: the source environment (profile included) by
    `ve.core@0.2` identity and the ASTs of the premise list and conclusion."""
    env, filled = document.env, document.filled.env

    def meaning(formula, generated):
        return digest(f"ve-meaning-{env.identity_version}\n",
                      {"environment_id": env.environment_id,
                       "ast": formula_to_data(filled, formula, _generated=generated)})
    return {"environment_id": env.environment_id,
            "premise_meaning_ids": [meaning(f, g) for f, g in _filled_premises(document, premises)],
            "conclusion_meaning_id": meaning(conclusion, False)}


def prove_filled_entailment(document, premises, conclusion, **kwargs):
    """A certificate for `Background(E‴) ++ Fill_T ++ T‴ ++ Γ ⊢ φ`, bound to the source."""
    from .entailment import prove_entailment
    # The prover lists Background(E‴) first; the rest is Fill_T ++ T‴ ++ Γ.
    regenerated = [f for _, f in document.fill_premises] + [f for _, f in document.filled.premises()]
    proof = prove_entailment(document.filled.env, (*regenerated, *premises), conclusion, **kwargs)
    if proof.status != "Found":
        raise VEError(f"no certificate: {proof.status}")
    return {**proof.certificate, **_source_binding(document, premises, conclusion)}


# W2 admission on `fill U` (spec 2.3 and 3.2; Lean `VE.NormDefaults.Admission`).

def fill_labels(document):
    """`Fill_T` premises under their wire labels (`unsaid:pair:<r>,<m>`)."""
    return dict(document.fill_premises)


def filled_environment_json(document):
    """The regenerated `E‴` JSON that admission certificates bind (Lean `fillJson`)."""
    return document.filled.env.to_dict()


@semantic_entry("admission")
def admit_norm_defaults_document(environment, document):
    """W1's admission on `fill U`: nodes over `E‴`, certificates bound to `E‴`, and
    leaves that are W2 provenance, a regenerated layer of `T‴`, a pair premise
    (`background:profile`) or a `Fill_T` premise under its label."""
    env = environment if type(environment) is Environment else Environment(environment)
    if nd.PROFILE not in env.profiles:
        raise UnsupportedProfile("UnsupportedProfile: norm-defaults@0 is required")
    if env.closure or env.order:
        raise UnsupportedProfile("norm document admission is FOL-only")
    w2._fields(document, ("units", "graph"), ("lemmas", "open_terms", "reading_sets", "narrowings"))
    raw_units = w2._array(document["units"])
    if len(raw_units) > 10000:
        raise ResourceLimit("ResourceLimit: unit count")
    split, active, quoted = [], [], []
    for raw in raw_units:
        if type(raw) is not dict:
            raise VEError("invalid unit")
        content = raw.get("content")
        if type(content) is dict and "norm" in content:
            w2._fields(raw, ("id", "span", "kind", "content"))
            if not w2.token(raw["id"]):
                raise VEError(f"invalid unit id {raw['id']}")
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
            split.append(("norm", w2._Unit(raw["id"], start, stop, kind, content)))
        else:
            split.append(("other", raw))
    source = nd.UnspecifiedDocument(env, [NormDocument._decode(c) for c in active])
    # A quoted norm is checked over the source with each `unspecified` read as the
    # placeholder `deny` (Lean `checkQuoted` on the decoded source).
    placeholder = Environment(nd._placeholder(env.to_dict())) if quoted else None
    for content in quoted:
        rule = NormDocument._decode(content)
        NormDocument(placeholder, [replace(rule, over=())])
    filled = source.filled.env
    units = [item if tag == "norm" else w2._decode_unit(filled, item) for tag, item in split]
    if len({u.id for u in units}) != len(units):
        raise VEError("duplicate unit id")
    if any(a.stop > b.start for a, b in zip(units, units[1:])):
        raise VEError("unit spans must be sorted and non-overlapping")
    decoded = w2._decode_doc(filled, {**document, "units": []})
    doc = w2._Doc(units, decoded.lemmas, decoded.open_terms, decoded.reading_sets,
                  decoded.narrowings, decoded.background)
    layers = dict(source.filled.premises())
    fill = fill_labels(source)

    graph = document["graph"]
    w2._fields(graph, ("root", "nodes"))
    if type(graph["root"]) is not str:
        raise VEError("expected a string")
    raw_nodes = w2._array(graph["nodes"])
    if len(raw_nodes) > 1000:
        raise ResourceLimit("ResourceLimit: graph node count")
    nodes = [w2._decode_node(filled, n) for n in raw_nodes]
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
        expected = ([meaning_id(filled, by_name[p].formula,
                                _generated=by_name[p].label.startswith("background:"))
                     for p in node.premises], meaning_id(filled, node.formula))
        if (type(cert) is not dict or cert.get("environment_id") != filled.environment_id
                or (cert.get("premise_meaning_ids"), cert.get("conclusion_meaning_id")) != expected):
            raise VEError("certificate is stale or bound to different inputs")
    for node in nodes:
        leaf = node.premises is None and node.unit is None
        if leaf and node.label.startswith("layer:norms:") and layers.get(node.label) == node.formula:
            continue
        if leaf and node.label in fill and fill[node.label] == node.formula:
            continue
        if not w2._node_admitted(doc, node):
            raise w2.AdmissionError(w2._diagnostic(doc, node))
    root, assumptions = w2._check_graph(filled, nodes, graph["root"])
    for leaf in assumptions:
        label = w2.parse_label(leaf[2])
        if label is not None and label.kind == "cite":
            lemma = next(m for m in doc.lemmas if m[0] == f"{label.args[0]}/{label.args[1]}")
            if not all(any(y[1] == f and y[2] == lab for y in assumptions) for f, lab in lemma[2]):
                raise w2.AdmissionError("AdmissionError: a cited lemma's leaves are missing from the report")
    if not all(w2._compatible(a[2], b[2]) for a in assumptions for b in assumptions):
        raise w2.AdmissionError("AdmissionError: incompatible reading choices")
    report = {"root": w2._claim_json(filled, root),
              "assumptions": [w2._claim_json(filled, a) for a in assumptions]}
    payload = {"environment_id": env.environment_id, "document": document, "report": report}
    return {"admitted": True, "report": report,
            "report_id": digest(f"ve-report-{env.identity_version}\n", payload),
            "kinds": [u.kind for u in units]}
