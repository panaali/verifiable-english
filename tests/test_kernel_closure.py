"""The kernel boundary's measuring tool (docs/spec/kernel-boundary.md, sections 2 and 6).

These tests cover the Python half (the registry's shape, the line counting, the requests sent to
the Lean half, the census and the saved baseline's consistency) and, on the built `VE`, the Lean
half's test of which theorems state a subject's answer. The full measurement
(`python3 tools/kernel_closure.py`, minutes) is run by hand and saved in
`docs/kernel/closure-baseline.json`; no gate tool runs it yet (KB-1 wires it).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import lean_build

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import kernel_closure  # noqa: E402
from lean_statements import inventory_path  # noqa: E402

REGISTRY = json.loads((ROOT / "tools/kernel-paths.json").read_text())
BASELINE = json.loads((ROOT / "docs/kernel/closure-baseline.json").read_text())
STATEMENTS = dict(re.findall(r"^theorem (\S+)\n((?:(?!theorem ).*\n)*)",
                             inventory_path("lean/statements.txt").read_text(), re.MULTILINE))
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
    through to the norms runner, which runs `Norms.Plain.run`), and whichever kernel theorem's statement
    unfolds to it (review kb-0 F3: `runCase_dispatch` read route's uncovered runners into its spec)."""
    a = {"name": "a", "tier": "kernel", "entry": ["Ea"], "theorems": ["Ta"], "subject": ["Sa"],
         "uncovered": [{"name": "Ua", "kinds": ["k"], "why": "a kind no listed theorem covers"}]}
    b = {"name": "b", "tier": "kernel", "entry": ["Eb"], "theorems": ["Tb"], "subject": ["Sb"]}
    c = {"name": "c", "tier": "candidate", "entry": ["Ec"], "theorems": ["Tc"], "subject": ["Sc"]}
    keys = {"paths": ["a"], "validators": {"v": ["V1", "V2"]}}
    out = {r["name"]: r for r in kernel_closure.requests({"paths": [a, b, c], "keys": keys})}
    assert out["body:a"]["opaque"] == ["Ua"] and out["body:b"]["opaque"] == ["Ua"]
    assert "body:c" not in out
    assert out["wrap:a"]["opaque"] == ["Sa"]
    assert out["spec:a"]["opaque"] == ["Sa", "Ua"] and out["spec:b"]["opaque"] == ["Sb", "Ua"]
    assert out["spec:c"]["opaque"] == ["Sc"]
    named = {"paths": [dict(a, subject=["Sa", "Ua"])]}
    assert kernel_closure.requests(named)[0]["opaque"] == ["Sa", "Ua"]
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


GATES = ["VE.Order.certificate_runCase_profiles", "VE.Order.profile_gate"]
SOUND = ["VE.CertificateWire.Query.accepts_sound", "VE.CertificateWire.ClosureQuery.accepts_sound"]
ACCEPTS = ["VE.CertificateWire.Query.accepts", "VE.CertificateWire.ClosureQuery.accepts"]
SPLITTER = "_private.VE.Route.Admission.0.VE.Route.Admission.NodeAdmitted.match_1.splitter"
ROUTE = next(path for path in KERNEL if path["name"] == "route")


@pytest.fixture(scope="module")
def lean_answer(lake):
    """One run of the Lean half (one load of the environment) for every test of it below: probe
    requests, and this registry's spec and wrap requests of every kernel path."""
    measured = [r for r in kernel_closure.requests(REGISTRY)
                if r["name"].split(":")[0] in {"spec", "wrap"} and r["name"].split(":")[1] in {p["name"] for p in KERNEL}]
    raw, census = kernel_closure.run_lean([
        {"name": "runner", "roots": GATES + SOUND, "opaque": ["VE.CertificateWire.runCase"]},
        {"name": "decision", "roots": GATES + SOUND, "opaque": ACCEPTS},
        {"name": "soft", "roots": ["VE.SoftNorms.Run.soft_wire_acceptance"], "opaque": ["VE.SoftNorms.Run.runCase"]},
        {"name": "splitter", "roots": [SPLITTER], "opaque": [], "mode": "run"},
        {"name": "route-uncut", "roots": ROUTE["theorems"], "opaque": ROUTE["subject"]},
        {"name": "open-tail", "roots": ["VE.KernelClosure.openTailFixture_stated"], "opaque": []},
        {"name": "keyed", "roots": ["VE.KernelClosure.keyedFixture_stated"], "opaque": []},
        *measured,
    ], [], [], HANG_TIMEOUT)
    return raw, census


