"""ME-0: gather the measured numbers into `docs/research/evidence/math-evidence/summary.json`.

Reads only saved evidence (each ledger's `run.json`, `*.units.json`, and the P3-P6 files), never a live tree, so
the numbers stay what the run measured.

    python3 -I research/math-evidence/summarise.py
"""
from __future__ import annotations

import collections
import json
from pathlib import Path

EV = Path(__file__).resolve().parents[2] / "docs/research/evidence/math-evidence"
TARGETS = {"H": "physics-michelson-morley", "M": "math-ramanujan-bertrand", "V": "ve-paper-e1",
           "DL": "dl-alphafold"}
ME_FEATURES = {"calc", "calc-data", "calc-derive", "calc-dimension", "calc-stats", "calc-algebra", "arith",
               "arith-import", "approximation"}
ESTIMATE_CHECKED = {"H": (1500, 2500), "V": (300, 800), "M": (0, 0), "DL": (2000, 4000)}
ESTIMATE_SIZE = {"H": (30000, 40000), "M": (4000, 6000)}
ESTIMATE_LABELLED = {"H": (13000, 16000)}
ESTIMATE_EXPOSITION = {"H": 0.60, "M": 0.15, "DL": 0.45}


def main() -> None:
    out = {}
    for row, target in TARGETS.items():
        run = json.loads((EV / target / "run.json").read_text())
        status, kinds, features = collections.Counter(), collections.Counter(), collections.Counter()
        unit_kinds, feature_units = collections.Counter(), collections.Counter()
        sources, total, accepted, leaf_bytes = {}, 0, True, 0
        for name, s in run["sources"].items():
            cov = s["coverage"]
            assert cov["accounted_bytes"] == cov["source_bytes"] and cov["coverage_percent"] == 100, (target, name)
            status.update(cov["bytes_by_status"])
            total += cov["source_bytes"]
            accepted &= bool(s["accepted"])
            ledger = json.loads((EV / target / (name.rsplit(".", 1)[0] + ".units.json")).read_text())
            assert ledger["source_bytes"] == cov["source_bytes"]
            parents: dict[str, list] = collections.defaultdict(list)
            for u in ledger["units"]:
                kinds[u["kind"]] += u["bytes"]
                if u["feature"]:
                    features[u["feature"]] += u["bytes"]
                    feature_units[u["feature"]] += 1
                parents[u.get("parent", u["id"])].append(u)
            for parts in parents.values():
                unit_kinds[max(parts, key=lambda p: p["bytes"])["kind"]] += 1
            leaves = set(s.get("graph_leaf_units", []))
            leaf_bytes += sum(u["bytes"] for u in ledger["units"] if u["id"] in leaves and u["status"] == "CHECKED")
            sources[name] = {k: s[k] for k in ("document_sha256", "document_bytes", "accepted", "graph_admitted",
                                                "premises", "rust_timeout_raised_to", "certified_consequences")}
            sources[name]["units"] = len(parents)
            sources[name]["source_bytes"] = cov["source_bytes"]
        me = sum(v for f, v in features.items() if f in ME_FEATURES)
        out[row] = {
            "target": target, "source_bytes": total, "all_documents_accepted": accepted,
            "bytes_by_status": dict(status), "checked_percent": round(100 * status["CHECKED"] / total, 2),
            "checked_bytes_in_certified_consequences": leaf_bytes,
            "checked_bytes_stated_only": status["CHECKED"] - leaf_bytes,
            "bytes_by_kind": dict(kinds.most_common()), "units_by_kind": dict(unit_kinds.most_common()),
            "unformalised_bytes_by_feature": dict(features.most_common()),
            "unformalised_units_by_feature": dict(feature_units.most_common()),
            "unformalised_bytes_this_plan": me,
            "unformalised_bytes_siblings": sum(features.values()) - me,
            "exposition_share": round(kinds["exposition"] / total, 3),
            "sources": sources,
        }
        checked = status["CHECKED"]
        theorems_imported = sum(
            u["bytes"] for name in run["sources"]
            for u in json.loads((EV / target / (name.rsplit(".", 1)[0] + ".units.json")).read_text())["units"]
            if u["feature"] == "arith-import" and u["kind"] == "theorem")
        out[row]["ceilings_percent"] = {
            "this_plan_all_features": round(100 * (checked + me) / total, 2),
            "this_plan_without_approximation (D17: reading sets, never CHECKED)":
                round(100 * (checked + me - features["approximation"]) / total, 2),
            "also_without_calc_data (DL: the data are figures and supplements, not pinned)":
                round(100 * (checked + me - features["approximation"] - features["calc-data"]) / total, 2),
            "without_imports (EX-1 fails)": round(
                100 * (checked + me - features["approximation"] - features["arith-import"]) / total, 2),
            "with_imports_of_theorem_statements_only": round(
                100 * (checked + me - features["approximation"] - features["arith-import"] + theorems_imported)
                / total, 2),
        }
        est = {}
        if row in ESTIMATE_CHECKED:
            lo, hi = ESTIMATE_CHECKED[row]
            est["checked"] = {"estimate": [lo, hi], "measured": status["CHECKED"],
                              "inside": lo <= status["CHECKED"] <= hi}
        if row in ESTIMATE_SIZE:
            lo, hi = ESTIMATE_SIZE[row]
            est["size"] = {"estimate": [lo, hi], "measured": total, "inside": lo <= total <= hi}
        if row in ESTIMATE_LABELLED:
            lo, hi = ESTIMATE_LABELLED[row]
            est["labelled"] = {"estimate": [lo, hi], "measured": status["LABELLED"],
                               "inside": lo <= status["LABELLED"] <= hi}
        if row in ESTIMATE_EXPOSITION:
            est["exposition_share"] = {"estimate": ESTIMATE_EXPOSITION[row], "measured": out[row]["exposition_share"]}
        out[row]["estimates"] = est
    p3 = json.loads((EV / "pilots-zero.json").read_text())
    p4 = json.loads((EV / "fixture-anchors.json").read_text())
    p6 = json.loads((EV / "date-floor.json").read_text())
    p2 = json.loads((EV / "dl-licence-check/licence-evidence.json").read_text())
    result = {
        "ledgers": out,
        "P1_pass": all(v["all_documents_accepted"] for v in out.values()),
        "P2_pinned": p2["pinned"],
        "P3_pass": p3["pass"],
        "P4_pass": p4["pass"], "P4_counts": p4["counts"], "P4_changed_or_absent": p4["changed_or_absent"],
        "P6_pass": p6["pass"],
    }
    (EV / "summary.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
