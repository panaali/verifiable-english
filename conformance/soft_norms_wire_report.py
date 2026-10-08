"""Deterministic Python shadow delta over the generic multi-fault selection."""

import argparse
from collections import Counter
from itertools import islice
import json
from pathlib import Path

from conformance.soft_norms import multi_fault_cases
from ve.errors import VEError
from ve.softnorms import load_soft_document
from conformance.softnorms_contract import REGISTRY
from conformance.wire_contract_engine import CLEAN, Deferred, Fault, load, run

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "conformance/wire-contract/soft-norms-python-delta.json"


def report(limit=2000):
    contract = load("soft-norms@0")
    counts = Counter()
    deltas = {}
    disagreements = []
    for label, environment, norms, expected_code in islice(multi_fault_cases(), limit):
        counts["cases"] += 1
        try:
            load_soft_document(environment, norms)
            legacy = None
        except VEError as error:
            legacy = error
        outcome = run(contract, {"environment": environment, "norms": norms}, registry=REGISTRY)
        if isinstance(outcome, Deferred):
            counts["deferred"] += 1
            disagreements.append({"case": label, "problem": "deferred", "at": outcome.id})
            continue
        if outcome is CLEAN:
            counts["clean"] += 1
            if legacy is not None:
                disagreements.append({"case": label, "problem": "residual", "legacy_code": legacy.code})
            continue
        assert isinstance(outcome, Fault)
        counts["fault"] += 1
        record = outcome.record
        if legacy is None or record["code"] != expected_code or record["code"] != legacy.code:
            disagreements.append({"case": label, "problem": "verdict or code",
                                  "check": record["check"], "contract_code": record["code"],
                                  "expected_code": expected_code,
                                  "legacy_code": None if legacy is None else legacy.code})
            continue
        if record["text"] != str(legacy):
            change = deltas.setdefault(record["check"], {"count": 0, "example": label,
                                                          "legacy": str(legacy),
                                                          "contract": record["text"]})
            change["count"] += 1
    return {"contract": contract["contract"], "revision": contract["revision"],
            "sample": "seed 0, first 2000 generic pair/triple cases",
            "counts": dict(sorted(counts.items())),
            "text_deltas": dict(sorted(deltas.items())),
            "disagreements": disagreements}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = report()
    rendered = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.check:
        if not REPORT.exists() or REPORT.read_text() != rendered:
            print("soft-norms Python shadow delta differs")
            return 1
    else:
        REPORT.write_text(rendered)
    print(f"{result['counts']['cases']} cases, {len(result['disagreements'])} disagreements, "
          f"{sum(row['count'] for row in result['text_deltas'].values())} text deltas")
    return bool(result["disagreements"])


if __name__ == "__main__":
    raise SystemExit(main())
