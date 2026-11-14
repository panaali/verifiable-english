"""tests/omission_rule.py, the port of the installed uc-audit omission rule (omission-2), on a small synthetic case.

One scenario per record path, each with its exact expected records. The same table was run once against the installed
rule itself (docs/usecases/openai-preparedness/openai-preparedness-fidelity-fix-5/omission-differential.json): the port
and the rule agree on every scenario. openai-preparedness-fidelity-fix-5 F1: the first copy of the rule in this repo
counted only a `loss` tag as a loss, so an `exposition` or `dropped` tag passed; those scenarios are the regression.
"""

import json

import pytest

import tests.omission_rule as omission_rule

CASE = "demo"
RULES = """## u-rule | RS1=strict | Src: "a widget must be inspected when hazardous, says the shiny guide"
Rule 1. Every situation must have a widget inspected, if that situation is classified as "hazard".  # polished brightly
## u-carrier | always | Src: "the blue widget is shiny"
Rule 1. Every situation must have a blue widget polished.
"""
FACTS = """## fact-a | always | Src: "a fact"
Fact 1. Every situation is classified as "hazard".
"""
VOCABULARY = """VOCABULARY = {
    "hazard": base(["situation"], "a hazard is present at {0}"),
    "inspect": act(["situation"], "{0} have a widget inspected"),
    "polish": act(["situation"], "{0} have a blue widget polished"),
}
"""
ENVIRONMENT = {"vocabulary": {"predicates": {
    "hazard": {"verbalisation": "a hazard is present at {0}"},
    "inspect": {"regulated": {"act": "{0} have a widget inspected"}},
    "polish": {"regulated": {"act": "{0} have a blue widget polished"}}}}}
PLAN = """# Plan

u-rule is named before section 12.

## 12. Deviations

Nothing changed.

## 13. Files

u-rule is named after section 12 and was dropped here.
"""
BASE = {
    f"usecases/{CASE}/rules.d1.ve": RULES,
    f"usecases/{CASE}/facts.d1.ve": FACTS,
    f"usecases/{CASE}/demo_vocabulary.py": VOCABULARY,
    f"usecases/{CASE}/environment.d1.json": json.dumps(ENVIRONMENT),
    f"usecases/{CASE}/PLAN.md": PLAN,
    f"usecases/{CASE}/README.md": "# Demo\n\nu-rule is translated in full.\n",
    f"usecases/{CASE}/spans.json": json.dumps({"units": [{"id": "s1", "status": "OPEN", "rule": "u-rule"}]}),
    f"usecases/{CASE}/accounting.d1.txt": "u-rule | omits:\nu-carrier | omits:\nfact-a | omits:\n",
    "docs/usecases/other-case/batch/REPORT.md": "u-rule was dropped (another case: not scanned).\n",
}
UNITS = ("u-rule", "u-carrier")


def acc(rule_entries, carrier_entries=""):
    return {f"usecases/{CASE}/accounting.d1.txt":
            f"u-rule | omits: {rule_entries}\nu-carrier | omits: {carrier_entries}\nfact-a | omits:\n"}


def plan12(text):
    return {f"usecases/{CASE}/PLAN.md": PLAN.replace("Nothing changed.", text)}


