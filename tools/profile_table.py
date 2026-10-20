"""Write `ve/profile_table.json` from its Lean owner, `VE.Compose.profileTable` (AR-10)."""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "ve/profile_table.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = subprocess.run(
        ["lake", "env", "lean", "--run", "VE/Compose/ProfilesMain.lean"],
        cwd=ROOT / "lean", capture_output=True, text=True, check=False,
    )
    if result.returncode:
        sys.stderr.write(result.stderr)
        return result.returncode
    expected = result.stdout.rstrip("\n") + "\n"
    if args.write:
        TARGET.write_text(expected)
        return 0
    if not TARGET.exists() or TARGET.read_text() != expected:
        sys.stderr.write("ve/profile_table.json is stale\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
