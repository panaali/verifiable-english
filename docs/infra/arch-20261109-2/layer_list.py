"""Print every Lean and Python module of this checkout with the layer a tools/layer_policy.py gives it, one per line.

    uv run python docs/infra/arch-20261109-2/layer_list.py [--policy-at COMMIT]

Without `--policy-at` the checkout's own tools/layer_policy.py places each module (reading the modules' first-line
declarations); with it, that commit's tools/layer_policy.py places the same modules, so both lists cover one tree.
The batch saved `--policy-at <merge base>` as layers-before.txt and the head's as layers-after.txt, both on the final
tree; REPORT.md compares them. After a sync with main, run both again on the synced tree.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]


def policy(commit: str | None, scratch: Path):
    """The layer policy module of `commit` (None: the checkout's), with ROOT reading this checkout's lean/."""
    if commit is None:
        sys.path.insert(0, str(ROOT / "tools"))
        import layer_policy
        return layer_policy
    (scratch / "tools").mkdir()
    (scratch / "lean").symlink_to(ROOT / "lean")  # its ROOT is the scratch directory: lean_executables reads lean/
    (scratch / "tools/layer_policy.py").write_bytes(subprocess.run(
        ["git", "show", f"{commit}:tools/layer_policy.py"], cwd=ROOT, capture_output=True, check=True).stdout)
    spec = importlib.util.spec_from_file_location("base_layer_policy", scratch / "tools/layer_policy.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--policy-at", help="place the modules with this commit's tools/layer_policy.py")
    args = parser.parse_args()
    lean = sorted(".".join(p.relative_to(ROOT / "lean").with_suffix("").parts)
                  for p in (ROOT / "lean").rglob("*.lean") if ".lake" not in p.parts)
    python = sorted(".".join(p.relative_to(ROOT).with_suffix("").parts).removesuffix(".__init__")
                    for package in ("ve", "ve_experiments") for p in (ROOT / package).rglob("*.py")
                    if "__pycache__" not in p.parts)
    with tempfile.TemporaryDirectory() as scratch:
        layers = policy(args.policy_at, Path(scratch))
        for module in lean:
            print(f"lean {module} {layers.lean_layer(module)}")
        for module in python:
            print(f"python {module} {layers.python_layer(module)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
