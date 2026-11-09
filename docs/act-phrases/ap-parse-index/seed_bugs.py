#!/usr/bin/env python3
"""ap-parse-index's seeded bugs: plant each, build the Lean module that must catch it (a proof of equality with the
definition it replaces in compiled code, or a `#guard`), record the failing lines (KILLED), restore the file, and
write mutants.json beside this script. One plant per new trusted definition and per claimed behaviour; the service
plant (the quadratic grammar build, caught by tests/test_ap_parse_index.py at the CPU deadline) is the REPORT's.
Run from the repository root: `python3 docs/act-phrases/ap-parse-index/seed_bugs.py [ids...]`."""
import json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
IX, GR, ME, RD, RUN, TB, WI, NW = (f"lean/VE/{m}.lean" for m in (
    "Acts/Index", "Acts/Grammar", "Acts/Meaning", "Acts/Readings", "Acts/Run", "Grammar/Table", "Acts/Wire", "Norms/Wire"))
DEC = ["VE.Acts.DecodeExamples", "VE.Service.ActsExamples"]
GEX = "VE.Acts.GrammarExamples"
# (file, id, definition, behaviour, before, after, lake targets)
BUGS = [
    (IX, "firstsGo-no-insert", "VE.Acts.firstsGo", "a repeated element is listed again",
     "x :: firstsGo (seen.insert x) xs", "x :: firstsGo seen xs", ["VE.Acts.Index"]),
    (IX, "idxGo-last-place", "VE.Acts.idxGo", "an element is numbered by its last occurrence",
     "(m.insertIfNew x i)", "(m.insert x i)", ["VE.Acts.Index"]),
    (GR, "closedFast-no-lhs", "VE.Acts.closedFast", "a nonterminal that has a rule is closed with `never` too",
     "(Std.HashSet.ofList (rs.map (·.lhs)))", "∅", ["VE.Acts.Grammar"]),
    (GR, "buildFast-start", "VE.Acts.buildFast", "the start symbol is numbered past the nonterminals",
     "start := ix.getD .S names.length", "start := names.length", ["VE.Acts.Grammar"]),
    (GR, "csimp-closed-build-dropped", "VE.Acts.closed_eq_fast", "compiled code builds the grammar in quadratic time",
     "@[csimp] theorem closed_eq_fast", "theorem closed_eq_fast", [GEX]),
    (ME, "meaningWith-no-fit", "VE.Acts.meaningWith", "an atom that does not fit its frame has a meaning",
     "if actOk V A then", "if true then", ["VE.Acts.MeaningExamples"]),
    (RD, "readingsOnce-csimp-dropped", "VE.Acts.readingsOnce", "compiled `readings` computes the rule table per "
     "derivation", "@[csimp] theorem readings_eq_once", "theorem readings_eq_once", [GEX]),
    (RD, "reader-no-table", "VE.Acts.reader", "the reader's meaning reads no rules",
     "(rs.toArray, (build rs).prepare)", "(#[], (build rs).prepare)", ["VE.Acts.Readings"]),
    (RD, "readingsBy-budget", "VE.Acts.readingsBy", "a reader's listing runs with half its budget",
     "(R.2.parse N b ts)", "(R.2.parse N (b / 2) ts)", ["VE.Acts.Readings"]),
    (RD, "readingsOnce-budget", "VE.Acts.readingsOnce", "compiled `readings` runs with another budget",
     "readingsBy V (reader V) N b ts\n", "readingsBy V (reader V) N (b / 2) ts\n", ["VE.Acts.Readings"]),
    (RD, "readOnce-budget", "VE.Acts.readOnce", "`read` runs with another budget than it is given",
     "readIn (build rs) (meaningWith rs.toArray V) N b ts", "readIn (build rs) (meaningWith rs.toArray V) N (b / 2) ts",
     ["VE.Acts.Readings"]),
    (RUN, "witnessed-empty-table", "VE.Acts.Run.witnessed", "the listing reads its derivations against no rules",
     "let μ := meaningWith rs.toArray V", "let μ := meaningWith #[] V", ["VE.Acts.Run"]),
    (RUN, "tagged-empty-table", "VE.Acts.Run.tagged", "the tagged meaning reads no rules",
     "taggedWith (closed (schema V)).toArray base t", "taggedWith #[] base t", ["VE.Acts.RunExamples"]),
    (RUN, "rowsOf-empty-table", "VE.Acts.Run.rowsOf", "each reading's acts are read against no rules",
     "let rs := (closed (schema V)).toArray\n  let tags", "let rs : Array RuleS := #[]\n  let tags", ["VE.Acts.RunExamples"]),
    (RUN, "taggedWith-keeps-words", "VE.Acts.Run.taggedWith", "no content word is tagged by its place",
     "(tagTree rs base false t 0)", "(tagTree rs base true t 0)", ["VE.Acts.RunExamples"]),
    (WI, "checkActBy-lexical-text", "VE.Acts.Wire.checkActBy", "a lexical act is returned with another text",
     "| .ok a => .ok (a, none)", "| .ok a => .ok (a ++ \" \", none)", ["VE.Acts.Wire"]),
    (WI, "joinedActBy-no-budget", "VE.Acts.Wire.joinedActBy", "a joined act is read with no step budget",
     "readingsBy V R rawCap stepBudget ts.toArray", "readingsBy V R rawCap 0 ts.toArray", DEC),
    (NW, "actsOf-no-frames", "VE.Norms.Wire.actsOf", "a document's acts are read under no frames",
     "let R := VE.Acts.reader V", "let R := VE.Acts.reader ⟨[], []⟩", DEC),
    (TB, "combineFast-dead-end-kept", "VE.Grammar.combineFast", "an end position with an empty suffix still combines",
     "      | [] => []\n", "      | [] => p.2.map fun t => (p.1, [t])\n", ["VE.Grammar.Table"]),
    (TB, "row-charged-a-constant", "VE.Grammar.rowAt", "a row is charged a constant, not its rules and positions",
     "(nt, o2, s1 + P.positions + c2)", "(nt, o2, 1 + c2)", [GEX]),
]


