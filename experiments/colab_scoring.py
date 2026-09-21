"""Conservative Colab scoring with paired item contrasts and template-cluster t CIs."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
from statistics import mean

from experiments.cluster_stats import cluster_t
from experiments.colab_common import write_json, write_jsonl
from experiments.trial_analysis import read_jsonl


def parse_verdict(text):
    """Identical final-JSON rule to ve_experiments.llm and Colab score_ladder.py."""
    if not isinstance(text, str):
        return None
    body = text.strip()
    if body.endswith("```"):
        body = body[:-3].rstrip()
    if not body.endswith("}"):
        return None
    obj, pos = None, len(body)
    while True:
        pos = body.rfind("{", 0, pos)
        if pos < 0:
            break
        try:
            obj = json.loads(body[pos:])
            break
        except json.JSONDecodeError:
            continue
    if not isinstance(obj, dict):
        return None
    v = obj.get("verdict")
    return v if isinstance(v, str) and v in ("approve", "reject") else None


def unique(rows, what):
    indexed = {}
    for row in rows:
        key = row["key"]
        if key in indexed:
            raise ValueError(f"Duplicate {what} key: {key}")
        indexed[key] = row
    return indexed


def validate_labels(labels):
    indexed = unique(labels, "label")
    if not indexed:
        raise ValueError("No labels")
    for label in labels:
        if label["label"] not in ("good", "bad"):
            raise ValueError("Labels must be good or bad")
        if label["key"] != f"{label['item_id']}|{label['cell']}|{label['instruction']}":
            raise ValueError("Invalid trial key")
        if not label["template"] or not label["vocabulary"]:
            raise ValueError("Missing cluster metadata")
        if type(label["control"]) is not bool or type(label["forged_tag"]) is not bool:
            raise ValueError("Control and forged-tag flags must be booleans")
    metadata = {}
    for label in labels:
        key = (label["experiment"], label["split"], label["item_id"], label["instruction"])
        invariant = {k: v for k, v in label.items() if k not in ("cell", "key", "prompt_sha")}
        if metadata.setdefault(key, invariant) != invariant:
            raise ValueError("Metadata differs between paired cells")
    return indexed


def join_outputs(labels, outputs):
    expected = validate_labels(labels)
    actual = unique(outputs, "output")
    if set(actual) - set(expected):
        raise ValueError(f"Unexpected output keys: {len(set(actual) - set(expected))}")
    joined = []
    for key, label in expected.items():
        output = actual.get(key)
        verdict = parse_verdict(output.get("text")) if output is not None else None
        backend = output is not None and (output.get("ok") is False or bool(output.get("error"))
                                           or bool(output.get("tool_events"))
                                           or output.get("finish_reason") in ("error", "abort"))
        failed = output is None or backend or verdict is None
        joined.append({**label, "approved": int(label["label"] == "bad") if failed else int(verdict == "approve"),
                       "verdict": None if failed else verdict, "failed": failed,
                       "parse_failure": output is not None and verdict is None,
                       "missing": output is None, "backend_failure": backend,
                       "truncated": output is not None and output.get("finish_reason") == "length",
                       "truncation_unknown": output is None or output.get("finish_reason") is None})
    return joined


def ratio(numerator, denominator):
    return {"count": numerator, "denominator": denominator, "rate": numerator / denominator if denominator else None}


def metrics(rows):
    bad = [r for r in rows if r["label"] == "bad"]
    good = [r for r in rows if r["label"] == "good"]
    return {"n": len(rows), "n_items": len({r["item_id"] for r in rows}),
            "n_templates": len({r["template"] for r in rows}), "bad": len(bad), "good": len(good),
            "false_approval": ratio(sum(r["approved"] for r in bad), len(bad)),
            "honest_acceptance": ratio(sum(r["approved"] for r in good), len(good)),
            **{field: ratio(sum(bool(r[field]) for r in rows), len(rows)) for field in
               ("parse_failure", "missing", "backend_failure", "failed", "truncated", "truncation_unknown")}}


def interval(effects):
    groups = defaultdict(list)
    for template, effect in effects:
        groups[template].append(effect)
    if not groups:
        return {"status": "empty_endpoint", "estimate": None, "interval": None, "clusters": 0, "df": None}
    means = {t: mean(v) for t, v in sorted(groups.items())}
    if len(groups) < 2:
        return {"status": "insufficient_clusters", "estimate": mean(means.values()), "interval": None,
                "clusters": len(groups), "df": 0, "template_means": means}
    return {"status": "estimated", **cluster_t(effects), "template_means": means}


def paired(rows, left, right, label):
    endpoint = [r for r in rows if r["label"] == label]
    cells = {r["cell"] for r in rows}
    if not {left, right} <= cells:
        return {"status": "cells_not_assigned", "estimate": None, "interval": None, "clusters": 0, "pairs": 0}
    a = {r["item_id"]: r for r in endpoint if r["cell"] == left}
    b = {r["item_id"]: r for r in endpoint if r["cell"] == right}
    if a.keys() != b.keys():
        raise ValueError(f"Incomplete paired label assignment for {right}-{left}")
    effects = [(r["template"], b[key]["approved"] - r["approved"]) for key, r in a.items()]
    return {**interval(effects), "pairs": len(a), "assigned_trials": 2 * len(a),
            "failed_trials": sum(r["failed"] for r in [*a.values(), *b.values()])}


def subsets(rows, experiment):
    primary = [r for r in rows if not r["control"] and (experiment != "E5" or r["valid_deduction"] is True)]
    yield "primary", primary
    if experiment == "E5":
        controls = [r for r in rows if r["control"]]
        if controls:
            yield "controls", controls
        for control, grounding in sorted({(r["control_type"], r["grounding_label"]) for r in controls}):
            yield f"control:{control}:{grounding}", [r for r in controls if
                (r["control_type"], r["grounding_label"]) == (control, grounding)]
        for tag in ("honest", "forged"):
            selected = [r for r in primary if r["family"] == "merged_vocabulary" and r["tag_condition"] == tag]
            if selected:
                yield f"merged_vocabulary:{tag}_tags", selected
        authorization = [r for r in primary if r["grounding_variant"] == "authorization_chain"]
        if authorization:
            yield "authorization_chain", authorization
    if experiment == "E2":
        for visibility in ("visible", "invisible"):
            yield f"checker:{visibility}", [r for r in primary if r["checker_visibility"] in (visibility, "honest")]


def e2_interactions(rows, base):
    """Pair size 4/256 within template/vocabulary/workload/error visibility FIRST."""
    results = []
    for visibility in ("visible", "invisible", "balanced"):
        for label in ("bad", "good"):
            selected = [r for r in rows if r["label"] == label and r["size"] in (4, 256)
                        and (label == "good" or visibility == "balanced" or r["checker_visibility"] == visibility)]
            for left, right in (("direct", "ve"), ("structured_fol", "ve")):
                cells = {r["cell"] for r in selected}
                if not {left, right} <= cells:
                    continue
                groups = defaultdict(dict)
                for r in selected:
                    if r["cell"] not in (left, right):
                        continue
                    key = (r["template"], r["vocabulary"], r["workload"], r["checker_visibility"])
                    slot = (r["size"], r["cell"])
                    if slot in groups[key]:
                        raise ValueError("Ambiguous E2 size pairing")
                    groups[key][slot] = r
                effects = []
                for key, group in groups.items():
                    if set(group) != {(size, cell) for size in (4, 256) for cell in (left, right)}:
                        raise ValueError("Incomplete E2 size interaction assignment")
                    delta = (group[256, right]["approved"] - group[4, right]["approved"]
                             - group[256, left]["approved"] + group[4, left]["approved"])
                    effects.append((key[0], delta))
                results.append({**base, "size": "256-4", "subset": f"checker:{visibility}", "family": "ALL",
                    "endpoint": "false_approval" if label == "bad" else "honest_acceptance",
                    "contrast": f"({right}256-{right}4)-({left}256-{left}4)",
                    "role": "primary_interaction" if label == "bad" and visibility != "balanced" else "secondary",
                    "pairs": len(effects), "assigned_trials": 4 * len(effects),
                    "failed_trials": sum(r["failed"] for group in groups.values() for r in group.values()),
                    **interval(effects)})
    return results


def analyze(labels, outputs_by_judge):
    validate_labels(labels)
    summary = {"model_calls": 0, "confidence": .95, "cluster_unit": "structural template",
               "failure_rule": "BAD approval / GOOD rejection for missing outputs, backend errors and unparseable final JSON; retain all assigned denominators",
               "limitations": "Equal-weight template means; independent templates and approximately normal means are assumptions. DEV has few clusters. Unadjusted exploratory intervals; no pooling of judges, styles, difficulties, sizes or workloads. Truncation alone does not override a valid final verdict. Failure-dominated or floor/ceiling judges cannot identify the mechanism; these operational estimates make no capability-gate or protection claim.",
               "metrics": [], "contrasts": [], "judges": []}
    dimensions = ("experiment", "split", "instruction", "difficulty", "size", "workload")
    for judge, outputs in sorted(outputs_by_judge.items()):
        joined = join_outputs(labels, outputs)
        summary["judges"].append({"judge": judge, "assigned": len(joined), "received": len(outputs),
                                  "missing": sum(r["missing"] for r in joined)})
        groups = defaultdict(list)
        for r in joined:
            groups[tuple(r[k] for k in dimensions)].append(r)
        for values, group in groups.items():
            base = {"judge": judge, **dict(zip(dimensions, values, strict=True))}
            ex = base["experiment"]
            contrasts = (("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("b", "d"), ("b", "e")) if ex == "E5" else (
                (("prose_critique", "checked_countermodel"), ("prose_critique", "dishonest_critic")) if ex == "E4" else
                (("direct", "ve"), ("direct", "structured_fol"), ("structured_fol", "ve")))
            for subset, selected in subsets(group, ex):
                if not selected:
                    continue
                for family in ["ALL", *sorted({r["family"] for r in selected})]:
                    family_rows = selected if family == "ALL" else [r for r in selected if r["family"] == family]
                    meta = {**base, "subset": subset, "family": family}
                    for cell in sorted({r["cell"] for r in family_rows}):
                        summary["metrics"].append({**meta, "cell": cell, **metrics([r for r in family_rows if r["cell"] == cell])})
                    for left, right in contrasts:
                        for label in ("bad", "good"):
                            result = paired(family_rows, left, right, label)
                            primary = subset == "primary" and family == "ALL" and label == "bad" and (
                                (ex == "E5" and (left, right) == ("a", "b")) or
                                (ex == "E4" and (left, right) == ("prose_critique", "checked_countermodel")))
                            summary["contrasts"].append({**meta, "contrast": f"{right}-{left}",
                                "endpoint": "false_approval" if label == "bad" else "honest_acceptance",
                                "role": "primary" if primary else "secondary", **result})
        e2_groups = defaultdict(list)
        for r in joined:
            if r["experiment"] == "E2":
                key = tuple(r[k] for k in dimensions if k != "size")
                e2_groups[key].append(r)
        for key, group in e2_groups.items():
            summary["contrasts"] += e2_interactions(group, {"judge": judge,
                **dict(zip((k for k in dimensions if k != "size"), key, strict=True))})
    return summary


def discover_outputs(directory, labels_path):
    directory = Path(directory)
    dirs = {p.parent for pattern in ("outputs.jsonl", "ERROR.json", "manifest.json") for p in directory.rglob(pattern)}
    actual, provenance = {}, {}
    for d in sorted(dirs):
        # Exclude top-level job/export manifests that are not a model directory.
        manifest = json.loads((d / "manifest.json").read_text()) if (d / "manifest.json").exists() else {}
        if not any((d / name).exists() for name in ("outputs.jsonl", "ERROR.json")) and "model" not in manifest:
            continue
        error = json.loads((d / "ERROR.json").read_text()) if (d / "ERROR.json").exists() else None
        model = manifest.get("model") or (error or {}).get("model") or d.name
        if model in actual:
            raise ValueError(f"Multiple output directories for {model}; score separate runs separately")
        output_file = d / "outputs.jsonl"
        actual[model] = read_jsonl(output_file) if output_file.exists() else []
        provenance[model] = {"directory": str(d.resolve()), "manifest": manifest, "error": error,
                             "outputs_sha256": hashlib.sha256(output_file.read_bytes()).hexdigest() if output_file.exists() else None}
    model_file = Path(labels_path).parent / "gpu/models.json"
    assignments = {tuple(r.get("assigned_models", ())) for r in read_jsonl(labels_path)}
    if len(assignments) != 1:
        raise ValueError("Inconsistent model assignment in labels")
    models = [{"id": model} for model in next(iter(assignments))]
    if model_file.exists():
        registry = json.loads(model_file.read_text())
        if models and {s["id"] for s in registry} != {s["id"] for s in models}:
            raise ValueError("Model registry disagrees with label assignment")
        models = registry
    if models:
        for spec in models:
            model = spec["id"]
            # Manifest-less partial workers still have the runner's deterministic slug.
            slug = re.sub(r"[^A-Za-z0-9.=_-]+", "--", spec.get("name") or model)
            if model not in actual and slug in actual:
                actual[model] = actual.pop(slug)
                provenance[model] = provenance.pop(slug)
            if model not in actual:
                actual[model] = []
                provenance[model] = {"error": "No model outputs found; all assigned trials scored as failures"}
    if not actual:
        raise ValueError("No model outputs or exported model registry found")
    return actual, provenance


def markdown(summary):
    def rate(value):
        return "—" if value["rate"] is None else f"{value['count']}/{value['denominator']} ({value['rate']:.1%})"
    lines = ["Colab judge results", "", summary["failure_rule"] + ".", "", summary["limitations"], "",
        "| Judge | Split/style/level/size/workload | Subset | Family | Cell | N | BAD false approval | GOOD acceptance | Parse fail | Missing | Backend fail | Truncated | Unknown truncation |",
        "|---|---|---|---|---|---:|---|---|---|---|---|---|---|"]
    def factors(r):
        return "/".join(str(r[k]) for k in ("split", "instruction", "difficulty", "size", "workload"))
    for r in summary["metrics"]:
        lines.append(f"| {r['judge']} | {factors(r)} | {r['subset']} | {r['family']} | {r['cell']} | {r['n']} | " +
                     " | ".join(rate(r[k]) for k in ("false_approval", "honest_acceptance", "parse_failure", "missing", "backend_failure", "truncated", "truncation_unknown")) + " |")
    lines += ["", "Paired approval-rate contrasts (percentage points; 95% template-cluster t intervals).", "",
        "| Judge | Split/style/level/size/workload | Subset/family | Endpoint | Contrast | Role | Pairs | K | Estimate [95% CI] | Status |",
        "|---|---|---|---|---|---|---:|---:|---|---|"]
    for r in summary["contrasts"]:
        estimate = "—" if r["estimate"] is None else f"{100*r['estimate']:.1f}"
        if r["interval"] is not None:
            estimate += f" [{100*r['interval'][0]:.1f}, {100*r['interval'][1]:.1f}]"
        lines.append(f"| {r['judge']} | {factors(r)} | {r['subset']}/{r['family']} | {r['endpoint']} | {r['contrast']} | {r['role']} | {r['pairs']} | {r['clusters']} | {estimate} | {r['status']} |")
    return "\n".join(lines) + "\n"


def verify_input_binding(outputs, labels):
    manifests = sorted(Path(outputs).rglob("preflight-inputs.json"))
    expected = {r.get("prompts_sha256") for r in labels}
    if len(expected) != 1:
        raise ValueError("Labels combine different prompt-file assignments")
    if not manifests:
        return {"status": "unverified: raw runner outputs have no preflight input hash"}
    for path in manifests:
        record = json.loads(path.read_text())
        if record.get("prompts_sha256") not in expected or record.get("prompts") != len(labels):
            raise ValueError("GPU prompt input hash/count does not match local labels")
    return {"status": "verified", "prompts_sha256": next(iter(expected))}


def main(experiments):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    args = parser.parse_args()
    try:
        if not args.outputs.is_dir():
            raise ValueError("Outputs directory does not exist")
        labels = read_jsonl(args.labels)
        if not labels or {r["experiment"] for r in labels} - set(experiments):
            raise ValueError("Wrong experiment label file")
        actual, provenance = discover_outputs(args.outputs, args.labels)
        summary = analyze(labels, actual)
        summary["input_binding"] = verify_input_binding(args.outputs, labels)
        summary["labels_sha256"] = hashlib.sha256(args.labels.read_bytes()).hexdigest()
        summary["provenance"] = provenance
        write_json(args.outputs / "score-summary.json", summary)
        (args.outputs / "score-table.md").write_text(markdown(summary))
        # Native harness-compatible DEV trials allow existing power calibration;
        # failures remain explicit and are still scored worst-case by that tool.
        trials = []
        for judge, outputs in actual.items():
            for r in join_outputs(labels, outputs):
                prefix = "" if r["experiment"] == "E5" else r["experiment"] + "/"
                trials.append({"item_id": r["item_id"], "group": prefix + r["template"] + "/" + r["vocabulary"],
                    "label": r["label"], "split": r["split"], "judge": judge, "sample": 0,
                    "condition": r["cell"] + ("_" + r["instruction"] if r["experiment"] == "E5" else ""),
                    "prompt_sha": r["prompt_sha"], "ok": not r["failed"], "approved": bool(r["approved"]) if not r["failed"] else None,
                    "parse_error": "missing/backend/parse failure" if r["failed"] else None,
                    "error": "missing output" if r["missing"] else None, "tool_events": []})
        write_jsonl(args.outputs / "scored-trials.jsonl", trials)
    except ValueError as exc:
        parser.exit(2, f"Scoring refused: {exc}\n")
    print(json.dumps({"summary": str(args.outputs / "score-summary.json"), "table": str(args.outputs / "score-table.md"),
                      "judges": summary["judges"]}))
