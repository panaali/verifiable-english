"""py_under.py before/after comparison for kb-10b step (4): which ve/norms.py functions stop running under each harness.
usage: pyunder_diff.py <harness>... (reads /tmp/kb10bs/pyunder-{before,after}-<harness>.json)"""
import json, sys, subprocess
def funcs(path, f):
    d = json.load(open(path))
    return d
for h in sys.argv[1:]:
    b = json.load(open(f"/tmp/kb10bs/pyunder-before-{h}.json")); a = json.load(open(f"/tmp/kb10bs/pyunder-after-{h}.json"))
    print(h, "total lines", b["total_lines"], "->", a["total_lines"], "functions", b["total_functions"], "->", a["total_functions"])
    for key in ("norms_functions",):
        gone = sorted(set(b[key]) - set(a[key])); new = sorted(set(a[key]) - set(b[key]))
        print("  norms.py gone:", gone); print("  norms.py new:", new)
    for f in ("evaluate.py", "norms.py", "softnorms.py"):
        print("  ", f, b["files"].get(f), "->", a["files"].get(f))
