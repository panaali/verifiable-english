#!/usr/bin/env python3
"""The x86 platform contract suite (test-architecture plan, rank 2, section 3.3).

Every merge candidate runs the tests in `tests/platform-contract.json` on the x86 VM, beside the complete
gate on the Mac. They are the tests whose outcome can depend on the platform, listed by cause:

* `pins`: pins and reproducible builds (`lean/checkers.lock` pins the x86 binaries; the Mac's are local);
* `process`: process supervision, injected deadlines, signals, file locks and resource limits;
* `agreement`: cross-implementation agreement on recorded fixtures (the gate's required families, the
  three-way files and the difffuzz CI sample);
* `divergence`: every test whose outcome differed between the Mac and the x86 VM on the same tree in the
  last 30 days (`tests/platform-divergences.json`, from the run records), each with its cause.

The contract adds a check; it replaces none. The complete live gate on the candidate, the full x86 gate for
native and runtime changes and the nightly `tools/gate.py --no-quarantine` still run everything.

    uv run python tools/platform_contract.py contract --write | --check
        tests/platform-contract.json from the tree and the saved divergence list (hermetic)
    python3 tools/platform_contract.py divergences --records DIR... [--mac-known FILE] --write | --check
        tests/platform-divergences.json from the gate records of both runners (the orchestrator's records)
    python3 tools/platform_contract.py run [--checkout DIR] [--output FILE] [--workers N] [--no-quarantine]
        exactly the contract suite, with the gate's stages, environment and pytest options
        (`tools/gate.py --contract`); its status is `contract-passed`, never a full gate's `passed`
    python3 tools/platform_contract.py misses RECORD [--mac RECORD] [--json]
        the failures of an x86 gate record that the contract list does not cover (exit 1 if any)
    python3 tools/platform_contract.py estimate [--durations FILE]
        the contract's test count and measured seconds (scheduling metadata, never a check)
"""
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass, field
import datetime
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "tests/platform-contract.json"
DIVERGENCES = ROOT / "tests/platform-divergences.json"
DURATIONS = ROOT / "tests/heavy-durations.json"
CONTRACT_FORMAT = "ve-platform-contract@1"
DIVERGENCE_FORMAT = "ve-platform-divergences@1"
WINDOW_DAYS = 30

CAUSES = {
    "pins": "pins and reproducible builds: lean/checkers.lock pins the x86 binaries, and the Mac's pins are "
            "runner-local, so only x86 can check them",
    "process": "process supervision, injected deadlines, signals, file locks and resource limits",
    "agreement": "cross-implementation agreement on recorded fixtures",
    "divergence": "the outcome differed between the Mac and the x86 VM on the same tree in the last 30 days",
}
# Named by the plan (section 3.3) or by the test inventory of the answer store (section 3.6, row 8). A name the
# tree no longer defines fails generation: rename it here with the test.
PINS = ("tests/test_rust_reproducible.py", "tests/test_gate_integrity.py")
PROCESS = ("tests/test_lean_service.py", "tests/test_lean_handles.py", "tests/test_hang_guards.py",
           "tests/test_stage2_faults.py", "tests/test_route_transport.py", "tests/test_native_build_lock.py",
           "tests/test_assist_deadline.py", "tests/test_cpu_bounds.py",
           "tests/test_soft_request_economy.py::test_soft_requests_on_the_widest_environment_stay_within_a_cpu_deadline",
           "tests/test_question_reading.py::test_the_whole_question_is_bounded_by_the_modes_deadline",
           "tests/test_w6a_limit_generator.py::test_every_backend_reports_resource_limit_in_bounded_time",
           "tests/test_w6a_limit_generator.py::test_lean_authority_reports_resource_limit_on_every_generated_case")
# A test file that imports one of these works with the operating system's signals, resource limits or file
# locks, so it is in `process` whether or not it is named above.
OS_MODULES = ("signal", "resource", "fcntl")
AGREEMENT_GLOBS = ("tests/test_*three_way*.py",)
AGREEMENT = ("tests/test_difffuzz.py::test_ci_run",)

# The causes of plan section 2.8. Only `elapsed time` and `repository state` make the test a bug by the
# repository's rules (docs/TESTING.md, CLAUDE.md); every divergence is in the contract whatever its cause.
DIVERGENCE_CAUSE_NAMES = ("pinned artefact", "toolchain", "elapsed time", "repository state", "environment",
                          "product race or arch bug", "unknown", "unclassified")
