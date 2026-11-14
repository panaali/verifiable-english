"""The kernel boundary's measuring tool (docs/spec/kernel-boundary.md, sections 2 and 6).

These tests cover the Python half (the registry's shape, the line counting, the requests sent to
the Lean half, the census and the saved baseline's consistency) and, on the built `VE`, the Lean
half's test of which theorems state a subject's answer. The full measurement
(`python3 tools/kernel_closure.py`, minutes) is saved in `docs/kernel/closure-baseline.json` by
`tools/regen_generated.py` (entry `kernel-closure`); the release gate runs its `--check` (KB-1).
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
import regen_generated  # noqa: E402
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


def test_a_listed_theorem_sits_no_lower_than_the_runner_its_statement_uses():
    """A module whose listed theorem's statement uses a path's subject imports the subject's module,
    so its layer (`tools/layer_policy.py`) is at least the subject's: KB-7's `VE.Route.MeteredWire`
    and `VE.SoftNorms.ElaborateSound` are layer 4, like `VE.Route.RunSound`. Seeded for review kb-7
    F-ready1: without ElaborateSound's entry the module falls to layer 2 under its layer-4 runner."""
    import layer_policy
    module_of = dict(re.findall(r"^\S+ \w+ (\S+)@(\S+)$", inventory_path("lean/declarations.txt").read_text(), re.M))
    pairs = {(path["name"], t, s) for path in REGISTRY["paths"] for t in path["theorems"] for s in path.get("subject", [])
             if f" {s}@{module_of[s]}" in STATEMENTS[t]}
    assert ("softNorms", "VE.SoftNorms.Run.soft_wire_elaborate", "VE.SoftNorms.Run.runCase") in pairs
    assert ("metered", "VE.Route.MeteredRun.runWith_sound", "VE.Route.MeteredRun.runWith") in pairs
    low = sorted((name, module_of[t], layer_policy.lean_layer(module_of[t]), module_of[s], layer_policy.lean_layer(module_of[s]))
                 for name, t, s in pairs if layer_policy.lean_layer(module_of[t]) < layer_policy.lean_layer(module_of[s]))
    assert low == []


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


KINDS = {"x": {"theorem": "T"}}  # a synthetic kernel path's kind table


def lean_part(decls=(), stated=None, unranged=(), missing=(), open_fields=()):
    return {"lines": sum(b - a + 1 for _, a, b in decls), "axioms": [], "modules": {}, "flagged": [],
            "missing": list(missing), "unranged": list(unranged), "stated": stated or {},
            "open_fields": list(open_fields),
            "decls": [{"name": f"{m}.d{a}", "module": m, "from": a, "to": b} for m, a, b in decls]}


