"""Plant this batch's Python bugs one at a time, run the test that must reject each, and restore the source.

  .venv/bin/python docs/test-architecture/cutoff/mutants.py

Each case is (file, anchor, mutant, test): the anchor must occur once; the test must pass on the
restored file and fail on the mutant. Writes evidence/mutants.json.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests"))
from subprocesses import HANG_TIMEOUT  # noqa: E402

TESTS = "tests/test_answer_cutoff.py::"
CASES = [
    ("M1", "tools/test_map_recorder.py",
     "        timed = local[\"timeout\"] is not None or service.timeout is not None\n",
     "        timed = False\n", "requests with an explicit timeout are recorded as untimed",
     TESTS + "test_timeouts_and_data_reads_of_the_pins_are_recorded"),
    ("M2", "tools/test_map_recorder.py",
     "\"client\" if _caller() == (CLIENT, \"_spawn\") else \"data\"", "\"client\"",
     "every read of the pins counts as the client's pin check",
     TESTS + "test_timeouts_and_data_reads_of_the_pins_are_recorded"),
    ("M3", "tools/test_map_recorder.py",
     "        os.environ.setdefault(\"VE_TESTMAP_REQUESTS_UNIT\", os.path.basename(os.path.normpath(_state[\"out\"])))\n",
     "        os.environ[\"VE_TESTMAP_REQUESTS_UNIT\"] = os.path.basename(os.path.normpath(_state[\"out\"]))\n",
     "a nested recording's requests count for its own output, not the outer unit",
     TESTS + "test_a_child_and_a_nested_recording_send_for_the_outer_unit"),
    ("M4", "tools/test_map_recorder.py",
     "        if (_relative(frame.f_code.co_filename), frame.f_code.co_name) != (CLIENT, \"exchange\"):\n"
     "            raise LookupError(\"the mode event was not raised by the client's exchange\")\n", "",
     "a mode event from outside the client is not marked unknown",
     TESTS + "test_service_uses_the_record_cannot_replay_make_the_unit_unknown"),
    ("M5", "tools/answer_cutoff.py",
     "    return [line for line in path.read_text(encoding=\"utf-8\").split(\"\\n\") if line]\n",
     "    return [line for line in path.read_text(encoding=\"utf-8\").splitlines() if line]\n",
     "record files split at U+2028 inside a case text",
     TESTS + "test_recorder_records_each_case_the_client_sent"),
    ("M6", "tools/answer_cutoff.py", "        return everyone & (users | unknown)\n",
     "        return everyone & users\n", "unknown service users are not selected",
     TESTS + "test_answers_rule_selects_changed_and_unknown_users_only"),
    ("M7", "tools/answer_cutoff.py",
     "REQUEST_HANDLING = (\"lean/VE/Service/Protocol.lean\", \"lean/Serve.lean\", \"lean/VE/Json.lean\")\n",
     "REQUEST_HANDLING = (\"lean/VE/Service/Protocol.lean\", \"lean/Serve.lean\")\n",
     "a change to request decoding (lean/VE/Json.lean) narrows by answers",
     TESTS + "test_request_handling_and_project_changes_select_every_service_user"),
    ("M8", "tools/answer_cutoff.py",
     "        return found - self.client_pin_readers if path == PIN_FILE else found\n",
     "        return set() if path == PIN_FILE else found\n", "a pin change selects no pin reader at all",
     TESTS + "test_a_pin_change_selects_only_data_readers_when_the_new_build_is_pinned"),
    ("M9", "tools/answer_cutoff.py",
     "        elif entry[\"timed\"]:\n            found[unit] = \"a request with an explicit timeout\"\n", "",
     "a unit with an explicitly timed request is not unknown",
     TESTS + "test_answers_rule_selects_changed_and_unknown_users_only"),
    ("M10", "tools/answer_cutoff.py",
     "    if diff[\"head\"] != build:\n", "    if False:\n",
     "a diff of another build than the one the tests run is accepted",
     TESTS + "test_select_answers_refuses_a_diff_it_cannot_trust"),
    ("M11", "tools/answer_replay.py", "                     or base[\"answers\"][key].startswith(UNREPLAYABLE))", ")",
     "a case neither side could replay counts as unchanged",
     TESTS + "test_diff_finds_changed_missing_and_unreplayable_answers"),
    ("M12", "tools/answer_replay.py",
     "    return hashlib.sha256(json.dumps(response, ensure_ascii=False, separators=(\",\", \":\"))\n",
     "    return hashlib.sha256(json.dumps(response, ensure_ascii=False, separators=(\",\", \":\"), sort_keys=True)"
     ".replace(\"true\", \"1\")\n", "the answer digest equates true with 1",
     TESTS + "test_diff_finds_changed_missing_and_unreplayable_answers"),
    ("M13", "tools/answer_cutoff.py",
     "                if module == \"random\" and name == \"Random\" and (node.args or node.keywords):\n",
     "                if module == \"random\":\n", "unseeded calls of the random module are not unknown",
     TESTS + "test_randomised_inputs_make_a_unit_unknown"),
    ("M15", "tools/answer_cutoff.py",
     "        elif stale and any(keys[i] in stale for i in entry[\"keys\"]):\n",
     "        elif False:\n", "a unit that read an answer the base build changed is not unknown",
     TESTS + "test_a_unit_that_read_an_answer_the_base_build_changed_is_unknown"),
    ("M16", "tools/answer_cutoff.py",
     "    if diff[\"base\"] != index[\"service\"] and diff.get(\"recording_build\") != index[\"service\"]:\n",
     "    if False:\n", "a diff from another base build than the recording's is accepted without its stale answers",
     TESTS + "test_select_answers_refuses_a_diff_it_cannot_trust"),
    ("M17", "tools/answer_replay.py",
     "    if isinstance(result, dict) and \"case_index\" in result:\n",
     "    if False:\n", "an error result's batch position counts in its answer",
     TESTS + "test_a_case_answers_alike_alone_and_in_a_batch"),
    ("M18", "tools/answer_cutoff.py", "    today = select_tests.resolve_map(base, coverage)\n",
     "    today = recorded\n", "today's rules read the recording's map, not the one R1 reads",
     TESTS + "test_answers_read_todays_map_and_count_the_recordings_staleness"),
    ("M19", "tools/answer_cutoff.py",
     "    unknown = unknown_units(index, today, graph, since, stale=frozenset(diff.get(\"stale\", ())))\n",
     "    unknown = unknown_units(index, today, graph, set(), stale=frozenset(diff.get(\"stale\", ())))\n",
     "a unit that ran code changed since the recording keeps its recorded requests",
     TESTS + "test_answers_read_todays_map_and_count_the_recordings_staleness"),
    ("M20", "tools/select_tests.py",
     "    if rule is None and args.run and not args.full:  # tarch-cutoff hook (see --cutoff): R1's rule\n",
     "    if rule is None and not args.full:  # tarch-cutoff hook (see --cutoff): R1's rule\n",
     "a plan print, which verify.sh's legacy fast gate reads, takes R1's rule",
     TESTS + "test_a_feedback_run_takes_the_r1_rule_and_nothing_else_does"),
    ("M14", "tools/select_tests.py",
     "        plan = answer_cutoff.select(rule, paths, full=args.full, base=base, after=after,\n",
     "        plan = answer_cutoff.select(\"modes\", paths, full=args.full, base=base, after=after,\n",
     "the hook ignores the rule it was given",
     TESTS + "test_the_hook_passes_its_rule_and_is_off_by_default"),
]


def pytest(test: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(ROOT / ".venv/bin/python"), "-m", "pytest", "-q", "-p", "no:cacheprovider", "-x",
                           test], cwd=ROOT, text=True, capture_output=True, timeout=HANG_TIMEOUT,
                          env={**os.environ, "VE_NATIVE_PREBUILT": "1", "VE_LEAN_PREBUILT": "1"})


def main() -> None:
    records = []
    for ident, name, anchor, mutant, fault, test in CASES:
        path = ROOT / name
        original = path.read_text()
        if original.count(anchor) != 1:
            raise RuntimeError(f"{ident}: anchor missing or ambiguous in {name}")
        if pytest(test).returncode:
            raise RuntimeError(f"{ident}: {test} fails on the restored source")
        try:
            path.write_text(original.replace(anchor, mutant, 1))
            failed = pytest(test)
        finally:
            path.write_text(original)
        if failed.returncode == 0:
            raise RuntimeError(f"{ident}: the mutant was not caught by {test}")
        line = next((line for line in failed.stdout.splitlines() if line.startswith(("FAILED", "ERROR"))), "")
        records.append({"id": ident, "language": "python", "file": name, "fault": fault, "test": test,
                        "result": "failed", "failure": line[:300]})
        print(ident, name, "caught by", test, flush=True)
    output = Path(__file__).resolve().parent / "evidence/mutants.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"batch": "tarch-cutoff", "mutants": records}, indent=1) + "\n")
    print(f"{len(records)} seeded bugs caught; sources restored")


if __name__ == "__main__":
    main()
