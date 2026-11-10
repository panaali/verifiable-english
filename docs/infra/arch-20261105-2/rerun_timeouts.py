"""Re-record the pilot documents a recording lost to the 600 s timeout under machine load (A/B evidence aid).

    uv run python docs/infra/arch-20261105-2/rerun_timeouts.py --root CHECKOUT --recording SIDE.jsonl \
        --other OTHER.jsonl --out SIDE-rerun.jsonl

Evidence tooling, not a test. For every `pilots` record of `--recording` whose outcome is `{"timeout": 600}` while the
same record of `--other` is not a timeout, this runs `tools/lean_first_diff.py`'s own `pilot_check` again in the
checkout `--root`, with the recorder's environment and pilot file (`write_pilot`, in the recording's `.pilots`
directory), one process per document, `--workers` at once (default one). Every other line is copied byte for
byte. A record that times out again stays a timeout. Records that time out on both sides are left as they are:
they are identical and listed under R7.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import lean_first_diff as lfd  # noqa: E402


def key(record: dict) -> tuple:
    return record["corpus"], record["authority"], record["op"], record["case"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--recording", required=True, type=Path)
    parser.add_argument("--other", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=1, help="documents checked at once (default one)")
    args = parser.parse_args()
    other = {}
    with args.other.open() as handle:
        for text in handle:
            record = json.loads(text)
            if record["corpus"] == "pilots":
                other[key(record)] = record["outcome"]
    lines = args.recording.read_text().splitlines(keepends=True)
    redo = [i for i, text in enumerate(lines) if '"corpus":"pilots"' in text
            and (record := json.loads(text))["outcome"] == {"timeout": lfd.PILOT_TIMEOUT}
            and other.get(key(record)) != {"timeout": lfd.PILOT_TIMEOUT}]
    documents = {name: (blob, text) for name, blob, text in lfd.pilot_documents(ROOT)}
    root = args.root.resolve()
    scratch = args.recording.resolve().with_suffix(".pilots")
    env = {**os.environ, "PYTHONPATH": str(root), "VE_SHADOW_LOG": str(scratch / "english-shadow.jsonl")}
    env.pop("VE_AUTHORITY", None)

    def again(index: int) -> tuple[int, str]:
        record = json.loads(lines[index])
        blob, text = documents[record["case"]]
        assert blob == record["source_sha256"], record["case"]
        path = lfd.write_pilot(ROOT, scratch, record["case"], blob, text)
        record["outcome"] = lfd.pilot_check(root, path, env)
        print(f"{record['case']}: {'timeout' if 'timeout' in record['outcome'] else 'exit %s' % record['outcome']['exit']}",
              flush=True)
        return index, lfd.line(record)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for index, text in pool.map(again, redo):
            lines[index] = text
    args.out.write_text("".join(lines))
    print(f"{len(redo)} record(s) re-run; {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
