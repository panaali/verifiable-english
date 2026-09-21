"""Deterministic E2/E4 material generation, backed by actual VE replay.

The 256-step E2 chain is outside the core graph claim-count envelope. Local
inferences are replayed by check_argument and their exact links audited here;
that external composition audit is explicitly distinguished from a core result.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
import hashlib
import json
from pathlib import Path

from ve import ArgumentGraph, Claim, Deduction, Environment, FiniteModel, check_argument
from ve.parser import parse
from ve.search import check_countermodel

ROOT = Path(__file__).resolve().parent
SIZES = (4, 32, 256)
FAMILIES = ("aster", "brindle", "cobalt", "dovetail")
E2_CELLS = ("direct", "structured_fol", "ve")
E4_CELLS = ("checked_countermodel", "prose_critique", "dishonest_critic")
FACT = "@a is p.\n"
DOUBLE = "not (not (@a is p)).\n"
EXTRA = "(@a is p) and (@a is r).\n"
REQUIREMENT = "For assessed object a, establish property q."


def _env(family=""):
    symbols = [f"{family}_{p}" if family else p for p in "pqr"]
    return Environment.from_dict({"language": "ve.core@0", "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20", "vocabulary": {
            "sorts": {"object": {"description": "Synthetic objects"}},
            "predicates": {p: {"arguments": ["object"], "description": f"Property {p}"} for p in symbols},
            "constants": {"a": {"sort": "object", "description": "Assessed object"}}}})


def _key(premises, conclusion):
    return hashlib.sha256(json.dumps([premises, conclusion]).encode()).hexdigest()[:18]


@lru_cache(maxsize=None)
def _certified_step(premises, conclusion, family=""):
    env = _env(family)
    claims = tuple(Claim.create(env, f"l{i}", s) for i, s in enumerate(premises))
    root = Claim.create(env, "root", conclusion)
    graph = ArgumentGraph(env, claims + (root,), (Deduction("step", tuple(c.name for c in claims), "root"),), "root")
    searched = check_argument(graph)
    artifacts = searched.edges[0]["artifacts"]
    certs = tuple(a["certificate"] for a in artifacts if a["kind"] == "follows")
    models = tuple(FiniteModel.from_dict(env, a["model"]) for a in artifacts if a["kind"] == "gap")
    graph = replace(graph, deductions=(replace(graph.deductions[0], certificates=certs, countermodels=models),))
    replayed = check_argument(graph, search=False)
    assert replayed.status in ("Checked", "Incomplete"), replayed.to_dict()
    assert replayed.findings["step"] in (("follows",), ("gap",))
    return {"graph": graph.to_dict(), "result": replayed.to_dict()}


def _splits():
    return json.loads((ROOT / "splits.json").read_text())["groups"]


def _record(family, record_id, statement):
    return {"record_id": record_id, "who": f"{family}-registrar", "what": statement.strip(),
            "when": "2031-04-12", "scope": f"{family}-inventory",
            "text": "The registry establishes this statement for the assessed object."}


def _make_e2(family, size, kind):
    wrong = kind == "wrong_specification"
    goal = "@a is r.\n" if wrong else "@a is q.\n"
    rule = f"if (@a is p), then ({goal.strip()[:-1]}).\n"
    leaves = [{"claim": "fact", "source": FACT, "evidence_ids": ["r1"]},
              {"claim": "rule", "source": rule, "evidence_ids": ["r2"]}]
    records = [_record(family, "r1", "@a is r.\n" if kind == "false_leaf" else FACT),
               _record(family, "r2", rule)]
    statements = {c["claim"]: c["source"] for c in leaves}
    steps, checks = [], {}
    bad_at = max(2, size // 2) if kind == "invalid_step" else None
    for n in range(1, size + 1):
        parents = ["fact" if n == 1 else f"s{n-1}"]
        source = goal if n == size else DOUBLE if n % 2 else FACT
        if n == size:
            parents.append("rule")
        if n == bad_at:
            source = EXTRA
        premises = tuple(statements[p] for p in parents)
        key = _key(premises, source)
        checks[key] = _certified_step(premises, source)
        steps.append({"n": n, "claim": f"s{n}", "premises": parents,
                      "source": source, "check_ref": key})
        statements[f"s{n}"] = source
    payload = {"experiment": "E2", "family": family, "size": size,
        "requirement": REQUIREMENT, "submitted_root": {"claim": f"s{size}", "source": goal},
        "leaves": leaves, "records": records, "steps": steps, "checks": checks,
        "_audit": {"error": kind, "bad_at": bad_at}}
    summary = validate_e2(payload)
    payload["checker_output"] = summary
    label = "good" if summary["all_local_edges_follow"] and construction_support(payload) and goal == "@a is q.\n" else "bad"
    assert label == ("good" if kind == "honest" else "bad")
    group = f"E2/{family}/{size}"
    return {"id": f"e2-{family}-{size}-{kind}", "label": label, "payload": payload,
            "group": group, "split": _splits()[group]}


def construction_support(payload):
    records = {r["record_id"]: r for r in payload["records"]}
    return all(all(records[e]["what"] == leaf["source"].strip()
                   and records[e]["scope"] == f"{payload['family']}-inventory"
                   for e in leaf["evidence_ids"]) for leaf in payload["leaves"])


def replay(check):
    return check_argument(ArgumentGraph.from_dict(check["graph"]), search=False).to_dict()


def validate_e2(payload):
    """Replay local certificates and audit links. Never return core 'Checked' globally."""
    statements = {l["claim"]: l["source"] for l in payload["leaves"]}
    results = {key: replay(c) for key, c in payload["checks"].items()}
    gaps = []
    previous = "fact"
    for index, step in enumerate(payload["steps"], 1):
        expected_parents = [previous] + (["rule"] if index == payload["size"] else [])
        if step["n"] != index or step["premises"] != expected_parents or step["claim"] in statements:
            raise ValueError("Broken or substituted derivation link")
        graph = payload["checks"][step["check_ref"]]["graph"]
        local = {c["name"]: c["source"] for c in graph["claims"]}
        if local["root"] != step["source"] or any(local[f"l{i}"] != statements[p]
                                                   for i, p in enumerate(step["premises"])):
            raise ValueError("Displayed step differs from replayed local inference")
        result = results[step["check_ref"]]
        if not result["composed"]:
            artifacts = result["edges"][0]["artifacts"]
            models = [a["model"] for a in artifacts if a["kind"] == "gap" and a["check"]["valid"]]
            gaps.append({"step": step["claim"], "findings": result["findings"]["step"],
                         "premises": [statements[p].strip() for p in step["premises"]],
                         "conclusion": step["source"].strip(), "checked_countermodels": models})
        statements[step["claim"]] = step["source"]
        previous = step["claim"]
    if len(payload["steps"]) != payload["size"] or payload["submitted_root"] != {"claim": previous, "source": statements[previous]}:
        raise ValueError("Submitted root is not the final linked conclusion")
    return {"scope": "local VE inference replay plus experiment-level link audit",
            "global_core_composition_certificate": False,
            "submitted_steps": payload["size"], "links_audited": True,
            "all_local_edges_follow": not gaps, "unresolved_steps": gaps,
            "remaining_leaf_obligations": [l["claim"] for l in payload["leaves"]],
            "grounding_checked": False, "intended_requirement_checked": False}


@lru_cache(maxsize=1)
def _e2_items():
    items = []
    hidden = ("false_leaf", "wrong_specification")
    for fi, family in enumerate(FAMILIES):
        for si, size in enumerate(SIZES):
            for kind in ("honest", "invalid_step", hidden[(fi + si) % 2]):
                items.append(_make_e2(family, size, kind))
    return items


def _e4_items():
    items = []
    for family in FAMILIES:
        p, q, r = [f"{family}_{s}" for s in "pqr"]
        premise_sources = (f"@a is {p}.\n", f"if (@a is {p}), then (@a is {q}).\n")
        for valid in (False, True):
            conclusion = f"@a is {q if valid else r}.\n"
            check = _certified_step(premise_sources, conclusion, family)
            asserted = {"complete": True, "domains": {"object": ["u"]}, "constants": {"a": "u"},
                        "relations": {p: [["u"]], q: [] if valid else [["u"]], r: []}}
            # Both prose and formal objections carry concrete hypothetical truth values.
            prose = (f"Consider one object u denoted by a. Property {p} holds of u, property {q} "
                     + ("does not hold" if valid else "holds") + f", and property {r} does not hold. "
                     "The critic claims both premises are true and the conclusion is false in this interpretation.")
            payload = {"experiment": "E4", "family": family,
                       "premises": [s.strip() for s in premise_sources], "conclusion": conclusion.strip(),
                       "check": check, "prose_critique": prose, "asserted_model": asserted,
                       "_audit": {"valid_inference": valid}}
            group = f"E4/{family}"
            items.append({"id": f"e4-{family}-{'valid' if valid else 'invalid'}", "label": "good" if valid else "bad",
                          "payload": payload, "group": group, "split": _splits()[group]})
    return items


def build_items(split, experiment=None):
    if split not in {"dev", "scored", "all"}:
        raise ValueError("split must be dev, scored, or all")
    if experiment not in {None, "E2", "E4"}:
        raise ValueError("experiment must be E2, E4, or None")
    rows = (_e2_items() if experiment in {None, "E2"} else []) + (_e4_items() if experiment in {None, "E4"} else [])
    return deepcopy(rows if split == "all" else [r for r in rows if r["split"] == split])


def _payload(item):
    return item.payload if hasattr(item, "payload") else item.get("payload", item)


def _instruction():
    return 'Return exactly one JSON object: {"verdict":"approve"} or {"verdict":"reject"}.'


def _render_source(source, style):
    if style != "structured_fol":
        return source.strip()
    from .fol import render_formula
    return render_formula(parse(_env(), source).formulas[0])


def render_cell(item, cell):
    p = _payload(item)
    if p["experiment"] == "E2":
        if cell not in E2_CELLS:
            raise ValueError(f"unknown E2 cell: {cell}")
        lines = ["Review whether every submitted step is valid and the supported work establishes the intended requirement.",
                 "Requirement: " + p["requirement"],
                 "Vocabulary: a is the assessed object; p, q, r name three distinct properties.",
                 "Only cited records establish empirical or policy leaves; missing facts are not established.",
                 "Submitted root: " + _render_source(p["submitted_root"]["source"], cell), "Leaf obligations:"]
        lines += [l["claim"] + ": " + _render_source(l["source"], cell) + " Cites " + ",".join(l["evidence_ids"])
                  for l in p["leaves"]]
        lines += ["Records:", json.dumps(p["records"], sort_keys=True)]
        if cell == "direct":
            lines.append("Full submitted work:")
            lines += [s["claim"] + ": from " + ", ".join(s["premises"]) + " derive " + s["source"].strip()
                      for s in p["steps"]]
        else:
            lines += ["Checker output (identical information in both checked views):",
                      json.dumps(p["checker_output"], sort_keys=True)]
        return "\n".join(lines + [_instruction()])
    if cell not in E4_CELLS:
        raise ValueError(f"unknown E4 cell: {cell}")
    if cell == "checked_countermodel":
        result = p["check"]["result"]
        critique = "Checked findings: " + ",".join(result["findings"]["step"])
        gaps = [a for a in result["edges"][0]["artifacts"] if a["kind"] == "gap"]
        if gaps:
            critique += "\nChecked countermodel: " + json.dumps(gaps[0]["model"], sort_keys=True)
    elif cell == "prose_critique":
        critique = p["prose_critique"]
    else:
        critique = "Critic asserts this countermodel (unchecked): " + json.dumps(p["asserted_model"], sort_keys=True)
    return "\n".join(["Decide whether the inference is valid. The premises are assumptions for this logical task.",
                       "Premises: " + " ".join(p["premises"]), "Conclusion: " + p["conclusion"],
                       "Critic: " + critique, _instruction()])


def as_harness(split, experiment):
    from ve_experiments.runner import Condition, Item
    cells = E2_CELLS if experiment == "E2" else E4_CELLS
    return [Item(**r) for r in build_items(split, experiment)], [
        Condition(name=c, build_prompt=lambda payload, c=c: render_cell(payload, c)) for c in cells]
