import re, sys
KW = r"^(def|structure|inductive|abbrev|theorem|instance)\s+(\S+)"
def decls(text):
    text = re.sub(r"/-.*?-/", " ", text, flags=re.S)
    text = re.sub(r"--[^\n]*", "", text)
    out, cur, name = {}, [], None
    for line in text.split("\n"):
        m = re.match(KW, line)
        if m or re.match(r"^(namespace|end|section|open|import|#guard|#eval|/-!)", line):
            if name: out[name] = " ".join(" ".join(cur).split())
            name, cur = (m.group(2), [line]) if m else (None, [])
        elif name: cur.append(line)
    if name: out[name] = " ".join(" ".join(cur).split())
    return out
wire = decls(open(sys.argv[1]).read())
stub_text = open(sys.argv[2]).read()
a, b = stub_text.index("inductive Carrier where"), stub_text.index("def stmt_admit_regenerates")
stub = decls(stub_text[a:b])
spec = open(sys.argv[3]).read().split("\n")
specblocks = "\n".join(spec[int(sys.argv[4]) - 1:int(sys.argv[5])])
specd = {}
for blk in re.findall(r"```lean\n(.*?)```", specblocks, flags=re.S): specd.update(decls(blk))
differ = [n for n in wire if n in stub and wire[n] != stub[n]]
spec_differ = [n for n in wire if n in specd and wire[n] != specd[n]]
print("declarations", len(wire), "in stub", sum(n in stub for n in wire), "differing from stub", differ)
print("in spec 4.7 blocks", sum(n in specd for n in wire), "differing from spec", spec_differ)
print("not in stub:", [n for n in wire if n not in stub], "stub 4.7 names not in Wire.lean:", [n for n in stub if n not in wire])
