"""Seeded bugs of ap-1bb: one per claimed behaviour and per new trusted definition (R16), planted, run and restored.

    uv run python docs/act-phrases/ap-1bb/seed_bugs.py [--only ID ...]

As ap-1b's: each mutant replaces one exact text in one file (it must occur once) and runs its check, a Lean module
build (killed when it fails; the first error line is recorded) or a pytest node (killed when it fails); the file is
restored, and the touched Lean modules are rebuilt. Results go to `mutants.json`.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
W, RUN, E = "lean/VE/Norms/Wire.lean", "lean/VE/Norms/Run.lean", "lean/VE/EnglishGrammar/Encode.lean"
EX, ENC = "lean:VE.Service.ActsExamples", "lean:ResponseShape.Encoders.Norms"
PY = "tests/test_acts_profile.py::"
SHOWN, BOUND = PY + "test_a_plain_act_reads_with_the_wording_lean_selected", \
    PY + "test_wordings_not_bound_to_the_request_are_unavailable"
SA, ENC_SA = "lean/VE/Service/Standalone.lean", "lean:ResponseShape.Encoders.Standalone"
ACTS_BOUND, ONE_ID = PY + "test_acts_not_bound_to_the_request_are_unavailable", \
    PY + "test_one_identity_is_one_environment_whichever_loads_first"
SLOTS = "test_slots_bound_is_the_one_slot_binding_of_every_relayed_wording"
RIGHTS_SLOTS = "tests/test_rights.py::test_a_generated_wording_whose_slots_are_not_its_predicates_arguments_is_unavailable"

# (id, definition, file, old, new, check)
MUTANTS = [
    ("plainWording-form", "plainWording", W, "| .plain, some act, some f => some (VE.Acts.Lexical.wording f act)",
     "| .plain, some act, some _ => some (VE.Acts.Lexical.wording .right act)", EX),
    ("plainWordings-first", "plainWordings", W, "  ne.regulated.filterMap fun r =>",
     "  (ne.regulated.take 1).filterMap fun r =>", EX),
    ("plainWordings-entry", "plainWordings", W, '.getObjValD r.name).getObjValD "regulated"))',
     '.getObjValD r.name).getObjValD "regulation"))', EX),
    ("runCase-wordings-empty", "Norms.Run.runCase", RUN, "((Wire.plainWordings src.ne).map fun",
     "(([] : List (String × String)).map fun", EX),
    ("runCase-wordings-untyped", "Norms.Run.runCase", RUN,
     '[("wordings", Json.mkObj ((Wire.plainWordings src.ne).map fun (p, w) => (p, .str w)))]',
     '[("wordings", toJson ((Wire.plainWordings src.ne).map (·.2)))]', EX),
    # the encoder theorem pins the member (skeletons hold fields, not types: the schema test types it)
    ("runCase-wordings-renamed", "Norms.Run.runCase", RUN, '[("wordings", Json.mkObj', '[("wording", Json.mkObj', ENC),
    ("modalForm-plain", "modalForm", E, "| _, _ => pure (none, VE.Norms.Wire.plainWording r raw)",
     "| _, _ => pure (none, none)", EX),
    # review F1: one identity, one environment (the row's canonical acts stored, bound and hashed)
    ("py-identity-unchecked", "validated_environment", "ve/backends/validation.py",
     'lambda built, row: row["environment_id"] == built.environment_id', "lambda built, row: True", ACTS_BOUND),
    ("py-acts-as-written", "Environment._decode", "ve/environment.py",
     'act = acts[name] if acts is not None else " ".join(act.split())', 'act = " ".join(act.split())', ONE_ID),
    ("py-acts-names-unbound", "Environment._decode", "ve/environment.py",
     "if acts is not None and set(acts) != {", "if False and set(acts) != {", ACTS_BOUND),
    ("canonicalActs-none", "canonicalActs", W, "| .ok act => do pure (some (p, ← act.getStr?))",
     "| .ok _ => do pure none", EX),
    ("canonicalActs-key", "canonicalActs", W, "| .ok act => do pure (some (p, ← act.getStr?))",
     '| .ok act => do pure (some ("p", ← act.getStr?))', EX),
    ("environmentCase-acts-as-written", "Standalone.environmentCase", SA,
     "let acts ← VE.Norms.Wire.canonicalActs canonical", "let acts ← VE.Norms.Wire.canonicalActs environment", EX),
    ("environmentCase-acts-empty", "Standalone.environmentCase", SA,
     '("acts", Json.mkObj (acts.map fun (p, a) => (p, .str a)))', '("acts", Json.mkObj [])', EX),
    ("environmentCase-acts-renamed", "Standalone.environmentCase", SA,
     '("acts", Json.mkObj (acts.map fun (p, a) => (p, .str a)))',
     '("act", Json.mkObj (acts.map fun (p, a) => (p, .str a)))', ENC_SA),
    ("environmentCase-legacy-acts-dropped", "Standalone.environmentCase", SA,
     '| _ => [("acts", Json.mkObj [])]))', "| _ => []))", ENC_SA),
    ("py-wordings-not-shown", "EnglishVocabulary", "ve/english.py",
     "            for name, template in plain_wordings(env).items():\n",
     "            for name, template in {}.items():\n", SHOWN),
    ("py-bind-off", "_bind_wordings", "ve/norms.py", "    if set(wordings) != _plain_acts(env) or not all(",
     "    if False and set(wordings) != _plain_acts(env) or False and not all(", BOUND),
    # review F2: a relayed wording's slots are its predicate's argument positions (`relay.slots_bound`)
    ("py-slots-names-only", "_bind_wordings", "ve/norms.py",
     "slots_bound(wording, len(env.predicates[p].arguments)) for p, wording in wordings.items()):",
     "True for p, wording in wordings.items()):", BOUND),
    ("py-slots-subset", "slots_bound", "ve/backends/relay.py",
     "return set(_SLOT.findall(template)) == {str(i) for i in range(arity)}",
     "return set(_SLOT.findall(template)) <= {str(i) for i in range(arity)}", PY + SLOTS),
    ("py-slots-past-arity", "slots_bound", "ve/backends/relay.py",
     "return set(_SLOT.findall(template)) == {str(i) for i in range(arity)}",
     "return set(_SLOT.findall(template)) <= {str(i) for i in range(arity + 1)}", RIGHTS_SLOTS),
    ("py-slots-braces", "slots_bound", "ve/backends/relay.py",
     'if type(template) is not str or "{" in _SLOT.sub("", template) or "}" in _SLOT.sub("", template):',
     "if type(template) is not str:", PY + SLOTS),
    ("py-rights-slots-off", "_bind_elaboration", "ve/rights_route.py",
     "if not slots_bound(wording, len(prime_predicates[name]['arguments'])):", "if False:", RIGHTS_SLOTS),
    ("py-bind-document-off", "NormDocument._lean_regenerated", "ve/norms.py",
     "            _bind_wordings(self.env, row)\n", "", BOUND),
    ("py-norm-defaults-asked", "plain_wordings", "ve/norms.py",
     "    if not _plain_acts(env) or NORM_DEFAULTS_PROFILE in env.profiles:",
     "    if not _plain_acts(env):", PY + "test_norm_defaults_keeps_todays_display_without_asking"),
    ("py-asked-without-acts", "plain_wordings", "ve/norms.py",
     "    if not _plain_acts(env) or NORM_DEFAULTS_PROFILE in env.profiles:",
     "    if NORM_DEFAULTS_PROFILE in env.profiles:",
     PY + "test_an_environment_without_a_plain_act_asks_lean_nothing_to_display"),
]
ENV = dict(os.environ, PATH=os.path.expanduser("~/.elan/bin") + ":" + os.environ["PATH"])


def run(check: str) -> tuple[bool, str]:
    if check.startswith("lean:"):
        done = subprocess.run(["lake", "build", check[5:]], cwd=ROOT / "lean", env=ENV, capture_output=True, text=True)
        first = next((m.group(0) for m in re.finditer(r"error: [^\s:]+\.lean:\d+:\d+[^\n]*", done.stdout + done.stderr)),
                     "")
        return done.returncode != 0, first[:200]
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
    out = ROOT / "docs/act-phrases/ap-1bb/mutants.json"
    listed = {m[0] for m in MUTANTS}
    results = {k: v for k, v in (json.loads(out.read_text()) if out.exists() else {}).items() if k in listed}
    touched = set()
    for ident, definition, file, old, new, check in MUTANTS:
        if args.only and ident not in args.only:
            continue
        path = ROOT / file
        text = path.read_text()
        assert text.count(old) == 1, (ident, file, text.count(old))
        path.write_text(text.replace(old, new))
        try:
            killed, line = run(check)
        finally:
            path.write_text(text)
        if file.startswith("lean/"):
            touched.add(check[5:])
        results[ident] = {"definition": definition, "file": file, "test": check.removeprefix("lean:"),
                          "killed": killed, "first_failure": line}
        print(ident, "KILLED" if killed else "SURVIVED", line, flush=True)
        out.write_text(json.dumps(results, indent=1, ensure_ascii=False) + "\n")
    for module in sorted(touched):  # the restored sources' modules, so no stale build is left
        subprocess.run(["lake", "build", module], cwd=ROOT / "lean", env=ENV, capture_output=True, check=True)
    return 0 if all(r["killed"] for r in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
