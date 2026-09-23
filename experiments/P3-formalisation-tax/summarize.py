"""Assemble results.json from the P3 runs.

Reruns the differential test (item questions + P3_N perturbations, default 300)
for every item's own formalisation and for the independent agents'
formalisations (items/<id>/agent/), then merges mutation_results.json,
naive_results.json, proof_results.json, arms_usage.json, the structured-review
answers, the authoring log and coverage.py.
"""
from __future__ import annotations

import json
import os
import statistics as st
from pathlib import Path

import coverage
import harness as H

HERE = H.HERE


def load(name, default=None):
    p = HERE / name
    return json.loads(p.read_text()) if p.exists() else default


def brief(r):
    keep = ("item", "family", "stage", "error", "original", "perturbed", "targeted", "reference_vs_recorded", "faithful", "statuses", "seconds")
    out = {k: r[k] for k in keep if k in r}
    out["mismatches"] = [{k: m[k] for k in m if k not in ("world", "request")} for m in r.get("mismatches", [])][:3]
    return out


def artefact_chars(d: Path):
    return sum((d / f).stat().st_size for f in ("formalisation.ve", "environment.json", "bindings.json") if (d / f).exists())


def my_authoring_seconds():
    """Wall-clock per item from authoring_log.jsonl. Items finishing together form a batch;
    a batch's interval runs from the previous batch's end (the first batch: from its logged
    start) to its end and is split equally over its non-reuse items. The interval includes
    reading the source, writing and running the VE check, and (for a few batches) harness
    edits made in between, so it is an upper bound on pure authoring time. Reuse items
    (k02-k07, w02-w03 copy the k01/w01 formalisation) are 0 s."""
    ev = [json.loads(l) for l in (HERE / "authoring_log.jsonl").read_text().splitlines()]
    reuse = {e["item"] for e in ev if "reuse" in e["note"]}
    first_start = min(e["t"] for e in ev if e["event"] == "start")
    ends = {e["item"]: e["t"] for e in ev if e["event"] == "end"}
    batches = {}  # ends logged within 2 s of each other belong to one batch
    for i, t in sorted(ends.items(), key=lambda kv: kv[1]):
        key = next((k for k in batches if t - k <= 2.0), t)
        batches.setdefault(key, []).append(i)
    batches = {max(ends[i] for i in v): v for v in batches.values()}
    out, prev = {}, first_start
    for t in sorted(batches):
        work = [i for i in batches[t] if i not in reuse]
        for i in batches[t]:
            out[i] = {"seconds": round((t - prev) / len(work), 1) if i in work else 0.0, "reuse": i in reuse}
        prev = t
    return out


