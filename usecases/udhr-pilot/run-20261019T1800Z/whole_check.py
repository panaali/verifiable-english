"""Load and check translation-whole.ve.md (the whole declaration as one document with component reading sets); record the outcome.

    uv run --frozen python usecases/udhr-pilot/run-20261019T0600Z/whole_check.py [load|check]
"""
import json, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from ve.document import check_document, coverage, load_document
from ve.errors import VEError

# optional argument "load" or "check": run one step (each takes about 43 min; a foreground command is limited to 60 min)
only = sys.argv[1:] or ["load", "check"]
resultfile = HERE / "experiment-whole" / "whole-check.json"
out = json.loads(resultfile.read_text()) if sys.argv[1:] and resultfile.exists() else {}
for step in only:
    t = time.monotonic()
    try:
        if step == "load":
            doc = load_document(HERE / "experiment-whole" / "translation-whole.ve.md")
            cov = coverage(doc)
            out[step] = {"seconds": round(time.monotonic() - t, 1), "coverage_percent": cov["coverage_percent"]}
        else:
            rep = check_document(HERE / "experiment-whole" / "translation-whole.ve.md")
            out[step] = {"seconds": round(time.monotonic() - t, 1), "readings_status": (rep.get("readings") or {}).get("status"),
                         "premises": rep["premises"].get("status")}
    except Exception as e:
        out[step] = {"seconds": round(time.monotonic() - t, 1), "error": f"{type(e).__name__}: {getattr(e, 'message', None) or e}"[:500]}
        print(step, out[step], flush=True)
        break
    print(step, out[step], flush=True)
resultfile.write_text(json.dumps(out, indent=1))