def test_measure_reports_what_the_lean_half_finds(monkeypatch):
    """`measure` on a fixed Lean answer: kernel and keyed totals, a subject no theorem states, an unranged
    constant, and a writer under a subject that no covered_writers entry names."""
    registry = {"verdict_tokens": ["CONFLICT"], "keys": {"paths": ["k"], "validators": {"v": ["V"]}}, "paths": [
        {"name": "k", "tier": "kernel", "entry": ["E"], "theorems": ["T"], "subject": ["S", "S2"], "kinds": KINDS},
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
        {"name": "k", "tier": "kernel", "entry": ["E"], "theorems": ["T"], "subject": ["S"], "uncovered": uncovered,
         "kinds": KINDS},
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


# -- KB-1: the per-kind table, the writer ratchet, the signed total --------------------------------------------

# The sources whose `kind == "<k>"` comparisons are each path's case kinds: the runners the path's subjects and
# entry dispatch through (route: Run.dispatch, the families' Wire runners and the closureNary family's Core
# runners; norms: Run.runCaseIn and the plain kinds of Norms.Plain.run). A candidate path's are read once it is
# promoted (`certificate` compares none today).
KIND_SOURCES = {
    "route": ["lean/VE/Route/Run.lean", "lean/VE/Route/Wire.lean", "lean/VE/Core/Wire.lean",
              "lean/VE/Core/Layers.lean"],
    "norms": ["lean/VE/Norms/Run.lean", "lean/VE/Norms/Plain.lean"],
    "softNorms": ["lean/VE/SoftNorms/Run.lean"],
    "metered": ["lean/VE/Route/MeteredRun.lean"],
    "certificate": ["lean/VE/CertificateWire.lean"],
}
KIND_LITERAL = re.compile(r'\bkind\s*==\s*"([^"]+)"')


def kind_literals(path: str) -> set[str]:
    return {kind for source in KIND_SOURCES[path] for kind in KIND_LITERAL.findall((ROOT / source).read_text())}


def test_every_case_kind_of_a_kernel_runner_has_an_entry_and_every_entry_a_kind():
    """Section 9: each kind a kernel path's runners compare with the case's `kind` is in the path's `kinds`
    (a theorem or a nonverdict reason) or in `untied_kinds`; no entry names a kind the runners never compare."""
    assert {path["name"] for path in KERNEL} <= set(KIND_SOURCES)
    untied = REGISTRY["untied_kinds"]
    for path in REGISTRY["paths"]:
        literals = kind_literals(path["name"]) if path["name"] in KIND_SOURCES else set()
        if path["tier"] != "kernel":
            assert "kinds" not in path and not [u for u in untied if u["path"] == path["name"]], path["name"]
            continue
        whole = {u["kind"] for u in untied if u["path"] == path["name"] and "family" not in u}
        partial = {u["kind"] for u in untied if u["path"] == path["name"] and "family" in u}
        assert literals == set(path["kinds"]) | whole, path["name"]
        assert partial <= set(path["kinds"]), path["name"]
    assert kind_literals("certificate") == set()


def test_each_kind_theorem_fixes_its_kind_and_no_theorem_states_an_untied_kind():
    """A `kinds` theorem's statement fixes the kind on one of the path's subjects; an `untied_kinds` kind has no
    theorem in lean/statements.txt that mentions it with a subject of its path (else tie it, do not list it)."""
    paths = {path["name"]: path for path in KERNEL}
    for path in KERNEL:
        for kind, entry in path["kinds"].items():
            if "theorem" in entry:
                text = STATEMENTS[entry["theorem"]]
                assert f'"{kind}"' in text and any(s + "@" in text for s in path["subject"]), (path["name"], kind)
    for entry in REGISTRY["untied_kinds"]:
        if "family" in entry:
            continue
        subjects = paths[entry["path"]]["subject"]
        tied = [name for name, text in STATEMENTS.items()
                if f'"{entry["kind"]}"' in text and any(s + "@" in text for s in subjects)]
        assert tied == [], (entry, tied)
        for near in entry.get("near", []):
            assert near in STATEMENTS and near not in paths[entry["path"]]["theorems"], near


def test_the_kind_table_problems_are_found_before_any_lean_runs():
    ok = {"name": "p", "tier": "kernel", "theorems": ["T"], "kinds": {"a": {"theorem": "T"}, "b": {"nonverdict": "x" * 20}}}
    assert kernel_closure.kind_problems({"paths": [ok]}) == []
    cases = [
        ({"kinds": None}, "p: a kernel path names no case kinds (kinds)"),
        ({"kinds": {}}, "p: a kernel path names no case kinds (kinds)"),
        ({"kinds": {"a": {"theorem": "Other"}}}, "p: kind a cites Other, not a theorem of the path"),
        ({"kinds": {"a": {"nonverdict": "too short"}}}, "p: kind a is nonverdict without a reason of at least 20 characters"),
        ({"kinds": {"a": {"theorem": "T", "nonverdict": "x" * 20}}}, "p: kind a must map to one theorem or one nonverdict reason"),
        ({"kinds": {"a": {}}}, "p: kind a must map to one theorem or one nonverdict reason"),
        ({"kinds": {"a": "T"}}, "p: kind a must map to one theorem or one nonverdict reason"),
        ({"tier": "candidate"}, "p: kinds on a candidate path"),
    ]
    for change, problem in cases:
        assert kernel_closure.kind_problems({"paths": [dict(ok, **change)]}) == [problem], change
    why = "w" * 20
    untied = [
        ({"path": "q", "kind": "c", "why": why}, "untied kind c: q is not a kernel path"),
        ({"path": "p", "kind": "c", "why": "short"}, "untied kind of p names no kind or no reason"),
        ({"path": "p", "kind": "a", "why": why}, "p: kind a is both in kinds and untied"),
        ({"path": "p", "kind": "b", "family": "f", "why": why},
         "p: untied kind b names a family, but no theorem of the path fixes the kind"),
    ]
    for entry, problem in untied:
        assert kernel_closure.kind_problems({"paths": [ok], "untied_kinds": [entry]}) == [problem], entry
    assert kernel_closure.kind_problems({"paths": [ok], "untied_kinds": [
        {"path": "p", "kind": "c", "why": why}, {"path": "p", "kind": "a", "family": "f", "why": why}]}) == []
    assert kernel_closure.registry_problems({"paths": [dict(ok, kinds={})]}) == ["p: a kernel path names no case kinds (kinds)"]


def writers(*outside, inside=()):
    return {"verdict_writers": [{"name": n, "module": "M", "in_kernel": False} for n in outside]
            + [{"name": n, "module": "M", "in_kernel": True} for n in inside]}


def test_the_check_fails_when_verdict_writers_outside_the_kernel_rise():
    """Section 6.3: no allowance; a fall or a writer moved inside passes, a new writer outside fails by name."""
    saved = writers("A", "B", inside=["K"])
    assert kernel_closure.check_writers(writers("A", "B"), saved)[0] is True
    assert kernel_closure.check_writers(writers("A", inside=["B", "K"]), saved)[0] is True
    ok, message = kernel_closure.check_writers(writers("A", "B", "leak"), saved)
    assert ok is False and message == "FAIL: verdict writers outside the kernel rose from 2 to 3: leak"
    ok, message = kernel_closure.check_writers(writers("A", "C", "D", inside=["B"]), saved)
    assert ok is False and message.endswith("rose from 2 to 3: C, D")
    ok, message = kernel_closure.check_writers(writers("A", "A", "B"), saved)  # a second writer of one name
    assert ok is False and message.endswith("rose from 2 to 3: A")


def run_main(monkeypatch, tmp_path, measured, *argv, signed=100):
    allowances = tmp_path / "ALLOWANCES.md"
    allowances.write_text(f"# Kernel allowances\n\nsigned total: {signed:,} lines\n")
    monkeypatch.setattr(kernel_closure, "measure", lambda registry, timeout=3600: measured)
    return kernel_closure.main(["--allowances", str(allowances), *argv])


def test_the_check_command_fails_on_kernel_growth_and_on_a_new_writer_outside(monkeypatch, tmp_path, capsys):
    saved = tmp_path / "baseline.json"
    saved.write_text(json.dumps({"kernel_lines": 100, "paths": [], "problems": [], **writers("A")}))
    base = {"kernel_lines": 100, "paths": [], "problems": [], **writers("A")}
    assert run_main(monkeypatch, tmp_path, base, "--check", str(saved)) == 0
    assert "PASS: verdict writers outside the kernel 1 <= 1" in capsys.readouterr().out
    assert run_main(monkeypatch, tmp_path, dict(base, kernel_lines=101), "--check", str(saved)) == 1
    assert "FAIL: the kernel grew from 100 to 101" in capsys.readouterr().out
    assert run_main(monkeypatch, tmp_path, dict(base, **writers("A", "leak")), "--check", str(saved)) == 1
    assert "FAIL: verdict writers outside the kernel rose from 1 to 2: leak" in capsys.readouterr().out


def test_the_write_refuses_a_kernel_total_above_the_signed_one(monkeypatch, tmp_path, capsys):
    """Section 6.2: `--out` saves at most the signed total of docs/kernel/ALLOWANCES.md, and nothing above it."""
    out = tmp_path / "baseline.json"
    measured = {"kernel_lines": 100, "paths": [], "problems": [], **writers()}
    assert run_main(monkeypatch, tmp_path, measured, "--out", str(out)) == 0
    assert json.loads(out.read_text())["kernel_lines"] == 100
    out.unlink()
    assert run_main(monkeypatch, tmp_path, dict(measured, kernel_lines=101), "--out", str(out)) == 1
    assert not out.exists() and "REFUSED: kernel_lines 101 is above the signed total 100" in capsys.readouterr().out
    assert run_main(monkeypatch, tmp_path, dict(measured, kernel_lines=1_200), "--out", str(out), signed=1_200) == 0
    with pytest.raises(SystemExit, match="not 2"):
        kernel_closure.signed_total("signed total: 1 lines\nsigned total: 2 lines\n")
    assert kernel_closure.signed_total((ROOT / "docs/kernel/ALLOWANCES.md").read_text()) >= BASELINE["kernel_lines"]


def test_the_write_refuses_more_verdict_writers_outside_than_the_file_it_replaces(monkeypatch, tmp_path, capsys):
    """kb-1 review F2: section 6.3 has no allowance, so `--out` (the regen entry's write) may not reset the ratchet
    that `--check` enforces: a new outside writer is refused and the old file stays; a fall or a first write passes."""
    out = tmp_path / "baseline.json"
    old = json.dumps({"kernel_lines": 100, "paths": [], "problems": [], **writers("A")}, indent=1, sort_keys=True)
    out.write_text(old + "\n")
    measured = {"kernel_lines": 100, "paths": [], "problems": [], **writers("A", "leak")}
    assert run_main(monkeypatch, tmp_path, measured, "--out", str(out)) == 1
    assert "REFUSED: verdict writers outside the kernel rose from 1 to 2: leak" in capsys.readouterr().out
    assert out.read_text() == old + "\n"
    assert run_main(monkeypatch, tmp_path, dict(measured, **writers("A", inside=["leak"])), "--out", str(out)) == 0
    assert run_main(monkeypatch, tmp_path, dict(measured, **writers()), "--out", str(out)) == 0  # a fall
    assert json.loads(out.read_text())["verdict_writers"] == []
    assert run_main(monkeypatch, tmp_path, measured, "--out", str(out)) == 1  # the fall is the new bound
    out.unlink()
    assert run_main(monkeypatch, tmp_path, measured, "--out", str(out)) == 0  # a first write has no bound
    entry = next(g for g in regen_generated.GENERATED if g.name == "kernel-closure")
    assert entry.write == ((regen_generated.PY, "tools/kernel_closure.py", "--out", "docs/kernel/closure-baseline.json"),)


def test_measure_builds_the_registry_imports_before_the_lean_half(monkeypatch):
    """The registry's `imports` (theorems only VE.Audit imports) are built before `lake env lean` imports them."""
    calls = []
    monkeypatch.setattr(kernel_closure, "build_imports", lambda imports, timeout: calls.append(("build", imports)))
    monkeypatch.setattr(kernel_closure, "run_lean", lambda paths, tokens, imports, timeout: (
        calls.append(("lean", imports)), ({}, []))[1])
    with pytest.raises(KeyError):  # the fake Lean half answers nothing; only the order matters here
        kernel_closure.measure(REGISTRY)
    assert calls == [("build", REGISTRY["imports"]), ("lean", REGISTRY["imports"])]
    assert REGISTRY["imports"] == ["VE.Route.MeteredProofs"]


def test_the_readme_quotes_what_checked_means():
    """The one wording of a unit's CHECKED status (DRI 2026-11-11, an admission status, not a proof) is the help's
    (`ve document check --help`); README.md quotes it verbatim."""
    from ve.document.cli import CHECKED_MEANS
    assert CHECKED_MEANS.startswith("CHECKED: the core statements shown for this unit were admitted by the checker")
    assert CHECKED_MEANS in (ROOT / "README.md").read_text()
    assert "were proved" not in CHECKED_MEANS


WHY_ROW = re.compile(r"^  (\w+) (spec|wrap): (\d+) lines; chain: (.+)$")


def test_why_names_the_part_and_one_shortest_chain_checked_by_hand(lake, capsys):
    """`--why NAME` (kb-8b, for KB-4's measure) on a definition whose chains were checked by hand. Norms spec: the
    statement of `norms_wire_conflict_free` names `decodeSource` (lean/statements.txt), whose body calls
    `decodeNormsEnvironment` (lean/VE/Norms/Wire.lean); no statement of a norms theorem names it, so no chain is
    shorter. Norms wrap: the entry `Norms.Run.runCaseReported` calls `runCaseRouted`, which hands `Acts.Run.normsSource`
    to the elaborate exit, and `normsSource` calls `decodeSource`. A name no kernel path counts is said to be so."""
    target, absent = "VE.Norms.Wire.decodeNormsEnvironment", "VE.Norms.Wire.noSuchDefinition"
    assert kernel_closure.main(["--why", target, "--why", absent]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0] == target and out[-1] == f"{absent}: counted by no kernel path"
    rows = {(m[1], m[2]): (int(m[3]), m[4].split(" -> ")) for line in out[1:-1] if (m := WHY_ROW.match(line))}
    assert len(rows) == len(out) - 2
    assert rows[("norms", "spec")][1] == ["VE.Norms.FlaggedSpec.norms_wire_conflict_free", "VE.Norms.Wire.decodeSource",
                                         target]
    assert rows[("norms", "wrap")][1] == ["VE.Norms.Run.runCaseReported", "VE.Norms.Run.runCaseRouted",
                                         "VE.Acts.Run.normsSource", "VE.Norms.Wire.decodeSource", target]
    # one definition, so the lines are its own source range, in every part that counts it
    assert len({lines for lines, _ in rows.values()}) == 1 and next(iter(rows.values()))[0] > 0
    kernel = {path["name"] for path in KERNEL}
    for (path, _), (_, chain) in rows.items():
        entry = next(p for p in KERNEL if p["name"] == path)
        assert path in kernel and chain[0] in entry["theorems"] + entry["entry"], chain
        assert chain[-1] == target or chain[-1].startswith(target + "."), chain
