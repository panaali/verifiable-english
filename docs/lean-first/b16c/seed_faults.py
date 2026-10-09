"""Plant each 16c boundary fault, prove its named test fails, then restore the source.

A fault in a Lean source is built into `ve_service`, whose hash is pinned in `lean/checkers.lock` for the run
only (the service refuses an unlisted build); the source and the lock are restored and the service rebuilt.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
SWITCH = "tests/test_document_lean_switch.py::"
WRAPPER = "tests/test_lean_document_wrapper.py::"
CASES = [
    ("null treated as present", "ve/document.py",
     'has_content = authored.get("content") is not None',
     'has_content = "content" in authored',
     SWITCH + "test_null_content_is_absent_on_the_lean_path"),
    ("forged checked formula accepted", "ve/document.py",
     'require(same(unit["content"], authored["content"]["ast"]))',
     'pass  # seeded fault: ignore the authored AST',
     SWITCH + "test_identities_and_content_are_leans"),
    ("untyped checked formula", "ve/backends/lean_service_schema/document.json",
     '"content": {"$ref": "common.json#/$defs/generated_formula"}',
     '"content": true',
     SWITCH + "test_document_schema_types_every_unit_field[units/0/content=7]"),
    # 16c review B1, B3.
    ("narrowings typed as tokens", "ve/backends/lean_service_schema/document.json",
     '"narrowings": {"items": {"$ref": "#/$defs/narrowing"}, "type": "array"}',
     '"narrowings": {"items": {"$ref": "common.json#/$defs/token"}, "type": "array"}',
     SWITCH + "test_a_narrowed_document_is_decided_by_lean"),
    ("untyped meaning", "ve/backends/lean_service_schema/document.json",
     '"meaning": {"$ref": "#/$defs/meaning"}',
     '"meaning": true',
     SWITCH + 'test_document_schema_types_every_unit_field[units/0/meaning="unspecified"]'),
    # 16c review B2.
    ("Python reads an unpaired surrogate", "ve/document.py",
     '        json.dumps(meta, ensure_ascii=False).encode("utf-8")\n',
     '        pass\n',
     WRAPPER + "test_json_unpaired_surrogate_is_the_boundary_diagnostic_in_both[high]"),
    ("Lean decides every null", "lean/VE/Service/Document.lean",
     'if let some key := strayNull j then',
     'if let some key := (none : Option String) then',
     WRAPPER + "test_null_and_number_forms_agree_with_python_or_fail_closed[reading-sets]"),
    # The lexer itself is pinned by `#guard`s in the module (a fault there fails the build); these skip it.
    ("Lean decides every number form", "lean/VE/Service/Document.lean",
     'match foreignLexeme (front.length + 1) false front.toList with',
     'match (none : Option Foreign) with',
     WRAPPER + "test_null_and_number_forms_agree_with_python_or_fail_closed[plain]"),
    ("Lean refuses a null status", "lean/VE/Service/Document.lean",
     '    | .ok .null => pure none\n    | .ok _ => throw "invalid unit status"',
     '    | .ok _ => throw "invalid unit status"',
     WRAPPER + "test_null_the_mode_reads_as_absent_is_decided"),
    ("Lean reads an unpaired surrogate", "lean/VE/Service/Document.lean",
     '| some .surrogate => throw loneSurrogate',
     '| some .surrogate => throw (unavailable "an unpaired surrogate")',
     WRAPPER + "test_json_unpaired_surrogate_is_the_boundary_diagnostic_in_both[high]"),
]
LOCK = ROOT / "lean/checkers.lock"
SERVICE = ROOT / "lean/.lake/build/bin/ve_service"


def build_service() -> None:
    run = subprocess.run(["lake", "build", "ve_service"], cwd=ROOT / "lean", capture_output=True, text=True)
    if run.returncode != 0:
        raise RuntimeError(f"lake build ve_service failed: {(run.stdout + run.stderr)[-2000:]}")


def pin_service() -> None:
    lock = json.loads(LOCK.read_text())
    digest = hashlib.sha256(SERVICE.read_bytes()).hexdigest()
    if digest not in lock["ve_service"]:
        lock["ve_service"].append(digest)
        LOCK.write_text(json.dumps(lock, indent=2) + "\n")


def main() -> None:
    records = []
    for name, relative, before, after, test in CASES:
        path = ROOT / relative
        original = path.read_text()
        lock = LOCK.read_text()
        lean = relative.endswith(".lean")
        if original.count(before) != 1:
            raise RuntimeError(f"expected one mutation site for {name}")
        try:
            path.write_text(original.replace(before, after, 1))
            if lean:
                build_service()
                pin_service()
            run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:xdist", test], cwd=ROOT,
                                 capture_output=True, text=True, check=False)
        finally:
            path.write_text(original)
            LOCK.write_text(lock)
            if lean:
                build_service()
        output = run.stdout + run.stderr
        if run.returncode == 0 or "1 failed" not in output:
            raise RuntimeError(f"{name}: expected a test failure, got {run.returncode}: {output[-1000:]}")
        records.append({"bug": name, "file": relative, "test": test,
                        "exit_code": run.returncode, "failure_excerpt": output[-1200:]})
    evidence = ROOT / "docs/lean-first/b16c/evidence/mutants.json"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(json.dumps(records, indent=2) + "\n")
    print(f"{len(records)} seeded faults caught")


if __name__ == "__main__":
    main()
