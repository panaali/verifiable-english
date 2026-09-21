"""New rules are paired with Lean soundness and independent replay evidence."""
import copy
from pathlib import Path

import pytest

from conformance.closure_certificates import environment, positive_cases, forged_cases, reviewer_queries
from conformance.certificates import envelope, invoke
from ve import (ArgumentGraph, Claim, Deduction, Document, Environment, check_argument,
                document_to_data, meaning_id, print_document, render, source_id, outstanding_obligations)
from ve.ast import Binary, Body, Const, Exists, Named, Reach, Top, Var
from ve.entailment import _binding, check_entailment_certificate, prove_entailment

ROOT = Path(__file__).resolve().parents[1]


def test_closure_certificates_replay_and_reviewer_regressions():
    positive, outcomes = positive_cases()
    forged = forged_cases(positive)
    assert outcomes['transitivity']['status'] == 'Found'
    assert outcomes['last_edge']['status'] == 'Found'
    assert outcomes['first_edge']['status'] == 'Found'
    assert outcomes['named_body']['status'] == outcomes['body_named']['status'] == 'Found'
    assert outcomes['monotonicity']['status'] == 'ResourceLimit'
    assert outcomes['symmetric_reversal']['status'] == 'ResourceLimit'
    rows = invoke(ROOT / 'lean/.lake/build/bin/ve_conformance', positive + forged)
    assert [r['valid'] for r in rows] == [True] * len(positive) + [False] * len(forged)


def test_body_symbol_spacing_changes_no_identity():
    env = environment()
    a, b = Const('a'), Const('b')
    body = Reach('plus', Body('item', Binary('rel', Var(1), Var(0))), a, b)
    named = Reach('plus', Named('rel'), a, b)
    doc = Document((body, named))
    raw = document_to_data(env, doc)
    strict = print_document(env, doc)
    before = env.environment_id, meaning_id(env, doc), source_id(strict, env)
    assert render(body, env, 'fol_symbols').endswith('(@a, @b)')
    assert render(named, env, 'fol_symbols').endswith('(@a, @b)')
    assert document_to_data(env, doc) == raw
    assert print_document(env, doc) == strict
    assert (env.environment_id, meaning_id(env, doc), source_id(strict, env)) == before
    # Pin the canonical commitments independently of display rendering.
    assert raw[0] == ['reach', 'plus', ['body', 'item', ['binary', 'rel', ['var', 1], ['var', 0]]],
                      ['const', 'a'], ['const', 'b']]


def test_closure_notfound_does_not_claim_saturation_completeness():
    env = environment()
    result = prove_entailment(env, [], Binary('rel', Const('a'), Const('b')))
    assert result.status == 'NotFound'
    assert 'inconclusive' in result.detail and 'saturated' not in result.detail


def test_argument_profile_and_actual_lean_status():
    env = environment()
    claims = (Claim.create(env, 'edge', '@a rel @b.\n'),
              Claim.create(env, 'path', 'tc[rel](@a, @b).\n'))
    graph = ArgumentGraph(env, claims, (Deduction('step', ('edge',), 'path'),), 'path')
    options = dict(max_proof_steps=40, max_models=0)
    python = check_argument(graph, **options)
    assert python.composed and not python.lean_checked
    assert python.to_dict()['profiles'] == ['closure@0', 'relational-fol@0']
    assert python.to_dict()['lean_status'] == 'Lean-checked: no'
    assert python.to_dict()['proof'] != 'checked'
    lean = check_argument(graph, lean_executable=ROOT / 'lean/.lake/build/bin/ve_conformance', **options)
    assert lean.composed and lean.lean_checked, lean.to_dict()
    assert outstanding_obligations(graph, lean)['lean_status'] == 'Lean-checked: yes'
    missing = check_argument(graph, lean_executable=ROOT / 'absent-checker', **options)
    assert missing.composed and not missing.lean_checked


def test_new_rules_reject_heterogeneous_edge_and_old_profile():
    env = environment()
    ps, goal = [Binary('visits', Const('a'), Const('here'))], Top()
    cert = {**_binding(env, tuple(ps), goal), 'trace': {'rule': 'closure-edge@0', 'at': 0,
                                                     'children': [{'rule': 'close'}]}}
    assert not check_entailment_certificate(env, ps, goal, cert).valid
    row = invoke(ROOT / 'lean/.lake/build/bin/ve_conformance', [envelope('hetero', env, ps, goal, cert)])[0]
    assert not row['valid']
    from conformance.certificates import environment as old_environment
    old = old_environment()
    ps = [Binary('rel', Const('a'), Const('b'))]
    cert = {**_binding(old, tuple(ps), goal), 'trace': cert['trace']}
    assert not check_entailment_certificate(old, ps, goal, cert).valid
