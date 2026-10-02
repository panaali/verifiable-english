"""The fault catalogue of the pilot `soft-norms@0` (wire-contract.md 8.3) and the oracle it feeds.

Every fault records, by hand, the check that must be the first diagnostic when the fault alone is applied
to its base source, the record's `path`, and, for a classifier member whose set section 6 orders by order
keys, its key inside the set; and, for a check that is not inherited, the record's `args` (`ARGS`), from
which the expected `text` is rendered by the contract's template. The expected `code`, `class` and `phase`
follow from the check by the contract. The oracle never runs an engine: a fault's table position is read from the contract's structure
and the expected path (`position`), and a combination of faults with disjoint footprints expects the record
of the fault of least position (`expected_first`).
"""

import argparse
from copy import deepcopy
from dataclasses import dataclass, field, replace
import json
from pathlib import Path
import re
from typing import Callable

from conformance.soft_norms import (_doubled, _exception, multi_fault_base, multi_faults, norm,
                                   soft3_reproducers, soft4_aggregate_reproducers, soft4_reproducers)

INDEX = Path(__file__).resolve().parent / "wire-contract/soft-norms@0-catalogue.json"
S = "/environment/vocabulary/soft"
P = "/environment/vocabulary/predicates"


@dataclass(frozen=True)
class Fault:
    name: str
    check: str
    path: str
    apply: Callable = field(compare=False)
    labels: frozenset = frozenset()   # hand-declared semantic footprint, beyond the fields it changes
    key: tuple = ()                   # order key inside a classifier set; () is the member's index
    readers: str = "both"             # "python": only the in-process reader carries it (a `null`)
    reads: tuple = ()                 # locations its expected outcome depends on beyond those it changes

    def source(self):
        raw, rules = multi_fault_base()
        root = {"environment": raw, "norms": rules}
        self.apply(root)
        return root["environment"], root["norms"]


