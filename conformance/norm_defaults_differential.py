"""Python/Lean differentials for norm-defaults@0 (docs/spec/norm-defaults.md 8).

Generated trees over completion assignments in {deny, allow, unspecified}, with a
declared pair and guards that mention lower regulated predicates (in a drawn order,
so other symbols land between the pair's members), each with one
generated finite situation. For every tree Lean's `norm-defaults-elaborate`
regenerates `fill U` from the same source and every output (`T‴`, `Fill_T`, the
unsaid tables, the reached formulas) must equal Python's byte for byte. For the
first `situations` trees, at every point of the situation:

* Lean's `table3` equals Python's (both definite with the same value, or both unknown);
* Python's status is the status Lean's replay reports: `table3` and enumeration
  are recomputed by Lean, an UNDECIDED witness pair is checked by Lean; some
  situations have more unsaid atoms than `MAX_UNSAID_ATOMS`, where both sides
  enumerate only the point's closed cone;
* a CONFLICT witness (settled or latent) is a Lean CONFLICT.

`python conformance/norm_defaults_differential.py` prints the counts.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve.ast import And, Not, Or, Top, Unary, Var  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.norms import Norm  # noqa: E402
from ve import norm_defaults as nd  # noqa: E402
from ve import norm_defaults_route as route  # noqa: E402
from conformance.norm_defaults import _environment, _regulated  # noqa: E402

# Each tree draws an order of the regulated predicates; a guard may mention only
# predicates earlier in it (no dependency cycles), so `a_permitted` and `y_permitted`
# can land between the members of the pair `x_required`/`x_permitted`.
REGULATED = ("a_permitted", "y_permitted", "x_permitted", "x_required")
BASE = ("c1", "c2")
NORMS_ONLY = ["norms@0", "relational-fol@0"]
CHUNK = 1000


def _guard(rng, allowed, depth=2):
    if depth == 0 or rng.random() < 0.35:
        return Top() if rng.random() < 0.15 else Unary(rng.choice(allowed), Var(0))
    kind = rng.choice(("and", "or", "not"))
    if kind == "not":
        return Not(_guard(rng, allowed, depth - 1))
    left, right = _guard(rng, allowed, depth - 1), _guard(rng, allowed, depth - 1)
    return And(left, right) if kind == "and" else Or(left, right)


def case(seed, *, profiled=None, domain=("a", "b")):
    """A generated tree and situation: `(environment, rules, situation)`.

    `profiled=None` enables norm-defaults@0 whenever a completion is unspecified and
    at random otherwise; `True` always enables it."""
    rng = random.Random(seed)
    completions = {p: rng.choice(("deny", "allow", "unspecified")) for p in REGULATED}
    predicates = {"a_permitted": _regulated("permission", completions["a_permitted"], "{0} be audited"),
                  "y_permitted": _regulated("permission", completions["y_permitted"], "{0} be tried"),
                  "x_permitted": _regulated("permission", completions["x_permitted"]),
                  "x_required": _regulated("obligation", completions["x_required"], permission="x_permitted"),
                  **{b: {"arguments": ["act"], "description": b} for b in BASE}}
    enable = "unspecified" in completions.values() or rng.random() < 0.5
    if profiled:
        enable = True
    env = Environment(_environment(predicates, profiles=(["norm-defaults@0"] + NORMS_ONLY
                                                         if enable else NORMS_ONLY)))
    order = list(REGULATED)
    rng.shuffle(order)
    rules = []
    for index in range(rng.randint(0, 6)):
        predicate = rng.choice(order)
        allowed = list(BASE) + order[:order.index(predicate)]
        same = [r.name for r in rules if r.predicate == predicate]
        over = tuple(rng.sample(same, 1)) if same and rng.random() < 0.3 else ()
        unless = (_guard(rng, allowed, 1),) if rng.random() < 0.25 else ()
        rules.append(Norm(f"r{index}", predicate, rng.random() < 0.5, _guard(rng, allowed), unless, over))
    situation = {"complete": True, "domains": {"act": list(domain)}, "constants": {},
                 "relations": {b: [[e] for e in domain if rng.random() < 0.5] for b in BASE}}
    return env, rules, situation


def _filling_json(filling):
    return {name: [list(row) for row in sorted(rows)] for name, rows in filling.items()}


def _answer(value):
    return "UNKNOWN" if value is None else ("SETTLED yes" if value else "SETTLED no")


def point_cases(document, raw_situation):
    """(case, expected, kind) for Lean's `table3` and Python's status at every point."""
    situation = document.situation(raw_situation)
    table = document.table3(situation)
    rows = []
    for status in document.statuses(situation):
        base = route.source_case(document, "norm-defaults-status", model=situation.to_dict(),
                                 predicate=status.predicate, tuple=list(status.values))
        rows.append(({**base, "method": "table3"}, _answer(table[(status.predicate, status.values)]),
                     "table3"))
        if status.status == "SETTLED":
            method = "table3" if status.evidence == "table3" else "enumerate"
            rows.append(({**base, "method": method}, _answer(status.value), "status"))
        elif status.status == "UNDECIDED":
            rows.append(({**base, "method": "undecided", "yes": _filling_json(status.fillings[0]),
                          "no": _filling_json(status.fillings[1])}, "UNDECIDED", "status"))
        else:
            raise AssertionError(f"UNKNOWN status in a differential situation: {status}")
    report = nd.check_conflict(document, model=raw_situation)
    if report.status == "CONFLICT":
        filling = {k: frozenset(tuple(r) for r in v) for k, v in report.filling.items()}
        model = document.with_filling(situation, filling)
        rows.append((route.source_case(document, "norm-defaults-conflict", witness={
            "target": report.target, "model": model.to_dict(), "tuple": list(report.tuple)}),
            "CONFLICT", f"conflict:{report.kind}"))
    return rows


def run(executable=route.LEAN_ROUTE, *, trees=1000, situations=1000, seed=0):
    cases, expected, kinds, documents, wide = [], [], [], [], 0
    for index in range(trees):
        draw = random.Random(f"domain:{seed + index}").random()
        domain = (tuple("abcdefg") if draw < 0.08 else ("a", "b", "c") if draw < 0.3 else ("a", "b"))
        env, rules, raw_situation = case(seed + index, profiled=True, domain=domain)
        document = nd.UnspecifiedDocument(env, rules)
        documents.append(document)
        if index < situations and len(document.unspec) * len(domain) > nd.MAX_UNSAID_ATOMS:
            wide += 1
        cases.append({**route.source_case(document, "norm-defaults-elaborate"), "id": f"t{index}"})
        expected.append(document)
        kinds.append("elaborate")
        if index < situations:
            for case_, answer, kind in point_cases(document, raw_situation):
                cases.append({**case_, "id": f"t{index}:{len(cases)}"})
                expected.append(answer)
                kinds.append(kind)
    results = []
    for start in range(0, len(cases), CHUNK):
        # one process per chunk: the route reads at most 16 MiB of input
        results.extend(route.run_cases(cases[start:start + CHUNK], executable, timeout=600))
    mismatches, counts = [], {}
    for case_, answer, kind, row in zip(cases, expected, kinds, results):
        counts[kind] = counts.get(kind, 0) + 1
        if row.get("status") != "ok":
            mismatches.append((case_["id"], kind, row.get("error")))
            continue
        if kind == "elaborate":
            try:
                route.check_regenerated(answer, row)
            except Exception as error:  # noqa: BLE001 - reported as a mismatch row
                mismatches.append((case_["id"], kind, str(error)))
            continue
        got = row["verdict"] if kind.startswith("conflict") else row["point_status"]
        if got != answer:
            mismatches.append((case_["id"], kind, got, answer))
    return {"trees": trees, "situations": situations, "counts": counts,
            "unspecified": sum(bool(d.unspec) for d in documents),
            # situations with more unsaid atoms than MAX_UNSAID_ATOMS: only the cone is enumerated
            "wide": wide, "mismatches": mismatches}


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=1))