# (id, edits to BASE (None deletes a file), units, case, expected record_paths; None = the rule fails closed)
SCENARIOS = [
    ("clean", {}, UNITS, CASE, {}),
    # accounting tags: anything but restates / rule / reading is a loss (F1's class)
    ("tag-loss", acc('"a widget" loss 1'), UNITS, CASE, {"u-rule": ["loss"]}),
    ("tag-exposition", acc('"In the rare case that" exposition'), UNITS, CASE, {"u-rule": ["loss"]}),
    ("tag-dropped", acc('"a widget" dropped'), UNITS, CASE, {"u-rule": ["loss"]}),
    ("tag-empty", acc('"a widget"'), UNITS, CASE, {"u-rule": ["loss"]}),
    ("tag-unknown-case", acc('"a widget" Restates'), UNITS, CASE, {"u-rule": ["loss"]}),
    ("line-unparseable", acc('"a "widget" inspected" restates'), UNITS, CASE, {"u-rule": ["loss"]}),
    # restates: every token but the articles, whole tokens, in ONE segment of the formal carrier
    ("restates-carried", acc('"a widget inspected" restates'), UNITS, CASE, {}),
    ("restates-in-legend", acc('"a hazard is present" restates'), UNITS, CASE, {}),
    ("restates-missing-word", acc('"a widget never inspected" restates'), UNITS, CASE, {"u-rule": ["mistag"]}),
    ("restates-negation-counts", acc('"not inspected" restates'), UNITS, CASE, {"u-rule": ["mistag"]}),
    ("restates-across-segments", acc('"widget hazard present" restates'), UNITS, CASE, {"u-rule": ["mistag"]}),
    ("restates-header-quote", acc('"shiny guide" restates'), UNITS, CASE, {"u-rule": ["mistag"]}),
    ("restates-comment", acc('"polished brightly" restates'), UNITS, CASE, {"u-rule": ["mistag"]}),
    ("restates-quoted-literal", acc('"hazard" restates', '"hazard" restates'), UNITS, CASE, {"u-carrier": ["mistag"]}),
    ("restates-substring", acc('"widg" restates'), UNITS, CASE, {"u-rule": ["mistag"]}),
    ("restates-articles-only", acc('"the a" restates'), UNITS, CASE, {"u-rule": ["mistag"]}),
    # rule <id> and reading RSn
    ("rule-carried", acc('"blue widget polished" rule u-carrier'), UNITS, CASE, {}),
    ("rule-not-carried", acc('"blue widget inspected" rule u-carrier'), UNITS, CASE, {"u-rule": ["mistag"]}),
    ("rule-unknown-id", acc('"a widget" rule u-none'), UNITS, CASE, {"u-rule": ["mistag"]}),
    ("rule-no-id", acc('"a widget" rule'), UNITS, CASE, {"u-rule": ["mistag"]}),
    ("reading-named", acc('"a widget inspected" reading RS1'), UNITS, CASE, {}),
    ("reading-other-set", acc('"a widget inspected" reading RS2'), UNITS, CASE, {"u-rule": ["mistag"]}),
    ("reading-not-in-header", acc("", '"blue widget polished" reading RS1'), UNITS, CASE, {"u-carrier": ["mistag"]}),
    ("words-empty", acc('"" restates'), UNITS, CASE, {"u-rule": ["mistag"]}),
    # no accounting line; no accounting file
    ("no-line", {f"usecases/{CASE}/accounting.d1.txt": "u-carrier | omits:\n"}, UNITS, CASE, {"u-rule": ["no-record"]}),
    ("no-file", {f"usecases/{CASE}/accounting.d1.txt": None}, UNITS, CASE, {"*": ["no-record"]}),
    # PLAN section 12: every sentence naming the unit, bare or backticked, drop word or not; outside 12 nothing
    ("plan12-bare", plan12("u-rule is a new rule."), UNITS, CASE, {"u-rule": ["plan12"]}),
    ("plan12-backticks", plan12("`u-carrier` and `u-rule` quote the passage."), UNITS, CASE,
     {"u-rule": ["plan12"], "u-carrier": ["plan12"]}),
    ("plan12-h3", {f"usecases/{CASE}/PLAN.md": PLAN.replace("## 12.", "### 12").replace("## 13.", "### 13")
                   .replace("Nothing changed.", "u-rule moved.")}, UNITS, CASE, {"u-rule": ["plan12"]}),
    ("plan12-missing", {f"usecases/{CASE}/PLAN.md": "# Plan\n\nu-rule is fine.\n"}, UNITS, CASE, {"u-rule": ["plan12"]}),
    # README and the case's docs REPORT.md: a sentence with a drop word naming the unit
    ("readme-drop", {f"usecases/{CASE}/README.md": "u-rule omits nothing.\n"}, UNITS, CASE, {"u-rule": ["report"]}),
    ("readme-loss-word", {f"usecases/{CASE}/README.md": 'Its tag was "loss 1" for u-rule.\n'}, UNITS, CASE,
     {"u-rule": ["report"]}),
    ("readme-lowercase-start", {f"usecases/{CASE}/README.md":
                                "Ten units left UNFORMALISED (see below). since then u-rule is OPEN.\n"}, UNITS, CASE,
     {"u-rule": ["report"]}),
    ("readme-new-sentence", {f"usecases/{CASE}/README.md":
                             "Ten units left UNFORMALISED (see below). Since then u-rule is OPEN.\n"}, UNITS, CASE, {}),
    # a table cell is a sentence of its own: only the cell with the drop word records
    ("report-drop", {f"docs/usecases/{CASE}/batch/REPORT.md": "| u-carrier | merged into u-rule |\n"}, UNITS, CASE,
     {"u-rule": ["report"]}),
    ("report-safetyfw-dir", {f"docs/usecases/safetyfw/{CASE}/REPORT.md": "u-rule was removed.\n"}, UNITS, CASE,
     {"u-rule": ["report"]}),
    ("report-no-drop-word", {f"docs/usecases/{CASE}/batch/REPORT.md": "u-rule is translated.\n"}, UNITS, CASE, {}),
    # gaps / coverage files: a JSON object or any text sentence naming the unit
    ("gaps-json", {f"usecases/{CASE}/coverage.json": json.dumps({"units": [{"id": "u-rule", "n": 1}]})}, UNITS, CASE,
     {"u-rule": ["gaps"]}),
    ("gaps-json-key", {f"docs/usecases/{CASE}/gaps.json": json.dumps({"u-carrier": {"n": 1}})}, UNITS, CASE,
     {"u-carrier": ["gaps"]}),
    ("gaps-text", {f"usecases/{CASE}/GAPS.md": "u-rule is complete.\n"}, UNITS, CASE, {"u-rule": ["gaps"]}),
    ("gaps-unparseable", {f"usecases/{CASE}/coverage.json": "{"}, UNITS, CASE, None),
    # UNFORMALISED spans blocked on the unit (a list or a comma list too)
    ("unformalised", {f"usecases/{CASE}/spans.json": json.dumps({"units": [
        {"id": "s2", "status": "UNFORMALISED", "blocked_rule": "u-rule"},
        {"id": "s3", "status": "unformalised", "blocked_rule": ["u-carrier, u-rule"]},
        {"id": "s4", "status": "OPEN", "blocked_rule": "u-carrier"}]})}, UNITS, CASE,
     {"u-rule": ["unformalised", "unformalised"], "u-carrier": ["unformalised"]}),
    # a FACTS sub-block's record goes to FACTS
    ("facts", {f"usecases/{CASE}/accounting.d1.txt": 'u-rule | omits:\nu-carrier | omits:\nfact-a | omits: "x" loss\n'},
     UNITS + ("FACTS",), CASE, {"FACTS": ["loss"]}),
    # a revoked documentation clearance (openai-preparedness: f9-threshold)
    ("revoked", {}, ("u-rule", "f9-threshold"), "openai-preparedness", {"f9-threshold": ["no-record", "revoked"]}),
    # an unreadable rules, PLAN or spans file: the rule fails closed
    ("no-rules", {f"usecases/{CASE}/rules.d1.ve": None}, UNITS, CASE, None),
    ("no-plan", {f"usecases/{CASE}/PLAN.md": None}, UNITS, CASE, None),
    ("bad-spans", {f"usecases/{CASE}/spans.json": '{"units": 7}'}, UNITS, CASE, None),
]


