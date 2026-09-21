"""Freeze the full v0 corpus using only the pinned pre-closure integration code.

Run with the project Python from the repository root. The ordinary regression
test reads the committed JSON and needs neither git nor a second prover run.
"""
from pathlib import Path
import io
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "6798e034c4aa7082dafacbb7b130879cd4eec4f6"
OUTPUT = ROOT / "conformance/v0-replay-baseline.json"


def main():
    archive = subprocess.check_output(
        ["git", "archive", BASELINE, "ve", "conformance", "examples"], cwd=ROOT)
    with tempfile.TemporaryDirectory(prefix="ve-v0-replay-") as directory:
        with tarfile.open(fileobj=io.BytesIO(archive)) as tree:
            tree.extractall(directory, filter="data")
        # Imports, corpus generation AND replay all happen in the old checkout.
        result = subprocess.run([sys.executable, "-c", '''
from dataclasses import asdict
import json
from conformance.certificates import positive_cases, forged_cases
from ve import Environment
from ve.ast import document_from_data
from ve.entailment import check_entailment_certificate
positive, report = positive_cases()
forged = forged_cases()
rows = []
for case in positive + forged:
    env = Environment(case["environment"])
    fs = document_from_data(env, case["premises"] + [case["conclusion"]]).formulas
    verdict = check_entailment_certificate(env, fs[:-1], fs[-1], case["certificate"])
    rows.append({"case": case, "before": asdict(verdict)})
print(json.dumps({"positive": len(positive), "forged": len(forged),
                  "generation_report": report, "rows": rows}, sort_keys=True))
'''], cwd=directory, text=True, capture_output=True, check=True)
    import json
    data = json.loads(result.stdout)
    data["baseline_commit"] = BASELINE
    # One case per line keeps the uncompressed fixture reviewable and small.
    rows = data.pop("rows")
    header = json.dumps(data, indent=2, sort_keys=True)
    OUTPUT.write_text(header[:-2] + ',\n  "rows": [\n' +
                      ',\n'.join('    ' + json.dumps(row, sort_keys=True) for row in rows) +
                      '\n  ]\n}\n')
    print(f"{OUTPUT.name}: {len(rows)} cases ({data['positive']} valid, {data['forged']} invalid)")


if __name__ == "__main__":
    main()
