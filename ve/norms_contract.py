"""Python hooks, classifiers and adapter of the `norms@0` wire table (wire-contract-s5.md 2.3, 2.5).

The diagnostic engine observes a source only after the legacy validator rejects
it. It never decides acceptance or identity.
"""

import json

from ve.ast import _Checker
from ve.environment import Environment
from ve.errors import UnsupportedProfile, VEError
from ve.limits import MAX_DEPTH, MAX_INDEX, MAX_NODES
from ve.norms import NormDocument, _used_predicates, dependency_order
from ve.wire_contract.engine import Registry


# The profiles of the unit's domain (2.2): checker profiles are refused by both routes before the validator
# runs, and the statement layers are dispatched to other routes.
DOMAIN_PROFILES = frozenset({"data@0", "definitions@0", "documents@1", "norm-defaults@0", "norms@0",
                             "relational-fol@0", "time@0"})
NORM_KINDS = ("norms-elaborate", "norms-conflict", "norms-certificate")
OUTSIDE = "UnsupportedProfile: the case is outside the unit's domain"


def legacy_validation(environment, norms):
    """The route's own statements in the route's order (2.2): the environment, then the norm document."""
    return NormDocument(Environment(environment), norms)


def active_norms(document):
    """The norm objects a route validates: the `content` of each unit of kind `norm` whose `content` is an
    object with a member `norm`, in document order (`ve/norm_admission.py`)."""
    units = document.get("units", []) if type(document) is dict else []
    return [unit["content"] for unit in units
            if type(unit) is dict and unit.get("kind") == "norm"
            and type(unit.get("content")) is dict and "norm" in unit["content"]]


def in_domain(environment, norms, *, defaults):
    """Whether a source is in the domain of `norms@0` (`defaults` False) or of `norm-defaults@0` (2.2)."""
    if type(norms) is not list or any(type(unit) is not dict for unit in norms):
        return False
    if type(environment) is dict:
        if "unit_schema" in environment or "units" in environment:
            return False
        listed = environment.get("profiles")
        if type(listed) is list:
            if any(type(p) is not str or p not in DOMAIN_PROFILES for p in listed):
                return False
            if ("norm-defaults@0" in listed) != defaults:
                return False
    return True


def source(case, *, kinds, defaults):
    """The root of a case of one of `kinds` or of an `admission` case, as the Lean adapter builds it: a
    member the case lacks is `null`; any other kind has no wire contract input, and a source outside the
    unit's domain is refused (2.2)."""
    kind = case.get("kind")
    if kind == "admission":
        root = {"environment": case.get("environment"), "norms": active_norms(case.get("document"))}
    elif kind in kinds:
        root = {"environment": case.get("environment"), "norms": case.get("norms")}
    else:
        shown = kind if type(kind) is str else json.dumps(kind, separators=(",", ":"))
        raise UnsupportedProfile(f"UnsupportedProfile: case kind {shown} has no wire contract input")
    if not in_domain(root["environment"], root["norms"], defaults=defaults):
        raise UnsupportedProfile(OUTSIDE)
    return root


def norm_source(case):
    return source(case, kinds=NORM_KINDS, defaults=False)


def _item(root, path):
    value = root
    for token in path:
        value = value[int(token)] if type(value) in (list, tuple) else value[token]
    return value


def _failure(call):
    try:
        call()
    except VEError as exc:
        return {"message": str(exc)}
    return None


def w1_environment(root, items):
    """1.1, inherited: the environment decoder accepts the environment."""
    return _failure(lambda: Environment(root["environment"]))


# 2.5, the syntax walk: the first-order tags of the P0 wire form with their number of members, by
# position, and the seven tags `_Decoder` also reads, which the walk refuses at their node.
FORMULA_TAGS = {"top": 1, "bottom": 1, "unary": 3, "binary": 4, "eq": 3, "not": 2, "and": 3, "or": 3,
                "implies": 3, "forall": 3, "exists": 3}
TERM_TAGS = {"var": 2, "const": 2}
NON_FIRST_ORDER = frozenset({"reach", "atom", "lt", "le", "num", "add", "scale"})


class Refused(Exception):
    """The syntax walk's first refused node: the member (`a`, the budget; `b`, the shape) and the text
    `ve.ast._Decoder` raises there, or `invalid indexed formula` at a non-first-order tag."""

    def __init__(self, member, message):
        super().__init__(message)
        self.member, self.message = member, message


def syntax_walk(node, count=0, depth=1, term=False):
    """Visit a formula on the wire in pre-order with `_Decoder`'s depths (a term under an atom is at depth
    1) and one running node count; return the count, or raise `Refused` at the first refused node. At each
    node the budget is checked before the shape; names are not examined."""
    count += 1
    if count > MAX_NODES or depth > MAX_DEPTH:
        raise Refused("a", "AST exceeds depth or node budget")
    if type(node) is not list or not node or type(node[0]) is not str:
        raise Refused("b", "AST nodes must be nonempty tagged JSON arrays")
    tag = node[0]
    if tag in NON_FIRST_ORDER:
        raise Refused("b", "invalid indexed formula")
    arity = (TERM_TAGS if term else FORMULA_TAGS).get(tag)
    if arity is None or len(node) != arity:
        raise Refused("b", f"Unknown AST tag or incorrect arity: {tag!r}")
    if tag == "var":
        if type(node[1]) is not int or not 0 <= node[1] <= MAX_INDEX:
            raise Refused("b", "Invalid variable index")
        return count
    if tag in ("const", "top", "bottom"):
        return count
    if tag == "unary":
        return syntax_walk(node[2], count, 1, True)
    if tag in ("binary", "eq"):
        count = syntax_walk(node[-2], count, 1, True)
        return syntax_walk(node[-1], count, 1, True)
    if tag == "not":
        return syntax_walk(node[1], count, depth + 1)
    if tag in ("and", "or", "implies"):
        count = syntax_walk(node[1], count, depth + 1)
        return syntax_walk(node[2], count, depth + 1)
    return syntax_walk(node[2], count, depth + 1)


