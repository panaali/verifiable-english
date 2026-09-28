"""Build `news-w6a.ve.md`: the news article as a W6a quantity document.

The source is `source.md` byte for byte. Units partition it; the numeric
clauses of rows 1, 7, 13, 15, 21, 22, 23 and 24 carry Lean-admitted quantity
statements from `w6a-quantity-fixtures.json`, attributed or projected figures
keep their attributed kind and enter the claim graph only through bridge
leaves, and the S12 year keeps both readings of "not ... until". Every other
clause is recorded with its reason; the relational claims of those clauses live
in `claims.ve` on the relational route. The graph certifies the fixture's
consequences (`ve-quantity-certificate@1`, found by `prove_quantity`; Lean
checks them). Deterministic: rerun to regenerate; tests compare the output.

    python usecases/news-article/build_w6a_document.py [--check]

It also writes `coverage.json`, the measured source partition.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from ve.environment import Environment  # noqa: E402
from ve.model import FiniteModel  # noqa: E402
from ve.units import erased_environment, prove_quantity, quantity_meaning_id  # noqa: E402

OUTPUT = HERE / "news-w6a.ve.md"
COVERAGE = HERE / "coverage.json"
FIXTURE = json.loads((HERE / "w6a-quantity-fixtures.json").read_text())
SOURCE = (HERE / "source.md").read_bytes()


def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def eq(const, tag, amount):
    return ["eq", ["const", tag, const], ["decimal", tag, amount]]


def both(*formulas):
    result = formulas[-1]
    for f in reversed(formulas[:-1]):
        result = ["and", f, result]
    return result


FOMC_EXPECTS = ["attributed", "fomc", "expects", "asserted"]
FOMC_SAYS = ["attributed", "fomc", "says", "asserted"]
WARSH_PROMISED = ["attributed", "warsh", "promised", "asserted"]


def skip(reason, kind="exposition", support="none"):
    """A clause without quantity content. A reported claim whose formalisation
    is blocked keeps the blocking reason as its kind."""
    if kind == "asserted":
        kind = ["unformalised", reason]
    return {"kind": kind, "meaning": {"unformalised": reason}, "support": support}


def fact(formula, kind="asserted", support="testimony", meaning="specified"):
    return {"kind": kind, "meaning": meaning, "support": support, "content": {"quantity": q(formula)}}


# Each unit starts at its anchor (the first occurrence after the previous
# anchor) and runs to the next one; the first starts at byte 0.
UNITS = [
    ("# Source", "preamble", skip("provenance_metadata", "meta")),
    ("1. The Federal Reserve raised", "s1_date",
     fact(["date_on", ["const", "day", "decision_date"], ["date", "2026-09-16"]])),
    (" and signaled that further", "s1_rest", skip("relational_route_claims_ve")),
    ("2. President Trump had promised", "s2_causes", skip("relational_route_claims_ve")),
    ("quarter-percentage-point rate increase", "s2_move", skip("missing_old_range", "asserted", "testimony")),
    ("taking the target range to", "s2_range",
     fact(both(eq("new_target_lower", "bp", "3.75"), eq("new_target_upper", "bp", "4.00")))),
    ("3. New projections show 16 of the 18", "s3_count", skip("count_exceeds_bound", "asserted", "testimony")),
    ("4. Warsh again did not submit", "s4_s5", skip("relational_route_claims_ve")),
    ("6. Contrary to that expectation", "s6_framing", skip("figurative_or_vague")),
    ("4.00%-4.25% range", "s6_range",
     fact(both(eq("projected_range_lower", "bp", "4.00"), eq("projected_range_upper", "bp", "4.25")),
          FOMC_EXPECTS)),
    (" by the end of 2026 and to remain", "s6_years",
     fact(both(eq("projected_reach_year", "calendar_year", "2026"),
               eq("projected_remain_year", "calendar_year", "2027")),
          FOMC_EXPECTS, meaning={"open": ["projection_horizon"]})),
    ("7. The FOMC's policy statement said", "s7_quote", skip("vague_timelier", "exposition")),
    ("2% goal,", "s7_goal", fact(eq("statement_goal", "bp", "2"), FOMC_SAYS)),
    (" issued after a two-day meeting", "s7_rest", skip("relational_route_claims_ve")),
    ("8. The statement gave no forward", "s8_s10", skip("relational_route_claims_ve")),
    ("11. The Fed's new quarterly", "s11_pce",
     fact(both(eq("pce_september_estimate", "bp", "3.7"), eq("pce_june_estimate", "bp", "3.6")))),
    ("12. Inflation is now not projected", "s12_target", fact(eq("target_rate", "bp", "2"))),
    (" until 2029", "s12_year", {"kind": FOMC_EXPECTS, "meaning": "specified", "support": "testimony"}),
    (" — a year later than previously", "s12_later", skip("missing_previous_expectation", "asserted", "testimony")),
    ("13. Projected economic growth was raised slightly", "s13_slightly", skip("vague_degree")),
    ("from 2.2% to 2.3%;", "s13_growth",
     fact(both(eq("growth_old_projection", "bp", "2.2"), eq("growth_new_projection", "bp", "2.3")),
          FOMC_EXPECTS)),
    (" the projected year-end unemployment", "s13_unemployment",
     fact(both(eq("unemployment_old_projection", "bp", "4.3"), eq("unemployment_new_projection", "bp", "4.1")),
          FOMC_EXPECTS)),
    ("14. Warsh has pledged", "s14_goal", fact(eq("pledged_goal", "bp", "2"), WARSH_PROMISED)),
    (' "clearly and at sufficient speed"', "s14_rest", skip("vague_pledge_manner")),
    ("\n## Direct quotation", "quotation", skip("duplicate_of_paraphrase", "meta")),
]

YEAR_EQ = ["eq", ["const", "calendar_year", "first_projected_target_year"], ["decimal", "calendar_year", "2029"]]
YEAR_LB = ["le", ["decimal", "calendar_year", "2029"], ["const", "calendar_year", "first_projected_target_year"]]

OPEN_TERMS = [{"name": "projection_horizon", "arguments": [], "decided_by": "reader",
               "necessary": [], "sufficient": [],
               "factors": ["'by the end of 2026' and 'remain there through the end of 2027' are "
                           "temporal obligations of a projection, not observed future rates"],
               "precedents": [], "jurisdiction": "news_reading", "version": 1}]


def spans():
    starts, cursor = [], 0
    for anchor, _, _ in UNITS:
        at = SOURCE.find(anchor.encode(), cursor)
        if at < 0:
            raise SystemExit(f"anchor not found after byte {cursor}: {anchor!r}")
        starts.append(0 if not starts else at)
        cursor = at + 1
    return list(zip(starts, starts[1:] + [len(SOURCE)]))


def environment():
    raw = copy.deepcopy(FIXTURE["environment"])
    raw["profiles"] = ["documents@1", *raw["profiles"]]
    return raw


def distinguishing_model(env):
    data = copy.deepcopy(FIXTURE["model"])
    data["constants"]["first_projected_target_year"] = "2030"
    return FiniteModel.from_dict(erased_environment(env), data)


def build():
    raw = environment()
    env = Environment(raw)
    units = []
    for (anchor, uid, spec), span in zip(UNITS, spans()):
        unit = {"id": uid, "span": list(span), **spec}
        if "content" in spec:
            unit["meaning_id"] = quantity_meaning_id(env, spec["content"]["quantity"])
        units.append(unit)
    model = distinguishing_model(env)
    readings = []
    for rid, formula, other in (("equal", YEAR_EQ, "lower_bound"), ("lower_bound", YEAR_LB, "equal")):
        readings.append({"id": rid, "kind": "asserted", "meaning_id": quantity_meaning_id(env, q(formula)),
                         "content": q(formula),
                         "admission": {"who": "w6a_builder",
                                       "why": ("'not projected to reach ... until 2029' as the first year "
                                               if rid == "equal" else
                                               "'not ... until 2029' read only as a lower bound "),
                                       "distinguishing_models": {other: model.model_id}}})
    reading_sets = [{"id": "first_target_year", "unit": "s12_year", "version": 1, "status": "open",
                     "readings": readings, "models": {model.model_id: model.to_dict()}}]

    content = {u["id"]: u["content"]["quantity"] for u in units if "content" in u}
    nodes = [{"name": "n01", "quantity": content["s1_date"], "unit": "s1_date"},
             {"name": "n07", "quantity": content["s2_range"], "unit": "s2_range"},
             {"name": "n13", "quantity": content["s6_range"], "label": "bridge:accepts(fomc,s6_range)"},
             {"name": "n13y", "quantity": content["s6_years"], "label": "bridge:accepts(fomc,s6_years)"},
             {"name": "n15", "quantity": content["s7_goal"], "label": "bridge:accepts(fomc,s7_goal)"},
             {"name": "n21", "quantity": content["s11_pce"], "unit": "s11_pce"},
             {"name": "n22", "quantity": content["s12_target"], "unit": "s12_target"},
             {"name": "n22y", "quantity": q(["or", YEAR_EQ, YEAR_LB]),
              "label": "readings:first_target_year@1:all"},
             {"name": "n23g", "quantity": content["s13_growth"], "label": "bridge:accepts(fomc,s13_growth)"},
             {"name": "n23u", "quantity": content["s13_unemployment"],
              "label": "bridge:accepts(fomc,s13_unemployment)"},
             {"name": "n24", "quantity": content["s14_goal"], "label": "bridge:accepts(warsh,s14_goal)"}]
    by_name = {n["name"]: n for n in nodes}
    consequences = {c["id"]: c for c in FIXTURE["consequences"]}
    derived = [("N07-order", ["n07"]), ("N13-order", ["n13"]), ("N13-years", ["n13y"]),
               ("N15-N24-same-goal", ["n15", "n24"]), ("N21-order", ["n21"]), ("N21-difference", ["n21"]),
               ("N22-year-lower-bound", ["n22y"]), ("N23-growth-increase", ["n23g"]),
               ("N23-unemployment-decrease", ["n23u"]), ("N23-unemployment-order", ["n23u"])]
    conclusions = []
    for cid, premises in derived:
        formula = YEAR_LB if cid == "N22-year-lower-bound" else consequences[cid]["formula"]
        certificate = prove_quantity(env, [by_name[p]["quantity"] for p in premises], q(formula))
        if certificate is None:
            raise SystemExit(f"no certificate for {cid}")
        node = {"name": cid, "quantity": q(formula), "premises": premises, "certificate": certificate}
        nodes.append(node)
        by_name[cid] = node
        conclusions.append(formula)
    root = q(both(*conclusions))
    names = [cid for cid, _ in derived]
    certificate = prove_quantity(env, [by_name[n]["quantity"] for n in names], root)
    nodes.append({"name": "news_consequences", "quantity": root, "premises": names,
                  "certificate": certificate})
    meta = {"format": "ve-document@1", "environment": raw, "units": units, "open_terms": OPEN_TERMS,
            "reading_sets": reading_sets, "graph": {"root": "news_consequences", "nodes": nodes}}
    return b"---\n" + json.dumps(meta, indent=1, ensure_ascii=False).encode() + b"\n---\n" + SOURCE


def partition(data):
    """The measured partition of the built document (`coverage.json`, read by
    tools/coverage_dashboard.py)."""
    import tempfile
    from ve.document import coverage, load_document
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / OUTPUT.name
        path.write_bytes(data)
        measured = coverage(load_document(path))
    return (json.dumps({"document": OUTPUT.name, **measured}, indent=1, sort_keys=True) + "\n").encode()


if __name__ == "__main__":
    data = build()
    measured = partition(data)
    if "--check" in sys.argv:
        sys.exit(0 if OUTPUT.read_bytes() == data and COVERAGE.read_bytes() == measured else 1)
    OUTPUT.write_bytes(data)
    COVERAGE.write_bytes(measured)
    print(f"wrote {OUTPUT} ({len(data)} bytes) and {COVERAGE}")
