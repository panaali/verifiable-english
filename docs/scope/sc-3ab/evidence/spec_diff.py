"""sc-3ab's statement gate. Compares the declarations built here with docs/spec/scope.md 4.2 and 5.5 (whitespace and
comments ignored, theorems up to `:=`), and the compiled statements (lean/statements.txt) of the sc-3a theorems this
item must keep with those at the merge base 68f18dcdc. Run from the repository root:
python3 docs/scope/sc-3ab/evidence/spec_diff.py"""
import re
import subprocess


def decls(text):
    text = re.sub(r"/-[-!].*?-/", "", text, flags=re.S)
    text = re.sub(r"--[^\n]*", "", text)
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^(def|theorem) (\S+)", line)
        if m:
            cur = m.group(2); out[cur] = [line]; continue
        if line and not line[0].isspace():
            cur = None; continue
        if cur:
            out[cur].append(line)
    norm = {k: " ".join(" ".join(ls).split()) for k, ls in out.items()}
    return {k: (s.split(" := ")[0] if s.startswith("theorem") else s) for k, s in norm.items()}


def statements(text):
    out, cur = {}, None
    for line in text.splitlines():
        if line.startswith(("theorem ", "def ")):
            cur = line.split()[1]; out[cur] = []
        elif cur and not line.startswith("  -- "):
            out[cur].append(line)
    return {k: " ".join(" ".join(v).split()) for k, v in out.items()}


blocks = re.findall(r"```lean\n(.*?)```", open("docs/spec/scope.md").read(), flags=re.S)
spec = {**decls(next(b for b in blocks if "namespace VE.Scope\nopen Lean" in b)),
        **decls(next(b for b in blocks if "theorem anchor_reach_iff" in b))}
built = {**decls(open("lean/VE/Scope/Govern.lean").read()), **decls(open("lean/VE/Scope/Theorems.lean").read())}
print("sc-3ab statement diff against docs/spec/scope.md 4.2 and 5.5 (whitespace and comments ignored)\n")
for name in ["coveredLayout", "kindOf", "defSpans", "admitBlock", "anchor_reach_iff", "label_reach_iff", "title_identity"]:
    if name not in built:
        print(f"NOT BUILT {name} (the statement gate: false as stated, F-raw-title)")
    elif built[name] == spec[name]:
        print(f"exact     {name}")
    else:
        a, b = spec[name].split(), built[name].split()
        i = next(i for i in range(min(len(a), len(b))) if a[i] != b[i])
        print(f"DIFFERS   {name}: spec `{' '.join(a[i:i + 4])}`, built `{' '.join(b[i:i + 4])}`")

base = statements(subprocess.run(["git", "show", "17ea952d883cc269dbc37f0879e2e52b3a6d1ac2:lean/statements.txt"], capture_output=True, text=True,
                                 check=True).stdout)
head = statements(open("lean/statements.txt").read())
print("\nsc-3a's statements, compiled, at 68f18dcdc and on this tree:\n")
for name in ["VE.Discourse.acc_no_heuristic", "VE.Discourse.name_scope", "VE.Discourse.innermost_within",
             "VE.Layout.discourse_anchorsOk_unchanged", "VE.Layout.discourse_within_unchanged",
             "VE.Layout.discourse_innermost_unchanged", "VE.Layout.anchorReach_iff", "VE.Layout.itemRun_iff"]:
    print(("unchanged " if base[name] == head[name] else "CHANGED   ") + name)
changed = sorted(n for n in base if n in head and base[n] != head[n])
print(f"\nall {len(base)} statements at 68f18dcdc: {len(changed)} changed, "
      f"{len([n for n in base if n not in head])} removed" + (": " + ", ".join(changed) if changed else ""))
