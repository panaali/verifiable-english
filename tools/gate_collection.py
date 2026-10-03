#!/usr/bin/env python3
"""Check or regenerate tools/gate-collection.json from the gate's own collection.

Run from the checkout after `lake build`:
    uv run python tools/gate_collection.py --check
    uv run python tools/gate_collection.py --write
Both collect with the gate's pytest arguments and its event plugin. Every
differing ID is reported with the first-parent commit after which the gate's
collection of its file has it as it is now (present or absent), found by
collecting that file at each first-parent commit; on main that is the merge
that changed it.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.gate import COLLECTION, PYTEST_ARGS  # noqa: E402

# Variables the collection inherits; pytest options and plugins never do.
INHERITED = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR")
# The gate's event plugin, loaded under a name no collected tree's own `tools` shadows.
PLUGIN = Path(__file__).with_name("gate_pytest.py")
PLUGIN_NAME = "ve_gate_collection_events"
# A past tree is collected without these on PATH, so a conftest from before
# VE_NATIVE_PREBUILT fails its build instead of building in a temporary tree.
TOOLCHAINS = ("lake", "lean", "elan", "cargo", "rustc", "rustup")
# Bounds the first-parent commits collected for a difference; older changes are not named.
SCANNED = 200


class CollectionError(RuntimeError):
    """The collection itself is incomplete, so no baseline may be taken from it."""


def _collection(root: Path, targets: list[str], *, prebuilt: bool,
                toolchains: bool = True) -> tuple[dict | None, subprocess.CompletedProcess]:
    """The plugin's events for the gate's collection of `targets` in `root`, and the run."""
    with tempfile.TemporaryDirectory(prefix="ve-gate-collection-") as directory:
        output = Path(directory) / "events.json"
        shutil.copyfile(PLUGIN, Path(directory) / f"{PLUGIN_NAME}.py")
        env = {name: os.environ[name] for name in INHERITED if name in os.environ}
        env.update(PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", VE_GATE_PYTEST_RESULT=str(output),
                   PYTHONPATH=os.pathsep.join((directory, str(root))), PYTHONDONTWRITEBYTECODE="1")
        if prebuilt:
            # Inside a running suite, whose session holds the shared build lock.
            env["VE_NATIVE_PREBUILT"] = "1"
        if not toolchains:
            env["PATH"] = os.pathsep.join(
                entry for entry in env.get("PATH", "").split(os.pathsep)
                if entry and not any((Path(entry) / tool).exists() for tool in TOOLCHAINS))
        args = list(PYTEST_ARGS)
        args[args.index("tools.gate_pytest")] = PLUGIN_NAME
        at = args.index("tests")
        args[at:at + 1] = ["--collect-only", *targets]
        run = subprocess.run([sys.executable, "-m", "pytest", *args], cwd=root, env=env,
                             text=True, capture_output=True)
        events = json.loads(output.read_text()) if output.exists() else None
    return events, run


def collect(root: Path = ROOT, *, prebuilt: bool = False) -> list[str]:
    """The IDs the gate's plugin records as collected, in collection order."""
    events, run = _collection(root, ["tests"], prebuilt=prebuilt)
    if events and events["collection_reports"]:
        # A module skipped or broken at collection drops its IDs without a trace.
        raise CollectionError("collection reports: " + json.dumps(events["collection_reports"])[:4000])
    if run.returncode not in (0, 5) or events is None:
        raise CollectionError(f"collection failed (exit {run.returncode}):\n"
                              f"{run.stdout[-4000:]}{run.stderr[-4000:]}")
    if len(events["collected"]) != len(set(events["collected"])):
        raise CollectionError("duplicate test ID in collection")
    return events["collected"]


def _file(nodeid: str) -> str:
    return nodeid.split("::", 1)[0]


