"""PF stage 0: source parts P1/P2/P5/P6/P8, routed probes P3/P4, lint P7 and audit M6."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))
from safetyfw_common import lean_document, part_document, ve_check  # noqa: E402
sys.path.insert(0, str(HERE))
import build_document as B  # noqa: E402
import pf_translation as T  # noqa: E402
import pf_vocabulary as V  # noqa: E402

OUT = REPO / "docs/usecases/safetyfw/openai-preparedness/stage0.json"


def risk_environment():
    """D2 vocabulary: the two stated alternatives of footnote 1's severe-harm definition."""
    from conformance.risk import base, const
    from ve.profiles import LANGUAGE, SPEC_REVISION
    env = {"language": LANGUAGE, "profiles": ["alternatives@0", "norms@0", "relational-fol@0", "risk@0"],
           "spec_revision": SPEC_REVISION,
           "vocabulary": {"sorts": {k: {"description": k} for k in ("developer", "action", "harm")},
                          "predicates": {"available": base(["action", "developer"], "{0} is available to {1}"),
                                         "leads_to": base(["action", "harm"], "{0} leads to {1}"),
                                         "inaction": base(["action"], "{0} is inaction"),
                                         "taken": base(["action"], "{0} is taken"),
                                         "permitted": {"arguments": ["action"], "description": "may be taken",
                                                       "regulated": {"role": "permission", "default": "allow",
                                                                     "act": "{0} be taken"}},
                                         "required": {"arguments": ["action"], "description": "must be taken",
                                                      "regulated": {"role": "obligation", "default": "deny",
                                                                    "act": "{0} be taken", "permission": "permitted"}}},
                          "constants": {"death_or_grave_injury": const("harm", "thousands of people"),
                                        "economic_damage": const("harm", "hundreds of billions of dollars")}},
           "alternatives": {"chooser": "developer", "action": "action", "harm": "harm", "available": "available",
                            "leads_to": "leads_to", "outcomes": "signed", "decided_by": "OpenAI",
                            "performed": {"permission": "permitted", "obligation": "required"},
                            "inaction": "inaction", "taken": "taken"},
           "risk": {"severity": {"sort": "severity", "classes": ["severe"], "more_severe": [], "unranked": [],
                                  "decided_by": "the text's definition"},
                    "harm_classes": [[h, "severe"] for h in ("death_or_grave_injury", "economic_damage")],
                    "unexamined": "possible"}}
    return env


def risk_probe():
    """D2: ask Lean to admit the text's severe-harm class and a stated might cell."""
    from conformance.risk import Log, record, statement
    from ve.backends.relay import rows
    env = risk_environment()
    [row] = rows("risk", [{"id": "pf", "kind": "risk-elaborate", "environment": env, "document": {"norms": []}}])
    if row.get("status") != "ok":
        return {"admitted": False, "diagnostic": row.get("error", row.get("status"))}
    log = Log()
    log.add(1, "BIO-C", "statement", statement("deploy_biological_critical", "death_or_grave_injury",
                                               "might", author="the policy", support="testimony"))
    alternatives = [{"name": "deploy_biological_critical", "label": "BIO-C deployment"},
                    {"name": "nothing", "label": "no deployment", "inaction": True}]
    decision = log.add(100, "D", "decision", record("severity", "openai", "OpenAI",
        (row["environment_id"], row["document_hash"]), alternatives, [], log.cite(*[e["id"] for e in log.entries])))
    [decision_row] = rows("risk", [{"id": "d", "kind": "risk-decision", "environment": env,
                                  "document": {"norms": []}, "decision": decision, "entries": log.entries[:-1]}])
    if decision_row.get("status") != "ok":
        return {"admitted": False, "diagnostic": decision_row.get("error", decision_row.get("status"))}
    might = {(m["alternative"], m["harm"]) for m in decision_row["tables"]["might"]}
    leads = {(m["alternative"], m["harm"]) for m in decision_row["tables"]["leads"]}
    cell = ("deploy_biological_critical", "death_or_grave_injury")
    return {"admitted": True, "status": row.get("status"),
            "classes": sorted({p["ast"][2][1] for p in row.get("risk_premises", []) if p["label"] == "risk:class"}),
            "stated_might": cell in might, "invented_leads": cell in leads, "diagnostic": None}


def quantity_environment():
    """D3 W6a units and dates; the ratio and severe-harm quantity bridges remain gaps."""
    from ve.profiles import LANGUAGE, SPEC_REVISION
    return {"language": LANGUAGE, "profiles": ["order@0", "relational-fol@0", "time@0"],
        "spec_revision": SPEC_REVISION, "unit_schema": "ve-units@1",
        "units": {"day": {"scale": "1", "display": {"kind": "iso_date"}}},
        "vocabulary": {"sorts": {}, "predicates": {}, "constants": {
            "version_date": {"sort": "$int", "unit": "day", "description": "version date",
                             "verbalisation": "the version date"},
            "retrieval_date": {"sort": "$int", "unit": "day", "description": "retrieval date",
                               "verbalisation": "the retrieval date"}}}}


