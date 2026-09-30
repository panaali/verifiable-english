"""The constitution example of docs/spec/discourse.md 2.5 (u0214.s02) as a regression fixture.

The constitution pilot (run 20260930T0600Z, `probes/discourse-probe.json`) found the spec's own
example failing four ways on the discourse route: fenced content and a missing claim graph (stated
abstentions, 3.4 and 11), the curly apostrophe of `Claude’s` rejected as discourse wording (4.1(4)),
and `this broad pattern of treatment and trust` read as a slot (`MentionNotSlot`). A pronoun or
demonstrative naming a `unit` target is a location binding (1.4): never a slot, never parsed. The
example also needs `MIXED` units, which the Lean route now reads as Python does.

The source is the pinned constitution text (`claude-constitution.md`, SHA-256 fa10ed48...d50dd),
bytes [133600, 133882): u0214.s01 and u0214.s02 with the blank line after them. Each case runs in
Lean (`ve_discourse_route`, the admission) and through Python's `check_document` (whose verdict is
Lean's; its own port gives the diagnostic of a document both reject).
"""
from __future__ import annotations

import hashlib
import json

import pytest

from tests.test_discourse_lean import lean, run  # noqa: F401  (the `lean` fixture builds the route)
from ve.document import check_document
from ve.errors import UnsupportedProfile, VEError

S01 = ("As discussed above, Claude’s three main principals—Anthropic, operators, and users—warrant different "
       "sorts of treatment and trust from Claude. ")
S02 = ("We call this broad pattern of treatment and trust Claude’s principal hierarchy, and it helps define "
       "what we mean by broad safety.\n\n")
SOURCE = S01 + S02
SOURCE_SHA256 = "79655878ef0f4b35f6248a3adca7ea78f6ce14fffb882494cd3f9e8acac55939"
NAMING = "We call this broad pattern of treatment and trust Claude’s principal hierarchy"
NAME = "Claude’s principal hierarchy"
PATTERN = "this broad pattern of treatment and trust"
PROFILES = ["relational-fol@0", "ve.discourse@1"]


def at(text):
    """The prose byte offset of `text`'s first occurrence."""
    return len(SOURCE[:SOURCE.index(text)].encode())


def size(text):
    return len(text.encode())


A1 = size(S01)
A2 = A1 + size(NAMING)
END = size(SOURCE)
TARGET = {"kind": "unit", "units": ["u0214.s01"], "content_name": NAME}


def unformalised(uid, span, feature, **extra):
    return {"id": uid, "span": span, "kind": ["unformalised", feature], "meaning": {"unformalised": feature},
            "support": "none", **extra}


def environment(profiles=PROFILES, helps=False):
    """The example's environment; `helps` declares `helps(agent)` and the constant `claude`, for the
    variants that give a part content."""
    return {"language": "ve.core@0.2", "profiles": list(profiles), "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"agent": {"description": "agent"}},
                           "predicates": {"helps": {"arguments": ["agent"], "description": "helps"}} if helps else {},
                           "constants": {"claude": {"sort": "agent", "description": "Claude"}} if helps else {}}}


HELPS = ["unary", "helps", ["const", "claude"]]


