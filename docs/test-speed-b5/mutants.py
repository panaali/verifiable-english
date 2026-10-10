"""Seeded bugs for test speed B5: one per behaviour the batch claims. Each is applied alone, its test is run (it
must fail), and the source is restored and checked byte for byte. Writes `evidence/mutants.json`.

    uv run python docs/test-speed-b5/mutants.py
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import nested_pytest  # noqa: E402

HERE = Path(__file__).resolve().parent
ORDER, GATE = "tests/test_test_order.py", "tests/test_gate_quarantine.py"

# (id, behaviour, file, original, mutant, test)
MUTANTS = [
    ("changed_before_failed", "the tests that failed last time start first", "tools/test_order.py",
     "    return ([unit for unit in units if unit in failed]\n"
     "            + [unit for unit in units if unit in changed and unit not in failed]",
     "    return ([unit for unit in units if unit in changed and unit not in failed]\n"
     "            + [unit for unit in units if unit in failed]",
     f"{ORDER}::test_the_last_failed_then_the_changed_then_the_rest"),
    ("passed_units_stay_failed", "a unit that runs to the end leaves the last failures", "tools/test_order.py",
     "    state = {unit: list(ids) for unit, ids in previous.items() if unit not in set(completed)}",
     "    state = {unit: list(ids) for unit, ids in previous.items()}",
     f"{ORDER}::test_a_unit_leaves_the_last_failures_when_it_runs_to_the_end"),
    ("recorded_run_never_stops", "a recorded run stops after --maxfail failed tests", "tools/test_map.py",
     "            if stop_after and failed >= stop_after and not stop.stopped:",
     "            if stop_after and failed > stop_after and not stop.stopped:",
     f"{ORDER}::test_a_recorded_run_stops_after_maxfail_failures"),
    ("plain_run_ignores_maxfail", "a one-process run stops after --maxfail failed tests", "tools/select_tests.py",
     '        command = [*PYTEST, *options, *([f"--maxfail={maxfail}"] if maxfail else []),',
     '        command = [*PYTEST, *options,',
     f"{ORDER}::test_a_plain_run_stops_after_maxfail_and_keeps_what_it_did_not_run"),
    ("plain_run_counts_quarantined", "a quarantined failure does not fail an agent's run", "tools/select_tests.py",
     "    if code == 1 and failed and not set(failed) - held:",
     "    if code == 1 and failed and not set(failed):",
     f"{ORDER}::test_a_plain_run_whose_only_failures_are_quarantined_passes"),
    ("gate_plugin_allows_maxfail", "the gate never stops early", "tools/gate_pytest.py",
     "    if early:\n        raise pytest.UsageError(",
     "    if early and False:\n        raise pytest.UsageError(",
     f"{GATE}::test_the_gates_plugin_refuses_to_stop_early"),
    ("retry_failure_ignored", "a quarantined test that fails alone still fails the gate", "tools/gate.py",
     '        if outcome == "passed":\n            result["failures"] = [failure for failure in result["failures"]',
     '        if outcome != "skipped":\n            result["failures"] = [failure for failure in result["failures"]',
     f"{GATE}::test_a_quarantined_failure_that_fails_alone_fails_the_gate"),
    ("nightly_retries", "the nightly (--no-quarantine) retries nothing", "tools/gate.py",
     "            retry_quarantined(result, events, pytest_env, python, scratch, enabled=not args.no_quarantine)",
     "            retry_quarantined(result, events, pytest_env, python, scratch, enabled=True)",
     f"{GATE}::test_the_nightly_retries_nothing"),
    ("expired_entry_applies", "an expired entry no longer applies", "tools/quarantine.py",
     "            if datetime.date.fromisoformat(entry[\"added\"]) <= day <= "
     "datetime.date.fromisoformat(entry[\"expires\"])}",
     "            if datetime.date.fromisoformat(entry[\"added\"]) <= day}",
     f"{GATE}::test_an_entry_applies_from_its_added_day_to_its_expiry"),
    ("eight_day_entry", "an entry lives at most seven days", "tools/quarantine.py",
     "        if not added <= expires <= added + datetime.timedelta(days=MAX_DAYS):",
     "        if not added <= expires:",
     f"{GATE}::test_a_malformed_entry_is_refused"),
]


def run(test: str) -> int:
    command = nested_pytest.command(["-q", "-p", "no:cacheprovider", "-p", "no:randomly", test],
                                    python=[sys.executable])
    env = nested_pytest.environment(os.environ, VE_NATIVE_PREBUILT="1")
    return subprocess.run(command, cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode


def main() -> int:
    rows = []
    for name, behaviour, file, original, mutant, test in MUTANTS:
        path = ROOT / file
        before = path.read_bytes()
        text = before.decode()
        if text.count(original) != 1:
            raise SystemExit(f"{name}: the original text is not in {file} exactly once")
        try:
            path.write_text(text.replace(original, mutant))
            code = run(test)
        finally:
            path.write_bytes(before)
        if hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(before).digest():
            raise SystemExit(f"{name}: {file} was not restored")
        rows.append({"id": name, "behaviour": behaviour, "file": file, "test": test, "exit": code,
                     "caught": code == 1})
        print(f"{name}: {file}: {test} exit {code} ({'caught' if code == 1 else 'MISSED'})", flush=True)
    clean = {test: run(test) for test in sorted({row["test"] for row in rows})}
    (HERE / "evidence/mutants.json").write_text(json.dumps(
        {"mutants": rows, "clean": clean, "language": "Python"}, indent=1) + "\n")
    missed = [row["id"] for row in rows if not row["caught"]] + [test for test, code in clean.items() if code]
    print(f"{len(rows) - len(missed)} of {len(rows)} caught; clean source passes: {not any(clean.values())}")
    return 1 if missed else 0


if __name__ == "__main__":
    raise SystemExit(main())
