"""Word senses, version 1 (row word-senses-v1; ruling 2026-11-27): `ve read` with words that may carry more than one
meaning. Layer 1 (a word on two kinds of thing is two words), layer 2 (the meaning check: the writer's opt-in reader,
run twice, or the word list alone; Lean answers each question one meaning / split, and Python only compares), layer 3
(the writer settles a meaning in plain English). No test calls a model: every reader here is a recorded answer.

Every test fails on main (no ve.word_senses; `ve read` refuses a word on two kinds and merges every word silently)."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from subprocesses import HANG_TIMEOUT
from ve import word_senses as ws

ROOT = Path(__file__).resolve().parents[1]
PROMPT_SHA256 = "e80bd349b03e2ceed840a3e3af15cc1d071022b5db8df05ddc7ab7da62b945ec"  # frozen before the build

# Layer 2: "available" may mean not busy (sentence 1) or offered (sentence 2).
GUESTS = """Every guest who is idle is available.
Every guest who is available is invited.
Ben is a guest.
Ben is idle.
Is Ben invited?
Is Ben available?
"""
# Layer 1: "valid" of a ticket and "valid" of a visitor, one of them negated.
TWO_KINDS = """Every ticket that is unused is valid.
Every visitor who is valid is admitted.
Every visitor who is banned is not valid.
Pass is a ticket.
Pass is unused.
Kim is a visitor.
Kim is banned.
Is Pass valid?
Is Kim valid?
Is Kim admitted?
"""
# Layer 3: two glosses, two words.
GLOSSED = """Every guest who is idle is free (not busy).
Every guest who is free (no charge) is welcome.
Every guest who is late is not free (not busy).
Ben is a guest.
Ben is idle.
Is Ben welcome?
Is Ben free (not busy)?
"""
CONTRADICTION = """Every room that is booked is closed.
Every room that is cleaned is not closed.
Ola is a room.
Ola is booked.
Ola is cleaned.
Is Ola closed?
"""


def recorded(*runs):
    """A reader that gives the recorded answers in turn (a dict is printed as JSON; None is a failed run)."""
    calls = []

    def reader(text):
        calls.append(text)
        out = runs[(len(calls) - 1) % len(runs)]
        return json.dumps(out) if isinstance(out, dict) else out
    reader.calls = calls
    return reader


def same(*labels):
    return {label: {"verdict": "same"} for label in labels}


def answer_of(result, question):
    return next(a for a in result["answers"] if a["question"] == question)


@pytest.fixture(autouse=True)
def own_settings(tmp_path, monkeypatch):
    """Each test has its own settings (no yes given) and no reader program."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.delenv("VE_WORD_READER", raising=False)


# --- the frozen reader prompt and format ---------------------------------------------------------------------------

