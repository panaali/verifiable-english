| rsp-case-1.json, median of 5 | wall ms | CPU ms | answer |
|---|---:|---:|---|
| parse (bad kind) | 11.6 | 10.0 | error: UnsupportedProfile: case kind no-such-kind is not available on the soft-norms ro |
| source (no model) | 128.8 | 130.0 | error: property not found: model |
| vocabulary (model 7) | 836.1 | 840.0 | error: object expected |
| model (no query) | 792.9 | 790.0 | error: InvalidInput: soft-selected needs at least one query |
| 1 query | 1142.4 | 1120.0 | ok |
| captured (8 queries) | 1153.5 | 1140.0 | ok |
| 200 queries | 1194.2 | 1160.0 | ok |
