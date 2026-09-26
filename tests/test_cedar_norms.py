"""Runtime-type Cedar conditions from W1 section 10.2."""
import pytest
import json
from pathlib import Path

from ve.adapters.cedar import _parser_module, translate
from ve.model import FiniteModel
from ve.norms import check_conflict

REQUEST = {"principal": 'User::"alice"', "action": 'Action::"read"',
           "resource": 'Doc::"one"'}
ENTITIES = [{"uid": REQUEST[key], "parents": []}
            for key in ("principal", "action", "resource")]


@pytest.mark.parametrize("condition", [
    'principal in [User::"alice", "x"]',
    'principal in ["x", User::"alice"]',
    '"x" in []',
    'principal in "x"',
    'principal in []',
    'principal in [User::"alice"]',
    'true && "x"',
    'false || "x"',
    '!"x"',
    'if "x" then true else false',
    '"x"',
    'false && "x"',
    'true || "x"',
    'if true then true else !"x"',
    'if false then !"x" else false',
    'principal is Group in "x"',
    'principal == "alice"',
    'principal != "alice"',
])
def test_type_errors_and_short_circuit_match_reference(condition):
    source = ("permit(principal, action, resource); "
              f"forbid(principal, action, resource) when {{ {condition} }};")
    translated = translate(source, [], ENTITIES, [REQUEST])
    actual = translated.decisions()[0]
    reference = _parser_module().explain(source, [], ENTITIES, REQUEST)
    assert actual["decision"] == reference["decision"]
    assert set(actual["errors"]) == set(reference["errors"])
    assert not translated.exclusions


def test_forbid_overrides_and_same_sign_overlap():
    source = ('permit(principal, action, resource); '
              'forbid(principal, action, resource); '
              'forbid(principal, action, resource);')
    translated = translate(source, [], ENTITIES, [REQUEST])
    assert translated.decisions()[0]["decision"] == "deny"
    assert all(rule.over == ("policy0",) for rule in translated.document.rules[1:])
    assert check_conflict(translated.document, prove=True).status == "CONFLICT-FREE"
    base_wire = translated.model.to_dict()
    del base_wire["relations"]["permitted"]
    base = FiniteModel.from_dict(translated.document.base_environment(), base_wire)
    assert translated.document.overlap_witnesses(base) == (("policy1", "policy2", ("request0",)),)
    permit_only = translate('permit(principal, action, resource);', [], ENTITIES, [REQUEST])
    assert check_conflict(permit_only.document, prove=True).status == "CONFLICT-FREE"


@pytest.mark.parametrize("condition", [
    '[1, 2] == [2, 1]',
    '[1, 2] != [2, 1]',
    '[[1, 2], [3]] == [[3], [2, 1]]',
    '[[1, 2], [1, 2]] == [[2, 1]]',
    '[[1, 2]] != [[2, 1]]',
])
def test_recursive_set_equality_matches_reference(condition):
    source = f'permit(principal, action, resource) when {{ {condition} }};'
    actual = translate(source, [], ENTITIES, [REQUEST]).decisions()[0]
    expected = _parser_module().explain(source, [], ENTITIES, REQUEST)
    assert actual['decision'] == expected['decision']
    assert set(actual['errors']) == set(expected['errors'])


def test_excluded_attribute_is_explicit():
    source = 'permit(principal, action, resource) when { principal.age == 18 };'
    translated = translate(source, [], ENTITIES, [REQUEST])
    assert translated.exclusions == (("policy0", "attribute"),)


def test_pinned_no_attribute_integration_cases():
    root = Path(__file__).resolve().parents[1] / "experiments/P3-formalisation-tax/items"
    accepted = 0
    decisions = 0
    reference = _parser_module()
    for path in sorted(root.glob("c*_cit_*/item.json")):
        item = json.loads(path.read_text())
        policy = (path.parent / "source.cedar").read_text()
        questions = item["questions"]
        translated = translate(policy, item["world"].get("linked", []),
                               item["world"]["entities"], [q["request"] for q in questions])
        if translated.exclusions:
            continue
        accepted += 1
        for actual, question in zip(translated.decisions(), questions):
            expected = reference.explain(policy, item["world"].get("linked", []),
                                         item["world"]["entities"], question["request"])
            assert actual["decision"] == question["recorded_decision"] == expected["decision"]
            assert set(actual["errors"]) == set(expected["errors"])
            decisions += 1
    assert accepted == 6
    assert decisions == 22
