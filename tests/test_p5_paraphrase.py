"""Paraphrase validation and durable correction attempts; strictly offline."""
from copy import deepcopy
from dataclasses import replace
import json

import pytest

from experiments import p5
from experiments.p5_materials import archive, read, write_json
from experiments.p5_paraphrase import validate_reply
from ve_experiments import paid


@pytest.fixture
def dossier():
    return read(p5.HERE / 'materials/dossiers.jsonl.gz')[0]


def response(dossier):
    return {'texts': {n['id']: n['text'] for n in dossier['nodes']}}


@pytest.mark.parametrize('fenced', [False, True])
def test_strict_parse_and_original_step_order(dossier, fenced):
    row = response(dossier)
    row['texts'] = dict(reversed(list(row['texts'].items())))
    text = json.dumps(row)
    if fenced:
        text = ' \n```json\n' + text + '\n```\n '
    texts, error = validate_reply(text, dossier)
    assert error is None
    assert list(texts) == [n['id'] for n in dossier['nodes']]


@pytest.mark.parametrize('value', [None, '', 'not JSON', '[]', 'null', '{"texts": []}',
                                  '{"texts": {}}', '{"texts": {}, "extra": 1}'])
def test_malformed_reply_is_named_failure(dossier, value):
    texts, error = validate_reply(value, dossier)
    assert texts is None and ('parse_failure' in error or 'schema_failure' in error)


@pytest.mark.parametrize('value', [None, 1, [], {}, '', ' \n '])
def test_text_values_are_nonempty_strings(dossier, value):
    row = response(dossier)
    row['texts'][dossier['nodes'][0]['id']] = value
    assert 'schema_failure' in validate_reply(json.dumps(row), dossier)[1]


def test_duplicate_and_missing_extra_keys_rejected(dossier):
    row = response(dossier)
    text = json.dumps(row)
    assert 'parse_failure' in validate_reply(text[:-1] + ',"texts":' + json.dumps(row['texts']) + '}', dossier)[1]
    key = dossier['nodes'][0]['id']
    assert 'parse_failure' in validate_reply(text.replace('"texts": {', '"texts": {' + json.dumps(key) + ': "duplicate",', 1), dossier)[1]
    row['texts']['n99'] = row['texts'].pop(key)
    assert 'schema_failure' in validate_reply(json.dumps(row), dossier)[1]


@pytest.mark.parametrize('prose, violation', [
    ('unit2 is free (space available).', 'parenthetical glossary sense'),
    ('unit2 is free (FREE: Space   Available).', 'parenthetical glossary sense'),
    ('unit2 is free ((space available)).', 'parenthetical glossary sense'),
    ('By n03, unit2 is free.', 'node/rule ID'),
    ('By [N99], unit2 is free.', 'node/rule ID'),
    ('Using r06, unit2 is free.', 'node/rule ID'),
    ('Using R06, unit2 is free.', 'node/rule ID'),
])
def test_prose_leaks_rejected(dossier, prose, violation):
    row = response(dossier)
    row['texts'][dossier['nodes'][0]['id']] = prose
    texts, error = validate_reply(json.dumps(row), dossier)
    assert texts is None and violation in error


def test_glossary_phrase_outside_parentheses_and_unit_ids_allowed(dossier):
    row = response(dossier)
    row['texts'][dossier['nodes'][0]['id']] = 'Because unit2 has space available, unit2 is free.'
    assert validate_reply(json.dumps(row), dossier)[1] is None


def test_paraphrase_prompt_is_isolated_from_judge_instructions(dossier):
    req = p5.request({'id': dossier['id'], 'split': 'materials', 'payload': dossier}, 'shared', 'paraphrase')
    system = req.messages[0]['content']
    assert 'No parenthetical glosses or sense labels' in system
    assert 'Keep every step in the same given topological order' in system
    assert 'State premises by content' in system
    assert 'Cite at most two node IDs' not in system
    assert 'Separate glossary:\n' + paid.packed(dossier['glossary']) in req.messages[1]['content']