_CPU = ("environment", "an x86 CPU deadline exceeded by the kernel's memory compaction, charged to ve_service as "
        "system time on the loaded VM (docs/fix-x86-cpu-deadline/REPORT.md); fixed by counting user CPU")
_DIRTY = ("environment", "the branch verify ran on a dirty worktree (plan 2.8: a pipeline bug, verify.sh had no "
          "clean-tree check)")
# Each observed divergence's cause, by its test function (`file::function`). An observed divergence missing
# here is `unclassified` until the DRI classifies it.
DIVERGENCE_CAUSES = {
    "tests/test_rust_reproducible.py::test_release_binary_is_pinned":
        ("pinned artefact", "lean/checkers.lock pins the x86 Rust binary; the Mac's pins are runner-local"),
    "tests/test_question_reading.py::test_the_whole_question_is_bounded_by_the_modes_deadline":
        ("elapsed time", "a deadline measured on a fast machine (plan 2.8)"),
    "tests/test_lean_service.py::test_the_sub_tick_deadline_tests_hold_on_a_fast_machine_and_need_the_response_check":
        ("elapsed time", "elapsed time under load 70-160 (plan 2.8; quarantined, PIPELINE-LIMITS L36)"),
    "tests/test_readings_defaults_rd8_report.py::test_review_fix_commit_chain_and_final_gate_target":
        ("repository state", "the length of `%h` grows with the repository's object count (plan 2.8)"),
    "tests/test_agent_policy_rerun.py::test_counts_equal_the_committed_run":
        ("unknown", "CheckerUnavailable under load: an availability bug or a test that assumes an answer (plan 2.8)"),
    "tests/test_agent_policy_rerun.py::test_every_action_and_policy_query_equals_the_committed_results":
        ("unknown", "CheckerUnavailable under load: an availability bug or a test that assumes an answer (plan 2.8)"),
    "tests/test_agent_policy_rerun.py::test_lean_replays_every_certificate_of_the_rerun":
        ("unknown", "CheckerUnavailable under load: an availability bug or a test that assumes an answer (plan 2.8)"),
    "tests/test_difffuzz.py::test_ci_run":
        ("elapsed time", "the CI run's hang guard timed out on the loaded VM (quarantined)"),
    "tests/test_english_evidence.py::test_english_mixed_merge_smoke": _CPU,
    "tests/test_readings_rd6b_differential.py::test_generated_documents_agree_on_both_routes": _CPU,
    "tests/test_asimov_extended.py::test_rerun_mutant_equals_the_committed_results": _CPU,
    "tests/test_definitions_differential.py::test_populated_defined_table_limit_boundary": _CPU,
    "tests/test_readings_verdicts_lean.py::test_fnd1_conflict_free_under_every_reading_conditional_on_the_pair_premise":
        _CPU,
    "tests/test_propose.py::test_adoption_roundtrip_provenance_and_all_derivations": _CPU,
    **{f"tests/test_relay_mutation_gate.py::{name}": _DIRTY for name in (
        "test_a_client_without_its_length_check_fails_the_gate",
        "test_a_reader_without_its_row_count_check_fails_the_gate",
        "test_a_route_without_fixtures_fails_the_gate",
        "test_the_client_reader_accepts_a_genuine_answer_and_refuses_a_rebound_one",
        "test_the_gate_fails_on_an_unlisted_accepted_mutant_and_on_a_stale_entry",
        "test_the_gate_passes_on_sample_routes_with_the_committed_allow_list",
        "test_the_recorder_writes_every_relayed_case",
        "test_the_speech_source_reader_refuses_an_unhashable_unit_class")},
}
# The divergences of plan section 2.8 (reviews/test-architecture-2026-10-14.md, Oct 11-14), found in pipeline
# logs that no gate record keeps: (node ID, the runner it failed on, the day). The clang SIGBUS of 2.8 was a build
# failure, not a test, and is fixed in the build.
PLAN_OBSERVATIONS = (
    ("tests/test_rust_reproducible.py::test_release_binary_is_pinned", "mac", "2026-10-14"),
    ("tests/test_question_reading.py::test_the_whole_question_is_bounded_by_the_modes_deadline", "mac", "2026-10-14"),
    ("tests/test_lean_service.py::test_the_sub_tick_deadline_tests_hold_on_a_fast_machine_and_need_the_response_check",
     "x86", "2026-10-14"),
    ("tests/test_readings_defaults_rd8_report.py::test_review_fix_commit_chain_and_final_gate_target", "x86",
     "2026-10-14"),
    ("tests/test_agent_policy_rerun.py::test_counts_equal_the_committed_run", "x86", "2026-10-14"),
    ("tests/test_agent_policy_rerun.py::test_every_action_and_policy_query_equals_the_committed_results", "x86",
     "2026-10-14"),
    ("tests/test_agent_policy_rerun.py::test_lean_replays_every_certificate_of_the_rerun", "x86", "2026-10-14"),
    *((f"tests/test_relay_mutation_gate.py::{name.rsplit('::', 1)[1]}", "x86", "2026-10-13")
      for name in DIVERGENCE_CAUSES if name.startswith("tests/test_relay_mutation_gate.py::")),
)
ARCHES = ("mac", "x86")
# Gate stages (`tools/gate.py`) the contract run leaves out: the full gates on both runners run them.
NOT_IN_CONTRACT_RUN = ("Lean audit",)


