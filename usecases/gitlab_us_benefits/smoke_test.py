"""Smoke test: run the made-up cases (smoke_cases.py) through run.py with Lean and compare with the hand answers.
usage (repository root): .venv/bin/python -B usecases/gitlab_us_benefits/smoke_test.py"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import smoke_cases as S  # noqa: E402

with tempfile.TemporaryDirectory() as d:
    out = Path(d) / "smoke.json"
    subprocess.run([sys.executable, "-B", str(HERE / "run.py"), "--cases-module", "smoke_cases", "--out", str(out)],
                   check=True, capture_output=True)
    run = json.loads(out.read_text())
bad = [(q, a, S.EXPECT[q]) for r in run["records"] for q, a in r["answers"].items() if a.get("value", a["answer"]) != S.EXPECT[q]]
for b in bad:
    print("DIFF", *b)
print(f"smoke: {len(S.EXPECT) - len(bad)}/{len(S.EXPECT)}")
sys.exit(1 if bad else 0)
