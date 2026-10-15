"""Batch 14b corpus: norm documents with non-first-order guards on the closure, core and order families.

    uv run python docs/lean-first/b14b/corpus.py --record OUT.json [--seed N] [--count N]

Each record is one public operation on one generated document (`NormDocument.premises`, the norms
certificate check, `check_conflict` with proof search, with no packages, with no evidence and with
finite witness models), with the answer or the raised diagnostic. No such document is in the
stage-0 probe matrix or the conformance corpus (docs/spec/stage2-progress.md, "Scope gaps"), so
this corpus is the batch's A/B: `--record` runs at the base commit (the retained Python fallback)
and at the head (Lean's `family-norms` mode), and `compare.py` reads both files.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from ve.ast import (And, Atom, Binary, Body, Const, Exists, Forall, Implies, Le, Lt, Add, Named,  # noqa: E402
                    Not, Num, Or, Reach, Scale, Top, Unary, Var, _to_data)
from ve.environment import Environment  # noqa: E402
from ve.errors import VEError  # noqa: E402
from ve.norms import (Norm, NormDocument, check_conflict, check_norm_entailment_certificate,  # noqa: E402
                      prove_norm_entailment)
from ve.profiles import LANGUAGE, SPEC_REVISION  # noqa: E402

FAMILIES = {"closure": ("closure@0",), "core": ("closure@0", "nary@0"), "order": ("order@0",)}


def environment(family, allow, definitions):
    reg = {"role": "obligation", "default": "allow" if allow else "deny", "act": "{0} be done",
           "permission": "permitted"}
    predicates = {
        "required": {"arguments": ["act"], "description": "required", "regulated": reg},
        "permitted": {"arguments": ["act"], "description": "permitted",
                      "regulated": {"role": "permission", "default": "deny", "act": "{0} be done"}},
        "reviewed": {"arguments": ["act", "party"], "description": "reviewed",
                     "regulated": {"role": "plain", "default": "allow"}},
        "before": {"arguments": ["act", "act"], "description": "before"},
        "urgent": {"arguments": ["act"], "description": "urgent"},
        "owner": {"arguments": ["act", "party"], "description": "owner"},
    }
    constants = {}
    profiles = {"norms@0", "relational-fol@0", *FAMILIES[family]}
    if family == "core":
        predicates["tri"] = {"arguments": ["act", "act", "party"], "description": "tri"}
    if family == "order":
        predicates["cost"] = {"arguments": ["act", "$int"], "description": "cost"}
        constants["budget"] = {"sort": "$int", "description": "budget"}
    if definitions and family != "order":
        profiles.add("definitions@0")
        predicates["pressing"] = {"arguments": ["act"], "description": "pressing",
                                  "defined": {"arguments": ["act"], "body": ["unary", "urgent", ["var", 0]]}}
    return Environment({"language": LANGUAGE, "profiles": sorted(profiles), "spec_revision": SPEC_REVISION,
                        "vocabulary": {"sorts": {"act": {"description": "act"}, "party": {"description": "party"}},
                                       "predicates": predicates, "constants": constants}})


def leaves(family, depth):
    """Non-first-order formulas over one act variable `depth` binders up (and FOL ones to mix in)."""
    x = Var(depth)
    fol = [Unary("urgent", x), Exists("party", Binary("owner", Var(depth + 1), Var(0)))]
    if family in ("closure", "core"):
        rich = [Reach("star", Named("before"), x, x),
                Reach("plus", Named("before"), x, x),
                Exists("act", Reach("plus", Named("before"), Var(depth + 1), Var(0))),
                Reach("plus", Body("act", And(Binary("before", Var(1), Var(0)), Unary("urgent", Var(0)))), x, x),
                Reach("star", Body("act", Binary("before", Var(depth + 2), Var(0))), x, x)]
        if family == "core":
            rich += [Exists("party", Atom("tri", (Var(depth + 1), Var(depth + 1), Var(0)))),
                     Exists("act", Exists("party", Atom("tri", (Var(depth + 2), Var(1), Var(0)))))]
    else:
        budget = Const("budget")
        rich = [Le(budget, Num(5)), Lt(Add(budget, Num(1)), Scale(2, budget)),
                And(Binary("cost", x, budget), Le(budget, Num(3))),
                Not(Lt(Scale(-1, budget), Num(-7)))]
    return fol, rich


def guard(rng, family, depth=0, lower=None):
    fol, rich = leaves(family, depth)
    parts = [rng.choice(rich)]
    if rng.random() < 0.5:
        parts.append(rng.choice(fol))
    if lower is not None and rng.random() < 0.7:
        # a lower regulated atom, bare or under a binder (the substitution under binders)
        parts.append(rng.choice([Unary(lower, Var(depth)),
                                 Exists("act", And(Binary("before", Var(depth + 1), Var(0)),
                                                   Unary(lower, Var(0)))),
                                 Forall("party", Implies(Binary("owner", Var(depth + 1), Var(0)),
                                                         Unary(lower, Var(depth + 1))))]))
    rng.shuffle(parts)
    result = parts[0]
    for part in parts[1:]:
        result = rng.choice([And, Or, Implies])(result, part)
    return result


def document(rng, family, env):
    rules = [Norm("may", "permitted", True, guard(rng, family)),
             Norm("may-not", "permitted", False, guard(rng, family), (guard(rng, family),), ("may",))
             if rng.random() < 0.5 else Norm("may-not", "permitted", False, guard(rng, family)),
             Norm("must", "required", True, guard(rng, family, lower="permitted"))]
    if rng.random() < 0.5:
        rules.append(Norm("need-not", "required", False, guard(rng, family), (), ("must",)))
    if rng.random() < 0.5:
        rules.append(Norm("check", "reviewed", True,
                          Exists("act", And(Binary("before", Var(2), Var(0)), guard(rng, family, 0)))
                          if family != "order" else And(Binary("owner", Var(1), Var(0)),
                                                        guard(rng, family, 1))))
    return NormDocument(env, rules)


def answer(fn):
    try:
        value = fn()
    except VEError as exc:
        return {"error": type(exc).__name__, "text": str(exc)}
    if hasattr(value, "_asdict"):
        value = value._asdict()
    elif hasattr(value, "__dataclass_fields__"):
        value = {k: getattr(value, k) for k in value.__dataclass_fields__}
    return {"ok": json.loads(json.dumps(value, default=list))}


def models(rng, env, n):
    acts, parties = ["a", "b"], ["p"]
    out = []
    for _ in range(n):
        relations = {"before": [[x, y] for x in acts for y in acts if rng.random() < 0.4],
                     "urgent": [[x] for x in acts if rng.random() < 0.5],
                     "owner": [[x, p] for x in acts for p in parties if rng.random() < 0.5]}
        if "tri" in env.predicates:
            relations["tri"] = [[x, y, p] for x in acts for y in acts for p in parties if rng.random() < 0.4]
        if "cost" in env.predicates:
            relations["cost"] = [[x, str(v)] for x in acts for v in (rng.choice([2, 3, 9]),)]
        constants = {"budget": str(rng.choice([2, 3, 9]))} if "budget" in env.constants else {}
        out.append({"complete": True, "domains": {"act": acts, "party": parties},
                    "constants": constants, "relations": relations})
    return out


def records(seed, count):
    rng = random.Random(seed)
    for index in range(count):
        family = list(FAMILIES)[index % 3]
        allow, definitions = rng.random() < 0.5, rng.random() < 0.3
        env = environment(family, allow, definitions)
        doc = document(rng, family, env)
        key = {"index": index, "family": family, "rules": [r.to_dict() for r in doc.rules],
               "allow": allow, "definitions": definitions}
        yield {**key, "op": "premises",
               "answer": answer(lambda: [[label, _to_data(f)] for label, f in doc.premises()])}
        proof = prove_norm_entailment(doc, (), Top(), max_steps=200)
        yield {**key, "op": "certificate",
               "answer": answer(lambda: check_norm_entailment_certificate(doc, (), Top(), proof.certificate))}
        yield {**key, "op": "certificate-stale",
               "answer": answer(lambda: check_norm_entailment_certificate(doc, (Top(),), Top(), proof.certificate))}
        yield {**key, "op": "conflict-prove", "answer": answer(lambda: check_conflict(doc, prove=True,
                                                                                     tableau_steps=300))}
        yield {**key, "op": "conflict-missing", "answer": answer(lambda: check_conflict(doc, certificates={}))}
        yield {**key, "op": "conflict-none", "answer": answer(lambda: check_conflict(doc))}
        for m, model in enumerate(models(rng, env, 3)):
            yield {**key, "op": f"conflict-model-{m}", "model": model,
                   "answer": answer(lambda: check_conflict(doc, model=model))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=14)
    parser.add_argument("--count", type=int, default=150)
    args = parser.parse_args()
    rows = list(records(args.seed, args.count))
    args.record.write_text(json.dumps({"seed": args.seed, "count": args.count, "records": rows},
                                      sort_keys=True) + "\n")
    print(f"{len(rows)} records -> {args.record}")


if __name__ == "__main__":
    main()
