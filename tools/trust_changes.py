#!/usr/bin/env python3
"""The trust report's changed files (architecture decision D2, AR-2): each Lean file changed since a base
commit, with the lines it holds in each trusted class.

    python3 tools/trust_changes.py --since BASE          # a table by class
    python3 tools/trust_changes.py --since BASE --json   # the same as JSON

The hash freeze covers only the files with K declarations and the `ve.core@0.1` decoders
(`lean/VE/Route/frozen.py`), and `lean/statements.txt` cannot see an edit to a definition's body that leaves
every theorem statement as it was. So the batch gate (`tools/trust_map.py --since BASE` beside this report)
lists every `.lean` file under `lean/` whose bytes differ from BASE's: added, edited or deleted. Each is shown
with its K, S, D[V] and G[V] lines as `tools/trust_map.py` measures the current tree, and is listed under every
one of the classes D[V] and G[V] it holds lines in. A deleted file has no current lines; it is listed as deleted
under the classes recorded for it at BASE.

Line counts cannot see trusted code written onto fewer, longer lines: three lines added and three collapsed into
one 290-character line measure +0 (AR-2 review F3). So each changed file also carries the width of its widest
trusted line (K, S or untied [V], as `tools/trust_map.py` decides) now and at BASE (BASE's tree classified as
BASE's side table classifies it), and `widened` lists the changed files whose widest trusted line is wider than
every trusted line the file had at BASE. A long untrusted line at BASE, such as a comment, hides nothing (review
F8). A new file has no base width and is not listed there; all its lines are new in its row.

It reports and never fails on a change. It exits 1 when git cannot read BASE or the measurement of the tree or of
BASE fails (a stale `lean/declarations.txt` included), so a report is never made from a classification that did
not validate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lean_statements  # noqa: E402
import trust_map  # noqa: E402

CLASSES = ("K", "S", "D[V]", "G[V]")
LISTED = ("D[V]", "G[V]")


def blob_id(data: bytes) -> str:
    """Git's object id of a blob with these bytes (no attribute or filter applied)."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def base_blobs(rev: str, root: Path = ROOT) -> dict[str, str]:
    """Each `.lean` file under `lean/` at commit `rev` (its path from `lean/`) with its blob id."""
    done = subprocess.run(["git", "-C", str(root), "ls-tree", "-r", "-z", "--full-tree", rev, "--", "lean"],
                          capture_output=True)
    if done.returncode:
        raise RuntimeError(f"git ls-tree {rev}: {done.stderr.decode(errors='replace').strip()}")
    blobs = {}
    for row in filter(None, done.stdout.split(b"\0")):
        meta, path = row.decode().split("\t", 1)
        key = path.removeprefix("lean/")
        if meta.split()[1] == "blob" and key.endswith(".lean") and ".lake" not in Path(key).parts:
            blobs[key] = meta.split()[2]
    return blobs


def changed(rev: str, root: Path = ROOT) -> tuple[list[str], list[str], dict[str, str]]:
    """The Lean files of the tree whose bytes differ from `rev`'s or that `rev` lacks, and those `rev` has that
    the tree lacks, each sorted; and `rev`'s blob ids."""
    before = base_blobs(rev, root)
    now = {trust_map.module_key(path, root): blob_id(path.read_bytes()) for path in lean_statements.sources(root)}
    return (sorted(key for key, blob in now.items() if before.get(key) != blob),
            sorted(before.keys() - now.keys()), before)


def base_widths(rev: str, edited: list[str], blobs: dict[str, str], root: Path = ROOT) -> dict[str, int | None]:
    """The widest trusted line of each edited file at the base `rev` (`trusted_widths` over that commit's tree,
    classified there as `tools/trust_map.py` classifies it), None for a file the base lacks. A long untrusted
    line at the base, such as a comment, does not widen the base (AR-2 review F8)."""
    kept = [key for key in edited if key in blobs]
    widths: dict[str, int] = {}
    if kept:
        with tempfile.TemporaryDirectory() as scratch:
            tree = Path(scratch)
            problem = trust_map.extract_rev(rev, tree, root)
            if problem:
                raise RuntimeError(problem)
            decls, _, problems = trust_map.walk(tree, *trust_map.rev_paths(tree))
            if problems:
                raise RuntimeError(f"the trust classification of {rev} fails:\n" + "\n".join(problems))
            widths = trusted_widths(decls, kept, tree)
    return {key: widths.get(key) for key in edited}


