"""ap-4b statement gate: each declaration below equals the specification's text, whitespace normalised.

    python3 docs/act-phrases/ap-4b/check_statements.py

Reads each from docs/spec/act-phrases.md section 7 (up to the next declaration, docstring, `end` or fence) and from
lean/VE/Acts/Sources.lean or Situation.lean (a theorem up to its `:=`; a definition, structure or abbreviation whole,
up to the next declaration or docstring). Exit 1 on any difference or a declaration missing on either side.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAN = "lean/VE/Acts/Sources.lean"
# (keyword, name, whole[, Lean file]): `whole` compares the body too
DECLS = [
    ("theorem", "sourceCheck_exact", False),
    ("def", "SourceExact", True),
    ("structure", "Source", True),
    ("abbrev", "View", True),
    ("def", "expected", True),
    ("def", "choicesOn", True),
    ("def", "choiceViews", True),
    ("def", "readingViews", True),
    ("def", "ruleView", False),
    ("def", "choiceRules", False),
    ("def", "opOfSource", False),
    ("def", "sourceCheck", False),
    ("def", "atomSituation", False, "lean/VE/Acts/Situation.lean"),
]
NEXT = ["\ntheorem", "\n/--", "\ndef ", "\nend ", "\n```", "\nabbrev", "\nstructure", "\nset_option", "\ninstance"]


def cut(text, kw, name, ends):
    i = text.index(f"{kw} {name} ")
    j = min(k for k in (text.find(e, i + 1) for e in ends) if k > 0)
    return " ".join(text[i:j].split())


def main():
    spec = (ROOT / "docs/spec/act-phrases.md").read_text()
    spec = spec[spec.index("## 7. AP-4"):spec.index("\n## 8. ")]
    bad = []
    for kw, name, whole, *path in DECLS:
        lean = (ROOT / (path[0] if path else LEAN)).read_text()
        ends = NEXT if whole else NEXT + [" :=", "\n:="]
        want, have = cut(spec, kw, name, ends), cut(lean, kw, name, ends)
        print(("EQUAL " if want == have else "DIFF  ") + f"{kw} {name}")
        if want != have:
            print("  spec:", want, "\n  lean:", have)
            bad.append(name)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
