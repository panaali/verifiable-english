"""Refusal at a clash (row duties-clash-refuse-gate; docs/spec/norm-defaults.md 2.5, "Refusal at a clash").

Before this gate, where two rules give opposite outcomes for the same point (a 'must' and a 'need not' rule, a 'may'
and a 'may not' rule, or a 'must' rule beside a 'may not' on its permission), three developer commands printed a
definite answer: `ve norms completions --audit --situation` (the default broke the clash: SETTLED yes or no),
`ve document readings --conclusion` on a norms document without a content-bearing reading set (verdict ALL, the
clash ruling out the situation), and the same with `--assume-no-exception` on a soft-norms document (both "must" and
"need not" valid). `ve read` answered the tour's stop-12 pattern "No. The document rules this out."

Each now refuses, naming the two rules, when the clash happens in a situation the text allows (both rules' conditions
hold, consistent with the document's facts and its other statements, those two rules left out), and prints what it
printed before where there is none. The gate is untrusted Python (`ve/clash_gate.py`) that can only withhold an
answer. The fixtures are tests/data/norm-defaults-clash (measured on main b47dd5a505; see their `main_row`).
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path

import pytest

from tests import lean_routes
from ve import clash_gate
from ve.__main__ import main as ve_main
from ve.norm_defaults import UnspecifiedDocument

DATA = Path(__file__).resolve().parent / "data" / "norm-defaults-clash"

# The clash fixtures the gate refuses at `ve norms completions --situation`: fixture -> the two rules it names.
SITUATION_CLASHES = {
    "a1-stated--file_required--clash-in-cone": ("members-file", "contractors-need-not"),
    "b1-stated--file_required--clash-in-cone": ("members-file", "contractors-may-not"),
    "b1-stated--file_permitted--clash-in-cone": ("members-file", "contractors-may-not"),
    "u6--x_permitted--clash-in-cone": ("must-x", "not-x"),
}
# The unstated-fact fixtures: contractor(omar) is not stated, and the text allows it; where it holds, two rules clash
# at file_required(omar). The document's question (may Omar book?) is refused at `ve document readings --conclusion`,
# which answers over every situation the text allows.
DOCUMENT_CLASHES = {
    "a1-unstated--book_permitted--unstated-cone-fact": ("members-file", "contractors-need-not"),
    "b1-unstated--book_permitted--unstated-cone-fact": ("members-file", "contractors-may-not"),
}
# Not refused by this gate: the ask-both text writes "should file" and "should not file" as two request predicates
# with '+' rules only, and nothing declares one the refrain of the other, so no two rules give opposite outcomes for
# one predicate (the conflict check does not see them either). Recorded in test_norm_defaults_clash_known_defect.py.
NOT_A_CLASH_HERE = ("askboth--file_requested--clash-in-cone", "askboth--refrain_file_requested--clash-in-cone")
CONTROLS_ANSWERED = ("a1-stated--book_permitted--control-answer", "b1-stated--book_permitted--control-answer")
CONTROLS_UNDECIDED = ("u6--y_permitted--control-main-undecided", "u6--x_required--control-main-undecided")
RECORD = "askboth-onepred--file_requested--record"

STOP12 = """Every member who is paid is allowed.
Every member who is suspended is not allowed.
Bo is a member.
Bo is paid.
Is Bo suspended?
"""


@pytest.fixture(scope="module")
def lean_executable():
    if not lean_routes.SERVICE.exists():
        if os.environ.get("VE_LEAN_PREBUILT"):
            raise AssertionError(f"gate Lean build missing: {lean_routes.SERVICE}")
        pytest.skip("the Lean service has not been built")


def _fixture(name):
    path = DATA / f"{name}.json" if (DATA / f"{name}.json").exists() else DATA / "controls" / f"{name}.json"
    return json.loads(path.read_text())


def _cli(capsys, *argv):
    code = ve_main(list(argv))
    out = capsys.readouterr().out
    return code, out


def _completions(tmp_path, capsys, case, *, gate=True, monkeypatch=None):
    policy = tmp_path / "policy.json"
    situation = tmp_path / "situation.json"
    policy.write_text(json.dumps({"environment": case["environment"], "norms": case["norms"]}))
    situation.write_text(json.dumps(case["model"]))
    if not gate:
        monkeypatch.setattr(clash_gate, "gate_completions", lambda env, units, model, result: result)
    code, out = _cli(capsys, "norms", "completions", "--audit", str(policy), "--situation", str(situation),
                     "--no-prove")
    assert code == 0, out
    return json.loads(out)


def _refused_points(result):
    return {(p, tuple(row["tuple"])): row for row in result.get("refused", ())
            for p in row["target"].split("->")}


def _document(tmp_path, case, *, drop=(), extra_profiles=("documents@1",)):
    """A ve-document@1 of the fixture's rules and its situation's facts, without the facts on `drop`."""
    env = copy.deepcopy(case["environment"])
    env["profiles"] = sorted(set(env["profiles"]) | set(extra_profiles))
    lines, units = [], []
    for i, norm in enumerate(case["norms"], 1):
        lines.append(f"Rule {i}: {norm['norm']['name']}.")
        units.append({"id": f"rule{i}", "kind": "norm", "meaning": "specified", "support": "none", "content": norm})
    for predicate, rows in sorted(case["model"]["relations"].items()):
        if predicate in drop:
            continue
        for row in rows:
            lines.append(f"Fact: {predicate} {' '.join(row)}.")
            units.append({"id": f"fact{len(units)}", "kind": "asserted", "meaning": "specified",
                          "support": "observation",
                          "content": {"ast": ["unary", predicate, ["const", row[0]]]}})
    offset = 0
    for unit, line in zip(units, lines):
        end = offset + len(line) + 1
        unit["span"] = [offset, end]
        offset = end
    meta = {"format": "ve-document@1", "environment": env, "units": units}
    path = tmp_path / "doc.ve.md"
    path.write_text("---\n" + json.dumps(meta, indent=1) + "\n---\n" + "".join(line + "\n" for line in lines))
    return path


def _readings(tmp_path, capsys, path, conclusion, *flags):
    concl = tmp_path / "conclusion.json"
    concl.write_text(json.dumps(conclusion))
    code, out = _cli(capsys, "document", "readings", str(path), "--conclusion", str(concl), *flags)
    assert code == 0, out
    return json.loads(out)


# -- the 8 clash fixtures: 6 refused, both rule names in the refusal

@pytest.mark.parametrize("name", sorted(SITUATION_CLASHES))
def test_clash_fixture_is_refused_at_completions_situation(name, tmp_path, capsys, lean_executable):
    (run,) = _fixture(name)["runs"]
    case = run["case"]
    assert run["main_row"]["point_status"].startswith("SETTLED ")  # main's definite answer, recorded
    result = _completions(tmp_path, capsys, case)
    row = _refused_points(result)[(case["predicate"], tuple(case["tuple"]))]
    assert sorted(row["rules"]) == sorted(SITUATION_CLASHES[name])
    assert row["text"].startswith("VE could not decide this. The document's rules conflict in this situation")
    for rule in SITUATION_CLASHES[name]:
        assert f'rule "{rule}"' in row["text"]


@pytest.mark.parametrize("name", sorted(SITUATION_CLASHES))
def test_clash_fixture_point_status_is_refused(name, lean_executable):
    """The status the command would print for the asked point: REFUSED, with the clash that refuses it."""
    (run,) = _fixture(name)["runs"]
    case = run["case"]
    env, rows = clash_gate.lowered(case["environment"], case["norms"])
    _, refused = clash_gate.point_refusals(UnspecifiedDocument(env, rows), case["model"])
    clash = refused[(case["predicate"], tuple(case["tuple"]))]
    assert sorted(clash.rules) == sorted(SITUATION_CLASHES[name])


@pytest.mark.parametrize("name", sorted(DOCUMENT_CLASHES))
def test_unstated_fact_fixture_is_refused_at_document_readings(name, tmp_path, capsys, lean_executable):
    runs = _fixture(name)["runs"]
    assert {r["main_row"]["point_status"] for r in runs} == {"SETTLED yes", "SETTLED no"}  # main, per completion
    case = runs[0]["case"]
    path = _document(tmp_path, case, drop=("contractor",))
    result = _readings(tmp_path, capsys, path, ["unary", case["predicate"], ["const", case["tuple"][0]]])
    assert result["status"] == "refused" and result["reason"] == "rules-conflict", result
    assert sorted(result["rules"]) == sorted(DOCUMENT_CLASHES[name])
    for rule in DOCUMENT_CLASHES[name]:
        assert f'rule "{rule}"' in result["text"]
    assert "the text allows a situation where both apply" in result["text"]


@pytest.mark.parametrize("name", NOT_A_CLASH_HERE)
def test_ask_both_fixture_is_outside_this_gate(name, tmp_path, capsys, lean_executable):
    """Two '+' rules on two predicates that nothing links: no clash under the gate's rule (a request/refrain link
    would need its own declaration and ruling). The command prints what it printed before."""
    (run,) = _fixture(name)["runs"]
    result = _completions(tmp_path, capsys, run["case"])
    assert "refused" not in result


def test_one_predicate_ask_both_record_is_refused(tmp_path, capsys, lean_executable):
    """The fifth control file: 'should file' (+) and 'should not file' (-) on one predicate: a clash, refused (its
    file expects REFUSE; main answered SETTLED yes)."""
    (run,) = _fixture(RECORD)["runs"]
    assert run["main_row"]["point_status"] == "SETTLED yes"
    result = _completions(tmp_path, capsys, run["case"])
    row = _refused_points(result)[("file_requested", ("omar",))]
    assert sorted(row["rules"]) == ["should-file", "should-not-file"]


# -- the controls beside the clashes: unchanged

@pytest.mark.parametrize("name", CONTROLS_ANSWERED)
def test_control_beside_a_clash_is_still_answered(name, tmp_path, capsys, lean_executable):
    (run,) = _fixture(name)["runs"]
    case = run["case"]
    env, rows = clash_gate.lowered(case["environment"], case["norms"])
    clashes, refused = clash_gate.point_refusals(UnspecifiedDocument(env, rows), case["model"])
    assert clashes and (case["predicate"], tuple(case["tuple"])) not in refused  # the clash is beside it, not in it
    status = {"predicate": case["predicate"], "tuple": case["tuple"], "before": run["main_row"]["point_status"],
              "after": "SETTLED no"}
    gated = clash_gate.gate_completions(UnspecifiedDocument(env, rows).env, rows, case["model"],
                                        {"completions": [{"predicate": "file_required",
                                                          "changes_if_switched": [status]}]})
    assert gated["completions"][0]["changes_if_switched"] == [status]


@pytest.mark.parametrize("name", CONTROLS_UNDECIDED)
def test_undecided_control_is_never_replaced(name, lean_executable):
    """UNDECIDED is no definite answer: the gate leaves it as it is (u6's points, main's own UNDECIDED)."""
    (run,) = _fixture(name)["runs"]
    case = run["case"]
    assert run["main_row"]["point_status"] == "UNDECIDED"
    env, rows = clash_gate.lowered(case["environment"], case["norms"])
    status = {"predicate": case["predicate"], "tuple": case["tuple"], "before": "UNDECIDED", "after": "UNDECIDED"}
    gated = clash_gate.gate_completions(UnspecifiedDocument(env, rows).env, rows, case["model"],
                                        {"completions": [{"predicate": case["predicate"],
                                                          "changes_if_switched": [dict(status)]}]})
    assert gated["completions"][0]["changes_if_switched"] == [status]


# -- the four commands, end to end: refused at a clash, as before without one

def test_completions_refuses_the_status_it_printed(tmp_path, capsys, monkeypatch, lean_executable):
    """A1 with 'must file' allow-by-default: main printed before SETTLED no, after SETTLED yes for Omar; both now
    REFUSED, the sentence beside each, nothing else in the output changed."""
    (run,) = _fixture("a1-stated--file_required--clash-in-cone")["runs"]
    case = copy.deepcopy(run["case"])
    case["environment"]["vocabulary"]["predicates"]["file_required"]["regulated"]["default"] = "allow"
    gated = _completions(tmp_path, capsys, case)
    plain = _completions(tmp_path, capsys, case, gate=False, monkeypatch=monkeypatch)
    (before,) = [c for e in plain["completions"] for c in e.get("changes_if_switched", ())]
    assert (before["before"], before["after"]) == ("SETTLED no", "SETTLED yes")
    (after,) = [c for e in gated["completions"] for c in e.get("changes_if_switched", ())]
    assert (after["before"], after["after"]) == ("REFUSED", "REFUSED")
    assert 'rule "members-file"' in after["refusal"]["before"] and 'rule "contractors-need-not"' in after["refusal"]["after"]
    stripped = copy.deepcopy(gated)
    stripped.pop("refused")
    for entry in stripped["completions"]:
        for change in entry.get("changes_if_switched", ()):
            change.pop("refusal")
            change["before"], change["after"] = before["before"], before["after"]
    assert stripped == plain


def test_completions_without_a_clash_is_unchanged(tmp_path, capsys, monkeypatch, lean_executable):
    (run,) = _fixture("a1-stated--file_required--clash-in-cone")["runs"]
    case = copy.deepcopy(run["case"])
    case["norms"] = [n for n in case["norms"] if n["norm"]["name"] != "contractors-need-not"]
    case["environment"]["vocabulary"]["predicates"]["file_required"]["regulated"]["default"] = "allow"
    gated = _completions(tmp_path, capsys, case)
    plain = _completions(tmp_path, capsys, case, gate=False, monkeypatch=monkeypatch)
    assert gated == plain and "refused" not in gated


def test_completions_over_budget_refuses_as_unchecked(tmp_path, capsys, monkeypatch, lean_executable):
    """u6 has one unsaid point; with no room to enumerate it the check cannot rule a clash out: refused, never
    answered."""
    monkeypatch.setattr(clash_gate, "MAX_UNSAID_ATOMS", 0)
    (run,) = _fixture("u6--x_permitted--clash-in-cone")["runs"]
    result = _completions(tmp_path, capsys, run["case"])
    assert result["refused"]["reason"] == "clash-unchecked"


def test_document_readings_refuses_at_a_clash_and_not_without(tmp_path, capsys, monkeypatch, lean_executable):
    (run,) = _fixture("a1-stated--file_required--clash-in-cone")["runs"]
    case = run["case"]
    # T5: main answered "Omar is not a contractor" ALL, a fact the text never states (only the clash forces it).
    refused = _readings(tmp_path, capsys, _document(tmp_path, case, drop=("contractor",)),
                        ["not", ["unary", "contractor", ["const", "omar"]]])
    assert refused["status"] == "refused" and sorted(refused["rules"]) == ["contractors-need-not", "members-file"]
    calm = copy.deepcopy(case)
    calm["norms"] = [n for n in case["norms"] if n["norm"]["name"] != "contractors-need-not"]
    path = _document(tmp_path, calm)
    conclusion = ["unary", "file_required", ["const", "omar"]]
    gated = _readings(tmp_path, capsys, path, conclusion)
    monkeypatch.setattr(clash_gate, "document_refusal", lambda doc: None)
    assert gated == _readings(tmp_path, capsys, path, conclusion) and "verdict" in gated


def test_document_facts_can_rule_a_clash_out(tmp_path, capsys, lean_executable):
    """'No team member is a contractor', asserted: the two rules' conditions never hold together in a situation the
    text allows, so there is no clash and no refusal."""
    (run,) = _fixture("a1-stated--file_required--clash-in-cone")["runs"]
    case = copy.deepcopy(run["case"])
    case["model"]["relations"] = {"team_member": [["omar"]]}
    path = _document(tmp_path, case)
    meta_text = path.read_text()
    head, rest = meta_text.split("\n---\n", 1)
    meta = json.loads(head.removeprefix("---\n"))
    line = "Fact: no team member is a contractor.\n"
    start = len(rest.encode())
    meta["units"].append({"id": "fact-none", "kind": "asserted", "meaning": "specified", "support": "observation",
                          "span": [start, start + len(line)],
                          "content": {"ast": ["forall", "person", ["not", ["and", ["unary", "team_member", ["var", 0]],
                                                                         ["unary", "contractor", ["var", 0]]]]]}})
    path.write_text("---\n" + json.dumps(meta, indent=1) + "\n---\n" + rest + line)
    result = _readings(tmp_path, capsys, path, ["unary", "file_required", ["const", "omar"]])
    assert result.get("status") != "refused" and "verdict" in result, result


def _soft(tmp_path, case, *, keep=None):
    """The fixture as a soft-norms@0 document (strict rules), as the exposure page's soft example."""
    soft = copy.deepcopy(case)
    soft["environment"]["vocabulary"]["soft"] = {"outranking": {"mode": "strict"}}
    if keep is not None:
        soft["norms"] = [n for n in soft["norms"] if n["norm"]["name"] in keep]
    return _document(tmp_path, soft, extra_profiles=("documents@1", "soft-norms@0"))


