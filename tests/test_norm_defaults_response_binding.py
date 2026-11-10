"""norm-defaults-cfr-1 (regrade #3, ND-FC2) and norm-defaults-cfr-1b: the norm-defaults mode's answers are bound to
their request.

A `norm-defaults-status` row's `tuple` is the request's, its `rules` are distinct and it carries one `sources` echo per
rule (response schema, rendered from `ResponseShape/Schemas/NormDefaults.lean`). Each echo names its rule and the request
rule it comes from, a rule of the request (`lean_service.bind_answers`); a rule may differ from its source, a name Lean
generated, only when the profiles list contains `acts@0` (a part) or `rights@0` (a fan-out or bar rule). A forged
generated name is refused whatever the profile. A `norm-defaults-certificate`
row's `premises` is the count of the regenerated premises its certificate is bound to (`bind_answers`). Each forged
row reaches the client from a scripted service and is `CheckerUnavailable`; Lean's own rows still pass. The assurance
manifest lists every kind the mode answers.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from conformance import norm_defaults_layered as layered
from conformance.norm_defaults import sources
from conformance.norm_defaults_three_way import _conjunction, certificate_case
from tests.lean_build import lean_build
from tests.subprocesses import HANG_TIMEOUT
from tests.test_lean_service import fake
from tests.test_norm_defaults import CSAM_RULE, CSAM_SITUATION, csam
from ve import norm_defaults as nd
from ve.ast import Top, formula_to_data
from ve.backends.lean_service import Invalid, LeanService, _rule_names, bind_answers
from ve.backends.service_schema import check_row
from ve.errors import CheckerUnavailable
from ve.norm_defaults_route import prove_filled_entailment, source_case

ROOT = Path(__file__).resolve().parents[1]
MODE = "norm-defaults"
ACTS_RULE = {"norm": {"name": "r027", "predicate": "p027", "sign": False, "guard": ["top"], "unless": [],
                      "over": []}}
ARREST_MODEL = {"complete": True, "domains": {"state": ["s"], "person": ["p"]}, "constants": {},
                "relations": {"arbitrary": [["s", "p"]], "rights__lim__1": [], "rights__cond__1": []}}


def _acts_environment():
    """A joined act `acts@0` splits into two parts (tests/test_acts_joined_route.py, ap-3db)."""
    from tests.test_acts_joined_route import DEFAULT_PROFILES, environment
    return environment(DEFAULT_PROFILES, default="unspecified")


def _rights_fan_out(case):
    """The rights case with its line fanned out to the `state` bearer: Lean names the instance `rights-fan-1`."""
    fanned = copy.deepcopy(case)
    fanned["document"][0]["right"]["lines"][0]["fan_out"] = {"state": "arrest_permitted"}
    return fanned


def _certificate_with_a_premise(document):
    """`certificate_case` with the case's own premise `⊤`: the row counts the regenerated premises only."""
    conclusion = _conjunction([f for _, f in document.fill_premises] + [f for _, f in document.filled.premises()])
    return source_case(document, "norm-defaults-certificate", premises=[formula_to_data(document.filled.env, Top())],
                       conclusion=formula_to_data(document.filled.env, conclusion),
                       certificate=prove_filled_entailment(document, (Top(),), conclusion))


def _cases():
    csam_doc = nd.UnspecifiedDocument(csam("unspecified"), [CSAM_RULE])
    u5a = next(document for name, document, _ in sources() if name == "u5a")
    kind, env, source = next((kind, env, source) for _, kind, env, source, _ in layered.fixtures()
                             if kind == "rights")
    rights = layered.case(kind, env, source, "norm-defaults-status", model=ARREST_MODEL,
                          predicate="arrest_permitted", tuple=["s", "p"], method="table3")
    return {
        "status": source_case(csam_doc, "norm-defaults-status", model=CSAM_SITUATION,
                              predicate="csam_generation_permitted", tuple=["claude0"], method="enumerate"),
        "rights-status": rights,
        "rights-fan-status": _rights_fan_out(rights),
        "acts-status": {"id": "norm-defaults-status", "kind": "norm-defaults-status", "norms": [ACTS_RULE],
                        "environment": _acts_environment(), "predicate": "p027__1", "tuple": ["a"],
                        "method": "table3", "model": {"complete": True, "domains": {"person": ["a"]},
                                                      "constants": {}, "relations": {}}},
        "certificate": certificate_case(u5a),
        "certificate-premise": _certificate_with_a_premise(u5a),
    }


