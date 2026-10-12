"""Generate service mode roots from Lean's proved runMode equations.

The selector reads the generated file without starting Lean. An absent or stale
file disables per-mode narrowing; the ordinary service-wide rule then applies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

from layer_policy import ROOT

OUTPUT = ROOT / "tools/lean-mode-deps.json"
SOURCES = ("tools/lean_mode_deps.lean", "lean/VE/Service/Protocol.lean")


def digests() -> dict[str, str]:
    return {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in SOURCES}


def valid(data: object) -> bool:
    if not isinstance(data, dict) or data.get("sources") != digests():
        return False
    modes = data.get("modes")
    return (isinstance(modes, dict) and bool(modes)
            and all(isinstance(mode, str) and mode and isinstance(roots, list) and roots
                    and all(isinstance(root, str) and root.startswith("VE.")
                            and (ROOT / "lean" / (root.replace(".", "/") + ".lean")).is_file()
                            for root in roots)
                    for mode, roots in modes.items()))


def load() -> dict[str, list[str]] | None:
    try:
        data = json.loads(OUTPUT.read_text())
    except (OSError, ValueError):
        return None
    return data["modes"] if valid(data) else None


def generate() -> dict:
    env = dict(os.environ)
    env["PATH"] = str(Path.home() / ".elan/bin") + os.pathsep + env.get("PATH", "")
    result = subprocess.run(("lake", "env", "lean", "../tools/lean_mode_deps.lean"), cwd=ROOT / "lean",
                            env=env, text=True, capture_output=True, check=True)
    modes = json.loads(result.stdout)
    data = {"sources": digests(), "modes": modes}
    if not valid(data):
        raise ValueError("Lean mode roots are incomplete or malformed")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = generate()
    content = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(content)
        return 0
    if not OUTPUT.exists() or OUTPUT.read_text() != content:
        print(f"stale: {OUTPUT.relative_to(ROOT)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
