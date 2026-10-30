"""The anthropic-rsp baseline: what each byte that is not CHECKED waits for (PLAN 7 feature map, metric M3).

    python usecases/anthropic-rsp/measure.py [--check]

Reads the saved `spans.json` and `coverage.json` only (`build_document.py` writes them) and writes `units.json` and
`gaps.json` to `docs/usecases/safetyfw/anthropic-rsp/`; `--check` fails if either would change. Each unit that is not
CHECKED gets every feature family it waits for: JT (judgment terms, open terms), DF (defaults), SC (scope,
quantifiers, addressees, reading sets of scope), QT (quantities), ET (time, deadlines, event order), AP (act phrases),
WG (weighing, comparison, causation), AT (attitudes: belief, expectation, aim, intent, hedges), "external reference",
"readings" (a set whose readings differ in which rules hold) or "no claim to check" (layout, exposition,
definitions, examples, history). A family's bytes count each unit under every blocker it has; "alone" counts the
units with that one blocker, whose bytes move when that one feature lands.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_document as B  # noqa: E402
sys.path.insert(0, str(HERE.parent))
from safetyfw_common import FAMILIES, measure_units  # noqa: E402

EVIDENCE = HERE.parents[1] / "docs" / "usecases" / "safetyfw" / "anthropic-rsp"
NO_CLAIM = "no claim to check"
UNFORMALISED = {"external_reference": "external reference", "no_deadline_or_trigger": "ET",
                "process_description": "ET", "aim_without_force": "AT", "hope": "AT", "preference": "AT",
                "degree_term": "JT", "as_appropriate": "JT", "addressed_to_others": "SC"}
LABELLED = {"attributed": "AT", "hedged": "AT", "causal": "WG"}


def blockers(record):
    """The families a unit that is not CHECKED waits for; [] for a CHECKED unit."""
    if record["status"] == "CHECKED":
        return []
    found = []
    if record["status"] == "UNFORMALISED":
        found.append(UNFORMALISED[record["reason"]])
    elif record["status"] == "OPEN":
        if record.get("open_terms"):
            found.append("JT")
        if "reading_set" in record:
            found.append(B.SET_FAMILIES[B.READINGS[record["reading_set"]][0]])
    elif "restates" not in record and "history" not in record:
        found.append(LABELLED.get(record["kind"], NO_CLAIM) if not record.get("waits") else record["waits"][0])
    found += [w for w in record.get("waits", []) if w not in found]
    return found or [NO_CLAIM]


def measure():
    return measure_units(HERE / "spans.json", HERE / "coverage.json", blockers)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    units, gaps = measure()
    for name, data in (("units.json", units), ("gaps.json", gaps)):
        text = json.dumps(data, indent=1, sort_keys=True) + "\n"
        if args.check:
            if (EVIDENCE / name).read_text() != text:
                raise SystemExit(f"{name} is out of date")
        else:
            EVIDENCE.mkdir(parents=True, exist_ok=True)
            (EVIDENCE / name).write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
