"""P0 route fixtures shared by Python, Rust and the Lean `route` subcommand.

Every case carries `kind` and an `expected` verdict that all three
implementations must reproduce (tests/test_p0_three_way.py). Certificates are
produced by the Python prover on the v0.2 environment itself, so their binding
(Background ++ premises, v0.2 meaning ids) is part of what is tested.

Families: `elaborated-document`, `invalid-background-model`,
`dependency-order`, `labels`, `admission`, `vacuity`.
"""
from __future__ import annotations

import random
from copy import deepcopy

from ve.profiles import LANGUAGE, SPEC_REVISION

STRING = "$string"
EMPTY_MODEL = {"complete": True, "domains": {}, "constants": {}, "relations": {}}


def environment():
    return {"language": LANGUAGE, "profiles": ["relational-fol@0"],
            "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": {}, "predicates": {}, "constants": {
                "alpha": {"sort": STRING},
                "beta": {"sort": STRING}}}}


def envelope(vocabulary, profiles=("relational-fol@0",)):
    return {"language": LANGUAGE, "profiles": list(profiles), "spec_revision": SPEC_REVISION,
            "vocabulary": deepcopy(vocabulary)}


# A vocabulary with ordinary symbols beside the literals. Stage 1 is equality
# only: `$string` is the sort of declared literal constants, never a predicate
# argument; a literal's description is optional.
VOCAB = {
    "sorts": {"person": {"description": "a person"}},
    "predicates": {"in_finance": {"arguments": ["person"], "description": "works in finance"},
                   "in_legal": {"arguments": ["person"], "description": "works in legal"},
                   "senior": {"arguments": ["person"], "description": "is senior"}},
    "constants": {"alice": {"sort": "person", "description": "Alice"},
                  "bob": {"sort": "person", "description": "Bob"},
                  "finance": {"sort": STRING, "description": "the string finance"},
                  "legal": {"sort": STRING}},
}
MODEL = {"complete": True, "domains": {"person": ["a", "b"], STRING: ["f", "l"]},
         "constants": {"alice": "a", "bob": "b", "finance": "f", "legal": "l"},
         "relations": {"in_finance": [["a"]], "in_legal": [], "senior": [["a"]]}}
ALIAS = deepcopy(MODEL)
ALIAS["constants"]["legal"] = "f"

FIN_A = ["unary", "in_finance", ["const", "alice"]]
LEGAL_A = ["unary", "in_legal", ["const", "alice"]]
SAME = ["eq", ["const", "finance"], ["const", "legal"]]
SENIOR_A = ["unary", "senior", ["const", "alice"]]
DISTINCT = ["not", SAME]

ORDER_VOCAB = {"sorts": {}, "predicates": {},
               "constants": {"limit": {"sort": "$int", "description": "the limit"},
                             "finance": {"sort": STRING}, "legal": {"sort": STRING}}}
ORDER_MODEL = {"complete": True, "domains": {STRING: ["f", "l"]},
               "constants": {"limit": "2", "finance": "f", "legal": "l"}, "relations": {}}
ORDER_ALIAS = deepcopy(ORDER_MODEL)
ORDER_ALIAS["constants"]["legal"] = "f"
LIMIT_SMALL = ["le", ["const", "limit"], ["num", "3"]]


# W3: identity-bound definitions over a base vocabulary, with literals beside
# them (Background is definitions, then literals). Bodies are typed in the
# argument context, index 0 being the last argument.
def _unary(p, i):
    return ["unary", p, ["var", i]]


def _binary(p, i, j):
    return ["binary", p, ["var", i], ["var", j]]


def defined(arguments, body, description):
    return {"arguments": arguments, "description": description,
            "defined": {"arguments": arguments, "body": body}}


DEF_VOCAB = {
    "sorts": {"person": {"description": "a person"}},
    "predicates": {
        "in_finance": {"arguments": ["person"], "description": "works in finance"},
        "senior": {"arguments": ["person"], "description": "is senior"},
        "supervises": {"arguments": ["person", "person"], "description": "supervises"},
        "lead": defined(["person"], ["and", _unary("boss", 0), _unary("senior_finance", 0)],
                        "is a senior finance boss"),
        "boss": defined(["person"], ["exists", "person", _binary("supervises", 1, 0)],
                        "supervises someone"),
        "senior_finance": defined(["person"], ["and", _unary("senior", 0), _unary("in_finance", 0)],
                                  "is senior and works in finance"),
        "above": defined(["person", "person"],
                         ["or", _binary("supervises", 1, 0),
                          ["exists", "person", ["and", _binary("supervises", 2, 0),
                                                _binary("supervises", 0, 1)]]],
                         "supervises directly or through one person")},
    "constants": {"alice": {"sort": "person", "description": "Alice"},
                  "bob": {"sort": "person", "description": "Bob"},
                  "finance": {"sort": STRING}, "legal": {"sort": STRING}},
}
DEF_MODEL = {"complete": True, "domains": {"person": ["a", "b", "c"], STRING: ["f", "l"]},
             "constants": {"alice": "a", "bob": "b", "finance": "f", "legal": "l"},
             "relations": {"in_finance": [["a"]], "senior": [["a"], ["b"]],
                           "supervises": [["a", "b"], ["b", "c"]]}}
