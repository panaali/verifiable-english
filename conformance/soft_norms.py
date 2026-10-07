"""Deterministic Python/Lean regeneration comparison for 1,000 soft trees."""
from __future__ import annotations

import json
from copy import deepcopy
from itertools import combinations
from pathlib import Path
import random
import sys

from ve.ast import formula_to_data
from ve.ast import formula_from_data, Top
from ve.norms import check_conflict, prove_norm_entailment
from ve.environment import Environment
from ve.errors import VEError
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.softnorms import SoftEnvironment, SoftNormDocument, load_soft_document
from conformance.soft_oracle import check_regenerated
from tests import lean_routes
from tests.test_soft_norms_lean import env, norm, should, ranks
from conformance.wire_contract import choose_combinations, first_fault

ROOT = Path(__file__).resolve().parents[1]
RUST_FIXTURES = ROOT / "conformance/soft_norms_rust.json"
# The accepted seeded trees `main` compares.
TREES = 1000


def generated(seed):
    rng = random.Random(seed)
    ranks = ["high", "middle", "low"][:rng.randrange(4)]
    parties = ["operator", "user"][:rng.randrange(3)]
    mode = rng.choice(["strict", "holistic"])
    block = {"parties": parties, "ranks": ranks,
             "outranks": [[a, b] for a, b in zip(ranks, ranks[1:])],
             "ties": [], "outranking": {"mode": mode}}
    if mode == "holistic":
        block["outranking"]["decided_by"] = "assistant"
    extra = {p: {"arguments": ["assistant"], "description": p} for p in ("q", "u")}
    raw = env(block, extra=extra)
    rules = []
    # Names out of document order and `over` a random subset in random order, so
    # children (sorted by name on both sides) differ from source order.
    count = rng.randrange(1, 7)
    names = [f"n{j}" for j in rng.sample(range(6), count)]
    for name in names:
        pred = rng.choice(["x_required", "x_permitted"])
        soft_mode = rng.choice(["strict", "default"])
        parents = [r["norm"]["name"] for r in rules if r["norm"]["predicate"] == pred
                   and (soft_mode == "strict" or r["norm"].get("mode") == "default")]
        fields = {}
        if soft_mode == "default":
            fields["mode"] = "default"
            fields["exception"] = {"decided_by": "assistant", "sufficient": [],
                                   "necessary": [], "factors": []}
            if rng.randrange(4) == 0:
                fields["exception"][rng.choice(["sufficient", "necessary"])] = [
                    ["unary", "q", ["var", 0]]]
        if ranks and rng.randrange(3):
            fields["rank"] = rng.choice(ranks)
        switches = sorted(p for p in parties if rng.randrange(3) == 0)
        if switches:
            fields["alterable"] = switches
        if soft_mode == "strict" and not switches and rng.randrange(5) == 0:
            fields["hard"] = True
        guard = (["unary", "q", ["var", 0]] if rng.randrange(4) == 0 else ["top"])
        unless = (["unary", "u", ["var", 0]] if rng.randrange(4) == 0 else None)
        over = (rng.sample(parents, rng.randint(1, len(parents)))
                if parents and rng.randrange(3) else [])
        rules.append(norm(name, pred, rng.choice([True, False]), guard=guard,
                          unless=[unless] if unless else [], over=over, **fields))
    return raw, rules


def rust_sources():
    """Identity-bound soft sources and decision assignments for Rust replay."""
    return [
        ("default-live", env(), [should("a", "x_required", True)], []),
        ("default-excepted", env(), [should("a", "x_required", True)], ["soft__excepted__a"]),
        ("hard", env(), [norm("h", "x_required", True, hard=True)], []),
        ("switch-live", env({"parties": ["user"], "outranking": {"mode": "strict"}}),
         [norm("h", "x_required", True, alterable=["user"])], []),
        ("switch-off", env({"parties": ["user"], "outranking": {"mode": "strict"}}),
         [norm("h", "x_required", True, alterable=["user"])], ["soft__off__h__user"]),
        ("three-switches", env({"parties": ["a", "b", "c"], "outranking": {"mode": "strict"}}),
         [norm("h", "x_required", True, alterable=["a", "b", "c"])], ["soft__off__h__c"]),
        ("holistic-high", env(ranks(["high", "low"], "holistic")),
         [should("h", "x_required", True, rank="high"),
          should("l", "x_required", False, rank="low")], []),
        ("holistic-low", env(ranks(["high", "low"], "holistic")),
         [should("h", "x_required", True, rank="high"),
          should("l", "x_required", False, rank="low")],
         ["soft__outweighs__low__high__x_permitted"]),
        ("open-pair", env(), [should("a", "x_required", True),
                               should("b", "x_permitted", False)], []),
    ]


def loop_recheck_reproducers():
    """Independent faults and ordering changes found in the soft loop recheck."""
    missing = norm("a", "x_required", True, mode="default")
    unknown_rank = norm("b", "x_required", True, rank="z")
    yield "missing-exception-before-next-rule", env(), [missing, unknown_rank], "SOFT_MISSING_EXCEPTION"

    # The validation table (8) puts factors (4.14) before exception typing (5.8)
    # and the rule's predicate reference (5.4); these superseded the loop's order.
    for variable in (0, 1):
        exception = {"decided_by": "assistant", "sufficient": [
            ["unary", "x_required", ["var", variable]]],
            "necessary": [], "factors": False}
        yield f"factors-before-exception-typing-{variable}", env(), [
            norm("a", "x_required", True, mode="default", exception=exception)], "SOFT_INVALID_FACTORS"

    unknown_predicate = {"decided_by": "assistant", "sufficient": [],
                         "necessary": [], "factors": False}
    yield "factors-before-predicate-reference", env(), [
        norm("a", "missing", True, mode="default", exception=unknown_predicate)], "SOFT_INVALID_FACTORS"

    for names in (("z", "soft__a"), ("soft__a", "z")):
        raw = env({"parties": ["p"], "outranking": {"mode": "strict"}})
        for name in names:
            raw["vocabulary"]["predicates"][name] = {
                "arguments": ["assistant"], "description": name,
                **({"instruction_of": "missing"} if name == "z" else {})}
        yield f"predicate-order-{names[0]}", raw, [], "SOFT_INVALID_NAME"

    raw = env({"outranking": {"mode": "bad"}})
    raw["profiles"].reverse()
    yield "profile-order-after-soft-block", raw, [], "SOFT_INVALID_OUTRANKING"


def _predicate(name, **fields):
    return {"arguments": ["assistant"], "description": name, **fields}


def _declare(raw, **entries):
    """Add predicate entries W1's fixture builder would reject."""
    raw["vocabulary"]["predicates"].update(entries)
    return raw


