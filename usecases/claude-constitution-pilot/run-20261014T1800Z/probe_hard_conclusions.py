#!/usr/bin/env python3
"""Run 20261013T0600Z: conclusion queries on the seven hard-constraint rules of the repaired translation (superposed route).

For each constraint, over every instance of Claude and every situation, `ve document readings translation.ve.md --conclusion`:
  * knowing:  Claude would be knowingly and intentionally doing what the bullet says (u0173.s01, first alternative)  -> not permitted
  * belief:   Claude thinks it quite likely that the action falls into the category (second alternative)             -> not permitted
  * neither:  neither of the two holds (an unclear, uncertain or unknowing case)  -> not permitted  (NOT meant to be entailed)
Writes probes/nd/hard/<unit>-<kind>.json (the query) and <unit>-<kind>-result.json (VE's answer), and probes/hard-conclusions-probe.json.
"""
from __future__ import annotations

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(RUN))
import spec_nd  # noqa: E402

OUT = RUN / "probes/nd/hard"
WORKERS = 4  # independent queries, one `ve document readings` process each


def ask(unit, kind, pred, premise, doc):
    query = ["forall", "claude_instance", ["forall", "situation",
             ["implies", premise, ["not", ["binary", pred, ["var", 1], ["var", 0]]]]]]
    qpath = OUT / f"{unit}-{kind}.json"
    qpath.write_text(json.dumps(query) + "\n")
    proc = subprocess.run([sys.executable, "-m", "ve", "document", "readings", doc, "--conclusion", str(qpath.relative_to(ROOT))],
                          cwd=ROOT, capture_output=True, text=True)
    (OUT / f"{unit}-{kind}-result.json").write_text(proc.stdout)
    row = {"unit": unit, "kind": kind, "predicate": pred, "returncode": proc.returncode}
    try:
        d = json.loads(proc.stdout)
        row.update({k: d.get(k) for k in ("verdict", "route", "evidence", "english")})
    except ValueError:
        row["stderr"] = proc.stderr[-400:]
    print(unit, kind, row.get("verdict"), row.get("route"), row.get("evidence"), flush=True)
    return row


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    doc = str((RUN / "translation.ve.md").relative_to(ROOT))
    jobs = []
    for unit, _rule, pred, term, _act, _words in spec_nd.HARD:
        x, b = "knowingly_" + term, "thought_likely_" + term
        # premise -> the act is not permitted; "neither" is NOT meant to be entailed
        prem = {
            "knowing": ["unary", x, ["var", 0]],
            "belief": ["unary", b, ["var", 0]],
            "neither": ["and", ["not", ["unary", x, ["var", 0]]], ["not", ["unary", b, ["var", 0]]]],
        }
        jobs += [(unit, kind, pred, premise) for kind, premise in prem.items()]
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        rows = list(pool.map(lambda j: ask(*j, doc), jobs))  # map keeps the job order
    summary = {"document": "translation.ve.md", "queries": rows}
    (RUN / "probes/hard-conclusions-probe.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
