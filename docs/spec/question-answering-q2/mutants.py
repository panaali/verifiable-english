"""Seeded bugs of question answering Q2 (build checklist 13): each plants one bug in a file the batch changed, shows
that the named test (or the Lean build, where a proof catches it) fails, and restores the file. Lean mutants rebuild
`ve_service` and admit its build in `lean/checkers.lock` for the run; the lock and the binary are restored at the
end. Writes `evidence/mutants.json`.

Run from the repository root, with `lake` on PATH: `uv run python docs/spec/question-answering-q2/mutants.py
[ID ...]` (with ids, only those mutants are rerun and the others' saved results kept).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import nested_pytest  # noqa: E402
HERE = Path(__file__).resolve().parent
LOCK = ROOT / "lean/checkers.lock"
SERVICE = ROOT / "lean/.lake/build/bin/ve_service"

MUTANTS = [
    {"id": "lean-lead-yes-without-model", "language": "Lean", "file": "lean/VE/Ask/Basic.lean",
     "behaviour": "answer soundness: yes needs a model of the premises (lead_sound)",
     "old": "else if r.query == .proved then (if r.premise == .model then .yes else .unknown)",
     "new": "else if r.query == .proved then .yes",
     "test": ["lake", "build", "VE.Ask.Sound"], "build": False},
    {"id": "lean-cited-reversed", "language": "Lean", "file": "lean/VE/Ask/Run.lean",
     "behaviour": "citation exactness, in segment order: a row cites its sources in the certificate's order",
     "old": '("cited", Json.arr ((v.key r).2.map sourceJson).toArray)',
     "new": '("cited", Json.arr ((v.key r).2.reverse.map sourceJson).toArray)',
     "test": ["tests/test_ask_fixtures.py::test_a_recorded_answer_replays_and_says_what_the_spec_says[G1]"],
     "build": True},
    {"id": "lean-gaps-dropped", "language": "Lean", "file": "lean/VE/Ask/Run.lean",
     "behaviour": "not settled: a refuted row names the gaps its countermodel turns on, for the split",
     "old": '("gaps", VE.Readings.Wire.gapsJson (if r.query == .refuted then v.gaps r.choice else []))',
     "new": '("gaps", VE.Readings.Wire.gapsJson ([] : List (String × List String × Bool)))',
     "test": ["tests/test_ask_fixtures.py::test_a_recorded_answer_replays_and_says_what_the_spec_says[U3]"],
     "build": True},
    {"id": "lean-evidence-unbound", "language": "Lean", "file": "lean/VE/Ask/Wire.lean",
     "behaviour": "request binding: every evidence entry names a compatible choice, once",
     "old": "unless evidenceBound case (x.evs.map (·.1)) do",
     "new": "unless true do",
     "test": ["tests/test_ask_relay.py::test_lean_refuses_a_request_not_bound_to_its_document"],
     "build": True},
    {"id": "lean-environment-unbound", "language": "Lean", "file": "lean/VE/Ask/PlainWire.lean",
     "behaviour": "request binding: the plain case's environment is the document's",
     "old": 'unless decide (Same (case.getObjValD "environment") (sp.front.getObjValD "environment")) do',
     "new": "unless true do",
     "test": ["tests/test_ask_fixtures.py::test_a_case_of_another_document_is_not_this_documents"],
     "build": True},
    {"id": "python-choice-unbound", "language": "Python", "file": "ve/ask.py",
     "behaviour": "relay binding: a row's choice names the request's open sets, each once, in order",
     "old": '    _need([s for s, _ in choice] == list(sets), "a choice does not name every open set once, in order")\n',
     "new": "",
     "test": ["tests/test_ask_relay.py::test_every_id_rebound_is_refused"], "build": False},
    {"id": "python-text-unbound", "language": "Python", "file": "ve/ask.py",
     "behaviour": "relay binding: the answer's text is its lines' text",
     "old": '    _need(result["text"] == [line["text"] for line in lines], "the text is not the lines\' text")\n',
     "new": "",
     "test": ["tests/test_ask_relay.py::test_every_id_rebound_is_refused"], "build": False},
    {"id": "python-statement-text-ignored", "language": "Python", "file": "tools/question_statements.py",
     "behaviour": "statement check: a Q2 statement whose text differs from the approved text fails",
     "old": "failed = bool(missing or absent or unlisted or differ)",
     "new": "failed = bool(missing or absent or unlisted)",
     "test": ["tests/test_question_statements.py::test_a_changed_statement_or_definition_fails"], "build": False},
]


def build_service():
    done = subprocess.run(["lake", "build", "ve_service"], cwd=ROOT / "lean", capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit(done.stdout[-3000:] + done.stderr[-3000:])
    return hashlib.sha256(SERVICE.read_bytes()).hexdigest()


def admit(build, lock_text):
    data = json.loads(lock_text)
    data["ve_service"] = sorted(set(data["ve_service"]) | {build})
    LOCK.write_text(json.dumps(data, indent=2) + "\n")


def main() -> int:
    only = set(sys.argv[1:])
    saved = HERE / "evidence/mutants.json"
    results = [r for r in json.loads(saved.read_text())["mutants"] if r["id"] not in only] if only else []
    lock_text = LOCK.read_text()
    try:
        for m in MUTANTS:
            if only and m["id"] not in only:
                continue
            path = ROOT / m["file"]
            original = path.read_text()
            assert original.count(m["old"]) == 1, (m["id"], "the planted text is not found once")
            path.write_text(original.replace(m["old"], m["new"], 1))
            try:
                if m["build"]:
                    admit(build_service(), lock_text)
                if m["test"][0] == "lake":
                    done = subprocess.run(m["test"], cwd=ROOT / "lean", capture_output=True, text=True)
                else:
                    done = subprocess.run(nested_pytest.command(["-q", "-x", *m["test"]]), cwd=ROOT,
                                          env=nested_pytest.environment(os.environ), capture_output=True, text=True)
                caught = done.returncode != 0
                tail = (done.stdout + done.stderr).strip().splitlines()
                failing = [line for line in tail if line.startswith(("FAILED", "error:")) or "error:" in line][:3]
            finally:
                path.write_text(original)
            results.append({k: m[k] for k in ("id", "language", "file", "behaviour", "test")} |
                           {"caught": caught, "evidence": failing or tail[-2:]})
            print(f"{m['id']}: {'caught' if caught else 'NOT CAUGHT'}", flush=True)
    finally:
        LOCK.write_text(lock_text)
        restored = build_service()
        if restored not in json.loads(lock_text)["ve_service"]:
            print(f"the restored build {restored} is not in the lock; rebuild and admit it", file=sys.stderr)
    results.sort(key=lambda r: [m["id"] for m in MUTANTS].index(r["id"]))
    out = {"mutants": results, "all_caught": all(r["caught"] for r in results)}
    (HERE / "evidence").mkdir(exist_ok=True)
    (HERE / "evidence/mutants.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    return 0 if out["all_caught"] else 1


if __name__ == "__main__":
    sys.exit(main())
