"""Replay `select_tests.py --commit <c> --json` from one checkout over main's last N first-parent commits.

usage: replay.py <checkout> <python> <out.json> [N]
"""
import json
import subprocess
import sys
import time

checkout, python, out = sys.argv[1:4]
count = int(sys.argv[4]) if len(sys.argv) > 4 else 30
commits = subprocess.run(["git", "log", "--first-parent", "--format=%H", f"-{count}", "main"], cwd=checkout,
                         check=True, capture_output=True, text=True).stdout.split()
rows = []
for commit in commits:
    started = time.monotonic()
    result = subprocess.run([python, "tools/select_tests.py", "--commit", commit, "--json"], cwd=checkout,
                            capture_output=True, text=True)
    if result.returncode:
        rows.append({"commit": commit, "error": result.stderr[-2000:]})
        continue
    plan = json.loads(result.stdout)
    drift_lean = None
    if plan["map"]:
        names = subprocess.run(["git", "diff", "--no-renames", "--name-only", plan["map"]["commit"], f"{commit}^"],
                               cwd=checkout, check=True, capture_output=True, text=True).stdout.split()
        drift_lean = sorted(p for p in names if (p.startswith("lean/") and p.endswith(".lean"))
                            or p in ("lean/lakefile.toml", "lean/lean-toolchain", "lean/lake-manifest.json"))
    cut = plan.get("lean_cutoff") or {}
    drift_cut = plan.get("map_lean_cutoff") or {}
    rows.append({"commit": commit, "map": plan["map"]["commit"] if plan["map"] else None,
                 "drift_files": plan["map"]["files_changed_since"] if plan["map"] else None,
                 "drift_lean_files": len(drift_lean) if drift_lean is not None else None,
                 "uncertain": plan["map"]["uncertain_units"] if plan["map"] else None,
                 "selected": plan["selected_count"], "full_count": plan["full_count"], "full": plan["full"],
                 "selected_units": plan["selected"],
                 "unmapped": plan["unmapped"] if isinstance(plan["unmapped"], list) else None,
                 "lean_cutoff": cut.get("state"), "lean_cutoff_rebuilt": cut.get("rebuilt"),
                 "map_lean_cutoff": drift_cut.get("state"), "map_lean_cutoff_rebuilt": drift_cut.get("rebuilt"),
                 "seconds": round(time.monotonic() - started, 1)})
    print(commit[:10], rows[-1]["map"] and rows[-1]["map"][:10], rows[-1]["drift_files"], rows[-1]["drift_lean_files"],
          rows[-1]["uncertain"], rows[-1]["selected"], rows[-1]["lean_cutoff"], "|", rows[-1]["map_lean_cutoff"],
          flush=True)
json.dump(rows, open(out, "w"), indent=1)
