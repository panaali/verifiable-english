"""Operation assurance manifest: runtime bindings and the authority guard.

`assurance-manifest.json` (specified in docs/spec/assurance-manifest.md) records,
for every public semantic operation, which engine is its verdict authority,
which Lean theorems and tests back it, and what is trusted. This module binds
the manifest to the code paths:

* `semantic_entry(op)` marks each Python function that produces a verdict for
  `op`. tests/test_assurance_manifest.py requires the marked set to equal the
  manifest's `python` entries exactly.
* The authority guard: once the manifest records an operation as `migrated`
  (SEMANTICS-MIGRATION-PLAN.md stage 4), a Python entry for it raises
  `AuthorityViolation`, a `CheckerUnavailable`, instead of producing a verdict,
  so that operation's verdict can only come from Lean. Nothing is migrated yet.
* `require_lean_binding` pins every Lean invocation (`ve.backends.lean.run`) to
  a mode and case kind the manifest declares for that operation, and
  `require_lean_call_site` to a calling function it declares.

The guard never computes a verdict and never falls back to another engine.
"""
from __future__ import annotations

from contextlib import contextmanager
import functools
import json
import sys
from pathlib import Path

from .errors import AuthorityViolation

MANIFEST_PATH = Path(__file__).with_name("assurance-manifest.json")
MANIFEST_VERSION = "ve-assurance-manifest@1"
AUTHORITIES = ("python", "migrated", "lean-only")
ENGINES = ("python", "lean", "rust")


def _load():
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if data.get("version") != MANIFEST_VERSION:
        raise RuntimeError(f"{MANIFEST_PATH.name} is not {MANIFEST_VERSION}")
    return data


_MANIFEST = _load()
OPERATIONS = {op["id"]: op for op in _MANIFEST["operations"]}
_migrated = frozenset(op_id for op_id, op in OPERATIONS.items() if op["authority"] == "migrated")
_simulated: frozenset[str] = frozenset()
# op id -> [(qualified name, engine)], filled as modules are imported.
ENTRIES: dict[str, list[tuple[str, str]]] = {}


def manifest() -> dict:
    """The parsed manifest (shared; do not mutate)."""
    sys.audit("ve.manifest.all")
    return _MANIFEST


def operation(op_id: str) -> dict:
    sys.audit("ve.manifest.operation", op_id)
    try:
        return OPERATIONS[op_id]
    except KeyError:
        raise KeyError(f"operation {op_id!r} is not in the assurance manifest") from None


def enforced_operations() -> frozenset[str]:
    """Operations whose verdict may only come from Lean on this run."""
    sys.audit("ve.manifest.all")
    return _migrated | _simulated


def require_authority(op_id: str, engine: str) -> None:
    """Refuse a verdict for `op_id` from a non-authoritative `engine`."""
    sys.audit("ve.manifest.operation", op_id)
    if engine != "lean" and op_id in _migrated | _simulated:
        raise AuthorityViolation(
            f"{op_id} is Lean-authoritative; a {engine} implementation cannot produce its verdict",
            operation=op_id, backend=engine)


def semantic_entry(op_id: str, *, engine: str = "python"):
    """Register a verdict-producing function for `op_id` and guard its calls."""
    # Registration needs only the id's presence. Reading the whole entry here
    # would make every importer of a registered function depend on every field.
    sys.audit("ve.manifest.presence", op_id)
    if op_id not in OPERATIONS:
        raise KeyError(f"operation {op_id!r} is not in the assurance manifest")
    if engine not in ENGINES:
        raise ValueError(f"unknown engine {engine!r}")

    def wrap(fn):
        ENTRIES.setdefault(op_id, []).append((f"{fn.__module__}:{fn.__qualname__}", engine))

        @functools.wraps(fn)
        def guarded(*args, **kwargs):
            if _migrated or _simulated:
                require_authority(op_id, engine)
            return fn(*args, **kwargs)

        guarded.__ve_operation__ = op_id
        guarded.__ve_engine__ = engine
        return guarded
    return wrap


