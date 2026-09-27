"""Security boundary and library integration tests: no real model calls."""
import asyncio
import json
import re
import subprocess
import sys
import time

import pytest
from fastapi.testclient import TestClient
from ve_webapp.server import Settings, create_app, Quota
from ve_webapp.worker import run
from ve_webapp.examples import EXAMPLES

TOKEN = 'test-only-random-token-' + 'x' * 32


@pytest.fixture
def setup(tmp_path):
    settings = Settings(TOKEN, tmp_path, secure=False, assist=True, minute_cap=2,
                        claude_cli_version='test CLI version')
    calls = []
    async def runner(action, data, settings):
        calls.append(action)
        return run(action, data, proposer=lambda *args: {'text': json.dumps({'candidates': [
            {'ve': '@api is safe.', 'reading': '<script>alert(1)</script>'}]})})
    with TestClient(create_app(settings, runner)) as client:
        yield client, settings, calls


def login(client):
    response = client.post('/api/login', json={'token': TOKEN}, headers={'x-ve-csrf':'login'})
    assert response.status_code == 200
    return {'x-ve-csrf': response.json()['csrf']}


def test_auth_csrf_and_logout(setup):
    client, _, calls = setup
    assert client.get('/api/examples').status_code == 401
    assert client.post('/api/login', json={'token':TOKEN}).status_code == 403
    assert client.post('/api/login', json={'token':TOKEN}, headers={'x-ve-csrf':'login','origin':'https://evil.test'}).status_code == 403
    assert client.post('/api/login', json={'token':'wrong'}, headers={'x-ve-csrf':'login'}).status_code == 401
    headers = login(client)
    assert client.get('/api/examples').status_code == 200
    assert client.post('/api/check', json={'example':'policy'}).status_code == 403
    assert client.post('/api/check', json={'example':'policy'}, headers={**headers,'origin':'https://evil.test'}).status_code == 403
    assert not calls
    assert client.post('/api/logout', json={}, headers=headers).status_code == 200
    assert client.get('/api/session').status_code == 401


def test_limits_and_static(setup):
    client, _, calls = setup
    headers=login(client)
    assert client.post('/api/check', content=b'x'*32769, headers=headers).status_code == 413
    assert client.post('/api/check', content=(b'x'*10000 for _ in range(4)), headers=headers).status_code == 413
    for body in ({'example':'../../etc/passwd'}, {'example':'policy','text':7}, {'example':'policy','text':'x'*6001}, {'example':'policy','path':'/etc/passwd'}):
        assert client.post('/api/check', json=body, headers=headers).status_code == 400
    assert not calls
    assert client.get('/assets/server.py').status_code == 404
    response=client.get('/')
    assert "script-src 'self'" in response.headers['content-security-policy']
    assert response.headers['cache-control']=='no-store'


@pytest.mark.parametrize('id,expected',[('policy','certified'),('citizenship','certified'),('math','certified'),('news','countermodel')])
def test_examples(setup,id,expected):
    client,_,_=setup
    result=client.post('/api/check',json={'example':id},headers=login(client))
    assert result.status_code==200, result.text
    data=result.json()
    assert data['status']==expected
    assert data['evaluation']['value']==(id!='news')
    if expected=='certified': assert data['replay']['valid']
    else: assert data['countermodel']['complete']


def test_reader_facing_example_outputs_are_symbol_free_except_checked_fallbacks(setup):
    client, _, _ = setup
    headers = login(client)
    forbidden = re.compile(r'[@()\[\]*<=]')
    for example in EXAMPLES:
        assert not forbidden.search(example['english'])
        for text in (example['premises'] + '\n' + example['claim'], example['claim']):
            response = client.post('/api/validate', json={'example': example['id'], 'text': text}, headers=headers)
            assert response.status_code == 200, response.text
            for sentence in response.json()['natural']['sentences']:
                if sentence['form'] == 'explicit form':
                    assert sentence['fallback_reason']
                else:
                    assert sentence['form'] == 'natural'
                    assert not forbidden.search(sentence['text'])
        result = client.post('/api/check', json={'example': example['id']}, headers=headers)
        assert result.status_code == 200, result.text
        for sentence in result.json().get('countermodel_summary', []):
            assert not forbidden.search(sentence)
    response = client.post('/api/propose', json={'example':'policy','text':'The API is safe.'}, headers=headers)
    assert response.status_code == 200, response.text
    for candidate in response.json()['candidates']:
        assert candidate['natural']['sentences']
        for sentence in candidate['natural']['sentences']:
            if sentence['form'] == 'natural':
                assert not forbidden.search(sentence['text'])
            else:
                assert sentence['form'] == 'explicit form' and sentence['fallback_reason']


