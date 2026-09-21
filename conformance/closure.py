"""Deterministic closure fixtures; v0 fixture files are never regenerated here."""
from pathlib import Path
import json
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ve import *
from ve.environment import CLOSURE_LANGUAGE, CLOSURE_PROFILES, CLOSURE_REVISION


def environment(nonempty=True):
    return Environment({"language": CLOSURE_LANGUAGE, "profiles": list(CLOSURE_PROFILES),
        "spec_revision": CLOSURE_REVISION, "vocabulary": {
            "sorts": {"node": {"description": "A graph vertex.", "verbalisation": {"singular": "vertex", "plural": "vertices"}},
                      "other": {"description": "An independent possibly empty sort."}},
            "predicates": {"edge": {"arguments": ["node", "node"], "description": "One directed step from source to destination.", "verbalisation": "{0} reaches {1}"},
                           "marked": {"arguments": ["node"], "description": "A selected vertex."}},
            "constants": {name: {"sort": "node", "description": name} for name in ("start", "end") if nonempty}}})


def formulas(nonempty=True):
    pair = lambda f: Forall("node", Forall("node", f))
    named = lambda k: Reach(k, Named("edge"), Var(1), Var(0))
    body = lambda k: Reach(k, Body("node", Binary("edge", Var(1), Var(0))), Var(1), Var(0))
    fs = [Forall("node", Reach("star", Named("edge"), Var(0), Var(0))),
          Exists("node", Reach("plus", Named("edge"), Var(0), Var(0))),
          pair(Implies(named("plus"), named("star"))),
          pair(Implies(named("plus"), body("plus"))),
          pair(Implies(body("plus"), named("plus"))),
          pair(Implies(body("star"), named("star"))),
          Forall("other", Exists("node", Reach("star", Named("edge"), Var(0), Var(0)))),
          Forall("node", Reach("star", Body("node", Bottom()), Var(0), Var(0))),
          Exists("node", Reach("plus", Body("node", Bottom()), Var(0), Var(0))),
          Forall("node", Forall("node", Forall("node", Reach("plus", Body("node",
              And(Binary("edge", Var(1), Var(0)), Not(Eq(Var(0), Var(4))))), Var(1), Var(0))))),
          pair(Reach("plus", Body("node", Reach("star", Named("edge"), Var(1), Var(0))), Var(1), Var(0)))]
    if nonempty:
        for k in ("plus", "star"):
            fs += [Reach(k, Named("edge"), Const("start"), Const("end")),
                   Reach(k, Named("edge"), Const("end"), Const("start")),
                   Reach(k, Named("edge"), Const("start"), Const("start")),
                   Forall("node", Reach(k, Body("node", And(Binary("edge", Var(1), Var(0)),
                       Not(Eq(Var(0), Var(2))))), Const("start"), Const("end")))]
    return Document(tuple(fs))


def cases():
    graphs = [(0, [], "empty"), (1, [], "isolated"), (1, [(0, 0)], "self_loop"),
              (3, [(0, 1), (1, 2)], "directed_chain"),
              (3, [(0, 1), (1, 2), (2, 0)], "cycle"),
              (3, [(1, 0), (2, 1)], "reverse_chain")]
    for mask in range(16):
        graphs.append((2, [(i, j) for i in range(2) for j in range(2) if mask & (1 << (2*i+j))], f"two_{mask}"))
    rng = random.Random(20260921)
    for n in (3, 4):
        for i in range(12):
            graphs.append((n, [(a,b) for a in range(n) for b in range(n) if rng.random() < .3], f"seeded_{n}_{i}"))
    result = []
    for n, edges, label in graphs:
        env = environment(n > 0)
        doc = formulas(n > 0)
        model = FiniteModel.from_dict(env, {"complete": True,
            "domains": {"node": [f"n{i}" for i in range(n)], "other": [] if n % 2 == 0 else ["q"]},
            "constants": {"start": "n0", "end": f"n{n-1}"} if n else {},
            "relations": {"edge": [[f"n{a}", f"n{b}"] for a,b in edges], "marked": [["n0"]] if n else []}})
        values = [evaluate(env, f, model, trace=False).value for f in doc.formulas]
        assert all(type(v) is bool for v in values)
        result.append({"id": "closure_" + label, "environment": env.to_dict(), "model": model.to_dict(),
            "ast": document_to_data(env, doc), "source": print_document(env, doc), "expected": values})
    return result


if __name__ == "__main__":
    result = cases()
    Path(__file__).with_name("closure.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"{len(result)} closure models; {sum(len(c['ast']) for c in result)} formulas")
