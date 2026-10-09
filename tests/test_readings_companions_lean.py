"""Readings with their own vocabulary through the Lean service (docs/spec/readings-defaults.md 1.9, 3, 4.1 step 0,
5 rows 6 to 13, 8.4; plan RD-4a).

A candidate carrying `companion: {environment, open_terms}` is written over its own environment. Lean splits the
case (`splitCase`): `main`, the document without its companion sets, then one case per companion set over the
companions' merged environment. `readings-validate` and `readings-elaborate` answer per case; the other kinds take
`component`. Python decides nothing here: every expected value is the spec's, or Lean's own answer on the same
component written as a document of its own (F-C1: "per-component answers as F-ND1's"). Meaning ids are proposed
with Python's W1 identity (`norm_meaning_id`, test tooling only) and checked by Lean (`companionMeaningId`).
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tests.test_readings_nd_lean import ASKS, PROBE1, base1, choice_case, doc1, env1, environment, lower, one, \
    regulated, run
from tests.test_readings_s1_lean import entry, norm, reading, reading_set, situation_id
from ve.environment import Environment
from ve.errors import VEError
from ve.norms import NormDocument, norm_meaning_id
from tests import lean_routes

ROOT = Path(__file__).resolve().parents[1]
LEAN = "ve_readings_route"
ND = ("norm-defaults@0", "norms@0", "readings@1", "relational-fol@0")
UDHR = json.loads((ROOT / "tests/data/readings_companions/udhr-20261006T1800Z.json").read_text())


@pytest.fixture(scope="module")
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")
    return LEAN


def mid(companion_env, content):
    """The W1 identity of `content` over its own environment (Python's, as the pilot recorded it)."""
    return norm_meaning_id(Environment(companion_env), NormDocument._decode(content))


def with_companion(r, companion_env, open_terms=()):
    r = copy.deepcopy(r)
    r["companion"] = {"environment": companion_env, "open_terms": list(open_terms)}
    if r["content"] is not None:
        try:
            r["meaning_id"] = mid(companion_env, r["content"])
        except VEError:
            pass  # an environment Python refuses: the fixture's error comes before the meaning id (5 row 13)
    return r


def merged(companion_env):
    """The merged environment of companions that all declare `companion_env`: it with `readings@1` added."""
    out = copy.deepcopy(companion_env)
    out["profiles"] = sorted(set(out["profiles"]) | {"readings@1"})
    return out


# F-C1: F-ND1's frame twice (the second with help→warn, asks→calls), plus a main fixed norm.

def env_b(profiles=ND):
    return environment({
        "calls": {"arguments": ["user", "agent"], "description": "{0} calls {1}"},
        "warn_required": {"arguments": ["agent", "user"], "description": "obligation",
                          "regulated": regulated("obligation", "unspecified", "{0} warn {1}",
                                                 permission="warn_permitted")},
        "warn_permitted": {"arguments": ["agent", "user"], "description": "permission",
                           "regulated": regulated("permission", "unspecified", "{0} warn {1}")}},
        ("agent", "user"), profiles)


def env_main():
    return environment({
        "greet_required": {"arguments": ["agent"], "description": "obligation",
                           "regulated": regulated("obligation", "deny", "{0} greet", permission="greet_permitted")},
        "greet_permitted": {"arguments": ["agent"], "description": "permission",
                            "regulated": regulated("permission", "deny", "{0} greet")}}, ("agent",))


CALLS = ("binary", "calls", ["var", 0], ["var", 1])
PROBE_B = {"outcome": {"predicate": "warn_required", "tuple": ["a", "u"]}}


def set_a(sigma=None, set_id="rs_a", unit="u_a"):
    """F-ND1's set over its own environment: (the set as a W2 set, the situation id, the companion environment)."""
    document, sid = doc1(env1(), sigma, set_id=set_id, unit=unit)
    [rs] = document["reading_sets"]
    companion = lower(env1())
    rs["readings"] = [with_companion(r, companion) for r in rs["readings"]]
    return rs, sid, companion


def set_b(set_id="rs_b", unit="u_b"):
    raw = env_b()
    sigma = entry({"domains": {"agent": ["a"], "user": ["u"]}, "constants": {},
                   "relations": {"calls": [], "unsaid__warn_permitted": [["a", "u"]], "unsaid__warn_required": []}},
                  "every", PROBE_B, True)
    sid = situation_id(raw, sigma)
    companion = lower(raw)
    rs = reading_set(set_id, unit, [
        with_companion(reading("every", norm("must-warn", "warn_required", True), {"calls": sid}), companion),
        with_companion(reading("calls", norm("must-warn", "warn_required", True, guard=CALLS), {"every": sid}),
                       companion)], {sid: sigma})
    return rs, sid, companion


MAIN_UNIT = {"id": "u0", "kind": "norm", "content": norm("must-greet", "greet_required", True)}


def fc1(**extra):
    a, sid_a, _ = set_a()
    b, sid_b, _ = set_b()
    document = {"units": [MAIN_UNIT, {"id": "u_a"}, {"id": "u_b"}], "reading_sets": [a, b], **extra}
    return document, sid_a, sid_b


def own(rs):
    """A companion set's readings without their companions: the set as a document of its own writes it."""
    rs = copy.deepcopy(rs)
    for r in rs["readings"]:
        r.pop("companion")
    return rs


def alone(rs, units, **extra):
    """A companion set written as a document of its own over its merged environment."""
    return {"units": units, "reading_sets": [own(rs)], **extra}


def components(row):
    assert row["status"] == "ok", row
    return {c["component"]: c["answer"] for c in row["components"]}, [c["component"] for c in row["components"]]


def test_fc1_three_components_each_answered_as_a_document_of_its_own(lean):
    document, _, _ = fc1()
    a, _, ca = set_a()
    b, _, cb = set_b()
    for kind in ("readings-validate", "readings-elaborate"):
        answers, order = components(one(lean, kind, env_main(), document))
        assert order == ["main", "rs_a", "rs_b"]
        assert answers["rs_a"] == one(lean, kind, merged(ca), alone(a, [{"id": "u_a"}]))
        assert answers["rs_b"] == one(lean, kind, merged(cb), alone(b, [{"id": "u_b"}]))
        main = {"units": [MAIN_UNIT, {"id": "u_a"}, {"id": "u_b"}], "reading_sets": []}
        assert answers["main"] == one(lean, kind, env_main(), main)
    answers, _ = components(one(lean, "readings-validate", env_main(), document))
    # F-ND1's answers on the first component: separated on the filled document, its `Fill_T` per reading
    assert answers["rs_a"]["sets"][0]["pairs"][0]["pair"]["separated"] is True
    assert answers["rs_b"]["sets"][0]["pairs"][0]["pair"]["separated"] is True
    assert answers["main"]["content_bearing"] is False
    # F-C5 on the wire: the two readings' identical `agent` and `user` sorts are one sort each in the merged frame
    assert sorted(answers["rs_a"]["filled"]["environment"]["vocabulary"]["sorts"]) == ["agent", "user"]
    elaborate, _ = components(one(lean, "readings-elaborate", env_main(), document))
    assert elaborate["rs_a"]["finding"] == {"text": "ReadingsNotSuperposable: rs_a", "cause": "the unspecified completion"}
    assert elaborate["rs_b"]["choices"] == [[["rs_b", 0]], [["rs_b", 1]]]
    for name in ("rs_a", "rs_b"):
        assert "fill_premises" in elaborate[name]
        assert elaborate[name]["filled"] == answers[name]["filled"]


def test_kinds_naming_one_component(lean):
    """`readings-separate`, `readings-choice` and the others run on the case `component` names (`main` when absent)."""
    document, sid_a, sid_b = fc1()
    a, _, ca = set_a()
    separate = one(lean, "readings-separate", env_main(), document, component="rs_a", set="rs_a", situation=sid_a,
                   other="asks")
    assert separate == one(lean, "readings-separate", merged(ca), alone(a, [{"id": "u_a"}]), set="rs_a",
                           situation=sid_a, other="asks")
    assert separate["pair"]["separated"] is True
    inner = {"kind": "norm-defaults-elaborate"}
    [row, own] = run(lean, [{**choice_case(env_main(), document, [("rs_a", 0)], inner), "component": "rs_a"},
                            choice_case(merged(ca), alone(a, [{"id": "u_a"}]), [("rs_a", 0)], inner)])
    assert row == own and row["status"] == "ok"
    # validate and elaborate answer one case when the request names it
    validate = one(lean, "readings-validate", env_main(), document, component="rs_b")
    assert "components" not in validate and validate["sets"][0]["set"] == "rs_b"
    # without `component` a kind of one case runs on `main`, where the companion sets are not
    assert one(lean, "readings-separate", env_main(), document, set="rs_a", situation=sid_a,
               other="asks")["status"] == "error"
    for c in ("rs_c", "", "u_a"):
        assert one(lean, "readings-validate", env_main(), document, component=c)["error"] == \
            f"InvalidInput: component {c} is not main or a reading set with its own vocabulary"
    assert one(lean, "readings-validate", env_main(), document, component=7)["error"] == \
        "InvalidInput: component  is not main or a reading set with its own vocabulary"


def test_without_companions_the_answer_is_todays(lean):
    """Conservativity (4.6): a document without `companion` is one case; `component` may name only `main`."""
    raw = env1()
    document, sid = doc1(raw)
    for kind in ("readings-validate", "readings-elaborate"):
        today = one(lean, kind, raw, document)
        assert "components" not in today
        assert one(lean, kind, raw, document, component="main") == today
        assert one(lean, kind, raw, document, component="rs_1")["error"] == \
            "InvalidInput: component rs_1 is not main or a reading set with its own vocabulary"


def two_readings(env0, env1_, set_id="rs_a"):
    """A set of two readings over `env0` and `env1_` (their declarations as given), unseparated."""
    sid = "s"
    return reading_set(set_id, "u_a", [
        with_companion(reading("r0", norm("r0", "help_required", True), {"r1": sid}), env0),
        with_companion(reading("r1", norm("r1", "help_required", True, guard=ASKS), {"r0": sid}), env1_)], {})


def validate_error(lean, rs, units=({"id": "u_a"},), **document):
    return one(lean, "readings-validate", env_main(), {"units": list(units), "reading_sets": [rs], **document})["error"]


def test_fc2_a_name_declared_differently(lean):
    e0, e1 = lower(env1()), lower(env1())
    e1["vocabulary"]["predicates"]["asks"]["arguments"] = ["agent", "user"]
    assert validate_error(lean, two_readings(e0, e1)) == \
        "InvalidInput: readings rs_a@1:0 and rs_a@1:1 declare asks differently"
    # the spec's own example: a predicate over (bearer, person) against (state, person)
    p0, p1 = lower(env1()), lower(env1())
    p0["vocabulary"]["sorts"].update({"bearer": {"description": "bearer"}, "person": {"description": "person"}})
    p1["vocabulary"]["sorts"].update({"bearer": {"description": "bearer"}, "person": {"description": "person"},
                                      "state": {"description": "state"}})
    p0["vocabulary"]["predicates"]["avoid_life_required"] = {"arguments": ["bearer", "person"], "description": "d"}
    p1["vocabulary"]["predicates"]["avoid_life_required"] = {"arguments": ["state", "person"], "description": "d"}
    p1["vocabulary"]["sorts"].pop("state")
    p1["vocabulary"]["sorts"]["state"] = {"description": "state"}
    assert validate_error(lean, two_readings(p0, p1)) == \
        "InvalidInput: readings rs_a@1:0 and rs_a@1:1 declare avoid_life_required differently"


def test_fc3_a_set_mixing_readings_with_and_without_their_own_vocabulary(lean):
    rs = two_readings(lower(env1()), lower(env1()))
    rs["readings"][1].pop("companion")
    assert validate_error(lean, rs) == \
        "InvalidInput: reading set rs_a mixes readings with and without their own vocabulary"


def test_fc4_language_revision_and_profiles_must_agree(lean):
    for key, value in (("profiles", ["norms@0", "relational-fol@0"]), ("language", "ve.core@0.1"),
                       ("spec_revision", "other")):
        e1 = lower(env1())
        e1[key] = value
        assert validate_error(lean, two_readings(lower(env1()), e1)) == \
            f"InvalidInput: the readings of rs_a declare different {key}"


def test_fc5_identical_declarations_unite_whatever_their_key_order(lean):
    """Two readings declaring `asks` with the same entries written in another key order are one declaration
    (canonical bytes, not the request's order: checklist 3)."""
    e1 = lower(env1())
    asks = e1["vocabulary"]["predicates"]["asks"]
    e1["vocabulary"]["predicates"]["asks"] = dict(reversed(list(asks.items())))
    e1["vocabulary"]["predicates"] = dict(reversed(list(e1["vocabulary"]["predicates"].items())))
    rs = two_readings(lower(env1()), e1)
    # the merge passes; the unseparated pair is then refused by S1's admission of the component, not by the merge
    assert validate_error(lean, rs) == "distinguishing model id does not match model"


def test_fc6_a_main_rule_over_a_companion_readings_rule(lean):
    document, _, _ = fc1()
    document["units"][0] = {"id": "u0", "kind": "norm",
                            "content": norm("must-greet", "greet_required", True, over=["must-help"])}
    for kind in ("readings-validate", "readings-elaborate", "readings-separate", "readings-choice",
                 "readings-conflict", "readings-certificate", "readings-model", "readings-dead"):
        for component in (None, "rs_a", "rs_b"):
            fields = {} if component is None else {"component": component}
            row = one(lean, kind, env_main(), document, **fields)
            assert row["error"] == "UnknownRule: rule must-help", (kind, component, row)
    # A later companion's admission error also prevents an answer from an earlier, valid component.
    document, _, _ = fc1()
    reading = document["reading_sets"][1]["readings"][0]
    reading["content"] = norm("must-warn", "warn_required", True, over=["ghost"])
    reading["meaning_id"] = mid(lower(env_b()), reading["content"])
    for kind in ("readings-validate", "readings-elaborate", "readings-separate", "readings-choice",
                 "readings-conflict", "readings-certificate", "readings-model", "readings-dead"):
        row = one(lean, kind, env_main(), document, component="rs_a")
        assert row["error"].startswith("UnknownRule: rule ghost"), (kind, row)


def test_fc7_meaning_ids_of_the_udhr_companions(lean):
    """`companionMeaningId` on u022a.entitlement, u048.state_negative and u074.prohibition (run 20261006T1800Z,
    saved in tests/data): equal to the recorded `meaning_id` (the companion unit's id for u074). Each is a one-reading
    companion set; the split checks every meaning id (5 row 13) before any case is admitted."""
    sets, units = [], []
    for k, c in enumerate(UDHR["companions"]):
        expected = c.get("recorded_meaning_id", c["companion_unit_meaning_id"])
        assert expected == c["companion_unit_meaning_id"]
        r = reading(c["candidate"], c["content"], {})
        r["companion"], r["meaning_id"] = c["companion"], expected
        sets.append(reading_set(f"rs_{c['unit']}", c["unit"], [r], {}))
        units.append({"id": c["unit"]})
    document = {"units": units, "reading_sets": sets}
    # recorded ids accepted: each companion set is its own component, admitted under the completion
    answers, order = components(one(lean, "readings-validate", env_main(), document))
    assert order == ["main", "rs_u022a", "rs_u048", "rs_u074"]
    assert all(answers[s]["content_bearing"] is True for s in order[1:])
    for k in range(len(sets)):
        tampered = copy.deepcopy(document)
        tampered["reading_sets"][k]["readings"][0]["meaning_id"] = "0" * 64
        assert one(lean, "readings-validate", env_main(), tampered)["error"] == \
            "reading meaning id does not match content"
    # the recorded ids are not those of the main environment (the identity is over the companion's own)
    c = UDHR["companions"][0]
    assert c["recorded_meaning_id"] != mid(lower(env1()) | {"vocabulary": c["companion"]["environment"]["vocabulary"]},
                                           c["content"])


def test_fc8_a_companion_on_the_soft_or_rights_chain(lean):
    for profile in ("soft-norms@0", "rights@0"):
        e1 = lower(env1())
        e1["profiles"] = sorted(e1["profiles"] + [profile])
        assert validate_error(lean, two_readings(lower(env1()), e1)) == \
            "UnsupportedProfile: readings with their own vocabulary on the soft or rights chain are not implemented"


def pending_set(set_id, unit, labels):
    return reading_set(set_id, unit, [
        {**reading(f"{set_id}_{k}", None, {f"{set_id}_{1 - k}": "s"}), "labels": {"who": label}}
        for k, label in enumerate(labels)], {})


def coupling(cid, *sets):
    return {"id": cid, "axis": "who", "by": "w", "reason_spans": ["u0"],
            "sets": [{"set": s, "version": 1} for s in sets]}


def test_fc9_a_coupling_across_components_is_refused_one_within_main_is_kept(lean):
    document, _, _ = fc1(couplings=[coupling("c1", "rs_a", "rs_b")])
    assert one(lean, "readings-validate", env_main(), document)["error"] == \
        "InvalidInput: coupling c1 links rs_a and rs_b, which do not share one vocabulary"
    document, _, _ = fc1(couplings=[coupling("c2", "rs_m1", "rs_a")])
    document["reading_sets"] += [pending_set("rs_m1", "u_m1", ["state", "anyone"])]
    document["units"] += [{"id": "u_m1"}]
    assert one(lean, "readings-validate", env_main(), document)["error"] == \
        "InvalidInput: coupling c2 links rs_a and rs_m1, which do not share one vocabulary"
    # a coupling over two main sets stays in the main case, where W2's coupling checks read it
    document, _, _ = fc1(couplings=[coupling("c3", "rs_m1", "rs_m2")])
    document["reading_sets"] += [pending_set("rs_m1", "u_m1", ["state", "anyone"]),
                                 pending_set("rs_m2", "u_m2", ["state", "anyone"])]
    document["units"] += [{"id": "u_m1"}, {"id": "u_m2"}]
    # (S2a's admission reads couplings and narrowings: `readings-elaborate`)
    answers, order = components(one(lean, "readings-elaborate", env_main(), document))
    assert order == ["main", "rs_a", "rs_b"]
    document["reading_sets"][-1]["readings"][0]["labels"] = {"other": "x"}
    assert one(lean, "readings-elaborate", env_main(), document)["error"] == "CouplingLabelMissing: c3, rs_m2"


def ill_treatment(*necessary):
    return {"name": "ill_treatment", "arguments": [], "decided_by": "court", "jurisdiction": "universal",
            "necessary": list(necessary), "sufficient": [], "factors": [], "precedents": [], "version": 1}


ASKS_SOMEONE = ["exists", "user", ["exists", "agent", ["binary", "asks", ["var", 1], ["var", 0]]]]


def test_fc10_open_terms_merge_by_name_and_are_typed_in_the_merged_frame(lean):
    def with_terms(t0, t1):
        rs = two_readings(lower(env1()), lower(env1()))
        rs["readings"][0]["companion"]["open_terms"] = [t0]
        rs["readings"][1]["companion"]["open_terms"] = [t1]
        return rs
    assert validate_error(lean, with_terms(ill_treatment(), ill_treatment(ASKS_SOMEONE))) == \
        "InvalidInput: readings rs_a@1:0 and rs_a@1:1 declare open term ill_treatment differently"
    # identical entries pass the merge, and a condition over a companion predicate types in the merged frame
    assert validate_error(lean, with_terms(ill_treatment(ASKS_SOMEONE), ill_treatment(ASKS_SOMEONE))) == \
        "distinguishing model id does not match model"
    # a condition over a predicate the companions do not declare (the main frame's) is refused there
    greets = ["exists", "agent", ["unary", "greet_required", ["var", 0]]]
    assert validate_error(lean, with_terms(ill_treatment(greets), ill_treatment(greets))) == \
        "UnknownSymbol: Unknown predicate 'greet_required'"


def test_fc11_a_narrowing_travels_with_its_companion_set(lean):
    narrowing = {"id": "n1", "set": "rs_a", "version": 1, "keeps": ["every"], "by": "w", "reason_spans": ["u0"]}
    document, _, _ = fc1(narrowings=[narrowing])
    answers, _ = components(one(lean, "readings-elaborate", env_main(), document))
    assert answers["rs_a"]["choices"] == [[["rs_a", 0]]]
    assert answers["rs_b"]["choices"] == [[["rs_b", 0]], [["rs_b", 1]]]
    a, _, ca = set_a()
    assert answers["rs_a"] == one(lean, "readings-elaborate", merged(ca),
                                  alone(a, [{"id": "u0"}, {"id": "u_a"}], narrowings=[narrowing]))
    # in the main case the narrowing would name a set it does not have
    narrowing_main = {**narrowing, "set": "rs_x"}
    document, _, _ = fc1(narrowings=[narrowing_main])
    assert one(lean, "readings-elaborate", env_main(), document)["error"] == \
        "narrowing cites unknown reading set version"


def test_fc12_an_unseparated_set_stays_in_main_as_w2(lean):
    document, _, _ = fc1()
    document["reading_sets"][1] = pending_set("rs_b", "u_b", ["state", "anyone"])
    for kind in ("readings-validate", "readings-elaborate"):
        answers, order = components(one(lean, kind, env_main(), document))
        assert order == ["main", "rs_a"]
    elaborate, _ = components(one(lean, "readings-elaborate", env_main(), document))
    assert elaborate["main"]["route"] == "w2"


@pytest.mark.parametrize("value", [7, True, [], {}, "x"])
def test_malformed_companions_are_refused_by_name(lean, value):
    """Checklist 5: a companion, its environment or its open terms replaced by another JSON value gives an error
    row, never a crash or an answer."""
    for path in (("companion",), ("companion", "environment"), ("companion", "open_terms")):
        if path[-1] == "open_terms" and value == []:
            continue  # no open terms: well formed
        rs = two_readings(lower(env1()), lower(env1()))
        for r in rs["readings"]:
            target = r
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
        row = one(lean, "readings-validate", env_main(), {"units": [{"id": "u_a"}], "reading_sets": [rs]})
        # refused by the split itself, before the (unseparated) set's admission could be reached
        assert row["status"] == "error", (path, value, row)
        assert row["error"] != "distinguishing model id does not match model", (path, value, row)