def test_the_reader_prompt_is_the_one_frozen_before_the_build():
    raw = (ROOT / "ve" / "word_senses_prompt.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PROMPT_SHA256


def test_the_reader_input_is_the_numbered_text_and_the_repeated_words():
    ps, _ = ws.pieces(GUESTS)
    words = ws.words_of(ws.uses_of(ps, ws._classified(ps), {"Ben": "guest"}))
    text = ws.reader_input(ps, ws.candidates(words))
    assert text.startswith(ws.prompt().rstrip("\n") + "\n\nTEXT:\n1. Every guest who is idle is available.\n")
    assert "\n6. Is Ben available?\n\nWORDS: " in text
    assert text.endswith('WORDS: "available" (sentences 1, 2, 6), "idle" (sentences 1, 4), "invited" (sentences 2, 5)')


@pytest.mark.parametrize("out, verdict", [
    ('{"free": {"verdict": "same"}}', "same"),
    ('```json\n{"free": {"verdict": "differ", "groups": [[1], [2]]}}\n```', "differ"),
    ('{"free": {"verdict": "unsure"}}', "unsure"),
    ('{"free": {"verdict": "same"}}\n{"free": {"verdict": "differ"}}', "missing"),  # two objects: unusable
    ('{"free": "same"}', "missing"), ('{"other": {"verdict": "same"}}', "missing"), ("I think so.", "missing"),
    ("", "missing"), (None, "missing"), ('["free"]', "missing"),
])
def test_a_reader_answer_counts_only_in_the_frozen_format(out, verdict):
    assert ws.parse_reader(out, ["free"]) == {"free": verdict}


# --- the writer's yes: nothing leaves the machine without it -------------------------------------------------------

def test_without_the_yes_no_text_leaves_the_machine(tmp_path, monkeypatch):
    marker = tmp_path / "sent"
    command = f"{sys.executable} -I -c \"open({str(marker)!r}, 'w').write('x')\""
    monkeypatch.setenv("VE_WORD_READER", command)
    assert not ws.consent_given(command) and ws.reader_for() is None
    text = tmp_path / "guests.txt"
    text.write_text(GUESTS)
    done = subprocess.run([sys.executable, "-m", "ve", "read", str(text)], cwd=ROOT,
                          env={**os.environ, "TMPDIR": str(tmp_path), "XDG_CONFIG_HOME": str(tmp_path / "config")},
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert done.returncode in (0, 3), done.stdout + done.stderr
    assert not marker.exists()
    assert "meaning check: word list alone; VE sends your text nowhere until you say yes" in done.stdout
    assert "was sent to the reader program" not in done.stdout


def test_the_yes_is_stored_in_the_settings_and_can_be_taken_back(tmp_path, monkeypatch):
    monkeypatch.setenv("VE_WORD_READER", "reader-program")
    ws.give_consent("reader-program")
    stored = json.loads((tmp_path / "config" / "ve" / "settings.json").read_text())
    assert stored == {"word_reader": {"consent": True, "consent_command": "reader-program"}}
    assert ws.consent_given("reader-program") and ws.reader_for() is not None
    ws.withdraw_consent()
    assert not ws.consent_given("reader-program") and ws.reader_for() is None
    assert json.loads((tmp_path / "config" / "ve" / "settings.json").read_text())["word_reader"]["consent"] is False


def test_the_editors_assist_mode_counts_as_the_yes_unless_the_yes_was_taken_back(monkeypatch):
    monkeypatch.setenv("VE_WORD_READER", "reader-program")
    assert ws.reader_for() is None and ws.reader_for(assist=True) is not None
    ws.withdraw_consent()
    assert ws.reader_for(assist=True) is None


def test_a_yes_without_a_reader_program_sends_nothing_even_after_one_is_set(monkeypatch):
    ws.give_consent(None)
    assert ws.reader_for() is None
    monkeypatch.setenv("VE_WORD_READER", "reader-program")
    assert ws.reader_for() is None


def test_a_yes_covers_only_the_program_it_was_given_for(monkeypatch):
    ws.give_consent("my-reader", store=True)
    assert ws.reader_command() == "my-reader" and ws.reader_for() is not None
    monkeypatch.setenv("VE_WORD_READER", "another-program")   # set later, or by someone else: not covered
    assert ws.reader_command() == "another-program" and ws.reader_for() is None


def _cli(tmp_path, *args, stdin=""):
    env = {**os.environ, "TMPDIR": str(tmp_path), "XDG_CONFIG_HOME": str(tmp_path / "config")}
    env.pop("VE_WORD_READER", None)
    return subprocess.run([sys.executable, "-m", "ve", "read", *args], cwd=ROOT, env=env, input=stdin,
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)


def test_the_yes_is_asked_in_plain_words_once_and_only_a_yes_stores_it(tmp_path):
    done = _cli(tmp_path, "--reader-yes", "--reader-command", "my-reader", stdin="no\n")
    assert "sends the sentences of the text you are reading" in done.stdout
    assert "(my-reader)" in done.stdout and "AI service outside this computer" in done.stdout
    assert "Nothing changed" in done.stdout and not (tmp_path / "config" / "ve" / "settings.json").exists()
    done = _cli(tmp_path, "--reader-yes", "--reader-command", "my-reader", stdin="yes\n")
    assert done.returncode == 0
    stored = json.loads((tmp_path / "config" / "ve" / "settings.json").read_text())
    assert stored == {"word_reader": {"command": "my-reader", "consent": True, "consent_command": "my-reader"}}
    assert "covers this reader program only (my-reader)" in done.stdout
    done = _cli(tmp_path, "--reader-off")
    assert done.returncode == 0 and "send nothing" in done.stdout
    assert json.loads((tmp_path / "config" / "ve" / "settings.json").read_text())["word_reader"]["consent"] is False


def test_ve_has_no_mode_that_merges_a_raised_word_silently(tmp_path):
    done = _cli(tmp_path, "--help")
    assert done.returncode == 0
    assert "merge" not in done.stdout.lower() and "silent" not in done.stdout.lower()
    # every option `ve read` has: none of them reads a raised word as one meaning without asking
    assert {o for a in ws.parser()._actions for o in a.option_strings} == {
        "-h", "--help", "--json", "--ask", "--reader-yes", "--reader-off", "--reader-command"}
    assert set(ws.read.__code__.co_varnames[:ws.read.__code__.co_argcount + ws.read.__code__.co_kwonlyargcount]) == {
        "path", "text", "reader", "scratch"}


# --- the trigger: two runs, or the word list alone -----------------------------------------------------------------

def _word(senses=2, declared=False, statements=2):
    uses = [ws.Use(i, "free", "guest", True) for i in range(1, statements + 1)] + [ws.Use(9, "free", "guest", False)]
    return ws.Word("free", "guest", "free", uses, senses=senses, declared=declared)


@pytest.mark.parametrize("runs, senses, raised", [
    (("same", "same"), 9, False),
    (("same", "differ"), 1, True),      # either run raises it
    (("differ", "same"), 9, True),
    (("unsure", "same"), 9, True),      # not same, and the list has several meanings
    (("unsure", "same"), 1, False),     # not same, but one meaning in the list
    (("missing", "same"), 9, True),     # no usable answer counts as not same
    (("missing", "missing"), 1, False),
])
def test_two_reader_runs_and_a_word_is_raised_if_either_raises_it(runs, senses, raised):
    w = _word(senses=senses)
    reader = recorded(*[({"free": {"verdict": r}} if r != "missing" else "no json") for r in runs])
    ws.meaning_check(ws.pieces(GUESTS)[0], [w], reader)
    assert len(reader.calls) == 2 and reader.calls[0] == reader.calls[1]
    assert w.raised is raised and w.check == {"by": "reader", "runs": list(runs)}


def test_a_declared_word_counts_as_unknown_to_the_list_for_the_reader():
    w = _word(senses=0, declared=True)
    ws.meaning_check(ws.pieces(GUESTS)[0], [w], recorded({"free": {"verdict": "unsure"}}))
    assert w.raised


@pytest.mark.parametrize("senses, declared, raised", [(9, False, True), (1, False, False), (0, True, False),
                                                     (9, True, True)])
def test_the_word_list_alone_raises_a_repeated_word_with_several_meanings(senses, declared, raised):
    w = _word(senses=senses, declared=declared)
    ws.meaning_check(ws.pieces(GUESTS)[0], [w], None)
    assert w.raised is raised and w.check == {"by": "list"}


def test_only_words_used_in_two_or_more_sentences_on_one_kind_are_checked():
    ps, _ = ws.pieces(TWO_KINDS)
    words = ws.words_of(ws.uses_of(ps, ws._classified(ps), {"Pass": "ticket", "Kim": "visitor"}))
    assert [w.label for w in ws.candidates(words)] == ["admitted", "banned", "unused", "valid, of a ticket",
                                                           "valid, of a visitor"]


# --- "does the difference matter": Lean answers both ways, Python only compares ------------------------------------

def _fake_lean(monkeypatch, merged, split, unknown_reason="X3"):
    """Lean's checked answers, recorded: `merged` and `split` map a question line in the hidden document to its answer;
    a "no answer" carries Lean's reason code `unknown_reason`."""
    calls = []

    def lean(hid, name, scratch):
        calls.append(hid.text)
        table = split if name.endswith("-split") else merged
        answers = []
        for line in hid.text.splitlines():
            if line.startswith("Is "):
                got = table.get(line, "not determined")
                lead = {"Yes": "yes", "No": "no", "not determined": "notSettled", "no answer": "unknown"}[got]
                answers.append({"question": line, "lead": lead, "answer": got, "text": [f"Lean: {got}"],
                                "reasons": [unknown_reason] if got == "no answer" else []})
        return {"status": "read", "answers": answers, "text": ["Lean read every sentence: 2 of 2 CHECKED"],
                "coverage": {}}
    monkeypatch.setattr(ws, "_lean", lean)
    return calls


def test_equal_answers_mean_no_question_and_the_answer_stands(monkeypatch):
    calls = _fake_lean(monkeypatch, {"Is Ben invited?": "Yes"}, {"Is Ben invited?": "Yes"})
    result = ws.read("t.txt", GUESTS, reader=recorded(
        {"available": {"verdict": "differ"}, "idle": {"verdict": "same"}, "invited": {"verdict": "same"}}))
    a = answer_of(result, "Is Ben invited?")
    assert len(calls) == 2 and a["answer"] == "Yes" and "both_ways" not in a
    assert result["questions_for_writer"] == []


def test_different_answers_are_answered_both_ways_naming_the_link(monkeypatch):
    _fake_lean(monkeypatch, {"Is Ben invited?": "Yes", "Is Ben available?": "Yes"},
               {"Is Ben invited?": "not determined", "Is Ben availablezqa?": "Yes", "Is Ben availablezqb?": "not determined"})
    reader = recorded({"available": {"verdict": "differ"}, "idle": {"verdict": "same"}, "invited": {"verdict": "same"}})
    result = ws.read("t.txt", GUESTS, reader=reader)
    a = answer_of(result, "Is Ben invited?")
    assert a["answer"] == "depends on meaning"
    assert a["both_ways"] == {"words": ["available"], "same": "Yes", "different": "not determined"}
    assert a["text"][0] == ("Depends on what 'available' means. If it means the same in all its sentences "
                            "(available: sentences 1 and 2): Yes. If not: the text does not settle this.")
    b = answer_of(result, "Is Ben available?")
    assert b["both_ways"]["uses"] == [{"sentence": 1, "answer": "Yes"}, {"sentence": 2, "answer": "not determined"}]
    assert "in sentence 1: Yes; in sentence 2: the text does not settle this." in b["text"][0]
    assert result["questions_for_writer"] == [{"word": "available", "kind": "guest", "sentences": [1, 2],
                                               "question": "In sentences 1 and 2, does 'available' mean the same thing?"}]


def test_python_compares_answers_and_reads_nothing_else_of_them(monkeypatch):
    """Two answers that are equal stand, whatever Lean's lines say; two that differ are both shown."""
    _fake_lean(monkeypatch, {"Is Ben invited?": "No"}, {"Is Ben invited?": "No"})
    result = ws.read("t.txt", GUESTS, reader=recorded({"available": {"verdict": "differ"}}))
    assert answer_of(result, "Is Ben invited?")["answer"] == "No"
    _fake_lean(monkeypatch, {"Is Ben invited?": "No"}, {"Is Ben invited?": "Yes"})
    result = ws.read("t.txt", GUESTS, reader=recorded({"available": {"verdict": "differ"}}))
    assert answer_of(result, "Is Ben invited?")["both_ways"]["different"] == "Yes"


def test_a_text_that_cannot_all_be_true_is_never_answered_from_the_split_text(monkeypatch):
    calls = _fake_lean(monkeypatch, {"Is Ola closed?": "no answer"}, {"Is Ola closed?": "Yes"})
    result = ws.read("t.txt", CONTRADICTION, reader=recorded({**same("booked", "cleaned"),
                                                              "closed": {"verdict": "differ"}}))
    a = answer_of(result, "Is Ola closed?")
    assert len(calls) == 1 and a["answer"] == "no answer" and "both_ways" not in a
    assert a["text"][-1] == "(This reads 'closed' with one meaning in sentences 1 and 2.)"


def test_a_text_whose_consistency_lean_could_not_check_is_never_answered_from_the_split_text(monkeypatch):
    """X6 is treated like X3: when Lean found no answer because it could not check that the sentences can all be true
    together, the split text is not read and no branch answers from it."""
    calls = _fake_lean(monkeypatch, {"Is Ola closed?": "no answer"}, {"Is Ola closed?": "Yes"}, unknown_reason="X6")
    result = ws.read("t.txt", CONTRADICTION, reader=recorded({**same("booked", "cleaned"),
                                                              "closed": {"verdict": "differ"}}))
    a = answer_of(result, "Is Ola closed?")
    assert len(calls) == 1 and a["answer"] == "no answer" and "both_ways" not in a
    assert a["text"][-1] == "(This reads 'closed' with one meaning in sentences 1 and 2.)"


def test_a_split_reading_lean_does_not_read_is_never_a_plain_answer(monkeypatch):
    def lean(hid, name, scratch):
        if "zq" in hid.text.split("Words:")[0]:
            return {"status": "refused", "refusals": [], "text": []}
        return {"status": "read", "text": [], "coverage": {}, "answers": [
            {"question": x, "lead": "yes", "answer": "Yes", "text": ["Yes."], "reasons": []}
            for x in hid.text.splitlines() if x.startswith("Is ")]}
    monkeypatch.setattr(ws, "_lean", lean)
    result = ws.read("t.txt", GUESTS, reader=recorded({"available": {"verdict": "differ"}}))
    assert answer_of(result, "Is Ben invited?")["both_ways"]["different"] == "cannot check"


# --- the whole read, with Lean -------------------------------------------------------------------------------------

def test_layer_1_a_word_on_two_kinds_is_two_separate_words(tmp_path):
    reader = recorded(same("admitted", "banned", "unused", "valid, of a ticket", "valid, of a visitor"))
    result = ws.read("t.txt", TWO_KINDS, reader=reader, scratch=tmp_path)
    assert result["status"] == "read", result["text"]
    assert ("  valid, of a ticket (sentences 1 and 8) / valid, of a visitor (sentences 2, 3 and 9): read as two "
            "separate words") in result["text"]
    got = {a["question"]: a["answer"] for a in result["answers"]}
    assert got == {"Is Pass valid?": "Yes", "Is Kim valid?": "No", "Is Kim admitted?": "not determined"}
    assert '"valid, of a ticket" (sentences 1, 8), "valid, of a visitor" (sentences 2, 3, 9)' in reader.calls[0]


def test_layer_2_a_raised_word_that_changes_the_answer_is_answered_both_ways(tmp_path):
    reader = recorded({"available": {"verdict": "differ"}, "idle": {"verdict": "same"}, "invited": {"verdict": "same"}})
    result = ws.read("t.txt", GUESTS, reader=reader, scratch=tmp_path)
    a = answer_of(result, "Is Ben invited?")
    assert a["both_ways"] == {"words": ["available"], "same": "Yes", "different": "not determined"}
    b = answer_of(result, "Is Ben available?")
    assert b["both_ways"]["same"] == "Yes"
    assert b["both_ways"]["uses"] == [{"sentence": 1, "answer": "Yes"}, {"sentence": 2, "answer": "not determined"}]
    assert not any("zq" in line for line in result["text"])  # hidden words are shown as the writer's words
    assert any(line.startswith("  available (sentences 1, 2 and 6): may mean different things (meaning check: the "
                               "reader said differ") for line in result["text"])


def test_layer_2_a_word_the_reader_finds_used_one_way_is_read_as_one_meaning(tmp_path):
    reader = recorded(same("available", "idle", "invited"))
    result = ws.read("t.txt", GUESTS, reader=reader, scratch=tmp_path)
    assert answer_of(result, "Is Ben invited?")["answer"] == "Yes"
    assert any(line.startswith("  available (sentences 1, 2 and 6): read as ONE meaning (meaning check: the reader "
                               "said same") for line in result["text"])


@pytest.mark.parametrize("text, welcome, free", [
    (GLOSSED, "not determined", "Yes"),
    (GLOSSED.replace("(no charge)", "(not busy)"), "Yes", "Yes"),
    ("Every guest who is idle is free.\nHere 'free' means not busy.\nEvery guest who is free is welcome.\n"
     "Here 'free' means no charge.\nBen is a guest.\nBen is idle.\nIs Ben welcome?\n", "not determined", None),
    ("In this text, free means no charge.\nEvery guest who is idle is free.\nEvery guest who is free is welcome.\n"
     "Ben is a guest.\nBen is idle.\nIs Ben welcome?\n", "Yes", None),
])
def test_layer_3_the_writer_settles_a_meaning_in_plain_english(tmp_path, text, welcome, free):
    # a settled word is not sent to the reader at all
    reader = recorded({**same("idle", "late", "welcome"), "free": {"verdict": "differ"}})
    result = ws.read("t.txt", text, reader=reader, scratch=tmp_path)
    assert result["status"] == "read", result["text"]
    assert answer_of(result, "Is Ben welcome?")["answer"] == welcome
    if free:
        assert answer_of(result, "Is Ben free (not busy)?")["answer"] == free
    assert all('"free"' not in call.split("WORDS:")[-1] for call in reader.calls)


def test_layer_3_a_bare_question_on_a_word_with_two_meanings_is_answered_per_meaning(tmp_path):
    text = GLOSSED.replace("Is Ben free (not busy)?", "Is Ben free?")
    result = ws.read("t.txt", text, scratch=tmp_path)
    a = answer_of(result, "Is Ben free?")
    # "not busy: Yes" holds only if 'idle' (raised by the word list) means the same in sentences 1 and 5: the answer
    # says so (review A2: the split reading of the other raised words was not looked at)
    assert a["both_ways"] == {"meanings": [{"meaning": "not busy", "answer": "Yes", "different": "not determined"},
                                           {"meaning": "no charge", "answer": "not determined"}], "words": ["idle"]}
    assert a["text"][0] == ("Depends on which meaning is meant: if 'free' here means not busy: Yes if 'idle' means "
                            "the same in all its sentences (idle: sentences 1 and 5), and the text does not settle "
                            "this if not; if 'free' here means no charge: the text does not settle this.")


def test_layer_3_a_bare_use_of_a_word_given_two_meanings_is_asked_about(tmp_path):
    text = GLOSSED.replace("Every guest who is late is not free (not busy).", "Every guest who is late is not free.")
    result = ws.read("t.txt", text, scratch=tmp_path)
    assert result["status"] == "refused"
    assert [r["code"] for r in result["refusals"]] == ["MEANING_NOT_SAID"]
    assert "'not busy'" in result["refusals"][0]["message"] and "free (not busy)" in result["refusals"][0]["message"]


def test_without_the_yes_the_word_list_alone_decides_what_is_raised(tmp_path):
    result = ws.read("t.txt", GUESTS, scratch=tmp_path)
    assert result["meaning_check"] == "word list"
    raised = [line for line in result["text"] if "may mean different things" in line]
    assert raised and all("word list alone" in line for line in raised)


def test_interactive_use_asks_one_plain_question_and_writes_the_reply_into_the_text(tmp_path):
    reader = recorded({"available": {"verdict": "differ"}, "idle": {"verdict": "same"}, "invited": {"verdict": "same"}})
    replies = iter(["no", "not busy", "offered"])
    asked = []

    def ask(prompt):
        asked.append(prompt)
        return next(replies)
    text, result = ws.interactive(Path("t.txt"), GUESTS, reader, ask, scratch=tmp_path)
    assert asked[0] == "In sentences 1 and 2, does 'available' mean the same thing? (yes/no) "
    assert text.splitlines()[:2] == ["Every guest who is idle is available (not busy).",
                                     "Every guest who is available (offered) is invited."]
    assert result["questions_for_writer"] == []
    assert answer_of(result, "Is Ben invited?")["answer"] == "not determined"


def test_a_yes_reply_makes_one_word_and_nothing_is_asked_again(tmp_path):
    reader = recorded({"available": {"verdict": "differ"}, "idle": {"verdict": "same"}, "invited": {"verdict": "same"}})
    replies = iter(["yes", "not busy"])
    text, result = ws.interactive(Path("t.txt"), GUESTS, reader, lambda prompt: next(replies), scratch=tmp_path)
    assert "available (not busy) is invited" in text and result["questions_for_writer"] == []
    assert answer_of(result, "Is Ben invited?")["answer"] == "Yes"


# --- review fixes (2026-11-27) -------------------------------------------------------------------------------------

def test_a_contradiction_about_one_kind_leaves_no_answer_about_any_kind(tmp_path):
    """Layer 1 reads one hidden document per kind; each asks Lean a probe question, so the ticket sentences'
    contradiction (no question about tickets) is found, and the visitor question is not answered (real Lean)."""
    text = ("Every ticket that is used is not valid.\nPass is a ticket.\nPass is used.\nPass is valid.\n"
            "Every visitor who is valid is admitted.\nKim is a visitor.\nKim is valid.\nIs Kim admitted?\n")
    result = ws.read("t.txt", text, scratch=tmp_path)
    a = answer_of(result, "Is Kim admitted?")
    assert a["answer"] == "no answer" and a["reasons"] == ["X3"]
    assert a["text"] == ["VE does not answer this: the sentences about tickets cannot all be true together, so the "
                         "whole text cannot either."]
    fine = ws.read("t.txt", text.replace("Pass is valid.\n", ""), scratch=tmp_path)
    a = answer_of(fine, "Is Kim admitted?")   # without the contradiction: answered ('valid' may be raised)
    assert (a.get("both_ways") or {}).get("same", a["answer"]) == "Yes"


def test_each_kind_document_carries_a_probe_and_its_answer_is_not_shown(monkeypatch):
    calls = _fake_lean(monkeypatch, {}, {})
    result = ws.read("t.txt", TWO_KINDS, reader=recorded({}))
    assert all(any(line.startswith("Is ") for line in text.splitlines()) for text in calls)
    assert [a["question"] for a in result["answers"]] == ["Is Pass valid?", "Is Kim valid?", "Is Kim admitted?"]


def test_lean_answers_must_be_to_the_hidden_documents_own_questions(monkeypatch):
    def lean(hid, name, scratch):
        return {"status": "read", "text": [], "coverage": {}, "answers": [
            {"question": "Is Somebody else?", "lead": "yes", "answer": "Yes", "text": ["Yes."], "reasons": []}
            for x in hid.text.splitlines() if x.startswith("Is ")]}
    monkeypatch.setattr(ws, "_lean", lean)
    with pytest.raises(ws.CheckerUnavailable):
        ws.read("t.txt", GUESTS, reader=recorded({"available": {"verdict": "differ"}}))


def test_a_meaning_branch_is_never_shown_as_a_sentence_number(monkeypatch):
    """Per-meaning answers equal, but the split reading of a raised word differs for one meaning."""
    text = GLOSSED.replace("Is Ben free (not busy)?", "Is Ben free?")
    _fake_lean(monkeypatch, {"Is Ben freezqa?": "Yes", "Is Ben freezqb?": "Yes"},
               {"Is Ben freezqa?": "not determined", "Is Ben freezqb?": "Yes"})
    result = ws.read("t.txt", text, reader=recorded({**same("late", "welcome"), "idle": {"verdict": "differ"}}))
    a = answer_of(result, "Is Ben free?")
    assert "sentence not busy" not in a["text"][0] and "uses" not in a["both_ways"]
    assert a["both_ways"]["meanings"][0] == {"meaning": "not busy", "answer": "Yes", "different": "not determined"}


def test_hidden_words_never_reach_a_refusal(monkeypatch):
    def lean(hid, name, scratch):
        token = next(iter(hid.tokens), "freezqa")
        return {"status": "refused", "text": [], "refusals": [
            {"code": "LEAN_REFUSED", "line": 1, "word": token, "message": f"Lean did not read '{token}'.", "fix": None}]}
    monkeypatch.setattr(ws, "_lean", lean)
    result = ws.read("t.txt", GLOSSED)
    assert result["status"] == "refused" and not any("zq" in str(r) for r in result["refusals"])


@pytest.mark.parametrize("extra, said", [
    ("In this text, free means no charge.\nIn this text, free means not busy.\n", "a second meaning for the whole text"),
    ("Every guest who is idle is free.\nHere 'free' means not busy.\nHere 'free' means no charge.\n",
     "in sentence 1 a second meaning"),
    ("Every guest who is idle is free (not busy).\nHere 'free' means no charge.\n", "in sentence 1 a second meaning"),
])
def test_two_meanings_given_for_the_same_use_are_refused(extra, said, tmp_path):
    result = ws.read("t.txt", extra + "Ben is a guest.\nBen is idle.\nIs Ben free?\n", scratch=tmp_path)
    assert result["status"] == "refused"
    assert any(r["code"] == "GLOSS_UNREAD" and said in r["message"] for r in result["refusals"]), result["refusals"]


@pytest.mark.parametrize("gloss", ["or not", "if late", "maybe busy", "not", "yes"])
def test_a_bracket_that_hedges_is_not_read_as_a_meaning(gloss, tmp_path):
    assert ws.normal_gloss(gloss) is None
    result = ws.read("t.txt", f"Every guest who is idle is free ({gloss}).\nBen is a guest.\nBen is idle.\nIs Ben free?\n",
                     scratch=tmp_path)
    assert result["status"] == "refused" and result["refusals"][0]["code"] == "GLOSS_UNREAD"


def test_a_gloss_on_one_use_only_is_said_to_be_unused(tmp_path):
    text = GUESTS.replace("Every guest who is idle is available.", "Every guest who is idle is available (not busy).")
    result = ws.read("t.txt", text, reader=recorded(same("available", "idle", "invited")), scratch=tmp_path)
    assert any(line.startswith("  available: the meaning in brackets in sentence 1 ('not busy') is not used")
               for line in result["text"])


def test_a_checked_word_is_not_also_said_to_be_read_with_one_meaning_throughout(tmp_path):
    result = ws.read("t.txt", GUESTS, scratch=tmp_path)
    for line in result["text"]:
        if line.startswith("  available: a property"):
            assert "ONE meaning throughout" not in line


def test_a_raised_word_stated_once_says_how_its_question_is_read(tmp_path):
    text = "Every guest who is idle is available.\nBen is a guest.\nIs Ben available?\nIs Ben idle?\n"
    result = ws.read("t.txt", text, reader=recorded({"available": {"verdict": "differ"}, "idle": {"verdict": "differ"}}),
                     scratch=tmp_path)
    assert any(line.startswith("  available (sentences 1 and 3): may mean different things") and
               "only sentence 1 states it" in line for line in result["text"]), result["text"]


def test_the_output_says_when_the_text_was_sent_and_to_which_program(tmp_path):
    (tmp_path / "same.py").write_text("import json, re, sys\n"
                                      "t = sys.stdin.read()\n"
                                      "w = re.findall(r'\"([^\"]+)\" \\(sentences', t.split('WORDS:')[-1])\n"
                                      "print(json.dumps({x: {'verdict': 'same'} for x in w}))\n")
    command = f"{sys.executable} -I {tmp_path / 'same.py'}"
    (tmp_path / "config" / "ve").mkdir(parents=True)
    (tmp_path / "config" / "ve" / "settings.json").write_text(json.dumps(
        {"word_reader": {"consent": True, "consent_command": command, "command": command}}))
    (tmp_path / "g.txt").write_text(GUESTS)
    done = _cli(tmp_path, str(tmp_path / "g.txt"))
    assert f"your text was sent to the reader program ({command}), two times" in done.stdout, done.stdout