def test_candidate_distinguishing_worlds_have_plain_readings():
    proposals = {'candidates': [
        {'ve': '@api is safe.', 'reading': 'The API is safe.'},
        {'ve': '@api is reviewed.', 'reading': 'The API is reviewed.'},
    ]}
    result = run('propose', {'example': 'policy', 'text': 'The API is safe.'},
                 proposer=lambda *args: {'text': json.dumps(proposals)})
    assert result['comparisons'][0]['distinguishing_models']
    for model in result['comparisons'][0]['distinguishing_models']:
        assert any('It is true that' in sentence for sentence in model['reader_summary'])
        assert all(not re.search(r'[@()\[\]*<=]', sentence) for sentence in model['reader_summary'])


def test_removed_rule_and_diagnostics(setup):
    client,_,_=setup; headers=login(client)
    data=client.post('/api/check',json={'example':'policy','premises':'@api is reviewed.'},headers=headers).json()
    assert data['status']=='countermodel'
    # Production worker serializes library diagnostics, including source location.
    result=subprocess.run([sys.executable,'-m','ve_webapp.worker'],input=json.dumps({'action':'validate','data':{'example':'policy','text':'@api is .'}}),text=True,capture_output=True,timeout=10)
    error=json.loads(result.stdout)['error']
    assert error['span']['line']==1 and error['span']['column']>0


def test_mocked_assist_and_persistent_quota(setup):
    client,settings,calls=setup; headers=login(client)
    for _ in range(2):
        response=client.post('/api/propose',json={'example':'policy','text':'The API is safe.'},headers=headers)
        assert response.status_code==200, response.text
        assert response.json()['candidates'][0]['text']=='@api is safe.'
    headers=login(client)
    assert client.post('/api/propose',json={'example':'policy','text':'The API is safe.'},headers=headers).status_code==429
    with pytest.raises(Exception) as exc: Quota(settings).reserve()
    assert exc.value.status_code==429
    assert calls==['propose','propose']


def test_live_assist_controls_with_mocked_cli(tmp_path, monkeypatch):
    from ve_experiments.claude_cli import ClaudeCLI, MODELS
    monkeypatch.setenv('VE_CLAUDE_ACCOUNT_CONFIG_DIR', str(tmp_path / 'account'))
    monkeypatch.setattr('ve_webapp.server.subprocess.check_output',
                        lambda args, **kwargs: '2.1.283 (Claude Code)\n')
    settings = Settings(TOKEN, tmp_path / '.webapp-private', assist=True)
    assert (settings.state / 'claude-empty').is_dir()
    assert settings.claude_cli_version == '2.1.283 (Claude Code)'
    seen = []
    def sample(client, item_id, system, prompt, sample_index):
        seen.append(client)
        return {'text': json.dumps({'candidates': [{'ve': '@api is safe.', 'reading': 'The API is safe.'}]}),
                'input_tokens': 1, 'output_tokens': 1, 'served_model': MODELS['haiku'],
                'account_label': client.account_label, 'key': 'mocked'}
    monkeypatch.setattr(ClaudeCLI, 'sample', sample)
    config = {'state': str(settings.state), 'model': settings.model,
              'cli_version': settings.claude_cli_version,
              'account_config_dir': str(settings.account_config_dir)}
    result = run('propose', {'example': 'policy', 'text': 'The API is safe.'}, config=config)
    assert result['candidates'][0]['text'] == '@api is safe.'
    assert len(seen) == 1
    controls = seen[0].controls
    assert controls.cli_version == '2.1.283 (Claude Code)'
    assert controls.model == MODELS['haiku']
    assert controls.working_directory == str(settings.state / 'claude-empty' / 'cwd')
    assert not (settings.state / 'claude-empty' / 'cwd').exists()
    assert seen[0].ledger.name.startswith('calls-')
    assert seen[0].account_config == tmp_path / 'account'
    assert seen[0].allow_builtin_agents_md is True