def soft2_reproducers():
    """The soft2 loop findings and one instance of each bug class they exposed."""
    long_factor = {"decided_by": "assistant", "sufficient": [], "necessary": [],
                   "factors": ["x" * 201]}
    yield "soft2-factors-before-next-rule-rank", env(), [
        norm("a", "x_required", True, mode="default", exception=long_factor),
        norm("b", "x_required", True, rank="z")], "SOFT_INVALID_FACTORS"
    yield "soft2-next-rule-rank-after-factors", env(), [
        norm("b", "x_required", True, rank="z"),
        norm("a", "x_required", True, mode="default", exception=long_factor)], "SOFT_INVALID_FACTORS"
    # Environment cross references wait for every rule's fields.
    raw = _declare(env({"parties": ["p"], "outranking": {"mode": "strict"}}),
                   z=_predicate("z", instruction_of="missing"))
    yield "soft2-rule-fields-before-environment-references", raw, [
        norm("a", "x_required", True, mode="default", exception=long_factor)], "SOFT_INVALID_FACTORS"
    raw = env({"ranks": ["a", "b"], "outranks": [["a", "b"], ["b", "a"]],
               "outranking": {"mode": "strict"}})
    yield "soft2-rule-references-before-rank-cycle", raw, [
        norm("a", "x_required", True, rank="z")], "SOFT_UNKNOWN_RANK"

    # Malformed declarations are checked after reserved names, never skipped.
    raw = _declare(env(), soft__a=False)
    yield "soft2-malformed-reserved-predicate", raw, [], "SOFT_INVALID_NAME"
    raw = _declare(env({"parties": ["p"], "outranking": {"mode": "strict"}}),
                   soft__a=False, z=_predicate("z", instruction_of="missing"))
    yield "soft2-malformed-reserved-before-party", raw, [], "SOFT_INVALID_NAME"
    raw = _declare(env(), w=False)
    yield "soft2-malformed-predicate", raw, [], "SOFT_INVALID_INPUT"
    raw = _declare(env(), w=False, soft__a=_predicate("soft__a"))
    yield "soft2-reserved-before-malformed-predicate", raw, [], "SOFT_INVALID_NAME"
    raw = _declare(env({"parties": ["p"], "outranking": {"mode": "strict"}}),
                   w=False, z=_predicate("z", instruction_of="missing"))
    yield "soft2-malformed-predicate-before-party", raw, [], "SOFT_INVALID_INPUT"
    raw = _declare(env(), d=_predicate("d", defined={"arguments": ["assistant"], "body": ["top"]}))
    yield "soft2-defined-without-definitions", raw, [], "SOFT_INVALID_INPUT"

    # Profiles are one phase with one code, whatever the decoder that sees them first.
    raw = env()
    raw["profiles"].reverse()
    yield "soft2-profiles-reversed", raw, [], "SOFT_UNSUPPORTED_PROFILE"
    raw = env()
    raw["profiles"].append("soft-norms@0")
    yield "soft2-profiles-duplicate", raw, [], "SOFT_UNSUPPORTED_PROFILE"
    raw = env({"outranking": {"mode": "bad"}})
    raw["profiles"].append("soft-norms@0")
    yield "soft2-declarations-before-profiles", raw, [], "SOFT_INVALID_OUTRANKING"
    raw = env(profiles=("closure@0", "norms@0", "soft-norms@0"))
    yield "soft2-checker-profile", raw, [], "SOFT_UNSUPPORTED_PROFILE"
    raw = env(profiles=("norms@0", "other@0", "soft-norms@0"))
    yield "soft2-unknown-profile", raw, [], "SOFT_UNSUPPORTED_PROFILE"
    raw = _declare(env(profiles=("definitions@0", "norms@0", "soft-norms@0")),
                   d=_predicate("d", defined={"arguments": ["assistant"], "body": ["top"]}))
    yield "soft2-definitions-unsupported", raw, [], "SOFT_UNSUPPORTED_PROFILE"
    raw = env()
    raw["language"] = "ve.core@0.1"
    yield "soft2-language", raw, [], "SOFT_UNSUPPORTED_PROFILE"
    raw = env()
    raw["spec_revision"] = "other"
    yield "soft2-spec-revision", raw, [], "SOFT_UNSUPPORTED_PROFILE"

    # Inherited W1 classes are fixed by the check's position, not the message.
    yield "soft2-parties-limit", env({"parties": [f"p{i}" for i in range(9)],
                                      "outranking": {"mode": "strict"}}), [], "SOFT_RESOURCE_LIMIT"
    yield "soft2-ranks-limit", env({"ranks": [f"r{i}" for i in range(17)],
                                    "outranking": {"mode": "strict"}}), [], "SOFT_RESOURCE_LIMIT"
    yield "soft2-rules-limit", env(), [norm(f"r{i}", "x_required", True) for i in range(257)], \
        "SOFT_RESOURCE_LIMIT"
    yield "soft2-duplicate-rule", env(), [norm("a", "x_required", True),
                                          norm("a", "x_required", False)], "SOFT_DUPLICATE_DECLARATION"
    chain = [norm("r0", "x_required", True)] + [
        norm(f"r{i}", "x_required", True, over=[f"r{i - 1}"]) for i in range(1, 17)]
    yield "soft2-precedence-depth", env(), chain, "SOFT_RESOURCE_LIMIT"
    carve = [["unary", "q", ["var", 0]]] * 8
    yield "soft2-derived-carve-out-count", env(extra={"q": _predicate("q")}), [
        should("a", "x_required", True, unless=carve)], "SOFT_RESOURCE_LIMIT"
    many = {f"p{i:03}": _predicate(f"p{i:03}") for i in range(300)}
    yield "soft2-inherited-vocabulary-limit", _declare(env(), **many), [], "SOFT_INVALID_INPUT"
    yield "soft2-non-string-rank", env(), [norm("a", "x_required", True, rank=7)], \
        "SOFT_INVALID_RULE_FIELDS"
    yield "soft2-closure-guard", env(), [norm("a", "x_required", True, guard=(
        "reach", "plus", ["named", "x_required"], ["var", 0], ["var", 0]), rank="z")], \
        "SOFT_INVALID_INPUT"


def _doubled(times, leaf=("top",)):
    """A balanced `and` tree of 2 ** (times + 1) - 1 nodes, depth times + 1."""
    tree = list(leaf)
    for _ in range(times):
        tree = ["and", tree, tree]
    return tree


def _regulated(raw, name, **fields):
    reg = raw["vocabulary"]["predicates"][name]["regulated"]
    for key, value in fields.items():
        if value is _DELETE:
            del reg[key]
        else:
            reg[key] = value
    return raw


def soft3_reproducers():
    """The soft3 loop findings and the other instances of their classes."""
    long_factor = {"decided_by": "assistant", "sufficient": [], "necessary": [],
                   "factors": ["x" * 201]}
    # W1's act-role and permission-dual checks are declaration checks (2.3): they
    # precede the profile phase and every rule.
    later = {
        "profiles": lambda raw: (raw["profiles"].reverse(), [])[1],
        "factors": lambda raw: [norm("a", "x_required", True, mode="default",
                                     exception=long_factor)],
        "rank": lambda raw: [norm("a", "x_required", True, rank="z")],
    }
    duals = {
        "missing-dual": lambda raw: _regulated(raw, "x_required", permission="missing"),
        "dual-not-permission": lambda raw: _declare(
            _regulated(raw, "x_required", permission="w"), w=_predicate("w")),
        "dual-sort": lambda raw: _declare(
            _regulated(raw, "x_required", permission="y_permitted"),
            y_permitted=_predicate("y_permitted", arguments=["user"], regulated={
                "role": "permission", "default": "allow", "act": "{0} do x"})),
        "dual-act": lambda raw: _regulated(raw, "x_permitted", act="{0} do y"),
        "undeclared-dual": lambda raw: _regulated(raw, "x_required", permission=_DELETE),
        "act-role": lambda raw: _declare(raw, y_required=_predicate("y_required", regulated={
            "role": "obligation", "default": "deny", "act": "{0} do x", "permission": "x_permitted"})),
        "permission-act-role": lambda raw: _declare(raw, y_permitted=_predicate("y_permitted", regulated={
            "role": "permission", "default": "deny", "act": "{0} do x"})),
    }
    for fault, declare in duals.items():
        for after, rules in later.items():
            raw = declare(env())
            yield f"soft3-{fault}-before-{after}", raw, rules(raw), "SOFT_INVALID_INPUT"

    # Python's node budgets, at each position the table gives them: the decoder's
    # per formula (4.2, 4.13), the checker's per rule over its guard, carve-outs
    # and exception conditions (5.7, 5.8), the W1 checker's over the whole of T
    # (6.5) and of T' (6.10), and each generated premise's (6.11).
    big = _doubled(13)  # 16,383 nodes
    yield "soft3-guard-nodes-before-rank", env(), [
        norm("a", "x_required", True, guard=big, rank="missing")], "SOFT_INVALID_INPUT"
    yield "soft3-guard-nodes", env(), [norm("a", "x_required", True, guard=big)], "SOFT_INVALID_INPUT"
    yield "soft3-carve-out-nodes-before-rank", env(), [
        norm("a", "x_required", True, unless=[big], rank="missing")], "SOFT_INVALID_INPUT"
    yield "soft3-guard-nodes-before-next-rule", env(), [
        norm("a", "x_required", True, guard=big),
        norm("b", "x_required", True, extra=1)], "SOFT_INVALID_INPUT"
    for kind in ("sufficient", "necessary"):
        yield f"soft3-{kind}-nodes-before-rank", env(), [
            norm("a", "x_required", True, mode="default", exception=_exception(kind, big),
                 rank="missing")], "SOFT_INVALID_INPUT"
    # Term nodes count: 4,096 atoms under 4,095 conjunctions is 12,287 nodes.
    atoms = _doubled(12, ("unary", "x_permitted", ["var", 0]))
    yield "soft3-term-nodes-before-rank", env(), [
        norm("a", "x_required", True, guard=atoms, rank="missing")], "SOFT_INVALID_INPUT"
    half = _doubled(11)  # 4,095 nodes
    yield "soft3-rule-nodes-guard-and-carve-outs", env(), [
        norm("a", "x_required", True, guard=["and", half, half], unless=[half, half])], \
        "SOFT_INVALID_INPUT"
    condition = _doubled(11, ("unary", "x_permitted", ["var", 0]))  # 6,143 nodes
    yield "soft3-rule-nodes-before-exception-condition", env(), [
        should("a", "x_required", True, guard=half, exception=_exception("sufficient", condition))], \
        "SOFT_INVALID_INPUT"
    yield "soft3-rule-nodes-before-next-rule-condition", env(), [
        should("a", "x_required", True, guard=half, exception=_exception("sufficient", condition)),
        should("b", "x_required", True, exception=_exception("sufficient", ["unary", "x_permitted", ["var", 0]]))], \
        "SOFT_INVALID_INPUT"
    yield "soft3-rule-nodes-guard-and-condition", env(), [
        should("a", "x_required", True, exception=_exception("sufficient", _exact(10000)))], \
        "SOFT_INVALID_INPUT"
    three = [norm(f"r{i}", "x_required", True, guard=half) for i in range(3)]
    yield "soft3-document-nodes", env(), three, "SOFT_RESOURCE_LIMIT"
    cycle = deepcopy(three)
    cycle[0]["norm"]["over"], cycle[2]["norm"]["over"] = ["r2"], ["r0"]
    yield "soft3-document-nodes-before-precedence-cycle", env(), cycle, "SOFT_RESOURCE_LIMIT"
    over_hard = deepcopy(three)
    over_hard[2] = should("r2", "x_required", True, guard=half, over=["r0"])
    yield "soft3-document-nodes-before-soft-over-hard", env(), over_hard, "SOFT_RESOURCE_LIMIT"
    for n in (9990, 10000):
        yield f"soft3-derived-nodes-{n}", env(), [should("a", "x_required", True, guard=_exact(n))], \
            "SOFT_RESOURCE_LIMIT"
    yield "soft3-premise-nodes", env(), [
        should("a", "x_required", True, exception=_exception("sufficient", _exact(9998)))], \
        "SOFT_RESOURCE_LIMIT"
    for depth in (63, 64):
        yield f"soft3-premise-depth-{depth}", env(), [
            should("a", "x_required", True, exception=_exception("sufficient", _nested(depth)))], \
            "SOFT_RESOURCE_LIMIT"