def test_the_lean_half_tells_a_gate_theorem_from_one_that_states_the_answer(lean_answer):
    """`answersStated` on the compiled statements: the profile gates (`runCase j = .ok r → P j`, `r`
    unused) state no answer; `Query.accepts q = true → Entails …` and `runCase j = .ok answer → …
    answer …` do. A private `match_1.splitter` that `unfold` creates is ranged by its user name."""
    raw, census = lean_answer
    assert census == []
    assert raw["runner"]["stated"] == {"VE.CertificateWire.runCase": []}
    assert raw["decision"]["stated"] == {ACCEPTS[0]: [SOUND[0]], ACCEPTS[1]: [SOUND[1]]}
    assert raw["soft"]["stated"] == {"VE.SoftNorms.Run.runCase": ["VE.SoftNorms.Run.soft_wire_acceptance"]}
    assert raw["splitter"]["unranged"] == [] and raw["splitter"]["missing"] == []
    assert any(d["name"] == "VE.Route.Admission.NodeAdmitted" for d in raw["splitter"]["decls"])


def test_the_lean_half_finds_answer_fields_left_open_and_passes_fields_read_by_key(lean_answer):
    """Review kb-7 F1, the class: `Json.mkObj` keeps the last value of a repeated key, so a statement
    that writes an answer as `mkObj (fields ++ rest)` with `rest` existentially open lets the tail
    override every field it states. The Lean half's `hasOpenFields` finds the tool's own open-tail
    fixture and passes the same answer read by key."""
    raw, _ = lean_answer
    assert raw["open-tail"]["open_fields"] == ["VE.KernelClosure.openTailFixture"]
    assert raw["keyed"]["open_fields"] == []


def test_no_kernel_statement_leaves_answer_fields_open(lean_answer):
    """Review kb-7 F1: no listed theorem of a kernel path, and no definition its statement reaches,
    quantifies existentially over a list of answer fields (`soft_wire_elaborate`'s
    `ElaborationAnswer` did, with `rest` free after the six fields it named)."""
    raw, _ = lean_answer
    assert {p["name"]: raw["spec:" + p["name"]]["open_fields"] for p in KERNEL} == {p["name"]: [] for p in KERNEL}


def test_an_open_field_statement_is_a_problem_on_a_kernel_path_only():
    kernel = {"name": "k", "tier": "kernel"}
    assert kernel_closure.open_field_problems(kernel, ["M.Answer"]) == [
        "k: a statement leaves answer fields open (state them by key): M.Answer"]
    assert kernel_closure.open_field_problems(kernel, []) == []
    assert kernel_closure.open_field_problems(dict(kernel, tier="candidate"), ["M.Answer"]) == []


def lean_check(source: str, where: Path) -> subprocess.CompletedProcess[str]:
    """Elaborate one Lean source against the built `VE`."""
    file = where / "Probe.lean"
    file.write_text(source)
    env = dict(os.environ, PATH=str(Path.home() / ".elan/bin") + os.pathsep + os.environ.get("PATH", ""))
    return subprocess.run(("lake", "env", "lean", str(file)), cwd=ROOT / "lean", env=env,
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)


ELABORATE_PROBE = """import VE.SoftNorms.ElaborateSound
open Lean VE.SoftNorms.Run
"""


