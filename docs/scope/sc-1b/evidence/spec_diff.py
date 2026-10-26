"""Compare SC-1b's built statements with docs/spec/scope.md 5.2 (spec 8.1's `Pinned.` placeholders resolved to the names
built) and with the plan's SC-1b block, ignoring whitespace and comments, theorems up to `:=`.
Run from the repository root: python3 docs/scope/sc-1b/evidence/spec_diff.py"""
import re


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
    return {k: s.split(" := ")[0] if s.startswith("theorem") else s for k, s in norm.items()}


def block(path, marker):
    return next(b for b in re.findall(r"```lean\n(.*?)```", open(path).read(), flags=re.S) if marker in b)


spec = {k: v.replace("Pinned.", "") for k, v in decls(block("docs/spec/scope.md", "theorem scope_admission")).items()}
plan = {k: v.replace("Lean.Json", "Json") for k, v in decls(block("docs/spec/scope-PLAN.md", "theorem scope_admission")).items()}
built = {**decls(open("lean/VE/Scope/Wire.lean").read()), **decls(open("lean/VE/Service/ScopeAdmission.lean").read())}
print("sc-1b statement diff (whitespace and comments ignored; spec 8.1's Pinned. resolved; plan's Lean.Json read as Json)\n")
for name in spec:
    if name in built:
        s = "exact" if built[name] == spec[name] else "DIFFERS"
        p = "absent" if name not in plan else "exact" if built[name] == plan[name] else "differs"
        print(f"{s:8} {name}   (spec 5.2; plan: {p})")
        if s == "DIFFERS":
            print("  spec : " + spec[name] + "\n  built: " + built[name])
    else:
        print(f"NOT BUILT {name}   (sc-1ae: BlockBound, HasStr)")
