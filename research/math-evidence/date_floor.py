"""ME-0, P6 (fixture H-10): is a W6a date of 1887 refused today, with a 1970-01-01 control admitted?

Builds two one-unit `ve-document@1` files whose source is "July 8, 1887.\n" (and "January 1, 1970.\n"), each stating
the observation date as a `day` quantity, and runs `ve document check` in today's VE. Writes
`docs/research/evidence/math-evidence/date-floor.json`.

    prlimit --as=6442450944 $VE_CHECKOUT/.venv/bin/python -I research/math-evidence/date_floor.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ledger import BASE_ENV, EVIDENCE, run_ve  # noqa: E402

CASES = {"1887-07-08": "July 8, 1887.\n", "1970-01-01": "January 1, 1970.\n"}


def document(iso: str, text: str) -> bytes:
    env = dict(BASE_ENV, unit_schema="ve-units@1", units={"day": {"scale": "1", "display": {"kind": "iso_date"}}},
               vocabulary={"sorts": {}, "predicates": {}, "constants": {"observation_date": {
                   "sort": "$int", "unit": "day", "description": "date of the observation",
                   "verbalisation": "the observation date"}}})
    src = text.encode()
    unit = {"id": "date", "span": [0, len(src)], "kind": "asserted", "meaning": "specified", "support": "testimony",
            "content": {"quantity": {"format": "ve-quantity@1", "formula": [
                "date_on", ["const", "day", "observation_date"], ["date", iso]]}}}
    meta = {"format": "ve-document@1", "environment": env, "units": [unit]}
    return b"---\n" + json.dumps(meta, indent=1).encode() + b"\n---\n" + src


def main() -> int:
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        for iso, text in CASES.items():
            path = Path(tmp) / f"date-{iso}.ve.md"
            path.write_bytes(document(iso, text))
            code, answer = run_ve(["document", "check", str(path)])
            last = answer.strip().splitlines()[-1] if answer.strip() else ""
            out[iso] = {"exit": code, "accepted": code == 0 and '"error"' not in answer,
                        "last_line": last[:400]}
    out["pass"] = (not out["1887-07-08"]["accepted"]) and out["1970-01-01"]["accepted"]
    (EVIDENCE / "date-floor.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