def test_a_soft_elaborate_answer_has_no_tail_that_overrides_its_fields(lake, tmp_path):
    """Review kb-7 PROBE F1: the reviewer's counterexample (a `Wire.ok` answer whose tail rebinds
    `background` to `null`) is not an `ElaborationAnswer`: it does not elaborate, and its negation is
    a theorem (`not_elaborationAnswer_of_null_background`) that a client's reading follows from."""
    probe = ELABORATE_PROBE + (
        "example (D : VE.SoftNorms.SoftDoc) (e : Json) : ∃ a : Json, ElaborationAnswer \"x\" D a ∧ "
        "a.getObjValD \"background\" = Json.null := by\n"
        "  obtain ⟨p, d, r, o, b, q, _, _, hb, hq⟩ := regeneratedCore_fields D e\n"
        "  exact ⟨VE.Route.Wire.ok \"x\" ([(\"environment_prime\", p), (\"decisions\", d), (\"derived\", r), "
        "(\"order\", o), (\"background\", b), (\"premises\", q)] ++ [(\"background\", Json.null)]), "
        "⟨p, d, r, o, b, q, [(\"background\", Json.null)], rfl, hb, hq⟩, rfl⟩\n")
    assert lean_check(probe, tmp_path).returncode != 0
    control = ELABORATE_PROBE + (
        "example (D : VE.SoftNorms.SoftDoc) : ¬ ∃ a : Json, ElaborationAnswer \"x\" D a ∧ "
        "a.getObjValD \"background\" = Json.null :=\n"
        "  fun ⟨a, ha, hn⟩ => not_elaborationAnswer_of_null_background \"x\" D a hn ha\n"
        "example (D : VE.SoftNorms.SoftDoc) (a : Json) (h : ElaborationAnswer \"x\" D a) :\n"
        "    BackgroundField D (a.getObjValD \"background\") ∧ PremisesField D (a.getObjValD \"premises\") :=\n"
        "  (elaborationAnswer_reads h).2.2\n")
    done = lean_check(control, tmp_path)
    assert done.returncode == 0, done.stdout[-2000:] + done.stderr[-2000:]


def test_the_spec_claims_no_carry_that_no_theorem_states():
    """Review kb-7 PROBE F2: `soft_wire_elaborate` states the `background` and `premises` fields of a
    `soft-elaborate` answer, not that the premises a harness carries to a certificate case are those
    fields (the Python client reads only `premises`' labels and takes the coherence premises from
    `colliding_pairs`). The spec says so and makes neither of the two claims the review found."""
    text = " ".join((ROOT / "docs/spec/kernel-boundary.md").read_text().split())
    assert [s for s in ("over exactly these fields", "states that those premises are the document") if s in text] == []
    assert "No theorem yet ties what the keys' certificates replay to these fields" in text
    assert "none yet states that the premises the harness carries to the certificate case are those fields" in text
    lean = " ".join((ROOT / "lean/VE/SoftNorms/ElaborateSound.lean").read_text().split())
    assert "has the route replay a certificate over them" not in lean
    assert "nor about what a harness carries from this answer to a later certificate case" in lean


def test_no_kernel_spec_or_wrap_reads_an_uncovered_runner(lean_answer):
    """Review kb-0 F3: the records say `uncovered` code is outside the kernel, but only the census body
    was cut there. Route's `runCase_dispatch` states `runCase = dispatch …`, so its spec read
    `Definitions.Bundle.runBundle` and `Route.Run.runAdmit` (the `bundle` and `admission` kinds) into
    the kernel's 8,956 lines. Every kernel path's spec is now cut at every `uncovered` name, and the
    tool reports one a kernel spec or wrap still reaches."""
    raw, _ = lean_answer
    uncovered = kernel_closure.uncovered_names(REGISTRY)
    uncut = {d["name"] for d in raw["route-uncut"]["decls"]}
    assert {"VE.Definitions.Bundle.runBundle", "VE.Route.Run.runAdmit"} <= uncut  # the finding's example
    for path in KERNEL:
        parts = {part: raw[f"{part}:{path['name']}"] for part in ("spec", "wrap")}
        assert all(not part["missing"] for part in parts.values()), path["name"]
        assert kernel_closure.uncovered_problems(path, parts, uncovered) == [], path["name"]
        assert {d["name"] for part in parts.values() for d in part["decls"]}.isdisjoint(uncovered), path["name"]


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
        assert sorted(saved[path["name"]]["stated"]) == sorted(path["subject"]), path["name"]
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


def lean_part(decls=(), stated=None, unranged=(), missing=(), open_fields=()):
    return {"lines": sum(b - a + 1 for _, a, b in decls), "axioms": [], "modules": {}, "flagged": [],
            "missing": list(missing), "unranged": list(unranged), "stated": stated or {},
            "open_fields": list(open_fields),
            "decls": [{"name": f"{m}.d{a}", "module": m, "from": a, "to": b} for m, a, b in decls]}


