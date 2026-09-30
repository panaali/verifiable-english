"""norm-defaults@0 evidence against brute force (docs/spec/norm-defaults.md 2.5, 3.1, 8).

Random trees over deny, allow and unspecified completions, with pairs and guards
that mention lower regulated predicates, on random two-element situations. Every
filling of the unsaid tables is enumerated as ground truth: `table3` is sound
(`table3_sound`), a SETTLED status holds under every admissible filling, an
UNDECIDED one has two checked fillings, no status is UNKNOWN within the atom
budget, the conflict search finds a witness exactly when some admissible filling
makes a target true, and without unspecified predicates `fill` is the identity.
"""
import random
from itertools import product

import pytest

from ve.ast import And, Binary, Not, Or, Top, Unary, Var
from ve.environment import Environment
from ve.evaluate import _Evaluator
from ve.norms import Norm, NormDocument
from ve import norm_defaults as nd
from tests.test_norm_defaults import obligation, permission, raw_environment

# Guards may mention only predicates earlier in this order (no dependency cycles).
ORDER = ("y_permitted", "x_permitted", "x_required")
BASE = ("c1", "c2")


def _atom(rng, allowed):
    name = rng.choice(allowed)
    return Unary(name, Var(0))


def _guard(rng, allowed, depth=2):
    if depth == 0 or rng.random() < 0.35:
        return Top() if rng.random() < 0.15 else _atom(rng, allowed)
    kind = rng.choice(("and", "or", "not"))
    if kind == "not":
        return Not(_guard(rng, allowed, depth - 1))
    left, right = _guard(rng, allowed, depth - 1), _guard(rng, allowed, depth - 1)
    return And(left, right) if kind == "and" else Or(left, right)


def case(seed):
    rng = random.Random(seed)
    completions = {p: rng.choice(("deny", "allow", "unspecified")) for p in ORDER}
    predicates = {"y_permitted": permission(completions["y_permitted"], act="{0} be tried"),
                  "x_permitted": permission(completions["x_permitted"]),
                  "x_required": obligation(completions["x_required"]),
                  **{b: {"arguments": ["act"], "description": b} for b in BASE}}
    profiles = (["norm-defaults@0", "norms@0", "relational-fol@0"]
                if "unspecified" in completions.values() or rng.random() < 0.5
                else ["norms@0", "relational-fol@0"])
    env = Environment(raw_environment(predicates, profiles=profiles))
    rules = []
    for index in range(rng.randint(0, 5)):
        predicate = rng.choice(ORDER)
        allowed = list(BASE) + list(ORDER[:ORDER.index(predicate)])
        same = [r.name for r in rules if r.predicate == predicate]
        over = tuple(rng.sample(same, 1)) if same and rng.random() < 0.3 else ()
        unless = (_guard(rng, allowed, 1),) if rng.random() < 0.25 else ()
        rules.append(Norm(f"r{index}", predicate, rng.random() < 0.5, _guard(rng, allowed), unless, over))
    situation = {"complete": True, "domains": {"act": ["a", "b"]}, "constants": {},
                 "relations": {b: [[e] for e in ("a", "b") if rng.random() < 0.5] for b in BASE}}
    return env, rules, situation


def fillings(document, situation):
    atoms = [(nd.unsaid_name(p), (e,)) for p in document.unspec for e in situation.domains["act"]]
    for bits in product((False, True), repeat=len(atoms)):
        filling = {nd.unsaid_name(p): set() for p in document.unspec}
        for (name, row), bit in zip(atoms, bits):
            if bit:
                filling[name].add(row)
        yield {k: frozenset(v) for k, v in filling.items()}


SEEDS = range(300)


@pytest.mark.parametrize("seed", SEEDS)
def test_evidence_agrees_with_every_filling(seed):
    env, rules, raw_situation = case(seed)
    if "norm-defaults@0" not in env.profiles:
        # Conservativity: a W1 document is its own fill, statuses are its outcomes.
        raw = env.to_dict()
        raw["profiles"] = sorted(raw["profiles"] + ["norm-defaults@0"])
        document = nd.UnspecifiedDocument(Environment(raw), rules)
        w1 = NormDocument(env, rules)
        assert document.filled.rules == w1.rules and document.fill_premises == ()
        assert document.filled.premises() == w1.premises()
        assert document.filled.conflict_targets() == w1.conflict_targets()
        return
    document = nd.UnspecifiedDocument(env, rules)
    situation = document.situation(raw_situation)
    admissible = [f for f in fillings(document, situation) if document.fill_valid(situation, f)]
    assert admissible, "canonical_fill_sat: some filling is admissible"
    assert document.fill_valid(situation, document.canonical_filling(situation))
    table = document.table3(situation)
    for p in ORDER:
        for e in situation.domains["act"]:
            truth = {document.value(situation, f, p, (e,)) for f in admissible}
            settled = table[(p, (e,))]
            if settled is not None:
                assert truth == {settled}, ("table3", p, e)
            status = document.status(situation, p, (e,))
            assert status.status != "UNKNOWN", (p, e, status)
            if status.status == "SETTLED":
                assert truth == {status.value}, (p, e, status)
            else:
                assert truth == {True, False}, (p, e, status)
                assert nd.check_undecided(document, situation, p, (e,), *status.fillings)
    # 3.1: a witness exactly when some admissible filling makes some target true.
    base = document._raw_base()
    targets = document.filled.conflict_targets()
    expected = False
    for f in admissible:
        model = document.with_filling(situation, f, checked=False)
        evaluator = _Evaluator(base, model, 1_000_000, trace=False)
        for _, sorts, formula in targets:
            for e in situation.domains["act"]:
                if evaluator.formula(formula, (("act", e),))[0]:
                    expected = True
    report = nd.check_conflict(document, model=situation.to_dict())
    assert (report.status == "CONFLICT") == expected, report
    if report.status == "CONFLICT":
        filling = {k: frozenset(tuple(r) for r in v) for k, v in report.filling.items()}
        assert filling in admissible
