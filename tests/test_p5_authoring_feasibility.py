"""Probe boundaries, syntax teaching and authentic offline decoder replay."""
from decimal import Decimal
import json
import pytest
from experiments import p5 as p
from experiments import p5_authoring_feasibility as f
from experiments.p5_oracle import author_graph
from experiments.p5_tokens import config_key, frozen_calibration
from ve import Environment, Claim
from ve_experiments.paid import PreflightError, cost


def test_documented_toy_replays_with_real_certificates():
    result = author_graph(f.TOY, f.TOY_PACKET)
    assert result['ok']
    assert result['graph']['deductions'][0]['certificates']
    env = Environment.from_dict(f.TOY_ENV)
    for source in [
        '((@pebble is marked) and (@pebble is round)) and (@pebble is inspected).\n',
        '(if (@pebble is marked), then (@pebble is round)) and (if (@pebble is round), then (@pebble is inspected)).\n',
        'for every toy x, (if (x is marked), then (x is round)).\n']:
        Claim.create(env, 'example', source)
    with pytest.raises(Exception):
        Claim.create(env, 'bad', '@pebble is marked.\n@pebble is round.\n')


def test_no_judges_scored_items_or_unbudgeted_configs():
    reqs = [f.request(i, s) for i in p.materials('dev') for s in ('author', 'repair')]
    assert len(reqs) == 24
    assert sum(cost(r.model, r.max_input_tokens, r.billed_output_cap) for r in reqs) < Decimal(3)
    for req in reqs:
        assert req.model == 'pro' and req.max_output_tokens == 4096
        assert config_key(req) in frozen_calibration()['configs']
        assert req.identity.startswith(f.REVISION+'/dev/')
        assert f.GUIDE in req.messages[-1]['content']
        assert 'acceptable_locations' not in req.messages[-1]['content']
    with pytest.raises(PreflightError): f.request(p.materials('dev')[0], 'judge')
    with pytest.raises(PreflightError): f.request(p.materials('scored')[0], 'author')


def test_retained_taxonomy_and_x_offline(tmp_path, monkeypatch):
    monkeypatch.setattr(f, 'OUT', tmp_path)
    report = f.offline_audit()
    assert report['categories'] == {
        'syntax/parse error': 24, 'undeclared or misspelled predicate': 0,
        'sort/type error': 1, 'wrong graph shape': 0,
        'missing premise so the step does not entail': 0,
        'certificate/format': 5, 'prover ResourceLimit': 0, 'other': 0}
    assert report['delivery_failures'] == 6 and report['paid_calls'] == 0
    x = report['x_decoder']
    assert len(x) == 12 and all(r['texts_unchanged'] and r['isolated_context_exact'] for r in x)
    assert sum(r['previous_wrapper_failure'] for r in x) == 9
    assert sum(bool(r['followup_error']) for r in x) == 1
    assert sum(r['historical_completed'] for r in x) == 2


def test_failed_parse_feedback_locates_claim_without_modification():
    from copy import deepcopy
    a = deepcopy(f.TOY)
    a['claims'][0]['source'] = 'pebble is marked.\n'
    text = json.dumps(a)
    result = f.replay(text, {'payload': f.TOY_PACKET})
    assert not result['ok'] and result['claim_id'] == 'given' and result['span']['line'] == 1
    assert f.category(result) == 'sort/type error'
    assert json.loads(text) == a
