"""Post-stop regression: a valid stream can still violate study budget controls."""
import importlib.util
import json
from pathlib import Path
import sys
from unittest.mock import patch

import pytest


def test_valid_cli_stream_above_cap_is_not_scored_or_retried(tmp_path):
    here = Path(__file__).resolve().parents[1] / "experiments/V4-D-pilot"
    sys.path.insert(0, str(here))
    try:
        spec = importlib.util.spec_from_file_location("d_cap_run", here / "run.py")
        run = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(run)
    finally:
        sys.path.remove(str(here))
    runner = object.__new__(run.Runner)
    runner.spent = 209
    runner.manifest = {"hard_max_calls": 790}
    runner.date = "2026-09-22"
    item = {"id": "d-00"}
    row = {"status":"ok", "key":"over-cap", "thinking_tokens_reported":1188,
           "raw_stream":json.dumps({"type":"assistant", "message":{"model":run.MODELS["haiku"]}})}
    def response(client, *args):
        client.ledger.parent.mkdir(parents=True,exist_ok=True)
        client.ledger.write_text(json.dumps({"status":"started"}) + "\n" + json.dumps(row) + "\n")
        return row
    with patch.object(run,"OUT",tmp_path), \
         patch.object(run,"judge_prompt",return_value=("system","prompt")), \
         patch.object(run.ClaudeCLI,"sample",autospec=True,side_effect=response) as sample:
        with pytest.raises(run.EndpointError,match="1188 exceed declared cap 1024"):
            runner.judge(item,"mistranslation","haiku",0,{})
        with pytest.raises(run.EndpointError,match="permanently stopped"):
            runner.judge(item,"mistranslation","haiku",0,{})
        sample.assert_called_once()
    assert not (tmp_path / "scores/d-00-mistranslation-haiku-0.json").exists()
    stop = json.loads((tmp_path / "STOP.json").read_text())
    assert stop["observed_model_ids"] == [run.MODELS["haiku"]]
    assert "1188" in stop["error"] and stop["substituted_models"] is False