LEAD_A = ["unary", "lead", ["const", "alice"]]
LEAD_B = ["unary", "lead", ["const", "bob"]]
BOSS_A = ["unary", "boss", ["const", "alice"]]
SF_A = ["unary", "senior_finance", ["const", "alice"]]
SUP_AB = ["binary", "supervises", ["const", "alice"], ["const", "bob"]]
ABOVE_AB = ["binary", "above", ["const", "alice"], ["const", "bob"]]
NOBODY_ABOVE_A = ["forall", "person", ["not", ["binary", "above", ["var", 0], ["const", "alice"]]]]


def definitions_envelope(vocabulary=DEF_VOCAB, profiles=("definitions@0", "relational-fol@0")):
    return envelope(vocabulary, profiles)


def two_definitions(a_body, b_body):
    vocabulary = {"sorts": {"point": {"description": "a point"}},
                  "predicates": {"base": {"arguments": ["point"], "description": "base"},
                                 "a": defined(["point"], a_body, "a"),
                                 "b": defined(["point"], b_body, "b")},
                  "constants": {}}
    return definitions_envelope(vocabulary)


def _python_env(env_json):
    from ve import Environment
    return Environment(env_json)


def certificate(env_json, premises, conclusion):
    """A Python certificate; its checked list is Background ++ premises."""
    from ve.ast import formula_from_data
    from ve.entailment import prove_entailment
    env = _python_env(env_json)
    result = prove_entailment(env, [formula_from_data(env, p) for p in premises],
                              formula_from_data(env, conclusion))
    assert result.certificate is not None, (premises, conclusion, result)
    return result.certificate


def _background_count(env_json):
    from ve.background import background
    return len(background(_python_env(env_json)))


