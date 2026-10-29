"""Map every PF byte outside CHECKED to the feature it awaits (PLAN 7, M3)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from safetyfw_common import FAMILIES, measure_units  # noqa: E402
sys.path.insert(0, str(HERE))
import build_document as B  # noqa: E402

EVIDENCE = HERE.parents[1] / "docs/usecases/safetyfw/openai-preparedness"
REASONS = {"external_reference": "external reference", "hedged_claim": "AT", "event_order": "ET",
           "not_translated": "readings", "quantity": "QT", "quantifier_scope": "SC"}


def blockers(record):
    if record["status"] == "CHECKED":
        return []
    found = list(record.get("waits", []))
    if record["status"] == "UNFORMALISED":
        found.append(REASONS[record["reason"]])
    elif record["status"] == "OPEN":
        if record.get("open_terms"):
            found.append("JT")
        if record.get("reading_set"):
            found.append(B.SET_FAMILIES[B.READINGS[record["reading_set"]][0]])
    elif not found:
        found.append("no claim to check")
    return list(dict.fromkeys(found)) or ["no claim to check"]


def measure():
    return measure_units(HERE / "spans.json", HERE / "coverage.json", blockers)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    units, gaps = measure()
    for name, data in (("units.json", units), ("gaps.json", gaps)):
        text = json.dumps(data, indent=1, sort_keys=True) + "\n"
        path = EVIDENCE / name
        if args.check:
            if path.read_text() != text:
                raise ValueError(f"{name} is out of date")
        else:
            EVIDENCE.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
