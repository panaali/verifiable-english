"""A stand-in for an AI reader program, for stop 12's recorded example (tour/data/reader-two-meanings.txt): it answers
`ve read`'s meaning check with the replies a real AI reader gave to the same input, recorded in
tour/data/reader-two-meanings-replies.json, so the example runs again without sending anything anywhere.

`ve read` runs its reader program twice per text and compares the two replies; this program hands back the first
recorded reply on the first run and the second on the second (it counts runs per `ve read` process, in a temporary
file it removes after the last one). Any other input is refused (exit code 1, so `ve read` treats the reader as
failed): it only replays what was recorded.

Run by `ve read --reader-yes --reader-command "python3 tour/data/recorded_reader.py tour/data/reader-two-meanings-replies.json"`.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile


def main(argv: list) -> int:
    recorded = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    text = sys.stdin.buffer.read()
    if hashlib.sha256(text).hexdigest() != recorded["input_sha256"]:
        print("recorded_reader.py: this is not the input that was recorded; nothing to replay", file=sys.stderr)
        return 1
    count = Path(tempfile.gettempdir()) / f"ve-recorded-reader-{os.getppid()}"
    run = int(count.read_text()) if count.exists() else 0
    if run >= len(recorded["outputs"]):
        print("recorded_reader.py: no recorded reply left", file=sys.stderr)
        return 1
    if run + 1 == len(recorded["outputs"]):
        count.unlink(missing_ok=True)
    else:
        count.write_text(str(run + 1))
    sys.stdout.write(recorded["outputs"][run])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
