#!/usr/bin/env python3
"""relb-clean-run: check.py <out-dir>: compare a clean run with the cloned DEMO.md.

verbatim: commands.txt's DEMO ids (1..4c) equal DEMO.md's sh lines, in order.
expected: step 4b's (and 4c's) stdout equals DEMO.md's expected-output block exactly; a unified diff otherwise.
Writes <out>/check.json and prints it.
"""
import difflib, json, os, re, sys

out = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
cmds = [l.rstrip("\n").split("\t", 1) for l in open(os.path.join(here, "commands.txt"), encoding="utf-8")
        if l.strip() and not l.startswith("#")]
demo = [c for i, c in cmds if not i.startswith(("h", "x"))]
res = {"steps": []}
if os.path.exists(f"{out}/steps.tsv"):
    rows = [l.rstrip("\n").split("\t") for l in open(f"{out}/steps.tsv", encoding="utf-8")][1:]
    res["steps"] = [{"id": r[0], "rc": int(r[1]), "seconds": int(r[2]), "start": r[3]} for r in rows]
md_path = f"{out}/DEMO.md"
if not os.path.exists(md_path):
    res["verbatim"] = res["expected"] = "no DEMO.md copied (the clone or step hrev failed)"
else:
    md = open(md_path, encoding="utf-8").read()
    lines = [l for b in re.findall(r"^```sh\n(.*?)^```", md, re.S | re.M) for l in b.splitlines() if l.strip()]
    res["verbatim"] = "EXACT" if lines == demo else {"demo_md": lines, "harness": demo}
    m = re.search(r"<!-- expected-output.*?-->\n```text\n(.*?)^```", md, re.S | re.M)
    exp = m.group(1) if m else None
    res["expected"] = {}
    for sid in ("4b", "4c"):
        p = f"{out}/step-{sid}.out"
        if exp is None or not os.path.exists(p):
            res["expected"][sid] = "not run" if exp is not None else "no expected-output block in DEMO.md"
            continue
        got = open(p, encoding="utf-8", errors="replace").read()
        if got == exp:
            res["expected"][sid] = "EXACT"
            continue
        diff = list(difflib.unified_diff(exp.splitlines(True), got.splitlines(True), "DEMO.md expected", f"step {sid}"))
        open(f"{out}/expected-{sid}.diff", "w", encoding="utf-8").writelines(diff)
        same_ws = [l.rstrip() for l in exp.splitlines() if l.strip()] == [l.rstrip() for l in got.splitlines() if l.strip()]
        res["expected"][sid] = (f"DIFFERS ({sum(1 for l in diff if l[:1] in '+-') - 2} +/- lines, expected-{sid}.diff)"
                                + ("; equal apart from whitespace" if same_ws else ""))
json.dump(res, open(f"{out}/check.json", "w"), indent=1)
print(json.dumps(res, indent=1))
