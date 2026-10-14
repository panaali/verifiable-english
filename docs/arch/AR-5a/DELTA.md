# AR-5a: deltas

No product behaviour changes: the batch changes no file under `ve/`, `lean/` or `rust/` (the saved scope,
`evidence/scope.json`, lists every path). The deltas below are in development tools. None removes a check or a
field, and none accepts evidence the tools refused before.

| # | Tool | Delta | Ruling | Test |
|---|---|---|---|---|
| 1 | `tools/batch_evidence.py` (positional form) | Reads its three files with `tools.evidence.load`. A JSON object with a key twice, or an empty file, is now an error; `json.loads` kept the last row of a duplicated key. | SIGNED by standing ruling R11 (DRI-RULINGS.md): D4 adopts plan row AR-5a, whose latency "fails on empty, missing or duplicated keys" | `tests/test_evidence_toolkit.py::test_a_duplicated_latency_key_is_refused_when_read`, `::test_load_refuses_empty_and_missing_files` |
| 2 | `tools/batch_evidence.py` (positional form) | The latency failure keeps its line `latency evidence is empty, malformed or above the 20% Lean CPU budget` and adds one line per failing row naming the key. The gate, corpus and latency messages are otherwise unchanged. | SIGNED by standing ruling R3 (DRI-RULINGS.md): information is added, nothing is removed or renamed | `tests/test_evidence_toolkit.py::test_missing_empty_unavailable_or_slow_latency_rows_fail`, `tests/test_batch_evidence.py` (unchanged, passes) |
| 3 | `tools/readings_batch_latency.py` | Each sample row adds `pairs` and the record adds `allowance`; existing fields are unchanged. `pass` is computed by `tools/evidence/latency.py`. It is also false when a base sample is not positive, and two selected cases with one name are refused instead of the last replacing the first. | Added fields: SIGNED by standing ruling R3 (DRI-RULINGS.md). Refusals: SIGNED by standing ruling R11 (DRI-RULINGS.md), D4 / AR-5a "fails on empty, missing or duplicated keys" | `tests/test_evidence_toolkit.py::test_readings_batch_latency_applies_the_shared_rule`, `::test_readings_batch_latency_refuses_two_cases_with_one_name` |
| 4 | `tools/lean_service_latency.py` | None: `schedstat` moved to `tools/evidence/latency.py` and is imported. | n/a | `tests/test_evidence_tools.py`, `tests/test_lean_service.py::test_latency_harness_closes_every_cold_start` |
| 5 | `tools/gate-collection.json` | Adds the IDs of `tests/test_evidence_toolkit.py`; removes none. | SIGNED by standing ruling R12 (DRI-RULINGS.md): a generated inventory, regenerated with `tools/regen_generated.py --write --only gate-collection` | `tests/test_gate_collection.py` |

Merge resolution rule for the shared inventory (section 4.2): a conflict in `tools/gate-collection.json`
means taking `main`'s file and running `uv run python tools/regen_generated.py --write --only gate-collection`.