@pytest.fixture(scope="module")
def genuine():
    """Each case with Lean's own row, from the real service (whose answers the binding checks too)."""
    cases = _cases()
    with LeanService(lean_build("ve_service") / "ve_service", timeout=HANG_TIMEOUT) as service:
        rows = service.run(MODE, list(cases.values()), timeout=HANG_TIMEOUT)
    return {name: (case, row) for (name, case), row in zip(cases.items(), rows)}


def _scripted(tmp_path, case, row):
    """The client's answer when the service sends `row` for `case`."""
    answer = {"id": "__nonce__", "status": "ok", "mode": MODE, "results": [row],
              "counts": {"cases": 1, "bytes": "__bytes__", "errors": 0}}
    (tmp_path / "marker").write_text(json.dumps(answer))
    with LeanService(fake(tmp_path, "scripted"), allow_unlisted_build=True) as service:
        return service.run(MODE, [case])


def test_genuine_answers_pass(genuine, tmp_path):
    """Lean's rows name what the binding allows, on each source shape, and pass it again from a script."""
    assert genuine["status"][1]["rules"] == ["no-csam-generation"]
    assert genuine["rights-status"][1]["rules"] == ["art9"]
    assert genuine["acts-status"][1]["rules"] == ["r027-a1"]  # Lean's part name (`Acts.Elaborate.partRule`)
    assert genuine["rights-fan-status"][1]["rules"] == ["rights-fan-1"]  # Lean's fan-out name (`Rights.fanName`)
    # Each rule with the request rule Lean echoes as its source: itself, the split rule, the fanned-out norm.
    assert [genuine[name][1]["sources"] for name in ("status", "rights-status", "acts-status", "rights-fan-status")] == [
        [{"rule": "no-csam-generation", "source": "no-csam-generation"}], [{"rule": "art9", "source": "art9"}],
        [{"rule": "r027-a1", "source": "r027"}], [{"rule": "rights-fan-1", "source": "art9"}]]
    for name, own in (("certificate", 0), ("certificate-premise", 1)):
        case, row = genuine[name]
        assert len(case["premises"]) == own and row["valid"] is True
        assert row["premises"] == len(case["certificate"]["premise_meaning_ids"]) - own > 0
    for name, (case, row) in genuine.items():
        assert row["status"] == "ok", (name, row)
        assert _scripted(tmp_path, case, row) == [row], name


def _forge(name, field, value):
    def forge(case, row):
        return {**row, field: value(case, row)}
    return pytest.param(name, forge, id=f"{name}-{field}-{value.__name__}")


def ghost(case, row):
    return ["no-such-rule"]


def appended(case, row):
    return [*row["rules"], "no-such-rule"]


def duplicated(case, row):
    return row["rules"] * 2


def predicate_named(case, row):
    return [case["predicate"]]


def part_without_acts(case, row):
    return [f"{row['rules'][0]}-a1"]


def forged_generated(case, row):
    """Lean's generated name with another index: a part or fan-out instance Lean did not answer."""
    return [row["rules"][0][:-1] + "7"]


def _echo(rule, source):
    def echo(case, row):
        return [{"rule": rule(row), "source": source(row)}]
    echo.__name__ = f"echo_{rule.__name__}_{source.__name__}"
    return echo


def own_rule(row):
    return row["rules"][0]


def own_source(row):
    return row["sources"][0]["source"]


def no_such_rule(row):
    return "no-such-rule"


def generated_name(row):
    return own_rule(row)[:-1] + "7"


def dropped(case, row):
    return row["sources"][:-1]


def doubled(case, row):
    return row["sources"] * 2


def other_entity(case, row):
    return ["sol0"]


def absent_entity(case, row):
    return ["ghost0"]


def longer(case, row):
    return [*row["tuple"], row["tuple"][0]]


def reversed_tuple(case, row):
    return row["tuple"][::-1]


def emptied(case, row):
    return []


def one_more(case, row):
    return row["premises"] + 1


def one_fewer(case, row):
    return row["premises"] - 1


def zero(case, row):
    return 0


def every_id(case, row):
    return len(case["certificate"]["premise_meaning_ids"])