def build(root, edits, case=CASE):
    files = dict(BASE)
    if case != CASE:
        files = {k.replace(f"usecases/{CASE}/", f"usecases/{case}/"): v for k, v in files.items()}
    files.update(edits)
    for rel, text in files.items():
        if text is not None:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    return root


@pytest.mark.parametrize("name,edits,units,case,expected", SCENARIOS, ids=[s[0] for s in SCENARIOS])
def test_each_record_path_of_the_omission_rule(tmp_path, name, edits, units, case, expected):
    root = build(tmp_path, edits, case)
    if expected is None:
        assert omission_rule.exposures(case, units, root) is None
        with pytest.raises(AssertionError, match="fails closed"):
            omission_rule.record_paths(case, units, root)
    else:
        assert omission_rule.record_paths(case, units, root) == expected


def test_an_exposition_tag_records_its_words_as_a_loss(tmp_path):
    """F1's example: the K13 chair units' exposition entries are losses, with their words and tag in the record."""
    root = build(tmp_path, acc('"In the rare case that" exposition ; "a widget inspected" restates'))
    assert omission_rule.exposures(CASE, UNITS, root) == {
        "u-rule": [("u-rule", "u-rule", "loss", "In the rare case that (exposition)")]}


def test_every_record_path_has_a_scenario():
    """The table covers each path the rule names (a path added to the port without a scenario fails here)."""
    seen = {p for *_, expected in SCENARIOS if expected for paths in expected.values() for p in paths}
    assert seen == set(omission_rule.PATHS)
