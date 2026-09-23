"""Narrow replacement identities, immutable L/S retention, and no-network replay."""
import json
from decimal import Decimal
from types import SimpleNamespace

from experiments import p5 as p, p5_dev_revision as revision
from experiments.p5_budget import matched_charges
from experiments.p5_dev_dry_run import artifact, dry_run
from experiments.p5_preflight import explanations
from experiments.p5_materials import write_json
from ve_experiments.paid import Ledger, packed, digest
from ve import Environment, parse


def test_complete_offline_protocols_and_checker_replay():
    result = dry_run()
    assert result['passed'] and result['paid_calls'] == 0
    assert sum(r.get('isolated_answers', 0) for r in result['results']) == 36
    assert sum(r.get('adaptive_answers', 0) for r in result['results']) == 12
    assert sum(r.get('author_replay', 0)+r.get('repair_replay', 0)+r.get('defender_replay', 0)
               for r in result['results']) == 36
    env = Environment.from_dict(revision.ENVIRONMENT_EXAMPLE)
    parse(env, '@sample is marked.\n')
    parse(env, 'for every thing x, (if (x is marked), then (x is marked)).\n')


def test_actual_ve_repair_branch_replays_valid_replacement():
    item = p.materials('dev')[0]
    roles = []
    def call(req):
        role = req.metadata['role']; roles.append(role)
        value = artifact(item)
        if role == 'author': value['environment'] = 'invalid environment string'
        if role == 'critic': value = {'queries': [], 'splits': []}
        if role == 'judge': value = {'verdict':'unknown','issue_type':'unknown','locations':[], 'explanation':'synthetic'}
        return SimpleNamespace(text=packed(value))
    client = SimpleNamespace(call=call)
    events = []
    row = p.execute(item, 'VE', client, {'pro':client}, local_events=events)[0]
    assert roles == ['author','repair','critic','defender','judge']
    assert [r['ok'] for r in events] == [False, True, True]
    assert not row['author_failure'] and not row['protocol_error'] and not row['unresolved']


def test_new_identities_do_not_reuse_any_old_x_ve_stage():
    revision.verify_retained()
    old = {r.get('identity') for r in p.read(p.HERE/'runs/study/costs.jsonl')
           if not r.get('identity','').startswith('study-v10/')}
    for item in p.materials('dev'):
        for arm in revision.RERUN_ARMS:
            for stage in p.stage_list(arm):
                for judge in p.SCENARIOS['dual_judge'] if stage=='judge' else ('pro',):
                    req = p.request(item, arm, stage, judge=judge)
                    assert req.identity.startswith('study-v10/dev/') and req.identity not in old
        for arm in revision.RETAINED_ARMS:
            assert p.request(item,arm,'lone' if arm=='L' else 'judge').identity in old
    rows = [r for r in revision.trials('dev') if r['condition'] in revision.RETAINED_ARMS]
    assert len(rows)==48 and {r['condition'] for r in rows}=={'L','S'}


def test_superseded_costs_still_spent_but_not_replacement_reasoning():
    rows = []
    for prefix in ('study-v9','study-v10'):
        identity = prefix+'/dev/item/VE/pro/author/0'
        rows += [{'event':'reserve','identity':identity,'ceiling_usd':'.1','model':'pro',
                  'metadata':{'item_id':'item','arm':'VE','role':'author'}},
                 {'event':'complete','identity':identity,'cost_usd':'.03','model':'pro','revision':'offline'}]
    assert matched_charges(rows)[1]['item','VE'] == Decimal('.03')
    assert Ledger.state(rows)[1] == Decimal('.06')


def test_export_only_final_judgments_with_arm_and_judge_blinded(tmp_path, monkeypatch):
    retained = [r for r in revision.trials('dev') if r['condition'] in revision.RETAINED_ARMS]
    monkeypatch.setattr(revision, 'trials', lambda split:retained)
    out = tmp_path/'ratings.json'
    result = explanations('dev', export=out)
    assert result['packets'] == 48
    manifest = json.loads(out.read_text())
    exported = [json.loads((out.parent/path).read_text())[0]
                for assignment in manifest['assignments'] for path in assignment]
    rows = revision.trials('dev')
    keys = {digest({k:r[k] for k in ('item_id','condition','judge','answer')}) for r in rows}
    assert {r['response_sha256'] for r in exported} == keys
    assert all(set(r)=={'response_sha256','item_id','packet','answer','rater_id','source_grounded',
                       'reason','protocol_recognized','source_fidelity','event'} for r in exported)
    assert all(not r['rater_id'] and r['source_grounded'] is None for r in exported)


def test_dev_dispatch_excludes_retained_arms(tmp_path, monkeypatch):
    items = p.materials('dev')
    retained = p.read(p.run_path('dev','trials.jsonl'))
    monkeypatch.setattr(p, 'HERE', tmp_path)
    for row in retained: p.append(p.run_path('dev','trials.jsonl'), row)
    monkeypatch.setattr(p,'scheduled_materials',lambda split:items)
    monkeypatch.setattr(p,'labels',lambda:[])
    f = {'scenario':'dual_judge','manifest_sha256':'offline'}
    monkeypatch.setattr(p,'require_gates',lambda scored:f)
    monkeypatch.setattr(p,'verify_freeze',lambda:f)
    monkeypatch.setattr(p,'infrastructure_state',lambda book:({},{}))
    reserved = []
    book = SimpleNamespace(allowance=lambda *a:None,
        reserve_block=lambda *a,**kw:reserved.append(a), release_block=lambda *a:None)
    monkeypatch.setattr(p,'ledger',lambda cap:book)
    monkeypatch.setattr(p,'VertexBackend',lambda:None)
    monkeypatch.setattr(p,'OpenRouterBackend',lambda x:None)
    monkeypatch.setattr(p,'native_counter',lambda:None)
    monkeypatch.setattr(p,'PaidClient',lambda *a,**kw:SimpleNamespace(close=lambda:None))
    dispatched = []
    def execute(item,arm,*a,**kw):
        dispatched.append((item['id'],arm))
        return [{'item_id':item['id'],'condition':arm,'judge':j} for j in ('pro','replication')]
    monkeypatch.setattr(p,'execute',execute)
    def analyze(rows,*a,**kw):
        assert len(rows)==96 and len({(r['item_id'],r['condition'],r['judge']) for r in rows})==96
        assert [r for r in rows if r['condition'] in revision.RETAINED_ARMS]==[
            r for r in retained if r['condition'] in revision.RETAINED_ARMS]
        return {'missing':0}
    monkeypatch.setattr(p,'analyze',analyze)
    monkeypatch.setattr(p,'contract_report',lambda rows,n,plan:{'assigned':n*len(plan)})
    result = p.run('dev',40,resume=True)
    assert len(dispatched)==24 and {a for _,a in dispatched}=={'X','VE'}
    assert reserved[0][0]=='study-v10/dual_judge/dev'
    assert result['assigned']==96
    p.run('dev',40,resume=True)
    assert len(dispatched)==24  # Completed cells do not dispatch on resume.
