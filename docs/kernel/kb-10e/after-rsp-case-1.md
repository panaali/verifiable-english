| rsp-case-1.json, median of 5 | wall ms | CPU ms | answer |
|---|---:|---:|---|
| parse (bad kind) | 8.4 | 10.0 | error: UnsupportedProfile: case kind no-such-kind is not available on the soft-norms ro |
| source (no model) | 113.3 | 110.0 | error: property not found: model |
| vocabulary (model 7) | 705.0 | 700.0 | error: object expected |
| model (no query) | 711.1 | 710.0 | error: InvalidInput: soft-selected needs at least one query |
| 1 query | 1006.9 | 970.0 | ok |
| captured (8 queries) | 1024.4 | 1000.0 | ok |
| 200 queries | 1068.4 | 1050.0 | ok |
| handle: first call (registers, fresh process) | 135.1 | 130.0 | ok |
| handle: repeat call | 1.7 | 0.0 | ok |
| handle: first call (process holds another document), once | 128.1 | 130.0 | ok |
| handle: repeat call, 1 query | 1.0 | 0.0 | ok |
