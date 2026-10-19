"""Asimov's v2 rules re-run with `permitted` completed `unspecified` (events-time-causation ET-8, fixture R2).

`python usecases/asimov-extended/asimov_unspecified.py` writes `unspecified-results.json`. The v2 environment
(`usecases/asimov-laws/environment.json`) completes `permitted` to allow, a modeling choice the source does not
make. Here the same 13 rules run on Lean's alternatives route with `norm-defaults@0` and `permitted` completed
`unspecified` ("the text does not say"): an action is clear only when it is clear under every admissible filling
of what the text leaves unsaid. What runs:

1. The 13 rules under the switched environment: one reading each, rendered back to the same text.
2. Conflict certificates found by Python's prover over the premises Lean binds and replayed by Lean.
3. The 9 distinct spec models and the 51 records of the extended case, decided by Lean's scenario check. A record
   with a `might` cell needs `risk@0`, which does not combine with the completion yet, so it is listed and not run.
   Each run record is decided under allow and deny too; under allow it must equal the extended case's committed
   v2 result (`results.json`), which ran on the risk route.
4. The three DILEMMA witnesses of the v2 README, each with the filling that leaves nothing unsaid permitted.

The extended rules (1-29) are not re-run: every one of their results is a `risk@0` decision.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import asimov_extended_cases as cases  # noqa: E402
from asimov_extended_cases import HARMS, HUMAN, HUMANITY, SELF, V2  # noqa: E402
from conformance.alternatives import cases as spec_cases  # noqa: E402
from conformance.alternatives import scenario  # noqa: E402
from tests import test_alternatives_fill as fill  # noqa: E402
from ve.alternatives import run_case  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.norm_english import parse_english, render_english  # noqa: E402

# The v2 README's nine distinct spec models (one name per model).
SPEC_MODELS = ("a", "b-A0", "b-A1", "c-7", "o-7", "d-full", "e", "j", "l5")
WITNESSES = ("b-A0", "b-A1", "j")
V2_FACTS = ("ordered", "injures_human", "injures_humanity", "protects_robot")
# A wall-clock limit per scenario in place of the route's CPU deadline (180 s): under `unspecified`,
# `R:dominated-action-when-threats-conflict` (four actions, two threats) takes about 145 s of Lean CPU.
TIMEOUT = 900.0


def environment(default="unspecified"):
    """v2's environment with `permitted` completed `default`; `unspecified` adds `norm-defaults@0`."""
    raw = json.loads((V2 / "environment.json").read_text())
    raw["vocabulary"]["predicates"]["permitted"]["regulated"]["default"] = default
    if default == "unspecified":
        raw["profiles"] = sorted({*raw["profiles"], "norm-defaults@0"})
    return raw


def checked(raw):
    """The 13 rules under `raw`: parsed with v2's rule names, one reading each, and rendered back to v2's text
    and to v2's manifest blocks (the manifest's identities move with the environment)."""
    source = (V2 / "rules.ve").read_text()
    manifest = json.loads((V2 / "rules.manifest.json").read_text())
    names = [block["name"] for block in manifest["blocks"]]
    doc = cases._named(Environment(raw), parse_english(Environment(raw), source), names)
    text, rendered = render_english(doc)
    return doc, {"rules": len(doc.rules), "same_text": text == source,
                 "same_blocks": rendered["blocks"] == manifest["blocks"],
                 "same_text_digest": rendered["text_digest"] == manifest["text_digest"]}


def source_case(raw, rules):
    return {"id": "asimov-v2", "environment": raw, "norms": rules, "units": []}


def conflict(src):
    """A certificate per conflict target, searched by `conflict_packages` of tests/test_alternatives_fill.py and
    replayed by Lean. Within the step budget the prover finds `permitted`'s certificate only over `Fill_T` without
    the slot premises; a certificate over fewer premises holds over all of them."""
    elaborated = run_case(src | {"kind": "alt-elaborate"})
    packages = fill.conflict_packages(src, elaborated, slots=False)
    if len(packages) < len(elaborated["conflict_targets"]):
        packages = {**fill.conflict_packages(src, elaborated), **packages}
    row = run_case(src | {"kind": "alt-conflict", "packages": packages})
    targets = [t["target"] for t in elaborated["conflict_targets"]]
    return packages, {"verdict": row.get("verdict"), "targets": targets,
                      "unproved": [t for t in targets if t not in packages],
                      "unspecified": elaborated.get("unspecified", [])}


