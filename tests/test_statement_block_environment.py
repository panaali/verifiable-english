"""The statement-layer block routes as environment validators (lf-5 post-merge).

`Environment` asks the alternatives and risk routes about a block environment
before Python materialises it (`validation.validated_statement_block`). The
alternatives route was asked with a document case, so the document route's
limits (no definitions, no data flags) refused environments the English
boundary of english-lean S3 accepts. The class is "a route's document limits
applied to an environment alone"; these tests enumerate it:

* every declaration kind of another profile (definitions, data flags, `$string`
  literals) × well-formed or malformed, on an alternatives environment: the
  well-formed one is accepted and the malformed one is rejected by Lean's owner,
  never refused as unsupported and never dropped;
* the same kinds on a risk environment: refused, as risk.md 6 orders;
* every role predicate × every fixing key (`defined`, `functional`, `total`,
  including a false flag): `AlternativesRegulated`, on both routes;
* the alternatives document cases still refuse what they do not run.
"""
from __future__ import annotations

import copy
import re

import pytest

from ve import Environment
from ve.backends.relay import decide
from ve.errors import CheckerUnavailable, UnsupportedProfile, VEError

from conformance.english_lean_s3_fixtures import FA, FR


def _profile(raw: dict, profile: str) -> None:
    raw["profiles"] = sorted(set(raw["profiles"]) | {profile})


def definition(raw: dict, malformed: bool = False) -> None:
    _profile(raw, "definitions@0")
    raw["vocabulary"]["predicates"]["safe"]["defined"] = {
        "arguments": ["action"], "body": ["var", 0] if malformed else ["top"]}


def flags(raw: dict, malformed: bool = False) -> None:
    _profile(raw, "data@0")
    raw["vocabulary"]["predicates"]["owner_of"] = {
        "arguments": ["action", "agent"], "description": "action owner",
        "functional": "yes" if malformed else True, "total": True}


def false_flag(raw: dict, malformed: bool = False) -> None:
    _profile(raw, "data@0")
    raw["vocabulary"]["predicates"]["owner_of"] = {
        "arguments": ["action", "agent"] if not malformed else ["action"],
        "description": "action owner", "functional": False}


def literal(raw: dict, malformed: bool = False) -> None:
    _profile(raw, "data@0")
    raw["vocabulary"]["constants"]["label"] = {"sort": "$string", "description": 7 if malformed else "label"}


OTHER_DECLARATIONS = {"definition": definition, "data flags": flags, "false flag": false_flag,
                      "string literal": literal}


@pytest.mark.parametrize("kind", OTHER_DECLARATIONS)
def test_alternatives_environment_validates_other_profiles_declarations(kind):
    raw = FA()
    OTHER_DECLARATIONS[kind](raw)
    env = Environment(raw)
    assert env.environment_id == Environment(copy.deepcopy(raw)).environment_id
    bad = FA()
    OTHER_DECLARATIONS[kind](bad, malformed=True)
    with pytest.raises(VEError) as caught:
        Environment(bad)
    assert not isinstance(caught.value, (CheckerUnavailable, UnsupportedProfile)), caught.value


@pytest.mark.parametrize("kind", ["definition", "data flags", "string literal"])
def test_risk_environment_still_refuses_other_profiles_declarations(kind):
    raw = FR()
    OTHER_DECLARATIONS[kind](raw)
    word = {"definition": "definitions", "data flags": "data flags", "string literal": "$string literals"}[kind]
    with pytest.raises(UnsupportedProfile, match=re.escape(f"risk route with {word} is not implemented")):
        Environment(raw)


@pytest.mark.parametrize("kind", ["definition", "data flags"])
def test_alternatives_document_cases_still_refuse_what_they_do_not_run(kind):
    raw = FA()
    OTHER_DECLARATIONS[kind](raw)
    Environment(raw)
    word = {"definition": "definitions", "data flags": "data flags"}[kind]
    with pytest.raises(UnsupportedProfile, match=f"alternatives route with {word} is not implemented"):
        decide("alternatives", [{"id": "d", "kind": "alt-elaborate", "environment": raw, "norms": []}])


def _role_cases():
    for role, name in (("available", "available"), ("leads_to", "leads_to")):
        for key, value in (("defined", None), ("functional", True), ("functional", False), ("total", False)):
            for fixture in ("FA", "FR"):
                if fixture == "FR" and value is not False:
                    continue  # the risk route refuses definitions and true flags before its block
                yield pytest.param(fixture, role, name, key, value, id=f"{fixture}-{role}-{key}-{value}")


@pytest.mark.parametrize("fixture, role, name, key, value", list(_role_cases()))
def test_a_role_predicate_whose_declaration_fixes_it_is_regulated(fixture, role, name, key, value):
    raw = {"FA": FA, "FR": FR}[fixture]()
    entry = raw["vocabulary"]["predicates"][name]
    if key == "defined":
        _profile(raw, "definitions@0")
        entry["defined"] = {"arguments": entry["arguments"], "body": ["top"]}
    else:
        _profile(raw, "data@0")
        entry[key] = value
    with pytest.raises(VEError, match=f"AlternativesRegulated: {role} {name}"):
        Environment(raw)
