"""Evaluation items: 12 P5 DEV items (tuning) and 12 HELD-OUT P5 scored items.

Materials are byte copies of ve-codex experiments/P5-shifting-definitions
(commit afa11f4); their sha256 values match that directory's
MATERIALS-HASHES.txt and are re-checked on load. Labels are read ONLY for
held-out stratification and post-hoc scoring; nothing from a label ever
reaches an author or auditor prompt.

Held-out selection (seeded, labelled "held-out P5 scored items"): shuffle the
24 scored families with ``random.Random(HELDOUT_SEED)``, keep the first 12,
assign kinds from a seeded shuffle of benign/shift/smuggle x 4, and take that
family's item of that kind. One item per family, 4 per kind.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[2]
MATERIALS = ROOT / "experiments" / "assist-eval" / "materials"
SHA256 = {
    "dev.jsonl.gz": "ed709b3b5f36c1ea109dfaf6e2ba6a436abbf3d49af242093aa74bda7d28f06a",
    "scored.jsonl.gz": "8b5ddb7acfe7704f91554eb2c0a45a787d48b2133a1fba57e9c0e1067731e144",
    "labels.jsonl.gz": "cd9f0f491492d9066bbcd3803968ca9f1bf50ac3dd48f47f0927d382148324c3",
}
HELDOUT_SEED = 20260922
HELDOUT_N = 12
KINDS = ("benign", "shift", "smuggle")


def _read(name):
    path = MATERIALS / name
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != SHA256[name]:
        raise RuntimeError(f"{name}: sha256 does not match the P5 materials hash")
    return [json.loads(line) for line in gzip.decompress(data).decode().splitlines() if line.strip()]


def labels():
    return {row["id"]: row for row in _read("labels.jsonl.gz")}


def dev_items():
    return _read("dev.jsonl.gz")


def heldout_items():
    rows = _read("scored.jsonl.gz")
    kinds = {k: v["kind"] for k, v in labels().items()}
    families = sorted({r["group"] for r in rows})
    rng = random.Random(HELDOUT_SEED)
    rng.shuffle(families)
    chosen = families[:HELDOUT_N]
    plan = list(KINDS) * (HELDOUT_N // len(KINDS))
    rng.shuffle(plan)
    out = []
    for family, kind in zip(chosen, plan):
        match = [r for r in rows if r["group"] == family and kinds[r["id"]] == kind]
        if len(match) != 1:
            raise RuntimeError(f"family {family} has {len(match)} items of kind {kind}")
        out.append(match[0])
    return out


def items(split):
    if split == "dev":
        return dev_items()
    if split == "heldout":
        return heldout_items()
    raise ValueError("split must be dev or heldout")


def item_ids(split):
    return [row["id"] for row in items(split)]