def lake(targets):
    env = dict(os.environ, PATH=str(Path.home() / ".elan/bin") + os.pathsep + os.environ["PATH"])
    p = subprocess.run(["lake", "build", *targets], cwd=ROOT / "lean", env=env, capture_output=True, text=True)
    out = p.stdout + p.stderr
    lines = ["lean/" + x for x in re.findall(r"^error: (VE/[^:]+\.lean:\d+):", out, re.M)]
    if p.returncode and not lines and "Lean exited with code 134" in out:  # the elaborator aborted on a #guard
        lines = [f"lean/{m.replace('.', '/')}.lean (aborted)" for m in re.findall(r"✖ \[\d+/\d+\] Building (\S+)", out)]
    return p.returncode, sorted(set(lines))


def main():
    only = set(sys.argv[1:])
    out = Path(__file__).with_name("mutants.json")
    rows = [r for r in json.loads(out.read_text())["mutants"] if r["id"] not in only] if out.exists() and only else []
    for f, mid, defn, beh, before, after, check in BUGS:
        if only and mid not in only:
            continue
        path = ROOT / f
        text = path.read_text()
        assert text.count(before) == 1, (mid, text.count(before))
        try:
            path.write_text(text.replace(before, after))
            rc, failing = lake(check)
        finally:
            path.write_text(text)
        rows.append({"id": mid, "language": "Lean", "file": f, "definition": defn, "behaviour": beh,
                     "status": "KILLED" if rc != 0 and failing else "SURVIVED", "test": ", ".join(failing)})
        print(mid, rows[-1]["status"], rows[-1]["test"], flush=True)
    order = [b[1] for b in BUGS]
    rows.sort(key=lambda r: order.index(r["id"]) if r["id"] in order else len(order))
    rc, _ = lake([GEX, "VE.Acts.RunExamples", "VE.Acts.MeaningExamples", *DEC])
    head = {"item": "ap-parse-index", "command": "python3 docs/act-phrases/ap-parse-index/seed_bugs.py",
            "restored_build_returncode": rc}
    body = ",\n".join("  " + json.dumps(r, ensure_ascii=False) for r in rows)
    out.write_text(json.dumps(head, ensure_ascii=False)[:-1] + ', "mutants": [\n' + body + "\n]}\n")
    sys.exit(0 if rc == 0 and all(r["status"] == "KILLED" for r in rows) else 1)


if __name__ == "__main__":
    main()
