"""Spec 8.8 for df-5: every `norm-defaults` route case of the merge base answers byte for byte as main's service does.

Run once, saved: `uv run python docs/defeasible/df-5/evidence/conservativity.py <base cases.jsonl> <main ve_service>
<head ve_service> > docs/defeasible/df-5/evidence/conservativity.json` (the base file is `git show <merge-base>:tests/
data/route-cases.jsonl`, written before the run). Both services are this checkout's client, each with its own binary.
"""
import collections
import hashlib
import json
import sys
from pathlib import Path

from ve.backends.lean_service import LeanService

cases = [json.loads(line)[1] for line in Path(sys.argv[1]).read_text().splitlines()
         if json.loads(line)[0] == "norm-defaults"]
rows = {}
for name, binary in (("main", sys.argv[2]), ("head", sys.argv[3])):
    with LeanService(Path(binary), allow_unlisted_build=True, timeout=600) as service:
        out = []
        for start in range(0, len(cases), 16):
            chunk = cases[start:start + 16]
            text = json.dumps(chunk, ensure_ascii=False, separators=(",", ":"))
            out += [json.dumps(r["result"], sort_keys=True) for r in service.exchange("norm-defaults", text,
                                                                                      len(chunk))[1]["results"]]
        rows[name] = out
differ = [i for i, (a, b) in enumerate(zip(rows["main"], rows["head"])) if a != b]
print(json.dumps({"cases": len(cases), "kinds": dict(sorted(collections.Counter(
    str(c.get("kind")) for c in cases).items())), "identical": len(cases) - len(differ), "differ": differ,
    "main_rows": [rows["main"][i] for i in differ],
    "sha256": {k: hashlib.sha256("\n".join(v).encode()).hexdigest() for k, v in rows.items()}}, indent=1))
