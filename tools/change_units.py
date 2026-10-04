"""Split a Python source into the units a change can touch, using `ast`.

A *unit* is one `def` (function or method), named by the `__qualname__`
CPython gives its code object, so it can be looked up in the coverage map.
Everything else at module or class level is a *statement*: what it binds,
what names it reads, and whether it has an effect beyond binding names (a call
at top level, such as a registration). Docstrings and comments are not part of
either, so editing only those changes nothing.
"""
from __future__ import annotations

import ast
from collections import Counter
import hashlib
from dataclasses import dataclass, field

# Decorators that only wrap or describe the function they decorate. Any other
# decorator may register the function somewhere, which is an import-time effect.
BENIGN_DECORATORS = frozenset({
    "property", "staticmethod", "classmethod", "cache", "lru_cache", "cached_property",
    "wraps", "abstractmethod", "overload", "contextmanager", "asynccontextmanager",
    "setter", "getter", "deleter", "dataclass", "total_ordering", "unique", "final",
    "override", "singledispatch", "singledispatchmethod", "fixture", "parametrize",
    "mark", "skip", "skipif", "xfail", "given", "settings", "example", "seed", "composite",
    "no_type_check", "runtime_checkable",
})


@dataclass(frozen=True)
class Unit:
    qualname: str
    top: str                 # the module-level name the unit is reached through
    body: str                # digest of the def without docstrings or decorators
    decorators: str          # digest of the decorator list
    benign: bool             # every decorator is in BENIGN_DECORATORS
    references: frozenset[str]


@dataclass(frozen=True)
class Statement:
    body: str                # digest of the import-time residue
    binds: frozenset[str]
    references: frozenset[str]
    effect: bool             # does more than bind names (a top-level call, del, ...)
    is_import: bool = False  # binds each imported name to its own source


@dataclass(frozen=True)
class ImportEdge:
    module: str              # absolute dotted module, or "" when unresolvable
    names: tuple[tuple[str, str], ...] | None   # (name, local alias); None for `import m`
    local: str | None        # the name `import m as a` binds


@dataclass
class Summary:
    units: dict[str, Unit] = field(default_factory=dict)
    statements: list[Statement] = field(default_factory=list)
    imports: list[ImportEdge] = field(default_factory=list)
    constants: frozenset[str] = frozenset()      # string literals, for path and program mentions
    identifiers: frozenset[str] = frozenset()    # every Name id, attribute and import alias
    attributes: frozenset[str] = frozenset()     # names read as `something.NAME`


def _digest(node: ast.AST) -> str:
    """A short fingerprint of a node's structure (positions and comments excluded)."""
    return hashlib.blake2b(ast.dump(node).encode(), digest_size=10).hexdigest()


def _strip_docstring(body: list[ast.stmt]) -> list[ast.stmt]:
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
            and isinstance(body[0].value.value, str):
        return body[1:]
    return body


def _decorator_name(node: ast.expr) -> str:
    while isinstance(node, ast.Call):
        node = node.func
    if isinstance(node, ast.Attribute):
        return node.attr
    return node.id if isinstance(node, ast.Name) else ""


def _references(node: ast.AST) -> frozenset[str]:
    found = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Name):
            found.add(child.id)
        elif isinstance(child, ast.Attribute):
            found.add(child.attr)
        elif isinstance(child, ast.alias):
            found.add(child.asname or child.name.split(".")[0])
            found.add(child.name.split(".")[-1])
    return frozenset(found)