def elaborated_document_cases():
    cases = []

    def case(id_, kind, expected, environment, **fields):
        cases.append({"id": id_, "kind": kind, "environment": deepcopy(environment), **fields,
                      "expected": expected})

    # Sort-only literals (the P0-Py seed cases).
    env = environment()
    model = {"complete": True, "domains": {STRING: ["a", "b"]},
             "constants": {"alpha": "a", "beta": "b"}, "relations": {}}
    alpha_beta = ["eq", ["const", "alpha"], ["const", "beta"]]
    case("literals-distinct", "evaluate", {"status": "ok", "values": [True]}, env,
         model=model, ast=[["not", alpha_beta]])
    case("literals-equal-false", "evaluate", {"status": "ok", "values": [False]}, env,
         model=model, ast=[alpha_beta])
    case("literals-countermodel", "countermodel", {"status": "ok", "refutes": True}, env,
         model=model, premises=[], conclusion=alpha_beta)
    case("literals-search", "search", {"status": "ok", "found": True}, env,
         max_domain_size=2, premises=[], conclusion=alpha_beta)
    order_env = deepcopy(env)
    order_env["profiles"] = ["order@0", "relational-fol@0"]
    case("order-with-literals", "evaluate", {"status": "ok", "values": [True]}, order_env,
         model=model, ast=[["not", alpha_beta]])

    # Literals beside ordinary symbols; described and undescribed literals.
    rich = envelope(VOCAB)
    case("eval-literals", "evaluate", {"status": "ok", "values": [True, False]}, rich,
         model=MODEL, ast=[FIN_A, SAME])
    case("countermodel-refutes", "countermodel", {"status": "ok", "refutes": True}, rich,
         model=MODEL, premises=[FIN_A], conclusion=LEGAL_A)
    case("search-respects-background", "search", {"status": "ok", "found": True}, rich,
         max_domain_size=2, premises=[FIN_A], conclusion=["not", DISTINCT])
    case("string-quantifier-rejected", "evaluate", {"status": "error", "code": "rejected"}, rich,
         model=MODEL, ast=[["forall", STRING, ["top"]]])
    case("undeclared-literal-rejected", "evaluate", {"status": "error", "code": "rejected"}, rich,
         model=MODEL, ast=[["eq", ["const", "finance"], ["const", "marketing"]]])
    string_arg = deepcopy(VOCAB)
    string_arg["predicates"]["dept"] = {"arguments": ["person", STRING], "description": "department"}
    case("string-predicate-argument-rejected", "evaluate", {"status": "error", "code": "rejected"},
         envelope(string_arg), model=MODEL, ast=[["top"]])
    bad_description = deepcopy(VOCAB)
    bad_description["constants"]["legal"] = {"sort": STRING, "description": ""}
    case("literal-empty-description-rejected", "evaluate", {"status": "error", "code": "rejected"},
         envelope(bad_description), model=MODEL, ast=[["top"]])
    extra_field = deepcopy(VOCAB)
    extra_field["constants"]["legal"] = {"sort": STRING, "value": "legal"}
    case("literal-extra-field-rejected", "evaluate", {"status": "error", "code": "rejected"},
         envelope(extra_field), model=MODEL, ast=[["top"]])
    too_many = envelope({"sorts": {}, "predicates": {},
                         "constants": {f"lit{i}": {"sort": STRING} for i in range(65)}})
    case("too-many-literals", "evaluate", {"status": "error", "code": "ResourceLimit"}, too_many,
         model=EMPTY_MODEL, ast=[["top"]])

    # Certificates: the checked list is Background ++ premises, bound by v0.2 meaning ids.
    gamma = [["or", SAME, FIN_A]]
    cert = certificate(rich, gamma, FIN_A)
    bg = _background_count(rich)
    case("certificate-uses-background", "certificate", {"status": "ok", "valid": True, "background": bg},
         rich, premises=gamma, conclusion=FIN_A, certificate=cert)
    # A premise list that happens to start with the Background premise is still
    # prefixed by Background: the binding is always Background ++ premises.
    doubled = [DISTINCT] + gamma
    case("certificate-background-prefix-not-merged", "certificate",
         {"status": "ok", "valid": True, "background": bg}, rich,
         premises=doubled, conclusion=FIN_A, certificate=certificate(rich, doubled, FIN_A))
    case("certificate-premise-list-mismatch", "certificate", {"status": "ok", "valid": False}, rich,
         premises=doubled, conclusion=FIN_A, certificate=cert)
    from ve.identity import meaning_id
    from ve.ast import formula_from_data
    penv = _python_env(rich)
    unbound = dict(cert, premise_meaning_ids=[meaning_id(penv, formula_from_data(penv, p)) for p in gamma])
    case("certificate-without-background-binding", "certificate", {"status": "ok", "valid": False},
         rich, premises=gamma, conclusion=FIN_A, certificate=unbound)
    case("certificate-stale-environment", "certificate", {"status": "ok", "valid": False}, rich,
         premises=gamma, conclusion=FIN_A, certificate=dict(cert, environment_id="0" * 64))

    # The closure family carries the same literals and Background.
    closure = envelope(VOCAB, ["closure@0", "relational-fol@0"])
    case("closure-literals", "evaluate", {"status": "ok", "values": [True, False]}, closure,
         model=MODEL, ast=[FIN_A, SAME])
    case("closure-certificate-uses-background", "certificate",
         {"status": "ok", "valid": True, "background": bg}, closure,
         premises=gamma, conclusion=FIN_A, certificate=certificate(closure, gamma, FIN_A))

    # The order family admits literals (plan 3.1: Background depends on env only).
    order = envelope(ORDER_VOCAB, ["order@0", "relational-fol@0"])
    order_gamma = [["or", SAME, LIMIT_SMALL]]
    case("order-literals-evaluate", "evaluate", {"status": "ok", "values": [True, False]}, order,
         model=ORDER_MODEL, ast=[LIMIT_SMALL, SAME])
    case("order-countermodel", "countermodel", {"status": "ok", "refutes": True}, order,
         model=ORDER_MODEL, premises=[DISTINCT], conclusion=["lt", ["const", "limit"], ["num", "0"]])
    case("order-certificate-uses-background", "certificate",
         {"status": "ok", "valid": True, "background": 1}, order,
         premises=order_gamma, conclusion=LIMIT_SMALL,
         certificate=certificate(order, order_gamma, LIMIT_SMALL))
    case("order-string-quantifier-rejected", "evaluate", {"status": "error", "code": "rejected"}, order,
         model=ORDER_MODEL, ast=[["forall", STRING, ["top"]]])

    # Envelopes: UnsupportedProfile names the profile or the pair.
    for id_, profiles, message in [
            ("unknown-profile", ["mystery@0", "relational-fol@0"], "Unsupported profile mystery@0"),
            ("profile-unsorted", ["relational-fol@0", "closure@0"], "profiles must be sorted and unique"),
            ("profile-duplicate", ["relational-fol@0", "relational-fol@0"],
             "profiles must be sorted and unique"),
            ("profile-missing-base", ["definitions@0"], "Missing profile relational-fol@0"),
            ("order-nary", ["nary@0", "order@0", "relational-fol@0"],
             "Unsupported profile combination nary@0 x order@0"),
            ("closure-order", ["closure@0", "order@0", "relational-fol@0"],
             "Unsupported profile combination closure@0 x order@0"),
            ("nary-without-closure", ["nary@0", "relational-fol@0"],
             "Unsupported profile nary@0 without closure@0"),
            ("closure-nary-gated", ["closure@0", "nary@0", "relational-fol@0"],
             "the closure+n-ary checker is gated until W4 stage 1 lands")]:
        case(id_, "evaluate", {"status": "error", "code": "UnsupportedProfile",
                               "error": "UnsupportedProfile: " + message},
             envelope({"sorts": {}, "predicates": {}, "constants": {}}, profiles),
             model=EMPTY_MODEL, ast=[["top"]])
    case("revision-unsupported", "evaluate",
         {"status": "error", "code": "UnsupportedProfile",
          "error": "UnsupportedProfile: Unsupported specification revision ve-v0.2-other"},
         dict(envelope({"sorts": {}, "predicates": {}, "constants": {}}), spec_revision="ve-v0.2-other"),
         model=EMPTY_MODEL, ast=[["top"]])
    definition_cases(case)
    for id_, profiles in [("family-fol", ["definitions@0", "documents@1", "relational-fol@0"]),
                          ("family-closure", ["closure@0", "relational-fol@0"]),
                          ("family-order", ["order@0", "relational-fol@0"])]:
        case(id_, "evaluate", {"status": "ok", "values": [True]},
             envelope({"sorts": {}, "predicates": {}, "constants": {}}, profiles),
             model=EMPTY_MODEL, ast=[["top"]])
    return cases


