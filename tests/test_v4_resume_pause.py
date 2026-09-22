"""Runner-level exhaustion pauses without scoring or permanently stopping."""
import importlib.util
import json
from pathlib import Path
import sys
from unittest.mock import patch
import pytest
from ve_experiments.claude_cli import ClaudeCLI, InfrastructurePaused


def test_runner_pause_and_resume(tmp_path):
    here = Path(__file__).resolve().parents[1]/'experiments/V4-D-pilot'
    sys.path.insert(0,str(here))
    try:
        spec = importlib.util.spec_from_file_location('retry_pause_runner',here/'rerun.py')
        rerun = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rerun)
    finally:
        sys.path.remove(str(here))
    runner = object.__new__(rerun.Runner)
    runner.spent,runner.date = 341,'2026-09-22'
    runner.config,runner.account = tmp_path/'.claude-danielsaeedi37','danielsaeedi37'
    with patch.object(rerun,'OUT',tmp_path),patch.object(rerun,'verify'), \
         patch.object(ClaudeCLI,'sample',side_effect=InfrastructurePaused('exhausted')):
        with pytest.raises(InfrastructurePaused):
            runner.sample('item','alone','haiku','s','p')
    pause = json.loads((tmp_path/'PAUSE.json').read_text())
    assert pause['classification']=='INFRASTRUCTURE'
    assert pause['sample_index']==0 and pause['item_id']=='item'
    assert not (tmp_path/'STOP.json').exists()
    assert not (tmp_path/'ENDPOINT_STOP.json').exists()
    assert not (tmp_path/'scores').exists()
    def success(client,*args):
        assert client.infrastructure_retries
        client.ledger.parent.mkdir(parents=True,exist_ok=True)
        client.ledger.write_text(json.dumps({'status':'started'})+'\n')
        return {'thinking_tokens_reported':12}
    with patch.object(rerun,'OUT',tmp_path),patch.object(rerun,'verify'), \
         patch.object(ClaudeCLI,'sample',autospec=True,side_effect=success):
        assert runner.sample('item','alone','haiku','s','p')['thinking_tokens_reported']==12
    assert not (tmp_path/'PAUSE.json').exists()