def main():
    ids = sorted(p.name for p in H.ITEMS.iterdir() if p.is_dir())
    rows = {}
    for i in ids:
        r = H.diff_item(i)
        rows[i] = brief(r)
        print("diff", i, r.get("faithful"), r.get("perturbed"), flush=True)
    first_rows = {}
    H.FORMAL_SUBDIR = "first_pass"  # the frozen first-pass files, before any differential feedback
    for i in ids:
        first_rows[i] = brief(H.diff_item(i))
        print("first_pass", i, first_rows[i].get("faithful"), first_rows[i].get("perturbed"), flush=True)
    H.FORMAL_SUBDIR = ""
    agent_rows = {}
    os.environ["P3_FORMAL_DIR"] = "agent"
    H.FORMAL_SUBDIR = "agent"
    for i in ids:
        if (H.ITEMS / i / "agent" / "formalisation.ve").exists():
            try:
                agent_rows[i] = brief(H.diff_item(i))
            except Exception as e:  # noqa: BLE001
                agent_rows[i] = {"item": i, "stage": "error", "error": f"{type(e).__name__}: {e}"[:300]}
            print("agent", i, agent_rows[i].get("faithful"), agent_rows[i].get("perturbed"), flush=True)
    H.FORMAL_SUBDIR = ""

    timing = my_authoring_seconds()
    log_events = [json.loads(l) for l in (HERE / "authoring_log.jsonl").read_text().splitlines()]
    mutation = {m["item"]: m for m in load("mutation_results.json", [])}
    naive = load("naive_results.json", [])
    proofs = load("proof_results.json", [])
    usage = load("arms_usage.json", {})
    keys = load("review_packets/keys.json", {})

    items = []
    for i in ids:
        item = H.load_item(i)
        d = H.ITEMS / i
        fp_same = all((d / "first_pass" / f).read_bytes() == (d / f).read_bytes()
                      for f in ("formalisation.ve", "environment.json", "bindings.json") if (d / f).exists())
        m = mutation.get(i, {})
        items.append({
            "id": i, "family": item["family"], "synthetic_parts": item.get("synthetic_parts") or
            ("instances" if item["family"] == "alloy" else "requests" if item["family"] in ("k8s", "iam") else None),
            "provenance": item["provenance"], "questions": len(item["questions"]),
            "differential": rows[i], "differential_first_pass": first_rows[i], "coverage": {**coverage.summary(i), **{k: v for k, v in coverage.COVERAGE[i].items() if k != "units"}},
            "authoring": {**timing.get(i, {}), "artefact_chars": artefact_chars(d), "artefact_tokens_est": round(artefact_chars(d) / 4),
                          "source_chars": sum(len(v) for v in item["sources"].values()),
                          "first_pass_unchanged": fp_same,
                          "repair_iterations": sum(1 for e in log_events if e["item"] == i and e["event"] in ("checker_fix", "diff_fix")),
                          "repairs": [e["note"] for e in log_events if e["item"] == i and e["event"] in ("checker_fix", "diff_fix")]},
            "mutation": {k: m.get(k) for k in ("mutants", "killed", "killed_by_item_questions_alone", "survivors_equivalent",
                                                "survivors_distinguishable", "survivors_unknown")},
            "agent_author": agent_rows.get(i),
        })

    def rate(xs):
        return f"{sum(xs)}/{len(xs)}"

    fam = sorted({x["family"] for x in items})
    faithful = [x["differential"].get("faithful") is True for x in items]
    pure = [x["differential"].get("faithful") is True and x["coverage"]["fully_expressible"] for x in items]
    muts = [x["mutation"] for x in items if x["mutation"]["mutants"]]
    tot_m = sum(m["mutants"] for m in muts)
    tot_k = sum(m["killed"] for m in muts)
    review_acc = {}
    for k, v in keys.items():
        p = HERE / "review_packets" / "answers" / f"{k}.json"
        if p.exists():
            got = [a["answer"] for a in sorted(json.loads(p.read_text())["answers"], key=lambda a: a["n"])]
            review_acc[k] = {"correct": sum(g == r for g, r in zip(got, v)), "total": len(v)}
    paired = []
    for k in usage.get("review", {}):
        a, rv = usage.get("author", {}).get(k), usage["review"][k]
        if a:
            paired.append({"item": k, "review_tokens": rv["tokens"], "review_seconds": round(rv["ms"] / 1000, 1),
                           "author_tokens": a["tokens"], "author_seconds": round(a["ms"] / 1000, 1),
                           "author_check_runs": a.get("check_runs"), "author_error_runs": a.get("error_runs"),
                           "author_faithful": (agent_rows.get(k) or {}).get("faithful"),
                           "review_correct": review_acc.get(k)})
    summary = {
        "items": len(items), "by_family": {f: sum(x["family"] == f for x in items) for f in fam},
        "questions": sum(x["questions"] for x in items),
        "perturbations_per_item": H.N_PERTURB,
        "targeted_perturbations_per_item": H.N_TARGETED,
        "targeted_perturbations_total": sum((x["differential"].get("targeted") or {}).get("total", 0) for x in items),
        "faithful_first_pass_author_me": rate([x["differential_first_pass"].get("faithful") is True for x in items]),
        "faithful_after_repair_author_me": rate(faithful),
        "faithful_and_fully_expressible": rate(pure),
        "faithful_by_family": {f: rate([x["differential"].get("faithful") is True for x in items if x["family"] == f]) for f in fam},
        "reference_vs_recorded_cedar_decisions": f'{sum(x["differential"]["reference_vs_recorded"]["agree"] for x in items)}/'
                                                  f'{sum(x["differential"]["reference_vs_recorded"]["total"] for x in items)}',
        "independent_agent_authors": {"faithful": rate([(r or {}).get("faithful") is True for r in agent_rows.values()]),
                                      "items": sorted(agent_rows)},
        "coverage": {"units": sum(x["coverage"]["units"] for x in items),
                     "a": sum(x["coverage"]["a"] for x in items), "b": sum(x["coverage"]["b"] for x in items),
                     "c": sum(x["coverage"]["c"] for x in items), "d": sum(x["coverage"]["d"] for x in items),
                     "fully_expressible_items": rate([x["coverage"]["fully_expressible"] for x in items]),
                     "mean_expressible_fraction": round(st.mean(x["coverage"]["expressible_fraction"] for x in items), 3)},
        "authoring_me": {"repair_iterations_total": sum(x["authoring"]["repair_iterations"] for x in items),
                         "checker_errors_before_first_pass": 0,
                         "wall_clock_seconds_total": round(sum(x["authoring"].get("seconds", 0) for x in items), 1),
                         "wall_clock_seconds_median_nonreuse": st.median([x["authoring"]["seconds"] for x in items if not x["authoring"].get("reuse")]),
                         "artefact_tokens_median": st.median(x["authoring"]["artefact_tokens_est"] for x in items)},
        "mutation_adequacy": {"mutants": tot_m, "killed": tot_k, "kill_rate": round(tot_k / tot_m, 3) if tot_m else None,
                              "killed_by_item_questions_alone": sum(m["killed_by_item_questions_alone"] for m in muts),
                              "survivors_equivalent": sum(m["survivors_equivalent"] for m in muts),
                              "survivors_distinguishable": sum(m["survivors_distinguishable"] for m in muts),
                              "survivors_unknown": sum(m["survivors_unknown"] for m in muts)},
        "naive_variants": {"caught": rate([n["caught"] for n in naive]),
                           "caught_by_item_questions_alone": rate([n["caught_by_item_questions_alone"] for n in naive])},
        "proof_tasks": [{k: p.get(k) for k in ("id", "prove", "prove_steps", "prove_seconds", "certificate_replayed",
                                                "countermodel", "ve_verdict", "agrees")} | {"reference": p["reference"].get("verdict"),
                                                                                           "reference_method": p["reference"].get("method")}
                        for p in proofs],
        "review_arm": {"accuracy": f'{sum(v["correct"] for v in review_acc.values())}/{sum(v["total"] for v in review_acc.values())}',
                       "per_item": review_acc},
        "paired_cost": paired,
    }
    out = {"summary": summary, "items": items, "naive_variants": naive, "proofs": proofs}
    (HERE / "results.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps(summary, indent=1, default=str))


if __name__ == "__main__":
    main()
