| pf-case-1.json, median of 5 | wall ms | CPU ms | answer |
|---|---:|---:|---|
| parse (bad kind) | 9.0 | 10.0 | error: UnsupportedProfile: case kind no-such-kind is not available on the soft-norms ro |
| source (no model) | 105.7 | 100.0 | error: property not found: model |
| vocabulary (model 7) | 632.3 | 630.0 | error: object expected |
| model (no query) | 705.5 | 680.0 | error: InvalidInput: soft-selected needs at least one query |
| 1 query | 987.4 | 980.0 | ok |
| captured (9 queries) | 949.2 | 930.0 | ok |
| 200 queries | 950.3 | 940.0 | ok |
| handle: first call (registers, fresh process) | 114.5 | 120.0 | ok |
| handle: repeat call | 2.1 | 0.0 | ok |
| handle: first call (process holds another document), once | 130.2 | 120.0 | ok |
| handle: repeat call, 1 query | 1.3 | 0.0 | ok |
