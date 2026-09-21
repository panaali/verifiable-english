"""Eight scored inference-shape clusters; fresh vocabulary; growing obligations."""
from copy import deepcopy
from functools import lru_cache
import hashlib
import json
import random

from ve import ast, Environment
from ve.parser import parse
from .common import certified_step, fresh, source, replay, instruction, environment
from .fol import render_formula

SIZES = (4, 32, 256)
CELLS = ("direct", "structured_fol", "ve")
# Each pair is (faithful base, strict strengthening). All invalid intermediate
# steps have precisely the SAME symbol and connective inventory as valid ones.
SHAPES = {
    "nested_or": ("p | (q & r)", "p & (q | r)"),
    "mixed_clauses": ("(p | (q & r)) & (s | t)", "(p & (q | r)) & (s | t)"),
    "outer_disjunction": ("(p | q) | (r & s)", "(p | q) & (r | s)"),
    "two_conjunctions": ("(p & q) | (r & s)", "(p | q) & (r & s)"),
    "disjunct_extension": ("(p | (q & r)) | s", "(p & (q | r)) | s"),
    "conjunct_extension": ("(p | (q & r)) & s", "(p & (q | r)) & s"),
    "parallel_conjuncts": ("(p | (q & r)) & (s | (t & u))", "(p & (q | r)) & (s & (t | u))"),
    "parallel_disjuncts": ("(p | (q & r)) | (s | (t & u))", "(p & (q | r)) | (s & (t | u))"),
    "dev_nested": ("p | (q & (r & s))", "p & (q | (r & s))"),
    "dev_guarded": ("t & (p | (q & r))", "t & (p & (q | r))"),
    "dev_repeated": ("(p | (q & r)) | (p & s)", "(p & (q | r)) | (p & s)"),
    "dev_deep": ("p | (q & (r | s))", "p & (q | (r | s))"),
}
VOCABS = {"dev_aster": "dev", "dev_brindle": "dev", "score_cobalt": "scored", "score_dovetail": "scored"}


def shape_tree(expression, symbols):
    # Parse this tiny INTERNAL construction DSL; no eval of data or prompts.
    import ast as pyast
    def convert(node):
        if isinstance(node, pyast.Name):
            return ast.Unary(symbols[node.id], ast.Const("a"))
        if isinstance(node, pyast.BinOp) and isinstance(node.op, (pyast.BitAnd, pyast.BitOr)):
            return (ast.And if isinstance(node.op, pyast.BitAnd) else ast.Or)(convert(node.left), convert(node.right))
        raise ValueError("Invalid construction expression")
    return convert(pyast.parse(expression, mode="eval").body)


def commute(node):
    if isinstance(node, (ast.And, ast.Or)):
        return type(node)(commute(node.right), commute(node.left))
    return node


def record(family, rid, statement):
    return {"record_id": rid, "who": f"{family}-registrar", "what": statement.strip(),
            "when": "2031-04-12", "scope": f"{family}-inventory"}


def construction_support(payload):
    records = {r["record_id"]: r for r in payload["records"]}
    return all(all(records[e]["what"] == leaf["source"].strip()
                   and records[e]["scope"] == f"{payload['family']}-inventory"
                   for e in leaf["evidence_ids"]) for leaf in payload["leaves"])


def key(premises, conclusion):
    return hashlib.sha256(json.dumps([premises, conclusion]).encode()).hexdigest()[:18]


def make_item(template, family, size, kind, workload):
    symbols = {s: fresh(family, s) for s in "pqrstughv"}
    base, stronger = [shape_tree(s, symbols) for s in SHAPES[template]]
    wrong = kind == "wrong_specification"
    goal = source(ast.Unary(symbols["h" if wrong else "g"], ast.Const("a")))
    intended = source(ast.Unary(symbols["g"], ast.Const("a")))
    rule = source(ast.Implies(base, ast.Unary(symbols["h" if wrong else "g"], ast.Const("a"))))
    leaves = [{"claim": "fact", "source": source(base), "evidence_ids": ["r000"]},
              {"claim": "rule", "source": rule, "evidence_ids": ["r001"]}]
    records = [record(family, "r000", source(base)), record(family, "r001", rule)]
    statements = {c["claim"]: c["source"] for c in leaves}
    rng = random.Random(f"5204/{template}/{family}/{size}/{workload}")
    bad_at = rng.randint(1, size-1) if kind == "invalid_step" else None
    steps, checks = [], {}
    for n in range(1, size + 1):
        parents = ["fact" if n == 1 else f"s{n-1}"]
        if n == size:
            parents.append("rule")
            statement = goal
        else:
            form = stronger if n == bad_at else base
            if n % 2:
                form = commute(form)
            if workload == "growing":
                # New empirical fact is required for this intermediate claim.
                # Constants denote different named work units (not assumed unequal).
                side = ast.Unary(symbols["v"], ast.Const(f"unit{n:03}"))
                claim, rid = f"audit{n:03}", f"r{n+1:03}"
                leaf = {"claim": claim, "source": source(side), "evidence_ids": [rid]}
                leaves.append(leaf)
                records.append(record(family, rid, leaf["source"]))
                statements[claim] = leaf["source"]
                parents.append(claim)
                form = ast.And(form, side)
            statement = source(form)
        premises = tuple(statements[p] for p in parents)
        ref = key(premises, statement)
        checks[ref] = certified_step(premises, statement, family)
        steps.append({"n": n, "claim": f"s{n}", "premises": parents, "source": statement, "check_ref": ref})
        statements[f"s{n}"] = statement
    if kind == "false_leaf":
        victim = rng.randrange(len(records))
        records[victim]["what"] = source(ast.Unary(symbols["h"], ast.Const("a"))).strip()
    env = environment(family, tuple(statements.values()) + (intended,) + tuple(source(ast.Unary(p, ast.Const("a"))) for p in symbols.values()))
    payload = {"experiment": "E2", "family": family, "template": template, "size": size, "workload": workload,
        "environment": env.to_dict(), "requirement": f"For assessed object a, establish property {symbols['g']}.",
        "intended_source": intended, "submitted_root": {"claim": f"s{size}", "source": goal},
        "leaves": leaves, "records": records, "steps": steps, "checks": checks,
        "_audit": {"error": kind, "bad_at": bad_at, "template": template, "vocabulary_family": family,
                   "workload": workload, "checker_visibility": "visible" if kind == "invalid_step" else "invisible" if kind != "honest" else "honest"}}
    payload["checker_output"] = validate(payload)
    label = "good" if payload["checker_output"]["all_local_edges_follow"] and construction_support(payload) and goal == intended else "bad"
    assert label == ("good" if kind == "honest" else "bad")
    return {"id": "e2-" + hashlib.sha256(f"{template}/{family}/{size}/{kind}/{workload}".encode()).hexdigest()[:18],
            "label": label, "payload": payload, "group": f"E2/{template}/{family}", "split": VOCABS[family]}


