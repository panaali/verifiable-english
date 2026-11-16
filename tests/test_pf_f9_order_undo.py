"""pf-f9-order-undo: the order of 4.1's two safeguard-selection steps is again a self-declared ET gap.

The orchestrator's ruling (record-void-astra 2026-11-15 section C, finding 1.15; DRI decisions 2026-11-15
record-void-ruling and 2026-11-16 adv0244 item 2) keeps the three f9 units UNRESOLVED and does not make the "order
follows" record correction that pf-f7-timed-act carried (94167f21d4). These tests pin the undo: f9-risk-paths' header,
act legend and unit record each declare the order not formalised (ET, PLAN O7); no rule or legend says the order
follows; pf-f7-timed-act's other f9 lines stay.
"""
import json
from pathlib import Path

from tests.test_pf_fidelity_fix import T, V

PF = Path(__file__).resolve().parents[1] / "usecases" / "openai-preparedness"
ORDER_CLAIM = "order follows"


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
    assert ORDER_CLAIM not in (PF / "rules.d1.ve").read_text()
    assert ORDER_CLAIM not in (PF / "environment.d1.json").read_text()
    assert ORDER_CLAIM not in json.dumps(V.environment(), ensure_ascii=False)


def test_pf_f7_timed_act_f9_lines_are_kept():
    """The undo is of the order sentence only: f9-specific's and f9-efficacy's 'facts are not classified' records and
    f9-efficacy's quoted legend stay."""
    assert "per-path facts are not classified" in block("f9-specific").source
    assert "per-safeguard facts are not classified" in block("f9-efficacy").source
    assert legend("efficacy_methods_per_safeguard") == (
        "4.1: “For each identified safeguard, we identify methods to measure their efficacy” (the third "
        "safeguard-selection step)")
