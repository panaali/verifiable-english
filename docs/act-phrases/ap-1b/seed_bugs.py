"""Seeded bugs of ap-1b: one per new trusted definition and per claimed behaviour (R16), planted, run and restored.

    uv run python docs/act-phrases/ap-1b/seed_bugs.py [--only ID ...]

Each mutant replaces one exact text in one file (it must occur once) and runs its check: a Lean module build
(killed when it fails; the first error line is recorded) or a pytest node (killed when it fails). The file is then
restored from git and, after the Lean mutants, the touched modules are rebuilt. Results go to `mutants.json`.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
W, P, R, E = "lean/VE/Norms/Wire.lean", "lean/VE/Norms/Plain.lean", "lean/VE/Norms/Replay.lean", \
    "lean/VE/EnglishGrammar/Encode.lean"
S, F, D, T = "lean/VE/Service/Standalone.lean", "lean/VE/Service/FamilyNorms.lean", \
    "lean/VE/Compose/Dispatch.lean", "lean/VE/Norms/Tree.lean"
EX, CX, LX = "lean:VE.Service.ActsExamples", "lean:VE.Compose.Examples", "lean:VE.Acts.LexicalExamples"
PY = "tests/test_acts_profile.py::"
LOADS, ROUTE = PY + "test_an_acts_environment_loads_with_its_block_and_forms_as_data", \
    PY + "test_the_norms_route_checks_rules_on_acts"

# (id, definition, file, old, new, check)
MUTANTS = [
    ("actsFixed-fields", "actsFixed", W, '    exactFields block ["fixed"]\n', "", EX),
    ("actsFixed-unchecked", "actsFixed", W, "    let _ ← VE.Acts.Lexical.decodeFixed fx\n", "", EX),
    ("actsProfiles-any", "actsProfiles", W, "if readsActs ps then ps else []", "ps", EX),
    # ap-1b review F1: `acts@0` is read only from a sorted unique list, on every reader
    ("readsActs-sorted", "readsActs", W, 'ps.contains "acts@0" && decide (ps.Pairwise (· < ·))', 'ps.contains "acts@0"', EX),
    ("actsView-premise", "actsView", W, "  if readsActs ps then (environment", "  if true then (environment", EX),
    ("baseEnvironmentJson-whole-list", "baseEnvironmentJson", R, "pure (if Wire.readsActs profiles then",
     'pure (if profiles.contains "acts@0" then', EX),
    ("placeholderJson-acts-order", "placeholderJson", "lean/VE/NormDefaults/Wire.lean",
     ' || (profiles.contains "acts@0" && !VE.Norms.Wire.readsActs profiles)', "", EX),
    # ap-1b review F2: without `acts@0` the block is not read
    ("actsFixed-premise", "actsFixed", W, "  | false, .ok block => do", "  | _, .ok block => do", EX),
    ("actsProfiles-flag", "actsProfiles", W, "  | true, .ok ps =>", "  | _, .ok ps =>", EX),
    ("actsView-block", "actsView", W, '    | .obj kvs => Json.obj (kvs.erase "acts")', "    | .obj kvs => Json.obj kvs", EX),
    ("actsView-profile", "actsView", W, '(toJson (ps.erase "acts@0"))', "(toJson ps)", EX),
    ("actsFamilyRefusal-text", "actsFamilyRefusal", W, 's!"acts@0 on the {f} family is not implemented"',
     's!"acts@0 on {f} is not implemented"', CX),
    ("decodeNormsEnvironment-fixed", "decodeNormsEnvironment", W, "decodeRegulatedIn ps fx p args raw",
     "decodeRegulatedIn ps [] p args raw", EX),
    ("decodeNormsEnvironment-profiles", "decodeNormsEnvironment", W,
     "if ps.isEmpty then e.profiles else ps, environment⟩", "e.profiles, environment⟩", EX),
    ("canonicalEnvironmentJson-act", "canonicalEnvironmentJson", W, "canonicalActIn ps fx name args.length act",
     "canonicalAct name args.length act", EX),
    ("decodeSource-acts", "decodeSource", W, "decodeNormsEnvironment environment displayConstants (acts := true)",
     "decodeNormsEnvironment environment displayConstants", EX),
    ("decodeEnvironmentU-acts", "decodeEnvironmentU", "lean/VE/NormDefaults/Wire.lean",
     "decodeNormsEnvironment frame (acts := true)", "decodeNormsEnvironment frame", EX),
    ("decodeRegulatedAllIn-check", "decodeRegulatedAllIn", P, "some <$> Wire.decodeRegulatedIn ps fx p args raw",
     "some <$> Wire.decodeRegulated p args raw", EX),
    # ap-1b review C1: the plain route gates the submitted list (the row's texts, its family refusals included)
    ("plainRun-gate", "Plain.run", P, '  if profiles.contains "acts@0" then\n', "  if false then\n", EX),
    ("plainRun-view", "Plain.run", P, "let environment := if ps.isEmpty then environment else Wire.actsView environment ps",
     "let environment := environment", EX),
    ("baseEnvironmentJson-view", "baseEnvironmentJson", R,
     'pure (if Wire.readsActs profiles then Wire.actsView base (profiles.filter (· != "norms@0")) else base)',
     "pure base", EX),
    ("treeCheck-plain-act", "Tree.check", T, "    | .permission, none | .obligation, none =>",
     '    | .plain, some _ => throw s!"InvalidInput: invalid regulated fields for {r.name}"\n'
     "    | .permission, none | .obligation, none =>", EX),
    ("validatedComposed-gate", "validatedComposedEnvironment", S, '  if rawProfiles.contains "acts@0" then\n',
     "  if false then\n", EX),
    ("validatedComposed-checkRegulated", "validatedComposedEnvironment", S,
     ' && !named.contains "acts@0" &&', " &&", EX),
    ("folView-gate", "folView", F, '  if listed.contains "acts@0" then\n', "  if false then\n", EX),
    ("modalForm-plain", "modalForm", E, "| .plain, some act, some f => pure (none, some (VE.Acts.Lexical.wording f act))",
     "| .plain, some act, some _ => pure (none, none)", EX),
    ("modalForm-not-modal", "modalForm", E, "pure (none, some (VE.Acts.Lexical.wording f act))",
     "pure (some (VE.Acts.Lexical.wording f act), none)", EX),
    ("envDecode-fixed", "Env.decode", E, "  let fx ← VE.Norms.Wire.actsFixed acts environment\n", "  let fx : List String := []\n", EX),
    ("typingView-acts", "typingView", E, '  let env := if ps.contains "acts@0" then VE.Norms.Wire.actsView env ps else env\n',
     "", EX),
    ("actsRefuses-speech", "actsRefuses", D, '"alternatives@0", "speech-acts@0"].map', '"alternatives@0"].map', CX),
    ("row-requires", "profileTable (acts row)", D, '⟨"acts@0", ["norms@0"], actsRefuses, "layer"⟩,\n  ⟨"closure@0"',
     '⟨"acts@0", [], actsRefuses, "layer"⟩,\n  ⟨"closure@0"', CX),
    # with Tree.check's refusal NormDefaults' regBody keeps it too, so `check_eq` holds and only a fixture can fail
    ("treeCheck-and-regBody-plain-act", "Tree.check", T, "    | .permission, none | .obligation, none =>",
     '    | .plain, some _ => throw s!"InvalidInput: invalid regulated fields for {r.name}"\n'
     "    | .permission, none | .obligation, none =>", EX,
     ("lean/VE/NormDefaults/Check.lean", "        | .permission, none =>",
      '        | .plain, some _ => throw s!"InvalidInput: invalid regulated fields for {r.name}"\n'
      "        | .permission, none =>")),
    # fault order (ap-1a review F2; DELTA row 4): each swap must fail a LexicalExamples guard (or a proof first)
    ("order-bytes-first", "Lexical.check", "lean/VE/Acts/Lexical.lean", '  unless act.startsWith "{0} " && slots',
     '  unless act.utf8ByteSize ≤ maxActBytes do throw s!"ResourceLimit: act phrase for {name} is over '
     '{maxActBytes} bytes"\n  unless act.startsWith "{0} " && slots', LX),
    ("order-phrases-first", "Lexical.decodeFixed", "lean/VE/Acts/Lexical.lean",
     '  if fx.length > maxPhrases then throw s!"ResourceLimit: more than {maxPhrases} fixed phrases"\n'
     "  let ps ← fx.mapM phraseToks\n", "  let ps ← fx.mapM phraseToks\n"
     '  if fx.length > maxPhrases then throw s!"ResourceLimit: more than {maxPhrases} fixed phrases"\n', LX),
    ("order-form-first", "decodeRegulatedWith", W,
     '    if keys.contains "act" != keys.contains "form" then\n'
     '      throw s!"InvalidInput: a plain act for {name} needs its form, and a form needs its act"\n',
     "", LX, (W, '      throw s!"InvalidInput: invalid form for {name}"\n',
              '      throw s!"InvalidInput: invalid form for {name}"\n    if keys.contains "act" != keys.contains '
              '"form" then\n      throw s!"InvalidInput: a plain act for {name} needs its form, and a form needs '
              'its act"\n')),
    # Python
    ("py-drop-form", "Environment._decode (form)", "ve/environment.py", 'raw_reg.get("permission"), raw_reg.get("form"))',
     'raw_reg.get("permission"))', LOADS),
    ("py-drop-block", "Environment._decode (acts block)", "ve/environment.py",
     'object.__setattr__(self, "acts", canonical_json(vocabulary["acts"]))', 'object.__setattr__(self, "acts", None)',
     LOADS),
    ("py-base-keeps-acts", "NormDocument.base_environment", "ve/norms.py",
     'if p not in ("norms@0", "readings@1", "acts@0")]', 'if p not in ("norms@0", "readings@1")]', ROUTE),
    ("py-model-not-kept", "MODEL_REDUCTIONS", "ve/profiles.py", '    "acts@0": _KEPT,', '    "acts@0": ModelReduction(),',
     "tests/test_model_environment.py::test_model_environment_keeps_everything_a_model_reads"),
]

ENV = dict(os.environ, PATH=os.path.expanduser("~/.elan/bin") + ":" + os.environ["PATH"])


def run(check: str) -> tuple[bool, str]:
    if check.startswith("lean:"):
        done = subprocess.run(["lake", "build", check[5:]], cwd=ROOT / "lean", env=ENV, capture_output=True, text=True)
        first = next((m.group(0) for m in re.finditer(r"error: [^\s:]+\.lean:\d+:\d+[^\n]*", done.stdout + done.stderr)),
                     "")
        return done.returncode != 0, first[:200]
    import sys
    sys.path.insert(0, str(ROOT))
    from tools.nested_pytest import command, environment
    done = subprocess.run(command(["-q", "-x", check], python=("uv", "run", "python")), cwd=ROOT,
                          env=environment(ENV), capture_output=True, text=True)
    failed = next((line for line in done.stdout.splitlines() if line.startswith("FAILED")), "")
    return done.returncode != 0, failed[:200]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*")
    args = parser.parse_args()
    out = ROOT / "docs/act-phrases/ap-1b/mutants.json"
    listed = {m[0] for m in MUTANTS}
    results = {k: v for k, v in (json.loads(out.read_text()) if out.exists() else {}).items() if k in listed}
    touched = set()
    for ident, definition, file, old, new, check, *more in MUTANTS:
        if args.only and ident not in args.only:
            continue
        originals = {}
        for path, o, n in [(ROOT / file, old, new)] + [(ROOT / f, o, n) for f, o, n in more]:
            text = path.read_text()
            originals.setdefault(path, text)
            assert text.count(o) == 1, (ident, path, text.count(o))
            path.write_text(text.replace(o, n))
        try:
            killed, line = run(check)
        finally:
            for path, text in originals.items():
                path.write_text(text)
        if file.startswith("lean/"):
            touched.add(check[5:])
        results[ident] = {"definition": definition, "file": file, "test": check.removeprefix("lean:"),
                          "killed": killed, "first_failure": line}
        print(ident, "KILLED" if killed else "SURVIVED", line, flush=True)
        out.write_text(json.dumps(results, indent=1, ensure_ascii=False) + "\n")
    for module in sorted(touched):  # the restored sources' modules, so no stale build is left
        subprocess.run(["lake", "build", module], cwd=ROOT / "lean", env=ENV, capture_output=True, check=True)
    out.write_text(json.dumps(results, indent=1, ensure_ascii=False) + "\n")
    return 0 if all(r["killed"] for r in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
