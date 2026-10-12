"""Re-record, on both sides, the records an A/B comparison found unavailable through a host-load timeout.

    uv run python docs/lean-first/b14a/rerecord.py AB.json BASE_ROOT BASE_REC HEAD_ROOT HEAD_REC OUT_PREFIX

Under load, Rust's flat 5 s per-call limit (plan section 4, F4) and the recorder's 600 s per-pilot limit stop
some documents on one side only. This reruns every `pilots` or `document` difference of class `availability`
or `unavailable` whose either side timed out, on both sides, with `VE_RUST_TIMEOUT` raised to the test suite's
hang guard (`RERUN_RUST_TIMEOUT`) and the per-document limit to `RERUN_PILOT_TIMEOUT`, through the recorder's own
`pilot_check` (pilots) or its in-process document operations (document corpus, one child per record). It
writes `OUT_PREFIX.base.json` and `OUT_PREFIX.head.json`: each recording with those rows replaced, every other
row unchanged, so `tools/lean_first_diff.py compare` reads them as complete recordings.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools import lean_first_diff as diff  # noqa: E402

RERUN_RUST_TIMEOUT = "300"
RERUN_PILOT_TIMEOUT = 3000
FIELDS = ("corpus", "authority", "case", "op")


def timed_out(outcome) -> bool:
    text = json.dumps(outcome)
    return "timed out after" in text or '"timeout"' in text


def key(row):
    return tuple(row[name] for name in FIELDS)


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open() if line.strip()]


DOCUMENT_CHILD = r"""
import json, sys
from tools import lean_first_diff as diff
from ve.document import check_document, render_document
path, op = sys.argv[1], sys.argv[2]
call = check_document if op == "document_check" else render_document
print(json.dumps(diff.outcome(lambda: call(path)), sort_keys=True, ensure_ascii=False))
"""


def rerun(root: Path, scratch: Path, row: dict) -> dict:
    env = {**os.environ, "PYTHONPATH": str(root), "VE_RUST_TIMEOUT": RERUN_RUST_TIMEOUT}
    env.pop("VE_AUTHORITY", None)
    if row["corpus"] == "pilots":
        env["VE_SHADOW_LOG"] = str(scratch / "english-shadow.jsonl")
        diff.PILOT_TIMEOUT = RERUN_PILOT_TIMEOUT
        return {**row, "outcome": diff.pilot_check(root, scratch / f"{row['source_sha256']}.ve.md", env)}
    path = scratch / row["case"].replace("/", "_") / "document.ve.md"
    done = subprocess.run([sys.executable, "-c", DOCUMENT_CHILD, str(path), row["op"]], cwd=root, env=env,
                          capture_output=True, text=True, timeout=RERUN_PILOT_TIMEOUT)
    return {**row, "outcome": json.loads(done.stdout)}


def main() -> None:
    ab, base_root, base_rec, head_root, head_rec, prefix = sys.argv[1:7]
    wanted = {(d["corpus"], d["authority"], d["case"], d["op"]) for d in json.load(open(ab))["differences"]
              if d["corpus"] in ("pilots", "document") and d["class"] in ("availability", "unavailable")
              and (timed_out(d["base"]) or timed_out(d["head"]))}
    for side, root, rec in (("base", base_root, base_rec), ("head", head_root, head_rec)):
        rec, root = Path(rec), Path(root).resolve()
        recorded = rows(rec)
        todo = [row for row in recorded if key(row) in wanted]
        assert {key(row) for row in todo} == wanted, side

        def scratch(row):
            return rec.with_suffix(".pilots" if row["corpus"] == "pilots" else ".document")

        with ThreadPoolExecutor(max_workers=4) as pool:
            fresh = {key(new): new for new in pool.map(lambda row: rerun(root, scratch(row), row), todo)}
        out = Path(f"{prefix}.{side}.json")
        with out.open("w") as handle:
            for row in recorded:
                row = fresh.get(key(row), row)
                handle.write(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
        print(f"{side}: re-recorded {len(fresh)} rows into {out}")


if __name__ == "__main__":
    main()