def definition_cases(case):
    """W3: defined tables computed from bodies, Background = definitions ++
    literals, the shared cycle diagnostic, and the explicit gates."""
    env = definitions_envelope()
    rejected = {"status": "error", "code": "rejected"}
    case("defs-evaluate", "evaluate", {"status": "ok", "values": [True, False, True, True]}, env,
         model=DEF_MODEL, ast=[LEAD_A, LEAD_B, ABOVE_AB, NOBODY_ABOVE_A])
    case("defs-countermodel", "countermodel", {"status": "ok", "refutes": True}, env,
         model=DEF_MODEL, premises=[BOSS_A], conclusion=LEAD_B)
    case("defs-search", "search", {"status": "ok", "found": True}, env, max_domain_size=2,
         premises=[BOSS_A], conclusion=LEAD_A)
    gamma = [SF_A, SUP_AB]
    bg = _background_count(env)
    case("defs-certificate-uses-definitions", "certificate",
         {"status": "ok", "valid": True, "background": bg}, env,
         premises=gamma, conclusion=LEAD_A, certificate=certificate(env, gamma, LEAD_A))
    changed = deepcopy(DEF_VOCAB)
    changed["predicates"]["boss"]["defined"]["body"] = ["top"]
    case("defs-certificate-other-version", "certificate", {"status": "ok", "valid": False}, env,
         premises=gamma, conclusion=LEAD_A,
         certificate=certificate(definitions_envelope(changed), gamma, LEAD_A))
    closure = definitions_envelope(DEF_VOCAB, ("closure@0", "definitions@0", "relational-fol@0"))
    case("defs-closure-certificate", "certificate",
         {"status": "ok", "valid": True, "background": bg}, closure,
         premises=gamma, conclusion=LEAD_A, certificate=certificate(closure, gamma, LEAD_A))
    case("defs-closure-evaluate", "evaluate", {"status": "ok", "values": [True, False]}, closure,
         model=DEF_MODEL, ast=[LEAD_A, LEAD_B])
    case("defs-background", "background", {"status": "ok", "background": _background_data(env),
                                           "generators": ["definitions"] * 4 + ["literals"]}, env)
    case("defs-cycle", "evaluate",
         {"status": "error", "code": "DependencyCycle", "error": "DependencyCycle: a, b"},
         two_definitions(_unary("b", 0), _unary("a", 0)), model=EMPTY_MODEL, ast=[["top"]])
    case("defs-self-reference", "evaluate",
         {"status": "error", "code": "DependencyCycle", "error": "DependencyCycle: a"},
         two_definitions(_unary("a", 0), _unary("base", 0)), model=EMPTY_MODEL, ast=[["top"]])
    typed_error = {"status": "error", "error":
                   "Definition a: the body is not a typed formula over the symbols below it"}
    case("defs-free-variable", "evaluate", typed_error,
         two_definitions(_unary("base", 1), _unary("base", 0)), model=EMPTY_MODEL, ast=[["top"]])
    case("defs-unknown-symbol", "evaluate", typed_error,
         two_definitions(_unary("missing", 0), _unary("base", 0)), model=EMPTY_MODEL, ast=[["top"]])
    mismatch = deepcopy(DEF_VOCAB)
    mismatch["predicates"]["boss"]["defined"]["arguments"] = ["person", "person"]
    case("defs-arguments-mismatch", "evaluate", rejected, definitions_envelope(mismatch),
         model=DEF_MODEL, ast=[["top"]])
    case("defs-profile-missing", "evaluate", rejected, envelope(DEF_VOCAB), model=DEF_MODEL, ast=[["top"]])
    # Flags (W5) are never allowed on a defined predicate: its table is its body's.
    flagged = deepcopy(DEF_VOCAB)
    flagged["predicates"]["boss"]["functional"] = True
    case("defs-flag-rejected", "evaluate", rejected,
         definitions_envelope(flagged, ("data@0", "definitions@0", "relational-fol@0")),
         model=DEF_MODEL, ast=[["top"]])
    order = definitions_envelope(
        {"sorts": {"point": {"description": "a point"}},
         "predicates": {"base": {"arguments": ["point"], "description": "base"},
                        "a": defined(["point"], _unary("base", 0), "a")}, "constants": {}},
        ("definitions@0", "order@0", "relational-fol@0"))
    case("defs-order-family-gated", "evaluate",
         {"status": "error", "code": "UnsupportedProfile", "error":
          "UnsupportedProfile: definitions on the order family require an order definition layer"},
         order, model=EMPTY_MODEL, ast=[["top"]])
    reach = deepcopy(closure)
    reach["vocabulary"]["predicates"]["boss"]["defined"]["body"] = [
        "exists", "person", ["reach", "plus", ["named", "supervises"], ["var", 1], ["var", 0]]]
    case("defs-reach-body-gated", "evaluate",
         {"status": "error", "code": "UnsupportedProfile", "error":
          "UnsupportedProfile: definition bodies with reachability require a closure definition layer"},
         reach, model=DEF_MODEL, ast=[["top"]])


