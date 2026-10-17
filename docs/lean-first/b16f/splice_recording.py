"""Re-record named cases of a complete nine-corpus recording, and splice them in by key.

    python docs/lean-first/b16e/splice_recording.py pilots ROOT OUT NAME...            # pilot cases on ROOT
    python docs/lean-first/b16e/splice_recording.py documents ROOT CORPUS OUT NAME...  # document corpus cases
    python docs/lean-first/b16e/splice_recording.py splice FULL PART OUT                # replace FULL's rows PART holds

A row that a loaded machine's wall-clock limits decided (the Rust checker's 5 s, a pilot's 600 s) is re-recorded on
both sides with one worker and the same wall-clock guards (`VE_RUST_TIMEOUT`, a guard and not a work limit); every
other row of the complete recording is kept. Each spliced row must name the same corpus, authority, case, operation
and source digest as the row it replaces.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

from tools import lean_first_diff as diff

FIELDS = ("corpus", "authority", "case", "op")


def key(row):
    return tuple(row[name] for name in FIELDS)


def pilots(root: Path, out: Path, names: list[str]) -> None:
    documents = [d for d in diff.pilot_documents(diff.ROOT) if d[0] in names]
    assert sorted(d[0] for d in documents) == sorted(names), "every named pilot case exists"
    with tempfile.TemporaryDirectory(prefix="b16f-pilots-") as scratch, \
            patch.object(diff, "pilot_documents", lambda _root: documents):
        rows = list(diff.pilot_records(root, Path(scratch), 1))
    with out.open("w") as output:
        for row in rows:
            output.write(json.dumps({"corpus": "pilots", **row}, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False) + "\n")


CHILD = """
import json, os, sys, tempfile
from pathlib import Path
from tools.lean_first_diff import _rights_case, digest
corpus, out, names = Path(sys.argv[1]), Path(sys.argv[2]), set(sys.argv[3:])
os.environ.pop("VE_AUTHORITY", None)
source = digest(corpus)
with tempfile.TemporaryDirectory(prefix="b16f-documents-") as scratch, out.open("w") as output:
    for entry in json.loads(corpus.read_text()):
        if entry["case"] in names:
            names.discard(entry["case"])
            for row in _rights_case((scratch, source, entry)):
                output.write(json.dumps({"corpus": "document", **row}, sort_keys=True, separators=(",", ":"),
                                        ensure_ascii=False) + "\\n")
assert not names, names
"""


def documents(root: Path, corpus: Path, out: Path, names: list[str]) -> None:
    """The named cases of the document corpus file `corpus` (its digest kept), recorded in the checkout `root`."""
    import os
    import subprocess
    import sys
    subprocess.run([sys.executable, "-c", CHILD, str(corpus.resolve()), str(out.resolve()), *names],
                   cwd=root, env={**os.environ, "PYTHONPATH": str(root)}, check=True)


def splice(full: Path, part: Path, out: Path) -> None:
    replacement = {key(row): row for line in part.open() if (row := json.loads(line))}
    found = set()
    with full.open() as source, out.open("w") as output:
        for line in source:
            row = json.loads(line)
            if key(row) in replacement:
                new = replacement[key(row)]
                assert row["source_sha256"] == new["source_sha256"], key(row)
                row = new
                found.add(key(row))
            output.write(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
    assert found == set(replacement), set(replacement) - found
    print(f"replaced {len(found)} rows in a complete recording")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("pilots")
    p.add_argument("root", type=Path)
    p.add_argument("out", type=Path)
    p.add_argument("names", nargs="+")
    d = sub.add_parser("documents")
    d.add_argument("root", type=Path)
    d.add_argument("corpus", type=Path)
    d.add_argument("out", type=Path)
    d.add_argument("names", nargs="+")
    s = sub.add_parser("splice")
    s.add_argument("full", type=Path)
    s.add_argument("part", type=Path)
    s.add_argument("out", type=Path)
    args = parser.parse_args()
    if args.command == "pilots":
        pilots(args.root, args.out, args.names)
    elif args.command == "documents":
        documents(args.root, args.corpus, args.out, args.names)
    else:
        splice(args.full, args.part, args.out)


if __name__ == "__main__":
    main()
