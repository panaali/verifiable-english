"""Write the EN-2 route fixtures (docs/spec/en-e3-norm.md section 8: R-f1..R-f24, R-stale) into
`tests/data/route-cases.jsonl` as `["english.statement", case]` lines, replacing any earlier ones.

    uv run python docs/en-e3-norm/en-2b/route_fixtures.py --write
    uv run python docs/en-e3-norm/en-2b/route_fixtures.py --check   # exit 1 if --write would change the file

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
    if argv not in (["--write"], ["--check"]):
        print(__doc__)
        return 2
    before = TARGET.read_text()
    kept = [line for line in before.splitlines() if json.loads(line)[0] != "english.statement"]
    lines = [json.dumps(["english.statement", case], separators=(",", ":")) for _, case, _ in route_fixtures()]
    text = "\n".join(kept + lines) + "\n"
    if argv == ["--check"]:
        if text != before:
            print(f"{TARGET.relative_to(ROOT)} is stale: run {Path(__file__).relative_to(ROOT)} --write", file=sys.stderr)
            return 1
        return 0
    TARGET.write_text(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
