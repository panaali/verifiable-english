"""Python-side seeded bugs of lean-first batch 2: plant one at a time, run the tests that must catch it, revert
(git checkout). `uv run --frozen python docs/lean-first/b2/seeds.py`"""
import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools import nested_pytest  # noqa: E402
SEEDS = [
  ("S1 handle answers equal re-sending: every case is sent with the first environment's handle",
   "ve/backends/lean_service.py",
   "        if id(environment) not in texts:\n",
   "        if not texts:\n",
   "        text, digest = texts[id(environment)]\n",
   "        text, digest = next(iter(texts.values()))\n",
   ["tests/test_lean_handles.py::test_handles_answer_the_evaluation_corpus_as_resending_does"]),
  ("S2 a miss is resent: the client raises instead of resending",
   "ve/backends/lean_service.py",
   "                with self._lock:\n                    self.stats[\"handle_resends\"] += 1\n",
   "                raise CheckerUnavailable(\"CheckerUnavailable: seeded: no resend\")\n",
   None, None,
   ["tests/test_lean_handles.py::test_a_missed_handle_is_resent_with_its_environment"]),
  ("S3 the client mirrors the service's eviction: it never empties its table",
   "ve/backends/lean_service.py",
   "        if len(self._registered) + 1 > MAX_HANDLES or self._handle_bytes + size > MAX_HANDLE_BYTES:\n            self._forget_handles()\n",
   "",
   None, None,
   ["tests/test_lean_handles.py::test_the_client_mirrors_the_services_eviction"]),
  ("S4 a Rust process that gives no record is killed: a timed-out process goes back to the idle list",
   "ve/backends/rust_jsonl.py",
   "    finally:\n        if not answered:\n            checker.close()\n",
   "    finally:\n        if not answered:\n            _idle.setdefault(tuple(checker.argv), []).append(checker)\n",
   None, None,
   ["tests/test_lean_handles.py::test_a_rust_process_that_times_out_is_killed_and_not_reused"]),
  ("S5 a Rust process is reused only while its executable is unchanged: identity ignored",
   "ve/backends/rust_jsonl.py",
   "            if self.process.poll() is not None or _identity(self.argv[0]) != self.identity:\n",
   "            if self.process.poll() is not None:\n",
   None, None,
   ["tests/test_lean_handles.py::test_a_replaced_rust_executable_gets_a_new_process"]),
  ("S6 the same request is asked once per pool: one memo shared by every pool",
   "ve/backends/relay.py",
   "    pool = _pool_for(None)\n    key = (mode,",
   "    pool = _pool_for(None)\n    pool = _close\n    key = (mode,",
   None, None,
   ["tests/test_lean_handles.py::test_lean_background_is_asked_once_per_request",
    "tests/test_stage2_faults.py::test_lean_faults_fail_closed_in_every_adapter"]),
]
results = []
for name, path, old, new, old2, new2, tests in SEEDS:
    p = Path(path); s = p.read_text()
    assert old in s, name
    s = s.replace(old, new, 1)
    if old2:
        assert old2 in s, name
        s = s.replace(old2, new2, 1)
    p.write_text(s)
    try:
        proc = subprocess.run(nested_pytest.command(["-q", "-x", *tests], workers=4),
                              env=nested_pytest.environment(os.environ), capture_output=True, text=True, timeout=1500)
        tail = [l for l in proc.stdout.splitlines() if l.strip()][-1]
        results.append((name, proc.returncode, tail))
        print(name, "->", "CAUGHT" if proc.returncode != 0 else "MISSED", "|", tail, flush=True)
    finally:
        subprocess.run(["git", "checkout", "--", path], check=True)
print("all caught" if all(r[1] != 0 for r in results) else "SOME MISSED")
