"""Collect the shadow diagnostic deltas without changing public errors."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "conformance/wire-contract"
OUTPUT = ROOT / "soft-norms@0-delta.json"


def report():
    python = json.loads((ROOT / "soft-norms-python-delta.json").read_text())
    gate = json.loads((ROOT / "soft-norms@0-gate.json").read_text())
    return {
        "contract": gate["contract"], "revision": gate["revision"], "status": "shadow",
        "public_diagnostic_changes": [],
        "python_legacy_sample": python["sample"],
        "python_legacy_text_deltas": python["text_deltas"],
        "python_legacy_code_disagreements": python["disagreements"],
        "three_way_cases": sum(gate["tiers"].values()),
        "three_way_disagreements": gate["mismatches"],
        "inherited_records": "text and args are language-specific until base contracts exist",
        "s3_pre": {
            "status": gate["s3_pre"],
            "verdict_differences": gate["legacy_verdict_differences"],
            "code_differences": gate["legacy_code_differences"],
            "detail": "conformance/wire-contract/s3-pre.md",
        },
        "continuation_coverage_met": gate["coverage_met"],
        "coverage_unmet": gate["coverage_unmet"],
        "coverage_unmet_reasons": gate["coverage_unmet_reasons"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(report(), ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            print("wire delta report differs")
            return 1
    else:
        OUTPUT.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
