"""at-1c statement gate: each declaration of the Lean blocks of docs/spec/attitudes.md 2.7-2.9 and seven 6.1 statements
appears, after whitespace normalisation, in lean/VE/Attitudes/{Frame,Semantics,Route,Theorems,Scale}.lean. 2.9's second
block (`pointCheck` in `VE.NormDefaults.Packs`) is AT-2's and is not read. No difference is allowed. Run from the repo
root."""
import re
import sys

SEVEN = ("frame_wellFormed", "frame_universalQF", "frameLabels_nodup", "framePairs_modes", "framePairs_transitive",
         "empty_relations_frame", "table_reviewed")
FILES = ("Frame", "Semantics", "Route", "Theorems", "Scale")
spec = open("docs/spec/attitudes.md").read().splitlines()
norm = lambda s: " ".join(s.split())
src = norm("\n".join(open(f"lean/VE/Attitudes/{f}.lean").read() for f in FILES))


def blocks(first, last, skip=()):
    """The docstring-and-declaration pieces of the Lean blocks between these two headings, but blocks holding `skip`."""
    lines = spec[spec.index(first):spec.index(last)]
    pieces, cur, block, inside = [], [], [], False
    for line in lines:
        if line.startswith("```"):
            if inside and not any(s in "\n".join(block) for s in skip):
                pieces += [p for p in cur if p]
            inside, cur, block = line.startswith("```lean"), [[]], []
            continue
        if inside:
            block.append(line)
            if re.match(r"^(/--|def |abbrev |structure |inductive |theorem |open )", line) and cur[-1] and \
                    not cur[-1][-1].endswith("-/"):
                cur.append([])
            cur[-1].append(line)
    return pieces


pieces = blocks("### 2.7 The frame", "## 3. English, one reading each", skip=("def pointCheck",))


def theorem(p):
    """The name of the theorem a piece (its docstring first, when it has one) states, or None."""
    m = re.search(r"^theorem (\S+)", "\n".join(p), re.M)
    return m.group(1) if m else None


statements = [p for p in blocks("### 6.1 AT-1 (`lean/VE/Attitudes/Theorems.lean`)", "### 6.2 AT-2 (`lean/VE/Attitudes/Route.lean`)")
              if theorem(p) in SEVEN]
missing = [norm("\n".join(p))[:100] for p in pieces + statements if norm("\n".join(p)) not in src]
found = {theorem(p) for p in statements}
print(f"{len(pieces)} pieces, {len(missing)} missing, {len(found)} of 7 statements", *missing, sep="\n")
sys.exit(1 if missing or found != set(SEVEN) or any("pointCheck" in " ".join(p) for p in pieces) else 0)
