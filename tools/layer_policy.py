"""Single source of truth for the five repository layers.

The Stage 0 symbol/import inventory on mig/stage0 informed these module-level
assignments. A module with mixed responsibilities is assigned to its outermost
responsibility until it is split; exact legacy edges are tracked separately.

A module may instead declare its layer on its own first line, `-- ve-layer: <1-5> (<reason>)` in a Lean file and
`# ve-layer: <1-5> (<reason>)` in a Python module or package `__init__.py` (`layer_declaration`). This module
reads the declaration; the name rules below are the fallback, and a role rule (`lean_fixed`, the app areas)
outranks both.
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
    # the senses and speech-source routes (they read the English parser and build environments); `senses.display`
    # renders and re-reads candidates through the senses route.
    4: ("__main__ adapters admission argument ask attacks authoring bundle check "
        "document equivalence norm_admission norm_defaults norm_defaults_contract norm_defaults_english norm_defaults_route norm_strict "
        "defaults_english filling_search openterms propose readings search stream_audit vacuity assist discourse words calc scope judgment_lines cardinality acts "
        "reports reports_route risk rights_route soft_route speech_document readings_route readings_s1 "
        "readings_sup readings_verdicts readings_components readings_s2_wording senses_document defaults "
        "backends.senses backends.speech_source senses.display").split(),
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
# An in-module layer declaration: the file's first line is this comment marker, a layer number and a reason in
# parentheses (docs/ARCHITECTURE-LAYERS.md). Lean's `--` line sits in the header's plain layout
# (tools/check_lean_imports.py, PLAIN_LAYOUT allows full-line `--` comments); Python's `#` line sits before the
# module docstring.
DECLARATION_KEY = "ve-layer"
LEAN_COMMENT = "--"
PYTHON_COMMENT = "#"
# A line is read as an attempted declaration when, past blanks, it starts with `ve-layer`, or with a comment or doc
# marker and then one of these, in any case; code such as `VE_LAYER = 4` is not one.
DECLARATION_LOOKALIKE = ("ve-layer", "ve_layer")
DECLARATION_MARKS = "#-/!*"
# The Python packages whose modules may declare their layer (an app area's modules are layer 5 by rule).
PYTHON_PACKAGES = ("ve",)


def declaration_form(comment: str) -> str:
    """How to write a declaration, for the messages of the layer checks."""
    return f"declare it on the file's first line: `{comment} {DECLARATION_KEY}: <1-5> (<reason>)`"


def layer_declaration(source: str | None, path: str, comment: str) -> tuple[int, str] | None:
    """The layer a file declares on its first line, `<comment> ve-layer: <n> (<reason>)`, as (layer, reason);
    None when the file is absent (`source` None) or declares none. Fails closed: a first line that looks like a
    declaration but is not exactly this form, an unknown layer, an empty reason, and a look-alike line anywhere
    else in the file raise ValueError naming `path` and the line."""
    if source is None:
        return None
    lines = source.split("\n")
    form = declaration_form(comment)

    def lookalike(line: str) -> bool:
        text = line.lstrip(" \t\ufeff")
        rest = text.lstrip(DECLARATION_MARKS)
        word = rest.lstrip(" \t").lower()
        return word.startswith(DECLARATION_LOOKALIKE if rest != text else DECLARATION_LOOKALIKE[:1])

    for number, line in enumerate(lines[1:], 2):
        if lookalike(line):
            raise ValueError(f"{path}:{number}: a layer declaration must be the file's first line; {form}")
    first = lines[0]
    if not lookalike(first):
        return None
    mark = f"{comment} {DECLARATION_KEY}: "
    if not first.startswith(mark) or not first.isprintable():
        raise ValueError(f"{path}:1: malformed layer declaration {first!r}; {form}")
    number, _, rest = first[len(mark):].partition(" ")
    if not (number.isascii() and number.isdigit()):
        raise ValueError(f"{path}:1: malformed layer declaration {first!r}: {number!r} is not a layer number; {form}")
    if number not in {str(layer) for layer in NAMES}:
        raise ValueError(f"{path}:1: unknown layer {number} in {first!r}: the layers are "
                         + ", ".join(f"{layer} {name}" for layer, name in NAMES.items()))
    if not rest.strip() or (rest.startswith("(") and rest.endswith(")") and not rest[1:-1].strip()):
        raise ValueError(f"{path}:1: layer declaration {first!r} gives no reason; {form}")
    depths = [rest[:end].count("(") - rest[:end].count(")") for end in range(1, len(rest) + 1)]
    if not (rest.startswith("(") and rest.endswith(")")) or min(depths[:-1], default=1) < 1 or depths[-1] != 0:
        raise ValueError(f"{path}:1: malformed layer declaration {first!r}: the reason goes in one pair of "
                         f"parentheses that ends the line; {form}")
    return int(number), rest[1:-1]


def read_file(root: Path, path: str) -> str | None:
    """A checkout file's text, or None when there is none; a file that is not UTF-8 raises ValueError naming it."""
    file = root / path
    if not file.is_file():
        return None
    try:
        return file.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"{path}: not UTF-8 ({error.reason})") from None


