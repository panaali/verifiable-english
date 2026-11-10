"""ps-2aa's probe form for ps-2ab: each theorem of Statements.lean (its text up to `:=`) against spec 4.7's
statements block, comments stripped and whitespace normalised. Usage: probe.py Statements.lean presupposition.md"""
import re, sys
def decls(text):
    text = re.sub(r"/-.*?-/", " ", text, flags=re.S)
    text = re.sub(r"--[^\n]*", "", text)
    out, cur, name = {}, [], None
    for line in text.split("\n"):
        m = re.match(r"^theorem\s+(\S+)", line)
        if m or re.match(r"^(def|namespace|end|universe|import)\b", line):
            if name: out[name] = " ".join(" ".join(cur).split()).split(" :=")[0]
            name, cur = (m.group(1), [line]) if m else (None, [])
        elif name: cur.append(line)
    if name: out[name] = " ".join(" ".join(cur).split()).split(" :=")[0]
    return out
lean = decls(open(sys.argv[1]).read())
spec = open(sys.argv[2]).read()
a = spec.index("**Statements.** `admit` is PS-2a's function")
block = re.search(r"```lean\n(.*?)```", spec[a:], flags=re.S).group(1)
want = decls(block)
print("spec statements", len(want), "proved here", sum(n in lean for n in want))
print("equal", sum(lean.get(n) == s for n, s in want.items()), "differing", [n for n, s in want.items() if lean.get(n) != s])
print("missing", [n for n in want if n not in lean], "helpers (not in the spec)", [n for n in lean if n not in want])
