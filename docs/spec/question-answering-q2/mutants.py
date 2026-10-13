"""Seeded bugs of question answering Q2 (build checklist 13): each plants one bug in a file the batch changed, shows
that the named test (or the Lean build, where a proof catches it) fails, and restores the file. Lean mutants rebuild
`ve_service` and admit its build in `lean/checkers.lock` for the run; the lock and the binary are restored at the
end. A mutant of a response shape (`schemas`) re-renders the client's schemas from it, and again after the restore.
Writes `evidence/mutants.json`.

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
    {"id": "python-quote-unbound", "language": "Python", "file": "ve/ask.py",
     "behaviour": "relay binding: a line's quote is text of the unit it names",
     "old": '            _need(line["quote"][1] and line["quote"][1] in units[line["quote"][0]],\n'
            '                  "a line\'s quote is not from its unit\'s text")\n',
     "new": "",
     "test": ["tests/test_ask_relay.py::test_every_id_rebound_is_refused"], "build": False},
    {"id": "python-gap-unbound", "language": "Python", "file": "ve/ask.py",
     "behaviour": "relay binding: a gap names elements of the models the request's evidence holds",
     "old": '            _need(all(e in request["_elements"] for e in gap[1]),\n',
     "new": '            _need(True,\n',
     "test": ["tests/test_ask_relay.py::test_every_id_rebound_is_refused"], "build": False},
    {"id": "python-definition-unbound", "language": "Python", "file": "ve/ask.py",
     "behaviour": "relay binding: a cited definition belongs to the request's document",
     "old": '        _need(source["name"] in request["_definitions"],\n',
     "new": '        _need(True,\n',
     "test": ["tests/test_ask_relay.py::test_every_id_rebound_is_refused"], "build": False},
    {"id": "python-row-omitted", "language": "Python", "file": "ve/ask.py",
     "behaviour": "relay binding: a readings answer has one row for every compatible choice",
     "old": '    _need(set(choices) == {json.dumps(choice) for choice in expected_choices} and\n'
            '          len(choices) == len(expected_choices), "the rows do not cover exactly the request\'s choices")\n',
     "new": '',
     "test": ["tests/test_ask_relay.py::test_every_id_rebound_is_refused"], "build": False},
    {"id": "python-gate-transport-only", "language": "Python", "file": "tools/relay_mutation_gate.py",
     "behaviour": "relay gate: ask's mutants are read as ve ask reads them, not by the transport alone",
     "old": 'SERVICE_READERS = {"ask": _ask_reader}',
     "new": "SERVICE_READERS = {}",
     "test": ["tests/test_relay_mutation_gate.py::test_ask_is_read_as_ve_ask_reads_it"], "build": False},
    {"id": "lean-row-id-untyped", "language": "Lean", "file": "lean/ResponseShape/Schemas/Ask.lean",
     "behaviour": "response schema: an answer row's id is the case's id",
     "old": '("id", n [str, .equals "/id"])',
     "new": '("id", .bool true)',
     "test": ["tests/test_ask_relay.py::test_the_rows_id_is_typed_and_bound_to_the_case"], "build": False,
     "schemas": True},
    {"id": "python-statement-text-ignored", "language": "Python", "file": "tools/question_statements.py",
     "behaviour": "statement check: a Q2 statement whose text differs from the approved text fails",
     "old": "failed = bool(missing or absent or unlisted or differ)",
     "new": "failed = bool(missing or absent or unlisted)",
     "test": ["tests/test_question_statements.py::test_a_changed_statement_or_definition_fails"], "build": False},
    # The fixes of the qa-q2 review (F2 to F4).
    {"id": "lean-words-article-by-letter", "language": "Lean", "file": "lean/VE/Words/Situation.lean",
     "behaviour": "one owner of situation wording (F2): an element line's article is chosen by sound, as before Q2.4",
     "old": 'if ["uni", "use", "usu", "uti", "eu", "one", "once"].any w.startsWith then "a"',
     "new": 'if false then "a"',
     "test": ["tests/test_words.py::test_lean_words_as_the_pre_q24_producers_did"], "build": True},
    {"id": "lean-words-negation-must-not", "language": "Lean", "file": "lean/VE/Words/Situation.lean",
     "behaviour": "one owner of point wording (F2): an obligation's negation is `need not`, a permission's `must not`",
     "old": 'else (if role == .permission then "must not" else "need not")',
     "new": 'else "must not"',
     "test": ["tests/test_words.py::test_lean_words_as_the_pre_q24_producers_did"], "build": True},
    {"id": "python-words-count-unbound", "language": "Python", "file": "ve/words.py",
     "behaviour": "words relay binding (F2): one line per requested item",
     "old": '    if type(lines) is not list or len(lines) != len(case["items"]):',
     "new": '    if type(lines) is not list:',
     "test": ["tests/test_words.py::test_an_answer_not_bound_to_its_request_is_refused"], "build": False},
    {"id": "python-lint-element-line", "language": "Python", "file": "tools/relay_lint.py",
     "behaviour": "relay lint (F2): an element line built from parts outside Lean is a finding",
     "old": '                and isinstance(b, ast.FormattedValue) for a, b in zip(node.values, node.values[1:])):',
     "new": '                and False for a, b in zip(node.values, node.values[1:])):',
     "test": ["tests/test_words.py::test_the_lint_refuses_a_producer_that_comes_back"], "build": False},
    {"id": "python-point-search-own-fillings", "language": "Python", "file": "ve/filling_search.py",
     "behaviour": "one flip search (F3): the point search's fillings are the shared split's",
     "old": "    candidate = split(start, gaps) if gaps else None",
     "new": '    candidate = {"true": start, "false": start} if gaps else None',
     "test": ["tests/test_filling_search.py::test_point_search_sends_the_shared_split_to_lean"], "build": False},
]


def build_service():
    done = subprocess.run(["lake", "build", "ve_service"], cwd=ROOT / "lean", capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit(done.stdout[-3000:] + done.stderr[-3000:])
    return hashlib.sha256(SERVICE.read_bytes()).hexdigest()


def render_schemas():
    """Rebuild the decoder that renders the response schemas and rewrite them from the (planted) Lean shapes."""
    for argv, cwd in ((["lake", "build", "ve_response_decode"], ROOT / "lean"),
                      ([sys.executable, "tools/response_schemas.py", "--write"], ROOT)):
        done = subprocess.run(argv, cwd=cwd, capture_output=True, text=True)
        if done.returncode != 0:
            raise SystemExit(done.stdout[-3000:] + done.stderr[-3000:])


def admit(build, lock_text):
    data = json.loads(lock_text)
    data["ve_service"] = sorted(set(data["ve_service"]) | {build})
    LOCK.write_text(json.dumps(data, indent=2) + "\n")


def main() -> int:
    only = set(sys.argv[1:])
    saved = HERE / "evidence/mutants.json"
    results = [r for r in json.loads(saved.read_text())["mutants"] if r["id"] not in only] if only else []
    order = [m["id"] for m in MUTANTS]

    def save():
        """Write the results so far (each mutant's result is kept even if a later one is stopped)."""
        results.sort(key=lambda r: order.index(r["id"]))
        out = {"mutants": results, "all_caught": len(results) == len(MUTANTS) and all(r["caught"] for r in results)}
        saved.parent.mkdir(exist_ok=True)
        saved.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
        return out

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
                if m.get("schemas"):
                    render_schemas()
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
                if m.get("schemas"):
                    render_schemas()
            results.append({k: m[k] for k in ("id", "language", "file", "behaviour", "test")} |
                           {"caught": caught, "evidence": failing or tail[-2:]})
            save()
            print(f"{m['id']}: {'caught' if caught else 'NOT CAUGHT'}", flush=True)
    finally:
        LOCK.write_text(lock_text)
        restored = build_service()
        if restored not in json.loads(lock_text)["ve_service"]:
            print(f"the restored build {restored} is not in the lock; rebuild and admit it", file=sys.stderr)
    return 0 if save()["all_caught"] else 1


if __name__ == "__main__":
    sys.exit(main())
