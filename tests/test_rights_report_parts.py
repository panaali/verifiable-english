"""rights-cfr-2/3 (docs/rights/rights-cfr-2/REPORT.md): a CONFLICT-FREE answer gives rights.md 7.3's report parts
(the spec's line, read from the spec file, and the same parts as fields); both finding kinds carry their line's span
(rights.md 8); the relay only types and binds the new fields (R8)."""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

from tests.test_rights_lean import (ARBITRARY, ARREST, BLOCK, DEPRIVE, GAMMA, L29, condition, env, limitation, line,
                                    norm, packages, right, run)
from tests.test_soft_norms_lean import DECIDER, SERVICE
from tests.test_soft_norms_lean import elaborate as soft_elaborate, packages as soft_packages, run as soft_run
from ve import rights_route
from ve.backends.service_schema import Invalid, check_row
from ve.errors import CheckerUnavailable, VEError
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


def _template():
    """rights.md 7.3's CONFLICT-FREE line as the spec file writes it (its two lines joined)."""
    block = SPEC.read_text(encoding="utf-8").split("### 7.3 Status text", 1)[1].split("```text\n", 1)[1]
    first, second = block.splitlines()[:2]
    return f"{first} {second.strip()}"


# rights-cfr-2-budget-1 (docs/rights/rights-cfr-2-budget-1/DELTA.md): the line names what `<j>` counts (R3), and with
# no situation supplied it says none was searched, keeping the quoted budget (R1), never "UNKNOWN (budget 10000)".
# Both are rights.md 7.3's own words, read from the spec by `_spec_line`; these constants pin them in the tests below.
GLOSS = "colliding default pairs no ranking resolves"
NOT_SEARCHED = "none supplied (not searched; budget 10000 unused)"


def _spec_line(template, *, k, l, labels, j, exhibited):
    """The template's placeholders filled and one of its situation alternatives chosen (`exhibited`: "yes" or
    "none supplied"); the rights-conflict case has no couplings, so the optional `[, under couplings <ids>]` is left
    out, and `<budget>` is rendered `budget 10000`, as on the UNKNOWN line."""
    head, alternatives = template.split("situation exhibited: ")
    [chosen] = [a for a in alternatives.split(" | ") if a.startswith(exhibited)]
    filled = (f"{head}situation exhibited: {chosen}".replace("[, under couplings <ids>]", "")
              .replace("<k>", str(k)).replace("<l>", str(l)).replace("<labels>", ", ".join(labels))
              .replace("<j>", str(j)).replace("<budget>", "budget 10000"))
    assert "<" not in filled and "[" not in filled
    return filled


# --- 1. the CONFLICT-FREE report parts ------------------------------------------------------------------------

def test_rights_conflict_free_report_evidence():
    environment, certified, situation = _weighed()
    labels = ["soft:coherence:may-detain,no-arbitrary-arrest",
              "rights:limitation:l29:arrest_permitted:necessary:determined_by_law",
              "rights:limitation:l29:arrest_permitted:sufficient:diplomatic_immunity"]
    # Lean's own line, before any relay, is the spec's line byte for byte (the DRI-signed row's condition).
    [raw] = run("ve_rights_route", [{"id": "c", "kind": "rights-conflict", "environment": env(ARREST),
                                     "document": WEIGHED, "packages": certified}])
    assert raw["status_text"] == _spec_line(_template(), k=1, l=2, labels=labels, j=1, exhibited="none supplied")
    bare = rights_route.run_rights_case(environment, WEIGHED, "rights-conflict", packages=certified)
    shown = rights_route.run_rights_case(environment, WEIGHED, "rights-conflict", packages=certified,
                                         situation=situation)
    for row in (bare, shown):
        assert row["verdict"] == "CONFLICT-FREE"
        assert row["conditional_on"] == labels
        assert row["weighing_points"] == ["soft:coherence:may-detain,no-arbitrary-arrest"]
        assert row["budget"] == 10000
        # The first sentence is kept byte for byte; 7.3's parts follow it.
        assert row["status_text"].startswith("CONFLICT-FREE among rules on the same act, conditional on 1 coherence "
                                             "premises and 2 limitation premises (")
    # No situation sent: the line says none was supplied or searched, with the unused budget; none is shown.
    assert bare["status_text"] == _spec_line(_template(), k=1, l=2, labels=labels, j=1, exhibited="none supplied")
    assert bare["situation_exhibited"] is False and bare["situation"] is None
    # A checked situation: its decision, exception and limitation tables, as the request gave them.
    assert shown["status_text"] == _spec_line(_template(), k=1, l=2, labels=labels, j=1, exhibited="yes")
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


