"""Offline Colab exports. Hidden labels never enter the upload directory."""
from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
from statistics import mean
import subprocess

ROOT = Path(__file__).resolve().parents[1]
# ve_experiments.llm.DEFAULT_SYSTEM, claude/harness f016ab082fd8ad919fab6fc7c6ace87b50cb9677.
# The renderers receive Item.visible() exactly as runner.build_prompts does.
DEFAULT_SYSTEM = "You are a careful reviewer. Follow the instructions in the user message exactly."
MODEL_IDS = (
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2.5-14B-Instruct-AWQ",
    "Qwen/Qwen2.5-32B-Instruct-AWQ",
)
CONTEXT = 8192


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def write_jsonl(path, rows):
    with Path(path).open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")


def committed(path, root=ROOT):
    path, root = Path(path).resolve(), Path(root).resolve()
    rel = path.relative_to(root).as_posix()
    blob = subprocess.run(["git", "-C", str(root), "show", f"HEAD:{rel}"], capture_output=True)
    if blob.returncode or blob.stdout != path.read_bytes():
        raise ValueError(f"{rel} must be byte-identical to HEAD")


def read_budget(prereg, split, root=ROOT):
    raw = Path(prereg).read_bytes()
    if split == "scored":
        if not raw.splitlines() or raw.splitlines()[0] != b"Status: FROZEN":
            raise ValueError(f"Scored export refused: {prereg} must start with Status: FROZEN")
        committed(prereg, root)
    matches = re.findall(rb"^max_new_tokens: ([1-9][0-9]*)$", raw, re.M)
    if len(matches) != 1:
        raise ValueError(f"{prereg} must declare exactly one max_new_tokens budget")
    budget = int(matches[0])
    if budget >= CONTEXT:
        raise ValueError("Response budget must leave room for a prompt")
    return budget


def cells_arg(value, allowed):
    cells = tuple(value.split(",")) if value else tuple(allowed)
    if not cells or len(set(cells)) != len(cells) or set(cells) - set(allowed):
        raise ValueError(f"Cells must be distinct members of {','.join(allowed)}")
    return cells


def trial_rows(item, cell, instruction, prompt, budget, experiment):
    key = f"{item['id']}|{cell}|{instruction}"
    if item["id"] in prompt:
        raise ValueError("Item id leaked into judge message")
    a = item["payload"]["_audit"]
    control = a.get("control", "none")
    forged = (experiment == "E5" and a["family"] == "merged_vocabulary"
              and a["grounding_label"] == "bad" and a["tag_condition"] == "forged")
    label = {
        "key": key, "item_id": item["id"], "cell": cell, "instruction": instruction,
        "experiment": experiment, "split": item["split"], "label": item["label"],
        "family": a.get("family", a.get("error", a["template"])),
        "template": a["template"], "vocabulary": a["vocabulary_family"],
        "control": control != "none", "control_type": control, "forged_tag": forged,
        "tag_condition": "forged" if forged else "honest",
        "valid_deduction": not a.get("invalid_deduction", False) if experiment == "E5" else None,
        "difficulty": a.get("difficulty", "native"),
        "grounding_label": a.get("grounding_label"), "grounding_variant": a.get("grounding_variant"),
        "pair": a.get("pair"), "size": item["payload"].get("size"),
        "workload": a.get("workload"), "checker_visibility": a.get("checker_visibility"),
        "max_new_tokens": budget, "prompt_sha": hashlib.sha256(prompt.encode()).hexdigest()[:16],
        "assigned_models": list(MODEL_IDS),
    }
    return {"key": key, "messages": [{"role": "system", "content": DEFAULT_SYSTEM},
            {"role": "user", "content": prompt}], "max_new_tokens": budget}, label


def distribution(values):
    values = sorted(values)
    def quantile(p):
        loc = (len(values) - 1) * p
        lo = int(loc)
        return values[lo] + (values[min(lo + 1, len(values) - 1)] - values[lo]) * (loc - lo)
    return {"n": len(values), "min": values[0], "p50": quantile(.5), "p90": quantile(.9),
            "p95": quantile(.95), "p99": quantile(.99), "max": values[-1], "mean": mean(values)}


def length_stats(rows, lengths):
    return {"prompt_tokens": distribution(lengths),
            "prompt_plus_budget": distribution([n + r["max_new_tokens"] for r, n in zip(rows, lengths, strict=True)]),
            "prompts_over_6000": sum(n > 6000 for n in lengths),
            "items_over_6000": len({r["key"].split("|")[0] for r, n in zip(rows, lengths, strict=True) if n > 6000}),
            "prompts_over_context": sum(n + r["max_new_tokens"] > CONTEXT for r, n in zip(rows, lengths, strict=True)),
            "items_over_context": len({r["key"].split("|")[0] for r, n in zip(rows, lengths, strict=True)
                                       if n + r["max_new_tokens"] > CONTEXT})}