def _multi_expected():
    """The first check and path of each fault of `multi_faults()`, read from section 6 and the base."""
    expected = {
        "language": ("1.2", "/environment/language"),
        "revision": ("1.4", "/environment/spec_revision"),
        "vocabulary-field": ("1.5a", "/environment/vocabulary"),
        "profiles-shape": ("1.3", "/environment/profiles"),
        "reserved-name": ("2.1a", P + "/soft__a"),
        "reserved-name-z": ("2.1a", P + "/soft__z"),
        "instruction-type": ("2.2a", P + "/q/instruction_of"),
        "malformed-predicate": ("2.3", "/environment"),
        "missing-dual": ("2.3", "/environment"),
        "act-role": ("2.3", "/environment"),
        "block-field": ("2.4", S),
        "parties-shape": ("2.5", S + "/parties"),
        "party-name": ("2.7a", S + "/parties/1"),
        "party-repeat": ("2.7b", S + "/parties/2"),
        "rank-repeat": ("2.8d", S + "/ranks/3"),
        "outranking-mode": ("2.9b", S + "/outranking/mode"),
        "strict-decider": ("2.10", S + "/outranking"),
        "holistic-decider": ("2.12", S + "/outranking"),
        "exception-decider": ("2.14", S + "/exception_decider"),
        "outranks-pair": ("2.16b", S + "/outranks/1/1"),
        "ties-pair": ("2.17d", S + "/ties/1"),
        "profiles-order": ("3.1", "/environment/profiles"),
        "profiles-repeat": ("3.1", "/environment/profiles"),
        "profile-unknown": ("3.2", "/environment/profiles/3"),
        "profile-norms": ("3.3c", "/environment/profiles"),
        "profile-checker": ("3.4a", "/environment/profiles"),
        "r1-strict-exception": ("4.8", "/norms/1/norm/exception"),
        "inherited-decider": ("4.11a", "/norms/2/norm/exception"),
        "instruction-party": ("5.1", P + "/q/instruction_of"),
        "outranks-rank": ("5.2a", S + "/outranks/0/1"),
        "ties-rank": ("5.2b", S + "/ties/0/1"),
        "duplicate-rule": ("5.3", "/norms/3/norm/name"),
        "rank-cycle": ("6.1", S + "/outranks"),
        "tie-against-order": ("6.2", S + "/ties/1"),
        "tie-repeat": ("6.3", S + "/ties"),
        "decision-name": ("6.4a", ""),
        "document-nodes": ("6.5a", ""),
        "precedence-cycle": ("6.5b", ""),
        "soft-over-hard": ("6.8", ""),
        "derived-depth": ("6.9", ""),
        "derived-nodes": ("6.10b", ""),
        "premise-depth": ("6.11", ""),
        "layer-nodes": ("6.12", ""),
    }
    for i in range(4):
        r = f"/norms/{i}"
        expected.update({
            f"r{i}-field": ("4.1c", r + "/norm"),
            f"r{i}-sign": ("4.2a", r + "/norm"),
            f"r{i}-over-repeat": ("4.2b", r + "/norm/over/1"),
            f"r{i}-guard-nodes": ("4.2a", r + "/norm"),
            f"r{i}-mode": ("4.3", r + "/norm/mode"),
            f"r{i}-rank-type": ("4.4", r + "/norm/rank"),
            f"r{i}-alterable": ("4.5b", r + "/norm/alterable"),
            f"r{i}-hard-type": ("4.6", r + "/norm/hard"),
            f"r{i}-rank": ("5.5", r + "/norm/rank"),
            f"r{i}-party": ("5.6", r + "/norm/alterable/0"),
            f"r{i}-guard": ("5.7", r),
            f"r{i}-predicate": ("5.4", r + "/norm/predicate"),
            f"r{i}-over": ("5.9a", r + "/norm/over/0"),
        })
    for i in (0, 2, 3):
        r = f"/norms/{i}"
        expected.update({
            f"r{i}-hard": ("4.7a", r + "/norm/mode"),
            f"r{i}-exception": ("4.9b", r + "/norm/exception"),
            f"r{i}-sufficient": ("4.13a", r + "/norm/exception/sufficient"),
            f"r{i}-condition-syntax": ("4.13b", r + "/norm/exception/sufficient/0"),
            f"r{i}-factors": ("4.14b", r + "/norm/exception/factors/0"),
            # 5.8b on the rule's first condition: order key (condition 0, member 2), section 6.
            f"r{i}-condition": ("5.8b", r),
        })
    for i in (0, 3):
        r = f"/norms/{i}/norm/exception/decided_by"
        expected.update({f"r{i}-decider-type": ("4.10", r), f"r{i}-decider": ("4.12", r)})
    return expected


KEYS = {f"r{i}-condition": (0, 2) for i in (0, 2, 3)} | {f"r{i}-guard": (0,) for i in range(4)}


def _name(i):
    """The location of the name of the base's rule `i`, which a record's `name` or `detail` may repeat."""
    return ("norms", i, "norm", "name")


NAMES = ("a0", "b1", "c2", "d3")