def _background_data(env_json):
    from ve.ast import _to_data
    from ve.background import background
    return [_to_data(p.formula) for p in background(_python_env(env_json))]


def invalid_background_model_cases():
    env = environment()
    flags = deepcopy(env)
    flags["profiles"] = ["data@0", "relational-fol@0"]
    flags["vocabulary"] = {"sorts": {"person": {"description": "Person."},
                                      "department": {"description": "Department."}},
                            "predicates": {"dept": {"arguments": ["person", "department"],
                                                    "description": "Department of person.",
                                                    "functional": True, "total": True}},
                            "constants": {}}
    defined_env = deepcopy(env)
    defined_env["profiles"] = ["definitions@0", "relational-fol@0"]
    defined_env["vocabulary"] = {"sorts": {"person": {"description": "Person."}},
                             "predicates": {"base": {"arguments": ["person"], "description": "Base."},
                                            "derived": {"arguments": ["person"],
                                                        "description": "Defined from base.",
                                                        "defined": {"arguments": ["person"],
                                                                    "body": ["unary", "base", ["var", 0]]}}},
                             "constants": {}}
    invalid = {"status": "error", "code": "InvalidModel", "generator": "literals"}
    rich = envelope(VOCAB)
    return [{"id": "literal-alias", "kind": "evaluate", "environment": env,
             "model": {"complete": True, "domains": {STRING: ["a"]},
                       "constants": {"alpha": "a", "beta": "a"}, "relations": {}},
             "ast": [["top"]], "expected": invalid},
            {"id": "literal-alias-countermodel", "kind": "countermodel", "environment": rich,
             "model": ALIAS, "premises": [FIN_A], "conclusion": LEGAL_A, "expected": invalid},
            {"id": "literal-alias-closure", "kind": "evaluate",
             "environment": envelope(VOCAB, ["closure@0", "relational-fol@0"]),
             "model": ALIAS, "ast": [["top"]], "expected": invalid},
            {"id": "literal-alias-order", "kind": "evaluate",
             "environment": envelope(ORDER_VOCAB, ["order@0", "relational-fol@0"]),
             "model": ORDER_ALIAS, "ast": [["top"]], "expected": invalid},
            {"id": "literal-alias-order-countermodel", "kind": "countermodel",
             "environment": envelope(ORDER_VOCAB, ["order@0", "relational-fol@0"]),
             "model": ORDER_ALIAS, "premises": [], "conclusion": ["bottom"], "expected": invalid},
            {"id": "partial-total-table", "kind": "evaluate", "pending": "W5", "environment": flags,
             "model": {"complete": True, "domains": {"person": ["alice"],
                        "department": ["finance"]}, "constants": {}, "relations": {"dept": []}},
             "ast": [["top"]], "expected": {"status": "error", "code": "InvalidModel", "generator": "flags"}},
            {"id": "supplied-defined-table", "kind": "evaluate", "environment": defined_env,
             "model": {"complete": True, "domains": {"person": ["alice"]},
                       "constants": {}, "relations": {"base": [["alice"]],
                                                     "derived": [["alice"]]}},
             "ast": [["top"]],
             "expected": {"status": "error", "code": "InvalidModel", "generator": "definitions"}}]


def _dag_reference(nodes):
    """The documented algorithm (docs/P0-Lean-NOTES.md), used only to write expectations."""
    names = [n["name"] for n in nodes]
    duplicate = next((n for n in names if names.count(n) > 1), None)
    if duplicate is not None:
        return {"status": "error", "code": "DuplicateDeclaration",
                "error": f"DuplicateDeclaration: dependency node {duplicate}"}
    remaining = {n["name"]: set(n["mentions"]) & set(names) for n in nodes}
    order = []
    while remaining:
        ready = [n for n in sorted(remaining) if not remaining[n]]
        if not ready:
            return {"status": "error", "code": "DependencyCycle",
                    "error": "DependencyCycle: " + ", ".join(sorted(remaining))}
        order.append(ready[0])
        del remaining[ready[0]]
        for deps in remaining.values():
            deps.discard(ready[0])
    return {"status": "ok", "order": order}


