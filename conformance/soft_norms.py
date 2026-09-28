"""Deterministic Python/Lean regeneration comparison for 1,000 soft trees."""
from __future__ import annotations

import json
from copy import deepcopy
from itertools import combinations
from pathlib import Path
import random
import subprocess
import sys

from ve.ast import formula_to_data
from ve.ast import formula_from_data
from ve.environment import Environment
from ve.errors import VEError
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.softnorms import SoftEnvironment, SoftNormDocument, load_soft_document
from tests.test_soft_norms_lean import env, norm, should, ranks

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_soft_norms_route"
RUST_FIXTURES = ROOT / "conformance/soft_norms_rust.json"


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
    for i in range(rng.randrange(1, 5)):
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
        rules.append(norm(f"n{i}", pred, rng.choice([True, False]), guard=guard,
                          unless=[unless] if unless else [],
                          over=[rng.choice(parents)] if parents and rng.randrange(3) == 0 else [],
                          **fields))
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
        ("precedence-cycle", "r0-over", (6, 4), "SOFT_DEPENDENCY_CYCLE", _set(rule(0, "over"), ["c2"])),
        ("soft-over-hard", "r3-over", (6, 7), "SOFT_OVER_HARD", _set(rule(3, "over"), ["b1"])),
    ]


def multi_fault_cases(pairs=900, triples=600, seed=0):
    """Two or three faults from different phases, and two within one phase.

    Every pair within one phase is kept; the other pairs and the triples are a
    deterministic sample. Yields (name, raw, rules, expected code)."""
    faults = multi_faults()
    rng = random.Random(seed)
    combos = [c for c in combinations(faults, 2) if c[0][1] != c[1][1]]
    same_phase = [c for c in combos if c[0][2][0] == c[1][2][0]]
    other = [c for c in combos if c[0][2][0] != c[1][2][0]]
    chosen = same_phase + rng.sample(other, min(pairs, len(other)))
    three = [c for c in combinations(faults, 3) if len({f[1] for f in c}) == 3
             and len({f[2][0] for f in c}) >= 2]
    chosen += rng.sample(three, min(triples, len(three)))
    for combo in chosen:
        raw, rules = multi_fault_base()
        for fault in combo:
            fault[4](raw, rules)
        first = min(combo, key=lambda f: f[2])
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
        "parties": [False, {}, "p", [False], ["Bad!"], ["p", "p"]],
        "ranks": [False, {}, "a", [42], ["Bad!"], ["a", "a"]],
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
            *multi_fault_cases()]


def compare_rejected():
    named = expected_rejections()
    cases = (rejected_sources() +
             [(raw, rules) for _, raw, rules, _ in named] +
             list(generated_invalid_soft_blocks()) +
             list(generated_invalid_soft_rules()) +
             list(combined_invalid_soft_blocks()) +
             list(generated_invalid_exceptions()))
    expected = []
    for raw, rules in cases:
        try:
            load_soft_document(raw, rules)
        except VEError as exc:
            expected.append((str(exc), exc.code))
        else:
            raise AssertionError("Python unexpectedly accepted a rejected soft source")
    wire = [{"id": str(i), "kind": "soft-elaborate", "environment": raw, "norms": rules}
            for i, (raw, rules) in enumerate(cases)]
    run = subprocess.run([str(LEAN), "-"], input=json.dumps(wire), text=True,
                         capture_output=True, timeout=300, check=False)
    rows = json.loads(run.stdout)
    if len(rows) != len(cases):
        raise AssertionError("Lean returned the wrong rejected row count")
    for i, (row, (error, code)) in enumerate(zip(rows, expected)):
        if row.get("status") != "error" or row.get("code") != code:
            raise AssertionError((i, error, code, row))
        if i < len(rejected_sources()) and row.get("error") != error:
            raise AssertionError((i, error, row))
    offset = len(rejected_sources())
    for i, (name, _, _, table_code) in enumerate(named):
        if expected[offset + i][1] != table_code:
            raise AssertionError((name, table_code, expected[offset + i]))
    return len(cases)


def rust_fixture_rows():
    result = []
    for name, raw, rules, present in rust_sources():
        soft = SoftNormDocument(SoftEnvironment(raw), rules)
        case = {"id": name, "kind": "soft-elaborate", "environment": raw, "norms": rules}
        run = subprocess.run([str(LEAN), "-"], input=json.dumps([case]), text=True,
                             capture_output=True, timeout=120, check=False)
        row = json.loads(run.stdout)[0]
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
    compared = 0
    seed = 0
    while compared < 1000:
        batch = []
        while len(batch) < min(25, 1000 - compared):
            raw, rules = generated(seed)
            seed += 1
            try:
                soft = SoftNormDocument(SoftEnvironment(raw), rules)
            except Exception:
                continue  # generate another accepted tree
            batch.append((raw, rules, soft))
        cases = [{"id": str(compared + i), "kind": "soft-elaborate",
                  "environment": raw, "norms": rules}
                 for i, (raw, rules, _) in enumerate(batch)]
        run = subprocess.run([str(LEAN), "-"], input=json.dumps(cases), text=True,
                             capture_output=True, timeout=120, check=False)
        rows = json.loads(run.stdout)
        if len(rows) != len(batch):
            raise AssertionError("Lean returned the wrong row count")
        for i, ((_, _, soft), row) in enumerate(zip(batch, rows)):
            if row.get("status") != "ok":
                raise AssertionError((compared + i, row))
            py_layers = [(l, formula_to_data(soft.extended_env, f, _generated=True))
                         for l, f in soft.elaborated.premises()]
            lean_layers = [(p["label"], p["ast"]) for p in row["premises"]]
            py_soft = [(l, formula_to_data(soft.extended_env, f, _generated=True))
                       for l, f in soft.extended_env.soft_premises]
            lean_soft = [(p["label"], p["ast"]) for p in row["background"]
                         if p["generator"] == "soft"]
            if (soft.extended_env.to_dict() != row["environment_prime"] or
                    py_layers != lean_layers or py_soft != lean_soft or
                    list(soft.warnings) != row["warnings"] or
                    set(soft.extended_env.decision_names) !=
                    {d["name"] for d in row["decisions"]}):
                raise AssertionError(f"regeneration mismatch at seed {seed - len(batch) + i}")
        compared += len(batch)
    print(json.dumps({"accepted_trees": compared, "seeds_examined": seed,
                      "environment_matches": compared, "layer_matches": compared,
                      "soft_background_matches": compared, "decision_matches": compared,
                      "rejected_inputs": compare_rejected()}))


if __name__ == "__main__":
    main()
