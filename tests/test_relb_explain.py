"""relb-explain: the plain-English printout of usecases/eligibility/explain.py (release B, item 4).

One test per output part (the answer, the clauses with gloss and quoted source, the assumptions,
the guide's £35,000 section as an assumption for questions 3 and 4, the Lean certificate count)
on three profiles: B15 entitled (£200, the demo case), B01 not entitled, D02 taken back by HMRC.
Plus: a step premise with no gloss fails; every rule has a cite whose quotes match the source
files; the printout carries no ids but regulation numbers; the command line prints the same text.
"""
import copy
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest

from tests import lean_routes

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "usecases" / "eligibility"
sys.path.insert(0, str(HERE))

import explain as X  # noqa: E402
import translation as T  # noqa: E402

LEAN = lean_routes.SERVICE.exists()
PROFILES = {  # profile -> the key's answers (cases.json), as the printout shows them
    "B15": {"Q1": "YES", "Q2": "£200.00", "Q3": "NO", "Q4": "£200.00"},
    "B01": {"Q1": "NO", "Q2": "Not applicable: the applicant is not entitled.",
            "Q3": "Not applicable: the applicant is not entitled.", "Q4": "Not applicable: the applicant is not entitled."},
    "D02": {"Q1": "YES", "Q2": "£200.00", "Q3": "YES", "Q4": "£0.00"},
}


@pytest.fixture(scope="module")
def runs():
    return {pid: X.explanation(pid, lean=LEAN) for pid in PROFILES}


@pytest.fixture(scope="module")
def texts(runs):
    return {pid: X.render(data) for pid, data in runs.items()}


def flat(text):
    """The printout with its line wrapping undone."""
    return " ".join(text.split())


def _answer(data, question):
    return next(e for e in data["answers"] if e["question"] == question)


def _source_text(name):
    return (HERE / "source" / X.SOURCES[name][0]).read_text(encoding="utf-8")


def test_each_answer_is_printed_with_its_question(runs, texts):
    keys = {c["id"]: c["key"] for c in T.load_cases(strip_keys=False)["cases"]}
    for pid, expected in PROFILES.items():
        got = {e["question"]: e["display"] for e in runs[pid]["answers"]}
        assert got == expected, pid
        assert keys[pid]["entitled"] == (expected["Q1"] == "YES")
        for question, shown in expected.items():
            assert f"{X.QUESTIONS[question]}\nAnswer: {shown}\n" in texts[pid], (pid, question)


def test_clauses_show_the_gloss_and_the_quoted_source(runs, texts):
    rules = {r["id"]: r for r in X.load_rules()}
    for pid in PROFILES:
        q1 = _answer(runs[pid], "Q1")
        assert q1["clauses"], pid
        for c in q1["clauses"]:
            assert c["glosses"] and c["quotes"], (pid, c["heading"])
            for quote in c["quotes"]:  # quoted word for word from a source file
                assert any(quote in _source_text(s) for s in X.SOURCES), (pid, quote)
                assert f"“{quote}”" in flat(texts[pid])
    # The demo case: regs. 2(a), 2(b) and 4(4) for entitlement, 3(1) for the amount, each with its gloss.
    b15 = runs["B15"]
    headings = {c["heading"]: c for c in _answer(b15, "Q1")["clauses"]}
    for heading in ("regulation 2(a)", "regulation 2(b)", "regulation 4(4)"):
        assert heading in headings
    assert rules["R2.applicant"]["gloss"] in headings["regulation 2(a)"]["glosses"]
    assert "P has reached pensionable age" in " ".join(headings["regulation 2(a)"]["quotes"])
    assert "P becomes ordinarily resident in Scotland or Northern Ireland" in headings["regulation 4(4)"]["quotes"][0]
    q2 = {c["heading"]: c for c in _answer(b15, "Q2")["clauses"]}
    assert rules["R14.1"]["gloss"] in q2["regulation 3(1)"]["glosses"]
    assert "the amount of a winter fuel payment is £200" in q2["regulation 3(1)"]["quotes"][0]
    # Questions after the first list only the clauses they add.
    assert "Clauses used: those listed above, plus:" in texts["B15"]
    # Not entitled: the reg. 4(2)(a) exclusion (partner of a pension credit claimant) is shown.
    b01 = {c["heading"]: c for c in _answer(runs["B01"], "Q1")["clauses"]}
    assert "a partner of and living with" in b01["regulation 4(2)(a)"]["quotes"][1]
    assert rules["R7.applicant"]["gloss"] in b01["regulation 4(2)(a)"]["glosses"]


