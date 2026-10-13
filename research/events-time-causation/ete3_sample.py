"""ET-E3: draw the pre-registered sample of 20 causal units (phase-1 doc 1.4).

Pool: every unit whose primary blocker is `causation` in the run 20261012T1800Z ledgers of both pilots,
named U:<id> (UDHR) and C:<id> (constitution), sorted as strings. Sample: random.Random("ET-E3").sample(pool, 20).
Writes the pool and the sample, with each unit's span and source sentence, to the evidence directory.

Usage: python3 ete3_sample.py <pilots-dir> <out.json>
"""
import json
import random
import sys
from pathlib import Path

RUN = "run-20261012T1800Z"


def ledger(path):
    data = json.loads(Path(path).read_text())
    return data["units"] if isinstance(data, dict) else data


def main(pilots, out):
    pilots = Path(pilots)
    udhr_src = (pilots / "udhr/source/udhr.md").read_bytes()
    con_src = (pilots / "claude-constitution/source/claude-constitution.md").read_bytes()
    rows = {}
    for prefix, name, src in (("U", "udhr", udhr_src), ("C", "claude-constitution", con_src)):
        for u in ledger(pilots / name / RUN / "units.json"):
            if u.get("missing_feature") == "causation":
                a, b = u["span"]
                rows[f"{prefix}:{u['id']}"] = {"span": [a, b], "bytes": b - a, "status": u["status"],
                                              "source": src[a:b].decode("utf-8"),
                                              "other_blockers": u.get("other_blockers", [])}
    pool = sorted(rows)
    sample = random.Random("ET-E3").sample(pool, 20)
    Path(out).write_text(json.dumps({"rule": 'random.Random("ET-E3").sample(sorted(pool), 20)',
                                     "pool_size": len(pool), "pool": pool, "sample": sample,
                                     "units": {k: rows[k] for k in sample}}, indent=1, ensure_ascii=False) + "\n")
    print(len(pool), sample)


if __name__ == "__main__":
    main(*sys.argv[1:])
