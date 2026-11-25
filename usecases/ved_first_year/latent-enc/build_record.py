"""Build latent-enc/mcaravan.json (encode.py C6) from the fresh encoder seat's enc.jsonl (latent-ved-1125).

Set "a" = questions-enc.jsonl (cases.py), set "b" = xfam/questions-enc.jsonl (xfam/cases_xfam.py). Vehicles are matched by
order (cases.py: one vehicle v1; cases_xfam.py: V[case] in order, ids v1, v2, ...) and the owner names are checked against
cases_xfam.V. Every frozen case is keyed by id + "/" + the sha256 of its encoded vehicles (encode.vehicles_sha256).
usage (repository root): .venv/bin/python -B usecases/ved_first_year/latent-enc/build_record.py
"""
import hashlib
import json
import sys
from pathlib import Path

L = Path(__file__).resolve().parent
UC = L.parent
sys.path[:0] = [str(UC), str(UC / "xfam"), str(UC.parents[1])]
import cases as KA  # noqa: E402
import cases_xfam as KB  # noqa: E402
import encode as E  # noqa: E402

enc = [json.loads(x) for x in (L / "enc.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
by = {(r["set"], r["id"]): r["vehicles"] for r in enc}
out, keys = {}, []
for s, K in (("a", KA), ("b", KB)):
    for c in K.CASES:
        key = c["id"] + "/" + E.vehicles_sha256(c)
        keys.append(f"{s}:{key}")
        got = by.get((s, c["id"]))
        if got is None or len(got) != len(c["vehicles"]):
            raise SystemExit(f"set {s} {c['id']}: encoder record missing or vehicle count differs")
        if s == "b":
            owners = [v["owner"] for v in KB.V[c["id"]]]
            if [g["owner"] for g in got] != owners:
                raise SystemExit(f"set b {c['id']}: owners {[g['owner'] for g in got]} != {owners}")
        if key in out:
            raise SystemExit(f"{key}: the two sets share a case fingerprint")
        out[key] = {v["id"]: g["mcaravan"] for v, g in zip(c["vehicles"], got)}
rec = {"format": "ved-mcaravan@1", "source": "latent-enc/enc.jsonl sha256 "
       + hashlib.sha256((L / "enc.jsonl").read_bytes()).hexdigest(),
       "sets": {"a": KA.ENC_SHA256, "b": KB.ENC_SHA256}, "frozen_cases": sorted(keys), "cases": out}
(L / "mcaravan.json").write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n", encoding="utf-8")
vals = [v for d in out.values() for v in d.values()]
print(f"{len(out)} cases, {len(vals)} vehicles: true {vals.count(True)}, false {vals.count(False)}, "
      f"unknown {vals.count(None)}")