def _expected_args():
    """The `args` of each fault's expected record, written by hand from the contract's texts (2.7) and the
    base, for every fault whose check is not inherited and whose text has a placeholder; a fault whose text
    has none expects `{}`. Each entry also gives the locations it reads beyond those the fault writes (a
    rule's name or predicate), so that no fault that changes them is combined with it (`footprint`)."""
    args = {
        "reserved-name": ({"key": "soft__a"}, ()),
        "reserved-name-z": ({"key": "soft__z"}, ()),
        "instruction-type": ({"key": "q"}, ()),
        "party-name": ({"value": "Q!"}, ()),
        "party-repeat": ({"value": "p"}, ()),
        "rank-repeat": ({"value": "a"}, ()),
        "profile-unknown": ({"value": "zz@0"}, ()),
        "r1-strict-exception": ({"name": "b1"}, (_name(1),)),
        "inherited-decider": ({"name": "c2"}, (_name(2),)),
        "null-decider": ({"name": "c2"}, (_name(2),)),
        "instruction-party": ({"value": "zz"}, ()),
        "outranks-rank": ({"value": "z"}, ()),
        "ties-rank": ({"value": "z"}, ()),
        "duplicate-rule": ({"value": "b1"}, (_name(1),)),
        "rank-cycle": ({"detail": "a, b"}, ()),
        "tie-against-order": ({"a": "a", "b": "b"}, ()),
        "decision-name": ({"name": "soft__excepted__" + "d" * 49}, ()),
        "precedence-cycle": ({"detail": "a0, c2"}, (_name(0), _name(2))),
        "soft-over-hard": ({"detail": "rule d3 over b1"}, (_name(3), _name(1))),
        "derived-depth": ({"detail": " of rule c2"}, (_name(2),)),
        "layer-nodes": ({"detail": "layer:norms:x_permitted"}, ()),
        "dunder-regulated": ({"key": "a__b"}, ()),
        "instruction-regulated": ({"key": "q"}, ()),
        "instruction-defined": ({"key": "q"}, ()),
        "rank-name": ({"value": "Bad!"}, ()),
        "r1-alterable-shape": ({"name": "b1"}, (_name(1),)),
        "r1-hard-alterable": ({"name": "b1"}, (_name(1),)),
        "r0-no-exception": ({"name": "a0"}, (_name(0),)),
        "r0-factors-shape": ({"name": "a0"}, (_name(0),)),
        "r3-over-predicate": ({"rule": "d3", "predicate": "x_permitted", "value": "a0",
                               "parent_predicate": "x_required"},
                              (_name(3), _name(0), ("norms", 3, "norm", "predicate"),
                               ("norms", 0, "norm", "predicate"))),
        "long-decision-names": ({"name": "soft__excepted__" + "d" * 52}, ()),
        "stratification": ({"detail": "x_permitted, x_required"}, ()),
        "softened-cycle": ({"detail": "x_permitted, x_required"}, ()),
        "soft4-target-doubling-11": ({"detail": "p10"}, ()),
    }
    for i, name in enumerate(NAMES):
        args.update({
            f"r{i}-over-repeat": ({"value": "a0", "name": name}, (_name(i),)),
            f"r{i}-mode": ({"name": name}, (_name(i),)),
            f"r{i}-rank-type": ({"name": name}, (_name(i),)),
            f"r{i}-alterable": ({"name": name}, (_name(i),)),
            f"r{i}-hard-type": ({"name": name}, (_name(i),)),
            f"r{i}-rank": ({"name": name, "value": "z"}, (_name(i),)),
            f"r{i}-party": ({"value": "zz"}, ()),
            f"r{i}-predicate": ({"value": "u"}, ()),
            f"r{i}-over": ({"value": "nosuch"}, ()),
        })
    for i in (0, 2, 3):
        name = NAMES[i]
        args.update({
            f"r{i}-hard": ({"name": name}, (_name(i),)),
            f"r{i}-exception": ({"name": name}, (_name(i),)),
            f"r{i}-factors": ({"name": name}, (_name(i),)),
            f"r{i}-condition": ({"detail": f"{name} mentions x_permitted"}, (_name(i),)),
        })
    for i in (0, 3):
        args.update({f"r{i}-decider-type": ({"name": NAMES[i]}, (_name(i),)),
                     f"r{i}-decider": ({"name": NAMES[i]}, (_name(i),))})
    return args


ARGS = _expected_args()


def _replacing(apply, *paths):
    """Mark a mutation as replacing the values at `paths` whole (its footprint covers everything under them)."""
    apply.replaces = paths
    return apply


