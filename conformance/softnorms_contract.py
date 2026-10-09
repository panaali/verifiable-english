"""Python predicates and public rejection boundary for the soft-norms wire table.

The diagnostic engine observes a source only after the legacy validator rejects
it. It never decides acceptance or identity.
"""

from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
import json

from ve import profiles
from ve.errors import ResourceLimit, UnsupportedProfile, VEError
from ve.limits import MAX_IDENTIFIER_BYTES, MAX_PREDICATES
from conformance import softnorms_legacy as soft
from conformance.wire_contract_engine import Registry, load, overlay, run


@lru_cache(maxsize=1)
def _locked_contract():
    return load("soft-norms@0")


def public_rejection(environment, norms, error: VEError, *, contract=None, registry=None) -> VEError:
    """Attach the public record to a legacy rejection without replacing the error."""
    if error.diagnostic is not None:
        return error
    try:
        active_contract = _locked_contract() if contract is None else contract
        if active_contract["status"] != "public":
            return error
        root = {"environment": deepcopy(environment), "norms": deepcopy(norms)}
        outcome = run(active_contract, root, registry=REGISTRY if registry is None else registry)
        record = overlay(active_contract, error, outcome)
    except Exception:
        return error
    error.diagnostic = record
    error.message = record["text"]
    error.args = (record["text"],)
    return error


# The Lean engine is the specification (wire-contract.md D3) and every hook must agree with it on the
# inputs where it is reached (2.5, rule 2). Two lists differ between `ve/softnorms.py` and the Lean
# route, so the hooks below use Lean's, and a test compares them with the Lean sources:
# the profiles that phase 2 passes on to W1's decoding (`Phases.inheritedProfiles`) and the
# registry of check 3.2 (`VE.Route.Gate.registry` with `soft-norms@0`). Python's legacy
# registry adds six statement layers; S3-pre and S4-pre record the resulting comparisons.
INHERITED_PROFILES = ("data@0", "definitions@0", "documents@1", "time@0")
ROUTE_PROFILES = frozenset({"closure@0", "data@0", "definitions@0", "documents@1", "nary@0", "norms@0",
                            "order@0", profiles.BASE, "time@0", "soft-norms@0"})
DECISION_PREFIXES = ("soft__excepted__", "soft__off__", "soft__outweighs__")


def soft_source(case):
    """Build the root of a `soft-elaborate` or `admission` route case, as the Lean adapter does: a
    member the case lacks is `null` (2.1), and any other kind has no wire contract input."""
    kind = case.get("kind")
    if kind == "admission":
        document = case.get("document", {})
        units = document.get("units", []) if type(document) is dict else []
        active = [unit["content"] for unit in units
                  if type(unit) is dict and unit.get("kind") == "norm"
                  and type(unit.get("content")) is dict
                  and "norm" in unit["content"]]
        return {"environment": case.get("environment"), "norms": active}
    if kind != "soft-elaborate":
        shown = kind if type(kind) is str else json.dumps(kind, separators=(",", ":"))
        raise UnsupportedProfile(f"UnsupportedProfile: case kind {shown} has no wire contract input")
    return {"environment": case.get("environment"), "norms": case.get("norms")}


def _environment(root):
    return root["environment"]


def _vocabulary(root):
    return _environment(root)["vocabulary"]


def _block(root):
    return _vocabulary(root).get("soft", {"outranking": {"mode": "strict"}})


def _failure(call):
    try:
        call()
    except VEError as exc:
        return {"message": str(exc)}
    return None


def w1_declarations(root, items):
    data = _environment(root)
    vocabulary = _vocabulary(root)
    base = sorted({p for p in data["profiles"] if p in INHERITED_PROFILES}
                  | {"norms@0", profiles.BASE})
    stripped = {**data, "profiles": base, "vocabulary": {
        "sorts": vocabulary["sorts"], "constants": vocabulary["constants"],
        "predicates": {name: ({k: v for k, v in entry.items() if k != "instruction_of"}
                             if type(entry) is dict else entry)
                       for name, entry in vocabulary["predicates"].items()}}}
    return _failure(lambda: soft.soft_route_environment(stripped, data["profiles"]))


def profile_registered(root, items):
    value = soft_source_item(root, items)
    return value not in ROUTE_PROFILES


def soft_source_item(root, items):
    value = root
    for token in items[0]:
        value = value[int(token)] if type(value) in (list, tuple) else value[token]
    return value


