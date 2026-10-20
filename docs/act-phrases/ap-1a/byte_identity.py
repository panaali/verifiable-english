"""A31 of the act-phrases specification for ap-1a: without `acts@0`, today's documents decode byte-identically.

    uv run python docs/act-phrases/ap-1a/byte_identity.py --base ../base --out docs/act-phrases/ap-1a/evidence/byte-identity.json

Every case recorded from the suite in `tests/data/route-cases.jsonl` (all route modes, the norms family's decoders
among them) goes through the merge base's `ve_service` and this checkout's, in the same batches, and the two
answers are compared as JSON texts with sorted keys. ap-1a moves the act words to `VE.Acts.LexicalBase` and makes
`decodeRegulated` the `acts`-free case of `decodeRegulatedIn`; no answer may change. Exit 0 only when every case
gives identical answers on both sides.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from ve.backends.lean_service import LeanService
from ve.errors import VEError

HEAD = Path(__file__).resolve().parents[3]
CASES = HEAD / "tests/data/route-cases.jsonl"
SERVICE = "lean/.lake/build/bin/ve_service"


def answers(root: Path, rows: list) -> list[str]:
    service = LeanService(root / SERVICE, allow_unlisted_build=True)
    try:
        out = []
        for mode, case in rows:
            try:
                [result] = service.run(mode, [case])
                out.append(json.dumps(result, sort_keys=True, ensure_ascii=False))
            except VEError as refused:
                out.append("refused: " + refused.message)
        return out
    finally:
        service.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    rows = [json.loads(line) for line in CASES.read_text().splitlines() if line.strip()]
    base, head = answers(args.base.resolve(), rows), answers(HEAD, rows)
    differ = [{"mode": m, "case": c.get("id") if isinstance(c, dict) else None, "base": b[:300], "head": h[:300]}
              for (m, c), b, h in zip(rows, base, head) if b != h]
    report = {"cases": len(rows), "per_mode": dict(Counter(m for m, _ in rows)),
              "errors_on_both": sum(1 for b, h in zip(base, head) if b == h and '"status": "error"' in b),
              "identical": len(rows) - len(differ), "differing": differ}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    print(f"{report['identical']} of {report['cases']} identical, {len(differ)} differ")
    raise SystemExit(0 if not differ and rows else 1)


if __name__ == "__main__":
    main()
