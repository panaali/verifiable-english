"""rights-licence-relay: Lean returns each narrowing mechanism's licence with the grounds it rests on, and the
relay binds them to the request instead of deriving them (ends rd-9's D1 exception, `_narrowings`).

The elaboration names what the relay binds: per line, the limitations in scope and the bar's reach; per
mechanism, its licence and grounds (the citation, the colliding right line or the strict rule); per rule, the
mechanisms that name it and what each of its citations licenses (Run.lean `elaboratedNarrowingsJson`,
`ruleNarrowingsJson`; Scope.lean `ground`, `citedBy_sound`, `ground_isSome`, `licence_spec`). A corrupted
mechanism, licence, target, scope flag, bar reach, grounds or rule row is still `CheckerUnavailable`, in the
elaboration alone and when the elaboration and the scope answer are forged together.
"""
from __future__ import annotations

import ast
import copy
from pathlib import Path

import pytest

from ve.errors import CheckerUnavailable

ROOT = Path(__file__).resolve().parents[1]


def _source(name):
    from tests.test_relay_binding_inventory import _rights_sources
    from ve.rights import RightsEnvironment
    raw, units = _rights_sources()[name]
    return RightsEnvironment(raw), units


def test_probe_the_relay_holds_no_copy_of_the_licence_derivation():
    """No function, helper or citation key of Lean's derivation is left in the relay: `_narrowings` and `_in_scope`
    are gone, the soft relations they filtered by are not imported, and no `cited` key or limitation scope is read."""
    tree = ast.parse((ROOT / "ve/rights_route.py").read_text())
    functions = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    assert not functions & {"_narrowings", "_in_scope"}
    imported = {alias.name for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) for alias in node.names}
    assert not imported & {"_incompatible", "_rank_above"}
    strings = [node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and type(node.value) is str]
    assert not [s for s in strings if s.startswith(("unless:", "over:", "narrows:", "alterable:"))]
    keys = {node.slice.value for node in ast.walk(tree)
            if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant)}
    assert not keys & {"scope", "kinds", "rank"}


def _forge(monkeypatch, mutation, kinds):
    from tests.test_soft_decision_keys import _rights_relay
    _rights_relay(monkeypatch, mutation, kinds)


def _mechanism(row, text):
    return next(m for entry in row["narrowings"] for m in entry["mechanisms"] if m["mechanism"] == text)


def _rename(old, new):
    def mutation(row):
        mechanism = _mechanism(row, old)
        rule = mechanism["target"].split(":", 1)[0]
        mechanism.update(mechanism=new, target=f"{rule}:{new}")
        for entry in row.get("rule_narrowings", []):
            entry["narrows"] = [f"{rule}:{new}" if t == f"{rule}:{old}" else t for t in entry["narrows"]]
    return mutation


def _drop(text):
    def mutation(row):
        for entry in row["narrowings"]:
            entry["mechanisms"] = [m for m in entry["mechanisms"] if m["mechanism"] != text]
    return mutation


def _relicense(text, licence):
    def mutation(row):
        _mechanism(row, text)["licence"] = licence
    return mutation


def _set(text, field, value):
    def mutation(row):
        _mechanism(row, text)[field] = value
    return mutation


def _flip_scope(row):
    for entry in row["narrowings"]:
        entry["in_scope"] = not entry["in_scope"]


def _elaboration(edit):
    def mutation(row):
        if "rule_narrowings" in row:
            edit(row)
    return mutation


