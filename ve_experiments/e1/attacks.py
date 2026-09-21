"""Mechanical attacks on wire-format ASTs, meaning-preserving rewrites, and validation.

An attack is a single local edit of the faithful AST. Every attack is validated:

1. it type-checks under the item's environment (`ve.formula_from_data`);
2. a *distinguishing finite model* exists: faithful and attacked ASTs evaluate differently on it.
   The model is stored with the item. If randomized search finds none, the attack is discarded
   (it may be equivalent), never kept on faith;
3. it is not detectable by string comparison: it mentions exactly the same sorts and predicates as
   the faithful AST (so "the requirement mentions X but the formula does not" cannot flag it), and
   its rendering differs from the faithful rendering.

`direction` records whether the attacked formula is weaker, stronger, or incomparable, estimated on
the same random models (exact on the sampled models only).
"""

from __future__ import annotations

import random
from collections.abc import Iterator

from ..ve_iface import StubBackend

_EVAL = StubBackend()
BIN = ("and", "or", "implies")
QUANT = ("forall", "exists")


# --------------------------------------------------------------------------- tree utilities


def subformulas(f: list, path: tuple[int, ...] = ()) -> Iterator[tuple[tuple[int, ...], list]]:
    yield path, f
    tag = f[0]
    if tag == "not":
        yield from subformulas(f[1], (*path, 1))
    elif tag in BIN:
        yield from subformulas(f[1], (*path, 1))
        yield from subformulas(f[2], (*path, 2))
    elif tag in QUANT:
        yield from subformulas(f[2], (*path, 2))


def replace(f: list, path: tuple[int, ...], new: list) -> list:
    if not path:
        return new
    out = list(f)
    out[path[0]] = replace(f[path[0]], path[1:], new)
    return out


def get(f: list, path: tuple[int, ...]) -> list:
    for i in path:
        f = f[i]
    return f


def map_vars(f: list, fn, depth: int = 0) -> list:
    """Apply fn(index_relative_to_root_context, depth) -> new relative index to free variables of f."""
    tag = f[0]
    if tag == "var":
        return ["var", fn(f[1] - depth) + depth] if f[1] >= depth else f
    if tag in ("unary",):
        return [tag, f[1], map_vars(f[2], fn, depth)]
    if tag == "binary":
        return [tag, f[1], map_vars(f[2], fn, depth), map_vars(f[3], fn, depth)]
    if tag == "eq":
        return [tag, map_vars(f[1], fn, depth), map_vars(f[2], fn, depth)]
    if tag == "not":
        return [tag, map_vars(f[1], fn, depth)]
    if tag in BIN:
        return [tag, map_vars(f[1], fn, depth), map_vars(f[2], fn, depth)]
    if tag in QUANT:
        return [tag, f[1], map_vars(f[2], fn, depth + 1)]
    return f


def symbols(f: list) -> frozenset[str]:
    out = set()
    for _, g in subformulas(f):
        if g[0] in ("unary", "binary"):
            out.add("pred:" + g[1])
        elif g[0] in QUANT:
            out.add("sort:" + g[1])
    return frozenset(out)


def inside_negation(f: list, path: tuple[int, ...]) -> bool:
    node = f
    for i in path:
        if node[0] == "not":
            return True
        node = node[i]
    return False


# --------------------------------------------------------------------------- attack operators


def _swap01(i: int) -> int:
    return {0: 1, 1: 0}.get(i, i)


