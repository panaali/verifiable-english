# ar-10b delta: the route registry

No verdict, text, code, path, fault order or availability moves. The service states the same 37 modes in the same
order (`VE.Service.registry_modes`: the registry's modes are `modes`), and the client's `MODES` is that list, read
from `envelope.json` (`tests/test_lean_service.py::test_handshake` compares it with the live service). The client
now refuses a handshake whose modes are not exactly that list (before: a list containing each mode). The service
built from this tree always states exactly that list, so no user-visible answer changes; the five refused forms are
fixtures of `tests/test_lean_service.py::test_bad_or_missing_handshake_is_unavailable`.

| # | Change | Where | Test | Ruling |
|---|---|---|---|---|
| 1 | Trust budget: K +0, S +0, untied V +6, recorded with `tools/trust_map.py --allow` in `docs/trust-baseline.json`. Per file: `lean/VE/Service/Registry.lean` +61 (`Mode`, `Mode.name`, `Mode.ofName?` and `modes` moved from `Protocol.lean`; `RouteSpec` new; `registry` tied by `VE.Service.registry_modes`), `lean/VE/Service/Protocol.lean` −55. The lines replace the Python mode list `MODES` of `ve/backends/service_schema.py`, deleted in this item (0414d2d1c). | `lean/VE/Service/Registry.lean`, `lean/VE/Service/Protocol.lean` | `tools/trust_map.py --check`; [`mutants.json`](mutants.json) | SIGNED by standing ruling R6 (DRI-RULINGS.md) |