def function_of(nodeid: str) -> str:
    """The test function of a node ID: `file::function` (or `file::Class::function`), parameters dropped."""
    return nodeid.split("[", 1)[0]


def covers(selector: str, nodeid: str) -> bool:
    """Whether running `selector` runs `nodeid`: the selector is the node ID, its file, its class or its function."""
    return nodeid == selector or nodeid.startswith(selector + "::") or nodeid.startswith(selector + "[")


# The tree: test definitions, read with Python's parser


def _nightly(decorators: list[ast.expr]) -> bool:
    for decorator in decorators:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        if isinstance(target, ast.Attribute) and target.attr == "nightly" and isinstance(target.value, ast.Attribute) \
                and target.value.attr == "mark":
            return True
    return False


def _module_marks(tree: ast.Module) -> list[ast.expr]:
    marks = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "pytestmark"
                                                for t in node.targets):
            value = node.value
            marks.extend(value.elts if isinstance(value, (ast.List, ast.Tuple)) else [value])
    return marks


def definitions(path: Path) -> dict[str, bool]:
    """The test functions `path` defines (`function` or `Class::function`), each with whether it is `nightly`."""
    tree = ast.parse(path.read_text(), filename=str(path))
    module = _nightly(_module_marks(tree))
    found = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            found[node.name] = module or _nightly(node.decorator_list)
        elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name.startswith("test"):
                    found[f"{node.name}::{item.name}"] = (module or _nightly(node.decorator_list)
                                                          or _nightly(item.decorator_list))
    return found


def imports_os_primitives(path: Path) -> list[str]:
    """The modules of `OS_MODULES` that `path` imports."""
    found = set()
    for node in ast.walk(ast.parse(path.read_text(), filename=str(path))):
        if isinstance(node, ast.Import):
            found |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.add(node.module.split(".")[0])
    return sorted(found & set(OS_MODULES))


class Tree:
    """The test files of a checkout, parsed once."""

    def __init__(self, root: Path):
        self.root = root
        self._definitions: dict[str, dict[str, bool]] = {}

    def files(self) -> list[str]:
        return sorted(str(path.relative_to(self.root)) for path in (self.root / "tests").glob("test_*.py"))

    def definitions(self, file: str) -> dict[str, bool]:
        if file not in self._definitions:
            self._definitions[file] = definitions(self.root / file)
        return self._definitions[file]

    def exists(self, selector: str) -> bool:
        file, _, function = selector.partition("::")
        if not (self.root / file).is_file():
            return False
        return not function or function_of(function) in self.definitions(file)


# The contract list


def required_families() -> tuple[str, ...]:
    """The gate's required cross-implementation families: one owner, `tools/gate.py`."""
    from tools import gate
    return tuple(f"tests/{family}" for family in gate.REQUIRED_FAMILIES)


