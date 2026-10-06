"""Python hooks and adapter of the `norm-defaults@0` wire table (wire-contract-s5.md 2.4, 2.5).

The table includes the phases of `norms@0`, whose hooks and classifiers are registered here under the same
names. The diagnostic engine observes a source only after the legacy validator rejects it. It never decides
acceptance or identity.
"""

from conformance import frozen_norm_defaults as nd
from ve.ast import _Checker
from ve.environment import Environment
from ve.errors import ResourceLimit
from ve.limits import MAX_PREDICATES
from ve.norms import NormDocument
from ve.norms_contract import CLASSIFIERS, HOOKS, heights, source
from ve.wire_contract.engine import Registry


def legacy_validation(environment, norms):
    """The route's own statements in the route's order (2.2): the environment, each unit decoded, then the
    document with its `unspecified` completion."""
    return nd.UnspecifiedDocument(Environment(environment), [NormDocument._decode(c) for c in norms])


def norm_defaults_source(case):
    return source(case, kinds=lambda kind: kind.startswith("norm-defaults-"), defaults=True)


def _prepared(root):
    """`UnspecifiedDocument` up to its limits: the environment, the author document (W1's checks hold, as the
    engine may assume of every earlier instance) and the unspecified predicates."""
    env = Environment(root["environment"])
    document = object.__new__(nd.UnspecifiedDocument)
    document.env = env
    document.author = NormDocument(env, [NormDocument._decode(unit) for unit in root["norms"]])
    document.unspec = tuple(sorted(p for p, d in env.predicates.items()
                                   if d.regulated is not None and d.regulated.default == "unspecified"))
    return document


def filled_vocabulary_fits(root, items):
    """5.1: the declared and the unspecified predicates are together at most `MAX_PREDICATES`."""
    document = _prepared(root)
    return len(document.env.predicates) + len(document.unspec) > MAX_PREDICATES


def filled_rules_fit(root, items):
    """5.2: the rules and the unspecified predicates are together at most 256."""
    document = _prepared(root)
    return len(document.author.rules) + len(document.unspec) > 256


def unspecified_names_fit(root, items):
    """5.3: every unspecified predicate's name is at most `MAX_NAME_BYTES` long in UTF-8."""
    return any(len(p.encode("utf-8")) > nd.MAX_NAME_BYTES for p in _prepared(root).unspec)


def filled_ast_fits(root, items):
    """6.1: one `_Checker` over the filled environment types every author formula and one fill guard per
    unspecified predicate within its node budget (`UnspecifiedDocument._check_ast`)."""
    document = _prepared(root)
    checker = _Checker(document._filled_environment())
    try:
        for rule in document.author.rules:
            context = tuple(reversed(document.env.predicates[rule.predicate].arguments))
            for formula in (rule.guard, *rule.unless):
                checker.formula(formula, context)
        for p in document.unspec:
            context = tuple(reversed(document.env.predicates[p].arguments))
            checker.formula(document._fill_guard(p), context)
    except ResourceLimit:
        return True
    return False


def filled_precedence_depth_fits(root, items):
    """6.2: every author rule on an unspecified predicate has precedence height at most 15."""
    unspec = set(_prepared(root).unspec)
    rules = [unit["norm"] for unit in root["norms"]]
    height = heights(rules)
    return any(height[rule["name"]] > 15 for rule in rules if rule["predicate"] in unspec)


def fill_premises_fit(root, items):
    """6.3: the pair premises of `Fill_T` share one node budget and each is at most 64 levels deep
    (`UnspecifiedDocument`, the `fill premise` limit)."""
    try:
        legacy_validation(root["environment"], root["norms"])
    except ResourceLimit as exc:
        message = str(exc)
        if message.startswith("fill premise "):
            return {"label": message.removeprefix("fill premise ")}
    return None


REGISTRY = Registry().register(
    hooks={**HOOKS, **{name: globals()[name] for name in (
        "filled_vocabulary_fits", "filled_rules_fit", "unspecified_names_fit", "filled_ast_fits",
        "filled_precedence_depth_fits", "fill_premises_fit")}},
    classifiers=CLASSIFIERS, adapters={"norm_defaults_source": norm_defaults_source})
