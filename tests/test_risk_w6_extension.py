"""The W6 unit extension on the risk route: Python's `Environment` and the Lean route decide alike.

Review risk-looprecheck1 B1: the route's unit decoder skipped W6's sort/tag collision check, and
`argument_units`, constant units and verbalisations, a `$string` literal with units, and `units` or
`unit_schema` alone were decided differently by Python and Lean. The class is every W6 declaration rule
Python applies to a risk environment. Each is checked here, with the route gates that surround them (the
checker family, the W6 profile tuple, and the definitions, data flags and `$string` literals the route
refuses). Each mutation below gets one answer from both, text included. Python's W6 texts are Lean's frozen
ones.
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from tests import lean_routes

from conformance.risk import agent_ops, asimov_risk, asimov_rules
from ve.environment import Environment
from ve.errors import VEError

ROOT = Path(__file__).resolve().parents[1]
BIN = "ve_risk_route"  # its service mode, through tests/lean_routes.py

pytestmark = pytest.mark.skipif(not lean_routes.SERVICE.exists(), reason="the Lean service is not built")

GB = {"scale": "1", "display": {"kind": "decimal", "label": "GB"}}
W6_PROFILE = ("UnsupportedProfile: ve-units@1 requires exactly order@0, relational-fol@0 and time@0, "
              "optionally with documents@1")


def _sort(name):
    return lambda r: r["vocabulary"]["sorts"].update({name: {"description": name}})


def _pred(extra):
    return lambda r: r["vocabulary"]["predicates"]["taken"].update(extra)


def _const(name, **entry):
    return lambda r: r["vocabulary"]["constants"].update({name: {"description": name, **entry}})


def _string_const(r):
    r["vocabulary"]["constants"]["s1"] = {"sort": "$string"}


def _unit(tag, record):
    return lambda r: r["units"].update({tag: record})


def _display(**fields):
    return lambda r: r["units"]["gb"]["display"].update(fields)


def _profiles(*extra):
    return lambda r: r.update(profiles=sorted(r["profiles"] + list(extra)))


def _no_units(r):
    del r["units"], r["unit_schema"], r["risk"]["quantity_kinds"], r["risk"]["required_estimators"]


def _all(*edits):
    def edit(raw):
        for e in edits:
            e(raw)
    return edit


def _defined(r):
    r["vocabulary"]["predicates"]["dd"] = {"arguments": ["action"], "description": "d", "defined": {
        "arguments": ["action"], "body": ["unary", "taken", ["var", 0]]}}


def _flagged(value):
    return lambda r: r["vocabulary"]["predicates"].update(ff={
        "arguments": ["action", "harm"], "description": "f", "functional": value})


# One text from both. The review's reproducers come first.
EXACT = {
    "sort-gb": (_sort("gb"), "Unit tag gb collides with a declared sort"),
    "sort-dimensionless": (_sort("dimensionless"), "Unit tag dimensionless collides with a declared sort"),
    "argument-units-slot": (_pred({"argument_units": {"0": "gb"}}), "Unit on non-integer slot 0"),
    "argument-units-slots-sorted": (_pred({"argument_units": {"9": "gb", "0": "gb"}}), "Unit on non-integer slot 0"),
    "argument-units-name": (_pred({"argument_units": {"x": "gb"}}), "Invalid argument unit slot x"),
    "argument-units-range": (_pred({"argument_units": {"5": "gb"}}), "Invalid argument unit slot 5"),
    "argument-units-type": (_pred({"argument_units": []}), "argument_units must be an object"),
    "constant-unit": (_const("c1", sort="action", unit="gb"), "Unit on non-integer constant c1"),
    "string-with-units": (_string_const, "UnsupportedProfile: $string literals are not admitted with ve-units@1"),
    "schema-alone": (lambda r: r.pop("units"),
                     "UnsupportedProfile: unit_schema and units require the ve.core@0.2 quantity route together"),
    "units-alone": (lambda r: r.pop("unit_schema"),
                    "UnsupportedProfile: unit_schema and units require the ve.core@0.2 quantity route together"),
    "schema-other": (lambda r: r.update(unit_schema="ve-units@2"), "UnsupportedProfile: Unsupported unit schema"),
    "schema-type": (lambda r: r.update(unit_schema=3), "UnsupportedProfile: Unsupported unit schema"),
    "units-type": (lambda r: r.update(units=[]), "units must be an object"),
    "units-many": (lambda r: r["units"].update({f"u{i}": {"scale": "1", "display": {
        "kind": "decimal", "label": f"L{i}x"}} for i in range(70)}), "ResourceLimit: At most 64 unit tags"),
    "tag-invalid": (_unit("Gb", {"scale": "1", "display": {"kind": "percent"}}), 'Invalid unit tag "Gb"'),
    "tag-dimensionless": (_unit("dimensionless", {"scale": "1", "display": {"kind": "percent"}}),
                          'Invalid unit tag "dimensionless"'),
    "tags-sorted": (lambda r: r.update(units={"zz": {"scale": "3", "display": {"kind": "percent"}},
                                              "aa": {"scale": "7", "display": {"kind": "percent"}}}),
                    "UnitScale(aa): expected a positive power of ten"),
    "record-type": (_unit("gb", []), "object expected"),
    "record-fields": (lambda r: r["units"]["gb"].update(x=1),
                      "fields do not match: expected [scale, display], got [display, scale, x]"),
    "scale-power": (lambda r: r["units"]["gb"].update(scale="20"), "UnitScale(gb): expected a positive power of ten"),
    "scale-negative": (lambda r: r["units"]["gb"].update(scale="-10"),
                       "UnitScale(gb): expected a positive power of ten"),
    "scale-type": (lambda r: r["units"]["gb"].update(scale=10), "String expected"),
    "scale-noncanonical": (lambda r: r["units"]["gb"].update(scale="010"), "non-canonical integer"),
    "scale-minus-zero": (lambda r: r["units"]["gb"].update(scale="-0"), "non-canonical integer"),
    "scale-dash": (lambda r: r["units"]["gb"].update(scale="-"), "invalid integer"),
    "scale-long": (lambda r: r["units"]["gb"].update(scale="1" + "0" * 45), "ResourceLimit: numeral length"),
    "display-type": (lambda r: r["units"]["gb"].update(display=[]), "Invalid display for gb"),
    "display-kind-type": (lambda r: r["units"]["gb"].update(display={"kind": 3}), "String expected"),
    "display-kind": (lambda r: r["units"]["gb"].update(display={"kind": "weird"}), "Unknown display kind weird"),
    "display-fields": (_display(x=1),
                       "fields do not match: required [kind, label], optional [placement], got [kind, label, x]"),
    "percent-fields": (_unit("pct", {"scale": "1", "display": {"kind": "percent", "x": 1}}),
                       "fields do not match: expected [kind], got [kind, x]"),
    "label-spaces": (_display(label="G  B"), 'Display string "G  B" must be whitespace-normalized'),
    "label-tab": (_display(label="G\tB"), 'Display string "G\\tB" must be whitespace-normalized'),
    "label-empty": (_display(label=""), "Display string must be nonempty"),
    "label-type": (_display(label=1), "String expected"),
    "placement": (_display(placement="mid"), "Invalid placement for gb"),
    "placement-type": (_display(placement=1), "String expected"),
    "currency": (_unit("eur", {"scale": "1", "display": {"kind": "money", "currency": "eu"}}),
                 "Invalid currency for eur"),
    "currency-type": (_unit("eur", {"scale": "1", "display": {"kind": "money", "currency": 1}}), "String expected"),
    "affix-touches": (_display(label="GB1"), 'DisplayCollision(" GB1" touches the amount)'),
    "affix-extends": (_unit("eur", {"scale": "1", "display": {"kind": "money", "currency": "EUR",
                                                              "input_symbol": "EUR "}}),
                      'DisplayCollision("EUR ", "EUR ")'),
    "iso-date-tag": (_unit("when", {"scale": "1", "display": {"kind": "iso_date"}}),
                     "iso_date requires day at scale 1"),
    "day-scale": (_unit("day", {"scale": "10", "display": {"kind": "iso_date"}}), "iso_date requires day at scale 1"),
    "elapsed-day": (_unit("elapsed_day", {"scale": "1", "display": {"kind": "decimal", "label": "d"}}),
                    "Reserved unit elapsed_day has a fixed declaration"),
    "verbalisation-collision": (_all(_const("c1", sort="action", verbalisation="run"),
                                     _const("c2", sort="action", verbalisation="Run")),
                                "VerbalisationCollision(c1, c2)"),
    "verbalisation-collision-sorted": (_all(_const("c2", sort="action", verbalisation="Run"),
                                            _const("c1", sort="action", verbalisation="run")),
                                       "VerbalisationCollision(c1, c2)"),
    "verbalisation-spaces": (_const("c1", sort="action", verbalisation="a  b"),
                             'Verbalisation "a  b" must be whitespace-normalized'),
    "verbalisation-long": (_const("c1", sort="action", verbalisation="x" * 257),
                           "ResourceLimit: Verbalisation exceeds 256 characters"),
    "profile-data": (_profiles("data@0"), W6_PROFILE),
    "profile-definitions": (_profiles("definitions@0"), W6_PROFILE),
    "profile-order": (_profiles("order@0", "time@0"), "UnsupportedProfile: the risk norms route admits FOL documents only"),
    # Without the extension: the route's display field and its refusals, with Python's texts.
    "plain-verbalisation-empty": (_all(_no_units, _const("c1", sort="action", verbalisation="")),
                                  "Verbalisations must be nonempty strings"),
    "plain-verbalisation-type": (_all(_no_units, _const("c1", sort="action", verbalisation=3)),
                                 "Verbalisations must be nonempty strings"),
    "plain-verbalisation-long": (_all(_no_units, _const("c1", sort="action", verbalisation="x" * 257)),
                                 "ResourceLimit: Verbalisation exceeds 256 characters"),
    "plain-string": (_all(_no_units, _string_const),
                     "UnsupportedProfile: risk route with $string literals is not implemented"),
    "plain-definitions": (_all(_no_units, _profiles("definitions@0"), _defined),
                          "UnsupportedProfile: risk route with definitions is not implemented"),
    "plain-flags": (_all(_no_units, _profiles("data@0"), _flagged(True)),
                    "UnsupportedProfile: risk route with data flags is not implemented"),
    "plain-order": (_all(_no_units, _profiles("order@0", "time@0")),
                    "UnsupportedProfile: the risk norms route admits FOL documents only"),
    # Two faults: the W6 conditions come after the vocabulary and before both blocks, in both.
    "sort-gb+string": (_all(_sort("gb"), _string_const), "Unit tag gb collides with a declared sort"),
    "sort-gb+verbalisation-collision": (_all(_sort("gb"), _const("c1", sort="action", verbalisation="run"),
                                             _const("c2", sort="action", verbalisation="Run")),
                                        "Unit tag gb collides with a declared sort"),
    "sort-gb+not-fresh": (_all(_sort("gb"), lambda r: r["risk"]["severity"].update(sort="harm")),
                          "Unit tag gb collides with a declared sort"),
    "string+not-fresh": (_all(_string_const, lambda r: r["risk"]["severity"].update(sort="harm")),
                         "UnsupportedProfile: $string literals are not admitted with ve-units@1"),
    "sort-gb+outcomes": (_all(_sort("gb"), lambda r: r["alternatives"].update(outcomes={"complete_by": "x"})),
                         "Unit tag gb collides with a declared sort"),
    "schema-alone+profile-order": (_all(lambda r: r.pop("units"), _profiles("order@0", "time@0")),
                                   "UnsupportedProfile: unit_schema and units require the ve.core@0.2 quantity "
                                   "route together"),
}

# Accepted by both; the route elaborates them with Python's environment identity.
ACCEPTED = {
    "argument-units-empty": _pred({"argument_units": {}}),
    "second-unit": _unit("tb", {"scale": "1", "display": {"kind": "decimal", "label": "B"}}),
    "day": _unit("day", {"scale": "1", "display": {"kind": "iso_date"}}),
    "money": _unit("eur", {"scale": "100", "display": {"kind": "money", "currency": "EUR", "input_symbol": "€"}}),
    "verbalisation": _const("c1", sort="action", verbalisation="the run"),
    "plain-verbalisation": _all(_no_units, _const("c1", sort="action", verbalisation="run")),
    # W6's spelling rule is part of the extension: without it, two spellings may coincide (Python alike)
    "plain-verbalisations-coincide": _all(_no_units, _const("c1", sort="action", verbalisation="run"),
                                          _const("c2", sort="action", verbalisation="Run")),
    "plain-flag-false": _all(_no_units, _profiles("data@0"), _flagged(False)),
}

# Faults of the vocabulary decoders W1 and alt share (not W6's): both reject, each with its generic text.
GENERIC = {
    "argument-units-without-extension": _all(_no_units, _pred({"argument_units": {}})),
    "constant-unit-without-extension": _all(_no_units, _const("c1", sort="action", unit="gb")),
    "constant-unit-int": _const("c1", sort="$int", unit="gb"),
    "constant-unit-undeclared-sort": _const("c1", sort="widget", unit="gb"),
}


def _raw(edit):
    raw = agent_ops()
    edit(raw)
    return raw


def _python(raw):
    try:
        Environment(deepcopy(raw))
    except VEError as exc:
        return str(exc) if type(exc) is VEError or str(exc).startswith(f"{exc.code}: ") else f"{exc.code}: {exc}"
    return "ok"


def _route(raws, kind="risk-elaborate", document=None):
    cases = [{"id": str(i), "kind": kind, "environment": raw, "document": document or {"norms": []}}
             for i, raw in enumerate(raws)]
    out = lean_routes.completed(BIN, cases)
    assert out.returncode in (0, 1), out.stderr
    return json.loads(out.stdout)


def _lean(raws):
    return [row["error"] if row["status"] == "error" else "ok" for row in _route(raws)]


def test_every_w6_rule_has_one_answer_and_text():
    names = list(EXACT)
    raws = [_raw(EXACT[name][0]) for name in names]
    lean = _lean(raws)
    rows = [(name, EXACT[name][1], _python(raw), got) for name, raw, got in zip(names, raws, lean)]
    assert [row for row in rows if not row[1] == row[2] == row[3]] == []


def test_accepted_variants_elaborate_with_pythons_identity():
    raws = [_raw(edit) for edit in ACCEPTED.values()]
    for name, raw, row in zip(ACCEPTED, raws, _route(raws)):
        assert row["status"] == "ok", (name, row)
        assert row["environment_id"] == Environment(deepcopy(raw)).environment_id, name


def test_generic_vocabulary_faults_are_rejected_by_both():
    raws = [_raw(edit) for edit in GENERIC.values()]
    for name, raw, got in zip(GENERIC, raws, _lean(raws)):
        assert got != "ok" and _python(raw) != "ok", name


def test_base_environment_binding_drops_the_annotations():
    """The inner certificates bind the base environment without W6's annotations: packages proved over it are
    accepted, packages proved over a base that keeps a constant's verbalisation are not."""
    from tests.test_risk_fixtures import conflict_packages, elaborate, risk_base_environment
    from tests.test_risk_lean_route import A1, one
    from ve.ast import Not, _Decoder
    from ve.entailment import prove_entailment
    from ve.norms import _bind
    norms = [asimov_rules()[r] for r in ("1", "2")]
    plain = asimov_risk(A1)
    plain["vocabulary"]["constants"]["death"]["verbalisation"] = "death"
    extended = deepcopy(plain)
    extended.update(unit_schema="ve-units@1", units={"gb": GB})
    extended["vocabulary"]["predicates"]["taken"]["argument_units"] = {}
    for env in (plain, extended):
        elaborated, packages = conflict_packages(env, norms)
        assert packages and set(packages) == {t["target"] for t in elaborated["conflict_targets"]}
        res = one({"id": "c", "kind": "risk-conflict", "environment": env, "document": {"norms": norms},
                   "packages": packages})
        assert res["verdict"] == "CONFLICT-FREE", res
    elaborated = elaborate(plain, norms)
    kept = risk_base_environment(plain, elaborated)
    kept["vocabulary"]["constants"]["death"]["verbalisation"] = "death"
    base = Environment(kept)
    target = elaborated["conflict_targets"][0]
    proof = prove_entailment(base, (), _bind(Not(_Decoder().decode(target["ast"])), target["sorts"]),
                             max_steps=10000)
    assert proof.status == "Found"
    package = {"environment_id": elaborated["environment_id"], "document_hash": elaborated["document_hash"],
               "target": target["target"], "certificate": proof.certificate}
    res = one({"id": "c", "kind": "risk-conflict", "environment": plain, "document": {"norms": norms},
               "packages": {target["target"]: package}})
    assert res["verdict"] != "CONFLICT-FREE", res