def dependency_order_cases(count=200, seed=20260925):
    env = envelope({"sorts": {}, "predicates": {}, "constants": {}},
                   ["definitions@0", "norms@0", "relational-fol@0"])
    fixed = [
        # A definition above a norm: violation(a) := required(a) ∧ ¬done(a).
        ("definition-above-norm", [{"name": "violation", "mentions": ["required", "done"]},
                                   {"name": "required", "mentions": ["safe"]},
                                   {"name": "safe", "mentions": ["base"]}]),
        # A norm whose guard uses a definition below it.
        ("norm-guard-uses-definition", [{"name": "required", "mentions": ["eligible"]},
                                        {"name": "eligible", "mentions": ["member", "adult"]}]),
        ("cycle-definition-norm", [{"name": "a", "mentions": ["b"]}, {"name": "b", "mentions": ["a"]},
                                   {"name": "c", "mentions": ["a"]}, {"name": "d", "mentions": []}]),
        ("self-loop", [{"name": "p", "mentions": ["p"]}]),
        ("duplicate-node", [{"name": "q", "mentions": []}, {"name": "p", "mentions": []},
                            {"name": "q", "mentions": ["p"]}]),
        ("empty-graph", []),
        ("too-large", [{"name": f"n{i}", "mentions": []} for i in range(257)]),
    ]
    rng = random.Random(seed)
    alphabet = [chr(ord("a") + i) for i in range(10)] + ["_x", "Z", "é"]
    for index in range(count):
        size = rng.randint(1, 9)
        names = rng.sample(alphabet, size) if rng.random() > 0.1 else rng.choices(alphabet, k=size)
        nodes = []
        for name in names:
            mentions = rng.sample(alphabet + ["base", "done"], rng.randint(0, 3))
            if rng.random() < 0.6:  # mostly downward edges, so both outcomes occur
                mentions = [m for m in mentions if m not in names or m < name]
            nodes.append({"name": name, "mentions": mentions})
        fixed.append((f"generated-{index:03d}", nodes))
    cases = []
    for id_, nodes in fixed:
        expected = (_dag_reference(nodes) if len(nodes) <= 256 else
                    {"status": "error", "code": "ResourceLimit", "error": "ResourceLimit: dependency graph size"})
        cases.append({"id": id_, "kind": "dependency-order", "environment": env, "nodes": nodes,
                      "expected": expected})
    return cases


LABELS_VALID = [
    "asserted", "bridge:accepts(bob,u2)", "bridge:accepts(A.b-c_d,unit.1)",
    "background:flags", "background:definitions", "background:literals", "background:profile",
    "cite:bundle/lemma", "cite:b-1/l.2", "open:reasonable", "readings:s1@0:0", "readings:s1@1:all",
    "readings:s@12:340", "readings:s@123456789012345678901234567890:7", "narrowing:n1",
    "open:" + "x" * 64,
]
LABELS_INVALID = [
    "", "Asserted", "asserted ", "bridge:accepts(bob)", "bridge:accepts(bob,u2,u3)",
    "bridge:accepts(,u2)", "bridge:accepts(bob,u2", "bridge:accepts (bob,u2)", "bridge:accepts(b b,u2)",
    "background:", "background:Literals", "background:strings", "cite:bundle", "cite:a/b/c", "cite:/l",
    "open:", "open:a b", "open:é", "open:" + "x" * 65, "readings:s1@01:0", "readings:s1@1:01",
    "readings:s1@1:", "readings:s1@:0", "readings:@1:0", "readings:s1@1:-1", "readings:s1@1_0:0",
    "readings:s1@1:ALL", "readings:s1@1:0:0", "readings:s1@1@2:0", "readings:s1@+1:0", "narrowing:",
    "narrowing:a/b", "label:x", "bridge:accepts(bob,u2) ", "cite:a/b\n", "readings:s1@١:0",
]


def label_cases():
    env = envelope({"sorts": {}, "predicates": {}, "constants": {}})
    cases = [{"id": f"valid-{i:02d}", "kind": "label", "environment": env, "label": label,
              "expected": {"status": "ok", "label": label}} for i, label in enumerate(LABELS_VALID)]
    cases += [{"id": f"invalid-{i:02d}", "kind": "label", "environment": env, "label": label,
               "expected": {"status": "error", "code": "AdmissionError",
                            "error": f"AdmissionError: invalid label {label}"}}
              for i, label in enumerate(LABELS_INVALID)]
    return cases


