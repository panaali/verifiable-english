"""ps-2aa's probe form for ps-2ac: each declaration of Run.lean (its text, comments stripped and whitespace
normalised) against every same-named declaration in the spec's Lean blocks and in the PS-S stub.
Usage: probe.py Run.lean presupposition.md SpecStubs_presupposition.lean"""
import re, sys
HEAD = r"^(?:def|theorem|structure|inductive|abbrev)\s+([^\s(:]+)"
def decls(text):
    text = re.sub(r"/-.*?-/", " ", text, flags=re.S)
    text = re.sub(r"--[^\n]*", "", text)
    out, cur, name = {}, [], None
    for line in text.split("\n"):
        m = re.match(HEAD, line)
        if m or re.match(r"^(namespace|end|universe|import|open|#guard|#eval)\b", line):
            if name: out[name] = " ".join(" ".join(cur).split())
            name, cur = (m.group(1), [line]) if m else (None, [])
        elif name: cur.append(line)
    if name: out[name] = " ".join(" ".join(cur).split())
    return out
run = decls(open(sys.argv[1]).read())
spec = decls("\n".join(re.findall(r"```lean\n(.*?)```", open(sys.argv[2]).read(), flags=re.S)))
stub = decls(open(sys.argv[3]).read())
named = {n: (n in spec, n in stub) for n in run}
print("Run.lean declarations", len(run), "named in the spec", sum(a for a, _ in named.values()),
      "named in the stub", sum(b for _, b in named.values()))
print("differing", [n for n in run if (n in spec and spec[n] != run[n]) or (n in stub and stub[n] != run[n])])
print("same name elsewhere", [n for n, (a, b) in named.items() if a or b])