@pytest.mark.skipif(not lean_routes.SERVICE.exists(), reason="the Lean service is not built")
@pytest.mark.parametrize("units,constants,text", [
    ({"Gb": {"scale": "1", "display": {"kind": "percent"}}}, {}, 'Invalid unit tag "Gb"'),
    ({"gx": {"scale": "1", "display": {"kind": "decimal", "label": "GB1"}}}, {},
     'DisplayCollision(" GB1" touches the amount)'),
    ({"gx": {"scale": "1", "display": {"kind": "decimal", "label": "G\tB"}}}, {},
     'Display string "G\\tB" must be whitespace-normalized'),
    ({"e1": {"scale": "1", "display": {"kind": "money", "currency": "EUR", "input_symbol": "EUR "}}}, {},
     'DisplayCollision("EUR ", "EUR ")'),
    ({"zz": {"scale": "3", "display": {"kind": "percent"}}, "aa": {"scale": "7", "display": {"kind": "percent"}}},
     {}, "UnitScale(aa): expected a positive power of ten"),
    ({}, {"b": {"sort": "$int", "description": "b", "unit": "bp", "verbalisation": "The rate"},
          "a": {"sort": "$int", "description": "a", "unit": "bp", "verbalisation": "the rate"}},
     "VerbalisationCollision(a, b)"),
], ids=["tag", "touches", "tab", "extends", "tag-order", "constant-order"])
def test_w6_texts_are_one_text_relay_and_lean(units, constants, text):
    """Python's W6 texts are the frozen Lean ones (quoted and ordered as Lean reads JSON)."""
    from tests.test_units_lean_w6a import lean, quantity
    from tests.test_w6a_review_regressions import raw_environment
    raw = raw_environment(constants=constants)
    raw["units"].update(units)
    assert _python(raw) == text
    [got] = lean([{"id": "e", "environment": raw, "quantity": quantity(["top"])}])
    assert got["error"] == text, got
