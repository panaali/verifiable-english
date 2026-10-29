"""DF-E1 blind reader: one subscription Sonnet call for each preregistered item and form."""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
MODEL = "claude-sonnet-5-5"
CLAUDE = "/home/seyran/.local/bin/claude"
PICKER = "/home/seyran/code/manage-agents/pick-claude-account.sh"
QUESTION = ("Could the conclusion be false in a situation the text allows, if the decider finds that an exception "
            "applies, a party turns the rule off, or the lower-ranked consideration outweighs the higher one?")
MAX_CALLS = 40
MAX_CW = 3_000_000
RESERVE_CW = 100_000
ANSWER = re.compile(r"^ANSWER:\s*(YES|NO)\s*$", re.IGNORECASE | re.MULTILINE)


def items():
    rows = json.loads((HERE / "items.json").read_text())
    assert len(rows) == 24 and len({r["id"] for r in rows}) == 24
    assert sum(r["expected"] == "yes" for r in rows) == 12
    assert sum(r["expected"] == "no" for r in rows) == 12
    assert sum("short" in r["rendered"] for r in rows) == 6
    return rows


def jobs(rows):
    return [(r, form) for r in rows for form in ("long", "short") if form in r["rendered"]]


def prompt(row, form):
    return (f"Rule text:\n{row['rule_text']}\n\nRendered answer:\n" +
            "\n".join(row["rendered"][form]) + f"\n\n{QUESTION}\n\nANSWER: YES or NO")


def parse(reply):
    found = ANSWER.findall(reply or "")
    return found[-1].lower() if len(found) == 1 else None


def cw(usage):
    if not isinstance(usage, dict):
        return RESERVE_CW
    fields = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
    if any(type(usage.get(key)) is not int or usage[key] < 0 for key in fields):
        return RESERVE_CW
    return int(0.68 * (usage.get("input_tokens", 0) + 1.2 * usage.get("cache_creation_input_tokens", 0)
                       + 0.025 * usage.get("cache_read_input_tokens", 0) + 5 * usage.get("output_tokens", 0)))


def account():
    result = subprocess.run(["zsh", PICKER], capture_output=True, text=True,
                            env=dict(os.environ, PICK_SHORT="1", PICK_NOWAIT="1"), check=True)
    cfg = result.stdout.strip()
    auth = json.loads((Path(cfg) / ".claude.json").read_text())
    if not auth.get("oauthAccount") or auth.get("primaryApiKey"):
        raise RuntimeError("the picked account is not an OAuth subscription; paid credits are forbidden")
    return cfg


def prereg_committed():
    paths = ["PRE-REGISTRATION.md", "items.json", "runner.py"]
    for name in paths:
        rel = f"docs/defeasible/df-e1/{name}"
        stored = subprocess.run(["git", "show", f"HEAD:{rel}"], capture_output=True, check=True).stdout
        if stored != (HERE / name).read_bytes():
            raise RuntimeError(f"commit the final {name} before the first reader call")