@pytest.fixture
def stage(tmp_path, monkeypatch):
    dossiers = read(p5.HERE / 'materials/dossiers.jsonl.gz')[:3]
    labels = p5.labels(False)
    monkeypatch.setattr(p5, 'HERE', tmp_path)
    monkeypatch.setattr(p5, 'verify_freeze', lambda **_: {'manifest_sha256': 'frozen'})
    monkeypatch.setattr(p5, 'labels', lambda _: labels)
    monkeypatch.setattr(p5, 'native_counter', lambda: None)
    archive(tmp_path / 'materials/dossiers.jsonl.gz', dossiers)
    write_json(tmp_path / 'checks/provider-preflight.json', {
        'freeze_sha256': 'frozen', 'models': {'replication': {'passed': True}}})
    return dossiers, p5.ledger('.17')


def reply(text):
    return paid.PaidReply(text, 100, 10, 0, 0, 'revision', {'provider': 'DeepInfra'}, {})


def seed_completed(book, dossiers, bad_second=False):
    book.reserve_block('shared-paraphrase', str(84 * paid.cost('replication', *p5.STAGES['paraphrase'])))
    for index, dossier in enumerate(dossiers[:2]):
        req = p5.request({'id': dossier['id'], 'split': 'materials', 'payload': dossier}, 'shared', 'paraphrase')
        req = replace(req, messages=[{'role': 'system', 'content': 'old paraphrase prompt'}, req.messages[1]],
                      metadata={**req.metadata, 'block_id': 'shared-paraphrase'})
        row = response(dossier)
        if bad_second and index == 1:
            sense = dossier['glossary'][0]['sense'].split(': ', 1)[1].split(' (R', 1)[0]
            row['texts'][dossier['nodes'][0]['id']] += ' (' + sense + ')'
        book.reserve(req)
        book.complete(req, reply('```json\n' + json.dumps(row) + '\n```'))


def test_two_old_completions_revalidated_not_rebought(stage, monkeypatch):
    dossiers, book = stage
    seed_completed(book, dossiers)
    original = book.path.read_bytes()
    calls = []
    def respond(req):
        calls.append(req)
        return reply(json.dumps(response(dossiers[2])))
    monkeypatch.setattr(p5, 'OpenRouterBackend', lambda _: paid.OfflineBackend(respond))
    result = p5.paraphrase('.17')
    assert result['accepted'] == 3 and result['paraphrase_failed'] == 0
    assert len(calls) == 1 and calls[0].metadata['item_id'] == dossiers[2]['id']
    assert book.path.read_bytes().startswith(original)
    outputs = read(p5.HERE / 'materials/paraphrases.jsonl.gz')
    reservations = {r['identity']: r for r in read(book.path) if r['event'] == 'reserve'}
    for row in outputs:
        provenance = row['provenance']
        assert provenance['request_sha256'] == paid.digest(reservations[provenance['identity']]['messages'])
    assert p5.paraphrase('.17') == result
    assert len(calls) == 1


@pytest.mark.parametrize('retry_valid', [False, True])
def test_invalid_cached_reply_gets_one_named_correction_then_exclusion(stage, monkeypatch, retry_valid):
    dossiers, book = stage
    seed_completed(book, dossiers, bad_second=True)
    calls = []
    def respond(req):
        calls.append(req)
        dossier = next(d for d in dossiers if d['id'] == req.metadata['item_id'])
        row = response(dossier)
        if dossier == dossiers[1]:
            assert req.metadata['turn'] == 1
            assert 'parenthetical glossary sense' in req.messages[1]['content']
            assert dossiers[1]['glossary'][0]['sense'].split(': ', 1)[1].split(' (R', 1)[0] in req.messages[1]['content']
            if not retry_valid:
                row['texts'][dossier['nodes'][0]['id']] += ' by r00'
        return reply(json.dumps(row))
    monkeypatch.setattr(p5, 'OpenRouterBackend', lambda _: paid.OfflineBackend(respond))
    result = p5.paraphrase('.17')
    assert result['paraphrase_failed'] == int(not retry_valid)
    assert result['accepted'] == 2 + int(retry_valid)
    assert [r.metadata['turn'] for r in calls] == [1, 0]
    outputs = read(p5.HERE / 'materials/paraphrases.jsonl.gz')
    assert len(outputs[1]['provenance']['attempts']) == 2
    if not retry_valid:
        assert outputs[1]['status'] == 'paraphrase-failed' and outputs[1]['excluded']
        assert 'argument' not in outputs[1]
        assert dossiers[1]['id'] not in {i['id'] for i in p5.materials()}
        status = json.loads((p5.HERE / 'runs/study/paraphrase-status.json').read_text())
        assert status['paraphrase_failed'] == 1 and status['excluded_ids'] == [dossiers[1]['id']]
    assert p5.paraphrase('.17') == result
    assert len(calls) == 2


