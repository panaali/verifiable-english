"""Question answering Q2: the report's numbers, from saved evidence only (`evidence/`).

`capture` (run once, before the gate, on the batch's committed code) saves the evidence: the commit list and line
counts of `main..HEAD --no-merges`, the recorded fixtures' leads, the statement check's output, the trust budget at
the base and at HEAD. `block()` renders REPORT.md's generated block from the saved files alone, never from live git,
so it still holds after syncs with main and after the merge (`tests/test_question_answering_q2_report.py`). The
final gate's result is saved as `evidence/gate-result.json` after the gate, and the block shows it when present.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVIDENCE = HERE / "evidence"
BEGIN = "<!-- BEGIN GENERATED: report.py -->"
END = "<!-- END GENERATED: report.py -->"
LANGUAGES = {"Lean": lambda p: p.startswith("lean/") and p.endswith(".lean"),
             "Python (product)": lambda p: p.endswith(".py") and p.split("/", 1)[0] in ("ve", "tools", "conformance"),
             "Python (tests)": lambda p: p.startswith("tests/") and p.endswith(".py"),
             "Rust": lambda p: p.startswith("rust/") and p.endswith(".rs")}


def load(name):
    return json.loads((EVIDENCE / name).read_text())


def git(*args):
    return subprocess.run(["git", "--no-optional-locks", *args], cwd=ROOT, check=True, capture_output=True,
                          text=True).stdout


def capture() -> None:
    base = git("merge-base", "HEAD", "main").strip()
    head = git("rev-parse", "HEAD").strip()
    commits = git("rev-list", "--no-merges", "--reverse", "main..HEAD").split()
    numstat = []
    for commit in commits:
        for line in git("show", "--numstat", "--format=", commit).splitlines():
            added, deleted, path = line.split("\t", 2)
            if added != "-":
                numstat.append({"commit": commit, "path": path, "added": int(added), "deleted": int(deleted)})
    statements_diff = git("diff", f"{base}..{head}", "--", "lean/statements.txt")
    added = {line.split()[1] for line in statements_diff.splitlines() if line.startswith("+theorem ")}
    removed = {line.split()[1] for line in statements_diff.splitlines() if line.startswith("-theorem ")}
    new_theorems = sorted(added - removed)
    (EVIDENCE / "scope.json").write_text(json.dumps(
        {"range": "main..HEAD --no-merges", "base": base, "captured_head": head, "commits": commits,
         "numstat": numstat, "new_theorems": new_theorems}, indent=1) + "\n")
    fixtures = []
    for path in sorted((ROOT / "tests/fixtures/ask").glob("*.json")):
        if path.stem.startswith("packages-"):
            continue
        entry = json.loads(path.read_text())
        row = {"id": path.stem, "document": entry["path"], "question": entry["question"]}
        if "error" in entry:
            row["error"] = entry["error"]["class"]
        else:
            result = entry["result"]
            row |= {"route": result["route"], "lead": result["lead"], "rows": len(result["rows"]),
                    "row_leads": sorted({r["lead"] for r in result["rows"]}),
                    "reasons": sorted({r["reason"] for r in result["rows"] if r["reason"]}),
                    "lean_seconds": entry.get("seconds")}
        fixtures.append(row)
    (EVIDENCE / "fixtures.json").write_text(json.dumps({"fixtures": fixtures}, indent=1) + "\n")
    done = subprocess.run([sys.executable, "tools/question_statements.py", "--q2"], cwd=ROOT, capture_output=True,
                          text=True)
    (EVIDENCE / "statements.json").write_text(json.dumps(
        {"command": "tools/question_statements.py --q2", "exit": done.returncode,
         "output": done.stdout.splitlines()}, indent=1) + "\n")
    budgets = {}
    for name, rev in (("base", base), ("head", head)):
        budgets[name] = json.loads(git("show", f"{rev}:docs/trust-baseline.json"))["budget"]
    (EVIDENCE / "trust.json").write_text(json.dumps(budgets, indent=1) + "\n")


def metrics() -> dict:
    scope = load("scope.json")
    out = {"commits": len(scope["commits"]), "theorems": len(scope["new_theorems"]),
           "ask_theorems": sum(name.startswith(("VE.Ask.", "VE.Words.")) for name in scope["new_theorems"])}
    for language, matches in LANGUAGES.items():
        rows = [r for r in scope["numstat"] if matches(r["path"])]
        out[language] = {"added": sum(r["added"] for r in rows), "deleted": sum(r["deleted"] for r in rows),
                         "files": len({r["path"] for r in rows})}
    return out


def block() -> str:
    scope, m = load("scope.json"), metrics()
    lines = [BEGIN, "",
             f"Scope: `{scope['range']}` at `{scope['captured_head'][:8]}` (base `{scope['base'][:8]}`): "
             f"{m['commits']} commits; {m['theorems']} new theorems in `lean/statements.txt` "
             f"({m['ask_theorems']} in `VE.Ask` and `VE.Words`).", "",
             "| Language | Files | Lines added | Lines deleted |", "|---|---:|---:|---:|"]
    for language in LANGUAGES:
        lines.append(f"| {language} | {m[language]['files']} | {m[language]['added']} | {m[language]['deleted']} |")
    lines += ["", "Recorded answers (`tests/fixtures/ask`, replayed by `tests/test_ask_fixtures.py`):", "",
              "| Fixture | Route | Lead | Rows | Row leads | Reasons | Replay s |", "|---|---|---|---:|---|---|---:|"]
    for f in load("fixtures.json")["fixtures"]:
        if "error" in f:
            lines.append(f"| {f['id']} | — | refused: {f['error']} | 0 | — | — | — |")
        else:
            lines.append(f"| {f['id']} | {f['route']} | {f['lead']} | {f['rows']} | {', '.join(f['row_leads'])} | "
                         f"{', '.join(f['reasons']) or '—'} | {f['lean_seconds']} |")
    statements = load("statements.json")
    lines += ["", f"Statement check (`{statements['command']}`, exit {statements['exit']}):", ""]
    lines += [f"    {line}" for line in statements["output"]]
    mutants = load("mutants.json")["mutants"]
    lines += ["", f"Seeded bugs (`mutants.py`, `evidence/mutants.json`): {sum(x['caught'] for x in mutants)} of "
              f"{len(mutants)} caught.", "", "| Seeded bug | File | Behaviour | Caught by |", "|---|---|---|---|"]
    for x in mutants:
        lines.append(f"| {x['id']} | `{x['file']}` | {x['behaviour']} | `{' '.join(x['test'])}` |")
    relay = load("relay-gate.json")
    ask = relay["routes"]["service:ask"]
    lines += ["", f"Relay mutation gate (`tools/relay_mutation_gate.py --json`, `evidence/relay-gate.json`): "
                  f"{len(relay['failures'])} failures and {len(relay['findings'])} findings over all routes; `ask`: "
                  f"{ask['mutants']} mutants of {ask['fixtures']} fixtures, {ask['refused']} refused, "
                  f"{ask.get('accepted', 0)} accepted, each by a listed by-design class ("
                  + ", ".join(f"{k.split(':', 1)[1]} {v}" for k, v in sorted(ask.items()) if k.startswith("allowed:"))
              + f"), {ask.get('untyped', 0)} untyped."]
    trust = load("trust.json")
    lines += ["", "Trust budget (`docs/trust-baseline.json`): " + ", ".join(
        f"{k} {trust['base'][k]} → {trust['head'][k]} ({trust['head'][k] - trust['base'][k]:+d})" for k in
        ("K", "S", "V")) + "."]
    gate = EVIDENCE / "gate-result.json"
    if gate.exists():
        g = json.loads(gate.read_text())
        counts = g.get("counts", {})
        lines += ["", f"Full gate (`tools/gate.py`, `evidence/gate-result.json`): {g['status']} on "
                      f"`{g['commit_sha'][:8]}` (dirty: {str(g['dirty']).lower()}); stages "
                      f"{', '.join(g.get('stages', []))}; " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
                  + "."]
    else:
        lines += ["", "Full gate: not yet saved (`evidence/gate-result.json` is written after the gate)."]
    return "\n".join(lines + ["", END])


def write() -> None:
    path = HERE / "REPORT.md"
    text = path.read_text()
    path.write_text(text[:text.index(BEGIN)] + block() + text[text.index(END) + len(END):])


if __name__ == "__main__":
    {"capture": capture, "write": write}[sys.argv[1]]()
