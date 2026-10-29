# Safety framework follow-ups

| Item | Follow-up | Evidence |
|---|---|---|
| Trust ties for route envelope guard | Tie the 13 S lines of `VE.Service.Standalone.routeHeaderAccepted` and the 2 V lines of its `reportedEnvironment` branch to the existing route envelope and response encoder theorems, including `VE.Route.Gate.decodeEnvelope_sound` and `ResponseShape.Encoders.Standalone.environment_reported`. | R16 allowance in `docs/trust-baseline.json`; `tests/test_difffuzz.py::test_request_envelope_fields_precede_predicate_sort_fault` |
| PF F5 modal strength | Seven must-to-should source mutants escape M6; add a source-sensitive modal-strength check in a later round. | `usecase-safetyfw-b-c290542-looprecheck2.final.md` F5 (C); DRI focus 2026-10-29 |
