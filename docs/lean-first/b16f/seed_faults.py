"""Temporarily plant each batch 16f fault, run the test meant to catch it, and save every result, caught or not.

The review fixes add faults for F1 (a soft document's parts pre-scan) and F2 (the senses route's composition, its
transport, binding and the recorders that write a pilot with its files); looprecheck1's F7 adds the binding of a
senses fence's content to the senses route's reading, and the relay gate's document reader.

    python docs/lean-first/b16f/seed_faults.py                    # every fault
    python docs/lean-first/b16f/seed_faults.py ve/document.py ...  # the faults in these files; the others' records kept

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
SENSES = "tests/test_b16f_senses_document.py"
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
     "test_a_norm_fault_keeps_the_retained_loader_s_diagnostic[quoted unregulated]"),
    ("a soft document's formulas read in its own environment instead of E''", LEAN,
     "  pure ⟨declared ++ VE.SoftNorms.decisionNames src.D, ← extendedEnv prime, ← softRules prime (partsPrefix raw)⟩",
     "  pure ⟨declared ++ VE.SoftNorms.decisionNames src.D, E, ← softRules prime (partsPrefix raw)⟩",
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
    # Lean, review F1: a soft document's parts pre-scan stops at the first fault, as Python's swallowed generator.
    ("a soft document's parts pre-scan raises its fault before the unit loop", LEAN,
     "  pure ⟨declared ++ VE.SoftNorms.decisionNames src.D, ← extendedEnv prime, ← softRules prime (partsPrefix raw)⟩",
     "  pure ⟨declared ++ VE.SoftNorms.decisionNames src.D, ← extendedEnv prime,\n"
     "    ← softRules prime (← raw.foldlM (fun acc u => do pure (acc ++ (← Loader.partsOf u))) [])⟩",
     "test_a_later_unit_s_structural_fault_comes_after_an_earlier_unit_s_fault[soft-norms]"),
    # Lean, review F2: the senses route's composition.
    ("a frozen envelope's meaning id under the profiles' identity version", LEAN,
     "  | some l => Standalone.legacyMeaningId l E.envId ast",
     "  | some _ => VE.Route.Wire.meaningId E.profiles E.envId ast",
     f"{SENSES}::test_a_valid_senses_document_is_decided_by_lean[a_front_matter_default-frozen]"),
    ("a senses refusal decided without its diagnostic", LEAN,
     '  unless reading.getObjValD "status" == .str "one" || reading.getObjValD "status" == .str "open" do',
     '  unless true do',
     f"{SENSES}::test_a_senses_refusal_with_its_diagnostic_keeps_the_retained_path[b_no_choice_made]"),
    ("pack texts of another count read", LEAN,
     "  unless texts.size == entries.size && texts.all (·.getStr?.toOption.isSome) do",
     "  unless texts.all (·.getStr?.toOption.isSome) do",
     f"{SENSES}::test_a_request_without_the_pack_texts_keeps_the_retained_path[two]"),
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
    # Python, review F2: the senses transport, binding and recorders.
    ("a senses document's pack texts not sent", "ve/document.py",
     '            case["packs"] = texts',
     '            pass',
     f"{SENSES}::test_a_valid_senses_document_is_decided_by_lean[d_parenthetical_switch-modern]"),
    ("a senses unit's meaning id bound to the document's environment", "ve/document.py",
     "        formula_env = env if senses is None else senses.environment\n",
     "        formula_env = env\n",
     f"{SENSES}::test_a_senses_unit_s_meaning_id_is_bound_to_the_projected_environment"),
    ("a fence's content optional outside a senses document", "ve/document.py",
     '    if "senses" in meta:\n        require(senses is not None)',
     '    if senses is not None:\n        require(senses is not None)',
     f"{SENSES}::test_a_fence_without_a_formula_may_have_no_content_but_others_must"),
    # Python, looprecheck1 F7: a senses fence's content bound to the reading Python holds, and the gate reads it so.
    ("a fence the senses route read may drop its content", "ve/document.py",
     '        has_content = (authored.get("id") in formulas if authored.get("id") in read\n'
     '                       else authored.get("content") is not None)',
     '        has_content = authored.get("content") is not None and not (\n'
     '            authored.get("id") in read and "content" not in unit)',
     f"{SENSES}::test_a_fence_the_route_read_keeps_its_formula[1-frozen]"),
    ("a fence's formula not compared with the senses route's reading", "ve/document.py",
     '            require("content" in unit and same(unit["content"], formulas[authored["id"]]))',
     '            require("content" in unit)',
     f"{SENSES}::test_a_fence_the_route_read_keeps_its_formula[0-modern]"),
    ("a preamble line's content not refused", "ve/document.py",
     '        has_content = (authored.get("id") in formulas if authored.get("id") in read\n'
     '                       else authored.get("content") is not None)\n'
     '        if has_content and authored.get("id") in read:',
     '        has_content = (("content" in unit or authored.get("id") in formulas) if authored.get("id") in read\n'
     '                       else authored.get("content") is not None)\n'
     '        if has_content and authored.get("id") in formulas:',
     f"{SENSES}::test_a_fence_the_route_read_to_no_formula_has_no_content"),
    ("the relay gate reads a document answer by its transport only", "tools/relay_mutation_gate.py",
     '        document._lean_document(raw, path, row, admitted=case.get("admit", False))',
     '        del row',
     "tests/test_relay_mutation_gate.py::test_document_is_read_as_ve_document_reads_it[content and identity]"),
    ("a pilot written without the files it names", "tools/lean_first_diff.py",
     "    companions = pilot_companions(root, name, text)\n",
     "    companions = {}\n",
     f"{SENSES}::test_a_pilot_is_written_with_the_files_it_names_beside_it"),
]


def build() -> None:
    env = {**os.environ, "PATH": f"{Path.home() / '.elan/bin'}:{os.environ.get('PATH', '')}"}
    built = subprocess.run(["lake", "build", "ve_service"], cwd=ROOT / "lean", capture_output=True, text=True,
                           check=False, env=env)
    if built.returncode:
        raise RuntimeError((built.stdout + built.stderr)[-1500:])


def main(files: list[str]) -> None:
    path = Path(__file__).resolve().parent / "evidence/mutants.json"
    kept = {r["bug"]: r for r in json.loads(path.read_text())} if files and path.exists() else {}
    records = []
    for bug, relative, before, after, test in CASES:
        if files and relative not in files:
            records.append(kept[bug])
            continue
        target = test if "::" in test else f"{TESTS}::{test}"
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
                                   target], cwd=ROOT, env=env, capture_output=True, text=True,
                                  check=False)
        finally:
            source.write_text(original)
            LOCK.write_text(lock)
            if lean:
                build()
        output = done.stdout + done.stderr
        caught = done.returncode == 1 and " failed" in output
        records.append({"bug": bug, "file": relative, "test": target, "exit_code": done.returncode,
                        "caught": caught, "failure_excerpt": output[-1500:]})
        print(f"{bug}: {test} {'failed as expected' if caught else 'PASSED: the fault survived'}", flush=True)
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(records, indent=2) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
