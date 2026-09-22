"""D must never spend after a model mismatch or a persisted stop."""
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

import pytest


def gate_module():
    path = Path(__file__).resolve().parents[1] / "experiments/V4-D-pilot/gate.py"
    spec = importlib.util.spec_from_file_location("v4_d_gate", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_identity_inventory_preserves_midstream_fallback():
    module = gate_module()
    raw = "\n".join(map(json.dumps, [
        {"type": "system", "subtype": "init", "model": "claude-opus-5-5"},
        {"type": "assistant", "message": {"model": "claude-opus-4-8"}},
        {"type": "result", "modelUsage": {"claude-opus-4-8": {}}},
    ]))
    assert module.identities(raw) == ["claude-opus-4-8", "claude-opus-5-5"]


def test_persisted_stop_prevents_subscription_call(tmp_path):
    module = gate_module()
    out = tmp_path / "results"
    out.mkdir()
    (out / "STOP.json").write_text('{"status":"stopped"}')
    with patch.object(module, "HERE", tmp_path), patch.object(module.ClaudeCLI, "sample") as sample:
        with pytest.raises(module.EndpointError, match="permanently stopped"):
            module.main()
        sample.assert_not_called()


def test_gate_failure_persists_stop_and_never_substitutes(tmp_path):
    module = gate_module()
    (tmp_path / "PREREG-D-pilot.md").write_text("test protocol")
    (tmp_path / "PREREG-D-pilot.md.ots").write_bytes(b"test receipt")
    def fail(client, *args, **kwargs):
        client.ledger.write_text(json.dumps({"status":"started"}) + "\n" + json.dumps({
            "status":"error", "raw_stream":json.dumps({"type":"assistant", "message":{"model":"claude-opus-4-8"}})
        }) + "\n")
        raise module.EndpointError("Served model mismatch")
    with patch.object(module, "HERE", tmp_path), \
         patch.object(module.subprocess, "run"), \
         patch.object(module.subprocess, "check_output", return_value="testcommit\n"), \
         patch.object(module.ClaudeCLI, "sample", autospec=True, side_effect=fail) as sample:
        with pytest.raises(SystemExit) as exc:
            module.main()
        assert exc.value.code == 2
        assert sample.call_count == 1
    stop = json.loads((tmp_path / "results/STOP.json").read_text())
    assert stop["observed_model_ids"] == ["claude-opus-4-8"]
    assert stop["started_calls"] == 1 and stop["accepted_experimental_samples"] == 0
    assert stop["substituted_models"] is False
