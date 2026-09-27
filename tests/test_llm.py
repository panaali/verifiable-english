import json
import threading

import pytest

from ve_experiments.llm import CODEX_FLAGS, parse_codex_events, BackendError, LLMClient, RawReply, Request, VerdictParseError, parse_verdict, summarize_log


class FakeBackend:
    def __init__(self, fail_first=0, barrier=None, text='{"verdict": "approve"}'):
        self.calls = 0
        self.fail_first = fail_first
        self.barrier = barrier
        self.text = text
        self.active = 0
        self.max_active = 0
        self.cwds = set()
        self.lock = threading.Lock()

    def __call__(self, model, system, prompt, timeout_s, cwd):
        with self.lock:
            self.calls += 1
            n = self.calls
            self.active += 1
            self.max_active = max(self.max_active, self.active)
            self.cwds.add(cwd)
        try:
            if self.barrier is not None:
                self.barrier.wait(timeout=30)
            if n <= self.fail_first:
                raise BackendError("transient")
            return RawReply(f"{self.text}", input_tokens=10, output_tokens=5)
        finally:
            with self.lock:
                self.active -= 1


def client(tmp_path, backend, **kw):
    return LLMClient(cache_dir=tmp_path / "cache", backend=backend, backoff_s=0.0, **kw)


def test_cache_is_keyed_by_model_prompt_and_seed(tmp_path):
    be = FakeBackend()
    c = client(tmp_path, be)
    a = c.call("m1", "p")
    assert a.ok and not a.from_cache and be.calls == 1
    b = c.call("m1", "p")
    assert b.from_cache and b.text == a.text and be.calls == 1
    c.call("m1", "p", seed=1)
    c.call("m2", "p")
    c.call("m1", "q")
    c.call("m1", "p", system="other")
    assert be.calls == 5
    # a new client on the same directory reuses the cache
    assert client(tmp_path, be).call("m1", "p").from_cache and be.calls == 5


def test_retries_then_succeeds(tmp_path):
    be = FakeBackend(fail_first=2)
    r = client(tmp_path, be, retries=3).call("m", "p")
    assert r.ok and r.attempts == 3


def test_failure_is_returned_not_raised_and_not_cached(tmp_path):
    be = FakeBackend(fail_first=99)
    c = client(tmp_path, be, retries=2)
    r = c.call("m", "p")
    assert not r.ok and r.text is None and r.error == "transient" and r.attempts == 2
    be.fail_first = 0
    assert c.call("m", "p").ok  # the failure was not cached


def test_empty_reply_counts_as_failure(tmp_path):
    r = client(tmp_path, FakeBackend(text="  "), retries=1).call("m", "p")
    assert not r.ok and r.error == "empty reply"


def test_concurrency_limit_and_order(tmp_path):
    be = FakeBackend(barrier=threading.Barrier(3))
    c = client(tmp_path, be, max_concurrency=3)
    res = c.map(Request("m", f"p{i}") for i in range(12))
    assert [r.key for r in res] == [c.call("m", f"p{i}").key for i in range(12)]
    assert be.max_active <= 3 and be.max_active >= 2


def test_identical_concurrent_requests_make_one_call(tmp_path):
    be = FakeBackend()
    c = client(tmp_path, be, max_concurrency=3)
    call = c.call
    together = threading.Barrier(6)
    def simultaneous(*args, **kwargs):
        together.wait(timeout=30)
        return call(*args, **kwargs)
    c.call = simultaneous
    res = c.map(Request("m", "same") for _ in range(6))
    assert be.calls == 1 and sum(r.from_cache for r in res) == 5


def test_calls_run_outside_the_repository(tmp_path):
    be = FakeBackend()
    client(tmp_path, be).call("m", "p")
    (cwd,) = be.cwds
    assert list(cwd.iterdir()) == [] and "ve-claude" not in str(cwd)


def test_log_records_tokens_and_cache_hits(tmp_path):
    c = client(tmp_path, FakeBackend())
    c.call("m", "p", tag="t")
    c.call("m", "p", tag="t")
    rows = [json.loads(x) for x in c.log_path.read_text().splitlines()]
    assert [r["from_cache"] for r in rows] == [False, True]
    assert rows[0]["input_tokens"] == 10 and rows[0]["tag"] == "t" and "text" not in rows[0]
    s = summarize_log(c.log_path)["m"]
    assert s["calls"] == 2 and s["cache_hits"] == 1 and s["output_tokens"] == 5


@pytest.mark.parametrize(
    "text,expected",
    [
        ('{"verdict": "approve"}', "approve"),
        ('Reasoning here {not json}.\n{"verdict": "reject", "confidence": 0.7}', "reject"),
        ('text\n```json\n{"verdict": "reject"}\n```', "reject"),
        ('{"verdict": "approve"}\n\nfinal: {"verdict": "reject", "why": {"a": 1}}', "reject"),
    ],
)
def test_parse_verdict_accepts(text, expected):
    assert parse_verdict(text).value == expected


