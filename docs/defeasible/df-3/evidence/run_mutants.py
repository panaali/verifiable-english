"""Seeded bugs for df-3: each applied alone, built (Lean), its named check run, then restored."""
import json, os, subprocess, sys
ROOT = "/home/seyran/code/ve-df-3"
sys.path.insert(0, ROOT)
from tools import nested_pytest
T = "tests/test_defaults_readings.py::"
DV, WI, SC = "lean/VE/Readings/DefaultVerdicts.lean", "lean/VE/Defaults/Wire.lean", "lean/ResponseShape/Schemas/ReadingsRoute.lean"
STOP_ROW = ("    HoldsG (dSem.{u} N) [] .bottom c (dConflictRow e d) := by\n", "    HoldsG (dSem.{u} N) [] .bottom c (dConflictRow e d) := by\n  stop\n")
STOP_COL = ("    dConflictRow e d = .conflict := by\n", "    dConflictRow e d = .conflict := by\n  stop\n")
M = [
 # id, definition, file, [(old, new)], check: ("build", module) | ("test", [ids])
 ("L1", "choiceSoft", DV, [("VE.Rights.correlate (choiceDoc N.D c).1", "VE.Rights.correlate (choiceDoc N.D []).1")], ("build", "VE.Readings.DefaultVerdictsExamples")),
 ("L2", "dSem", DV, [("free := fun c => (VE.Readings.Wire.sdSem.{u} N).free c ∧ DefaultCoherent.{u} (choiceU N c) (choiceSoft N c) []", "free := fun c => (VE.Readings.Wire.sdSem.{u} N).free c")], ("build", "VE.Readings.DefaultVerdicts")),
 ("L3", "dConflictRow", DV, [("  if xFree e && d.coherent then .free else", "  if xFree e then .free else"), STOP_ROW, STOP_COL], ("test", [T+"test_df_rho_default_conflict_from_the_gate_only"])),
 ("L4", "dBasis", DV, [("some (basisOf as ((e.counter.map (xModelOk U X A Γ φ · false)).getD false), as)", "some (basisOf as false, as)"),
   ("((choiceDoc z.y.r.N.D c).2 ++ z.y.x.Γ) z.y.x.φ) := by\n  intro c b as hm\n", "((choiceDoc z.y.r.N.D c).2 ++ z.y.x.Γ) z.y.x.φ) := by\n  stop\n  intro c b as hm\n")], ("test", [T+"test_df_nu_default_fold_all_with_the_default_readings_assumption"])),
 ("L5", "DVerdicts.hasDefaults", DV, [("  z.ds.any (fun d => !(dfltLabelled (choiceSoft z.y.r.N d.1)).isEmpty)", "  z.ds.any (fun _ => true)")], ("test", [T+"test_without_a_default_premise_there_is_no_member"])),
 ("L6", "dEnglish", DV, [("    .de8 :: z.bases.flatMap (fun p =>", "    z.bases.flatMap (fun p =>")], ("test", [T+"test_df_nu_default_fold_all_with_the_default_readings_assumption"])),
 ("L7", "runVerdictsD", DV, [("        | none => a)", "        | none => a.setObjVal! \"default\" (defaultJson z))")], ("test", [T+"test_df_tau_a_strict_conflict_leaves_no_member"])),
 ("L8", "verdictWord", DV, [('  | .all => "ALL" | .some => "SOME"', '  | .all => "SOME" | .some => "SOME"')], ("test", [T+"test_df_nu_default_fold_all_with_the_default_readings_assumption"])),
 ("L9", "dChoiceJson", DV, [('("assumptions", toJson p.2)]', '("assumptions", toJson (p.2 ++ p.2))]')], ("test", [T+"test_df_nu_default_fold_all_with_the_default_readings_assumption"])),
 ("L10", "DLine.json", DV, [('  | .de7 c => Json.mkObj [("row", .str "DE7")', '  | .de7 c => Json.mkObj [("row", .str "DE12")')], ("test", [T+"test_df_rho_default_conflict_from_the_gate_only"])),
 ("L11", "defaultJson", DV, [('Json.mkObj [("conflict", .str (word (foldConflict z.dConflictRows))),', 'Json.mkObj [("conflict", .str (word (foldConflict z.y.x.conflictRows))),')], ("test", [T+"test_df_rho_default_conflict_from_the_gate_only"])),
 ("L12", "collisionFields", WI, [('("deciders", toJson (giveWayDeciders D P Q))]),', '("deciders", toJson ([] : List String))]),')], ("test", [T+"test_df_rho_default_conflict_from_the_gate_only"])),
 ("L13", "verdicts_default", SC, [('("verdict", enumS ["ALL", "SOME", "NONE", "UNKNOWN"]),', '("verdict", enumS ["ALL", "SOME", "NONE"]),')], ("build", "ResponseShape.Encoders.ReadingsRoute")),
 ("L14", "verdicts_default_line", SC, [('closed [("row", enumS ["DE7", "assumptions", "DE12"])', 'closed [("row", enumS ["assumptions", "DE12"])')], ("build", "ResponseShape.Encoders.ReadingsRoute")),
 ("L15", "verdicts_default_choice", SC, [('      ("query", enumS ["proved", "refuted", "UNKNOWN"]),', '      ("query", enumS ["proved", "refuted"]),')], ("build", "ResponseShape.Encoders.ReadingsRoute")),
 ("L16", "DLine", DV, [("inductive DLine | de8 | de7 (c : Choice) | assumptions (c : Choice) | de12 (c : Choice)", "inductive DLine | de8 | de7 (c : Choice) | assumptions (c : Choice)")], ("build", "VE.Readings.DefaultVerdicts")),
 ("P1", "_check_default (labels)", "ve/readings_verdicts/binding.py", [("            _need(kept == [label for label in labels if label in kept])\n", "")], ("test", [T+"test_df_nu_every_forged_field_is_refused[a label the choice has not]"])),
 ("P2", "_check_default (choices)", "ve/readings_verdicts/binding.py", [('    _need([e["choice"] for e in member["per_choice"]] == [e["choice"] for e in row["per_choice"]])\n', "")], ("test", [T+"test_df_nu_every_forged_field_is_refused[a row dropped]", T+"test_df_nu_every_forged_field_is_refused[rows reordered]"])),
 ("P3", "_check_default (presence)", "ve/readings_verdicts/binding.py", [("    _need((member is not None) == defaults)\n", "")], ("test", [T+"test_df_nu_every_forged_field_is_refused[member absent]"])),
 ("P4", "defaults_english.readings", "ve/defaults_english.py", [('        out += [f"Under {under(line[\'choice\'])}: {sentences[0]}", *sentences[1:]]', '        out += sentences')], ("test", [T+"test_df_rho_english_is_de7_under_the_colliding_reading_never_a_contradiction"])),
 ("P5", "_readings_without_exception (--under)", "ve/document/cli.py", [("    row = route.default_answer(conclusion, assumed=assumed)", "    row = route.default_answer(conclusion)")], ("test", [T+"test_under_names_readings_and_other_flags_are_refused"])),
 ("P6", "default_case", "ve/readings_verdicts/choice.py", [('            piece["model"] = search.model(X, own, Bottom())\n', "")], ("test", [T+"test_df_nu_default_fold_all_with_the_default_readings_assumption"])),
]