def _exception(kind, formula):
    return {"decided_by": "assistant", "sufficient": [], "necessary": [], "factors": [], kind: [formula]}


def _exact(n):
    """A formula of exactly n nodes and logarithmic depth."""
    if n == 1:
        return ["top"]
    if n == 2:
        return ["not", ["top"]]
    left = (n - 1) // 2
    return ["and", _exact(left), _exact(n - 1 - left)]


def _nested(depth):
    formula = ["top"]
    for _ in range(depth - 1):
        formula = ["not", formula]
    return formula


def soft3_accepted():
    """Sources at each budget that both validators accept and that elaborate.

    A layer states a rule's guard twice (selected, and silent), and the layers
    share one checker's budget with the conclusion of an entailment query (6.15),
    so the layer budgets bind before the source and document budgets: the largest
    guard is 4970 nodes for a strict rule and 4953 for a default one. The soft
    premises share one budget with the rest of background′ (6.14)."""
    return [
        ("strict-guard-4970", env(), [norm("a", "x_required", True, guard=_exact(4970))]),
        ("default-guard-4953", env(), [should("a", "x_required", True, guard=_exact(4953))]),
        ("document-guards-2481-2482", env(), [norm("r0", "x_required", True, guard=_exact(2481)),
                                              norm("r1", "x_required", True, guard=_exact(2482))]),
        ("premise-nodes-9990", env(), [
            should("a", "x_required", True, exception=_exception("sufficient", _exact(9990)))]),
        ("premise-depth-62", env(), [
            should("a", "x_required", True, exception=_exception("sufficient", _nested(62)))]),
        ("strict-guard-depth-56", env(), [norm("a", "x_required", True, guard=_nested(56))]),
        ("default-guard-depth-56", env(), [should("a", "x_required", True, guard=_nested(56))]),
        ("derived-guard-wrappers-43", env(), _strict_under_default(43)),
    ]


def _strict_under_default(wrappers):
    """A strict rule's guard, `wrappers` negations deep, read by a default rule's
    derived carve-out (through `blocked`) and by the predicate's layer."""
    guard = ["top"]
    for _ in range(wrappers):
        guard = ["not", guard]
    return [norm("s", "x_required", True, guard=guard), should("d", "x_required", True)]


def soft_limits_reproducers():
    """soft3-loop.final.md and the directive's class: a derived structure beyond a limit.

    Each was accepted by at least one validator before and could not be
    elaborated; each is now rejected by both at the same check."""
    half = _doubled(11)
    # Finding 1: the derived carve-out reaches depth 65 (6.9, both validators).
    yield "soft-limits-derived-wrappers-54", env(), _strict_under_default(54), "SOFT_RESOURCE_LIMIT"
    # 53 negations: the derived carve-out fits, but the layer nests it past depth 64 (6.12).
    yield "soft-limits-layer-wrappers-53", env(), _strict_under_default(53), "SOFT_RESOURCE_LIMIT"
    yield "soft-limits-layer-wrappers-44", env(), _strict_under_default(44), "SOFT_RESOURCE_LIMIT"
    # Finding 2: the four formerly accepted fixtures whose layers exceed MAX_NODES.
    yield "soft-limits-guard-8191", env(), [
        norm("a", "x_required", True, guard=["and", half, half])], "SOFT_RESOURCE_LIMIT"
    yield "soft-limits-strict-guard-10000", env(), [
        norm("a", "x_required", True, guard=_exact(10000))], "SOFT_RESOURCE_LIMIT"
    yield "soft-limits-default-guard-9980", env(), [
        should("a", "x_required", True, guard=_exact(9980))], "SOFT_RESOURCE_LIMIT"
    yield "soft-limits-document-nodes-9999", env(), [
        norm("r0", "x_required", True, guard=_exact(4999)),
        norm("r1", "x_required", True, guard=_exact(5000))], "SOFT_RESOURCE_LIMIT"
    # One past each accepted boundary of soft3_accepted.
    yield "soft-limits-strict-guard-4982", env(), [
        norm("a", "x_required", True, guard=_exact(4982))], "SOFT_RESOURCE_LIMIT"
    yield "soft-limits-default-guard-4965", env(), [
        should("a", "x_required", True, guard=_exact(4965))], "SOFT_RESOURCE_LIMIT"
    yield "soft-limits-document-guards-2488", env(), [
        norm("r0", "x_required", True, guard=_exact(2487)),
        norm("r1", "x_required", True, guard=_exact(2488))], "SOFT_RESOURCE_LIMIT"
    yield "soft-limits-strict-guard-depth-57", env(), [
        norm("a", "x_required", True, guard=_nested(57))], "SOFT_RESOURCE_LIMIT"
    yield "soft-limits-default-guard-depth-57", env(), [
        should("a", "x_required", True, guard=_nested(57))], "SOFT_RESOURCE_LIMIT"
    # E′ (6.4): the decision predicates are within MAX_IDENTIFIER_BYTES and
    # MAX_PREDICATES; Lean used to accept an E′ that no environment decoder loads.
    yield "soft-limits-excepted-name", env(), [should("a" * 49, "x_required", True)], \
        "SOFT_RESOURCE_LIMIT"
    yield "soft-limits-off-name", env({"parties": ["p" * 30], "outranking": {"mode": "strict"}}), [
        norm("r" * 30, "x_required", True, alterable=["p" * 30])], "SOFT_RESOURCE_LIMIT"
    yield "soft-limits-outweighs-name", env(ranks(["h" * 20, "l" * 20], "holistic")), [
        should("a", "x_required", True, rank="h" * 20),
        should("b", "x_required", False, rank="l" * 20)], "SOFT_RESOURCE_LIMIT"
    many = {f"e{i}": {"arguments": ["assistant"], "description": "e"} for i in range(252)}
    yield "soft-limits-extended-vocabulary", env(extra=many), [
        should(f"n{i}", "x_required", True) for i in range(3)], "SOFT_RESOURCE_LIMIT"


def _plain_chain(count, guard_of, extra_rules=()):
    """Plain deny predicates p0 … p{count-1}; a positive strict rule on each, guarded by
    `top` for p0 and `guard_of(<predecessor atom>)` after, then `extra_rules`."""
    extra = {f"p{i}": _predicate(f"p{i}", regulated={"role": "plain", "default": "deny"})
             for i in range(count)}
    rules = [norm(f"r{i}", f"p{i}", True,
                  guard=["top"] if i == 0 else guard_of(["unary", f"p{i - 1}", ["var", 0]]))
             for i in range(count)]
    return env(extra=extra), rules + list(extra_rules)


def _twice(atom):
    return ["and", atom, atom]


def _negations(times):
    def wrap(formula):
        for _ in range(times):
            formula = ["not", formula]
        return formula
    return wrap


