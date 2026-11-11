"""The kernel boundary's measuring tool (docs/spec/kernel-boundary.md, sections 2 and 6).

These tests cover the Python half (the registry's shape, the line counting, the requests sent to
the Lean half, the census and the saved baseline's consistency) and, on the built `VE`, the Lean
half's test of which theorems state a subject's answer. The full measurement
(`python3 tools/kernel_closure.py`, minutes) is run by hand and saved in
`docs/kernel/closure-baseline.json`; no gate tool runs it yet (KB-1 wires it).
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import lean_build

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import kernel_closure  # noqa: E402

REGISTRY = json.loads((ROOT / "tools/kernel-paths.json").read_text())
BASELINE = json.loads((ROOT / "docs/kernel/closure-baseline.json").read_text())
STATEMENTS = dict(re.findall(r"^theorem (\S+)\n((?:(?!theorem ).*\n)*)",
                             (ROOT / "lean/statements.txt").read_text(), re.MULTILINE))
KERNEL = [path for path in REGISTRY["paths"] if path["tier"] == "kernel"]


def test_overlapping_ranges_are_counted_once():
    ranges = [("A", 1, 10), ("A", 5, 12), ("A", 20, 20), ("B", 1, 3), ("A", 2, 3)]
    assert kernel_closure.covered(ranges) == 12 + 1 + 3
    assert kernel_closure.covered([]) == 0
    assert kernel_closure.covered([("A", 7, 7), ("A", 7, 7)]) == 1


def test_every_path_names_its_entry_theorems_and_subject():
    names = [path["name"] for path in REGISTRY["paths"]]
    assert len(names) == len(set(names))
    for path in REGISTRY["paths"]:
        assert path["tier"] in {"kernel", "candidate"}, path["name"]
        assert path["entry"] and path["theorems"] and path["subject"], path["name"]
        assert len(path["theorems"]) == len(set(path["theorems"])), path["name"]
        for exit_ in path.get("nonverdict", []):
            assert exit_["name"] and len(exit_["why"]) > 20, path["name"]
    assert REGISTRY["verdict_tokens"] == sorted(set(REGISTRY["verdict_tokens"]), key=REGISTRY["verdict_tokens"].index)


def test_the_requests_leave_the_subject_unread_and_cut_the_wrap_at_it():
    path = {"name": "p", "entry": ["E"], "theorems": ["T"], "subject": ["S"], "delegates": ["D"],
            "nonverdict": [{"name": "N", "why": "a reviewed exit that carries no verdict"}]}
    spec, wrap = kernel_closure.requests({"paths": [path]})
    assert spec == {"name": "spec:p", "roots": ["T"], "opaque": ["S"]}
    assert wrap == {"name": "wrap:p", "roots": ["E"], "opaque": ["S", "D", "N"], "mode": "run"}
    *_, body = kernel_closure.requests({"paths": [dict(path, tier="kernel")]})
    assert body == {"name": "body:p", "roots": ["S"], "opaque": [], "mode": "run"}


def test_every_subject_body_is_cut_at_every_uncovered_kind():
    """Uncovered code is outside the kernel whichever kernel subject runs it (a soft-norms case falls
    through to the norms runner, which runs `Norms.Plain.run`)."""
    a = {"name": "a", "tier": "kernel", "entry": ["Ea"], "theorems": ["Ta"], "subject": ["Sa"],
         "uncovered": [{"name": "Ua", "kinds": ["k"], "why": "a kind no listed theorem covers"}]}
    b = {"name": "b", "tier": "kernel", "entry": ["Eb"], "theorems": ["Tb"], "subject": ["Sb"]}
    c = {"name": "c", "tier": "candidate", "entry": ["Ec"], "theorems": ["Tc"], "subject": ["Sc"]}
    keys = {"paths": ["a"], "validators": {"v": ["V1", "V2"]}}
    out = {r["name"]: r for r in kernel_closure.requests({"paths": [a, b, c], "keys": keys})}
    assert out["body:a"]["opaque"] == ["Ua"] and out["body:b"]["opaque"] == ["Ua"]
    assert "body:c" not in out
    assert out["wrap:a"]["opaque"] == ["Sa"]
    assert out["keys:v"] == {"name": "keys:v", "roots": ["V1", "V2"], "opaque": [], "mode": "run"}


def statement_states(theorem: str, subject: str) -> bool:
    """Review kb-0 F1's probe: the statement names the subject and says something an answer means."""
    text = STATEMENTS.get(theorem, "")
    return subject + "@" in text and re.search(r'"valid"|"verdict"|Answer|Entails', text) is not None


