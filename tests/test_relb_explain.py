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

# The answers that use the GOV.UK guide's £35,000 section (questions 3 and 4 of an entitled applicant): marked
# "basis: guidance" (row tour-basis-guidance).
GUIDANCE = {"B15": {"Q3", "Q4"}, "B01": set(), "D02": {"Q3", "Q4"}}


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
            mark = " (basis: guidance)" if question in GUIDANCE[pid] else ""
            assert f"{X.QUESTIONS[question]}\nAnswer: {shown}{mark}\n" in texts[pid], (pid, question)


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
    assert "the applicant's pensionable-age date is 2021-03-14" in b15["ages"]  # bridge B2, worked out from Sch. 4
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
def test_lean_line_says_the_answer_was_accepted(texts):
    for pid in PROFILES:
        assert "the answer was checked by Lean and accepted." in texts[pid]
        assert "NOT accepted" not in texts[pid]


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


# --- relb-explain-checked-english: the rules' checked English wordings (relb-f1f2 made all 56 read back) ---

STALE = "The rules have no checked English wording"


def _recorded_wordings():
    rows = json.loads((HERE / "results.json").read_text(encoding="utf-8"))["english"]["rule_rows"]
    return {r["rule"]: r for r in rows}


def test_every_rule_explain_names_has_its_checked_english_wording(runs):
    """Each rule premise an answer uses carries the wording run.py recorded for it (english.rule_rows), and
    all 56 rules have one; the explanation's clause groups pair each gloss with its rule's wording."""
    rule_of = {r["gloss"]: r["id"] for r in X.load_rules()}
    rows = _recorded_wordings()
    assert len(rows) == 56 and all(r["round_trip"] and r["sentence"] for r in rows.values())
    assert X.load_wordings() == {rid: r["sentence"] for rid, r in rows.items()}
    for pid, data in runs.items():
        named = 0
        for e in data["answers"]:
            for rid, wording in e.get("wordings", {}).items():
                assert wording == rows[rid]["sentence"], (pid, e["question"], rid)
                named += 1
            for c in e["clauses"] + e["guide_clauses"]:
                assert len(c["wordings"]) == len(c["glosses"]), (pid, c["heading"])
                for gloss, wording in zip(c["glosses"], c["wordings"]):
                    assert wording == rows[rule_of[gloss]]["sentence"], (pid, c["heading"], gloss[:40])
        assert named, pid


def test_the_stale_no_wording_sentence_is_gone(texts):
    assert STALE not in X.ASSUMPTIONS["glosses"] and "checked English wording" in X.ASSUMPTIONS["glosses"]
    for pid, text in texts.items():
        assert STALE not in flat(text), pid
        assert "the gloss is taken to state the rule" not in flat(text), pid
        assert " ".join(X.ASSUMPTIONS["glosses"].split()) in flat(text), pid
    demo = (HERE / "DEMO.md").read_text(encoding="utf-8")  # its expected-output block, as test_relb_demo_cli reads it
    block = flat(re.search(r"<!-- expected-output:[^>]*-->\n```text\n(.*?)^```$", demo, re.S | re.M).group(1))
    assert STALE not in block and " ".join(X.ASSUMPTIONS["glosses"].split()) in block


def test_the_wording_printout_shows_each_rules_checked_wording(runs):
    """Under --wording, every rule explain() names for an answer has its gloss printed, with its checked
    wording right under it."""
    glosses = {r["id"]: flat(r["gloss"]) for r in X.load_rules()}
    for pid, data in runs.items():
        text = flat(X.render(data, wording=True))
        assert " ".join(X.GLOSSES_WORDED.split()) in text and STALE not in text, pid
        named = 0
        for e in data["answers"]:
            for rid, wording in e.get("wordings", {}).items():
                assert f"- {glosses[rid]} Checked English wording: {flat(wording)}" in text, (pid, e["question"], rid)
                named += 1
        assert named, pid


def _q4_section(text):
    return flat(text.split(X.QUESTIONS["Q4"], 1)[1])


