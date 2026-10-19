"""The initial v0 runtime envelope; these bounds are not logical axioms.

Lean owns every limit (`lean/VE/Limits.lean`, lean-first batch 18). The service states them in
its handshake (`VE.Limits.stated`), the response schema rendered from the Lean shapes pins each
one (`lean_service_schema/envelope.json`, `handshake.limits`), and this module reads them from
there; the client refuses a service whose handshake states other values (`check_handshake`).
"""
import json
from pathlib import Path

_STATED = {name: schema["const"] for name, schema in json.loads(
    (Path(__file__).resolve().parent / "backends/lean_service_schema/envelope.json").read_text()
)["handshake"]["properties"]["limits"]["properties"].items()}

MAX_SOURCE_BYTES = _STATED["max_source_bytes"]
MAX_PACKAGE_BYTES = _STATED["max_package_bytes"]
MAX_DEPTH = _STATED["max_depth"]
MAX_NODES = _STATED["max_nodes"]
MAX_SORTS = _STATED["max_sorts"]
MAX_PREDICATES = _STATED["max_predicates"]
MAX_ENTITIES = _STATED["max_entities"]
MAX_TUPLES = _STATED["max_tuples"]
MAX_IDENTIFIER_BYTES = _STATED["max_identifier_bytes"]
MAX_EVALUATIONS = _STATED["max_evaluations"]
MAX_INDEX = _STATED["max_index"]
MAX_JSON_DEPTH = _STATED["json_depth"]
# The service's request caps: its longest request line and most cases per request.
MAX_LINE_BYTES = _STATED["max_line_bytes"]
MAX_CASES = _STATED["max_cases"]
# The Rust binary's memory budget (`VE_RUST_MEMORY_LIMIT`; rust/ve/src/memory.rs DEFAULT_LIMIT).
MAX_RUST_MEMORY_BYTES = 8 << 30

# Each tableau expansion nests a children array and a node object. Reserve
# eight levels for the certificate and its argument-package envelope.
MAX_TABLEAU_DEPTH = (MAX_JSON_DEPTH - 8) // 2
