"""rights-cfr-2 and rights-cfr-3 (docs/rights/rights-cfr-2/REPORT.md).

1. A CONFLICT-FREE rights-conflict answer gives the report parts of docs/spec/rights.md 7.3: its status line is the
   spec's line, read from the spec file, with the premise labels, the weighing points open and either the exhibited
   situation (a finite base model Lean checked against `Background_base″`, 5.3 (2)) or UNKNOWN with the budget; the
   same parts are fields beside it.
2. Both finding kinds (`UnlicensedLimitation`, `ProtectedInCone`) carry their line's span (rights.md 8): the source
   unit the request's `located` field names for the line's unit; the report shows it beside the text.
3. The relay only types and binds the new fields (R8): every mutation of them is CheckerUnavailable.
"""
from __future__ import annotations

import copy
import re
from pathlib import Path

import pytest

from tests.test_rights_lean import (ARBITRARY, ARREST, BLOCK, DEPRIVE, GAMMA, L29, condition, env, limitation, line,
                                    norm, packages, right)
from tests.test_soft_norms_lean import DECIDER, SERVICE
from ve import rights_route
from ve.backends.service_schema import Invalid, check_row
from ve.errors import CheckerUnavailable
from ve.rights import RightsEnvironment

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/spec/rights.md"


@pytest.fixture(scope="module", autouse=True)
def _service():
    if not SERVICE.exists():
        pytest.skip("the Lean service has not been built")


# --- fixtures -------------------------------------------------------------------------------------------------

RULE7 = norm("rule-7", "arrest_permitted", True, guard=("unary", "journalist", ["var", 0]), over=["no-arbitrary-arrest"])
# Two rights in two units, the limitation and an uncited adopter exception: `UnlicensedLimitation` on r9's line and
# `ProtectedInCone` on both lines (their guards read the protected `arbitrary_arrest`, uncited).
SPANNED = [{"source_units": ["s1", "s2", "s3", "s4", "s5"]}, GAMMA[0],
           right("r3", [line("claim", norm("no-deprivation", "deprive_permitted", False, guard=ARBITRARY))]),
           L29, {"norm": RULE7}]
LOCATED = ["s2", "s3", "s4", "s5"]


def _spanned_environment():
    return RightsEnvironment(env({**ARREST, **DEPRIVE}, rights={**BLOCK, "protected": ["arbitrary_arrest"]}))


def _default(name, predicate, sign, **soft):
    return norm(name, predicate, sign, mode="default", exception=dict(DECIDER), **soft)


# An unranked default pair on `arrest_permitted` (one weighing point) and limitation 29 with a sufficient condition
# that guards an adopter's permission: CONFLICT-FREE conditional on the coherence premise and the limitation premises.
WEIGHED = [right("r9", [line("claim", _default("no-arbitrary-arrest", "arrest_permitted", False, guard=ARBITRARY))]),
           limitation(conditions=[condition("determined_by_law"), condition("diplomatic_immunity", "sufficient")]),
           {"norm": norm("may-arrest", "arrest_permitted", True,
                         guard=("binary", "rights__cond__2", ["var", 1], ["var", 0]))},
           {"norm": _default("may-detain", "arrest_permitted", True)}]


def _weighed():
    raw = env(ARREST)
    environment = RightsEnvironment(raw)
    elaborated = rights_route.run_rights_case(environment, WEIGHED, "rights-elaborate")
    relations = {name: [] for name, entry in elaborated["environment_prime"]["vocabulary"]["predicates"].items()
                 if "regulated" not in entry and not name.startswith("soft__")}
    relations.update({entry["name"]: [] for entry in elaborated["decisions"]})
    # A situation with rows: the exception of `may-detain` decided, condition 1 of limitation 29 holding.
    relations["soft__excepted__may_detain"] = [["s", "p"]]
    relations["rights__cond__1"] = [["s", "p"]]
    situation = {"complete": True, "domains": {"state": ["s"], "person": ["p"]}, "constants": {},
                 "relations": relations}
    return environment, packages(raw, WEIGHED, elaborated), situation


