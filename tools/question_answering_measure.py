"""Measure Q2's non-model service and CLI costs on recorded U3 and A1 inputs.

The raw service requests bypass the relay cache, so the CPU delta is Lean's process
time for the named mode.  The CLI measurement includes evidence generation.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/spec/question-answering-q2/evidence/measurements.json"
sys.path.insert(0, str(ROOT / "tests"))
_spec = importlib.util.spec_from_file_location("ask_fixtures", ROOT / "tools/ask_fixtures.py")
AF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AF)


def service_case(ident):
    from ve.ask import _identities, environment
    from ve.backends import english_lean
    from ve.english import EnglishVocabulary
    from ve.document import load_document
    entry = AF.load(ident)
    raw = (ROOT / entry["path"]).read_bytes()
    doc = load_document(ROOT / entry["path"])
    lexicon, _ = _identities(raw, entry["question"], doc)
    ask_case = {"id": "ask", "document": raw.decode(), "question": entry["question"],
                "lexicon": lexicon, "case": entry["case"], "names": entry["names"]}
    env = environment(raw)
    question_case = english_lean.request(env, entry["question"],
                                         EnglishVocabulary(env, _defer_overlay_refusals=True), {})
    question_case.update(id="english.question", question=entry["question"])
    return entry, question_case, ask_case


def measure_service(service, mode, case):
    wire = json.dumps([case], ensure_ascii=False, separators=(",", ":"))
    # Start the persistent service and register any one-time work before timing.
    service.exchange(mode, wire, 1)
    before = service.cpu_seconds()
    start = time.monotonic()
    _, response = service.exchange(mode, wire, 1)
    wall = time.monotonic() - start
    after = service.cpu_seconds()
    if response["status"] != "ok" or response["results"][0]["result"]["status"] != "ok":
        raise RuntimeError(f"{mode} did not answer: {response}")
    return {"cpu_s": None if before is None or after is None else round(after - before, 3),
            "wall_s": round(wall, 3)}


def measure_cli(entry):
    from subprocesses import HANG_TIMEOUT
    import tempfile
    env = {k: v for k, v in os.environ.items()
           if k in ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "PYTHONPATH", "PYTHONNOUSERSITE",
                    "PYTHONPYCACHEPREFIX") or k.startswith("VE_")}
    with tempfile.TemporaryDirectory(prefix="ve-ask-measure-") as directory:
        evidence = Path(directory) / "evidence.json"
        evidence.write_text(json.dumps(entry["case"]["evidence"]))
        start = time.monotonic()
        done = subprocess.run([sys.executable, "-m", "ve", "ask", str(ROOT / entry["path"]), entry["question"],
                               "--evidence", str(evidence)], cwd=ROOT, env=env, text=True,
                              capture_output=True, timeout=HANG_TIMEOUT)
    wall = time.monotonic() - start
    if done.returncode not in (0, 3) or done.stdout.splitlines() != entry["result"]["text"]:
        raise RuntimeError(f"ve ask {entry['id']}: {done.returncode}\n{done.stdout}\n{done.stderr}")
    return {"wall_s": round(wall, 3), "exit": done.returncode}


def main():
    from ve.backends.lean_service import LeanService
    cases = {ident: service_case(ident) for ident in ("U3", "A1")}
    out = {"method": "warm persistent ve_service; child CPU delta for second request; cold ve ask wall",
           "fixtures": {}}
    with LeanService(ROOT / "lean/.lake/build/bin/ve_service") as service:
        for ident, (entry, question, ask) in cases.items():
            out["fixtures"][ident] = {
                "english.question": measure_service(service, "english.question", question),
                "ask": measure_service(service, "ask", ask)}
            out["fixtures"][ident]["ve ask"] = measure_cli(entry)
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
