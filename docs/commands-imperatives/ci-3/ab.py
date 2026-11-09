"""The CI-3 A/B, from a checkout's root after `lake build VE.Commands.RunExamples`: `uv run python <this file> AB.json`.

(i) `surfaceKind` flips ((iii)): every string literal of the pinned corpus (tests/*speech*.py, tests/frozen_speech/,
docs/question-answering/q1-4/evidence/speech_ab.py) whose normalised text starts `if ` or `then `, the only texts the
new cases can change (`Wire.surfaceKind`); each is then read by main's and this item's `surfaceKind` over `E_web`.
(ii) The `english.command` reader: every wording of the commands fixtures (Examples, StepsExamples, RunExamples) over
`E_web`, by main's entry (`proofTask`, else `readCommand`; Read.lean is unchanged by ci-3, so it is evaluated at
HEAD, lifted with `lift (.core s) false`) and by `readInstruction`. Unchanged rows are counted, changed rows listed
with their class (DRI 2026-10-28 item 2(b)): b1 refused -> read for a section 7 shape, b2 the refusing direction,
STOP a read wording that now reads differently."""
import ast
import glob
import json
import re
import subprocess
import sys
from pathlib import Path

SPACE = re.compile("[ \t\n\r\x0b\x0c]+")
FOLD = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")
CORPUS = sorted(glob.glob("tests/*speech*.py")) + sorted(glob.glob("tests/frozen_speech/*.py")) + [
    "docs/question-answering/q1-4/evidence/speech_ab.py"]
FIXTURES = ["lean/VE/Commands/Examples.lean", "lean/VE/Commands/StepsExamples.lean", "lean/VE/Commands/RunExamples.lean"]
# main's `surfaceKind` (lean/VE/SpeechActs/Wire.lean at the merge base), for the A/B only.
OLD_KIND = '''def oldKind (regulated : List VE.Norms.Regulated) (source : String) : String := Id.run do
  let text := VE.SpeechActs.Wire.surfaceWords source
  if text.endsWith "?" then return "question"
  if text.startsWith "in this task, " || text.startsWith "this document is task " then return "binding"
  if text.startsWith "do not " || text.startsWith "prove that " || text.startsWith "command " then
    return "instruction"
  for r in regulated do
    if let some verb := r.act.bind VE.SpeechActs.Wire.actVerb then
      if VE.SpeechActs.Wire.startsWithWord text verb then return "instruction"
  if ["question ", "is ", "are ", "does ", "do ", "did ", "was ", "were ", "will ", "would ",
      "who ", "what ", "when ", "where ", "why ", "how ", "which ", "must ", "can "].any text.startsWith then
    return "question"
  return "asserted"
'''


def literals(path):
    return [n.value for n in ast.walk(ast.parse(Path(path).read_text())) if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def flippable(text):
    t = " ".join(w for w in SPACE.split(text) if w).translate(FOLD)
    return t.startswith("if ") or t.startswith("then ")


def lean_rows(kinds, wordings):
    q = lambda s: json.dumps(s)
    src = ["import VE.Commands.RunExamples", "open VE.Commands VE.Commands.Examples VE.Commands.RunExamples", OLD_KIND,
           "def oldEntry (c : Context) (s : String) : StepOutcome := lift (.core s) false ((proofTask c s).getD "
           "(readCommand c.se c.sc c.E c.L c.b s))",
           "def regs : List VE.Norms.Regulated := match VE.SpeechActs.Wire.decodeSpeechEnvironmentFull E_web with"
           " | .ok se => se.ne.regulated | .error _ => []",
           "def both (s : String) : List String := match ctxOf (request \"x\" (env := E_web)) [] with"
           " | some c => [toString (repr (oldEntry c s)), toString (repr (readInstruction c s))] | none => []"]
    for s in kinds:
        src.append(f"#eval IO.println (Lean.Json.compress (Lean.toJson [\"kind\", {q(s)}, oldKind regs {q(s)}, "
                   f"VE.SpeechActs.Wire.surfaceKind regs {q(s)}]))")
    for s in wordings:
        src.append(f"#eval IO.println (Lean.Json.compress (Lean.toJson ([\"read\", {q(s)}] ++ both {q(s)} ++ "
                   f"[toString (repr (shapes {q(s)}))])))")
    scratch = Path("lean/.lake/ci3-ab.lean")
    scratch.write_text("\n".join(src) + "\n")
    out = subprocess.run(["lake", "env", "lean", ".lake/ci3-ab.lean"], cwd="lean", capture_output=True, text=True,
                         env={"PATH": str(Path.home() / ".elan/bin") + ":/usr/bin:/bin", "HOME": str(Path.home())})
    return [json.loads(line) for line in out.stdout.splitlines() if line.startswith("[")], out.stderr


def kind_of(o):
    return re.match(r"VE\.Commands\.StepOutcome\.(\w+)", o).group(1)


def main(out):
    kinds = sorted({s for f in CORPUS for s in literals(f) if flippable(s)})
    wordings = sorted({w for f in FIXTURES for w in re.findall(r'"([A-Z ][^"\\]*[.?])"', Path(f).read_text())})
    rows, err = lean_rows(kinds, wordings)
    flips = [r for r in rows if r[0] == "kind" and r[2] != r[3]]
    reads, changed = [r for r in rows if r[0] == "read"], []
    for _, s, base, head, shp in reads:
        if base == head:
            continue
        b, h = kind_of(base), kind_of(head)
        # b2 includes a refusal whose code and text change (ci-5's DELTA row 6 precedent).
        cls = ("b1" if b in ("refused", "limit") and h in ("one", "steps", "many") and "Shape.core" not in shp
               else "b2" if h in ("refused", "limit") else "STOP")
        changed.append({"wording": s, "class": cls, "base": base, "head": head, "shapes": shp})
    rec = {"corpus_files": CORPUS, "corpus_if_then_literals": len(kinds), "surface_kind_flips": flips,
           "fixture_wordings": len(wordings), "unchanged": len(reads) - len(changed), "changed": changed}
    Path(out).write_text(json.dumps(rec, indent=1) + "\n")
    print(len(rows), "rows;", len(flips), "flips;", len(changed), "changed;", err[-400:])


main(sys.argv[1])
