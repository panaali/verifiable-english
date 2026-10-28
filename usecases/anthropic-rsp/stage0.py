"""Stage 0 of the anthropic-rsp case (PLAN section 9): probes P1 to P8, the identifier lint (P7, M5) and the invention
audit (M6).

    python usecases/anthropic-rsp/stage0.py [--source PATH] [--check]

Writes `docs/usecases/safetyfw/anthropic-rsp/stage0.json`; `--check` fails if it would change. P1, P2, P5, P6 and P8
are cut from the pinned source (not committed), so without it `--check` checks the lint and the audit alone. D2 (P3)
and D3 (P4) hold no source prose; `routed_checked()` gives `build_document.py` their verdicts: a unit routed to D2 or
D3 is CHECKED in the master map exactly when its document is admitted with its evidence (certificates replayed).
Every verdict here is VE's (the Lean service and VE's quantity checker); this file only builds the inputs.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))
from safetyfw_common import part_document as _part_document, ve_check as _ve_check, lean_document as _lean_document  # noqa: E402
sys.path.insert(0, str(HERE))
import build_document as B  # noqa: E402
import rsp_translation as T  # noqa: E402
import rsp_vocabulary as V  # noqa: E402

OUT = REPO / "docs" / "usecases" / "safetyfw" / "anthropic-rsp" / "stage0.json"
RETRIEVED = "2026-10-28"
CHANGELOG = {"v1_0": "2023-09-19", "v2_0": "2024-10-15", "v2_1": "2025-03-31", "v2_2": "2025-05-14",
             "v3_0": "2026-02-24", "v3_1": "2026-04-02", "v3_2": "2026-04-29", "v3_3": "2026-05-26",
             "v3_4": "2026-07-08"}


# --- D2: harm classes and might cells (P3) --------------------------------------------------------------------------

HARMS = {  # harm constant -> (class or None, the text's words)
    "harm_of_non_novel_chem_bio_weapons": ("catastrophic", "row T1: \"serious potential for catastrophic damages\""),
    "harm_of_novel_chem_bio_weapons": ("catastrophic", "row T2: \"potential for catastrophic harm\""),
    "harm_of_misaligned_high_stakes": ("catastrophic", "row T3: \"irreversibly and substantially higher odds of a "
                                                       "later "
                                                       "global catastrophe\""),
    "harm_of_automated_rd": (None, "row T4: \"threats to international security and/or rapid disruptions to the "
                                   "global balance of power\" (no harm class word)"),
    "existential_threats": ("catastrophic", "footnote 1: catastrophic risk \"such as existential threats or "
                                            "fundamental destabilization of global systems\" (a stated instance)"),
}


def risk_environment(harms=None):
    """D2 over `harms` (default: every harm with a class; the risk route refuses a harm with none, and T4 states
    none, so T4's harm is not a D2 constant: S1-T4 is its absence)."""
    from conformance.risk import base, const
    harms = {h: v for h, v in HARMS.items() if v[0]} if harms is None else harms
    from ve.profiles import LANGUAGE, SPEC_REVISION
    return {"language": LANGUAGE, "profiles": ["alternatives@0", "norms@0", "relational-fol@0", "risk@0"],
            "spec_revision": SPEC_REVISION,
            "vocabulary": {
                "sorts": {"developer": {"description": "the frontier developer"},
                          "action": {"description": "a development or deployment the developer may take"},
                          "harm": {"description": "the harm a threshold's row names"}},
                "predicates": {
                    "available": base(["action", "developer"], "{0} is available to {1}"),
                    "leads_to": base(["action", "harm"], "{0} leads to {1}"),
                    "inaction": base(["action"], "{0} is inaction"),
                    "taken": base(["action"], "{0} is taken"),
                    "permitted": {"arguments": ["action"], "description": "the action may be taken",
                                  "regulated": {"role": "permission", "default": "allow", "act": "{0} be taken"}},
                    "required": {"arguments": ["action"], "description": "the action must be taken",
                                 "regulated": {"role": "obligation", "default": "deny", "act": "{0} be taken",
                                               "permission": "permitted"}}},
                "constants": {h: const("harm", words) for h, (_, words) in harms.items()}},
            "alternatives": {"chooser": "developer", "action": "action", "harm": "harm", "available": "available",
                             "leads_to": "leads_to", "outcomes": "signed", "decided_by": "the company",
                             "performed": {"permission": "permitted", "obligation": "required"},
                             "inaction": "inaction", "taken": "taken"},
            "risk": {"severity": {"sort": "severity", "classes": ["catastrophic"], "more_severe": [], "unranked": [],
                                  "decided_by": "the policy's own words"},
                     "harm_classes": [[h, c] for h, (c, _) in harms.items() if c], "unexamined": "possible"}}


@lru_cache(maxsize=None)
def d2():
    """P3: the risk route admits D2 and a decision record of the stated `might` cells (rows T1 to T3)."""
    from conformance.risk import Log, record, statement
    from ve.backends.relay import rows
    [with_t4] = rows("risk", [{"id": "p", "kind": "risk-elaborate", "environment": risk_environment(HARMS),
                               "document": {"norms": []}}])
    env = risk_environment()
    [policy] = rows("risk", [{"id": "p", "kind": "risk-elaborate", "environment": env, "document": {"norms": []}}])
    if policy.get("status") != "ok":
        return {"admitted": False, "answer": policy}
    log = Log()
    cells = [(f"deploy_without_{h[len('harm_of_'):]}_plans", h) for h, (c, _) in HARMS.items()
             if h.startswith("harm_of_") and c]
    for seq, (action, harm) in enumerate(cells, 1):
        log.add(seq, f"T{seq}", "statement", statement(action, harm, "might", author="the policy",
                                                       support="testimony"))
    alternatives = [{"name": a, "label": a.replace("_", " ")} for a, _ in cells] + [
        {"name": "nothing", "label": "not deploying", "inaction": True}]
    decision = log.add(100, "D", "decision", record("severity", "the_company", "the company",
                                                    (policy["environment_id"], policy["document_hash"]),
                                                    alternatives, [], log.cite(*[e["id"] for e in log.entries])))
    [report] = rows("risk", [{"id": "d", "kind": "risk-decision", "environment": env, "document": {"norms": []},
                              "decision": decision, "entries": log.entries[:-1]}])
    if report.get("status") != "ok":
        return {"admitted": False, "answer": report}
    classes = {p["ast"][2][1]: p["ast"][3][1] for p in policy["risk_premises"] if p["label"] == "risk:class"}
    might = {(m["alternative"], m["harm"]) for m in report["tables"]["might"]}
    leads = {(m["alternative"], m["harm"]) for m in report["tables"]["leads"]}
    return {"admitted": True, "environment_id": policy["environment_id"], "classes": classes,
            "with_unclassified_t4_harm": with_t4.get("error", with_t4.get("status")),
            "stated_cells": [{"alternative": a, "harm": h, "might": (a, h) in might, "leads": (a, h) in leads}
                             for a, h in cells], "might_cells": len(might), "leads_cells": len(leads)}


# --- D3: dates (P4) -------------------------------------------------------------------------------------------------

def date_environment(extra=()):
    from ve.environment import Environment
    from ve.profiles import LANGUAGE, SPEC_REVISION
    names = [f"{v}_date" for v in CHANGELOG] + ["retrieval_date", *extra]
    return Environment({"language": LANGUAGE, "profiles": ["order@0", "relational-fol@0", "time@0"],
                        "spec_revision": SPEC_REVISION, "unit_schema": "ve-units@1",
                        "units": {"day": {"scale": "1", "display": {"kind": "iso_date"}},
                                  "elapsed_day": {"scale": "1", "display": {"kind": "decimal", "label": "days"}}},
                        "vocabulary": {"sorts": {}, "predicates": {}, "constants": {
                            n: {"sort": "$int", "unit": "day", "description": n.replace("_", " "),
                                "verbalisation": "the " + n.replace("_", " ")} for n in names}}})


def _q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def _day(name):
    return ["const", "day", name]


def _proved(env, stated, goal):
    from ve.units import check_quantity_certificate, prove_quantity
    certificate = prove_quantity(env, stated, goal)
    return certificate is not None and bool(check_quantity_certificate(env, stated, goal, certificate))


@lru_cache(maxsize=None)
def d3():
    """P4: the changelog dates (D1), the effective date before retrieval (D2), and the day counts of F8, F9 and F16
    (D3b, D4, D5) as W6a day quantities; each goal holds with a certificate that VE's checker replays."""
    stated = [_q(["date_on", _day(f"{v}_date"), ["date", iso]]) for v, iso in CHANGELOG.items()]
    stated.append(_q(["date_on", _day("retrieval_date"), ["date", RETRIEVED]]))
    env = date_environment()
    versions = list(CHANGELOG)
    chain = [_q(["date_before", _day(f"{a}_date"), _day(f"{b}_date")]) for a, b in zip(versions, versions[1:])]
    out = {"D1": all(_proved(env, stated, goal) for goal in chain),
           "D2": _proved(env, stated, _q(["date_before", _day("v3_4_date"), _day("retrieval_date")]))}
    # D3b: the coverage date is "no more than 30 days prior to the publication" (F8): the publication is no later
    # than 30 days after it. D4, D5: the deadline ("Within 30 days" of F9; "within one week" of F16, 7 days) is no
    # later than the day asked about.
    counts = {"D3b": ("2026-06-10", "2026-07-01", "30", "publication within"),
              "D4": ("2026-08-03", "2026-09-02", "30", "deadline by"), "D5": ("2026-09-01", "2026-09-08", "7",
                                                                             "deadline by")}
    for item, (start, day, days, question) in counts.items():
        env = date_environment(("start_day", "limit_day"))
        facts = [_q(["date_on", _day("start_day"), ["date", start]]),
                 _q(["shift_days", _day("limit_day"), _day("start_day"), days])]
        goal = (["date_no_later", ["date", day], _day("limit_day")] if question == "publication within" else
                ["date_no_later", _day("limit_day"), ["date", day]])
        out[item] = _proved(env, facts, _q(goal))
    return {"certificates": out, "admitted": all(out.values())}


def routed_checked():
    return {"D2": d2()["admitted"], "D3": d3()["admitted"]}


# --- P1, P2, P5, P6, P8: part documents over the source ----------------------------------------------------------

def part_document(source, uids, profiles=None):
    document, records = B.build(source)
    return _part_document(document, records, source, uids, profiles)


def ve_check(text):
    return _ve_check(text)


def lean_document(text):
    return _lean_document(text)


def source_probes(source):
    coverage = json.loads((HERE / "coverage.json").read_text())
    spans = json.loads((HERE / "spans.json").read_text())["units"]
    routed = [u for u in spans if "routed" in u]
    return {
        "P1": {"input": "s36-full-review alone: f14-full-review, whose guard reads the open terms OT5 and OT4",
               "expected": "admitted; the rule is OPEN", **ve_check(part_document(source, {"s36-full-review"}))},
        "P2": {"input": "t1-plan alone with RS1 (cond, uncond, ov: no rule), through ve document check",
               "expected": "a set with a no-rule reading stays pending",
               **ve_check(part_document(source, {"t1-plan"}))},
        "P5": {"input": "D1 over the 59,410-byte text", "expected": "bytes_by_status totals 59,410",
               "bytes_by_status": coverage["bytes_by_status"],
               "total": sum(coverage["bytes_by_status"].values()), "units": len(spans)},
        "P6": {"input": "the units routed to D2 and D3", "expected": "the master map is total and disjoint",
               "routed": {d: sum(u["span"][1] - u["span"][0] for u in routed if u["routed"]["document"] == d)
                          for d in ("D2", "D3")},
               "master_total": sum(coverage["master_bytes_by_status"].values()),
               "contiguous": all(a["span"][1] == b["span"][0] for a, b in zip(spans, spans[1:]))
               and spans[0]["span"][0] == 0 and spans[-1]["span"][1] == B.TEXT_BYTES},
        "P8": {"input": "s36-full-review with judgments@0 and documents@1 added to D1's profiles",
               "expected": "admitted or refused (jt-2c, the composing modes, is not merged)",
               **lean_document(part_document(source, {"s36-full-review"}, sorted(
                   {*B.environment()["profiles"], "documents@1", "judgments@0"})))},
    }


# --- P7 (M5) and M6 -------------------------------------------------------------------------------------------------

def identifier_lint():
    """P7 / M5: no identifier packs a threshold, number or condition into its name. A constant is a threshold with
    the source's own label; no predicate name holds a threshold's name, a digit or a condition word (scenario_2 is
    the source's own label for T4's (2)); one source bullet gives one rule (the rules per source are counted)."""
    env = V.environment()["vocabulary"]
    words = ("_if_", "_unless_", "_after_", "_before_", "_requires_", "_when_")
    violations = [f"constant {c}" for c in env["constants"] if re.search(r"[0-9]", c)]
    for name in env["predicates"]:
        if (re.search(r"[0-9]", name) and name != "scenario_2") or any(w in f"_{name}_" for w in words) or any(
                c in name for c in env["constants"]):
            violations.append(f"predicate {name}")
    per_source = {}
    for block in T.rule_blocks():
        per_source.setdefault(block.source.split(",")[0], []).append(block.id)
    return {"violations": violations, "rules_per_source": per_source}


def invention_audit():
    """M6: every rule and premise is traced to a span: it has a source quote and a unit carries it (as its content,
    a restatement or a reading); every default rule is the default reading of a force or aim set; every permission
    is the P reading of an RS6 set; every threshold is a premise on its own row's unit; the vocabulary has no order,
    ranking or causal predicate."""
    spans = B.UNITS
    placed = {spec.get("rule") for _, _, spec in spans} | {f for _, _, spec in spans for f in spec.get("facts", [])}
    readings = {}
    for set_id, (harness, choices) in B.READINGS.items():
        for choice, items in choices.items():
            for item in items:
                for part in item.split(" or "):
                    readings.setdefault(part, []).append((harness, choice))
    blocks = list(T.rule_blocks()) + [b for b, _ in T.facts()]
    untraced = [b.id for b in blocks if not b.source.strip() or (b.id not in placed and b.id not in readings)]
    defaults, permissions = [], []
    for block in T.rule_blocks():
        norm = json.loads(T.parsed_rule(block.id))
        if norm.get("mode") == "default" and not any(c == "default" or c.endswith("_default")
                                                     for _, c in readings.get(block.id, [])):
            defaults.append(block.id)
        role = V.environment()["vocabulary"]["predicates"][norm["predicate"]]["regulated"]["role"]
        if role == "permission" and norm["sign"] and not any(h.startswith("RS6") and c == "P"
                                                             for h, c in readings.get(block.id, [])):
            permissions.append(block.id)
    thresholds = {f for _, _, spec in spans for f in spec.get("facts", []) if f.startswith("threshold-")}
    banned = [p for p in V.environment()["vocabulary"]["predicates"]
              if re.search(r"leads_to|causes|above|ranked|more_severe|order", p)]
    return {"untraced": untraced, "defaults_untraced": defaults, "permissions_untraced": permissions,
            "thresholds_without_premise": sorted({f"threshold-{k}" for k in ("t1", "t2", "t3", "t4")} - thresholds),
            "order_or_causal_predicates": banned,
            "narrowings": {"N1": "every RS0 statement is a commitment (no set)", "N2": "the changelog for v1.0 to "
                           "v3.3 is history: LABELLED, no rule", "N3": "3.6.1 \"may not\" is a prohibition "
                           "(f15-financial-interest, no set)"}}


def run(source=None):
    out = {"P3": {"input": "D2: a risk environment of the four row harms and footnote 1's instance, with the stated "
                           "might cells", "expected": "admitted, or S3 and S4 move to D1 as plain facts", **d2()},
           "P4": {"input": "D3: the changelog dates and the day counts of F8, F9, F16", "expected": "admitted, with "
                           "certificates", **d3()},
           "P7": identifier_lint(), "M6": invention_audit()}
    if source is not None:
        out.update(source_probes(source))
    return dict(sorted(out.items()))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=B.DEFAULT_SOURCE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    source = None
    if args.source.exists():
        source = args.source.read_bytes()
        B.check_source(source)
    elif not args.check:
        raise SystemExit(f"the pinned source is not at {args.source}")
    result = run(source)
    if args.check:
        saved = json.loads(OUT.read_text())
        if source is None:
            saved = {k: v for k, v in saved.items() if k in result}
        if saved != json.loads(json.dumps(result)):
            raise SystemExit("stage0.json is out of date")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
