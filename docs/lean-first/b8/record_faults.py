"""Record a checkout's public answer to every reports fault-corpus document.

Usage::

    python docs/lean-first/b8/record_faults.py CHECKOUT OUT.json --label REV
    python docs/lean-first/b8/record_faults.py --evidence      # this checkout against the base

CHECKOUT's `ve` (and its own Lean service build) answers; the documents come from this
checkout's `tests/reports_fault_corpus.py`. The base recording,
`tests/data/reports_base_faults.json`, is this script run on the batch's base `9aaf918d`
(`git archive 9aaf918d`, with its `lean/` built by `lake build ve_service`). `--evidence`
writes `docs/lean-first/b8/evidence/fault-delta.json`, the grouped differences of this
checkout against that recording, which `tests/test_reports_fault_order.py` recomputes.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parents[3]
BASE = HERE / "tests/data/reports_base_faults.json"
EVIDENCE = HERE / "docs/lean-first/b8/evidence/fault-delta.json"


def corpus():
    spec = importlib.util.spec_from_file_location("reports_fault_corpus", HERE / "tests/reports_fault_corpus.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def record(checkout: Path, label: str) -> dict:
    sys.path.insert(0, str(checkout))
    from ve.document import check_document
    from ve.profiles import LANGUAGE, SPEC_REVISION
    faults = corpus()
    outcomes = {}
    with tempfile.TemporaryDirectory(prefix="ve-reports-faults-") as directory:
        for case_id, meta, source in faults.cases(LANGUAGE, SPEC_REVISION):
            path = Path(directory) / "case.md"
            path.write_text(faults.text(meta, source))
            outcomes[case_id] = faults.outcome(check_document, path)
    return {"format": "ve-reports-faults@1", "digest": faults.digest(LANGUAGE, SPEC_REVISION),
            "checkout": label, "outcomes": outcomes}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("checkout", nargs="?", type=Path)
    parser.add_argument("out", nargs="?", type=Path)
    parser.add_argument("--label", default="HEAD")
    parser.add_argument("--evidence", action="store_true")
    args = parser.parse_args()
    if args.evidence:
        head = record(HERE, "HEAD")
        result = corpus().classify(json.loads(BASE.read_text())["outcomes"], head["outcomes"])
        EVIDENCE.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
        return
    args.out.write_text(json.dumps(record(args.checkout.resolve(), args.label), indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