def test_rights_conflict_free_without_a_situation_names_no_search():
    """rights-cfr-2-budget-1 (1): no situation supplied, so no search ran; the line must not read as one that hit its
    budget. It keeps the quoted budget 10000 (R1), and every JSON field is as before; a supplied one still says yes."""
    environment, certified, situation = _weighed()
    [raw] = run("ve_rights_route", [{"id": "c", "kind": "rights-conflict", "environment": env(ARREST),
                                     "document": WEIGHED, "packages": certified}])
    bare = rights_route.run_rights_case(environment, WEIGHED, "rights-conflict", packages=certified)
    for row in (raw, bare):
        assert "UNKNOWN (budget" not in row["status_text"] and "UNKNOWN" not in row["status_text"]
        assert row["status_text"].endswith(f"; situation exhibited: {NOT_SEARCHED}")
        assert (row["situation_exhibited"], row["budget"], row["situation"]) == (False, 10000, None)
    shown = rights_route.run_rights_case(environment, WEIGHED, "rights-conflict", packages=certified,
                                         situation=situation)
    assert shown["status_text"].endswith("; situation exhibited: yes") and shown["situation_exhibited"] is True
    assert shown["budget"] == 10000


def test_rights_weighing_points_name_what_they_count():
    """rights-cfr-2-budget-1 (2), step 1's fixture: `<j>` is WP(T) with no pair evidence (the colliding default pairs no
    ranking resolves, `openCoherence`), and the line names it (R3); the count is unchanged (1)."""
    environment, certified, _ = _weighed()
    bare = rights_route.run_rights_case(environment, WEIGHED, "rights-conflict", packages=certified)
    assert bare["weighing_points"] == ["soft:coherence:may-detain,no-arbitrary-arrest"]
    assert f"; 1 weighing points open ({GLOSS}); situation exhibited: " in bare["status_text"]


def test_rights_no_search_delta_keeps_every_quoted_value():
    """The R1/R3 delta test over the saved evidence (docs/rights/rights-cfr-2-budget-1/delta.json): each record's head
    is Lean's line now, at the base's path, and it keeps every number and label the base quoted."""
    saved = json.loads((ROOT / "docs/rights/rights-cfr-2-budget-1/delta.json").read_text(encoding="utf-8"))
    environment, certified, situation = _weighed()
    assert [r["situation"] for r in saved["records"]] == [False, True]
    for record in saved["records"]:
        shown = {"situation": situation} if record["situation"] else {}
        row = rights_route.run_rights_case(environment, WEIGHED, "rights-conflict", packages=certified, **shown)
        assert record["path"] == "status_text" and row[record["path"]] == record["head"]
        quoted = re.findall(r"[a-z]+:[\w:,-]+[\w]|\d+", record["base"])
        assert "10000" in quoted or record["situation"]
        assert all(record["head"].count(value) >= record["base"].count(value) for value in quoted)
        # The words kept, and the one phrase removed: the no-search line no longer says UNKNOWN of a search.
        assert all(w in record["head"] for w in ("weighing points open", "situation exhibited: "))
        removed = "UNKNOWN (budget 10000)" if not record["situation"] else None
        assert (removed is None or (removed in record["base"] and removed not in record["head"]
                                    and "budget 10000" in record["head"]))


def test_rights_and_soft_routes_count_the_same_weighing_points():
    """rights-cfr-2-budget-1 (2), step 1's pair: one unranked default pair, as a rights document and as a soft-norms
    document. Both routes' `<j>` is WP(T) (`openCoherence`, one owner), so both lines say 1, from Lean's raw answers."""
    pair = [_default("no-arbitrary-arrest", "arrest_permitted", False, guard=ARBITRARY),
            _default("may-detain", "arrest_permitted", True)]
    raw = env(ARREST)
    soft_env = {**raw, "profiles": [p for p in raw["profiles"] if p != "rights@0"],
                "vocabulary": {k: v for k, v in raw["vocabulary"].items() if k != "rights"}}
    soft_doc = [{"norm": n} for n in pair]
    certified = soft_packages(soft_env, soft_doc, soft_elaborate("ve_soft_norms_route", soft_env, soft_doc))
    [soft] = soft_run("ve_soft_norms_route", [{"id": "s", "kind": "soft-conflict", "environment": soft_env,
                                               "norms": soft_doc, "packages": certified}])
    rights_doc = [right("r9", [line("claim", pair[0])]), {"norm": pair[1]}]
    elaborated = rights_route.run_rights_case(RightsEnvironment(raw), rights_doc, "rights-elaborate")
    [rights] = run("ve_rights_route", [{"id": "r", "kind": "rights-conflict", "environment": raw,
                                        "document": rights_doc, "packages": packages(raw, rights_doc, elaborated)}])
    assert (soft["verdict"], rights["verdict"]) == ("CONFLICT-FREE", "CONFLICT-FREE")
    assert "; 1 weighing points open; " in soft["status_text"]
    assert f"; 1 weighing points open ({GLOSS}); " in rights["status_text"]
    assert rights["weighing_points"] == ["soft:coherence:may-detain,no-arbitrary-arrest"]