def trusted_widths(decls: list, edited: list[str], root: Path = ROOT) -> dict[str, int]:
    """The widest trusted line of each edited file: the lines of its declarations `tools/trust_map.py` counts
    as trusted (`walk`'s `trusted`), 0 for a file with none."""
    lines = {key: (root / "lean" / key).read_text().split("\n") for key in edited}
    out = dict.fromkeys(edited, 0)
    for d in decls:
        if d.module in lines and d.trusted:
            out[d.module] = max([out[d.module], *map(len, lines[d.module][d.decl.start - 1:d.decl.end])])
    return out


def base_classes(rev: str, root: Path = ROOT) -> dict[str, dict]:
    """The base trust table, so deleted D[V] and G[V] files retain their old class in the report."""
    done = subprocess.run(["git", "-C", str(root), "show", f"{rev}:tools/trust-classes.json"],
                          capture_output=True, text=True)
    if done.returncode:
        raise RuntimeError(f"git show {rev}:tools/trust-classes.json: {done.stderr.strip()}")
    try:
        return json.loads(done.stdout)["modules"]
    except (ValueError, KeyError, TypeError) as error:
        raise RuntimeError(f"{rev}:tools/trust-classes.json is malformed: {error}") from error


def report(files: dict[str, dict[str, int]], edited: list[str], deleted: list[str],
           old_classes: dict[str, dict], widths: dict[str, int], old_widths: dict[str, int | None]) -> dict:
    """The changed files with their lines per trusted class and their widths, the changed files holding D[V]
    or G[V] lines, by class, and the changed files whose trusted lines grew wider than they were at the base."""
    rows = {key: {**{cls: files[key][cls] for cls in CLASSES},
                  "trusted_width": widths[key], "base_width": old_widths[key]} for key in edited}
    return {"changed": rows, "deleted": deleted,
            "by_class": {cls: sorted([key for key in edited if rows[key][cls]] +
                                     [key for key in deleted if old_classes.get(key, {}).get(cls)])
                         for cls in LISTED},
            "widened": [key for key in edited if old_widths[key] is not None and widths[key] > old_widths[key]]}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--since", metavar="BASE", required=True, help="the batch's merge base")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        edited, deleted, blobs = changed(args.since, root)
        old_classes = base_classes(args.since, root)
        old_widths = base_widths(args.since, edited, blobs, root)
    except RuntimeError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    paths = (root / trust_map.TABLE.relative_to(ROOT), root / trust_map.STATEMENTS.relative_to(ROOT))
    files, problems = trust_map.measure(root, *paths)
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        print("FAIL: the changed files are not reported while the trust classification fails", file=sys.stderr)
        return 1
    decls, _, _ = trust_map.walk(root, *paths)
    out = report(files, edited, deleted, old_classes, trusted_widths(decls, edited, root), old_widths)
    if args.json:
        print(json.dumps(out, indent=1))
        return 0
    print(f"{len(edited)} Lean files changed and {len(deleted)} deleted since {args.since}")
    for cls in LISTED:
        print(f"{cls}: {len(out['by_class'][cls])} changed files")
        for key in out["by_class"][cls]:
            if key in out["changed"]:
                print(f"  {key}: " + ", ".join(f"{c} {out['changed'][key][c]}" for c in CLASSES
                                               if out["changed"][key][c]))
            else:
                print(f"  {key}: deleted ({cls} in base)")
    for key in deleted:
        print(f"deleted: {key}")
    print(f"widened: {len(out['widened'])} changed files hold a trusted line wider than any trusted line they had "
          "at base")
    for key in out["widened"]:
        row = out["changed"][key]
        print(f"  {key}: trusted line of {row['trusted_width']} characters, base at most {row['base_width']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
