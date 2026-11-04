"""Seeded bugs of me-8: each planted alone, `lake build VE.Calc.ConsistencyExamples`, restored. Prints one JSON row a bug
with the guards that failed. Run from the checkout with a clean Lean tree: python3 docs/math-evidence/me-8/evidence/seed.py"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

LEAN = Path("lean")
INTERVAL, CONSISTENCY, EXAMPLES = (f"VE/Calc/{n}.lean" for n in ("Interval", "Consistency", "ConsistencyExamples"))
CHARGED = """  if limit < w + qbits i.1 + qbits i.2 then none
  else if Small i.1 ∧ Small i.2 then some (some i, w + qbits i.1 + qbits i.2)
  else some (none, w + qbits i.1 + qbits i.2)
"""
# id, file, definition, old, new, proofs cut to sorry, guards dropped because under this bug they run past the timeout.
BUGS = [
    ("S1", INTERVAL, "Interval.sub", "(a.1 - b.2, a.2 - b.1)", "(a.1 - b.1, a.2 - b.2)", ["enclose_sound"], []),
    ("S2", INTERVAL, "Printed.box", "(2 * D + 1) / (2 * u))", "(2 * D + 3) / (2 * u))", [], []),
    ("S3", CONSISTENCY, "endpointPoint", "if m % 2 = 1 then (i.2.box r).2 else (i.2.box r).1", "(i.2.box r).2", [], []),
    ("S4", CONSISTENCY, "refuteC", "else refuteC limit r inputs cs (j + 1) w", "else refuteC limit r inputs cs j w", [], []),
    ("S5", INTERVAL, "chargeI", CHARGED, CHARGED.replace(" + qbits i.1 + qbits i.2", ""), [], []),
    ("S6", CONSISTENCY, "grainRefutes", "!decide (RoundsTo r p (((a + i : Int) : Rat) / g))",
     "!decide (RoundsTo .halfEven p (((a + i : Int) : Rat) / g))", ["grain_sound"], []),
    ("S7", CONSISTENCY, "freeReadTable", "| .defined e => e.names.findSome? fun n => (t.lookup n).join",
     "| .defined _ => none", [], []),
    ("S8", CONSISTENCY, "consistencyInputFault", "if n ∈ ns ∨ !(ds.any", "if !(ds.any", ["consistencyInputFault_none"], []),
    ("S9", CONSISTENCY, "pointHoldsC", "visitC limit (u + pass) fun u =>", "visitC limit u fun u =>", [], []),
    ("S10", INTERVAL, "chargeI", "else if Small i.1 ∧ Small i.2 then", "else if True then",
     ["chargeI_some"], []),
    ("S11", INTERVAL, "chargeI", "else if Small i.1 ∧ Small i.2 then", "else if Small i.1 then", ["chargeI_some"], []),
    ("S12", INTERVAL, "chargeI", "else if Small i.1 ∧ Small i.2 then", "else if Small i.2 then", ["chargeI_some"], []),
    ("S13", CONSISTENCY, "outputNodes", ".foldlM (fun n (e : Expr) => e.nodesWithin n) maxPolyTerms)",
     ".foldlM (fun n (_ : Expr) => some n) maxPolyTerms)", [],
     [r'#guard run \(chain 40\)', r'#guard run \(squares 23\)']),
    ("S14", CONSISTENCY, "outputNodes", ".foldlM (fun n (e : Expr) => e.nodesWithin n) maxPolyTerms)",
     ".foldlM (fun _ (e : Expr) => e.nodesWithin maxPolyTerms) maxPolyTerms)", [], []),
    ("S15", CONSISTENCY, "consistencyRun", "| none => some (.unknown .consistencyInconclusive)",
     "| none => some (.fails 0 [])", [], []),
    ("S16", CONSISTENCY, "passWork", "nodes * (inputs.length + 64)", "nodes", [], []),
    ("S17", CONSISTENCY, "passWork", "8 * (inputs.length * inputs.length +", "(inputs.length * inputs.length +", [], []),
    ("S18", CONSISTENCY, "consistencyRun", "(refuteC limit r inputs outs' 0 pass)", "(refuteC limit r inputs outs' 0 0)",
     [], []),
]
LAKE = os.path.expanduser("~/.elan/bin/lake")


def cut_to_sorry(text: str, theorem: str) -> str:
    """The theorem's proof replaced by `sorry`: from its `:= by` up to the next top-level item."""
    start = text.index(f"theorem {theorem} ")
    body = text.index(":= by", start)
    end = re.compile(r"\n\n(?=\S)").search(text, body).start()
    return text[:body] + ":= by sorry" + text[end:]


def run(bug, only) -> dict | None:
    name, path, definition, old, new, sorries, drops = bug
    if only and name not in only:
        return None
    source, examples = LEAN / path, LEAN / EXAMPLES
    saved_source, saved_examples = source.read_text(), examples.read_text()
    if old not in saved_source:
        return {"id": name, "result": "NOT PLANTED", "old": old}
    planted = saved_source.replace(old, new, 1)
    for theorem in sorries:
        planted = cut_to_sorry(planted, theorem)
    try:
        source.write_text(planted)
        if drops:
            kept = [line for line in saved_examples.split("\n") if not any(re.match(d, line) for d in drops)]
            examples.write_text("\n".join(kept))
        done = subprocess.run([LAKE, "build", "VE.Calc.ConsistencyExamples"], cwd=LEAN, capture_output=True, text=True)
    finally:
        source.write_text(saved_source)
        examples.write_text(saved_examples)
    output = done.stdout + done.stderr
    return {"id": name, "language": "Lean", "file": f"lean/{path}", "definition": definition,
            "bug": f"{old!r} -> {new!r}", "proofs_cut_to_sorry": sorries, "guards_dropped": drops,
            "build_exit": done.returncode, "result": "KILLED" if done.returncode else "SURVIVED",
            "failed_at": sorted(set(re.findall(r"error: (VE/Calc/[\w]+\.lean:\d+)", output)))}


for row in (run(bug, set(sys.argv[1:])) for bug in BUGS):
    if row:
        print(json.dumps(row, ensure_ascii=False), flush=True)
