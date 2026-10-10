"""Write or check `ve/question/codes.json`, Lean's contract of the question reader.

    python tools/question_codes.py --write
    python tools/question_codes.py --check

The table is the `english.question` export (`{"id", "export": "codes"}`): `VE.Question.Run.codeClasses`, its
`statusCodes`, `statusFields`, `texts` (the lines its clients show as they are) and `questionVersion`, read from the
built `ve_service`. The question relay
(`ve/backends/english_lean.py`, `read_question`) reads the file and holds no table of its own; `--check` fails
when the file differs from the service (docs/spec/question-answering.md 4.1, 8).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TARGET = ROOT / "ve/question/codes.json"
FORMAT = "ve.question-codes@1"


def from_lean() -> dict:
    from ve.backends import relay
    row = relay.decide_once("english.question", {"id": "english.question", "export": "codes"})
    if row.get("status") != "ok" or type(row.get("result")) is not dict:
        raise SystemExit(f"english.question did not export its contract: {row!r}")
    result = row["result"]
    return {"format": FORMAT, "question_version": result["question_version"], "codes": result["codes"],
            "statuses": result["statuses"], "fields": result["fields"], "texts": result["texts"]}


def render(table: dict) -> str:
    """One row per line: the format and version, then the codes with their classes, then the statuses."""
    rows = lambda key: ",\n".join("  " + json.dumps(row) for row in table[key])
    return (f'{{\n "format": {json.dumps(table["format"])},\n'
            f' "question_version": {json.dumps(table["question_version"])},\n'
            f' "codes": [\n{rows("codes")}\n ],\n "statuses": [\n{rows("statuses")}\n ],\n'
            f' "fields": [\n{rows("fields")}\n ],\n "texts": [\n{rows("texts")}\n ]\n}}\n')


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    text = render(from_lean())
    if args.write:
        TARGET.write_text(text)
        return 0
    if TARGET.read_text() != text:
        print(f"{TARGET.relative_to(ROOT)} differs from the english.question export; run --write")
        return 1
    print("PASS: the question contract is the english.question export")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
