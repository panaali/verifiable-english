"""Temporarily plant each batch 16f fault, run the test meant to catch it, and save every result, caught or not.

    python docs/lean-first/b16f/seed_faults.py

A Lean fault is built into `ve_service` and pinned for the run; the source, the lock and the build are restored
after each fault. `evidence/mutants.json` keeps the file, the test, its exit code and a failure excerpt.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
LOCK = ROOT / "lean/checkers.lock"
SERVICE = ROOT / "lean/.lake/build/bin/ve_service"
TESTS = "tests/test_b16f_document.py"
LEAN = "lean/VE/Service/Document.lean"
CASES = [
    # Lean: the document mode's composition of the soft and norms routes, and its located diagnostics.
    ("a norm object outside the soft source accepted without the soft route's check", LEAN,
     "      let N ← (VE.SoftNorms.Wire.decodeSoftNorm se (wireJson 257 content)).mapError fun m =>",
     "      let N ← (VE.SoftNorms.Wire.decodeSoftNorm se (wireJson 257 (Json.mkObj [(\"norm\", "
     "value.setObjVal! \"predicate\" (Json.str \"share_required\"))]))).mapError fun m =>",
     "test_a_quoted_soft_norm_s_fault_keeps_the_retained_path"),
    ("quoted norms not checked by the norms route", LEAN,
     "    single.forM (VE.Norms.Admission.checkQuoted base)",
     "    let _ := single.length",
     "test_norm_faults_are_the_norms_route_s[quoted unregulated]"),
    ("a soft document's formulas read in its own environment instead of E''", LEAN,
     "  pure ⟨declared ++ VE.SoftNorms.decisionNames src.D, ← extendedEnv prime, ← softRules prime flat⟩",
     "  pure ⟨declared ++ VE.SoftNorms.decisionNames src.D, E, ← softRules prime flat⟩",
     "test_a_formula_over_a_decision_predicate_is_read_in_the_extended_environment"),
    ("a refused model decided when the set has two", LEAN,
     "  | [f] => if f.1.isEmpty then none else some f",
     "  | f :: _ => if f.1.isEmpty then none else some f",
     "test_two_refused_models_of_one_set_keep_the_retained_path"),
    ("the environment mode's fault taken before a soft source's check", LEAN,
     '  if ["soft-norms@0", "rights@0"].any listed.contains then none else',
     '  if ["rights@0"].any listed.contains then none else',
     "test_a_soft_or_rights_environment_keeps_its_route_s_order[unknown profile]"),
    ("a strict fence's syntax error left to the retained path", LEAN,
     "  else if message == strictRefused then locatedFence E doc",
     "  else if message == strictRefused then none",
     "test_a_strict_fence_s_syntax_error_has_the_parse_mode_s_span"),
    # Python: the binding of the answer's new fields.
    ("a model path not bound to a model member", "ve/document.py",
     "                else:\n                    break\n            else:\n                return True\n    return False",
     "                else:\n                    break\n            else:\n                return True\n    return True",
     "test_a_model_path_is_bound_to_a_member_of_a_model_of_the_document[/relations/absent]"),
    ("a fence span's line not bound", "ve/document.py",
     '        if (0 <= start <= end <= len(text) and line == text.count("\\n", 0, start) + 1',
     '        if (0 <= start <= end <= len(text)',
     "test_a_fence_span_is_bound_to_a_strict_fence_of_the_document[span1]"),
    ("a soft rule bound as a subset of the authored one", "ve/document.py",
     '    return same(answer.get("norm"), written)',
     '    return set(answer.get("norm", {})) <= set(written)',
     "test_the_copied_soft_content_mutants_the_transport_accepts_are_refused_by_the_binding[drop mode]"),
    ("a soft document's meaning ids bound to the document's environment", "ve/document.py",
     "            formula_env = soft_document.extended_env\n        if \"rights@0\" in env.profiles:",
     "            formula_env = env\n        if \"rights@0\" in env.profiles:",
     "test_the_layer_seeds_are_decided_by_lean_with_the_retained_public_outcome[soft-norms]"),
]


def build() -> None:
    env = {**os.environ, "PATH": f"{Path.home() / '.elan/bin'}:{os.environ.get('PATH', '')}"}
    built = subprocess.run(["lake", "build", "ve_service"], cwd=ROOT / "lean", capture_output=True, text=True,
                           check=False, env=env)
    if built.returncode:
        raise RuntimeError((built.stdout + built.stderr)[-1500:])


def main() -> None:
    records = []
    for bug, relative, before, after, test in CASES:
        source = ROOT / relative
        original = source.read_text()
        lock = LOCK.read_text()
        lean = relative.endswith(".lean")
        assert original.count(before) == 1, bug
        try:
            source.write_text(original.replace(before, after, 1))
            if lean:
                build()
                pinned = json.loads(LOCK.read_text())
                pinned["ve_service"] = sorted(set(pinned["ve_service"]) |
                                              {hashlib.sha256(SERVICE.read_bytes()).hexdigest()})
                LOCK.write_text(json.dumps(pinned, indent=2) + "\n")
            env = {**os.environ, "VE_NATIVE_PREBUILT": "1"}
            done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:xdist", "-p", "no:cacheprovider",
                                   f"{TESTS}::{test}"], cwd=ROOT, env=env, capture_output=True, text=True,
                                  check=False)
        finally:
            source.write_text(original)
            LOCK.write_text(lock)
            if lean:
                build()
        output = done.stdout + done.stderr
        caught = done.returncode == 1 and " failed" in output
        records.append({"bug": bug, "file": relative, "test": f"{TESTS}::{test}", "exit_code": done.returncode,
                        "caught": caught, "failure_excerpt": output[-1500:]})
        print(f"{bug}: {test} {'failed as expected' if caught else 'PASSED: the fault survived'}", flush=True)
    path = Path(__file__).resolve().parent / "evidence/mutants.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(records, indent=2) + "\n")


if __name__ == "__main__":
    main()
