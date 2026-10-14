"""Question answering Q2's report numbers come from its saved evidence (docs/spec/question-answering-q2/evidence/),
never from live git: the generated block of REPORT.md is regenerated from the saved files, the prose numbers are
checked against the same files, and the evidence itself must show what the build checklist asks for (build checklist
20). The commit list is `main..HEAD --no-merges` as saved at capture, so the tests still hold after syncs with main
and after the merge."""
from __future__ import annotations

import json
import importlib.util
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "docs/spec/question-answering-q2"
SPEC = importlib.util.spec_from_file_location("question_answering_q2_report", HERE / "report.py")
assert SPEC is not None and SPEC.loader is not None
report = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(report)


def test_generated_block_is_the_saved_evidence():
    assert Path(report.__file__).resolve() == HERE / "report.py"
    text = (HERE / "REPORT.md").read_text()
    assert text[text.index(report.BEGIN):text.index(report.END) + len(report.END)] == report.block()


def test_scope_is_a_saved_commit_list():
    scope = report.load("scope.json")
    assert scope["range"] == "main..HEAD --no-merges" and scope["captured_head"] in scope["commits"]
    assert all(re.fullmatch(r"[0-9a-f]{40}", c) for c in [scope["base"], *scope["commits"]])
    assert len(set(scope["commits"])) == len(scope["commits"])
    assert {row["commit"] for row in scope["numstat"]} <= set(scope["commits"])
    metrics = report.metrics()
    assert metrics["Lean"]["added"] > 0 and metrics["Python (product)"]["added"] > 0
    assert metrics["Rust"]["files"] == 0
    assert metrics["ask_theorems"] > 0


def test_the_prose_numbers_are_the_evidence():
    """The report's prose cites the same counts the evidence holds."""
    text = (HERE / "REPORT.md").read_text()
    prose = text[:text.index(report.BEGIN)]
    statements = report.load("statements.json")
    assert statements["exit"] == 0
    assert "Q2 statements: 27 of 27 implemented; 0 missing; 0 differ in text" in statements["output"]
    assert any(line.endswith("elaborated against the implementation; PASS") for line in statements["output"])
    assert "27 approved theorems" in prose and "41 approved statements and signatures" in prose
    mutants = report.load("mutants.json")["mutants"]
    assert f"{len(mutants)} seeded bugs" in prose
    fixtures = report.load("fixtures.json")["fixtures"]
    assert f"{len(fixtures)} recorded fixtures" in prose


def test_every_seeded_bug_was_caught_in_each_changed_language():
    scope = report.load("scope.json")
    changed = {row["path"] for row in scope["numstat"]}
    mutants = report.load("mutants.json")["mutants"]
    assert len(mutants) >= 3 and all(m["caught"] for m in mutants)
    assert {m["language"] for m in mutants} == {"Lean", "Python"}
    assert all(m["file"] in changed for m in mutants)
    assert len({m["behaviour"] for m in mutants}) == len(mutants)


def test_the_fixtures_are_answers_or_leans_refusals():
    fixtures = report.load("fixtures.json")["fixtures"]
    leads = {"yes", "no", "notSettled", "notNecessarily", "unknown", "by_reading"}
    for f in fixtures:
        if "error" in f:
            assert f["id"] == "A1d" and f["error"] == "UnsupportedProfile"
            continue
        assert f["lead"] in leads and f["rows"] >= 1
        assert (f["lead"] == "by_reading") == (len(f["row_leads"]) > 1) or f["route"] == "readings"
        assert ("unknown" in f["row_leads"]) == bool(f["reasons"])
    assert {f["route"] for f in fixtures if "route" in f} == {"readings", "plain", "norm-defaults"}


def test_the_trust_growth_is_the_saved_budget():
    trust = report.load("trust.json")
    assert trust["base"]["K"] == trust["head"]["K"]
    grew = {k: trust["head"][k] - trust["base"][k] for k in ("S", "V")}
    assert all(n > 0 for n in grew.values())
    delta = (HERE / "DELTA.md").read_text()
    assert f"S +{grew['S']}, V +{grew['V']} over `main`'s budget" in delta
    assert (f"S {trust['base']['S']:,} → {trust['head']['S']:,}, V {trust['base']['V']:,} → {trust['head']['V']:,})"
            in delta)


def test_every_delta_row_has_its_status():
    rows = [line for line in (HERE / "DELTA.md").read_text().splitlines() if re.match(r"\| D\d+ \|", line)]
    assert [re.match(r"\| (D\d+) \|", row).group(1) for row in rows] == [f"D{n}" for n in range(1, 16)]
    for row in rows:
        item = re.match(r"\| (D\d+) \|", row).group(1)
        specific = re.search(r"SIGNED by item-specific DRI ruling (D\d+)", row)
        if specific:
            assert specific.group(1) == item
        assert ("DRI signature needed" in row or re.search(r"SIGNED by standing ruling R\d+", row)
                or "SIGNED by DRI 2026-10-13" in row
                or specific), row[:60]


def test_q2_f6_historical_gate_cannot_claim_the_current_head():
    """Render only the selected saved gate, identified by its own SHA.

    A report commit follows the gated commit, and the report survives later merges.
    Gate validity is checked by batch_evidence at the gate and merge boundary.
    """
    archived = json.loads((report.EVIDENCE / "gate-previous-passed.json").read_text())
    rendered = report.block()
    current = report.EVIDENCE / "gate-result.json"
    if current.exists():
        saved = json.loads(current.read_text())
        assert f"on `{saved['commit_sha'][:8]}`" in rendered
        if archived["commit_sha"][:8] != saved["commit_sha"][:8]:
            assert f"on `{archived['commit_sha'][:8]}`" not in rendered
    else:
        assert "Full gate: not yet saved" in rendered


def test_q2_f10_saved_gate_rendering_never_reads_live_git(tmp_path, monkeypatch):
    """A committed gate result remains renderable after HEAD moves or a merge."""
    shutil.copytree(report.EVIDENCE, tmp_path, dirs_exist_ok=True)
    archived = json.loads((tmp_path / "gate-previous-passed.json").read_text())
    saved = {**archived, "commit_sha": "a" * 40}
    (tmp_path / "gate-result.json").write_text(json.dumps(saved))
    monkeypatch.setattr(report, "EVIDENCE", tmp_path)

    def unexpected_git(*args, **kwargs):
        raise AssertionError("report rendering must use saved evidence, never live git")

    monkeypatch.setattr(report.subprocess, "run", unexpected_git)
    rendered = report.block()
    assert "Full gate (`tools/gate.py`, `evidence/gate-result.json`): passed on `aaaaaaaa`" in rendered
    assert f"on `{archived['commit_sha'][:8]}`" not in rendered
