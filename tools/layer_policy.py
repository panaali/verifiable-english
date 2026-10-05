"""Single source of truth for the five repository layers.

The Stage 0 symbol/import inventory on mig/stage0 informed these module-level
assignments. A module with mixed responsibilities is assigned to its outermost
responsibility until it is split; exact legacy edges are tracked separately.
"""
from __future__ import annotations

import ast
from functools import cache
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]
NAMES = {1: "kernel", 2: "profiles", 3: "surface", 4: "tools", 5: "apps-and-measurements"}

PYTHON = {
    1: "ast environment errors identity limits model wire wire_contract assurance".split(),
    2: ("background closure definitions entailment evaluate norms order profiles "
        "alternatives reports rights softnorms softnorms_contract norms_contract speech_acts units").split(),
    3: ("english english_phrases english_vocabulary fluent fol grammar natural "
        "norm_english parser printer surface lexicon report_english speech_english readings_english "
        "readings_s2_english").split(),
    4: ("__main__ adapters admission argument attacks authoring backends bundle check "
        "document equivalence norm_admission norm_defaults norm_defaults_contract norm_defaults_english norm_defaults_route norm_strict "
        "openterms propose readings search stream_audit vacuity assist discourse quantity_admission "
        "reports_route risk rights_route soft_route speech_document readings_route readings_s1 "
        "readings_sup readings_verdicts readings_s2_wording").split(),
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
        # A directory without __init__.py still imports, as a namespace package.
        path = root.joinpath(*name.split("."))
        return path.with_suffix(".py").exists() or path.is_dir()

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


@cache
def lean_executables(root: Path = ROOT) -> dict[str, str]:
    """Map each `lean_exe` in lean/lakefile.toml to its root module."""
    lakefile = tomllib.loads((root / "lean/lakefile.toml").read_text())
    return {exe["name"]: exe.get("root", exe["name"]) for exe in lakefile.get("lean_exe", [])}


def lean_default_targets(root: Path = ROOT) -> set[str]:
    """Targets a plain `lake build` produces; other executables must be named."""
    return set(tomllib.loads((root / "lean/lakefile.toml").read_text()).get("defaultTargets", []))


def lean_entry(module: str) -> bool:
    """Executable roots and top-level `*Main` modules are route and service entry points."""
    return module in lean_executables().values() or ("." not in module and module.endswith("Main"))


def lean_layer(module: str) -> int | None:
    if module in {"VE", "VE.Audit", "Iceberg", "VE.Checks", "VE.Route.Checks"}:
        return 5  # aggregation and audit targets
    if lean_entry(module) or module.endswith(".Run") or module.startswith("VE.Service."):
        return 4
    if module in {"VE.Norms.FlaggedSpec"}:
        return 4  # states theorems on Norms.Run.runCase (docs/CONSOLIDATION-PLAN.md step 1a)
    if module in {"VE.Route.RunSound", "VE.Norms.RunSound"}:
        return 4  # states theorems on Route.Run.runCase and Norms.Run.runCase (step 2a)
    if module.startswith(("VE.English.", "VE.Grammar.", "VE.EnglishGrammar.")) or module in {
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
            # The ve-core facade's tests exercise the whole API, so a change there selects as kernel.
            crate = parts[1] if len(parts) > 1 else ""
            return {"ve-kernel": 1, "ve-core": 1, "ve-profile": 2, "ve-surface": 3}.get(crate, 4)
        if p.suffix in {".py", ".json"} and p.name not in {"Cargo.lock"}:
            return 5  # benchmarks and generated measurement reports
        return 1 if p.name in {"Cargo.toml", "Cargo.lock"} else None
    if parts[0] in {"ve_experiments", "experiments", "usecases", "paper"}:
        return 5
    if parts[0] == "tools":
        if p.name in {"layer_policy.py", "select_tests.py", "mutation_check.py", "nested_pytest.py",
                      "check_python_layers.py", "check_lean_imports.py",
                      "check_rust_deps.py", "test_layer_policy.py", "lean_header_imports.lean"}:
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
