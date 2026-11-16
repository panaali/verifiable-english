"""pf-f9-order-undo: the order of 4.1's two safeguard-selection steps is again a self-declared ET gap.

The orchestrator's ruling (record-void-astra 2026-11-15 section C, finding 1.15; DRI decisions 2026-11-15
record-void-ruling and 2026-11-16 adv0244 item 2) keeps the three f9 units UNRESOLVED and does not make the "order
follows" record correction that pf-f7-timed-act carried (94167f21d4). These tests pin the undo: f9-risk-paths' header,
act legend and unit record each declare the order not formalised (ET, PLAN O7); no rule or legend says the order
follows; pf-f7-timed-act's other f9 lines stay.
"""
import json
import re
from pathlib import Path

from tests.test_pf_fidelity_fix import T, V

PF = Path(__file__).resolve().parents[1] / "usecases" / "openai-preparedness"
# The struck claim in any wording a record has used: "the order follows from ..." (header, legend) and "the order of
# 4.1's two selection steps follows from the second step's ..." (PLAN 12 item 29). Matched on text with its whitespace
# folded, so a claim wrapped across lines is found.
ORDER_CLAIM_RE = re.compile(r"\border\b[^.;:]{0,80}?\bfollows\b|\bfollows from the second step\b", re.I)
SUPERSEDES_RE = re.compile(r"\bsupersedes item (\d+)\b")


def states_order_claim(text):
    """Whether the text says the order of 4.1's selection steps follows (the claim the ruling struck)."""
    return bool(ORDER_CLAIM_RE.search(" ".join(text.split())))


def plan12_items(plan_text):
    """PLAN.md section 12's numbered items: number -> text (up to the next item or bold batch header)."""
    section = plan_text.split("\n## 12.", 1)[1].split("\n## 13.", 1)[0]
    return {int(m[1]): m[0] for m in re.finditer(r"^(\d+)\. .*?(?=^\d+\. |^\*\*|\Z)", section, re.S | re.M)}


def superseded_items(items):
    """Item numbers a later PLAN 12 item says it supersedes ("supersedes item N", N earlier than the item)."""
    return {int(n) for number, text in items.items() for n in SUPERSEDES_RE.findall(" ".join(text.split()))
            if int(n) < number}


def live_plan_text(plan_text):
    """PLAN.md with every superseded PLAN 12 item removed: what the deviation log still states."""
    items = plan12_items(plan_text)
    for number in superseded_items(items):
        plan_text = plan_text.replace(items[number], "")
    return plan_text


