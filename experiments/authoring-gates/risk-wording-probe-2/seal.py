#!/usr/bin/env python3
"""Seal risk wording probe 2, the c5 re-probe (docs/spec/risk-PLAN.md 2.6 rule 4).

Adapted from ../risk-wording-probe/seal.py; only DROP and this docstring differ. Run once, before any reader
session:

    python3 seal.py [--seed <n>]

It drops the items the checking reviewer rejected, writes the reader prompt, the reader list, the session
assignment (with the seed) and every rendered session text, then MANIFEST.sha256 over all sealed files.
"""

import argparse
import hashlib
import json
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent

# The DROP line of the checking reviewer's report (manage-agents/risk-probe2-check.final.md): "DROP: none".
DROP = []

# 2.6 Readers: the fixed instruction, and nothing else.
INSTRUCTION = ("Read each short text and answer its question from the text alone. "
               "Choose one option and give a one-sentence reason.")

READERS = [
    {
        "family": "haiku",
        "name": "Claude Haiku 4.5",
        "model": "claude-haiku-4-5-20251001",
        "command": ("CLAUDE_CONFIG_DIR=$(zsh /home/seyran/code/manage-agents/pick-claude-account.sh) "
                    "/home/seyran/.local/bin/claude -p --model claude-haiku-4-5-20251001 --tools \"\" "
                    "--output-format json < session.txt"),
        "input": "session text on stdin",
    },
    {
        "family": "sol",
        "name": "GPT-6 Sol",
        "model": "gpt-6-sol",
        "command": ("CODEX_HOME=/home/seyran/.agent-accounts/codex codex exec -m gpt-6-sol -s read-only "
                    "--skip-git-repo-check -C <empty dir> --json \"<session text>\""),
        "input": "session text as the prompt argument",
    },
]
REPLICATES = 2          # independent sessions per family per item and condition
MAX_PER_SESSION = 8
CONDITIONS = ["L", "C"]


def dump_items(items):
    """Serialise items in the hand-written layout of items.json (one option per line, short lists inline)."""
    out = ["["]
    for i, item in enumerate(items):
        out.append("  {")
        keys = list(item)
        for j, k in enumerate(keys):
            v = item[k]
            comma = "," if j < len(keys) - 1 else ""
            if k == "options":
                out.append(f'    "{k}": [')
                for m, opt in enumerate(v):
                    oc = "," if m < len(v) - 1 else ""
                    out.append("      " + json.dumps(opt, separators=(", ", ": ")) + oc)
                out.append("    ]" + comma)
            else:
                out.append(f'    "{k}": ' + json.dumps(v, separators=(", ", ": ")) + comma)
        out.append("  }" + ("," if i < len(items) - 1 else ""))
    out.append("]")
    return "\n".join(out) + "\n"


def conflicts(a, b):
    """2.6: at most one item per construct, never c3a with c3b, never c12 with a prevents control."""
    ca, cb = a["construct"], b["construct"]
    if ca == cb:
        return True
    pair = {ca, cb}
    return pair == {"c3a", "c3b"} or pair == {"c12", "control-prevents"}


def assign(items, rng):
    """Split items (one condition) into sessions of at most MAX_PER_SESSION with no conflicting pair."""
    groups = {}
    for it in items:
        key = "c3" if it["construct"] in ("c3a", "c3b") else it["construct"]
        groups[key] = groups.get(key, 0) + 1
    n = max(math.ceil(len(items) / MAX_PER_SESSION), max(groups.values()))
    for _ in range(10000):
        order = items[:]
        rng.shuffle(order)
        sessions = [[] for _ in range(n)]
        ok = True
        for it in order:
            cands = [s for s in sessions
                     if len(s) < MAX_PER_SESSION and not any(conflicts(it, o) for o in s)]
            if not cands:
                ok = False
                break
            least = min(len(s) for s in cands)
            rng.choice([s for s in cands if len(s) == least]).append(it)
        if ok:
            for s in sessions:
                rng.shuffle(s)
            return sessions
    raise SystemExit("no assignment found")


def render_item(n, item, cond, rng):
    """Render one item; options are shown in a seeded random order and relabelled a, b, c, d."""
    opts = item["options"][:]
    rng.shuffle(opts)
    shown = "abcd"[:len(opts)]
    mapping = {shown[i]: opts[i]["label"] for i in range(len(opts))}
    lines = [f"Text {n}", ""]
    if cond == "L":
        lines += ["Legend:"] + item["legend_text"].split("\n") + [""]
    lines += item["situation_text"].split("\n") + [""]
    lines.append(item["question"])
    lines += [f"({shown[i]}) {opts[i]['text']}" for i in range(len(opts))]
    return "\n".join(lines), mapping


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, help="default: a fresh random seed, recorded in sessions.json")
    args = ap.parse_args()
    if args.seed is None:
        import secrets
        args.seed = secrets.randbelow(2 ** 31)

    items_path = HERE / "items.json"
    original = items_path.read_text()
    items = json.loads(original)
    assert dump_items(items) == original, "items.json layout does not round-trip"
    ids = {it["id"] for it in items}
    missing = [d for d in DROP if d not in ids]
    assert not missing, f"DROP ids not found: {missing}"
    items = [it for it in items if it["id"] not in DROP]
    items_path.write_text(dump_items(items))

    (HERE / "prompt.txt").write_text(INSTRUCTION + "\n")
    (HERE / "readers.json").write_text(json.dumps(READERS, indent=2) + "\n")

    rng = random.Random(args.seed)
    sessions = []
    sess_dir = HERE / "sessions"
    sess_dir.mkdir(exist_ok=True)
    for reader in READERS:
        for rep in range(1, REPLICATES + 1):
            for cond in CONDITIONS:
                pool = [it for it in items if cond in it["conditions"]]
                for k, members in enumerate(assign(pool, rng), start=1):
                    sid = f"{reader['family']}-r{rep}-{cond}-{k:02d}"
                    blocks, entries = [], []
                    for n, it in enumerate(members, start=1):
                        text, mapping = render_item(n, it, cond, rng)
                        blocks.append(text)
                        entries.append({"position": n, "item": it["id"], "shown_to_label": mapping})
                    body = INSTRUCTION + "\n\n" + "\n\n".join(blocks) + "\n"
                    (sess_dir / f"{sid}.txt").write_text(body)
                    sessions.append({"session": sid, "family": reader["family"], "replicate": rep,
                                     "condition": cond, "items": entries})

    (HERE / "sessions.json").write_text(json.dumps(
        {"seed": args.seed, "generator": "seal.py (random.Random(seed), Python 3)",
         "dropped": DROP, "sessions": sessions}, indent=2) + "\n")

    sealed = sorted(p for p in HERE.rglob("*")
                    if p.is_file() and p.name != "MANIFEST.sha256" and "runs" not in p.relative_to(HERE).parts
                    and "__pycache__" not in p.parts)
    lines = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(HERE)}" for p in sealed]
    (HERE / "MANIFEST.sha256").write_text("\n".join(lines) + "\n")
    print(f"seed {args.seed}: {len(items)} items, {len(sessions)} sessions, {len(sealed)} sealed files")


if __name__ == "__main__":
    main()
