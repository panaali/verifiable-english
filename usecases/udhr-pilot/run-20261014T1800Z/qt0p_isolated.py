"""QT-0p measured on a copy: the previous run's part03 with ONLY u097 changed (the plan's stated check), foreground.

Copies the previous run's translation and readings to a scratch directory (outside the repository), applies repair13 for u097 alone,
rebuilds part03 there and checks it. Writes qt0p-isolated.json. The scratch copy is removed at the end.

    uv run --frozen python usecases/udhr-pilot/run-20261014T1800Z/qt0p_isolated.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "tools"))

scratch = Path(tempfile.mkdtemp(prefix="udhr-qt0p-"))
run = scratch / "usecases" / "udhr-pilot" / "run-iso"
(run.parent / "source").mkdir(parents=True)
shutil.copy(HERE.parent / "source" / "udhr.md", run.parent / "source" / "udhr.md")
shutil.copytree(HERE / "previous-20261013T0600Z", run / "prev")
for f in HERE.glob("*.py"):
    shutil.copy(f, run / f.name)
shutil.copytree(HERE / "evidence", run / "evidence")
shutil.copy(run / "prev" / "translation.ve.md", run / "translation.ve.md")
shutil.copy(HERE / "units.json", run / "units.json")
shutil.copytree(run / "prev" / "readings", run / "readings")
sys.path.insert(0, str(run))

import repair13_specs as R  # noqa: E402
R.ORDER[:] = ["u097"]                              # only u097; the module object is the one repair13 imports
import repair13  # noqa: E402
repair13.HERE = run
repair13.READINGS = run / "readings"
repair13.main()
import integrate as I  # noqa: E402
I.HERE = run
I.READINGS = run / "readings"
path, info = I.main("u072", "u103", "part03", run / "translation-part03.ve.md")
from ve.document import check_document, load_document  # noqa: E402
rep = check_document(path)
doc = load_document(path)
prev = json.loads((HERE / "previous-20261013T0600Z" / "metrics.json").read_text())["part_checks"]["translation-part03.ve.md"]
out = {"part03_bytes_by_status_before": prev["coverage_bytes_by_status"], "part03_bytes_by_status_after": rep["coverage"]["bytes_by_status"],
       "premises_after": rep["premises"].get("status"), "premises_before": prev["premises"].get("status"),
       "u097_status": next(u["status"] for u in doc["units"] if u["id"] == "u097"), "gaps": rep["coverage"]["residual"].get("gaps"),
       "expected": "part03 OPEN +76 B, premise check stays `model`"}
out["open_delta"] = out["part03_bytes_by_status_after"].get("OPEN", 0) - out["part03_bytes_by_status_before"].get("OPEN", 0)
out["as_expected"] = out["open_delta"] == 76 and out["premises_after"] == "model" == out["premises_before"]
(HERE / "qt0p-isolated.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
shutil.rmtree(scratch)
