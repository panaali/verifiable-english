"""Shared offline proof/replay helpers; no experiment labels enter the checker."""
from dataclasses import replace, fields, is_dataclass
from functools import lru_cache
import hashlib
import re
import json
from copy import deepcopy

from ve import ArgumentGraph, Claim, Deduction, Environment, FiniteModel, check_argument
from ve.argument import deduction_identity
from ve.entailment import prove_entailment
from ve.search import find_countermodel
from ve import ast
from ve.printer import print_formula


def fresh(family, letter):
    raw = hashlib.sha256(f"{family}/{letter}".encode()).digest()
    return "".join("bcdfghjklmnprstvz"[raw[2*i] % 16] + "aeiou"[raw[2*i+1] % 5] for i in range(4))


def environment(family, sources, binary=()):
    predicates = set(re.findall(r"\bis (\w+)", " ".join(sources))) | set(binary)
    constants = set(re.findall(r"@(\w+)", " ".join(sources)))
    return Environment.from_dict({"language": "ve.core@0", "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20", "vocabulary": {
            "sorts": {"object": {"description": "Synthetic objects"}},
            "predicates": {p: {"arguments": ["object"] * (2 if p in binary else 1), "description": f"Property {p}"} for p in sorted(predicates)},
            "constants": {c: {"sort": "object", "description": f"Object {c}"} for c in sorted(constants)}}})


def ast_environment(nodes):
    predicates, constants = {}, set()
    def walk(node):
        if isinstance(node, ast.Unary): predicates[node.predicate] = 1
        if isinstance(node, ast.Binary): predicates[node.predicate] = 2
        if isinstance(node, ast.Const): constants.add(node.name)
        if is_dataclass(node):
            for f in fields(node): walk(getattr(node, f.name))
    for node in nodes: walk(node)
    return Environment.from_dict({"language": "ve.core@0", "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20", "vocabulary": {
        "sorts": {"object": {"description": "Synthetic objects"}},
        "predicates": {p: {"arguments": ["object"] * n, "description": f"Property {p}"} for p, n in sorted(predicates.items())},
        "constants": {c: {"sort": "object", "description": f"Object {c}"} for c in sorted(constants)}}})


def source(node):
    return print_formula(ast_environment((node,)), node) + ".\n"


def conjunct(nodes):
    nodes = tuple(nodes)
    result = nodes[0]
    for node in nodes[1:]:
        result = ast.And(result, node)
    return result


@lru_cache(maxsize=None)
def certified_step(premises, conclusion, family="", binary=()):
    env = environment(family, premises + (conclusion,), binary)
    claims = tuple(Claim.create(env, f"l{i}", s) for i, s in enumerate(premises))
    root = Claim.create(env, "root", conclusion)
    graph = ArgumentGraph(env, claims + (root,), (Deduction("step", tuple(c.name for c in claims), "root"),), "root")
    proof = prove_entailment(env, tuple(c.ast for c in claims), root.ast)
    if proof.status == "Found":
        certs = ({"edge_id": deduction_identity(graph, graph.deductions[0]), "direction": "follows", "proof": proof.certificate},)
        models = ()
    else:
        found = find_countermodel(env, tuple(c.ast for c in claims), root.ast, max_domain_size=1)
        assert found.model is not None, (premises, conclusion, found.status)
        certs, models = (), (found.model,)
    graph = replace(graph, deductions=(replace(graph.deductions[0], certificates=certs, countermodels=models),))
    result = check_argument(graph, search=False)
    assert result.findings["step"] in (("follows",), ("gap",)), result.to_dict()
    return {"graph": graph.to_dict(), "result": result.to_dict()}


@lru_cache(maxsize=30000)
def _replay_graph(serialized):
    return check_argument(ArgumentGraph.from_dict(json.loads(serialized)), search=False).to_dict()


def replay(check):
    return deepcopy(_replay_graph(json.dumps(check["graph"], sort_keys=True, separators=(",", ":"))))


def instruction():
    return 'Return exactly one JSON object: {"verdict":"approve"} or {"verdict":"reject"}.'
