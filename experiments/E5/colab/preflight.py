"""Standalone GPU-side exact context check; imports no repo or hidden labels.

The exported job runs this before loading model weights. Tokenizers may download
on the GPU; offline export only attempts local_files_only=True. No truncation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def token_count(tokenizer, row):
    # Match jobs_lib/vllm_judge.py: chat template first, no extra BOS on tokenization.
    text = tokenizer.apply_chat_template(row["messages"], add_generation_prompt=True, tokenize=False)
    return len(tokenizer(text, add_special_tokens=False).input_ids)


def check(rows, models, load_tokenizer):
    reports = []
    for spec in models:
        tokenizer = load_tokenizer(spec)
        lengths = [token_count(tokenizer, row) for row in rows]
        over = [{"key": row["key"], "prompt_tokens": n, "max_new_tokens": row["max_new_tokens"]}
                for row, n in zip(rows, lengths, strict=True) if n + row["max_new_tokens"] > spec["max_model_len"]]
        reports.append({"model": spec["id"], "max_model_len": spec["max_model_len"],
                        "n_prompts": len(rows), "max_prompt_tokens": max(lengths),
                        "max_total_tokens": max(n + r["max_new_tokens"] for r, n in zip(rows, lengths, strict=True)),
                        "prompts_over_6000": sum(n > 6000 for n in lengths),
                        "prompts_over_context": len(over), "overlength": over,
                        "tokenizer_revision": tokenizer.init_kwargs.get("_commit_hash")})
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompts", type=Path, required=True)
    parser.add_argument("--models", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=Path("out"))
    parser.add_argument("--run", type=Path, help="Runner file; invoked only if every assigned prompt fits")
    args = parser.parse_args()
    from transformers import AutoTokenizer
    from huggingface_hub import HfApi
    rows = [json.loads(line) for line in args.prompts.read_text().splitlines() if line.strip()]
    models = json.loads(args.models.read_text())
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "preflight-inputs.json").write_text(json.dumps({
        "prompts_sha256": hashlib.sha256(args.prompts.read_bytes()).hexdigest(), "prompts": len(rows),
        "models_sha256": hashlib.sha256(args.models.read_bytes()).hexdigest()}, indent=2) + "\n")
    # Resolve each model once, so tokenizer preflight and weight loading cannot
    # observe different upstream revisions. This downloads metadata, not weights.
    api = HfApi()
    models = [{**spec, "revision": api.model_info(spec["id"], revision=spec.get("revision")).sha}
              for spec in models]
    reports = check(rows, models, lambda spec: AutoTokenizer.from_pretrained(
        spec["id"], revision=spec.get("revision"), trust_remote_code=False))
    (args.out_dir / "preflight.json").write_text(json.dumps(reports, indent=2) + "\n")
    for r in reports:
        print(json.dumps({k: v for k, v in r.items() if k != "overlength"}), flush=True)
    if any(r["prompts_over_context"] for r in reports):
        parser.exit(2, "Context exceeded: refused ALL inference; no prompts truncated or excluded. See preflight.json.\n")
    if args.run:
        pinned = []
        for spec, report in zip(models, reports, strict=True):
            revision = spec["revision"]
            if not revision:
                parser.exit(2, "Cannot pin tokenizer/model revision; refusing inference.\n")
            pinned.append({**spec, "revision": revision})
        model_path = args.out_dir / "models-checked.json"
        model_path.write_text(json.dumps(pinned, indent=2) + "\n")
        raise SystemExit(subprocess.call([sys.executable, str(args.run), "--prompts", str(args.prompts),
            "--models", str(model_path), "--out-dir", str(args.out_dir), "--batch-size", "1",
            "--max-model-len", "8192", "--temperature", "0", "--seed", "0"]))


if __name__ == "__main__":
    main()
