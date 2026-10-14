"""DF-E3, POST HOC (not part of the pre-registered method): settle the undecided implication directions.

    uv run python research/defeasible/resolve_unknown_directions.py

The pre-registered method (docs/research/defeasible-phase1.md 1.5, step 4) can refute an implication only by a truth
table, so a direction between quantified guards without a tableau certificate stays unknown, and the pre-registered
verdict is the one `specificity_pairs.py` reports. This script, written after that run, searches small finite
countermodels for each unknown direction of a pair without written precedence: an assignment of the rule's arguments
and a finite model where the first guard holds and the second does not. Each countermodel found is then confirmed by
VE's own evaluator (`ve.evaluate.evaluate`) on the closed implication, which must be false. A direction with a
confirmed countermodel is "no"; otherwise it stays unknown.
"""
from __future__ import annotations

import json
import random
import re
import sys

from common import EVIDENCE, ROOT, write_json

sys.path.insert(0, str(ROOT))
import specificity_pairs as S  # noqa: E402
from ve.ast import formula_from_data  # noqa: E402
from ve.errors import VEError  # noqa: E402
from ve.evaluate import evaluate  # noqa: E402
from ve.model import FiniteModel  # noqa: E402

TRIALS = 20000
MAX_REFUSED = 200


def term(t, env_vars, model):
    if t[0] == "var":
        return env_vars[t[1]]
    if t[0] == "const":
        return model["constants"][t[1]]
    raise ValueError(f"term {t[0]}")


def holds(f, env_vars, model):
    head = f[0]
    if head == "top":
        return True
    if head == "bottom":
        return False
    if head == "and":
        return all(holds(x, env_vars, model) for x in f[1:])
    if head == "or":
        return any(holds(x, env_vars, model) for x in f[1:])
    if head == "not":
        return not holds(f[1], env_vars, model)
    if head == "implies":
        return (not holds(f[1], env_vars, model)) or holds(f[2], env_vars, model)
    if head == "iff":
        return holds(f[1], env_vars, model) == holds(f[2], env_vars, model)
    if head in ("forall", "exists"):
        values = (holds(f[2], [d, *env_vars], model) for d in model["domains"][f[1]])
        return all(values) if head == "forall" else any(values)
    if head == "unary":
        return (term(f[2], env_vars, model),) in model["relations"][f[1]]
    if head == "binary":
        return (term(f[2], env_vars, model), term(f[3], env_vars, model)) in model["relations"][f[1]]
    if head == "eq":
        return term(f[1], env_vars, model) == term(f[2], env_vars, model)
    raise ValueError(f"formula {head}")


def symbols(f, preds, consts):
    if not isinstance(f, list):
        return
    if f[0] in ("unary", "binary"):
        preds.add(f[1])
    if f[0] == "const":
        consts.add(f[1])
    for x in f[1:]:
        symbols(x, preds, consts)


def element(sort, i):
    return "e_" + re.sub(r"[^a-z0-9_]", "_", sort.lower()) + f"_{i}"


def search(g, h, env_data, predicate, rng):
    vocabulary = env_data["vocabulary"]
    base_preds = {n: d for n, d in vocabulary["predicates"].items() if "regulated" not in d}
    preds, consts = set(), set()
    symbols(g, preds, consts)
    symbols(h, preds, consts)
    arguments = vocabulary["predicates"][predicate]["arguments"]
    for _ in range(TRIALS):
        domains = {s: [element(s, i) for i in range(rng.randint(1, 3))] for s in vocabulary["sorts"]}
        for name, decl in vocabulary["constants"].items():
            domains.setdefault(decl["sort"], [element(decl["sort"], i) for i in range(rng.randint(1, 3))])
        model = {"domains": domains,
                 "constants": {c: rng.choice(domains[vocabulary["constants"][c]["sort"]]) for c in consts},
                 "relations": {}}
        for p in preds:
            sorts = base_preds[p]["arguments"]
            tuples = [()]
            for s in sorts:
                tuples = [(*t, d) for t in tuples for d in domains[s]]
            model["relations"][p] = {t for t in tuples if rng.random() < 0.5}
        env_vars = [rng.choice(domains[s]) for s in reversed(arguments)]
        if holds(g, env_vars, model) and not holds(h, env_vars, model):
            yield model, env_vars


