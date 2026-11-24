"""The frozen six-year bridge (bridge/years.py, unchanged) on the cross-family encoder's dates: writes
xfam/bridge/inputs.jsonl from cases_xfam.BRIDGE_INPUTS (copied from the encoder's records), then runs years.main() with its
directory pointed at xfam/bridge/ (so it reads that inputs.jsonl and writes xfam/bridge/bridges.jsonl; the same-family
bridge/ files are not touched).
usage (repository root): python3 -I usecases/ved_first_year/xfam/bridge_xfam.py"""
import json
import sys
from pathlib import Path

X = Path(__file__).resolve().parent
sys.path.insert(0, str(X.parent / "bridge"))
sys.path.insert(0, str(X))
import cases_xfam  # noqa: E402
import years as Y  # noqa: E402

D = X / "bridge"
D.mkdir(exist_ok=True)
rows = [{k: r[k] for k in ("case", "date", "licence", "registered")} for r in cases_xfam.BRIDGE_INPUTS]
(D / "inputs.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
Y.HERE = D
sys.exit(Y.main())
