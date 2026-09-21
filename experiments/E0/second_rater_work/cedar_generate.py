"""Generate the blinded E0 Cedar second-rating record.

This file intentionally reads only the frozen drawn sample, never first-rater output.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "/private/tmp/ve-e0-integration")
from ve import Environment, check  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "survey_samples/_drawn/cedar.json"
OUT = Path(__file__).with_name("cedar.jsonl")

# Exact source spellings for compiled typed literals. This prevents a friendly
# identifier from silently standing in for a different Cedar value.
CEDAR_LITERALS = {
    "view_document": 'Taxpreparer::Action::"viewDocument"',
    "view_document_capital": 'Action::"ViewDocument"',
    "modify_document": 'Action::"ModifyDocument"', "push": 'Action::"push"',
    "public_principal": 'Public::"public"', "edit_level": 'the string literal "edit"',
    "assign_issue": 'Action::"assign_issue"', "alice_admin": 'User::"Alice_admin"',
    "read_action": 'Action::"Read"',
    "confidential_doc1": 'Document::"confidential_doc1"', "edit_issue": 'Action::"edit_issue"',
    "bob_admin": 'User::"Bob_admin"', "protected_doc1": 'Document::"protected_doc1"',
    "modify_group": 'Action::"ModifyGroup"', "delete_group": 'Action::"DeleteGroup"',
    "delete_action": 'Action::"Delete"', "public_group": 'DocumentGroup::"Public"',
    "watch_action": 'Action::"watch"', "ip_222_222_222_222": 'ip("222.222.222.222")',
    "false_value": 'the Boolean literal false', "true_value": 'the Boolean literal true',
    "view_action": 'Action::"view"', "vacation_photo_94": 'Photo::"VacationPhoto94.jpg"',
}


def atom(left, relation, right=None):
    return f"{left} is {relation}" if right is None else f"{left} {relation} {right}"


def conj(*parts):
    parts = [p for p in parts if p]
    out = parts[0]
    for part in parts[1:]:
        out = f"({out}) and ({part})"
    return out


def disj(*parts):
    parts = [p for p in parts if p]
    out = parts[0]
    for part in parts[1:]:
        out = f"({out}) or ({part})"
    return out


def exists(sort, var, body):
    return f"there exists {sort} {var}, ({body})"


def forall(sort, var, body):
    return f"for every {sort} {var}, ({body})"


def eq(a, b):
    return f"{a} equals {b}"


def neg(a):
    return f"not ({a})"


def implies(a, b):
    return f"if ({a}), then ({b})"


def desc_args(name, args):
    descriptions = {
        "exact_assignment_shape": "Mechanical adapter fact: the raw Cedar record has exactly the keys organization, serviceline, and location, with no additional keys.",
    }
    return {"arguments": args, "description": descriptions.get(name, "Relational input used by this policy translation.")}


def witness(condition, *, effect="permit", predicates=None, constants=None, extra_sorts=None):
    """Make a full request/effect equivalence plus singleton request projections."""
    predicates = dict(predicates or {})
    constants = dict(constants or {})
    sorts = {s: {"description": f"A {s} value in the Cedar request or entity data."}
             for s in ["request", "principal", "action", "resource"]}
    for s in extra_sorts or []:
        sorts[s] = {"description": f"A {s} value occurring in the Cedar entity data."}
    base = {
        "request_principal": ["request", "principal"],
        "request_action": ["request", "action"],
        "request_resource": ["request", "resource"],
        f"contributes_{effect}": ["request"],
    }
    base.update(predicates)
    env = {
        "language": "ve.core@0", "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20",
        "vocabulary": {
            "sorts": sorts,
            "predicates": {k: desc_args(k, v) for k, v in base.items()},
            "constants": {k: {"sort": v, "description": f"The fixed Cedar source literal {CEDAR_LITERALS.get(k, k)}."}
                          for k, v in constants.items()},
        },
    }
    rp = atom("q", "request_principal", "p")
    ra = atom("q", "request_action", "a")
    rr = atom("q", "request_resource", "r")
    match = exists("principal", "p", exists("action", "a", exists("resource", "r", conj(rp, ra, rr, condition))))
    eff = atom("q", f"contributes_{effect}")
    statements = [forall("request", "q", implies(eff, match)), forall("request", "q", implies(match, eff))]
    # Cedar requests have exactly one value in each projection. State both totality and functionality.
    for sort, rel, var in [("principal", "request_principal", "p"), ("action", "request_action", "a"), ("resource", "request_resource", "r")]:
        statements.append(forall("request", "q", exists(sort, var, atom("q", rel, var))))
        unique = forall(sort, "u", forall(sort, "v", implies(conj(atom("q", rel, "u"), atom("q", rel, "v")), eq("u", "v"))))
        statements.append(forall("request", "q", unique))
    # These encode Cedar scalar record/entity fields. They may be absent (an absent
    # field or failed lookup cannot make the condition match), but cannot have two
    # values. Set-valued attributes such as writer/reader remain unrestricted.
    scalar_fields = {"assignment_org", "resource_org", "assignment_service",
                     "resource_service", "assignment_location", "resource_location",
                     "owned_by", "access_level", "in_repo", "reported_by",
                     "private_value", "authenticated_value", "rent_or_buy_value", "source_ip"}
    for rel in sorted(scalar_fields & predicates.keys()):
        left_sort, right_sort = predicates[rel]
        functional = forall(right_sort, "u", forall(right_sort, "v",
            implies(conj(atom("z", rel, "u"), atom("z", rel, "v")), eq("u", "v"))))
        statements.append(forall(left_sort, "z", functional))
    # Cedar entity/string literals are distinct within a type.
    by_sort = {}
    for name, sort in constants.items():
        by_sort.setdefault(sort, []).append(name)
    for names in by_sort.values():
        for i, left in enumerate(names):
            for right in names[i + 1:]:
                statements.append(neg(eq("@" + left, "@" + right)))
    if constants.get("false_value") == "boolean_value" and constants.get("true_value") == "boolean_value":
        statements.append(forall("boolean_value", "b", disj(eq("b", "@false_value"), eq("b", "@true_value"))))
    source = "".join(s + ".\n" for s in statements)
    parsed = check(Environment(env), source)
    return source, env, parsed


def action_is(name):
    return eq("a", "@" + name)


def resource_is(name):
    return eq("r", "@" + name)


def principal_is(name):
    return eq("p", "@" + name)


R = {}


def reified(i, condition, rationale, *, effect="permit", predicates=None, constants=None, sorts=None, constructs=None):
    source, env, parsed = witness(condition, effect=effect, predicates=predicates, constants=constants, extra_sorts=sorts)
    R[i] = {"label": "REIFIED", "construct_needed": constructs or ["request/effect reification"],
            "rationale": rationale, "formalization": source, "environment": env,
            "parse_result": parsed,
            "reification": "A request is reified with total singleton principal, action, and resource projections. The unary effect means only that this one policy contributes its permit/forbid effect; Cedar's combining algorithm and final authorization decision are outside the claim."}


def opaque(i, needed, rationale):
    R[i] = {"label": "OPAQUE", "construct_needed": needed, "rationale": rationale,
            "formalization": None, "environment": None,
            "parse_result": {"status": "not_checked", "reason": "No faithful v0 witness for an OPAQUE item."},
            "reification": None}


# 0: record-valued set membership, expanded into its three field equalities.
c0 = exists("assignment", "m", conj(atom("p", "has_assignment", "m"), atom("m", "exact_assignment_shape"), atom("m", "assignment_org", "o"), atom("r", "resource_org", "o"), atom("m", "assignment_service", "s"), atom("r", "resource_service", "s"), atom("m", "assignment_location", "l"), atom("r", "resource_location", "l")))
# Bind join values explicitly.
c0 = conj(action_is("view_document"), exists("organization","o",exists("service","s",exists("location","l",c0))))
reified(0, c0, "The record membership is mechanically expanded into existence of an assigned record whose raw record has exactly the organization, serviceline, and location keys and whose three values equal the resource fields. The exact_assignment_shape fact is supplied by a mechanical raw-key-set adapter, preventing a record with extra fields from spuriously matching Cedar record equality.", predicates={"has_assignment":["principal","assignment"], "exact_assignment_shape":["assignment"], "assignment_org":["assignment","organization"], "resource_org":["resource","organization"], "assignment_service":["assignment","service"], "resource_service":["resource","service"], "assignment_location":["assignment","location"], "resource_location":["resource","location"]}, constants={"view_document":"action"}, sorts=["assignment","organization","service","location"], constructs=["request/effect reification","exact record-shape input adapter","record expansion","relational join"])
reified(1, conj(action_is("modify_document"), atom("r","owned_by","p")), "Exact action equality and resource ownership are binary/equality constraints after reifying the request and policy effect.", predicates={"owned_by":["resource","principal"]}, constants={"modify_document":"action"})
opaque(2, ["entity-hierarchy transitive closure"], "The owner equality is relational, but `action in PrezEditActions` invokes Cedar entity-hierarchy reachability. A binary `in_group` predicate would hide that closure, so the useful skeleton still depends on an unavailable interpreted check.")
reified(3, conj(action_is("push"), atom("r","writer","p")), "The writers attribute is a set-valued resource field, represented directly as a resource-to-principal relation.", predicates={"writer":["resource","principal"]}, constants={"push":"action"})
reified(4, conj(principal_is("public_principal"), action_is("view_document_capital"), atom("r","access_level","@edit_level"), exists("boolean_value","b",conj(atom("r","private_value","b"),eq("b","@false_value")))), "The fixed public principal, exact action, string-valued access field, and unless guard are preserved. The explicit false Boolean value makes a missing isPrivate field fail rather than count as false.", predicates={"access_level":["resource","access_value"],"private_value":["resource","boolean_value"]}, constants={"public_principal":"principal","view_document_capital":"action","edit_level":"access_value","false_value":"boolean_value","true_value":"boolean_value"}, sorts=["access_value","boolean_value"], constructs=["request/effect reification","string literal as value constant","explicit Boolean value"])
opaque(5, ["entity-hierarchy transitive closure"], "The viewerMarkets collection is relational, but the action-group `in` guard requires Cedar hierarchy reachability, which v0 cannot define without hiding it in a predicate.")
opaque(6, ["template parameter binding","entity-hierarchy transitive closure"], "The resource template slot can be reified as a parameter, but `principal in ?principal` has Cedar hierarchy semantics over a runtime-bound entity. v0 has neither policy parameters nor transitive closure; an `in` predicate would conceal the essential check.")
opaque(7, ["entity-hierarchy transitive closure"], "Both principal and resource scopes use Cedar `in`, whose membership includes transitive entity ancestry. General reachability is not function-free FOL definable by a finite witness.")
reified(8, exists("boolean_value","b",conj(atom("q","authenticated_value","b"),eq("b","@false_value"))), "The forbid policy matches an explicitly present false authenticated field. A missing field has no value tuple and therefore cannot spuriously match. The result is this policy's forbid contribution, not a final engine decision.", effect="forbid", predicates={"authenticated_value":["request","boolean_value"]}, constants={"false_value":"boolean_value","true_value":"boolean_value"}, sorts=["boolean_value"], constructs=["request/effect reification","explicit Boolean value"])
opaque(9, ["entity-hierarchy transitive closure"], "The action list, attribute-presence guard, and contributors collection are relational, but `resource in GitApp` requires entity-hierarchy closure. Treating that as an input predicate would hide a necessary Cedar computation.")
opaque(10, ["entity-hierarchy transitive closure"], "The policy has a useful relational contributors skeleton, but its resource hierarchy scope is essential and cannot be implemented in v0.")
reified(11, conj(action_is("assign_issue"), exists("repository","repo",conj(atom("r","in_repo","repo"),atom("repo","triager","p")))), "The nested resource.repo.triagers lookup is expanded into an existential repository join and set membership.", predicates={"in_repo":["resource","repository"],"triager":["repository","principal"]}, constants={"assign_issue":"action"}, sorts=["repository"], constructs=["request/effect reification","relational join"])
opaque(12, ["template parameter binding","entity-hierarchy transitive closure"], "Both template slots are used as hierarchy ancestors. Their transitive `in` meaning cannot be represented faithfully as an unconstrained relation.")
reified(13, conj(principal_is("alice_admin"),action_is("read_action"),resource_is("confidential_doc1")), "All three scope components are exact entity equalities and become typed constants in the request match.", constants={"alice_admin":"principal","read_action":"action","confidential_doc1":"resource"})
reified(14, conj(action_is("edit_issue"),exists("repository","repo",conj(atom("r","in_repo","repo"),atom("repo","reader","p"))),atom("r","reported_by","p")), "The repo readers membership and reporter equality are explicit joins over resource, repository, and principal.", predicates={"in_repo":["resource","repository"],"reader":["repository","principal"],"reported_by":["resource","principal"]}, constants={"edit_issue":"action"}, sorts=["repository"], constructs=["request/effect reification","relational join"])
opaque(15, ["entity-hierarchy transitive closure"], "Owner-writers membership is relational, but the action hierarchy scope `action in write` is an essential transitive ancestry test unavailable in v0.")
opaque(16, ["entity-hierarchy transitive closure"], "The principal equality is expressible, but resource membership below the album entity uses Cedar's transitive hierarchy closure.")
reified(17, conj(principal_is("bob_admin"),action_is("read_action"),resource_is("protected_doc1")), "The forbid rule is an exact typed tuple match; the witness records only this rule's forbid effect.", effect="forbid", constants={"bob_admin":"principal","read_action":"action","protected_doc1":"resource"})
opaque(18, ["entity-hierarchy transitive closure"], "Cedar `in` is hierarchy-aware even when its right operand is a set. Thus the action can descend from a listed action and the resource can descend from an entity in either permission attribute. Replacing these with ordinary set membership would omit essential closure semantics.")
reified(19, atom("r","owned_by","p"), "The `has owner` guard plus equality is equivalent in a well-typed relational encoding to existence of the owned_by tuple for the request principal; absence makes the condition false.", predicates={"owned_by":["resource","principal"]})
opaque(20, ["entity-hierarchy transitive closure"], "Principal membership in jane_friends is a Cedar entity-ancestry query. The exact action and resource do not remove that essential unavailable check.")
opaque(21, ["entity-hierarchy transitive closure"], "Although ownership is relational, Cedar `action in [ModifyGroup, DeleteGroup]` is hierarchy-aware: a descendant of either listed action also matches. A finite equality disjunction would be too narrow, while an ancestry predicate would hide transitive closure.")
reified(22, conj(principal_is("alice_admin"),action_is("delete_action"),resource_is("public_group"),atom("q","authenticated"),atom("q","delete_confirmed")), "Boolean context equality to true is represented by unary request facts, together with exact request scope equalities.", predicates={"authenticated":["request"],"delete_confirmed":["request"]}, constants={"alice_admin":"principal","delete_action":"action","public_group":"resource"})
opaque(23, ["entity-hierarchy transitive closure"], "Maintainers membership is relational, but `action in maintain` uses the Cedar action hierarchy and cannot be replaced with plain equality or an opaque ancestry predicate.")
reified(24, conj(action_is("view_action"),resource_is("vacation_photo_94"),exists("ip_value","i",conj(atom("q","source_ip","i"),eq("i","@ip_222_222_222_222")))), "The IP constructor is applied once to a fixed source literal at translation time, yielding a typed IP constant; the runtime policy operation is then exact equality of two already-typed IP values. The witness exposes the context-to-IP relation and exact constructor spelling rather than hiding a `source_ip_matches` check.", predicates={"source_ip":["request","ip_value"]}, constants={"view_action":"action","vacation_photo_94":"resource","ip_222_222_222_222":"ip_value"}, sorts=["ip_value"], constructs=["request/effect reification","compile-time typed IP literal"])
opaque(25, ["entity-hierarchy transitive closure"], "All three scopes use Cedar hierarchy membership. General transitive ancestry cannot be expressed by this fragment without an unimplemented closure predicate.")
opaque(26, ["entity-hierarchy transitive closure"], "The action equality is direct, but resource membership under the album depends on Cedar hierarchy closure.")
opaque(27, ["entity-hierarchy transitive closure"], "The action enumeration and reporters collection are relational, but the resource scope requires hierarchy reachability and is essential to matching.")
opaque(28, ["entity-hierarchy transitive closure"], "The schema makes documentsAndFoldersWithViewAccess an entity-valued View ancestor, and Cedar `resource in` tests whether the resource equals or descends from it. A principal-to-resource relation would hide the required closure.")
reified(29, conj(atom("p","subscriber"),action_is("watch_action"),atom("r","movie"),exists("boolean_value","b",conj(atom("r","rent_or_buy_value","b"),eq("b","@false_value")))), "Cedar type tests become unary predicates on typed request entities. The unless guard requires an explicitly present false Boolean field, so a missing field does not spuriously permit. This rule contributes permit only.", predicates={"subscriber":["principal"],"movie":["resource"],"rent_or_buy_value":["resource","boolean_value"]}, constants={"watch_action":"action","false_value":"boolean_value","true_value":"boolean_value"}, sorts=["boolean_value"], constructs=["request/effect reification","entity type tests","explicit Boolean value"])


def main():
    drawn = json.loads(SAMPLE.read_text())
    assert len(drawn["sample"]) == 30 and set(R) == set(range(30))
    records = []
    for i, item in enumerate(drawn["sample"]):
        rec = {"dataset":"cedar", "id":item["id"], **R[i],
               "source_evidence": [
                   "https://docs.cedarpolicy.com/policies/syntax-operators.html",
                   "https://docs.cedarpolicy.com/policies/syntax-datatypes.html",
               ]}
        records.append(rec)
    OUT.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records))
    counts = {k: sum(r["label"] == k for r in records) for k in ["DIRECT","REIFIED","OPAQUE","NO"]}
    print(json.dumps({"records":len(records),"counts":counts,"checked":sum(r["parse_result"].get("language") == "accepted" for r in records)}))


if __name__ == "__main__":
    main()