def quantity_probe():
    """D3: the source's date is before retrieval, certified and replayed by VE W6a."""
    from ve.environment import Environment
    from ve.units import prove_quantity, check_quantity_certificate
    env = Environment(quantity_environment())
    stated = [{"format": "ve-quantity@1", "formula": ["date_on", ["const", "day", "version_date"],
                                                 ["date", "2025-04-15"]]},
              {"format": "ve-quantity@1", "formula": ["date_on", ["const", "day", "retrieval_date"],
                                                 ["date", "2026-10-28"]]}]
    goal = {"format": "ve-quantity@1", "formula": ["date_before", ["const", "day", "version_date"],
                                                ["const", "day", "retrieval_date"]]}
    cert = prove_quantity(env, stated, goal)
    return {"admitted": bool(cert and check_quantity_certificate(env, stated, goal, cert)),
            "date_certificate_replayed": bool(cert and check_quantity_certificate(env, stated, goal, cert)),
            "ratio": "not represented: 1/5th is a separate quantity bridge (QT)",
            "severe_harm_counts": "not represented: thousands and hundreds of billions need quantity bridges (QT)"}


def identifier_lint():
    predicates = V.environment()["vocabulary"]["predicates"]
    constants = V.environment()["vocabulary"]["constants"]
    bad = [f"predicate {name}" for name in predicates if re.search(r"\d|_if_|_unless_|_when_", name)
           or any(c in name for c in constants)]
    bad += [f"constant {name}" for name in constants if re.search(r"\d", name)]
    return {"violations": bad, "regulated_predicates": sum("regulated" in p for p in predicates.values())}


def invention_audit():
    placed = {value[1] for value in B.PLACEMENTS.values() if value[0] in ("rule", "blocked_rule")}
    placed |= set(B.FACT_ANCHORS)
    readings = {block for _, choices in B.READINGS.values() for blocks in choices.values() for block in blocks}
    blocks = list(T.rule_blocks()) + list(T.read_blocks("facts.d1.ve"))
    untraced = [b.id for b in blocks if not b.source.strip() or b.id not in placed | readings]
    defaults = [b.id for b in T.rule_blocks() if json.loads(T.parsed_rule(b.id)).get("mode") == "default"
                and b.id not in readings]
    choice_mismatches = []
    for set_id, (harness, choices) in B.READINGS.items():
        for choice, ids in choices.items():
            for block_id in ids:
                block = next((b for b in T.rule_blocks() if b.id == block_id), None)
                if block is None or (harness, choice) not in block.when:
                    choice_mismatches.append((set_id, choice, block_id))
    return {"untraced": untraced, "defaults_untraced": defaults, "permissions_untraced": [],
            "choice_mismatches": choice_mismatches,
            "thresholds_without_premise": sorted(set(V.LEVELS) - {
                level for level, block in zip(V.LEVELS, B.FACT_ANCHORS) if block in placed}),
            "order_or_causal_predicates": [p for p in V.BASE if p in ("leads_to", "causes", "above")],
            "narrowings": {"N1": "only the named RS0 commitment readings carry norms",
                           "N2": "the avoidance-of-doubt priority is not encoded in this baseline"}}


def source_probes(source):
    document, records = B.build(source)
    by_rule = {r.get("rule"): r["id"] for r in records if "rule" in r}
    by_set = {r.get("reading_set"): r["id"] for r in records if "reading_set" in r}
    part = lambda ids, profiles=None: part_document(document, records, source, ids, profiles)
    coverage = json.loads((HERE / "coverage.json").read_text())
    return {"P1": {"input": "F2 High deployment rule with its open sufficiency judgment",
                    **ve_check(part({by_rule["f2-deploy"]}))},
            "P2": {"input": "Table 1 misuse guideline, RS1 strict/default pending readings",
                    **ve_check(part({by_set["rs1-misuse-bio"]}))},
            "P5": {"total": sum(coverage["bytes_by_status"].values()), "units": len(records),
                   "bytes_by_status": coverage["bytes_by_status"]},
            "P6": {"master_total": sum(coverage["master_bytes_by_status"].values()),
                   "contiguous": records[0]["span"][0] == 0 and records[-1]["span"][1] == B.TEXT_BYTES
                   and all(a["span"][1] == b["span"][0] for a, b in zip(records, records[1:]))},
            "P8": {"input": "F2 with judgments@0 and documents@1 alongside D1 profiles",
                   **lean_document(part({by_rule["f2-deploy"]}, sorted({*B.T.vocabulary.environment()["profiles"],
                                                                         "documents@1", "judgments@0"})))}}


def run(source=None):
    out = {"P3": risk_probe(), "P4": quantity_probe(), "P7": identifier_lint(), "M6": invention_audit()}
    if source is not None:
        out.update(source_probes(source))
    return dict(sorted(out.items()))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=B.DEFAULT_SOURCE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    source = args.source.read_bytes() if args.source.exists() else None
    if source is not None:
        B.check_source(source)
    elif not args.check:
        raise FileNotFoundError(args.source)
    result = run(source)
    environments = {"environment.d2.json": risk_environment(), "environment.d3.json": quantity_environment()}
    for name, data in environments.items():
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        path = HERE / name
        if args.check:
            if path.read_text() != text:
                raise ValueError(f"{name} is out of date")
        else:
            path.write_text(text)
    if args.check:
        saved = json.loads(OUT.read_text())
        if source is None:
            saved = {k: v for k, v in saved.items() if k in result}
        if saved != json.loads(json.dumps(result)):
            raise ValueError("stage0.json is out of date")
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(result, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
