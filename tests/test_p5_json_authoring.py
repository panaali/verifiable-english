"""Structured authoring conversion, no answer supply, and spend boundaries."""
from copy import deepcopy
from decimal import Decimal
import json
import subprocess
import sys
import pytest
from experiments import p5 as p
from experiments import p5_json_authoring as j
from experiments.p5_oracle import author_graph
from ve_experiments.paid import PreflightError, cost


def toy():
    packet = {'glossary': [{'term': 'marked', 'sense': 'marked: mark present (R01)'},
                           {'term': 'round', 'sense': 'round: circular shape (R02)'}],
              'premises': [{'id': 'given', 'text': 'unit1 is marked.'},
                           {'id': 'rule', 'text': 'If unit1 is marked then unit1 is round.'}],
              'nodes': [{'id': 'result', 'parents': ['given'], 'text': 'unit1 is round.'}],
              'records': [{'id': 'record', 'text': 'unrelated toy'}], 'root': 'result'}
    raw = {'expressions': [{'op': 'unary', 'predicate': 'p01', 'term': {'const': 'unit1'}},
                           {'op': 'unary', 'predicate': 'p02', 'term': {'const': 'unit1'}},
                           {'op': 'implies', 'left': 0, 'right': 1}],
           'claims': [{'id': n, 'formula': index, 'records': ['record']}
                      for n,index in [('given',0), ('rule',2), ('result',1)]],
           'support': {'result': ['rule']}, 'root': 'result'}
    return packet, raw


def test_real_import_cli_and_certificate_replay(tmp_path):
    packet, raw = toy()
    original = deepcopy(raw)
    artifact, docs = j.convert(raw, packet)
    assert raw == original
    assert author_graph(artifact, packet)['ok']
    (tmp_path/'env.json').write_text(json.dumps(artifact['environment']))
    for claim in artifact['claims']:
        result = subprocess.run([sys.executable, '-m', 've', 'import-fol', '--env',
                                 str(tmp_path/'env.json'), '-'], input=json.dumps(docs[claim['id']]),
                                text=True, capture_output=True, check=True)
        assert result.stdout == claim['source']


def test_missing_support_is_located_and_never_auto_repaired():
    packet, raw = toy()
    raw['support']['result'] = []
    result = j.replay(json.dumps(raw), {'payload': packet})
    assert not result['ok']
    assert result['diagnostics'][0]['claim_id'] == 'result'
    assert result['diagnostics'][0]['path'] == '/support/result'
    assert result['canonical_artifact']['edges'][0]['premises'] == ['given']
    assert 'canonical_artifact' not in j.feedback(result)


@pytest.mark.parametrize('mutation', ['predicate','constant','forward','duplicate','root','parent'])
def test_invalid_symbols_refs_coverage_and_edges_rejected(mutation):
    packet, raw = toy()
    if mutation == 'predicate': raw['expressions'][0]['predicate'] = 'invented'
    if mutation == 'constant': raw['expressions'][0]['term']['const'] = 'unit9'
    if mutation == 'forward': raw['expressions'][2]['left'] = 2
    if mutation == 'duplicate': raw['claims'][2]['id'] = 'given'
    if mutation == 'root': raw['root'] = 'given'
    if mutation == 'parent': raw['support']['result'] = ['result']
    result = j.replay(json.dumps(raw), {'payload': packet})
    assert not result['ok'] and result['path']


def test_ast_expansion_is_bounded():
    packet, raw = toy()
    for i in range(3, 30):
        raw['expressions'].append({'op':'and','left':i-1,'right':i-1})
    with pytest.raises(j.InterfaceError, match='node/depth'):
        j.convert(raw, packet)


def test_request_scope_schema_and_whole_probe_cap():
    items = p.materials('dev')
    requests = [j.request(i,s) for i in items for s in ('author','repair')]
    assert len(requests) == 24
    assert sum(cost(r.model,r.max_input_tokens,r.billed_output_cap) for r in requests) <= j.cap_remaining()
    for req in requests:
        _, cfg = j.count_wire(req)
        assert cfg.generation_config.response_schema is not None
        assert 'maxItems' not in json.dumps(req.response_schema)
        assert cfg.generation_config.response_mime_type == 'application/json'
        assert req.metadata['require_response_schema']
        assert req.identity.startswith(j.REVISION + '/dev/')
        assert 'strict VE' not in req.messages[0]['content']
        assert 'acceptable_locations' not in req.messages[-1]['content']
    with pytest.raises(PreflightError): j.request(items[0], 'judge')
    with pytest.raises(PreflightError): j.request(p.materials('scored')[0], 'author')
    with pytest.raises(PreflightError): j.request(items[0], 'repair', [{'item_id':'another'}])


def test_public_only_schema_no_per_use_answers():
    item = p.materials('dev')[0]
    changed = deepcopy(item)
    changed.update(label='approve', reference_graph='secret', variant='secret')
    assert j.request(changed,'author') == j.request(item,'author')
    packet = changed['payload']
    before = j.schema(packet)
    # Permuting paragraphs' English content cannot generate formulas or answers.
    packet['nodes'][0]['text'], packet['nodes'][1]['text'] = packet['nodes'][1]['text'], packet['nodes'][0]['text']
    assert j.schema(packet) == before


def test_wire_schema_only_drops_length_bounds_and_local_bounds_still_enforced():
    packet, raw = toy()
    assert j.wire_schema(packet) != j.schema(packet)
    assert 'maxItems' not in json.dumps(j.wire_schema(packet))
    raw['claims'].pop()  # wire schema would admit it; local exact coverage must not
    result = j.replay(json.dumps(raw), {'payload': packet})
    assert not result['ok'] and result['path'] == '/claims'
