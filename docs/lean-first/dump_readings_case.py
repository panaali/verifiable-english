"""Write the single `ve_readings_route` case a document's load sends, then stop (no Lean call).

    uv run --frozen python docs/lean-first/dump_readings_case.py DOCUMENT OUT.json [--sets N]

`--sets N` keeps the first N reading sets of the case's document, so the route's cost can be measured
against the number of sets: `ve_readings_route - < OUT.json`.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


class _Captured(Exception):
    pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--sets", type=int)
    args = parser.parse_args()
    import ve.readings_route as route
    from ve.document import load_document

    def capture(cases, **_):
        raise _Captured(cases)

    route.run_lean = capture
    try:
        load_document(args.document)
    except _Captured as captured:
        cases = captured.args[0]
    else:
        raise SystemExit("the document made no readings-validate call")
    if args.sets is not None:
        for case in cases:
            document = case["document"]
            sets = document.get("reading_sets", [])
            document["reading_sets"] = sets[:args.sets]
    args.out.write_text(json.dumps(cases, ensure_ascii=False))
    case = cases[0]
    print(json.dumps({"bytes": args.out.stat().st_size, "keys": sorted(case["document"]),
                      "reading_sets": len(case["document"].get("reading_sets", []))}))


if __name__ == "__main__":
    main()
