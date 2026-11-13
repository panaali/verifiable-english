"""Fill the original kb-10b reports' empty choice inventories from the same direct probe calls.

The reports keep the original full-run commit and counts. This only supplies labels for documents
that bypassed document() in the original shadow. The targeted probes execute no Lean comparison.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from usecases import safetyfw_shadow as shadow_module  # noqa: E402


PROBES = {
    "anthropic-rsp": ({"id": "G1", "case": None, "item": ""},
                      {"id": "G3", "case": None, "item": ""}),
    "openai-preparedness": ({"id": "N2", "case": None, "item": ""},),
}


def repair(name):
    path = ROOT / "docs" / "usecases" / "safetyfw" / name / "kb10-shadow.json"
    report = json.loads(path.read_text())
    missing = {digest for digest, labels in report["document_choices"].items() if not labels}
    if not missing:
        raise ValueError(f"{name}: no empty choice inventories to repair")
    harness = shadow_module.load(name)
    shadow = shadow_module.Shadow()
    modes = [(None, None)] + [(f"m{n}", None) for n in range(1, 7)] + [
        (None, f"N{n}") for n in range(1, 4)]
    with shadow_module.installed(shadow, harness, shadow_module.HARNESSES[name]):
        try:
            for mutant, narrowing in modes:
                harness.MUTANT, harness.WITHOUT_NARROWING = mutant, narrowing
                for item in PROBES[name]:
                    harness.answer(item)
        finally:
            harness.MUTANT = harness.WITHOUT_NARROWING = None
    for digest in sorted(missing):
        labels = shadow.documents.get(digest, (None, []))[1]
        if not labels:
            raise ValueError(f"{name}: probe did not reconstruct {digest}")
        report["document_choices"][digest] = labels
    report["choice_label_correction"] = {
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "method": "direct G1/G3 or N2 probes over baseline, m1-m6, N1-N3; no full replay",
        "documents": len(missing),
    }
    path.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    print(f"{name}: repaired {len(missing)} document choice inventories")


if __name__ == "__main__":
    for name in PROBES:
        repair(name)
