"""DF-0.3, the defeasible plan's baseline, checked from its SAVED evidence only
(`docs/research/evidence/defeasible/baseline/`, written by `research/defeasible/baseline.py`; report section 6 of
`docs/research/defeasible-phase1.md`). Nothing here runs `ve` or reads git: the documents are compared with what the
script builds from the pinned `CE4`, and the measured values with the verbatim answers.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path

import pytest

from tests import ce4

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/research/evidence/defeasible/baseline"
REPORT = ROOT / "docs/research/defeasible-phase1.md"
SETS = ("force-u0036-s05", "force-u0156-s03", "force-u0263-s04-p2")


def _cases():
    spec = importlib.util.spec_from_file_location("df_baseline_cases", ROOT / "research/defeasible/baseline_cases.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


baseline = _cases()
RECORD = json.loads((EVIDENCE / "baseline.json").read_text())


def front(data):
    end = data.index(b"\n---\n", 4)
    return json.loads(data[4:end]), data[end + 5:]


def test_saved_files_are_the_recorded_ones():
    """The directory holds the record and exactly the files it lists, each with its recorded hash."""
    assert {p.name for p in EVIDENCE.iterdir()} == {"baseline.json", *RECORD["files"]}
    for name, digest in RECORD["files"].items():
        assert hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest() == digest, name


def rule_question(set_id):
    """The set's rule read as a strict universal over its predicate's sorts: `∀ x̄. guard → (¬) p(x̄)`."""
    [R] = [R for R in ce4.reading_sets() if R["id"] == set_id]
    rule = R["readings"][0]["content"]["norm"]
    sorts = ce4.environment()["vocabulary"]["predicates"][rule["predicate"]]["arguments"]
    variables = [["var", i] for i in reversed(range(len(sorts)))]
    atom = [{1: "unary", 2: "binary"}[len(sorts)], rule["predicate"], *variables]
    body = atom if rule["sign"] else ["not", atom]
    body = body if rule["guard"] == ["top"] else ["implies", rule["guard"], body]
    for sort in reversed(sorts):
        body = ["forall", sort, body]
    return body


def test_questions_are_p1s_three():
    """P-1's three sets in order; each saved question is the script's and is the set's own rule as a universal."""
    assert list(baseline.QUESTIONS) == list(SETS) and set(SETS) < set(ce4.SETS)
    for set_id in SETS:
        assert json.loads((EVIDENCE / f"question-{set_id}.json").read_text()) == baseline.QUESTIONS[set_id]
        assert baseline.QUESTIONS[set_id] == rule_question(set_id)


@pytest.mark.parametrize("set_id", SETS)
def test_p1_document_is_the_default_candidate_alone(set_id):
    """P-1: the saved document is `CE4`'s frame with one unit whose content is the set's `default` candidate (mode
    default, unstated exception), over the set's sentence."""
    data = (EVIDENCE / f"p1-{set_id}.ve.md").read_bytes()
    assert data == baseline.p1_document(set_id)
    meta, text = front(data)
    assert meta["environment"] == ce4.environment()
    [unit] = meta["units"]
    [R] = [R for R in ce4.reading_sets() if R["id"] == set_id]
    assert unit["id"] == R["unit"] and unit["span"] == [0, len(text)]
    assert unit["content"] == R["readings"][1]["content"] and unit["content"]["norm"]["mode"] == "default"


def test_p2_document_is_ce4():
    """P-2: the saved document is `CE4`: its frame, its four sentences and its sets' readings."""
    meta, text = front((EVIDENCE / "p2-ce4.ve.md").read_bytes())
    assert meta["environment"] == ce4.environment() and text == ce4.source_text()[0]
    saved = [(R["id"], [(a["id"], a["content"]) for a in R["readings"]]) for R in meta["reading_sets"]]
    assert saved == [(R["id"], [(a["id"], a["content"]) for a in R["readings"]]) for R in ce4.reading_sets()]


def _answers(part, document):
    answers = RECORD[part]
    assert [a["set"] for a in answers] == list(SETS)
    for a in answers:
        name = document(a["set"])
        assert a["argv"] == ["ve", "document", "readings", f"docs/research/evidence/defeasible/baseline/{name}",
                             "--conclusion", f"docs/research/evidence/defeasible/baseline/question-{a['set']}.json"]
        assert (a["exit"], a["stderr"]) == (0, "")
        assert json.loads(a["stdout"])["verdict"] == a["verdict"]
    return answers


def test_p1_measured_zero_of_three():
    """P-1's "0": each standalone default answers NONE, so no probe is answered; no answer speaks of exceptions."""
    answers = _answers("p1", lambda s: f"p1-{s}.ve.md")
    for a in answers:
        data = json.loads(a["stdout"])
        assert data["verdict"] == "NONE" and data["premises"]["status"] == "model" and not data["vacuous"]
        assert "exception" not in a["stdout"]
        # Review df-03 F1: the route reads no rule of a soft document, so the NONE is over an empty premise set.
        assert a["fixed_premises"] == RECORD["measured"]["p1_fixed_premises"][a["set"]] == 0
    assert sum(baseline.follows(a) for a in answers) == RECORD["measured"]["p1_answered"] == 0
    assert RECORD["measured"]["p1_answered"] == RECORD["expected"]["p1_answered"]
    assert RECORD["measured"]["p1_verdicts"] == {a["set"]: a["verdict"] for a in answers}


