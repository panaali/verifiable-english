"""Part01 measurement (X4): `ve document check` under an address-space cap: wall time, peak resident set of the child processes, verdict.

    prlimit --as=6442450944 uv run --frozen python usecases/udhr-pilot/run-20261021T0600Z/part01_measure.py <label>

The default VE_RUST_TIMEOUT is kept (no environment override). Writes evidence/part01-check-<label>.json.
"""
import json, os, sys, threading, time, resource
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from ve.document import check_document, load_document

label = sys.argv[1]
doc = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "translation-part01.ve.md"
peaks, stop = {}, threading.Event()


def descendants(pid):
    kids = {}
    for p in Path("/proc").iterdir():
        if p.name.isdigit():
            try:
                stat = (p / "stat").read_text()
                kids.setdefault(int(stat.rsplit(")", 1)[1].split()[1]), []).append((int(p.name), stat.split("(", 1)[1].rsplit(")", 1)[0]))
            except OSError:
                pass
    out, todo = [], [pid]
    while todo:
        for c, name in kids.get(todo.pop(), []):
            out.append((c, name)); todo.append(c)
    return out


def poll():
    while not stop.is_set():
        for pid, name in descendants(os.getpid()):
            try:
                for line in (Path("/proc") / str(pid) / "status").read_text().splitlines():
                    if line.startswith("VmHWM:"):
                        kb = int(line.split()[1]); key = f"{name}"
                        peaks[key] = max(peaks.get(key, 0), kb)
            except OSError:
                pass
        stop.wait(0.1)


t = threading.Thread(target=poll, daemon=True); t.start()
limit = resource.getrlimit(resource.RLIMIT_AS)
started = time.monotonic()
try:
    rep = check_document(doc)
    wall = time.monotonic() - started
    d = load_document(doc)
    out = {"verdict": "ok", "premises": rep["premises"].get("status"), "readings_status": (rep.get("readings") or {}).get("status"),
           "conflict": ((rep.get("readings") or {}).get("conflict") or {}).get("status"),
           "bytes_by_status": rep["coverage"]["bytes_by_status"], "unit_status": {u: s["status"] for s in [d] for u, s in [(x["id"], x) for x in d["units"]] if u in ("u010", "u042", "u043", "u060", "u061")}}
except Exception as e:
    wall = time.monotonic() - started
    out = {"verdict": f"{type(e).__name__}: {getattr(e, 'message', None) or e}"[:500]}
stop.set(); t.join()
out.update({"label": label, "document": str(doc.relative_to(HERE.parents[2])), "wall_seconds": round(wall, 1), "address_space_cap_bytes": limit[0],
            "VE_RUST_TIMEOUT": os.environ.get("VE_RUST_TIMEOUT", "default (unset)"),
            "peak_child_resident_set_mb": {k: round(v / 1024, 1) for k, v in sorted(peaks.items(), key=lambda kv: -kv[1])},
            "peak_child_resident_set_mb_max": round(max(peaks.values(), default=0) / 1024, 1)})
(HERE / "evidence").mkdir(exist_ok=True)
(HERE / "evidence" / f"part01-check-{label}.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