def _opposed(predicate):
    """Two opposing default rules on one predicate: a colliding pair, one coherence premise."""
    return [should("da", predicate, True), should("db", predicate, False)]


def _diamond(levels, width, default=False):
    """`levels` ranks of `width` strict rules on x_required, each over every rule of
    the level before: width ** (levels - 1) precedence paths from the top."""
    rules = [norm(f"r{i}x{j}", "x_required", True,
                  over=[f"r{i - 1}x{m}" for m in range(width)] if i else [])
             for i in range(levels) for j in range(width)]
    return env(), rules + ([should("d", "x_required", True)] if default else [])


def _rank_tower(ranks_count, per_rank, mode="strict", dense=True):
    """Default rules of alternating sign at every rank; `dense` declares every pair of
    the order, so the rank graph has 2 ** (ranks_count - 2) paths from the top."""
    names = [f"k{i}" for i in range(ranks_count)]
    edges = ([[a, b] for i, a in enumerate(names) for b in names[i + 1:]] if dense
             else [[a, b] for a, b in zip(names, names[1:])])
    block = {"ranks": names, "outranks": edges, "outranking": {"mode": mode}}
    if mode == "holistic":
        block["outranking"]["decided_by"] = "assistant"
    return env(block), [should(f"n{i}x{j}", "x_required", (i + j) % 2 == 0, rank=names[i])
                        for i in range(ranks_count) for j in range(per_rank)]


def _dual_outcomes(count):
    """A doubling chain p0 … p{count-1}, and rules requiring x and forbidding it
    guarded by the chain's last predicate: the pair target states both expansions."""
    atom = ["unary", f"p{count - 1}", ["var", 0]]
    return _plain_chain(count, _twice, [norm("a", "x_required", True, guard=atom),
                                        norm("b", "x_permitted", False, guard=atom)])


def soft4_aggregate_reproducers():
    """soft4-looprecheck1.final.md B1: two accepted fixtures whose elaboration
    fits formula by formula but not as the entailment route types it, one
    checker over a list: the layers of strict-guard-4981 are 10,021 nodes, and
    the background′ of premise-nodes-9996 is 10,006. Each is now rejected at the
    aggregate row, with the sources one past each new accepted boundary."""
    yield "soft4-layers-strict-guard-4981", env(), [
        norm("a", "x_required", True, guard=_exact(4981))], "SOFT_RESOURCE_LIMIT"
    yield "soft4-background-premise-nodes-9996", env(), [
        should("a", "x_required", True, exception=_exception("sufficient", _exact(9996)))], \
        "SOFT_RESOURCE_LIMIT"
    yield "soft4-layers-strict-guard-4971", env(), [
        norm("a", "x_required", True, guard=_exact(4971))], "SOFT_RESOURCE_LIMIT"
    yield "soft4-layers-default-guard-4954", env(), [
        should("a", "x_required", True, guard=_exact(4954))], "SOFT_RESOURCE_LIMIT"
    yield "soft4-layers-document-guards-2481-2483", env(), [
        norm("r0", "x_required", True, guard=_exact(2481)),
        norm("r1", "x_required", True, guard=_exact(2483))], "SOFT_RESOURCE_LIMIT"
    yield "soft4-background-premise-nodes-9991", env(), [
        should("a", "x_required", True, exception=_exception("sufficient", _exact(9991)))], \
        "SOFT_RESOURCE_LIMIT"
    # Two exception premises that fit one by one but not together.
    yield "soft4-background-two-premises", env(), [
        should("a", "x_required", True, exception={
            **_exception("sufficient", _exact(4995)), "necessary": [_exact(4995)]})], \
        "SOFT_RESOURCE_LIMIT"


def soft4_reproducers():
    """soft4-looprecheck1.final.md B3 and its class: a derived structure whose
    unfolding is exponential in the source (outcome expansion across layers,
    precedence paths, dominance over ranks), built before its limit was checked.

    Python raised RecursionError or ran for hours and Lean ran for hours; each is
    now sized from per-rule tables and rejected at its check by both."""
    raw, rules = _plain_chain(26, _negations(40), _opposed("p25"))
    yield "soft4-coherence-negations-26", raw, rules, "SOFT_RESOURCE_LIMIT"
    # B2: each strict rule guarded by its predecessor twice; the p10 conflict target
    # expands to 18,427 nodes, which both validators accepted and no decoder loads.
    raw, rules = _plain_chain(11, _twice)
    yield "soft4-target-doubling-11", raw, rules, "SOFT_RESOURCE_LIMIT"
    raw, rules = _plain_chain(40, _twice)
    yield "soft4-target-doubling-40", raw, rules, "SOFT_RESOURCE_LIMIT"
    # The pair target `r->m` states both outcomes: each fits on its own, the pair does not.
    raw, rules = _dual_outcomes(10)
    yield "soft4-pair-target-10", raw, rules, "SOFT_RESOURCE_LIMIT"
    raw, rules = _plain_chain(40, _twice, _opposed("p39"))
    yield "soft4-coherence-doubling-40", raw, rules, "SOFT_RESOURCE_LIMIT"
    raw, rules = _diamond(15, 16)
    yield "soft4-layer-diamond-15x16", raw, rules, "SOFT_RESOURCE_LIMIT"
    raw, rules = _diamond(15, 16, default=True)
    yield "soft4-derived-diamond-15x16", raw, rules, "SOFT_RESOURCE_LIMIT"
    for mode in ("strict", "holistic"):
        raw, rules = _rank_tower(16, 2, mode)
        yield f"soft4-derived-rank-tower-{mode}", raw, rules, "SOFT_RESOURCE_LIMIT"
    raw, rules = _rank_tower(16, 15, "holistic")
    yield "soft4-vocabulary-rank-tower", raw, rules, "SOFT_RESOURCE_LIMIT"


def soft4_near_limit():
    """Each exponential family swept across its limit, so both sides of every boundary
    are compared: coherence premises by nodes and by depth, conflict targets and
    pair targets, layers and derived carve-outs over precedence diamonds, derived
    carve-outs over rank towers."""
    for count in range(6, 12):
        yield (f"soft4-near-doubling-{count}", *_plain_chain(count, _twice, _opposed(f"p{count - 1}")))
        yield f"soft4-near-target-{count}", *_plain_chain(count, _twice)
        yield f"soft4-near-pair-target-{count}", *_dual_outcomes(count)
    for times in range(6, 12):
        yield (f"soft4-near-negations-{times}", *_plain_chain(5, _negations(times), _opposed("p4")))
    for levels, width in ((3, 3), (4, 3), (5, 3), (6, 3), (4, 4), (5, 4), (3, 6)):
        for default in (False, True):
            yield (f"soft4-near-diamond-{levels}x{width}{'-default' if default else ''}",
                   *_diamond(levels, width, default))
    for ranks_count in range(3, 10):
        for mode in ("strict", "holistic"):
            yield (f"soft4-near-rank-tower-{ranks_count}-{mode}", *_rank_tower(ranks_count, 1, mode))


def soft_over_reproducers():
    """soft4-loop.final B, class: `over` is a set of rule names (3.2). Python merged a
    repeated name and Lean kept every copy, so the two sized and built different
    derived formulas. A repeat is now rejected at 4.2, after W1's field decoding
    and before the rule's soft fields (4.3 on) and every cross reference (5)."""
    a, d = norm("a", "x_required", True), should("d", "x_required", True)
    code = "SOFT_INVALID_INPUT"
    for times in (2, 41):
        yield (f"soft-over-repeat-{times}", env(),
               [a, norm("b", "x_required", False, over=["a"] * times), d], code)
    yield ("soft-over-repeat-apart", env(),
           [a, norm("c", "x_required", True), norm("b", "x_required", False, over=["a", "c", "a"]), d], code)
    yield ("soft-over-repeat-before-mode", env(),
           [a, norm("b", "x_required", False, over=["a", "a"], mode="other"), d], code)
    yield ("soft-over-repeat-before-predicate", env(),
           [a, norm("b", "u", False, over=["zz", "zz"]), d], code)
    yield ("soft-over-repeat-after-earlier-rule", env({"parties": ["p", "q"], "outranking": {"mode": "strict"}}),
           [norm("a", "x_required", True, alterable=["q", "p"]),
            norm("b", "x_required", False, over=["a", "a"]), d], "SOFT_INVALID_ALTERABLE")
    yield ("soft-over-repeat-default", env(),
           [should("a", "x_required", True), should("b", "x_required", False, over=["a", "a"])], code)