def _set_at(path, value):
    def apply(root):
        target = root
        for step in path[:-1]:
            target = target[step]
        target[path[-1]] = deepcopy(value)
    return _replacing(apply, tuple(path))


def _replace_rules(new_rules):
    def apply(root):
        root["norms"] = deepcopy(new_rules)
    return _replacing(apply, ("norms",))


def _env(change):
    """A mutation of the environment alone."""
    return lambda root: change(root["environment"])


def _rules(change):
    """A mutation of the norm array alone."""
    return lambda root: change(root["norms"])


def _derived():
    """Single-check faults derived from the kinds of the T1 checks and the hooks that `multi_faults()`
    does not reach, with the witnesses of the classifier members: (name, check, path, mutation)."""
    E = ("environment",)
    V = E + ("vocabulary",)
    SB = V + ("soft",)
    N = ("norms",)
    rules_6_7 = [norm("ra", "x_required", True, guard=["unary", "x_permitted", ["var", 0]]),
                 norm("rb", "x_permitted", True, guard=["unary", "x_required", ["var", 0]])]
    # 6.10a: the holistic collision of a default denial of x_permitted with a strict x_required whose
    # guard denies x_permitted puts a cycle into T′ that T does not have (found by a seeded search).
    rules_6_10a = [norm("r0", "x_permitted", False, guard=["unary", "u", ["var", 0]], mode="default",
                        rank="a", exception={"decided_by": "assistant", "sufficient": [], "necessary": [],
                                             "factors": []}),
                   norm("r1", "x_required", True, guard=["not", ["unary", "x_permitted", ["var", 0]]])]

    def holistic_6_10a(root):
        root["environment"]["vocabulary"]["soft"]["outranking"] = {"mode": "holistic",
                                                                    "decided_by": "assistant"}
        root["norms"] = deepcopy(rules_6_10a)

    def necessary_budget(root):
        rules = root["norms"]
        # The rule's guard and a necessary condition exceed the rule's budget at the condition after the
        # first sufficient one: 5.8a with order key (condition 1, member 1).
        rules[0]["norm"]["guard"] = _doubled(11)
        rules[0]["norm"]["exception"]["necessary"] = [_doubled(11, ("unary", "u", ["var", 0]))]

    def long_decision_names(root):
        rules = root["norms"]
        # A strict rule with a long `off` decision name before a default rule with a long `excepted`
        # one: legacy Python and Lean report the `excepted` name, prefix by prefix (Fable B1).
        rules[1]["norm"]["name"] = "b" * 52
        rules[3]["norm"]["name"] = "d" * 52

    return [
        ("env-extra", "1.1", "/environment", _env(lambda r: r.update(extra=1))),
        ("sorts-shape", "1.5b", "/environment/vocabulary/sorts", _set_at(V + ("sorts",), [])),
        ("predicates-shape", "1.5c", P, _set_at(V + ("predicates",), [])),
        ("constants-shape", "1.5d", "/environment/vocabulary/constants", _set_at(V + ("constants",), [])),
        ("norms-shape", "1.6", "/norms", _set_at(N, {})),
        ("norms-limit", "1.7", "/norms", _rules(lambda rules: rules.extend([deepcopy(rules[0])] * 257))),
        ("dunder-regulated", "2.1b", P + "/a__b", _env(lambda r: r["vocabulary"]["predicates"].update(
            {"a__b": deepcopy(r["vocabulary"]["predicates"]["x_required"])}))),
        ("instruction-regulated", "2.2b", P + "/q", _env(lambda r: r["vocabulary"]["predicates"]["q"].update(
            regulated=deepcopy(r["vocabulary"]["predicates"]["x_required"]["regulated"])))),
        ("instruction-defined", "2.2c", P + "/q",
         _env(lambda r: r["vocabulary"]["predicates"]["q"].update(defined=["top"]))),
        ("parties-limit", "2.6", S + "/parties", _set_at(SB + ("parties",), [f"p{i}" for i in range(9)])),
        ("ranks-shape", "2.8a", S + "/ranks", _set_at(SB + ("ranks",), "a")),
        ("ranks-limit", "2.8b", S + "/ranks", _set_at(SB + ("ranks",), [f"r{i}" for i in range(17)])),
        ("rank-name", "2.8c", S + "/ranks/1", _set_at(SB + ("ranks",), ["a", "Bad!"])),
        ("outranking-field", "2.9a", S + "/outranking",
         _set_at(SB + ("outranking",), {"mode": "strict", "extra": 1})),
        ("outranking-decider-type", "2.11", S + "/outranking/decided_by",
         _set_at(SB + ("outranking",), {"mode": "holistic", "decided_by": 7})),
        ("outranking-decider-name", "2.13", S + "/outranking/decided_by",
         _set_at(SB + ("outranking",), {"mode": "holistic", "decided_by": ""})),
        ("outranks-shape", "2.15", S + "/outranks", _set_at(SB + ("outranks",), "a")),
        ("outranks-arity", "2.16a", S + "/outranks/0", _set_at(SB + ("outranks",), [["a"]])),
        ("outranks-repeat", "2.16c", S + "/outranks/1", _set_at(SB + ("outranks",), [["a", "b"], ["a", "b"]])),
        ("ties-shape", "2.17a", S + "/ties", _set_at(SB + ("ties",), "a")),
        ("ties-arity", "2.17b", S + "/ties/0", _set_at(SB + ("ties",), [["b"]])),
        ("ties-same", "2.17c", S + "/ties/0/1", _set_at(SB + ("ties",), [["b", "b"]])),
        ("profile-base", "3.3a", "/environment/profiles", _env(lambda r: r.update(
            profiles=[p for p in r["profiles"] if p != "relational-fol@0"]))),
        ("profile-soft", "3.3b", "/environment/profiles", _env(lambda r: r.update(
            profiles=[p for p in r["profiles"] if p != "soft-norms@0"]))),
        ("profile-nary", "3.4b", "/environment/profiles",
         _env(lambda r: r.update(profiles=sorted(r["profiles"] + ["nary@0"])))),
        ("profile-order", "3.4c", "/environment/profiles",
         _env(lambda r: r.update(profiles=sorted(r["profiles"] + ["order@0"])))),
        ("definition", "3.5a", P, _env(lambda r: (
            r.update(profiles=sorted(r["profiles"] + ["definitions@0"])),
            r["vocabulary"]["predicates"]["u"].update(defined={"arguments": ["assistant"], "body": ["top"]})))),
        ("data-flag", "3.5b", P, _env(lambda r: (
            r.update(profiles=sorted(r["profiles"] + ["data@0"])),
            r["vocabulary"]["predicates"]["u"].update(arguments=["assistant", "assistant"], functional=True)))),
        ("r0-unit-field", "4.1a", "/norms/0", _rules(lambda rules: rules[0].update(extra=1))),
        ("r0-norm-shape", "4.1b", "/norms/0/norm", _set_at(N + (0, "norm"), 7)),
        ("r1-alterable-shape", "4.5a", "/norms/1/norm/alterable", _set_at(N + (1, "norm", "alterable"), "p")),
        ("r1-hard-alterable", "4.7b", "/norms/1/norm/alterable",
         _rules(lambda rules: rules[1]["norm"].update(hard=True))),
        ("r0-no-exception", "4.9a", "/norms/0/norm", _rules(lambda rules: rules[0]["norm"].pop("exception"))),
        ("r0-necessary-shape", "4.13c", "/norms/0/norm/exception/necessary",
         _set_at(N + (0, "norm", "exception", "necessary"), "x")),
        ("r0-necessary-syntax", "4.13d", "/norms/0/norm/exception/necessary/0",
         _set_at(N + (0, "norm", "exception", "necessary"), [["bad"]])),
        ("r0-factors-shape", "4.14a", "/norms/0/norm/exception/factors",
         _set_at(N + (0, "norm", "exception", "factors"), [1])),
        ("r0-necessary-budget", "5.8a", "/norms/0", necessary_budget),
        ("r3-over-predicate", "5.9b", "/norms/3/norm/over/0",
         _rules(lambda rules: rules[3]["norm"].update(over=["a0"]))),
        ("long-decision-names", "6.4a", "", long_decision_names),
        ("vocabulary-limit", "6.4b", "", _env(lambda r: r["vocabulary"]["predicates"].update({
            f"z{i}": {"arguments": ["assistant"], "description": "z"} for i in range(248)}))),
        ("precedence-depth", "6.6", "", _rules(lambda rules: rules.extend(
            norm(f"z{i}", "x_required", True, over=[f"z{i - 1}"] if i else []) for i in range(20)))),
        ("stratification", "6.7", "", _replace_rules(rules_6_7)),
        ("softened-cycle", "6.10a", "", _replacing(holistic_6_10a, ("norms",),
                                                     ("environment", "vocabulary", "soft", "outranking"))),
    ]


