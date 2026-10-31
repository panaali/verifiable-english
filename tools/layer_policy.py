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

# Python's five layers after lean-first (architecture plan T5, DRI decision D5). An import points inward: to its own
# layer or a lower one; tools/check_python_layers.py and the generated `.importlinter` enforce it. A package's row
# places every module under it, so a new module there needs no row; a longer row overrides it where the module's
# role is not its package's. A module that no row places fails the check: there is no default layer.
PYTHON = {
    # 1 transport and wire: errors, wire forms, limits, the profile table the wire projects through, the service
    # clients and the one relay (`ve.backends`).
    1: "errors wire environment_wire limits backends wire_contract assurance profiles".split(),
    # 2 containers built from Lean's answers, their identities, and the encoders of the cases they send: the Lean
    # cases (`backends.lean_runner`) and Rust's case lines (`backends.rust_jsonl`) encode these containers.
    2: ("ast environment model identity background closure definitions entailment evaluate norms order "
        "alternatives rights softnorms norms_contract speech_acts units "
        "backends.lean_runner backends.rust_jsonl").split(),
    # 3 display and English rendering; `backends.english_lean` decodes Lean's English reading into the AST and
    # prints it.
    3: ("english english_grammar english_phrases english_vocabulary fluent fol grammar natural "
        "norm_english parser printer surface lexicon report_english speech_english readings_english "
        "readings_s2_english senses backends.english_lean").split(),
    # 4 CLI, documents, assist, adapters and route modules; `backends.senses` and `backends.speech_source` are
    # the senses and speech-source routes (they read the English parser and build environments).
    4: ("__main__ adapters admission argument ask attacks authoring bundle check "
        "document equivalence norm_admission norm_defaults norm_defaults_contract norm_defaults_english norm_defaults_route norm_strict "
        "defaults_english filling_search openterms propose readings search stream_audit vacuity assist discourse words calc scope "
        "reports reports_route risk rights_route soft_route speech_document readings_route readings_s1 "
        "readings_sup readings_verdicts readings_components readings_s2_wording senses_document defaults "
        "backends.senses backends.speech_source").split(),
    # 5 apps: fixtures and the experiments (every module of the APP_AREAS trees below).
    5: ["argument_fixtures"],
}
# Python modules off the live Lean path, kept only for the files that still import them (no other file may).
# `ve.openterms`: a document Lean's `document` mode answers takes its open terms from Lean's W2 check (jt-2b); Python's
# own path for a document Lean cannot decide yet, and the frozen speech snapshot, still read it.
RETAINED = {"ve.openterms": ("ve/document/load.py", "tests/frozen_speech/speech_document.py")}
# Top-level trees of apps, experiments, research and the paper: every path in them is layer 5.
APP_AREAS = frozenset({"ve_experiments", "experiments", "usecases", "paper", "research"})
PYTHON_MODULES = {f"ve.{name}": layer for layer, names in PYTHON.items() for name in names}


def lazy_exports(tree: ast.Module) -> dict[str, str]:
    """A package `__init__`'s lazy table, `_EXPORTS = {"module": ("name", ...)}`, which `ve/__init__.py`'s
    `__getattr__` resolves (PEP 562), as {name: module}. The one reader of that table: the layer check, the
    pre-commit hook, test selection (`tools/change_units.py`) and the semantic inventory reach it through here."""
    for node in tree.body:
        if isinstance(node, ast.Assign) and [getattr(t, "id", None) for t in node.targets] == ["_EXPORTS"]:
            return {name: module for module, names in ast.literal_eval(node.value).items() for name in names}
    return {}


def facade_table(tree: ast.Module) -> dict[str, str]:
    """A package `__init__`'s public names and the submodules (relative names) that define them: its
    `from .module import name` lines and its lazy table."""
    return {**{alias.asname or alias.name: node.module
               for node in tree.body if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module
               for alias in node.names},
            **lazy_exports(tree)}


def python_exports(root: Path = ROOT) -> dict[str, str]:
    """Map public facade names to the modules that define them."""
    return {name: f"ve.{module}"
            for name, module in facade_table(ast.parse((root / "ve/__init__.py").read_text())).items()}