def soft_over_accepted():
    """soft4-loop.final B, class: distinct children out of name order. Both
    validators sort a rule's children by name wherever a derived formula is
    built, sized or regenerated, whatever the children's document order and the
    order of each `over` list."""
    bottom, d = ("bottom",), should("d", "x_required", True)
    yield ("soft-over-children-reversed", env(),
           [norm("a", "x_required", True), norm("c", "x_required", True, unless=[bottom], over=["a"]),
            norm("b", "x_required", False, over=["a"]), d])
    yield ("soft-over-list-reversed", env(),
           [norm("c", "x_required", True), norm("b", "x_required", False, unless=[bottom]),
            norm("a", "x_required", True), norm("g", "x_required", False, over=["c", "b", "a"]),
            norm("f", "x_required", True, unless=[bottom, bottom], over=["c", "a"]), d])
    levels = [norm("r", "x_required", True)]
    for depth, names in enumerate((["m3", "m1", "m2"], ["k2", "k0", "k1"])):
        parents = [n["norm"]["name"] for n in levels[-3:]] if depth else ["r"]
        levels += [norm(n, "x_required", i % 2 == 0, unless=[bottom] * i, over=parents[::-1])
                   for i, n in enumerate(names)]
    yield "soft-over-diamond-shuffled", env(), [*levels, d]
    yield ("soft-over-defaults-shuffled", env(ranks(["hi", "lo"], "holistic")),
           [should("z", "x_required", True, rank="hi"),
            should("y", "x_required", False, rank="lo", over=["z"]),
            should("x", "x_required", True, unless=[bottom], rank="lo", over=["z"]),
            norm("w", "x_permitted", False), norm("v", "x_permitted", True, unless=[bottom], over=["w"]),
            norm("u", "x_permitted", False, over=["w"])])


def near_limit_sources(count=120, seed=0):
    """Seeded sources near every budget: deep guards, many exception
    conditions, large guards (the 8191-node doubled tree among them), shared
    guards under default rules, and ranked collisions."""
    rng = random.Random(seed)
    extra = {"q": {"arguments": ["assistant"], "description": "q"}}
    leaves = ('["top"]', '["unary", "q", ["var", 0]]')

    def leaf():
        return json.loads(rng.choice(leaves))

    def formula():
        kind = rng.randrange(5)
        if kind == 0:
            return _nested(rng.randint(40, 64))
        if kind == 1:
            return _exact(rng.choice([rng.randint(2400, 2600), rng.randint(4900, 5050),
                                      rng.randint(9900, 10000)]))
        if kind == 2:
            return ["and", _doubled(11), _doubled(11)]
        if kind == 3:
            return _doubled(rng.randint(8, 12))
        return _exact(rng.randint(1, 64))

    def json_leaf(tree):
        return json.loads(json.dumps(tree).replace('["top"]', json.dumps(leaf()), 1))

    levels = ["high", "middle", "low"]
    for index in range(count):
        mode = rng.choice(["strict", "holistic"])
        block = {"ranks": levels, "outranks": [["high", "middle"], ["middle", "low"]],
                 "ties": [], "outranking": {"mode": mode}, "parties": ["user"]}
        if mode == "holistic":
            block["outranking"]["decided_by"] = "assistant"
        raw = env(block, extra=extra)
        rules = []
        for i in range(rng.randint(1, 4)):
            pred = rng.choice(["x_required", "x_permitted"])
            fields = {}
            if rng.randrange(2):
                conditions = {"sufficient": [], "necessary": []}
                for _ in range(rng.choice([0, 1, 2, 8, 24])):
                    conditions[rng.choice(["sufficient", "necessary"])].append(
                        json_leaf(formula()) if rng.randrange(8) == 0 else leaf())
                fields = {"mode": "default", "rank": rng.choice(levels),
                          "exception": {"decided_by": "assistant", "factors": [], **conditions}}
            elif rng.randrange(3) == 0:
                fields["alterable"] = ["user"]
            guard = json_leaf(formula()) if rng.randrange(2) else leaf()
            unless = [leaf() for _ in range(rng.choice([0, 0, 1, 7, 8]))]
            rules.append(norm(f"n{i}", pred, rng.choice([True, False]),
                              guard=guard, unless=unless, **fields))
        yield f"near-limit-{seed}-{index}", raw, rules


def near_limit_cases():
    """Every accepted fixture, the limits reproducers and the near-limit generator."""
    raw, rules = multi_fault_base()
    return [*soft3_accepted(), *((name, raw, rules) for name, raw, rules, _ in rust_sources()),
            ("multi-fault-base", raw, rules),
            *((name, raw, rules) for name, raw, rules, _ in soft_limits_reproducers()),
            *((name, raw, rules) for name, raw, rules, _ in soft4_reproducers()),
            *((name, raw, rules) for name, raw, rules, _ in soft4_aggregate_reproducers()),
            *soft4_near_limit(), *soft_over_accepted(), *near_limit_sources()]


def smallest_queries(soft):
    """Accepted means usable (6.14, 6.15): the smallest entailment query on the
    elaboration, `⊢ ⊤`, and a proof attempt for every conflict target type-check
    within the checker's limits; a ResourceLimit here fails the comparison."""
    prove_norm_entailment(soft.elaborated, (), Top(), max_steps=50)
    check_conflict(soft.elaborated, prove=True, tableau_steps=50)


def compare_near_limit(sources):
    """accepted => Lean accepts, `check_regenerated` (the public elaboration
    check) passes and the smallest queries run; rejected => Lean rejects with
    the same code. Returns the accepted and rejected counts."""
    expected = []
    for name, raw, rules in sources:
        try:
            expected.append((name, load_soft_document(raw, rules), None))
        except VEError as exc:
            expected.append((name, None, exc.code))
    wire = [{"id": name, "kind": "soft-elaborate", "environment": raw, "norms": rules}
            for name, raw, rules in sources]
    rows = lean_routes.rows("soft-norms", wire)
    if len(rows) != len(sources):
        raise AssertionError("Lean returned the wrong near-limit row count")
    accepted = 0
    for (name, soft, code), row in zip(expected, rows):
        if soft is None:
            if row.get("status") != "error" or row.get("code") != code:
                raise AssertionError((name, code, row))
            continue
        if row.get("status") != "ok":
            raise AssertionError((name, "accepted by Python", row))
        check_regenerated(soft, row)
        smallest_queries(soft)
        accepted += 1
    return accepted, len(sources) - accepted


# The multi-fault generator. A valid base source, then faults each tagged with its
# position in the validation table (8) and its code. Faults in one group touch the
# same field and are never combined; otherwise faults are independent, so the
# expected diagnostic is the fault with the least table position.

def multi_fault_base():
    block = {"parties": ["p", "q"], "ranks": ["a", "b", "c"], "outranks": [["a", "b"]],
             "ties": [["b", "c"]], "outranking": {"mode": "strict"},
             "exception_decider": "assistant"}
    raw = _declare(env(block, extra={"u": _predicate("u")}), q=_predicate("q", instruction_of="p"))
    exception = {"decided_by": "assistant", "sufficient": [["unary", "q", ["var", 0]]],
                 "necessary": [], "factors": ["f"]}
    rules = [norm("a0", "x_required", True, mode="default", rank="a", exception=exception),
             norm("b1", "x_permitted", False, alterable=["p", "q"]),
             norm("c2", "x_required", False, mode="default", rank="b", over=["a0"],
                  exception={"sufficient": [], "necessary": [], "factors": []}),
             norm("d3", "x_permitted", True, mode="default", exception=dict(exception))]
    return raw, rules


def _set(path, value):
    def apply(raw, rules):
        target = raw if path[0] == "env" else rules
        for key in path[1:-1]:
            target = target[key]
        if value is _DELETE:
            del target[path[-1]]
        else:
            target[path[-1]] = deepcopy(value)
    return apply


_DELETE = object()


def _profiles(update):
    def apply(raw, rules):
        raw["profiles"] = update(raw["profiles"])
    return apply


def _carve_outs(indices, formula):
    def apply(raw, rules):
        for i in indices:
            rules[i]["norm"]["unless"] = [deepcopy(formula)]
    return apply