@pytest.mark.parametrize("pid", ["B15", "D02"])
def test_question_4_prints_the_all_or_nothing_rules_gloss(runs, texts, pid):
    """Question 4 adds the guide's all-or-nothing rule to the income section question 3 showed; the
    printout shows that rule's gloss under the all-or-nothing assumption (and its wording with --wording)."""
    rule = next(r for r in X.load_rules() if r["id"] == "R16c")
    q4 = _answer(runs[pid], "Q4")
    assert "R16c" in q4["wordings"] and "income" not in q4["new_assumptions"], pid
    gloss = flat(rule["gloss"])
    after = _q4_section(texts[pid]).split(flat(X.ASSUMPTIONS["all_or_nothing"]), 1)[1]
    assert after.split("Lean check:")[0].count(f"- {gloss}") == 1, pid
    assert f"- {gloss} Checked English wording: {flat(X.load_wordings()['R16c'])}" in \
        _q4_section(X.render(runs[pid], wording=True)), pid
    assert f"- {gloss}" not in flat(texts[pid].split(X.QUESTIONS["Q4"], 1)[0]), pid  # question 3 did not show it
    [section] = q4["new_guide_clauses"]
    assert section["glosses"] == [rule["gloss"]], pid


def test_a_rule_without_a_checked_wording_is_said_so(monkeypatch):
    """A changed rule gets no recorded wording; an answer using a rule with none says the gloss stands for it."""
    rules = copy.deepcopy(X.load_rules())
    changed = next(r for r in rules if r["id"] == "R2.applicant")
    changed["formula"] = ["not", changed["formula"]]
    assert "R2.applicant" not in X.load_wordings(rules) and "R3.applicant" in X.load_wordings(rules)
    full = X.load_wordings
    monkeypatch.setattr(X, "load_wordings", lambda rules=None: {k: v for k, v in full(rules).items()
                                                                 if k != "R2.applicant"})
    data = X.explanation("B15", lean=False)
    q1 = _answer(data, "Q1")
    assert q1["wordings"]["R2.applicant"] is None and q1["assumptions"]["glosses"] == X.GLOSSES_UNWORDED
    text = X.render(data, wording=True)
    assert "Checked English wording: none." in text and " ".join(X.GLOSSES_UNWORDED.split()) in flat(text)


def test_the_command_line_wording_option(tmp_path):
    out = subprocess.run([sys.executable, str(HERE / "explain.py"), "B15", "--no-lean", "--wording"],
                         capture_output=True, text=True, check=True).stdout
    assert out == X.explain("B15", lean=False, wording=True) and "Checked English wording:" in out


# --- tour-stop6-wording: the checked wording in place of the gloss (ask.py --wording, tour stop 6) -------------------

def test_the_wording_in_place_of_the_gloss(runs):
    """With gloss=False each rule an answer uses is read as its checked English wording, and no rule's hand-written
    gloss is printed; the clause label and the "glosses" assumption say so."""
    glosses = [flat(r["gloss"]) for r in X.load_rules()]
    for pid, data in runs.items():
        text = X.render(data, wording=True, gloss=False)
        body = flat(text)
        assert " ".join(X.GLOSSES_WORDING_ONLY.split()) in body, pid
        assert "Read as:" not in text and "Checked English wording:" not in text, pid
        for gloss in glosses:
            assert f"- {gloss}" not in body, (pid, gloss[:40])
        named = 0
        for e in data["answers"]:
            for rid, wording in e.get("wordings", {}).items():
                assert wording is not None, (pid, e["question"], rid)
                assert f"- {flat(wording)}" in body, (pid, e["question"], rid)
                named += 1
        assert named, pid


def test_gloss_false_without_wording_keeps_the_glosses(runs):
    """gloss=False alone has no wording to show, so the printout is the default one."""
    for pid, data in runs.items():
        assert X.render(data, gloss=False) == X.render(data), pid


