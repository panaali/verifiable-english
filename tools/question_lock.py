"""Generate or verify the Q1 Lean source lock list."""

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUESTION = ROOT / "lean/VE/Question"
LOCK = ROOT / "ve/question/LOCK.json"
CODES = ROOT / "ve/question/codes.json"


def expected() -> dict:
    # The version as Lean's service exports it (`ve/question/codes.json`, tools/question_codes.py), not read from
    # the Lean source text.
    version = json.loads(CODES.read_text())["question_version"]
    prefix, _, number = version.partition("@")
    if prefix != "question" or not number.isdigit():
        raise SystemExit(f"{CODES.relative_to(ROOT)}: question_version {version!r} is not question@N")
    files = {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(QUESTION.glob("*.lean"))
    }
    return {"format": "ve.question-lock@1", "question_version": int(number), "files": files}


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
        print(f"PASS: {LOCK.relative_to(ROOT)} covers every Question Lean file")


if __name__ == "__main__":
    main()
