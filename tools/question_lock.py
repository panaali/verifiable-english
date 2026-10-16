"""Generate or verify the Q1 lock: the question version the relay is built for.

It hashes no Lean module (architecture decision D2, AR-2): each Question module's compiled source hash is in
`lean/declarations.txt`, its statements are in `lean/statements.txt`, and a Question module holding a K declaration
would be in the frozen list `lean/VE/Route/frozen-sources.sha256`.
"""

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "ve/question/LOCK.json"
CODES = ROOT / "ve/question/codes.json"


def expected() -> dict:
    # The version as Lean's service exports it (`ve/question/codes.json`, tools/question_codes.py), not read from
    # the Lean source text.
    version = json.loads(CODES.read_text())["question_version"]
    prefix, _, number = version.partition("@")
    if prefix != "question" or not number.isdigit():
        raise SystemExit(f"{CODES.relative_to(ROOT)}: question_version {version!r} is not question@N")
    return {"format": "ve.question-lock@2", "question_version": int(number)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    blob = json.dumps(expected(), indent=2, ensure_ascii=False) + "\n"
    if args.write:
        LOCK.parent.mkdir(parents=True, exist_ok=True)
        LOCK.write_text(blob)
        print(f"wrote {LOCK.relative_to(ROOT)}")
    elif not LOCK.exists() or LOCK.read_text() != blob:
        raise SystemExit("ve/question/LOCK.json is stale; run tools/question_lock.py --write")
    else:
        print(f"PASS: {LOCK.relative_to(ROOT)} records the service's question version")


if __name__ == "__main__":
    main()