def clear(row):
    """The clear actions of a scenario row and, under the completion, each action's status and evidence."""
    if row.get("status") != "ok":
        return {"error": row.get("error") or row.get("text")}
    (chooser,) = row["choosers"]
    if "statuses" not in chooser:
        return {"clear": chooser["clear"]}
    pairs = list(zip(chooser["alternatives"], chooser["statuses"], chooser["evidence"]))
    return {"clear": [a for a, status, _ in pairs if status == "clear"],
            "statuses": {a: [status, evidence] for a, status, evidence in pairs}}


def record_scenario(spec):
    """An extended-case record as a v2 alternatives scenario: its certain cells, harm classes and v2 facts. The
    order data (`ordered_before`, `outranks`) is not v2 vocabulary and no v2 rule reads it."""
    leads = [pair for pair, cell in spec["cells"].items() if cell == "leads"]
    facts = {name: [list(row) for row in spec["facts"][name]] for name in V2_FACTS}
    facts["harm_to"] = [[h, "r"] for h in SELF]
    return scenario(list(spec["actions"]), list(HARMS), leads, human=HUMAN, humanity=HUMANITY, facts=facts)


def decide(src, situations):
    return {name: clear(run_case(src | {"kind": "alt-validate", "scenario": s}, timeout=TIMEOUT))
            for name, s in situations.items()}


def records_section(sources, names=None):
    """The 51 records (or `names`): those with a `might` cell are listed and not run; the others are decided under
    each completion of `sources`. Under allow, each must equal the committed risk-route result of `results.json`."""
    records = cases.all_records()
    risky = sorted(n for n, spec in records.items() if "might" in spec["cells"].values())
    situations = {n: record_scenario(spec) for n, spec in records.items()
                  if n not in risky and (names is None or n in names)}
    committed = json.loads((HERE / "results.json").read_text())["records"]
    decided = {default: decide(src, situations) for default, src in sources.items()}
    results = {n: {"allow": decided["allow"][n]["clear"], "deny": decided["deny"][n]["clear"],
                   "unspecified": decided["unspecified"][n]} for n in situations}
    unspec = {n: r["unspecified"] for n, r in results.items()}
    return {"records": len(records), "not_run_need_risk": risky, "run": len(situations),
            "allow_differs_from_committed": sorted(n for n, r in results.items()
                                                   if sorted(r["allow"]) != sorted(committed[n]["base"]["clear"])),
            "clear": {default: sum(bool(r[default] if default != "unspecified" else r[default]["clear"])
                                   for r in results.values()) for default in sources},
            "unspecified_clear_not_clear_under_allow": sorted(
                n for n, r in results.items() if not set(r["unspecified"]["clear"]) <= set(r["allow"])),
            "with_undecided": sorted(n for n in situations
                                     if any(s == "undecided" for s, _ in unspec[n]["statuses"].values())),
            "results": results}


def witnesses(src, packages):
    """Each DILEMMA witness of the v2 README with the filling that permits nothing unsaid."""
    models = {item["id"]: item["scenario"] for item in spec_cases()}
    out = {}
    for name in WITNESSES:
        witness = {**models[name], "chooser": "r", "filling": {"unsaid__permitted": []}}
        row = run_case(src | {"kind": "alt-followable", "packages": packages, "witness": witness})
        out[name] = {"verdict": row.get("verdict"), "diagnosis": row.get("diagnosis")}
    return out


def compute():
    raw = environment()
    doc, check = checked(raw)
    rules = [rule.to_dict() for rule in doc.rules]
    sources = {default: source_case(environment(default), rules) for default in ("allow", "deny", "unspecified")}
    packages, conflict_result = conflict(sources["unspecified"])
    models = {item["id"]: item["scenario"] for item in spec_cases()}
    spec = decide(sources["unspecified"], {name: models[name] for name in SPEC_MODELS})
    return {"checked": check, "conflict": conflict_result,
            "spec_models": {"models": len(SPEC_MODELS), "clear": sum(bool(r["clear"]) for r in spec.values()),
                            "results": spec},
            "records": records_section(sources), "witnesses": witnesses(sources["unspecified"], packages)}


def main():
    results = compute()
    (HERE / "unspecified-results.json").write_text(json.dumps(results, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in results.items() if k != "records"} | {
        "records": {k: v for k, v in results["records"].items() if k != "results"}}, indent=1)[:6000])


if __name__ == "__main__":
    main()
