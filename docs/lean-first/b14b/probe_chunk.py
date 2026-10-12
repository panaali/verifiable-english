"""Record one disjoint slice of the Stage-0 probe matrix for a long A/B run.

The slices retain the original probe generator, observer and record projection.
Concatenate ``--aux`` and every ``--chunk I --chunks N`` output, then use
``tools/lean_first_diff.py compare --corpus probe`` to check completeness.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--authority", choices=("python", "lean"), required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--aux", action="store_true")
    group.add_argument("--chunk", type=int)
    parser.add_argument("--chunks", type=int, default=6)
    args = parser.parse_args()
    root = args.root.resolve()
    if args.chunks < 1 or (args.chunk is not None and not 0 <= args.chunk < args.chunks):
        parser.error("chunk must be in [0, chunks)")
    sys.path.insert(0, str(root))
    from tests import probe_matrix as probe
    from tools import lean_first_diff, stage2_parity
    from ve.backends import dispatch

    if not Path(probe.__file__).resolve().is_relative_to(root):
        raise RuntimeError("probe generator was imported from the wrong checkout")
    operations = () if args.aux else probe.OPERATIONS[args.chunk::args.chunks]
    probe.OPERATIONS = operations
    probe.outcome = stage2_parity._outcome
    if stage2_parity._observe not in dispatch.observers:
        dispatch.observers.append(stage2_parity._observe)
    probe.graph_baselines = stage2_parity._backend_graph_baselines if args.aux else dict
    if not args.aux:
        probe.boundary_baselines = dict
        probe.feature_baselines = dict
    os.chdir(root)
    data = stage2_parity._generate(args.authority)
    source = lean_first_diff.digest(root / "tests/probe_matrix.py")
    count = 0
    with args.out.open("w") as out:
        for row in lean_first_diff.probe_rows(data, source):
            if (row["op"] in lean_first_diff.PROBE_SECTIONS) != args.aux:
                continue
            if not args.aux and row["op"] not in operations:
                continue
            out.write(json.dumps({"corpus": "probe", "authority": args.authority, **row},
                                 sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
            count += 1
    print(f"{args.authority}: {count} records in {args.out}")


if __name__ == "__main__":
    main()
