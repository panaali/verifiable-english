**Recommendation:** adopt the proposed split in stages: Python for English, assist/IDE, web, CLI and harnesses; compiled Lean as the authority for checking, elaboration and model validation; Rust for fast evaluation/search. These measurements give no performance reason to retain duplicate Python semantic checkers, but do not establish that deleting them immediately preserves functionality.

Sources: [full report](results-full/REPORT.md), [raw measurements](results-full/results.json), [harness](run.py), and `~/code/manage-agents/bench-run.log`; measured commit `5c20b6b`.

Every ordinary measured Lean check meets the approximately 200 ms target, including its worst reported p95. The 2,047-node certificate does not reliably meet it. Each call checks **one case**; ranges below span repeated measurements at different batch sizes, not increasing case complexity.

| Workload | Lean call ms: median range / worst p95 | Lean median cases/s (batch size) |
|---|---:|---:|
| Tableau certificate | 84–91 / 184 | 1,576 (2,048) |
| Closure certificate | 57–61 / 70 | 1,798 (2,048) |
| Order/Farkas certificate | 54–63 / 117 | 1,870 (2,048) |
| Large tableau certificate | 76–152 / 248 | 33.5 (8) |
| Finite-model evaluation | 63–70 / 85 | 3,376 (2,048) |
| W1 norm elaboration | 90–102 / 122 | 3,269 (2,048) |
| W1 conflict replay | 78–109 / 120 | 548 (256) |
| W3 definitions | 52–116 / 123 | 2,058 (2,048) |
| W3 bundle | 50–54 / 56 | 1,258 (256) |
| English parse | 47–49 / 54 | 9,359 (512) |
| English admission fixture | 47–49 / 62 | 9,428 (512) |

Lean calls include process startup; Python/Rust calls are warmed. Batch rates also include startup. Most ordinary Python checks take 1–12 ms, definitions 17–44 ms: switching increases interactive latency. Large certificates improve from Python's 508–766 ms medians. Several serial Lean invocations per sentence can exceed 200 ms. Batch operations now; add persistent Lean IPC and measure it before promising IDE latency. Lean currently lacks JSON-lines service mode.

Pilot throughput looks adequate **when batched**: 2,048 definition cases take 0.995 s versus Python's 32.51 s; 256 bundles take 0.203 s versus 2.881 s; 256 conflicts take 0.468 s versus 1.131 s. Eight large certificates take 0.239 s versus 4.292 s. These are repeated independent fixtures, not growing documents; throughput cannot establish whole-document or end-to-end IDE performance.

Keep Rust for supported countermodel search and frequent evaluations: 22,145 searches/s versus Python's 1,215 (18.2×), and 6,646 evaluations/s versus Lean's 3,376 (2.0×). Rust warmed calls are roughly 0.6–1.0 ms/search and 2.4–2.5 ms/evaluation. Lean has countermodel validation but no search; validate final candidates there. Rust supplies none of the other measured checker routes. No evidence requires Rust for ordinary checking.

Removal needs adapters preserving Python result schemas, identities, diagnostics, traces and resource limits, plus packaged Lean executables and failure handling. Retain Python proof/certificate generators until replaced: certificate replay timings exclude generation. Full profile parity, negative inputs and standalone countermodel validation latency remain unmeasured. English's apparent speedup is not equivalent work: Lean receives pretokenized input/formulas and checks core syntax/typing; Python runs the full parser/reading audit. Keep that surface layer.

Noise limits confidence: load started at **2.26/2.42/2.22** on eight logical CPUs; JSON records approximately 2.37/2.44/2.23 before and 2.00/2.22/2.34 after. This neither proves saturation nor isolation. Five alternating repetitions give weak tail estimates; identical large-proof calls varied sharply. JSON/IPC are included, harness input serialization and builds excluded. Recheck realistic pilots and latency tails on a quiet machine before final deletion.