def example(mixed=True):
    """The 2.5 entry as written: u0214.s01 UNFORMALISED; u0214.s02 MIXED, its naming clause a LABELLED
    `meta` part with the demonstrative, the rest an UNFORMALISED part with `it`; both mentions name
    the content name's `unit` target. The document's claim graph is its open term `broad_safety`."""
    naming = {"id": "u0214.s02.p1", "span": [A1, A2], "kind": "meta", "meaning": "specified", "support": "none"}
    rest = unformalised("u0214.s02.p2", [A2, END], "other.discourse")
    if mixed:
        s02 = [{"id": "u0214.s02", "span": [A1, END], "status": "MIXED",
                "parts": [dict(naming, status="LABELLED"), dict(rest, status="UNFORMALISED")]}]
    else:
        s02 = [naming, rest]
    return {
        "format": "ve-document@2", "environment": environment(),
        "units": [unformalised("u0214.s01", [0, A1], "counting")] + s02,
        "open_terms": [{"name": "broad_safety", "arguments": [], "decided_by": "reviewer", "necessary": [],
                        "sufficient": [], "factors": [], "precedents": [], "jurisdiction": "policy", "version": 1}],
        "graph": {"root": "n", "nodes": [{"name": "n", "ast": ["top"], "label": "open:broad_safety"}]},
        "discourse": {
            "version": "ve.discourse@1",
            "anchors": [{"id": "doc", "kind": "document", "label": "Claude’s constitution", "span": [0, END]}],
            "content_names": [{"name": NAME, "units": ["u0214.s01"], "scope": "doc"}],
            "mentions": [
                {"id": "m-this-pattern", "unit": "u0214.s02.p1", "span": [at(PATTERN), at(PATTERN) + size(PATTERN)],
                 "form": "demonstrative", "target": dict(TARGET)},
                {"id": "m-it", "unit": "u0214.s02.p2", "span": [at("it helps"), at("it helps") + 2],
                 "form": "pronoun", "target": dict(TARGET)}]}}


def text(front, source=SOURCE):
    return "---\n" + json.dumps(front, ensure_ascii=False) + "\n---\n" + source


def admit(front, source=SOURCE):
    return run([{"id": "c", "kind": "admission", "document": text(front, source)}])[0]


def python(front, tmp_path, source=SOURCE):
    path = tmp_path / "doc.ve.md"
    path.write_text(text(front, source), encoding="utf-8")
    return check_document(path)


def rejected(front, tmp_path, source=SOURCE):
    """Lean's diagnostic and Python's for a document both reject."""
    row = admit(front, source)
    assert row["status"] == "error", row
    with pytest.raises(VEError) as exc:
        python(front, tmp_path, source)
    return row["error"], str(exc.value)


EXPECTED_REFERENCES = [
    {"mention": "m-this-pattern", "unit": "u0214.s02.p1", "form": "demonstrative", "target": TARGET,
     "status": "navigation"},
    {"mention": "m-it", "unit": "u0214.s02.p2", "form": "pronoun", "target": TARGET, "status": "navigation"}]
EXPECTED_STATUSES = {"u0214.s01": "UNFORMALISED", "u0214.s02.p1": "LABELLED", "u0214.s02.p2": "UNFORMALISED"}


def test_source_is_the_pinned_bytes():
    assert hashlib.sha256(SOURCE.encode()).hexdigest() == SOURCE_SHA256
    assert "’" in NAMING  # U+2019: the example is not discourse wording (4.1(4))


@pytest.mark.parametrize("mixed", [True, False], ids=["mixed", "flat"])
def test_spec_example_is_admitted(lean, tmp_path, mixed):
    doc = example(mixed)
    row = admit(doc)
    assert row["status"] == "ok" and row["admitted"] is True, row
    assert row["statuses"] == EXPECTED_STATUSES
    assert row["references"] == EXPECTED_REFERENCES
    assert row["bound"] == {}  # a location binding elaborates nothing
    result = python(doc, tmp_path)
    assert result["references"] == EXPECTED_REFERENCES
    assert result["report_id"] == row["report_id"]
    assert "discourse_hints" not in result  # Python's port agrees
    assert result["coverage"]["bytes_by_status"] == {"UNFORMALISED": END - size(NAMING), "LABELLED": size(NAMING)}


def test_pilot_attempt_four_fragment(lean, tmp_path):
    """The pilot's last attempt: the naming clause cut before the name into two labelled fragments,
    the demonstrative in the ASCII one. It was `MentionNotSlot` (Python) and outside the fragment
    (Lean); a location binding is no slot, so it is admitted."""
    doc = example(mixed=False)
    lead = size("We call this broad pattern of treatment and trust ")
    naming = doc["units"][1]
    doc["units"][1:2] = [dict(naming, span=[A1, A1 + lead]), dict(naming, id="u0214.s02.p1b", span=[A1 + lead, A2])]
    row = admit(doc)
    assert row["status"] == "ok" and row["admitted"] is True, row
    assert [r["status"] for r in row["references"]] == ["navigation", "navigation"]
    assert python(doc, tmp_path)["report_id"] == row["report_id"]