def _saved_strict(set_id):
    """The set's `strict` candidate as the saved `CE4` document has it."""
    meta, _ = front((EVIDENCE / "p2-ce4.ve.md").read_bytes())
    [R] = [R for R in meta["reading_sets"] if R["id"] == set_id]
    [strict] = [a for a in R["readings"] if a["id"] == "strict"]
    return strict["content"]


@pytest.mark.parametrize("set_id", SETS)
def test_p1_controls_are_the_p1_document_with_one_change(set_id):
    """Each saved control is the saved P-1 document with only its unit's content changed (to the saved `strict`
    candidate, or none), or with `soft-norms@0` also dropped from the profiles."""
    meta, text = front((EVIDENCE / f"p1-{set_id}.ve.md").read_bytes())
    assert set(baseline.CONTROLS) == {"strict", "no-content", "strict-no-soft"}
    for control, (candidate, soft) in baseline.CONTROLS.items():
        expected = json.loads(json.dumps(meta))
        expected["units"][0]["content"] = None if candidate is None else _saved_strict(set_id)
        if not soft:
            expected["environment"]["profiles"].remove("soft-norms@0")
        data = (EVIDENCE / baseline.control_name(control, set_id)).read_bytes()
        assert data == baseline.document_bytes(expected, text), control


@pytest.mark.parametrize("set_id", SETS)
def test_p1_none_is_the_empty_premise_set_not_an_exception(set_id):
    """Review df-03 F1: on a `soft-norms@0` document today's `--conclusion` route reads no norm unit, so the `strict`
    candidate answers exactly as no content does (NONE over 0 fixed premises, the same model ids); without
    `soft-norms@0` the same rule is read and answers ALL."""
    answers = {a["control"]: a for a in RECORD["controls"] if a["set"] == set_id}
    assert list(answers) == list(baseline.CONTROLS)
    for control, a in answers.items():
        assert a["argv"] == ["ve", "document", "readings",
                             f"docs/research/evidence/defeasible/baseline/{baseline.control_name(control, set_id)}",
                             "--conclusion", f"docs/research/evidence/defeasible/baseline/question-{set_id}.json"]
        assert (a["exit"], a["stderr"]) == (0, "")
        assert json.loads(a["stdout"])["verdict"] == a["verdict"]
        assert RECORD["measured"]["control_verdicts"][f"{control} {set_id}"] == a["verdict"]
    strict, empty, plain = answers["strict"], answers["no-content"], answers["strict-no-soft"]
    assert strict["fixed_premises"] == empty["fixed_premises"] == 0 and strict["stdout"] == empty["stdout"]
    assert strict["verdict"] == "NONE" and json.loads(strict["stdout"])["premises"]["status"] == "model"
    assert plain["verdict"] == "ALL" and plain["fixed_premises"] > 0


def test_p2_measured_some_from_the_sets_own_default():
    """P-2's SOME on `CE4`: proved with every set strict, refuted with the probed set read by its default only."""
    answers = _answers("p2", lambda s: "p2-ce4.ve.md")
    strict = [[s, 0] for s in ce4.SETS]
    for a in answers:
        data = json.loads(a["stdout"])
        assert data["verdict"] == RECORD["expected"]["p2_verdict"] == "SOME"
        assert data["proof"]["choice"] == strict
        assert data["countermodel"]["choice"] == [[s, 1 if s == a["set"] else 0] for s in ce4.SETS]
    assert RECORD["measured"]["p2_verdicts"] == {a["set"]: a["verdict"] for a in answers}


def test_record_names_main_the_command_the_host_and_pinned_binaries():
    assert re.fullmatch(r"[0-9a-f]{40}", RECORD["main_commit"]) and RECORD["inputs_changed_from_main"] == []
    assert RECORD["command"] == baseline.COMMAND and RECORD["item"] == "DF-0.3"
    host = RECORD["host"]
    assert host["cpus"] > 0 and len(host["load_before"]) == len(host["load_after"]) == 3
    assert {b["path"] for b in RECORD["binaries"].values()} == set(baseline.BINARIES.values())
    assert all(b["pinned"] and re.fullmatch(r"[0-9a-f]{64}", b["sha256"]) for b in RECORD["binaries"].values())


def test_report_section_states_the_recorded_values():
    """Section 6 names the main commit and states, per set, the recorded P-1 and P-2 verdicts, then P-1's fixed
    premises and its controls' verdicts."""
    section = REPORT.read_text().split("## 6. DF-0.3 baseline (", 1)[1]
    assert RECORD["date"].startswith(section[:10])
    assert f"`{RECORD['main_commit'][:8]}`" in section
    measured = RECORD["measured"]
    for set_id in SETS:
        verdicts, controls = ([c.strip() for c in line.strip("|").split("|")]
                              for line in section.splitlines() if line.startswith(f"| {set_id} |"))
        assert verdicts[2:] == [measured["p1_verdicts"][set_id], measured["p2_verdicts"][set_id]]
        assert controls[1:] == [str(measured["p1_fixed_premises"][set_id]),
                                *(measured["control_verdicts"][f"{c} {set_id}"] for c in baseline.CONTROLS)]
    assert "0 of 3 probes answered" in section
    # Review df-03 F1: the NONE is over 0 premises, so the section must not call it the strict countermodel.
    assert "the strict countermodel the plan expects" not in section
