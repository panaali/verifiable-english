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
| U3 | 0.05 | 2.83 | 7.813 |
| A1 | 0.06 | 0.6 | 126.855 |

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
| A1 | notSettled | — | older route exceeded 120 s wall |
| A1d | refused | — | outside ask route |
| A2 | unknown | — | older route exceeded 120 s wall |
| A3 | notNecessarily | — | older route exceeded 120 s wall |
| A4 | unknown | — | older route exceeded 120 s wall |
| A5 | unknown | — | older route exceeded 120 s wall |
| A7 | notSettled | — | older route exceeded 120 s wall |
| A8 | notSettled | — | older route exceeded 120 s wall |

The registered limits are `ask` CPU ≤ 2 s and U3 `ve ask` wall ≤ 60 s. These measurements used a warm persistent Lean service for CPU and a cold CLI process for wall time. `ask` CPU: U3 FAIL, A1 PASS; U3 CLI wall: PASS.

## Scope

The evaluation made no model calls. Reader and writer accuracy, including the comparison of ‘No.’ and ‘Not necessarily.’, remains unmeasured. The conformance-corpus agreement comparison with the older verdict routes is not yet recorded; this report does not claim that agreement gate has passed.
