"""JT-E1r blinded reader calls and scoring; display bytes come from render.py."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import render

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
MODEL = "claude-sonnet-5-5"
PICKER = "/home/seyran/code/manage-agents/pick-claude-account.sh"
CALL_CAP = 100
CW_CAP = 3_000_000
RESERVE_CW = 25_000
RAW_CAP = 2_000_000
PROMPT = (
    "Read only the source and displayed lines below as a reader of this document. "
    "For the named conclusion, answer in exactly this format: "
    "`CLASS: SETTLED|TURNS|CONDITIONAL; DECIDER: <name or NONE>; WHY: <one sentence>`. "
    "SETTLED means it holds whatever is judged. TURNS means two admissible judgments can change it. "
    "CONDITIONAL means it is certified only given a judgment criterion. "
    "Name the decider if the text names one; otherwise say NONE. Do not use outside knowledge."
)
ANSWER = re.compile(r"CLASS:\s*(SETTLED|TURNS|CONDITIONAL)\s*;\s*DECIDER:\s*([^;\n]+)", re.I)
USAGE_KEYS = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")


def prompt(row, arm):
    old, new = render.displays(row)
    shown = old if arm == "identifier" else new
    return PROMPT + "\n\n" + render.common_text(row) + shown.decode("utf-8")


def parse_answer(answer):
    found = ANSWER.findall(answer)
    return (found[0][0].upper(), found[0][1].strip().upper()) if len(found) == 1 else (None, None)


def score(row, answer):
    cls, decider = parse_answer(answer)
    expected = row["answer"].upper()
    who = "NONE" if row["decider"] == "unstated" else row["decider"].upper()
    critical = expected in {"TURNS", "CONDITIONAL"} and (
        cls == "SETTLED" or bool(re.search(r"\b(?:is|was|remains)\s+(?:settled|checked)\b", answer, re.I)))
    return {"correct": cls == expected and decider == who, "critical": critical,
            "class": cls, "decider": decider}


def record_score(row, record):
    """A failed call counts incorrect and is not a misreading, so its answer is never scored."""
    if record.get("error"):
        return {"correct": False, "critical": False, "class": None, "decider": None}
    return score(row, record["answer"])


def usage_cw(result):
    if not isinstance(result, dict):
        raise RuntimeError("missing CLI wrapper")
    usage = result.get("usage")
    if not isinstance(usage, dict) or usage.get("fallback_credit", "missing") is not None:
        raise RuntimeError("missing usage or paid-credit fallback")
    if any(type(usage.get(key)) is not int or usage[key] < 0 for key in USAGE_KEYS):
        raise RuntimeError("missing or malformed usage counters")
    return sum(usage[key] for key in USAGE_KEYS)


def usage_summary(wrapper):
    """Keep enough of an oversized response to audit a known CW charge."""
    try:
        usage_cw(wrapper)
    except RuntimeError:
        return {}
    usage = wrapper["usage"]
    return {"usage": {key: usage[key] for key in USAGE_KEYS} | {"fallback_credit": None}}


def record_cw(record):
    if record.get("state") == "dispatched":
        raise RuntimeError("reader dispatch has no completed usage")
    cli = record.get("cli")
    if not record.get("error"):
        if (not isinstance(cli, dict) or record.get("exit_code") != 0
                or cli.get("subtype") != "success" or cli.get("is_error") is not False
                or not isinstance(cli.get("modelUsage"), dict)
                or set(cli["modelUsage"]) != {MODEL}
                or type(cli.get("result")) is not str
                or record.get("answer") != cli["result"]):
            raise RuntimeError("raw record is not a successful reader result")
    elif type(record["error"]) is not str or not record["error"] or record.get("answer") != "":
        raise RuntimeError("raw record has invalid failure state")
    reported = usage_cw(cli)
    charged = max(RESERVE_CW, reported) if record.get("error") else reported
    if type(record.get("charged_cw")) is not int or record["charged_cw"] != charged:
        raise RuntimeError("raw record has incorrect CW charge")
    return charged


def save_record(path, record):
    """Replace a journal entry durably before a call or a cap decision."""
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     prefix=".reader-", delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(record, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def within_caps(calls, charged):
    return calls < CALL_CAP and charged + RESERVE_CW <= CW_CAP


def committed():
    for name in ("PRE-REGISTRATION.md", "items.tsv", "render.py", "runner.py"):
        relative = f"docs/judgment-terms/jt-e1r/{name}"
        saved = subprocess.run(["git", "show", f"HEAD:{relative}"], capture_output=True, check=True).stdout
        if saved != (HERE / name).read_bytes():
            raise RuntimeError(f"commit {name} before reader calls")


def existing():
    records = {}
    for path in RAW.glob("*.json"):
        if path.stat().st_size > RAW_CAP:
            raise RuntimeError(f"oversized raw record: {path.name}")
        record = json.loads(path.read_text())
        if path.name != f"{record['id']}-{record['arm']}.json":
            raise RuntimeError(f"unexpected raw record: {path.name}")
        records[path.name] = record
    return records


def account():
    picked = subprocess.run(["zsh", PICKER], capture_output=True, text=True,
                            env=os.environ | {"PICK_NOWAIT": "1", "PICK_SHORT": "1"})
    cfg = picked.stdout.strip()
    if picked.returncode or not cfg.startswith("/home/seyran/.agent-accounts/claude-"):
        raise RuntimeError(f"account picker unavailable: exit {picked.returncode}: {picked.stderr.strip()}")
    auth = json.loads((Path(cfg) / ".claude.json").read_text())
    if not auth.get("oauthAccount") or auth.get("primaryApiKey"):
        raise RuntimeError("picked account is not an OAuth subscription")
    return cfg


def call(row, arm, cfg):
    body = prompt(row, arm)
    env = {k: v for k, v in os.environ.items() if not k.endswith("API_KEY")
           and k not in {"ANTHROPIC_BASE_URL", "OPENAI_BASE_URL"}}
    env["CLAUDE_CONFIG_DIR"] = cfg
    cmd = ["claude", "-p", "--model", "sonnet", "--max-turns", "1",
           "--restricted", "--no-session-persistence", "--output-format", "json", body]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="/tmp", env=env, timeout=1200)
    except (subprocess.TimeoutExpired, OSError) as exc:
        raw = getattr(exc, "stdout", None) or b""
        stdout = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else raw
        result = subprocess.CompletedProcess(cmd, -1, stdout, str(exc))
        process_error = f"CLI did not complete: {type(exc).__name__}"
    else:
        process_error = None
    oversized = len(result.stdout.encode()) > RAW_CAP
    try:
        wrapper = json.loads(result.stdout)
    except (TypeError, ValueError):
        wrapper = {"raw_stdout": result.stdout[:RAW_CAP]} if not oversized else {}
    if not isinstance(wrapper, dict):
        wrapper = {"raw_stdout": result.stdout[:RAW_CAP]} if not oversized else {}
    if oversized:
        wrapper = usage_summary(wrapper)
    record = {"id": row["id"], "arm": arm, "account": Path(cfg).name,
              "prompt": body, "cli": wrapper, "stderr": result.stderr,
              "exit_code": result.returncode}
    error = process_error or ("CLI output exceeds raw record limit" if oversized else None)
    if not error and (result.returncode or wrapper.get("subtype") != "success"
                      or wrapper.get("is_error") is not False):
        error = f"CLI exit {result.returncode} or unsuccessful result"
    if not error:
        models = wrapper.get("modelUsage")
        if not isinstance(models, dict) or set(models) != {MODEL}:
            error = "CLI did not use Sonnet 5.5 exclusively"
        elif type(wrapper.get("result")) is not str:
            error = "CLI result is not text"
    try:
        reported = usage_cw(wrapper)
    except RuntimeError as exc:
        error = error or str(exc)
        reported = None
    charged = max(RESERVE_CW, reported) if error and reported is not None else reported
    final = record | {"charged_cw": charged, "answer": "" if error else wrapper["result"],
                      **({"error": error} if error else {})}
    if len((json.dumps(final, indent=2, ensure_ascii=False) + "\n").encode()) > RAW_CAP:
        final = record | {"cli": usage_summary(wrapper), "stderr": str(result.stderr)[:4096],
                          "charged_cw": max(RESERVE_CW, reported) if reported is not None else None,
                          "answer": "", "error": "CLI record exceeds raw record limit"}
    return final


def run():
    committed()
    render.audit()
    rows = render.rows()
    queue = [(row, arm) for row in rows for arm in ("identifier", "english")]
    if len(queue) > CALL_CAP:
        raise RuntimeError("frame exceeds call cap")
    RAW.mkdir(exist_ok=True)
    saved = existing()
    known = {f"{row['id']}-{arm}.json": (row, arm) for row, arm in queue}
    if set(saved) - set(known):
        raise RuntimeError("extra raw record")
    charged = 0
    for name, record in saved.items():
        row, arm = known[name]
        if record["prompt"] != prompt(row, arm):
            raise RuntimeError(f"rebound raw record: {name}")
        try:
            charged += record_cw(record)
        except RuntimeError as exc:
            raise RuntimeError(f"unaccounted raw call {name}; inspect before continuing") from exc
    if len(saved) > CALL_CAP or charged > CW_CAP:
        raise RuntimeError("saved calls exceed cap")
    if any(record.get("error") for record in saved.values()):
        raise RuntimeError("saved reader call failed; inspect before continuing")
    for row, arm in queue:
        name = f"{row['id']}-{arm}.json"
        if name in saved:
            continue
        if not within_caps(len(saved), charged):
            raise RuntimeError("reader cap reached")
        cfg = account()
        save_record(RAW / name, {"id": row["id"], "arm": arm, "account": Path(cfg).name,
                                 "prompt": prompt(row, arm), "state": "dispatched",
                                 "charged_cw": None})
        record = call(row, arm, cfg)
        save_record(RAW / name, record)
        if record["charged_cw"] is None:
            raise RuntimeError(f"reader usage unknown for {name}; inspect before continuing")
        if charged + record["charged_cw"] > CW_CAP:
            raise RuntimeError("reported CW cap exceeded; inspect last call")
        saved[name] = record
        charged += record["charged_cw"]
        print(f"{name}: {charged} CW / {len(saved)} calls", flush=True)
        if record.get("error"):
            raise RuntimeError(f"reader call failed and was saved as {name}: {record['error']}")


def results():
    rows = render.rows()
    records = existing()
    if len(records) != 80:
        raise RuntimeError(f"only {len(records)} of 80 reader calls saved")
    for record in records.values():
        record_cw(record)
    scores = {arm: [record_score(row, records[f"{row['id']}-{arm}.json"])
                    for row in rows] for arm in ("identifier", "english")}
    count = {arm: sum(s["correct"] for s in scores[arm]) for arm in scores}
    critical = [row["id"] for row, s in zip(rows, scores["english"], strict=True) if s["critical"]]
    a = count["english"] >= 36 and count["english"] - count["identifier"] >= 6
    b = not critical
    return {"counts": count, "critical": critical, "bar_a": a, "bar_b": b,
            "fallback": [r["id"] for r in rows if r["lint"] != "accepted"],
            "errors": sorted(f"{r['id']}-{r['arm']}" for r in records.values() if r.get("error")),
            "calls": len(records), "cw": sum(r["charged_cw"] for r in records.values())}


if __name__ == "__main__":
    if sys.argv[1:] == ["--run"]:
        run()
    elif sys.argv[1:] == ["--score"]:
        print(json.dumps(results(), indent=2))
    else:
        raise SystemExit("usage: runner.py --run|--score")
