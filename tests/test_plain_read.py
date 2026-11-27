"""`ve read`: a plain text with no front matter, its vocabulary derived from the word list (plain vocabulary, version 1;
row plain-vocabulary-1126, ruling 2026-11-26 items 1 and 3).

Before: every one of these texts was refused with "ve-document@1 needs JSON front matter", and `ve read` did not exist
(the CLI rejected the command, exit 2). The deriver is untrusted Python: these tests are its only check that no line is
skipped, that every refusal class names its word and offers its line, and that Lean's coverage gates every answer.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from subprocesses import HANG_TIMEOUT
from ve import plain_read
from ve.errors import CheckerUnavailable, ResourceLimit, VEError
from ve.plain_read import derive, read, vocabulary_lines

ROOT = Path(__file__).resolve().parents[1]
ENV_ALLOW = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "PYTHONPATH", "PYTHONNOUSERSITE", "PYTHONPYCACHEPREFIX")

# The three texts of part 1 (b), as a writer ends up writing them, with no front matter (writer-runs pet11, gym4, hw2;
# each name now says what it is in one line).
PET = """Every puppy that is sellable is vaccinated.
Every puppy that is underage is not sellable.
Every puppy that is vaccinated and is not underage is sellable.
Rex is a puppy.
Rex is vaccinated.
Rex is not underage.
Is Rex sellable?
"""
GYM = """Every member who is paid and is not expired is admitted.
Every member who is expired is not admitted.
Every member who is premium is paid.
Mia is a member.
Mia is premium.
Mia is not expired.
Is Mia admitted?
"""
HOMEWORK = """Every student who is late and is not excused is penalised.
Every student who is certified is excused.
Every student who is excused is not penalised.
Sam is a student.
Sam is late.
Sam is certified.
Is Sam penalised?
"""


def cli(tmp, *args, env_extra=None):
    """`ve read`, writing its scratch document under the test's own directory (TMPDIR), with settings of its own
    (XDG_CONFIG_HOME: no reader yes unless the test gives one) and no reader program unless the test sets one."""
    env = {**{k: v for k, v in os.environ.items() if (k in ENV_ALLOW or k.startswith("VE_")) and k != "VE_WORD_READER"},
           "TMPDIR": str(tmp), "XDG_CONFIG_HOME": str(tmp / "config"), **(env_extra or {})}
    return subprocess.run([sys.executable, "-m", "ve", "read", *map(str, args)], cwd=ROOT, env=env, text=True,
                          capture_output=True, timeout=HANG_TIMEOUT)


def test_ve_read_runs_the_word_senses_reader():
    """`ve read` (every cli() call here) runs ve/word_senses.py's main, so a change there selects this file."""
    assert (ROOT / "ve" / "word_senses.py").is_file()
    assert "word_senses" in (ROOT / "ve" / "__main__.py").read_text()


def codes(text):
    return sorted((r.code, r.word) for r in derive(text).refusals)


# A reader program that says "same" for every word it is given (word senses v1: the writer's yes is in the test's
# own settings; tests/test_word_senses.py covers the reader itself).
SAME_READER = """import json, re, sys
words = re.findall(r'"([^"]+)" [(]sentences', sys.stdin.read().split("WORDS:")[-1])
print(json.dumps({w: {"verdict": "same"} for w in words}))
"""


def reader_yes(tmp):
    (tmp / "config" / "ve").mkdir(parents=True, exist_ok=True)
    command = f"{sys.executable} -I {tmp / 'same_reader.py'}"
    (tmp / "config" / "ve" / "settings.json").write_text(json.dumps({"word_reader": {"consent": True,
                                                                                      "consent_command": command}}))
    (tmp / "same_reader.py").write_text(SAME_READER)
    return {"VE_WORD_READER": command}


