"""Print every Lean and Python module of the checkout with the layer tools/layer_policy.py gives it, one per line.

Run from the checkout: `uv run python docs/infra/arch-20261109-2/layer_list.py > <file>`. The batch ran it on the
base tree before the change (layers-before.txt) and on the final tree (layers-after.txt); the two are identical.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import layer_policy  # noqa: E402

lean = sorted(".".join(p.relative_to(ROOT / "lean").with_suffix("").parts)
              for p in (ROOT / "lean").rglob("*.lean") if ".lake" not in p.parts)
python = sorted(".".join(p.relative_to(ROOT).with_suffix("").parts).removesuffix(".__init__")
                for package in ("ve", "ve_experiments") for p in (ROOT / package).rglob("*.py")
                if "__pycache__" not in p.parts)
for module in lean:
    print(f"lean {module} {layer_policy.lean_layer(module)}")
for module in python:
    print(f"python {module} {layer_policy.python_layer(module)}")
