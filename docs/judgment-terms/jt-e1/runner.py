"""JT-E1 sealed proxy reader. Run from repo root: uv run python docs/judgment-terms/jt-e1/runner.py."""
from __future__ import annotations

import csv
import json
import os
from pathlib import Path
import random
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
MODEL = "claude-sonnet-5-5"
PICK = ["zsh", "/home/seyran/code/manage-agents/pick-claude-account.sh"]
PROMPT = (
    "Read only the source and displayed lines below as a reader of this document. "
    "For the named conclusion, answer in exactly this format: "
    "`CLASS: SETTLED|TURNS|CONDITIONAL; DECIDER: <name or NONE>; WHY: <one sentence>`. "
    "SETTLED means it holds whatever is judged. TURNS means two admissible judgments can change it. "
    "CONDITIONAL means it is certified only given a judgment criterion. "
    "Name the decider if the text names one; otherwise say NONE. Do not use outside knowledge."
)
CALL_CAP = 100
CW_CAP = 3_000_000
RESERVE_CW = 25_000


def items():
    with (HERE / "items.tsv").open(newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="|"))
    assert len(rows) == 40 and len({r["id"] for r in rows}) == 40
    assert sum(r["id"].startswith("U") for r in rows) == 20
    assert sum(r["id"].startswith("C") for r in rows) == 20
    return rows


def render(row, arm):
    atom, who, conclusion = row["atom"], row["decider"], row["conclusion"]
    if arm == "identifier":
        legend = f'Open reading: "{row["subject"]}" is classified as "{row["predicate"]}".'
        line = {
            "turns": f'left_to({row["predicate"]}; decider={who}): {conclusion}',
            "settled": f"settled: {conclusion}",
            "conditional": f'conflict_free_given({row["predicate"]}): {conclusion}',
        }[row["answer"]]
    elif arm == "english":
        legend = (f"Whether {atom} is a judgment; the text does not say who makes it."
                  if who == "unstated" else f"Whether {atom} is a judgment for {who}.")
        line = {
            "turns": (f"Left to {who}: these two admissible completions give different answers and "
                      f"differ on whether {atom} "
                      + ("(the text does not say who makes it)." if who == "unstated"
                         else f"(a judgment for {who}).")),
            "settled": f"Settled: whatever is judged here, the text requires {conclusion}.",
            "conditional": f"Conflict-free, given these sentences: {row['source']}. {conclusion}.",
        }[row["answer"]]
    else:
        raise ValueError(arm)
    return f"{PROMPT}\n\nSOURCE: {row['source']}\nCONCLUSION: {conclusion}\n{legend}\n{line}\n"


def parse_answer(raw):
    match = re.search(r"CLASS:\s*(SETTLED|TURNS|CONDITIONAL)\s*;\s*DECIDER:\s*([^;\n]+)", raw, re.I)
    if not match:
        return None, None
    return match.group(1).upper(), match.group(2).strip().upper()


def score(row, raw):
    cls, decider = parse_answer(raw)
    expected = row["answer"].upper()
    expected_decider = "NONE" if row["decider"] == "unstated" or expected == "SETTLED" else row["decider"].upper()
    correct = cls == expected and decider == expected_decider
    critical = expected in {"TURNS", "CONDITIONAL"} and (
        cls == "SETTLED" or bool(re.search(r"\b(?:is|was|remains)\s+(?:settled|checked)\b", raw, re.I))
    )
    return {"class": cls, "decider": decider, "correct": correct, "critical": critical}


def usage_cw(result):
    usage = result.get("usage", {})
    return sum(int(usage.get(k, 0)) for k in (
        "input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))


def within_budget(calls, cw):
    return calls < CALL_CAP and cw + RESERVE_CW <= CW_CAP


def existing():
    return [json.loads(p.read_text()) for p in RAW.glob("*.json")]


def call(prompt):
    env = os.environ.copy()
    for key in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "CLAUDE_CODE_USE_BEDROCK",
                "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY"):
        env.pop(key, None)
    env["PICK_SHORT"] = "1"
    env["PICK_LIGHT"] = "1"
    account = subprocess.run(PICK, env=env, capture_output=True, text=True, check=True).stdout.strip()
    env["CLAUDE_CONFIG_DIR"] = account
    auth = subprocess.run(["claude", "auth", "status", "--json"], env=env,
                          capture_output=True, text=True, check=True)
    auth_state = json.loads(auth.stdout)
    if auth_state.get("authMethod") != "claude.ai" or not auth_state.get("subscriptionType"):
        raise RuntimeError("selected account is not a Claude subscription")
    with tempfile.TemporaryDirectory(prefix="jt-e1-reader-") as cwd:
        proc = subprocess.run(
            ["claude", "-p", "--model", MODEL, "--tools", "", "--strict-mcp-config",
             "--disable-slash-commands", "--output-format", "json"],
            input=prompt, text=True, capture_output=True, cwd=cwd, env=env, timeout=600)
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        result = {"raw_stdout": proc.stdout}
    return {"account": Path(account).name, "returncode": proc.returncode,
            "stderr": proc.stderr[-2000:], "result": result, "cw": usage_cw(result)}


def main():
    RAW.mkdir(exist_ok=True)
    rows = items()
    jobs = [(r, arm) for r in rows for arm in ("identifier", "english")]
    random.Random(20261029).shuffle(jobs)
    records = existing()
    seen = {(r["id"], r["arm"]) for r in records}
    calls, cw = len(records), sum(r["call"]["cw"] for r in records)
    for row, arm in jobs:
        if (row["id"], arm) in seen:
            continue
        if not within_budget(calls, cw):
            print(f"STOP cap: {calls} calls, {cw} CW", flush=True)
            return 2
        prompt = render(row, arm)
        try:
            response = call(prompt)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, RuntimeError) as exc:
            print(f"STOP account or call unavailable: {exc}", flush=True)
            return 2
        result = response["result"]
        rec = {"id": row["id"], "arm": arm, "prompt": prompt, "call": response,
               "raw_answer": result.get("result", "")}
        (RAW / f"{row['id']}-{arm}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n")
        calls += 1
        cw += response["cw"]
        print(f"{calls}/80 {row['id']} {arm}: rc={response['returncode']} cw={cw}", flush=True)
        if response["returncode"] or result.get("is_error") or result.get("subtype") != "success":
            print("STOP failed CLI result; inspect raw record", flush=True)
            return 2
        if result.get("usage", {}).get("fallback_credit"):
            print("STOP paid-credit fallback reported; inspect raw record", flush=True)
            return 2
        models = result.get("modelUsage", {})
        if models and MODEL not in models:
            print(f"STOP unexpected model: {list(models)}", flush=True)
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