def length_report(rows, labels, models):
    # Punctuation counts supplement whitespace: minified JSON is otherwise one "word".
    text = ["\n".join(m["content"] for m in row["messages"]) for row in rows]
    words = [len(t.split()) for t in text]
    lexical = [len(re.findall(r"\w+|[^\w\s]", t)) for t in text]
    report = {"max_model_len_hint": CONTEXT, "max_prompt_tokens": CONTEXT - rows[0]["max_new_tokens"],
              "whitespace_proxy": length_stats(rows, words),
              "punctuation_proxy": length_stats(rows, lexical),
              "characters": distribution([len(t) for t in text]), "by_cell": {}, "tokenizers": {},
              "note": "Proxies exclude chat-template overhead and are NOT token counts or bounds. No prompts are truncated or excluded. Exact preflight is mandatory; 8k context does not guarantee 32B AWQ fits L4 GPU memory."}
    groups = defaultdict(list)
    for i, label in enumerate(labels):
        groups[(label["cell"], label["size"], label["workload"])].append(i)
    for (cell, size, workload), indices in groups.items():
        name = cell if size is None else f"{cell}|size={size}|workload={workload}"
        selected = [rows[i] for i in indices]
        report["by_cell"][name] = {"whitespace_proxy": length_stats(selected, [words[i] for i in indices]),
                                  "punctuation_proxy": length_stats(selected, [lexical[i] for i in indices])}
    available = importlib.util.find_spec("transformers") is not None
    for model in models:
        if not available:
            report["tokenizers"][model["id"]] = {"status": "unavailable_offline", "reason": "transformers is not installed"}
            continue
        from transformers import AutoTokenizer
        try:
            tokenizer = AutoTokenizer.from_pretrained(model["id"], local_files_only=True, trust_remote_code=False)
        except (OSError, ValueError) as exc:
            report["tokenizers"][model["id"]] = {"status": "unavailable_offline", "reason": type(exc).__name__}
            continue
        from experiments.E5.colab.preflight import token_count
        counts = [token_count(tokenizer, row) for row in rows]
        report["tokenizers"][model["id"]] = {"status": "exact_offline", **length_stats(rows, counts)}
    exact = list(report["tokenizers"].values())
    report["context_fit"] = ("exceeds_context" if any(r.get("prompts_over_context", 0) for r in exact)
                             else "verified" if all(r["status"] == "exact_offline" for r in exact)
                             else "UNVERIFIED_REQUIRES_PREFLIGHT")
    return report


def export_bundle(out, rows, labels, *, prereg, sources, split, experiment, selection):
    source_dir = "E5" if experiment == "E5" else "E2E4"
    sources = [*sources, Path(__file__).resolve(), ROOT / f"experiments/{source_dir}/colab/export_prompts.py",
               ROOT / "experiments/E5/colab/preflight.py"]
    if not rows or len(rows) != len(labels) or len({r["key"] for r in rows}) != len(rows):
        raise ValueError("Export must contain unique nonempty paired prompts and labels")
    if [r["key"] for r in rows] != [r["key"] for r in labels]:
        raise ValueError("Prompt/label assignment mismatch")
    if split == "scored":
        for path in sources:
            committed(path)
    models = [{"id": model, "max_model_len": CONTEXT, "gpu_memory_utilization": .9,
               "max_num_seqs": 1, "enforce_eager": True,
               **({"quantization": "awq", "dtype": "half"} if model.endswith("AWQ") else {})}
              for model in MODEL_IDS]
    lengths = length_report(rows, labels, models)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)  # never mix styles/assignments or overwrite exports
    gpu = out / "gpu"
    gpu.mkdir()
    write_jsonl(gpu / "prompts.jsonl", rows)
    prompts_sha = sha(gpu / "prompts.jsonl")
    for label in labels:
        label["prompts_sha256"] = prompts_sha
    write_jsonl(out / "labels.jsonl", labels)
    write_json(gpu / "models.json", models)
    shutil.copyfile(ROOT / "experiments/E5/colab/preflight.py", gpu / "preflight.py")
    identifier = f"{experiment.lower()}-{split}-{selection}-" + sha(gpu / "prompts.jsonl")[:10]
    write_json(gpu / "job.json", {
        "id": identifier,
        "cmd": "python preflight.py --prompts prompts.jsonl --models models.json --out-dir out --run vllm_judge.py",
        "inputs": ["jobs_lib/vllm_judge.py"], "pip": ["vllm"], "outputs": ["out/**"], "max_minutes": 180,
    })
    write_json(out / "lengths.json", lengths)
    manifest = {"experiment": experiment, "split": split, "selection": selection,
                "prompts": len(rows), "items": len({r["item_id"] for r in labels}),
                "cells": sorted({r["cell"] for r in labels}), "instructions": sorted({r["instruction"] for r in labels}),
                "max_new_tokens": rows[0]["max_new_tokens"], "model_calls": 0,
                "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "harness_system_source": "claude/harness:f016ab082fd8ad919fab6fc7c6ace87b50cb9677:ve_experiments/llm.py",
                "sources_sha256": {str(Path(p).relative_to(ROOT)): sha(p) for p in [prereg, *sources]},
                "files_sha256": {str(p.relative_to(out)): sha(p) for p in sorted(out.rglob('*')) if p.is_file()},
                "upload_directory": "gpu", "labels_upload": False, "context_fit": lengths["context_fit"]}
    write_json(out / "manifest.json", manifest)
    print(json.dumps({"out": str(out.resolve()), **{k: manifest[k] for k in ("prompts", "items", "context_fit")}}))
    return manifest
