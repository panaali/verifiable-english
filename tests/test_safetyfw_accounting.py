"""Source accounting of the safety-framework-style cases (usecases/safetyfw_accounting.py).

Each block of a case's rules.d1.ve and facts.d1.ve has one line in the case's accounting.d1.txt that says which
words of its quoted source span the rule leaves out, and why. These tests pin the tool's word tables, exercise each
check on small fixtures under tmp_path, and check both cases' sidecars in form and against their saved reports
(docs/usecases/safetyfw/<case>/accounting.json). The pinned source texts are not in the repository, so the case
tests run without `--source`: the anchoring itself is tested on fixtures.
"""
import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("safetyfw_accounting", REPO / "usecases" / "safetyfw_accounting.py")
A = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)

CASES = ("anthropic-rsp", "openai-preparedness")
# A change to either table changes every case's result: re-run both cases with --source and re-save their reports.
STOP_SHA256 = "0965966db2a91f0a0ee3f1d1488161af96d852affd6b6dea80a9e0d221e661d9"
STEMMER_SHA256 = "bf124f8977c80e2bbd62466bd79d117d29f36bf388e8f01d0ebffa1571a982c8"

ENVIRONMENT = {"vocabulary": {
    "predicates": {
        "audited": {"arguments": ["situation"], "description": "the ledger at {0} is audited by an auditor",
                    "regulated": {"role": "obligation", "default": "deny", "act": "{0} have the ledger audited"}},
        "filed": {"arguments": ["situation", "form"], "description": "the quarterly return is filed",
                  "regulated": {"role": "obligation", "default": "deny", "act": "{0} file {1} on time"}},
        "material": {"arguments": ["situation"], "description": "a material error occurs. Open term OT1, decided by "
                     "the board", "verbalisation": "{0} has a material error"},
        "minor": {"arguments": ["situation"], "description": "a minor error occurs (no decider named)"},
    },
    "constants": {"ledger_book": {"sort": "book", "description": "the general ledger of the company"}}}}

PLAN = """# Plan
## 3. Translation rules
### 3.1 Reading sets
| Id | Source unit | Readings |
|---|---|---|
| RS1 | the "should" | **strict** / **default** |
### 3.2 Open terms
## 12. Deviations
1. **First limit.** text
2. **Second limit.** text
## 13. Files
"""

SOURCE = ("Preamble text. The company will have the ledger audited every year by an independent auditor, "
          "and in addition it will keep the receipts for seven years before any disposal. Unrelated tail.")


def make_case(tmp_path, rules, facts=(), sidecar=None, plan=PLAN):
    """A case directory: blocks are (id, when, source field, VE text); sidecar lines are written as given."""
    case = tmp_path / "case"
    case.mkdir(parents=True)
    for name, blocks in (("rules.d1.ve", rules), ("facts.d1.ve", facts)):
        (case / name).write_text("".join(f"## {i} | {w} | {s}\n{t}\n" for i, w, s, t in blocks), encoding="utf-8")
    (case / "environment.d1.json").write_text(json.dumps(ENVIRONMENT), encoding="utf-8")
    (case / "PLAN.md").write_text(plan, encoding="utf-8")
    if sidecar is not None:
        (case / "accounting.d1.txt").write_text("".join(line + "\n" for line in sidecar), encoding="utf-8")
    return case


AUDIT = ("r-audit", "always", 'F1 "will have the ledger audited every year"',
         "Rule 1. Every situation must have the ledger audited.")
AUDIT_LINE = 'r-audit | omits: "every year" loss 1'


def problems(case, source=None):
    return A.account(case, source)["problems"]


# ---------------------------------------------------------------------------------------------------------------
# Word tables


def test_stop_list_and_stemmer_are_pinned():
    assert A.table_digest(sorted(A.STOP)) == STOP_SHA256
    assert A.table_digest(list(A.SUFFIXES) + [str(A.STEM_MIN)]) == STEMMER_SHA256


def test_words_are_account_py_words():
    assert A.words("The Board of Directors (Board) reviewed 30 well-founded reports") == {
        "board", "director", "review", "30", "well", "found", "report"}
    assert A.words("e.g. see section 3") == {"3"}


# ---------------------------------------------------------------------------------------------------------------
# Anchoring


