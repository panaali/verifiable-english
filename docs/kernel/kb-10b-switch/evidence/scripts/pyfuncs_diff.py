"""Task item (4): the ve/norms.py and ve/evaluate.py functions that no longer run under each safety-framework harness.
usage: pyfuncs_diff.py <dir with pyfuncs-{before,after}-<harness>.json> <out.json>
Writes, per harness and side: exit, totals, the function count of each file, and the full function lists of norms.py,
evaluate.py and softnorms.py; then the norms.py and evaluate.py functions gone and new. Prints the same diff."""
import json
import sys
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
FILES = ("norms.py", "evaluate.py", "softnorms.py")
report = {}
for harness in ("anthropic-rsp", "safety-framework", "openai-preparedness"):
    sides = {side: json.loads((src / f"pyfuncs-{side}-{harness}.json").read_text()) for side in ("before", "after")}
    entry = {side: {"exit": d["exit"], "total_functions": d["total_functions"], "total_lines": d["total_lines"],
                    "functions_per_file": {f: len(v["functions"]) for f, v in d["files"].items()},
                    **{f: d["files"].get(f, {}).get("functions", []) for f in FILES}}
             for side, d in sides.items()}
    for f in ("norms.py", "evaluate.py"):
        before, after = set(entry["before"][f]), set(entry["after"][f])
        entry[f"{f} gone"], entry[f"{f} new"] = sorted(before - after), sorted(after - before)
        print(harness, f, len(before), "->", len(after), "gone", entry[f"{f} gone"], "new", entry[f"{f} new"])
    report[harness] = entry
out.write_text(json.dumps(report, indent=1) + "\n")
