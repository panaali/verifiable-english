"""Generate the Lean `route` subcommand's shipped cases.

Usage (repo root): uv run python lean/VE/Route/examples/generate.py
Writes lean/VE/Route/examples/route-cases.json: every active case of the shared
P0 conformance families (conformance/p0.py), in the form the Lean runner takes,
each with the Lean verdict it must produce under "expected" (Lean ignores the
field). tests/test_p0_three_way.py checks the file is current and runs the
same families through Python, Rust and Lean.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from conformance.p0 import FAMILIES, lean_case  # noqa: E402

OUT = Path(__file__).with_name("route-cases.json")


def cases():
    return [lean_case(case) for build in FAMILIES.values() for case in build() if "pending" not in case]


def main():
    OUT.write_text(json.dumps(cases(), indent=1, ensure_ascii=False) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