def test_assume_no_exception_refuses_at_a_clash_and_not_without(tmp_path, capsys, monkeypatch, lean_executable):
    (run,) = _fixture("a1-stated--file_required--clash-in-cone")["runs"]
    case = run["case"]
    must = ["unary", "file_required", ["const", "omar"]]
    for conclusion in (must, ["not", must]):  # main: both "must" and "need not" valid, no flag
        refused = _readings(tmp_path, capsys, _soft(tmp_path, case), conclusion, "--assume-no-exception")
        assert refused["status"] == "refused" and sorted(refused["rules"]) == ["contractors-need-not", "members-file"]
    path = _soft(tmp_path, case, keep=("members-file", "contractors-book"))
    gated = _readings(tmp_path, capsys, path, must, "--assume-no-exception")
    monkeypatch.setattr(clash_gate, "document_refusal", lambda doc: None)
    assert gated == _readings(tmp_path, capsys, path, must, "--assume-no-exception")
    assert gated.get("status") != "refused"


def _read(tmp_path, capsys, text):
    path = tmp_path / "text.txt"
    path.write_text(text)
    code, out = _cli(capsys, "read", str(path), "--json")
    return code, json.loads(out)


def test_read_refuses_the_stop12_pattern(tmp_path, capsys, lean_executable):
    """Main answered "No. The document rules this out.": only the clash rules out Bo being suspended."""
    code, result = _read(tmp_path, capsys, STOP12)
    (answer,) = result["answers"]
    assert answer["lead"] == "unknown" and answer["answer"] == "no answer"
    text = " ".join(answer["text"])
    assert "rules this out" not in text and "The text's rules conflict in this situation" in text
    assert '"Every member who is paid is allowed."' in text and '"Every member who is suspended is not allowed."' in text
    assert "Bo" in text and code == 3