def test_every_kernel_subject_has_a_listed_theorem_that_states_its_answer():
    """Review kb-0 F1: `certificate` named `CertificateWire.runCase` as its subject although its only
    theorems on it were profile gates; the binding check and the closure branch were then neither spec
    nor wrap. Every kernel subject must be named by a listed theorem that says what an answer means."""
    bad = [(path["name"], subject) for path in KERNEL for subject in path["subject"]
           if not any(statement_states(theorem, subject) for theorem in path["theorems"])]
    assert bad == []
    assert not any(statement_states(t, "VE.CertificateWire.runCase") for t in STATEMENTS)


def test_the_saved_baseline_has_a_stating_theorem_for_every_kernel_subject():
    """The same rule, as the Lean half decided it from the compiled statements (`answersStated`)."""
    rows = {row["name"]: row for row in BASELINE["paths"]}
    for path in KERNEL:
        stated = rows[path["name"]]["stated"]
        assert set(stated) == set(path["subject"]), path["name"]
        for subject, theorems in stated.items():
            assert theorems and set(theorems) <= set(path["theorems"]), (path["name"], subject)


def test_a_kernel_subject_no_theorem_states_is_a_problem():
    path = {"name": "certificate", "tier": "kernel", "subject": ["VE.CertificateWire.runCase"]}
    assert kernel_closure.subject_problems(path, {"VE.CertificateWire.runCase": []}) == [
        "certificate: no listed theorem states what the answer of VE.CertificateWire.runCase means"]
    assert kernel_closure.subject_problems(path, {}) != []
    assert kernel_closure.subject_problems(path, {"VE.CertificateWire.runCase": ["T"]}) == []
    assert kernel_closure.subject_problems(dict(path, tier="candidate"), {}) == []


@pytest.fixture(scope="module")
def lake():
    found = shutil.which("lake")
    if found is None:
        pytest.skip("lake is not available")
    lean_build("VE", "ve_service")
    return found


def test_the_lean_half_tells_a_gate_theorem_from_one_that_states_the_answer(lake):
    """`answersStated` on the compiled statements: the profile gates (`runCase j = .ok r → P j`, `r`
    unused) state no answer; `Query.accepts q = true → Entails …` and `runCase j = .ok answer → …
    answer …` do. A private `match_1.splitter` that `unfold` creates is ranged by its user name."""
    gates = ["VE.Order.certificate_runCase_profiles", "VE.Order.profile_gate"]
    sound = ["VE.CertificateWire.Query.accepts_sound", "VE.CertificateWire.ClosureQuery.accepts_sound"]
    accepts = ["VE.CertificateWire.Query.accepts", "VE.CertificateWire.ClosureQuery.accepts"]
    splitter = "_private.VE.Route.Admission.0.VE.Route.Admission.NodeAdmitted.match_1.splitter"
    raw, census = kernel_closure.run_lean([
        {"name": "runner", "roots": gates + sound, "opaque": ["VE.CertificateWire.runCase"]},
        {"name": "decision", "roots": gates + sound, "opaque": accepts},
        {"name": "soft", "roots": ["VE.SoftNorms.Run.soft_wire_acceptance"], "opaque": ["VE.SoftNorms.Run.runCase"]},
        {"name": "splitter", "roots": [splitter], "opaque": [], "mode": "run"},
    ], [], [], HANG_TIMEOUT)
    assert census == []
    assert raw["runner"]["stated"] == {"VE.CertificateWire.runCase": []}
    assert raw["decision"]["stated"] == {accepts[0]: [sound[0]], accepts[1]: [sound[1]]}
    assert raw["soft"]["stated"] == {"VE.SoftNorms.Run.runCase": ["VE.SoftNorms.Run.soft_wire_acceptance"]}
    assert raw["splitter"]["unranged"] == [] and raw["splitter"]["missing"] == []
    assert any(d["name"] == "VE.Route.Admission.NodeAdmitted" for d in raw["splitter"]["decls"])


def census_row(name, module="VE.M", first=1):
    return {"name": name, "module": module, "from": first, "to": first + 1, "tokens": ["CONFLICT"]}


