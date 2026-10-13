"""ME-0 labels: VE's own paper, E1 (`ve-paper-e1/source-04-e1.md`, v001-v089) and the appendix rows of the
per-template differences (`ve-paper-e1/source-appendix-per-template.md`, a001-a007).

Stated counts are W6a facts (dimensionless, support testimony). The graph certifies the count identities the text
states: 280 + 594 = 874 candidates, 874 x 5 views x 2 explanation states = 8,740 trials, and 9 + 3 = 12 templates.
Rates, intervals and statistics are UNFORMALISED (`calc`, `calc-data`, `calc-stats`).
"""
from __future__ import annotations

import re
from pathlib import Path

TARGET = "ve-paper-e1"
SOURCES = [("source-04-e1.md", "v"), ("source-appendix-per-template.md", "a")]
APPENDIX = (Path(__file__).resolve().parents[3] / "docs/research/evidence/math-evidence" / TARGET /
            "source-appendix-per-template.md").read_text(encoding="utf-8")

UNITS = {
    "token": {"scale": "1", "display": {"kind": "decimal", "label": "tokens"}},
    "rate_difference": {"scale": "1000", "display": {"kind": "decimal", "label": "false-approval difference"}},
}

COUNTS = {
    "base_items": "scored base items", "templates": "authored templates", "candidates": "scored candidates",
    "equivalent_candidates": "candidates equivalent to their reference",
    "non_equivalent_candidates": "candidates not equivalent to their reference",
    "views": "views per candidate", "explanation_states": "explanation states (present, absent)",
    "trials_per_judge": "E1 sign-off trials per judge", "failed_trials": "failed E1 sign-off trials",
    "e1b_calls_per_judge": "E1b calls per judge", "weakening_candidates": "weakening candidates",
    "templates_with_weakening": "templates containing a weakening",
    "templates_without_weakening": "templates containing no weakening",
}
CONSTANTS: dict[str, tuple[str, str, str]] = {
    name: ("dimensionless", desc, f"the number of {desc}") for name, desc in COUNTS.items()}
CONSTANTS["response_cap"] = ("token", "response cap of both scored judges", "the response cap")


def _c(tag, name):
    return ["const", tag, name]


def _n(name, value):
    return ["eq", _c("dimensionless", name), ["num", "dimensionless", value]]


def both(*fs):
    out = fs[-1]
    for f in reversed(fs[:-1]):
        out = ["and", f, out]
    return out


ROWS = {}
for line in APPENDIX.splitlines():
    m = re.match(r"\| (\d+)B AWQ \| (P\d) [a-z]+ \| (.*?) \| ([0-9.]+) \|", line)
    if not m:
        continue
    facts = []
    for t, v in re.findall(r"(t\d\d): ([+-][0-9.]+)", m.group(3)):
        name = f"diff_{m.group(1)}b_{m.group(2).lower()}_{t}"
        CONSTANTS[name] = ("rate_difference", f"{m.group(1)}B {m.group(2)} per-template FA difference, {t}",
                           f"the {m.group(1)}B {m.group(2)} difference for template {t}")
        facts.append(["eq", _c("rate_difference", name), ["decimal", "rate_difference", v.lstrip("+")]])
    ROWS[(m.group(1), m.group(2))] = (both(*facts), f"| {m.group(4)} |")