DERIVED_KEYS = {"r0-necessary-budget": (1, 1)}
# Faults whose expected check also depends on what other faults change: 6.4a and 6.4b count and name the
# decision predicates, which the rules determine.
READS = {"vocabulary-limit": (("norms",),), "long-decision-names": (("norms",),)}
# Faults that spend one shared node budget (W1's document budget, 6.5a and 6.10b): two of them together can
# exceed it although each fits, so they are never combined.
BUDGET = frozenset({"document-budget"})
LABELS = {name: BUDGET for name in ("document-nodes", "derived-depth", "derived-nodes", "premise-depth",
                                    "layer-nodes", "r0-necessary-budget")}


def _reproducers():
    """Classifier members reached only by the reproducers of the soft conformance suite."""
    wanted = {"soft4-target-doubling-11": ("6.13", ""),
              "soft4-background-premise-nodes-9996": ("6.14", ""),
              "soft4-layers-strict-guard-4981": ("6.15", ""),
              "soft3-rule-nodes-before-exception-condition": ("5.8a", "/norms/0")}
    keys = {"soft3-rule-nodes-before-exception-condition": (0, 1)}
    found = []
    for name, environment, rules, *_ in (*soft4_aggregate_reproducers(), *list(soft4_reproducers())[:3],
                                         *soft3_reproducers()):
        if name in wanted and name not in {f.name for f in found}:
            check, path = wanted[name]

            def apply(root, environment=environment, rules=rules):
                root["environment"] = deepcopy(environment)
                root["norms"] = deepcopy(rules)
            found.append(Fault(name, check, path, _replacing(apply, ("environment",), ("norms",)),
                               frozenset({"whole-source"}), keys.get(name, ())))
    return found