def test_a_writer_under_a_subject_is_inside_only_when_a_theorem_covers_its_kind():
    """Review kb-0 F1 sweep: `runSoftKind` (soft-certificate, soft-conflict) counted as inside the kernel
    because a kernel subject runs it, though no theorem covers those kinds."""
    census = [census_row("W.spec", first=1), census_row("W.covered", first=10), census_row("W.uncovered", first=20),
              census_row("W.outside", first=30), census_row("W.example", module="VE.X.Examples", first=1)]
    spec_wrap, body = {("VE.M", 1)}, {("VE.M", 10), ("VE.M", 20)}
    rows, problems = kernel_closure.classify_writers(census, spec_wrap, body, {"W.covered"})
    inside = {row["name"]: row["inside"] for row in rows}
    assert inside == {"W.spec": "spec-or-wrap", "W.covered": "body", "W.uncovered": None, "W.outside": None}
    assert {row["name"]: row["in_kernel"] for row in rows} == {
        "W.spec": True, "W.covered": True, "W.uncovered": False, "W.outside": False}
    assert len(problems) == 1 and "W.uncovered" in problems[0]
    _, stale = kernel_closure.classify_writers(census, spec_wrap, body, {"W.covered", "W.uncovered", "W.outside"})
    assert len(stale) == 1 and "W.outside" in stale[0] and "not a verdict writer reached only" in stale[0]


def test_the_registry_problems_are_found_before_any_lean_runs():
    assert kernel_closure.registry_problems(REGISTRY) == []
    path = {"name": "p", "tier": "kernel", "theorems": ["T"],
            "covered_writers": [{"name": "W", "kinds": ["k"], "theorems": ["T", "Other"]}],
            "uncovered": [{"name": "U", "kinds": ["k"], "why": "short"}]}
    problems = kernel_closure.registry_problems({"paths": [path], "keys": {"paths": ["p", "q"]}})
    assert any("cites Other" in p for p in problems)
    assert any("uncovered U names no case kind or no reason" in p for p in problems)
    assert any("keys: q is not a path" in p for p in problems)
    candidate = dict(path, tier="candidate", covered_writers=[], uncovered=[{"name": "U", "kinds": ["k"], "why": "x" * 30}])
    assert kernel_closure.registry_problems({"paths": [candidate]}) == ["p: uncovered on a candidate path: U"]


def test_the_saved_census_counts_uncovered_writers_outside_and_covered_ones_by_their_theorem():
    """Each writer the baseline counts inside through a subject is a `covered_writers` entry whose theorems
    are statements about that path's subject for each of its case kinds; each uncovered runner's own
    writers count outside."""
    writers = {w["name"]: w for w in BASELINE["verdict_writers"]}
    covered = {entry["name"]: (path, entry) for path in KERNEL for entry in path.get("covered_writers", [])}
    assert {n for n, w in writers.items() if w["inside"] == "body"} == set(covered)
    for name, (path, entry) in covered.items():
        for theorem in entry["theorems"]:
            text = STATEMENTS[theorem]
            assert any(subject + "@" in text for subject in path["subject"]), theorem
            assert all(f'"{kind}"' in text for kind in entry["kinds"]), theorem
    uncovered = {entry["name"] for path in KERNEL for entry in path.get("uncovered", [])}
    assert {"VE.SoftNorms.Run.runSoftKind", "VE.Norms.Plain.run"} <= uncovered
    for name in uncovered & set(writers):
        assert writers[name]["in_kernel"] is False, name
    assert writers["VE.SoftNorms.Run.runSoftKind"]["in_kernel"] is False
    assert writers["VE.SoftNorms.Wire.residualStatus"]["in_kernel"] is False


def test_the_check_fails_above_the_saved_total_and_passes_at_it():
    assert kernel_closure.check_total({"kernel_lines": 100}, 100)[0] is True
    assert kernel_closure.check_total({"kernel_lines": 99}, 100)[0] is True
    ok, message = kernel_closure.check_total({"kernel_lines": 101}, 100)
    assert ok is False and "from 100 to 101" in message


def test_keyed_lines_count_the_kernel_part_once():
    registry = {"keys": {"paths": ["a"], "validators": {"v": []}}}
    figures = kernel_closure.keyed(registry, {"a": [("M", 1, 10)]}, {"v": [("N", 1, 5)]}, [("M", 6, 20)])
    assert figures == {"keyed_lines": 15, "keyed_kernel_lines": 5}
    assert kernel_closure.keyed({}, {}, {}, []) == {}


def test_fixture_modules_are_not_verdict_writers():
    assert kernel_closure.is_fixture("VE.Service.DocumentChainChecks")
    assert kernel_closure.is_fixture("VE.Compose.Examples")
    assert kernel_closure.is_fixture("ResponseShape.Schemas.NormDefaults")
    assert not kernel_closure.is_fixture("VE.Service.Document")