def multi_faults():
    """(name, group, table position, code, mutation)."""
    E, R = ("env",), ("rules",)
    V, S = E + ("vocabulary",), E + ("vocabulary", "soft")
    P = V + ("predicates",)
    rule = lambda i, *path: R + (i, "norm") + path
    return [
        ("language", "language", (1, 2), "SOFT_UNSUPPORTED_PROFILE", _set(E + ("language",), "x")),
        ("revision", "revision", (1, 4), "SOFT_UNSUPPORTED_PROFILE", _set(E + ("spec_revision",), "x")),
        ("vocabulary-field", "vocabulary", (1, 5), "SOFT_INVALID_INPUT", _set(V + ("extra",), {})),
        ("profiles-shape", "profiles", (1, 3), "SOFT_UNSUPPORTED_PROFILE", _set(E + ("profiles",), "x")),
        ("reserved-name", "soft__a", (2, 1, "soft__a"), "SOFT_INVALID_NAME",
         _set(P + ("soft__a",), False)),
        ("reserved-name-z", "soft__z", (2, 1, "soft__z"), "SOFT_INVALID_NAME",
         _set(P + ("soft__z",), _predicate("soft__z"))),
        ("instruction-type", "q-instruction", (2, 2), "SOFT_INVALID_INPUT",
         _set(P + ("q", "instruction_of"), 3)),
        ("malformed-predicate", "w", (2, 3), "SOFT_INVALID_INPUT", _set(P + ("w",), False)),
        ("missing-dual", "x-dual", (2, 3), "SOFT_INVALID_INPUT",
         _set(P + ("x_required", "regulated", "permission"), "missing")),
        ("act-role", "y", (2, 3), "SOFT_INVALID_INPUT", _set(P + ("y_permitted",), _predicate(
            "y_permitted", regulated={"role": "permission", "default": "deny", "act": "{0} do x"}))),
        ("block-field", "block", (2, 4), "SOFT_INVALID_BLOCK", _set(S + ("extra",), 1)),
        ("parties-shape", "parties", (2, 5), "SOFT_INVALID_ARRAY", _set(S + ("parties",), "p")),
        ("party-name", "parties", (2, 7), "SOFT_INVALID_NAME", _set(S + ("parties",), ["p", "Q!"])),
        ("party-repeat", "parties", (2, 7), "SOFT_DUPLICATE_DECLARATION",
         _set(S + ("parties",), ["p", "q", "p"])),
        ("rank-repeat", "ranks", (2, 8), "SOFT_DUPLICATE_DECLARATION",
         _set(S + ("ranks",), ["a", "b", "c", "a"])),
        ("outranking-mode", "outranking", (2, 9), "SOFT_INVALID_OUTRANKING",
         _set(S + ("outranking",), {"mode": "other"})),
        ("strict-decider", "outranking", (2, 10), "SOFT_STRICT_OUTRANKING_DECIDER",
         _set(S + ("outranking",), {"mode": "strict", "decided_by": "x"})),
        ("holistic-decider", "outranking", (2, 12), "SOFT_MISSING_DECIDER",
         _set(S + ("outranking",), {"mode": "holistic"})),
        ("exception-decider", "exception-decider", (2, 14), "SOFT_INVALID_DECIDER",
         _set(S + ("exception_decider",), "")),
        ("outranks-pair", "outranks", (2, 16), "SOFT_INVALID_OUTRANKS_PAIR",
         _set(S + ("outranks",), [["a", "b"], ["a", "a"]])),
        ("ties-pair", "ties", (2, 17), "SOFT_INVALID_TIES_PAIR",
         _set(S + ("ties",), [["b", "c"], ["b", "c"]])),
        ("profiles-order", "profiles", (3, 1), "SOFT_UNSUPPORTED_PROFILE", _profiles(lambda ps: ps[::-1])),
        ("profiles-repeat", "profiles", (3, 1), "SOFT_UNSUPPORTED_PROFILE",
         _profiles(lambda ps: sorted(ps + ["norms@0"]))),
        ("profile-unknown", "profiles", (3, 2), "SOFT_UNSUPPORTED_PROFILE",
         _profiles(lambda ps: sorted(ps + ["zz@0"]))),
        ("profile-norms", "profiles", (3, 3), "SOFT_UNSUPPORTED_PROFILE",
         _profiles(lambda ps: [p for p in ps if p != "norms@0"])),
        ("profile-checker", "profiles", (3, 4), "SOFT_UNSUPPORTED_PROFILE",
         _profiles(lambda ps: sorted(ps + ["closure@0"]))),
        *[fault for i in range(4) for fault in (
            (f"r{i}-field", f"r{i}-extra", (4, i, 1), "SOFT_INVALID_INPUT", _set(rule(i, "extra"), 1)),
            (f"r{i}-sign", f"r{i}-sign", (4, i, 2), "SOFT_INVALID_INPUT", _set(rule(i, "sign"), "yes")),
            (f"r{i}-over-repeat", f"r{i}-over", (4, i, 2, 1), "SOFT_INVALID_INPUT",
             _set(rule(i, "over"), ["a0", "a0"])),
            (f"r{i}-guard-nodes", f"r{i}-guard", (4, i, 2), "SOFT_INVALID_INPUT",
             _set(rule(i, "guard"), _doubled(13))),
            (f"r{i}-mode", f"r{i}-mode", (4, i, 3), "SOFT_INVALID_RULE_FIELDS", _set(rule(i, "mode"), "x")),
            (f"r{i}-rank-type", f"r{i}-rank", (4, i, 4), "SOFT_INVALID_RULE_FIELDS",
             _set(rule(i, "rank"), 7)),
            (f"r{i}-alterable", f"r{i}-alterable", (4, i, 5), "SOFT_INVALID_ALTERABLE",
             _set(rule(i, "alterable"), ["q", "p"])),
            (f"r{i}-hard-type", f"r{i}-hard", (4, i, 6), "SOFT_INVALID_RULE_FIELDS",
             _set(rule(i, "hard"), "yes")),
            (f"r{i}-rank", f"r{i}-rank", (5, 4, i, 5), "SOFT_UNKNOWN_RANK", _set(rule(i, "rank"), "z")),
            (f"r{i}-party", f"r{i}-alterable", (5, 4, i, 6), "SOFT_UNKNOWN_PARTY",
             _set(rule(i, "alterable"), ["zz"])),
            (f"r{i}-guard", f"r{i}-guard", (5, 4, i, 7), "SOFT_INVALID_INPUT",
             _set(rule(i, "guard"), ["unary", "nosuch", ["var", 0]])),
            (f"r{i}-predicate", f"r{i}-predicate", (5, 4, i, 4), "SOFT_INVALID_INPUT",
             _set(rule(i, "predicate"), "u")),
            (f"r{i}-over", f"r{i}-over", (5, 4, i, 9), "SOFT_INVALID_INPUT",
             _set(rule(i, "over"), ["nosuch"])),
        )],
        *[fault for i in (0, 2, 3) for fault in (
            (f"r{i}-hard", f"r{i}-hard", (4, i, 7), "SOFT_HARD_CONSTRAINT", _set(rule(i, "hard"), True)),
            (f"r{i}-exception", f"r{i}-factors", (4, i, 9), "SOFT_MISSING_EXCEPTION",
             _set(rule(i, "exception", "factors"), _DELETE)),
            (f"r{i}-sufficient", f"r{i}-sufficient", (4, i, 13), "SOFT_EXCEPTION_ARRAY",
             _set(rule(i, "exception", "sufficient"), {})),
            (f"r{i}-condition-syntax", f"r{i}-sufficient", (4, i, 13), "SOFT_INVALID_INPUT",
             _set(rule(i, "exception", "sufficient"), [["bogus"]])),
            (f"r{i}-factors", f"r{i}-factors", (4, i, 14), "SOFT_INVALID_FACTORS",
             _set(rule(i, "exception", "factors"), ["x" * 201])),
            (f"r{i}-condition", f"r{i}-sufficient", (5, 4, i, 8), "SOFT_INVALID_EXCEPTION_CONDITION",
             _set(rule(i, "exception", "sufficient"), [["unary", "x_permitted", ["var", 0]]])),
        )],
        *[fault for i in (0, 3) for fault in (
            (f"r{i}-decider-type", f"r{i}-decider", (4, i, 10), "SOFT_INVALID_DECIDER",
             _set(rule(i, "exception", "decided_by"), 3)),
            (f"r{i}-decider", f"r{i}-decider", (4, i, 12), "SOFT_INVALID_DECIDER",
             _set(rule(i, "exception", "decided_by"), "")),
        )],
        ("r1-strict-exception", "r1-exception", (4, 1, 8), "SOFT_STRICT_EXCEPTION",
         _set(rule(1, "exception"), {})),
        ("inherited-decider", "exception-decider", (4, 2, 11), "SOFT_MISSING_DECIDER",
         _set(S + ("exception_decider",), _DELETE)),
        ("instruction-party", "q-instruction", (5, 1), "SOFT_UNKNOWN_PARTY",
         _set(P + ("q", "instruction_of"), "zz")),
        ("outranks-rank", "outranks", (5, 2, 0), "SOFT_UNKNOWN_RANK", _set(S + ("outranks",), [["a", "z"]])),
        ("ties-rank", "ties", (5, 2, 1), "SOFT_UNKNOWN_RANK", _set(S + ("ties",), [["b", "z"]])),
        ("duplicate-rule", "r3-name", (5, 3), "SOFT_DUPLICATE_DECLARATION", _set(rule(3, "name"), "b1")),
        ("rank-cycle", "outranks", (6, 1), "SOFT_DEPENDENCY_CYCLE",
         _set(S + ("outranks",), [["a", "b"], ["b", "a"]])),
        ("tie-against-order", "ties", (6, 2), "SOFT_TIE_AGAINST_ORDER",
         _set(S + ("ties",), [["b", "c"], ["a", "b"]])),
        ("tie-repeat", "ties", (6, 3), "SOFT_DUPLICATE_DECLARATION",
         _set(S + ("ties",), [["b", "c"], ["c", "b"]])),
        ("document-nodes", "unless", (6, 5, 0), "SOFT_RESOURCE_LIMIT", _carve_outs(range(3), _doubled(11))),
        ("precedence-cycle", "r0-over", (6, 5, 1), "SOFT_DEPENDENCY_CYCLE", _set(rule(0, "over"), ["c2"])),
        ("soft-over-hard", "r3-over", (6, 8), "SOFT_OVER_HARD", _set(rule(3, "over"), ["b1"])),
        # d3's decision predicate soft__excepted__d... exceeds MAX_IDENTIFIER_BYTES in E′.
        ("decision-name", "r3-name", (6, 4), "SOFT_RESOURCE_LIMIT", _set(rule(3, "name"), "d" * 49)),
        # b1's guard is read by d3's derived carve-out (blocked), which passes depth 64.
        ("derived-depth", "r1-guard", (6, 9), "SOFT_RESOURCE_LIMIT", _set(rule(1, "guard"), _nested(56))),
        ("derived-nodes", "r3-guard", (6, 10), "SOFT_RESOURCE_LIMIT", _set(rule(3, "guard"), _exact(9990))),
        ("premise-depth", "r0-sufficient", (6, 11), "SOFT_RESOURCE_LIMIT",
         _set(rule(0, "exception", "sufficient"), [_nested(63)])),
        # d3's guard is read by no derived carve-out or premise; its layer states it twice.
        ("layer-nodes", "r3-guard", (6, 12), "SOFT_RESOURCE_LIMIT", _set(rule(3, "guard"), _exact(6000))),
    ]


