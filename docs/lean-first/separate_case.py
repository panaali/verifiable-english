"""Turn a captured `readings-validate` case into one `readings-separate` case for a single pair.

    uv run --frozen python docs/lean-first/separate_case.py CASE.json ANSWER.json OUT.json

ANSWER.json is the route's answer to some (possibly smaller) case with the same first set; its first recorded
pair is the one asked. One pair costs the route's admission plus one replay, so comparing it across documents of
different sizes separates per-document from per-pair work.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

case_path, answer_path, out_path = map(Path, sys.argv[1:4])
case = json.loads(case_path.read_text())[0]
answer = json.loads(answer_path.read_text())[0]
first = answer["sets"][0]
pair = first["pairs"][0]
witness = pair["pair"]["witness"]
separate = {"id": "separate", "kind": "readings-separate", "environment": case["environment"],
            "document": case["document"], "set": first["set"], "situation": pair["pair"]["situation"],
            "other": pair["other"] if witness == pair["reading"] else pair["reading"]}
out_path.write_text(json.dumps([separate], ensure_ascii=False))
print(json.dumps({"set": separate["set"], "situation": separate["situation"], "other": separate["other"],
                  "bytes": out_path.stat().st_size}))
