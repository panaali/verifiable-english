#!/usr/bin/env python3
"""Check or regenerate tools/gate-collection.json from the gate's own collection.

Run from the checkout after `(cd lean && lake build)`:
    uv run python tools/gate_collection.py --check
    uv run python tools/gate_collection.py --write
Both collect with the gate's pytest arguments and its event plugin, and list
every ID collected but not pinned and pinned but not collected.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.gate import COLLECTION, collection_command, collection_difference  # noqa: E402
from tools.pytest_run import pytest_environment  # noqa: E402

# Variables the collection inherits; pytest options and plugins never do.
INHERITED = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR")


class CollectionError(RuntimeError):
    """The collection itself is incomplete, so no baseline may be taken from it."""


def collect(root: Path = ROOT, *, prebuilt: bool = False) -> list[str]:
    """The IDs the gate's plugin records as collected, in collection order."""
    with tempfile.TemporaryDirectory(prefix="ve-gate-collection-") as directory:
        output = Path(directory) / "events.json"
        env = {name: os.environ[name] for name in INHERITED if name in os.environ}
        # Bytecode is checked only against its source's size and whole-second
        # mtime, so a same-size edit within the second would load the earlier
        # source. An empty cache, never the tree's __pycache__, compiles it fresh.
        env.update(VE_GATE_PYTEST_RESULT=str(output),
                   PYTHONPATH=str(ROOT), PYTHONPYCACHEPREFIX=str(Path(directory) / "pycache"))
        if prebuilt:
            # Inside a running suite, whose session holds the shared build lock.
            env["VE_NATIVE_PREBUILT"] = "1"
        run = subprocess.run(collection_command([sys.executable]), cwd=root, env=pytest_environment(env),
                             text=True, capture_output=True)
        events = json.loads(output.read_text()) if output.exists() else None
    if events and events["collection_reports"]:
        # A module skipped or broken at collection drops its IDs without a trace.
        raise CollectionError("collection reports: " + json.dumps(events["collection_reports"])[:4000])
    if run.returncode not in (0, 5) or events is None:
        raise CollectionError(f"collection failed (exit {run.returncode}):\n"
                              f"{run.stdout[-4000:]}{run.stderr[-4000:]}")
    if len(events["collected"]) != len(set(events["collected"])):
        raise CollectionError("duplicate test ID in collection")
    return events["collected"]


def difference(expected: list[str], collected: list[str]) -> tuple[list[str], list[str]]:
    """(collected but not pinned, pinned but not collected)."""
    return sorted(set(collected) - set(expected)), sorted(set(expected) - set(collected))


def baseline_text(ids: list[str]) -> str:
    return json.dumps(sorted(ids), indent=2) + "\n"


def write(*, prebuilt: bool, check: bool = False) -> int:
    """Rewrite the baseline from the collection (or, with `check`, only compare them)."""
    try:
        collected = collect(prebuilt=prebuilt)
    except CollectionError as exc:
        print(f"gate collection: {exc}", file=sys.stderr)
        return 2
    expected = json.loads(COLLECTION.read_text())
    added, removed = difference(expected, collected)
    if added or removed:
        print(collection_difference(added, removed), file=sys.stderr if check else sys.stdout)
    if not check:
        COLLECTION.write_text(baseline_text(collected))
        print(f"wrote {len(collected)} IDs to {COLLECTION.relative_to(ROOT)}")
        return 0
    return 1 if added or removed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="fail if the baseline differs")
    mode.add_argument("--write", action="store_true", help="rewrite the baseline")
    parser.add_argument("--prebuilt", action="store_true",
                        help="skip the suite's native build (run `(cd lean && lake build)` first)")
    args = parser.parse_args()
    return write(prebuilt=args.prebuilt, check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
