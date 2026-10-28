# Recipe: a relayed Lean route

Worked example: the `discourse` mode.

1. **Lean runner.** `lean/VE/Discourse/Run.lean` defines `VE.Discourse.Run.runCaseReported`.
   The mode is registered in `lean/VE/Service/Registry.lean` (its `Mode` constructor, name and `modes` entry).
   `VE.Service.runMode` in `lean/VE/Service/Protocol.lean` dispatches the mode to it, and the equation
   `VE.Service.runMode_discourse` is listed in `lean/VE/Audit.lean`.
2. **Shape.** `lean/ResponseShape/Schemas/Discourse.lean` writes the row's shape, typed to the leaves.
3. **Encoder theorem.** `lean/ResponseShape/Encoders/Discourse.lean` proves
   `ResponseShape.Encoders.Discourse.runCaseReported_fits`: every row the runner writes fits the shape.
   It is listed in `lean/ResponseShape/Audit.lean`.
4. **Generated schema.** `ve/backends/lean_service_schema/discourse.json`, rendered from the shape by
   `uv run python tools/response_schemas.py --write`. The handshake's mode list in
   `ve/backends/lean_service_schema/envelope.json` comes from the registry, and `MODES` of
   `ve/backends/service_schema.py` reads it; add the mode's CPU deadline to `DEADLINES` in
   `ve/backends/lean_service.py` (Python's operational policy).
5. **Python relay.** `ve/discourse.py` sends the case with `rows` from `ve/backends/relay.py` and binds
   the answer to the document it asked about; it checks schema and binding only (R8 in the DRI rulings).
6. **Fixtures.** Genuine cases recorded from the suite in `tests/data/route-cases.jsonl`
   (`tests/route_case_recorder.py`), checked against the schemas by `tests/test_route_row_schemas.py`;
   the route's own documents in `tests/test_discourse_lean.py`.
7. **Fuzz tests.** `tests/test_discourse_answer.py` mutates genuine answers one and two faults at a time
   (each member dropped, emptied, retyped, duplicated or reordered, an index pushed out of range):
   every mutant is `CheckerUnavailable` or changes nothing the relay shows.
