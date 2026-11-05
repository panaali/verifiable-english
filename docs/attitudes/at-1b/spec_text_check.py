"""at-1b statement gate: each declaration of the Lean blocks of docs/spec/attitudes.md 2.5-2.6 and the five 6.1
statements appears, after whitespace normalisation, in lean/VE/Attitudes/Syntax.lean or Theorems.lean. Two differences are
allowed, by exact string: D14c's call, at both of its lines (reviews/dri-decisions-20261105-at-1b.md item 1), and
`checkNames`'s read of the identifier limit, at its one line (reviews/dri-decisions-20261105-at-1b-limit.md item 1). Run
from the repo root."""
import re
import sys

# (the spec's text, the source's, how many times each occurs)
SIGNED = (("(A.lex.lexicon.wordings.lookup p).bind VE.Reports.wantsPhrase?",
           '(A.lex.lexicon.wordings.lookup p).bind (fun w => VE.Reports.wantsPhrase? (w.stripPrefix "{0} "))', 2),
          ("throwIf (n.utf8ByteSize > 64) s!", "throwIf (n.utf8ByteSize > VE.Limits.maxIdentifierBytes) s!", 1))
FIVE = ("names_fresh", "names_injective", "keyOf_name", "envAtt_extends", "toNorms_wellFormed")
spec = open("docs/spec/attitudes.md").read().splitlines()
norm = lambda s: " ".join(s.split())
src = norm(open("lean/VE/Attitudes/Syntax.lean").read() + "\n" + open("lean/VE/Attitudes/Theorems.lean").read())


def blocks(first, last):
    """The docstring-and-declaration pieces of the Lean blocks between these two section headings."""
    lines = spec[spec.index(first):spec.index(last)]
    pieces, cur, inside = [], [], False
    for line in lines:
        if line.startswith("```"):
            inside = line.startswith("```lean")
            if cur:
                pieces.append(cur)
            cur = []
            continue
        if inside:
            if re.match(r"^(/--|def |abbrev |structure |inductive |theorem )", line) and cur and not cur[-1].endswith("-/"):
                pieces.append(cur)
                cur = []
            cur.append(line)
    return pieces


pieces = blocks("### 2.5 Elaboration", "### 2.7 The frame")
pieces += [p for p in blocks("### 6.1 AT-1 (`lean/VE/Attitudes/Theorems.lean`)", "### 6.2 AT-2 (`lean/VE/Attitudes/Route.lean`)")
           if re.match(r"^theorem (\S+)", p[0]) and re.match(r"^theorem (\S+)", p[0]).group(1) in FIVE]
spec_text = [norm("\n".join(p)) for p in pieces]
signed = [sum(s.count(old) for s in spec_text) for old, _, _ in SIGNED]


def signed_form(s):
    for old, new, _ in SIGNED:
        s = s.replace(old, new)
    return s


missing = [s[:100] for s in spec_text if signed_form(s) not in src]
found = {m.group(1) for p in pieces for m in [re.match(r"^theorem (\S+)", p[0])] if m}
wrong = [old[:40] for (old, new, n), got in zip(SIGNED, signed) if got != n or src.count(new) != n or old in src]
print(f"{len(pieces)} pieces, {len(missing)} missing, {signed} signed differences, {len(found)} of 5 statements", *missing, *wrong, sep="\n")
sys.exit(1 if missing or wrong or found != set(FIVE) else 0)
