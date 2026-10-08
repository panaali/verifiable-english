"""Write or check `ve/english_grammar/codes.json`, Lean's table of codes, classes and statuses.

    python tools/english_codes.py --write
    python tools/english_codes.py --check

The table is the `codes` and `statuses` fields of the `english.grammar` export (`VE.EnglishGrammar.Run.codeClasses`
and `statusCodes`), read from the built `ve_service`. The relay (`ve/backends/english_lean.py`) and the senses relay
read the file and hold no table of their own (spec 2.6, D9); `--check` fails when the file differs from the service.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TARGET = ROOT / "ve/english_grammar/codes.json"
ENVIRONMENT = {"language": "ve.core@0", "profile": "relational-fol@0", "spec_revision": "ve-v0-draft-2026-09-20",
               "vocabulary": {"sorts": {"service": {"description": "A sort."}},
                              "predicates": {"deployed": {"arguments": ["service"], "description": "A predicate.",
                                                          "verbalisation": "{0} is deployed"}},
                              "constants": {"legacy": {"sort": "service", "description": "A constant."}}}}


def from_lean() -> dict:
    from ve import Environment
    from ve.backends import relay
    from ve.english import EnglishVocabulary
    from ve.english_grammar import CODES_FORMAT, export
    env = Environment(ENVIRONMENT)
    row = relay.decide_once("english.grammar", {"id": "english.grammar", "environment": env.to_dict(),
                                                 "lexicon": export(EnglishVocabulary(env))})
    if row.get("status") != "ok" or type(row.get("result")) is not dict:
        raise SystemExit(f"english.grammar did not export a grammar: {row!r}")
    result = row["result"]
    return {"format": CODES_FORMAT, "codes": result["codes"], "statuses": result["statuses"],
            "unsentenced": result["unsentenced"]}


def render(table: dict) -> str:
    """One row per line: the format, then the codes with their classes, then the statuses with their codes."""
    rows = lambda key: ",\n".join("  " + json.dumps(row) for row in table[key])
    return (f'{{\n "format": {json.dumps(table["format"])},\n "codes": [\n{rows("codes")}\n ],\n'
            f' "statuses": [\n{rows("statuses")}\n ],\n "unsentenced": {json.dumps(table["unsentenced"])}\n}}\n')


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
        print(f"{TARGET.relative_to(ROOT)} differs from the english.grammar export; run --write")
        return 1
    print("PASS: the code table is the english.grammar export")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