FORGERIES = [
    # A rule reference absent from the request.
    _forge("status", "rules", ghost), _forge("status", "rules", appended), _forge("status", "rules", duplicated),
    _forge("status", "rules", predicate_named),
    _forge("status", "rules", part_without_acts),
    # A generated rule name Lean did not answer, under acts@0 and under rights@0 (norm-defaults-cfr-1b), or one no
    # rule of the request.
    _forge("acts-status", "rules", forged_generated), _forge("rights-fan-status", "rules", forged_generated),
    _forge("acts-status", "rules", ghost), _forge("rights-fan-status", "rules", ghost),
    _forge("acts-status", "rules", appended), _forge("rights-fan-status", "rules", appended),
    # A source echo that names another rule, or a source that is no rule of the request (cfr-1b).
    _forge("acts-status", "sources", _echo(generated_name, own_source)),
    _forge("rights-fan-status", "sources", _echo(generated_name, own_source)),
    _forge("acts-status", "sources", _echo(own_rule, no_such_rule)),
    _forge("rights-fan-status", "sources", _echo(own_rule, no_such_rule)),
    _forge("rights-fan-status", "sources", _echo(own_rule, own_rule)),
    _forge("status", "sources", _echo(own_rule, no_such_rule)),
    _forge("acts-status", "sources", dropped), _forge("rights-fan-status", "sources", doubled),
    # The rule and its echo forged together to a generated name, without acts@0 or rights@0.
    pytest.param("status", lambda case, row: {**row, "rules": [generated_name(row)],
                                              "sources": [{"rule": generated_name(row), "source": own_rule(row)}]},
                 id="status-rules-and-sources-generated_name"),
    # An entity reference that is not the request's tuple.
    _forge("status", "tuple", other_entity), _forge("status", "tuple", absent_entity),
    _forge("status", "tuple", longer), _forge("status", "tuple", emptied),
    _forge("rights-status", "tuple", reversed_tuple), _forge("acts-status", "tuple", absent_entity),
    # A premise count that is not the count the certificate carries.
    _forge("certificate", "premises", one_more), _forge("certificate", "premises", one_fewer),
    _forge("certificate", "premises", zero), _forge("certificate-premise", "premises", every_id),
    _forge("certificate-premise", "premises", one_more),
]


@pytest.mark.parametrize("name, forge", FORGERIES)
def test_norm_defaults_response_binding(genuine, tmp_path, name, forge):
    """Each forged row, the rest of Lean's row kept, is no answer: `CheckerUnavailable` after one retry."""
    case, row = genuine[name]
    forged = forge(case, copy.deepcopy(row))
    assert forged != row
    with pytest.raises(CheckerUnavailable, match="malformed response"):
        _scripted(tmp_path, case, forged)


# Each bound field deleted or retyped (BUILDER-CHECKLIST 1): the schema or the binding refuses it.
RETYPED = [7, True, None, [], {}, 1.5, "\ud800", [7], [True], [None], [[]], [{}]]
FIELDS = [("status", "tuple"), ("status", "rules"), ("acts-status", "rules"), ("rights-fan-status", "rules"),
          ("status", "sources"), ("acts-status", "sources"), ("rights-fan-status", "sources"),
          ("certificate", "premises")]


@pytest.mark.parametrize("name, field", FIELDS)
def test_each_bound_field_deleted_or_retyped_is_no_answer(genuine, tmp_path, name, field):
    case, row = genuine[name]
    mutants = [{k: v for k, v in row.items() if k != field}]
    # No rule deciding is an answer Lean gives (UNKNOWN, or a point its default settles): `rules: []` is no forgery.
    mutants += [{**row, field: value} for value in RETYPED if not (field == "rules" and value == [])]
    for mutant in mutants:
        with pytest.raises(CheckerUnavailable, match="malformed response"):
            _scripted(tmp_path, case, mutant)


def test_a_certificate_case_without_its_certificate_has_no_count(genuine, tmp_path):
    """No certificate (or no premise list) in the request: no premise count binds, so no `ok` row is an answer."""
    case, row = genuine["certificate"]
    for missing in ("certificate", "premises"):
        with pytest.raises(CheckerUnavailable, match="malformed response"):
            _scripted(tmp_path, {k: v for k, v in case.items() if k != missing}, row)