def admission_cases():
    """Python `ve.admission` and Lean `route` admit the same documents (FOL family)."""
    from ve.admission import admit_document
    env = envelope(VOCAB)
    cases = []

    def case(id_, document, error=None, environment=env):
        """`error`: an exact AdmissionError diagnostic, an error code, or a
        fragment of any other rejection."""
        if error is None:
            expected = {"status": "ok", **admit_document(environment, document)}
        elif error.startswith(("AdmissionError", "UnsupportedProfile:")):
            expected = {"status": "error", "code": error.split(":", 1)[0], "error": error}
        else:
            expected = {"status": "error",
                        "code": error if error in ("ResourceLimit", "UnsupportedProfile") else "rejected"}
        cases.append({"id": id_, "kind": "admission", "environment": deepcopy(environment),
                      "document": document, "expected": expected})

    bg_formula = DISTINCT
    units = [{"id": "u1", "span": [0, 20], "kind": "asserted", "content": SENIOR_A},
             {"id": "u2", "span": [21, 60], "kind": ["attributed", "bob", "says", "asserted"],
              "content": ["or", SAME, FIN_A]},
             {"id": "u3", "span": [61, 120],
              "kind": ["attributed", "alice", "believes",
                       ["hedged", "likely", ["causal", "because", "asserted", "asserted"]]]},
             {"id": "u4", "span": [120, 130], "kind": ["unformalised", "rhetoric"]}]
    raw = lambda premises, conclusion: _raw_certificate(env, premises, conclusion)  # noqa: E731
    premises = [["or", SAME, FIN_A], bg_formula]
    nodes = [{"name": "claim-u2", "ast": ["or", SAME, FIN_A], "label": "bridge:accepts(bob,u2)", "unit": "u2"},
             {"name": "distinct", "ast": bg_formula, "label": "background:literals"},
             {"name": "senior", "ast": SENIOR_A, "unit": "u1"},
             {"name": "root", "ast": FIN_A, "premises": ["claim-u2", "distinct"],
              "certificate": raw(premises, FIN_A)}]
    document = {"units": units, "graph": {"root": "root", "nodes": nodes}}
    case("bridge-background", document)

    def mutate(id_, change, error):
        doc = deepcopy(document)
        change(doc)
        case(id_, doc, error)

    def strip_bridge(doc):
        del doc["graph"]["nodes"][0]["label"]
    mutate("quoted-without-bridge", strip_bridge,
           "AdmissionError: quoted content of unit u2 is used without a bridge leaf")

    def strip_background(doc):
        del doc["graph"]["nodes"][1]["label"]
    mutate("background-label-stripped", strip_background,
           "AdmissionError: node distinct is not admitted under label asserted")

    def wrong_agent(doc):
        doc["graph"]["nodes"][0]["label"] = "bridge:accepts(alice,u2)"
    mutate("bridge-wrong-agent", wrong_agent,
           "AdmissionError: node claim-u2 is not admitted under label bridge:accepts(alice,u2)")

    def wrong_generator(doc):
        doc["graph"]["nodes"][1]["label"] = "background:flags"
    mutate("background-wrong-generator", wrong_generator,
           "AdmissionError: node distinct is not admitted under label background:flags")

    def invalid_label(doc):
        doc["graph"]["nodes"][1]["label"] = "background:strings"
    mutate("invalid-label", invalid_label, "AdmissionError: invalid label background:strings")

    def explicit_default(doc):
        doc["graph"]["nodes"][2]["label"] = "asserted"
    mutate("explicit-default-label", explicit_default, "non-canonical label")

    def overlapping(doc):
        doc["units"][1]["span"] = [10, 60]
    mutate("overlapping-spans", overlapping, "unit spans must be sorted and non-overlapping")

    def deep_kind(doc):
        kind = "asserted"
        for _ in range(16):
            kind = ["hedged", "could", kind]
        doc["units"][3]["kind"] = kind
    mutate("kind-too-deep", deep_kind, "ResourceLimit")

    def stale(doc):
        # A valid proof, bound to the premises in the other order.
        doc["graph"]["nodes"][3]["certificate"] = raw([bg_formula, ["or", SAME, FIN_A]], FIN_A)
    mutate("stale-edge-certificate", stale, "certificate is stale")

    # Citation and reading choices.
    cited = deepcopy(document)
    cited["lemmas"] = [{"name": "b1/t1", "conclusion": FIN_A,
                        "leaves": [{"ast": ["or", SAME, FIN_A], "label": "bridge:accepts(bob,u2)"}]}]
    cited["graph"] = {"root": "uses", "nodes": [
        nodes[0], {"name": "cited", "ast": FIN_A, "label": "cite:b1/t1"},
        {"name": "uses", "ast": FIN_A, "premises": ["cited", "claim-u2"],
         "certificate": raw([FIN_A, ["or", SAME, FIN_A]], FIN_A)}]}
    case("citation-with-leaves", cited,
         "UnsupportedProfile: document citations require a checked bundle binding")
    missing = deepcopy(cited)
    missing["graph"] = {"root": "cited", "nodes": [missing["graph"]["nodes"][1]]}
    case("citation-missing-leaf", missing, "AdmissionError: a cited lemma's leaves are missing from the report")

    readings = deepcopy(document)
    readings["reading_sets"] = [{"id": "s1", "version": 1, "readings": [FIN_A, LEGAL_A]}]
    readings["graph"] = {"root": "r", "nodes": [
        {"name": "r0", "ast": FIN_A, "label": "readings:s1@1:0"},
        {"name": "r1", "ast": LEGAL_A, "label": "readings:s1@1:1"},
        {"name": "r", "ast": FIN_A, "premises": ["r0", "r1"], "certificate": raw([FIN_A, LEGAL_A], FIN_A)}]}
    case("incompatible-choices", readings, "AdmissionError: incompatible reading choices")
    one = deepcopy(readings)
    one["graph"] = {"root": "r", "nodes": [
        {"name": "r0", "ast": FIN_A, "label": "readings:s1@1:0"},
        {"name": "r", "ast": FIN_A, "premises": ["r0"], "certificate": raw([FIN_A], FIN_A)}]}
    case("one-choice", one)
    both = deepcopy(readings)
    either = ["or", FIN_A, LEGAL_A]
    both["graph"] = {"root": "r", "nodes": [
        {"name": "rall", "ast": either, "label": "readings:s1@1:all"},
        {"name": "r0", "ast": FIN_A, "label": "readings:s1@1:0"},
        {"name": "r", "ast": FIN_A, "premises": ["rall", "r0"], "certificate": raw([either, FIN_A], FIN_A)}]}
    case("all-with-choice", both)
    extras = deepcopy(document)
    extras["open_terms"] = ["reasonable"]
    extras["narrowings"] = ["n1"]
    extras["graph"] = {"root": "r", "nodes": [
        {"name": "o", "ast": SENIOR_A, "label": "open:reasonable"},
        {"name": "n", "ast": FIN_A, "label": "narrowing:n1"},
        {"name": "r", "ast": FIN_A, "premises": ["o", "n"], "certificate": raw([SENIOR_A, FIN_A], FIN_A)}]}
    case("open-and-narrowing", extras)
    undeclared = deepcopy(extras)
    undeclared["narrowings"] = []
    case("undeclared-narrowing", undeclared, "AdmissionError: node n is not admitted under label narrowing:n1")
    order_doc = {"units": [], "graph": {"root": "t", "nodes": [{"name": "t", "ast": ["top"], "unit": "u"}]}}
    case("order-family-deferred", order_doc, "UnsupportedProfile",
         environment=envelope(ORDER_VOCAB, ["order@0", "relational-fol@0"]))
    return cases


