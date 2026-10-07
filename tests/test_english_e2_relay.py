"""E2's Lean-authoritative admission and untrusted response boundary."""

import copy

import pytest

from conformance import english_lean_s3_fixtures as fixtures
from ve import Environment
from ve import ast
from ve.backends import english_lean
from ve.english import EnglishVocabulary
from ve.english_grammar import export


@pytest.fixture
def answer():
    env = Environment(fixtures.F())
    words = EnglishVocabulary(env)
    source = "Legacy is deployed."
    expected = english_lean.identities(env, source, words, export(words))
    response = {"status": "one", "identities": expected,
                "ast": [ast._to_data(ast.Unary("deployed", ast.Const("legacy")))],
                "conclusions": [], "derivation": [[['sentence', 0, 1]]],
                "obligations": [], "spans": [[0, len(source)]]}
    return env, source, response


def test_e2_response_has_bound_formulas_spans_and_obligations(answer):
    env, source, response = answer
    assert english_lean.response_problem(response, response['identities'], env, source) is None
    for field in ('ast', 'derivation', 'spans', 'obligations'):
        bad = copy.deepcopy(response)
        del bad[field]
        assert english_lean.response_problem(bad, response['identities'], env, source)


def test_e2_response_rejects_bool_indices_and_substituted_identity(answer):
    env, source, response = answer
    bad = copy.deepcopy(response)
    bad['conclusions'] = [True]
    assert english_lean.response_problem(bad, response['identities'], env, source)
    bad = copy.deepcopy(response)
    bad['derivation'][0][0][1] = False
    assert english_lean.response_problem(bad, response['identities'], env, source)
    bad = copy.deepcopy(response)
    bad['identities']['environment_id'] = '0' * 64
    assert english_lean.response_problem(bad, response['identities'], env, source)


def test_e2_response_binds_each_obligation_to_an_earlier_premise(answer):
    env, source, response = answer
    response['ast'].append(response['ast'][0])
    response['derivation'].append(response['derivation'][0])
    response['spans'] = [[0, 19], [20, 40]]
    source = "Legacy is deployed. Therefore legacy is deployed."
    response['conclusions'] = [1]
    response['obligations'] = [{"conclusion": 1, "premises": [0],
                                "unproved": "No proof: {status}"}]
    assert english_lean.response_problem(response, response['identities'], env, source) is None
    for changed in ([], [1], [True], [0, 0]):
        bad = copy.deepcopy(response)
        bad['obligations'][0]['premises'] = changed
        assert english_lean.response_problem(bad, response['identities'], env, source)