def generate(root: Path = ROOT, divergences: dict | None = None, families: tuple[str, ...] | None = None) -> dict:
    """The contract list of the tree at `root`, from its test files and its saved divergence list."""
    tree = Tree(root)
    if divergences is None:
        divergences = json.loads((root / DIVERGENCES.relative_to(ROOT)).read_text())
    check_divergences(divergences)
    named: dict[str, set[str]] = {}

    def add(selector: str, cause: str, *, required: bool = True) -> None:
        if required and not tree.exists(selector):
            raise ValueError(f"{selector} ({cause}) is not defined in the tree: rename or remove it in "
                             "tools/platform_contract.py")
        named.setdefault(selector, set()).add(cause)

    for selector in PINS:
        add(selector, "pins")
    for selector in PROCESS:
        add(selector, "process")
    for file in tree.files():
        if imports_os_primitives(root / file):
            add(file, "process")
    for selector in (*(families if families is not None else required_families()), *AGREEMENT):
        add(selector, "agreement")
    for pattern in AGREEMENT_GLOBS:
        for file in tree.files():
            if fnmatch.fnmatchcase(file, pattern):
                add(file, "agreement")

    divergent: dict[str, list[dict]] = {}
    retired = []
    for nodeid, row in divergences["divergences"].items():
        selector = function_of(nodeid)
        if tree.exists(selector):
            divergent.setdefault(selector, []).append({"nodeid": nodeid, **row})
            add(selector, "divergence")
        else:
            retired.append({"nodeid": nodeid, "cause": row["cause"], "reason": "the tree no longer defines this test"})

    tests, left_out = [], []
    for selector in sorted(named):
        file, _, function = selector.partition("::")
        nightly = sorted(name for name, marked in tree.definitions(file).items()
                         if marked and (not function or name == function_of(function)))
        if nightly and not function:
            # A nightly corpus-scale rerun is left to the full gates; the file's other tests are listed one by one.
            selectors = [f"{file}::{name}" for name, marked in tree.definitions(file).items() if not marked]
            left_out.extend({"selector": f"{file}::{name}", "causes": sorted(named[selector]),
                             "reason": "nightly: the complete gates (R2, the full x86 gate, R3) run it"}
                            for name in nightly)
        else:
            selectors = [selector]
        for one in selectors:
            entry = {"selector": one, "causes": sorted(named[selector])}
            rows = divergent.get(selector, [])
            if rows:
                entry["divergence"] = sorted({row["cause"] for row in rows})
                entry["nodeids"] = sorted({row["nodeid"] for row in rows})
            tests.append(entry)
    return {
        "format": CONTRACT_FORMAT,
        "generated_by": "tools/platform_contract.py contract --write",
        "causes": CAUSES,
        "divergence_window": divergences["window"],
        "tests": sorted(tests, key=lambda entry: entry["selector"]),
        "left_out": sorted(left_out, key=lambda entry: entry["selector"]),
        "retired": sorted(retired, key=lambda entry: entry["nodeid"]),
    }


def read_contract(path: Path = CONTRACT) -> dict:
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or data.get("format") != CONTRACT_FORMAT or not isinstance(data.get("tests"), list):
        raise ValueError(f"{path} is not a {CONTRACT_FORMAT} list")
    for entry in data["tests"]:
        if not (isinstance(entry, dict) and isinstance(entry.get("selector"), str)
                and entry["selector"].startswith("tests/test_") and isinstance(entry.get("causes"), list)
                and entry["causes"] and set(entry["causes"]) <= set(CAUSES)):
            raise ValueError(f"{path}: malformed entry {entry!r}")
    if not data["tests"]:
        raise ValueError(f"{path} lists no test")
    return data


def run_selectors(contract: dict) -> list[str]:
    """The pytest arguments that run exactly the contract: each selector once, none inside another."""
    selectors = sorted({entry["selector"] for entry in contract["tests"]})
    return [selector for selector in selectors
            if not any(other != selector and covers(other, selector) for other in selectors)]


def coverage(contract: dict, nodeid: str) -> list[dict]:
    """The contract entries whose selector runs `nodeid`."""
    return [entry for entry in contract["tests"] if covers(entry["selector"], nodeid)]


def dumps(data: dict) -> str:
    return json.dumps(data, indent=1, sort_keys=False, ensure_ascii=False) + "\n"


# The divergence list, from the run records