def _collected_at(commit: str, files: set[str], tree: Path, index: Path,
                  root: Path) -> tuple[set[str], set[str]]:
    """(IDs collected from `files` at `commit`, those of `files` whose collection failed).

    A file the commit lacks has no IDs. The tree is checked out with its own
    index, so the repository's worktrees and index are never touched.
    """
    checkout = subprocess.run(["git", f"--work-tree={tree}", "read-tree", "--reset", "-u", commit],
                              cwd=root, env={**os.environ, "GIT_INDEX_FILE": str(index)},
                              capture_output=True)
    if checkout.returncode != 0:
        return set(), set(files)
    present = sorted(name for name in files if (tree / name).is_file())
    if not present:
        return set(), set()
    events, run = _collection(tree, present, prebuilt=True, toolchains=False)
    # A file skipped or broken at collection has unknown IDs, not none, and so
    # has every file when the session itself failed.
    failed = {_file(item["nodeid"]) for item in events["collection_reports"]} if events else set()
    if (events is None or not failed <= set(present)
            or run.returncode not in (0, 5) + ((1, 2) if failed else ())):
        return set(), set(present)
    return set(events["collected"]), failed


def describe(commit: str, root: Path = ROOT) -> str:
    found = subprocess.run(["git", "log", "-1", "--format=%h %s", commit],
                           cwd=root, text=True, capture_output=True)
    return found.stdout.strip() or commit[:8]


def introduced_by(added: list[str], removed: list[str], root: Path = ROOT) -> dict[str, str]:
    """For each ID, the newest first-parent commit after which the gate's collection
    of its file has it as it is now: present for `added`, absent for `removed`.

    Its file is collected at each first-parent commit from HEAD back, so a
    changed parameter, a renamed class, or IDs from data or a conftest are
    named by the commit that changed them, not by the one that added the test.
    """
    now = dict.fromkeys(added, True) | dict.fromkeys(removed, False)
    history = subprocess.run(["git", "rev-list", "--first-parent", f"--max-count={SCANNED + 1}",
                              "HEAD"], cwd=root, text=True, capture_output=True)
    commits = history.stdout.split() if history.returncode == 0 else []
    if not commits:
        return dict.fromkeys(now, "no commit (history git cannot read)")
    found: dict[str, str] = {}
    newer = "no commit (an uncommitted change)"
    with tempfile.TemporaryDirectory(prefix="ve-gate-history-") as directory:
        tree, index = Path(directory) / "tree", Path(directory) / "index"
        tree.mkdir()
        for position, commit in enumerate(commits):
            pending = [nodeid for nodeid in now if nodeid not in found]
            if not pending:
                break
            if position == SCANNED:
                found.update(dict.fromkeys(
                    pending, f"no commit in the newest {SCANNED} first-parent commits"))
                break
            collected, failed = _collected_at(commit, {_file(nodeid) for nodeid in pending},
                                              tree, index, root)
            for nodeid in pending:
                if _file(nodeid) in failed:
                    found[nodeid] = (f"no commit found ({describe(commit, root)} "
                                     "could not be collected)")
                elif (nodeid in collected) != now[nodeid]:
                    found[nodeid] = newer
            newer = describe(commit, root)
    shallow = subprocess.run(["git", "rev-parse", "--is-shallow-repository"],
                             cwd=root, text=True, capture_output=True).stdout.strip() != "false"
    for nodeid in now:
        if nodeid not in found:
            # As now at the root commit: it brought the ID in, or the ID was never
            # collected. A shallow clone's oldest commit is not the root.
            found[nodeid] = ("no commit in the shallow clone's history" if shallow else
                             newer if now[nodeid] else
                             "no commit (never collected on first-parent history)")
    return found


def attributed(added: list[str], removed: list[str],
               root: Path = ROOT) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """The added and the removed IDs, each grouped by the commit that changed them."""
    commits = introduced_by(added, removed, root)
    groups: tuple[dict[str, list[str]], ...] = (defaultdict(list), defaultdict(list))
    for group, ids in zip(groups, (added, removed)):
        for nodeid in ids:
            group[commits[nodeid]].append(nodeid)
    return dict(groups[0]), dict(groups[1])


def difference(expected: list[str], collected: list[str]) -> tuple[list[str], list[str]]:
    """(collected but not pinned, pinned but not collected)."""
    return sorted(set(collected) - set(expected)), sorted(set(expected) - set(collected))


def report(added: list[str], removed: list[str], root: Path = ROOT, *, sample: int | None = 5) -> str:
    lines = [f"{COLLECTION.relative_to(ROOT)} differs from the gate's collection: "
             f"{len(added)} collected but not pinned, {len(removed)} pinned but not collected."]
    for title, groups in zip(("Collected but not pinned", "Pinned but not collected"),
                             attributed(added, removed, root)):
        for commit, group in groups.items():
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