CORRUPTIONS = [
    # The mechanism: renamed to another slot of a declared rule (target kept consistent), or dropped.
    ("same effect strict", _rename("blockedBy rule-4", "dominatedBy rule-4"), "mechanism renamed to a dominance"),
    ("same effect strict", _rename("blockedBy rule-4", "blockedBy may-publish"), "mechanism blocked by itself"),
    ("same effect strict", _drop("blockedBy rule-4"), "a rule-named mechanism dropped"),
    ("weighed and protected", _drop("switch person"), "a switch dropped"),
    ("default gamma", _drop("exception"), "the default exception dropped"),
    # The licence: each flip with every other field kept.
    ("same effect strict", _relicense("blockedBy rule-4", None), "effect licence dropped"),
    ("same effect strict", _relicense("blockedBy rule-4", "collision"), "effect relicensed as a collision"),
    ("strict liberty blocks", _relicense("blockedBy may-publish", None), "collision licence dropped"),
    ("cited opposite effect", _relicense("blockedBy rule-5", None), "citation licence dropped"),
    ("opposite effect", _relicense("blockedBy rule-5", "cited"), "an uncited mechanism licensed as cited"),
    ("opposite effect", _relicense("blockedBy rule-5", "effect delivered by strict rule rule-5"),
     "an opposite-effect rule as a same-effect licence"),
    # The target.
    ("same effect strict", _set("blockedBy rule-4", "target", "rule-4:blockedBy rule-4"), "target of another rule"),
    # The scope flag and the bar's reach.
    ("gamma", _flip_scope, "scope flag flipped"),
    ("bar", _elaboration(lambda row: row["narrowings"][0].update(bar=None)), "bar reach dropped"),
    ("gamma", _elaboration(lambda row: row["narrowings"][0].update(limitations=[])), "limitations in scope dropped"),
    # The grounds.
    ("cited opposite effect", _elaboration(_set("blockedBy rule-5", "grounds",
                                                {"citation": {"rule": "rule-5", "key": "exception"}})),
     "grounds name a citation the request lacks"),
    ("cited switch", _elaboration(_set("switch person", "grounds",
                                       {"citation": {"rule": "no-arbitrary-arrest", "key": "exception"}})),
     "grounds name another mechanism's citation key"),
    ("strict liberty blocks", _elaboration(_set("blockedBy may-publish", "grounds", {"line": "no-attack"})),
     "collision grounds name another line"),
    ("same effect strict", _elaboration(_set("blockedBy rule-4", "grounds", None)), "effect grounds dropped"),
    # The per-rule rows.
    ("same effect strict", _elaboration(lambda row: row["rule_narrowings"][1].update(narrows=[])),
     "a rule's mechanisms dropped from its row"),
    ("cited opposite effect", _elaboration(lambda row: row["rule_narrowings"][1]["citations"][0].update(licenses=[])),
     "a citation's licenses dropped"),
    ("cited opposite effect", _elaboration(lambda row: row["rule_narrowings"][1].update(citations=[])),
     "a citation row dropped"),
    ("same effect strict", _elaboration(lambda row: row["rule_narrowings"].pop()), "a rule row dropped"),
]


@pytest.mark.parametrize("kinds", [("rights-elaborate",), ("rights-elaborate", "rights-scope")],
                         ids=["elaboration", "elaboration and scope"])
@pytest.mark.parametrize("source,mutation", [pytest.param(s, m, id=i) for s, m, i in CORRUPTIONS])
def test_a_corrupted_lean_answer_is_still_refused(monkeypatch, source, mutation, kinds):
    from ve import rights_route
    environment, units = _source(source)
    rights_route.report_rights(environment, units)  # the genuine answers pass
    _forge(monkeypatch, mutation, kinds)
    with pytest.raises(CheckerUnavailable):
        rights_route.report_rights(environment, units)


@pytest.mark.parametrize("source,mutation", [pytest.param(s, m, id=i) for s, m, i in CORRUPTIONS])
def test_the_elaboration_binder_alone_refuses_it(monkeypatch, source, mutation):
    """The elaboration's own binder (the call `RightsDocument` makes) refuses each corruption without the scope
    answer to compare with."""
    from ve import rights_route
    environment, units = _source(source)
    _forge(monkeypatch, mutation, ("rights-elaborate",))
    with pytest.raises(CheckerUnavailable):
        rights_route.run_rights_case(environment, units, "rights-elaborate")


def test_the_genuine_grounds_name_request_items():
    """Acceptance against Lean: in every genuine elaboration, a licence is null exactly when its grounds are, a
    cited licence's citation is a key the request's rule cites, and a collision or effect names the mechanism's
    own rule; the scope answer's licences are the elaboration's."""
    from tests.test_relay_binding_inventory import _rights_sources
    from ve import rights_route
    from ve.rights import RightsEnvironment
    kinds = set()
    for raw, units in _rights_sources().values():
        environment = RightsEnvironment(raw)
        elaborated = rights_route.run_rights_case(environment, units, "rights-elaborate")
        report = rights_route.report_rights(environment, units)
        for entry, shown in zip(elaborated["narrowings"], report["narrowings"]):
            assert [m["licence"] for m in entry["mechanisms"]] == [m["licence"] for m in shown["mechanisms"]]
            for mechanism in entry["mechanisms"]:
                grounds, licence = mechanism["grounds"], mechanism["licence"]
                kinds.add(next(iter(grounds)) if grounds else licence)
                if licence in (None, "limitation", "bar"):
                    assert grounds is None
                elif licence == "cited":
                    rule, key = grounds["citation"]["rule"], grounds["citation"]["key"]
                    assert any(key in ((unit.get("cites") or {}) if unit.get("norm", {}).get("name") == rule else {})
                               for unit in units) or any(
                        key in (line.get("cites") or {}) for unit in units
                        for body in [unit.get("right") or unit.get("right_lines") or {}]
                        for line in body.get("lines", []))
                else:
                    assert next(iter(grounds.values())) == mechanism["mechanism"].split(" ", 1)[1]
    assert kinds == {None, "limitation", "bar", "citation", "line", "rule"}
