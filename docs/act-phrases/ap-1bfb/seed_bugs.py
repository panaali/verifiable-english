"""ap-1bfb's seeded bugs: each is planted in the worktree, the named test or the module's `#guard`s run, and the file is
restored from git. A Lean mutant is run by `lake build VE.WireContract.Hooks.Acts` (its `#guard`s); a Python one by
its pytest selection, on the service built from this item's clean Lean; the Rust one by the table test. A Lean mutant
whose check is a test on the service (`SERVICE`: review F2, a cost no `#guard` sees) rebuilds and pins `ve_service`,
runs the test, then restores `lean/checkers.lock` and rebuilds the service from the restored tree. Writes
`mutants.json` beside this file. A mutant is KILLED when its check fails; the record keeps the failing lines.

    uv run python docs/act-phrases/ap-1bfb/seed_bugs.py
"""

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tools import nested_pytest  # noqa: E402
HOOK = "lean/VE/WireContract/Hooks/Acts.lean"
NORMS = "lean/VE/WireContract/Hooks/Norms.lean"
REGISTRY = "ve/wire_contract/registry.py"
NORMS_PY = "ve/norms_contract.py"
ONCE = "tests/test_wire_contract_once.py"
PY = "conformance/acts_contract.py"
FAULTS = "conformance/wire_contract_faults_acts.py"
TEST = "tests/test_acts_contract.py"

LEAN = "lake build VE.WireContract.Hooks.Acts"
SERVICE = "service:"  # + a pytest node, run on `ve_service` built from the mutated tree