def test_assumptions_are_the_bridges_and_readings_used(runs, texts):
    b15 = _answer(runs["B15"], "Q1")["assumptions"]
    assert {"week", "ages", "statuses", "glosses", "move_order", "other_schemes"} <= set(b15)
    assert "the applicant's pensionable-age date is 2021-03-14" in b15["ages"]  # bridge B2, by hand
    assert "ordinarily resident in Scotland or Northern Ireland" in b15["statuses"]
    assert X.ASSUMPTIONS["move_order"] in flat(texts["B15"])
    # B15 lives alone: the proof still shows reg. 4(2)(a) does not apply, so its reading is used;
    # the common-day reading of reg. 3(3) is used only by the amount (question 2).
    assert "throughout" in b15 and "common_day" not in b15
    assert "common_day" in _answer(runs["B15"], "Q2")["new_assumptions"]
    b01 = _answer(runs["B01"], "Q1")["assumptions"]
    assert {"throughout", "household", "one_other", "benefit_paid_to"} <= set(b01)
    assert "a partner (a member of a couple)" in b01["statuses"]
    for pid in PROFILES:  # the assumptions come under their own heading, in plain words
        assert "Assumptions (taken as given, not checked):" in texts[pid]


def test_the_guide_income_section_is_an_assumption_for_q3_and_q4(runs, texts):
    d02 = runs["D02"]
    for question in ("Q3", "Q4"):
        e = _answer(d02, question)
        assert "income" in e["assumptions"], question
        assert not any("£35,000" in c["heading"] for c in e["clauses"]), question  # never a clause of the Regulations
    q3 = _answer(d02, "Q3")
    [section] = q3["guide_clauses"]
    assert "If your total income is over £35,000, HM Revenue and Customs (HMRC) will take your Winter Fuel Payment back." in section["quotes"]
    assert "all_or_nothing" in _answer(d02, "Q4")["assumptions"]
    text = flat(texts["D02"])
    assert X.ASSUMPTIONS["income"] in text
    assert "“If your total income is over £35,000, HM Revenue and Customs (HMRC) will take your Winter Fuel Payment back.”" in text
    assert "If you do not opt out and your total income is over £35,000" in text
    for question in ("Q1", "Q2"):
        assert "income" not in _answer(d02, question)["assumptions"]
    for question in ("Q3", "Q4"):  # not entitled: no Q3/Q4 answer, so no income assumption
        assert "income" not in _answer(runs["B01"], question)["assumptions"]
    assert "£35,000 test" not in flat(texts["B01"])


def test_each_answer_gives_its_lean_certificate_count(runs, texts):
    for pid in PROFILES:
        for e in runs[pid]["answers"]:
            if e["display"].startswith("Not applicable"):
                assert "certificates" not in e
                continue
            n = e["certificates"]
            assert n > 0, (pid, e["question"])
            assert f"this answer rests on {n} proof step" in flat(texts[pid]), (pid, e["question"])
            if LEAN:
                assert e["lean"] == {"checked": n, "accepted": n, "admitted": True}, (pid, e["question"])
    q = {e["question"]: e["certificates"] for e in runs["D02"]["answers"]}
    assert q["Q1"] < q["Q2"] < q["Q4"]  # each later answer's document rests on the earlier steps


@pytest.mark.skipif(not LEAN, reason="build the Lean service first")
def test_lean_line_says_the_document_was_admitted(texts):
    for pid in PROFILES:
        assert "the answer document was admitted." in texts[pid]
        assert "NOT admitted" not in texts[pid]


def test_a_step_premise_without_a_gloss_fails():
    rules = copy.deepcopy(X.load_rules())
    for r in rules:
        if r["id"] == "R2.applicant":
            r["gloss"] = ""
    with pytest.raises(X.MissingGloss, match="R2.applicant"):
        X.explanation("B15", rules=rules, lean=False)
    for r in rules:  # a gloss on a rule no step uses is not checked
        if r["id"] == "R2.applicant":
            r["gloss"] = "restored"
        if r["id"] == "G3":
            r["gloss"] = ""
    X.explanation("B15", rules=rules, lean=False)


def test_every_rule_has_a_cite_matching_the_source_files():
    rules = X.load_rules()
    assert X.check_cites(rules) == sorted({r["rule"] for r in rules})
    assert json.loads((HERE / "rules.json").read_text())["rules"] == T.rules()  # the glosses are the translation's
    with pytest.raises(X.SourceMismatch):  # a cite whose line no longer opens with its words
        X.quote("S1", 61, "(b)in respect of any day")


def test_the_printout_has_no_ids_but_regulation_numbers(texts):
    pattern = re.compile(r"\b(?:R\d+[a-c]?(?:\.\d)?|AR\d|O\d|G\d|B\d|S\d|Sch4|[A-D]\d\d|Q\d)\b|\w+_\w+")
    for pid, text in texts.items():
        assert not pattern.findall(text), (pid, pattern.findall(text)[:5])


def test_the_command_line_prints_the_same_text(tmp_path):
    case = next(c for c in T.load_cases()["cases"] if c["id"] == "B15")
    path = tmp_path / "b15.json"
    path.write_text(json.dumps({k: v for k, v in case.items() if k not in ("id", "summary")}), encoding="utf-8")
    by_id = subprocess.run([sys.executable, str(HERE / "explain.py"), "B15", "--no-lean"],
                           capture_output=True, text=True, check=True).stdout
    by_file = subprocess.run([sys.executable, str(HERE / "explain.py"), str(path), "--no-lean"],
                             capture_output=True, text=True, check=True).stdout
    assert by_id == by_file == X.explain("B15", lean=False)
    assert "Answer: £200.00" in by_id and "Lean was not run for this printout." in by_id
