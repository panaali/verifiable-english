"""The batch's seeded bugs: plant each one, run the tests that should catch it, record the outcome, restore the file.

    uv run --frozen python docs/test-architecture/slowtail/mutants.py docs/test-architecture/slowtail/seeded-mutants.json

Run on a clean tree; each file is restored after its run.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MUTANTS = [
 ("M1", "tools/test_schedule.py", "the scheduler drops an unmeasured test",
  "return [*order[:heads], *unknown, *(index for index in rest if index not in chosen)], len(unknown)",
  "return [*order[:heads], *unknown[1:], *(index for index in rest if index not in chosen)], len(unknown)",
  ["tests/test_test_schedule.py::test_unmeasured_tests_start_right_after_the_long_ones_in_shares_by_count",
   "tests/test_test_schedule.py::test_the_durations_source_never_changes_which_tests_run"]),
 ("M2", "tools/test_schedule.py", "the scheduler hands one test out twice",
  "return [*order[:heads], *unknown, *(index for index in rest if index not in chosen)], len(unknown)",
  "return [*order[:heads], *unknown, *(index for index in rest if index not in chosen), *unknown[:1]], len(unknown)",
  ["tests/test_test_schedule.py::test_unmeasured_tests_start_right_after_the_long_ones_in_shares_by_count",
   "tests/test_test_schedule.py::test_the_durations_source_never_changes_which_tests_run"]),
 ("M3", "tools/test_schedule.py", "the overlay changes the selection: unmeasured tests are left out",
  "return [*order[:heads], *unknown, *(index for index in rest if index not in chosen)], len(unknown)",
  "return [*order[:heads], *(index for index in rest if index not in chosen)], len(unknown)",
  ["tests/test_test_schedule.py::test_the_durations_source_never_changes_which_tests_run"]),
 ("M4", "tools/test_schedule.py", "the count cap is ignored",
  "least, max(least, len(self.pending) // share - len(held)))",
  "least)",
  ["tests/test_test_schedule.py::test_an_unrecorded_expensive_module_at_the_end_is_not_one_workers_run"]),
 ("M5", "tools/test_schedule.py", "unmeasured tests are not moved first",
  "    if measured is None:\n        return list(order), 0",
  "    if True:\n        return list(order), 0",
  ["tests/test_test_schedule.py::test_unmeasured_tests_start_right_after_the_long_ones_in_shares_by_count"]),
 ("M6", "tools/test_schedule.py", "the scheduler ignores the durations file the gate names",
  "    return Path(named) if named else DURATIONS",
  "    return DURATIONS",
  ["tests/test_test_schedule.py::test_the_suite_conftest_installs_the_scheduler"]),
 ("M7", "tools/gate.py", "a record without durations",
  "    result[\"durations\"] = test_schedule.record_field(seconds)\n",
  "",
  ["tests/test_gate_durations.py::test_the_gate_names_the_overlay_to_its_suite_and_records_the_suites_seconds",
   "tests/test_gate_durations.py::test_the_log_names_the_twenty_slowest_and_ignores_what_is_not_seconds"]),
 ("M8", "tools/gate.py", "the gate gives the suite the committed durations only, never the base's",
  "    found = base_durations(result, env)\n",
  "    found = None\n",
  ["tests/test_gate_durations.py::test_the_gate_names_the_overlay_to_its_suite_and_records_the_suites_seconds"]),
 ("M9", "tools/gate_pytest.py", "the event plugin times no test",
  "    _EVENTS[\"seconds\"][report.nodeid] = _EVENTS[\"seconds\"].get(report.nodeid, 0.0) + report.duration\n",
  "",
  ["tests/test_test_schedule.py::test_the_durations_source_never_changes_which_tests_run"]),
 ("M10", "tools/test_schedule.py", "the record field keeps short tests' mean as zero",
  "\"unrecorded_seconds\": data[\"unrecorded_seconds\"],",
  "\"unrecorded_seconds\": 0.0,",
  ["tests/test_gate_durations.py::test_the_record_field_keeps_the_recorded_tests_and_the_mean_of_the_others"]),
 ("M11", "tools/gate.py", "a base suite that did not time every test still names its measured tests",
  "    complete = type(timed) is int and timed == counts.get(\"selected\")",
  "    complete = True",
  ["tests/test_gate_durations.py::test_the_base_durations_come_from_the_base_gate_record"]),
 ("M12", "tools/bench/suite_tail.py", "the tail starts at the last worker's finish, not the busy-th",
  "\"tail_seconds\": round(last[0] - last[busy - 1], 1) if len(last) >= busy else None,",
  "\"tail_seconds\": round(last[0] - last[0], 1) if len(last) >= busy else None,",
  ["tests/test_suite_tail.py::test_tail_reads_when_each_worker_finished_its_last_test"]),
 ("M13", "tools/test_schedule.py", "the gate's durations file is named in a variable nested runs inherit",
  "SOURCE_VARIABLE = \"VE_GATE_PYTEST_DURATIONS\"",
  "SOURCE_VARIABLE = \"VE_TEST_DURATIONS\"",
  ["tests/test_test_schedule.py::test_a_nested_run_and_the_run_cache_never_see_the_gates_durations_file"]),
]
rows = []
for name, file, what, old, new, tests in MUTANTS:
    path = ROOT / file
    text = path.read_text()
    assert text.count(old) == 1, (name, old)
    path.write_text(text.replace(old, new))
    try:
        run = subprocess.run(["uv", "run", "--frozen", "pytest", "-q", "-p", "no:cacheprovider", *tests],
                             cwd=ROOT, env={**os.environ, "VE_NATIVE_PREBUILT": "1"},
                             capture_output=True, text=True, timeout=1800)
    finally:
        path.write_text(text)
    summary = [line for line in run.stdout.splitlines() if " passed" in line or " failed" in line or "error" in line][-1:]
    failed = sorted({line[len("FAILED "):].split(" - ")[0] for line in run.stdout.splitlines()
                     if line.startswith("FAILED ")})
    rows.append({"name": name, "file": file, "bug": what, "tests": tests, "failed": failed,
                 "caught": run.returncode != 0 and bool(failed), "summary": summary[0] if summary else ""})
    print(name, rows[-1]["caught"], rows[-1]["summary"], failed, flush=True)
Path(sys.argv[1]).write_text(json.dumps(rows, indent=1) + "\n")
sys.exit(0 if all(row["caught"] for row in rows) else 1)
