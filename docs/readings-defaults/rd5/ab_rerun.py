"""Rerun, one at a time, the pilot records an A/B comparison found different or unavailable (RD-5's A/B).

    uv run --frozen python docs/readings-defaults/rd5/ab_rerun.py AB.json BASE_ROOT HEAD_ROOT OUT.json [CASE ...]

The A/B's two recordings run each pilot document in a process of its own with several workers, so under host load
a document can hit a wall-clock limit on one side only (the Rust checker's 5 s, the recorder's 600 s). This script
takes every pilot record of class `availability`, `unavailable` or `wording` in `AB.json`, checks its document again
on each side, serially, with `tools/lean_first_diff.py`'s own `pilot_check`, and records both outcomes, each with its
side's scratch directory replaced by `<scratch>` (the sense-pack probes print the absolute path of a pack next to the
document), and whether they are equal. Given `CASE` names, only those records are
rerun. The Rust checker's wall-clock limit (`VE_RUST_TIMEOUT`) is recorded as the run's setting.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tools.lean_first_diff import pilot_check, pilot_documents  # noqa: E402

CLASSES = ("availability", "unavailable", "wording")


def normalized(outcome, scratch):
    return json.loads(json.dumps(outcome).replace(str(scratch), "<scratch>"))


def main(argv=None):
    ab, base, head, out, *only = (sys.argv[1:] if argv is None else argv)
    differing = [d for d in json.loads(Path(ab).read_text())["differences"]
                 if d["corpus"] == "pilots" and d["class"] in CLASSES and (not only or d["case"] in only)]
    texts = {name: text for name, _, text in pilot_documents(ROOT)}
    rows = []
    for d in differing:
        row = {"case": d["case"], "class": d["class"], "load_before": round(os.getloadavg()[0], 1)}
        for side, root in (("base", base), ("head", head)):
            scratch = Path(tempfile.mkdtemp(prefix=f"rd5-ab-{side}-"))
            path = scratch / "document.ve.md"
            path.write_bytes(texts[d["case"]])
            env = {**os.environ, "PYTHONPATH": str(root), "VE_SHADOW_LOG": str(scratch / "shadow.jsonl")}
            env.pop("VE_AUTHORITY", None)
            started = time.monotonic()
            outcome = pilot_check(Path(root), path, env)
            row[side] = {"outcome": normalized(outcome, scratch), "wall_seconds": round(time.monotonic() - started, 1)}
        row["equal"] = row["base"]["outcome"] == row["head"]["outcome"]
        row["available"] = all(row[s]["outcome"].get("exit") in (0, 1) for s in ("base", "head"))
        rows.append(row)
        print(row["case"], row["equal"], row["base"]["wall_seconds"], row["head"]["wall_seconds"], flush=True)
    Path(out).write_text(json.dumps({"ab": str(ab), "VE_RUST_TIMEOUT": os.environ.get("VE_RUST_TIMEOUT"), "rows": rows},
                                    indent=1, ensure_ascii=False) + "\n")
    return 0 if all(r["equal"] for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