@pytest.mark.parametrize("text, answer", [(PET, "Yes."), (GYM, "Yes."), (HOMEWORK, "No. The document rules this out.")])
def test_part1_texts_are_read_with_no_front_matter(tmp_path, text, answer):
    """Fails on main: `ve read` is not a command, and `ve ask` refuses the file ("needs JSON front matter").
    Word senses v1: with the writer's yes and a reader that finds every word used in one meaning, the answer is
    plain; with the word list alone, words of several meanings that change the answer make it an answer both ways
    whose same-meaning branch is the same answer."""
    path = tmp_path / "rules.txt"
    path.write_text(text)
    alone = cli(tmp_path, path)
    assert alone.returncode in (0, 3), alone.stderr
    if alone.returncode == 3:
        assert any(line.startswith("  Depends on what ") and f": {answer.split('.')[0]}." in line
                   for line in alone.stdout.splitlines()), alone.stdout
    done = cli(tmp_path, path, env_extra=reader_yes(tmp_path))
    assert done.returncode == 0, done.stdout + done.stderr
    out = done.stdout.splitlines()
    assert out[0] == "I read these words as:"
    question = next(i for i, line in enumerate(out) if line.startswith("Question (line 7): Is "))
    # The vocabulary and Lean's 100% coverage line come before any answer.
    assert any(line.startswith("Lean read every sentence: 5 of 5 CHECKED") and "100%" in line for line in out[:question])
    assert out[question + 2] == "  " + answer


def test_every_sentence_is_accounted_for():
    """No line is ever skipped: every sentence is a statement, a name's kind, a question or a declaration."""
    d = derive(PET + "\nWords: overlimit (property of puppy)\nRex is vaccinated. Is Rex underage?\n")
    assert not d.refusals
    shapes = [s.shape for s in d.sentences]
    assert len(d.sentences) == 10 and None not in shapes
    assert len(d.statements) + shapes.count("kind") + len(d.questions) + shapes.count("words-property") == 10
    assert [s.where for s in d.questions] == ["line 7", "line 10 (sentence 2)"]


def test_an_unknown_line_refuses_the_whole_text(tmp_path):
    """Challenge 1: a skipped "No ..." line would turn the text's answer into a Yes; the whole text is refused."""
    text = ("Every visitor who is young is admitted.\nNo visitor who is unaccompanied is admitted.\n"
            "Mia is a visitor.\nMia is young.\nMia is unaccompanied.\nIs Mia admitted?\n")
    assert codes(text) == [("UNKNOWN_LINE", "")]
    path = tmp_path / "visit.txt"
    path.write_text(text)
    done = cli(tmp_path, path)
    assert done.returncode == 2
    assert done.stdout.startswith("Not read: 1 problem; nothing is answered.")
    assert 'line 2: "No visitor who is unaccompanied is admitted." is not in a shape VE reads' in done.stdout
    assert "Yes" not in done.stdout and "Question" not in done.stdout


BASE = "Every member who is paid is admitted.\nMia is a member.\nMia is paid.\nIs Mia admitted?\n"


@pytest.mark.parametrize("extra, code, word, fix", [
    # a word not in the list (or not an adjective or participle there)
    ("Every member who is overlimit is fined.\n", "UNKNOWN_WORD", "overlimit", "Words: overlimit (property of member)"),
    ("Every member who is eating is fined.\n", "UNKNOWN_WORD", "eating", "Words: eating (property of member)"),
    ("Every zorblat who is late is fined.\n", "UNKNOWN_WORD", "zorblat", "Words: zorblat (kind of thing)"),
    # two content words in one slot
    ("Ben is a premium member.\n", "TWO_WORDS", "premium member", None),
    ("Mia is too young.\n", "TWO_WORDS", "too young", None),
    # a word used on two kinds
    ("Every guest who is paid is welcome.\n", "WORD_TWO_KINDS", "paid", None),
    # a word that is also a kind
    ("Every member who is member is fined.\n", "WORD_IS_KIND", "member", None),
    # a name with no 'is a' line, or two
    ("Ben is paid.\n", "NAME_NO_KIND", "Ben", "Ben is a member."),
    ("Mia is a member.\n", "NAME_TWO_KINDS", "Mia", None),
    # un-/non- next to its base: the fix writes 'not'
    ("Every member who is unpaid is fined.\n", "NEGATED_PAIR", "unpaid", "Every member who is not paid is fined."),
])
def test_each_refusal_class_names_its_word_and_offers_its_line(extra, code, word, fix):
    d = derive(BASE + extra)
    assert [(r.code, r.word) for r in d.refusals] == [(code, word)] and d.raw is None
    refusal = d.refusals[0]
    assert refusal.fix == fix
    assert word.split()[0] in refusal.message and refusal.line == 5 or code in ("WORD_TWO_KINDS", "NAME_TWO_KINDS")
    if fix is not None:
        # The offered line, applied as offered (added, or replacing the named line), clears the refusal.
        lines = (BASE + extra).splitlines()
        if refusal.replaces:
            lines[refusal.replaces - 1] = fix
        else:
            lines.append(fix)
        assert not [r for r in derive("\n".join(lines) + "\n").refusals if r.code == code]