# (id, file, definition, bug, old, new, check): `check` is `LEAN` or a pytest node selection.
MUTANTS = [
    ("lean-norms-branch-removed", HOOK, "decoded", "the profile row's gate removed (F1 again)",
     '''  if listed.contains "acts@0" then
    let _ ← VE.Compose.gateOf VE.Compose.baseRows listed
''', "", LEAN),
    ("lean-typing-without-acts", HOOK, "decodeOf", "decoded without `acts := true`",
     "VE.Norms.Wire.decodeNormsEnvironment environment (acts := true) (joined := true)",
     "VE.Norms.Wire.decodeNormsEnvironment environment", LEAN),
    ("lean-typing-error-ignored", NORMS, "typingList", "the refused rule's member dropped",
     "    | some (.error e) => [typingMember e]\n", "    | some (.error _) => [.ok]\n", LEAN),
    ("lean-typing-first-rule-only", NORMS, "tableAt", "every item typed as the first rule",
     "  ((itemIndex items 0).bind (table[·]?)).getD .ok", "  (table[0]?).getD .ok", LEAN),
    # review F1: the frames members only when the decoder refuses there first
    ("lean-frames-first-refusal", HOOK, "framesRefusal", "an earlier refusal read as the frames' (F1 again)",
     "  | some j, some k => refusedWith e (decoded j) && (decoded k).isOk", "  | some j, some _ => refusedWith e (decoded j)",
     LEAN),
    ("lean-alone-fixed-emptied", HOOK, "alone", "the block's `fixed` emptied, as Python's oracle did (F1 again)",
     '      ("acts", if frames then .obj kvs else .obj ((kvs.erase "frames").erase "adverbs"))]))',
     '      ("acts", if frames then .obj (kvs.insert "fixed" (Json.arr #[])) else Json.mkObj [("fixed", Json.arr #[])])]))',
     LEAN),
    # review F2: one decode and one typing pass per run
    ("lean-hooks-per-rule", HOOK, "hooksFor", "the run's hooks decode and type at every rule (F2 again)",
     '  ⟨Hooks.Norms.predicate, Hooks.Norms.onInput j (fun\n'
     '    | "acts_environment" => some fun _ => environmentBy (environmentOf j) fun _ => ne.get\n'
     '    | "rule_typing" => some (Hooks.Norms.tableAt table.get)\n'
     '    | _ => none) classifier, Hooks.Norms.view⟩',
     '  let _ := (ne, table)\n  hooks',
     SERVICE + f"{ONCE}::test_rule_typing_reads_the_environment_and_each_rule_once_per_run"),
    ("py-once-not-kept", REGISTRY, "once", "every read evaluated again (F2 again)",
     "    if memo is None:\n        return compute(root)", "    if True:\n        return compute(root)", ONCE),
    ("py-typing-per-rule", NORMS_PY, "rule_typing", "a typing pass from the first rule at every rule",
     '    return once("rule_typing", root, _Typing).at(int(items[0][-1]))',
     '    return _Typing(root).at(int(items[0][-1]))',
     f"{ONCE}::test_a_typing_fault_at_a_late_rule_is_found_with_each_rule_typed_once"),
    ("py-environment-per-read", NORMS_PY, "decoded_environment", "the environment decoded at each read",
     '    return once("environment", root, lambda r: Environment(r["environment"]))',
     '    return Environment(root["environment"])',
     f"{ONCE}::test_rule_typing_reads_the_environment_and_each_rule_once_per_run"),
    ("py-soft-declarations-per-rule", "conformance/softnorms_contract.py", "rule_typing",
     "soft-norms@0's declarations decoded at every rule",
     '    context = once("declarations", root, lambda r: soft._declarations(_environment(r), False))',
     '    context = soft._declarations(_environment(root), False)',
     f"{ONCE}::test_soft_rule_typing_reads_the_declarations_once_per_run"),
    ("lean-block-level", HOOK, "blockOf", "the block read one level too high",
     'def blockOf (environment : Json) : Json := (environment.getObjValD "vocabulary").getObjValD "acts"',
     'def blockOf (environment : Json) : Json := environment.getObjValD "acts"', LEAN),
    ("lean-frames-members-swapped", HOOK, "member", "1.1e and 1.1f swapped",
     '''.fail (if e.startsWith "ResourceLimit:" then "1.1e" else "1.1f") (message e)''',
     '''.fail (if e.startsWith "ResourceLimit:" then "1.1f" else "1.1e") (message e)''', LEAN),
    ("lean-classifier-norms-typing", HOOK, "classifier", "4.7 left to `Hooks.Norms`' typing environment",
     '  | "rule_typing", root, items =>\n'
     '    Hooks.Norms.tableAt (Hooks.Norms.typingTableOver root (typingEnvironment (decodeOf (environmentOf root)))) items\n',
     "", LEAN),
    ("lean-hooks-no-predicates", HOOK, "hooks", "the included hooks hold everywhere",
     "def hooks : Hooks := ⟨Hooks.Norms.predicate, classifier, Hooks.Norms.view⟩",
     "def hooks : Hooks := ⟨fun _ _ _ => .ok, classifier, Hooks.Norms.view⟩", LEAN),
    ("lean-registered-own-only", HOOK, "registered", "the included hook names unregistered",
     'def registered : List String := "acts_environment" :: Hooks.Norms.registered',
     'def registered : List String := ["acts_environment"]', LEAN),
    ("py-recorder-units", "tests/contract_input_recorder.py", "UNITS", "acts@0 dropped from the recorder's UNITS",
     'UNITS = {"soft-norms@0", "norms@0", "norm-defaults@0", "acts@0"}',
     'UNITS = {"soft-norms@0", "norms@0", "norm-defaults@0"}', f"{TEST}::test_the_recorded_corpus_gives_one_record_in_both_engines"),
    ("py-s5-units", "tests/test_wire_contract_s5_lean.py", "UNITS", "acts@0 dropped from the s5 tests' UNITS",
     '    "acts@0": (base_a, ACTS, "norms-elaborate", "Acts", legacy_norms),\n', "",
     f"{TEST}::test_the_recorded_corpus_gives_one_record_in_both_engines"),
    ("py-d31-text-copied", PY, "acts_environment", "a D-31 text copied into Python with one word changed",
     "    if vocabulary_refusal(root[\"environment\"], text):\n",
     "    if text.startswith(\"InvalidInput: the adverb '\") and text.endswith(\"' is declared twice\"):\n"
     "        return \"1.1f\", {\"message\": text.replace(\"declared\", \"listed\")}\n"
     "    if vocabulary_refusal(root[\"environment\"], text):\n",
     f"{TEST}::test_every_fault_gives_its_member_in_python_with_leans_text"),
    ("py-oracle-unguarded", PY, "vocabulary_refusal", "an earlier refusal read as the frames'",
     "    return _refusal(alone(True)) == text and _refusal(alone(False)) is None",
     "    return _refusal(alone(True)) == text", f"{TEST}::test_the_frames_members_name_only_the_first_refusal"),
    ("py-alone-fixed-emptied", PY, "vocabulary_refusal", "the block's `fixed` emptied (F1 again)",
     '        acts = block if frames else {k: v for k, v in block.items() if k not in ("frames", "adverbs")}',
     '        acts = {"fixed": [], **{k: block[k] for k in ("frames", "adverbs") if k in block and frames}}',
     f"{TEST}::test_the_frames_members_name_only_the_first_refusal"),
    ("py-frames-class", PY, "acts_environment", "the frame limit named 1.1f",
     '        return ("1.1e" if text.startswith("ResourceLimit:") else "1.1f"), {"message": text}',
     '        return "1.1f", {"message": text}', f"{TEST}::test_every_fault_gives_its_member_in_python_with_leans_text"),
    ("py-registry-no-hooks", PY, "REGISTRY", "norms@0's hooks unregistered",
     "REGISTRY = Registry().register(hooks=HOOKS, classifiers=", "REGISTRY = Registry().register(classifiers=",
     f"{TEST}::test_every_fault_gives_its_member_in_python_with_leans_text"),
    ("py-frame-limit-oracle", FAULTS, "limits", "the frame limit one too low",
     '"maxFrames": _largest(lambda n: lambda root: _block(root).update(frames=frames(n)), 2)',
     '"maxFrames": _largest(lambda n: lambda root: _block(root).update(frames=frames(n + 1)), 2)',
     f"{TEST}::test_every_fault_gives_its_member_in_python_with_leans_text"),
    ("rust-table-code", "rust/ve-kernel/src/contract_tables.rs", "ACTS", "1.1f's code",
     'id: "1.1f", code: "ACTS_INVALID_FRAMES"', 'id: "1.1f", code: "ACTS_INVALID_ENVIRONMENT"',
     "tests/test_wire_contract_rust.py::test_rust_table_rows_equal_the_contract_rows"),
]