def no_definitions(root, items):
    return any(type(entry) is dict and "defined" in entry
               for entry in _vocabulary(root)["predicates"].values())


def no_data_flags(root, items):
    return any(type(entry) is dict and (entry.get("functional") or entry.get("total"))
               for entry in _vocabulary(root)["predicates"].values())


def w1_rule_fields(root, items):
    raw = soft_source_item(root, items)["norm"]
    def check():
        name = raw["name"]
        if type(name) is not str or len(name) > 64 or not soft._NAME.fullmatch(name):
            raise VEError(f"InvalidInput: invalid rule name {name!r}")
        if type(raw["predicate"]) is not str:
            raise VEError("InvalidInput: rule predicate and precedence edges must be strings")
        if type(raw["sign"]) is not bool:
            raise VEError("InvalidInput: invalid sign or too many carve-outs")
        if type(raw["unless"]) is not list or type(raw["over"]) is not list:
            raise VEError("InvalidInput: unless and over must be arrays")
        if len(raw["unless"]) > 8:
            raise VEError("InvalidInput: invalid sign or too many carve-outs")
        if any(type(parent) is not str for parent in raw["over"]):
            raise VEError("InvalidInput: rule predicate and precedence edges must be strings")
        soft._fol(raw["guard"])
        for formula in raw["unless"]:
            soft._fol(formula)
    return _failure(check)


def fol_formula(root, items):
    return _failure(lambda: soft._fol(soft_source_item(root, items)))


def regulated_predicate(root, items):
    rule = soft_source_item(root, items)
    predicate = rule["norm"]["predicate"]
    declaration = _vocabulary(root)["predicates"].get(predicate)
    return type(declaration) is not dict or "regulated" not in declaration


def over_same_predicate(root, items):
    parent_name = soft_source_item(root, items)
    rule = root["norms"][int(items[1][-1])]["norm"]
    parent = next(item["norm"] for item in root["norms"]
                  if item["norm"]["name"] == parent_name)
    if rule["predicate"] != parent["predicate"]:
        return {"rule": rule["name"], "predicate": rule["predicate"],
                "parent_predicate": parent["predicate"]}
    return None


def _rank_above(root):
    block = _block(root)
    above = {rank: set() for rank in block.get("ranks", [])}
    for higher, lower in block.get("outranks", []):
        above[lower].add(higher)
    for rank in above:
        pending = list(above[rank])
        while pending:
            parent = pending.pop()
            for ancestor in above[parent] - above[rank]:
                above[rank].add(ancestor)
                pending.append(ancestor)
    return above


def outranks_acyclic(root, items):
    ranks = _block(root).get("ranks", [])
    graph = {rank: set() for rank in ranks}
    for higher, lower in _block(root).get("outranks", []):
        graph[higher].add(lower)
    try:
        soft.dependency_order(graph)
    except VEError as exc:
        message = str(exc)
        return {"detail": message.removeprefix("DependencyCycle: ")}
    return None


def tie_not_comparable(root, items):
    a, b = soft_source_item(root, items)
    above = _rank_above(root)
    return a in above[b] or b in above[a]


def ties_distinct_unordered(root, items):
    ties = _block(root).get("ties", [])
    return len({frozenset(pair) for pair in ties}) != len(ties)


def _prepared(root):
    environment = soft.SoftEnvironment(_environment(root))
    fields = [soft._rule_fields(unit, environment.soft.get("exception_decider"))
              for unit in root["norms"]]
    document = object.__new__(soft.SoftNormDocument)
    document.env = environment
    document.rules = tuple(soft._soft_rule(x) for x in fields)
    document.collisions = tuple(sorted(((min(left, right, key=lambda r: r.core.name),
                                         max(left, right, key=lambda r: r.core.name))
                                        for i, left in enumerate(document.rules)
                                        for right in document.rules[i + 1:]
                                        if left.mode == right.mode == "default"
                                        and document._incompatible(left, right)),
                                       key=lambda pair: (pair[0].core.name, pair[1].core.name)))
    return document


def _oracle_decisions(document):
    """The frozen Python oracle's decision names, used only by wire-contract tests."""
    generated = {}
    for rule in document.rules:
        args = list(document.env.predicates[rule.core.predicate].arguments)
        if rule.mode == "default":
            generated[soft._decision_name(rule)] = args
        for party in rule.alterable:
            generated[soft._decision_name(rule, party)] = args
    if document.env.soft["outranking"]["mode"] == "holistic":
        for left, right in document.collisions:
            pair = document._rank_pair(left, right)
            if pair is not None:
                name = document._outweighs_name(*pair, document._act(left),
                                                 document.env.predicates[left.core.predicate].arguments)
                generated[name] = list(document.env.predicates[left.core.predicate].arguments)
    return generated