def _spec_line(*, k, l, labels, j, exhibited, template=None):
    """rights.md 7.3's CONFLICT-FREE line, read from the spec file, its placeholders filled; the rights-conflict case
    has no couplings, so the optional `[, under couplings <ids>]` is left out."""
    if template is None:
        text = SPEC.read_text(encoding="utf-8")
        block = text[text.index("### 7.3 Status text"):]
        first, second = block[block.index("```text\n") + len("```text\n"):].splitlines()[:2]
        template = f"{first} {second.strip()}"
    assert template.count("[, under couplings <ids>]") == 1 and template.count("yes | UNKNOWN (<budget>)") == 1
    filled = (template.replace("[, under couplings <ids>]", "").replace("<k>", str(k)).replace("<l>", str(l))
              .replace("<labels>", ", ".join(labels)).replace("<j>", str(j))
              .replace("yes | UNKNOWN (<budget>)", exhibited))
    assert "<" not in filled and "[" not in filled
    return filled


# --- 1. the CONFLICT-FREE report parts ------------------------------------------------------------------------

def test_rights_conflict_free_report_evidence():
    environment, certified, situation = _weighed()
    bare = rights_route.run_rights_case(environment, WEIGHED, "rights-conflict", packages=certified)
    shown = rights_route.run_rights_case(environment, WEIGHED, "rights-conflict", packages=certified,
                                         situation=situation)
    labels = ["soft:coherence:may-detain,no-arbitrary-arrest",
              "rights:limitation:l29:arrest_permitted:necessary:determined_by_law",
              "rights:limitation:l29:arrest_permitted:sufficient:diplomatic_immunity"]
    for row in (bare, shown):
        assert row["verdict"] == "CONFLICT-FREE"
        assert row["conditional_on"] == labels
        assert row["weighing_points"] == ["soft:coherence:may-detain,no-arbitrary-arrest"]
        assert row["budget"] == 10000
        # The first sentence is kept byte for byte; 7.3's parts follow it.
        assert row["status_text"].startswith("CONFLICT-FREE among rules on the same act, conditional on 1 coherence "
                                             "premises and 2 limitation premises (")
    # No situation sent: the line says UNKNOWN with its budget, and no situation is shown.
    assert bare["status_text"] == _spec_line(k=1, l=2, labels=labels, j=1, exhibited="UNKNOWN (budget 10000)")
    assert bare["situation_exhibited"] is False and bare["situation"] is None
    # A checked situation: its decision, exception and limitation tables, as the request gave them.
    assert shown["status_text"] == _spec_line(k=1, l=2, labels=labels, j=1, exhibited="yes")
    assert shown["situation_exhibited"] is True
    assert shown["situation"] == [{"predicate": "soft__excepted__no_arbitrary_arrest", "tuples": []},
                                  {"predicate": "soft__excepted__may_detain", "tuples": [["s", "p"]]},
                                  {"predicate": "rights__lim__1", "tuples": []},
                                  {"predicate": "rights__cond__1", "tuples": [["s", "p"]]},
                                  {"predicate": "rights__cond__2", "tuples": []}]
    # The report shows the parts beside the verdict (no certificates there: UNKNOWN, without them).
    report = rights_route.report_rights(environment, WEIGHED)
    assert report["conflict"]["verdict"] == "UNKNOWN"
    assert not {"weighing_points", "situation_exhibited", "budget", "situation"} & set(report["conflict"])


def test_the_spec_comparison_refuses_a_one_character_edit():
    """The negative side of the DRI-signed row (adv0838 item 3 (b)): the comparison is byte for byte with the spec
    text, so a one-character edit of the template, or of Lean's line, no longer compares equal."""
    environment, certified, _ = _weighed()
    row = rights_route.run_rights_case(environment, WEIGHED, "rights-conflict", packages=certified)
    args = dict(k=1, l=2, labels=row["conditional_on"], j=1, exhibited="UNKNOWN (budget 10000)")
    assert row["status_text"] == _spec_line(**args)
    text = SPEC.read_text(encoding="utf-8")
    block = text[text.index("### 7.3 Status text"):]
    first, second = block[block.index("```text\n") + len("```text\n"):].splitlines()[:2]
    template = f"{first} {second.strip()}"
    for word in ("CONFLICT-FREE", "among", "coherence", "limitation", "weighing", "open;", "exhibited:"):
        i = template.index(word)
        edited = template[:i] + template[i].swapcase() + template[i + 1:]
        assert row["status_text"] != _spec_line(**args, template=edited)
    assert row["status_text"][:-1] + "!" != _spec_line(**args)


def test_an_invalid_situation_is_refused_by_lean():
    environment, certified, situation = _weighed()
    broken = copy.deepcopy(situation)
    # Limitation 29's sufficient condition without the limitation violates Lim_D: not a situation of Background_base″.
    broken["relations"]["rights__cond__2"] = [["s", "p"]]
    with pytest.raises(Exception, match="InvalidModel"):
        rights_route.run_rights_case(environment, WEIGHED, "rights-conflict", packages=certified, situation=broken)