def test_webapp_allows_only_cli_builtin_agents_md():
    from ve_experiments.claude_cli import EndpointError, MODELS, parse_stream
    model = MODELS['haiku']
    records = [
        {'type': 'system', 'subtype': 'init', 'model': model, 'tools': [], 'mcp_servers': [],
         'agents': [], 'skills': [], 'plugins': [
             {'name': 'agents-md', 'path': 'builtin', 'source': 'agents-md@builtin'}]},
        {'type': 'assistant', 'message': {'id': 'm1', 'model': model,
                                         'content': [{'type': 'text', 'text': 'ok'}]}},
        {'type': 'result', 'subtype': 'success', 'is_error': False, 'num_turns': 1,
         'result': 'ok', 'stop_reason': 'end_turn', 'modelUsage': {model: {}},
         'usage': {'input_tokens': 1, 'cache_creation_input_tokens': 0,
                   'cache_read_input_tokens': 0, 'output_tokens': 1}},
    ]
    raw = lambda: '\n'.join(json.dumps(record) for record in records)
    with pytest.raises(EndpointError, match='Ambient agents'):
        parse_stream(raw(), model)
    assert parse_stream(raw(), model, allow_builtin_agents_md=True)['text'] == 'ok'
    records[0]['plugins'].append({'name': 'other', 'path': '/tmp/other', 'source': 'other'})
    with pytest.raises(EndpointError, match='Ambient agents'):
        parse_stream(raw(), model, allow_builtin_agents_md=True)


def test_daily_cap_and_disabled(tmp_path):
    settings=Settings(TOKEN,tmp_path,secure=False,daily_cap=1)
    quota=Quota(settings);quota.reserve()
    import sqlite3
    with sqlite3.connect(quota.path) as db: db.execute('UPDATE calls SET at=?',(time.time()-61,))
    # Avoid crossing UTC midnight in this artificial timestamp test.
    if time.time()%86400>61:
        with pytest.raises(Exception) as exc: quota.reserve()
        assert exc.value.status_code==429
    with TestClient(create_app(settings)) as client:
        assert client.post('/api/propose',json={'example':'policy','text':'Hello.'},headers=login(client)).status_code==503


def test_secure_cookie(tmp_path):
    with TestClient(create_app(Settings(TOKEN,tmp_path)),base_url='https://testserver') as client:
        response=client.post('/api/login',json={'token':TOKEN},headers={'x-ve-csrf':'login'})
        cookie=response.headers['set-cookie']
        assert 'Secure' in cookie and 'HttpOnly' in cookie and 'SameSite=strict' in cookie
        assert 'strict-transport-security' in response.headers


def test_real_worker_without_model(tmp_path):
    with TestClient(create_app(Settings(TOKEN,tmp_path,secure=False))) as client:
        response=client.post('/api/check',json={'example':'policy'},headers=login(client))
        assert response.status_code==200, response.text
        assert response.json()['status']=='certified'


def test_assistant_does_not_repair_or_call_for_multiple_sentences():
    calls=[]
    def bad(*args):
        calls.append(args)
        return {'text':'{"candidates":[{"ve":"nonsense"}]}'}
    result=run('propose',{'example':'policy','text':'The API is safe.'},proposer=bad)
    assert result['candidates']==[] and len(calls)==1
    with pytest.raises(ValueError): run('propose',{'example':'policy','text':'The API is safe. It is reviewed.'},proposer=bad)
    assert len(calls)==1


