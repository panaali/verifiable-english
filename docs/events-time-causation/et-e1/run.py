#!/usr/bin/env python3
"""ET-E1: comprehension of the explicit event and time wordings (events-time-causation-PLAN.md ET-E1).

    python3 run.py render <item-id>       print the exact prompt of one item
    python3 run.py run [--workers W]      ask Sonnet 5.5 every item, samples_per_item times; skips saved answers
    python3 run.py score [--write]        score raw/ against items.json; --write saves results.json

Each call runs once, in a fresh empty temporary directory outside the repository, with no tools, through the
`claude` CLI on the account pick-claude-account.sh picks (an OAuth subscription login; the runner refuses an
account without one and strips API-key variables). Only transport errors are retried, and each is recorded.
The pre-registration (PREREGISTRATION.md, items.json, prompt.txt, this file) is committed before the first call.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
CLAUDE = "/home/seyran/.local/bin/claude"
PICKER = "/home/seyran/code/manage-agents/pick-claude-account.sh"
MODEL = "claude-sonnet-5-5"
MAX_ATTEMPTS = 3
CALL_TIMEOUT_S = 600
ISOLATION = ["--tools", "", "--strict-mcp-config", "--safe-mode", "--setting-sources", "", "--disable-slash-commands"]
ANSWER = re.compile(r"^\s*\**ANSWER:?\**\s*:?\s*\**([A-Z])\b", re.MULTILINE)


def load_items(path=HERE / "items.json"):
    return json.loads(Path(path).read_text())


def options_of(spec, item):
    opts = item["options"]
    return spec["option_sets"][opts] if isinstance(opts, str) else opts


def prompt_parts(spec, item, template_path=HERE / "prompt.txt"):
    raw = Path(template_path).read_text()
    system, user = raw.split("=== USER ===\n")
    system = system.removeprefix("=== SYSTEM ===\n").strip()
    situation = f"\nSituation:\n{item['situation']}\n" if item["situation"] else ""
    options = "\n".join(f"{k}. {v}" for k, v in options_of(spec, item))
    user = user.format(text=item["text"], situation_block=situation, question=item["question"], options=options)
    return system, user


def parse_answer(reply, letters):
    """The letter of the last ANSWER line; None when there is none or it names no option."""
    found = ANSWER.findall(reply or "")
    if not found or found[-1] not in letters:
        return None
    return found[-1]


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def pick_account():
    cfg = subprocess.run(["zsh", PICKER], capture_output=True, text=True, env=dict(os.environ, PICK_SHORT="1"),
                         check=True).stdout.strip()
    conf = json.loads((Path(cfg) / ".claude.json").read_text())
    if not conf.get("oauthAccount") or conf.get("primaryApiKey"):
        sys.exit(f"STOP: {cfg} is not a subscription (OAuth) login; ET-E1 runs on no paid API credits")
    return cfg


def call(cfg, system, user):
    env = {k: v for k, v in os.environ.items() if not k.startswith("ANTHROPIC_")}
    env["CLAUDE_CONFIG_DIR"] = cfg
    cmd = [CLAUDE, "-p", "--model", MODEL, "--output-format", "json", *ISOLATION, "--system-prompt", system]
    with tempfile.TemporaryDirectory(prefix="et-e1-") as tmp:
        p = subprocess.run(cmd, input=user, capture_output=True, text=True, cwd=tmp, env=env, timeout=CALL_TIMEOUT_S)
    info = {"exit_code": p.returncode}
    try:
        out = json.loads(p.stdout)
    except json.JSONDecodeError:
        return info, None, f"no JSON on stdout: {p.stderr[-300:]}"
    info |= {"cli_session_id": out.get("session_id"), "model_usage": sorted((out.get("modelUsage") or {}).keys()),
             "usage": out.get("usage"), "num_turns": out.get("num_turns")}
    if p.returncode != 0 or out.get("is_error") or out.get("subtype") != "success":
        return info, None, f"CLI error: subtype={out.get('subtype')} result={str(out.get('result'))[:300]}"
    return info, out.get("result", ""), None


def run_one(cfg, spec, item, k):
    path = RAW / f"{item['id']}__s{k}.json"
    if path.exists():
        return "saved"
    system, user = prompt_parts(spec, item)
    record = {"item": item["id"], "sample": k, "model": MODEL, "account": Path(cfg).name,
              "prompt_sha256": hashlib.sha256((system + "\n" + user).encode()).hexdigest(),
              "started": now(), "errors": []}
    for _ in range(MAX_ATTEMPTS):
        try:
            info, reply, err = call(cfg, system, user)
        except subprocess.TimeoutExpired:
            info, reply, err = {}, None, "timeout"
        if err is None:
            record |= {"finished": now(), "cli": info, "reply": reply}
            path.write_text(json.dumps(record, indent=1) + "\n")
            return "ok"
        record["errors"].append(err)
    record |= {"finished": now(), "reply": None}
    path.write_text(json.dumps(record, indent=1) + "\n")
    return "missing"


def run(workers):
    spec = load_items()
    RAW.mkdir(exist_ok=True)
    cfg = pick_account()
    print(f"account {Path(cfg).name}, model {MODEL}", flush=True)
    jobs = [(item, k) for item in spec["items"] for k in range(spec["samples_per_item"])]
    with ThreadPoolExecutor(workers) as pool:
        done = list(pool.map(lambda j: run_one(cfg, spec, *j), jobs))
    print({s: done.count(s) for s in sorted(set(done))})


def load_raw(spec, raw_dir=RAW):
    """Bind every saved answer to the pre-registration: a known item, a sample in range, no duplicate, none missing."""
    ids = {i["id"] for i in spec["items"]}
    n = spec["samples_per_item"]
    answers = {}
    for path in sorted(Path(raw_dir).glob("*.json")):
        rec = json.loads(path.read_text())
        key = (rec.get("item"), rec.get("sample"))
        if key[0] not in ids or type(key[1]) is not int or not 0 <= key[1] < n:
            raise ValueError(f"{path.name}: not a pre-registered item and sample: {key}")
        if path.name != f"{key[0]}__s{key[1]}.json" or key in answers:
            raise ValueError(f"{path.name}: duplicate or misnamed answer for {key}")
        answers[key] = rec.get("reply")
    absent = [(i, k) for i in sorted(ids) for k in range(n) if (i, k) not in answers]
    if absent:
        raise ValueError(f"{len(absent)} answers absent, first {absent[0]}")
    return answers


def score(spec, answers):
    bar = spec["bar"]
    by_item = {}
    for item in spec["items"]:
        letters = [k for k, _ in options_of(spec, item)]
        got = [parse_answer(answers[(item["id"], k)], letters) for k in range(spec["samples_per_item"])]
        by_item[item["id"]] = {"group": item["group"], "expected": item["expected"], "answers": got,
                               "correct": sum(g == item["expected"] for g in got)}
    wordings = []
    for w in spec["wordings"]:
        rows = [r for r in by_item.values() if r["group"] == w["group"]]
        total = len(rows) * spec["samples_per_item"]
        correct = sum(r["correct"] for r in rows)
        wordings.append({**w, "correct": correct, "total": total,
                         "verdict": "PASS" if total and correct >= bar["per_wording"] * total else "BELOW BAR"})
    pairs = []
    for u1, u2 in spec["until_pairs"]:
        a, b = by_item[u1], by_item[u2]
        apart = sum(x == a["expected"] and y == b["expected"] for x, y in zip(a["answers"], b["answers"]))
        pairs.append({"u1": u1, "u2": u2, "told_apart": apart, "total": spec["samples_per_item"]})
    apart = sum(p["told_apart"] for p in pairs)
    total = sum(p["total"] for p in pairs)
    until = {"told_apart": apart, "total": total,
             "verdict": "PASS" if total and apart >= bar["until_told_apart"] * total else "BELOW BAR"}
    return {"model": MODEL, "items": by_item, "wordings": wordings, "until_pairs": pairs, "until": until}


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("render").add_argument("item")
    sub.add_parser("run").add_argument("--workers", type=int, default=4)
    sub.add_parser("score").add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    spec = load_items()
    if args.cmd == "render":
        item = next(i for i in spec["items"] if i["id"] == args.item)
        system, user = prompt_parts(spec, item)
        print(f"[system]\n{system}\n[user]\n{user}")
    elif args.cmd == "run":
        run(args.workers)
    else:
        result = score(spec, load_raw(spec))
        for w in result["wordings"]:
            print(f"{w['group']:16} {w['correct']:3}/{w['total']:<3} {w['verdict']}")
        u = result["until"]
        print(f"{'until told apart':16} {u['told_apart']:3}/{u['total']:<3} {u['verdict']}")
        if args.write:
            (HERE / "results.json").write_text(json.dumps(result, indent=1) + "\n")


if __name__ == "__main__":
    main()
