"""pf-f7-timed-act: the condition tests of the PF split-unit wording round (architect ruling pf-split-units-20261115,
section 2; DRI decision 2026-11-15, arch-round6 items 1 and 2; PLAN 12 item 29).

The round is wording only: no answer may move against the snapshot of results.json taken at the merge base
(saved with the batch), and each signed fix is pinned in the case's own files. Parts A (f7-evaluations), B1
(f1-misuse-bio's own act) and B4 (f16-without's guard) are not in this round: each needs a DRI ruling (REPORT).
"""
import json
import re
from pathlib import Path

import tests.omission_rule as omission
from tests.test_pf_fidelity_fix import T, V

REPO = Path(__file__).resolve().parents[1]
PF = REPO / "usecases" / "openai-preparedness"
SNAPSHOT = REPO / "docs/usecases/openai-preparedness/pf-f7-timed-act/answers-at-merge-base.json"


def legend(name):
    return V.environment()["vocabulary"]["predicates"][name]["description"]


def block(block_id):
    return next(b for b in T.rule_blocks() if b.id == block_id)


def guard_atoms(block_id):
    return set(re.findall(r'"unary", "([a-z_]+)"', json.dumps(json.loads(T.parsed_rule(block_id))["guard"])))


def plan12_item(number):
    section = (PF / "PLAN.md").read_text().split("## 12.")[1].split("## 13.")[0]
    return re.search(rf"^{number}\. .*?(?=^\d+\. |^\*\*|\Z)", section, re.S | re.M)[0]


# --- (a) the moved check -------------------------------------------------------------------------------------------

def test_no_pf_answer_moved_against_the_merge_base_snapshot():
    """Every keyed answer VE gives equals the one it gave at the merge base, and the key column equals the frozen
    answer-key.json: `moved` is empty."""
    snapshot = json.loads(SNAPSHOT.read_text())["answers"]
    rows = {row["id"]: row for row in json.loads((PF / "results.json").read_text())["comparison"]}
    key = {item["id"]: item["key"] for item in json.loads((PF / "answer-key.json").read_text())["items"]}
    assert len(snapshot) == len(rows) == len(key) == 239
    assert {i: row["key"] for i, row in rows.items()} == key == {i: s["key"] for i, s in snapshot.items()}
    moved = sorted(i for i, s in snapshot.items() if rows[i]["ve"] != s["ve"])
    assert moved == []


# --- (c) the dropped conjunct --------------------------------------------------------------------------------------

def test_f16_sag_recommend_tests_only_its_own_condition():
    """"For each deployment under the Preparedness Framework, providing recommendations ...": one condition, so the
    rule's guard is `framework_deployment` alone, with no `covered` conjunct (P4)."""
    assert guard_atoms("f16-sag-recommend") == {"framework_deployment"}
    assert "is covered" not in block("f16-sag-recommend").text


# --- the legends of the signed units -------------------------------------------------------------------------------

def test_critical_standard_legend_names_the_rows_object_of_specified():
    """f1-halt: what the row leaves unspecified is the safeguards and security controls (CYB-C: their standards),
    not "the Critical standard"; the condition stays a guard atom of both f1-halt rules."""
    text = legend("critical_standard_unspecified")
    assert "has not yet specified" in text and "{0}" in text
    assert "“Until we have specified safeguards and security controls that would meet a Critical standard”" in text
    assert "“safeguards and security controls standards that would meet a Critical standard”" in text
    assert "the Critical standard has not yet been specified" not in text
    for block_id in ("f1-halt-strict", "f1-halt-default"):
        assert "critical_standard_unspecified" in guard_atoms(block_id)


def test_deeper_testing_legend_keeps_a_deployment():
    """f15-third-party, item (3) of its row: the deeming is about a deployment."""
    text = legend("deeper_testing_warranted")
    assert "deems that the deployment at {0} warrants deeper testing of Tracked Categories of capability" in text
    assert "deeper_testing_warranted" in guard_atoms("f15-third-party")


def test_board_guard_legend_is_the_open_term_form_with_no_decider():
    """f16-board-reverse/-mandate: "Where necessary" names no judge; the legend says the decider is unstated (as
    OT13) and no longer has the Board find it necessary. The predicate is not renamed."""
    text = legend("board_finds_necessary")
    assert "“Where necessary”" in text and "the decider is unstated" in text and "OT13" in text
    assert "Board finds" not in text
    for block_id in ("f16-board-reverse", "f16-board-mandate"):
        assert "board_finds_necessary" in guard_atoms(block_id)


def test_efficacy_legend_quotes_its_sentence():
    """f9-efficacy: the legend quotes 4.1's sentence, not the bare pointer the 2026-11-12 translation rule forbids."""
    text = legend("efficacy_methods_per_safeguard")
    assert "“For each identified safeguard, we identify methods to measure their efficacy”" in text
    assert text != "4.1: third safeguard-selection step"


def test_risk_paths_order_follows_from_each_of_those():
    """f9-risk-paths: header and legend give the order's ground, and neither declares it unformalised."""
    for text in (block("f9-risk-paths").source, legend("risk_paths")):
        assert "the order follows from the second step's 'each of those'" in text
        assert "not formalised" not in text


def test_f9_record_lines_and_kept_legend_words():
    """f9-specific and f9-efficacy each record their limit in one line (header and PLAN 12 item 29); f9-specific's
    legend keeps "that either exist or should be implemented"."""
    assert "per-path facts are not classified" in block("f9-specific").source
    assert "per-safeguard facts are not classified" in block("f9-efficacy").source
    item = plan12_item(29)
    assert "`f9-specific` records its limit in one line: per-path facts are not classified" in item
    assert "`f9-efficacy` records its" in item and "per-safeguard facts are not classified" in item
    assert "that either exist or should be implemented" in legend("specific_safeguards_per_path")


def test_plan12_item_29_names_only_the_units_it_records():
    """The wording fixes add no record to the units they repair: item 29 names a unit only where it records one (the
    two f9 limits and the dropped conjunct), and the other repaired units keep the record paths they had."""
    item = plan12_item(29)
    named = set(re.findall(r"\b(f\d+-[a-z0-9-]*[a-z0-9])\b", item))
    assert named == {"f9-specific", "f9-efficacy", "f16-sag-recommend"}
    repaired = ("f1-halt-strict", "f1-halt-default", "f15-third-party", "f16-board-reverse", "f16-board-mandate",
                "f9-risk-paths")
    records = omission.record_paths("openai-preparedness", repaired)
    # the record paths each unit had at the merge base (measured with the same rule), the `report` path left out:
    # it reads batch reports, which no permanent test pins (D4)
    assert {u: [p for p in records.get(u, []) if p != "report"] for u in repaired} == {
        "f1-halt-strict": ["mistag", "loss"], "f1-halt-default": ["mistag"],
        "f15-third-party": ["loss", "loss", "plan12"], "f16-board-reverse": ["mistag", "plan12"],
        "f16-board-mandate": ["plan12"], "f9-risk-paths": []}