# --- 2. finding spans -----------------------------------------------------------------------------------------

def test_rights_findings_preserve_source_spans():
    report = rights_route.report_rights(_spanned_environment(), copy.deepcopy(SPANNED), located=LOCATED)
    assert report["unlicensed_limitations_located"] == [
        {"code": "UnlicensedLimitation", "rule": "no-arbitrary-arrest", "right": "r9", "span": "s2",
         "text": "UnlicensedLimitation: exception rule-7 of rule no-arbitrary-arrest on right r9"}]
    assert report["distinction_hits_located"] == [
        {"code": "ProtectedInCone", "rule": "no-arbitrary-arrest", "right": "r9", "span": "s2",
         "text": "ProtectedInCone: arbitrary_arrest in rule no-arbitrary-arrest on right r9"},
        {"code": "ProtectedInCone", "rule": "no-deprivation", "right": "r3", "span": "s3",
         "text": "ProtectedInCone: arbitrary_arrest in rule no-deprivation on right r3"}]
    # The text fields are kept, each beside its span.
    assert report["unlicensed_limitations"] == [r["text"] for r in report["unlicensed_limitations_located"]]
    assert report["distinction_hits"] == [r["text"] for r in report["distinction_hits_located"]]
    # Another location of the same source moves only the spans.
    moved = rights_route.report_rights(_spanned_environment(), copy.deepcopy(SPANNED),
                                       located=["s5", "s1", "s2", "s3"])
    assert [r["span"] for r in moved["distinction_hits_located"]] == ["s5", "s1"]
    assert [r["span"] for r in moved["unlicensed_limitations_located"]] == ["s5"]
    # Without `located` no line is located: the span is null, never a guess.
    plain = rights_route.report_rights(_spanned_environment(), copy.deepcopy(SPANNED))
    assert [r["span"] for r in plain["distinction_hits_located"] + plain["unlicensed_limitations_located"]] == \
        [None, None, None]


@pytest.mark.parametrize("located, error", [
    (["s2", "s3", "s4"], "InvalidInput: located must name one source unit per document unit"),
    (["s2", "s3", "s4", "s5", "s1"], "InvalidInput: located must name one source unit per document unit"),
    (["s2", "s3", "absent", "s5"], "UnknownSymbol: unit absent"),
])
def test_lean_refuses_located_lines_the_request_does_not_have(located, error):
    with pytest.raises(Exception, match=re.escape(error)):
        rights_route.run_rights_case(_spanned_environment(), copy.deepcopy(SPANNED), "rights-elaborate",
                                     located=located)


# --- 3. R8: the relay types and binds every new field ----------------------------------------------------------

def _forge(monkeypatch, kind, mutation):
    real = rights_route.decide_once

    def forged(mode, case):
        row = copy.deepcopy(real(mode, case))
        if case["kind"] == kind:
            mutation(row)
            try:
                check_row(mode, row, case, 0)
            except Invalid as error:
                raise CheckerUnavailable(f"CheckerUnavailable: {error}") from error
        return row

    monkeypatch.setattr(rights_route, "decide_once", forged)


def _set(field, index, key, value):
    def mutation(row):
        if value is _DROP:
            del row[field][index][key]
        else:
            row[field][index][key] = value
    return mutation


_DROP = object()
FINDING_MUTATIONS = {
    "span another located unit": ("s4",),
    "span a unit the request lacks": ("absent",),
    "span emptied": ("",),
    "span null": (None,),
    "span retyped 7": (7,),
    "span retyped true": (True,),
    "span retyped list": ([],),
    "span retyped object": ({},),
    "span dropped": (_DROP,),
}


@pytest.mark.parametrize("kind", ["rights-elaborate", "rights-scope"])
@pytest.mark.parametrize("label", sorted(FINDING_MUTATIONS))
def test_a_mutated_finding_span_is_refused(monkeypatch, kind, label):
    _forge(monkeypatch, kind, _set("located_findings", 0, "span", FINDING_MUTATIONS[label][0]))
    with pytest.raises(CheckerUnavailable):
        rights_route.report_rights(_spanned_environment(), copy.deepcopy(SPANNED), located=LOCATED)