def multi_fault_cases(pairs=900, triples=600, seed=0):
    """Two or three faults from different phases, and two within one phase.

    Every pair within one phase is kept; the other pairs and the triples are a
    deterministic sample. Yields (name, raw, rules, expected code)."""
    for combo in choose_combinations(multi_faults(), phase=lambda fault: fault[2][0],
                                     footprint=lambda fault: (fault[1],),
                                     pairs=pairs, triples=triples, seed=seed):
        raw, rules = multi_fault_base()
        for fault in combo:
            fault[4](raw, rules)
        first = first_fault(combo, position=lambda fault: fault[2])
        yield "+".join(f[0] for f in combo), raw, rules, first[3]


def rejected_sources():
    """Wire inputs both regenerators must reject with identical diagnostics."""
    return [
        (env({"ranks": ["Bad!"], "outranking": {"mode": "strict"}}), []),
        (env({"ranks": ["a", "a"], "outranking": {"mode": "strict"}}), []),
        (env({"parties": ["a", "a"], "outranking": {"mode": "strict"}}), []),
        (env({"ranks": ["x", "y", "z"], "outranks": [["x", "y"], ["y", "z"], ["z", "y"]],
              "outranking": {"mode": "strict"}}), []),
        (env(), [norm("a", "x_required", True, alterable=["user"])]),
        (env(), [norm("a", "x_required", True, mode="default", exception={
            "decided_by": "", "sufficient": [], "necessary": [], "factors": []})]),
        (env({"outranking": {"mode": "strict", "decided_by": "assistant"}}), []),
        (env({"ranks": ["a", "b"], "ties": [["a", "b"], ["a", "b"]],
              "outranking": {"mode": "strict"}}), []),
        (env({"ranks": ["a", "b"], "outranks": [["a", "b"], ["a", "b"]],
              "outranking": {"mode": "strict"}}), []),
        (env(), [norm("a", "x_required", True, mode="default",
                      exception={"decided_by": "assistant"})]),
        (env({"parties": ["assistant", "user"], "outranking": {"mode": "strict"}}),
         [norm("a", "x_required", True, alterable=["user", "assistant"])]),
        # Diagnostic parity reproducers from the soft route review.
        (env(), [norm("a", "x_required", True, mode="default")]),
        (env({"ranks": ["a"], "ties": [["a"]],
              "outranking": {"mode": "strict"}}), []),
        (env(), [norm("a", "x_required", True, mode="default", hard=True)]),
        (env(), [norm("a", "x_required", True, mode="default", alterable=["z"])]),
        (env(), [norm("a", "x_required", True, mode="default", rank="z")]),
        (env(), [norm("a", "x_required", True, alterable=False)]),
    ]


def generated_invalid_soft_blocks():
    """Single-field mutations of a valid block, including every collection shape."""
    baseline = env({"parties": ["p"], "ranks": ["a", "b"],
                    "outranking": {"mode": "strict"}})
    mutations = {
        # A name that is not a string, for each JSON kind whose Python spelling is not its compact JSON
        # (wire-contract.md 6, checks 2.7a and 2.8c): a Boolean, an array and an object; and an integer.
        "parties": [False, {}, "p", [False], [["p"]], [{"p": 1}], ["Bad!"], ["p", "p"]],
        "ranks": [False, {}, "a", [42], [False], [["a"]], [{"a": 1}], ["Bad!"], ["a", "a"]],
        "outranks": [False, {}, "a", [[]], [["a"]], [["a", "b", "a"]],
                     [[1, "b"]], [["a", "a"]], [["a", "b"], ["a", "b"]],
                     [["a", "unknown"]]],
        "ties": [False, {}, "a", [[]], [["a"]], [["a", "b", "a"]],
                 [[1, "b"]], [["a", "a"]], [["a", "b"], ["a", "b"]],
                 [["a", "b"], ["b", "a"]], [["a", "unknown"]]],
        "outranking": [False, {}, "strict", {"mode": "other"},
                       {"mode": "strict", "extra": 1},
                       {"mode": "strict", "decided_by": False},
                       {"mode": "holistic"},
                       {"mode": "holistic", "decided_by": False},
                       {"mode": "holistic", "decided_by": ""}],
        "exception_decider": [False, 3, ""],
        "unknown_field": [True],
    }
    for field, values in mutations.items():
        for value in values:
            raw = deepcopy(baseline)
            raw["vocabulary"]["soft"][field] = value
            yield raw, []
    for value in (False, True, 0, "strict", [], {}):
        raw = deepcopy(baseline)
        raw["vocabulary"]["soft"] = value
        yield raw, []
    for name in ("soft__reserved",):
        raw = deepcopy(baseline)
        raw["vocabulary"]["predicates"][name] = {
            "arguments": ["assistant"], "description": name}
        yield raw, []
    # Diagnostic strings supplied as names must not change the rejection class.
    for name in ("needs an exception", "invalid ties pair", "UnknownRank: x"):
        raw = deepcopy(baseline)
        raw["vocabulary"]["soft"]["ranks"] = [name]
        yield raw, []
    for value in (False, True, 0, 1, [], {}, ["p"], {"party": "p"}):
        raw = deepcopy(baseline)
        raw["vocabulary"]["predicates"]["q"] = {
            "arguments": ["assistant"], "description": "q", "instruction_of": value}
        yield raw, []


def combined_invalid_soft_blocks():
    """Independent block faults must have the same diagnostic precedence."""
    baseline = env({"parties": ["p"], "ranks": ["a", "b"],
                    "outranking": {"mode": "strict"}})
    original = baseline["vocabulary"]["soft"]
    mutations = []
    for raw, _ in generated_invalid_soft_blocks():
        block = raw["vocabulary"].get("soft")
        if type(block) is not dict:
            continue
        changed = {k: v for k, v in block.items() if k not in original or v != original[k]}
        if len(changed) == 1:
            mutations.append(changed)
    for left, right in combinations(mutations, 2):
        if left.keys() & right.keys():
            continue
        raw = deepcopy(baseline)
        raw["vocabulary"]["soft"].update(left)
        raw["vocabulary"]["soft"].update(right)
        yield raw, []