def validate(payload):
    statements = {l["claim"]: l["source"] for l in payload["leaves"]}
    # Parse EVERY stored artifact, even ones with a cached result; mutation tests
    # ensure displayed links, sources and certificates cannot be substituted.
    results = {key: replay(c) for key, c in payload["checks"].items()}
    gaps, previous = [], "fact"
    for index, step in enumerate(payload["steps"], 1):
        expected = [previous] + (["rule"] if index == payload["size"] else
                   [f"audit{index:03}"] if payload["workload"] == "growing" else [])
        if step["n"] != index or step["premises"] != expected or step["claim"] in statements:
            raise ValueError("Broken or substituted derivation link")
        graph = payload["checks"][step["check_ref"]]["graph"]
        local = {c["name"]: c["source"] for c in graph["claims"]}
        if local["root"] != step["source"] or any(local[f"l{i}"] != statements[p] for i, p in enumerate(step["premises"])):
            raise ValueError("Displayed step differs from replayed local inference")
        result = results[step["check_ref"]]
        if not result["composed"]:
            artifacts = result["edges"][0]["artifacts"]
            gaps.append({"step": step["claim"], "findings": result["findings"]["step"],
                         "premises": [statements[p].strip() for p in step["premises"]],
                         "conclusion": step["source"].strip(),
                         "checked_countermodels": [a["model"] for a in artifacts if a["kind"] == "gap" and a["check"]["valid"]]})
        statements[step["claim"]] = step["source"]
        previous = step["claim"]
    if len(payload["steps"]) != payload["size"] or payload["submitted_root"] != {"claim": previous, "source": statements[previous]}:
        raise ValueError("Submitted root is not the final linked conclusion")
    return {"scope": "local VE inference replay plus experiment-level link audit", "global_core_composition_certificate": False,
        "submitted_steps": payload["size"], "links_audited": True, "all_local_edges_follow": not gaps,
        "unresolved_steps": gaps, "remaining_leaf_obligations": [{"claim": l["claim"], "source": l["source"].strip(),
            "evidence_ids": l["evidence_ids"]} for l in payload["leaves"]],
        "grounding_checked": False, "intended_requirement_checked": False}


@lru_cache(maxsize=1)
def items():
    result = []
    for template in SHAPES:
        for vi, (family, split) in enumerate(VOCABS.items()):
            if template.startswith("dev_") != (split == "dev"):
                continue
            for si, size in enumerate(SIZES):
                for wi, workload in enumerate(("fixed", "growing")):
                    hidden = ("false_leaf", "wrong_specification")[(vi + si + wi) % 2]
                    for kind in ("honest", "invalid_step", hidden):
                        result.append(make_item(template, family, size, kind, workload))
        print(f"E2 certified template {template}", flush=True)
    return sorted(result, key=lambda r: r["id"])


def render(payload, cell):
    if cell not in CELLS:
        raise ValueError(cell)
    env = Environment.from_dict(payload["environment"])
    def displayed(s):
        return render_formula(parse(env, s.rstrip() + ("" if s.rstrip().endswith(".") else ".") + "\n").formulas[0]) if cell == "structured_fol" else s.strip()
    p = payload
    lines = ["Review whether every submitted step is valid and the supported work establishes the intended requirement.",
             "Requirement: " + p["requirement"], "Vocabulary: " + ", ".join(sorted(env.predicates)) + "; these are distinct properties.",
             "Only cited records establish leaves; missing facts are not established. Every submitted intermediate claim also requires support.",
             "Submitted root: " + displayed(p["submitted_root"]["source"]), "Leaf obligations:"]
    lines += [l["claim"] + ": " + displayed(l["source"]) + " Cites " + ",".join(l["evidence_ids"]) for l in p["leaves"]]
    records = [{**r, "what": displayed(r["what"])} for r in p["records"]]
    lines += ["Records:", json.dumps(records, sort_keys=True)]
    if cell == "direct":
        lines.append("Full submitted work:")
        lines += [s["claim"] + ": from " + ", ".join(s["premises"]) + " derive " + s["source"].strip() for s in p["steps"]]
    else:
        report = deepcopy(p["checker_output"])
        for leaf in report["remaining_leaf_obligations"]:
            leaf["source"] = displayed(leaf["source"])
        for gap in report["unresolved_steps"]:
            gap["premises"] = [displayed(s) for s in gap["premises"]]
            gap["conclusion"] = displayed(gap["conclusion"])
        lines += ["Checker output (same findings and obligations in both checked views):", json.dumps(report, sort_keys=True)]
    return "\n".join(lines + [instruction()])
