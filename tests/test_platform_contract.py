"""`tools/platform_contract.py`: the x86 platform contract suite (test-architecture plan rank 2, section 3.3).

* The contract list `tests/platform-contract.json` is generated from the tree, by cause (pins, process
  behaviour, cross-implementation agreement) and from the saved divergence list; `contract --check` regenerates
  it. The assertion on the pinned x86 digest is in it.
* The divergence list `tests/platform-divergences.json` is generated from the gate records of both runners: a
  test that failed on one runner and passed on the other, on the same tree, in the last 30 days. A divergence
  planted in a fake record appears in the regenerated list.
* `tools/gate.py --contract` runs exactly the listed tests with the gate's stages and options, and its status is
  never a full gate's `passed`.
* `misses` names the failures of an x86 gate record that the list does not cover.
"""
from __future__ import annotations

import datetime
import json
import os
from pathlib import Path
import sys
import textwrap

import pytest

from test_gate_rerun import FakeGate
from tools import gate, platform_contract as pc

ROOT = Path(__file__).resolve().parents[1]
PIN_TEST = "tests/test_rust_reproducible.py::test_release_binary_is_pinned"
DAY = "2026-10-15"


# The committed lists


def test_the_contract_list_is_generated_from_the_tree():
    assert (ROOT / "tests/platform-contract.json").read_text() == pc.dumps(pc.generate())


def test_the_pinned_x86_digest_assertion_is_in_the_contract_for_its_pin():
    contract = pc.read_contract()
    entries = pc.coverage(contract, PIN_TEST)
    assert "pins" in {cause for entry in entries for cause in entry["causes"]}
    assert any(pc.covers(selector, PIN_TEST) for selector in pc.run_selectors(contract))


def test_each_cause_lists_its_tests():
    contract = pc.read_contract()
    causes = {entry["selector"]: set(entry["causes"]) for entry in contract["tests"]}
    for family in gate.REQUIRED_FAMILIES:  # the gate's cross-implementation families, one owner
        assert "agreement" in causes[f"tests/{family}"]
    for selector in (*pc.PINS, *pc.PROCESS):
        assert selector in causes
    assert "process" in causes["tests/test_native_build_lock.py"]  # imports fcntl
    saved = json.loads((ROOT / "tests/platform-divergences.json").read_text())
    retired = {row["nodeid"] for row in contract["retired"]}
    for nodeid in saved["divergences"]:
        if nodeid not in retired:
            assert "divergence" in {cause for entry in pc.coverage(contract, nodeid)
                                    for cause in entry["causes"]}, nodeid


def test_the_saved_divergence_list_is_well_formed_and_each_row_has_a_known_cause():
    saved = json.loads((ROOT / "tests/platform-divergences.json").read_text())
    pc.check_divergences(saved)
    assert saved["divergences"]
    nodeid, row = next(iter(saved["divergences"].items()))
    for broken in ({**saved, "format": "other"}, {**saved, "window": None}, {**saved, "divergences": [row]},
                   {**saved, "divergences": {nodeid: {**row, "cause": "load"}}},
                   {**saved, "divergences": {nodeid: {**row, "observations": []}}},
                   {**saved, "divergences": {"tests/test_a.py": row}}):
        with pytest.raises(ValueError):
            pc.check_divergences(broken)


@pytest.mark.parametrize("data", [
    {"format": "other", "tests": [{"selector": "tests/test_a.py", "causes": ["pins"]}]},
    {"format": pc.CONTRACT_FORMAT, "tests": []},
    {"format": pc.CONTRACT_FORMAT, "tests": [{"selector": "tests/test_a.py", "causes": []}]},
    {"format": pc.CONTRACT_FORMAT, "tests": [{"selector": "tests/test_a.py", "causes": ["speed"]}]},
    {"format": pc.CONTRACT_FORMAT, "tests": [{"selector": "-k test_a", "causes": ["pins"]}]},
    {"format": pc.CONTRACT_FORMAT, "tests": [{"selector": 7, "causes": ["pins"]}]},
])
def test_a_malformed_contract_list_is_refused(tmp_path, data):
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        pc.read_contract(path)


# Generation, on a scratch tree


