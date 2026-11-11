"""Temporary probe (soft-cf-text-1 step 1): log every soft CONFLICT-FREE status line in any answer, nested included."""
import json, os
from ve.backends import lean_service as LS
LOG = "/tmp/scprobe/log-%d.jsonl" % os.getpid()
HEAD = "CONFLICT-FREE among rules on the same act, conditional on "
def found(x, path=()):
    if isinstance(x, dict):
        t = x.get("status_text")
        if isinstance(t, str) and t.startswith(HEAD) and "coherent situation exhibited" in t:
            yield path, x
        for k, v in x.items():
            yield from found(v, path + (k,))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from found(v, path + (i,))
def wrap(cls):
    orig = cls.run_bound
    def run(self, mode, cases, *, timeout=None):
        rows = orig(self, mode, cases, timeout=timeout)
        try:
            for c, r in zip(cases, rows):
                for path, hit in found(r):
                    with open(LOG, "a") as f:
                        f.write(json.dumps({"test": os.environ.get("PYTEST_CURRENT_TEST", "?"), "mode": mode,
                                            "path": list(path), "case": c, "row": hit}) + "\n")
        except Exception:
            pass
        return rows
    cls.run_bound = run
for name in dir(LS):
    obj = getattr(LS, name)
    if isinstance(obj, type) and "run_bound" in obj.__dict__ and obj.__module__ == LS.__name__:
        wrap(obj)
