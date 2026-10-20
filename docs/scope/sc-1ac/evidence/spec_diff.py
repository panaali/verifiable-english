"""Compare sc-1ac's built declarations with docs/spec/scope.md 4.2 and 5.1, ignoring whitespace and comments, and
theorems up to `:=`. Run from the repository root: python3 docs/scope/sc-1ac/evidence/spec_diff.py"""
import re


def decls(text):
    text = re.sub(r"/-[-!].*?-/", "", text, flags=re.S)
    text = re.sub(r"--[^\n]*", "", text)
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^(def|theorem|structure|inductive) (\S+)", line)
        if m:
            cur = (m.group(1), m.group(2)); out[cur] = [line]; continue
        if line and not line[0].isspace():
            cur = None; continue
        if cur:
            out[cur].append(line)
    norm = {k: " ".join(" ".join(ls).split()) for k, ls in out.items()}
    return {k: (s.split(" := ")[0] if k[0] == "theorem" else s) for k, s in norm.items()}


blocks = re.findall(r"```lean\n(.*?)```", open("docs/spec/scope.md").read(), flags=re.S)
spec = {**decls(next(b for b in blocks if "namespace VE.Scope\nopen Lean" in b)),
        **decls(next(b for b in blocks if "theorem substOwn_no_own" in b))}
theorems = open("lean/VE/Scope/Theorems.lean").read()
built = {**decls(open("lean/VE/Scope/Govern.lean").read()), **decls(theorems[theorems.index("section Govern"):])}
# built before: sc-1a's two layout theorems, and sc-1ab's Effects.lean with its five theorems
earlier = {n for (_, n) in decls(open("lean/VE/Scope/Effects.lean").read())} | {"listRun_iff", "listRun_ok_iff",
    "substOwn_no_own", "substOwn_id", "commutes_symm", "mergeParts_keys", "mergeParts_conflict"}
print("sc-1ac statement diff against docs/spec/scope.md 4.2 and 5.1 (whitespace and comments ignored)\n")
for k in spec:
    if k in built and k[1] not in earlier:
        print(("exact   " if built[k] == spec[k] else "DIFFERS ") + f"{k[0]} {k[1]}")
        if built[k] != spec[k]:
            print("  spec : " + spec[k])
            print("  built: " + built[k])
print("\nnot built here (sc-1ad, sc-3ab, or later batches):",
      ", ".join(k[1] for k in spec if k not in built and k[1] not in earlier))
print("\nnot in the spec (helpers):", ", ".join(sorted(k[1] for k in built if k not in spec and k[1] not in earlier)))