@pytest.fixture
def tree(tmp_path, monkeypatch):
    root = tmp_path / "tree"
    files = {
        "tests/test_pins.py": "def test_pinned():\n    pass\n",
        "tests/test_supervise.py": "def test_kill():\n    pass\n",
        "tests/test_locks.py": "import fcntl\n\ndef test_lock():\n    pass\n",
        "tests/test_plain.py": "import json\n\ndef test_plain():\n    pass\n\ndef test_other():\n    pass\n",
        "tests/test_x_three_way.py": textwrap.dedent("""\
            import pytest

            def test_hundred():
                pass

            @pytest.mark.nightly
            def test_thousand():
                pass

            class TestRoutes:
                def test_route(self):
                    pass
            """),
    }
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    monkeypatch.setattr(pc, "PINS", ("tests/test_pins.py",))
    monkeypatch.setattr(pc, "PROCESS", ("tests/test_supervise.py::test_kill",))
    monkeypatch.setattr(pc, "AGREEMENT", ())
    return root


def divergence_list(*rows) -> dict:
    return {"format": pc.DIVERGENCE_FORMAT, "window": {"since": "2026-09-15", "until": DAY},
            "divergences": {nodeid: {"cause": cause, "note": "", "observations": [{"day": DAY}]}
                            for nodeid, cause in rows}}


def test_generation_lists_each_cause_and_leaves_nightly_reruns_to_the_full_gates(tree):
    contract = pc.generate(tree, divergence_list(("tests/test_plain.py::test_plain", "environment")), families=())
    listed = {entry["selector"]: entry["causes"] for entry in contract["tests"]}
    assert listed == {
        "tests/test_pins.py": ["pins"],
        "tests/test_supervise.py::test_kill": ["process"],
        "tests/test_locks.py": ["process"],
        "tests/test_plain.py::test_plain": ["divergence"],
        "tests/test_x_three_way.py::test_hundred": ["agreement"],
        "tests/test_x_three_way.py::TestRoutes::test_route": ["agreement"],
    }
    assert [row["selector"] for row in contract["left_out"]] == ["tests/test_x_three_way.py::test_thousand"]
    entry = next(entry for entry in contract["tests"] if entry["selector"] == "tests/test_plain.py::test_plain")
    assert (entry["divergence"], entry["nodeids"]) == (["environment"], ["tests/test_plain.py::test_plain"])


def test_a_divergence_names_its_test_function_whatever_its_parameters(tree):
    contract = pc.generate(tree, divergence_list(("tests/test_plain.py::test_other[news-0]", "environment"),
                                                 ("tests/test_plain.py::test_other[news-1]", "environment")),
                           families=())
    entry = next(entry for entry in contract["tests"] if entry["selector"] == "tests/test_plain.py::test_other")
    assert entry["nodeids"] == ["tests/test_plain.py::test_other[news-0]", "tests/test_plain.py::test_other[news-1]"]
    assert pc.covers(entry["selector"], "tests/test_plain.py::test_other[news-7]")


def test_a_named_test_the_tree_does_not_define_fails_generation(tree, monkeypatch):
    monkeypatch.setattr(pc, "PROCESS", ("tests/test_supervise.py::test_renamed",))
    with pytest.raises(ValueError, match="test_renamed"):
        pc.generate(tree, divergence_list(), families=())
    monkeypatch.setattr(pc, "PROCESS", ())
    with pytest.raises(ValueError, match="test_gone"):
        pc.generate(tree, divergence_list(), families=("tests/test_gone.py",))


def test_a_divergence_whose_test_is_gone_is_retired_and_named(tree):
    contract = pc.generate(tree, divergence_list(("tests/test_plain.py::test_deleted", "elapsed time")), families=())
    assert contract["retired"] == [{"nodeid": "tests/test_plain.py::test_deleted", "cause": "elapsed time",
                                    "reason": "the tree no longer defines this test"}]
    assert not any("test_deleted" in entry["selector"] for entry in contract["tests"])


def test_only_imports_of_the_operating_systems_primitives_put_a_file_in_process(tmp_path):
    for text, expected in (("import signal\n", ["signal"]), ("from resource import setrlimit\n", ["resource"]),
                           ("import os, fcntl\n", ["fcntl"]), ("import json\nsignal = 1\n", []),
                           ("from .signal import x\n", []), ("import signals\n", [])):
        path = tmp_path / "test_x.py"
        path.write_text(text)
        assert pc.imports_os_primitives(path) == expected, text


