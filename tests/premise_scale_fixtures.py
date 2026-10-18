"""Premise sets for premise-scale's tests and the service corpus: content whose smallest model needs more
entities of one sort than the shared domain bound (QT-0p's "exactly three principal types", by constants
and by an existential chain), the same content past the per-sort cap, and ground stated quantities (the
math-evidence documents' shape)."""
from __future__ import annotations

SPEC = "ve-v0.2-expand2-2026-09-25"
TYPES = ("anthropic", "operators", "users")


def relational_environment(constants: dict[str, str] | None = None) -> dict:
    """Sorts `principal_type` and `person`, a unary `principal`, and `constants` ({name: sort})."""
    if constants is None:
        constants = {**dict.fromkeys(TYPES, "principal_type"), "alice": "person", "bob": "person"}
    return {"language": "ve.core@0.2", "profiles": ["relational-fol@0"], "spec_revision": SPEC,
            "vocabulary": {
                "sorts": {"person": {"description": "a person"},
                          "principal_type": {"description": "a type of principal"}},
                "predicates": {"principal": {"arguments": ["principal_type"], "description": "is a principal type"},
                               "trusts": {"arguments": ["person", "principal_type"],
                                          "description": "trusts the principal type"}},
                "constants": {name: {"sort": sort, "description": name} for name, sort in constants.items()}}}


def conjunction(facts: list) -> list:
    formula = facts[-1]
    for fact in reversed(facts[:-1]):
        formula = ["and", fact, formula]
    return formula


def distinct(names) -> list:
    """`¬(a = b)` for every pair of `names`, in order."""
    names = list(names)
    return [["not", ["eq", ["const", a], ["const", b]]] for i, a in enumerate(names) for b in names[i + 1:]]


def exactly_constants(names=TYPES) -> list:
    """The named types are principal types, pairwise distinct, and the only ones (u0043.s02.p2's shape)."""
    closure = ["eq", ["var", 0], ["const", names[-1]]]
    for name in reversed(names[:-1]):
        closure = ["or", ["eq", ["var", 0], ["const", name]], closure]
    return conjunction([*(["unary", "principal", ["const", n]] for n in names), *distinct(names),
                        ["forall", "principal_type", ["implies", ["unary", "principal", ["var", 0]], closure]]])


def exactly_chain(k: int = 3) -> list:
    """`∃ x₁ … x_k : principal_type`, each a principal, pairwise distinct (u0042's presupposition shape)."""
    body = conjunction([*(["unary", "principal", ["var", i]] for i in range(k)),
                        *(["not", ["eq", ["var", i], ["var", j]]] for i in range(k) for j in range(i + 1, k))])
    for _ in range(k):
        body = ["exists", "principal_type", body]
    return body


def quantity_environment(n: int) -> dict:
    """`n` integer constants (an order@0 environment, as the quantity route's erased target)."""
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": SPEC, "vocabulary": {
                "sorts": {}, "predicates": {},
                "constants": {f"q{i:03d}": {"sort": "$int", "description": f"quantity {i}"} for i in range(n)}}}


def stated_quantities(n: int, per_premise: int = 20) -> list[list]:
    """Each constant stated equal to a numeral, `per_premise` facts per premise (H's tables)."""
    facts = [["eq", ["const", f"q{i:03d}"], ["num", str(4000 + 7 * i)]] for i in range(n)]
    return [conjunction(facts[i:i + per_premise]) for i in range(0, n, per_premise)]


def search_budget_cases() -> list[dict]:
    """The `search-budget` mode's answers: a sort raised by constants and by a chain, none raised, an
    order case (no sort), a sort past the cap, and malformed requests."""
    env = relational_environment()
    nine = [f"t{i}" for i in range(9)]
    capped = relational_environment(dict.fromkeys(nine, "principal_type"))
    return [
        {"id": "constants", "environment": env, "premises": [exactly_constants()],
         "sorts": ["person", "principal_type"]},
        {"id": "chain", "environment": env, "premises": [exactly_chain()], "sorts": ["principal_type"]},
        {"id": "plain", "environment": env, "premises": [["unary", "principal", ["const", "users"]]],
         "sorts": ["person", "principal_type"]},
        {"id": "order", "environment": quantity_environment(3), "premises": stated_quantities(3), "sorts": []},
        {"id": "capped", "environment": capped, "premises": [conjunction(distinct(nine))],
         "sorts": ["principal_type"]},
        {"id": "no-sorts", "environment": env, "premises": []},
        {"id": "bad-sorts", "environment": env, "premises": [], "sorts": [7]},
    ]