def guard_syntax(root, items):
    """3.8: the syntax walk on the item's guard, with a fresh count."""
    try:
        syntax_walk(_item(root, items[0])["norm"]["guard"])
    except Refused as refused:
        return "3.8" + refused.member, {"message": refused.message}
    return None


def carve_out_syntax(root, items):
    """3.9: the syntax walk on the rule's guard and on its carve-outs up to and including the item, with one
    count; the item's first refused node names the member."""
    rule = _item(root, items[1])["norm"]
    index = int(items[0][-1])
    count = 0
    try:
        for position, formula in enumerate([rule["guard"], *rule["unless"][:index + 1]]):
            count = syntax_walk(formula, count)
    except Refused as refused:
        if position != index + 1:
            return None
        return "3.9" + refused.member, {"message": refused.message}
    return None


def rule_name_not_reserved(root, items):
    """4.3: under `norm-defaults@0` no rule name starts with `unsaid--`."""
    name = _item(root, items[0])["norm"]["name"]
    return "norm-defaults@0" in root["environment"]["profiles"] and name.startswith("unsaid--")


def regulated_predicate(root, items):
    """4.4: the rule's predicate is declared with `regulated`."""
    predicate = _item(root, items[0])["norm"]["predicate"]
    declaration = root["environment"]["vocabulary"]["predicates"].get(predicate)
    return type(declaration) is not dict or "regulated" not in declaration


# 4.7: the member of each class `ve.ast._Checker` raises.
TYPING_MEMBERS = {"TypeMismatch": "a", "UnknownSymbol": "b", "UnboundVariable": "c", "ResourceLimit": "d",
                  "UnsupportedProfile": "e"}


def typing_failure(env, rules, prefix):
    """One `_Checker` over `env` types the decoded guard and carve-outs of `rules` in order, each over the
    sorts of its rule's predicate; the first exception's class names the member of `prefix`."""
    checker = _Checker(env)
    try:
        for rule in rules:
            context = tuple(reversed(env.predicates[rule.predicate].arguments))
            for formula in (rule.guard, *rule.unless):
                checker.formula(formula, context)
    except VEError as exc:
        member = TYPING_MEMBERS.get(exc.code)
        return None if member is None else (prefix + member, {"message": str(exc)})
    return None


def rule_typing(root, items):
    """4.7: the guards and carve-outs of the earlier rules, then the item's, under one `_Checker`."""
    index = int(items[0][-1])
    env = Environment(root["environment"])
    rules = [NormDocument._decode(unit) for unit in root["norms"][:index + 1]]
    return typing_failure(env, rules, "4.7")


def over_same_predicate(root, items):
    """5.2: the rule named by the item is on the enclosing rule's predicate."""
    parent_name = _item(root, items[0])
    rule = root["norms"][int(items[1][-1])]["norm"]
    parent = next(item["norm"] for item in root["norms"] if item["norm"]["name"] == parent_name)
    if rule["predicate"] != parent["predicate"]:
        return {"rule": rule["name"], "predicate": rule["predicate"], "parent_predicate": parent["predicate"]}
    return None


def _cycle(graph):
    try:
        dependency_order(graph)
    except VEError as exc:
        return {"detail": str(exc).removeprefix("DependencyCycle: ")}
    return None


def precedence_acyclic(root, items):
    """6.1: the precedence graph over the rules is acyclic."""
    return _cycle({unit["norm"]["name"]: set(unit["norm"]["over"]) for unit in root["norms"]})


def heights(rules):
    """Each rule's precedence height, as `NormDocument` computes it: 1, or 1 more than the greatest height
    of the rules that name it in `over`."""
    children = {rule["name"]: [] for rule in rules}
    for rule in rules:
        for parent in rule["over"]:
            children[parent].append(rule["name"])
    depth = {}
    def height(name):
        if name not in depth:
            depth[name] = 1 + max((height(child) for child in children[name]), default=0)
        return depth[name]
    return {name: height(name) for name in children}


def precedence_depth_fits(root, items):
    """6.2: every rule's precedence height is at most 16."""
    return any(h > 16 for h in heights([unit["norm"] for unit in root["norms"]]).values())


def layers_acyclic(root, items):
    """6.3: the graph over the regulated predicates, with an edge from a rule's predicate to each regulated
    predicate its guard or carve-outs mention, is acyclic."""
    env = Environment(root["environment"])
    dependencies = {p: set() for p, d in env.predicates.items() if d.regulated is not None}
    for unit in root["norms"]:
        rule = NormDocument._decode(unit)
        dependencies[rule.predicate].update(
            q for f in (rule.guard, *rule.unless) for q in _used_predicates(f) if q in dependencies)
    return _cycle(dependencies)


HOOKS = {name: globals()[name] for name in (
    "w1_environment", "rule_name_not_reserved", "regulated_predicate", "over_same_predicate",
    "precedence_acyclic", "precedence_depth_fits", "layers_acyclic")}
CLASSIFIERS = {"guard_syntax": guard_syntax, "carve_out_syntax": carve_out_syntax, "rule_typing": rule_typing}

REGISTRY = Registry().register(hooks=HOOKS, classifiers=CLASSIFIERS, adapters={"norm_source": norm_source})
