# DEV export report

Offline exports only; model calls: **0**. All bundles retain the complete assignment.
Transformers and offline Qwen tokenizer files are unavailable locally. Exact 8k context fit and L4 memory fit are **unverified**. The generated job must pass exact-token preflight before loading weights.

| Bundle | Items | Prompts | Whitespace min / p50 / p95 / max | Punctuation proxy >6k (prompts/items) | Proxy prompt + 400 >8192 (prompts/items) |
|---|---:|---:|---|---:|---:|
| E5 medium neutral | 256 | 1280 | 1396 / 1536.5 / 1616.05 / 1678 | 256/256 | 2/2 |
| E5 medium audit | 256 | 1280 | 1410 / 1550.5 / 1630.05 / 1692 | 256/256 | 2/2 |
| E4 DEV | 16 | 48 | 149 / 157.5 / 163 / 163 | 0/0 | 0/0 |
| E2 DEV | 144 | 432 | 189 / 337.5 / 10898 / 11934 | 96/48 | 96/48 |

The punctuation proxy counts word and punctuation units separately. It is neither a Qwen token count nor a bound; counts above are risk flags, not exact overlength findings. Whitespace alone undercounts compact JSON. Model specs set `max_model_len: 8192`, with no shorter fallback or silent truncation.

All 256 E5 cell-e prompts in each style exceed 6k under the punctuation proxy. Two cell-e prompts per style exceed the 8k hint including the response cap under that proxy. E2 has 96 flagged prompts across 48 distinct items; these include all direct size-256 prompts and the growing size-256 checked prompts. Whitespace alone flags 24 E2 prompts across 24 items beyond the context hint.

| Bundle | Upload directory (only this child) | Local label sidecar |
|---|---|---|
| E5 medium neutral | `experiments/E5/colab/out/dev-medium/neutral/gpu/` | `experiments/E5/colab/out/dev-medium/neutral/labels.jsonl` |
| E5 medium audit | `experiments/E5/colab/out/dev-medium/audit/gpu/` | `experiments/E5/colab/out/dev-medium/audit/labels.jsonl` |
| E4 DEV | `experiments/E2E4/colab/out/dev/E4/gpu/` | `experiments/E2E4/colab/out/dev/E4/labels.jsonl` |
| E2 DEV | `experiments/E2E4/colab/out/dev/E2/gpu/` | `experiments/E2E4/colab/out/dev/E2/labels.jsonl` |

Paths are relative to `/Users/seyran/code/ve-codex`. There are **3,040 prompts** total, or 9,120 assigned trials if all three judges run every bundle once. No submission was performed. The Colab client copies every submission-directory file: never submit a parent containing labels.

The accompanying `dev-export-report.json` retains full per-cell/size/workload distributions, file hashes, source hashes and export manifests. Reproduce the underlying reports with the four export commands in the E5 and E2E4 Colab READMEs, choosing fresh output directories. Scored export remains refused because the PREREGs are drafts.

Merged-core artifact refresh: all 30,720 E5 prompts and 48 E4 DEV prompts are byte-identical to pre-refresh materials. Changed certified witnesses affect 48 E2 DEV, 96 E2 scored and 66 E4 scored prompts. Labels, IDs, splits and inference definitions are preserved; all 3,640 labels replay successfully. See `experiments/colab-material-refresh.json` for changed keys and prompt-stream hashes.
