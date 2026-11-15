"""Safety-framework use case: src:4's TCL proximity commitment (row safety-framework-proximity-tcl).

1.2 "Similarly to CCLs, early warning evaluations will be used to assess the proximity of a model to a TCL and analyze
the risk posed, involving internal and external experts as needed" is carried by rule f6-tcl (F6's act; 1.3.3's
trigger, an alert threshold reached, carried to TCLs), no longer by unformalised('no_trigger_stated'). Three answers
move away from the frozen key, and each has a PLAN section-12 entry (item 27) beside the old key cell.
Ruling: reviews/dri-decisions-20261114-safety-framework-fidelity-fix-3.md item 2.
"""
import json
import re

from tests.pinned_source import pinned_source
from tests.test_safety_framework import HERE, RESULTS, _own_modules, build_document, translation  # noqa: F401

SENTENCE = ("Similarly to CCLs, early warning evaluations will be used to assess the proximity of a model to a TCL and "
            "analyze the risk posed, involving internal and external experts as needed.")
ANCHOR = "Similarly to CCLs, early warning evaluations will be used"
# The answers that moved, (old key cell, new VE answer), each pinned beside its PLAN section-12 entry.
MOVES = {"K2-L1/PROXIMITY": ("NONE", "ALL"), "K2-L5/PROXIMITY": ("NONE", "ALL"), "G3": ("ALL", "NONE")}
ENTRY = 27
BULLET = re.compile(r"^\s*- \*\*([A-Za-z0-9/-]+)\.\*\* Key: (.+?)\. Entry: \*\*([A-Z]+)\*\*\.", re.M)


def section_12(plan=None):
    text = (HERE / "PLAN.md").read_text() if plan is None else plan
    return text.split("\n## 12. ", 1)[1].split("\n## 13. ", 1)[0]


def key_findings(plan=None):
    """{answer id: (section-12 item, key cell, entry answer)} from every `- **<id>.** Key: k. Entry: **v**.` bullet."""
    found, item = {}, None
    for line in section_12(plan).splitlines():
        top = re.match(r"(\d+)\. \*\*", line)
        if top:
            item = int(top[1])
        bullet = BULLET.match(line)
        if bullet:
            assert bullet[1] not in found, f"two section-12 entries for {bullet[1]}"
            found[bullet[1]] = (item, bullet[2], bullet[3])
    return found


def check_findings(findings, comparison):
    """Every answer that disagrees with the key has its section-12 entry with that answer, and every entry of item
    ENTRY records an answer that moved off the key cell it names."""
    rows = {r["id"]: r for r in comparison}
    for row in comparison:
        if not row["agree"]:
            assert row["id"] in findings, f"{row['id']} moved off the key with no section-12 entry"
            assert findings[row["id"]][2] == row["ve"], row["id"]
    for answer, (item, key, entry) in findings.items():
        if item == ENTRY:
            row = rows[answer]
            assert (row["key"], row["ve"]) == (key, entry) and key != entry, f"{answer}: an entry with no answer move"


def test_the_three_answers_are_pinned_beside_their_section_12_entries():
    rows = {r["id"]: r for r in RESULTS["comparison"]}
    assert {i: (rows[i]["key"], rows[i]["ve"]) for i in MOVES} == MOVES
    assert {a: (key, entry) for a, (item, key, entry) in key_findings().items() if item == ENTRY} == MOVES
    keys = {i["id"]: i["key"] for i in json.loads((HERE / "answer-key.json").read_text())["items"]}
    assert {i: keys[i] for i in MOVES} == {i: old for i, (old, _) in MOVES.items()}
    item = section_12().split(f"\n{ENTRY}. ", 1)[1].split(f"\n{ENTRY + 1}. ", 1)[0]
    assert f'"{SENTENCE}"' in " ".join(item.split())
    check_findings(key_findings(), RESULTS["comparison"])


def test_a_move_without_its_entry_or_an_entry_without_a_move_fails():
    plan = (HERE / "PLAN.md").read_text()
    g3 = next(line for line in plan.splitlines() if line.lstrip().startswith("- **G3.** Key:"))
    rows = RESULTS["comparison"]
    try:
        check_findings(key_findings(plan.replace(g3 + "\n", "")), rows)
    except AssertionError as error:
        assert "G3 moved off the key" in str(error)
    else:
        raise AssertionError("a deleted section-12 entry passed")
    unmoved = [dict(r, ve=r["key"], agree=True) if r["id"] == "G3" else r for r in rows]
    try:
        check_findings(key_findings(plan), unmoved)
    except AssertionError as error:
        assert "G3: an entry with no answer move" in str(error)
    else:
        raise AssertionError("an entry with no answer move passed")


def test_src4_is_carried_by_a_rule_and_not_unformalised():
    units = [u for u in build_document.UNITS if u[0] == ANCHOR]
    assert len(units) == 1 and units[0][1] == "s12-tcl-proximity"
    assert units[0][2] == {"kind": "norm", "meaning": {"open": ["ot1_level_reached"]}, "support": "testimony",
                           "rule": "f6-tcl"}
    assert not any(u[2].get("meaning") == {"unformalised": "no_trigger_stated"} for u in build_document.UNITS)
    span = next(u for u in json.loads((HERE / "spans.json").read_text())["units"] if u["id"] == "s12-tcl-proximity")
    assert (span["status"], span["rule"], "reason" in span) == ("OPEN", "f6-tcl", False)
    blocks = {b.id: b for b in translation.rule_blocks()}
    tcl, ccl = blocks["f6-tcl"], blocks["f6"]
    assert tcl.when == () and f'F6, 1.2 "{SENTENCE[:-1]}"' in tcl.source
    # F6's act and trigger, for a tracked level instead of a critical one.
    assert tcl.text == ccl.text.replace("that level is critical.", "that level is tracked.") != ccl.text
    assert json.loads(translation.parsed_rule("f6-tcl"))["name"] == "f6-tcl"
    assert "f6-tcl" in translation.will_rules()   # a "will": RS0, narrowed by N1 as F6 is
    for answer in ("K2-L1/PROXIMITY", "K2-L5/PROXIMITY"):
        assert RESULTS["items"][answer]["details"]["-"] == {"holds": True, "rules": ["f6-tcl"]}
    source = pinned_source("safety-framework", skip=False)
    if source is not None:
        text = " ".join(source.read_text().split())
        assert text.count(SENTENCE) == 1