def test_elided_quote_spans_the_source_between_its_fragments(tmp_path):
    quote = "have the ledger audited ... receipts for seven years"
    span = A.Source(SOURCE).anchor(quote)
    assert span == ("have the ledger audited every year by an independent auditor, and in addition it will keep the "
                    "receipts for seven years")
    rules = [("r-keep", "always", f'F2 "{quote}"', "Rule 1. Every situation must have the ledger audited.")]
    result = A.account(make_case(tmp_path, rules, sidecar=["r-keep | omits: nothing"]), SOURCE)
    assert {"independent", "keep", "addition"} <= set(result["blocks"][0]["unaccounted"])
    assert any("'independent' is in no entry" in p for p in result["problems"])


def test_elided_quote_without_the_source_is_listed_not_refused(tmp_path):
    rules = [("r-keep", "always", '"have the ledger audited ... receipts for seven years"',
              "Rule 1. Every situation must have the ledger audited.")]
    line = 'r-keep | omits: "receipts for seven years" loss 1 ; "an independent auditor" loss 1'
    result = A.account(make_case(tmp_path, rules, sidecar=[line]))
    assert result["problems"] == []
    assert result["blocks"][0]["elided_needs_source"] == ["have the ledger audited ... receipts for seven years"]
    assert result["totals"]["elided_quotes_without_source"] == 1


def test_unanchored_quotes_are_problems(tmp_path):
    for quote in ("the ledger is burned every year",  # not in the source
                  "receipts for seven years ... have the ledger audited",  # fragments out of order
                  "Preamble text ... Unrelated tail"):  # in order, but beyond the 2,500-character window
        source = SOURCE.replace("Unrelated", "x " * 1300 + "Unrelated")
        rules = [("r-x", "always", f'"{quote}"', "Rule 1. Every situation must have the ledger audited.")]
        result = A.account(make_case(tmp_path / str(len(quote)), rules, sidecar=["r-x | omits: nothing"]), source)
        assert result["totals"]["unanchored_quotes"] == 1, quote
        assert any("UNANCHORED" in p for p in result["problems"]), quote


def header_source(case, block_id):
    path = REPO / "usecases" / case / "rules.d1.ve"
    return {b["id"]: b for b in A.read_blocks(path)}[block_id]["source"]


def test_nested_quote_keeps_its_inner_words_on_the_real_header():
    """F1 (fid-account-1 review): the inner “filibuster” used to close the outer quote, so the word left the span."""
    found = A.quotes(header_source("openai-preparedness", "f16-without-noinput"))
    assert found == ["For the avoidance of doubt, OpenAI Leadership can also make decisions without the SAG's "
                     'participation, i.e., the SAG does not have the ability to "filibuster"']
    rows = {b["id"]: b for b in A.account(REPO / "usecases" / "openai-preparedness")["blocks"]}
    for block_id in ("f16-without-noinput", "f16-without-nodelib"):
        assert any("filibuster" in e["words"] for e in rows[block_id]["entries"]), block_id


def test_a_short_quote_does_not_make_the_text_between_two_quotes_a_quote():
    """The same pairing class: a straight-quote regex skipping a short quote paired its closing mark with the next
    quote's opening one (safety-framework f16-ds took ', read distributively, ... 1.3.5's ' as a quote)."""
    assert A.quotes(header_source("safety-framework", "f16-ds")) == ["otherwise assess"]


@pytest.mark.parametrize("field, expected", [
    ("“the board may “veto” any launch”", ['the board may "veto" any launch']),
    ('“the board may "veto" any launch”', ['the board may "veto" any launch']),
    ('"the board may “veto” any launch"', ['the board may "veto" any launch']),
    ('F2 "x" and "the board may veto"', ["the board may veto"]),
    ("“a “b “c”” d e f g h” then “the second quote”",
     ['a "b "c"" d e f g h', "the second quote"]),
    ("the SAG’s view, “the company’s own plan”", ["the company's own plan"]),
])
def test_quotes_pair_by_direction_and_nest(field, expected):
    assert A.scan_quotes(field) == (expected, None)


@pytest.mark.parametrize("field", [
    "“the board may veto any launch",  # never closed
    "the board may veto any launch”",  # closed, never opened
    '"the board may veto" any "launch',  # odd number of straight marks
    '“the board may "veto any launch”',  # the curly mark closes while a straight quote is open inside
    '“the board may "veto” any launch”',  # the same, with a curly mark left to close the outer quote
    "“the board may “veto any launch”",  # the inner quote is closed, the outer one never
])
def test_unpaired_quote_marks_are_problems(tmp_path, field):
    assert A.scan_quotes(field)[1] is not None
    rules = [("r-x", "always", field, "Rule 1. Every situation must have the ledger audited.")]
    found = problems(make_case(tmp_path, rules, sidecar=["r-x | omits: nothing"]))
    assert any("r-x: UNPAIRED quote marks" in p for p in found), found