# The class: a pronoun or demonstrative naming a unit (or anchor) target is a location binding (1.4).

def test_unit_target_in_a_slot_position_is_a_kind_mismatch(lean, tmp_path):
    """In a unit with meaning (content, or an active reading set) or a group span the position is a
    slot, so a location target there is `TargetKindMismatch`, never a silent binding."""
    doc = example(mixed=False)
    doc["environment"] = environment(helps=True)
    rest = doc["units"][2]
    doc["units"][2] = {"id": rest["id"], "span": rest["span"], "kind": "asserted", "meaning": "specified",
                       "support": "assumption", "content": {"ast": HELPS}}
    lean_error, python_error = rejected(doc, tmp_path)
    assert lean_error == python_error == "TargetKindMismatch: m-it: pronoun, unit"


@pytest.mark.parametrize("target, expected", [
    ({"kind": "unit", "units": ["u9"]}, "UnresolvedReference: m-it"),
    ({"kind": "unit", "units": []}, "UnresolvedReference: m-it"),
    ({"kind": "unit", "units": ["u0214.s01", "u0214.s02.p1"], "content_name": NAME},
     "ManifestMismatch: mentions.m-it.content_name"),
], ids=["unknown-unit", "empty-units", "content-name"])
def test_location_targets_must_exist(lean, tmp_path, target, expected):
    """A location binding's target is checked like any other (4.1(4)); Lean admitted these."""
    doc = example()
    doc["discourse"]["mentions"][1]["target"] = target
    assert rejected(doc, tmp_path) == (expected, expected)


@pytest.mark.parametrize("form", ["navigation", "section_ref"])
@pytest.mark.parametrize("target, expected", [
    ({"kind": "anchor", "name": "sec9"}, "DanglingAnchor: sec9"),
    ({"kind": "anchor"}, "InvalidInput: mention m-this-pattern target"),
    ({"kind": "unit", "units": ["u9"]}, "UnresolvedReference: m-this-pattern"),
    ({"kind": "rule", "name": "r1"}, "UnknownRule: r1"),
    ({"kind": "rule"}, "InvalidInput: mention m-this-pattern target"),
], ids=["anchor", "anchor-no-name", "unit", "rule", "rule-no-name"])
def test_every_location_target_must_exist(lean, tmp_path, form, target, expected):
    """discourse-example looprecheck1 B (WellFormed.lean:197): Lean admitted a `section_ref` to the
    rule `r1` as `navigation` though the route reads no norm content, so no rule exists (4.1(4)
    `UnknownRule`). Every location form and target kind is checked in both; a `navigation` to a
    rule is the form/kind mismatch it is in both."""
    doc = example(mixed=False)
    doc["discourse"]["mentions"][0].update(form=form, target=target)
    if form == "navigation" and target["kind"] == "rule":
        expected = "TargetKindMismatch: m-this-pattern: navigation, rule"
    assert rejected(doc, tmp_path) == (expected, expected)


def test_section_ref_to_a_unit_is_a_location(lean, tmp_path):
    """A `section_ref` fits a `unit` target in both (Python rejected it as `TargetKindMismatch`)."""
    doc = example()
    doc["discourse"]["mentions"][0]["form"] = "section_ref"
    row = admit(doc)
    assert row["status"] == "ok" and row["admitted"] is True, row
    assert [(r["form"], r["status"]) for r in row["references"]] == [("section_ref", "navigation"),
                                                                      ("pronoun", "navigation")]
    result = python(doc, tmp_path)
    assert (result["report_id"], result["references"]) == (row["report_id"], row["references"])


