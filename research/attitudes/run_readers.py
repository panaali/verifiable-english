#!/usr/bin/env python3
"""E1 and E2's readers (docs/spec/attitudes-PLAN.md section 4; the DRI's decision AT1, 2026-10-13).

One fresh `claude -p` process per call (G2): an empty working directory of its own, no system prompt beyond the item's
own preamble (`--system-prompt ""`), no tools, no settings files, no MCP servers, no session saved. Calls are dispatched
in the seeded order of the item files (session 0's order, then session 1's, ...), at most PARALLEL at a time. Reader
settings are the reader's defaults (G6): nothing sets temperature, output limit or thinking; what the reader reports
(model, thinking and output tokens, stop reason) is saved with each answer.

    python3 research/attitudes/run_readers.py ACCOUNT_DIR [e1] [e2]

Writes docs/research/evidence/attitudes/e{1,2}-raw.jsonl, one line per answered call, and resumes from them: an
(item, session) already answered is not asked again. A call that fails (process error, timeout, API error) gives no
answer; it is logged in e-calls-failed.jsonl and asked again, at most RETRIES times. Dispatch stops when the account's
five-hour window reaches 80% or its week 88% (the usage cap rules); a rerun resumes.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import experiments as ex  # noqa: E402

CLAUDE = "/home/seyran/.local/bin/claude"
FLAGS = ["-p", "--model", ex.READER, "--system-prompt", "", "--tools", "", "--strict-mcp-config", "--setting-sources", "",
         "--no-session-persistence", "--disable-slash-commands", "--output-format", "stream-json", "--verbose"]
PARALLEL = 8
RETRIES = 3
CALL_TIMEOUT = 900
STOP_5H, STOP_WEEK = 0.80, 0.88

lock = threading.Lock()
stop = threading.Event()
usage = {}


def call(account, prompt):
    with tempfile.TemporaryDirectory() as cwd:
        run = subprocess.run([CLAUDE, *FLAGS, prompt], cwd=cwd, env={**os.environ, "CLAUDE_CONFIG_DIR": account},
                             capture_output=True, text=True, timeout=CALL_TIMEOUT, stdin=subprocess.DEVNULL)
    events = [json.loads(ln) for ln in run.stdout.splitlines() if ln.strip().startswith("{")]
    result = next((e for e in events if e.get("type") == "result"), None)
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})
    for e in events:
        if e.get("type") == "rate_limit_event":
            w = e["rate_limit_info"].get("unifiedWindows", {})
            with lock:
                usage.update({k: v["utilization"] for k, v in w.items()})
    if run.returncode != 0 or result is None or result.get("is_error") or result.get("subtype") != "success":
        raise RuntimeError(f"rc={run.returncode} result={json.dumps(result)[:500] if result else None} "
                           f"stderr={run.stderr[-500:]}")
    mu = result.get("modelUsage", {})
    u = result.get("usage", {})
    return {"answer": result["result"], "model": init.get("model"), "model_usage": list(mu),
            "claude_code_version": init.get("claude_code_version"), "stop_reason": result.get("stop_reason"),
            "input_tokens": u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0),
            "output_tokens": u.get("output_tokens"), "thinking_tokens": (u.get("output_tokens_details") or {}).get("thinking_tokens"),
            "max_output_tokens": next(iter(mu.values()), {}).get("maxOutputTokens"), "reader_session_id": result.get("session_id")}


def main(account, exps):
    jobs = []
    for exp in exps:
        data = json.loads((ex.EVIDENCE / f"{exp}-items.json").read_text())
        text = {i["id"]: i["text"] for i in data["items"]}
        raw = ex.EVIDENCE / f"{exp}-raw.jsonl"
        done = {(r["item"], r["session"]) for r in map(json.loads, raw.read_text().splitlines())} if raw.exists() else set()
        n = 0
        for s, order in enumerate(data["orders"]):
            for item in order:
                if (item, s) not in done:
                    jobs.append((exp, raw, n, item, s, ex.PROMPT.format(text=text[item])))
                n += 1
    failed = ex.EVIDENCE / "e-calls-failed.jsonl"
    print(f"{len(jobs)} calls to make", flush=True)
    count = [0]

    def work(job):
        exp, raw, n, item, s, prompt = job
        for attempt in range(1, RETRIES + 1):
            with lock:
                if usage.get("five_hour", 0) >= STOP_5H or usage.get("seven_day", 0) >= STOP_WEEK:
                    stop.set()
            if stop.is_set():
                return
            started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            try:
                out = call(account, prompt)
            except (RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
                with lock, failed.open("a") as f:
                    f.write(json.dumps({"experiment": exp, "item": item, "session": s, "attempt": attempt,
                                        "started": started, "error": str(e)[:1500]}) + "\n")
                continue
            row = {"item": item, "session": s, "answer": out.pop("answer"), "call_index": n, "attempt": attempt,
                   "started": started, **out}
            with lock:
                with raw.open("a") as f:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                count[0] += 1
                if count[0] % 50 == 0:
                    print(f"{count[0]} answered; usage {usage}", flush=True)
            return

    with ThreadPoolExecutor(PARALLEL) as pool:
        list(pool.map(work, jobs))
    print(f"{count[0]} answered this run; usage {usage}; stopped by the usage cap: {stop.is_set()}", flush=True)
    return 3 if stop.is_set() else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2:] or ["e1", "e2"]))
