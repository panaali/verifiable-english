"""Audit every prompt after a core/certificate refresh; refuse changed E5 prompts."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

from experiments.colab_common import ROOT, write_json
from experiments.E5.materials import render_cell as render_e5
from experiments.E2E4.materials import load_frozen, render_cell, E2_CELLS, E4_CELLS
from experiments.trial_analysis import read_jsonl


def check(before):
    def archive(path):
        raw = subprocess.check_output(["git", "show", f"{before}:{path}"], cwd=ROOT)
        return [json.loads(line) for line in gzip.decompress(raw).decode().splitlines()]
    certificates = {}
    rows = []
    for ex in ("E5", "E2", "E4"):
        for split in ("dev", "scored"):
            path = f"experiments/E5/{split}.jsonl.gz" if ex == "E5" else f"experiments/E2E4/{ex.lower()}-{split}.jsonl.gz"
            old = archive(path)
            new = read_jsonl(ROOT / path) if ex == "E5" else load_frozen(split, ex)
            if ex == "E2":
                for item in old:
                    p = item["payload"]
                    template = p["template"]
                    if template not in certificates:
                        certificates[template] = {r["ref"]: r["check"] for r in
                            archive(f"experiments/E2E4/certificates/{template}.jsonl.gz")}
                    p["checks"] = {ref: certificates[template][ref] for ref in p.pop("check_refs")}
            indexed = {r["id"]: r for r in new}
            assert {r["id"] for r in old} == set(indexed)
            digests = [hashlib.sha256(), hashlib.sha256()]
            count, changed = 0, []
            for item in old:
                current = indexed[item["id"]]
                assert all(item[k] == current[k] for k in ("id", "label", "group", "split"))
                if ex != "E5":
                    omitted = {"checks", "checker_output"} if ex == "E2" else {
                        "check", "oracle", "asserted_model", "asserted_model_check", "critiques"}
                    assert {k: v for k, v in item["payload"].items() if k not in omitted} == {
                        k: v for k, v in current["payload"].items() if k not in omitted}
                    if ex == "E2":
                        def without_models(report):
                            return {**report, "unresolved_steps": [{k: v for k, v in step.items()
                                if k != "checked_countermodels"} for step in report["unresolved_steps"]]}
                        assert without_models(item["payload"]["checker_output"]) == without_models(current["payload"]["checker_output"])
                conditions = [(c, style) for c in "abcde" for style in ("neutral", "audit")] if ex == "E5" else [
                    (c, "harness") for c in (E2_CELLS if ex == "E2" else E4_CELLS)]
                for cell, style in conditions:
                    texts = [render_e5(r, cell, style) if ex == "E5" else render_cell(r, cell) for r in (item, current)]
                    key = f"{item['id']}|{cell}|{style}"
                    if texts[0] != texts[1]:
                        assert ex != "E5", f"Changed E5 prompt: {key}"
                        changed.append(key)
                    for digest, text in zip(digests, texts, strict=True):
                        digest.update((key + "\0" + text + "\0").encode())
                    count += 1
            rows.append({"experiment": ex, "split": split, "items": len(old), "prompts": count,
                         "identical_prompts": count - len(changed), "changed_prompts": len(changed),
                         "changed_keys": changed, "old_prompt_stream_sha256": digests[0].hexdigest(),
                         "new_prompt_stream_sha256": digests[1].hexdigest()})
    return {"before": subprocess.check_output(["git", "rev-parse", before], cwd=ROOT, text=True).strip(),
            "model_calls": 0, "labels_ids_splits_and_inference_definitions_preserved": True,
            "note": "E5 prompts unchanged. New core model enumeration can change certified E2/E4 witnesses and their displayed critiques; all labels are independently replayed by validate_materials.",
            "results": rows, "total_identical_prompts": sum(r["identical_prompts"] for r in rows),
            "total_changed_prompts": sum(r["changed_prompts"] for r in rows)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = check(args.before)
    write_json(args.out, result)
    print(json.dumps({**result, "results": [{k: v for k, v in r.items() if k != "changed_keys"}
                                          for r in result["results"]]}, indent=2))
