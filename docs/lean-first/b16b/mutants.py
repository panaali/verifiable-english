"""Seeded faults for 16b: one per behaviour the switch claims. Each is applied alone, its test is run (it must
fail), and the source is restored; a Lean fault is built and its build pinned for the run, then the original source
is rebuilt and its hash checked against the one before. Writes `evidence/mutants.json`.

    python docs/lean-first/b16b/mutants.py
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import nested_pytest  # noqa: E402

HERE = Path(__file__).resolve().parent
SERVICE = ROOT / "lean/.lake/build/bin/ve_service"
LOCK = ROOT / "lean/checkers.lock"
TESTS = "tests/test_document_lean_switch.py"

MUTANTS = [
    ("rejection_falls_back", "Lean's rejection is final", "ve/document.py",
     "    if error is not None:\n        raise error\n    return row",
     "    if error is not None:\n        return None\n    return row",
     "test_lean_rejections_are_raised_verbatim"),
    ("service_failure_falls_back", "a service failure is never answered by Python", "ve/document.py",
     '    row, error = answer("document", {"id": "document", "document": text, "admit": admit})',
     '    try:\n        row, error = answer("document", {"id": "document", "document": text, "admit": admit})\n'
     '    except CheckerUnavailable:\n        return None',
     "test_a_service_failure_is_never_answered_by_python"),
    ("unbound_answer", "the answer is bound to the request", "ve/document.py",
     "    require(same(coverage, expected))\n", "",
     "test_answers_not_bound_to_the_request_are_unavailable"),
    ("python_coverage", "coverage is Lean's", "ve/document.py",
     '    if "lean" in doc:\n        return deepcopy(doc["lean"]["coverage"])\n', "",
     "test_coverage_and_statuses_are_leans"),
    ("python_document_id", "identities are Lean's", "ve/document.py",
     '"document_id": row["document_id"], "directory"', '"document_id": _document_id(meta, source, {}), "directory"',
     "test_identities_and_content_are_leans"),
    ("load_admits", "load_document does not admit the graph", "ve/document.py",
     "    return _load(Path(path), admit=False)", "    return _load(Path(path), admit=True)",
     "test_load_does_not_admit_the_graph_and_check_does"),
    ("admission_disagreement_kept", "a route rejecting what Lean admitted is unavailable", "ve/document.py",
     "            except VEError as exc:\n                raise CheckerUnavailable(",
     "            except KeyError as exc:\n                raise CheckerUnavailable(",
     "test_the_admission_route_rejecting_what_lean_admitted_is_unavailable"),
    ("lean_senses_guard_removed", "a senses document takes the retained path (Lean)", "lean/VE/Service/Document.lean",
     '  if (fm.getObjVal? "senses").isOk then\n', '  if false && (fm.getObjVal? "senses").isOk then\n',
     "test_undecided_answers_take_the_retained_path"),
    ("lean_admission_bypasses_route", "the graph is admitted through the route's own case (Lean)",
     "lean/VE/Service/Document.lean",
     '    | .none => VE.Route.Run.dispatch "admission" E.json E.checked.envelope\n'
     '        (Json.mkObj [("kind", .str "admission"), ("document", document)])',
     '    | .none => VE.Route.Run.runAdmit E.profiles E.json E.rv "admission" (Json.mkObj [("document", document)])',
     "test_definitions_graph_is_deferred_as_the_admission_route_defers_it"),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> None:
    env = {**os.environ, "PATH": f"{Path.home()}/.elan/bin:{os.environ['PATH']}"}
    subprocess.run(["lake", "build", "ve_service"], cwd=ROOT / "lean", env=env, check=True, capture_output=True)


def main() -> int:
    rows = []
    original_build = sha(SERVICE)
    lock_text = LOCK.read_text()
    for name, behaviour, file, old, new, test in MUTANTS:
        path = ROOT / file
        source = path.read_text()
        assert source.count(old) == 1, name
        lean = file.endswith(".lean")
        try:
            path.write_text(source.replace(old, new))
            if lean:
                build()
                lock = json.loads(lock_text)
                lock["ve_service"].append(sha(SERVICE))
                LOCK.write_text(json.dumps(lock, indent=2) + "\n")
            done = subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", "-x", f"{TESTS}::{test}"]),
                                  cwd=ROOT, env=nested_pytest.environment(os.environ), capture_output=True,
                                  text=True)
        finally:
            path.write_text(source)
            LOCK.write_text(lock_text)
        failed = [line.split(" ")[1] for line in done.stdout.splitlines() if line.startswith("FAILED ")]
        rows.append({"mutant": name, "behaviour": behaviour, "file": file, "test": test,
                     "exit": done.returncode, "failed": failed, "caught": done.returncode == 1 and bool(failed)})
        print(name, done.returncode, failed, flush=True)
    build()
    restored = sha(SERVICE) == original_build
    (HERE / "evidence/mutants.json").write_text(json.dumps(
        {"mutants": rows, "service_build_restored": restored, "service_build": original_build}, indent=1) + "\n")
    return 0 if restored and all(row["caught"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
