"""The answer-store batch's seeded bugs, run on the test runner in one job (copy into tests/ to run; not collected here).

Each mutant replaces one text in one changed file, runs the tests that should catch it in a nested pytest,
and restores the file byte for byte."""
import json
import os
from pathlib import Path
import subprocess

from subprocesses import HANG_TIMEOUT
from tools import nested_pytest

ROOT = Path(__file__).resolve().parents[1]
LS, AS, T = "ve/backends/lean_service.py", "tests/answer_store.py", "tests/test_answer_store.py"
MUTANTS = [
    ("M1", LS, "stored line skips the client's checks",
     "            self._buffer += stored + b\"\\n\"\n        raw = self._read_line(deadline)",
     "            return stored, _decode_json(stored)\n        raw = self._read_line(deadline)",
     [f"{T}::test_a_planted_positional_mismatch_is_refused_not_served"]),
    ("M2", LS, "store-mode nonce random, not derived from the line",
     "        if store is None:\n            return nonce, self._request_line(",
     "        if True:\n            return nonce, self._request_line(",
     [f"{T}::test_a_store_mode_line_stands_alone", f"{T}::test_a_stored_answer_is_served_after_the_process_starts"]),
    ("M3", LS, "store mode registers only the environments the process lacks",
     "needed = (dict(environments) if store is not None else",
     "needed = (dict(environments) if False else",
     [f"{T}::test_a_store_mode_line_stands_alone"]),
    ("M4", LS, "the store answers before _ensure (no spawn, pin check or handshake on a hit)",
     "                try:\n                    self._ensure()\n                    if environments:",
     "                try:\n                    (self._ensure() if store is None else None)\n                    if environments:",
     [f"{T}::test_a_stored_answer_is_served_after_the_process_starts"]),
    ("M5", LS, "RLIMIT_AS not applied to the process",
     "                resource.prlimit(self._proc.pid, resource.RLIMIT_AS, (limit, limit))",
     "                pass",
     ["tests/test_lean_service.py::test_the_service_runs_under_its_address_space_limit"]),
    ("M6", LS, "RSS recycle disabled",
     "            if rss is not None and rss > self.max_rss:",
     "            if rss is not None and rss > self.max_rss and False:",
     ["tests/test_lean_service.py::test_a_process_above_its_rss_threshold_is_recycled_before_the_next_request"]),
    ("M7", AS, "no gate check in the seam",
     "        if os.environ.get(GATE_FLAG):\n            return \"gate\"\n",
     "",
     [f"{T}::test_a_store_hit_in_an_r2_flagged_run_is_impossible"]),
    ("M8", AS, "the plugin accepts the store under the gate",
     "    if environ.get(GATE_FLAG):\n        raise pytest.UsageError(",
     "    if False:\n        raise pytest.UsageError(",
     [f"{T}::test_a_store_hit_in_an_r2_flagged_run_is_impossible"]),
    ("M9", AS, "live_service tests served",
     "        if self.live:\n            return \"live_service test\"",
     "        if False:\n            return \"live_service test\"",
     [f"{T}::test_a_live_service_test_is_never_served_and_is_counted",
      f"{T}::test_serving_is_off_for_every_request_the_plan_excludes"]),
    ("M10", AS, "client replaced by a test still served",
     "        if any(LeanService.__dict__.get(name) is not self.methods[name] or name in vars(service) for name in SEAM):",
     "        if False:",
     [f"{T}::test_serving_is_off_for_every_request_the_plan_excludes"]),
    ("M11", AS, "ve/backends/ not guarded",
     "GUARDED = (\"ve/backends/\", ", "GUARDED = (",
     [f"{T}::test_serving_is_off_for_a_branch_that_changes_a_guarded_path"]),
    ("M12", AS, "the byte replay compares decoded values, not bytes",
     "                    if answer == expected and not written:",
     "                    if json.loads(answer) == json.loads(expected) and not written:",
     [f"{T}::test_a_planted_wrong_entry_fails_the_byte_replay",
      f"{T}::test_a_planted_nondeterministic_answer_fails_the_byte_replay"]),
    ("M13", AS, "a CheckerUnavailable request error is recorded",
     "        if response.get(\"status\") == \"error\" and response.get(\"code\") == \"CheckerUnavailable\":",
     "        if False:",
     [f"{T}::test_a_checker_unavailable_request_error_is_never_recorded"]),
    ("M14", AS, "a sampled hit is served without the live comparison",
     "        if self.rng.random() < self.sample:",
     "        if False:",
     [f"{T}::test_a_sampled_hit_that_drifted_is_an_alarm_and_the_caller_gets_the_process_answer"]),
    # The review fix round (tarch-store-review.final.md F1, F2)
    ("M15", AS, "an answer whose request wrote to standard error (a PANIC) is stored",
     "        _, written = service.stderr(start)\n        if written:\n",
     "        _, written = service.stderr(start)\n        if False:\n",
     [f"{T}::test_an_answer_whose_request_wrote_to_standard_error_is_never_served"]),
    ("M16", AS, "the byte replay ignores standard error",
     "                    if answer == expected and not written:",
     "                    if answer == expected:",
     [f"{T}::test_an_answer_whose_request_wrote_to_standard_error_is_never_served"]),
    ("M17", LS, "the retry after a failed live attempt still uses the store (and records)",
     "                    if store is not None:  # a refused stored line or a failed process",
     "                    if stored is not None:  # a refused stored line or a failed process",
     [f"{T}::test_an_answer_that_needed_a_retry_is_never_stored"]),
    ("M18", AS, "a client table changed in place (a lowered DEADLINES entry) is still served",
     "        if any(self.globals[name] != value for name, value in self.tables.items()):",
     "        if False:",
     [f"{T}::test_a_changed_client_setting_turns_the_store_off"]),
    ("M19", AS, "a changed VE_LEAN_SERVICE* setting is still served",
     "        if self._environment() != self.environment:",
     "        if False:",
     [f"{T}::test_a_changed_client_setting_turns_the_store_off"]),
    ("M20", AS, "the plugin never reads the live_service mark (PROBE F2)",
     "item.get_closest_marker(LIVE_MARK) is not None",
     "False",
     [f"{T}::test_the_plugin_serves_only_unmarked_tests_and_an_alarm_fails_the_run"]),
    ("M21", AS, "an alarm never fails the run",
     "    if summary[\"alarms\"] and session.exitstatus == 0:",
     "    if False:",
     [f"{T}::test_the_plugin_serves_only_unmarked_tests_and_an_alarm_fails_the_run"]),
    ("M22", AS, "the workers' reports are dropped (pytest_testnodedown)",
     "        reports.append(report)",
     "        pass",
     [f"{T}::test_the_plugin_serves_only_unmarked_tests_and_an_alarm_fails_the_run"]),
]


