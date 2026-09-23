"""A4: output-cap exhaustion is infrastructure, never a sample; other multi-turn streams still stop."""
from contextlib import ExitStack
import json
from pathlib import Path
from unittest.mock import patch
import pytest
from ve_experiments.t1b.a4_transport import (
    ClaudeCLI, Controls, EndpointError, InfrastructureError, InfrastructurePaused, MODELS, RETRY_BACKOFF,
    SessionLimit, infrastructure_failure, parse_stream,
)
from test_t1b_a3 import proc
from test_v4_infrastructure import stream

SONNET = MODELS['sonnet']
LEDGER = Path(__file__).resolve().parents[1]/'experiments/T1b/results-full/ledgers/sonnet-attack_monitor-saeedi.danial-2026-09-23.jsonl'


def continuation(model=SONNET, user_text='Output token limit hit. Resume directly — no apology.', synthetic=True, block='text'):
    first = {'id':'m1','model':model,'content':[{'type':'thinking','thinking':''}]}
    second = {'id':'m2','model':model,'content':[{'type':block,'text':'{"plausible": true}'}]}
    return '\n'.join(map(json.dumps, [
        {'type':'system','subtype':'init','model':model,'tools':[],'mcp_servers':[],'agents':[],'skills':[],'plugins':[]},
        {'type':'assistant','message':first},
        {'type':'user','message':{'role':'user','content':[{'type':'text','text':user_text}]},'parent_tool_use_id':None,'isSynthetic':synthetic},
        {'type':'assistant','message':{**second,'content':[{'type':'thinking','thinking':''}]}},
        {'type':'assistant','message':second},
        {'type':'result','subtype':'success','stop_reason':'end_turn','num_turns':2,'is_error':False,'result':'{"plausible": true}',
         'usage':{'input_tokens':4,'cache_creation_input_tokens':1,'cache_read_input_tokens':0,'output_tokens':20121},'modelUsage':{model:{}}},
    ]))


def environment(tmp_path, responses):
    stack = ExitStack()
    binary = tmp_path/'claude'; binary.write_text('fixture binary')
    controls = Controls(working_directory=str(tmp_path/'empty'))
    client = ClaudeCLI(tmp_path/'ledger.jsonl', controls, infrastructure_retries=True)
    for name, value in [('shutil.which', str(binary)), ('subprocess.check_output', controls.cli_version),
                        ('oauth_token', 'secret-token'), ('check_context_date', None)]:
        stack.enter_context(patch('ve_experiments.t1b.a4_transport.'+name, return_value=value))
    sleep = stack.enter_context(patch('ve_experiments.t1b.a4_transport.time.sleep'))
    call = stack.enter_context(patch('ve_experiments.t1b.a4_transport.subprocess.run', side_effect=responses))
    return stack, client, sleep, call


def test_output_cap_continuation_is_infrastructure_not_a_sample():
    assert infrastructure_failure(continuation(), SONNET) == 'output cap exhausted'
    with pytest.raises(InfrastructureError):
        parse_stream(continuation(), SONNET)


def test_bare_max_tokens_is_infrastructure():
    raw = stream(stop='max_tokens')
    assert infrastructure_failure(raw, MODELS['opus']) == 'output cap exhausted'
    with pytest.raises(InfrastructureError):
        parse_stream(raw, MODELS['opus'])


@pytest.mark.parametrize('raw', [
    continuation(user_text='Please also check the other file.'),
    continuation(synthetic=False),
    continuation(block='tool_use'),
    continuation().replace('"tools": []', '"tools": ["Bash"]'),
])
def test_other_multi_turn_streams_remain_integrity_stops(raw):
    assert infrastructure_failure(raw, SONNET) is None
    with pytest.raises(EndpointError) as caught:
        parse_stream(raw, SONNET)
    assert not isinstance(caught.value, InfrastructureError)


def test_model_change_and_session_limit_still_win():
    raw = continuation(model=MODELS['opus'])
    assert infrastructure_failure(raw, SONNET) is None
    with pytest.raises(EndpointError, match='model mismatch'):
        parse_stream(raw, SONNET)
    limit = '\n'.join(map(json.dumps, [
        {'type':'system','subtype':'init','model':SONNET,'tools':[],'mcp_servers':[]},
        {'type':'assistant','message':{'model':'<synthetic>','content':[{'type':'text','text':"You've hit your session limit"}]}},
        {'type':'result','is_error':True,'result':"You've hit your session limit",'modelUsage':{}}]))
    with pytest.raises(SessionLimit):
        parse_stream(limit, SONNET)


def test_continuation_retried_in_place_then_cached(tmp_path):
    stack, client, sleep, call = environment(tmp_path, [proc(continuation(MODELS['opus'])), proc(stream())])
    with stack:
        row = client.sample('item', 's', 'p', 1)
        assert client.sample('item', 's', 'p', 1) == row
    assert call.call_count == 2 and [c.args[0] for c in sleep.call_args_list] == [30]
    rows = [json.loads(x) for x in client.ledger.read_text().splitlines()]
    failed = [r for r in rows if r['status'] == 'infrastructure_error']
    assert len(failed) == 1 and failed[0]['counts_as_sample'] is False and failed[0]['error'] == 'output cap exhausted'
    assert sum(r['status'] == 'ok' for r in rows) == 1 and len({r['key'] for r in rows}) == 1


def test_repeated_cap_exhaustion_pauses_after_five_retries(tmp_path):
    stack, client, sleep, call = environment(tmp_path, [proc(stream(stop='max_tokens'))]*6)
    with stack:
        with pytest.raises(InfrastructurePaused):
            client.sample('item', 's', 'p')
    assert call.call_count == 6 and [c.args[0] for c in sleep.call_args_list] == list(RETRY_BACKOFF)


@pytest.mark.skipif(not LEDGER.exists(), reason='A3 ledger not present')
def test_recorded_a3_stop_is_reclassified():
    rows = [json.loads(line) for line in LEDGER.read_text().splitlines()]
    failed = [r for r in rows if r['item_id'] == '5a47675a06cf/b-monitor/1' and r['status'] == 'error']
    assert len(failed) == 1 and failed[0]['error'] == 'Not a single-turn response'
    assert infrastructure_failure(failed[0]['raw_stream'], SONNET, failed[0]['error']) == 'output cap exhausted'