def test_unknown_is_not_certified(monkeypatch):
    from types import SimpleNamespace
    import ve
    monkeypatch.setattr(ve,'prove_entailment',lambda *a,**kw:SimpleNamespace(certificate=None))
    monkeypatch.setattr(ve,'find_countermodel',lambda *a,**kw:SimpleNamespace(model=None))
    result=run('check',{'example':'policy'})
    assert result['status']=='unknown'
    assert 'certificate' not in result


def test_worker_timeout_kills_process_group(monkeypatch,tmp_path):
    import ve_webapp.server as server
    killed=[]
    class Process:
        pid=123456
        async def communicate(self, payload): raise asyncio.TimeoutError
        async def wait(self): return 0
    async def spawn(*args,**kwargs):
        assert kwargs['start_new_session'] is True
        assert 'VE_WEB_TOKEN' not in kwargs['env']
        return Process()
    monkeypatch.setenv('VE_WEB_TOKEN',TOKEN)
    monkeypatch.setattr(asyncio,'create_subprocess_exec',spawn)
    monkeypatch.setattr(server.os,'killpg',lambda pid,sig:killed.append(pid))
    with pytest.raises(Exception) as exc:
        asyncio.run(server.worker('check',{'example':'policy'},Settings(TOKEN,tmp_path)))
    assert exc.value.status_code==504 and killed==[123456]


def test_cli_rejects_insecure_deployment():
    for args in (['--http','--host','0.0.0.0'], ['--http','--host','127.0.0.1','--port','443'], []):
        result=subprocess.run([sys.executable,'-m','ve_webapp',*args],capture_output=True,text=True,timeout=10)
        assert result.returncode==2


def test_expired_session(setup,monkeypatch):
    client,_,_=setup
    login(client)
    now=time.time()
    monkeypatch.setattr('ve_webapp.server.time.time',lambda:now+9*3600)
    assert client.get('/api/session').status_code==401


def _command(client, headers, doc, action, args=None, request_id=None):
    return client.post(f"/api/drafts/{doc['id']}/commands", headers=headers, json={
        'revision': doc['revision'], 'request_id': request_id or f'request-{doc["revision"]:08d}',
        'action': action, 'args': args or {}})


def test_blank_document_persists_approval_across_session_and_restart(tmp_path):
    settings = Settings(TOKEN, tmp_path, secure=False)
    with TestClient(create_app(settings)) as client:
        headers = login(client)
        assert client.post('/api/drafts', json={'example': []}, headers=headers).status_code == 400
        doc = client.post('/api/drafts', json={}, headers=headers).json()
        assert doc['units'] == [] and doc['revision'] == 0
        for action, args in [('save', {'source': 'Api is safe.'}), ('analyze', {}),
                             ('approve', {'wording': 'Api is safe.'})]:
            response = _command(client, headers, doc, action, args)
            assert response.status_code == 200, response.text
            doc = response.json()
        assert doc['units'][0]['state'] == 'approved'
        assert doc['units'][0]['approval']
        assert client.get(f"/api/drafts/{doc['id']}").json()['units'][0]['state'] == 'approved'
    with TestClient(create_app(settings)) as client:
        login(client)
        restored = client.get(f"/api/drafts/{doc['id']}")
        assert restored.status_code == 200
        assert restored.json()['units'][0]['approval'] == doc['units'][0]['approval']


