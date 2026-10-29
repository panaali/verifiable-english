"""DF-E1 blind reader: one subscription Sonnet call for each preregistered item and form."""
from __future__ import annotations

import argparse
import datetime
import fcntl
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
# The subscription CLI has no enforceable output-token ceiling. A transport may
# set this only when it can enforce a bound on the *billed* charge before dispatch.
DISPATCH_CW_BOUND = None
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
    if not isinstance(reply, str):
        return None
    found = ANSWER.findall(reply)
    return found[-1].lower() if len(found) == 1 else None


def cw(usage):
    if not valid_usage(usage):
        return RESERVE_CW
    return int(0.68 * (usage.get("input_tokens", 0) + 1.2 * usage.get("cache_creation_input_tokens", 0)
                       + 0.025 * usage.get("cache_read_input_tokens", 0) + 5 * usage.get("output_tokens", 0)))


def valid_usage(usage):
    fields = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
    return (isinstance(usage, dict) and usage.get("fallback_credit") is None
            and all(type(usage.get(key)) is int and usage[key] >= 0 for key in fields))


def valid_answer(record):
    usage = record.get("usage")
    model_usage = record.get("modelUsage")
    return (type(record.get("exit_code")) is int and record["exit_code"] == 0
            and record.get("subtype") == "success" and record.get("cli_error") is None
            and record.get("is_error") is False
            and record.get("model") == MODEL and isinstance(model_usage, dict)
            and set(model_usage) == {MODEL} and isinstance(usage, dict)
            and valid_usage(usage) and type(record.get("reserved_cw")) is int
            and record["reserved_cw"] > 0 and type(record.get("charged_cw")) is int
            and record["charged_cw"] == max(record["reserved_cw"], cw(usage))
            and parse(record.get("reply")) is not None)


def valid_record(record, row, form):
    return (isinstance(record, dict) and record.get("id") == row["id"]
            and record.get("form") == form
            and record.get("prompt_sha256") == hashlib.sha256(prompt(row, form).encode()).hexdigest()
            and valid_answer(record))


def save(path, record):
    """Replace a reservation atomically and durably, including across a crash."""
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, prefix=".attempt-", delete=False) as out:
        json.dump(record, out, indent=2, ensure_ascii=False)
        out.write("\n")
        out.flush()
        os.fsync(out.fileno())
        tmp = Path(out.name)
    os.replace(tmp, path)
    descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


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
    # The lock covers reconciliation, reservation and dispatch. Another process
    # cannot observe spare capacity while this process is making a call.
    with (raw / ".lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        _run_locked(queue, raw)


def _run_locked(queue, raw):
    bound = DISPATCH_CW_BOUND
    if type(bound) is not int or bound <= 0:
        raise RuntimeError("reader transport has no enforceable per-call CW bound")
    known = {f"{row['id']}__{form}.json": (row, form) for row, form in queue}
    saved = {}
    for path in raw.glob("*.json"):
        if path.name not in known:
            raise RuntimeError(f"unexpected reader record: {path}")
        try:
            record = json.loads(path.read_text())
        except (ValueError, OSError) as error:
            raise RuntimeError(f"unreadable reader record: {path}") from error
        if not valid_record(record, *known[path.name]):
            raise RuntimeError(f"reader call needs inspection: {path}")
        saved[path.name] = record
    cfg = account()
    for row, form in queue:
        path = raw / f"{row['id']}__{form}.json"
        if path.name in saved:
            continue
        used = sum(rec["charged_cw"] for rec in saved.values())
        if len(saved) >= MAX_CALLS or used + bound > MAX_CW:
            raise RuntimeError(f"reader cap reached: {len(saved)} calls, {used} CW")
        body = prompt(row, form)
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        record = {"id": row["id"], "form": form, "model": MODEL, "account": Path(cfg).name,
                  "prompt_sha256": hashlib.sha256(body.encode()).hexdigest(), "started": started,
                  "finished": None, "exit_code": None, "reply": None, "usage": None,
                  "charged_cw": bound, "reserved_cw": bound, "cli_error": "attempt reserved", "subtype": None,
                  "is_error": True, "modelUsage": None}
        save(path, record)
        saved[path.name] = record
        env = {key: value for key, value in os.environ.items() if not key.startswith("ANTHROPIC_")}
        env["CLAUDE_CONFIG_DIR"] = cfg
        command = [CLAUDE, "-p", "--model", MODEL, "--effort", "low", "--output-format", "json",
                   "--max-turns", "1", "--tools", "", "--strict-mcp-config", "--safe-mode",
                   "--setting-sources", "", "--disable-slash-commands"]
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
        if not isinstance(output, dict):
            output = {"error": "invalid CLI JSON object", "raw_output": result.stdout[:5000]}
        usage = output.get("usage")
        record.update(finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      exit_code=result.returncode if result is not None else None,
                      reply=output.get("result"), usage=usage, charged_cw=max(bound, cw(usage)),
                      cli_error=output.get("error"), subtype=output.get("subtype"),
                      is_error=output.get("is_error"), modelUsage=output.get("modelUsage"))
        save(path, record)
        if record["charged_cw"] > bound or not valid_answer(record):
            raise RuntimeError(f"reader call {row['id']} {form} failed; raw answer saved, stop for inspection")
        print(row["id"], form, parse(record["reply"]), record["charged_cw"], "CW", flush=True)


def score():
    rows = items()
    raw = HERE / "raw"
    expected = {(r["id"], form): r for r, form in jobs(rows)}
    got = {}
    for path in raw.glob("*.json"):
        try:
            record = json.loads(path.read_text())
        except (ValueError, OSError) as error:
            raise ValueError(f"unreadable reader answer: {path}") from error
        if not isinstance(record, dict):
            raise ValueError(f"unreadable reader answer: {path}")
        key = (record.get("id"), record.get("form"))
        if key not in expected or key in got or path.name != f"{key[0]}__{key[1]}.json":
            raise ValueError(f"extra or duplicated answer: {path}")
        if not valid_record(record, expected[key], key[1]):
            raise ValueError(f"failed or unverified reader answer: {path}")
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
