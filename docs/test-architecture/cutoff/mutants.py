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
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "tools")]
import nested_pytest  # noqa: E402
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
     "    if rule is not None or (args.run and not args.full):  # tarch-cutoff hook (see --cutoff); R1 takes R1_RULE\n",
     "    if rule is not None or not args.full:  # tarch-cutoff hook (see --cutoff); R1 takes R1_RULE\n",
     "a plan print, which verify.sh's legacy fast gate reads, takes R1's rule",
     TESTS + "test_a_feedback_run_takes_the_r1_rule_and_nothing_else_does"),
    ("M21", "tools/answer_cutoff.py", 'R1_RULE: str | None = "modes"\n', 'R1_RULE: str | None = "answers=diff.json"\n',
     "R1 takes the answers rule before the DRI has read its measurement",
     TESTS + "test_r1_never_takes_the_answers_rule"),
    ("M14", "tools/select_tests.py",
     "        plan = answer_cutoff.select(rule, paths, full=args.full, base=base, after=after,\n",
     "        plan = answer_cutoff.select(\"modes\", paths, full=args.full, base=base, after=after,\n",
     "the hook ignores the rule it was given",
     TESTS + "test_the_hook_passes_its_rule_and_is_off_by_default"),
    # The review's surviving mutants (tarch-cutoff-review.final.md F1) and the branches next to them.
    ("M22", "tools/answer_cutoff.py",
     "        return found - self.client_pin_readers if path == PIN_FILE else found\n",
     "        return found - self.client_pin_readers\n",
     "the pin exemption drops a client-only pin reader from the readers of every file",
     TESTS + "test_the_pin_exemption_is_for_the_pins_only"),
    ("M23", "tools/answer_cutoff.py", "        return build in json.loads(text)[\"ve_service\"]\n",
     "        return True\n", "every build counts as pinned",
     TESTS + "test_pinned_reads_the_pins_of_the_tree_or_of_a_commit"),
    ("M24", "tools/answer_cutoff.py",
     "    head_pinned = pinned(build, after) if head_pinned is None else head_pinned\n",
     "    head_pinned = True\n", "a pin change exempts client-only pin readers when the new build is not pinned",
     TESTS + "test_the_pin_exemption_and_the_stale_answers_reach_the_plan"),
    ("M25", "tools/answer_cutoff.py",
     "    client_only = {unit for unit, entry in index[\"units\"].items() if entry[\"pins\"] == [\"client\"]} - since\n",
     "    client_only = {unit for unit, entry in index[\"units\"].items() if entry[\"pins\"] == [\"client\"]}\n",
     "a unit that ran code changed since the recording keeps its recorded pin exemption",
     TESTS + "test_the_pin_exemption_and_the_stale_answers_reach_the_plan"),
    ("M26", "tools/answer_cutoff.py",
     "    unknown = unknown_units(index, today, graph, since, stale=frozenset(diff.get(\"stale\", ())))\n",
     "    unknown = unknown_units(index, today, graph, since)\n",
     "the diff's stale answers do not make their readers unknown",
     TESTS + "test_the_pin_exemption_and_the_stale_answers_reach_the_plan"),
    ("M27", "tools/answer_cutoff.py", "        return everyone & (users | unknown)\n",
     "        return users | unknown\n", "a recorded user that starts no ve_service today is selected",
     TESTS + "test_answers_rule_selects_changed_and_unknown_users_only"),
    ("M28", "tools/answer_cutoff.py",
     "        property_tests = path == unit or not Path(path).name.startswith(\"test_\")\n",
     "        property_tests = path == unit\n", "hypothesis in a helper module the unit imports is not counted",
     TESTS + "test_property_tests_count_in_the_unit_and_its_helpers_but_not_in_another_test_file"),
    ("M29", "tools/answer_cutoff.py",
     "        property_tests = path == unit or not Path(path).name.startswith(\"test_\")\n",
     "        property_tests = True\n", "another test file's property tests count in the unit that imports it",
     TESTS + "test_property_tests_count_in_the_unit_and_its_helpers_but_not_in_another_test_file"),
    ("M30", "tools/answer_replay.py", "    return [ask(service, mode, [text])[0] for text in texts]\n",
     "    return [ask(service, mode, [texts[0]])[0]] * len(texts)\n",
     "a refused batch gives every case the first case's answer",
     TESTS + "test_a_refused_batch_is_asked_again_case_by_case"),
    ("M31", "tools/answer_cutoff.py", 'R1_RULE: str | None = "modes"\n', "R1_RULE: str | None = None\n",
     "R1 loses ts-B2's per-mode rule the report activates", TESTS + "test_a_feedback_run_takes_the_modes_rule"),
    ("M32", "tools/answer_replay.py",
     "        return [answer_digest({key: value for key, value in response.items() if key != \"id\"})]\n",
     "        return [answer_digest(response)]\n", "a refusal's answer holds its nonce, which differs per request",
     TESTS + "test_a_refused_batch_is_asked_again_case_by_case"),
    ("M33", "tools/answer_replay.py",
     "            return [f\"{UNREPLAYABLE}: the case does not fit one request line inline\"]\n",
     "            return [\"raised: ResourceLimit\"]\n",
     "a case the client cannot send counts as replayed", TESTS + "test_a_refused_batch_is_asked_again_case_by_case"),
    ("M34", "tools/answer_cutoff.py", "    if data[\"commit\"] != index[\"commit\"]:\n", "    if False:\n",
     "a request index and a map of different commits are read as one recording",
     TESTS + "test_select_answers_refuses_a_diff_it_cannot_trust"),
    ("M35", "tools/answer_cutoff.py", "            return f\"{path} does not parse\"\n", "            continue\n",
     "a unit whose test code does not parse is not unknown", TESTS + "test_a_unit_that_does_not_parse_is_unknown"),
    ("M36", "tools/answer_cutoff.py", "UNSEEDED[module] is None and name != \"Random\"",
     "UNSEEDED[module] is None", "importing the seedable random.Random makes a unit unknown",
     TESTS + "test_seeded_randomness_is_not_unknown"),
    ("M37", "tools/answer_replay.py", "        if \"partial\" in side:\n", "        if False:\n",
     "a replay of some modes only is diffed as a whole one",
     TESTS + "test_diff_finds_changed_missing_and_unreplayable_answers"),
    ("M38", "tools/answer_replay.py", "        lost = [key for key in keys\n", "        lost = [key for key in keys if False\n",
     "a case whose environment the recording lacks is sent as it is",
     TESTS + "test_replay_answers_each_case_as_recorded_and_again_alike"),
]


def pytest(test: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", "-x", test],
                                                python=[str(ROOT / ".venv/bin/python")]),
                          cwd=ROOT, text=True, capture_output=True, timeout=HANG_TIMEOUT,
                          env=nested_pytest.environment(os.environ, VE_NATIVE_PREBUILT="1", VE_LEAN_PREBUILT="1"))


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
