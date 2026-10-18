"""Static dependency graph of the repository's Python files, Lean modules and tests.

This is the selector's fallback when the coverage map cannot answer: a test
depends on the Python files its imports reach (imports from the `ve` facade
resolve to the module that defines the name, as in tools/layer_policy.py), and
on the files, directories and programs whose names appear as string literals
in any of those files. Parsed summaries are cached per file by size and
modification time, so a selection rereads only edited files.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import os
from pathlib import Path
import pickle
import posixpath
import subprocess

from change_units import ROOT_SPELLINGS, Summary, summarize
from check_lean_imports import HeaderError, imports as lean_imports
from layer_policy import ROOT, lean_executables

# String literals naming these directories say nothing about which files a test uses.
GENERIC_DIRECTORIES = frozenset({"ve", "tests", "tools", "lean", "rust", "src", "build", "bin",
                                 "target", "VE", "docs", "__pycache__"})
# In the product's modules "." is the English full stop; the test side (tests,
# their helpers, tools) names the root "." it lists.
PRODUCT = ("ve/", "ve_experiments/")
CODE_VERSION = hashlib.sha256(b"".join(
    (Path(__file__).parent / name).read_bytes()
    for name in ("source_graph.py", "change_units.py"))).hexdigest()[:16]


def cache_path(root: Path) -> Path:
    base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    return base / "ve-testselect" / f"graph-{hashlib.sha256(str(root.resolve()).encode()).hexdigest()[:16]}.pickle"


def tracked(root: Path) -> list[str]:
    """Tracked and untracked-but-not-ignored files, relative to the root."""
    out = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                         cwd=root, capture_output=True, check=True).stdout.decode()
    return sorted({path for path in out.split("\0") if path and (root / path).is_file()})


def module_name(path: str) -> tuple[str, bool]:
    parts = Path(path).with_suffix("").parts
    if parts[-1] == "__init__":
        return ".".join(parts[:-1]), True
    return ".".join(parts), False


@dataclass
class Graph:
    root: Path
    files: list[str]
    summaries: dict[str, Summary | None]            # None: not valid Python for this parser
    edges: dict[str, set[str]] = field(default_factory=dict)          # file -> files it imports
    imported_names: dict[tuple[str, str], set[str]] = field(default_factory=dict)  # (importer, file) -> names, "*" or "<module>"
    reverse: dict[str, set[str]] = field(default_factory=dict)
    mentions: dict[str, set[str]] = field(default_factory=dict)       # file -> mentioned paths and tokens
    exports: dict[str, str] = field(default_factory=dict)             # ve facade name -> defining file
    lean_modules: dict[str, str] = field(default_factory=dict)        # Lean module -> file
    lean_imports: dict[str, list[str]] = field(default_factory=dict)
    lean_unreadable: list[str] = field(default_factory=list)
    # Earlier versions of changed files that still exist (see `overlay`).
    previous: dict[str, Summary] = field(default_factory=dict)

    def overlay(self, earlier: dict[str, str | None]) -> Graph:
        """This graph with the earlier version of each changed file kept too.

        `earlier` maps each changed path to its content before the change, or
        None where it did not exist (for non-Python files only presence
        matters). A removed file stays a node with its old imports and
        mentions, so its importers and the tests that named it still reach
        it; a file that still exists keeps the edges of its old version as
        well as its new ones, so an import or mention that the change dropped
        still counts.
        """
        present = set(self.files)
        summaries, previous = dict(self.summaries), {}
        lean_imports_by_module = dict(self.lean_imports)
        lean_modules = dict(self.lean_modules)
        unreadable = list(self.lean_unreadable)
        removed = {path for path, text in earlier.items() if text is not None and path not in present}
        for path, text in earlier.items():
            if text is None:
                continue
            if path.endswith(".py"):
                module, package = module_name(path)
                try:
                    old = summary_of(text, module, package)
                except SyntaxError:
                    old = None
                if path in removed:
                    summaries[path] = old
                elif old is not None:
                    previous[path] = old
            elif path in removed and path.startswith("lean/") and path.endswith(".lean"):
                module = ".".join(Path(path).with_suffix("").parts[1:])
                try:
                    lean_imports_by_module[module] = list(lean_imports(text))
                    lean_modules[module] = path
                except HeaderError:
                    unreadable.append(path)
        if not removed and not previous:
            return self
        graph = Graph(self.root, sorted(present | removed), summaries, lean_modules=lean_modules,
                      lean_imports=lean_imports_by_module, lean_unreadable=unreadable, previous=previous)
        graph.prepare_names()
        graph.build()
        return graph

    # -- Python ---------------------------------------------------------------
    def resolve(self, importer: str, name: str) -> str | None:
        """The file an absolute module name denotes for this importer."""
        if not name:
            return None
        here = posixpath.dirname(importer)
        for base in ("", here + "/" if here else "", "tests/", "tools/"):
            stem = base + name.replace(".", "/")
            for candidate in (stem + ".py", stem + "/__init__.py"):
                if candidate in self._file_set:
                    return candidate
        return None

    def versions(self, path: str) -> list[Summary]:
        """The parsed versions of a file: now, and before the change if it changed."""
        return [s for s in (self.summaries.get(path), self.previous.get(path)) if s is not None]

    def build(self) -> None:
        self._file_set = set(self.files)
        for init in self.versions("ve/__init__.py"):
            for edge in init.imports:
                target = self.resolve("ve/__init__.py", edge.module)
                if target and edge.names:
                    for name, alias in edge.names:
                        self.exports.setdefault(alias, target)  # the current version first
        for path in self.summaries:
            targets: dict[str, set[str]] = {}
            self.mentions[path] = set()
            for summary in self.versions(path):
                self._targets(path, summary, targets)
                self.mentions[path] |= self._mentions(path, summary)
            self.edges[path] = set(targets)
            for target, names in targets.items():
                self.imported_names[(path, target)] = names
                self.reverse.setdefault(target, set()).add(path)

    def _targets(self, path: str, summary: Summary, targets: dict[str, set[str]]) -> None:
        """Add to `targets` the files one version of `path` imports, with the names it takes."""
        def add(target: str | None, names) -> None:
            if target and target != path:
                targets.setdefault(target, set()).update(names)

        for edge in summary.imports:
            if edge.names is None:  # import a.b.c
                parts = edge.module.split(".")
                for i in range(1, len(parts)):
                    parent = self.resolve(path, ".".join(parts[:i]))
                    if parent and parent != "ve/__init__.py":
                        add(parent, {"<module>"})
                if edge.module == "ve":
                    for name, owner in self.exports.items():
                        if name in summary.identifiers:
                            add(owner, {name})
                else:
                    add(self.resolve(path, edge.module), {"<module>"})
                continue
            if edge.module == "ve":
                for name, alias in edge.names:
                    if name == "*":
                        for exported, owner in self.exports.items():
                            add(owner, {exported})
                    elif name in self.exports:
                        add(self.exports[name], {name})
                    else:
                        add(self.resolve(path, f"ve.{name}"), {"<module>"})
                continue
            base = self.resolve(path, edge.module)
            for name, alias in edge.names:
                submodule = self.resolve(path, f"{edge.module}.{name}") if name != "*" else None
                if submodule:
                    add(submodule, {"<module>"})
                    if base and base != "ve/__init__.py":
                        add(base, {"<module>"})
                else:
                    add(base, {name})

    def _mentions(self, path: str, summary: Summary) -> set[str]:
        found = set()
        constants = summary.constants
        product = path.startswith(PRODUCT)
        for constant in constants:
            text = constant.strip()
            text = "." if text in ROOT_SPELLINGS else text.removeprefix("./").rstrip("/")
            if not text or "\n" in text or (text == "." and product):
                continue
            if text in self._file_set:
                found.add(text)
            elif text in self._directories and text not in GENERIC_DIRECTORIES:
                found.add(f"dir:{text}")
            if "/" not in text:
                found.update(self._basenames.get(text, ()))
                if text not in GENERIC_DIRECTORIES:
                    # A product module finds its own data beside it (`Path(__file__).parent / "packs"`);
                    # a bare word such as "evidence" or "reports" there is a key or a name under a path
                    # its caller gives, and the test side names that path. So in a product module a
                    # bare name stands only for directories of that name inside the product.
                    found.update(f"dir:{d}" for d in self._directory_names.get(text, ())
                                 if not product or d.startswith(PRODUCT))
            if text in self._executables:
                found.add(f"lean-exe:{text}")
            if text in ("lake", "lean"):
                found.add("lean-tool")
            if text == "git":
                found.add("git-tool")
            if "rust/target" in text or text in ("VE_W5_RUST_BIN", "cargo"):
                found.add("rust")
        if "-m" in constants and "ve" in constants:
            found.add("ve/__main__.py")
        return found

    def prepare_names(self) -> None:
        self._file_set = set(self.files)
        self._executables = set(lean_executables(self.root))
        self._basenames: dict[str, set[str]] = {}
        # The root by the recorder's name for it: a test that lists "." names it.
        self._directories: set[str] = {"."}
        self._directory_names: dict[str, set[str]] = {}
        for path in self.files:
            name = posixpath.basename(path)
            if name != "__init__.py":
                self._basenames.setdefault(name, set()).add(path)
            parent = posixpath.dirname(path)
            while parent and parent not in self._directories:
                self._directories.add(parent)
                self._directory_names.setdefault(posixpath.basename(parent), set()).add(parent)
                parent = posixpath.dirname(parent)

    def closure(self, start: str) -> tuple[set[str], set[str]]:
        """Files a test reaches through imports and named scripts, and every mention.

        pytest imports every conftest.py from the root down to a test's directory
        for each test below it, so what those reach is the test's too. Their
        native mentions are not: the conftest builds the checkers once per
        session and starts none, so the test's own code decides whether it runs one.
        """
        seen, mentioned = self._reach(start)
        conftests = [posixpath.join(directory, "conftest.py") if directory else "conftest.py"
                     for directory in self._directories_down_to(start)]
        for conftest in conftests:
            if conftest != start and conftest in self.summaries:
                files, tokens = self._reach(conftest)
                seen |= files
                mentioned |= {token for token in tokens if token not in ("rust", "lean-tool")
                              and not token.startswith("lean-exe:")}
        return seen, mentioned

    @staticmethod
    def _directories_down_to(path: str) -> list[str]:
        """The root ("") and each directory above `path`, outermost first."""
        parts = path.split("/")[:-1]
        return ["/".join(parts[:end]) for end in range(len(parts) + 1)]

    def _reach(self, start: str) -> tuple[set[str], set[str]]:
        seen, mentioned, stack = {start}, set(), [start]
        while stack:
            path = stack.pop()
            for target in self.edges.get(path, ()):
                if target not in seen:
                    seen.add(target)
                    stack.append(target)
            for token in self.mentions.get(path, ()):
                mentioned.add(token)
                if token.endswith(".py") and token in self.summaries and token not in seen:
                    seen.add(token)  # a script the test runs
                    stack.append(token)
        return seen, mentioned

    def importers(self, path: str) -> set[str]:
        """Every file whose static imports reach `path` (transitively), and `path`."""
        seen, stack = {path}, [path]
        while stack:
            for importer in self.reverse.get(stack.pop(), ()):
                if importer not in seen:
                    seen.add(importer)
                    stack.append(importer)
        return seen

    # -- Lean -------------------------------------------------------------------
    def lean_closure(self, module: str) -> set[str]:
        seen, stack = {module}, [module]
        while stack:
            for imported in self.lean_imports.get(stack.pop(), ()):
                if imported not in seen:
                    seen.add(imported)
                    stack.append(imported)
        return seen

    def executables_using(self, module: str) -> set[str]:
        """Lean executables whose root imports `module`; all of them if a header is unreadable."""
        executables = lean_executables(self.root)
        if self.lean_unreadable:
            return set(executables)
        return {name for name, root in executables.items() if module in self.lean_closure(root)}


_blob_summaries: dict | None = None
_blob_dirty = False
INVALID = "invalid"


def _blob_cache_path() -> Path:
    base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    return base / "ve-testselect" / "summaries.pickle"


def summary_of(text: str, module: str, package: bool) -> Summary:
    """`summarize`, cached by content hash; raises SyntaxError for invalid source."""
    global _blob_summaries, _blob_dirty
    if _blob_summaries is None:
        try:
            with _blob_cache_path().open("rb") as handle:
                cached = pickle.load(handle)
            _blob_summaries = cached["entries"] if cached.get("version") == CODE_VERSION else {}
        except (OSError, pickle.PickleError, EOFError, AttributeError, ImportError, KeyError):
            _blob_summaries = {}
    key = (hashlib.blake2b(text.encode("utf-8", "surrogateescape"), digest_size=16).hexdigest(),
           module, package)
    found = _blob_summaries.get(key)
    if found is None:
        try:
            found = summarize(text, module, package=package)
        except (SyntaxError, ValueError, RecursionError):
            found = INVALID
        _blob_summaries[key] = found
        _blob_dirty = True
    if found == INVALID:
        raise SyntaxError(f"{module}: not valid Python for this parser")
    return found


def save_summaries() -> None:
    global _blob_dirty
    if not _blob_dirty or _blob_summaries is None:
        return
    entries = dict(list(_blob_summaries.items())[-4000:])  # newest entries; dicts keep insertion order
    path = _blob_cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    with temporary.open("wb") as handle:
        pickle.dump({"version": CODE_VERSION, "entries": entries}, handle)
    temporary.replace(path)
    _blob_dirty = False


def load(root: Path = ROOT) -> Graph:
    files = tracked(root)
    path = cache_path(root)
    try:
        with path.open("rb") as handle:
            cached = pickle.load(handle)
        if cached.get("version") != CODE_VERSION:
            cached = {}
    except (OSError, pickle.PickleError, EOFError, AttributeError, ImportError):
        cached = {}
    entries = cached.get("entries", {})
    fresh, summaries, lean_imports_by_file, unreadable = {}, {}, {}, []
    dirty = False
    for file in files:
        if not file.endswith((".py", ".lean")) or (file.endswith(".lean") and not file.startswith("lean/")):
            continue
        stat = (root / file).stat()
        key = (stat.st_size, stat.st_mtime_ns)
        entry = entries.get(file)
        if entry is None or entry[0] != key:
            text = (root / file).read_text(encoding="utf-8", errors="replace")
            if file.endswith(".py"):
                module, package = module_name(file)
                try:
                    value = summary_of(text, module, package)
                except SyntaxError:
                    value = None
            else:
                try:
                    value = tuple(lean_imports(text))
                except HeaderError:
                    value = None
            entry = (key, value)
            dirty = True
        fresh[file] = entry
        if file.endswith(".py"):
            summaries[file] = entry[1]
        elif entry[1] is None:
            unreadable.append(file)
        else:
            lean_imports_by_file[file] = entry[1]
    fingerprint = hashlib.sha256(repr((files, sorted((f, e[0]) for f, e in fresh.items()))).encode()).hexdigest()
    if not dirty and cached.get("fingerprint") == fingerprint:
        return cached["graph"]
    graph = Graph(root, files, summaries, lean_unreadable=unreadable)
    for file, imported in lean_imports_by_file.items():
        module = ".".join(Path(file).with_suffix("").parts[1:])
        graph.lean_modules[module] = file
        graph.lean_imports[module] = list(imported)
    graph.prepare_names()
    graph.build()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    with temporary.open("wb") as handle:
        pickle.dump({"version": CODE_VERSION, "entries": fresh, "fingerprint": fingerprint,
                     "graph": graph}, handle)
    temporary.replace(path)
    return graph
