"""Verify-first check for srccov-claude-constitution-excerpt-1119 (run before any edit, on main).

For each candidate unit: the source sentence (source.md's numbered list, "N. " marker dropped), whether it occurs
byte for byte (and after omit_norm) in each file the reader is shown, which vocabulary entries hold it, and whether
claims.ve uses that entry. For the recording units: whether claims.ve holds any comment naming them.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
sys.path.insert(0, str(ROOT / "tests"))
from omission_rule import omit_norm  # noqa: E402

CASE = ROOT / "usecases/claude-constitution-excerpt"
text = (CASE / "source.md").read_text(encoding="utf-8")
section = text.split("## Excerpt formalised", 1)[1].split("\n## ", 1)[0]
S = {int(m.group(1)): m.group(2) for m in re.finditer(r"^(\d+)\. (.+)$", section, re.M)}
assert sorted(S) == list(range(1, 22))
FILES = ["environment.json", "definitions-environment.json", "environment.english.json", "rendered.md",
         "rendered-english.md", "claims.ve"]
claims = (CASE / "claims.ve").read_text(encoding="utf-8")
used = set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", claims))
env = json.loads((CASE / "environment.json").read_text(encoding="utf-8"))["vocabulary"]
ROWS = {"s6-1": [4], "s6-2": [5], "s6-3": [6], "s6-4": [7], "s6-5": [20], "s6-6": [21], "s6-8": [1, 16],
        "s6-9": [10, 13]}
for row, units in ROWS.items():
    for n in units:
        span = S[n]
        print(f"{row} S{n:04d}: {span[:60]!r}...")
        for f in FILES:
            body = (CASE / f).read_text(encoding="utf-8")
            raw = span in body
            norm = omit_norm(span) in omit_norm(body)
            line = next((i + 1 for i, l in enumerate(body.splitlines()) if span in l), None)
            print(f"   {f}: raw={raw} norm={norm} line={line}")
        for cat, entries in env.items():
            if not isinstance(entries, dict):
                continue
            for key, val in entries.items():
                if isinstance(val, dict) and span in json.dumps(val, ensure_ascii=False):
                    print(f"   legend {cat}.{key}: used_by_claims={key in used}")
print("claims.ve comment-like lines:", [l for l in claims.splitlines() if l.lstrip().startswith(("#", "--", "//"))])
print("claims.ve lines:", len(claims.splitlines()))
