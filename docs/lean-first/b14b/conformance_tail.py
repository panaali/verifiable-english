"""Resume a timed-out conformance recording or repair unavailable checker cases.

The named case is repeated, or every case with an operational start failure is
rerun. Merge this output with the partial file by full
``(corpus, authority, case, op)`` key, checking duplicate outcomes agree, then
run ``lean_first_diff.py compare`` to verify complete corpus coverage.
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
    group.add_argument("--start", help="first case as corpus-name/case-id")
    group.add_argument("--affected-from", type=Path,
                       help="rerun cases whose existing outcome says a checker could not start")
    parser.add_argument("--resume-at", help="with --affected-from, resume at this affected case")
    args = parser.parse_args()
    if args.resume_at and not args.affected_from:
        parser.error("--resume-at requires --affected-from")
    root = args.root.resolve()
    sys.path.insert(0, str(root))
    from tools import lean_first_diff as diff
    import ve
    if not Path(ve.__file__).resolve().is_relative_to(root):
        raise RuntimeError("ve was imported from the wrong checkout")
    os.chdir(root)
    os.environ["VE_AUTHORITY"] = args.authority
    affected = set()
    if args.affected_from:
        lines = args.affected_from.read_text().split("\n")
        if lines and not lines[-1]:
            lines.pop()
        for index, line in enumerate(lines):
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                if index != len(lines) - 1:
                    raise
                continue  # a timeout may interrupt the last write
            if row.get("corpus") == "conformance" and row.get("authority") == args.authority \
                    and "cannot start" in json.dumps(row.get("outcome")):
                affected.add(row["case"])
        if not affected:
            raise RuntimeError("no affected cases were found")
    active = False
    resumed = args.resume_at is None
    seen = set()
    count = 0
    with args.out.open("w") as out:
        for name in diff.CONFORMANCE:
            path = root / f"conformance/{name}.json"
            source = diff.digest(path)
            for case in json.loads(path.read_text()):
                key = f"{name}/{case['id']}"
                if args.start:
                    active |= key == args.start
                    chosen = active
                else:
                    resumed |= key == args.resume_at
                    chosen = resumed and key in affected
                if not chosen:
                    continue
                seen.add(key)
                calls = diff.conformance_calls(case)
                for op, result in diff.conformance_ops(case, lambda op: diff.outcome(calls[op])).items():
                    row = {"corpus": "conformance", "authority": args.authority,
                           "case": key, "source_sha256": source, "op": op, "outcome": result}
                    out.write(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
                    out.flush()
                    count += 1
    if args.start and not active:
        raise RuntimeError(f"start case {args.start!r} was not found")
    if args.resume_at and args.resume_at not in seen:
        raise RuntimeError(f"resume case {args.resume_at!r} was not affected")
    if affected and not args.resume_at and not affected <= seen:
        raise RuntimeError(f"affected cases missing from input: {sorted(affected - seen)[:5]}")
    print(f"{args.authority}: {count} rows from {args.start or len(affected)} cases")


if __name__ == "__main__":
    main()
