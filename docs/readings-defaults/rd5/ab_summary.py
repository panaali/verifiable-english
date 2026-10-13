"""Summarise RD-5's saved A/B evidence (`ab.json.gz` and its reruns) into `ab-summary.json`.

    uv run --frozen python docs/readings-defaults/rd5/ab_summary.py docs/readings-defaults/rd5/evidence

Each difference of the recorded comparison is paired with its serial rerun: the rerun with the Rust checker's limit
raised (`ab-rerun-rust600.json.gz`) when it holds the case, else the first rerun (`ab-rerun.json.gz`). The probe and
conformance corpora's comparison (`ab-probe-conformance.json.gz`) is added with its totals.
"""
import json, gzip, sys
E = sys.argv[1]
ab = json.load(gzip.open(f"{E}/ab.json.gz"))
r1 = json.load(gzip.open(f"{E}/ab-rerun.json.gz"))
r2 = json.load(gzip.open(f"{E}/ab-rerun-rust600.json.gz"))
pc = json.load(gzip.open(f"{E}/ab-probe-conformance.json.gz"))
final = {r["case"]: r for r in r1["rows"]}
final.update({r["case"]: r for r in r2["rows"]})
out = {"base": "cc534bfc (merge base, worktree with this branch's Lean and Rust builds: no Lean or Rust file differs)",
       "corpora": ["pilots", "readings"], "totals": ab["totals"], "records": ab["records"],
       "differences": [{"case": d["case"], "class": d["class"],
                        "rerun": "ab-rerun-rust600.json.gz" if d["case"] in {r["case"] for r in r2["rows"]} else "ab-rerun.json.gz",
                        "rerun_equal": final[d["case"]]["equal"],
                        "rerun_wall_seconds": [final[d["case"]]["base"]["wall_seconds"], final[d["case"]]["head"]["wall_seconds"]]}
                       for d in ab["differences"]],
       "probe_conformance": {k: pc[k] for k in ("totals", "records", "unlisted", "unavailable_both")},
       "rerun_settings": {"ab-rerun.json.gz": r1.get("VE_RUST_TIMEOUT"), "ab-rerun-rust600.json.gz": r2.get("VE_RUST_TIMEOUT")}}
json.dump(out, open(f"{E}/ab-summary.json", "w"), indent=1)
print(out["totals"], sum(d["rerun_equal"] for d in out["differences"]), len(out["differences"]))
