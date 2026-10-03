#!/usr/bin/env python3
"""Check or regenerate tools/gate-collection.json from the gate's own collection.

Run from the checkout after `lake build`:
    uv run python tools/gate_collection.py --check
    uv run python tools/gate_collection.py --write
Both collect with the gate's pytest arguments and its event plugin. Every
differing ID is reported with the first-parent commit that last changed its
test's name in its file, which on main is the merge that brought it in.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.gate import COLLECTION, PYTEST_ARGS  # noqa: E402

# Variables the collection inherits; pytest options and plugins never do.
INHERITED = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR")
# Bounds the git lookups for a large difference; the rest are named by count.
ATTRIBUTED = 200


class CollectionError(RuntimeError):
    """The collection itself is incomplete, so no baseline may be taken from it."""


def collect(root: Path = ROOT, *, prebuilt: bool = False) -> list[str]:
    """The IDs the gate's plugin records as collected, in collection order."""
    with tempfile.TemporaryDirectory(prefix="ve-gate-collection-") as directory:
        output = Path(directory) / "events.json"
        env = {name: os.environ[name] for name in INHERITED if name in os.environ}
        env.update(PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", VE_GATE_PYTEST_RESULT=str(output),
                   PYTHONPATH=str(ROOT))
        if prebuilt:
            # Inside a running suite, whose session holds the shared build lock.
            env["VE_NATIVE_PREBUILT"] = "1"
        args = list(PYTEST_ARGS)
        args.insert(args.index("tests"), "--collect-only")
        run = subprocess.run([sys.executable, "-m", "pytest", *args], cwd=root, env=env,
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


def introduced_by(nodeid: str, root: Path = ROOT) -> str:
    """The newest first-parent commit changing how often the test's name occurs in its file."""
    path, *_, test = nodeid.split("::")
    name = test.split("[", 1)[0]
    found = subprocess.run(["git", "log", "--first-parent", "-1", "-S", name,
                            "--format=%h %s", "HEAD", "--", path],
                           cwd=root, text=True, capture_output=True)
    if found.returncode == 0 and found.stdout.strip():
        return found.stdout.strip()
    return "no commit (an uncommitted change, or history git cannot read)"


def attributed(ids: list[str], root: Path = ROOT) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    commits: dict[tuple[str, str], str] = {}
    for nodeid in ids:
        path, *_, test = nodeid.split("::")
        key = (path, test.split("[", 1)[0])
        if key not in commits:
            commits[key] = introduced_by(nodeid, root) if len(commits) < ATTRIBUTED else "not looked up"
        groups[commits[key]].append(nodeid)
    return dict(groups)


def difference(expected: list[str], collected: list[str]) -> tuple[list[str], list[str]]:
    """(collected but not pinned, pinned but not collected)."""
    return sorted(set(collected) - set(expected)), sorted(set(expected) - set(collected))


def report(added: list[str], removed: list[str], root: Path = ROOT, *, sample: int | None = 5) -> str:
    lines = [f"{COLLECTION.relative_to(ROOT)} differs from the gate's collection: "
             f"{len(added)} collected but not pinned, {len(removed)} pinned but not collected."]
    for title, ids in (("Collected but not pinned", added), ("Pinned but not collected", removed)):
        for commit, group in attributed(ids, root).items():
            lines.append(f"{title}, from {commit}: {len(group)}")
            shown = group if sample is None else group[:sample]
            lines.extend(f"  {nodeid}" for nodeid in shown)
            if len(group) > len(shown):
                lines.append(f"  ... and {len(group) - len(shown)} more")
    lines.append("The merge or commit named above changed the tests without the baseline. Regenerate it "
                 "with `uv run python tools/gate_collection.py --write` after `lake build`, check every "
                 "removed ID is meant to go, and commit the file with that change.")
    return "\n".join(lines)


def baseline_text(ids: list[str]) -> str:
    return json.dumps(sorted(ids), indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="fail if the baseline differs")
    mode.add_argument("--write", action="store_true", help="rewrite the baseline")
    parser.add_argument("--prebuilt", action="store_true",
                        help="skip the suite's native build (run `lake build` first)")
    args = parser.parse_args()
    try:
        collected = collect(prebuilt=args.prebuilt)
    except CollectionError as exc:
        print(f"gate collection: {exc}", file=sys.stderr)
        return 2
    expected = json.loads(COLLECTION.read_text())
    added, removed = difference(expected, collected)
    if added or removed:
        print(report(added, removed, sample=None if args.write else 5),
              file=sys.stdout if args.write else sys.stderr)
    if args.write:
        COLLECTION.write_text(baseline_text(collected))
        print(f"wrote {len(collected)} IDs to {COLLECTION.relative_to(ROOT)}")
        return 0
    return 1 if added or removed else 0


if __name__ == "__main__":
    raise SystemExit(main())