def lean_path(module: str) -> str:
    """The checkout path of a Lean module's source."""
    return "lean/" + module.replace(".", "/") + ".lean"


def lean_declared(module: str, root: Path = ROOT, read=None) -> tuple[int, str] | None:
    """A Lean module's own declaration (`layer_declaration`), read through `read(path)` (default: the file under
    `root`). A declaration on a module whose role fixes its layer (`lean_fixed`), or that a set of `lean_name_layer`
    names (one owner), raises ValueError."""
    path = lean_path(module)
    found = layer_declaration((read or (lambda p: read_file(root, p)))(path), path, LEAN_COMMENT)
    fixed = lean_fixed(module)
    if found is not None and fixed is not None:
        raise ValueError(f"{path}:1: {module}'s role fixes its layer at {fixed[0]} ({fixed[1]}); "
                         "remove the layer declaration")
    if found is not None and module in lean_named():
        raise ValueError(f"{path}:1: {module} is also named in tools/layer_policy.py's lean_name_layer at layer "
                         f"{lean_name_layer(module)}; keep one of the two")
    return found


@cache
def lean_named() -> frozenset[str]:
    """The Lean modules `lean_name_layer` names one by one (in a set, or compared with `==`), read from this file's
    own source: a declaration on one of them would be a second owner of its layer."""
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "lean_name_layer")
    named = set()
    for node in ast.walk(function):
        if isinstance(node, ast.Compare) and isinstance(node.left, ast.Name) and node.left.id == "module":
            for op, right in zip(node.ops, node.comparators):
                if isinstance(op, ast.In) and isinstance(right, ast.Set):
                    named.update(item.value for item in right.elts if isinstance(item, ast.Constant))
                elif isinstance(op, ast.Eq) and isinstance(right, ast.Constant):
                    named.add(right.value)
    return frozenset(named)


def python_row_declared(row: str, path: str, read) -> tuple[int, str] | None:
    """The declaration of Python row `row` (a module, or a package through its `__init__.py`) at `path`, read
    through `read`. Refused (ValueError): one in a root package's `__init__.py`, in an app area (layer 5 by rule),
    or on a row the `PYTHON` table already lists (one owner)."""
    found = layer_declaration(read(path), path, PYTHON_COMMENT)
    if found is None:
        return None
    if row.split(".")[0] in APP_AREAS:
        raise ValueError(f"{path}:1: {row} is in an app area, layer 5 by rule; remove the layer declaration")
    if "." not in row:
        raise ValueError(f"{path}:1: the root package {row} declares no layer (its facade is in none); remove the "
                         "layer declaration")
    if row in PYTHON_MODULES:
        raise ValueError(f"{path}:1: {row} is also listed in tools/layer_policy.py's PYTHON table at layer "
                         f"{PYTHON_MODULES[row]}; keep one of the two")
    return found


def python_declared_rows(module: str, root: Path = ROOT, read=None) -> dict[str, int]:
    """The declared rows that place `module`: its own file's declaration and its packages' (`__init__.py`)."""
    read = read or (lambda p: read_file(root, p))
    parts = module.split(".")
    rows = {}
    for size in range(1, len(parts) + 1):
        row, base = ".".join(parts[:size]), "/".join(parts[:size])
        for path in (f"{base}.py", f"{base}/__init__.py") if size == len(parts) else (f"{base}/__init__.py",):
            found = python_row_declared(row, path, read)
            if found is not None:
                rows[row] = found[0]
    return rows


def lean_declarations(root: Path = ROOT) -> tuple[dict[str, tuple[int, str]], list[str]]:
    """Every Lean module under `root/lean` that declares its layer, as {module: (layer, reason)}, and one problem
    message per file whose declaration is refused."""
    declared, problems = {}, []
    for file in sorted((root / "lean").rglob("*.lean")):
        if ".lake" in file.parts:
            continue
        module = ".".join(file.relative_to(root / "lean").with_suffix("").parts)
        try:
            found = lean_declared(module, root)
        except ValueError as error:
            problems.append(str(error))
            continue
        if found is not None:
            declared[module] = found
    return declared, problems


