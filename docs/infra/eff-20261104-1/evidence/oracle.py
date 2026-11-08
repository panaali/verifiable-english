#!/usr/bin/env python3
"""eff-20261104-1 F2: `lean_code` against Lean's own parser over every Lean source of this tree, writing
oracle-result.json. Every token the parser reads must stand at its place in `lean_code`'s text.

    uv run python docs/infra/eff-20261104-1/evidence/oracle.py

The parser runs with the environment of `import Lean`, with no module of this tree loaded and nothing elaborated, so
syntax a module declares is a parse error there and that command's tokens are not compared (`files_with_parse_errors`).
tests/test_trust_mutants.py runs the same comparison, both ways, on pieces with no such error."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(REPO / "tools"), str(REPO / "tests")]
import trust_mutants as tm  # noqa: E402
from test_trust_mutants import LEAN_TOKENS, PATH  # noqa: E402


def main() -> None:
    files = sorted(p for p in (REPO / "lean").rglob("*.lean") if ".lake" not in p.parts)
    answers, unsure = [], 0
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp, "Tokens.lean")
        script.write_text(LEAN_TOKENS)
        for i in range(0, len(files), 100):
            done = subprocess.run(["lean", "--run", str(script), *map(str, files[i:i + 100])], capture_output=True,
                                  text=True, cwd=REPO / "lean", env={**os.environ, **PATH}, check=True)
            answers += [json.loads(line) for line in done.stdout.splitlines()]
    assert len(answers) == len(files)
    tokens, lost = 0, []
    for path, answer in zip(files, answers):
        raw = path.read_bytes()
        text = raw.decode()
        code = tm.lean_code(text)
        try:
            tm.lean_scan(text, 0, [])
        except tm.LeanUnsure:
            unsure += 1
        offsets = {}
        at = 0
        for char_at, char in enumerate(text):
            offsets[at] = char_at
            at += len(char.encode())
        offsets[at] = len(text)
        for position, token in answer["tokens"]:
            tokens += 1
            start = offsets[position]
            if code[start:start + len(token)] != token:
                lost.append([path.relative_to(REPO).as_posix(), position, token])
    Path(__file__).with_name("oracle-result.json").write_text(json.dumps({
        "files": len(files), "tokens": tokens, "tokens_lost": lost, "files_kept_from_an_unsure_point": unsure,
        "files_with_parse_errors": sum(a["errors"] for a in answers)}, indent=1) + "\n")


if __name__ == "__main__":
    main()
