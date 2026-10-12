"""Record a bounded slice of a generated document A/B corpus.

Uses ``lean_first_diff._rights_case`` on the frozen corpus JSON for rights,
norm defaults or document. Concatenate disjoint slices; the standard compare
checks that every case and both public operations are present exactly once.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing
import os
from pathlib import Path
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--corpus", choices=("rights", "norm_defaults", "document"), required=True)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--stop", type=int, required=True)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root))
    from tools import lean_first_diff as diff
    import ve
    if not Path(ve.__file__).resolve().is_relative_to(root):
        raise RuntimeError("ve was imported from the wrong checkout")
    os.chdir(root)
    os.environ.pop("VE_AUTHORITY", None)
    all_entries = json.loads(args.source.read_text())
    if not 0 <= args.start < args.stop <= len(all_entries):
        parser.error(f"slice must be inside the {len(all_entries)} corpus entries")
    source_hash = diff.digest(args.source)
    scratch = args.out.with_suffix(".scratch")
    scratch.mkdir(exist_ok=True)
    entries = [(str(scratch), source_hash, row) for row in all_entries[args.start:args.stop]]
    count = 0
    with args.out.open("w") as out, multiprocessing.get_context("fork").Pool(args.workers) as pool:
        for results in pool.imap(diff._rights_case, entries, chunksize=8):
            for row in results:
                out.write(json.dumps({"corpus": args.corpus, **row}, sort_keys=True,
                                     separators=(",", ":"), ensure_ascii=False) + "\n")
                out.flush()
                count += 1
    print(f"{args.corpus} [{args.start}, {args.stop}): {count} records")


if __name__ == "__main__":
    main()