def test_draft_security_stale_idempotency_and_token_isolation(tmp_path):
    settings = Settings(TOKEN, tmp_path, secure=False)
    with TestClient(create_app(settings)) as client:
        headers = login(client)
        doc = client.post('/api/drafts', json={}, headers=headers).json()
        path = f"/api/drafts/{doc['id']}/commands"
        body = {'revision': 0, 'request_id': 'same-request-1', 'action': 'save',
                'args': {'source': 'Api is safe.'}}
        assert client.post(path, json=body).status_code == 403
        assert client.post(path, json={**body, 'action': []}, headers=headers).status_code == 400
        assert client.post(path, json=body, headers={**headers, 'origin': 'https://evil.test'}).status_code == 403
        first = client.post(path, json=body, headers=headers)
        assert first.status_code == 200
        assert client.post(path, json=body, headers=headers).json()['revision'] == 1
        stale = {**body, 'request_id': 'other-request-2', 'args': {'source': 'Api is reviewed.'}}
        assert client.post(path, json=stale, headers=headers).status_code == 409
        assert client.get('/api/drafts/../../etc/passwd').status_code in (404, 400)
    with TestClient(create_app(Settings('other-token-' + 'y' * 40, tmp_path, secure=False))) as other:
        login_response = other.post('/api/login', json={'token': 'other-token-' + 'y' * 40},
                                    headers={'x-ve-csrf': 'login'})
        assert login_response.status_code == 200
        assert other.get(f"/api/drafts/{doc['id']}").status_code == 404


def test_checked_cards_recovery_and_export_tampering(setup):
    client, _, _ = setup
    headers = login(client)
    doc = client.post('/api/drafts', json={'example': 'scope'}, headers=headers).json()
    doc = _command(client, headers, doc, 'save', {'source': 'Every engineer checks a server.'}).json()
    doc = _command(client, headers, doc, 'analyze').json()
    unit = doc['units'][0]
    assert unit['state'] == 'needs_word'
    assert len(unit['cards']) == 1
    card = unit['cards'][0]
    assert card['values'][0] != card['values'][1]
    assert any('checks' in line for line in card['situation_text'])
    assert all(not re.search(r'[@()\[\]*<=]', text) for text in card['paraphrases'] + card['situation_text'])
    doc = _command(client, headers, doc, 'reply', {'text': card['paraphrases'][0],
        'rejected': [{'meaning_id': card['meaning_ids'][1], 'reason': 'Different intent.'}]}).json()
    doc = _command(client, headers, doc, 'analyze').json()
    assert doc['units'][0]['state'] == 'ready'
    doc = _command(client, headers, doc, 'approve', {'wording': card['paraphrases'][0]}).json()
    assert doc['units'][0]['state'] == 'approved'
    exported = client.get(f"/api/drafts/{doc['id']}/export").json()
    assert exported['authorship'] == 'The export is unsigned. The export does not prove the authorship.'
    imported = client.post('/api/drafts/import', json=exported, headers=headers)
    assert imported.status_code == 200, imported.text
    assert imported.json()['units'][0]['state'] == 'approved'
    exported['ledger']['events'][-1]['unit_snapshot']['source'] = 'tampered'
    assert client.post('/api/drafts/import', json=exported, headers=headers).status_code == 400


def test_recovery_outage_cancel_undo_and_unresolved(setup):
    client, settings, _ = setup
    settings.assist = False
    headers = login(client)
    doc = client.post('/api/drafts', json={}, headers=headers).json()
    doc = _command(client, headers, doc, 'save', {'source': 'A strange new assertion.'}).json()
    doc = _command(client, headers, doc, 'analyze').json()
    assert doc['units'][0]['state'] in ('needs_word', 'needs_repair')
    doc = _command(client, headers, doc, 'cancel').json()
    assert doc['units'][0]['state'] == 'draft'
    doc = _command(client, headers, doc, 'analyze').json()
    doc = _command(client, headers, doc, 'unresolved', {'reason': 'No faithful reading yet.'}).json()
    assert doc['units'][0]['state'] == 'unresolved'
    assert doc['units'][0]['reason'] == 'No faithful reading yet.'
    doc = _command(client, headers, doc, 'undo', {'target_revision': 1}).json()
    assert doc['units'][0]['state'] == 'draft'
    doc = _command(client, headers, doc, 'analyze').json()
    result = client.post(f"/api/drafts/{doc['id']}/assist", headers=headers,
                         json={'revision': doc['revision'], 'request_id': 'assist-123456'})
    assert result.status_code == 200, result.text
    assert result.json()['units'][0]['state'] == 'exhausted'
    assert 'proposer unavailable' in result.json()['units'][0]['reason']