def test_generated_nested_quotes_are_recovered_whole():
    """A seeded generator of fields with quotes nested up to three deep in every mark style: the scanner returns
    exactly the outermost quotes it built (those of MIN_QUOTE characters or more), in order, with no problem."""
    import random
    rng = random.Random(20261111)
    marks = (("“", "”"), ('"', '"'))
    vocabulary = "board may veto launch the plan threshold critical model safeguards report".split()

    def text():
        return " ".join(rng.choice(vocabulary) for _ in range(rng.randint(0, 4)))

    def quote(depth, outer):
        opens, closes = rng.choice([m for m in marks if not (m[0] == '"' and outer == '"')])
        inner = text()
        for _ in range(rng.randint(0, 2) if depth < 3 else 0):
            inner += " " + quote(depth + 1, opens) + " " + text()
        return opens + inner + closes

    for _ in range(2000):
        field, expected = text(), []
        for _ in range(rng.randint(0, 3)):
            q = quote(1, None)
            field += " " + q + " " + text()
            body = A.norm(q[1:-1])
            if len(body) >= A.MIN_QUOTE:
                expected.append(body)
        assert A.scan_quotes(field) == (expected, None), field


def test_anchoring_skips_layout_but_not_words():
    source = ("We will share sig- nificantly more 11 reports, Responsible Scaling Policy, Anthropic 16 with the "
              "Board within 30 days.")
    s = A.Source(source)
    assert s.anchor("share significantly more reports with the Board") == (
        "share significantly more reports with the Board")
    assert s.anchor("within 60 days") is None
    assert s.anchor("We will share reports") is None  # a skipped word is not layout


# ---------------------------------------------------------------------------------------------------------------
# Accounted words


def test_accounted_words_come_from_text_and_the_legends_it_uses(tmp_path):
    rules = [("r-file", "always", '"file the quarterly return on time"', "Rule 1. Every situation must file "
              '"ledger_book" on time, if that situation has a material error.')]
    block = A.account(make_case(tmp_path, rules, sidecar=["r-file | omits: nothing"]))["blocks"][0]
    assert block["used"] == ["filed", "ledger_book", "material"]  # act with a slot, verbalisation, constant
    assert block["unaccounted"] == []


# ---------------------------------------------------------------------------------------------------------------
# The sidecar


def test_a_complete_sidecar_passes(tmp_path):
    assert problems(make_case(tmp_path, [AUDIT], sidecar=[AUDIT_LINE]), SOURCE) == []


@pytest.mark.parametrize("lines, expected", [
    ([], "missing or empty"),
    (["r-other | omits: nothing"], "r-other: no such block"),
    (["r-audit | omits: nothing"], "'year' is in no entry"),
    ([AUDIT_LINE, AUDIT_LINE], "a second line for this block"),
    (['r-audit | omits: "every year" because'], "unreadable entry"),
    (['r-audit | omits: "every year" loss 1 ; "every year by an independent auditor" exposition'],
     "not in the source span"),
    (['r-audit | omits: "every year" loss 1 ; "every" exposition'], "has no content word"),
])
def test_sidecar_form_problems(tmp_path, lines, expected):
    found = problems(make_case(tmp_path, [AUDIT], sidecar=lines))
    assert any(expected in p for p in found), found


def test_a_missing_line_is_a_problem(tmp_path):
    second = ("r-two", "always", "F9", "Rule 1. Every situation must have the ledger audited.")
    found = problems(make_case(tmp_path, [AUDIT, second], sidecar=[AUDIT_LINE]))
    assert found == ["r-two: no sidecar line"]


def test_lines_follow_the_block_order(tmp_path):
    second = ("r-two", "always", "F9", "Rule 1. Every situation must have the ledger audited.")
    found = problems(make_case(tmp_path, [AUDIT, second], sidecar=["r-two | omits: nothing", AUDIT_LINE]))
    assert any("not in the order" in p for p in found)


KEEPER = ("r-keep", "always", '"it will keep the receipts for seven years"',
          "Rule 1. Every situation must keep the receipts for seven years.")


