"""CROSS-FAMILY bridge input and output: the encoder's records' own dates (cases_xfam.write_bridge_inputs, the frozen
template's writer) -> xfam/bridge/inputs.jsonl, then the FROZEN bridge script (bridge/fmla_bridge.py, unchanged) ->
xfam/bridge/bridges.jsonl. usage (repository root): python3 -I usecases/fmla_eligibility/xfam/bridges_xfam.py"""
import sys
from pathlib import Path

X = Path(__file__).resolve().parent
sys.path.insert(0, str(X.parent / "bridge"))
sys.path.insert(0, str(X))
import cases_xfam  # noqa: E402
import fmla_bridge  # noqa: E402

n = cases_xfam.write_bridge_inputs(X / "bridge" / "inputs.jsonl")
fmla_bridge.main([str(X / "bridge" / "inputs.jsonl"), str(X / "bridge" / "bridges.jsonl")])
print(n, "bridge input rows")