def _python_only():
    """Faults that only the in-process API can carry: an explicit `null`, which the wire readers refuse
    before diagnosis, so `ve_diagnose` never sees it."""
    def null_decider(root):
        root["environment"]["vocabulary"]["soft"].pop("exception_decider")
        root["norms"][2]["norm"]["exception"]["decided_by"] = None
    return [Fault("null-decider", "4.11b", "/norms/2/norm/exception/decided_by", null_decider,
                  frozenset({"exception-decider"}), readers="python")]


def catalogue():
    """Every fault: `multi_faults()`, then the derived faults, the reproducers and the Python-only ones."""
    expected = _multi_expected()
    faults = []
    for name, group, _, _, apply in multi_faults():
        check, path = expected[name]
        faults.append(Fault(name, check, path, lambda root, apply=apply: apply(root["environment"], root["norms"]),
                            frozenset({group}) | LABELS.get(name, frozenset()), KEYS.get(name, ())))
    for name, check, path, apply in _derived():
        faults.append(Fault(name, check, path, apply, frozenset({name}) | LABELS.get(name, frozenset()),
                            DERIVED_KEYS.get(name, ()), reads=READS.get(name, ())))
    faults += _reproducers() + _python_only()
    # The locations each fault's expected `args` read join its footprint (`_expected_args`).
    return [replace(fault, reads=fault.reads + ARGS[fault.name][1]) if fault.name in ARGS else fault
            for fault in faults]