ROW_MUTATIONS = {
    "row dropped": lambda rows: rows.pop(0),
    "row duplicated": lambda rows: rows.append(copy.deepcopy(rows[0])),
    "extra row": lambda rows: rows.append({**copy.deepcopy(rows[0]), "rule": "absent"}),
    "rows emptied": lambda rows: rows.clear(),
    "rule renamed": lambda rows: rows[0].update(rule="absent"),
    "right renamed": lambda rows: rows[0].update(right="absent"),
    "code swapped": lambda rows: rows[0].update(code="Unknown"),
    "text shifted": lambda rows: rows[0].update(text=rows[0]["text"] + " "),
    "rows reordered": lambda rows: rows.reverse() if len(rows) > 1 else rows.pop(0),
}


@pytest.mark.parametrize("kind", ["rights-elaborate", "rights-scope"])
@pytest.mark.parametrize("label", sorted(ROW_MUTATIONS))
def test_a_mutated_finding_row_is_refused(monkeypatch, kind, label):
    _forge(monkeypatch, kind, lambda row: ROW_MUTATIONS[label](row["located_findings"]))
    with pytest.raises(CheckerUnavailable):
        rights_route.report_rights(_spanned_environment(), copy.deepcopy(SPANNED), located=LOCATED)


def test_a_span_where_no_line_is_located_is_refused(monkeypatch):
    _forge(monkeypatch, "rights-scope", _set("located_findings", 0, "span", "s2"))
    with pytest.raises(CheckerUnavailable):
        rights_route.report_rights(_spanned_environment(), copy.deepcopy(SPANNED))


def _table(index, key, value):
    def mutation(row):
        row["situation"][index][key] = value
    return mutation


CONFLICT_MUTATIONS = {
    "weighing point dropped": lambda row: row["weighing_points"].clear(),
    "weighing point added": lambda row: row["weighing_points"].append("soft:coherence:absent,no-arbitrary-arrest"),
    "weighing point renamed": lambda row: row["weighing_points"].__setitem__(0, "soft:coherence:a,b"),
    "weighing points retyped": lambda row: row.update(weighing_points=7),
    "situation not exhibited": lambda row: row.update(situation_exhibited=False),
    "exhibited retyped": lambda row: row.update(situation_exhibited=1),
    "budget shifted": lambda row: row.update(budget=9999),
    "budget retyped": lambda row: row.update(budget="10000"),
    "budget retyped bool": lambda row: row.update(budget=True),
    "situation null": lambda row: row.update(situation=None),
    "situation retyped": lambda row: row.update(situation={}),
    "table renamed": _table(0, "predicate", "absent"),
    "table rows changed": _table(1, "tuples", [["s", "s"]]),
    "table rows retyped": _table(1, "tuples", [[7]]),
    "table dropped": lambda row: row["situation"].pop(),
    "table added": lambda row: row["situation"].append({"predicate": "journalist", "tuples": []}),
    "status line edited": lambda row: row.update(status_text=row["status_text"].replace("weighing", "weighting")),
    "status line labels dropped": lambda row: row.update(
        status_text=re.sub(r" \(.*\);", " ();", row["status_text"])),
    "part dropped": lambda row: row.pop("weighing_points"),
}


@pytest.mark.parametrize("label", sorted(CONFLICT_MUTATIONS))
def test_a_mutated_conflict_report_part_is_refused(monkeypatch, label):
    environment, certified, situation = _weighed()
    _forge(monkeypatch, "rights-conflict", CONFLICT_MUTATIONS[label])
    with pytest.raises(CheckerUnavailable):
        rights_route.run_rights_case(environment, WEIGHED, "rights-conflict", packages=certified,
                                     situation=situation)


def test_a_situation_shown_when_none_was_sent_is_refused(monkeypatch):
    environment, certified, situation = _weighed()
    tables = rights_route.run_rights_case(environment, WEIGHED, "rights-conflict", packages=certified,
                                          situation=situation)["situation"]
    _forge(monkeypatch, "rights-conflict", lambda row: row.update(situation=tables))
    with pytest.raises(CheckerUnavailable):
        rights_route.run_rights_case(environment, WEIGHED, "rights-conflict", packages=certified)


def test_the_genuine_answers_are_accepted():
    """The opposite direction of the refusals above: the relay accepts every genuine answer they mutate."""
    environment, certified, situation = _weighed()
    assert rights_route.run_rights_case(environment, WEIGHED, "rights-conflict", packages=certified,
                                        situation=situation)["situation_exhibited"] is True
    report = rights_route.report_rights(_spanned_environment(), copy.deepcopy(SPANNED), located=LOCATED)
    assert len(report["distinction_hits_located"]) == 2
