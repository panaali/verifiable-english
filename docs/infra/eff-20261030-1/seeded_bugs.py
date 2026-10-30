"""Seeded bugs of eff-20261030-1: plant each in the product file, show the named test fails, restore the file.

    uv run python docs/infra/eff-20261030-1/seeded_bugs.py [--json docs/infra/eff-20261030-1/seeded-bugs.json]

Each bug is one exact text replacement (it must occur once); the test must fail (pytest exit 1) with the bug and
the file is restored byte for byte afterwards, whatever happens. Exit 0 only when every bug was caught.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
TESTS = "tests/test_test_chunks.py"
BUGS = [
    {"bug": "the chunk rule drops the last node", "file": "tools/test_chunks.py",
     "old": "    nodes = sorted(set(nodeids))\n", "new": "    nodes = sorted(set(nodeids))[:-1]\n",
     "test": f"{TESTS}::test_the_parts_cover_every_node_exactly_once"},
    {"bug": "the union check is skipped", "file": "tools/select_tests.py",
     "old": "        problems = chunk_problems(file, counts[file], listings.get(file), ran, seconds)\n",
     "new": "        problems = []\n",
     "test": f"{TESTS}::test_a_test_missing_from_every_chunk_fails_the_unit"},
    {"bug": "a failed chunk is ignored", "file": "tools/select_tests.py",
     "old": "    failed = [code for code in exits if code not in (0, NO_TESTS_COLLECTED)]\n",
     "new": "    failed = []\n",
     "test": f"{TESTS}::test_a_failed_chunk_fails_the_unit"},
    {"bug": "the map keeps only chunk 1's edges", "file": "tools/select_tests.py",
     "old": "    result = {key: set().union(*(done[index][key] for index in done)) for key in test_map.EDGE_KEYS}\n",
     "new": "    result = {key: set(done[min(done)][key]) for key in test_map.EDGE_KEYS}\n",
     "test": f"{TESTS}::test_the_map_entry_of_a_chunked_file_is_the_union_of_its_chunks"},
    {"bug": "chunking is applied to a full run", "file": "tools/select_tests.py",
     "old": "        return run_recorded(plan, jobs, maxfail, held, chunked=not full)\n",
     "new": "        return run_recorded(plan, jobs, maxfail, held, chunked=True)\n",
     "test": f"{TESTS}::test_a_full_run_never_chunks"},
    {"bug": "a setup-dominated file is chunked", "file": "tools/select_tests.py",
     "old": "        if row is None or row.get(\"never\") or unit in EXTRA_UNITS or recorded <= CHUNK_SECONDS:\n",
     "new": "        if row is None or unit in EXTRA_UNITS or recorded <= CHUNK_SECONDS:\n",
     "test": f"{TESTS}::test_a_setup_dominated_file_is_never_chunked"},
    {"bug": "the plan lists chunks without --chunk-heavy", "file": "tools/select_tests.py",
     "old": "    if args.chunk_heavy:\n        plan = chunk_plan(plan)\n",
     "new": "    if True:\n        plan = chunk_plan(plan)\n",
     "test": f"{TESTS}::test_the_plan_lists_chunks_only_with_the_option"},
    {"bug": "a chunk's failures do not count towards --maxfail", "file": "tools/select_tests.py",
     "old": "        failures=lambda unit, result: len(set(unit_failures(file_of(unit), result, reports[unit])) - held))\n",
     "new": "        failures=lambda unit, result: 0 if file_of(unit) != unit else len(set(unit_failures(unit, result, "
            "reports[unit])) - held))\n",
     "test": f"{TESTS}::test_maxfail_stops_across_chunks_as_across_units"},
    {"bug": "the suite's conftest does not register the chunk hook", "file": "tests/conftest.py",
     "old": "    test_chunks.register(config, test_schedule.read_durations)\n", "new": "",
     "test": f"{TESTS}::test_the_suites_conftest_applies_the_chunk"},
    {"bug": "a nested run inherits the chunk", "file": "tools/nested_pytest.py",
     "old": "AMBIENT_NAMES = (\"VE_TEST_PROFILE_DIR\", test_chunks.VARIABLE)",
     "new": "AMBIENT_NAMES = (\"VE_TEST_PROFILE_DIR\",)",
     "test": f"{TESTS}::test_a_nested_run_never_inherits_the_chunk"},
    {"bug": "the hook keeps the chunk before -m deselects", "file": "tools/test_chunks.py",
     "old": "        @pytest.hookimpl(trylast=True)\n", "new": "        @pytest.hookimpl(tryfirst=True)\n",
     "test": f"{TESTS}::test_the_chunk_applies_after_marker_deselection"},
    {"bug": "JUnit node IDs drop the class", "file": "tools/run_order.py",
     "old": "            nodeid = \"::\".join([unit, *classname.removeprefix(module + \".\").split(\".\"), name])\n",
     "new": "            nodeid = f\"{unit}::{name}\"\n",
     "test": f"{TESTS}::test_junit_cases_are_the_node_ids_of_the_file"},
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    rows, caught = [], True
    for bug in BUGS:
        path = ROOT / bug["file"]
        original = path.read_bytes()
        text = original.decode()
        if text.count(bug["old"]) != 1:
            raise SystemExit(f"{bug['bug']}: the text to replace occurs {text.count(bug['old'])} times in {bug['file']}")
        try:
            path.write_text(text.replace(bug["old"], bug["new"]))
            done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-n", "0",
                                   bug["test"]], cwd=ROOT, capture_output=True, text=True, check=False)
        finally:
            path.write_bytes(original)
        failed = done.returncode == 1 and "failed" in done.stdout.splitlines()[-1]
        caught &= failed
        rows.append({"bug": bug["bug"], "file": bug["file"], "test": bug["test"], "exit": done.returncode,
                     "summary": done.stdout.strip().splitlines()[-1] if done.stdout.strip() else "",
                     "caught": failed})
        print(f"{'CAUGHT' if failed else 'MISSED'} {bug['bug']} ({bug['file']}): {bug['test']} -> {rows[-1]['summary']}",
              flush=True)
    if args.json:
        args.json.write_text(json.dumps(rows, indent=1) + "\n")
    return 0 if caught else 1


if __name__ == "__main__":
    raise SystemExit(main())
