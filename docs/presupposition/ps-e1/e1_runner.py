"""PS-E1 reader runner: one fresh, blinded Sonnet 5.5 call per trial, at most four at once, resumable, capped."""
from __future__ import annotations

import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e1_items  # noqa: E402
import e1_score  # noqa: E402
import e1_stub  # noqa: E402

PICKER = "/home/seyran/code/manage-agents/pick-claude-account.sh"
PILOT = e1_items.DATA / "pilot.json"
RESERVE_CW = 25_000
USAGE_KEYS = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
MAX_ATTEMPTS = 3
STOP_AFTER_FAILURES = 3
FROZEN = ("docs/research/presupposition-E1-prereg.md", "docs/research/presupposition-E1/items.jsonl",
          "docs/research/presupposition-E1/scenarios.json", "docs/presupposition/ps-e1/e1_items.py",
          "docs/presupposition/ps-e1/e1_score.py", "docs/presupposition/ps-e1/e1_stub.py",
          "docs/presupposition/ps-e1/e1_runner.py")


class Abort(RuntimeError):
    """A condition no retry may pass: a paid-credit fallback."""


def usage_cw(wrapper):
    """Reported CW of one CLI result (the jt-e1r rule): all four counters; a paid-credit fallback aborts the run."""
    usage = wrapper.get("usage") if isinstance(wrapper, dict) else None
    if not isinstance(usage, dict):
        return None
    if usage.get("fallback_credit") is not None:
        raise Abort(f"paid-credit fallback reported: {usage['fallback_credit']!r}")
    if any(type(usage.get(k)) is not int or usage[k] < 0 for k in USAGE_KEYS):
        return None
    return sum(usage[k] for k in USAGE_KEYS)


def classify(exit_code, wrapper, model):
    """(answer, error, outage). An outage never reached the model: no reported model usage or no output."""
    reported = usage_cw(wrapper)
    usage = wrapper.get("usage") if isinstance(wrapper, dict) else None
    models = wrapper.get("modelUsage") if isinstance(wrapper, dict) else None
    if reported is None or not models or not usage.get("output_tokens"):
        return "", f"no model usage (exit {exit_code})", True
    if exit_code or wrapper.get("subtype") != "success" or wrapper.get("is_error") is not False:
        return "", f"CLI exit {exit_code} or unsuccessful result", False
    if set(models) != {model}:
        return "", f"not {model} exclusively: {sorted(models)}", False
    if type(wrapper.get("result")) is not str:
        return "", "CLI result is not text", False
    return wrapper["result"], None, False


def reader_command(cfg, body):
    """The smallest context the CLI allows with subscription auth: no tools, no settings, no MCP, no project files
    (an empty working directory), the reader instruction as the whole system prompt. `--bare` refuses OAuth."""
    return ["claude", "-p", "--model", cfg["model"], "--system-prompt", cfg["reader_instruction"], "--tools", "",
            "--setting-sources", "", "--strict-mcp-config", "--disable-slash-commands", "--no-session-persistence",
            "--max-turns", "1", "--output-format", "json", body]