@dataclass
class Run:
    source: str            # `<directory>/<file>` of the record
    arch: str              # mac | x86
    commit: str            # full or abbreviated; "" when the record does not name it
    tree: str              # "" when the record does not name it
    day: str               # YYYY-MM-DD
    failed: dict[str, str] = field(default_factory=dict)  # node ID -> the last line of its failure


_HEX = re.compile(r"[0-9a-f]{40}")
_FIRST_LINE_COMMIT = re.compile(r"\b(?:candidate|of|daily,)\s+([0-9a-f]{8,40})\b")
_PASSED = re.compile(r"\b(\d+) passed\b")
_RETRIED = re.compile(r"RETRIED serially, flaky under load: ([^)]*)\)")


def _arch_from_name(name: str) -> str | None:
    if ".x86." in name or "-x86-" in name:
        return "x86"
    if ".mac." in name or "-mac-" in name:
        return "mac"
    return None


def _arch_from_text(text: str) -> str | None:
    if "aarch64" in text or "ve-mac-1" in text:
        return "mac"
    if "x86_64" in text or "on the VM" in text or "runner: VM" in text:
        return "x86"
    return None


def _day(path: Path) -> str:
    return datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.timezone.utc).date().isoformat()


def _last_line(reason) -> str:
    lines = [line.strip() for line in str(reason).splitlines() if line.strip()]
    return lines[-1][:200] if lines else ""


def read_gate_record(path: Path, label: str) -> Run | None:
    """A `tools/gate.py` record whose suite ran: its failed tests, including those the quarantine retried."""
    try:
        record = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(record, dict) or not record.get("tree_sha") or not isinstance(record.get("failures"), list):
        return None
    failures = [failure for failure in record["failures"] if isinstance(failure, dict)]
    ran = "pytest" in record.get("stages", []) or any(failure.get("stage") == "pytest command" for failure in failures)
    if not ran:
        return None
    arch = _arch_from_name(path.name) or _arch_from_text(str(record.get("toolchains", {}).get("lean", "")))
    if arch is None:
        return None
    failed = {failure["nodeid"]: _last_line(failure.get("reason", "")) for failure in failures
              if failure.get("stage") == "pytest" and isinstance(failure.get("nodeid"), str)}
    retried = record.get("quarantine", {}).get("retried", {}) if isinstance(record.get("quarantine"), dict) else {}
    for nodeid in retried if isinstance(retried, dict) else ():
        failed.setdefault(nodeid, "failed in the suite, retried alone (quarantine)")
    quarantine_day = record.get("quarantine", {}).get("day") if isinstance(record.get("quarantine"), dict) else None
    return Run(label, arch, str(record.get("commit_sha", "")), record["tree_sha"],
               quarantine_day if isinstance(quarantine_day, str) else _day(path), failed)


def read_summary(path: Path, label: str) -> Run | None:
    """A verify or gate summary (`*.md`): PASS or FAIL on line 1, `FAILED <node ID>` lines, a passed count."""
    try:
        lines = path.read_text().splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    if not lines or not lines[0].startswith(("PASS ", "FAIL ")):
        return None
    if not any(_PASSED.search(line) for line in lines[:6]):
        return None  # the suite did not run to a count
    arch = _arch_from_name(path.name) or _arch_from_text(lines[0])
    if arch is None:
        return None
    named = _HEX.match(path.name)
    match = _FIRST_LINE_COMMIT.search(lines[0])
    commit = named.group(0) if named else match.group(1) if match else ""
    if not commit:
        return None
    failed = {}
    for line in lines[1:]:
        if line.startswith("FAILED tests/"):
            nodeid = line[len("FAILED "):].split(" - ", 1)
            failed[nodeid[0].strip()] = nodeid[1][:200] if len(nodeid) > 1 else ""
    retried = _RETRIED.search(lines[0])
    if retried:
        for nodeid in retried.group(1).split(","):
            if nodeid.strip().startswith("tests/"):
                failed.setdefault(nodeid.strip(), "failed in the suite, passed on a serial retry")
    return Run(label, arch, commit, "", _day(path), failed)


