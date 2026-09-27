# Local VE runtime benchmark

Run from the repository root after building the native executables:

```sh
(cd lean && PATH="$HOME/.elan/bin:$PATH" lake build ve_conformance ve_norms_route ve_english_run)
(cd rust && cargo build --release --locked)
PATH="$HOME/.elan/bin:$PATH" UV_CACHE_DIR=/tmp/ve-uv-cache uv run --frozen python -m bench.run --out bench-results --quick
```

The **full** measurement command is:

```sh
PATH="$HOME/.elan/bin:$PATH" UV_CACHE_DIR=/tmp/ve-uv-cache uv run --frozen python -m bench.run --out bench-results
```

Expect roughly **1–3 hours** for the full measurement after builds, depending on the machine. `--quick` is a functional smoke run. Both write `results.json` and `REPORT.md` to `--out`. No model service is used.

The harness generates deterministic shared semantic cases. It times tableau, closure and order/Farkas certificate checking (including a 2,047-node certificate on the full run), finite-model evaluation, countermodel search, W1 norm elaboration and conflict certificate replay, W3 definition evaluation and bundle checking, plus English parse and checked-reading admission. Batch sizes grow per workload; the largest certificate batch traverses over 16,000 certificate nodes. Inputs for a row repeat the same case to isolate runtime scaling from fixture variation. The raw result records input byte counts, sample timings, commit, CPU model, version strings and load average before and after.

Python and Rust use persistent JSON-lines workers for warmed per-call latency. Lean has no JSON-lines mode, so its latency is a one-case process invocation, and its batch throughput uses each compiled executable's JSON-array input. Batch rates include startup; per-call Python and Rust times do not. Five repetitions alternate implementation order at every size. The harness checks semantic agreement on each shared case before timing. Rust lacks certificate, W1, W3 and English routes; Lean lacks countermodel search, so those comparisons use the available runtimes only. English Run checks the core token and formula layer while Python runs the full English parser and checked reading audit.

Run harness tests with `UV_CACHE_DIR=/tmp/ve-uv-cache uv run --frozen python -m pytest -q bench/test_harness.py`.
