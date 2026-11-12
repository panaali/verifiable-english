"""The `english.statement` shadow comparator (docs/spec/en-e3-norm.md 2.4, Shadow; fixtures E14 and P5).

Each record of the shadow has exactly one class, from Python's outcome and Lean's checked answer; `lean-unavailable`
is tested first (verifier 3). The shadow runs only with `VE_STATEMENT_COMPARATOR=1` and `VE_SHADOW_LOG` both set. The
relay that feeds it (`parse_english`'s W1 path) and the saved delta report (`docs/en-e3-norm/en-2/`) are en-e3bb's.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

import pytest

from tests.test_norms import environment, permission
from ve.english_grammar import codes, statement_codes
from ve.errors import CheckerUnavailable, SyntaxError
from ve.norm_english import parse_english, statement_class, statement_record, statement_shadow_log

NODE = {"name": "rule-1", "predicate": "in_scope", "sign": True, "guard": ["unary", "publicly_deployed", ["var", 0]],
        "unless": [], "over": []}


def refusal(status: str, code: str) -> dict:
    return {"status": status, "code": code, "text": "t", "class": codes()[0][code], "identities": {}}


def one(*nodes: dict) -> dict:
    return {"status": "one", "identities": {}, "statements": [
        {"kind": "rule", "number": i, "exception_to": [], "node": {"norm": node}, "span": [0, 1]}
        for i, node in enumerate(nodes, 1)]}


# E14's Lean answers by the class each takes when Python admits (section 8, from E1, E3, E6, E9, E11, E12, E16).
UNAVAILABLE = [refusal("rejected", "Internal"), refusal("invalidGrammar", "InvalidGrammar"),
               CheckerUnavailable("CheckerUnavailable: the answer is not bound to the request")]
UNKNOWN = [refusal("budget", "Budget"), refusal("rejected", "NodeLimit")]
STRICTER = [refusal("rejected", "NodeRefused"), refusal("rejected", "StrayConsequence"),
            refusal("none", "NoDerivation"), refusal("unformalised", "UnformalisedSpan"),
            refusal("invalidGrammar", "InvalidOverlay"), refusal("many", "Ambiguous")]
REFUSED = SyntaxError("Expected Rule 1 with its own block")


@pytest.mark.parametrize("lean", UNAVAILABLE, ids=repr)
def test_an_unavailable_answer_is_a_delta_row_whatever_python_did(lean):
    """verifier 3: a `CheckerUnavailable` answer (a relay failure, or a code of that class) is `lean-unavailable`
    when Python admits and when it refuses, never `both-refuse` or `lean-stricter`."""
    assert statement_class([NODE], lean) == statement_class(REFUSED, lean) == "lean-unavailable"


@pytest.mark.parametrize("lean", UNKNOWN + STRICTER, ids=repr)
def test_a_lean_refusal_is_classed_by_python_outcome(lean):
    """Python admits: a budget or ResourceLimit answer is `lean-unknown` (not a rejection), any other refusal
    `lean-stricter`; Python refuses: `both-refuse`, UNKNOWN included."""
    assert statement_class([NODE], lean) == ("lean-unknown" if lean in UNKNOWN else "lean-stricter")
    assert statement_class(REFUSED, lean) == "both-refuse"


def test_a_lean_reading_is_compared_by_position():
    """E1's `one`: `agree` when the nodes are equal after both sides name rule i `rule-i` (Python's names follow
    `existing_names`), `different-node` when they differ, `lean-looser` when Python refuses."""
    second = {**NODE, "name": "rule-2", "over": ["rule-1"]}
    renamed = [{**NODE, "name": "rule-7"}, {**second, "name": "rule-8", "over": ["rule-7"]}]
    assert statement_class(renamed, one(NODE, second)) == "agree"
    assert statement_class([NODE, {**second, "over": []}], one(NODE, second)) == "different-node"
    assert statement_class([{**NODE, "sign": False}], one(NODE)) == "different-node"
    assert statement_class([{**NODE, "sign": 1}], one(NODE)) == "different-node"  # JSON's true is not 1
    assert statement_class([NODE], one(NODE, second)) == "different-node"
    assert statement_class(REFUSED, one(NODE)) == "lean-looser"


def test_only_a_checked_answer_or_unavailability_is_classed():
    with pytest.raises(TypeError):
        statement_class([NODE], SyntaxError("InvalidInput: the lexicon names another environment"))


def test_a_record_holds_both_outcomes_and_one_class():
    record = statement_record("Rule 1. X.", REFUSED, refusal("rejected", "NodeRefused"))
    assert record == {"source_sha256": "b9f1e10dd9b146f928cd661dd716561decb1c7b41a7cf58e9680e90ff3ce94e1",
                      "python": {"class": "SyntaxError", "message": str(REFUSED)},
                      "lean": {"status": "rejected", "code": "NodeRefused", "nodes": []}, "class": "both-refuse"}
    assert statement_record("Rule 1. X.", [NODE], one(NODE))["lean"]["nodes"] == [NODE]
    assert statement_record("", [NODE], UNAVAILABLE[2])["lean"] == {"status": "unavailable",
                                                                    "message": str(UNAVAILABLE[2])}


def test_the_shadow_needs_both_flags(monkeypatch, tmp_path):
    """P5: with `VE_STATEMENT_COMPARATOR=1` and `VE_SHADOW_LOG` unset, Lean is not called and no file is written in
    the working directory; the log is the path `VE_SHADOW_LOG` names only when both are set (the W1 path's call
    through the relay, en-e3bb's, is `test_the_shadow_asks_lean_and_keeps_python_s_answer`)."""
    from ve.backends import relay
    from ve.backends.lean_service import LeanService
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VE_STATEMENT_COMPARATOR", "1")
    monkeypatch.delenv("VE_SHADOW_LOG", raising=False)
    modes = []
    original = LeanService._run_chunk

    def run_chunk(self, mode, *args, **kwargs):  # every batch of the service passes here (relay, pools, answer)
        modes.append(mode)
        return original(self, mode, *args, **kwargs)
    monkeypatch.setattr(LeanService, "_run_chunk", run_chunk)
    env = environment({"permitted": permission()})
    assert statement_shadow_log() is None
    document = parse_english(env, "Rule 1. Every act may be done.")
    assert [rule.name for rule in document.rules] == ["rule-1"]
    assert "english.statement" not in modes and list(tmp_path.iterdir()) == []
    relay.answer("english.statement", {"id": "spy", "kind": "blocks"})  # the spy sees the relay's answer path
    assert modes[-1] == "english.statement"
    monkeypatch.setenv("VE_SHADOW_LOG", str(tmp_path / "shadow.jsonl"))
    assert statement_shadow_log() == tmp_path / "shadow.jsonl"
    monkeypatch.setenv("VE_STATEMENT_COMPARATOR", "0")
    assert statement_shadow_log() is None


def test_the_statement_tables_are_the_lean_export():
    """`statement_codes()` reads english.statement's tables from codes.json: the field table has exactly the code
    table's statuses (`Run.statementFields_statuses`), every EN-2 code is classed (the render codes are EN-3's
    rows), and a rejection's optional members are `sentence` and `span`."""
    statuses, fields, unsentenced = statement_codes()
    classes = codes()[0]
    assert list(fields) == list(statuses) and "rendered" in statuses
    assert {code for found in statuses.values() for code in found} - set(classes) == {
        "RenderUnread", "RenderMismatch", "NoWording", "InvalidInput"}
    assert fields["rejected"] == (("code", "text", "class"), ("sentence", "span"))
    assert fields["one"] == (("statements",), ()) and "NodeRefused" in unsentenced


# en-e3bb: the relay that feeds the shadow, and the saved delta report (spec 2.4, Delta report; DRI 2026-11-02 item 2).
DELTA = Path(__file__).resolve().parents[1] / "docs/en-e3-norm/en-2"
CLASSES = ("lean-unavailable", "agree", "lean-unknown", "lean-stricter", "lean-looser", "different-node", "both-refuse")


def delta_rows(markdown: str) -> set[tuple[str, str, str]]:
    """DELTA.md's rows as (corpus, id, class), from its tables."""
    return {(m[1], m[2], m[3]) for m in re.finditer(r"^\| ([a-z-]+) \| `([^`]+)` \| ([a-z-]+) \|", markdown, re.M)}


def check_delta(delta: dict, markdown: str, pinned: list[str]) -> None:
    """Every corpus's per-class counts sum to its size; every record has one class of the table; every row of a
    class other than `agree` and `both-refuse` (or answered `NodeRefused`/`NodeLimit`) is a DELTA.md row with its
    class, and the `lean-unavailable` rows are listed by id; each pinned block is recorded once, and its class is
    `agree` or a DELTA.md row with that class."""
    for corpus in delta["corpora"]:
        counts = delta["counts"][corpus["name"]]
        assert set(counts) == set(CLASSES) and sum(counts.values()) == corpus["size"], corpus
    rows, table = delta["rows"], delta_rows(markdown)
    assert all(r["class"] in CLASSES for r in rows)
    assert {(r["corpus"], r["id"], r["class"]) for r in rows} == table
    assert all(r["class"] not in ("agree", "both-refuse") or r["lean"].get("code") in ("NodeRefused", "NodeLimit")
               for r in rows)
    assert sorted(delta["lean_unavailable"]) == sorted(r["id"] for r in rows if r["class"] == "lean-unavailable")
    for corpus in delta["corpora"]:
        listed = sum(r["corpus"] == corpus["name"] and r["class"] not in ("agree", "both-refuse") for r in rows)
        assert listed == corpus["size"] - delta["counts"][corpus["name"]]["agree"] \
            - delta["counts"][corpus["name"]]["both-refuse"], corpus
    assert sorted(delta["pinned"]) == sorted(pinned)
    assert all(found == "agree" or ("pinned", ident, found) in table for ident, found in delta["pinned"].items())
    assert "| lean-unavailable | unavailable |" not in markdown  # each refused request's cause is named (F2)
    check_suite(delta)


# The 10 test files review F1 (en-e3bb-review.final.md) found calling `parse_english` outside the hand-kept list.
REVIEW_F1 = ("agent_policy_rerun", "agent_policy_unspecified", "et8_completion", "natural", "pf_fidelity_fix",
             "question_fixture_sources", "rsp_fidelity_fix", "safety_framework", "safetyfw_usecases",
             "wire_gate_corpus")


def check_suite(delta: dict) -> None:
    """The suite corpus is its derivation (`w1_delta.derive_suite`): the units a map records calling
    `parse_english`, then the units it cannot rule out, disjoint and in order; the 10 files review F1 found are among
    them, and every suite and soft-rights record comes from one of them (a record's id is its test)."""
    suite = delta["suite"]
    assert suite["function"] == "ve/norm_english.py:parse_english" and suite["map"]
    assert suite["files"] == sorted(suite["reached"] + suite["unknown"]) and not set(suite["reached"]) & set(
        suite["unknown"]), suite
    assert {f"tests/test_{name}.py" for name in REVIEW_F1} <= set(suite["files"])
    assert re.fullmatch(r"\d+ passed(, \d+ [a-z]+)*", suite["result"]), suite["result"]
    tested = {r["id"].split("::")[0] for r in delta["rows"] if r["corpus"] in ("suite", "soft-rights")}
    assert tested <= set(suite["files"]), tested - set(suite["files"])


def test_the_suite_check_fails_on_a_hand_kept_or_incomplete_suite():
    """The other direction: the saved suite with a file review F1 found dropped, a record from a test outside it, a
    `files` that is not its derivation, or no pytest summary each fail `check_suite`."""
    delta = json.loads((DELTA / "delta.json").read_text())
    suite = delta["suite"]
    dropped = [f for f in suite["files"] if f != "tests/test_safety_framework.py"]
    row = next(r for r in delta["rows"] if r["corpus"] == "suite")
    for broken in ({**delta, "suite": {**suite, "files": dropped,
                                        "unknown": [f for f in suite["unknown"] if f in dropped],
                                        "reached": [f for f in suite["reached"] if f in dropped]}},
                   {**delta, "rows": [{**row, "id": "tests/test_elsewhere.py::test_x"}, *delta["rows"]]},
                   {**delta, "suite": {**suite, "files": suite["files"][1:]}},
                   {**delta, "suite": {**suite, "result": "no pytest summary (exit 2)"}}):
        with pytest.raises(AssertionError):
            check_suite(broken)


REPORT = DELTA.parent / "en-2c/REPORT.md"


def check_report(report: str, delta: dict) -> None:
    """F2: every number and cause the REPORT gives for the delta is the saved evidence's. Its corpus table gives each
    corpus's records and per-class counts (a class it leaves out is 0) and the suite's unit count; each cause line
    (`` - `corpus` `class` (n): `Lean's answer` ``) is that many rows of `delta.json` with Lean's answer beginning so,
    and every corpus and class with rows has its line; and no sentence says every record of a corpus has a class that
    only some of its records have."""
    counts, sizes = delta["counts"], {c["name"]: c["size"] for c in delta["corpora"]}
    header = next(line for line in report.splitlines() if line.startswith("| corpus | records |"))
    columns = [cell.strip() for cell in header.strip("|").split("|")][2:]
    seen = set()
    for line in report.splitlines():
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        name = cells[0].split(" ")[0] if line.startswith("| ") else None
        if name in sizes and len(cells) == len(columns) + 2:
            seen.add(name)
            assert int(cells[1]) == sizes[name], line
            assert all(int(n) == counts[name][k] for k, n in zip(columns, cells[2:])), line
            assert all(counts[name][k] == 0 for k in counts[name] if k not in columns), line
            if name == "suite":
                assert f"({len(delta['suite']['files'])} test units" in cells[0], line
    assert seen == set(sizes), seen
    causes = {}
    for r in delta["rows"]:
        lean = r["lean"]
        cause = lean["message"] if lean["status"] == "unavailable" else lean.get("code") or lean["status"]
        causes.setdefault((r["corpus"], r["class"]), []).append(cause)
    stated: dict = {}
    for m in re.finditer(r"^- `([a-z-]+)` `([a-z-]+)` \((\d+)\): `([^`]+)`", report, re.M):
        corpus, cls, n, lean = m[1], m[2], int(m[3]), m[4]
        assert sum(c.startswith(lean) for c in causes.get((corpus, cls), ())) == n, m[0]
        stated[(corpus, cls)] = stated.get((corpus, cls), 0) + n
    assert stated == {group: len(found) for group, found in causes.items()}, (stated, causes.keys())
    for corpus in sizes:
        for m in re.finditer(rf"every {re.escape(corpus)}\b[^.]*?`([a-z-]+)`", report):
            assert m[1] in counts[corpus] and counts[corpus][m[1]] == sizes[corpus], m[0]


def test_the_report_s_delta_numbers_and_causes_are_the_saved_evidence():
    """F2 (en-e3bb-review.final.md): the REPORT said every soft-rights W1 call is `lean-unavailable`, though 23 of
    them are answered. It reads the saved `delta.json` and the REPORT only."""
    check_report(REPORT.read_text(), json.loads((DELTA / "delta.json").read_text()))


def test_the_report_check_fails_on_review_f2_s_overclaim_and_on_a_wrong_number():
    """The other direction: review F2's sentence, a corpus count off by one, a cause line with a wrong count or a
    wrong cause, and a missing cause line each fail `check_report`."""
    report, delta = REPORT.read_text(), json.loads((DELTA / "delta.json").read_text())
    overclaim = report + "\nSo every soft-rights W1 call and every constitution unit is `lean-unavailable`.\n"
    line = next(m for m in re.finditer(r"^- `[a-z-]+` `[a-z-]+` \((\d+)\): `([^`]+)`.*$", report, re.M))
    pinned = next(m for m in re.finditer(r"^\| pinned [^|]*\| (\d+) \|", report, re.M))
    for broken in (overclaim,
                   report.replace(pinned[0], pinned[0].replace(f"| {pinned[1]} |", f"| {int(pinned[1]) + 1} |")),
                   report.replace(line[0], line[0].replace(f"({line[1]})", f"({int(line[1]) + 1})")),
                   report.replace(line[0], line[0].replace(f"`{line[2]}`", "`NodeLimit`")),
                   report.replace(line[0] + "\n", "")):
        with pytest.raises(AssertionError):
            check_report(broken, delta)


def pinned_ids() -> list[str]:
    root = DELTA.parents[2] / "tests/data/norm-blocks"
    return [f"{name}/{json.loads(line)['id']}" for name in ("rsp", "fsf")
            for line in (root / f"{name}.jsonl").read_text().splitlines()]


def test_the_saved_delta_report_records_every_disagreement_with_its_class():
    """The shadow agreement test (spec 2.4): it reads the saved `delta.json` and DELTA.md only."""
    check_delta(json.loads((DELTA / "delta.json").read_text()), (DELTA / "DELTA.md").read_text(), pinned_ids())


def test_the_delta_check_fails_on_an_unlisted_or_misclassed_disagreement():
    """The other direction: a pinned block recorded as a disagreement that DELTA.md does not list, a row listed
    under another class, a missing block, or counts that do not sum to the corpus each fail the check."""
    delta, markdown = json.loads((DELTA / "delta.json").read_text()), (DELTA / "DELTA.md").read_text()
    ident = pinned_ids()[0]
    for broken in ({**delta, "pinned": {**delta["pinned"], ident: "lean-stricter"}},
                   {**delta, "pinned": {k: v for k, v in delta["pinned"].items() if k != ident}},
                   {**delta, "rows": [{**delta["rows"][0], "class": "different-node"}, *delta["rows"][1:]]},
                   {**delta, "counts": {**delta["counts"], "pinned": {**delta["counts"]["pinned"], "agree": 119}}}):
        with pytest.raises(AssertionError):
            check_delta(broken, markdown, pinned_ids())


def test_the_shadow_asks_lean_and_keeps_python_s_answer(monkeypatch, tmp_path):
    """With both flags set, the W1 path asks `english.statement` once per call and appends one record to the log
    `VE_SHADOW_LOG` names: Python's document is returned as without the shadow, Python's refusal is raised as it
    stands, and a Lean that cannot answer is a `lean-unavailable` record, never a changed answer."""
    from ve.backends import relay
    monkeypatch.chdir(tmp_path)
    env = environment({"permitted": permission()})
    text = "Rule 1. Every act may be done."
    plain = parse_english(env, text)
    log = tmp_path / "shadow.jsonl"
    monkeypatch.setenv("VE_STATEMENT_COMPARATOR", "1")
    monkeypatch.setenv("VE_SHADOW_LOG", str(log))
    assert parse_english(env, text).document_hash == plain.document_hash
    with pytest.raises(SyntaxError, match="Expected Rule 1 with its own block"):
        parse_english(env, "Rule 1.\nEvery act may be done.")

    real = relay.decide

    def unreachable(mode, cases, **kwargs):  # Python's own reader asks other modes through the same relay
        if mode == "english.statement":
            raise CheckerUnavailable("CheckerUnavailable: the Lean service is not running")
        return real(mode, cases, **kwargs)
    monkeypatch.setattr(relay, "decide", unreachable)
    assert parse_english(env, text).document_hash == plain.document_hash
    records = [json.loads(line) for line in log.read_text().splitlines()]
    assert [r["class"] for r in records] == ["agree", "lean-looser", "lean-unavailable"]
    assert records[1]["python"]["class"] == "SyntaxError" and records[1]["lean"]["status"] == "one"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["shadow.jsonl"]
