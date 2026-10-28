"""Append the flag's genuine `norm-defaults` cases to tests/data/route-cases.jsonl (df-1bb, append-only).

Record first: `VE_ROUTE_CASES=<dir> uv run pytest -q -p tests.route_case_recorder tests/test_defaults_lean.py
-k "p1 or beta_forced or gamma_collision or delta or epsilon"`, then `uv run python <this file> <dir> [--write]`.
Kept: every case of P-1's documents (`claude_instance`), and the smallest other case of each group (kind, with a
strict model, with a collision, number of rules) not already in the file; none over 50,000 bytes.
"""
import collections
import json
import sys
from pathlib import Path

FILE = Path("tests/data/route-cases.jsonl")
existing = set(FILE.read_text().splitlines())
groups = collections.defaultdict(list)
for path in sorted(Path(sys.argv[1]).glob("*.jsonl")):
    for mode, text in map(json.loads, path.read_text().splitlines()):
        line = f'["{mode}",{text}]'
        if mode == "norm-defaults" and line not in existing and len(line) < 50_000:
            case = json.loads(text)
            groups[(case["kind"], "strict_model" in case, "collision" in case, len(case["norms"]))].append(line)
picked = []
for key in sorted(groups, key=str):
    lines = groups[key]
    picked += [line for line in lines if "claude_instance" in line]
    picked += sorted((line for line in lines if "claude_instance" not in line), key=len)[:1]
print(len(picked), "cases,", sum(map(len, picked)), "bytes")
if "--write" in sys.argv:
    with FILE.open("a") as out:
        out.writelines(line + "\n" for line in picked)
