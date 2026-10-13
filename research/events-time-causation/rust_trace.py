"""Run `ve document check` in-process and record every Rust `ve jsonl` call: its mode, size, time and outcome.

Measurement only: it wraps `ve.backends.rust_jsonl._run_checker` from outside (no product code changes). The
request line of each call that fails is saved next to the log, so the failing case can be inspected.

Usage: python3 rust_trace.py <document.ve.md> <out-prefix>
"""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import ve.backends.rust_jsonl as R  # noqa: E402
from ve.document import check_document  # noqa: E402

calls = []
_real = R._run_checker


def traced(args, input, timeout):
    case = json.loads(input)
    row = {"keys": sorted(case)[:12], "mode": case.get("mode") or case.get("kind") or case.get("route"),
           "bytes": len(input), "timeout": timeout}
    t = time.monotonic()
    try:
        out = _real(args, input=input, timeout=timeout)
        row["outcome"] = "ok"
        return out
    except subprocess.TimeoutExpired:
        row["outcome"] = "timeout"
        raise
    except OSError as exc:
        row["outcome"] = f"oserror: {exc}"
        raise
    finally:
        row["seconds"] = round(time.monotonic() - t, 2)
        if row["outcome"] != "ok":
            row["saved"] = f"{PREFIX}.case{len(calls)}.json"
            Path(row["saved"]).write_bytes(input)
        calls.append(row)


R._run_checker = traced

if __name__ == "__main__":
    doc, PREFIX = sys.argv[1], sys.argv[2]
    try:
        rep = check_document(Path(doc))
        result = {"ok": True, "readings_conflict": ((rep.get("readings") or {}).get("conflict") or {}).get("status")}
    except Exception as exc:  # the failure is the measurement
        result = {"ok": False, "error": f"{type(exc).__name__}: {exc}"[:600]}
    Path(f"{PREFIX}.rust-trace.json").write_text(json.dumps({"result": result, "calls": calls}, indent=1) + "\n")
    print(json.dumps(result), len(calls), "calls")
    for c in calls:
        print(c["mode"], c["bytes"], c["seconds"], c["outcome"], c["keys"])