def test_measure_reports_what_the_lean_half_finds(monkeypatch):
    """`measure` on a fixed Lean answer: kernel and keyed totals, a subject no theorem states, an unranged
    constant, and a writer under a subject that no covered_writers entry names."""
    registry = {"verdict_tokens": ["CONFLICT"], "keys": {"paths": ["k"], "validators": {"v": ["V"]}}, "paths": [
        {"name": "k", "tier": "kernel", "entry": ["E"], "theorems": ["T"], "subject": ["S", "S2"]},
        {"name": "c", "tier": "candidate", "entry": ["Ec"], "theorems": ["Tc"], "subject": ["Sc"]}]}
    raw = {"spec:k": lean_part([("M", 1, 10)], {"S": ["T"], "S2": []}), "wrap:k": lean_part([("M", 5, 12)]),
           "body:k": lean_part([("M", 30, 31)]), "spec:c": lean_part([("M", 40, 49)], {"Sc": []}),
           "wrap:c": lean_part([("M", 50, 50)], unranged=["_private.X.match_1"]),
           "keys:v": lean_part([("N", 1, 3)])}
    census = [{"name": "W", "module": "M", "from": 30, "to": 31, "tokens": ["CONFLICT"]}]
    monkeypatch.setattr(kernel_closure, "run_lean", lambda *args, **kw: (raw, census))
    result = kernel_closure.measure(registry)
    assert result["kernel_lines"] == 12 and result["keyed_lines"] == 15 and result["keyed_kernel_lines"] == 12
    assert [row["lines"] for row in result["paths"]] == [12, 11]
    assert result["paths"][0]["stated"] == {"S": ["T"], "S2": []}
    assert result["verdict_writers"] == [{"name": "W", "module": "M", "tokens": ["CONFLICT"],
                                          "in_kernel": False, "inside": None}]
    problems = result["problems"]
    assert "c: reached constants with no source range (not counted): _private.X.match_1" in problems
    assert "k: no listed theorem states what the answer of S2 means" in problems
    assert not any("answer of Sc" in p for p in problems)
    assert any(p.startswith("verdict writer W runs under a kernel subject") for p in problems)
    assert len(problems) == 3
    registry["paths"][0]["covered_writers"] = [{"name": "W", "kinds": ["x"], "theorems": ["T"]}]
    covered = kernel_closure.measure(registry)
    assert covered["verdict_writers"][0]["inside"] == "body" and len(covered["problems"]) == 2


def test_measure_reports_an_uncovered_runner_a_kernel_spec_or_wrap_reaches(monkeypatch):
    """Review kb-0 F3 on a fixed Lean answer: an `uncovered` declaration in a kernel path's spec or wrap
    would count inside the kernel, so it is a problem (exit 1); on a candidate path it is not; the
    spec's `stated` keeps the subjects only (the uncovered names are opaque there too)."""
    uncovered = [{"name": "M.d20", "kinds": ["k"], "why": "a kind no listed theorem covers"},
                 {"name": "M.d40", "kinds": ["k"], "why": "a kind no listed theorem covers"}]
    registry = {"verdict_tokens": [], "paths": [
        {"name": "k", "tier": "kernel", "entry": ["E"], "theorems": ["T"], "subject": ["S"], "uncovered": uncovered},
        {"name": "c", "tier": "candidate", "entry": ["Ec"], "theorems": ["Tc"], "subject": ["Sc"]}]}
    raw = {"spec:k": lean_part([("M", 1, 10), ("M", 20, 21)], {"S": ["T"], "M.d20": [], "M.d40": []}),
           "wrap:k": lean_part([("M", 40, 41)]), "body:k": lean_part([]),
           "spec:c": lean_part([("M", 20, 21)], {"Sc": ["Tc"]}), "wrap:c": lean_part([("M", 40, 41)])}
    monkeypatch.setattr(kernel_closure, "run_lean", lambda *args, **kw: (raw, []))
    result = kernel_closure.measure(registry)
    assert result["problems"] == [
        "k: uncovered M.d20 is reached by the path's spec (it would count inside the kernel)",
        "k: uncovered M.d40 is reached by the path's wrap (it would count inside the kernel)"]
    assert result["paths"][0]["stated"] == {"S": ["T"]}
    raw["spec:k"], raw["wrap:k"] = lean_part([("M", 1, 10)], {"S": ["T"]}), lean_part([("M", 5, 12)])
    assert kernel_closure.measure(registry)["problems"] == []