def python_declarations(root: Path = ROOT) -> tuple[dict[str, tuple[int, str, str]], list[str]]:
    """Every Python row under `root` that declares its layer (a module, or a package through its `__init__.py`),
    as {row: (layer, reason, path)}, and one problem message per file whose declaration is refused. Every Python file of
    the declaring packages and the app areas is read, so a declaration where none may stand is refused too."""
    declared, problems = {}, []
    files = sorted(file for top in (*PYTHON_PACKAGES, *sorted(APP_AREAS)) if (root / top).is_dir()
                   for file in (root / top).rglob("*.py") if "__pycache__" not in file.parts)
    for file in files:
        path = file.relative_to(root).as_posix()
        row = ".".join(file.relative_to(root).with_suffix("").parts).removesuffix(".__init__")
        try:
            found = python_row_declared(row, path, lambda p: read_file(root, p))
        except ValueError as error:
            problems.append(str(error))
            continue
        if found is not None:
            declared[row] = (*found, path)
    return declared, problems


def python_rows(root: Path = ROOT) -> dict[str, int]:
    """Every Python row and its layer: the `PYTHON` table's and the declared ones. A refused declaration raises
    ValueError (the layer check reports it through `python_declarations`)."""
    declared, problems = python_declarations(root)
    if problems:
        raise ValueError(problems[0])
    return {**PYTHON_MODULES, **{row: layer for row, (layer, _, _) in declared.items()}}


def lazy_exports(tree: ast.Module) -> dict[str, str]:
    """A package `__init__`'s lazy table, `_EXPORTS = {"module": ("name", ...)}`, which the `ve` package's
    `__getattr__` resolves (PEP 562), as {name: module}. The one reader of that table: the layer check, the
    pre-commit hook, test selection's change units and the semantic inventory reach it through here."""
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

    The pre-commit hook resolves each staged file with this, one file at a time and without the rest of the tree;
    the full Python layer check leaves the whole tree to import-linter.
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


