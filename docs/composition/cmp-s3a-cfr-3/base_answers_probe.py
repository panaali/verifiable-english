"""The `clauses-elaborate` answers to K1 and tests/test_right_clauses.py's K_FIXTURES, on the build of the tree it runs
in (run at the base commit, before this item: base-answers.json). The negative test reads the saved answers."""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, ".")
from tests.subprocesses import HANG_TIMEOUT
from tests.test_right_clauses import K_FIXTURES, document, environment
from ve.backends.lean_service import LeanService

cases = [{"id": name, "environment": environment(), "document": doc}
         for name, doc in [("K1", document()), *((name, f[0]) for name, f in K_FIXTURES.items())]]
with LeanService(Path("lean/.lake/build/bin/ve_service").resolve(), timeout=HANG_TIMEOUT, allow_unlisted_build=True) as s:
    _, response = s.exchange("clauses-elaborate", json.dumps(cases, ensure_ascii=False), len(cases), timeout=HANG_TIMEOUT)
out = {"commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
       "source": "K1 and K_FIXTURES of tests/test_right_clauses.py, run by that commit's clauses-elaborate mode",
       "answers": {case["id"]: bound["result"] for case, bound in zip(cases, response["results"])}}
print(json.dumps(out, indent=1, sort_keys=True, ensure_ascii=False))
