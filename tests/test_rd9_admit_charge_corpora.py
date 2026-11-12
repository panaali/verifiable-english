"""sc-admit-cpu, DRI amendment 2026-11-11 (reviews/dri-decisions-20261111-adv1118.md item 2): admission's per-reading
charge (`sdAdmitWork N ≤ maxSdAdmitWork`, SoftWire.lean) refuses only the documents named in
docs/rd-9/sc-admit-cpu/DELTA.md (NSDheavy and heavyIn, each with its own `#guard`). The three keyed corpora run live
and give their committed answers with no answer refused by the charge, and every soft-default readings document under
data/ and usecases/ is admitted. The main-vs-HEAD answer list is docs/rd-9/sc-admit-cpu/cpu.md."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests import lean_routes
from tests.subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]


def _answers():
    spec = importlib.util.spec_from_file_location("sc_admit_corpora", ROOT / "docs/rd-9/sc-admit-cpu/corpora_answers.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ANSWERS = _answers()
# Each corpus's base answers (its `run`, without the mutants), in a process of its own: the corpora import siblings by
# the same bare names. The child prints the rows `compare` scores and the refusals in the whole result.
BASE = """
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("run", f"usecases/{sys.argv[1]}/run.py")
run = importlib.util.module_from_spec(spec); sys.modules["run"] = run; spec.loader.exec_module(run)
result = run.run()
rows = result.get("comparison") or run.compare(result)
print(json.dumps({"rows": {r["id"]: r["ve"] for r in rows}, "refusals": json.dumps(result).count(sys.argv[2])}))
"""
# The probe's admission as measured on main and HEAD (docs/rd-9/sc-admit-cpu/cpu.md, output-corpora.txt).
PROBE = "usecases/claude-constitution-pilot/run-20261104T0716Z/probe-translation.probe.md"


@pytest.fixture(scope="module")
def service():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")


def _python(argv):
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    proc = subprocess.run([sys.executable, *argv], cwd=ROOT, env=env, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)
    assert proc.returncode == 0, proc.stderr[-2000:]
    return json.loads(proc.stdout.strip().splitlines()[-1]), proc.stdout + proc.stderr


@pytest.mark.parametrize("corpus", ANSWERS.CORPORA)
def test_keyed_corpus_answers_as_committed_and_none_refused_by_the_charge(service, corpus):
    live, text = _python(["-c", BASE, corpus, ANSWERS.REFUSAL])
    assert live["refusals"] == 0 and ANSWERS.REFUSAL not in text
    committed = {row["id"]: row["ve"] for row in
                 json.loads((ROOT / "usecases" / corpus / "results.json").read_text())["comparison"]}
    assert live["rows"], corpus
    assert live["rows"] == {k: committed[k] for k in live["rows"]}


def test_every_soft_default_document_under_data_and_usecases_is_admitted(service):
    documents = ANSWERS.soft_documents(ROOT)
    assert PROBE in documents
    for doc in documents:
        answer, text = _python(["-c", ANSWERS.LOAD, doc])
        assert answer["admitted"] is True and ANSWERS.REFUSAL not in text, doc
        if doc == PROBE:
            assert (answer["route"], answer["choices"]) == ("enumerated", 16)
