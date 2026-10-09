"""Generate or verify the Q1 Lean source lock list."""

import argparse
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
QUESTION = ROOT / "lean/VE/Question"
LOCK = ROOT / "ve/question/LOCK.json"


def expected() -> dict:
    text = (QUESTION / "Texts.lean").read_text()
    match = re.search(r"^def question_version : Nat := (\d+)$", text, re.M)
    if not match:
        raise SystemExit("question_version is missing from Texts.lean")
    files = {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(QUESTION.glob("*.lean"))
    }
    return {"format": "ve.question-lock@1", "question_version": int(match.group(1)), "files": files}


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
