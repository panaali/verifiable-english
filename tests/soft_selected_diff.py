"""kb-10a differential (test-only script, not collected): Python's retained answers against `soft-selected`.

Reads the JSON that the architect seat's `kb-10/dump.py` writes (per RSP document and case: the soft source,
the case model and, per regulated predicate and tuple, the rules Python selects and its completed outcome),
sends each document's model and queries to Lean's `soft-selected` through `ve.soft_route.selected_at` (one call
per document and case) and prints every query where the two differ. A mismatch is a finding for kb-10b, not
something this script fixes.

    uv run python tests/soft_selected_diff.py DUMP.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ve.soft_route import selected_at  # noqa: E402
from ve.softnorms import SoftEnvironment, SoftNormDocument  # noqa: E402


def compare(entry):
    """(queries, with a selected rule, background, mismatches) of one dumped document and case."""
    document = SoftNormDocument(SoftEnvironment(entry["environment"]), entry["norms"])
    queries = [{"predicate": q["predicate"], "tuple": q["tuple"]} for q in entry["queries"]]
    answer = selected_at(document, entry["model"], queries)
    mismatches = []
    for python, lean in zip(entry["queries"], answer["results"]):
        if sorted(lean["selected"]) != sorted(python["selected"]) or lean["outcome"] != python["outcome"]:
            mismatches.append(f"{python['predicate']} {python['tuple']}: lean {lean['selected']} {lean['outcome']}; "
                              f"python {python['selected']} {python['outcome']}")
    return len(queries), sum(1 for q in entry["queries"] if q["selected"]), answer["background"], mismatches


def main(path):
    total = selected = bad = 0
    for entry in json.loads(Path(path).read_text()):
        label = f"{entry['case']} default {entry['default']}"
        try:
            n, s, background, mismatches = compare(entry)
        except Exception as error:  # noqa: BLE001  (a refusal is a finding to print)
            print(f"{label}: REFUSED {type(error).__name__}: {error}")
            continue
        total, selected, bad = total + n, selected + s, bad + len(mismatches)
        print(f"{label}: {n} queries, {s} with a selected rule, background {background}, "
              f"{len(mismatches)} mismatches")
        for line in mismatches:
            print(f"  {line}")
    print(f"TOTAL: {total} queries, {selected} with a selected rule (Python), {bad} mismatches")


if __name__ == "__main__":
    main(sys.argv[1])