def test_the_run_selectors_run_each_listed_test_once():
    contract = {"tests": [{"selector": "tests/test_a.py", "causes": ["pins"]},
                          {"selector": "tests/test_a.py::test_x", "causes": ["divergence"]},
                          {"selector": "tests/test_ab.py::test_y", "causes": ["process"]},
                          {"selector": "tests/test_b.py::test_z", "causes": ["process"]},
                          {"selector": "tests/test_b.py::test_z", "causes": ["divergence"]}]}
    assert pc.run_selectors(contract) == ["tests/test_a.py", "tests/test_ab.py::test_y", "tests/test_b.py::test_z"]
    assert pc.covers("tests/test_a.py::test_x", "tests/test_a.py::test_x[1]")
    assert not pc.covers("tests/test_a.py::test_x", "tests/test_a.py::test_xy")
    assert not pc.covers("tests/test_a.py", "tests/test_ab.py::test_y")


def test_contract_check_fails_on_a_stale_list(tmp_path, monkeypatch, capsys):
    stale = tmp_path / "platform-contract.json"
    current = pc.dumps(pc.generate())
    stale.write_text(current.replace('"pins"', '"process"', 1))
    monkeypatch.setattr(pc, "CONTRACT", stale)
    assert pc.main(["contract", "--check"]) == 1
    assert "stale" in capsys.readouterr().err
    assert pc.main(["contract", "--write"]) == 0
    assert stale.read_text() == current
    assert pc.main(["contract", "--check"]) == 0


# The divergence list, from fake run records


def gate_record(tree: str, arch: str, failed=(), *, ran=True, retried=(), day=DAY) -> dict:
    lean = f"Lean (version 4.24.0, {'x86_64-unknown-linux-gnu' if arch == 'x86' else 'aarch64-apple-darwin'})"
    failures = [{"stage": "pytest", "nodeid": nodeid, "reason": "trace\nCheckerUnavailable"} for nodeid in failed]
    if failed:
        failures.insert(0, {"stage": "pytest command", "reason": "Python suite: exit 1"})
    if not ran:  # the gate stopped before its suite: no test has an outcome
        failures = [{"stage": "gate", "reason": "Wire contract check: exit 1"}]
    return {"schema_version": 1, "commit_sha": f"c{tree}".ljust(40, "0"), "tree_sha": tree, "dirty": False,
            "mode": "full", "status": "failed" if failures else "passed", "toolchains": {"lean": lean},
            "stages": list(gate.REQUIRED_STAGES if ran else gate.REQUIRED_STAGES[:-1]),
            "failures": failures, "quarantine": {"day": day, "retried": {nodeid: {"alone": "passed"}
                                                                         for nodeid in retried}}}


def write_records(directory: Path, records: dict[str, dict]) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    for name, record in records.items():
        (directory / name).write_text(json.dumps(record))
    return directory


PLANTED = "tests/test_planted.py::test_differs_on_x86[case-1]"


def regenerate(tmp_path, *directories, until=DAY, mac_known=None, check=False) -> tuple[int, dict]:
    output = tmp_path / "divergences.json"
    argv = ["divergences", "--records", *map(str, directories), "--until", until, "--output", str(output),
            "--check" if check else "--write"]
    if mac_known:
        argv += ["--mac-known", str(mac_known)]
    code = pc.main(argv)
    return code, json.loads(output.read_text()) if output.is_file() else {}


