"""The frozen NMW bridge (bridge/bridges.py, cd90cdc036) on the cross-family encoder's records: their "bridge" dates go
to xfam/bridge/inputs.jsonl (one row per record, as the build's own inputs.jsonl), then the frozen main() runs with HERE
swapped to xfam/bridge (writes xfam/bridge/bridges.jsonl). usage: python3 -I usecases/nmw/xfam/bridges_xfam.py"""
import json
import sys
from pathlib import Path

X = Path(__file__).resolve().parent
sys.path.insert(0, str(X.parent / "bridge"))
sys.path.insert(0, str(X))
import bridges as BR  # noqa: E402
import cases_xfam as K  # noqa: E402

rows = [c["bridge"] for c in K.CASES]
(X / "bridge" / "inputs.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
BR.HERE = str(X / "bridge")
sys.exit(BR.main())
