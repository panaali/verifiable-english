#!/usr/bin/env python3
"""Build and check the S1 document: the force-ambiguous units as content-bearing reading sets (composition S1, `readings@1`).

    uv run python usecases/claude-constitution-pilot/run-20261003T0600Z/s1.py

Run after build.py. Then adds the four operator ("can") sets (s1_operators.py). Starts from readings/all-default.ve.md (the soft chain: `soft-norms@0` + `documents@1`, the defeasible reading of
every force unit as a fixed rule), adds `readings@1`, and turns each unit whose main-document reading set is a strict/default pair
into an open set of two contents: the default rule, and its strict twin (the same rule without `mode` and `exception`, composition S1
1.7). Each set records the source word (the byte span of "should" / "shouldn’t" inside the unit), so VE can use its sentence E14.
Python's search finds one separating situation per pair (from the guard base first); Lean's `ve_readings_route` checks it when the
document loads, Python regenerates Lean's answer and Rust replays the situation.

The documents `readings@1` cannot yet join: `norm-defaults@0` (the main document), see `probe_s1.py`. So this document completes every
duty with `deny` (soft-norms@0 needs a completion), exactly as readings/all-default.ve.md did.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import time
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))

spec = importlib.util.spec_from_file_location("readings_s1_pilot", ROOT / "tools/readings_s1_pilot.py")
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)

import s1_operators  # noqa: E402
from ve.document import check_document, load_document  # noqa: E402
from ve.errors import VEError  # noqa: E402

SOURCE = (ROOT / "usecases/claude-constitution-pilot/source/claude-constitution.md").read_bytes()
OUT = RUN / "readings/s1.ve.md"
WORDS = re.compile("shouldn’t|should not|should|must not|must|shall not|shall|always|never")


def source_word(span):
    """The first modal word of the unit, as a byte span inside the unit (composition S1 2.1: a closed list)."""
    a, b = span
    text = SOURCE[a:b].decode("utf-8")
    m = WORDS.search(text)
    assert m, text
    start = a + len(text[:m.start()].encode("utf-8"))
    end = start + len(m.group(0).encode("utf-8"))
    assert SOURCE[start:end].decode("utf-8") == m.group(0)
    return [start, end], m.group(0)


def build():
    meta, source, named, skipped = pilot.constitution(RUN)
    main_meta, _ = pilot.read(RUN / "translation.ve.md")
    s1_operators.add(meta, main_meta)       # the four operator ("can") sets; recomputes the identities of the force sets
    spans = {u["id"]: u["span"] for u in pilot._flat(meta["units"])}
    words = {}
    for item in meta["reading_sets"]:
        if item["id"].startswith("force-"):  # "can" / "cannot" are not in the closed list of source words (spec 2.1)
            item["source_word"], words[item["id"]] = source_word(spans[item["unit"]])
    return meta, source, named, skipped, words


def main():
    meta, source, named, skipped, words = build()
    started = time.monotonic()
    meta, missing, limits = pilot.find_situations(meta)
    searched = round(time.monotonic() - started, 1)
    pilot.write(OUT, meta, source)
    result = {"document": str(OUT.relative_to(ROOT)), "search_seconds": searched,
              "sets": [{"set": i["id"], "unit": i["unit"], "source_word": words.get(i["id"]),
                        "candidates": [r["id"] for r in i["readings"]]} for i in meta["reading_sets"]],
              "units_with_strict_twin_noted": skipped, "pairs_without_situation": missing, "search_limits": limits}
    started = time.monotonic()
    try:
        load_document(OUT)
    except VEError as exc:
        result.update({"admitted": False, "rejection": getattr(exc, "message", str(exc))})
        print(json.dumps(result, indent=1, ensure_ascii=False))
        raise SystemExit(1)
    result["load_seconds"] = round(time.monotonic() - started, 1)
    result["admitted"] = True
    report = check_document(OUT)
    (RUN / "readings/check-s1.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    result["readings_report"] = report["readings"]
    result["premises"] = report["premises"]
    result["bytes_by_status"] = report["coverage"]["bytes_by_status"]
    (RUN / "readings/s1-result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "readings_report"}, indent=1, ensure_ascii=False))
    print(json.dumps({"separations": report["readings"].get("separations"), "findings": report["readings"].get("findings")}))
    for s in report["readings"]["sets"]:
        for p in s["pairs"]:
            print(s["set"], p["wording"], p["text"])


if __name__ == "__main__":
    main()