def mechanical_attacks(f: list) -> Iterator[tuple[str, tuple[int, ...], list]]:
    """Yield (kind, path, attacked AST). Kinds follow PLAN v2; `weakened_exception` is assigned later
    to edits inside a negated exception that make the whole formula weaker."""
    for path, g in subformulas(f):
        tag = g[0]
        # quantifier swap, adjacent binders of different kinds
        if tag in QUANT and g[2][0] in QUANT and g[2][0] != tag:
            inner = g[2]
            yield "quantifier_swap", path, replace(f, path, [inner[0], inner[1], [tag, g[1], map_vars(inner[2], _swap01)]])
        # quantifier swap through an implication: Qa (G -> Q'b H)  =>  Q'b Qa (G -> H)
        if tag in QUANT and g[2][0] == "implies" and g[2][2][0] in QUANT and g[2][2][0] != tag:
            guard, inner = g[2][1], g[2][2]
            new_guard = map_vars(guard, lambda i: i if i == 0 else i + 1)
            new_body = map_vars(inner[2], _swap01)
            yield "quantifier_swap", path, replace(f, path, [inner[0], inner[1], [tag, g[1], ["implies", new_guard, new_body]]])
        # Ex (G and Qy H) => Qy Ex (G and H) for Q = forall
        if tag == "exists" and g[2][0] == "and" and g[2][2][0] == "forall":
            guard, inner = g[2][1], g[2][2]
            new_guard = map_vars(guard, lambda i: i if i == 0 else i + 1)
            yield "quantifier_swap", path, replace(f, path, ["forall", inner[1], ["exists", g[1], ["and", new_guard, map_vars(inner[2], _swap01)]]])
        if tag == "and":
            for keep in (1, 2):
                dropped = g[3 - keep]
                kind = "vacuous_domain" if dropped[0] == "exists" and not path else "dropped_conjunct"
                yield kind, path, replace(f, path, g[keep])
            yield "and_or_swap", path, replace(f, path, ["or", g[1], g[2]])
        if tag == "or":
            yield "and_or_swap", path, replace(f, path, ["and", g[1], g[2]])
        if tag == "implies":
            yield "implication_reversal", path, replace(f, path, ["implies", g[2], g[1]])
        if tag == "exists" and g[2][0] == "and":
            yield "vacuous_domain", path, replace(f, path, ["exists", g[1], ["implies", g[2][1], g[2][2]]])
        if tag == "binary":
            yield "argument_reversal", path, replace(f, path, ["binary", g[1], g[3], g[2]])


# --------------------------------------------------------------------------- models


def random_model(vocabulary: dict, rng: random.Random, max_size: int = 3, allow_empty: bool = True) -> dict:
    sorts = sorted(vocabulary["sorts"])
    domains = {}
    for s in sorts:
        lo = 0 if allow_empty and rng.random() < 0.15 else 1
        n = rng.randint(lo, max_size)
        domains[s] = [f"{s[0]}{i + 1}" if len({t[0] for t in sorts}) == len(sorts) else f"{s}{i + 1}" for i in range(n)]
    relations = {}
    for name, decl in sorted(vocabulary["predicates"].items()):
        density = rng.choice((0.2, 0.5, 0.8))
        tuples = [[]]
        for arg in decl["arguments"]:
            tuples = [[*t, d] for t in tuples for d in domains[arg]]
        relations[name] = [t for t in tuples if rng.random() < density]
    return {"complete": True, "domains": domains, "constants": {}, "relations": relations}


def evaluate(f: list, model: dict) -> bool:
    return _EVAL.evaluate(f, model)


def model_size(model: dict) -> int:
    return sum(len(d) for d in model["domains"].values()) + sum(len(r) for r in model["relations"].values())


def compare(faithful: list, other: list, vocabulary: dict, seed: str, n: int = 600) -> dict:
    """Randomized semantic comparison. Returns the smallest distinguishing model found (or None) and
    counts of models where only the faithful / only the other formula holds."""
    rng = random.Random(seed)
    best, best_key = None, (True, 0)
    only_f = only_o = 0
    for k in range(n):
        m = random_model(vocabulary, rng, max_size=2 if k < n // 2 else 3)
        a, b = evaluate(faithful, m), evaluate(other, m)
        if a != b:
            only_f += a
            only_o += b
            # prefer a model in which every sort is inhabited, then the smallest one
            key = (any(not d for d in m["domains"].values()), model_size(m))
            if best is None or key < best_key:
                best, best_key = m, key
    if best is None:
        direction = "no_difference_found"
    elif only_f and only_o:
        direction = "incomparable"
    else:
        direction = "weaker" if only_o else "stronger"
    nonvacuous = best is not None and all(best["domains"].values())
    return {"model": best, "nonvacuous": nonvacuous, "only_faithful": only_f, "only_other": only_o, "direction": direction, "n_models": n}


# --------------------------------------------------------------------------- meaning-preserving rewrites


def equivalent_rewrites(f: list) -> Iterator[tuple[str, list]]:
    """Sound single-step rewrites, used to make faithful candidates that do not look canonical.
    Soundness is by construction (classical equivalences); `compare` re-checks each one."""
    for path, g in subformulas(f):
        tag = g[0]
        if tag == "implies":
            yield "contraposition", replace(f, path, ["implies", ["not", g[2]], ["not", g[1]]])
            if g[1][0] == "and":
                yield "exportation", replace(f, path, ["implies", g[1][1], ["implies", g[1][2], g[2]]])
            if g[2][0] != "not":
                yield "implication_as_disjunction", replace(f, path, ["or", ["not", g[1]], g[2]])
        if tag == "and":
            yield "commute_and", replace(f, path, ["and", g[2], g[1]])
        if tag == "not" and g[1][0] == "and":
            yield "de_morgan", replace(f, path, ["or", ["not", g[1][1]], ["not", g[1][2]]])
