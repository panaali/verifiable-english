"""sa-nd-atomsb evidence: the norm-defaults route cases answer byte-identically before and after.

Runs sa-nd-atoms' comparator (`docs/norm-defaults/sa-nd-atoms/byte_identity.py`, its one owner)
and saves its result here instead of beside it. The saved file is the evidence; nothing reads git.

    uv run python docs/norm-defaults/sa-nd-atomsb/byte_identity.py BASE_SERVICE BRANCH_SERVICE BASE_REV BRANCH_REV
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "sa-nd-atoms" / "byte_identity.py"

if __name__ == "__main__":
    spec = importlib.util.spec_from_file_location("sa_nd_atoms_byte_identity", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUT = Path(__file__).with_name("byte-identity.json")
    sys.exit(module.main(*sys.argv[1:5]))