def read_runs(directories: list[Path]) -> tuple[list[Run], int]:
    """Every gate record (`*.json`) and summary (`*.md`) under `directories` whose suite ran, with its runner; and
    how many files were read."""
    runs, read = [], 0
    for directory in directories:
        paths = sorted(directory.glob("*.json")) + sorted(directory.glob("*.md")) if directory.is_dir() \
            else [directory]
        for path in paths:
            read += 1
            label = f"{path.parent.name}/{path.name}"
            run = read_gate_record(path, label) if path.suffix == ".json" else read_summary(path, label)
            if run is not None:
                runs.append(run)
    return runs, read


def same_tree(one: Run, other: Run) -> bool:
    if one.tree and other.tree:
        return one.tree == other.tree
    short = min(len(one.commit), len(other.commit))
    return short >= 8 and one.commit[:short] == other.commit[:short]


def divergences_of(runs: list[Run], since: str, until: str, mac_known: list[str], plan: tuple | None = None) -> dict:
    """The divergence list: each test that failed on one runner and not on the other, on the same tree, in the
    window; each Mac-only known failure; each divergence of plan section 2.8 in the window."""
    inside = []
    for run in sorted((run for run in runs if since <= run.day <= until), key=lambda run: (not run.tree, run.source)):
        # A summary repeats a gate record of the same runner and commit, or an earlier summary of the same run.
        if not run.tree and any(other.arch == run.arch and same_tree(other, run)
                                and (other.tree or other.failed == run.failed) for other in inside):
            continue
        inside.append(run)
    observations: dict[str, list[dict]] = {}
    paired = set()
    for mac in (run for run in inside if run.arch == "mac"):
        for x86 in (run for run in inside if run.arch == "x86"):
            if not same_tree(mac, x86):
                continue
            paired |= {mac.source, x86.source}
            for nodeid in sorted(set(mac.failed) ^ set(x86.failed)):
                failing, passing = (mac, x86) if nodeid in mac.failed else (x86, mac)
                observations.setdefault(nodeid, []).append({
                    "failed_on": failing.arch, "passed_on": passing.arch, "tree": mac.tree or x86.tree,
                    "commit": failing.commit or passing.commit, "day": max(mac.day, x86.day),
                    "records": sorted([failing.source, passing.source]), "reason": failing.failed[nodeid]})
    for nodeid in mac_known:
        observations.setdefault(nodeid, []).append({
            "failed_on": "mac", "passed_on": "x86", "day": until, "records": ["mac-known-failures.txt"],
            "reason": "a known Mac-only failure: the runner's list of failures the x86 leg checks"})
    for nodeid, arch, day in PLAN_OBSERVATIONS if plan is None else plan:
        if since <= day <= until:
            observations.setdefault(nodeid, []).append({
                "failed_on": arch, "passed_on": "x86" if arch == "mac" else "mac", "day": day,
                "records": ["plan 2.8 (reviews/test-architecture-2026-10-14.md)"], "reason": "plan section 2.8"})
    rows = {}
    for nodeid in sorted(observations):
        cause, note = DIVERGENCE_CAUSES.get(function_of(nodeid), ("unclassified", "not yet classified by the DRI"))
        seen = sorted(observations[nodeid], key=lambda row: (row["day"], row["records"]))
        unique = [row for index, row in enumerate(seen) if row not in seen[:index]]
        rows[nodeid] = {"cause": cause, "note": note, "observations": unique}
    return {
        "format": DIVERGENCE_FORMAT,
        "generated_by": "tools/platform_contract.py divergences --write",
        "window": {"since": since, "until": until},
        "runs": {"in_window": len(inside), "paired": len(paired)},
        "divergences": rows,
    }


def check_divergences(data: dict) -> None:
    """The saved divergence list's shape: each row keyed by its test's node ID, with a known cause and at least one
    observation."""
    if not isinstance(data, dict) or data.get("format") != DIVERGENCE_FORMAT:
        raise ValueError(f"not a {DIVERGENCE_FORMAT} list")
    window = data.get("window")
    if not (isinstance(window, dict) and all(isinstance(window.get(k), str) for k in ("since", "until"))):
        raise ValueError("the divergence list has no window")
    if not isinstance(data.get("divergences"), dict):
        raise ValueError("the divergence list has no rows")
    for nodeid, row in data["divergences"].items():
        if not (nodeid.startswith("tests/test_") and "::" in nodeid and isinstance(row, dict)
                and row.get("cause") in DIVERGENCE_CAUSE_NAMES
                and isinstance(row.get("observations"), list) and row["observations"]):
            raise ValueError(f"malformed divergence row {nodeid}: {row!r}")


