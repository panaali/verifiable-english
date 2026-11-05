"""at-1a statement gate: each declaration of the Lean blocks of docs/spec/attitudes.md 2.1-2.4 (lines 242-552)
appears, after whitespace normalisation, in lean/VE/Attitudes/Scale.lean + Syntax.lean. Run from the repo root."""
import re
import sys

spec = open("docs/spec/attitudes.md").read().splitlines()[241:552]
norm = lambda s: " ".join(s.split())
src = norm(open("lean/VE/Attitudes/Scale.lean").read() + "\n" + open("lean/VE/Attitudes/Syntax.lean").read())
pieces, cur, inside = [], [], False
for line in spec:
    if line.startswith("```"):
        inside = line.startswith("```lean")
        if cur:
            pieces.append(cur)
        cur = []
        continue
    if inside:
        if re.match(r"^(/--|def |abbrev |structure |inductive |theorem )", line) and cur:
            pieces.append(cur)
            cur = []
        cur.append(line)
missing = [norm("\n".join(p))[:100] for p in pieces if norm("\n".join(p)) not in src]
print(f"{len(pieces)} pieces, {len(missing)} missing", *missing, sep="\n")
sys.exit(1 if missing else 0)
