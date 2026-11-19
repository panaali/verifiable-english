"""Base against head for the two BlueDot documents this item changes: legends only, same answers.

Checks main's bytes of each document (from `git show <base>:<path>`, written to a temporary directory) and
this tree's bytes with the same checker, then compares the whole answers value by value after masking the
values that hash the environment (its descriptions are part of identity): `environment_id`, `meaning_id`,
`seal_id`-like digests and the document's own SHA-256.

    uv run python docs/usecases/bluedot-grant/defs-repair-bluedot-grant-1119/ab_answers.py --base main \
        --out docs/usecases/bluedot-grant/defs-repair-bluedot-grant-1119/ab-answers.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

from ve.document import check_document

ROOT = Path(__file__).resolve().parents[4]
DOCUMENTS = ("usecases/bluedot-grant/document.ve.md", "usecases/bluedot-grant/causal.ve.md")
HEX = re.compile(r"^[0-9a-f]{64}$")


def masked(value):
    if isinstance(value, dict):
        return {k: masked(v) for k, v in value.items()}
    if isinstance(value, list):
        return [masked(v) for v in value]
    return "<digest>" if isinstance(value, str) and HEX.match(value) else value


def differences(base, head, path=""):
    if type(base) is not type(head):
        return [path]
    if isinstance(base, dict):
        return [d for k in sorted(set(base) | set(head))
                for d in differences(base.get(k), head.get(k), f"{path}/{k}")]
    if isinstance(base, list):
        if len(base) != len(head):
            return [path]
        return [d for i, (b, h) in enumerate(zip(base, head)) for d in differences(b, h, f"{path}/{i}")]
    return [] if base == head else [path]


def answer(path: Path) -> dict:
    return json.loads(json.dumps(check_document(path), sort_keys=True, default=str))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--base", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    base_commit = subprocess.run(["git", "rev-parse", args.base], cwd=ROOT, check=True,
                                 capture_output=True, text=True).stdout.strip()
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for rel in DOCUMENTS:
            data = subprocess.run(["git", "show", f"{base_commit}:{rel}"], cwd=ROOT, check=True,
                                  capture_output=True).stdout
            base_path = Path(tmp) / Path(rel).name
            base_path.write_bytes(data)
            head_path = ROOT / rel
            raw_base, raw_head = answer(base_path), answer(head_path)
            raw = sorted({d.rsplit("/", 1)[-1] for d in differences(raw_base, raw_head)})
            diff = differences(masked(raw_base), masked(raw_head))
            rows.append({"document": rel, "base_sha256": hashlib.sha256(data).hexdigest(),
                         "head_sha256": hashlib.sha256(head_path.read_bytes()).hexdigest(),
                         "raw_differing_keys": raw,
                         "identical_after_masking_digests": not diff, "differing_paths": diff})
    Path(args.out).write_text(json.dumps({"base": base_commit, "rows": rows}, indent=1) + "\n")


if __name__ == "__main__":
    main()
