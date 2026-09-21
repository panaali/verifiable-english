| Fixture | Size | Recorded comparison |
|---|---|---|
| `evaluation.json` | 701 cases; 4,912 formulas | Python / Lean / Rust evaluation and canonical text |
| `countermodels.json` | 708 | Python / Lean / Rust finite witnesses |
| `parser.json` | 742 | Python / Rust diagnostics; Lean acceptance/rejection |
| `identity.json` | 706 | Python / Rust hashes; Lean surface/evaluation only |
| `wire.json` | 40 | Python / Rust restricted JSON |
| `validation.json` | 43 | Python / Rust diagnostics; Lean rejection |
| `search.json` | 30 | Python / Rust bounded search / witnesses |
| `closure.json` | 46 cases; 866 formulas | Python / Lean evaluation and canonical text; no Rust |

<!-- src: conformance/{evaluation,countermodels,parser,identity,wire,validation,search,closure}.json; conformance/README.md for comparison scope. -->

| Development check | Recorded count |
|---|---|
| Recorded Python/Rust fuzz agreements | 5,000/5,000 |
| Certificate searches (all attempts) | 811 |
| Search Found / NotFound / ResourceLimit | 732 / 77 / 2 |
| Produced certificates accepted by Lean | 732/732 |
| Forged certificates rejected by Lean | 150/150 |

<!-- src: conformance/fuzz-summary.json; conformance/certificates-report.json. -->
