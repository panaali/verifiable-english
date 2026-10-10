"""Check, cover and render every translation part through the ordinary entry points (foreground)."""
import json, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from ve.document import check_document, load_document, render_document
from ve.errors import VEError

out = {}
for path in sorted(HERE.glob("translation-part*.ve.md")):
    t = time.monotonic()
    try:
        rep = check_document(path)
        doc = load_document(path)
        text = render_document(path)
        (HERE / "rendered-parts").mkdir(exist_ok=True)
        (HERE / "rendered-parts" / (path.name[:-len(".ve.md")] + ".md")).write_text(text)
        out[path.name] = {"seconds": round(time.monotonic() - t, 1), "coverage": rep["coverage"], "premises": {k: v for k, v in rep["premises"].items() if k not in ("choices", "model", "candidates")},
                          "readings_status": (rep.get("readings") or {}).get("status"),
                          "conflict": ((rep.get("readings") or {}).get("conflict") or {}).get("status"),
                          "unit_status": {u["id"]: u["status"] for u in doc["units"]},
                          "document_id": rep["document_id"], "source_id": rep["source_id"]}
        print(path.name, "ok", out[path.name]["premises"].get("status"), out[path.name]["readings_status"], out[path.name]["seconds"], flush=True)
    except Exception as e:
        c = getattr(e, "message", None) or str(e)
        out[path.name] = {"error": f"{type(e).__name__}: {c}"[:600]}
        print(path.name, "ERR", out[path.name]["error"], flush=True)
(HERE / "parts-check.json").write_text(json.dumps(out, indent=1))