def test_a_planted_divergence_in_a_fake_run_record_appears_in_the_regenerated_list(tmp_path, monkeypatch):
    monkeypatch.setattr(pc, "PLAN_OBSERVATIONS", ())
    records = write_records(tmp_path / "cand-runs", {
        "c1.mac.json": gate_record("t1", "mac"),
        "c1.x86.json": gate_record("t1", "x86", [PLANTED]),
    })
    code, saved = regenerate(tmp_path, records)
    assert code == 0
    pc.check_divergences(saved)
    assert {nodeid: row["cause"] for nodeid, row in saved["divergences"].items()} == {PLANTED: "unclassified"}
    [observation] = saved["divergences"][PLANTED]["observations"]
    assert observation == {"failed_on": "x86", "passed_on": "mac", "tree": "t1", "commit": "ct1".ljust(40, "0"),
                           "day": DAY, "records": ["cand-runs/c1.mac.json", "cand-runs/c1.x86.json"],
                           "reason": "CheckerUnavailable"}
    # The saved list is current; a second planted divergence makes it stale.
    assert regenerate(tmp_path, records, check=True)[0] == 0
    write_records(records, {"c2.mac.json": gate_record("t2", "mac", ["tests/test_mac.py::test_only_mac"]),
                            "c2.x86.json": gate_record("t2", "x86")})
    assert regenerate(tmp_path, records, check=True)[0] == 1


def test_a_divergence_needs_both_runners_suites_on_the_same_tree_in_the_window(tmp_path, monkeypatch):
    monkeypatch.setattr(pc, "PLAN_OBSERVATIONS", ())
    records = write_records(tmp_path / "runs", {
        "a.mac.json": gate_record("t1", "mac"),
        "a.x86.json": gate_record("t2", "x86", [PLANTED]),                   # another tree
        "b.mac.json": gate_record("t3", "mac", [PLANTED]),
        "b.x86.json": gate_record("t3", "x86", ran=False),                   # its suite never ran
        "c.mac.json": gate_record("t4", "mac", day="2026-09-01"),
        "c.x86.json": gate_record("t4", "x86", [PLANTED], day="2026-09-01"),  # outside the 30 days
        "d.mac.json": gate_record("t5", "mac", [PLANTED]),
        "d.x86.json": gate_record("t5", "x86", [PLANTED]),                   # failed on both: no divergence
    })
    assert regenerate(tmp_path, records)[1]["divergences"] == {}
    assert list(regenerate(tmp_path, records, until="2026-09-02")[1]["divergences"]) == [PLANTED]


def test_a_quarantined_failure_is_an_outcome_and_the_cause_is_the_test_functions(tmp_path, monkeypatch):
    monkeypatch.setattr(pc, "PLAN_OBSERVATIONS", ())
    smoke = "tests/test_english_evidence.py::test_english_mixed_merge_smoke[news-article-9]"
    records = write_records(tmp_path / "runs", {
        "a.mac.json": gate_record("t1", "mac"),
        "a.x86.json": gate_record("t1", "x86", retried=[smoke]),
    })
    [(nodeid, row)] = regenerate(tmp_path, records)[1]["divergences"].items()
    assert (nodeid, row["cause"]) == (smoke, "environment")
    assert row["observations"][0]["reason"] == "failed in the suite, retried alone (quarantine)"


def test_summaries_pair_by_commit_and_never_repeat_a_gate_record(tmp_path, monkeypatch):
    monkeypatch.setattr(pc, "PLAN_OBSERVATIONS", ())
    commit = "ab" * 20
    runs = tmp_path / "integ-runs"
    write_records(runs, {f"{commit}.mac.json": {**gate_record("t1", "mac"), "commit_sha": commit}})
    (runs / f"{commit}.mac.md").write_text("PASS cand-x-mac (runner: ve-mac-1 aarch64)\ngate.py: 10 passed\n")
    (runs / f"{commit}.x86.md").write_text(f"FAIL cand-x-x86 (gate.py of {commit[:8]} on the VM x86_64)\n"
                                           f"gate.py: 9 passed, 1 failed\nFAILED {PLANTED} - CheckerUnavailable: cpu\n")
    nightly = tmp_path / "nightly-vm-runs"
    nightly.mkdir()
    (nightly / f"{commit}.md").write_text(f"FAIL nightly-vm (runner: VM lab, x86 daily, {commit[:8]})\n"
                                          f"gate.py: 9 passed, 1 failed\nFAILED {PLANTED} - CheckerUnavailable: cpu\n")
    final = tmp_path / "integ-y-x86-verify.final.md"
    final.write_text("FAIL integ-y-x86 (lake=0 audit=0 pytest=1)\n10 passed\nFAILED tests/test_q.py::test_q - x\n")
    noon = datetime.datetime.fromisoformat(f"{DAY}T12:00:00+00:00").timestamp()
    for summary in (*runs.glob("*.md"), *nightly.glob("*.md"), final):  # a summary's day is its file's
        os.utime(summary, (noon, noon))
    [(nodeid, row)] = regenerate(tmp_path, runs, nightly, final)[1]["divergences"].items()
    assert nodeid == PLANTED
    # One observation: the Mac's gate record against the first x86 summary; the Mac summary and the second x86
    # summary repeat them, and the final report names no commit, so it pairs with nothing.
    assert [observation["records"] for observation in row["observations"]] == [
        [f"integ-runs/{commit}.mac.json", f"integ-runs/{commit}.x86.md"]]


