"""Check dated fuzz signatures against batch 14c's base revision.

Usage: uv run python docs/lean-first/b14c/date_seed_replay.py BASE_ROOT REPORT_DIR OUT
Each completed date seed may find signatures outside the fixed CI baseline.
Those signatures must reproduce unchanged on the base; this script does not
add them to the baseline or treat a head-only signature as approved.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import runpy
import subprocess
import sys

from tests.subprocesses import HANG_TIMEOUT

SETTINGS = runpy.run_path(str(Path(__file__).with_name("fuzzer_seeds.py")))
SEEDS = SETTINGS["SEEDS"]
BASELINE_ENTRIES = SETTINGS["BASELINE_ENTRIES"]


REPLAY = """import json,sys
from tools import difffuzz as d
entries=json.load(sys.stdin)
built={name:d.SURFACES[name]() for name in {e['surface'] for e in entries}}
try:
    rows=d.replay(entries,built)
    print(json.dumps([{'id':e['id'],'status':status,'base_signature':now['signature']}
                      for e,status,now in rows]))
finally:
    for surface in built.values(): surface.close()
"""


def main() -> int:
    base, scratch, out = map(Path, sys.argv[1:])
    reports = [json.loads((scratch / f"{seed}.json").read_text()) for seed in SEEDS]
    entries = [entry for report in reports for entry in report["new"]]
    env = {**os.environ, "PYTHONPATH": str(base)}
    done = subprocess.run([sys.executable, "-c", REPLAY], cwd=base, env=env,
                          input=json.dumps(entries), text=True, capture_output=True,
                          check=True, timeout=HANG_TIMEOUT)
    replay = json.loads(done.stdout)
    changed = [row for row in replay if row["status"] != "reproduces"]
    checks = [dict(seed=seed, new=len(report["new"]),
                   baseline_entries=report["baseline"]["entries"],
                   baseline_not_reproduced=len(report["baseline"]["not_reproduced"]),
                   sampled=sum(sum(group.values()) for group in report["mutants"].values()))
              for seed, report in zip(SEEDS, reports, strict=True)]
    passed = (len(reports) == len(SEEDS) and len(replay) == len(entries) and not changed and
              all(report["seed"] == seed and report["baseline"]["entries"] == BASELINE_ENTRIES and
                  not report["baseline"]["not_reproduced"] and
                  not report["baseline"]["unreviewed"]
                  for seed, report in zip(SEEDS, reports, strict=True)))
    out.write_text(json.dumps({"pass": passed, "seeds": checks,
                               "new_signatures": len(entries), "base_reproduced": len(replay) - len(changed),
                               "changed": changed}, indent=2, sort_keys=True) + "\n")
    print(f"{len(reports)} date seeds; {len(entries)} signatures outside the fixed CI baseline; "
          f"{len(replay) - len(changed)} reproduce on base; pass={passed}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