def test_the_saved_baseline_is_of_this_registry():
    """The baseline was measured with this registry: same paths, same tiers, and the kernel total
    is at least its largest kernel path and at most the sum of them."""
    saved = {row["name"]: row for row in BASELINE["paths"]}
    assert set(saved) == {path["name"] for path in REGISTRY["paths"]}
    for path in REGISTRY["paths"]:
        assert saved[path["name"]]["tier"] == path["tier"]
        assert saved[path["name"]]["theorems"] == len(path["theorems"])
    kernel = [row["lines"] for row in saved.values() if row["tier"] == "kernel"]
    assert max(kernel) <= BASELINE["kernel_lines"] <= sum(kernel)
    assert BASELINE["problems"] == []


def test_the_kernel_is_within_the_signed_total():
    """Section 6: the kernel total rises only with the architect's signature (docs/kernel/ALLOWANCES.md)."""
    text = (ROOT / "docs/kernel/ALLOWANCES.md").read_text()
    [figure] = re.findall(r"^signed total: ([0-9,]+) lines$", text, flags=re.MULTILINE)
    signed = int(figure.replace(",", ""))
    assert BASELINE["kernel_lines"] <= signed


RECORDS = ["tests/test_kernel_closure.py", "tools/kernel_closure.py", "tools/kernel_closure.lean",
           "tools/kernel-paths.json", "tools/kernel_trace.py", "docs/spec/kernel-boundary.md",
           "docs/kernel/ALLOWANCES.md", "docs/kernel/frozen-keys-20261111.md"]
GATE_CLAIM = re.compile(r"\b(?:runs?|is\s+run|is\s+checked)\s+in\s+the\s+gate\b", re.IGNORECASE)


def test_no_record_says_the_measure_is_gated_before_a_gate_tool_runs_it():
    """Review kb-0 F2: this file's docstring said the Lean half ran in the gate; nothing in `tools/` ran
    it. Until a gate tool names `kernel_closure`, no record of the batch may say so."""
    wired = any("kernel_closure" in tool.read_text() for tool in (ROOT / "tools").glob("gate*.py"))
    claims = [(name, m.group(0)) for name in RECORDS for m in GATE_CLAIM.finditer((ROOT / name).read_text())]
    assert wired or claims == []
    assert GATE_CLAIM.search("the Lean half runs in the " + "gate, not here")  # the review's quote, split


def figure(n: int) -> str:
    return f"{n:,}"


def test_the_records_quote_the_saved_measurement():
    """The specification's table and figures, the frozen keys' figures and the signed total are those of
    `closure-baseline.json` (review kb-0 F1: they kept 9,565 and 17,355 after the measure changed)."""
    spec = (ROOT / "docs/spec/kernel-boundary.md").read_text()
    prose = " ".join(spec.split())
    rows = {row["name"]: row for row in BASELINE["paths"]}
    table = re.findall(r"^\| (\w+)(?: \(`[^`]*`\))? \| (kernel|candidate) \| (\d+) \| ([\d,]+) \| ([\d,]+) \| ([\d,]+) \|$",
                       spec, flags=re.MULTILINE)
    assert sorted(name for name, *_ in table) == sorted(rows)
    for name, tier, theorems, spec_lines, wrap_lines, lines in table:
        row = rows[name]
        assert (tier, int(theorems), spec_lines, wrap_lines, lines) == (
            row["tier"], row["theorems"], figure(row["spec_lines"]), figure(row["wrap_lines"]), figure(row["lines"])), name
    kernel = figure(BASELINE["kernel_lines"])
    assert f"| **kernel, distinct lines** | | | | | **{kernel}** |" in spec
    assert f"**{kernel} lines (M)**" in prose and f"kernel at most {kernel} now" in prose
    writers = BASELINE["verdict_writers"]
    outside = [w for w in writers if not w["in_kernel"]]
    modules = len({w["module"] for w in outside})
    assert f"| {len(writers)}, of them {len(outside)} in {modules} modules outside the kernel (M) |" in spec
    assert f"Today {len(writers)} definitions write a verdict token and {len(outside)} of them, in {modules} modules" in prose
    keyed, keyed_kernel = figure(BASELINE["keyed_lines"]), figure(BASELINE["keyed_kernel_lines"])
    assert f"validators in full) | {keyed} |" in spec and f"| of which in the proved kernel | {keyed_kernel} |" in spec
    frozen = " ".join((ROOT / "docs/kernel/frozen-keys-20261111.md").read_text().split())
    assert f"**{keyed} distinct lines**" in frozen and f"The proved kernel is {keyed_kernel} of them" in frozen
    allowances = (ROOT / "docs/kernel/ALLOWANCES.md").read_text()
    assert f"signed total: {kernel} lines" in allowances
