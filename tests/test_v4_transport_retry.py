"""Offline transport faults never become samples or hide model substitution."""
from contextlib import ExitStack
import json
from unittest.mock import patch
import pytest
from ve_experiments.claude_cli import (
    ClaudeCLI, Controls, EndpointError, InfrastructureError, InfrastructurePaused,
    MODELS, RETRY_BACKOFF, infrastructure_failure, parse_stream,
)
from test_v4_infrastructure import stream


def placeholder(model='<synthetic>'):
    return '\n'.join(map(json.dumps, [
        {'type':'system','subtype':'init','model':MODELS['opus']},
        {'type':'assistant','message':{'model':model, 'content':[{'type':'text','text':'API Error: Connection dropped (ECONNRESET)'}]}},
        {'type':'result','is_error':True,'result':'API Error: Connection dropped (ECONNRESET)','modelUsage':{}},
    ]))


@pytest.mark.parametrize('raw', ['', '  \n', placeholder()])
def test_transport_not_a_sample(raw):
    with pytest.raises(InfrastructureError):
        parse_stream(raw, MODELS['opus'])


def test_real_model_mismatch_wins_and_answer_text_is_not_a_network_error():
    assert infrastructure_failure(placeholder(MODELS['sonnet']), MODELS['opus']) is None
    with pytest.raises(EndpointError, match='model mismatch'):
        parse_stream(placeholder(MODELS['sonnet']), MODELS['opus'])
    raw=stream().replace('OK','ECONNRESET connection error')
    assert parse_stream(raw,MODELS['opus'])['text']=='ECONNRESET connection error'


def environment(tmp_path, responses):
    stack=ExitStack()
    binary=tmp_path/'claude'; binary.write_text('fixture binary')
    controls=Controls(working_directory=str(tmp_path/'empty'))
    client=ClaudeCLI(tmp_path/'ledger.jsonl',controls,infrastructure_retries=True)
    for name,value in [('shutil.which',str(binary)),('subprocess.check_output',controls.cli_version),
                       ('oauth_token','secret-token'),('check_context_date',None)]:
        stack.enter_context(patch('ve_experiments.claude_cli.'+name,return_value=value))
    sleep=stack.enter_context(patch('ve_experiments.claude_cli.time.sleep'))
    call=stack.enter_context(patch('ve_experiments.claude_cli.subprocess.run',side_effect=responses))
    return stack,client,sleep,call


def proc(raw,code=0):
    return type('Process',(),{'stdout':raw,'stderr':'','returncode':code})()


def test_retry_same_identity_then_cached_success(tmp_path):
    stack,client,sleep,call=environment(tmp_path,[proc(placeholder(),1),proc(''),proc(stream())])
    with stack:
        row=client.sample('item','system','prompt',1)
        assert client.sample('item','system','prompt',1)==row
    assert call.call_count==3
    assert [c.args[0] for c in sleep.call_args_list]==[30,60]
    rows=[json.loads(x) for x in client.ledger.read_text().splitlines()]
    assert len({r['key'] for r in rows})==1
    assert sum(r['status']=='ok' for r in rows)==1
    assert sum(r['status']=='infrastructure_error' for r in rows)==2
    assert all(r['prompt']=='prompt' and r['sample_index']==1 for r in rows)


def test_exhaustion_is_resumable_and_bounded(tmp_path):
    stack,client,sleep,call=environment(tmp_path,[proc('')]*6+[proc(stream())])
    with stack:
        with pytest.raises(InfrastructurePaused):
            client.sample('item','s','p')
        assert call.call_count==6
        assert [c.args[0] for c in sleep.call_args_list]==list(RETRY_BACKOFF)
        rows=[json.loads(x) for x in client.ledger.read_text().splitlines()]
        assert not any(r['status']=='ok' for r in rows)
        assert client.sample('item','s','p')['status']=='ok'
    assert call.call_count==7
    assert sleep.call_args.args==(30,)


def test_legacy_error_reclassified_without_rewriting_history(tmp_path):
    stack,client,sleep,call=environment(tmp_path,[proc(placeholder(),1),proc(stream())])
    with stack:
        client.infrastructure_retries=False
        with pytest.raises(InfrastructureError): client.sample('item','s','p')
        rows=[json.loads(x) for x in client.ledger.read_text().splitlines()]
        rows[-1]['status']='error'; rows[-1]['error']='CLI exit 1'
        client.ledger.write_text(''.join(json.dumps(r)+'\n' for r in rows))
        prefix=client.ledger.read_bytes()
        client.infrastructure_retries=True
        assert client.sample('item','s','p')['status']=='ok'
    assert client.ledger.read_bytes().startswith(prefix)
    assert call.call_count==2
    assert sleep.call_args.args==(30,)


def test_integrity_error_is_never_retried(tmp_path):
    stack,client,sleep,call=environment(tmp_path,[proc(stream(model=MODELS['sonnet']))])
    with stack:
        with pytest.raises(EndpointError,match='model mismatch'):
            client.sample('item','s','p')
    assert call.call_count==1
    sleep.assert_not_called()
