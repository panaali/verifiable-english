"""Base against head over every document premise-scale's change reaches (build checklist item 8).

Each document runs `check_document` in a fresh process in each checkout (`--base` and `--head`,
each with its own Lean and Rust builds), and the whole answer is compared, value by value. The
rows record each document's premise status on each side and the JSON paths whose values differ,
with both values (cut to 300 characters). A failed check is compared by its error code and text.

    uv run python docs/premise-scale/ab_documents.py --base ../base --head . --out evidence/ab.json DOC...
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

INNER = r"""
import json, sys
from ve.document import check_document
try:
    print(json.dumps({"answer": check_document(sys.argv[1])}, sort_keys=True, default=str))
except Exception as exc:
    print(json.dumps({"error": {"type": type(exc).__name__, "code": getattr(exc, "code", None), "text": str(exc)}}))
"""


def answer(root: Path, path: Path, env: dict) -> dict:
    done = subprocess.run([sys.executable, "-c", INNER, str(path)], cwd=root, env=env, capture_output=True,
                          text=True, check=False)
    try:
        return json.loads(done.stdout.strip().splitlines()[-1])
    except (IndexError, ValueError):
        return {"error": {"type": "no answer", "code": None, "text": (done.stderr or done.stdout)[-300:]}}


def differences(a, b, path="") -> list[str]:
    if type(a) is not type(b):
        return [path or "/"]
    if isinstance(a, dict):
        return [d for key in sorted(set(a) | set(b)) for d in
                (differences(a.get(key), b.get(key), f"{path}/{key}") if key in a and key in b else [f"{path}/{key}"])]
    if isinstance(a, list):
        if len(a) != len(b):
            return [path or "/"]
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in differences(x, y, f"{path}/{i}")]
    return [] if a == b else [path or "/"]


def at(value, path: str):
    for key in filter(None, path.split("/")):
        value = value[int(key)] if isinstance(value, list) else value.get(key) if isinstance(value, dict) else None
    return json.dumps(value, sort_keys=True)[:300]


def status(side: dict):
    premises = side.get("answer", {}).get("premises") if "answer" in side else None
    return premises.get("status") if isinstance(premises, dict) else side.get("error", {}).get("type")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--head", type=Path, required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--rust-timeout", help="VE_RUST_TIMEOUT on both sides (default: unset)")
    parser.add_argument("documents", nargs="+", type=lambda p: Path(p).resolve())
    args = parser.parse_args()
    env = {k: v for k, v in os.environ.items() if k not in ("VE_RUST_TIMEOUT", "VE_RUST_JSONL", "VE_RUST_SHA256")}
    if args.rust_timeout:
        env["VE_RUST_TIMEOUT"] = args.rust_timeout
    rows = []
    for path in args.documents:
        base, head = answer(args.base.resolve(), path, env), answer(args.head.resolve(), path, env)
        changed = differences(base, head)
        row = {"document": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
               "base_premises": status(base), "head_premises": status(head), "identical": not changed,
               "differences": [{"path": p, "base": at(base, p), "head": at(head, p)} for p in changed[:40]],
               "differing_paths": len(changed)}
        print(json.dumps({k: row[k] for k in ("document", "base_premises", "head_premises", "identical",
                                              "differing_paths")}), flush=True)
        rows.append(row)
    Path(args.out).write_text(json.dumps({"rust_timeout": args.rust_timeout or "default", "rows": rows},
                                         indent=1) + "\n")


if __name__ == "__main__":
    main()
