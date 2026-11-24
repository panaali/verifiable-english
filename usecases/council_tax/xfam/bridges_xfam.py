"""The frozen age bridge (bridge/age.py, 1946ba1f0f) on the cross-family encoder's inputs: its own main() with HERE
swapped to xfam/bridge (reads xfam/bridge/inputs.jsonl, writes xfam/bridge/bridges.jsonl). usage: python3 -I usecases/council_tax/xfam/bridges_xfam.py"""
import sys
from pathlib import Path

X = Path(__file__).resolve().parent
sys.path.insert(0, str(X.parent / "bridge"))
import age as AGE  # noqa: E402

AGE.HERE = X / "bridge"
sys.exit(AGE.main())