def read_mac_known(path: Path | None) -> list[str]:
    if path is None:
        return []
    return sorted({line.split()[0] for line in path.read_text().splitlines()
                   if line.strip() and not line.startswith("#") and line.split()[0].startswith("tests/")})


# Checking an x86 gate failure against the list


def failed_tests_of(record: dict) -> dict[str, str]:
    """The tests an x86 gate record failed, each with how: in the suite, by the skip policy, or retried alone."""
    found = {}
    for failure in record.get("failures", []):
        if isinstance(failure, dict) and isinstance(failure.get("nodeid"), str):
            found[failure["nodeid"]] = failure.get("stage", "")
    retried = record.get("quarantine", {}).get("retried", {}) if isinstance(record.get("quarantine"), dict) else {}
    for nodeid in retried if isinstance(retried, dict) else ():
        found.setdefault(nodeid, "quarantine: failed in the suite, retried alone")
    return found


def misses(record: dict, contract: dict, mac: dict | None = None) -> dict:
    """Which failures of the x86 gate `record` the contract does not cover. A test that also failed in `mac` (a
    Mac record of the same tree) is not platform-specific. A failure outside the tests is covered when the contract
    run runs its stage."""
    if not isinstance(record, dict) or not isinstance(record.get("failures"), list):
        raise ValueError("not a tools/gate.py record")
    arch = _arch_from_text(str(record.get("toolchains", {}).get("lean", "")))
    if arch != "x86":
        raise ValueError(f"not an x86 gate record (Lean toolchain: {record.get('toolchains', {}).get('lean')!r})")
    if mac is not None and mac.get("tree_sha") != record.get("tree_sha"):
        raise ValueError("the Mac record is of another tree")
    on_mac = set(failed_tests_of(mac)) if mac is not None else set()
    tests = []
    for nodeid, how in sorted(failed_tests_of(record).items()):
        entries = coverage(contract, nodeid)
        tests.append({"nodeid": nodeid, "how": how, "covered": bool(entries),
                      "selectors": [entry["selector"] for entry in entries],
                      "causes": sorted({cause for entry in entries for cause in entry["causes"]}),
                      "also_failed_on_mac": nodeid in on_mac})
    others = []
    for failure in record["failures"]:
        if not isinstance(failure, dict) or isinstance(failure.get("nodeid"), str):
            continue
        stage = failure.get("stage", "")
        reason = str(failure.get("reason", ""))
        if stage in ("pytest command",):
            continue  # the suite's exit status: its tests are listed above
        if stage == "gate":
            covered = reason.split(":", 1)[0] not in NOT_IN_CONTRACT_RUN
            why = "a gate stage the contract run runs" if covered else "a gate stage the contract run leaves out"
        else:
            covered, why = False, "the collection check: platform-independent, run by every full gate"
        others.append({"stage": stage, "reason": _last_line(reason) if stage == "gate" else reason.split("\n", 1)[0],
                       "covered": covered, "why": why})
    missed = [row["nodeid"] for row in tests if not row["covered"] and not row["also_failed_on_mac"]]
    return {"commit_sha": record.get("commit_sha", ""), "tree_sha": record.get("tree_sha", ""),
            "status": record.get("status"), "tests": tests, "other_failures": others,
            "missed": missed, "missed_stages": [row["stage"] + ": " + row["reason"] for row in others
                                                if not row["covered"] and row["stage"] == "gate"]}


# Commands


def estimate(contract: dict, durations: dict[str, float]) -> dict:
    selectors = run_selectors(contract)
    chosen = {nodeid: seconds for nodeid, seconds in durations.items()
              if any(covers(selector, nodeid) for selector in selectors)}
    return {"selectors": len(selectors), "measured_tests": len(chosen), "measured_seconds": round(sum(chosen.values()), 1),
            "longest": sorted(chosen.items(), key=lambda item: -item[1])[:5],
            "share_of_suite": round(sum(chosen.values()) / max(sum(durations.values()), 1e-9), 3)}