def cli_call(cfg, item, account):
    env = {k: v for k, v in os.environ.items() if not k.endswith("API_KEY") and not k.startswith("CLAUDE")
           and k not in {"ANTHROPIC_BASE_URL", "OPENAI_BASE_URL"}}
    env |= {"CLAUDE_CONFIG_DIR": account, "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}
    with tempfile.TemporaryDirectory() as empty:
        try:
            done = subprocess.run(reader_command(cfg, e1_items.prompt(item)), capture_output=True, text=True, cwd=empty,
                                  env=env, stdin=subprocess.DEVNULL, timeout=1200)
            stdout, stderr, code = done.stdout, done.stderr, done.returncode
        except (subprocess.TimeoutExpired, OSError) as exc:
            stdout, stderr, code = "", f"CLI did not complete: {type(exc).__name__}", -1
    try:
        wrapper = json.loads(stdout)
    except ValueError:
        wrapper = {"raw_stdout": stdout[:4096]}
    return code, wrapper if isinstance(wrapper, dict) else {"raw_stdout": stdout[:4096]}, stderr[:2048]


def pick_account():
    """The picker's own class for short proxy answers (PICK_LIGHT): exempt from its worker cap, not from its limits."""
    picked = subprocess.run(["zsh", PICKER], capture_output=True, text=True,
                            env=os.environ | {"PICK_NOWAIT": "1", "PICK_SHORT": "1", "PICK_LIGHT": "1"})
    cfg = picked.stdout.strip()
    if picked.returncode or not cfg.startswith("/home/seyran/.agent-accounts/claude-"):
        raise RuntimeError(f"account picker unavailable: exit {picked.returncode}: {picked.stderr.strip()}")
    auth = json.loads((Path(cfg) / ".claude.json").read_text())
    if not auth.get("oauthAccount") or auth.get("primaryApiKey"):
        raise RuntimeError("picked account is not an OAuth subscription")
    return cfg


def save(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=".t-", delete=False) as stream:
        json.dump(record, stream, ensure_ascii=False, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(stream.name, path)


def committed():
    """R-12: the prereg file, the items and this code are in HEAD, byte for byte, before any call."""
    root = e1_items.ROOT
    for name in FROZEN:
        saved = subprocess.run(["git", "show", f"HEAD:{name}"], capture_output=True, cwd=root).stdout
        if saved != (root / name).read_bytes():
            raise RuntimeError(f"commit {name} before reader calls")
    return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=root, check=True).stdout.strip()


def spent(records):
    """(calls that may have reached the model, CW charged): an unfinished dispatch is charged the reserve."""
    calls = sum(r["model_calls"] for r in records.values())
    cw = sum((RESERVE_CW if r["charged_cw"] is None else r["charged_cw"]) + r["prior_cw"] for r in records.values())
    return calls, cw


def run(items, cfg, raw, call=cli_call, pick=pick_account, head="uncommitted", frame=None):
    """Run every trial of `items` not yet final; returns 'done', 'cap' or 'stopped: <why>'. Never exceeds the caps."""
    records = e1_score.load_records(raw)
    e1_score.bound(frame or items, cfg, records)
    calls, charged = spent(records)
    queue = [(i, t) for i in items for t in range(1, cfg["trials_per_item"] + 1)
             if records.get((i["id"], t), {}).get("state") != "final"]
    state = {"calls": calls, "charged": charged, "inflight": 0, "stop": None, "failures": 0, "account": None, "since": 0}
    lock = threading.Lock()

    def worker():
        while True:
            with lock:
                if state["stop"] or not queue:
                    return
                if (state["calls"] + state["inflight"] >= cfg["call_cap"]
                        or state["charged"] + RESERVE_CW * (state["inflight"] + 1) > cfg["cw_cap"]):
                    state["stop"] = "cap"
                    return
                item, trial = queue.pop(0)
                state["inflight"] += 1
                if state["account"] is None or state["since"] >= cfg["trials_per_item"]:
                    try:
                        state["account"], state["since"] = pick(), 0
                    except RuntimeError as exc:
                        state["stop"] = f"stopped: {exc}"
                        state["inflight"] -= 1
                        return
                state["since"] += 1
                account = state["account"]
            path = Path(raw) / item["id"] / f"{trial:02d}.json"
            before = records.get((item["id"], trial))
            prior = 0 if before is None else (
                before["prior_cw"] + (RESERVE_CW if before["charged_cw"] is None else before["charged_cw"]))
            base = {"id": item["id"], "trial": trial, "account": Path(account).name, "head": head,
                    "prompt_sha256": e1_items.sha(e1_items.prompt(item)),
                    "system_sha256": e1_items.sha(cfg["reader_instruction"]), "prior_cw": prior,
                    "attempts": (before["attempts"] if before else 0) + 1,
                    "model_calls": (before["model_calls"] if before else 0)}
            save(path, base | {"state": "dispatched", "charged_cw": None, "model_calls": base["model_calls"] + 1})
            code, wrapper, stderr = call(cfg, item, account)
            try:
                answer, error, outage = classify(code, wrapper, cfg["model"])
                reported = usage_cw(wrapper)
            except Abort as exc:
                answer, error, outage, reported = "", str(exc), False, None
                with lock:
                    state["stop"] = f"stopped: {exc}"
            used = RESERVE_CW if reported is None or outage else reported
            retry = outage and base["attempts"] < MAX_ATTEMPTS
            record = base | {"state": "outage" if retry else "final", "charged_cw": used, "answer": answer,
                             "model_calls": base["model_calls"] + (0 if outage else 1), "exit_code": code,
                             "cli": wrapper, "stderr": stderr} | ({"error": error} if error else {})
            save(path, record)
            with lock:
                records[item["id"], trial] = record
                state["inflight"] -= 1
                state["charged"] += used
                state["calls"] += 0 if outage else 1
                state["failures"] = state["failures"] + 1 if error else 0
                if outage:
                    state["account"] = None
                if record["state"] == "outage":
                    queue.append((item, trial))
                if state["failures"] >= STOP_AFTER_FAILURES and not state["stop"]:
                    state["stop"] = f"stopped: {state['failures']} calls in a row failed; last: {error}"
                print(f"{item['id']}#{trial:02d} {'ERROR ' + error if error else answer.strip()[:8]} "
                      f"calls {state['calls']} CW {state['charged']}", flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=cfg["concurrency"]) as pool:
        for future in [pool.submit(worker) for _ in range(cfg["concurrency"])]:
            future.result()
    return state["stop"] or "done"


def project(item, cfg, records):
    """Measured CW per call on the pilot item and the projection for every call of the plan."""
    rows = [records[item["id"], t] for t in range(1, cfg["trials_per_item"] + 1)]
    total = sum(r["charged_cw"] for r in rows)
    per_call = total / len(rows)
    projection = round(per_call * cfg["call_cap"])
    return {"item": item["id"], "calls": len(rows), "cw_total": total, "cw_per_call": per_call,
            "projection": projection, "cw_cap": cfg["cw_cap"], "within_cap": projection <= cfg["cw_cap"]}


def main(argv):
    cfg, items, rows = e1_score.config(), e1_items.load(), e1_stub.saved_table()
    e1_items.audit(items, cfg, rows)
    head = committed()
    raw = e1_score.RAW
    if argv == ["--pilot"]:
        status = run(items[:1], cfg, raw, head=head, frame=items)
        if status != "done":
            return f"pilot {status}"
        measured = project(items[0], cfg, e1_score.load_records(raw)) | {"head": head}
        PILOT.write_text(json.dumps(measured, indent=1) + "\n")
        print(json.dumps(measured))
        return 0 if measured["within_cap"] else 3
    if argv == ["--run"]:
        measured = json.loads(PILOT.read_text()) if PILOT.exists() else None
        if not measured or not measured["within_cap"]:
            return "no pilot within the cap: run --pilot, or ask the decider"
        status = run(items, cfg, raw, head=head)
        print(status)
        return 0 if status == "done" else (4 if status == "cap" else 5)
    return "usage: e1_runner.py --pilot|--run"


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