def require_lean_binding(op_id: str, executable: str, mode: str, kinds=()) -> dict:
    """The binding the manifest declares for `op_id` with this mode (and case kinds).

    Its `response` names the fields every `ok` row of the operation carries.
    """
    lean = operation(op_id).get("lean") or {}
    for binding in lean.get("bindings", ()):
        if binding["executable"] == executable and binding["mode"] == mode and \
                set(kinds) <= set(binding.get("kinds", ())):
            return binding
    raise RuntimeError(f"Lean call {executable} {mode or '(default)'} {sorted(set(kinds))} "
                       f"is not declared for {op_id} in the assurance manifest")


def require_lean_call_site(op_id: str, frame) -> None:
    """A Lean call from inside `ve` must come from a declared `lean_call_sites` function.

    `frame` is the caller's frame. The static test finds the call sites however
    the backend is imported; this check also catches calls it cannot see
    (aliases through data, getattr). Callers outside the package (tests,
    tools) produce no public verdict and are not restricted.
    """
    module = frame.f_globals.get("__name__", "")
    if module != "ve" and not module.startswith("ve."):
        return
    site = f"{module}:{frame.f_code.co_qualname}"
    if site not in operation(op_id)["lean_call_sites"]:
        raise RuntimeError(f"{site} is not a declared Lean call site of {op_id} in the assurance manifest")


@contextmanager
def simulate_migration(*op_ids: str):
    """Enforce Lean authority for `op_ids` as if migrated (tests and rehearsals)."""
    global _simulated
    for op_id in op_ids:
        operation(op_id)
    previous = _simulated
    _simulated = previous | frozenset(op_ids)
    try:
        yield
    finally:
        _simulated = previous


def render_decoders_markdown() -> str:
    """The generated pinned-decoder table in docs/spec/assurance-manifest.md section 4."""
    sys.audit("ve.manifest.all")
    decoders = _MANIFEST["lean_decoders"]
    rows = ["| File | File lines | Decoder lines | Ranges | File SHA-256 |", "|---|---:|---:|---|---|"]
    for entry in decoders["files"]:
        count = sum(end - start + 1 for start, end in entry["ranges"])
        ranges = ", ".join(f"{start}–{end}" for start, end in entry["ranges"])
        rows.append(f"| `{entry['file']}` | {entry['lines']} | {count} | {ranges} | `{entry['sha256'][:12]}…` |")
    rows.append(f"| **total** | | **{decoders['total_lines']:,}** | | |")
    return "\n".join(rows) + "\n"


def render_markdown() -> str:
    """The generated per-operation table in docs/spec/assurance-manifest.md."""
    sys.audit("ve.manifest.all")
    def cell(values):
        return "<br>".join(f"`{v}`" for v in values) if values else "none"

    rows = ["| Operation | Class | Authority now → target | Assurance now / at switch | Python entries | "
            "Lean bindings | Lean theorems | Rust | Trusted |",
            "|---|---|---|---|---|---|---|---|---|"]
    for op in _MANIFEST["operations"]:
        lean = op.get("lean") or {}
        bindings = [" ".join(filter(None, (b["executable"], b["mode"] or "(default)",
                                           ",".join(b.get("kinds", ())))))
                    for b in lean.get("bindings", ())]
        theorems = list(lean.get("theorems", ()))
        theorems += [f"{name} (planned)" for name in lean.get("planned_theorems", ())]
        rust = (op.get("rust") or {}).get("commands", ())
        assurance = op["assurance"]
        rows.append(" | ".join((
            f"| `{op['id']}`", op["class"], f"{op['authority']} → {op['target']}",
            f"{assurance['current']} / {assurance['at_switch']}", cell(op["python"]),
            cell(bindings), cell(theorems), cell(rust), cell(op["trusted"]))) + " |")
    return "\n".join(rows) + "\n"