def _raw_certificate(env_json, premises, conclusion):
    """An admission edge certificate: it binds exactly the premise nodes (the
    Background enters as explicit `background:<generator>` leaves)."""
    from ve.ast import formula_from_data
    from ve.entailment import _binding, _initial_branch, _Searcher, _validate_inputs
    env = _python_env(env_json)
    ps = _validate_inputs(env, [formula_from_data(env, p) for p in premises],
                          formula_from_data(env, conclusion), background=False)
    c = formula_from_data(env, conclusion)
    trace = _Searcher(10_000, env.closure, env=env).prove(_initial_branch(env, ps, c))
    assert trace is not None, (premises, conclusion)
    return {**_binding(env, ps, c), "trace": trace}


def vacuity_cases():
    """premises: model | INCONSISTENT. The witness is checked by Lean (a
    certificate for Background ++ premises ⊢ ⊥, or a model of the premises);
    Python computes the status; Rust's bounded search must agree."""
    cases = []

    def case(id_, environment, premises, status, model=None):
        witness = ({"model": model} if status == "model" else
                   {"certificate": certificate(environment, premises, ["bottom"])})
        cases.append({"id": id_, "kind": "vacuity", "environment": deepcopy(environment),
                      "premises": premises, **witness,
                      "expected": {"status": "ok", "premises": status}})

    rich = envelope(VOCAB)
    case("background-makes-inconsistent", rich, [SAME], "INCONSISTENT")
    case("plain-contradiction", rich, [SENIOR_A, ["not", SENIOR_A]], "INCONSISTENT")
    case("consistent-with-background", rich, [FIN_A, DISTINCT], "model", MODEL)
    case("empty-premises", rich, [], "model", MODEL)
    order = envelope(ORDER_VOCAB, ["order@0", "relational-fol@0"])
    case("order-background-inconsistent", order, [SAME], "INCONSISTENT")
    case("order-arithmetic-inconsistent", order,
         [LIMIT_SMALL, ["lt", ["num", "3"], ["const", "limit"]]], "INCONSISTENT")
    case("order-consistent", order, [LIMIT_SMALL], "model", ORDER_MODEL)
    return cases


FAMILIES = {
    "elaborated-document": elaborated_document_cases,
    "invalid-background-model": invalid_background_model_cases,
    "dependency-order": dependency_order_cases,
    "labels": label_cases,
    "admission": admission_cases,
    "vacuity": vacuity_cases,
}


def _python_search_model(case):
    from ve.ast import formula_from_data
    from ve.search import find_countermodel
    env = _python_env(case["environment"])
    found = find_countermodel(env, [formula_from_data(env, p) for p in case["premises"]],
                              formula_from_data(env, case["conclusion"]),
                              max_domain_size=case["max_domain_size"])
    assert found.status == "Found", case["id"]
    return found.model.to_dict()


def lean_case(case):
    """The case as the Lean `route` subcommand runs it, with the Lean-shaped
    expectation. Lean does not search: a Python search result is checked as a
    countermodel; a vacuity witness is checked as a model of the premises
    (countermodel to ⊥) or a certificate for Background ++ premises ⊢ ⊥."""
    out = {k: v for k, v in case.items() if k != "expected"}
    expected = case["expected"]
    kind = case["kind"]
    if kind == "search":
        out.update(kind="countermodel", model=_python_search_model(case))
        del out["max_domain_size"]
        lean = {"status": "ok", "refutes": True}
    elif kind == "vacuity":
        witness = "model" in case
        out.update(kind="countermodel" if witness else "certificate", conclusion=["bottom"])
        lean = {"status": "ok", "refutes": True} if witness else {"status": "ok", "valid": True}
    elif expected["status"] == "error":
        lean = {"status": "error", **{k: expected[k] for k in ("error", "generator") if k in expected}}
    elif kind == "certificate" and not expected["valid"]:
        lean = {"valid": False}  # a stale binding is rejected before replay
    elif kind == "admission":
        lean = {k: expected[k] for k in ("status", "admitted", "report", "report_id", "kinds")}
    else:
        lean = expected
    out["expected"] = lean
    return out


def main():
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    for name, build in FAMILIES.items():
        cases = build()
        (root / f"conformance/{name}.json").write_text(json.dumps(cases, indent=2, ensure_ascii=False) + "\n")
        print(f"Wrote {len(cases)} {name} cases")


if __name__ == "__main__":
    main()