def lake(*targets):
    env = {**os.environ, "PATH": str(Path.home() / ".elan/bin") + os.pathsep + os.environ["PATH"]}
    return subprocess.run(["lake", "build", *targets], cwd=ROOT / "lean", env=env, capture_output=True, text=True)


def pin_service():
    """`ve_service` built from the tree as it is, and pinned in `lean/checkers.lock`, so the suite's client runs it."""
    built = lake("ve_service")
    assert built.returncode == 0, built.stdout[-2000:]
    sys.path.insert(0, str(ROOT / "tools"))
    import regen_generated
    os.environ["VE_REGEN_NO_RUST"] = "1"
    assert regen_generated.pin_checkers() == 0


def check(command):
    if command.startswith(SERVICE):
        pin_service()
        try:
            return check(command.removeprefix(SERVICE))
        finally:
            subprocess.run(["git", "checkout", "--", "lean/checkers.lock"], cwd=ROOT, check=True)
    if command == LEAN:
        env = {**os.environ, "PATH": str(Path.home() / ".elan/bin") + os.pathsep + os.environ["PATH"]}
        result = subprocess.run(command.split(), cwd=ROOT / "lean", env=env, capture_output=True, text=True)
        lines = [line for line in (result.stdout + result.stderr).splitlines() if line.startswith("error: VE/")]
    else:
        result = subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", command]), cwd=ROOT,
                                env=nested_pytest.environment(os.environ), capture_output=True, text=True)
        lines = [line for line in result.stdout.splitlines() if line.startswith(("FAILED", "ERROR"))]
    return result.returncode != 0, lines


def main():
    records = []
    for name, path, definition, bug, old, new, command in MUTANTS:
        file = ROOT / path
        text = file.read_text()
        assert text.count(old) == 1, name
        file.write_text(text.replace(old, new, 1))
        try:
            killed, lines = check(command)
        finally:
            subprocess.run(["git", "checkout", "--", path], cwd=ROOT, check=True)
        if command.startswith(SERVICE):
            assert lake("ve_service").returncode == 0  # the restored tree's service, which lean/checkers.lock pins
        records.append({"id": name, "file": path, "definition": definition, "bug": bug,
                        "test": command.removeprefix(SERVICE) if command != LEAN
                        else f"{path} #guard (lake build VE.WireContract.Hooks.Acts)",
                        "status": "KILLED" if killed else "SURVIVED", "failures": lines[:6]})
        print(name, records[-1]["status"], lines[:2], flush=True)
    if any(r["file"] in (HOOK, NORMS) for r in records):
        check(LEAN)  # the restored module's build
    (Path(__file__).parent / "mutants.json").write_text(json.dumps(records, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
