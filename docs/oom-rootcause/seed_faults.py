"""Plant each seeded fault of the OOM batch, prove its named test fails, then restore the source
(evidence/mutants.json). A Rust fault in the binary is built into the release binary, and the
Python tests run against it, trusting that build's hash for this run only (VE_RUST_SHA256).
After the last fault, the release binary is rebuilt from the restored source and its hash is
checked against the pin."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from tools import nested_pytest  # noqa: E402  (the one builder of a nested pytest command)
import rust_build  # noqa: E402

TESTS = "tests/test_rust_memory_budget.py::"
SEARCH, MEMORY, MAIN = "rust/ve-profile/src/search.rs", "rust/ve/src/memory.rs", "rust/ve/src/main.rs"
CLIENT, LIMITS = "ve/backends/rust_jsonl.py", "ve/backends/process_limits.py"
# (bug, file, before, after, how the test runs, test)
CASES = [
    ("the same-total successor raises an entry whose suffix is already at its minima", SEARCH,
     "sizes[index] < self.maximum && suffix > suffix_minima",
     "sizes[index] < self.maximum && suffix >= suffix_minima",
     "cargo", "search::domain_size_tests::lazy_sizes_are_the_eager_order"),
    ("the search builds every domain-size vector before its first model again", SEARCH,
     "        let mut sizes = DomainSizes::new(&minima, maximum);\n",
     "        let _all: Vec<_> = DomainSizes::new(&minima, maximum).collect();\n"
     "        let mut sizes = DomainSizes::new(&minima, maximum);\n",
     "release", TESTS + "test_the_incidents_search_is_answered_within_a_small_budget"),
    ("the allocator charges nothing against the budget", MEMORY,
     "live.checked_add(size).filter(|n| *n <= limit)).is_ok()",
     "live.checked_add(size).filter(|n| *n <= limit)).is_ok() || limit > 0",
     "release", TESTS + "test_runaway_input_returns_resource_limit_within_the_budget"),
    ("an exhausted jsonl case is answered without its id", MAIN,
     'Some(id) => json!({"id":id,"status":"error","error":error}),',
     'Some(_) => json!({"status":"error","error":error}),',
     "release", TESTS + "test_the_client_reads_an_exhausted_budget_as_resource_limit"),
    ("the client starts the child without an address-space cap", CLIENT,
     "            limit_address_space(self.process.pid, self.memory + ADDRESS_SPACE_HEADROOM)\n",
     "            pass\n",
     "python", TESTS + "test_the_client_passes_the_budget_and_caps_the_address_space"),
    ("the client passes the default budget, not the configured one", CLIENT,
     '"VE_RUST_MEMORY_LIMIT": str(self.memory)}',
     '"VE_RUST_MEMORY_LIMIT": str(MAX_RUST_MEMORY_BYTES)}',
     "python", TESTS + "test_the_client_passes_the_budget_and_caps_the_address_space"),
    ("a process started under another budget is reused", CLIENT,
     "\n                    or self.memory != memory_limit()):",
     "):",
     "python", TESTS + "test_the_client_passes_the_budget_and_caps_the_address_space"),
    ("a one-shot runner starts without an address-space cap", LIMITS,
     "            limit_address_space(process.pid, address_space)\n",
     "            pass\n",
     "python", TESTS + "test_one_shot_runners_run_under_an_address_space_limit"),
    ("a byte setting in non-ASCII digits is read as a number", LIMITS,
     "if not (text.isascii() and text.isdigit() and len(text) <= 19 and int(text) > 0):",
     "if not (text.isdigit() and len(text) <= 19 and int(text) > 0):",
     "python", TESTS + "test_configured_bytes"),
]


def build() -> str:
    subprocess.run([sys.executable, str(ROOT / "tools/rust_build.py")], cwd=ROOT, check=True,
                   capture_output=True)
    return rust_build.digest(rust_build.RELEASE_BINARY)


def run(how: str, test: str) -> subprocess.CompletedProcess:
    if how == "cargo":
        return subprocess.run([sys.executable, str(ROOT / "tools/rust_build.py"), "test", "--locked",
                               "--manifest-path", str(ROOT / "rust/Cargo.toml"), "-p", "ve-profile", "--", test],
                              cwd=ROOT, capture_output=True, text=True, check=False)
    settings = {"VE_RUST_SHA256": build()} if how == "release" else {}
    return subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", test]), cwd=ROOT,
                          env=nested_pytest.environment(os.environ, VE_NATIVE_PREBUILT="1", **settings),
                          capture_output=True, text=True, check=False)


def main() -> None:
    pinned = rust_build.digest(rust_build.RELEASE_BINARY)
    records = []
    try:
        for name, relative, before, after, how, test in CASES:
            path = ROOT / relative
            original = path.read_text()
            if original.count(before) != 1:
                raise RuntimeError(f"expected one mutation site for {name}")
            try:
                path.write_text(original.replace(before, after, 1))
                done = run(how, test)
            finally:
                path.write_text(original)
            output = done.stdout + done.stderr
            failed = "1 failed" in output or "test result: FAILED" in output
            if done.returncode == 0 or not failed:
                raise RuntimeError(f"{name}: expected a test failure, got {done.returncode}: {output[-1500:]}")
            records.append({"bug": name, "file": relative, "test": test, "exit_code": done.returncode,
                            "failure_excerpt": output[-1200:]})
            print(f"caught: {name}", flush=True)
    finally:
        restored = build()
    if restored != pinned:
        raise RuntimeError(f"the restored release binary {restored} is not the one before the run {pinned}")
    evidence = ROOT / "docs/oom-rootcause/evidence/mutants.json"
    evidence.write_text(json.dumps(records, indent=2) + "\n")
    print(f"{len(records)} seeded faults caught")


if __name__ == "__main__":
    main()
