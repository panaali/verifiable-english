"""Compare every theorem statement of lean/statements.txt at main with HEAD, ignoring the `-- uses` and `-- expr`
metadata lines (the expression hash moves when an auxiliary matcher is renumbered)."""
import subprocess, sys
def blocks(text):
    out, name, body = {}, None, []
    for line in text.splitlines():
        if line.startswith("theorem "):
            if name: out[name] = body
            name, body = line.split()[1], []
        elif name and not line.lstrip().startswith(("-- uses", "-- expr")):
            body.append(line)
    if name: out[name] = body
    return out
base_rev = sys.argv[1]
base = blocks(subprocess.run(["git", "show", f"{base_rev}:lean/statements.txt"], capture_output=True, text=True, check=True).stdout)
head = blocks(open("lean/statements.txt").read())
changed = sorted(n for n in base if n in head and base[n] != head[n])
removed = sorted(n for n in base if n not in head)
added = sorted(n for n in head if n not in base)
print(f"base {base_rev}: {len(base)} theorems; HEAD: {len(head)}")
print(f"statements changed: {len(changed)} {changed}")
print(f"theorems removed: {len(removed)} {removed}")
print(f"theorems added: {len(added)}")
for n in added: print("  +", n)
for n in ["VE.Discourse.acc_no_heuristic", "VE.Discourse.name_scope", "VE.Discourse.innermost_within", "VE.Discourse.narrower_mem"]:
    print(f"{n}: {'unchanged' if base.get(n) == head.get(n) and n in base else 'CHANGED'}")
