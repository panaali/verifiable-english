"""Stage 0 executable Python oracle and frozen behaviour baseline.

Run ``uv run python tests/probe_matrix.py --write``. The JSON includes the full
return value (or exception record) for every executed cell; the Markdown is a
compact index. A plain invocation checks byte-for-byte reproducibility.
"""
from __future__ import annotations

import argparse
from dataclasses import fields, is_dataclass, replace
import itertools
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve import (ArgumentGraph, Claim, Deduction, Environment, FiniteModel, Top, Bottom,
                Unary, Const, check_argument, deduction_identity)
from ve.ast import Document, _to_data, check_formula, document_to_data, formula_from_data, formula_to_data
from ve.identity import meaning_id
from ve.background import background, dependency_order
from ve.definitions import compile_definitions
from ve.entailment import check_entailment_certificate, prove_entailment
from ve.evaluate import evaluate
from ve.errors import VEError, UnsupportedProfile
from ve.model import FiniteModel
from ve.parser import parse, canonicalize
from ve.printer import print_formula
from ve.search import check_countermodel, find_countermodel, find_distinguishing_model
from ve.admission import validate_label, admit_document
from ve.bundle import check_bundle
from ve.norms import NormDocument, check_conflict, check_norm_entailment_certificate, prove_norm_entailment
from ve.norm_admission import admit_norm_document
from ve.readings import check_readings
from ve.equivalence import compare, Budgets
from ve.vacuity import premise_status
from ve.profiles import SPEC_REVISION
from ve.english import parse_english
from ve.printer import render
from ve import limits
from ve.wire import canonical_json

OUT = ROOT / "conformance/baseline-2026-09"
LAYERS = ("data@0", "definitions@0", "documents@1", "norms@0", "time@0")
FAMILIES = ((), ("closure@0",), ("closure@0", "nary@0"), ("order@0",))
INPUT_CLASSES = ("positive", "rejection", "budget")
BUDGETED = {"evaluate", "evaluate_trace", "countermodel_check", "countermodel_search",
            "countermodel_search_nonempty", "countermodel_search_nonvacuous",
            "distinguishing_model", "certificate_replay", "norms_conflict", "readings",
            "compare", "premise_status"}
NO_REJECTION = {"background", "compare", "premise_status"}


def cases_for(name):
    return tuple(kind for kind in INPUT_CLASSES
                 if (kind != "budget" or name in BUDGETED)
                 and (kind != "rejection" or name not in NO_REJECTION))


def raw_environment(profiles):
    vocab = {"sorts": {"item": {"description": "item"}},
             "predicates": {"base": {"arguments": ["item"], "description": "base"}},
             "constants": {"x": {"sort": "item", "description": "x"}}}
    if "definitions@0" in profiles:
        vocab["predicates"]["derived"] = {"arguments": ["item"], "description": "derived",
            "defined": {"arguments": ["item"], "body": ["unary", "base", ["var", 0]]}}
    if "data@0" in profiles and "order@0" not in profiles:
        vocab["predicates"]["edge"] = {"arguments": ["item", "item"], "description": "edge",
                                             "functional": True}
    if "norms@0" in profiles:
        vocab["predicates"]["permitted"] = {"arguments": ["item"], "description": "permitted",
            "regulated": {"role": "plain", "default": "deny"}}
    return {"language": "ve.core@0.2", "profiles": sorted((*profiles, "relational-fol@0")),
            "spec_revision": SPEC_REVISION, "vocabulary": vocab}


def model_wire(env):
    return {"complete": True, "domains": {"item": ["i"]}, "constants": {"x": "i"},
            "relations": {name: ([["i"]] if name == "base" else []) for name, decl in env.predicates.items()
                          if decl.defined is None}}