def python_imports(module: str, source: str, exports: dict[str, str],
                   *, root: Path, package: bool = False) -> set[str]:
    """Resolve local imports, including names reexported by the ve facade.

    The pre-commit hook (tools/hooks/precommit.py) resolves each staged file with this, one file at a time and
    without the rest of the tree; tools/check_python_layers.py leaves the whole tree to import-linter.
    """
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
    """A Python module's layer: its longest row, or 5 in an app area; None when nothing places it."""
    if module.split(".")[0] in APP_AREAS:
        return 5
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
    if module in {"VE", "VE.Audit", "ResponseShapeAudit", "Iceberg", "VE.Checks", "VE.Route.Checks", "VE.LimitTies"}:
        return 5  # aggregation and audit targets (VE.LimitTies checks frozen and hashed copies of VE.Limits)
    if module in {"VE.EnglishGrammar.ProfileExamples", "VE.EnglishGrammar.E2Examples",
                  "VE.Question.Examples", "VE.Question.Fixtures", "VE.Alternatives.FillExamples",
                  "VE.Calc.RunExamples", "VE.Defaults.RouteExamples", "VE.Readings.ActsExamples",
                  "VE.Cardinality.RunExamples", "VE.Scope.RunExamples"}:
        return 4  # runner-boundary acceptance fixtures import EnglishGrammar.Run, Question.Run, Alternatives.Run, Calc.Run,
        # NormDefaults.Run, Readings.Run, Cardinality.Run or Scope.Run
    if lean_entry(module) or module.endswith(".Run") or module == "VE.Route.MeteredRun" or module.startswith("VE.Service."):
        return 4
    if module == "ResponseShape" or module.startswith("ResponseShape."):
        return 4  # the service's response shapes: ve_response_decode and the client's schema source
    if module in {"VE.Norms.FlaggedSpec"}:
        return 4  # states theorems on Norms.Run.runCase (docs/CONSOLIDATION-PLAN.md step 1a)
    if module in {"VE.Route.RunSound", "VE.Norms.RunSound", "VE.Cardinality.RunTheorems"}:
        return 4  # states theorems on Route.Run.runCase and Norms.Run.runCase (step 2a), and on Cardinality.Run's runner
    if module in {"VE.Question.Spans"}:
        return 4  # states theorems on EnglishGrammar.Run.codepointsBefore (question answering Q1.1)
    if module.startswith("VE.Ask."):
        return 4  # question answering Q2: binds a request to Service.Document's split and reads EnglishGrammar.Run
    if module in {"VE.Acts.LexicalBase", "VE.Acts.Lexical", "VE.Acts.LexicalProofs", "VE.Acts.Compat",
                  "VE.Acts.LexicalExamples"}:
        return 2  # act-phrases AP-1: the lexical act check, below the norms decoder that calls it
    if module.startswith("VE.Words."):
        return 3  # the answer's situation wording, from the English lexicon (question answering Q2.3)
    if module.startswith(("VE.English.", "VE.Grammar.", "VE.EnglishGrammar.", "VE.Senses.", "VE.Question.", "VE.Acts.")) or module in {
        "VE.Surface", "VE.SurfaceProofs", "VE.ParserContracts", "VE.LexicalProofs",
        "VE.Order.Surface", "VE.Core.Surface", "VE.Closure.Surface",
    }:
        return 3
    if module.startswith(("VE.Core.", "VE.Json", "VE.Kit.")) or module in {
        "VE.Limits", "VE.Paths", "VE.Syntax", "VE.Semantics", "VE.Typing", "VE.Finite", "VE.Consequence",
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
            return {"ve-kernel": 1, "ve-core": 1, "ve-profile": 2}.get(crate, 4)
        if p.suffix in {".py", ".json"} and p.name not in {"Cargo.lock"}:
            return 5  # benchmarks and generated measurement reports
        return 1 if p.name in {"Cargo.toml", "Cargo.lock"} else None
    if parts[0] in APP_AREAS:
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