def test_read_without_a_clash_is_unchanged(tmp_path, capsys, monkeypatch, lean_executable):
    """The tour's own-rules text writes the exception into the rule: no clash, the same answer as before."""
    text = (Path(__file__).resolve().parents[1] / "tour" / "texts" / "own-rules.txt").read_text()
    gated = _read(tmp_path, capsys, text)
    monkeypatch.setattr(clash_gate, "plain_clash", lambda d: None)
    assert gated == _read(tmp_path, capsys, text) and gated[1]["answers"][0]["lead"] == "yes"


def test_read_leaves_lean_refusals_alone(tmp_path, capsys, lean_executable):
    """Facts that make the text inconsistent: Lean already refuses; the gate replaces only a yes or a no."""
    code, result = _read(tmp_path, capsys, STOP12.replace("Is Bo suspended?", "Bo is suspended.\nIs Bo allowed?"))
    (answer,) = result["answers"]
    assert "cannot all be true together" in " ".join(answer["text"])
    assert "rules conflict" not in " ".join(answer["text"])


# -- the plain check itself (no Lean)

def _clash(text):
    from ve.plain_read import derive
    return clash_gate.plain_clash(derive(text))


def test_plain_clash_names_a_named_individual_or_any():
    assert "the text allows Bo to be one" in _clash(STOP12)
    named_out = STOP12.replace("Bo is paid.", "Bo is not suspended.")
    assert _clash(named_out).endswith("and the text allows one.")


