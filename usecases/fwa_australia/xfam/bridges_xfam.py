"""CROSS-FAMILY age bridge input and output: the encoder's records' own dates (cases_xfam.DOB[id], the stated date of birth;
the case's notice day dn_e) -> xfam/bridge/inputs.jsonl, then the FROZEN bridge function (bridge/age.py age(), unchanged; its
main() reads only the same-family inputs file) -> xfam/bridge/bridges.jsonl in the same format.
usage (repository root): python3 -I usecases/fwa_australia/xfam/bridges_xfam.py"""
import json
import sys
from pathlib import Path

X = Path(__file__).resolve().parent
sys.path.insert(0, str(X.parent / "bridge"))
sys.path.insert(0, str(X))
import age as AGE  # noqa: E402
import cases_xfam as K  # noqa: E402

rows = [{"case": c["id"], "date": c["ints"]["dn_e"], "dob": K.DOB[c["id"]]} for c in K.CASES]
(X / "bridge" / "inputs.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
out = []
for r in rows:
    y, n = AGE.age(r["dob"], r["date"])
    out.append({"case": r["case"], "years": y, "days": n})
(X / "bridge" / "bridges.jsonl").write_text("".join(json.dumps(o, sort_keys=True) + "\n" for o in out), encoding="utf-8")
print(f"bridges.jsonl: {len(out)} rows")
