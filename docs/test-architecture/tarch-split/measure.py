"""tarch-split's before/after numbers, from the saved Mac runs and the tests' own input partitions.

    uv run python docs/test-architecture/tarch-split/measure.py      # writes evidence/measure.json

Reads `evidence/mac-{before,after}-durations.txt` (pytest `--durations=0` of the same 18 files on ve-mac-1, 6
workers, at dae12d5f and at the batch's head) and writes, per group of split tests, the tests, their summed and
longest seconds (setup + call + teardown) before and after, and the inputs each group checks before and after:
rd6b's documents per chunk and the mixed smoke's documents per part are recomputed from the base's and the head's
partitions, so the totals are counted, not asserted. A measurement, never a test.
"""
from __future__ import annotations

from collections import defaultdict
import contextlib
import io
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
EVIDENCE = Path(__file__).resolve().parent / "evidence"
LINE = re.compile(r"^([0-9.]+)s (setup|call|teardown) +(\S+)$")
WALL = re.compile(r"(\d+) passed.* in ([0-9.]+)s")
GROUPS = {
    "assist fix3 property (test-tail's split, checked)": "test_assist.py::test_astra_fix3_property_success",
    "assist fix4 parent order": "test_assist.py::test_astra_fix4_parent_order",
    "assist rr2 budget monotonicity": "test_assist.py::test_astra_rr2_property_success_is_monotone",
    "assist rr2 inconclusive search": ("test_assist.py::test_astra_rr2_property_any_inconclusive",
                                       "test_assist.py::test_astra_rr2_every_search_exhausted"),
    "p1 (all test_p1*.py)": "tests/test_p1",
    "rd6b differential chunks": "test_readings_rd6b_differential.py::test_generated_documents_agree",
    "english mixed merge smoke": "test_english_evidence.py::test_english_mixed_merge_smoke",
    "risk margins (profiled, not split)": "test_risk_margins.py::",
}


def tests(path: Path) -> tuple[dict[str, float], dict]:
    seconds: dict[str, float] = defaultdict(float)
    run = {}
    for line in path.read_text().splitlines():
        if match := LINE.match(line.strip()):
            seconds[match[3]] += float(match[1])
        elif match := WALL.search(line):
            run = {"passed": int(match[1]), "pytest_wall_seconds": float(match[2])}
    return dict(seconds), run


def group(seconds: dict[str, float], key) -> dict:
    keys = key if isinstance(key, tuple) else (key,)
    rows = {nodeid: value for nodeid, value in seconds.items() if any(k in nodeid for k in keys)}
    longest = max(rows.items(), key=lambda row: row[1], default=(None, 0.0))
    return {"tests_timed": len(rows), "seconds_sum": round(sum(rows.values()), 1),
            "longest_seconds": round(longest[1], 1), "longest_test": longest[0]}


def rd6b_inputs() -> dict:
    from tests.test_readings_rd6b_differential import CHUNKS, DOCUMENTS
    partition = {name: [list(range(chunk, DOCUMENTS, chunks)) for chunk in range(chunks)]
                 for name, chunks in (("before", 10), ("after", CHUNKS))}
    return {name: {"chunks": len(parts), "documents": sum(map(len, parts)),
                   "distinct": len({i for part in parts for i in part}), "largest_chunk": max(map(len, parts))}
            for name, parts in partition.items()}


def english_inputs() -> dict:
    from conformance import english_mixed
    from tests.test_english_evidence import MIXED, MIXED_PARTS
    before = {'news-article-reviewed': 4, 'claude-constitution-excerpt-reviewed': 3, 'news-article': 2}
    rows = {}
    for name in sorted(set(before) | set(MIXED_PARTS)):
        with contextlib.redirect_stdout(io.StringIO()):  # the harness prints each configuration's row
            corpus = english_mixed.mixed(1, only={MIXED.index(name)}, check=False)["texts"]
        rows[name] = {"documents": corpus, **{
            label: {"parts": parts.get(name, 1),
                    "documents_per_part": [len(range(part, corpus, parts.get(name, 1)))
                                           for part in range(parts.get(name, 1))]}
            for label, parts in (("before", before), ("after", MIXED_PARTS))}}
        for label in ("before", "after"):
            assert sum(rows[name][label]["documents_per_part"]) == corpus
    return rows


def main() -> int:
    before, before_run = tests(EVIDENCE / "mac-before-durations.txt")
    after, after_run = tests(EVIDENCE / "mac-after-durations.txt")
    out = {"machine": "ve-mac-1 (aarch64), mac-pytest.sh, 6 xdist workers, the longest-first scheduler",
           "before": {"commit": "dae12d5ffd2622f584a164af3e5a2ee955e71f20", **before_run,
                      "longest": group(before, "tests/")},
           "after": {**after_run, "longest": group(after, "tests/")},
           "groups": {name: {"before": group(before, key), "after": group(after, key)}
                      for name, key in GROUPS.items()},
           "inputs": {"rd6b": rd6b_inputs(), "english_mixed": english_inputs()}}
    (EVIDENCE / "measure.json").write_text(json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
