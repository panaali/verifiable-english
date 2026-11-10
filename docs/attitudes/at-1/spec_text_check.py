"""at-1 statement gate (the pattern of docs/attitudes/at-1d/spec_text_check.py): each of the eight 6.1 statements
at-1 proves appears, with its docstring, after whitespace normalisation, in lean/VE/Attitudes/Theorems.lean, and is
followed there by ` :=`, so text appended to a statement (a weakened conclusion) is refused. No spec line differs and
none is added. Run from the repo root."""
import re
import sys

EIGHT = ("att_elaboration_faithful", "interp_admissible", "restrict_admissible", "restrict_intended", "interp_restrict",
         "old_formula_invariant", "att_old_language_conservative", "att_conservative_doc")
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
                                "### 6.2 AT-2 (`lean/VE/Attitudes/Route.lean`)") if theorem(p) in EIGHT]
missing = [theorem(p) for p in statements if norm("\n".join(p)) + " :=" not in src]
found = {theorem(p) for p in statements}
print(f"{len(statements)} statements, {len(missing)} missing, {len(found)} of 8 found", *missing, sep="\n")
sys.exit(1 if missing or found != set(EIGHT) or len(statements) != 8 else 0)
