# VE benchmark

Mode: **quick smoke**; 5 repetitions per measurement.

Times include runtime JSON decode/encode and IPC (input serialization by the harness is excluded). Batch throughput counts completed cases per wall second.
Python and Rust per-call figures use a persistent JSON-lines process; Lean per-call is one-shot.
Lean batch figures are amortized throughput in a single process, not interactive latency. Batch rates include process startup; interactive Python/Rust call latency follows one warm request.

| Workload | Cases | Proof nodes | Runtime | Startup median/p95 ms | Call median/p95 ms | Batch cases/s median/p95 |
|---|---:|---:|---|---:|---:|---:|
| certificate/tableau | 1 | — | python | 45.4968/51.8909 | 2.9843/4.3895 | 4.64/5.37 |
| certificate/tableau | 1 | — | lean_cert | 71.3031/78.6981 | 61.4466/65.8329 | 18.32/19.5 |
| certificate/tableau | 4 | — | python | 45.4968/51.8909 | 2.7807/6.6396 | 14.98/18.01 |
| certificate/tableau | 4 | — | lean_cert | 71.3031/78.6981 | 70.0206/75.4766 | 59.01/60.45 |
| certificate/tableau-large | 1 | 127 | python | 45.4968/51.8909 | 9.2284/10.0558 | 4.46/5.06 |
| certificate/tableau-large | 1 | 127 | lean_cert | 71.3031/78.6981 | 60.2732/66.7246 | 16.51/17.44 |
| certificate/tableau-large | 2 | 254 | python | 45.4968/51.8909 | 9.1062/11.198 | 8.1/8.18 |
| certificate/tableau-large | 2 | 254 | lean_cert | 71.3031/78.6981 | 66.7915/72.369 | 31.14/34.68 |
| certificate/closure | 1 | — | python | 45.4968/51.8909 | 5.1936/6.576 | 3.89/4.73 |
| certificate/closure | 1 | — | lean_cert | 71.3031/78.6981 | 57.9635/65.4382 | 15.39/20.0 |
| certificate/closure | 4 | — | python | 45.4968/51.8909 | 4.5291/5.7118 | 17.04/22.18 |
| certificate/closure | 4 | — | lean_cert | 71.3031/78.6981 | 60.9089/75.0214 | 56.17/73.3 |
| certificate/order-farkas | 1 | — | python | 45.4968/51.8909 | 2.8394/3.5348 | 4.69/6.4 |
| certificate/order-farkas | 1 | — | lean_order | 58.7983/61.4932 | 60.1739/65.027 | 17.94/20.63 |
| certificate/order-farkas | 4 | — | python | 45.4968/51.8909 | 3.3688/5.2721 | 15.87/17.32 |
| certificate/order-farkas | 4 | — | lean_order | 58.7983/61.4932 | 59.4126/74.8859 | 64.76/67.68 |
| finite-model/evaluation | 1 | — | python | 45.4968/51.8909 | 3.112/3.9728 | 4.54/5.44 |
| finite-model/evaluation | 1 | — | rust | 2.8498/5.5114 | 2.4866/2.5472 | 291.84/345.09 |
| finite-model/evaluation | 1 | — | lean | 64.7678/71.0105 | 51.8653/64.6355 | 16.71/18.21 |
| finite-model/evaluation | 4 | — | python | 45.4968/51.8909 | 3.0237/3.2335 | 17.77/21.93 |
| finite-model/evaluation | 4 | — | rust | 2.8498/5.5114 | 2.8276/3.1219 | 1012.09/1090.49 |
| finite-model/evaluation | 4 | — | lean | 64.7678/71.0105 | 55.7733/86.1657 | 72.18/79.3 |
| countermodel/search | 1 | — | python | 45.4968/51.8909 | 1.4523/1.6741 | 4.41/5.15 |
| countermodel/search | 1 | — | rust | 2.8498/5.5114 | 0.659/0.785 | 299.45/397.21 |
| countermodel/search | 4 | — | python | 45.4968/51.8909 | 1.5099/1.9752 | 17.73/20.85 |
| countermodel/search | 4 | — | rust | 2.8498/5.5114 | 0.6182/0.7263 | 1410.72/1528.97 |
| W1/norm-elaboration | 1 | — | python | 45.4968/51.8909 | 1.4782/2.9922 | 4.29/5.11 |
| W1/norm-elaboration | 1 | — | lean_norms | 60.8701/73.1888 | 61.5087/63.9978 | 17.26/17.86 |
| W1/norm-elaboration | 4 | — | python | 45.4968/51.8909 | 1.6097/1.7686 | 18.34/18.66 |
| W1/norm-elaboration | 4 | — | lean_norms | 60.8701/73.1888 | 60.1697/75.0055 | 64.26/68.93 |
| W1/conflict-check | 1 | — | python | 45.4968/51.8909 | 2.7231/2.9912 | 4.79/5.23 |
| W1/conflict-check | 1 | — | lean_norms | 60.8701/73.1888 | 59.8479/72.9342 | 14.94/17.23 |
| W1/conflict-check | 4 | — | python | 45.4968/51.8909 | 2.5703/3.083 | 19.66/21.41 |
| W1/conflict-check | 4 | — | lean_norms | 60.8701/73.1888 | 58.825/64.4724 | 67.08/78.24 |
| W3/definitions | 1 | — | python | 45.4968/51.8909 | 16.4524/18.1429 | 4.33/4.66 |
| W3/definitions | 1 | — | lean_route | 64.8151/65.8177 | 55.6314/67.3006 | 17.53/18.16 |
| W3/definitions | 4 | — | python | 45.4968/51.8909 | 18.3766/20.7164 | 15.35/16.98 |
| W3/definitions | 4 | — | lean_route | 64.8151/65.8177 | 57.7122/82.4844 | 65.87/72.86 |
| W3/bundle | 1 | — | python | 45.4968/51.8909 | 12.0416/12.7019 | 3.23/3.39 |
| W3/bundle | 1 | — | lean_route | 64.8151/65.8177 | 56.0937/60.0937 | 18.2/20.17 |
| W3/bundle | 4 | — | python | 45.4968/51.8909 | 16.0836/16.7492 | 9.41/11.4 |
| W3/bundle | 4 | — | lean_route | 64.8151/65.8177 | 57.1383/66.7307 | 66.9/72.27 |
| English/parse | 1 | — | python | 45.4968/51.8909 | 5.3033/7.3725 | 3.11/3.51 |
| English/parse | 1 | — | lean_english | 69.3352/74.772 | 57.9518/59.119 | 17.62/18.32 |
| English/parse | 4 | — | python | 45.4968/51.8909 | 4.6744/5.237 | 12.9/14.34 |
| English/parse | 4 | — | lean_english | 69.3352/74.772 | 52.9483/63.1596 | 78.48/87.78 |
| English/admission | 1 | — | python | 45.4968/51.8909 | 12.8249/14.0927 | 2.95/3.74 |
| English/admission | 1 | — | lean_english | 69.3352/74.772 | 56.3419/58.6805 | 19.21/20.65 |
| English/admission | 4 | — | python | 45.4968/51.8909 | 14.0281/14.7289 | 11.48/12.61 |
| English/admission | 4 | — | lean_english | 69.3352/74.772 | 51.7039/54.0783 | 74.35/76.69 |

Unsupported routes are omitted from the table: Rust has no certificate, norm, definition, bundle, or English checker; Lean has no interactive JSON-lines mode. Lean exposes countermodel checking but no search.

## Full measurement

```sh
PATH="$HOME/.elan/bin:$PATH" UV_CACHE_DIR=/tmp/ve-uv-cache uv run --frozen python -m bench.run --out bench-results
```

Expected duration: roughly 1–3 hours on an otherwise quiet workstation; the large certificate and 2,048-case search batches dominate. Build time is separate.
Build first: `PATH="$HOME/.elan/bin:$PATH" lake build` in `lean/`, and `cargo build --release --locked` in `rust/`.

These fixtures are deterministic development cases, not a representative workload sample. Batch size counts cases; each certificate case contains its own proof tree. Raw timings and input bytes are in `results.json`.