def decision_names_fit(root, items):
    """6.4a: the first decision name over the limit, prefix by prefix and in rule order within a prefix, as
    `SoftNormDocument` and Lean's `Wire.primeVocabulary` (`decisionNames`) report it."""
    decisions = _oracle_decisions(_prepared(root))
    for prefix in DECISION_PREFIXES:
        for name in decisions:
            if name.startswith(prefix) and len(name.encode("utf-8")) > MAX_IDENTIFIER_BYTES:
                return {"name": name}
    return None


def extended_vocabulary_fits(root, items):
    document = _prepared(root)
    return len(document.env.predicates) + len(_oracle_decisions(document)) > MAX_PREDICATES


def rule_typing(root, items):
    context = soft._declarations(_environment(root), False)
    index = int(items[0][-1])
    rule = soft._rule_fields(root["norms"][index], context.exception_decider)
    stripped = replace(rule, conditions={"sufficient": (), "necessary": ()})
    for candidate, member in ((stripped, "5.7"), (rule, "5.8a")):
        try:
            soft._rule_references(context.env, context.parties, context.ranks, candidate)
        except VEError as exc:
            message = str(exc)
            if member == "5.8a" and exc.code == "SOFT_INVALID_EXCEPTION_CONDITION":
                return "5.8b", {"detail": message.removeprefix("InvalidInput: exception condition of rule ")}
            return member, {"message": message}
    return None


def soft_semantic(root, items):
    document = _prepared(root)
    try:
        soft.NormDocument(document.env, [rule.core for rule in document.rules])
    except VEError as exc:
        message = str(exc)
        if message in ("AST exceeds 10,000 nodes", "ResourceLimit: AST exceeds 10,000 nodes"):
            return "6.5a", {}
        if message in ("precedence depth", "ResourceLimit: precedence depth"):
            return "6.6", {}
        if message.startswith("DependencyCycle: "):
            graph = {rule.core.name: set(rule.core.over) for rule in document.rules}
            try:
                soft.dependency_order(graph)
            except VEError:
                member = "6.5b"
            else:
                member = "6.7"
            return member, {"detail": message.removeprefix("DependencyCycle: ")}
        # 6.5 to 6.7 name only the base W1 faults above. A different base
        # rejection has no member in this classifier and remains a residual.
        return None
    try:
        soft.load_soft_document(_environment(root), root["norms"])
    except VEError as exc:
        message = str(exc)
        if message.startswith("SoftOverHard: "):
            return "6.8", {"detail": message.removeprefix("SoftOverHard: ")}
        for prefix, member in (("ResourceLimit: derived carve-out of rule ", "6.9"),
                               ("ResourceLimit: generated soft premise", "6.11"),
                               ("ResourceLimit: generated norm layer ", "6.12"),
                               ("ResourceLimit: generated conflict target ", "6.13")):
            if message.startswith(prefix):
                detail = message[len(prefix):]
                return member, {"detail": " of rule " + detail if member == "6.9" else detail}
        if message == "ResourceLimit: generated norm layers":
            return "6.15", {}
        if message == "ResourceLimit: generated background":
            return "6.14", {}
        if message.startswith("DependencyCycle: "):
            return "6.10a", {"detail": message.removeprefix("DependencyCycle: ")}
        # Rule 12 tests the exception class where Lean tests the leading `ResourceLimit: ` (section 6);
        # it also covers Python's extra rule, the text `ResourceLimit: derived carve-out` alone.
        if isinstance(exc, ResourceLimit):
            return "6.10b", {"message": message}
        # Rule 13: any other message names no member (revision 3), as rule 3a for the base, and shows as a
        # residual. No input is known that reaches it: W1 on T′ fails only on its limits or strata.
    return None


REGISTRY = Registry().register(
    hooks={name: globals()[name] for name in (
        "w1_declarations", "profile_registered", "no_definitions", "no_data_flags",
        "w1_rule_fields", "fol_formula", "regulated_predicate", "over_same_predicate",
        "outranks_acyclic", "tie_not_comparable", "ties_distinct_unordered",
        "decision_names_fit", "extended_vocabulary_fits")},
    classifiers={"rule_typing": rule_typing, "soft_semantic": soft_semantic},
    adapters={"soft_source": soft_source})
