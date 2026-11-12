"""Write `usecases/webapp-commands/environment.json` from its Lean owner, `VE.Commands.Examples.E_web` (CI-8, (iv))."""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "usecases/webapp-commands/environment.json"
PRINTER = "VE/Commands/WebEnvMain.lean"


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = subprocess.run(
        ["lake", "env", "lean", "--run", PRINTER],
        cwd=ROOT / "lean", capture_output=True, text=True, check=False,
    )
    if result.returncode:
        sys.stderr.write(result.stderr)
        return result.returncode or 1
    expected = result.stdout.rstrip("\n") + "\n"
    if args.write:
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_text(expected)
        return 0
    if not TARGET.exists() or TARGET.read_text() != expected:
        sys.stderr.write("usecases/webapp-commands/environment.json is stale: "
                         "run uv run python tools/regen_generated.py --write\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
