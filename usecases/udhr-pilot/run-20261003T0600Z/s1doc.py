"""Helpers: turn the previous run's translation into a `readings@1` document (composition S1) and measure it.

Reuses tools/readings_s1_pilot.py (the situation search, the identity helpers, the writer) without the companion merge:
the norm-defaults companions declare the completion `unspecified`, which a soft or rights document cannot hold, so
u017, u052, u112, u114 keep their candidates as the previous run had them (pending norm candidates, formula candidates).
"""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import readings_s1_pilot as P  # noqa: E402
from ve.document import _environment  # noqa: E402

CONTENT_KEYS = {"right", "right_lines", "limitation", "norm"}


def bearing(item):
    return any(type(r.get("content")) is dict and set(r["content"]) & CONTENT_KEYS for r in item["readings"])


def to_s1(meta):
    """`meta` with readings@1 on, every set re-identified over the new environment, situations still to be found."""
    meta = deepcopy(meta)
    meta["environment"] = P.with_readings(meta["environment"])
    env = _environment(meta["environment"])
    sets = []
    for item in meta["reading_sets"]:
        if not bearing(item):
            sets.append(P._reidentified(env, item))
            continue
        item = {k: v for k, v in item.items() if k != "models"}
        readings = []
        for r in item["readings"]:
            readings.append({**r, "meaning_id": P._identity(env, item["id"], r)})
        for r in readings:
            r["admission"]["distinguishing_models"] = {o["id"]: "pending" for o in readings if o["id"] != r["id"]}
        sets.append({**item, "readings": readings})
    meta["reading_sets"] = sets
    return meta, env


def read(path):
    return P.read(path)


def write(path, meta, source):
    Path(path).write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False, sort_keys=True, indent=2).encode()
                           + b"\n---\n" + source)