def test_request_rules_on_each_source_shape(genuine):
    """The rules an echoed source may name: the `norms` units', and under `rights@0` the rules its `document` holds
    (a line's norm, a power's liberty and recognition, a bar), at any depth."""
    assert _rule_names(genuine["status"][0]) == {"no-csam-generation"}
    assert _rule_names(genuine["acts-status"][0]) == {"r027"}
    assert _rule_names(genuine["rights-fan-status"][0]) == {"art9"}
    case = {"environment": {"profiles": ["rights@0"]}, "document": {"units": [{"content": {"right": {"lines": [
        {"kind": "power", "liberty": {"name": "may"}, "recognition": {"name": "rec"}}]}}}, {"content": {"bar": {
            "name": "b30"}}}, {"content": {"limitation": {"name": "l29"}}}]}}
    assert _rule_names(case) == {"may", "rec", "b30"}
    assert _rule_names({**case, "environment": {"profiles": ["soft-norms@0"]}}) == set()


@pytest.mark.parametrize("environment", [None, {}, {"profiles": None}, {"profiles": {}},
                                              {"profiles": []}, {"profiles": ["norms@0"]}])
def test_status_rule_binding_without_generated_profile(environment):
    """A missing or malformed profile list does not waive binding of an `ok` status row's rule names."""
    case = {"kind": "norm-defaults-status", "norms": [{"norm": {"name": "r1"}}]}
    if environment is not None:
        case["environment"] = environment
    def answer(rule, source):
        return {"status": "ok", "results": [{"index": 0, "result": {
            "status": "ok", "rules": [rule], "sources": [{"rule": rule, "source": source}]}}]}
    for rule, source in (("ghost", "ghost"), ("ghost", "r1"), ("r1", "ghost")):
        with pytest.raises(Invalid, match="no rule of the request"):
            bind_answers(MODE, answer(rule, source), {"cases": [case]})
    bind_answers(MODE, answer("r1", "r1"), {"cases": [case]})


@pytest.mark.parametrize("profile", ["acts@0", "rights@0"])
def test_a_generated_rule_needs_its_echo(profile):
    """Under `acts@0` or `rights@0` a rule Lean generated passes with the echo naming it and a request source, and
    with nothing less: no echo, an echo of another rule, or a source the request does not hold."""
    case = {"kind": "norm-defaults-status", "environment": {"profiles": [profile]}, "norms": [{"norm": {"name": "r1"}}]}

    def answer(rules, sources):
        return {"status": "ok", "results": [{"index": 0, "result": {"status": "ok", "rules": rules,
                                                                     "sources": sources}}]}
    bind_answers(MODE, answer(["g1"], [{"rule": "g1", "source": "r1"}]), {"cases": [case]})
    for rules, sources in ((["g1"], []), (["g1"], None), (["g2"], [{"rule": "g1", "source": "r1"}]),
                           (["g1"], [{"rule": "g1", "source": "g1"}]), (["g1"], ["r1"])):
        with pytest.raises(Invalid):
            bind_answers(MODE, answer(rules, sources), {"cases": [case]})


def test_status_tuple_schema_binds_request_without_service():
    """The Lean-rendered row shape rejects a different entity even before the client starts a service."""
    case = {"id": "norm-defaults-status", "kind": "norm-defaults-status", "predicate": "p", "tuple": ["a"]}
    row = {"id": "norm-defaults-status", "status": "ok", "point_status": "UNKNOWN", "predicate": "p",
           "tuple": ["a"], "rules": [], "sources": [], "differs": []}
    check_row(MODE, row, case, 0)
    with pytest.raises(Invalid):
        check_row(MODE, {**row, "tuple": ["ghost"]}, case, 0)


def test_the_manifest_lists_every_kind_the_mode_answers():
    """The kinds the manifest binds for ve_service mode norm-defaults are the kinds of the mode's own rows: the
    `kind` table of its response schema (rendered from `ResponseShape/Schemas/NormDefaults.lean`). A case off the
    norm-defaults path is the norms runner's, under the norms mode's own schema."""
    manifest = json.loads((ROOT / "ve/assurance-manifest.json").read_text())
    listed = [kind for op in manifest["operations"] for b in (op["lean"] or {}).get("bindings", ())
              if (b["executable"], b["mode"]) == ("ve_service", MODE) for kind in b["kinds"]]
    schema = json.loads((ROOT / "ve/backends/lean_service_schema/norm-defaults.json").read_text())
    answered = set(schema["$defs"]["kind"]) - {"$comment"}
    assert len(listed) == len(set(listed)) and set(listed) == answered, set(listed) ^ answered
