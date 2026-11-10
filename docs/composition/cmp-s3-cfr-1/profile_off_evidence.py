"""Digests of the rights mode's answers to the recorded rights route cases, on the build of the tree it runs in."""
import hashlib, json, subprocess, sys
from pathlib import Path
sys.path.insert(0, ".")
from tests.lean_service_corpus import recorded
from tests.subprocesses import HANG_TIMEOUT
from ve.backends.lean_service import LeanService, case_digest

def canonical(v): return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
cases = recorded("rights")
with LeanService(Path("lean/.lake/build/bin/ve_service").resolve(), timeout=HANG_TIMEOUT, allow_unlisted_build=True) as s:
    text = json.dumps(cases, ensure_ascii=False)
    _, response = s.exchange("rights", text, len(cases), timeout=HANG_TIMEOUT)
rows = [b["result"] for b in response["results"]]
out = {"commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
       "source": "tests/data/route-cases.jsonl rows named rights, run by the rights mode of that commit's ve_service",
       "cases": [case_digest(canonical(c)) for c in cases],
       "answers": [hashlib.sha256(canonical({k: v for k, v in r.items() if k != "id"}).encode()).hexdigest() for r in rows],
       "statuses": [r["status"] for r in rows]}
print("{\n" + ",\n".join(f" {json.dumps(k)}: {json.dumps(v, separators=(',', ':'))}" for k, v in out.items()) + "\n}")