def test_formula_producing_mentions_still_need_discourse_wording(lean, tmp_path):
    """Only location bindings are exempt: the demonstrative naming an entity in the naming clause
    (`Claude’s`) is a recorded reference again, and its unit is not discourse wording."""
    doc = example(mixed=False)
    doc["environment"] = environment(helps=True)
    doc["discourse"]["names"] = [{"constant": "claude", "display": "Claude", "scope": "doc"}]
    doc["discourse"]["mentions"][0]["target"] = {"kind": "entity", "name": "claude"}
    expected = "InvalidInput: discourse wording of u0214.s02.p1"
    assert rejected(doc, tmp_path) == (expected, expected)


# MIXED units: read as Python's `_parts` reads them, in both checkers.

@pytest.mark.parametrize("change, expected", [
    (lambda u: u["parts"][0].pop("status"), "MIXED parts must partition their parent span"),
    (lambda u: u["parts"][1].update(span=[A2 + 1, END]), "MIXED parts must partition their parent span"),
    (lambda u: u.update(parts=u["parts"][:1]), "MIXED unit needs partitioned parts"),
    (lambda u: u.update(extra=1), "invalid MIXED unit schema"),
    (lambda u: u["parts"][0].update(id="u0214.s02"), "duplicate or invalid unit id"),
], ids=["part-status", "gap", "one-part", "schema", "parent-id"])
def test_mixed_units_are_checked_alike(lean, tmp_path, change, expected):
    doc = example()
    change(doc["units"][1])
    assert rejected(doc, tmp_path) == (expected, expected)


def test_parts_are_the_units(lean, tmp_path):
    """The parent's id names no unit: a mention or content name citing it is rejected in both."""
    doc = example()
    doc["discourse"]["mentions"][1]["unit"] = "u0214.s02"
    expected = "InvalidInput: mention m-it names an unknown unit"
    assert rejected(doc, tmp_path) == (expected, expected)


# Stated limitations (3.4, 11): abstentions, never a rejection and never a Python-only verdict.

def abstains(front, tmp_path, feature, source=SOURCE):
    row = admit(front, source)
    assert row == {"id": "c", "status": "error", "error": f"NotImplemented: {feature}"}, row
    with pytest.raises(UnsupportedProfile, match=feature):
        python(front, tmp_path, source)


def test_no_claim_graph_abstains(lean, tmp_path):
    doc = example()
    del doc["graph"]
    abstains(doc, tmp_path, "a document without a claim graph")


def test_fenced_content_abstains(lean, tmp_path):
    doc = example(mixed=False)
    doc["environment"] = environment(helps=True)
    rest = doc["units"][2]
    doc["units"][2] = {"id": rest["id"], "span": rest["span"], "kind": "asserted", "meaning": "specified",
                       "support": "assumption", "surface": "english", "content": {"fence": rest["id"]}}
    del doc["discourse"]["mentions"][1]
    abstains(doc, tmp_path, "fenced English or strict content",
             SOURCE + "```ve u0214.s02.p2\nClaude helps.\n```\n")


def test_norm_content_abstains(lean, tmp_path):
    doc = example(mixed=False)
    doc["environment"] = environment(profiles=["norms@0"] + PROFILES, helps=True)
    rest = doc["units"][2]
    doc["units"][2] = {"id": rest["id"], "span": rest["span"], "kind": "norm", "meaning": "specified",
                       "support": "assumption",
                       "content": {"norm": {"name": "r1", "force": "permitted", "subject_sort": "agent",
                                            "condition": ["top"], "action": "helps"}}}
    del doc["discourse"]["mentions"][1]
    row = admit(doc)
    assert row["status"] == "error" and row["error"].startswith("NotImplemented: norm content"), row
    with pytest.raises(UnsupportedProfile):
        python(doc, tmp_path)


def test_soft_norms_profile_is_unsupported(lean, tmp_path):
    doc = example()
    doc["environment"] = environment(profiles=["relational-fol@0", "soft-norms@0", "ve.discourse@1"])
    row = admit(doc)
    assert row["error"] == "UnsupportedProfile: Unsupported profile soft-norms@0", row
    with pytest.raises(VEError, match="soft-norms@0"):
        python(doc, tmp_path)

