"""Q1 end to end: a question read by Lean's `english.question` (docs/spec/question-answering.md 4.1, 7, 8).

The fixture table (`tests/question_fixtures.py`) is compared three ways: with the spec's own rows of section 7, with
Lean (the `#guard`s generated into `lean/VE/Question/Fixtures.lean`, which `lake build` evaluates), and with the running
`ve_service`, through the relay (`ve.backends.english_lean.read_question`), through the one entry point `ve.ask.read`
and through the CLI `ve ask --reading`. The relay's checks of an untrusted answer are fuzzed on genuine answers; the
mode's own decoding is fuzzed on malformed cases; text variants (spacing, quotes, look-alike letters, control
characters) get well-formed answers.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

import question_fixtures as F
from subprocesses import HANG_TIMEOUT
from ve import ask
from ve.backends import english_lean, relay
from ve.english import EnglishVocabulary
from ve.errors import CheckerUnavailable, ResourceLimit, VEError

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/spec/question-answering.md"
MODE = "english.question"

pytestmark = pytest.mark.filterwarnings("ignore::ve.english.UnreviewedVocabularyWarning")

IDS = [row[0] for row in F.FIXTURES]
DOCUMENT_ROWS = [row for row in F.FIXTURES if row[1] in F.DOCUMENTS]


def live(frame: str, question: str) -> dict:
    row = relay.decide_once(MODE, F.request(frame, question))
    assert row.get("status") == "ok", row
    return row["result"]


# ------------------------------------------------------------------ the table against the spec

def _spec_rows() -> dict[str, tuple[str, str]]:
    """The rows of the fixture tables of section 7 by their id (`| G1 | ...`): the whole row, and its Q1 cell (the
    column whose header begins with `Q1`)."""
    section = SPEC.read_text().split("## 7. Acceptance fixtures", 1)[1].split("## 8. Wire", 1)[0]
    rows, q1 = {}, None
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        if line.startswith("| # |"):
            q1 = next((i for i, c in enumerate(cells) if c.startswith("Q1")), None)
        elif q1 is not None and re.fullmatch(r"G\d+|A\d+d?|U\d+", cells[0]):
            rows[cells[0]] = (line, cells[q1])
    return rows


def render_formula(data) -> str:
    """The spec's notation of a formula (section 7): `all s φ`, `ex s φ`, `not φ`, `implies φ ψ`,
    `pred p [args]`, `var i`, `const c`, each formula argument in parentheses."""
    def term(t):
        return f"{t[0]} {t[1]}"

    def sub(f):
        return f"({formula(f)})"

    def formula(f):
        head = f[0]
        if head == "forall":
            return f"all {f[1]} {sub(f[2])}"
        if head == "exists":
            return f"ex {f[1]} {sub(f[2])}"
        if head == "not":
            return f"not {sub(f[1])}"
        if head == "implies":
            return f"implies {sub(f[1])} {sub(f[2])}"
        if head == "unary":
            return f"pred {f[1]} [{term(f[2])}]"
        raise AssertionError(f"no spec notation for {head}")
    return formula(data)


SPEC_ROW = {"G22c": "G22", "G11c": "G11", "A6r": "A6", "A6c": "A6", "A6d": "A6"}
# A control question: a fixture its row names after `Control:`.
CONTROLS = {"G22c", "G11c"}


STATUS_WORDS = tuple(english_lean.QUESTION_FIELDS)


@pytest.mark.parametrize("fixture,frame,question,answer", F.FIXTURES, ids=IDS)
def test_the_fixture_table_is_the_specs(fixture, frame, question, answer):
    """Every fixture is a row of section 7, and what the row says of the answer is the table's: the status it
    names in bold, any code of the contract it names, its span, its formula, its asked sentence, and every piece
    (between `…`) of each text or rephrasing it quotes."""
    rows = _spec_rows()
    line, row = rows["A1"] if fixture == "A1d" else rows[SPEC_ROW.get(fixture, fixture)]
    if fixture in CONTROLS:
        assert f"Control: `{question}` on `{frame}` is **{answer['status']}**" in row, fixture
        return
    row = row.split("Control:")[0]
    assert f"`{question}`" in line or fixture in ("G20", "G25", "G26", "A1d"), fixture
    named = [w for w in STATUS_WORDS if f"**{w}**" in row]
    assert not named or named == [answer["status"]], (fixture, named)
    codes = {c for c in english_lean.QUESTION_CLASSES if re.search(rf"\b{c}\b", row)}
    assert codes <= {answer.get("code")}, (fixture, codes)
    if "span" in answer and re.search(r"span \(|\*\*\(\d", row):
        a, b = answer["span"]
        assert f"span ({a}, {b})" in row or f"**({a}, {b})**" in row, (fixture, answer["span"])
    if answer["status"] == "one" and re.search(r"`(all|ex|not|pred|implies) ", row):
        assert f"`{render_formula(answer['ast'])}`" in row, fixture
    if answer["status"] == "one" and "asked `" in row:
        assert f"asked `{answer['sentence']}`" in row, fixture
    texts = " ".join([answer.get("text", ""), *answer.get("rephrasings", ()),
                      answer.get("advice", {}).get("text", "")])
    for m in re.finditer(r"`([^`]+)`", row):
        quoted = m.group(1)
        # A text or a rephrasing: a quoted sentence of Lean's (the question itself and other questions the row
        # mentions, such as a control or a rephrasing that is not offered, are not the answer's).
        if not (quoted[0].isupper() or quoted[0] == "…") or " " not in quoted or quoted == question:
            continue
        if quoted.endswith("?") and "rephrasings" not in row[max(0, m.start() - 60):m.start()]:
            continue
        for piece in (p.strip() for p in quoted.split("…")):
            assert piece in texts, (fixture, piece)


def test_the_spec_rows_are_all_in_the_table():
    """No Q1 fixture of section 7 is left out, apart from the two the mode cannot reach (G21's work budget 0 and
    G24's speech-act auxiliaries, guarded in Lean only) and the Q2-only rows."""
    covered = {SPEC_ROW.get(f, f) for f in IDS}
    assert set(_spec_rows()) - covered == {"G21", "G24"}


# ------------------------------------------------------------------ the table against Lean

def test_the_lean_guards_are_the_fixture_table():
    """`lean/VE/Question/Fixtures.lean` is the rendering of the table, and the Lean build evaluates it."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("question_fixtures_tool", ROOT / "tools/question_fixtures.py")
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    assert generator.TARGET.read_text() == generator.render()
    assert "import VE.Question.Fixtures" in (ROOT / "lean/VE.lean").read_text().splitlines()
    text = generator.TARGET.read_text()
    assert text.count("\n#guard expect ") == len(F.FIXTURES)
    for fixture, _, question, _ in F.FIXTURES:
        assert f"-- {fixture}\n#guard expect " in text


def test_the_contract_files_are_the_services():
    """The relay's contract and the Lean lock are generated: from the service's export and the sources."""
    for tool in ("tools/question_codes.py", "tools/question_lock.py"):
        args = ["--check"] if tool.endswith("codes.py") else []
        done = subprocess.run([sys.executable, str(ROOT / tool), *args], cwd=ROOT, capture_output=True, text=True,
                              timeout=HANG_TIMEOUT)
        assert done.returncode == 0, (tool, done.stdout, done.stderr)


def test_every_approved_statement_is_proved_as_written():
    """Spec 5.1's fifteen Q1 statements are Lean theorems whose text is the approved text
    (tools/question_statements.py); `lean/audit.py` checks that they use the standard axioms only."""
    done = subprocess.run([sys.executable, str(ROOT / "tools/question_statements.py")], cwd=ROOT,
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert done.returncode == 0, done.stdout
    assert "15 of 15 implemented; 0 missing" in done.stdout
    audited = (ROOT / "lean/VE/Audit.lean").read_text()
    for name in re.findall(r"^theorem (\w+)", SPEC.read_text().split("### 5.1 Q1", 1)[1].split("### 5.2", 1)[0],
                           re.M):
        assert f"#print axioms VE.Question.{name}\n" in audited, name


# ------------------------------------------------------------------ the table against the service

@pytest.mark.parametrize("fixture,frame,question,answer", F.FIXTURES, ids=IDS)
def test_the_service_answers_the_fixture_table(fixture, frame, question, answer):
    result = live(frame, question)
    assert F.answer_of(result) == answer
    if "witnesses" in result:
        assert english_lean._trees(result["witnesses"], 2)


@pytest.mark.parametrize("fixture,frame,question,answer", DOCUMENT_ROWS, ids=[r[0] for r in DOCUMENT_ROWS])
def test_one_entry_point_gives_the_same_verdict(fixture, frame, question, answer):
    """`ve.ask.read` (the CLI's one entry point) and the relay give the service's answer: `one` returned, any other
    status raised as the class Lean names with Lean's text, its answer riding along."""
    raw = (ROOT / F.DOCUMENTS[frame]).read_bytes()
    env = ask.environment(raw)
    words = EnglishVocabulary(env, _defer_overlay_refusals=True)
    for call in (lambda: ask.read(raw, question), lambda: english_lean.read_question(env, question, words, {})):
        if answer["status"] == "one":
            assert F.answer_of(call()) == answer
            continue
        with pytest.raises((VEError, CheckerUnavailable)) as caught:
            call()
        assert type(caught.value).__name__ == answer["class"]
        assert F.answer_of(caught.value.lean_question) == answer
        assert str(caught.value).startswith(answer["text"])


# ------------------------------------------------------------------ the CLI

ENV_ALLOW = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "PYTHONPATH", "PYTHONNOUSERSITE", "PYTHONPYCACHEPREFIX")


def cli(*args):
    env = {k: v for k, v in os.environ.items() if k in ENV_ALLOW or k.startswith("VE_")}
    return subprocess.run([sys.executable, "-m", "ve", "ask", *map(str, args)], cwd=ROOT, env=env,
                          text=True, capture_output=True, timeout=HANG_TIMEOUT)


def exit_code(answer: dict) -> int:
    if answer["status"] == "one":
        return 0
    return {"ResourceLimit": 4, "CheckerUnavailable": 5}.get(answer["class"], 2)


@pytest.mark.parametrize("fixture,frame,question,answer", DOCUMENT_ROWS, ids=[r[0] for r in DOCUMENT_ROWS])
def test_the_cli_prints_leans_words_with_its_exit_code(fixture, frame, question, answer):
    done = cli(ROOT / F.DOCUMENTS[frame], question, "--reading")
    assert done.returncode == exit_code(answer), (done.stdout, done.stderr)
    text = answer["text"] if "advice" not in answer else f'{answer["text"]} {answer["advice"]["text"]}'
    assert done.stdout.splitlines() == [text, *answer.get("rephrasings", ())]


@pytest.mark.parametrize("fixture", ["G1", "G5", "G20"])
def test_the_cli_json_is_leans_result_with_the_honesty_fields(fixture):
    _, frame, question, answer = next(row for row in F.FIXTURES if row[0] == fixture)
    done = cli(ROOT / F.DOCUMENTS[frame], question, "--reading", "--json")
    assert done.returncode == exit_code(answer)
    record = json.loads(done.stdout)
    assert {k: record[k] for k in ("operation", "assurance", "intent", "proof", "answer")} == {
        "operation": "question.read", "assurance": "experimental", "intent": "unconfirmed",
        "proof": "not_checked", "answer": "not_built"}
    assert F.answer_of(record["result"]) == answer
    assert record["result"]["identities"]["question_version"] == english_lean.QUESTION_VERSION


def test_the_cli_does_not_answer_without_reading():
    """The answer itself is plan Q2: `ve ask` without `--reading` reads the question, prints Lean's A0 line and then
    Lean's own text that VE does not answer yet (the contract's `unanswered`, exported by the mode), and exits 5:
    never a verdict, never a silent exit (DRI ruling of 2026-10-09)."""
    unanswered = english_lean.QUESTION_TEXTS["unanswered"]
    assert unanswered == live_texts()["unanswered"]
    done = cli(ROOT / F.DOCUMENTS["G"], "Is every member eligible?")
    assert done.returncode == 5, done
    assert done.stdout.splitlines() == ["You asked whether every member is eligible.", unanswered], done
    as_json = json.loads(cli(ROOT / F.DOCUMENTS["G"], "Is every member eligible?", "--json").stdout)
    assert as_json["error"] == {"class": "CheckerUnavailable", "message": unanswered}
    assert as_json["result"]["status"] == "one" and as_json["answer"] == "not_built"
    # A question that is not read is refused as with --reading: Lean's refusal, its exit code.
    refused = cli(ROOT / F.DOCUMENTS["G"], "Who is eligible?")
    assert refused.returncode == 2 and unanswered not in refused.stdout


def live_texts() -> dict:
    row = relay.decide_once(MODE, {"id": MODE, "export": "codes"})
    assert row.get("status") == "ok", row
    return dict(row["result"]["texts"])


def test_a_gated_environment_never_returns_a_reading():
    """Review B1 (Fable): under an environment the core checker refuses as a whole (`ve-units@1`), every relay path
    that hands back a Lean reading raises the gate's refusal; `read_question` returned the unchecked formula. Each
    path is listed here, so a new one must be added: english.read's reading, and the question reader, which
    `ve.ask.read` and the CLI call."""
    from conformance import english_lean_s3_fixtures as X
    from ve import Environment
    from ve.errors import UnsupportedProfile
    env = Environment(X.FR_UNITS())
    assert env.unit_schema is not None
    words = EnglishVocabulary(env, _defer_overlay_refusals=True)
    with pytest.raises(UnsupportedProfile) as raised:
        english_lean.read_question(env, 'Is wait classified as "safe"?', words, {})
    assert not hasattr(raised.value, "lean_question")
    with pytest.raises(UnsupportedProfile):
        english_lean.read(env, 'Wait is classified as "safe".', words, {}).document()
    # Lean read the question: only the gate stands between it and the caller.
    case = english_lean.request(env, 'Is wait classified as "safe"?', words, {})
    case.update(id=MODE, question='Is wait classified as "safe"?')
    assert relay.decide_once(MODE, case)["result"]["status"] == "one"


def test_the_cli_refuses_a_document_it_cannot_load(tmp_path):
    missing = cli(tmp_path / "missing.ve.md", "Is every member eligible?", "--reading")
    assert missing.returncode == 2 and missing.stdout == ""
    (tmp_path / "plain.ve.md").write_text("Every member is eligible.\n")
    plain = cli(tmp_path / "plain.ve.md", "Is every member eligible?", "--reading", "--json")
    assert plain.returncode == 2 and json.loads(plain.stdout)["error"]["class"] == "VEError"


# ------------------------------------------------------------------ untrusted answers

def _genuine(fixture: str):
    _, frame, question, _ = next(row for row in F.FIXTURES if row[0] == fixture)
    env = F.environment(frame)
    words = EnglishVocabulary(env, _defer_overlay_refusals=True)
    return env, words, question, live(frame, question)


GENUINE = ["G1", "G5", "G9", "G14", "G15", "G20", "G22", "A9", "U8"]
REPLACEMENTS = [None, 7, True, "", [], {}, "x", -1, 1.5]


def _mutants(response: dict):
    """Each field dropped or replaced by another JSON kind, each identity changed, a field added. Not mutated: an
    optional field dropped, and the text replaced by another non-empty string: both are Lean's to choose, and the
    relay relays them (the contract cannot tell them from Lean's own)."""
    optional = english_lean.QUESTION_FIELDS[response["status"]][1]
    for key in response:
        if key not in optional:
            yield f"drop {key}", {k: v for k, v in response.items() if k != key}
        for value in REPLACEMENTS:
            if key == "text" and type(value) is str and value:
                continue
            if value != response[key] or type(value) is not type(response[key]):
                yield f"{key}={value!r}", {**response, key: value}
    for key in response["identities"]:
        yield f"identity {key}", {**response, "identities": {**response["identities"], key: "0" * 64}}
        yield f"identity {key} dropped", {**response, "identities": {
            k: v for k, v in response["identities"].items() if k != key}}
    yield "extra field", {**response, "extra": 1}
    yield "extra identity", {**response, "identities": {**response["identities"], "extra": "x"}}


@pytest.mark.parametrize("fixture", GENUINE)
def test_every_mutation_of_a_genuine_answer_is_refused(fixture, monkeypatch):
    """The relay takes no answer but Lean's: dropping, emptying, retyping (bool for int included) or changing any
    field of a genuine answer, or any identity, is CheckerUnavailable, never a verdict or a refusal."""
    env, words, question, genuine = _genuine(fixture)
    monkeypatch.setattr(english_lean, "QUESTION_TRANSPORT", lambda case: genuine)
    try:
        assert english_lean.read_question(env, question, words, {})["status"] == "one"
    except (VEError, CheckerUnavailable) as exc:
        assert not str(exc).startswith("CheckerUnavailable: the Lean question reader's answer is malformed")
    seen = 0
    for name, mutant in _mutants(genuine):
        monkeypatch.setattr(english_lean, "QUESTION_TRANSPORT", lambda case, m=mutant: copy.deepcopy(m))
        with pytest.raises(CheckerUnavailable, match="malformed"):
            english_lean.read_question(env, question, words, {})
        seen += 1
    assert seen > 20


@pytest.mark.parametrize("change", [
    lambda r: r.update(status="one"),
    lambda r: r.update(code="Budget"),
    lambda r: r.update(span=[0, 10_000]),
    lambda r: r.update(span=[5, 2]),
    lambda r: r.update(rephrasings=["Is every member eligible?", "Is every member eligible?"]),
    lambda r: r.update(rephrasings=["Every member is eligible."]),
    lambda r: r.update(advice={"id": "x"}),
    lambda r: r.update(text=r["text"] + " "),
    lambda r: r.update(span=[False, r["span"][1]]),
    lambda r: r.update(span=[0, True]),
    lambda r: r.update(span=[0.0, r["span"][1]]),
], ids=["status", "code", "span-out", "span-reversed", "rephrasing-twice", "rephrasing-not-question",
        "advice", "text-not-checked", "span-bool-start", "span-bool-stop", "span-float"])
def test_answer_mutations_inside_their_kinds(change, monkeypatch):
    """Mutations that keep each field's JSON kind: only those the contract can see are refused; a changed text is
    Lean's to write (it is relayed, never re-derived), so it passes and is printed as Lean wrote it."""
    env, words, question, genuine = _genuine("G5")
    mutant = copy.deepcopy(genuine)
    change(mutant)
    monkeypatch.setattr(english_lean, "QUESTION_TRANSPORT", lambda case: copy.deepcopy(mutant))
    if mutant["text"] != genuine["text"]:
        with pytest.raises(VEError) as caught:
            english_lean.read_question(env, question, words, {})
        assert str(caught.value) == mutant["text"]
        return
    with pytest.raises(CheckerUnavailable, match="malformed"):
        english_lean.read_question(env, question, words, {})


def test_the_question_request_binds_the_answer():
    """The request is english.read's for the question, plus the question; the answer's identities are the
    request's six and the contract's version."""
    env, words, question, genuine = _genuine("G1")
    case = F.request("G", question)
    assert case == {**english_lean.request(env, question, words, {}), "id": MODE, "question": question}
    assert genuine["identities"] == {**english_lean.identities(env, question, words, case["lexicon"]),
                                     "question_version": english_lean.QUESTION_VERSION}


# ------------------------------------------------------------------ malformed cases

def _nodes(value, path=()):
    yield path
    if type(value) is dict:
        for key, item in value.items():
            yield from _nodes(item, (*path, key))
    elif type(value) is list:
        for index, item in enumerate(value[:3]):
            yield from _nodes(item, (*path, index))


def _replace(value, path, new):
    if not path:
        return new
    out = copy.deepcopy(value)
    target = out
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = new
    return out


def _deep(depth: int) -> list:
    value: list = []
    for _ in range(depth - 1):
        value = [value]
    return value


DEEP = _deep(10_000)


def test_malformed_cases_are_error_rows_only():
    """Each node of a genuine case replaced by 7, true, null, [], {} or a 10k-deep array: the mode answers an error
    row, or (where the node is data the reader may accept, such as a description) a result whose identities are
    still the case's; it never crashes and never answers for another request."""
    case = F.request("G", "Is every member eligible?")
    cases, paths = [], []
    for path in _nodes(case):
        if path and path[0] == "environment" and len(path) > 4:
            continue
        for new in (7, True, [], {}):
            cases.append(_replace(case, path, new))
            paths.append((path, new))
        # A null is outside the service's restricted JSON: the request is refused whole, as VEError only.
        with pytest.raises(VEError, match="restricted JSON"):
            relay.rows(MODE, [_replace(case, path, None)])
        # Deeper than the JSON readers allow: a ResourceLimit (a VEError), never another exception.
        try:
            [row] = relay.rows(MODE, [_replace(case, path, DEEP)])
        except ResourceLimit:
            continue
        assert row["status"] == "error", (path, row)
    rows = relay.rows(MODE, cases)
    assert len(rows) == len(cases)
    for (path, new), mutant, row in zip(paths, cases, rows):
        assert row.get("status") in ("ok", "error"), (path, new, row)
        if row["status"] == "error":
            assert type(row.get("error")) is str and row["error"], (path, new)
        else:
            # Accepted only where the changed node does not reach the reader: never the question or its frame.
            assert path and path[0] in ("environment", "lexicon"), (path, new, row)
    assert sum(row["status"] == "error" for row in rows) > len(rows) // 2


@pytest.mark.parametrize("change,message", [
    (lambda c: c.update(source="Is Ann eligible?"), "the source is not the question"),
    (lambda c: c.update(mode="translation"), "authoring mode"),
    (lambda c: c.update(cap=3), "cap 2"),
    (lambda c: c.pop("question"), "fields do not match"),
    (lambda c: c.update(extra=1), "fields do not match"),
    (lambda c: c.update(question=7), ""),
])
def test_a_case_that_does_not_bind_its_question_is_refused(change, message):
    case = F.request("G", "Is every member eligible?")
    change(case)
    [row] = relay.rows(MODE, [case])
    assert row["status"] == "error" and message in row["error"], row


def test_the_export_case_is_exact():
    rows = relay.rows(MODE, [{"id": "x", "export": "tables"}, {"id": "x", "export": "codes", "more": 1},
                             {"id": "x", "export": "codes"}])
    assert [row["status"] for row in rows] == ["error", "error", "ok"]


# ------------------------------------------------------------------ text variants

VARIANTS = {"nbsp": "Is every member eligible?", "double space": "Is every  member eligible?",
            "tab": "Is every\tmember eligible?", "carriage return": "Is every member eligible?\r",
            "curly quotes": "Is “ann” eligible?", "kelvin sign": "Is every Kember eligible?",
            "dotted I": "İs every member eligible?", "control": "Is every member\u0007 eligible?",
            "leading space": " Is every member eligible?", "lower case": "is every member eligible?",
            "fullwidth question mark": "Is every member eligible？"}


@pytest.mark.parametrize("name", VARIANTS)
def test_text_variants_get_well_formed_answers(name):
    """The question's text is normalised by one function, E2's lexer, on every path: each variant gets a
    well-formed answer (the relay checks it), and no variant reads as a sentence with other words."""
    question = VARIANTS[name]
    env = F.environment("G")
    words = EnglishVocabulary(env, _defer_overlay_refusals=True)
    raw = (ROOT / F.DOCUMENTS["G"]).read_bytes()
    answers = []
    for call in (lambda: english_lean.read_question(env, question, words, {}), lambda: ask.read(raw, question)):
        try:
            answers.append(call())
        except CheckerUnavailable:
            raise
        except VEError as exc:
            answers.append(exc.lean_question)
    # The relay and the one entry point give the same answer.
    assert answers[0] == answers[1]
    answer = answers[0]
    if answer["status"] == "one":
        assert sorted(answer["sentence"].replace(".", "").lower().split()) == \
            sorted(question.rstrip("?").lower().split())


# ------------------------------------------------------------------ the whole operation's deadline

def test_the_whole_question_is_bounded_by_the_modes_deadline(monkeypatch):
    """The CPU deadline of `english.question` bounds the whole service operation (decoding, the lexicon's
    checks, every candidate's reading and the answer): with the deadline injected near zero, a question that
    needs work is CheckerUnavailable naming the mode, never a verdict, a refusal or ResourceLimit."""
    from ve.backends import lean_service
    monkeypatch.setitem(lean_service.DEADLINES, MODE, (1e-6, 1e-6))
    _, frame, question, _ = next(row for row in F.FIXTURES if row[0] == "U2")
    env = F.environment(frame)
    words = EnglishVocabulary(env, _defer_overlay_refusals=True)
    # A question no earlier request asked, so the relay's answer memo cannot hold it.
    question = question.replace("merit?", "merit ?").replace(" ?", "?") + ""
    case = F.request(frame, question)
    case["question"] = case["source"] = question[:-1] + " ?"
    with pytest.raises(CheckerUnavailable, match=f"mode {MODE} used more than its deadline") as caught:
        relay.decide(MODE, [case])
    assert not isinstance(caught.value, ResourceLimit)
