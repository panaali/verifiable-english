"""JT-E1s blinded reader calls and scoring: JT-E1r's frozen runner, bound to this frame and its displays.

The prompt, caps, account picker, call, accounting, journal and scoring are JT-E1r's code unchanged; only the
directory, the display generator and the pre-call commit check point here.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


render = _load("jt_e1s_render", HERE / "render.py")
_saved = sys.modules.get("render")
sys.modules["render"] = render  # JT-E1r's runner reads its displays through `import render`
try:
    base = _load("jt_e1s_base_runner", HERE.parent / "jt-e1r/runner.py")
finally:
    if _saved is None:
        del sys.modules["render"]
    else:
        sys.modules["render"] = _saved
base.render, base.HERE, base.RAW = render, HERE, HERE / "raw"
FROZEN = ("jt-e1s/PRE-REGISTRATION.md", "jt-e1s/items.tsv", "jt-e1s/render.py", "jt-e1s/runner.py",
          "jt-e1r/render.py", "jt-e1r/runner.py")


def committed():
    for name in FROZEN:
        saved = subprocess.run(["git", "show", f"HEAD:docs/judgment-terms/{name}"],
                               capture_output=True, check=True).stdout
        if saved != (HERE.parent / name).read_bytes():
            raise RuntimeError(f"commit {name} before reader calls")


base.committed = committed
PROMPT, prompt, score, record_score, results, run = (
    base.PROMPT, base.prompt, base.score, base.record_score, base.results, base.run)


if __name__ == "__main__":
    if sys.argv[1:] == ["--run"]:
        run()
    elif sys.argv[1:] == ["--score"]:
        print(json.dumps(results(), indent=2))
    else:
        raise SystemExit("usage: runner.py --run|--score")