def confirm(g, h, env_data, predicate, model, env_vars):
    """VE's evaluator on the implication closed by the countermodel's argument values, as constants."""
    base = S._BASE[json.dumps(env_data, sort_keys=True)]
    vocabulary = env_data["vocabulary"]
    base_preds = {n: d for n, d in vocabulary["predicates"].items() if "regulated" not in d}
    closed = ["implies", g, h]
    for sort in reversed(vocabulary["predicates"][predicate]["arguments"]):
        closed = ["forall", sort, closed]
    domains = {s: list(v) for s, v in model["domains"].items()}
    constants = {c: model["constants"].get(c, domains[d["sort"]][0]) for c, d in vocabulary["constants"].items()
                 if d["sort"] in domains}
    # Literal constants (sorts `$…`) name distinct elements: one element each.
    for sort in {d["sort"] for d in vocabulary["constants"].values() if d["sort"].startswith("$")}:
        names = sorted(c for c, d in vocabulary["constants"].items() if d["sort"] == sort)
        if any(c in model["constants"] for c in names):
            raise SystemExit("a guard names a literal constant; the search does not handle it")
        domains[sort] = [element(sort, i) for i in range(len(names))]
        constants.update({c: domains[sort][i] for i, c in enumerate(names)})
    relations = {p: sorted([list(t) for t in model["relations"].get(p, ())]) for p in base_preds}
    for p, decl in base_preds.items():
        # A functional, total predicate the guards do not mention is filled as a function (each first argument to
        # the first element of the last sort), so that the candidate keeps the environment's background premises.
        if decl.get("functional") and decl.get("total") and p not in model["relations"]:
            args = decl["arguments"]
            rows = [[]]
            for sort in args[:-1]:
                rows = [[*r, d] for r in rows for d in domains.setdefault(sort, [element(sort, 0)])]
            last = domains.setdefault(args[-1], [element(args[-1], 0)])
            relations[p] = sorted([*r, last[0]] for r in rows)
    wire = {"complete": True, "domains": domains, "constants": constants, "relations": relations}
    result = evaluate(base, formula_from_data(base, closed), FiniteModel.from_dict(base, wire))
    return {"value": result.value, "raw": repr(result)[:300]}


def main():
    data = json.loads((EVIDENCE / "specificity-pairs.json").read_text())
    envs = {}
    for corpus in S.corpora():
        envs.setdefault(corpus.name, corpus.env_data)
    rng = random.Random(20261014)
    out = []
    for row in data["pairs"]:
        if row["written_precedence_or_rank"] or "unknown" not in row["class"]:
            continue
        env_data = envs[row["corpus"]]
        a, b = row["rules"]
        S.implies(a["guard"], b["guard"], env_data, a["predicate"])  # builds the base environment
        resolved = {}
        for label, (g, h, pred), prior in (("a_implies_b", (a["guard"], b["guard"], a["predicate"]),
                                            row["a_implies_b"]),
                                           ("b_implies_a", (b["guard"], a["guard"], b["predicate"]),
                                            row["b_implies_a"])):
            if prior[0] != "unknown":
                resolved[label] = prior
                continue
            resolved[label] = ["unknown", "no countermodel in the search"]
            rejected = 0
            for model, env_vars in search(g, h, env_data, pred, rng):
                try:
                    checked = confirm(g, h, env_data, pred, model, env_vars)
                except VEError as exc:  # VE refuses the candidate (e.g. a background premise): keep searching
                    rejected += 1
                    resolved[label] = ["unknown", f"{rejected} candidates refused by VE, last: {exc}"[:200]]
                    if rejected >= MAX_REFUSED:
                        break
                    continue
                if checked.get("value") is not False:
                    resolved[label] = ["unknown", f"countermodel not confirmed: {json.dumps(checked)[:200]}"]
                    break
                resolved[label] = ["no", "finite countermodel, confirmed false by ve.evaluate"]
                resolved[label + "_countermodel"] = {
                    "domains": model["domains"], "constants": model["constants"],
                    "relations": {p: sorted(map(list, t)) for p, t in model["relations"].items()},
                    "arguments_innermost_first": env_vars, "candidates_refused_before": rejected}
                break
        cls = S.classify(False, tuple(resolved["a_implies_b"]), tuple(resolved["b_implies_a"]))
        out.append({"corpus": row["corpus"], "rules": [a["name"], b["name"]], "pre_registered_class": row["class"],
                    "post_hoc_class": cls, **resolved})
    summary = {}
    for r in out:
        summary[r["post_hoc_class"]] = summary.get(r["post_hoc_class"], 0) + 1
    write_json("specificity-unknown-resolved.json", {"post_hoc": True, "seed": 20261014, "trials": TRIALS,
                                                     "summary": summary, "pairs": out})
    print(json.dumps(summary, indent=1))
    for r in out:
        print(r["corpus"], r["rules"], r["post_hoc_class"])


if __name__ == "__main__":
    main()
