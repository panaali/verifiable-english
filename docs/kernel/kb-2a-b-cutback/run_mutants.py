"""Plant each seeded bug and mutant of kb-2a-b-cutback, build, record what fails, restore (evidence script).

    uv run python docs/kernel/kb-2a-b-cutback/run_mutants.py OUT.json [ID ...]

Each entry replaces one exact text (it must occur once) in one Lean file, runs `lake build` of the modules that state
the ties (`VE.Service.CoreCheckProofs`, `VE.Service.CoreCheckExamples`), restores the file whatever happens, and maps
each error line back to the declaration or `#guard` it sits in. An entry is killed when its named killer is among them.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAN = ROOT / "lean"
TARGETS = ["VE.Service.CoreCheckProofs", "VE.Service.CoreCheckExamples"]
CC = "lean/VE/Service/CoreCheck.lean"
P = "VE.Service.CoreCheck."

MUTANTS = [
    {"id": "a", "seeded": True, "definition": P + "reads", "file": CC,
     "what": "reads drops the exception formulas",
     "old": "(c.judgedIn rules I.d.R).toOption).join.map (·.formulas)).getD [] ++\n        exceptionFormulas rules u.content",
     "new": "(c.judgedIn rules I.d.R).toOption).join.map (·.formulas)).getD []",
     "killer": P + "reads_status"},
    {"id": "b", "seeded": True, "definition": P + "unitStatus", "file": CC,
     "what": "unitStatus renders the fold's labelled as UNFORMALISED",
     "old": "  | .labelled => .labelled\n", "new": "  | .labelled => .unformalised\n",
     "killer": P + "view_unit_status"},
    {"id": "c", "seeded": True, "definition": P + "routed", "file": CC,
     "what": "routed also accepts a soft-norms@0 document with alternatives@0",
     "old": "(listedProfiles env).all rowProfiles.contains &&",
     "new": "(listedProfiles env).all (fun p => rowProfiles.contains p || p == \"alternatives@0\") &&",
     "killer": P + "routed_iff"},
    {"id": "d", "seeded": True, "definition": P + "factsJson", "file": CC,
     "what": "factsJson drops the last formula",
     "old": "Json.arr (P.map VE.Route.Wire.encodeFormula).toArray",
     "new": "Json.arr (P.dropLast.map VE.Route.Wire.encodeFormula).toArray",
     "killer": P + "facts_round_trip"},
    {"id": "m-roundTrips", "definition": P + "roundTrips", "file": CC,
     "what": "roundTrips no longer refuses a soft decision predicate among the premises",
     "old": "decide ((P.map VE.Bridge.formulaNodes).foldl (· + ·) 0 ≤ VE.Limits.maxNodes) &&\n"
            "    (P.flatMap VE.Norms.preds).all (!(VE.SoftNorms.decisionNames src.D).contains ·)",
     "new": "decide ((P.map VE.Bridge.formulaNodes).foldl (· + ·) 0 ≤ VE.Limits.maxNodes)",
     "killer": P + "facts_round_trip"},
    {"id": "m-viewOf", "definition": P + "viewOf", "file": CC,
     "what": "viewOf renders each unit's own status, not the fold's",
     "old": "  let rows := I.rows.map fun r => { r with status := status r.id r.status }",
     "new": "  let rows := I.rows.map fun r => { r with status := r.status }",
     "killer": P + "view_unit_status"},
    {"id": "m-statuses", "definition": "VE.Kernel.DocumentFold.statuses", "file": "lean/VE/Kernel/DocumentFold.lean",
     "what": "statuses folds every unit over no rows",
     "old": "  table.map fun u => (u.id, status u rows)", "new": "  table.map fun u => (u.id, status u [])",
     "killer": P + "statuses_lookup"},
    {"id": "m-routedRefusals", "definition": P + "routedRefusals", "file": CC,
     "what": "the first refusal loses a word of environmentOf's text",
     "old": "  [unavailable \"judgments@0 with soft-norms@0 needs its composed Lean route\",",
     "new": "  [unavailable \"judgments@0 with soft-norms@0 needs its composed route\",",
     "killer": P + "routedRefusals_sites"},
    {"id": "m-runCaseReported", "definition": P + "runCaseReported", "file": CC,
     "what": "a routed refusal is no longer marked lowering",
     "old": "      row.setObjVal! \"lowering\" (.bool true)", "new": "      row",
     "killer": P + "runCaseReported_routes"},
    {"id": "m-Inputs", "definition": P + "Inputs", "file": CC,
     "what": "Inputs' first and third fields swap (the request id and the document id trade places)",
     "old": "structure Inputs where\n  id : String\n  d : Decoded\n  documentId : String",
     "new": "structure Inputs where\n  documentId : String\n  d : Decoded\n  id : String",
     "killer": "lean/VE/Service/CoreCheckExamples.lean #guard answer id"},
    {"id": "m-inputs", "definition": P + "inputs", "file": CC,
     "what": "inputs reads no judgment views",
     "old": "  let views ← if d.judged then judgedViews d.E d.front d.names active d.units rules d.R else pure []",
     "new": "  let views ← pure []",
     "killer": P + "inputs_reads"},
    {"id": "m-exceptionFormulas", "definition": P + "exceptionFormulas", "file": CC,
     "what": "exceptionFormulas drops the sufficient conditions",
     "old": "        e.sufficient ++ e.necessary).getD []", "new": "        e.necessary).getD []",
     "killer": "lean/VE/Service/CoreCheckExamples.lean #guard exception OPEN"},
    {"id": "m-tableOf", "definition": P + "tableOf", "file": CC,
     "what": "tableOf keeps, for a unit that does not assert its content, the statements that read nothing",
     "old": "else all.filter (!·.reads.isEmpty) }", "new": "else all.filter (·.reads.isEmpty) }",
     "killer": P + "tableOf_opens"},
    {"id": "m-statementJson", "definition": P + "statementJson", "file": CC,
     "what": "statementJson shows a premise as null",
     "old": "      | .premise φ => (\"premise\", VE.Route.Wire.encodeFormula φ)", "new": "      | .premise φ => (\"premise\", .null)",
     "killer": P + "statement_shown"},
    {"id": "m-decode", "definition": "VE.Service.Document.decode", "file": "lean/VE/Service/Document.lean",
     "what": "decode reads its environment without the core flag",
     "old": "    (if front == doc.front then some (Loader.optionalList front \"open_terms\") else none) core\n",
     "new": "    (if front == doc.front then some (Loader.optionalList front \"open_terms\") else none) false\n",
     "killer": P + "decode_reads"},
]

ERROR = re.compile(r"error: (?:\./)*([\w/]+\.lean):(\d+):\d+")
DECL = re.compile(r"^(?:theorem|def|structure)\s+(\S+)")


def enclosing(path: str, line: int) -> str:
    """The theorem or `#guard` that line `line` of `path` (under lean/) belongs to."""
    lines = (LEAN / path).read_text().splitlines()
    module = "VE.Service.CoreCheck." if path.startswith("VE/Service/CoreCheck") else ""
    for k in range(min(line, len(lines)) - 1, -1, -1):
        text = lines[k]
        if text.startswith("#guard"):
            return f"lean/{path}:{k + 1} #guard"
        m = DECL.match(text)
        if m:
            return module + m.group(1) if not m.group(1).startswith("VE.") else m.group(1)
    return f"lean/{path}:{line}"


def killed_by(entry: dict, failing: list[str]) -> bool:
    killer = entry["killer"]
    if "#guard" not in killer:
        return killer in failing
    path = killer.split(" ")[0]
    return any(f.startswith(path + ":") and f.endswith("#guard") for f in failing)


def run(entry: dict) -> dict:
    path = ROOT / entry["file"]
    original = path.read_text()
    assert original.count(entry["old"]) == 1, (entry["id"], original.count(entry["old"]))
    env = {**os.environ, "PATH": f"{Path.home()}/.elan/bin:{os.environ['PATH']}"}
    try:
        path.write_text(original.replace(entry["old"], entry["new"]))
        out = subprocess.run(["lake", "build", *TARGETS], cwd=LEAN, env=env, capture_output=True, text=True)
    finally:
        path.write_text(original)
    log = out.stdout + out.stderr
    failing = sorted({enclosing(f, int(n)) for f, n in ERROR.findall(log)})
    row = {k: entry[k] for k in ("id", "definition", "file", "what", "killer")}
    row |= {"seeded": entry.get("seeded", False), "build_rc": out.returncode, "failing": failing,
            "killed": out.returncode != 0 and killed_by(entry, failing)}
    print(row["id"], "killed" if row["killed"] else "SURVIVED", failing)
    return row


def main(out: Path, ids: list[str]) -> int:
    rows = [run(m) for m in MUTANTS if not ids or m["id"] in ids]
    out.write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    return 0 if all(r["killed"] for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]), sys.argv[2:]))
