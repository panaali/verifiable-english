"""D gate raw arm: Opus 5.5 answers each item from the artefact alone (PREREG-DRAFT.md).

NOT RUN YET. Refuses to call the model unless --execute is given, the freeze file exists and every
frozen hash matches. One account (``--account``, a ~/.claude-<label> config directory), one fresh
process per sample through ve_experiments/claude_cli.py; the ledger makes it resumable and never
replays a sample silently.

    python experiments/D-gate/run_raw.py --account <label> --arm high --execute
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))

K = 3
ARMS = {
    # primary: the strongest routine configuration; secondary: the T1c monitor configuration
    "high": dict(effort="high", thinking_tokens=None, output_tokens=32000, timeout_s=900),
    "low": dict(effort="low", thinking_tokens=1024, output_tokens=6000, timeout_s=600),
}
FROZEN = ("items.json", "ground_truth.json", "prompts.jsonl", "analyze.py", "run_raw.py", "PREREG-DRAFT.md")
ANSWER = re.compile(r"^\s*ANSWER:\s*(YES|NO)\s*$", re.MULTILINE)


def parse(text):
    m = ANSWER.findall(text or "")
    return m[-1] if m else "UNPARSED"


def check_freeze():
    f = HERE / "FREEZE.json"
    if not f.exists():
        sys.exit("FREEZE.json missing: the prereg is not frozen; no model calls")
    frozen = json.loads(f.read_text())
    for name in FROZEN:
        h = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        if frozen.get(name) != h:
            sys.exit(f"{name} changed since the freeze; no model calls")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--account", required=True)
    ap.add_argument("--arm", choices=sorted(ARMS), required=True)
    ap.add_argument("--execute", action="store_true")
    a = ap.parse_args()
    if not a.execute:
        sys.exit("dry: pass --execute to call the model (only after the freeze and both reviews)")
    check_freeze()
    from ve_experiments.claude_cli import ClaudeCLI, Controls, MODELS, SYSTEM, account_dir_for_label, EndpointError
    from datetime import datetime, timezone
    controls = Controls(model=MODELS["opus"], context_date=datetime.now(timezone.utc).date().isoformat(),
                        working_directory="/private/tmp/ve-dgate-claude-empty", **ARMS[a.arm])
    out = HERE / "runs" / a.arm
    out.mkdir(parents=True, exist_ok=True)
    done = set()
    if (out / "answers.jsonl").exists():
        done = {(r["id"], r["sample"]) for r in map(json.loads, open(out / "answers.jsonl"))
                if r["answer"] != "ENDPOINT_ERROR"}
    client = ClaudeCLI(out / "ledger.jsonl", controls, max_calls=len(open(HERE / "prompts.jsonl").readlines()) * K,
                       account_config_dir=account_dir_for_label(a.account))
    rows = [json.loads(l) for l in open(HERE / "prompts.jsonl")]
    with open(out / "answers.jsonl", "a") as f:
        for r in rows:
            for i in range(K):
                if (r["id"], i) in done:
                    continue
                try:
                    reply = client.sample(r["id"], SYSTEM, r["prompt"], i)
                    rec = dict(id=r["id"], sample=i, answer=parse(reply.get("text")),
                               output_tokens=reply.get("output_tokens"), served_model=reply.get("served_model"))
                except EndpointError as exc:
                    rec = dict(id=r["id"], sample=i, answer="ENDPOINT_ERROR", error=str(exc)[:500])
                f.write(json.dumps(rec) + "\n")
                f.flush()


if __name__ == "__main__":
    main()