def _binds(node: ast.AST, in_class: bool = False) -> set[str]:
    """Names a statement binds at its own level: not inside defs, and not method names."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return set() if in_class else {node.name}
    if isinstance(node, ast.ClassDef):
        names = {node.name}
        for child in node.body:
            names |= _binds(child, True)
        return names
    if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
        return {node.id}
    if isinstance(node, (ast.Attribute, ast.Subscript)) and isinstance(node.ctx, (ast.Store, ast.Del)):
        base = node.value
        while isinstance(base, (ast.Attribute, ast.Subscript)):
            base = base.value
        return {base.id} if isinstance(base, ast.Name) else set()  # `TABLE["k"] = v` changes TABLE
    if isinstance(node, ast.alias):
        return {node.asname or node.name.split(".")[0]}
    if isinstance(node, (ast.Global, ast.Nonlocal)):
        return set(node.names)
    names = set()
    for child in ast.iter_child_nodes(node):
        names |= _binds(child, in_class)
    return names


def _effect(node: ast.stmt) -> bool:
    """A statement that may act beyond binding names when the module runs."""
    if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign, ast.AnnAssign, ast.AugAssign,
                         ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Pass)):
        return False
    if isinstance(node, (ast.If, ast.Try, ast.With)):
        inner = [*node.body, *getattr(node, "orelse", []), *getattr(node, "finalbody", []),
                 *[stmt for handler in getattr(node, "handlers", []) for stmt in handler.body]]
        return any(_effect(stmt) for stmt in inner)
    return True  # expression statements, del, for/while loops, raise, assert, ...


def _benign(node: ast.AST) -> bool:
    return all(_decorator_name(d) in BENIGN_DECORATORS for d in node.decorator_list)


def _residue(node) -> str:
    """Dump of what runs at import: like ast.dump, with every def body left out.

    A def keeps its name and decorators; defaults and annotations belong to
    its unit. In a class, a method with only benign decorators is left out
    altogether (it is a unit of its own), as are docstrings.
    """
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return f"def {node.name}{_residue(node.decorator_list)}"
    if isinstance(node, list):
        return "[" + ",".join(_residue(item) for item in node) + "]"
    if not isinstance(node, ast.AST):
        return repr(node)
    fields = []
    for name, value in ast.iter_fields(node):
        if isinstance(node, ast.ClassDef) and name == "body":
            value = [stmt for stmt in _strip_docstring(value)
                     if not (isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)) and _benign(stmt))]
        fields.append(f"{name}={_residue(value)}")
    return f"{type(node).__name__}({','.join(fields)})"


def summarize(source: str, module: str, *, package: bool = False) -> Summary:
    """Units, statements and imports of a module. Raises SyntaxError for invalid source."""
    tree = ast.parse(source)
    summary = Summary()
    tree.body = _strip_docstring(tree.body)

    def visit(body, prefix: str, top: str | None, in_function: bool):
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qualname = f"{prefix}{node.name}"
                stripped = ast.FunctionDef(name=node.name, args=node.args,
                                           body=_strip_docstring(node.body) or [ast.Pass()],
                                           decorator_list=[], returns=node.returns, type_params=[])
                decorators = _digest(ast.List(elts=node.decorator_list, ctx=ast.Load()))
                unit = Unit(qualname, top or node.name, _digest(stripped), decorators,
                            _benign(node), _references(node))
                if qualname in summary.units:  # redefinition (property setters, overloads)
                    old = summary.units[qualname]
                    unit = Unit(qualname, unit.top, old.body + unit.body, old.decorators + unit.decorators,
                                old.benign and unit.benign, old.references | unit.references)
                summary.units[qualname] = unit
                visit(node.body, f"{qualname}.<locals>.", top or node.name, True)
            elif isinstance(node, ast.ClassDef):
                visit(node.body, f"{prefix}{node.name}.", top or node.name, in_function)
            elif hasattr(node, "body") and isinstance(node, (ast.If, ast.Try, ast.With, ast.For,
                                                             ast.While, ast.AsyncWith, ast.AsyncFor)):
                # A def under `if`/`try` at any level keeps the enclosing prefix.
                for block in ("body", "orelse", "finalbody"):
                    visit(getattr(node, block, []), prefix, top, in_function)
                for handler in getattr(node, "handlers", []):
                    visit(handler.body, prefix, top, in_function)

    visit(tree.body, "", None, False)
    for node in tree.body:
        body = hashlib.blake2b(_residue(node).encode(), digest_size=10).hexdigest()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            references = _references(ast.List(elts=node.decorator_list, ctx=ast.Load()))
        elif isinstance(node, ast.ClassDef):
            references = _references(ast.Module(body=[
                *node.bases, *node.keywords, *node.decorator_list,
                *[stmt for stmt in node.body if not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef))]],
                type_ignores=[]))
        else:
            references = _references(node)
        summary.statements.append(Statement(body, frozenset(_binds(node)), references, _effect(node),
                                            isinstance(node, (ast.Import, ast.ImportFrom))))
    parts = module.split(".") if package else module.split(".")[:-1]
    constants = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                summary.imports.append(ImportEdge(alias.name, None,
                                                  alias.asname or alias.name.split(".")[0]))
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base_parts = parts[:len(parts) - node.level + 1] if node.level <= len(parts) else None
                absolute = "" if base_parts is None else ".".join(
                    [*base_parts, *([node.module] if node.module else [])])
            else:
                absolute = node.module or ""
            summary.imports.append(ImportEdge(absolute, tuple((a.name, a.asname or a.name)
                                                              for a in node.names), None))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and len(node.value) < 300:
            constants.add(node.value)
    summary.constants = frozenset(constants)
    summary.identifiers = _references(tree)
    summary.attributes = frozenset(node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute))
    return summary


@dataclass
class Delta:
    """What differs between two versions of one module."""
    changed: set[str] = field(default_factory=set)      # units in both, body changed
    added: set[str] = field(default_factory=set)
    removed: set[str] = field(default_factory=set)
    decorated: set[str] = field(default_factory=set)    # units whose non-benign decorators changed
    binds: set[str] = field(default_factory=set)        # names bound by changed statements
    effect: bool = False                                # a changed statement acts at import
    imports_changed: bool = False
    # Names read by each changed or added unit (by qualname) and by changed statements ("").
    references: dict[str, frozenset[str]] = field(default_factory=dict)

    @property
    def empty(self) -> bool:
        return not (self.changed or self.added or self.removed or self.decorated or self.binds
                    or self.effect or self.imports_changed)


def delta(old: Summary | None, new: Summary | None) -> Delta:
    old = old or Summary()
    new = new or Summary()
    result = Delta()
    for qualname in old.units.keys() | new.units.keys():
        before, after = old.units.get(qualname), new.units.get(qualname)
        if before is None:
            result.added.add(qualname)
            if not after.benign:
                result.decorated.add(qualname)
        elif after is None:
            result.removed.add(qualname)
        else:
            if before.body != after.body:
                result.changed.add(qualname)
            if before.decorators != after.decorators:
                result.changed.add(qualname)
                if not (before.benign and after.benign):
                    result.decorated.add(qualname)
    before = Counter(s.body for s in old.statements)
    after = Counter(s.body for s in new.statements)
    differing = (before - after) + (after - before)
    statement_references = set()
    for statement in [*old.statements, *new.statements]:
        if statement.body in differing:
            result.binds |= statement.binds
            result.effect |= statement.effect
            statement_references |= statement.references
    result.references = {q: new.units[q].references for q in result.changed | result.added}
    result.references[""] = frozenset(statement_references)
    if not differing and [s.body for s in old.statements] != [s.body for s in new.statements]:
        result.effect = True  # only the order of top-level statements changed
    result.imports_changed = sorted(map(repr, old.imports)) != sorted(map(repr, new.imports))
    return result
