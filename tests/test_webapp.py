"""Security boundary and library integration tests: no real model calls."""
import asyncio
import json
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