def test_more_than_one_kind_offers_no_name_line():
    d = derive("Every member who is paid is admitted.\nEvery guest who is late is fined.\nBen is late.\n")
    assert [(r.code, r.fix) for r in d.refusals] == [("NAME_NO_KIND", None)]


@pytest.mark.parametrize("word", ["true", "all", "some", "only", "both"])
def test_structure_words_are_refused_not_read(word):
    d = derive(f"Every guest who is {word} is fined.\nAna is a guest.\nAna is {word}.\nIs Ana fined?\n")
    assert d.raw is None and {r.code for r in d.refusals} <= {"RESERVED_WORD", "WORDING_REFUSED"} and d.refusals


def test_the_multi_sense_notice_is_shown_for_every_such_word():
    """Ruling item 3: a property word with more than one sense in the list says so, every time it is shown."""
    d = derive("Every visitor who is free is admitted.\nEvery visitor who is sellable is fined.\nMia is a visitor.\n"
               "Mia is free.\nIs Mia admitted?\n")
    shown = vocabulary_lines(d)
    free = next(line for line in shown if line.startswith("  free:"))
    assert "9 senses in the list: this text reads it with ONE meaning throughout" in free
    single = next(line for line in shown if line.startswith("  sellable:"))
    assert "1 sense in the list" in single and "ONE meaning" not in single
    for word, row in d.properties.items():
        line = next(x for x in shown if x.startswith(f"  {word}:"))
        assert ("ONE meaning throughout" in line) == (row["senses"] > 1)
    assert vocabulary_lines(derive(PET)) == vocabulary_lines(derive(PET))


def test_the_shown_vocabulary_and_sense_notice_come_before_the_answer(tmp_path):
    result = read(tmp_path / "free.txt", "Every visitor who is free is admitted.\nMia is a visitor.\nMia is free.\n"
                  "Is Mia admitted?\n", scratch=tmp_path)
    text = result["text"]
    notice = next(i for i, line in enumerate(text) if "ONE meaning throughout" in line and line.startswith("  free:"))
    question = next(i for i, line in enumerate(text) if line.startswith("Question"))
    assert notice < question and result["answers"][0]["answer"] == "Yes"


def test_not_settled_is_not_determined(tmp_path):
    result = read(tmp_path / "pet.txt", PET + "Is Rex weaned?\nEvery puppy that is weaned is calm.\n",
                  scratch=tmp_path)
    assert result["status"] == "read"
    assert [a["answer"] for a in result["answers"]] == ["Yes", "not determined"]


def test_no_answer_unless_lean_shows_every_byte_checked(tmp_path, monkeypatch):
    from ve.document import report
    real = report.check_document

    def partial(path, **kw):
        out = real(path, **kw)
        out["coverage"] = {**out["coverage"], "coverage_percent": 99,
                           "bytes_by_status": {"CHECKED": out["coverage"]["source_bytes"] - 1, "OPEN": 1}}
        return out
    monkeypatch.setattr(report, "check_document", partial)
    result = read(tmp_path / "pet.txt", PET, scratch=tmp_path)
    assert result["status"] == "refused" and "answers" not in result
    assert [r["code"] for r in result["refusals"]] == ["NOT_ALL_CHECKED"]


def test_a_sentence_lean_refuses_is_named_by_its_line(tmp_path, monkeypatch):
    from ve.document import report

    def refuse_line_5(path, **kw):
        if "Rex is vaccinated." in Path(path).read_text().split("---\n")[-1]:
            raise VEError("Sentence 1: not read")
        return {"coverage": {}}
    monkeypatch.setattr(report, "check_document", refuse_line_5)
    result = read(tmp_path / "pet.txt", PET, scratch=tmp_path)
    assert result["status"] == "refused"
    assert [(r["code"], r["line"]) for r in result["refusals"]] == [("LEAN_REFUSED", 5)]


def test_a_no_front_matter_file_is_a_new_input(tmp_path, monkeypatch):
    """Existing documents keep their front matter and identities (`ve read` refuses a document); the derived document
    names the word list's digest, so a different list gives a different identity."""
    doc = tmp_path / "doc.ve.md"
    doc.write_text("---\n{}\n---\nRex is vaccinated.\n")
    done = cli(tmp_path, doc)
    assert done.returncode == 2 and "ask it with `ve ask`" in done.stderr
    before = derive(PET).raw
    assert plain_read.lexicon_digest()[:16] in before.decode()
    monkeypatch.setattr(plain_read, "lexicon_digest", lambda: "0" * 64)
    after = derive(PET).raw
    assert after != before and ("0" * 16) in after.decode()
    meta = json.loads(before.decode().split("---\n")[1])
    assert meta["format"] == "ve-document@1" and all(u["status"] == "CHECKED" for u in meta["units"])


