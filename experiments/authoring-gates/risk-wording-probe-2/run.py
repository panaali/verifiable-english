#!/usr/bin/env python3
"""Send sealed sessions to their proxy readers (risk-PLAN.md 2.6). Written after sealing; not in the manifest.

    python3 run.py --family haiku|sol [--limit N] [--workers W]

Each session runs once, in a fresh empty temporary directory outside the repository, with no tools. Raw output goes
to runs/<session>/. Only transport errors (non-zero exit, no parseable CLI output, CLI-reported error, timeout) are
retried, and each is recorded in meta.json.
"""

import argparse
import datetime
import json
import os
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLAUDE = "/home/seyran/.local/bin/claude"
PICKER = "/home/seyran/code/manage-agents/pick-claude-account.sh"
CODEX_HOME = "/home/seyran/.agent-accounts/codex"
MAX_ATTEMPTS = 3


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def call_haiku(text, tmp):
    cfg = subprocess.run(["zsh", PICKER], capture_output=True, text=True).stdout.strip()
    env = dict(os.environ, CLAUDE_CONFIG_DIR=cfg)
    cmd = [CLAUDE, "-p", "--model", "claude-haiku-4-5-20251001", "--tools", "", "--output-format", "json"]
    p = subprocess.run(cmd, input=text, capture_output=True, text=True, cwd=tmp, env=env, timeout=300)
    info = {"account": cfg, "argv": cmd, "exit_code": p.returncode}
    try:
        out = json.loads(p.stdout)
    except json.JSONDecodeError:
        return p, info, None, "no JSON on stdout"
    info["cli_session_id"] = out.get("session_id")
    info["model_usage"] = list((out.get("modelUsage") or {}).keys())
    if p.returncode != 0 or out.get("is_error") or out.get("subtype") != "success":
        return p, info, None, f"CLI error: subtype={out.get('subtype')} is_error={out.get('is_error')}"
    return p, info, out.get("result", ""), None


def call_sol(text, tmp):
    env = dict(os.environ, CODEX_HOME=CODEX_HOME)
    cmd = ["codex", "exec", "-m", "gpt-6-sol", "-s", "read-only", "--skip-git-repo-check", "-C", tmp, "--json"]
    p = subprocess.run(cmd + [text], stdin=subprocess.DEVNULL, capture_output=True, text=True, cwd=tmp, env=env,
                       timeout=540)
    info = {"argv": cmd + ["<session text>"], "exit_code": p.returncode, "tool_items": []}
    message, errors = None, []
    for line in p.stdout.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = ev.get("type")
        if t == "thread.started":
            info["cli_session_id"] = ev.get("thread_id")
        elif t in ("error", "turn.failed"):
            errors.append(json.dumps(ev)[:300])
        elif t == "item.completed":
            item = ev.get("item", {})
            if item.get("type") == "agent_message":
                message = item.get("text", "")
            elif item.get("type") not in ("reasoning",):
                info["tool_items"].append(item.get("type"))
    if p.returncode != 0 or errors or message is None:
        return p, info, None, f"exit {p.returncode}; " + ("; ".join(errors) or "no agent message")
    return p, info, message, None


def run_session(sess):
    sid = sess["session"]
    rdir = HERE / "runs" / sid
    if (rdir / "response.txt").exists():
        return sid, "skipped (done)"
    rdir.mkdir(parents=True, exist_ok=True)
    text = (HERE / "sessions" / f"{sid}.txt").read_text()
    call = call_haiku if sess["family"] == "haiku" else call_sol
    transport = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        tmp = tempfile.mkdtemp(prefix="riskprobe-", dir="/tmp")
        started = now()
        try:
            p, info, response, err = call(text, tmp)
        except subprocess.TimeoutExpired as e:
            p, info, response, err = None, {"exit_code": None}, None, f"timeout after {e.timeout}s"
        finished = now()
        leftovers = os.listdir(tmp)
        shutil.rmtree(tmp, ignore_errors=True)
        suffix = "" if err is None else f".attempt{attempt}"
        if p is not None:
            (rdir / f"stdout{suffix}.txt").write_text(p.stdout)
            (rdir / f"stderr{suffix}.txt").write_text(p.stderr)
        if err is None:
            (rdir / "response.txt").write_text(response)
            meta = {"session": sid, "family": sess["family"], "condition": sess["condition"],
                    "attempt": attempt, "started": started, "finished": finished, "tmpdir": tmp,
                    "tmpdir_leftovers": leftovers, "transport_errors": transport, **info}
            (rdir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
            return sid, f"ok (attempt {attempt})"
        transport.append({"attempt": attempt, "started": started, "summary": err})
    meta = {"session": sid, "family": sess["family"], "condition": sess["condition"], "failed": True,
            "transport_errors": transport}
    (rdir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    return sid, "FAILED: " + "; ".join(t["summary"] for t in transport)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True, choices=["haiku", "sol"])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    sessions = [s for s in json.loads((HERE / "sessions.json").read_text())["sessions"]
                if s["family"] == args.family and not (HERE / "runs" / s["session"] / "response.txt").exists()]
    if args.limit:
        sessions = sessions[:args.limit]
    with ThreadPoolExecutor(args.workers) as ex:
        for sid, status in ex.map(run_session, sessions):
            print(sid, status, flush=True)
    print(f"{len(sessions)} sessions attempted")


if __name__ == "__main__":
    main()