def python_layer(module: str, root: Path = ROOT, read=None) -> int | None:
    """A Python module's layer: 5 in an app area, else its longest row; a row is a `PYTHON` table entry or a module
    or package that declares its layer (`python_declared_rows`, files read through `read(path)`, default: under
    `root`). None when nothing places it; a refused declaration raises ValueError naming its file."""
    declared = python_declared_rows(module, root, read)
    if module.split(".")[0] in APP_AREAS:
        return 5
    matches = [(len(prefix), layer) for prefix, layer in {**PYTHON_MODULES, **declared}.items()
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


def lean_fixed(module: str) -> tuple[int, str] | None:
    """The layer a Lean module's role fixes, with the role; no in-module declaration may name another or the same."""
    if module in {"VE", "VE.Audit", "ResponseShapeAudit", "Iceberg", "VE.Checks", "VE.Route.Checks", "VE.LimitTies"}:
        # VE.LimitTies checks frozen and hashed copies of VE.Limits
        return 5, "an aggregation or audit target"
    if lean_entry(module) or module.endswith(".Run") or module == "VE.Route.MeteredRun" or module.startswith("VE.Service."):
        return 4, "an entry point, a runner or the service"
    if module == "ResponseShape" or module.startswith("ResponseShape."):
        return 4, "a response shape: ve_response_decode and the client's schema source"
    return None


def lean_layer(module: str, root: Path = ROOT, read=None) -> int | None:
    """A Lean module's layer: its role's (`lean_fixed`), else its own declaration (`lean_declared`, read through
    `read(path)`, default: the file under `root`), else its name rules; None when nothing places it. A refused
    declaration raises ValueError naming its file."""
    declared = lean_declared(module, root, read)
    return declared[0] if declared is not None else lean_name_layer(module)


def lean_name_layer(module: str) -> int | None:
    """A Lean module's layer by its role and its name rules alone, without reading its source."""
    if (fixed := lean_fixed(module)) is not None:
        return fixed[0]
    if module in {"VE.EnglishGrammar.ProfileExamples", "VE.EnglishGrammar.E2Examples",
                  "VE.Question.Examples", "VE.Question.Fixtures", "VE.Commands.Examples", "VE.Alternatives.FillExamples",
                  "VE.Calc.RunExamples", "VE.Defaults.RouteExamples", "VE.Defaults.ZoneWireExamples", "VE.Readings.ActsExamples",
                  "VE.Cardinality.RunExamples", "VE.Scope.RunExamples", "VE.Senses.RunExamples",
                  "VE.Events.RouteExamples", "VE.Commands.RunExamples", "VE.Commands.RunSplit",
                  "VE.EnglishGrammar.JudgmentRunExamples", "VE.Senses.TextsExamples", "VE.Acts.RunExamples",
                  "VE.Rights.OpenActExamples"}:
        return 4  # runner-boundary acceptance fixtures import EnglishGrammar.Run, Question.Run, Alternatives.Run, Calc.Run,
        # NormDefaults.Run, Readings.Run, Cardinality.Run, Scope.Run, Senses.Run, Commands.Run, Acts.Run or Rights.Run
    if module in {"VE.Discourse.Compose", "VE.Discourse.ComposeExamples"}:
        return 4  # the composed admission runs the chain routes and states theorems on Service.Document.profilesOf
        # (discourse 14.4 to 14.6, cmp-s4); its fixtures read Discourse.Run
    if module in {"VE.Norms.FlaggedSpec"}:
        return 4  # states theorems on Norms.Run.runCase (docs/CONSOLIDATION-PLAN.md step 1a)
    if module in {"VE.Acts.DecodeTwins"}:
        return 4  # states the twins of Norms.Run's and NormDefaults.Run's theorems (act-phrases 6.4)
    if module in {"VE.Route.RunSound", "VE.Norms.RunSound", "VE.Cardinality.RunTheorems"}:
        return 4  # states theorems on Route.Run.runCase and Norms.Run.runCase (step 2a), and on Cardinality.Run's runner
    if module in {"VE.Calc.Ties"}:
        return 4  # states theorems on Calc.Run's evidence and rows (the R16 ties of me-5e)
    if module in {"VE.Compose.Contract", "VE.Compose.ContractExamples"}:
        return 4  # states theorems on Service.Document.checkDocSets (profile-composition 1.5, PC-3)
    if module == "VE.Judgments.ChainExamples":
        return 4  # checks Service.Document.checkDocSets on PC-1's fixtures (profile-composition 5.1)
    if module in {"VE.Question.Spans"}:
        return 4  # states theorems on EnglishGrammar.Run.codepointsBefore (question answering Q1.1)
    if module in {"VE.Commands.Read", "VE.Commands.Steps", "VE.Commands.StepsExamples"}:
        return 4  # reads a condition through EnglishGrammar.Run.translation (commands-imperatives CI-1); CI-3's steps over it
    if module.startswith("VE.Ask."):
        return 4  # question answering Q2: binds a request to Service.Document's split and reads EnglishGrammar.Run
    if module in {"VE.Acts.LexicalBase", "VE.Acts.Lexical", "VE.Acts.LexicalProofs", "VE.Acts.Compat",
                  "VE.Acts.LexicalExamples"}:
        return 2  # act-phrases AP-1: the lexical act check, below the norms decoder that calls it
    if module in {"VE.Acts.Wire", "VE.Acts.Readings", "VE.Acts.Meaning", "VE.Acts.Grammar", "VE.Acts.Read",
                  "VE.Acts.Syntax", "VE.Acts.Table", "VE.Acts.Linearize", "VE.Acts.Tree"} or module in {
        "VE.Grammar.Basic", "VE.Grammar.Derives", "VE.Grammar.Reading", "VE.Grammar.Table",
        "VE.Grammar.TableInvariant", "VE.Grammar.TableProofs",
    }:
        return 2  # act-phrases AP-3: the act check and the grammar it reads, below the norms decoder that calls it
    if module in {"VE.Weighing.Tree", "VE.Weighing.Conditions", "VE.Weighing.Examples"}:
        return 3  # weighing WG-2: a weighing document carries AP's split map (`VE.Acts.Elaborate`, weighing.md 1.1)
    if module.startswith("VE.Words."):
        return 3  # the answer's situation wording, from the English lexicon (question answering Q2.3)
    if module.startswith("VE.Attitudes."):
        return 3  # AttDoc carries the English lexicon (attitudes.md 2.2, SR-3; reviews/dri-decisions-20261104-at-1a-layer.md)
    if module.startswith(("VE.English.", "VE.Grammar.", "VE.EnglishGrammar.", "VE.Senses.", "VE.Question.", "VE.Commands.", "VE.Acts.")) or module in {
        "VE.Surface", "VE.SurfaceProofs", "VE.ParserContracts", "VE.LexicalProofs",
        "VE.Order.Surface", "VE.Core.Surface", "VE.Closure.Surface",
    }:
        return 3
    if module.startswith(("VE.Core.", "VE.Json", "VE.Kit.")) or module in {
        "VE.Limits", "VE.Paths", "VE.Syntax", "VE.Semantics", "VE.Typing", "VE.Finite", "VE.Consequence",
        "VE.Bridge", "VE.RoundTrip", "VE.CertificateWire", "VE.ClaimGraph",
        "VE.GraphChecks", "VE.ModelProofs", "VE.EnvironmentProofs",
        "VE.Tableau", "VE.TableauClosure", "VE.TableauChecker",
        "VE.TableauChecks", "VE.Closure.Tableau",
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
        try:
            return python_layer(".".join(p.with_suffix("").parts))
        except ValueError:
            return None  # a refused layer declaration: the layer check reports it
    if parts[0] == "lean":
        if p.suffix == ".lean":
            try:
                return lean_layer(".".join(p.with_suffix("").parts[1:]))
            except ValueError:
                return None  # a refused layer declaration: the layer check reports it
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
