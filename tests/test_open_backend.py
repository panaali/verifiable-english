"""Open-weight backend, tested with a fake engine and a fake worker process. No downloads, no MLX."""

from __future__ import annotations

import json
import sys
import textwrap

import pytest

from ve_experiments import open_worker
from ve_experiments.llm import BackendError, LLMClient, Request, VerdictParseError, default_backend_for, parse_verdict
from ve_experiments.open_backend import Worker, open_backend, parse_open_model

FAKE_WORKER = textwrap.dedent(
    """
    import json, sys
    for line in sys.stdin:
        r = json.loads(line)
        if "DIE" in r["prompt"]:
            sys.exit(3)
        if "FAIL" in r["prompt"]:
            print(json.dumps({"id": r["id"], "error": "boom"}), flush=True)
            continue
        v = "approve" if r["verdict"] == "forced" else f"seed={r['seed']} temp={r['temp']} max_new={r['max_new']}"
        text = 'thinking... {"verdict": "%s"}' % v if r["verdict"] == "forced" else v
        print("noise that is not json", flush=True)
        print(json.dumps({"id": r["id"], "text": text, "input_tokens": 7, "output_tokens": 3, "gen_s": 0.01,
                          "batch_size": 1, "extra": {}}), flush=True)
    """
)


@pytest.fixture
def worker(tmp_path):
    script = tmp_path / "fake_worker.py"
    script.write_text(FAKE_WORKER)
    w = Worker(cmd=[sys.executable, str(script)], log_path=tmp_path / "open_calls.jsonl")
    yield w
    w.close()


def test_model_name_parsing():
    repo, s = parse_open_model("open:org/Model-4bit@temp=0.7,max_new=64")
    assert repo == "org/Model-4bit" and s == {"max_new": "64", "temp": "0.7", "verdict": "free"}
    assert parse_open_model("open:org/m")[1]["temp"] == "0"  # greedy by default
    for bad in ("org/m", "open:", "open:org/m@foo=1", "open:org/m@verdict=guess", "open:org/m@max_new=0"):
        with pytest.raises(ValueError):
            parse_open_model(bad)


def test_registration_hook_routes_open_models():
    assert default_backend_for("open:org/m") is open_backend
    assert default_backend_for("claude-haiku-4-5") is not open_backend


def test_client_passes_real_seed_caches_and_logs(tmp_path, worker):
    def backend(model, system, prompt, timeout_s, cwd, seed=0):
        return open_backend(model, system, prompt, timeout_s, cwd, seed=seed, worker=worker)

    backend.takes_seed = True
    client = LLMClient(cache_dir=tmp_path / "cache", backend=backend, retries=1)
    m = "open:org/m@temp=0.5,max_new=32"
    a, b = client.call(m, "p", seed=4, identity="t"), client.call(m, "p", seed=5, identity="t")
    assert a.text == "seed=4 temp=0.5 max_new=32" and b.text.startswith("seed=5")
    assert (a.input_tokens, a.output_tokens) == (7, 3)
    again = client.call(m, "p", seed=4, identity="t")
    assert again.from_cache and again.text == a.text
    other = client.call("open:org/m@temp=0.5", "p", seed=4, identity="t")  # settings are part of the key
    assert not other.from_cache and "max_new=400" in other.text
    rows = [json.loads(x) for x in (tmp_path / "open_calls.jsonl").read_text().splitlines()]
    assert len(rows) == 3 and rows[0]["output_tokens"] == 3 and rows[0]["batch_size"] == 1 and "gen_s" in rows[0]


def test_unparseable_and_failed_replies_are_not_rescued(tmp_path, worker):
    free = open_backend("open:org/m", "s", "p", 5, tmp_path, worker=worker)
    with pytest.raises(VerdictParseError):  # same strict parser as hosted judges; the runner scores this worst case
        parse_verdict(free.text)
    forced = open_backend("open:org/m@verdict=forced", "s", "p", 5, tmp_path, worker=worker)
    assert parse_verdict(forced.text).value == "approve"
    with pytest.raises(BackendError, match="boom"):
        open_backend("open:org/m", "s", "FAIL", 5, tmp_path, worker=worker)


def test_worker_death_is_a_backend_error_and_worker_restarts(tmp_path, worker):
    with pytest.raises(BackendError, match="exited"):
        open_backend("open:org/m", "s", "DIE", 5, tmp_path, worker=worker)
    assert open_backend("open:org/m", "s", "p", 5, tmp_path, worker=worker).text.startswith("seed=0")


def test_concurrent_requests_get_their_own_replies(tmp_path, worker):
    def backend(model, system, prompt, timeout_s, cwd, seed=0):
        return open_backend(model, system, prompt, timeout_s, cwd, seed=seed, worker=worker)

    backend.takes_seed = True
    client = LLMClient(cache_dir=tmp_path / "cache", backend=backend, retries=1)
    res = client.map([Request("open:org/m@temp=1", "p", seed=i, identity=str(i)) for i in range(20)])
    assert [r.text.split()[0] for r in res] == [f"seed={i}" for i in range(20)]


# ------------------------------------------------------------------ worker loop with a fake engine


class FakeEngine:
    def __init__(self):
        self.loads, self.batches = [], []

    def load(self, name):
        if not self.loads or self.loads[-1] != name:
            self.loads.append(name)  # one model at a time: a new name replaces the old one

    def generate(self, reqs):
        self.batches.append([r["id"] for r in reqs])
        if any("RAISE" in r["prompt"] for r in reqs):
            raise RuntimeError("engine failure")
        return [{"id": r["id"], "text": "ok", "input_tokens": 1, "output_tokens": 1, "extra": {}} for r in reqs]


def _req(i, model="a", temp=0.0, prompt="p", verdict="free"):
    return json.dumps({"id": i, "model": model, "system": "s", "prompt": prompt, "max_new": 8, "temp": temp, "seed": i,
                       "verdict": verdict, "allowed": ["approve", "reject"]})  # fmt: skip


def test_worker_batches_greedy_and_isolates_sampled_and_models():
    eng, out = FakeEngine(), []
    lines = [_req(1), _req(2), _req(3, temp=0.7), _req(4, temp=0.7), _req(5, model="b"), _req(6), _req(7, verdict="forced")]
    open_worker.serve(eng, iter(lines), out.append, max_batch=2, window_s=0.2)
    assert sorted(r["id"] for r in out) == [1, 2, 3, 4, 5, 6, 7]
    assert [1, 2] in eng.batches and [3] in eng.batches and [4] in eng.batches  # sampled requests run alone
    assert all(len(b) <= 2 for b in eng.batches)
    assert [5] in eng.batches and [7] in eng.batches  # never mixes models or verdict modes in a batch
    assert all(r["batch_size"] >= 1 and "gen_s" in r for r in out)


def test_worker_reports_engine_errors_per_request():
    eng, out = FakeEngine(), []
    open_worker.serve(eng, iter([_req(1, prompt="RAISE"), _req(2, model="b")]), out.append, max_batch=4, window_s=0.05)
    by = {r["id"]: r for r in out}
    assert "engine failure" in by[1]["error"] and by[2]["text"] == "ok"
