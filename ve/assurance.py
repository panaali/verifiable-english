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
  a mode and case kind the manifest declares for that operation.

The guard never computes a verdict and never falls back to another engine.
"""
from __future__ import annotations

from contextlib import contextmanager
import functools
import json
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
    return _MANIFEST


def operation(op_id: str) -> dict:
    try:
        return OPERATIONS[op_id]
    except KeyError:
        raise KeyError(f"operation {op_id!r} is not in the assurance manifest") from None


def enforced_operations() -> frozenset[str]:
    """Operations whose verdict may only come from Lean on this run."""
    return _migrated | _simulated


def require_authority(op_id: str, engine: str) -> None:
    """Refuse a verdict for `op_id` from a non-authoritative `engine`."""
    if engine != "lean" and op_id in _migrated | _simulated:
        raise AuthorityViolation(
            f"{op_id} is Lean-authoritative; a {engine} implementation cannot produce its verdict",
            operation=op_id, backend=engine)


def semantic_entry(op_id: str, *, engine: str = "python"):
    """Register a verdict-producing function for `op_id` and guard its calls."""
    operation(op_id)
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


def require_lean_binding(op_id: str, executable: str, mode: str, kinds=()) -> None:
    """A Lean call must use a mode (and case kinds) the manifest declares for `op_id`."""
    lean = operation(op_id).get("lean") or {}
    for binding in lean.get("bindings", ()):
        if binding["executable"] == executable and binding["mode"] == mode and \
                set(kinds) <= set(binding.get("kinds", ())):
            return
    raise RuntimeError(f"Lean call {executable} {mode or '(default)'} {sorted(set(kinds))} "
                       f"is not declared for {op_id} in the assurance manifest")


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


def render_markdown() -> str:
    """The generated per-operation table in docs/spec/assurance-manifest.md."""
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
