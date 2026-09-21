"""Independently replay frozen E5/E2/E4 labels; no generation and no model calls."""
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path

from ve import ArgumentGraph, FiniteModel, check_argument
from ve.parser import parse
from ve.search import check_countermodel
from experiments.E5.materials import HERE, grounding_audit, graph_for_payload, render_cell as e5_render
from experiments.E2E4.materials import load_frozen, validate_e2, construction_support, replay, render_cell

ROOT = Path(__file__).resolve().parent


def main():
    report = {"model_calls": 0, "inputs": {}, "experiments": {}, "E5_positions": {}, "E4_critique_lengths": {}}
    cert_path = HERE / "certificates.jsonl.gz"
    report["inputs"][str(cert_path.relative_to(ROOT))] = hashlib.sha256(cert_path.read_bytes()).hexdigest()
    with gzip.open(cert_path, "rt") as f:
        graphs = {(r["template"], r["vocabulary_family"], r["control"], r["graph_size"]): ArgumentGraph.from_dict(r["graph"])
                  for line in f if (r := json.loads(line))}
    positions = defaultdict(Counter)
    results = Counter()
    for split in ("dev", "scored"):
        path = HERE / f"{split}.jsonl.gz"
        report["inputs"][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        with gzip.open(path, "rt") as f:
            for line in f:
                row = json.loads(line)
                p, a = row["payload"], row["payload"]["_audit"]
                support = grounding_audit(p)
                base = graphs[a["template"], a["vocabulary_family"], a["control"], p["knobs"]["graph_size"]]
                result = check_argument(graph_for_payload(p, (base, None, None)), search=False)
                assert not result.errors
                assert support["label"] == a["grounding_label"]
                assert result.status == p["checker"]["status"]
                assert (support["label"] == "good" and result.composed) == (row["label"] == "good")
                results[split, row["label"]] += 1
                if a["grounding_label"] == "bad":
                    positions[f"{a['difficulty']}/flawed_leaf"][a["flawed_leaf"]] += 1
                    index = next(i for i, r in enumerate(p["records"], 1) if r["record_id"] == a["flawed_record"])
                    positions[f"{a['difficulty']}/record_ordinal"][str(index)] += 1
                if a["invalid_edge"] and a["grounding_label"] == "good":
                    positions[f"{a['difficulty']}/{a['control']}"][a["invalid_edge"]] += 1
    report["experiments"]["E5"] = {"labels_proved": sum(results.values()), "counts": {f"{s}/{label}": n for (s, label), n in sorted(results.items())}}
    report["E5_positions"] = {k: dict(sorted(v.items())) for k, v in sorted(positions.items())}
    lengths = defaultdict(list)
    for experiment in ("E2", "E4"):
        results = Counter()
        for split in ("dev", "scored"):
            path = ROOT / "E2E4" / f"{experiment.lower()}-{split}.jsonl.gz"
            report["inputs"][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
            for row in load_frozen(split, experiment):
                p = row["payload"]
                if experiment == "E2":
                    result = validate_e2(p)
                    assert result == p["checker_output"]
                    good = result["all_local_edges_follow"] and construction_support(p) and p["submitted_root"]["source"] == p["intended_source"]
                else:
                    result = replay(p["check"])
                    assert result == p["check"]["result"]
                    good = result["composed"]
                    graph = ArgumentGraph.from_dict(p["check"]["graph"])
                    premises = [parse(graph.env, s + "\n").formulas[0] for s in p["premises"]]
                    conclusion = parse(graph.env, p["conclusion"] + "\n").formulas[0]
                    asserted = check_countermodel(graph.env, premises, conclusion, FiniteModel.from_dict(graph.env, p["asserted_model"]))
                    assert asserted.valid == (not good)
                    assert len({len(v.split()) for v in p["critiques"].values()}) == 1
                    for cell, text in p["critiques"].items():
                        lengths[cell].append((len(text.split()), len(text)))
                assert good == (row["label"] == "good")
                results[split, row["label"]] += 1
        report["experiments"][experiment] = {"labels_proved": sum(results.values()), "counts": {f"{s}/{label}": n for (s, label), n in sorted(results.items())}}
    for path in sorted((ROOT / "E2E4/certificates").glob("*.gz")):
        report["inputs"][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    report["E4_critique_lengths"] = {cell: {"min_words": min(w for w, _ in v), "max_words": max(w for w, _ in v),
        "mean_words": sum(w for w, _ in v)/len(v), "mean_characters": sum(c for _, c in v)/len(v)} for cell, v in lengths.items()}
    (ROOT / "material-validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"model_calls": 0, "experiments": report["experiments"]}, indent=2))


if __name__ == "__main__":
    main()