def test_glossary_and_rules_checked_in_english(setup):
    client, _, _ = setup
    headers = login(client)
    doc = client.post('/api/drafts', json={}, headers=headers).json()
    doc = _command(client, headers, doc, 'save', {'source': 'Api is reliable.'}).json()
    for word in ('reliable', 'dependable'):
        response = _command(client, headers, doc, 'define', {'word': word, 'kind': 'property',
                    'sorts': ['service'], 'description': 'Confirmed property.',
                    'positive_example': 'Api has this property.',
                    'negative_example': 'Web lacks this property.'})
        assert response.status_code == 200, response.text
        doc = response.json()
    response = _command(client, headers, doc, 'glossary',
        {'sentence': 'In this document, reliable and dependable mean the same thing.'})
    assert response.status_code == 200, response.text
    assert response.json()['environment']['vocabulary']['predicates']['dependable']['defined']
    rules = client.get('/api/rules').json()
    assert rules['result']['status'] == 'clear'
    changed = rules['text'].replace(' (exception to rule 1)', '')
    conflict = client.post('/api/rules', json={'text': changed}, headers=headers)
    assert conflict.status_code == 200, conflict.text
    assert conflict.json()['status'] == 'conflict'
    assert 'urgent act' in conflict.json()['explanation']


def test_document_status_templates_and_unformalised_force(setup):
    client, _, _ = setup
    headers = login(client)
    doc = client.post('/api/drafts', json={}, headers=headers).json()
    doc = _command(client, headers, doc, 'save', {'source': 'An unknown statement.'}).json()
    doc = _command(client, headers, doc, 'analyze').json()
    assert doc['document_units'][0]['status'] == doc['units'][0]['state']
    templates = doc['units'][0]['templates']
    assert templates and all(not re.search(r'[@()\[\]*<=]', text) for text in templates)
    for source in ('The API is deployed. Some service is reviewed. It is safe.',
                   'They are safe.', 'Her manager is safe.',
                   'Alice reviews the API; Bob checks the service; Carol does too.',
                   'Take reasonable precautions.', 'The patch caused recovery.',
                   'The service is probably safe.'):
        doc = client.post('/api/drafts', json={}, headers=headers).json()
        doc = _command(client, headers, doc, 'save', {'source': source}).json()
        doc = _command(client, headers, doc, 'analyze').json()
        assert doc['units'][0]['state'] not in ('ready', 'approved'), source
        assert _command(client, headers, doc, 'approve', {'wording': 'Api is safe.'}).status_code == 400


def test_relation_direction_and_unconfirmed_examples_rejected(setup):
    client, _, _ = setup
    headers = login(client)
    doc = client.post('/api/drafts', json={}, headers=headers).json()
    doc = _command(client, headers, doc, 'save', {'source': 'Api links web.'}).json()
    args = {'word': 'links', 'kind': 'relation', 'sorts': ['service', 'service'],
            'positive_example': 'Api links web.', 'negative_example': 'Web does not link api.'}
    assert _command(client, headers, doc, 'define', {**args, 'direction': []}).status_code == 400
    assert _command(client, headers, doc, 'define', {**args, 'negative_example': '',
                                                    'direction': 'first_to_second'}).status_code == 400
    response = _command(client, headers, doc, 'define', {**args, 'direction': 'second_to_first'})
    assert response.status_code == 200, response.text
    assert response.json()['environment']['vocabulary']['predicates']['links']['verbalisation'] == '{1} links {0}'


