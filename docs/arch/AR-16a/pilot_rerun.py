"""AR-16a evidence (not a test): re-record pilot documents one at a time, base then head, as
`tools/lean_first_diff.py record --corpus pilots` records them (`pilot_documents`, `write_pilot`, `pilot_check`,
the same environment), for the records whose A/B outcome was a recorder time-out on one side under the machine's
load (PIPELINE-LIMITS L75). `--timeout` replaces the recorder's 600 s wall-clock limit for this re-run only; each
side's outcome is written as the recorder writes it, and the two are compared as JSON.

    python docs/arch/AR-16a/pilot_rerun.py --base-root DIR --head-root DIR --case NAME ... [--timeout S] --out FILE
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import lean_first_diff as diff  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--base-root", type=Path, required=True)
    parser.add_argument("--head-root", type=Path, required=True)
    parser.add_argument("--case", nargs="+", required=True)
    parser.add_argument("--timeout", type=int, default=diff.PILOT_TIMEOUT)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    diff.PILOT_TIMEOUT = args.timeout
    documents = {name: (blob, text) for name, blob, text in diff.pilot_documents(ROOT)}
    rows = []
    with tempfile.TemporaryDirectory(prefix="ar16a-pilot-rerun-") as scratch:
        for name in args.case:
            blob, text = documents[name]
            row = {"case": name, "source_sha256": blob, "timeout": args.timeout}
            for side, root in (("base", args.base_root.resolve()), ("head", args.head_root.resolve())):
                env = {**os.environ, "PYTHONPATH": str(root),
                       "VE_SHADOW_LOG": str(Path(scratch) / f"{side}-english-shadow.jsonl")}
                env.pop("VE_AUTHORITY", None)
                (Path(scratch) / side).mkdir(exist_ok=True)
                path = diff.write_pilot(ROOT, Path(scratch) / side, name, blob, text)
                start = time.monotonic()
                row[side] = diff.pilot_check(root, path, env)
                row[f"{side}_seconds"] = round(time.monotonic() - start)
            row["same"] = row["base"] == row["head"]
            row["answered"] = "timeout" not in row["base"] and "timeout" not in row["head"]
            rows.append(row)
            print(json.dumps({k: v for k, v in row.items() if k not in ("base", "head")}), flush=True)
    args.out.write_text(json.dumps(rows, indent=1, sort_keys=True) + "\n")
    return 0 if all(row["same"] and row["answered"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
