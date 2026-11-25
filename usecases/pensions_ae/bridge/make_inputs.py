"""Write bridge/inputs.jsonl from cases.py (no computing: the stated values are copied). Pass 1: every case's stated
days and windows; pass 2 (after `pae_bridge.py inputs.jsonl > bridges.jsonl`): adds each window point's age, stretch-end
age and prescribed-period start (encode.expand_bridge). usage (from usecases/pensions_ae):
  python3 -I bridge/make_inputs.py 1 && python3 -I bridge/pae_bridge.py bridge/inputs.jsonl > bridge/bridges.jsonl
  python3 -I bridge/make_inputs.py 2 && python3 -I bridge/pae_bridge.py bridge/inputs.jsonl > bridge/bridges.jsonl
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import cases as K  # noqa: E402
import encode as E  # noqa: E402

lines = [b for c in K.CASES for b in E.bridge_inputs(c)]
if sys.argv[1] == "2":
    br = E.bridges()
    lines += [b for c in K.CASES for b in E.expand_bridge(c, br)]
(HERE / "inputs.jsonl").write_text("".join(json.dumps(b, sort_keys=True) + "\n" for b in lines), encoding="utf-8")
print(len(lines), "input lines")
