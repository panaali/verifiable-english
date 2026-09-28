# English user paths: 16-vCPU VM profile

**Answer.** Python speed matters for long accepted English and editor catalogue tails. BlueDot's document breach is dominated by repeated model validation and hashing. Measure and remove redundant work before considering Rust. Warm-process Python 3.14.7, five sequential wall-time repeats per case; cProfile separately. Load was roughly 17–25 on 16 vCPUs. [Raw JSON](PROFILE-ENGLISH-BEFORE.json) includes each repeat, load, input hashes, and profiles. No proposer or model service was called.

| Accepted English tokens | Sentences / runs | Parse + one-reading audit + natural display, ms p50 / p95 / max |
|---|---:|---:|
| 5–19 | 10 / 50 | 29.9 / 79.4 / 115.5 |
| 20–39 | 6 / 30 | 46.0 / 84.3 / 85.8 |
| 40–79 | 4 / 20 | 102.1 / 133.8 / 153.4 |
| 80–159 | 2 / 10 | 129.1 / 194.3 / 204.7 |

P95 uses linear interpolation over pooled repeats. The longest admitted case (150 tokens, Claude excerpt corpus) was 158.4 / 200.1 / 204.7 ms, touching the ~200 ms budget. The 22 sentences come from the latest pilot documents and four corpora; Claude's pilot had one admitted five-token formula, UDHR none. The five longest pinned-source sentences per document (Claude 214–293 tokens, UDHR 55–348) were grammar-rejected before the derivation audit (0.4–2.8 ms median). The growth curve therefore covers admitted translations only. Longest-case cProfile: `require_unique_derivation` 0.51 s of 0.54 s inclusive, mainly Lark Earley (profiled time is inflated). Reuse the audit when natural rendering rechecks identical wording; then prune grammar alternatives.

| `ve document check` core (`check_document`) | Source bytes / units | ms p50 / p95 / max | Budget |
|---|---:|---:|---|
| Latest Claude pilot | 184,893 / 1,124 | 90.0 / 98.8 / 100.0 | <5 s |
| Latest UDHR pilot | 10,916 / 120 | 6.8 / 8.2 / 8.4 | <5 s |
| BlueDot grant | 7,619 / 93 | 18,919.9 / 21,939.9 / 22,208.4 | **>5 s** |

This is the CLI's core function, excluding startup and JSON printing. BlueDot cProfile: `premise_status` 34.4/34.6 s inclusive; `find_countermodel` 34.3 s; 10,001 `FiniteModel.from_dict` calls; 10,069 `environment_id` calls took 24.6 s through canonical JSON/digest. Compute immutable environment identity once per search, then prune models or reuse a witness. Claude's norm admission spent 0.14/0.27 profiled seconds in repeated canonical JSON/digest; cache stable digests if needed. Profile totals are diagnostic, not wall-time shares.

**Editor, proposer absent.** Raw source parse rejected in 0.7 ms (scope) and 0.2 ms (reference) p50. Catalogue produced one checked card per case, no pending pairs: scope 173.8 / 304.4 / 336.4 ms (**>200 ms tail**), reference 123.4 / 127.9 / 128.8 ms. Wording validation was 7.4 / 29.9 / 35.3 ms; scope recovery `classify` 181.6 / 183.1 / 183.3 ms. Catalogue cProfile made eight English parses, with 0.23/0.28 s inclusive in derivation audit. Cache checked card wording and AST; eliminate duplicate parses. Two local patterns do not establish a general editor p95.

**Reproduce.** The current harness uses a different sampling method, so a new run will not reproduce these historical numbers. From the repository root, use the [current harness command](PROFILE-ENGLISH-AFTER.md#reproduce) to collect comparable new measurements in a separate JSON file.
