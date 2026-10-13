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

each query of the readings suites and of the generated norm-defaults corpus asked as F1 (`Is it the case that <canonical sentence>?`) with ve ask, against ve document readings --conclusion on the same document and formula.

Scope: norm-defaults: seeds 0 to 449 of the 1,000 generated documents (`norm-defaults --trees 450`; the full run was stopped at 450 trees for time under load), 8 queries each; readings: the 8 distinct queries the readings suites ask in process (captured with `-p tools.question_answering_agreement`); the fixtures above. The 256 norm-defaults queries first refused for an exposition unit's null content were asked again after that fix (`tests/test_ask_null_free.py`).

| Corpus | Queries | agrees | ask refused | not asked | older route gave no verdict | requires review |
|---|---:|---:|---:|---:|---:|---:|
| norm-defaults | 3560 | 3555 | 0 | 0 | 1 | 4 |
| readings | 8 | 2 | 3 | 3 | 0 | 0 |

3568 queries; 4 required review:

- norm-defaults `s125`, Is it the case that every act must be done? every row yes, older UNKNOWN: reviewed (DELTA D15): the existing route's W2 fold answers UNKNOWN, 'no complete checked classification within the search budget'; ask's yes rests on a certificate Lean checked. An UNKNOWN does not contradict yes: an evidence difference, not a verdict contradiction.
- norm-defaults `s234`, Is it the case that every act may be tried? every row yes, older UNKNOWN: reviewed (DELTA D15): the existing route's W2 fold answers UNKNOWN, 'no complete checked classification within the search budget'; ask's yes rests on a certificate Lean checked. An UNKNOWN does not contradict yes: an evidence difference, not a verdict contradiction.
- norm-defaults `s312`, Is it the case that every act must be done? every row yes, older UNKNOWN: reviewed (DELTA D15): the existing route's W2 fold answers UNKNOWN, 'no complete checked classification within the search budget'; ask's yes rests on a certificate Lean checked. An UNKNOWN does not contradict yes: an evidence difference, not a verdict contradiction.
- norm-defaults `s361`, Is it the case that every act must be done? every row yes, older UNKNOWN: reviewed (DELTA D15): the existing route's W2 fold answers UNKNOWN, 'no complete checked classification within the search budget'; ask's yes rests on a certificate Lean checked. An UNKNOWN does not contradict yes: an evidence difference, not a verdict contradiction.

Queries not compared, by reason:

- ask refused: CheckerUnavailable: ask answers a readings document on the enumerated route with at most 64 compatible readings (1)
- ask refused: CheckerUnavailable: the answer's R1 line does not pass the all-derivations gate (1)
- ask refused: UnsupportedProfile: the document is not under the unspecified completion (1)
- older route gave no verdict: CheckerUnavailable (1)

## Scope

The evaluation made no model calls. Reader and writer accuracy, including the comparison of ‘No.’ and ‘Not necessarily.’, remains unmeasured.
