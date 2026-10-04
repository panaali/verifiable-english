"""Count the sets, candidates, pairs and findings of a `readings-validate` answer.

    uv run --frozen python docs/lean-first/count_answer.py ANSWER.json...
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

for name in sys.argv[1:]:
    row = json.loads(Path(name).read_text())[0]
    sets = row.get("sets", [])
    print(json.dumps({"answer": name, "status": row.get("status", "ok"), "error": row.get("error"),
                      "sets": len(sets), "candidates": sum(len(s["candidates"]) for s in sets),
                      "pairs": sum(len(s["pairs"]) for s in sets),
                      "findings": sum(len(s["findings"]) for s in sets)}))
