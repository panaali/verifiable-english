"""date arithmetic, the promotion to main (Opus review of promote-date-arith-1126): B1, an offset that adds days or
weeks before months or years is refused (no order is picked); B2, each quantity report claim's `inputs` is bound to the
request (the node's `cal`/`cal_cmp` subtrees, in order), so a changed, dropped, added or reordered entry is
CheckerUnavailable."""
import copy
import json

import pytest

from tests import lean_routes
from tests.test_date_arith import FACTS, environment
from ve.admission import admit_document, bind_quantity_inputs
from ve.environment import Environment
from ve.errors import CheckerUnavailable
from ve.surface.dates import DateRuleError, lower_date_item

CLAIM = ("claim", "the date of claim")


def _condition(text):
    lowered = lower_date_item(environment(CLAIM), text, {"dates": {"the date of claim": "2026-07-31"}}, facts=FACTS)
    [premise] = [p for p in lowered["premises"] if p["formula"][0] == "implies"]
    return premise["formula"][1]


@pytest.mark.parametrize("offset", ["30 days and 1 month", "1 day and 1 month", "2 weeks and 1 year",
                                    "1 month and 2 days and 1 year", "1 year and 1 week and 1 month"])
def test_b1_days_or_weeks_before_months_or_years_is_refused(offset):
    """1 June 2026 plus 30 days and 1 month is 31 July months first and 1 August in written order: refused."""
    with pytest.raises(DateRuleError, match="CANNOT \\(DateRuleScope\\).*adds days or weeks before months"):
        _condition(f"If the date of claim is on 1 June 2026 plus {offset}, then the person is eligible.")


def test_b1_months_before_days_still_lowers_in_written_order():
    """Months then days is the order the lowering applies, so the written order is the one read."""
    cond = _condition("If the date of claim is on 1 June 2026 plus 1 month and 30 days, then the person is eligible.")
    assert json.dumps(cond).count('"plus_days", ["plus_months", ["date", "2026-06-01"], "1", "none"], "30"') == 1, cond


def test_b1_thirty_first_of_january_plus_a_day_and_a_month_is_scope_not_missing_day():
    """The review's second example: refused for its order (DateRuleScope), never read as 31 February."""
    with pytest.raises(DateRuleError, match="CANNOT \\(DateRuleScope\\)"):
        _condition("If the date of claim is on 31 January 2026 plus 1 day and 1 month, then the person is eligible.")


# --- B2: a report claim's inputs, bound to the request -----------------------------------------------------------

def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


CAL = ["cal", ["plus_months", ["date", "1960-06-27"], "792", "none"]]
CMP = ["cal_cmp", "before", ["date", "1960-01-01"], ["date", "1960-06-27"]]
BOTH = q(["and", ["date_on", ["const", "day", "pa_person"], CAL], CMP])
PLAIN = q(["date_on", ["const", "day", "pa_partner"], ["date", "2026-06-27"]])


def _document():
    return {"units": [{"id": "u", "span": [0, 10], "kind": "asserted", "content": BOTH}],
            "graph": {"root": "n", "nodes": [{"name": "n", "quantity": BOTH, "unit": "u"}]}}


def _env():
    raw = environment().to_dict()
    return Environment(raw | {"profiles": ["documents@1", *raw["profiles"]]})


@pytest.fixture(scope="module")
def admitted():
    if not lean_routes.SERVICE.exists():
        pytest.skip("build the Lean service first")
    document = _document()
    return document, admit_document(_env(), document)


def test_b2_lean_reports_each_cal_node_and_the_binder_accepts_it(admitted):
    document, row = admitted
    root = row["report"]["root"]
    assert [json.loads(x) for x in root["inputs"]] == [CAL, CMP]
    bind_quantity_inputs(document, row["report"])


@pytest.mark.parametrize("change", [
    lambda c: c["inputs"].__setitem__(0, json.dumps(["cal", ["plus_months", ["date", "1960-06-28"], "792", "none"]])),
    lambda c: c["inputs"].reverse(),
    lambda c: c["inputs"].pop(),
    lambda c: c["inputs"].append(c["inputs"][0]),
    lambda c: c.pop("inputs"),
    lambda c: c.__setitem__("inputs", []),
    lambda c: c["inputs"].__setitem__(1, json.loads(c["inputs"][1])),
    lambda c: c["inputs"].__setitem__(1, c["inputs"][1][:-1]),
], ids=["changed", "reordered", "dropped", "extra", "field-dropped", "empty", "not-a-string", "not-json"])
def test_b2_a_changed_inputs_entry_is_checker_unavailable(admitted, change):
    document, row = admitted
    report = copy.deepcopy(row["report"])
    change(report["root"])
    with pytest.raises(CheckerUnavailable, match="inputs are not bound"):
        bind_quantity_inputs(document, report)


def test_b2_inputs_on_a_claim_without_cal_nodes_is_checker_unavailable(admitted):
    """A node with no cal or cal_cmp node has no inputs; a reported claim of it with inputs is refused."""
    document, row = admitted
    document = copy.deepcopy(document)
    document["graph"]["nodes"].append({"name": "m", "quantity": PLAIN})
    report = copy.deepcopy(row["report"])
    report["assumptions"] = [{"name": "m", "quantity": PLAIN, "meaning_id": "0" * 64, "inputs": [json.dumps(CMP)]}]
    with pytest.raises(CheckerUnavailable, match="inputs are not bound"):
        bind_quantity_inputs(document, report)


def test_b2_the_relay_refuses_a_tampered_lean_answer(admitted, monkeypatch):
    """End to end: the quantity admission relay calls the binder on Lean's row."""
    import ve.backends.relay as relay
    document, _ = admitted
    real = relay.decide

    def tampered(mode, cases, *args, **kwargs):
        rows = real(mode, cases, *args, **kwargs)
        rows[0]["report"]["root"]["inputs"].reverse()
        return rows

    monkeypatch.setattr(relay, "decide", tampered)
    with pytest.raises(CheckerUnavailable, match="inputs are not bound"):
        admit_document(_env(), document)
