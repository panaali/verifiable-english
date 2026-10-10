"""Plant each seeded bug of mutants.json, run its test, restore the file, and print whether the test failed.

    uv run python docs/devtime/devtime-1/seed_bugs.py            # exits 1 when any bug survives its test

Each entry names the file, the exact text replaced (`old`, which must occur once) and its replacement (`new`),
and the pytest node that must fail. The file is restored from its original bytes whatever happens. The
`observed` member of each entry is the outcome of the recorded run; this script only prints, it writes no file.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools import nested_pytest  # noqa: E402
MUTANTS = Path(__file__).with_name("mutants.json")


def run(entry: dict) -> dict:
    path = ROOT / entry["file"]
    original = path.read_bytes()
    text = original.decode("utf-8")
    assert text.count(entry["old"]) == 1, f"{entry['id']}: `old` must occur exactly once in {entry['file']}"
    try:
        path.write_text(text.replace(entry["old"], entry["new"]), encoding="utf-8")
        done = subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", entry["test"]]), cwd=ROOT,
                              env=nested_pytest.environment(os.environ), capture_output=True, text=True)
    finally:
        path.write_bytes(original)
    tail = [line for line in done.stdout.splitlines() if line.strip()][-1:]
    return {"exit": done.returncode, "summary": tail[0] if tail else ""}


def main() -> int:
    data = json.loads(MUTANTS.read_text(encoding="utf-8"))
    survived = []
    for entry in data["mutants"]:
        observed = run(entry)
        killed = observed["exit"] == 1
        print(f"{'KILLED' if killed else 'SURVIVED'} {entry['id']}: {entry['test']} -> {observed['summary']}")
        if not killed:
            survived.append(entry["id"])
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())
