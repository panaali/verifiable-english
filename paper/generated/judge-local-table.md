DEV-PILOT: local MLX, 4-bit; forced rows use log-probability verdict selection.

| Judge | False approval | Honest acceptance | Parse failures |
|---|---|---|---|
| Llama-3.2-1B | 107/109 (98.2%) | 39/48 (81.2%) | 24/157 (15.3%) |
| Llama-3.2-1B (forced) | 109/109 (100.0%) | 48/48 (100.0%) | 0/157 (0.0%) |
| Qwen2.5-0.5B | 107/109 (98.2%) | 42/48 (87.5%) | 19/157 (12.1%) |
| Qwen2.5-0.5B (forced) | 109/109 (100.0%) | 48/48 (100.0%) | 0/157 (0.0%) |
| Qwen2.5-1.5B | 109/109 (100.0%) | 45/48 (93.8%) | 20/157 (12.7%) |
| Qwen2.5-1.5B (forced) | 109/109 (100.0%) | 48/48 (100.0%) | 0/157 (0.0%) |
| Qwen2.5-3B | 99/109 (90.8%) | 41/48 (85.4%) | 16/157 (10.2%) |
| Qwen2.5-7B | 57/109 (52.3%) | 38/48 (79.2%) | 0/157 (0.0%) |
| gemma-2-2b (forced) | 109/109 (100.0%) | 48/48 (100.0%) | 0/157 (0.0%) |

<!-- src: paper/sources/local-ladder.md; original paths/revisions in paper/sources/manifest.json. -->
