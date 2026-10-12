"""Compare recorded ask leads with the existing document verdict route, without model calls."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/spec/question-answering-q2/evidence/agreement.json"
_spec = importlib.util.spec_from_file_location("ask_fixtures", ROOT / "tools/ask_fixtures.py")
AF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AF)


def compare(ident: str) -> dict:
    entry = AF.load(ident)
    if "error" in entry:
        return {"fixture": ident, "ask": "refused", "older": None, "status": "outside ask route"}
    with tempfile.TemporaryDirectory(prefix="ve-q2-agreement-") as directory:
        question = Path(directory) / "conclusion.json"
        question.write_text(json.dumps(entry["result"]["ast"]))
        try:
            done = subprocess.run([sys.executable, "-m", "ve", "document", "readings",
                                   str(ROOT / entry["path"]), "--conclusion", str(question)],
                                  cwd=ROOT, capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            return {"fixture": ident, "ask": entry["result"]["lead"], "older": None,
                    "status": "older route exceeded 120 s wall"}
    if done.returncode:
        return {"fixture": ident, "ask": entry["result"]["lead"], "older": None,
                "status": f"older route exit {done.returncode}: {done.stderr.strip()[:200]}"}
    answer = json.loads(done.stdout)
    verdict = answer.get("verdict") or answer.get("status")
    status = "compared"
    if entry["result"]["lead"] == "yes" and verdict != "ALL":
        status = "requires review: yes without ALL"
    return {"fixture": ident, "ask": entry["result"]["lead"], "older": verdict, "status": status}


def main():
    requested = set(sys.argv[1:])
    saved = json.loads(OUT.read_text())["rows"] if OUT.exists() else []
    rows = {row["fixture"]: row for row in saved}
    for ident, _, _ in AF.FIXTURES:
        if ident not in rows and (not requested or ident in requested):
            rows[ident] = compare(ident)
            OUT.write_text(json.dumps({"method": "ve document readings --conclusion on each recorded question AST",
                                       "rows": list(rows.values())}, indent=2) + "\n")
            print(f"{ident}: {rows[ident]['status']}", flush=True)
    ordered = [rows[ident] for ident, _, _ in AF.FIXTURES if ident in rows]
    OUT.write_text(json.dumps({"method": "ve document readings --conclusion on each recorded question AST",
                               "rows": ordered}, indent=2) + "\n")
    print(OUT)
    if any(row["status"].startswith("requires review") for row in ordered):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