def sh(cmd, timeout=3500):
    return subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=timeout)

only = set(sys.argv[1:])
results = []
baseline = {}
for mid, definition, path, edits, (kind, arg) in M:
    if only and mid not in only:
        continue
    if kind == "test":
        key = tuple(arg)
        if key not in baseline:
            baseline[key] = subprocess.run(
                nested_pytest.command(["-q", "-p", "no:cacheprovider", *arg]), cwd=ROOT,
                env=nested_pytest.environment(os.environ), capture_output=True, text=True, timeout=3000)
        if baseline[key].returncode != 0:
            raise RuntimeError(f"baseline tests for {mid} did not pass: {baseline[key].returncode}")
    full = f"{ROOT}/{path}"
    original = open(full).read()
    text = original
    for old, new in edits:
        assert text.count(old) == 1, (mid, old)
        text = text.replace(old, new)
    open(full, "w").write(text)
    try:
        if kind == "build":
            r = sh(f"cd lean && PATH=~/.elan/bin:$PATH lake build {arg}")
            killed, by = r.returncode != 0, f"lake build {arg}"
        else:
            b = sh("/tmp/df3probe/svcfast.sh") if path.startswith("lean/") else None
            if b is not None and "Build completed" not in b.stdout:
                killed, by = True, "lake build ve_service: " + b.stdout.splitlines()[0][:160]
            else:
                r = subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", *arg]), cwd=ROOT,
                                   env=nested_pytest.environment(os.environ), capture_output=True, text=True,
                                   timeout=3000)
                killed, by = nested_pytest.failed_test_run(r), arg[0]
    finally:
        open(full, "w").write(original)
    results.append({"id": mid, "definition": definition, "file": path, "test": by,
                    "killed": killed, "language": "Lean" if path.startswith("lean/") else "Python"})
    print(mid, definition, "KILLED" if killed else "SURVIVED", "by", by, flush=True)
json.dump(results, open("/tmp/df3probe/mutants.out.json", "w"), indent=1, ensure_ascii=False)
