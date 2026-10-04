"""One verification step of the built translation, written to JSON so no step exceeds a tool call's hour.

    VE_LEAN_TIMEOUT=3000 uv run --frozen python verify_step.py <path> load|check|render|unmodified

load        load_document, then coverage over the loaded document          -> coverage.json
check       check_document (readings report, premises, coverage)            -> verdict.json
render      render_document (the natural view)                              -> rendered.md
unmodified  check_document with the tag's own limits (no VE_LEAN_TIMEOUT)   -> unmodified.json

The tag's single Lean call has a hard 120 s timeout (ve/backends/lean.py run_readings_cases, no setting). VE_LEAN_TIMEOUT
raises it in this script only (the function's keyword default); every other limit is the tag's.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import s1doc as S  # noqa: E402,F401
from ve.document import check_document, coverage, load_document, render_document  # noqa: E402
from ve.errors import VEError  # noqa: E402
import ve.backends.lean as _lean  # noqa: E402

path, step = Path(sys.argv[1]), sys.argv[2]
if os.environ.get("VE_LEAN_TIMEOUT") and step != "unmodified":
    _lean.run_readings_cases.__kwdefaults__["timeout"] = float(os.environ["VE_LEAN_TIMEOUT"])
out = path.parent
started = time.monotonic()
try:
    if step == "load":
        doc = load_document(path)
        elapsed = time.monotonic() - started
        cov = coverage(doc)
        (out / "coverage.json").write_text(json.dumps({"load_seconds": round(elapsed, 1), "coverage": cov},
                                                      ensure_ascii=False, indent=1, default=str))
        print(f"load {elapsed:.1f}s", {k: cov[k] for k in ("source_bytes", "accounted_bytes", "coverage_percent")})
    elif step == "check":
        report = check_document(path)
        elapsed = time.monotonic() - started
        (out / "verdict.json").write_text(json.dumps({"check_seconds": round(elapsed, 1), "report": report},
                                                     ensure_ascii=False, indent=1, default=str))
        print(f"check {elapsed:.1f}s premises={report['premises']}")
    elif step == "render":
        text = render_document(path)
        (out / "rendered.md").write_text(text)
        print(f"render {time.monotonic() - started:.1f}s {len(text)} chars")
    elif step == "unmodified":
        try:
            check_document(path)
            result = {"status": "checked"}
        except Exception as exc:  # CheckerUnavailable is not a VEError
            result = {"status": "refused", "error": getattr(exc, "message", str(exc)), "type": type(exc).__name__}
        result["seconds"] = round(time.monotonic() - started, 1)
        (out / "unmodified.json").write_text(json.dumps(result, indent=1))
        print(result)
    else:
        raise SystemExit("unknown step")
except VEError as exc:
    print("REFUSED:", type(exc).__name__, getattr(exc, "message", str(exc)))
    raise SystemExit(1)
