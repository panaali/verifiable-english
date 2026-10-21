#!/usr/bin/env python3
"""Run 20261020T1800Z: re-run the five `ve ask` questions and the carried `ve document readings --conclusion` queries (probes/nd, probes/qt) on translation.ve.md.
Each output replaces the carried file in probes/ (the previous run's are in prev/probes/); the finish script compares them."""
import json, subprocess, sys
from pathlib import Path
RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
DOC = str((RUN / "translation.ve.md").relative_to(ROOT))
def ve(*a):
    p = subprocess.run([sys.executable, "-m", "ve", *a], cwd=ROOT, capture_output=True, text=True)
    return p.stdout, p.stderr
for i in range(1, 6):
    q = (RUN / f"probes/ask/q{i}.question.txt").read_text().strip()
    for suffix, flags in (("", ["--reading", "--json"]), (".answer", ["--json"])):
        out, err = ve("ask", *flags, DOC, q)
        (RUN / f"probes/ask/q{i}{suffix}.json").write_text(out)
        (RUN / f"probes/ask/q{i}{suffix}.err").write_text(err)
queries = {"nd/conclusion-no-denial-result": "nd/conclusion-no-denial.json", "nd/claim-human-result": "nd/conclusion-no-claim-human.json",
           "qt/fourth-result": "qt/fourth.conclusion.json", "qt/no-fourth-result": "qt/no-fourth.conclusion.json"}
for out_name, concl in queries.items():
    out, err = ve("document", "readings", DOC, "--conclusion", str((RUN / "probes" / concl).relative_to(ROOT)))
    (RUN / f"probes/{out_name}.json").write_text(out)
    (RUN / f"probes/{out_name}.err").write_text(err)
    d = json.loads(out)
    print(out_name, d.get("verdict"), d.get("evidence"), d.get("route"))
