"""norm-defaults-cfr-1 (regrade #3, ND-FC2): the norm-defaults mode's answers are bound to their request.

A `norm-defaults-status` row's `tuple` is the request's and its `rules` are distinct (response schema, rendered from
`ResponseShape/Schemas/NormDefaults.lean`) and rules of the request's `norms` (`lean_service.bind_answers`; not yet
when the profiles list contains `acts@0` or `rights@0`, whose rules Lean names itself: norm-defaults-cfr-1b); a `norm-defaults-certificate`
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
    return {
        "status": source_case(csam_doc, "norm-defaults-status", model=CSAM_SITUATION,
                              predicate="csam_generation_permitted", tuple=["claude0"], method="enumerate"),
        "rights-status": layered.case(kind, env, source, "norm-defaults-status", model=ARREST_MODEL,
                                      predicate="arrest_permitted", tuple=["s", "p"], method="table3"),
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
FIELDS = [("status", "tuple"), ("status", "rules"), ("acts-status", "rules"), ("certificate", "premises")]


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


def test_rules_named_by_lean_under_acts_or_rights_are_not_yet_bound(genuine):
    """`acts@0` parts and `rights@0` fan-out and bar rules have names the request does not carry, and Lean does not
    yet say which request rule each comes from (norm-defaults-cfr-1b), so their rows' rules are not bound; every other
    source's are."""
    assert _rule_names(genuine["acts-status"][0]) is None and _rule_names(genuine["rights-status"][0]) is None
    assert _rule_names(genuine["status"][0]) == {"no-csam-generation"}


@pytest.mark.parametrize("environment", [None, {}, {"profiles": None}, {"profiles": {}},
                                              {"profiles": []}, {"profiles": ["norms@0"]}])
def test_status_rule_binding_without_generated_profile(environment):
    """A missing or malformed profile list does not waive binding of an `ok` status row's rule names."""
    case = {"kind": "norm-defaults-status", "norms": [{"norm": {"name": "r1"}}]}
    if environment is not None:
        case["environment"] = environment
    response = {"status": "ok", "results": [{"index": 0, "result": {"status": "ok", "rules": ["ghost"]}}]}
    with pytest.raises(Invalid, match="no rule of the request"):
        bind_answers(MODE, response, {"cases": [case]})
    response["results"][0]["result"]["rules"] = ["r1"]
    bind_answers(MODE, response, {"cases": [case]})


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