def live_records():
    """Every text record of the case (rules, legends, spans, accounting, README, PLAN, harness files): path -> the
    text it still states. Batch REPORTs under docs/ are dated evidence (D4) and source/ is the framework's own text;
    neither is a live record."""
    out = {}
    for path in sorted(PF.rglob("*")):
        if not path.is_file() or {"__pycache__", "source"} & set(path.relative_to(PF).parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        out[path.relative_to(PF).as_posix()] = live_plan_text(text) if path.name == "PLAN.md" else text
    return out


def legend(name):
    return V.environment()["vocabulary"]["predicates"][name]["description"]


def block(block_id):
    return next(b for b in T.rule_blocks() if b.id == block_id)


def test_f9_risk_paths_header_declares_the_order_unformalised():
    """The f9-risk-paths header records the order 'first' states as event order, not formalised (its text before
    94167f21d4)."""
    assert ("; event order (ET, as PLAN O7): the order the word first states between the two selection steps is not "
            "formalised; the act with first would pass 80 characters, so the legend carries it") in block(
        "f9-risk-paths").source


def test_risk_paths_legend_declares_the_order_unformalised():
    """The risk_paths act legend (pf_vocabulary.py and the committed environment.d1.json) says the order is event
    order, not formalised."""
    text = legend("risk_paths")
    assert text.endswith("(the first step; 'first' is in this legend only, as the act with it would pass the "
                         "80-character limit; the order it states before the next step is event order, not "
                         "formalised: ET, as PLAN O7)")
    committed = json.loads((PF / "environment.d1.json").read_text())
    assert committed["vocabulary"]["predicates"]["risk_paths"]["description"] == text


def test_f9_risk_paths_unit_record_keeps_its_event_order_gap():
    """The unit record (spans.json, from build_document.UNTRANSLATED) keeps 'first' as an event_order gap."""
    units = [u for u in json.loads((PF / "spans.json").read_text())["units"] if u.get("rule") == "f9-risk-paths"]
    gaps = [g for u in units for g in u.get("untranslated", [])]
    assert any(g.get("reason") == "event_order" and "is not formalised" in g.get("detail", "") for g in gaps), gaps


def test_no_rule_or_legend_claims_the_order_follows():
    """No rules.d1.ve line and no vocabulary legend (generated or committed) says the order follows."""
    assert not states_order_claim((PF / "rules.d1.ve").read_text())
    assert not states_order_claim((PF / "environment.d1.json").read_text())
    assert not states_order_claim(json.dumps(V.environment(), ensure_ascii=False))


def test_no_live_record_of_the_case_claims_the_order_follows():
    """F1 (review of ccaa6de31d): PLAN 12 item 29 still said the legend and header derive the order from the second
    step. No live record of the case, in any wording, says the order follows: every file under the case directory,
    PLAN.md read without the PLAN 12 items a later item supersedes, and the generated vocabulary."""
    records = live_records()
    assert {"PLAN.md", "rules.d1.ve", "environment.d1.json", "spans.json", "pf_vocabulary.py"} <= set(records)
    assert [name for name, text in records.items() if states_order_claim(text)] == []
    assert not states_order_claim(json.dumps(V.environment(), ensure_ascii=False))


def test_plan12_records_the_undo_in_an_item_that_supersedes_item_29():
    """PLAN 12 records this item: a later item under the pf-f9-order-undo header supersedes item 29's sentence and
    says the order is event order, not formalised (ET), as item 27 does."""
    plan = (PF / "PLAN.md").read_text(encoding="utf-8")
    items = plan12_items(plan)
    assert states_order_claim(items[29])  # the history stays; it is superseded, not rewritten
    undo = [n for n, text in items.items() if 29 in superseded_items({n: text})]
    assert len(undo) == 1 and undo[0] > 29, undo
    text = " ".join(items[undo[0]].split())
    assert "event order, not formalised (ET, as O7)" in text and "`risk_paths`" in text
    assert not states_order_claim(text)
    section = plan.split("\n## 12.", 1)[1].split("\n## 13.", 1)[0]
    header = section[:section.index(items[undo[0]])].rstrip().rsplit("\n\n", 1)[-1]
    assert header.startswith("**`pf-f9-order-undo` (2026-11-16)"), header


def test_the_order_claim_detector_and_the_superseded_reader(tmp_path):
    """The detector finds each wording a record used, wrapped across lines, and not the case's other "follows"; a
    PLAN 12 item drops out of the live text only when a later item supersedes it."""
    assert states_order_claim("the order follows from the second step's 'each of those'")
    assert states_order_claim("say that the order of 4.1's two selection steps follows\n    from the second step's")
    assert states_order_claim("step ORDER Follows")
    assert not states_order_claim("This use case follows the method of safety-framework.")
    assert not states_order_claim("the order it states before the next step is event order, not formalised")
    plan = ("# P\n\n## 12. Log\n\n1. **A.** the order follows from the second step.\n\n"
            "2. **B (supersedes item 1).** event order.\n\n3. **C (supersedes item 4).** x.\n\n## 13. Files\n")
    assert superseded_items(plan12_items(plan)) == {1}
    assert not states_order_claim(live_plan_text(plan))
    assert states_order_claim(live_plan_text(plan.replace("supersedes item 1", "follows item 1")))


def test_pf_f7_timed_act_f9_lines_are_kept():
    """The undo is of the order sentence only: f9-specific's and f9-efficacy's 'facts are not classified' records and
    f9-efficacy's quoted legend stay."""
    assert "per-path facts are not classified" in block("f9-specific").source
    assert "per-safeguard facts are not classified" in block("f9-efficacy").source
    assert legend("efficacy_methods_per_safeguard") == (
        "4.1: “For each identified safeguard, we identify methods to measure their efficacy” (the third "
        "safeguard-selection step)")
