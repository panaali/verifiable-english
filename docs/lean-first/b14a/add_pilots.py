"""Add to a base and a head recording the pilot documents that pilot branches gained after they were recorded.

    prlimit --as=8589934592 -- uv run python docs/lean-first/b14a/add_pilots.py BASE_ROOT BASE_REC HEAD_ROOT HEAD_REC

`tools/lean_first_diff.py compare` expects every `.ve.md` on every `pilot/*` branch; a branch created while the
recordings ran leaves them short. This records the missing documents on both sides through the recorder's own
`pilot_check` (its default limits, no raised timeout), one document at a time, and appends the rows to each
recording. Neither checkout has the Rust memory budget (infra/oom-rootcause), so the command runs under an 8 GB
address-space limit that every child inherits; a document that reaches it is recorded with that failure.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools import lean_first_diff as diff  # noqa: E402


def main() -> None:
    base_root, base_rec, head_root, head_rec = sys.argv[1:5]
    have = {json.loads(line)["case"] for line in open(base_rec) if '"pilots"' in line}
    assert have == {json.loads(line)["case"] for line in open(head_rec) if '"pilots"' in line}
    documents = [item for item in diff.pilot_documents(ROOT) if item[0] not in have]
    for side, root, rec in (("base", base_root, base_rec), ("head", head_root, head_rec)):
        root, rec = Path(root).resolve(), Path(rec)
        scratch = rec.with_suffix(".pilots")
        scratch.mkdir(exist_ok=True)
        env = {**os.environ, "PYTHONPATH": str(root), "VE_SHADOW_LOG": str(scratch / "english-shadow.jsonl")}
        env.pop("VE_AUTHORITY", None)
        with rec.open("a") as out:
            for name, blob, text in documents:
                path = scratch / f"{blob}.ve.md"
                path.write_bytes(text)
                row = {"corpus": "pilots", "authority": "default", "case": name, "op": "document_check",
                       "source_sha256": blob, "outcome": diff.pilot_check(root, path, env)}
                out.write(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
                out.flush()
                print(side, name, json.dumps(row["outcome"])[:160], flush=True)


if __name__ == "__main__":
    main()