def wire(value):
    if hasattr(value, "to_dict"):
        return wire(value.to_dict())
    if is_dataclass(value):
        return {f.name: wire(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, tuple):
        return [wire(x) for x in value]
    if isinstance(value, list):
        return [wire(x) for x in value]
    if isinstance(value, dict):
        return {str(k): wire(v) for k, v in value.items()}
    if value is None or type(value) in (str, int, float, bool):
        return value
    raise TypeError(f"Unserializable baseline result: {type(value).__name__}")


def outcome(call):
    try:
        result = wire(call())
        status = (result.get("status", result.get("verdict")) if isinstance(result, dict) else None)
        return {"cell": "S", "status": status or "accepted", "output": result}
    except Exception as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        code = exc.code if isinstance(exc, VEError) else type(exc).__name__
        return {"cell": "U" if isinstance(exc, UnsupportedProfile) else "R",
                "status": code, "output": exc.to_dict() if isinstance(exc, VEError)
                else {"code": code, "message": str(exc)}}


def operation(name, kind, env, model):
    """Exercise a small, deliberately explicit input for each public operation."""
    budget = kind == "budget"
    bad = kind == "rejection"
    source = "broken.\n" if bad else "true.\n"
    if name == "parse_accept": return lambda: document_to_data(env, parse(env, source))
    if name == "canonicalize": return lambda: canonicalize(env, source)
    if name == "typing": return lambda: formula_to_data(env, formula_from_data(env, ["not", ["top"]] if not bad else ["unary", "missing", ["const", "x"]]))
    if name == "environment_validation":
        def check_env():
            data = env.to_dict()
            if bad: data["profiles"] = ["missing@0", *data["profiles"]]
            checked = Environment(data)
            return {"environment_id": checked.environment_id, "environment": checked.to_dict()}
        return check_env
    if name == "model_validation":
        def check_model():
            data = model_wire(env)
            if bad: data["constants"]["x"] = "absent"
            checked = FiniteModel.from_dict(env, data)
            return {"model_id": checked.model_id, "model": checked.to_dict()}
        return check_model
    if name == "evaluate": return lambda: evaluate(env, Top(), replace(model, model_id="0" * 64) if bad else model, trace=False, max_evaluations=0 if budget else 8)
    if name == "evaluate_trace": return lambda: evaluate(env, Top(), replace(model, model_id="0" * 64) if bad else model, trace=True, max_trace_nodes=0 if budget else 8)
    if name == "countermodel_check": return lambda: check_countermodel(env, (), Bottom(), replace(model, model_id="0" * 64) if bad else model, max_evaluations=0 if budget else 8)
    if name.startswith("countermodel_search"):
        opts = {"max_domain_size": 1, "max_models": 0 if budget else 2, "max_evaluations": 8}
        if name.endswith("nonempty"): opts["nonempty_domains"] = True
        if name.endswith("nonvacuous"): opts["nonvacuous_for"] = Top()
        if bad: opts["max_models"] = -1
        return lambda: find_countermodel(env, (), Bottom(), **opts)
    if name == "distinguishing_model": return lambda: find_distinguishing_model(env, Top(), Bottom(), max_domain_size=1, max_models=-1 if bad else 0 if budget else 2)
    if name == "certificate_replay":
        proof = prove_entailment(env, (), Top(), max_steps=100)
        cert = proof.certificate if not bad else {}
        return lambda: check_entailment_certificate(env, (), Top(), cert, max_steps=0 if budget else 100)
    if name == "background": return lambda: [{"generator": p.generator, "ast": formula_to_data(env, p.formula, _generated=True)} for p in background(env)]
    if name == "definitions_elaboration":
        if "definitions@0" not in env.profiles: raise UnsupportedProfile("definitions@0 required")
        entries = env.definition_entries if not bad else {"absent": {"arguments": ["item"], "body": ["top"]}}
        return lambda: [{"name": d.name, "arguments": list(d.arguments), "body": _to_data(d.body)}
                        for d in compile_definitions(env, entries, version=env.environment_id)]
    if name == "dependency_order": return lambda: dependency_order({"a": {"a"} if bad else set(), "b": {"a"}})
    if name == "label": return lambda: validate_label("not a label" if bad else "asserted")
    if name == "admission":
        data = {"units": [{"id": "u", "span": [0, 5], "kind": "asserted", "content": ["top"]}],
                "graph": {"root": "r", "nodes": [{"name": "r", "ast": ["top"], "unit": "u"}]}}
        if bad: data["graph"]["root"] = "absent"
        return lambda: admit_document(env, data)
    if name == "bundle":
        data = {"version": "ve-bundle@0", "environment": env.to_dict(), "lemmas": []}
        if bad: data["version"] = "wrong"
        return lambda: check_bundle(data)
    if name == "norms_elaborate":
        if "norms@0" not in env.profiles: raise UnsupportedProfile("norms@0 required")
        doc = NormDocument(env, [])
        return lambda: formula_to_data(env, doc.elaborate("absent" if bad else "permitted"), _generated=True)
    if name == "norms_conflict":
        if "norms@0" not in env.profiles: raise UnsupportedProfile("norms@0 required")
        return lambda: check_conflict(NormDocument(env, []), model={} if bad else None,
                                      prove=not budget, tableau_steps=0 if budget else 8)
    if name == "norms_certificate":
        if "norms@0" not in env.profiles: raise UnsupportedProfile("norms@0 required")
        doc = NormDocument(env, [])
        proof = prove_norm_entailment(doc, (), Top(), max_steps=100)
        return lambda: check_norm_entailment_certificate(doc, (), Top(), {} if bad else proof.certificate)
    if name == "norms_admission":
        if "norms@0" not in env.profiles: raise UnsupportedProfile("norms@0 required")
        data = {"units": [{"id": "u", "span": [0, 5], "kind": "asserted", "content": ["top"]}],
                "graph": {"root": "absent" if bad else "r", "nodes": [{"name": "r", "ast": ["top"], "unit": "u"}]}}
        return lambda: admit_norm_document(env, data)
    if name == "readings": return lambda: check_readings(env, [], ["missing"] if bad else ["top"], max_steps=0 if budget else 8)
    if name == "argument_graph":
        claim = Claim.create(env, "r", "true.\n")
        graph = ArgumentGraph(env, (claim,), (), "absent" if bad else "r")
        return lambda: check_argument(graph, search=False)
    if name == "compare": return lambda: compare(env, Top(), Bottom(), Budgets(0 if budget else 8, 1, 0 if budget else 2, 8))
    if name == "premise_status": return lambda: premise_status(env, (), max_proof_steps=0 if budget else 8, max_models=0 if budget else 2)
    raise AssertionError(name)


OPERATIONS = ("parse_accept", "canonicalize", "typing", "environment_validation",
    "model_validation", "evaluate", "evaluate_trace", "countermodel_check",
    "countermodel_search", "countermodel_search_nonempty", "countermodel_search_nonvacuous",
    "distinguishing_model", "certificate_replay", "background", "definitions_elaboration",
    "dependency_order", "admission", "label", "bundle", "norms_elaborate", "norms_conflict",
    "norms_certificate", "norms_admission", "readings", "argument_graph", "compare", "premise_status")


def graph_baselines():
    """Exact legacy projection probes required by the converged amendments."""
    env = Environment(raw_environment(()))
    def claim(name, formula=Top()):
        return Claim.create(env, name, print_formula(env, formula) + ".\n")
    def with_certs(graph):
        edges = []
        by_name = {c.name: c for c in graph.claims}
        for edge in graph.deductions:
            proof = prove_entailment(env, tuple(by_name[n].ast for n in edge.premises),
                                     by_name[edge.conclusion].ast, max_steps=100)
            if proof.status == "Found":
                edge = replace(edge, certificates=({"edge_id": deduction_identity(graph, edge),
                    "direction": "follows", "proof": proof.certificate},))
            edges.append(edge)
        return replace(graph, deductions=tuple(edges))
    base = ArgumentGraph(env, (claim("a"), claim("b"), claim("root")),
                         (Deduction("ea", ("a",), "b"), Deduction("er", ("b",), "root")), "root")
    cases = {
        "reordered_declarations": with_certs(replace(base, claims=(base.claims[2], base.claims[0], base.claims[1]))),
        "shared_leaf": with_certs(ArgumentGraph(env, (claim("a"), claim("b"), claim("c"), claim("root")),
            (Deduction("eb", ("a",), "b"), Deduction("ec", ("a",), "c"),
             Deduction("er", ("b", "c"), "root")), "root")),
        "equal_id_aliases": with_certs(ArgumentGraph(env, (claim("alias_a"), claim("alias_b"), claim("root")),
            (Deduction("er", ("alias_a", "alias_b"), "root"),), "root")),
        "incomplete_graph": base,
        "disconnected_unproved": ArgumentGraph(env, (claim("root"), claim("other", Bottom())),
            (Deduction("unproved", (), "other"),), "root"),
    }
    disconnected = cases["disconnected_unproved"]
    invalid_edge = replace(disconnected.deductions[0], certificates=({"edge_id": "stale", "direction": "follows", "proof": {}},))
    cases["disconnected_invalid_certificate"] = replace(disconnected, deductions=(invalid_edge,))
    # A defined predicate has truth only through generated Background; no
    # explicit premise in this edge supplies the needed implication.
    bg_raw = raw_environment(("definitions@0",))
    bg_raw["vocabulary"]["predicates"]["derived"]["defined"]["body"] = ["top"]
    def_env = Environment(bg_raw)
    conclusion = Unary("derived", Const("x"))
    named = Claim.create(def_env, "root", print_formula(def_env, conclusion) + ".\n")
    g = ArgumentGraph(def_env, (named,), (Deduction("er", (), "root"),), "root")
    proof = prove_entailment(def_env, (), conclusion, max_steps=1000)
    if proof.status != "Found":
        raise AssertionError("Background-dependent probe did not produce a proof")
    edge = replace(g.deductions[0], certificates=({"edge_id": deduction_identity(g, g.deductions[0]),
        "direction": "follows", "proof": proof.certificate},))
    cases["background_dependent_certificate"] = replace(g, deductions=(edge,))
    rows = {name: {"package": graph.to_dict(), "output": check_argument(graph, search=False).to_dict()}
            for name, graph in cases.items()}
    from ve.argument_fixtures import worked_examples, infinite_only_example
    for name, graph in {**worked_examples(), "infinite_only": infinite_only_example()}.items():
        rows[f"worked_{name}"] = {"package": graph.to_dict(), "output": check_argument(graph).to_dict()}
    return rows


def boundary_baselines():
    """Exact cap and first-over-cap inputs for structural and public work limits."""
    env = Environment(raw_environment(()))
    model = FiniteModel.from_dict(env, model_wire(env))
    rows = {}
    def pair(name, cap, build):
        rows[name] = {"cap": cap, "at": outcome(lambda: build(cap)),
                      "over": outcome(lambda: build(cap + 1))}
    def work_pair(name, needed, build):
        rows[name] = {"cap": needed, "at": outcome(lambda: build(needed)),
                      "under": outcome(lambda: build(needed - 1))}
    source_at_cap = "true.\n" * 4464 + "false.\n" * 5536
    assert len(source_at_cap) == limits.MAX_SOURCE_BYTES
    pair("MAX_SOURCE_BYTES", limits.MAX_SOURCE_BYTES,
         lambda size: len(parse(env, source_at_cap + " " * (size - limits.MAX_SOURCE_BYTES)).formulas))
    pair("MAX_IDENTIFIER_BYTES", limits.MAX_IDENTIFIER_BYTES,
         lambda size: __import__("ve.environment", fromlist=["validate_identifier"]).validate_identifier("a" * size))
    def vocab_size(size, field):
        raw = raw_environment(())
        if field == "sorts":
            raw["vocabulary"][field].update({f"s{i}": {"description": "s"} for i in range(size - 1)})
        else:
            raw["vocabulary"][field].update({f"p{i}": {"arguments": ["item"], "description": "p"}
                                              for i in range(size - 1)})
        return Environment(raw).environment_id
    pair("MAX_SORTS", limits.MAX_SORTS, lambda size: vocab_size(size, "sorts"))
    pair("MAX_PREDICATES", limits.MAX_PREDICATES, lambda size: vocab_size(size, "predicates"))
    def entities(size):
        data = model_wire(env)
        data["domains"]["item"] = ["i"] + [f"j{i}" for i in range(size - 1)]
        return FiniteModel.from_dict(env, data).model_id
    pair("MAX_ENTITIES", limits.MAX_ENTITIES, entities)
    pair("MAX_PACKAGE_BYTES", limits.MAX_PACKAGE_BYTES,
         lambda size: len(canonical_json("x" * (size - 2))))
    work_pair("max_evaluations", 1,
         lambda size: evaluate(env, Top(), model, trace=False, max_evaluations=size))
    work_pair("max_trace_nodes", 1,
         lambda size: evaluate(env, Top(), model, trace=True, max_trace_nodes=size))
    pair("shared_countermodel_evaluations", 2,
         lambda size: check_countermodel(env, (Top(), Top()), Bottom(), model, max_evaluations=size))
    pair("max_models", 0,
         lambda size: find_countermodel(env, (), Bottom(), max_domain_size=1, max_models=size))
    proof = prove_entailment(env, (), Top(), max_steps=100)
    exact = check_entailment_certificate(env, (), Top(), proof.certificate, max_steps=100).steps
    rows["tableau_max_steps"] = {"cap": exact,
        "at": outcome(lambda: check_entailment_certificate(env, (), Top(), proof.certificate, max_steps=exact)),
        "under": outcome(lambda: check_entailment_certificate(env, (), Top(), proof.certificate, max_steps=exact - 1))}
    return rows


def feature_baselines():
    rows = {}
    for family in FAMILIES:
        env = Environment(raw_environment(family))
        top = Top()
        leaf = {"label": "open:assumption", "ast": formula_to_data(env, top)}
        lemma = {"name": "first", "environment_id": env.environment_id,
                 "premises": [leaf], "cites": [], "conclusion": formula_to_data(env, top),
                 "meaning_id": meaning_id(env, top), "reading_choices": {},
                 "transitive_leaves": [leaf],
                 "certificate": prove_entailment(env, (top,), top).certificate}
        key = "+".join(family) or "fol"
        rows[f"bundle_nonempty:{key}"] = outcome(lambda: check_bundle({"version": "ve-bundle@0",
            "environment": env.to_dict(), "lemmas": [lemma]}))
    for layers in (("norms@0", "definitions@0"), ("norms@0", "data@0"),
                   ("norms@0", "definitions@0", "data@0")):
        env = Environment(raw_environment(layers))
        rows[f"norms_layers:{'+'.join(layers)}"] = outcome(
            lambda: check_conflict(NormDocument(env, []), prove=True))
    return rows


def generate():
    rows = []
    for family in FAMILIES:
        for mask in itertools.product((False, True), repeat=len(LAYERS)):
            profiles = tuple(x for x, active in zip(LAYERS, mask) if active) + family
            profile_names = sorted((*profiles, "relational-fol@0"))
            try:
                env = Environment(raw_environment(profiles))
                model = FiniteModel.from_dict(env, model_wire(env))
            except UnsupportedProfile as exc:
                for name in OPERATIONS:
                    for kind in cases_for(name):
                        rows.append({"profiles": profile_names, "operation": name,
                                     "input_class": kind, "cell": "U", "status": exc.code,
                                     "output": exc.to_dict()})
                continue
            for name in OPERATIONS:
                for kind in cases_for(name):
                    try:
                        call = operation(name, kind, env, model)
                        result = outcome(call)
                    except UnsupportedProfile as exc:
                        result = {"cell": "U", "status": exc.code, "output": exc.to_dict()}
                    rows.append({"profiles": profile_names, "operation": name,
                                 "input_class": kind, **result})
    # The three frozen language envelopes predate ve.core@0.2.
    from ve.environment import (LANGUAGE, PROFILE, SPEC_REVISION as V0_REV,
        CLOSURE_LANGUAGE, CLOSURE_PROFILES, CLOSURE_REVISION, ORDER_PROFILES, ORDER_REVISION)
    for language, profiles, revision in ((LANGUAGE, (PROFILE,), V0_REV),
                                          (CLOSURE_LANGUAGE, CLOSURE_PROFILES, CLOSURE_REVISION),
                                          (CLOSURE_LANGUAGE, ORDER_PROFILES, ORDER_REVISION)):
        raw = raw_environment(())
        raw.update(language=language, spec_revision=revision)
        raw.pop("profiles")
        raw["profile"] = PROFILE
        if language == CLOSURE_LANGUAGE:
            raw.pop("profile")
            raw["profiles"] = list(profiles)
        env = Environment(raw)
        model = FiniteModel.from_dict(env, model_wire(env))
        for name in OPERATIONS:
            for kind in cases_for(name):
                try:
                    result = outcome(operation(name, kind, env, model))
                except UnsupportedProfile as exc:
                    result = {"cell": "U", "status": exc.code, "output": exc.to_dict()}
                rows.append({"language": language, "profiles": list(profiles), "operation": name,
                             "input_class": kind, **result})
        english = render(Document((Top(),)), env, "ve_english")
        for kind in INPUT_CLASSES:
            source = "broken.\n" if kind == "rejection" else "x" * (limits.MAX_SOURCE_BYTES + 1) if kind == "budget" else english
            result = outcome(lambda: document_to_data(env, parse_english(env, source)))
            rows.append({"language": language, "profiles": [*profiles, "english-surface"],
                         "operation": "parse_accept", "input_class": kind, **result})
    source_commit = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", "tests/probe_matrix.py"], cwd=ROOT, text=True).strip()
    return {"schema": "ve-stage0-baseline@1", "source_commit": source_commit,
            "python": sys.version.split()[0], "cells": rows, "graph_probes": graph_baselines(),
            "budget_boundaries": boundary_baselines(), "feature_probes": feature_baselines()}


def render_matrix(data):
    counts = {}
    for row in data["cells"]:
        key = (row["operation"], row["input_class"], row["cell"], row["status"])
        counts[key] = counts.get(key, 0) + 1
    lines = ["# Stage 0 semantics support matrix", "", "Generated by `uv run python tests/probe_matrix.py --write`.",
        f"Generator commit: `{data['source_commit']}`. Profile envelopes: {len({(r.get('language', 've.core@0.2'), tuple(r['profiles'])) for r in data['cells']})}; cells: {len(data['cells'])}.",
        "Complete Python outputs and diagnostics are in `conformance/baseline-2026-09/python.json`; case inputs are constructed by the pinned generator.",
        "Input classes are emitted where the operation exposes that kind of input or budget; structural cap boundaries are listed separately below.",
        "S means a returned verdict, R an exception or rejection, U an `UnsupportedProfile` exception. Returned diagnostic statuses remain S with their exact status recorded.",
        "", "| Operation | Input class | Python cell/status | Profiles |", "|---|---|---|---:|"]
    lines += [f"| `{op}` | {kind} | {cell}: `{status}` | {count} |"
              for (op, kind, cell, status), count in sorted(counts.items())]
    lines += ["", "## Graph compatibility probes", "",
        "The baseline stores source bytes, submitted identities, declaration and edge order, complete checking records, ordered assumption aliases and IDs, supporting edge IDs, diagnostics, and Background assumptions.",
        "", "| Probe | Status | Composed | Ordered leaves | Unresolved |", "|---|---|:---:|---|---|"]
    for name, record in data["graph_probes"].items():
        out = record["output"]
        lines.append(f"| `{name}` | `{out['status']}` | {out['composed']} | `{out['remaining_assumptions']}` | `{out['unresolved_obligations']}` |")
    lines += ["", "## Boundary probes", "",
        "Each row records the exact cap and first over-cap input, or the exact work required and one fewer for tableau replay.",
        "", "| Limit | Cap | At | Over / under |", "|---|---:|---|---|"]
    for name, pair in data["budget_boundaries"].items():
        other = pair.get("over", pair.get("under"))
        lines.append(f"| `{name}` | {pair['cap']} | `{pair['at']['status']}` | `{other['status']}` |")
    lines += ["", "## Compatibility findings", "",
        "- A nonempty lemma bundle is `Checked` by Python on closure, closure+nary, order and FOL profiles. The plan's closure-bundle Lean gap is therefore a Stage 2 coverage task.",
        "- Python accepts norms with definitions and data flags, including both together; Lean's documented norms route gate must be closed before authority switches for those cells.",
        "- Sixteen ve.core@0.2 profile envelopes combining order and definitions fail during environment construction. They are U for all operations; `profiles.checker_family` alone does not describe this gate.",
        "", "| Feature probe | Cell/status |", "|---|---|"]
    for name, result in data["feature_probes"].items():
        lines.append(f"| `{name}` | {result['cell']}: `{result['status']}` |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    data = generate()
    payload = json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
    report = render_matrix(data)
    baseline = OUT / "python.json"
    matrix = ROOT / "docs/spec/semantics-support-matrix.md"
    if args.write:
        OUT.mkdir(parents=True, exist_ok=True)
        baseline.write_text(payload)
        matrix.write_text(report)
    else:
        assert baseline.read_text() == payload, "baseline changed; rerun --write and review"
        assert matrix.read_text() == report, "support matrix changed; rerun --write and review"


def test_amended_graph_baselines():
    rows = graph_baselines()
    def record(name):
        return rows[name]["output"]
    assert record("reordered_declarations")["composed"]
    assert record("shared_leaf")["remaining_assumptions"] == ["a"]
    aliases = record("equal_id_aliases")
    assert aliases["remaining_assumptions"] == ["alias_a", "alias_b"]
    assert len(set(aliases["composition"]["assumption_claim_ids"])) == 1
    assert record("incomplete_graph")["unresolved_obligations"] == ["b", "root"]
    assert record("disconnected_unproved")["composed"]
    assert record("disconnected_invalid_certificate")["status"] == "InvalidInput"
    background_row = record("background_dependent_certificate")
    assert background_row["composed"] and any(a["label"].startswith("background:")
                                                  for a in background_row["composition"]["assumptions"])


if __name__ == "__main__":
    main()