def test_mac_known_failures_and_the_plans_divergences_are_in_the_list(tmp_path):
    known = tmp_path / "mac-known-failures.txt"
    known.write_text(f"{PIN_TEST}\n\n# a comment\n")
    empty = write_records(tmp_path / "none", {})
    rows = regenerate(tmp_path, empty, mac_known=known)[1]["divergences"]
    assert rows[PIN_TEST]["cause"] == "pinned artefact"
    assert {tuple(o["records"]) for o in rows[PIN_TEST]["observations"]} == {
        ("mac-known-failures.txt",), ("plan 2.8 (reviews/test-architecture-2026-10-14.md)",)}
    assert rows["tests/test_readings_defaults_rd8_report.py::test_review_fix_commit_chain_and_final_gate_target"][
        "cause"] == "repository state"
    # 30 days on, the plan's observations of Oct 13-14 have left the window; the runner's list has not.
    later = set(regenerate(tmp_path, empty, until="2026-11-14", mac_known=known)[1]["divergences"])
    assert later == {PIN_TEST}


def test_every_classified_cause_is_a_cause_of_the_plan():
    assert {cause for cause, _ in pc.DIVERGENCE_CAUSES.values()} <= set(pc.DIVERGENCE_CAUSE_NAMES)
    assert all(nodeid in pc.DIVERGENCE_CAUSES for nodeid, _, _ in pc.PLAN_OBSERVATIONS)


# Checking an x86 failure against the list


def contract_of(*rows) -> dict:
    return {"format": pc.CONTRACT_FORMAT, "tests": [{"selector": selector, "causes": causes}
                                                     for selector, causes in rows]}


def test_misses_names_the_x86_failures_outside_the_list(tmp_path, capsys):
    contract = contract_of(("tests/test_lean_service.py", ["process"]), ("tests/test_a.py::test_x", ["divergence"]))
    record = gate_record("t1", "x86", ["tests/test_lean_service.py::test_kill[1]", "tests/test_a.py::test_x[p]",
                                       "tests/test_b.py::test_new"], retried=["tests/test_c.py::test_flaky"])
    report = pc.misses(record, contract)
    assert report["missed"] == ["tests/test_b.py::test_new", "tests/test_c.py::test_flaky"]
    covered = {row["nodeid"]: row["causes"] for row in report["tests"] if row["covered"]}
    assert covered == {"tests/test_lean_service.py::test_kill[1]": ["process"],
                       "tests/test_a.py::test_x[p]": ["divergence"]}
    # A test that failed on the Mac too, on the same tree, is not platform-specific.
    mac = gate_record("t1", "mac", ["tests/test_b.py::test_new"])
    assert pc.misses(record, contract, mac)["missed"] == ["tests/test_c.py::test_flaky"]
    with pytest.raises(ValueError, match="another tree"):
        pc.misses(record, contract, gate_record("t2", "mac"))


def test_misses_refuses_a_mac_record_and_judges_other_failures_by_the_contract_runs_stages():
    contract = contract_of(("tests/test_a.py", ["pins"]))
    with pytest.raises(ValueError, match="not an x86"):
        pc.misses(gate_record("t1", "mac", ["tests/test_b.py::test_b"]), contract)
    with pytest.raises(ValueError):
        pc.misses({"toolchains": {}}, contract)
    record = gate_record("t1", "x86")
    record["failures"] = [{"stage": "gate", "reason": "Rust build /x/ve is not pinned in lean/checkers.lock"},
                          {"stage": "gate", "reason": "Lean audit: exit 1"},
                          {"stage": "coverage", "reason": "1 tests collected at the merge base are not collected"}]
    report = pc.misses(record, contract)
    assert [row["covered"] for row in report["other_failures"]] == [True, False, False]
    assert report["missed"] == [] and report["missed_stages"] == ["gate: Lean audit: exit 1"]


