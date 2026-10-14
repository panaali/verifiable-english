# Question answering: Q2 non-model evidence

The recorded answer fixtures were replayed through Lean's `ask` mode by `tests/test_ask_fixtures.py`. The table records those saved results; it does not infer a new answer from the expected column.

| Fixture | Route | Lead | Rows | Replay wall s |
|---|---|---|---:|---:|
| A1 | norm-defaults | notSettled | 1 | 2.9 |
| A1d | — | refused: UnsupportedProfile | 0 | — |
| A2 | norm-defaults | unknown | 1 | 2.4 |
| A3 | norm-defaults | notNecessarily | 1 | 2.4 |
| A4 | norm-defaults | unknown | 1 | 2.9 |
| A5 | norm-defaults | unknown | 1 | 2.9 |
| A7 | norm-defaults | notSettled | 1 | 3.7 |
| A8 | norm-defaults | notSettled | 1 | 3.1 |
| G1 | plain | yes | 1 | 0.2 |
| G10 | plain | yes | 1 | 0.1 |
| G2 | plain | yes | 1 | 0.1 |
| G3 | plain | notNecessarily | 1 | 0.1 |
| G4 | plain | no | 1 | 0.1 |
| U2 | readings | yes | 6 | 10.9 |
| U3 | readings | by_reading | 6 | 8.6 |
| U5 | readings | by_reading | 6 | 7.4 |
| U6 | readings | yes | 6 | 10.9 |
| U7 | readings | by_reading | 6 | 4.7 |

## Timed requests

warm persistent ve_service; child CPU delta for second request; cold ve ask wall.

| Fixture | `english.question` Lean CPU s | `ask` Lean CPU s | `ve ask` wall s |
|---|---:|---:|---:|
| U3 | 0.06 | 0.7 | 11.007 |
| A1 | 0.07 | 0.6 | 199.109 |

## Existing verdict route

ve document readings --conclusion on each recorded question AST.

| Fixture | Ask lead | Older verdict | Comparison |
|---|---|---|---|
| G1 | yes | ALL | compared |
| G2 | yes | ALL | compared |
| G3 | notNecessarily | NONE | compared |
| G4 | no | NONE | compared |
| G10 | yes | ALL | compared |
| U2 | yes | ALL | compared |
| U3 | by_reading | SOME | compared |
| U5 | by_reading | SOME | compared |
| U6 | yes | ALL | compared |
| U7 | by_reading | UNKNOWN | compared |
| A1 | notSettled | UNKNOWN | compared |
| A1d | refused | — | outside ask route |
| A2 | unknown | UNKNOWN | compared |
| A3 | notNecessarily | UNKNOWN | compared |
| A4 | unknown | UNKNOWN | compared |
| A5 | unknown | UNKNOWN | compared |
| A7 | notSettled | UNKNOWN | compared |
| A8 | notSettled | UNKNOWN | compared |

The registered limits are `ask` CPU ≤ 2 s and U3 `ve ask` wall ≤ 60 s. These measurements used a warm persistent Lean service for CPU and a cold CLI process for wall time. `ask` CPU: U3 PASS, A1 PASS; U3 CLI wall: PASS.

## Agreement on the corpora

each query of the readings suites and of the generated norm-defaults corpus asked as F1 (`Is it the case that <canonical sentence>?`) with ve ask, against ve document readings --conclusion on the same document and formula; saved unknown leads were re-asked with Lean-checked conflict evidence to classify X1, with earlier full-replay reasons retained where recorded.

Scope: all 8 distinct captured readings-suite queries and 450 generated norm-defaults seeds (3560 distinct queries) (seeds 0–449; seeds 450–999 deferred by the DRI), with one ground and one universal query per regulated predicate.

| Corpus | Queries | ask refused | ask unknown (X1 conflict) | ask unknown (other) | compatible difference | not asked | older budget exhausted | same verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| norm-defaults | 3560 | 0 | 1448 | 5 | 771 | 0 | 4 | 1332 |
| readings | 8 | 2 | 1 | 0 | 1 | 3 | 0 | 1 |

Checked X1 conflicts where the older route answered ALL or NONE: 1392 (ALL 726; NONE 666).

3568 queries; 0 required review (no lead contradicts the existing route's verdict).


Queries not compared, by reason:

- ask refused: CheckerUnavailable: ask answers a readings document on the enumerated route with at most 64 compatible readings (1)
- ask refused: UnsupportedProfile: the document is not under the unspecified completion (1)

## Scope

The evaluation made no model calls. Reader and writer accuracy, including the comparison of ‘No.’ and ‘Not necessarily.’, remains unmeasured.