def run():
    prereg_committed()
    rows = items()
    queue = jobs(rows)
    if len(queue) > MAX_CALLS:
        raise RuntimeError("pre-registration exceeds the 40-call cap")
    raw = HERE / "raw"
    raw.mkdir(exist_ok=True)
    cfg = account()
    for row, form in queue:
        path = raw / f"{row['id']}__{form}.json"
        if path.exists():
            continue
        saved = [json.loads(p.read_text()) for p in raw.glob("*.json")]
        used = sum(rec.get("charged_cw", RESERVE_CW) for rec in saved)
        if len(saved) >= MAX_CALLS or used + RESERVE_CW > MAX_CW:
            raise RuntimeError(f"reader cap reached: {len(saved)} calls, {used} CW")
        body = prompt(row, form)
        env = {key: value for key, value in os.environ.items() if not key.startswith("ANTHROPIC_")}
        env["CLAUDE_CONFIG_DIR"] = cfg
        command = [CLAUDE, "-p", "--model", MODEL, "--effort", "low", "--output-format", "json",
                   "--max-turns", "1", "--tools", "", "--strict-mcp-config", "--safe-mode",
                   "--setting-sources", "", "--disable-slash-commands"]
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with tempfile.TemporaryDirectory(prefix="df-e1-") as tmp:
            try:
                result = subprocess.run(command, input=body, text=True, capture_output=True, cwd=tmp,
                                        env=env, timeout=600)
            except subprocess.TimeoutExpired as error:
                result = None
                output = {"error": "timeout", "stderr": str(error)[-500:]}
        if result is not None:
            try:
                output = json.loads(result.stdout)
            except json.JSONDecodeError:
                output = {"error": "invalid CLI JSON", "stderr": result.stderr[-500:]}
        usage = output.get("usage")
        record = {"id": row["id"], "form": form, "model": MODEL, "account": Path(cfg).name,
                  "prompt_sha256": hashlib.sha256(body.encode()).hexdigest(), "started": started,
                  "finished": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  "exit_code": result.returncode if result is not None else None,
                  "reply": output.get("result"), "usage": usage, "charged_cw": cw(usage),
                  "cli_error": output.get("error"), "subtype": output.get("subtype")}
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
        if (record["exit_code"] != 0 or output.get("is_error") or output.get("subtype") != "success"
                or set(output.get("modelUsage") or {}) != {MODEL} or parse(record["reply"]) is None
                or not isinstance(usage, dict) or usage.get("fallback_credit") is not None):
            raise RuntimeError(f"reader call {row['id']} {form} failed; raw answer saved, stop for inspection")
        print(row["id"], form, parse(record["reply"]), record["charged_cw"], "CW", flush=True)


def score():
    rows = items()
    raw = HERE / "raw"
    expected = {(r["id"], form): r for r, form in jobs(rows)}
    got = {}
    for path in raw.glob("*.json"):
        record = json.loads(path.read_text())
        key = (record.get("id"), record.get("form"))
        if key not in expected or key in got or path.name != f"{key[0]}__{key[1]}.json":
            raise ValueError(f"extra or duplicated answer: {path}")
        if record.get("prompt_sha256") != hashlib.sha256(prompt(expected[key], key[1]).encode()).hexdigest():
            raise ValueError(f"prompt changed: {path}")
        got[key] = parse(record.get("reply"))
    if got.keys() != expected.keys() or None in got.values():
        raise ValueError("missing or unreadable reader answers")
    strict = [r for r in rows if r["expected"] == "no"]
    needs = [r for r in rows if r["expected"] == "yes"]
    strict_wrong = sum(got[(r["id"], "long")] == "yes" for r in strict)
    long_wrong = sum(got[(r["id"], "long")] == "no" for r in needs)
    eligible = [r for r in needs if "short" in r["rendered"]]
    short_wrong = sum(got[(r["id"], "short")] == "no" for r in eligible)
    long_eligible_wrong = sum(got[(r["id"], "long")] == "no" for r in eligible)
    long_pass = long_wrong <= 1 and strict_wrong <= 1
    short_pass = short_wrong <= 1 and strict_wrong <= 1
    outcome = ("DF-3 waits for a redesign of the wording" if not long_pass else
               "short form KEPT" if short_pass and short_wrong < long_eligible_wrong else "short form DROPPED")
    return {"by_item": {f"{id}__{form}": answer for (id, form), answer in got.items()},
            "long": {"needs_read_strict": long_wrong, "strict_read_needs": strict_wrong, "pass": long_pass},
            "short": {"needs_read_strict": short_wrong, "strict_read_needs": strict_wrong, "pass": short_pass},
            "short_eligible": {"long_misreadings": long_eligible_wrong, "short_misreadings": short_wrong},
            "outcome": outcome, "calls": len(got),
            "charged_cw": sum(json.loads(p.read_text())["charged_cw"] for p in raw.glob("*.json"))}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["run", "score", "prompt"])
    parser.add_argument("item", nargs="?")
    parser.add_argument("form", nargs="?")
    args = parser.parse_args()
    if args.action == "run":
        run()
    elif args.action == "score":
        print(json.dumps(score(), indent=2))
    else:
        row = next(r for r in items() if r["id"] == args.item)
        print(prompt(row, args.form))
