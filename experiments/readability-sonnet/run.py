"""Run the sealed readability eval with Claude Sonnet 5.5 as the proxy user.

    uv run python experiments/readability-sonnet/run.py [--deadline-minutes 50] [--workers 3]

Resumable: a session whose record exists under runs/ is not run again, so the
command can be repeated until every session is done. `--assemble` only writes
runs/reading.jsonl and runs/writing.jsonl (score.py's input) from the records.

Protocol (fixed before any run, sealed with the contexts):
- One item per session. Each reading session gets exactly one sealed context
  file (contexts/<item>/<condition>.txt) on stdin; each writing session starts
  with contexts/<task>/attempt1.txt. One item per session meets "up to 6 items
  per session, never two items from the same excerpt in one session" and keeps
  every session's input byte-identical to the sealed file.
- Every session is fresh: its own empty temporary directory outside the repo,
  an account from pick-claude-account.sh, `claude -p --model claude-sonnet-5-5
  --tools ""` (FLAGS below). No other text is added to the conversation.
- Order: all sessions (reading item x condition x s1/s2, writing task x s1/s2)
  are shuffled with random.Random(SEED); runs/order.json records it. With
  parallel workers the start order follows that list.
- Writing loop: the SENTENCE line is scored with score.py's `check`. Unless the
  outcome is `correct`, and at most three attempts, the same conversation is
  resumed (`--resume <session id>`, same account and directory) with
  contexts/<task>/retry.txt, {ve_message} set to check's `ve_message` and
  {attempt} to the attempt number. A reply without a SENTENCE line is scored as
  the empty sentence. Only a wrapper around the whole sentence (backticks,
  straight or curly quotes, ** bold) is removed before scoring, as a person
  would not type it into the editor.
- Infrastructure failures (non-zero exit, an API error result, a timeout) are
  retried up to 3 times with a new temporary directory; for a writing turn the
  same conversation is resumed again. Every failed call is kept in the record.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

SEED = 20261003
MODEL = "claude-sonnet-5-5"
CLAUDE = "/home/seyran/.local/bin/claude"
PICK = ["zsh", "/home/seyran/code/manage-agents/pick-claude-account.sh"]
# The orchestrator's command, plus flags that only remove context (no MCP
# servers, no skills) and `--verbose`, which makes the JSON output include the
# session's init record (its tool, MCP server and skill lists are kept as proof).
FLAGS = ["-p", "--model", MODEL, "--tools", "", "--strict-mcp-config", "--disable-slash-commands",
         "--output-format", "json", "--verbose"]
TIMEOUT = 600
RUNS = HERE / "runs"
PICK_LOCK = threading.Lock()


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def jobs():
    items = json.loads((HERE / "items.json").read_text())["items"]
    tasks = json.loads((HERE / "writing.json").read_text())["tasks"]
    out = [{"kind": "reading", "item": i["id"], "condition": c, "session": s}
           for i in items for c in i["conditions"] for s in ("s1", "s2")]
    out += [{"kind": "writing", "task": t["id"], "session": s} for t in tasks for s in ("s1", "s2")]
    random.Random(SEED).shuffle(out)
    return out


def record_path(job):
    if job["kind"] == "reading":
        return RUNS / "reading" / job["item"] / f"{job['condition']}-{job['session']}.json"
    return RUNS / "writing" / job["task"] / f"{job['session']}.json"


def pick_account():
    return subprocess.run(PICK, capture_output=True, text=True, check=True).stdout.strip().splitlines()[-1]


def call(stdin_text, cwd, account=None, resume=None):
    """One `claude -p` call. Returns (account, call record)."""
    cmd = [CLAUDE, *FLAGS] + (["--resume", resume] if resume else [])
    with PICK_LOCK:
        # The picker counts running `claude -p` processes per account, so the
        # next pick waits until this process is visible.
        account = account or pick_account()
        started = time.time()
        proc = subprocess.Popen(cmd, cwd=cwd, env={**os.environ, "CLAUDE_CONFIG_DIR": account},
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(2)
    try:
        out, err = proc.communicate(stdin_text, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
        return account, {"ok": False, "error": "timeout", "stdout": out, "stderr": err[-4000:]}
    rec = {"account": Path(account).name, "cwd": cwd, "argv": cmd[1:], "stdin_sha256": sha(stdin_text),
           "returncode": proc.returncode, "seconds": round(time.time() - started, 1), "stderr": err[-4000:]}
    try:
        messages = json.loads(out)
    except json.JSONDecodeError:
        return account, dict(rec, ok=False, error="stdout is not JSON", stdout=out)
    messages = messages if isinstance(messages, list) else [messages]
    res = next((m for m in messages if m.get("type") == "result"), {})
    init = next((m for m in messages if m.get("type") == "system" and m.get("subtype") == "init"), {})
    ok = proc.returncode == 0 and not res.get("is_error") and res.get("subtype") == "success"
    return account, dict(rec, ok=ok, cli_result=res, text=res.get("result"), session_id=res.get("session_id"),
                         models=sorted(res.get("modelUsage", {})),
                         init={k: init.get(k) for k in ("model", "tools", "mcp_servers", "slash_commands",
                                                        "skills", "agents", "claude_code_version")})


def attempt_call(stdin_text, cwd_factory, account=None, resume=None, cwd=None):
    failures = []
    for _ in range(3):
        cwd_now = cwd or cwd_factory()
        account_now, rec = call(stdin_text, cwd_now, account, resume)
        if rec["ok"]:
            return account_now, cwd_now, rec, failures
        failures.append(rec)
        if not resume:
            shutil.rmtree(cwd_now, ignore_errors=True)
        time.sleep(30)
    return None, None, None, failures


def fresh_dir():
    return tempfile.mkdtemp(prefix="ve-proxy-", dir="/tmp")


def run_reading(job):
    stdin_text = (HERE / "contexts" / job["item"] / f"{job['condition']}.txt").read_text()
    _, cwd, rec, failures = attempt_call(stdin_text, fresh_dir)
    if rec is None:
        return dict(job, ok=False, failures=failures)
    shutil.rmtree(cwd, ignore_errors=True)
    return dict(job, ok=True, raw=rec["text"], call=rec, failures=failures)


SENTENCE = re.compile(r"^\s*\**SENTENCE:?\**:?\s*(.*)$", re.M | re.I)
REASON = re.compile(r"^\s*\**REASON:?\**:?\s*(.+)$", re.M | re.I)
WRAPPERS = [("**", "**"), ("`", "`"), ('"', '"'), ("“", "”")]


def parse_sentence(raw):
    m = SENTENCE.search(raw or "")
    sentence = m[1].strip() if m else ""
    changed = True
    while changed:
        changed = False
        for a, b in WRAPPERS:
            if len(sentence) > len(a) + len(b) and sentence.startswith(a) and sentence.endswith(b):
                sentence, changed = sentence[len(a):-len(b)].strip(), True
    r = REASON.search(raw or "")
    return sentence, (r[1].strip() if r else None)


def run_writing(job):
    import score
    first = (HERE / "contexts" / job["task"] / "attempt1.txt").read_text()
    template = (HERE / "contexts" / job["task"] / "retry.txt").read_text()
    turns, failures = [], []
    account, cwd, sid, stdin_text = None, None, None, first
    for n in range(1, 4):
        account, cwd, rec, fails = attempt_call(stdin_text, fresh_dir, account, sid, cwd)
        failures += fails
        if rec is None:
            return dict(job, ok=False, turns=turns, failures=failures)
        sid = rec["session_id"]
        sentence, reason = parse_sentence(rec["text"])
        checked = score.check(job["task"], sentence)
        turns.append({"attempt": n, "prompt": stdin_text, "raw": rec["text"], "sentence": sentence,
                      "reason": reason, "outcome": checked["outcome"], "ve_message": checked.get("ve_message"),
                      "call": rec})
        if checked["outcome"] == "correct" or n == 3:
            break
        stdin_text = template.replace("{ve_message}", str(checked.get("ve_message"))).replace("{attempt}",
                                                                                            str(n + 1))
    shutil.rmtree(cwd, ignore_errors=True)
    return dict(job, ok=True, turns=turns, failures=failures)


def run_job(job, deadline):
    path = record_path(job)
    if path.exists() and json.loads(path.read_text()).get("ok"):
        return "done"
    if time.time() > deadline:
        return "skipped"
    result = (run_reading if job["kind"] == "reading" else run_writing)(job)
    result["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=1, ensure_ascii=False, default=str) + "\n")
    label = job.get("item") or job.get("task")
    print(f"{label} {job.get('condition', '')} {job['session']} ok={result['ok']}", flush=True)
    return "ran" if result["ok"] else "failed"


def assemble():
    reading, writing, missing = [], [], []
    for job in jobs():
        path = record_path(job)
        rec = json.loads(path.read_text()) if path.exists() else None
        if not rec or not rec.get("ok"):
            missing.append(job)
            continue
        if job["kind"] == "reading":
            reading.append({"item": job["item"], "condition": job["condition"], "session": job["session"],
                            "raw": rec["raw"]})
        else:
            writing.append({"task": job["task"], "session": job["session"],
                            "attempts": [{"sentence": t["sentence"], "reason": t["reason"]} for t in rec["turns"]]})
    key = lambda r: (r.get("item") or r.get("task"), r.get("condition", ""), r["session"])
    for name, rows in (("reading.jsonl", reading), ("writing.jsonl", writing)):
        (RUNS / name).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in sorted(rows, key=key)))
    print(f"assembled {len(reading)} reading and {len(writing)} writing sessions; missing {len(missing)}")
    return missing


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--deadline-minutes", type=float, default=50)
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--assemble", action="store_true")
    args = p.parse_args(argv)
    RUNS.mkdir(exist_ok=True)
    order = jobs()
    (RUNS / "order.json").write_text(json.dumps({"seed": SEED, "model": MODEL, "flags": FLAGS, "order": order},
                                                indent=1) + "\n")
    if not args.assemble:
        deadline = time.time() + 60 * args.deadline_minutes
        with ThreadPoolExecutor(args.workers) as pool:
            counts = list(pool.map(lambda j: run_job(j, deadline), order))
        print({k: counts.count(k) for k in sorted(set(counts))})
    return 1 if assemble() else 0


if __name__ == "__main__":
    sys.exit(main())