@pytest.mark.parametrize("entry, ok", [
    ('"audited every year" rule r-keep', False),  # r-keep exists but does not account these words
    ('"every year" rule r-none', False),
    ('"every year" rule r-audit', False),  # a block cannot carry its own omission
    ('"every year" open material', True),
    ('"every year" open minor', False),  # its description names no decider
    ('"every year" open ledger_book', False),  # a constant, not a predicate
    ('"every year" reading RS1', True),  # PLAN 3.1's table
    ('"every year" reading RSX', True),  # the block's when field (set below)
    ('"every year" reading RS9', False),
    ('"every year" loss 1', True),
    ('"every year" loss 11', True),
    ('"every year" loss 12', False),
    ('"every year" loss limit 2', True),
    ('"every year" loss limit 3', False),
    ('"every year" restates', True),
    ('"every year" exposition', True),
])
def test_reason_arguments_resolve(tmp_path, entry, ok):
    audit = (AUDIT[0], "RSX=a", AUDIT[2], AUDIT[3])
    keep_line = 'r-keep | omits: nothing'
    found = problems(make_case(tmp_path, [audit, KEEPER], sidecar=[f"r-audit | omits: {entry}", keep_line]))
    assert (found == []) is ok, found


def test_rule_reason_passes_when_the_target_accounts_the_words(tmp_path):
    audit = ("r-audit", "always", '"will have the ledger audited every year ... for seven years"',
             "Rule 1. Every situation must have the ledger audited.")
    line = ('r-audit | omits: "every year" loss 1 ; "by an independent auditor" exposition ; '
            '"and in addition" exposition ; "it will keep the receipts for seven years" rule r-keep')
    found = problems(make_case(tmp_path, [audit, KEEPER], sidecar=[line, 'r-keep | omits: nothing']),
                     SOURCE)
    assert found == []


# ---------------------------------------------------------------------------------------------------------------
# Report, score and command line


def test_report_totals_and_score(tmp_path):
    second = ("r-two", "always", "F9", "Rule 1. Every situation must have the ledger audited.")
    case = make_case(tmp_path, [AUDIT, second], sidecar=[AUDIT_LINE, "r-two | omits: nothing"])
    verdicts = tmp_path / "VERDICTS.md"
    verdicts.write_text("VERDICTS:\nr-audit UNFAITHFUL\nr-two UNFAITHFUL\nr-gone FAITHFUL\n", encoding="utf-8")
    report = tmp_path / "out" / "accounting.json"
    assert A.main([str(case), "--check", "--report", str(report), "--score", str(verdicts)]) == 0
    data = json.loads(report.read_text())
    assert data["totals"]["blocks"] == 2 and data["totals"]["losses_by_class"] == {"1": 1}
    assert data["score"]["unfaithful_with_loss"] == 1
    assert data["score"]["unfaithful_without_loss"] == ["r-two"]
    assert data["score"]["units_not_blocks"] == ["r-gone"]
    (case / "accounting.d1.txt").write_text(AUDIT_LINE + "\n", encoding="utf-8")
    assert A.main([str(case), "--check"]) == 1


def test_malformed_blocks_are_refused(tmp_path):
    case = make_case(tmp_path, [AUDIT], sidecar=[AUDIT_LINE])
    (case / "rules.d1.ve").write_text("## R_BAD | always | x\nRule 1.\n", encoding="utf-8")
    assert A.main([str(case), "--check"]) == 2


# ---------------------------------------------------------------------------------------------------------------
# The two cases


def case_blocks(case):
    return [b["id"] for name in A.BLOCK_FILES for b in A.read_blocks(REPO / "usecases" / case / name)]


@pytest.mark.parametrize("case", CASES)
def test_case_sidecar_passes_in_form(case):
    """One line per block in file order, every unaccounted word in an entry, every reason resolved (no source)."""
    result = A.account(REPO / "usecases" / case)
    assert result["problems"] == []
    lines = (REPO / "usecases" / case / "accounting.d1.txt").read_text(encoding="utf-8").splitlines()
    assert [line.split(" | ")[0] for line in lines] == case_blocks(case)


@pytest.mark.parametrize("case", CASES)
def test_saved_report_totals_are_the_sidecars(case):
    """The saved --source report (evidence) and the committed sidecar agree on blocks and losses."""
    saved = json.loads((REPO / "docs" / "usecases" / "safetyfw" / case / "accounting.json").read_text())
    now = A.account(REPO / "usecases" / case)["totals"]
    for key in ("blocks", "blocks_with_loss", "losses_by_class", "entries_by_reason"):
        assert saved["totals"][key] == now[key], key
    assert saved["totals"]["unanchored_quotes"] == 0 and saved["problems"] == []
    assert saved["source_sha256"] is not None