def test_a_rule_without_a_checked_wording_keeps_its_gloss_marked(monkeypatch):
    """In place of the glosses, a rule with no checked wording is shown by its gloss, marked as one, and the
    assumption says the gloss stands for that rule."""
    full = X.load_wordings
    monkeypatch.setattr(X, "load_wordings", lambda rules=None: {k: v for k, v in full(rules).items()
                                                                 if k != "R2.applicant"})
    data = X.explanation("B15", lean=False)
    gloss = flat(next(r for r in X.load_rules() if r["id"] == "R2.applicant")["gloss"])
    text = flat(X.render(data, wording=True, gloss=False))
    assert f"- {gloss} (a hand-written gloss: this rule has no checked English wording)" in text
    assert " ".join(X.GLOSSES_WORDING_ONLY_UNWORDED.split()) in text
    assert " ".join(X.GLOSSES_WORDING_ONLY.split()) not in text
    assert "that a person reads the same meaning in it is taken as given" in text


# --- the "basis: guidance" mark (row tour-basis-guidance, 2026-11-28) ------------------------------------------------

def _used_sources(entry):
    """The sources of the rules an answer uses, as rules.json's own `source` field names them (S1, S2, ...): a path to
    the answer's basis that does not go through explain.py's cite table."""
    published = {r["id"]: r["source"] for r in X.load_rules()}
    return {re.match(r"[A-Za-z0-9]+", published[rid]).group(0) for rid in entry.get("wordings", {})}


def test_the_cite_table_agrees_with_the_published_source_of_each_rule():
    """Every rule's clause is cited from the source rules.json names for it, and every source has a basis: so the
    mark, read from the cited source, is the published rule's."""
    assert set(X.BASIS) == set(X.SOURCES) and set(X.BASIS.values()) == {"law", "guidance"}
    assert [s for s, b in X.BASIS.items() if b == "guidance"] == ["S2"]  # wfp-print.txt, the GOV.UK guide
    for r in X.load_rules():
        assert X.CLAUSES[r["rule"]][0] == re.match(r"[A-Za-z0-9]+", r["source"]).group(0), r["id"]


def test_an_answer_is_marked_guidance_exactly_when_a_rule_it_uses_is_read_from_the_guide(runs, texts):
    """For every answer of the three profiles: the mark is on it (in the data and on its Answer line, with the line
    that says what it means) exactly when one of its rules comes from the guide; no answer of the not-entitled
    profile, and no answer resting on the Regulations alone, is marked."""
    marked = {}
    for pid, data in runs.items():
        for e in data["answers"]:
            guide = "S2" in _used_sources(e) and e["answer"] not in ("OPEN", "N/A")
            assert (e["mark"] == " (basis: guidance)") is guide and (e["mark"] == "") is not guide, (pid, e["question"])
            line = f"Answer: {e['display']}{e['mark']}\n"
            assert line in texts[pid], (pid, e["question"])
            if guide:
                assert e["guidance_sources"] == [X.SOURCES["S2"][1]], (pid, e["question"])
                assert (f"{line}Basis: guidance: this answer uses a clause of the GOV.UK guide “Winter Fuel Payment”, "
                        "which is\n  guidance on the law, not law.\n") in texts[pid], (pid, e["question"])
            marked.setdefault(pid, set()).update({e["question"]} if guide else set())
    assert marked == GUIDANCE
    assert "basis: guidance" not in texts["B01"].lower()


def test_the_mark_follows_the_basis_of_the_source_not_the_question(monkeypatch):
    """Were the guide law, no answer would be marked; were the Regulations guidance, the entitlement and the amount
    would be marked too, naming them."""
    monkeypatch.setitem(X.BASIS, "S2", "law")
    data = X.explanation("B15", lean=False)
    assert [e["mark"] for e in data["answers"]] == [""] * 4
    assert "basis: guidance" not in X.render(data).lower()
    monkeypatch.setitem(X.BASIS, "S1", "guidance")
    data = X.explanation("B15", lean=False)
    assert [e["mark"] for e in data["answers"]] == [" (basis: guidance)"] * 4
    assert X.SOURCES["S1"][1] in data["answers"][0]["guidance_sources"]
