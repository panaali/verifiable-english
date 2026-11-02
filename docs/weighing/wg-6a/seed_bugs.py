"""Plant each wg-6a seeded bug alone, build the zone fixtures, record every failing fixture, restore.

Run from the repository root: `python3 docs/weighing/wg-6a/seed_bugs.py`; writes mutants.json beside this file.
"""
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ZONE = "lean/VE/Weighing/Zone.lean"
MUTANTS = [
    ("decisionAtoms-skips-last-tuple", "decisionAtoms",
     "(allTuples M ss).map (p, ·)", "(allTuples M ss).dropLast.map (p, ·)"),
    ("openNames-drops-unsaidNames", "openNames",
     "decisionNames L.D ++ unsaidNames L.U", "decisionNames L.D"),
    ("AdmissibleCompletion-record-flipped", "AdmissibleCompletion",
     "(R a.1 a.2 ↔ b = true)", "(R a.1 a.2 ↔ b = false)"),
    ("OutcomeIn-wrong-name", "OutcomeIn",
     "(outcomeBase (fill U) r.name)", "(outcomeBase (fill U) \"\")"),
    ("SettledZ-existence-ignores-record", "SettledZ",
     "(∃ R, AdmissibleCompletion U X M opens record R) ∧", "(∃ R, AdmissibleCompletion U X M opens [] R) ∧"),
    ("ZoneUnknown-no-branch", "ZoneUnknown",
     "  | branch (assignment", "  -- | branch (assignment"),
]


def build() -> list[str]:
    env = {**os.environ, "PATH": os.path.expanduser("~/.elan/bin") + os.pathsep + os.environ["PATH"]}
    run = subprocess.run(["lake", "build", "VE.Weighing.ZoneExamples"], cwd=ROOT / "lean", env=env,
                         capture_output=True, text=True)
    errors = re.findall(r"error: (VE/Weighing/\S+?:\d+):\d+: ([^\n]*)", run.stdout + run.stderr)
    return [f"lean/{where}: {what[:60]}" for where, what in errors]


def main() -> None:
    path = ROOT / ZONE
    original = path.read_text()
    rows = []
    try:
        for ident, definition, before, after in MUTANTS:
            assert original.count(before) == 1, ident
            path.write_text(original.replace(before, after))
            failing = build()
            rows.append({"id": ident, "definition": definition, "file": ZONE, "mutation": [before, after],
                         "test": failing[0] if failing else "", "tests": failing, "killed": bool(failing)})
    finally:
        path.write_text(original)
    assert build() == [], "the restored tree must build"
    (Path(__file__).parent / "mutants.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    print("\n".join(f"{r['id']}: {r['tests'] or 'SURVIVED'}" for r in rows))


if __name__ == "__main__":
    main()