def generated_invalid_soft_rules():
    """Pairs of independent rule faults check diagnostic precedence."""
    raw = env()
    valid = norm("a", "x_required", True, mode="default", exception={
        "decided_by": "assistant", "sufficient": [], "necessary": [], "factors": []})
    faults = [
        {"rank": "z"}, {"alterable": ["z"]}, {"alterable": False},
        {"hard": True}, {"exception": False},
        {"exception": {"decided_by": "", "sufficient": [], "necessary": [], "factors": []}},
        {"exception": {"decided_by": "assistant", "sufficient": [],
                       "necessary": [], "factors": False}},
        {"mode": "other"}, {"hard": "yes"},
    ]
    for left, right in combinations(faults, 2):
        if left.keys() & right.keys():
            continue
        yield raw, [{"norm": {**valid["norm"], **left, **right}}]


def generated_invalid_exceptions():
    """Exception fields are checked in wire order, including combined faults."""
    valid = {"decided_by": "assistant", "sufficient": [],
             "necessary": [], "factors": []}
    faults = [
        {"decided_by": False}, {"decided_by": ""},
        {"sufficient": False}, {"sufficient": [False]},
        {"necessary": False}, {"necessary": [False]},
        {"factors": False}, {"factors": [False]},
    ]
    for left, right in combinations(faults, 2):
        if left.keys() & right.keys():
            continue
        exception = {**valid, **left, **right}
        yield env(), [norm("a", "x_required", True, mode="default", exception=exception)]


def expected_rejections():
    """Named sources whose first diagnostic the validation table (8) fixes."""
    return [*loop_recheck_reproducers(), *soft2_reproducers(), *soft3_reproducers(),
            *soft_limits_reproducers(), *soft_over_reproducers(), *multi_fault_cases()]


def rejected_cases():
    """The sources `compare_rejected` submits, in its order: the fixed rejections, the named sources of
    `expected_rejections()`, then the generated block, rule, combined block and exception faults."""
    return (rejected_sources() +
            [(raw, rules) for _, raw, rules, _ in expected_rejections()] +
            list(generated_invalid_soft_blocks()) +
            list(generated_invalid_soft_rules()) +
            list(combined_invalid_soft_blocks()) +
            list(generated_invalid_exceptions()))


def generated_trees(count=TREES):
    """The seeded trees `main` examines, in seed order, until `count` are accepted: (seed, raw, rules,
    the Python document or None when Python rejects the tree)."""
    accepted, seed = 0, 0
    while accepted < count:
        raw, rules = generated(seed)
        try:
            soft = SoftNormDocument(SoftEnvironment(raw), rules)
            accepted += 1
        except Exception:
            soft = None
        yield seed, raw, rules, soft
        seed += 1


def exercised_sources():
    """Every source this module's comparison (`main`) submits to a validator, labelled: the seeded trees,
    the rejected cases and the near-limit cases. The wire gate replays each of them."""
    return [*((f"tree:{seed}", raw, rules) for seed, raw, rules, _ in generated_trees()),
            *((f"rejected:{i}", raw, rules) for i, (raw, rules) in enumerate(rejected_cases())),
            *((f"near-limit:{name}", raw, rules) for name, raw, rules in near_limit_cases())]


def compare_rejected(part=0, parts=1):
    """Every rejected input: Python and Lean reject it with the same code (and the same
    text for a fixture), and each named multi-fault case with its table's code. With
    `parts`, only the inputs whose index is `part` modulo `parts` (the suite runs the
    parts in parallel). Returns the number of inputs compared."""
    named = expected_rejections()
    cases = rejected_cases()
    indices = range(part, len(cases), parts)
    expected = {}
    for i in indices:
        raw, rules = cases[i]
        try:
            load_soft_document(raw, rules)
        except VEError as exc:
            expected[i] = (str(exc), exc.code)
        else:
            raise AssertionError("Python unexpectedly accepted a rejected soft source")
    wire = [{"id": str(i), "kind": "soft-elaborate", "environment": cases[i][0], "norms": cases[i][1]}
            for i in indices]
    rows = lean_routes.rows("soft-norms", wire)
    if len(rows) != len(indices):
        raise AssertionError("Lean returned the wrong rejected row count")
    fixtures = len(rejected_sources())
    for i, row in zip(indices, rows):
        error, code = expected[i]
        if row.get("status") != "error" or row.get("code") != code:
            raise AssertionError((i, error, code, row))
        if i < fixtures and row.get("error") != error:
            raise AssertionError((i, error, row))
    for i, (name, _, _, table_code) in enumerate(named):
        if fixtures + i in expected and expected[fixtures + i][1] != table_code:
            raise AssertionError((name, table_code, expected[fixtures + i]))
    return len(indices)


def rust_fixture_rows():
    result = []
    for name, raw, rules, present in rust_sources():
        soft = SoftNormDocument(SoftEnvironment(raw), rules)
        case = {"id": name, "kind": "soft-elaborate", "environment": raw, "norms": rules}
        row = lean_routes.rows("soft-norms", [case])[0]
        if row.get("status") != "ok":
            raise AssertionError((name, row))
        py_layers = [(label, formula_to_data(soft.extended_env, formula, _generated=True))
                     for label, formula in soft.elaborated.premises()]
        if py_layers != [(p["label"], p["ast"]) for p in row["premises"]]:
            raise AssertionError(f"Python/Lean layers differ: {name}")
        stripped = json.loads(json.dumps(row["environment_prime"]))
        stripped["profiles"] = [p for p in stripped["profiles"] if p != "soft-norms@0"]
        stripped["vocabulary"].pop("soft", None)
        for predicate in stripped["vocabulary"]["predicates"].values():
            predicate.pop("instruction_of", None)
        environment = Environment(stripped)
        formulas = [p["ast"] for p in row["premises"]] + [
            p["ast"] for p in row["background"] if p.get("generator") == "soft"]
        target_start = len(formulas)
        for target in row["conflict_targets"]:
            existential = target["ast"]
            for sort in reversed(target["sorts"]):
                existential = ["exists", sort, existential]
            formulas.append(existential)
        for required, permitted in ((False, False), (False, True), (True, True)):
            relations = {p: [] for p in environment.predicates}
            relations["x_required"] = [["a"]] if required else []
            relations["x_permitted"] = [["a"]] if permitted else []
            for decision in present:
                relations[decision] = [["a"]]
            model_data = {"complete": True, "domains": {"assistant": ["a"], "user": []},
                          "constants": {}, "relations": relations}
            model = FiniteModel.from_dict(environment, model_data)
            expected = [evaluate(environment, formula_from_data(environment, formula),
                                 model, trace=False).value for formula in formulas]
            result.append({"id": name + f"-{int(required)}{int(permitted)}",
                           "untrusted": True,
                           "source": {"environment": raw, "norms": rules},
                           "environment": stripped, "formulas": formulas,
                           "model": model_data, "expected": expected,
                           "target_start": target_start,
                           "conflict": any(expected[target_start:])})
    return result


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--write-rust-fixtures":
        rows = rust_fixture_rows()
        RUST_FIXTURES.write_text(json.dumps(rows, sort_keys=True, ensure_ascii=False,
                                            separators=(",", ":")) + "\n")
        print(json.dumps({"rust_cases": len(rows), "path": str(RUST_FIXTURES)}))
        return
    report = compare_generated()
    near_accepted, near_rejected = compare_near_limit(near_limit_cases())
    print(json.dumps({**report, "rejected_inputs": compare_rejected(),
                      "near_limit_accepted": near_accepted,
                      "near_limit_rejected": near_rejected}))


def compare_generated():
    """The TREES generated accepted trees: Lean accepts each, and the public elaboration
    check of its regenerated targets passes."""
    compared = 0
    seed = 0
    trees = generated_trees()
    while compared < TREES:
        batch = []
        while len(batch) < min(25, TREES - compared):
            tree_seed, raw, rules, soft = next(trees)
            seed = tree_seed + 1
            if soft is None:
                continue  # generate another accepted tree
            batch.append((raw, rules, soft))
        cases = [{"id": str(compared + i), "kind": "soft-elaborate",
                  "environment": raw, "norms": rules}
                 for i, (raw, rules, _) in enumerate(batch)]
        rows = lean_routes.rows("soft-norms", cases)
        if len(rows) != len(batch):
            raise AssertionError("Lean returned the wrong row count")
        for i, ((_, _, soft), row) in enumerate(zip(batch, rows)):
            if row.get("status") != "ok":
                raise AssertionError((compared + i, row))
            try:
                check_regenerated(soft, row)
            except VEError as exc:
                raise AssertionError(f"regeneration mismatch at seed {seed - len(batch) + i}") from exc
        compared += len(batch)
    return {"accepted_trees": compared, "seeds_examined": seed,
            "environment_matches": compared, "layer_matches": compared,
            "soft_background_matches": compared, "decision_matches": compared}


if __name__ == "__main__":
    main()
