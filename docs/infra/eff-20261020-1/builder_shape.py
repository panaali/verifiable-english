"""Plan a small non-Lean change at the base of each replayed main commit whose drift holds a Lean change.

usage: builder_shape.py <checkout> <replay.json> <out.json>
"""
import json
import subprocess
import sys
from pathlib import Path

checkout, replay, out = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
sys.path.insert(0, str(checkout / "tools"))
import select_tests  # noqa: E402

EDITS = {"docs/TESTING.md": "\n<!-- edit -->\n", "ve/discourse.py": "\n# edit\n"}
rows = []
for row in json.load(open(replay)):
    if not row.get("drift_lean_files"):
        continue
    base = row["commit"] + "^"
    found = {"commit": row["commit"], "map": row["map"]}
    for path, tail in EDITS.items():
        text = subprocess.run(["git", "show", f"{base}:{path}"], cwd=checkout, check=True, capture_output=True,
                              text=True).stdout
        plan = select_tests.select(changes=[select_tests.Change(path, text, text + tail)], base=base)
        found[path] = {"selected": plan["selected_count"], "uncertain": plan["map"]["uncertain_units"],
                       "map_lean_cutoff": (plan.get("map_lean_cutoff") or {}).get("state")}
    print(json.dumps(found), flush=True)
    rows.append(found)
json.dump(rows, open(out, "w"), indent=1)
