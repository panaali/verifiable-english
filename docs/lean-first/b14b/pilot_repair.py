"""Rerecord named pilot cases in a common scratch path after a loaded A/B run.

The same scratch path on each side avoids path-only diagnostic changes. Run the
base and head sequentially so their two recordings see comparable load.
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
    parser.add_argument("--differences", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--resume-at", help="repeat this named pilot and all later repair cases")
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root))
    from tools import lean_first_diff as diff
    import ve
    if not Path(ve.__file__).resolve().is_relative_to(root):
        raise RuntimeError("ve was imported from the wrong checkout")
    wanted = {row["case"] for row in json.loads(args.differences.read_text())["differences"]}
    documents = [item for item in diff.pilot_documents(diff.ROOT) if item[0] in wanted]
    if {name for name, _, _ in documents} != wanted:
        raise RuntimeError("the repair set names a pilot outside the frozen inventory")
    if args.resume_at:
        positions = [i for i, (name, _, _) in enumerate(documents) if name == args.resume_at]
        if len(positions) != 1:
            raise RuntimeError("resume case is not in the repair set")
        documents = documents[positions[0]:]
    args.scratch.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONPATH": str(root),
           "VE_SHADOW_LOG": str(args.scratch / "english-shadow.jsonl")}
    env.pop("VE_AUTHORITY", None)
    with args.out.open("w") as out:
        for name, blob, content in documents:
            path = args.scratch / f"{blob}.ve.md"
            path.write_bytes(content)
            row = {"corpus": "pilots", "authority": "default", "case": name,
                   "op": "document_check", "source_sha256": blob,
                   "outcome": diff.pilot_check(root, path, env)}
            out.write(json.dumps(row, sort_keys=True, separators=(",", ":"),
                                 ensure_ascii=False) + "\n")
            out.flush()
    print(f"rerecorded {len(documents)} pilot documents")


if __name__ == "__main__":
    main()
