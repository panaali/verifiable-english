"""Convert the `ask` fixtures to the format without run-time values, and show the conversion is mechanical.

    uv run python docs/infra/arch-20261105-2/convert.py --write                  # convert tests/fixtures/ask/ in place
    uv run python docs/infra/arch-20261105-2/convert.py --base main --out FILE   # the evidence (below)

Evidence tooling for arch-20261105-2, not a test and not a re-record: `--write` removes the top-level `seconds` and
`result.identities.actions_version` of each fixture and dumps it in `tools/ask_fixtures.py`'s format (it first checks
that the format reproduces the committed bytes, so nothing else can move). `--base REV` compares the parsed JSON of
every fixture at REV with the working tree's and saves, per file, the paths that differ: the conversion is mechanical
when each file differs in exactly those two keys (a refusal fixture, which has neither, in none).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "tests/fixtures/ask"
sys.path.insert(0, str(ROOT / "docs/infra/arch-20261105-2"))
from measure import paths  # noqa: E402  (the same parsed comparison as the "why now" figures)


def dump(value) -> str:
    """`tools/ask_fixtures.py`'s `_dump`, repeated here so that this script runs on any revision."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def write() -> int:
    for path in sorted(FIXTURES.glob("*.json")):
        text = path.read_text()
        entry = json.loads(text)
        if dump(entry) != text:
            raise SystemExit(f"{path.name}: the dump does not reproduce the committed bytes")
        entry.pop("seconds", None)
        if isinstance(entry.get("result"), dict):
            entry["result"]["identities"].pop("actions_version", None)
        path.write_text(dump(entry))
    return 0


def evidence(base: str, out: Path) -> int:
    rows, expected = {}, {"/seconds", "/result/identities/actions_version"}
    names = subprocess.run(["git", "ls-tree", "--name-only", f"{base}:tests/fixtures/ask"], cwd=ROOT, check=True,
                           capture_output=True, text=True).stdout.split()
    for name in names:
        before = json.loads(subprocess.run(["git", "show", f"{base}:tests/fixtures/ask/{name}"], cwd=ROOT,
                                           check=True, capture_output=True, text=True).stdout)
        after = json.loads((FIXTURES / name).read_text())
        rows[name] = paths(before, after)
    mechanical = all(set(found) <= expected and len(found) == len(set(found)) for found in rows.values())
    saved = {"base": subprocess.run(["git", "rev-parse", base], cwd=ROOT, check=True, capture_output=True,
                                    text=True).stdout.strip(),
             "files": len(rows), "same_names": sorted(names) == sorted(p.name for p in FIXTURES.glob("*.json")),
             "removed": {key: sum(key in found for found in rows.values()) for key in sorted(expected)},
             "mechanical": mechanical, "per_file": rows}
    out.write_text(json.dumps(saved, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in saved.items() if k != "per_file"}))
    return 0 if mechanical and saved["same_names"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--base")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.write:
        return write()
    return evidence(args.base, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
