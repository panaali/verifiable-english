#!/usr/bin/env python3
"""Run the two preregistered blind subscription raters, one call each."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CLASSES = {"judgment", "classification", "exception", "attitude", "proportion"}
MANAGE = Path("/home/seyran/code/manage-agents")


def input_rows():
    rows = json.loads((HERE / "INPUT.json").read_text())
    assert len(rows) == 60
    assert len({row["id"] for row in rows}) == 60
    assert all(set(row) == {"id", "pilot", "term", "source_sentence"} for row in rows)
    return rows


def prompt():
    lines = (HERE / "PRE-REGISTRATION.md").read_text().splitlines()
    start = lines.index("## Blind rater prompt")
    end = lines.index("Two different models rate all 60 terms independently: one Claude via the")
    rule = "\n".join(line[2:] for line in lines[start:end] if line.startswith("> "))
    return rule + "\n\nRecords:\n" + json.dumps(input_rows(), ensure_ascii=False)


def parse_answer(raw: str):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    answer = json.loads(raw)
    expected = input_rows()
    if not isinstance(answer, list) or len(answer) != 60:
        raise ValueError("answer must be an array of 60 rows")
    for a, e in zip(answer, expected, strict=True):
        if not isinstance(a, dict) or set(a) != {"id", "class"}:
            raise ValueError("answer row shape")
        if type(a["id"]) is not str or a["id"] != e["id"]:
            raise ValueError("answer id or order")
        if type(a["class"]) is not str or a["class"] not in CLASSES:
            raise ValueError("answer class")
    return answer


def clean_env():
    env = os.environ.copy()
    for key in list(env):
        if key.endswith("API_KEY") or key in {"OPENAI_BASE_URL", "ANTHROPIC_BASE_URL"}:
            env.pop(key)
    return env


def picked_claude(env):
    if not subprocess.run(["zsh", str(MANAGE / "codex-allowed.sh")],
                          capture_output=True, text=True, env=env, timeout=60).returncode == 0:
        raise RuntimeError("Codex is not allowed; stop after preregistration")
    pick_env = env | {"PICK_NOWAIT": "1", "ACCOUNTS_DIR": "/tmp/jt-e3-accounts"}
    result = subprocess.run(["zsh", str(MANAGE / "pick-claude-account.sh")],
                            capture_output=True, text=True, env=pick_env, timeout=120)
    account = result.stdout.strip()
    if result.returncode or not account.startswith("/home/seyran/.agent-accounts/claude-"):
        raise RuntimeError("Claude account picker found no eligible account")
    return account


def run_rater(rater):
    output = HERE / f"{rater}.json"
    if output.exists() or (HERE / f"{rater}.raw.txt").exists():
        raise RuntimeError(f"{rater} was already called; never overwrite or retry a rater")
    env = clean_env()
    if rater == "claude":
        account = picked_claude(env)
        env["CLAUDE_CONFIG_DIR"] = account
        cmd = ["claude", "-p", "--model", "sonnet", "--max-turns", "1",
               "--restricted", "--no-session-persistence", "--output-format", "json", prompt()]
    else:
        allowed = subprocess.run(["zsh", str(MANAGE / "codex-allowed.sh")],
                                 capture_output=True, text=True, env=env, timeout=60)
        if allowed.returncode:
            raise RuntimeError("Codex is not allowed; stop after preregistration")
        account = None
        cmd = ["codex", "exec", "--skip-git-repo-check", "--ephemeral", "--ignore-rules",
               "-s", "read-only", "-C", "/tmp", "-o", str(HERE / "codex.message.txt"), "-"]
    # A single complete batch per model: two rater calls, well below the ten-call cap.
    call = subprocess.run(cmd, input=prompt() if rater == "codex" else None,
                          capture_output=True, text=True, cwd="/tmp", env=env, timeout=1200)
    (HERE / f"{rater}.raw.txt").write_text(call.stdout)
    (HERE / f"{rater}.stderr.txt").write_text(call.stderr)
    if call.returncode:
        raise RuntimeError(f"{rater} call failed with exit {call.returncode}; raw output retained")
    if rater == "claude":
        wrapper = json.loads(call.stdout)
        answer_text = wrapper["result"]
    else:
        answer_text = (HERE / "codex.message.txt").read_text()
    answer = parse_answer(answer_text)
    output.write_text(json.dumps(answer, indent=2) + "\n")
    (HERE / f"{rater}.provenance.json").write_text(json.dumps({
        "account": account, "command": cmd[:4], "input_rows": 60,
        "prompt_bytes": len(prompt().encode()), "output_bytes": len(answer_text.encode()),
        "calls": 1, "payment": "subscription CLI"
    }, indent=2) + "\n")
    print(f"{rater}: 60 validated ratings")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("rater", choices=["claude", "codex"])
    run_rater(parser.parse_args().rater)
