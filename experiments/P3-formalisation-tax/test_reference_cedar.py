"""Validate reference_cedar.py against the upstream-recorded Cedar decisions, plus
unit tests of tricky semantics. Run: python3 test_reference_cedar.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from reference_cedar import (CedarError, Duration, authorize, explain, parse_datetime,  # noqa: E402
                             parse_duration)

# Schema-typed bare-string extension attributes (Cedar's schema-based "implicit
# constructor"). Upstream streaming_service/policies.cedarschema declares
# `entity Show = { releaseDate: datetime, ... }` while entities.json stores the
# plain string "2025-02-21"; the normalised item keeps the bare string.
SCHEMA_EXTN = {"c19_streaming": {"Show": {"releaseDate": "datetime"}}}


def check_recorded() -> None:
    total = matched = 0
    mismatches = []
    for item_json in sorted((HERE / "items").glob("c*/item.json")):
        item = json.loads(item_json.read_text())
        policy = (item_json.parent / "source.cedar").read_text()
        world = item["world"]
        for q in item["questions"]:
            total += 1
            got = authorize(policy, world["linked"], world["entities"], q["request"],
                            SCHEMA_EXTN.get(item["id"]))
            want = q["recorded_decision"] == "allow"
            if got == want:
                matched += 1
            else:
                mismatches.append((item["id"], q["description"],
                                   explain(policy, world["linked"], world["entities"],
                                           q["request"], SCHEMA_EXTN.get(item["id"]))))
    for m in mismatches:
        print("MISMATCH", m)
    print(f"recorded decisions matched: {matched}/{total}")
    assert matched == total and total > 0


# ------------------------------------------------------------------ unit tests

ENTS = [
    {"uid": 'User::"alice"', "attrs": {"age": 30, "tags": ["a", "b"]}, "parents": ['Group::"g1"']},
    {"uid": 'Group::"g1"', "attrs": {}, "parents": ['Group::"g2"']},
    {"uid": 'Group::"g2"', "attrs": {}, "parents": ['Group::"g3"']},
    {"uid": 'Group::"g3"', "attrs": {}, "parents": []},
    {"uid": 'Doc::"d"', "attrs": {"owner": {"__entity": 'User::"alice"'}}, "parents": []},
]


def req(p='User::"alice"', a='Action::"view"', r='Doc::"d"', ctx=None):
    return {"principal": p, "action": a, "resource": r, "context": ctx or {}}


def allow(text, request=None, linked=(), ents=ENTS):
    return authorize(text, list(linked), ents, request or req())


def unit_tests() -> None:
    ok = "permit(principal, action, resource);"
    # error-skipping of permit: erroring permit is not satisfied
    assert not allow("permit(principal, action, resource) when { principal.missing == 1 };")
    assert allow(ok + "permit(principal, action, resource) when { principal.missing };")
    # error-skipping of forbid: erroring forbid does not deny
    assert allow(ok + "forbid(principal, action, resource) when { resource.nope };")
    assert allow(ok + "forbid(principal, action, resource) when { 1 < \"x\" };")
    # a forbid that is satisfied denies
    assert not allow(ok + "forbid(principal, action, resource) when { principal.age >= 18 };")
    # unless with an erroring attribute -> the policy is skipped (not satisfied)
    assert not allow("permit(principal, action, resource) unless { resource.isPrivate };")
    assert allow(ok + "forbid(principal, action, resource) unless { resource.isPrivate };")
    assert allow("permit(principal, action, resource) unless { resource has isPrivate };")
    # when/unless conjunction short-circuits in textual order (visible only in diagnostics)
    sc = ok + "forbid(principal, action, resource) when { false } when { principal.x };"
    assert allow(sc) and explain(sc, [], ENTS, req())["errors"] == {}
    # && / || require booleans; short-circuit avoids the error
    assert allow("permit(principal, action, resource) when { true || principal.x };")
    assert not allow("permit(principal, action, resource) when { 1 || true };")
    assert not allow("permit(principal, action, resource) when { false || 1 };")
    # reflexive in; in through 1, 2 and 3 parent hops; not upward
    assert allow('permit(principal in User::"alice", action, resource);')
    assert allow('permit(principal in Group::"g1", action, resource);')
    assert allow('permit(principal in Group::"g2", action, resource);')
    assert allow('permit(principal in Group::"g3", action, resource);')
    assert not allow('permit(principal, action, resource) when { Group::"g3" in principal };')
    assert allow('permit(principal, action, resource) when { principal in [Group::"x", Group::"g3"] };')
    # entity not in the store: equality/in work, attributes error, has is false
    ghost = req(p='User::"ghost"')
    assert allow('permit(principal == User::"ghost", action, resource);', ghost)
    assert allow('permit(principal in User::"ghost", action, resource);', ghost)
    assert not allow('permit(principal in Group::"g1", action, resource);', ghost)
    assert not allow("permit(principal, action, resource) when { principal.age > 0 };", ghost)
    assert allow("permit(principal, action, resource) when { !(principal has age) };", ghost)
    # template linking: only linked instances are evaluated; unlinked template is inert
    tmpl = '@id("t") permit(principal == ?principal, action, resource in ?resource);'
    link = [{"template_id": "t", "link_id": "L1",
             "args": {"?principal": 'User::"bob"', "?resource": 'Doc::"d"'}}]
    assert not allow(tmpl)
    assert not allow(tmpl, linked=link)
    assert allow(tmpl, req(p='User::"bob"'), linked=link)
    assert not allow(tmpl, req(p='User::"bob"', r='Doc::"other"'), linked=link)
    assert explain(tmpl, link, ENTS, req(p='User::"bob"'))["permit"] == ["L1"]
    # equality is structural and false (not error) across types
    assert allow('permit(principal, action, resource) when { [1, 2, 2] == [2, 1] };')
    assert allow('permit(principal, action, resource) when { {a: 1, b: [true]} == {b: [true], a: 1} };')
    assert allow('permit(principal, action, resource) when { 1 != "1" && principal != "alice" };')
    assert allow('permit(principal, action, resource) when { resource.owner == principal };')
    # set methods, records, like, is, if, arithmetic
    assert allow('permit(principal, action, resource) when { principal.tags.containsAll(["a"]) '
                 '&& principal.tags.containsAny(["z", "b"]) && !principal.tags.contains("c") };')
    assert allow('permit(principal, action, resource) when { {"k y": 1}["k y"] == 1 && {a: {b: 2}}.a.b == 2 };')
    assert allow('permit(principal, action, resource) when { "a*b*c" like "a\\*b\\*c" && "abxc" like "a*c" && !("abxc" like "a\\*c") };')
    assert allow('permit(principal is User in Group::"g3", action, resource is Doc);')
    assert not allow('permit(principal is Doc, action, resource);')
    assert allow('permit(principal, action, resource) when { if principal.age > 1 then true else 1 };')
    assert allow('permit(principal, action, resource) when { principal.age * 2 - 1 + -1 == 58 };')
    assert not allow('permit(principal, action, resource) when { 9223372036854775807 + 1 > 0 };')
    # namespaced entity types
    ns = req(p='A::B::User::"x"', a='A::Action::"go"', r='A::Doc::"d"')
    assert allow('permit(principal is A::B::User, action == A::Action::"go", resource);', ns)
    # extensions: datetime / duration
    assert parse_datetime("2025-02-02T19:00:00-0500") == parse_datetime("2025-02-03T00:00:00Z")
    assert parse_duration("-24h") == Duration(-86_400_000)
    assert parse_duration("1d2h3m4s5ms").ms == 93_784_005
    try:
        parse_duration("1h1d")
        raise AssertionError("bad duration accepted")
    except CedarError:
        pass
    ctx = {"t": {"__extn": {"fn": "datetime", "arg": "2025-02-20T22:00:00-0500"}},
           "off": {"fn": "duration", "arg": "-5h"}}
    assert allow('permit(principal, action, resource) when { '
                 'context.t.offset(context.off).toTime() == duration("22h") && '
                 'context.t.toTime() == duration("3h") && '
                 'context.t > datetime("2025-02-20") && '
                 'context.t.toDate() == datetime("2025-02-21") && '
                 'duration("90m").toHours() == 1 };', req(ctx=ctx))
    # P3 correction: `in` over a set with any non-entity member is a type error, whatever the
    # order (cedar-spec Evaluator.lean inₛ uses mapOrErr before testing membership).
    mixed = [{"uid": 'User::"a"', "attrs": {"s": [{"__entity": 'G::"g"'}, "x"]}, "parents": ['G::"g"']}]
    assert not authorize('permit(principal, action, resource) when { principal in principal.s };', [], mixed,
                         {"principal": 'User::"a"', "action": 'A::"x"', "resource": 'R::"r"', "context": {}})
    print("unit tests passed")


if __name__ == "__main__":
    unit_tests()
    check_recorded()