def legacy_codes():
    """The code that `multi_faults()` records by hand for each of its faults."""
    return {f[0]: f[3] for f in multi_faults()}


# Members for which no input is known that reaches them, each with the reason. The `WC08` catalogue clause
# accepts a member declared here, and the gate reports it as uncovered: a declaration is not a witness.
UNREACHED = {
    "6.10c": "The fallback member of `soft_semantic`: W1's checks of T' other than its resource limits "
             "(6.10b) and its stratification (6.10a). T' is well typed by construction, 6.9 bounds its "
             "carve-out counts before W1 runs, and its new names are fresh by 2.1a and 6.4a. Seeded searches "
             "over 10,000 small documents (2026-10-02) reached 6.10a and never 6.10c.",
}


def catalogue_checks():
    """The checks and classifier members with a fault in the catalogue, and those declared unreached with a
    reason (the `WC08` catalogue clause)."""
    return {f.check for f in catalogue()} | set(UNREACHED)


def catalogue_index():
    """The catalogue's index, which `tools/wire_contract.py` reads for the `WC08` clause without importing
    the conformance suite: each check with the names of its faults, and the unreached members."""
    faults = {}
    for fault in catalogue():
        faults.setdefault(fault.check, []).append(fault.name)
    return {"contract": "soft-norms@0", "faults": {check: sorted(names) for check, names in faults.items()},
            "unreached": UNREACHED}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(catalogue_index(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not INDEX.exists() or INDEX.read_text() != rendered:
            print("fault catalogue index differs")
            return 1
    else:
        INDEX.write_text(rendered)
    return 0


# ## The oracle

def _tokens(pointer):
    return [t.replace("~1", "/").replace("~0", "~") for t in pointer.split("/")[1:]] if pointer else []


def _token_key(token):
    return (0, int(token)) if token.isdigit() else (1, token)


def _pattern_tokens(pattern, items):
    """The absolute tokens of a pattern, `*` kept, given the absolute patterns of the enclosing items."""
    if pattern.startswith("@"):
        head, _, tail = pattern.partition("/")
        base = items[int(head[1:] or 0)]
        return base + (tail.split("/") if tail else [])
    return pattern.split("/")[1:] if pattern else []


def route(contract, check):
    """The phase index and the entries from the phase down to `check`: [(index, entry), …] and, for a
    classifier member, its index in `emits` last."""
    def find(entries):
        for index, entry in enumerate(entries):
            if "each" in entry:
                below = find(entry["checks"])
                if below is not None:
                    return [(index, entry)] + below
            elif entry.get("kind") == "classifier":
                for member_index, member in enumerate(entry["emits"]):
                    if member["id"] == check:
                        return [(index, entry), (member_index, member)]
            elif entry.get("id") == check:
                return [(index, entry)]
        return None
    for phase_index, phase in enumerate(contract["phases"]):
        found = find(phase["checks"])
        if found is not None:
            return phase_index, found
    raise KeyError(check)


def position(contract, fault):
    """The fault's table position (2.6), from the contract and the hand-written path alone: phase index,
    entry index, the item of each enclosing group (its tokens, read from the path at the group's `*`
    steps), sub-entry index, …, then the order key inside a classifier set."""
    phase_index, steps = route(contract, fault.check)
    path = _tokens(fault.path)
    items = []
    result = [(0, phase_index)]
    for depth, (index, entry) in enumerate(steps):
        if entry.get("kind") == "classifier" and depth == len(steps) - 2:
            result.append((0, index))
            member_index = steps[-1][0]
            result.append((2, fault.key or (member_index,)))
            break
        result.append((0, index))
        if "each" in entry:
            pattern = _pattern_tokens(entry["each"], items)
            start = len(items[int(entry["each"][1:].partition("/")[0] or 0)]) if entry["each"].startswith("@") else 0
            stars = [k for k in range(start, len(pattern)) if pattern[k] == "*"]
            if len(path) < len(pattern):
                raise ValueError(f"{fault.name}: path {fault.path} is not under group {entry['id']}")
            result.append((1, tuple(_token_key(path[k]) for k in stars)))
            items.insert(0, path[:len(pattern)])
    return result


def expected_first(contract, combo):
    """The oracle: the fault of least table position."""
    return min(combo, key=lambda fault: position(contract, fault))


_PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)(?::[a-z]+)?\}")