L, U, C = "L", "U", "C"
LABELS = {
    "v001": ("meta", L), "v002": ("meta", L),
    "v003": ("quantity", C, both(_n("base_items", "96"), _n("templates", "12"), _n("candidates", "874"),
                                 _n("equivalent_candidates", "280"), _n("non_equivalent_candidates", "594"))),
    "v004": ("exposition", L), "v005": ("exposition", L), "v006": ("exposition", L), "v007": ("exposition", L),
    "v008": ("quantity", U, "approximation"),
    "v009": ("quantity", C, both(_n("views", "5"), _n("explanation_states", "2"), _n("trials_per_judge", "8740"))),
    "v010": ("exposition", L), "v011": ("exposition", L),
    "v012": ("mixed", [(None, "exposition", L),
                       ("receive the same 400-token", "quantity", C,
                        ["eq", _c("token", "response_cap"), ["num", "token", "400"]])]),
    "v013": ("mixed", [(None, "exposition", L),
                       ("no E1 sign-off trial failed", "quantity", C, _n("failed_trials", "0"))]),
    "v014": ("mixed", [(None, "exposition", L),
                       ("adding\n4,370 calls", "quantity", C, _n("e1b_calls_per_judge", "4370"))]),
    "v015": ("exposition", L),
    "v016": ("comparison", U, "calc"),
    "v017": ("comparison", U, "approximation"),
    "v018": ("comparison", U, "calc"),
    "v019": ("quantity", U, "approximation"),
    "v020": ("exposition", L), "v021": ("exposition", L),
    "v022": ("comparison", U, "approximation"),
    "v023": ("exposition", L), "v024": ("meta", L), "v025": ("exposition", L), "v026": ("exposition", L),
    "v027": ("exposition", L),
    "v028": ("empirical claim", U, "calc-data"),
    "v029": ("meta", L),
    **{f"v{i:03d}": ("definition", U, "calc-stats") for i in range(30, 35)},
    "v035": ("empirical claim", U, "calc-stats"), "v036": ("empirical claim", U, "calc-stats"),
    "v037": ("hedge", U, "attitudes"),
    "v038": ("meta", L), "v039": ("exposition", L), "v040": ("meta", L), "v041": ("meta", L),
    "v042": ("hedge", U, "attitudes"),
    "v043": ("comparison", U, "calc-stats"),
    "v044": ("meta", L), "v045": ("meta", L), "v046": ("meta", L),
    "v047": ("definition", U, "calc"),
    "v048": ("definition", U, "calc-stats"), "v049": ("definition", U, "calc-stats"),
    "v050": ("quantity", U, "calc-data"),
    "v051": ("empirical claim", U, "calc-stats"),
    "v052": ("quantity", U, "calc-data"),
    "v053": ("quantity", U, "calc-stats"),
    "v054": ("definition", U, "calc-stats"),
    "v055": ("meta", L), "v056": ("meta", L), "v057": ("meta", L),
    "v058": ("table", L), "v059": ("table", L),
    **{f"v{i:03d}": ("table", U, "calc-stats") for i in range(60, 66)},
    "v066": ("definition", U, "calc-stats"),
    "v067": ("quantity", U, "calc-stats"),
    "v068": ("empirical claim", U, "calc-stats"), "v069": ("empirical claim", U, "calc-stats"),
    "v070": ("exposition", L),
    "v071": ("caption", L),
    "v072": ("meta", L),
    "v073": ("definition", U, "calc-stats"),
    "v074": ("exposition", L), "v075": ("exposition", L),
    "v076": ("quantity", U, "calc-stats"),
    "v077": ("hedge", U, "attitudes"),
    "v078": ("meta", L), "v079": ("meta", L),
    "v080": ("definition", U, "calc-data"),
    "v081": ("meta", L),
    "v082": ("quantity", C, both(_n("weakening_candidates", "243"), _n("templates_with_weakening", "9"),
                                 _n("templates_without_weakening", "3"))),
    "v083": ("meta", L),
    "v084": ("definition", U, "calc-stats"),
    "v085": ("comparison", U, "calc"),
    "v086": ("quantity", U, "calc-stats"),
    "v087": ("hedge", U, "attitudes"), "v088": ("hedge", U, "attitudes"),
    "v089": ("exposition", L),
    "a001": ("meta", L), "a002": ("table", L), "a003": ("table", L),
}
for uid, key in zip(("a004", "a005", "a006", "a007"), (("14", "P1"), ("14", "P2"), ("32", "P1"), ("32", "P2"))):
    formula, anchor = ROWS[key]
    LABELS[uid] = ("mixed", [(None, "table", C, formula), (anchor, "table", U, "calc-stats")])


def graph(content, prefix, env, prove, q):
    if prefix != "v":
        return None
    nodes = [{"name": "inventory", "quantity": content["v003"], "unit": "v003"},
             {"name": "trials", "quantity": content["v009"], "unit": "v009"},
             {"name": "weakenings", "quantity": content["v082"], "unit": "v082"}]
    d = "dimensionless"
    claims = [
        ("candidates_partition", ["eq", _c(d, "candidates"),
                                  ["add", d, _c(d, "equivalent_candidates"), _c(d, "non_equivalent_candidates")]],
         ["inventory"]),
        ("trials_cross_views_and_explanations",
         ["eq", _c(d, "trials_per_judge"), ["scale", d, "5", ["scale", d, "2", _c(d, "candidates")]]],
         ["inventory", "trials"]),
        ("templates_partition", ["eq", _c(d, "templates"),
                                 ["add", d, _c(d, "templates_with_weakening"), _c(d, "templates_without_weakening")]],
         ["inventory", "weakenings"]),
    ]
    by = {n["name"]: n["quantity"] for n in nodes}
    for name, formula, premises in claims:
        cert = prove(env, [by[p] for p in premises], q(formula))
        if cert is None:
            raise SystemExit(f"no certificate for {name}")
        nodes.append({"name": name, "quantity": q(formula), "premises": premises, "certificate": cert})
        by[name] = q(formula)
    names = [c[0] for c in claims]
    root = q(both(*[by[n]["formula"] for n in names]))
    nodes.append({"name": "count_identities", "quantity": root, "premises": names,
                  "certificate": prove(env, [by[n] for n in names], root)})
    return {"root": "count_identities", "nodes": nodes}


def _control(specs):
    """Negative control: "594 non-equivalent" becomes 595 in v003; the certificate built for the true count is
    kept, so only Lean's replay can catch it."""
    kind, status, formula = specs["v003"]
    specs["v003"] = (kind, status, _swap(formula, ["num", "dimensionless", "594"], ["num", "dimensionless", "595"]))
    return specs


def _swap(formula, old, new):
    if formula == old:
        return new
    return [_swap(x, old, new) for x in formula] if isinstance(formula, list) else formula


CONTROL = ("source-04-e1.md", _control)
