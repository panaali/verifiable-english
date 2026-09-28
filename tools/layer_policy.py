"""Single source of truth for the five repository layers.

The Stage 0 symbol/import inventory on mig/stage0 informed these module-level
assignments. A module with mixed responsibilities is assigned to its outermost
responsibility until it is split; exact legacy edges are tracked separately.
"""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = {1: "kernel", 2: "profiles", 3: "surface", 4: "tools", 5: "apps-and-measurements"}

PYTHON = {
    1: "ast environment errors identity limits model wire".split(),
    2: ("background closure definitions entailment evaluate norms order profiles").split(),
    3: ("english english_phrases english_vocabulary fluent fol grammar natural "
        "norm_english parser printer surface lexicon").split(),
    4: ("__main__ adapters admission argument attacks authoring bundle check "
        "document equivalence norm_admission norm_strict openterms propose readings "
        "search stream_audit vacuity assist").split(),
    5: ["argument_fixtures"],
}
PYTHON_MODULES = {f"ve.{name}": layer for layer, names in PYTHON.items() for name in names}


def python_exports(root: Path = ROOT) -> dict[str, str]:
    """Map public facade names to the modules that define them."""
    tree = ast.parse((root / "ve/__init__.py").read_text())
    return {alias.asname or alias.name: f"ve.{node.module}"
            for node in tree.body
            if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module
            for alias in node.names}


def python_imports(module: str, source: str, exports: dict[str, str],
                   *, root: Path, package: bool = False) -> set[str]:
    """Resolve local imports, including names reexported by the ve facade."""
    tree = ast.parse(source)
    imported = set()
    facade_aliases = set()

    def local_module(name: str) -> bool:
        path = root.joinpath(*name.split("."))
        return path.with_suffix(".py").exists() or (path / "__init__.py").exists()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
            facade_aliases.update(alias.asname or "ve" for alias in node.names
                                  if alias.name == "ve")
        elif isinstance(node, ast.ImportFrom):
            parts = module.split(".") if package else module.split(".")[:-1]
            if node.level:
                parts = parts[:len(parts) - node.level + 1]
            base = ".".join([*parts, *node.module.split(".")]) if node.module else ".".join(parts)
            if not node.level:
                base = node.module or ""
            if base == "ve":
                for alias in node.names:
                    if alias.name == "*":
                        imported.update(exports.values())
                    else:
                        target = exports.get(alias.name, f"ve.{alias.name}")
                        if target in exports.values() or local_module(target):
                            imported.add(target)
            else:
                submodules = {f"{base}.{alias.name}" for alias in node.names
                              if alias.name != "*" and local_module(f"{base}.{alias.name}")}
                imported.update(submodules)
                if len(submodules) < len(node.names):
                    imported.add(base)
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id in facade_aliases:
                target = exports.get(node.attr, f"ve.{node.attr}")
                if target in exports.values() or local_module(target):
                    imported.add(target)
    return imported


def python_layer(module: str) -> int | None:
    matches = [(len(prefix), layer) for prefix, layer in PYTHON_MODULES.items()
               if module == prefix or module.startswith(prefix + ".")]
    return max(matches)[1] if matches else None


def lean_layer(module: str) -> int | None:
    if module in {"VE", "VE.Audit", "Iceberg", "VE.Checks", "VE.Route.Checks"}:
        return 5  # aggregation and audit targets
    if module in {"Main", "NormsMain"} or module.endswith(".Run"):
        return 4
    if module.startswith("VE.English.") or module in {
        "VE.Surface", "VE.SurfaceProofs", "VE.ParserContracts", "VE.LexicalProofs",
        "VE.Order.Surface", "VE.Core.Surface", "VE.Closure.Surface",
    }:
        return 3
    if module.startswith(("VE.Core.", "VE.Json")) or module in {
        "VE.Syntax", "VE.Semantics", "VE.Typing", "VE.Finite", "VE.Consequence",
        "VE.Bridge", "VE.RoundTrip", "VE.CertificateWire", "VE.ClaimGraph",
        "VE.GraphChecks", "VE.ModelProofs", "VE.EnvironmentProofs",
        "VE.Tableau", "VE.TableauClosure", "VE.TableauChecker",
        "VE.TableauChecks", "VE.TableauExtended", "VE.TableauExtendedRules",
        "VE.TableauExtendedClosure", "VE.TableauExtendedExtra",
        "VE.TableauExtendedInduction", "VE.TableauExtendedChecker",
    }:
        return 1
    if module.startswith("VE."):
        return 2
    return None


def source_layer(path: str) -> int | None:
    """Return the innermost affected layer; unknown paths require a full run."""
    p = Path(path)
    parts = p.parts
    if not parts:
        return None
    if path in {"docs/english-surface.md", "docs/fluent-examples.md"}:
        return 1  # generated documents asserted by surface tests
    if p.suffix in {".md", ".rst"} and parts[0] not in {"tests", "conformance"}:
        return 5
    if parts[0] == "ve" and p.suffix == ".py":
        if path == "ve/__init__.py":
            return 1  # public API reexports all layers
        return python_layer(".".join(p.with_suffix("").parts))
    if parts[0] == "lean":
        if p.suffix == ".lean":
            return lean_layer(".".join(p.with_suffix("").parts[1:]))
        return 1 if p.name in {"lakefile.toml", "lean-toolchain", "lake-manifest.json"} else None
    if parts[0] == "rust":
        if p.suffix == ".rs":
            return 1 if len(parts) > 1 and parts[1] == "ve-core" else 4
        if p.suffix in {".py", ".json"} and p.name not in {"Cargo.lock"}:
            return 5  # benchmarks and generated measurement reports
        return 1 if p.name in {"Cargo.toml", "Cargo.lock"} else None
    if parts[0] in {"ve_experiments", "experiments", "usecases", "paper"}:
        return 5
    if parts[0] == "tools":
        if p.name in {"layer_policy.py", "select_tests.py", "mutation_check.py",
                      "check_python_layers.py", "check_lean_imports.py",
                      "check_rust_deps.py", "test_layer_policy.py"}:
            return 1  # changing the policy invalidates every selection
        return 4 if p.suffix == ".py" else None
    if parts[0] == "tests":
        return 1 if not p.name.startswith("test_") else 5
    if parts[0] == "conformance":
        return 1  # shared fixtures and generated reports are cross-cutting
    if path in {"pyproject.toml", "uv.lock", ".importlinter"}:
        return 1
    if parts[0] == "docs":
        return 5
    return None
