"""Load the pinned pre-switch Python norm-defaults oracle for differential tests.

The source is kept in Git history so the production tree has one implementation.
No product entry point imports this module.
"""
from __future__ import annotations

import hashlib
from importlib.machinery import ModuleSpec
from pathlib import Path
import subprocess
import sys
from types import ModuleType

_ROOT = Path(__file__).resolve().parents[1]
_REVISION = "9160d326"
_SHA256 = "971ced0206d040903906b896c3a6902752db1d19788745bc4357fe53bfbad870"
_source = subprocess.check_output(["git", "show", f"{_REVISION}:ve/norm_defaults.py"], cwd=_ROOT)
if hashlib.sha256(_source).hexdigest() != _SHA256:
    raise RuntimeError("frozen norm-defaults oracle source changed")
_oracle = ModuleType("ve._frozen_norm_defaults")
_oracle.__package__ = "ve"
_oracle.__spec__ = ModuleSpec(_oracle.__name__, loader=None)
sys.modules[_oracle.__name__] = _oracle
exec(compile(_source, f"{_REVISION}:ve/norm_defaults.py", "exec"), _oracle.__dict__)
globals().update({name: value for name, value in vars(_oracle).items()
                  if not (name.startswith("__") and name.endswith("__"))})
