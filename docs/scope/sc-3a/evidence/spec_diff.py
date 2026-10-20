"""Compare SC-3a's built declarations with docs/spec/scope.md 4.1 and 5.5, ignoring whitespace and comments,
and theorems up to `:=`."""
import re
KW = r"^(def|theorem|structure|inductive|open|namespace|end|/-!)"
def decls(text):
    text = re.sub(r"/-[-!].*?-/", "", text, flags=re.S)          # doc and module comments
    text = re.sub(r"--[^\n]*", "", text)                          # line comments
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^(def|theorem|structure|inductive) (\S+)", line)
        if m: cur = (m.group(1), m.group(2)); out[cur] = [line]; continue
        if re.match(r"^(open|namespace|end|#guard|import)", line) or (line and not line[0].isspace()): cur = None; continue
        if cur: out[cur].append(line)
    norm = {}
    for k, ls in out.items():
        s = " ".join(" ".join(ls).split())
        if k[0] == "theorem": s = s.split(" := ")[0]
        norm[k] = s
    return norm
spec = open("docs/spec/scope.md").read()
blocks = re.findall(r"```lean\n(.*?)```", spec, flags=re.S)
s41 = decls(blocks[[i for i, b in enumerate(blocks) if "namespace VE.Layout" in b][0]])
s55 = decls([b for b in blocks if "theorem itemRun_iff" in b][0])
built = {}
for f in ["lean/VE/Layout/Discourse.lean", "lean/VE/Layout/Anchors.lean", "lean/VE/Layout/List.lean"]:  # Before.* share short names
    built.update(decls(open(f).read()))
names41 = ["itemFrom", "itemRun", "ItemUnit", "spansOf", "within", "narrower", "innermostAnchor", "anchorUnits",
           "headingOf", "anchorReach", "reachesRoot", "anchorsOk"]
names55 = ["itemRun_iff", "anchorReach_iff", "discourse_within_unchanged", "discourse_innermost_unchanged",
           "discourse_anchorsOk_unchanged"]
exact, differ = [], []
for src, names in ((s41, names41), (s55, names55)):
    for n in names:
        k = next(k for k in src if k[1] == n)
        (exact if built.get(k) == src[k] else differ).append(f"{k[0]} {n}")
        if built.get(k) != src[k]: print("SPEC ", src[k]); print("BUILT", built.get(k))
print(f"sc-3a statement diff against docs/spec/scope.md 4.1 (anchor and item parts) and 5.5 (VE.Layout)\n")
print(f"exact ({len(exact)}):"); [print("  " + x) for x in exact]
print(f"\ndiffer ({len(differ)}):"); [print("  " + x) for x in differ]
rest = sorted(k[1] for k in s55 if k[1] not in names55)
print(f"\nnot built in sc-3a, spec 5.5 (sc-3ab, after sc-1ac's SDoc and govern; or SC-3b) ({len(rest)}):")
[print("  " + x) for x in rest]