def rendered(template, args):
    """The text of a template (2.7) with rendered `args`, written here apart from the engines' renderer: each
    placeholder is replaced by its argument, and the placeholders must be exactly the arguments."""
    if "{{" in template or "}}" in template:
        raise ValueError(f"the oracle does not render escaped braces: {template}")
    names = {match[1] for match in _PLACEHOLDER.finditer(template)}
    if names != set(args):
        raise ValueError(f"template {template!r} has placeholders {sorted(names)}, args {sorted(args)}")
    return _PLACEHOLDER.sub(lambda match: args[match[1]], template)


def expected_record(contract, fault):
    """The expected record (2.7). Every field is the catalogue's, except, for an inherited check, `text` and
    `args`, which are each language's legacy text (section 6) and which the gate compares with it."""
    phase_index, steps = route(contract, fault.check)
    member = steps[-1][1]
    code = member["code"]
    record = {"contract": contract["contract"], "revision": contract["revision"], "check": fault.check,
              "phase": contract["phases"][phase_index]["name"], "code": code,
              "class": contract["codes"][code]["class"], "path": fault.path}
    if not member.get("inherited"):
        args = dict(ARGS[fault.name][0]) if fault.name in ARGS else {}
        record["text"], record["args"] = rendered(member["text"], args), args
    return record


def changed_paths(before, after, prefix=()):
    """The JSON locations where two values differ: a changed scalar or type, an added or removed member, or
    an array whose length changed."""
    if type(before) is not type(after):
        return {prefix}
    if type(before) is dict:
        out = set()
        for key in before.keys() | after.keys():
            if key not in before or key not in after:
                out.add(prefix + (key,))
            else:
                out |= changed_paths(before[key], after[key], prefix + (key,))
        return out
    if type(before) is list:
        if len(before) != len(after):
            return {prefix}
        out = set()
        for index, (a, b) in enumerate(zip(before, after)):
            out |= changed_paths(a, b, prefix + (index,))
        return out
    return set() if before == after else {prefix}


def footprint(fault):
    """A fault's hand-declared labels, the locations it writes (those where its source differs from the
    base, and those it replaces whole) and the further locations its expected outcome reads."""
    base = multi_fault_base()
    raw, rules = fault.source()
    writes = changed_paths({"environment": base[0], "norms": base[1]}, {"environment": raw, "norms": rules})
    writes |= set(getattr(fault.apply, "replaces", ()))
    return fault.labels, frozenset(writes), frozenset(fault.reads)


def overlaps(left, right):
    """Two faults are not independent when they share a label, or when a location one writes contains, or
    lies under, a location the other writes or reads."""
    (left_labels, left_writes, left_reads), (right_labels, right_writes, right_reads) = left, right
    if left_labels & right_labels:
        return True
    def meet(writes, others):
        return any(a[:len(b)] == b or b[:len(a)] == a for a in writes for b in others)
    return meet(left_writes, right_writes | right_reads) or meet(right_writes, left_reads)


if __name__ == "__main__":
    raise SystemExit(main())