@pytest.mark.parametrize(
    "text",
    [
        None,
        "",
        "I approve.",
        '{"verdict": "approve"} I hope this helps!',  # JSON is not final
        '{"verdict": "Approve"}',  # no case folding
        '{"verdict": "maybe"}',
        '{"decision": "approve"}',
        '{"verdict": true}',
        '["approve"]',
        '{"verdict": "approve"',
    ],
)
def test_parse_verdict_rejects(text):
    with pytest.raises(VerdictParseError):
        parse_verdict(text)


@pytest.mark.live
def test_live_smoke():
    from ve_experiments.smoke import DEFAULT_MODELS, main

    assert main(list(DEFAULT_MODELS)) == 0


def test_codex_command_execution_is_detected():
    # Reviewer's reproduction: a command_execution event followed by a verdict must not pass silently.
    out = "\n".join([
        '{"type":"item.started","item":{"id":"i1","type":"command_execution","command":"cat /repo/items.jsonl","status":"in_progress"}}',
        '{"type":"item.completed","item":{"id":"i1","type":"command_execution","command":"cat /repo/items.jsonl","exit_code":0}}',
        '{"type":"item.completed","item":{"id":"i2","type":"agent_message","text":"{\\"verdict\\": \\"reject\\"}"}}',
        '{"type":"turn.completed","usage":{"input_tokens":10,"output_tokens":2}}',
    ])  # fmt: skip
    reply = parse_codex_events(out)
    assert reply.text == '{"verdict": "reject"}' and reply.tool_events == ("codex:command_execution:cat /repo/items.jsonl",)
    clean = parse_codex_events('{"type":"item.completed","item":{"type":"reasoning","text":"hm"}}\n{"type":"item.completed","item":{"type":"agent_message","text":"ok"}}')
    assert clean.tool_events == ()


def test_codex_is_launched_without_tools_or_user_config():
    flags = " ".join(CODEX_FLAGS)
    for needed in ("--disable shell_tool", "--ignore-user-config", "--ignore-rules", "--ephemeral", "--json", 'web_search="disabled"'):
        assert needed in flags


def test_tool_events_survive_the_cache(tmp_path):
    def be(model, system, prompt, timeout_s, cwd):
        return RawReply("x", tool_events=("codex:command_execution:ls",))

    c = LLMClient(cache_dir=tmp_path / "c", backend=be)
    assert c.call("m", "p").used_tools and c.call("m", "p").used_tools and c.call("m", "p").from_cache


def test_identity_separates_cache_entries(tmp_path):
    be = FakeBackend()
    c = client(tmp_path, be)
    c.call("m", "p", identity="t1")
    c.call("m", "p", identity="t2")
    c.call("m", "p", identity="t1")
    assert be.calls == 2


def test_model_settings_suffix():
    from ve_experiments.llm import cache_key, default_backend_for, split_model

    assert split_model("gpt-5.6-luna@effort=none") == ("gpt-5.6-luna", {"effort": "none"})
    assert split_model("claude-haiku-4-5-20251001") == ("claude-haiku-4-5-20251001", {})
    assert cache_key("m@effort=none", "s", "p", 0) != cache_key("m", "s", "p", 0)
    assert default_backend_for("claude-haiku-4-5-20251001@thinking=0").__name__ == "claude_backend"
    with pytest.raises(ValueError):
        split_model("m@temperature=0")


def test_tool_use_in_a_failed_attempt_invalidates_the_successful_retry(tmp_path):
    from ve_experiments.llm import BackendError, parse_codex_events

    failed = "\n".join([
        json.dumps({"type": "item.completed", "item": {"type": "command_execution", "command": "cat labels.jsonl"}}),
        json.dumps({"type": "turn.failed", "error": {"message": "stream closed"}}),
    ])  # fmt: skip
    with pytest.raises(BackendError) as info:
        parse_codex_events(failed)
    assert info.value.tool_events and "cat labels.jsonl" in info.value.tool_events[0]
    calls = []

    def backend(model, system, prompt, timeout_s, cwd):
        calls.append(1)
        if len(calls) == 1:
            return parse_codex_events(failed)
        return RawReply('{"verdict": "approve"}')

    res = LLMClient(cache_dir=tmp_path, backend=backend, backoff_s=0).call("gpt-x", "p")
    assert res.ok and res.attempts == 2 and res.used_tools and "attempt1:" in res.tool_events[0]
    again = LLMClient(cache_dir=tmp_path, backend=backend).call("gpt-x", "p")
    assert again.from_cache and again.used_tools


def test_claude_is_launched_without_ambient_context(monkeypatch, tmp_path):
    import ve_experiments.llm as llm

    seen = {}

    def fake_run(cmd, stdin, timeout_s, cwd, env=None, events_from=None):
        seen["cmd"] = list(cmd)
        return json.dumps({"result": "ok", "usage": {}})

    monkeypatch.setattr(llm, "_run", fake_run)
    llm.claude_backend("claude-x", "sys", "p", 5, tmp_path)
    cmd = seen["cmd"]
    assert "--safe-mode" in cmd and "--disable-slash-commands" in cmd and "--strict-mcp-config" in cmd
    assert cmd[cmd.index("--setting-sources") + 1] == "" and cmd[cmd.index("--tools") + 1] == ""
