"""at-1d statement gate (the pattern of docs/attitudes/at-1c/spec_text_check.py): each of the seven 6.1 statements
at-1d proves appears, with its docstring, after whitespace normalisation, in lean/VE/Attitudes/Theorems.lean, and is
followed there by ` :=`, so text appended to a statement (a weakened conclusion) is refused. No spec line differs and
none is added. Run from the repo root."""
import re
import sys

SEVEN = ("frame_iff_intended", "knows_factive", "seed_intended", "seed_least", "forced_iff_reachable",
         "mistaken_belief_admissible", "guard_collapse")
spec = open("docs/spec/attitudes.md").read().splitlines()
norm = lambda s: " ".join(s.split())
src = norm(open("lean/VE/Attitudes/Theorems.lean").read())


def pieces(first, last):
    """The docstring-and-declaration pieces of the Lean blocks between these two headings."""
    lines = spec[spec.index(first):spec.index(last)]
    out, inside = [], False
    for line in lines:
        if line.startswith("```"):
            inside = line.startswith("```lean")
            continue
        if not inside or not line.strip():
            continue
        if re.match(r"^(/--|theorem )", line) and not (out and out[-1][0].startswith("/--") and
                                                       out[-1][-1].endswith("-/") and line.startswith("theorem ")):
            out.append([])
        out[-1].append(line)
    return out


def theorem(p):
    m = re.search(r"^theorem (\S+)", "\n".join(p), re.M)
    return m.group(1) if m else None


statements = [p for p in pieces("### 6.1 AT-1 (`lean/VE/Attitudes/Theorems.lean`)",
                                "### 6.2 AT-2 (`lean/VE/Attitudes/Route.lean`)") if theorem(p) in SEVEN]
missing = [theorem(p) for p in statements if norm("\n".join(p)) + " :=" not in src]
found = {theorem(p) for p in statements}
print(f"{len(statements)} statements, {len(missing)} missing, {len(found)} of 7 found", *missing, sep="\n")
sys.exit(1 if missing or found != set(SEVEN) or len(statements) != 7 else 0)