@pytest.mark.parametrize("line", ["Nobody is a member.", "Everyone is paid.", "She is paid.", "Is Everybody admitted?",
                                  "Nothing is a member.", "This is paid."])
def test_a_quantifier_or_pronoun_is_never_a_name(line):
    """Review 1 A3: "Nobody is a member." was consumed as a name's kind line, never fenced, and the text answered Yes."""
    d = derive(BASE + line + "\n")
    assert [(r.code, r.fix) for r in d.refusals] == [("NOT_A_NAME", None)] and d.raw is None
    assert line.split()[0 if not line.startswith("Is ") else 1] not in d.names


def test_a_two_word_kind_offers_no_line():
    """Review 1 A1: "Ben is a former member." split into "Ben is a member. Ben is former." would answer Yes."""
    d = derive("Every member who is paid is admitted.\nBen is a former member.\nBen is paid.\nIs Ben admitted?\n")
    assert [(r.code, r.fix) for r in d.refusals] == [("TWO_WORDS", None)]
    assert "a former member is not a member" in d.refusals[0].message


@pytest.mark.parametrize("text, fix", [
    # an adjective base: "unhappy" is not "not happy" (review 1 A2)
    ("Every guest who is happy is admitted.\nEvery guest who is unhappy is fined.\nMia is a guest.\n", None),
    # "not unpaid" is not "paid"
    ("Every guest who is paid is admitted.\nEvery guest who is not unpaid is fined.\nMia is a guest.\n", None),
    # a participle base, "is unX": the line is offered
    ("Every guest who is paid is admitted.\nEvery guest who is unpaid is fined.\nMia is a guest.\n",
     "Every guest who is not paid is fined."),
])
def test_un_words_get_a_line_only_where_it_means_not(text, fix):
    d = derive(text)
    assert [(r.code, r.fix) for r in d.refusals] == [("NEGATED_PAIR", fix)]


def test_a_question_about_an_un_word_is_not_turned_around():
    """Review 1 B5: "Is Mia unpaid?" -> "Is Mia paid?" would print the answer to the opposite question."""
    d = derive("Every guest who is paid is admitted.\nMia is a guest.\nIs Mia unpaid?\n")
    assert [(r.code, r.fix) for r in d.refusals] == [("NEGATED_PAIR", None)]


def test_a_line_fix_keeps_the_lines_other_sentences():
    """Review 1 B4: a fix replaces a whole line, so it carries the line's other sentences, and two fixes on one line are
    offered as one line."""
    d = derive("Every guest who is paid is admitted.\nMia is a guest. Mia is unpaid.\nIs Mia admitted?\n")
    assert [(r.fix, r.replaces) for r in d.refusals] == [("Mia is a guest. Mia is not paid.", 2)]
    d = derive("Every guest who is paid and is vaccinated is admitted.\nMia is a guest. Mia is unpaid. "
               "Mia is unvaccinated.\nIs Mia admitted?\n")
    fixes = [(r.fix, r.replaces) for r in d.refusals]
    assert fixes.count(("Mia is a guest. Mia is not paid. Mia is not vaccinated.", 2)) == 1
    assert sum(f is not None for f, _ in fixes) == 1
    fixed = derive("Every guest who is paid and is vaccinated is admitted.\n"
                   "Mia is a guest. Mia is not paid. Mia is not vaccinated.\nIs Mia admitted?\n")
    assert not fixed.refusals


@pytest.mark.parametrize("error", [CheckerUnavailable("CheckerUnavailable: no service"),
                                   ResourceLimit("ResourceLimit: out of budget")])
def test_a_checker_that_does_not_answer_is_not_a_refusal(tmp_path, monkeypatch, error):
    """Review 1 B6: CheckerUnavailable and ResourceLimit (a VEError) leave `read` (exit 5 or 4), never a refusal."""
    from ve.document import report

    def unavailable(path, **kw):
        raise error
    monkeypatch.setattr(report, "check_document", unavailable)
    with pytest.raises(type(error)):
        read(tmp_path / "pet.txt", PET, scratch=tmp_path)