def test_misses_exit_status_and_output(tmp_path, capsys):
    listing = tmp_path / "contract.json"
    listing.write_text(json.dumps(contract_of(("tests/test_a.py", ["pins"]))))
    record = tmp_path / "x86.json"
    record.write_text(json.dumps(gate_record("t1", "x86", ["tests/test_a.py::test_a"])))
    assert pc.main(["misses", str(record), "--list", str(listing)]) == 0
    assert "tests/test_a.py::test_a: in the contract (pins)" in capsys.readouterr().out
    record.write_text(json.dumps(gate_record("t1", "x86", ["tests/test_b.py::test_b"])))
    assert pc.main(["misses", str(record), "--list", str(listing), "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["missed"] == ["tests/test_b.py::test_b"]
    record.write_text(json.dumps(gate_record("t1", "mac", ["tests/test_b.py::test_b"])))
    assert pc.main(["misses", str(record), "--list", str(listing)]) == 2
    record.write_text("{")
    assert pc.main(["misses", str(record), "--list", str(listing)]) == 2


def test_misses_reads_a_real_x86_gate_records_shape():
    """The shape of cand-runs/a40a56df…x86.json (Oct 15): two CPU-deadline failures of test_english_mixed_merge_smoke
    and two failures the Mac shared; the smoke test is a divergence, so it is covered."""
    smoke = "tests/test_english_evidence.py::test_english_mixed_merge_smoke[news-article-0]"
    shared = "tests/test_stage2_norms.py::test_retained_python_route_keeps_the_base_nary_expansion"
    record = gate_record("22edef5b", "x86", [smoke, shared])
    mac = gate_record("22edef5b", "mac", [shared])
    report = pc.misses(record, pc.read_contract(), mac)
    assert report["missed"] == []
    rows = {row["nodeid"]: row for row in report["tests"]}
    assert "divergence" in rows[smoke]["causes"] and rows[shared]["also_failed_on_mac"]


# The contract run: tools/gate.py --contract


CONTRACT_IDS = ["tests/test_a.py::test_a", "tests/test_a.py::test_a2", "tests/test_b.py::test_b",
                "tests/test_b.py::test_b2[1]", "tests/test_c.py::test_c"]


class ContractGate(FakeGate):
    """The gate in a scratch root whose suite is CONTRACT_IDS; a pytest argument selects the IDs it covers."""

    def __init__(self, tmp_path, monkeypatch, selectors=("tests/test_a.py", "tests/test_b.py::test_b2")):
        super().__init__(tmp_path, monkeypatch)
        self.failing = set()
        listing = self.root / "tests/platform-contract.json"
        listing.parent.mkdir(parents=True, exist_ok=True)
        listing.write_text(json.dumps(contract_of(*((selector, ["process"]) for selector in selectors))))

    def command(self, args, *, env, stage, cwd=None):
        if stage not in ("Python collection", "Python suite"):
            return super().command(args, env=env, stage=stage, cwd=cwd)
        self.seen.append((stage, [str(arg) for arg in args]))
        targets = [str(arg) for arg in args if str(arg).startswith("tests")]
        ids = [nodeid for nodeid in CONTRACT_IDS if any(target == "tests" or pc.covers(target, nodeid)
                                                        for target in targets)]
        outcomes = {nodeid: {"outcome": "failed", "reason": "AssertionError"} if nodeid in self.failing
                    else {"outcome": "passed"} for nodeid in ids}
        Path(env["VE_GATE_PYTEST_RESULT"]).write_text(json.dumps(
            {"collected": ids, "selected": ids, "deselected": [], "collection_reports": [],
             "tests": outcomes if stage == "Python suite" else {}, "workers": {"gw0": ids}}))
        if stage == "Python suite" and self.failing & set(ids):
            raise RuntimeError("Python suite: exit 1")
        return ""


@pytest.fixture
def contract_gate(tmp_path, monkeypatch):
    return ContractGate(tmp_path, monkeypatch)


def test_the_contract_run_runs_exactly_the_listed_tests_with_the_gates_stages(contract_gate):
    code, record = contract_gate.run("--contract")
    assert (code, record["status"], record["mode"]) == (0, "contract-passed", "contract")
    assert contract_gate.pytest_targets() == [["tests/test_a.py", "tests/test_b.py::test_b2"]] * 2
    assert record["counts"]["selected"] == 3 and record["failures"] == []
    assert record["stages"] == list(gate.CONTRACT_STAGES)
    stages = contract_gate.stages()
    assert {"Lean build", "Wire contract check", "Rust build", "native Rust tests", "Python suite"} <= set(stages)
    assert "Lean audit" not in stages
    # Nothing is recorded for the commit: a contract run is never a gate result of it.
    assert contract_gate.records == [] and "collected_zlib" not in record.get("collection", {})
    assert record["contract"]["list"] == "tests/platform-contract.json"
    assert record["contract"]["selectors"] == ["tests/test_a.py", "tests/test_b.py::test_b2"]


def test_a_contract_run_is_never_a_full_gates_evidence(contract_gate):
    code, record = contract_gate.run("--contract")
    assert record["status"] != "passed"
    contract_gate.failing = {"tests/test_b.py::test_b2[1]"}
    code, record = contract_gate.run("--contract")
    assert (code, record["status"]) == (1, "failed")
    assert [failure["nodeid"] for failure in record["failures"] if failure["stage"] == "pytest"] == [
        "tests/test_b.py::test_b2[1]"]
    # A full gate on the same scratch tree still runs everything and the audit.
    contract_gate.failing = set()
    code, record = contract_gate.run()
    assert record["mode"] == "full" and "Lean audit" in contract_gate.stages()
    assert contract_gate.pytest_targets() == [["tests"], ["tests"]]


def test_a_listed_test_that_collects_nothing_fails_the_contract_run(tmp_path, monkeypatch):
    fake = ContractGate(tmp_path, monkeypatch, selectors=("tests/test_a.py", "tests/test_d.py::test_gone"))
    code, record = fake.run("--contract")
    assert (code, record["status"]) == (1, "failed")
    assert {"stage": "coverage", "reason": "contract test collected nothing: tests/test_d.py::test_gone"} \
        in record["failures"]


def test_a_malformed_contract_list_fails_the_contract_run(contract_gate):
    (contract_gate.root / "tests/platform-contract.json").write_text(json.dumps({"format": "x", "tests": []}))
    code, record = contract_gate.run("--contract")
    assert (code, record["status"]) == (1, "failed")
    assert record["failures"][0]["stage"] == "gate" and "Python suite" not in contract_gate.stages()


@pytest.mark.parametrize("flags", [("--contract", "--rerun-failed"), ("--contract", "--base", "main")])
def test_the_contract_run_takes_no_rerun_or_base(contract_gate, monkeypatch, flags):
    monkeypatch.setattr(sys, "argv", ["gate.py", *flags])
    with pytest.raises(SystemExit):
        gate.main()


def test_the_contract_runs_default_record_is_not_the_full_gates(contract_gate, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["gate.py", "--contract"])
    assert gate.main() == 0
    assert json.loads((contract_gate.root / "platform-contract-result.json").read_text())["mode"] == "contract"
    assert not (contract_gate.root / "gate-result.json").exists()


def test_run_starts_the_checkouts_own_gate_in_contract_mode(tmp_path, monkeypatch):
    checkout = tmp_path / "checkout"
    (checkout / "tools").mkdir(parents=True)
    (checkout / "tools/gate.py").write_text("")
    started = []
    monkeypatch.setattr(pc.os, "execv", lambda path, argv: started.append(argv))
    pc.main(["run", "--checkout", str(checkout), "--workers", "8", "--output", str(tmp_path / "r.json"),
             "--no-quarantine"])
    assert started == [[sys.executable, str(checkout.resolve() / "tools/gate.py"), "--contract", "--workers", "8",
                        "--output", str((tmp_path / "r.json").resolve()), "--no-quarantine"]]
    with pytest.raises(SystemExit):
        pc.main(["run", "--checkout", str(tmp_path / "nothing")])