NO_SEARCH_MUTATIONS = {
    "old UNKNOWN line restored": lambda row: row.update(
        status_text=row["status_text"].replace(NOT_SEARCHED, "UNKNOWN (budget 10000)")),
    "count gloss dropped": lambda row: row.update(status_text=row["status_text"].replace(f" ({GLOSS})", "")),
    "budget shifted": lambda row: row.update(status_text=row["status_text"].replace("10000 unused", "9999 unused")),
}


@pytest.mark.parametrize("label", sorted(NO_SEARCH_MUTATIONS))
def test_a_mutated_no_search_line_is_refused(monkeypatch, label):
    environment, certified, _ = _weighed()
    _forge(monkeypatch, "rights-conflict", NO_SEARCH_MUTATIONS[label])
    with pytest.raises(CheckerUnavailable):
        rights_route.run_rights_case(environment, WEIGHED, "rights-conflict", packages=certified)


@pytest.mark.parametrize("edit, error", [
    # Limitation 29's sufficient condition without the limitation violates Lim_D: not a situation of Background_base″.
    (lambda m: m["relations"].update(rights__cond__2=[["s", "p"]]), "InvalidModel"),
    (lambda m: m.pop("complete"), "fields do not match"),
    (lambda m: m["relations"].update(rights__cond__1=[["s", "x"]]), "dangling or wrong-sort tuple"),
])
def test_an_invalid_situation_is_refused_by_lean(edit, error):
    environment, certified, situation = _weighed()
    edit(situation)
    with pytest.raises(VEError, match=error):
        rights_route.run_rights_case(environment, WEIGHED, "rights-conflict", packages=certified, situation=situation)


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
    (7, "InvalidInput: located must name one source unit per document unit"),
    ({}, "InvalidInput: located must name one source unit per document unit"),
    ([7, 7, 7, 7], "String expected"),
])
def test_lean_refuses_located_lines_the_request_does_not_have(located, error):
    with pytest.raises(VEError, match=re.escape(error)):
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


SPANS = ["s4", "absent", "", None, 7, True, [], {}, "dropped"]


@pytest.mark.parametrize("kind", ["rights-elaborate", "rights-scope"])
@pytest.mark.parametrize("span", SPANS, ids=[repr(span) for span in SPANS])
def test_a_mutated_finding_span_is_refused(monkeypatch, kind, span):
    def mutation(row):
        if span == "dropped":
            del row["located_findings"][0]["span"]
        else:
            row["located_findings"][0]["span"] = span
    _forge(monkeypatch, kind, mutation)
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
}


@pytest.mark.parametrize("kind", ["rights-elaborate", "rights-scope"])
@pytest.mark.parametrize("label", sorted(ROW_MUTATIONS))
def test_a_mutated_finding_row_is_refused(monkeypatch, kind, label):
    _forge(monkeypatch, kind, lambda row: ROW_MUTATIONS[label](row["located_findings"]))
    with pytest.raises(CheckerUnavailable):
        rights_route.report_rights(_spanned_environment(), copy.deepcopy(SPANNED), located=LOCATED)


def test_a_span_where_no_line_is_located_is_refused(monkeypatch):
    _forge(monkeypatch, "rights-scope", lambda row: row["located_findings"][0].update(span="s2"))
    with pytest.raises(CheckerUnavailable):
        rights_route.report_rights(_spanned_environment(), copy.deepcopy(SPANNED))


CONFLICT_MUTATIONS = {
    "weighing point dropped": lambda row: row["weighing_points"].clear(),
    "weighing point added": lambda row: row["weighing_points"].append("soft:coherence:absent,no-arbitrary-arrest"),
    "weighing point renamed": lambda row: row["weighing_points"].__setitem__(0, "soft:coherence:a,b"),
    "weighing points retyped": lambda row: row.update(weighing_points=7),
    "situation not exhibited": lambda row: row.update(situation_exhibited=False),
    "budget shifted": lambda row: row.update(budget=9999),
    "budget retyped": lambda row: row.update(budget="10000"),
    "situation null": lambda row: row.update(situation=None),
    "situation retyped": lambda row: row.update(situation={}),
    "table renamed": lambda row: row["situation"][0].update(predicate="absent"),
    "table rows changed": lambda row: row["situation"][1].update(tuples=[["s", "s"]]),
    "table rows retyped": lambda row: row["situation"][1].update(tuples=[[7]]),
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
