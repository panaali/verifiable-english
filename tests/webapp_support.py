"""What the editor's tests need beyond the locked environment: its web server (fastapi) and node.

The gate's environment is synced from uv.lock, which the Lean-first oracle freezes
(tools/lean_first_oracle.py); the web server's packages come from webapp/requirements.txt on top
of it, and node reads the page's JavaScript. A module never skips at collection (the gate refuses
that: it drops the module's test IDs); each test that needs one of them carries its mark, and its
skip is listed in tools/gate-optional.json with this reason.
"""
import importlib.util
import shutil

import pytest

SERVER = importlib.util.find_spec("fastapi") is not None
NEEDS_SERVER = pytest.mark.skipif(not SERVER, reason="the editor's web server is not in uv.lock: "
                                  "uv pip install --require-hashes -r webapp/requirements.txt")
NEEDS_NODE = pytest.mark.skipif(shutil.which("node") is None,
                                reason="reads the page's JavaScript with node, not installed here")
