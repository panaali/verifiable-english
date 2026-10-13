#!/usr/bin/env python3
"""AR-2's seeded bugs, written to docs/arch/AR-2/evidence/mutants.json.

    python3 docs/arch/AR-2/mutants.py

Plants each bug below in the file it names (one per behaviour the batch claims), runs the test that must catch it,
restores the file byte for byte, and records whether the test failed. A bug whose `from` text is not in its file
exactly once is an error, never a pass. Batch evidence (D4): not a test of the suite.
"""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = Path(__file__).resolve().parent / "evidence/mutants.json"

MUTANTS = [
    ("F1", "lean/VE/Route/frozen.py", "the frozen list holds the files with K declarations",
     'kernel = {module for module, classes in json.loads(table)["modules"].items() if classes.get("K")}',
     "kernel = set()",
     "tests/test_frozen_sources.py::test_the_list_is_the_k_files_and_the_core_decoders"),
    ("F2", "lean/VE/Route/frozen.py", "an unhashed edit of a frozen file fails frozen.py",
     "elif hashlib.sha256(blob).hexdigest() != listed[name]:",
     "elif False:",
     "tests/test_frozen_sources.py::test_an_unhashed_edit_of_a_k_file_fails"),
    ("F3", "lean/VE/Route/frozen.py", "a listed file that is neither K nor a decoder is refused",
     "for name in sorted(listed.keys() - wanted):",
     "for name in []:",
     "tests/test_frozen_sources.py::test_a_new_k_module_must_be_listed_and_a_listed_file_must_be_frozen"),
    ("H1", "tools/hooks/precommit.py", "the hook re-checks the whole list when the trust-class table is staged",
     "whole = any(path in index.changed for path in (INVENTORY, FROZEN_SCRIPT, TRUST_TABLE))",
     "whole = any(path in index.changed for path in (INVENTORY, FROZEN_SCRIPT))",
     "tests/test_precommit_hook.py::test_frozen_guard_rejects_an_unlisted_k_module_bad_inventory_and_main"),
    ("H2", "tools/hooks/precommit.py", "the hook refuses an unhashed edit of a frozen file",
     "only=None if whole else staged)",
     "only=set())",
     "tests/test_precommit_hook.py::test_frozen_file_change_requires_an_inventory_update"),
    ("T1", "tools/trust_changes.py", "a body-only edit of a D[V] file is in the changed-files report",
     "return (sorted(key for key, blob in now.items() if before.get(key) != blob),",
     "return (sorted(key for key, blob in now.items() if key not in before),",
     "tests/test_frozen_sources.py::test_a_body_only_edit_of_a_dv_file_is_reported"),
    ("T2", "tools/trust_changes.py", "no report from a classification that does not validate",
     "    if problems:\n        print(\"FAIL: the changed files",
     "    if False:\n        print(\"FAIL: the changed files",
     "tests/test_frozen_sources.py::test_the_report_fails_closed"),
    ("Q1", "tools/question_lock.py", "an edit of a Question module needs no lock update",
     'return {"format": "ve.question-lock@2", "question_version": int(number)}',
     'return {"format": "ve.question-lock@2", "question_version": int(number), "files": {'
     'str(p.relative_to(ROOT)): __import__("hashlib").sha256(p.read_bytes()).hexdigest() '
     'for p in sorted((ROOT / "lean/VE/Question").glob("*.lean"))}}',
     "tests/test_frozen_sources.py::test_an_edit_of_a_question_module_needs_no_lock_update"),
    ("W1", "tools/wire_contract.py", "wire_contract --write touches no frozen-inventory line",
     "                target.write_text(source)\n",
     "                target.write_text(source)\n"
     "                (ROOT / \"lean/VE/Route/frozen-sources.sha256\").write_text(\"\")\n",
     "tests/test_wire_contract_lint.py::test_l13_write_after_a_revision_changes_only_generated_files"),
]


def run(test: str) -> tuple[bool, str]:
    done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", test], cwd=ROOT,
                          capture_output=True, text=True)
    lines = [line for line in done.stdout.splitlines() if line.strip()]
    return done.returncode != 0, lines[-1] if lines else f"exit {done.returncode}, no output"


def main() -> int:
    rows = []
    for ident, relative, behaviour, before, after, test in MUTANTS:
        path = ROOT / relative
        original = path.read_bytes()
        text = original.decode()
        if text.count(before) != 1:
            raise SystemExit(f"{ident}: the planted text occurs {text.count(before)} times in {relative}")
        clean, _ = run(test)
        if clean:
            raise SystemExit(f"{ident}: {test} fails before the bug is planted")
        try:
            path.write_text(text.replace(before, after))
            killed, summary = run(test)
        finally:
            path.write_bytes(original)
        rows.append({"id": ident, "language": "Python", "file": relative, "behaviour": behaviour,
                     "mutation": {"from": before, "to": after}, "test": test, "killed": killed,
                     "pytest_summary": summary})
        print(f"{ident} {'killed' if killed else 'SURVIVED'}: {relative} ({test})", flush=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(rows, indent=1) + "\n")
    return 0 if all(row["killed"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