def _compare(path: Path, expected: str, what: str) -> int:
    actual = path.read_text() if path.is_file() else ""
    if actual != expected:
        print(f"{path.relative_to(ROOT) if path.is_relative_to(ROOT) else path} is stale: run "
              f"`python3 tools/platform_contract.py {what}`", file=sys.stderr)
        return 1
    print(f"{path.name}: up to date")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    contract = commands.add_parser("contract", help="write or check tests/platform-contract.json")
    mode = contract.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    divergences = commands.add_parser("divergences", help="write or check tests/platform-divergences.json")
    divergences.add_argument("--records", type=Path, nargs="+", required=True,
                             help="directories (or files) of gate records and summaries of both runners")
    divergences.add_argument("--mac-known", type=Path, help="the Mac runner's known failures (mac-known-failures.txt)")
    divergences.add_argument("--until", help="the window's last day (default: today, UTC; --check: the saved window)")
    divergences.add_argument("--output", type=Path, default=DIVERGENCES)
    mode = divergences.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    run = commands.add_parser("run", help="run exactly the contract suite with the gate's options")
    run.add_argument("--checkout", type=Path, help="the checkout to run (default: this one); its own gate and list run")
    run.add_argument("--output", type=Path, help="the record (default: platform-contract-result.json in the checkout)")
    run.add_argument("--workers", default="auto")
    run.add_argument("--no-quarantine", action="store_true")
    check = commands.add_parser("misses", help="the failures of an x86 gate record the contract does not cover")
    check.add_argument("record", type=Path)
    check.add_argument("--mac", type=Path, help="the Mac gate record of the same tree")
    check.add_argument("--list", type=Path, default=CONTRACT)
    check.add_argument("--json", action="store_true")
    measure = commands.add_parser("estimate", help="the contract's measured test seconds (metadata only)")
    measure.add_argument("--durations", type=Path, default=DURATIONS)
    args = parser.parse_args(argv)

    if args.command == "contract":
        expected = dumps(generate())
        if args.write:
            CONTRACT.write_text(expected)
            return 0
        return _compare(CONTRACT, expected, "contract --write")

    if args.command == "divergences":
        saved = json.loads(args.output.read_text()) if args.check and args.output.is_file() else None
        if args.until:
            until = args.until
        elif saved is not None:
            until = saved["window"]["until"]
        else:
            until = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        since = (datetime.date.fromisoformat(until) - datetime.timedelta(days=WINDOW_DAYS)).isoformat()
        runs, _ = read_runs(args.records)
        expected = dumps(divergences_of(runs, since, until, read_mac_known(args.mac_known)))
        if args.write:
            args.output.write_text(expected)
            return 0
        return _compare(args.output, expected, "divergences --write --records ...")

    if args.command == "run":
        checkout = (args.checkout or ROOT).resolve()
        gate = checkout / "tools/gate.py"
        if not gate.is_file():
            parser.error(f"{checkout} has no tools/gate.py")
        command = [sys.executable, str(gate), "--contract", "--workers", args.workers]
        if args.output:
            command += ["--output", str(args.output.resolve())]
        if args.no_quarantine:
            command.append("--no-quarantine")
        print(f"[platform-contract] {' '.join(command)}", flush=True)
        os.execv(sys.executable, command)

    if args.command == "misses":
        try:
            record = json.loads(args.record.read_text())
            mac = json.loads(args.mac.read_text()) if args.mac else None
            report = misses(record, read_contract(args.list), mac)
        except (OSError, ValueError) as exc:
            print(f"platform_contract misses: {exc}", file=sys.stderr)
            return 2
        if args.json:
            print(json.dumps(report, indent=1))
        else:
            for row in report["tests"]:
                where = (f"in the contract ({', '.join(row['causes'])})" if row["covered"]
                         else "also failed on the Mac" if row["also_failed_on_mac"] else "NOT in the contract")
                print(f"{row['nodeid']}: {where}")
            for row in report["other_failures"]:
                print(f"[{row['stage']}] {row['reason']}: {row['why']}")
            print(f"{len(report['missed'])} failed tests NOT in the contract list"
                  + (f": {', '.join(report['missed'])}" if report["missed"] else ""))
        return 1 if report["missed"] or report["missed_stages"] else 0

    if args.command == "estimate":
        times = json.loads(args.durations.read_text())["tests"]
        print(json.dumps(estimate(read_contract(), times), indent=1))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