def run(tests):
    env = nested_pytest.environment(os.environ, VE_NATIVE_PREBUILT="1")
    result = subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", *tests]), cwd=ROOT, env=env,
                            capture_output=True, text=True, timeout=HANG_TIMEOUT)
    return result.returncode, result.stdout.strip().splitlines()[-1:] if result.stdout.strip() else []


def test_seeded_bugs():
    results = []
    every = sorted({t for *_, tests in MUTANTS for t in tests})
    baseline = run(every)
    results.append({"id": "baseline", "returncode": baseline[0], "tail": baseline[1]})
    for mid, path, fault, old, new, tests in MUTANTS:
        file = ROOT / path
        original = file.read_bytes()
        text = original.decode()
        assert text.count(old) == 1, (mid, text.count(old))
        file.write_text(text.replace(old, new))
        try:
            code, tail = run(tests)
        finally:
            file.write_bytes(original)
        results.append({"id": mid, "file": path, "fault": fault, "tests": tests, "returncode": code, "tail": tail,
                        "result": "failed" if code == 1 else f"exit {code}"})
    print("\nMUTANTS " + json.dumps(results))
    assert baseline[0] == 0
    assert all(row["returncode"] == 1 for row in results[1:]), [r["id"] for r in results[1:] if r["returncode"] != 1]