def test_interrupt_after_paid_correction_reuses_both_attempts(stage, monkeypatch):
    dossiers, book = stage
    seed_completed(book, dossiers, bad_second=True)
    calls = []
    def respond(req):
        calls.append(req)
        if req.metadata['item_id'] == dossiers[2]['id']:
            raise KeyboardInterrupt()
        return reply(json.dumps(response(dossiers[1])))
    monkeypatch.setattr(p5, 'OpenRouterBackend', lambda _: paid.OfflineBackend(respond))
    # Interrupt locally before the next reservation, avoiding an unknown billing hold.
    original_call = paid.PaidClient.call
    def call(client, req):
        if req.metadata['item_id'] == dossiers[2]['id']:
            raise KeyboardInterrupt()
        return original_call(client, req)
    monkeypatch.setattr(paid.PaidClient, 'call', call)
    with pytest.raises(KeyboardInterrupt):
        p5.paraphrase('.17')
    assert len(read(p5.HERE / 'materials/paraphrases.jsonl.gz')) == 2
    assert len(calls) == 1
    monkeypatch.setattr(paid.PaidClient, 'call', original_call)
    monkeypatch.setattr(p5, 'OpenRouterBackend', lambda _: paid.OfflineBackend(lambda req: reply(json.dumps(response(dossiers[2])))))
    assert p5.paraphrase('.17')['accepted'] == 3
    assert len([r for r in read(book.path) if r['event'] == 'complete']) == 4


def test_cached_request_cannot_cross_dossier_contract(stage):
    dossiers, book = stage
    seed_completed(book, dossiers)
    dossier = deepcopy(dossiers[0])
    dossier['argument'] += ' changed'
    req = p5.request({'id': dossier['id'], 'split': 'materials', 'payload': dossier}, 'shared', 'paraphrase')
    with pytest.raises(paid.PreflightError, match='dossier or request contract changed'):
        p5.retained_paraphrase_request(book, req)


def test_resume_freeze_allows_only_paraphrase_outputs(tmp_path, monkeypatch):
    monkeypatch.setattr(p5, 'HERE', tmp_path)
    monkeypatch.setattr(p5, 'ROOT', tmp_path)
    files = ['materials/dossiers.jsonl.gz', 'materials/paraphrases.jsonl.gz',
             'materials/dev.jsonl.gz', 'materials/scored.jsonl.gz', 'implementation.py']
    for name in files:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('frozen')
    write_json(tmp_path / 'freeze.json', {
        'hashes': {name: p5.sha(tmp_path / name) for name in files},
        'ceilings': {'within_cap': True}})
    for name in files[1:4]:
        (tmp_path / name).write_text('checkpoint')
    assert p5.verify_freeze(paraphrase_progress=True)
    with pytest.raises(paid.PreflightError, match='freeze changed'):
        p5.verify_freeze()  # Scoring must still refreeze and satisfy every gate.
    for name in (files[0], files[-1]):
        (tmp_path / name).write_text('changed')
        with pytest.raises(paid.PreflightError, match='freeze changed'):
            p5.verify_freeze(paraphrase_progress=True)
        (tmp_path / name).write_text('frozen')


def test_validation_covers_every_glossary_phrase():
    for dossier in read(p5.HERE / 'materials/dossiers.jsonl.gz'):
        row = response(dossier)
        first = dossier['nodes'][0]['id']
        for entry in dossier['glossary']:
            phrase = entry['sense'].split(': ', 1)[1].split(' (R', 1)[0]
            row['texts'][first] = 'The result holds (' + phrase.upper() + ').'
            assert 'parenthetical glossary sense' in validate_reply(json.dumps(row), dossier)[1]
