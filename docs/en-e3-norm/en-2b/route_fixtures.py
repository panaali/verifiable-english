"""Write the EN-2 route fixtures (docs/spec/en-e3-norm.md section 8: R-f1..R-f24, R-stale) into
`tests/data/route-cases.jsonl` as `["english.statement", case]` lines, replacing any earlier ones.

    uv run python docs/en-e3-norm/en-2b/route_fixtures.py --write

The cases are `tests/test_english_statement_blocks.py`'s `route_fixtures()`; its
`test_the_route_fixtures_are_recorded` fails when the file differs from them.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tests.test_english_statement_blocks import route_fixtures  # noqa: E402

TARGET = ROOT / "tests/data/route-cases.jsonl"


def main(argv: list[str]) -> int:
    if argv != ["--write"]:
        print(__doc__)
        return 2
    kept = [line for line in TARGET.read_text().splitlines() if json.loads(line)[0] != "english.statement"]
    lines = [json.dumps(["english.statement", case], separators=(",", ":")) for _, case, _ in route_fixtures()]
    TARGET.write_text("\n".join(kept + lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