def test_inflight_assistant_result_is_discarded_after_cancel(tmp_path):
    import threading
    started, release = threading.Event(), threading.Event()
    async def slow_runner(action, data, settings):
        started.set()
        await asyncio.to_thread(release.wait, 5)
        return {'candidates': [{'natural': {'sentences': [{'form': 'natural', 'text': 'Api is safe'}]}}]}
    settings = Settings(TOKEN, tmp_path, secure=False, assist=True,
                        claude_cli_version='test CLI version')
    with TestClient(create_app(settings, slow_runner)) as client:
        headers = login(client)
        doc = client.post('/api/drafts', json={}, headers=headers).json()
        doc = _command(client, headers, doc, 'save', {'source': 'Unknown statement.'}).json()
        doc = _command(client, headers, doc, 'analyze').json()
        answer = []
        thread = threading.Thread(target=lambda: answer.append(client.post(
            f"/api/drafts/{doc['id']}/assist", headers=headers,
            json={'revision': doc['revision'], 'request_id': 'slow-assist-1'})))
        thread.start()
        try:
            assert started.wait(3)
            current = client.get(f"/api/drafts/{doc['id']}").json()
            assert current['history'][-1]['action'] == 'proposer_reserved'
            cancelled = _command(client, headers, current, 'cancel')
            assert cancelled.status_code == 200, cancelled.text
        finally:
            release.set()
            thread.join(6)
        assert not thread.is_alive()
        assert answer[0].json()['status'] == 'stale'
        restored = client.get(f"/api/drafts/{doc['id']}").json()
        assert restored['units'][0]['state'] == 'draft'
        assert not restored['units'][0]['suggestions']


def test_persistent_ledger_and_import_tampering_are_rejected(tmp_path):
    import sqlite3
    settings = Settings(TOKEN, tmp_path, secure=False)
    with TestClient(create_app(settings)) as client:
        headers = login(client)
        doc = client.post('/api/drafts', json={}, headers=headers).json()
        doc = _command(client, headers, doc, 'save', {'source': 'Api is safe.'}).json()
        doc = _command(client, headers, doc, 'analyze').json()
        doc = _command(client, headers, doc, 'approve', {'wording': 'Api is safe.'}).json()
        exported = client.get(f"/api/drafts/{doc['id']}/export").json()
        for field, altered in [('source', 'Forged source.'), ('anchor', {'start': 9, 'end': 10}),
                               ('meaning_id', 'forged-meaning-id'), ('approval', None)]:
            bad = json.loads(json.dumps(exported))
            bad['ledger']['events'][-1]['unit_snapshot'][field] = altered
            assert client.post('/api/drafts/import', json=bad, headers=headers).status_code == 400
        bad = json.loads(json.dumps(exported))
        bad['document']['environment']['vocabulary']['predicates']['safe']['description'] = 'Forged.'
        assert client.post('/api/drafts/import', json=bad, headers=headers).status_code == 400
        db = settings.state / 'drafts.sqlite3'
        with sqlite3.connect(db) as connection:
            connection.execute('UPDATE drafts SET ledger=? WHERE id=?', ('{}', doc['id']))
        assert client.get(f"/api/drafts/{doc['id']}").status_code == 404


def test_translation_preserves_alternatives_without_cited_narrowing(setup):
    client, _, _ = setup
    headers = login(client)
    doc = client.post('/api/drafts', json={'example': 'scope'}, headers=headers).json()
    doc = _command(client, headers, doc, 'save', {'source': 'Every engineer checks a server.',
                                                   'mode': 'translation'}).json()
    doc = _command(client, headers, doc, 'analyze').json()
    unit = doc['units'][0]
    assert unit['mode'] == 'translation'
    assert len(unit['readings']) == 2
    assert unit['cards'] and unit['cards'][0]['values'][0] != unit['cards'][0]['values'][1]
    for wording in unit['cards'][0]['paraphrases']:
        assert _command(client, headers, doc, 'approve', {'wording': wording}).status_code == 400
    assert _command(client, headers, doc, 'save', {'source': unit['source'],
                                                  'mode': 'authoring'}).status_code == 400
    exported = client.get(f"/api/drafts/{doc['id']}/export").json()
    imported = client.post('/api/drafts/import', json=exported, headers=headers)
    assert imported.status_code == 200, imported.text
    assert len(imported.json()['units'][0]['readings']) == 2
    assert imported.json()['units'][0]['approval'] is None