def test_plain_clash_needs_both_conditions_possible():
    exception_written = STOP12.replace("is paid is allowed", "is paid and is not suspended is allowed")
    assert _clash(exception_written) is None
    third_rule = STOP12.replace("Bo is a member.", "Every member who is paid is not suspended.\nBo is a member.")
    assert _clash(third_rule) is None
    same_sign = STOP12.replace("is suspended is not allowed", "is suspended is allowed")
    assert _clash(same_sign) is None


def test_a_status_that_reads_a_clash_is_refused_with_it(lean_executable):
    """'Every member who must file must report': report_required(omar) reads file_required(omar), where the two rules
    clash; its status rests on how the default broke the clash, so it is refused with the clash's rules."""
    (run,) = _fixture("a1-stated--file_required--clash-in-cone")["runs"]
    case = copy.deepcopy(run["case"])
    case["environment"]["vocabulary"]["predicates"]["report_required"] = {
        "arguments": ["person"], "description": "{0} report the expense",
        "regulated": {"role": "obligation", "default": "deny", "act": "{0} report the expense"}}
    case["norms"].append({"norm": {"name": "filers-report", "predicate": "report_required", "sign": True,
                                   "guard": ["unary", "file_required", ["var", 0]], "unless": [], "over": []}})
    env, rows = clash_gate.lowered(case["environment"], case["norms"])
    _, refused = clash_gate.point_refusals(UnspecifiedDocument(env, rows), case["model"])
    assert sorted(refused[("report_required", ("omar",))].rules) == ["contractors-need-not", "members-file"]
    assert ("book_permitted", ("omar",)) not in refused


def test_a_filling_fill_t_refutes_is_no_clash(tmp_path, capsys, lean_executable):
    """'Must X' beside an unspecified 'may X' with no rule: the pair target is true only under the filling that leaves
    X not permitted, which `Fill_T` refutes (2.4), so no situation the text allows has the clash: answered as before."""
    (run,) = _fixture("u6--x_permitted--clash-in-cone")["runs"]
    case = copy.deepcopy(run["case"])
    predicates = case["environment"]["vocabulary"]["predicates"]
    predicates["x_permitted"]["regulated"]["default"] = "unspecified"
    predicates["y_permitted"]["regulated"]["default"] = "deny"
    case["norms"] = [{"norm": {"name": "must-x", "predicate": "x_required", "sign": True, "guard": ["top"],
                               "unless": [], "over": []}}]
    env, rows = clash_gate.lowered(case["environment"], case["norms"])
    assert clash_gate.situation_clashes(UnspecifiedDocument(env, rows), case["model"]) == []
    assert clash_gate.document_clash(case["environment"], case["norms"]) is None
    assert "refused" not in _completions(tmp_path, capsys, case)
