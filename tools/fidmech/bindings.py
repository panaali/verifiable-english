"""Load a use case's case-to-atom tables from its frozen `fidmech/bindings.json`, with their exact Python types.

Plan section 2a: a table that maps a question or a case to atoms, predicates or entities is data of one translation
version, not code; run.py reads it from here. Each table names its type in a small grammar (`str`, `bool`, `int`,
`list[T]`, `set[T]`, `tuple[T,...]`, `tuple[T1,T2]`, `dict[str,T]`) and the loader rebuilds exactly that type, so
run.py sees the same tuples, lists and sets as the literals it replaced. A value of the wrong shape is refused by
name. The sha256 of each file is pinned in tests/test_fidmech_bindings.py; `frozen_diff` prints the tables against
the run.py literals at the file's `frozen_from` commit.
"""
from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

SCHEMA = "fidmech-bindings/1"
REPO = Path(__file__).resolve().parents[2]


class BindingsError(ValueError):
    """A bindings file or table that is malformed: the message names the file, the table and the path."""


def parse_type(text):
    """The type tree of a type string: ("str",), ("list", T), ("set", T), ("tuple...", T), ("tuple", (T1, T2)),
    ("dict", T)."""
    tree, rest = _parse(text.replace(" ", ""))
    if rest:
        raise BindingsError(f"type {text!r}: unread text {rest!r}")
    return tree


def _parse(text):
    for scalar in ("str", "bool", "int"):
        if text.startswith(scalar) and not text[len(scalar):len(scalar) + 1].isalnum():
            return (scalar,), text[len(scalar):]
    for kind in ("list", "set", "tuple", "dict"):
        if text.startswith(kind + "["):
            rest = text[len(kind) + 1:]
            if kind == "dict":
                if not rest.startswith("str,"):
                    raise BindingsError(f"type {text!r}: a dict key is str")
                rest = rest[4:]
            args = []
            while True:
                if rest.startswith("..."):
                    args.append(...)
                    rest = rest[3:]
                else:
                    arg, rest = _parse(rest)
                    args.append(arg)
                if rest.startswith(","):
                    rest = rest[1:]
                    continue
                if not rest.startswith("]"):
                    raise BindingsError(f"type {text!r}: expected ']'")
                rest = rest[1:]
                break
            if kind == "tuple":
                if len(args) == 2 and args[1] is ...:
                    return ("tuple...", args[0]), rest
                if ... in args:
                    raise BindingsError(f"type {text!r}: '...' only as tuple[T,...]")
                return ("tuple", tuple(args)), rest
            if len(args) != 1 or args[0] is ...:
                raise BindingsError(f"type {text!r}: {kind} takes one type")
            return (kind, args[0]), rest
    raise BindingsError(f"type {text!r}: unknown")


def build(tree, value, where):
    """`value` (decoded JSON) as the Python type `tree`; any other shape is refused with its path."""
    kind = tree[0]
    if kind == "str" and type(value) is str or kind == "bool" and type(value) is bool \
            or kind == "int" and type(value) is int:
        return value
    if kind in ("list", "set", "tuple...") and type(value) is list:
        items = [build(tree[1], v, f"{where}[{i}]") for i, v in enumerate(value)]
        if kind == "set":
            if len(set(items)) != len(items):
                raise BindingsError(f"{where}: a set lists a member twice")
            return set(items)
        return items if kind == "list" else tuple(items)
    if kind == "tuple" and type(value) is list:
        if len(value) != len(tree[1]):
            raise BindingsError(f"{where}: expected {len(tree[1])} members, found {len(value)}")
        return tuple(build(t, v, f"{where}[{i}]") for i, (t, v) in enumerate(zip(tree[1], value)))
    if kind == "dict" and type(value) is dict:
        return {k: build(tree[1], v, f"{where}.{k}") for k, v in value.items()}
    raise BindingsError(f"{where}: expected {kind}, found {type(value).__name__}")


def unbuild(value):
    """A table value as JSON data: tuples and lists as lists, a set as its sorted members."""
    if isinstance(value, dict):
        return {k: unbuild(v) for k, v in value.items()}
    if isinstance(value, (set, frozenset)):
        return [unbuild(v) for v in sorted(value)]
    if isinstance(value, (list, tuple)):
        return [unbuild(v) for v in value]
    return value


def load_bindings(path, document=None):
    """{table name: value} of a bindings.json, each value rebuilt as its declared type."""
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise BindingsError(f"{path}: not readable JSON ({e})") from e
    if type(data) is not dict or data.get("schema") != SCHEMA:
        raise BindingsError(f"{path}: schema is not {SCHEMA}")
    if set(data) != {"schema", "document", "frozen_from", "tables"}:
        raise BindingsError(f"{path}: keys {sorted(data)} are not schema, document, frozen_from, tables")
    if document is not None and data["document"] != document:
        raise BindingsError(f"{path}: document {data['document']!r} is not {document!r}")
    if type(data["frozen_from"]) is not str or type(data["tables"]) is not dict or not data["tables"]:
        raise BindingsError(f"{path}: frozen_from is a commit and tables a non-empty object")
    out = {}
    for name, table in data["tables"].items():
        if type(table) is not dict or set(table) != {"type", "value"} or type(table["type"]) is not str:
            raise BindingsError(f"{path}: table {name} is not {{type, value}}")
        out[name] = build(parse_type(table["type"]), table["value"], f"{path.name}:{name}")
    return out


def dump_bindings(document, frozen_from, tables):
    """The canonical text of a bindings.json; `tables` is {name: (type string, value)}. Each value must rebuild to
    itself, so a type that loses information (a list declared as a tuple) is refused here, not at load."""
    body = {}
    for name, (type_, value) in tables.items():
        data = unbuild(value)
        if build(parse_type(type_), data, name) != value:
            raise BindingsError(f"table {name}: the type {type_} does not rebuild the value")
        body[name] = (type_, data)

    def one(value):
        return json.dumps(value, ensure_ascii=False)

    lines = ["{" + f'"schema": {one(SCHEMA)}, "document": {one(document)}, "frozen_from": {one(frozen_from)},',
             ' "tables": {']
    for i, (name, (type_, data)) in enumerate(body.items()):
        if isinstance(data, dict) and data:
            value = "{\n" + ",\n".join(f"   {one(k)}: {one(v)}" for k, v in data.items()) + "}"
        else:
            value = one(data)
        lines.append(f"  {one(name)}: " + "{" + f'"type": {one(type_)}, "value": {value}' + "}"
                     + ("," if i < len(body) - 1 else ""))
    text = "\n".join(lines) + "}}\n"
    if json.loads(text) != {"schema": SCHEMA, "document": document, "frozen_from": frozen_from,
                            "tables": {n: {"type": t, "value": d} for n, (t, d) in body.items()}}:
        raise BindingsError("dump_bindings: the text does not read back as the tables")
    return text


def module_tables(source, scope=None):
    """{name: value} of every module-level `name = expression` in source text that evaluates with no builtins and
    only `scope` plus the earlier such names in reach: the literals, comprehensions and sums of tables. Any other
    assignment (a call, a path) is left out."""
    scope, out = dict(scope or {}), {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                value = eval(compile(ast.Expression(node.value), "<run.py>", "eval"),  # noqa: S307
                             {"__builtins__": {}}, dict(scope))
            except Exception:  # noqa: BLE001 - not a table: it needs a name outside the tables
                continue
            scope[node.targets[0].id] = out[node.targets[0].id] = value
    return out


def bound_names(source):
    """The module-level names whose assignment reads the bindings (`_B`), directly or through an earlier such name,
    in source order."""
    bound = ["_B"]
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) \
                and node.targets[0].id != "_B" \
                and any(isinstance(n, ast.Name) and n.id in bound for n in ast.walk(node.value)):
            bound.append(node.targets[0].id)
    return bound[1:]


def frozen_diff(path, *, new_source=None, old_source=None):
    """Lines comparing every run.py name that reads the bindings with the same name at the file's frozen_from
    commit (plan 2a: the report prints this diff). A name with no literal at frozen_from (a table that was inline
    code) is printed as new."""
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    tables = load_bindings(path, data.get("document"))
    run_py = path.parent.parent / "run.py"
    rel = run_py.resolve().relative_to(REPO).as_posix()
    if new_source is None:
        new_source = run_py.read_text(encoding="utf-8")
    if old_source is None:
        old_source = subprocess.run(["git", "-C", str(REPO), "show", f"{data['frozen_from']}:{rel}"], check=True,
                                    capture_output=True, text=True).stdout
    new = module_tables(new_source, {"_B": tables})
    old = module_tables(old_source)
    lines = [f"{data['document']}: run.py names read from bindings.json against {rel} at {data['frozen_from']}"]
    for name in bound_names(new_source):
        if name not in new:
            lines.append(f"  {name}: DOES NOT EVALUATE from the bindings")
        elif name not in old:
            lines.append(f"  {name}: new name (no literal at frozen_from)")
        elif old[name] == new[name] and type(old[name]) is type(new[name]):
            lines.append(f"  {name}: same")
        else:
            lines.append(f"  {name}: DIFFERS ({old[name]!r} -> {new[name]!r})")
    unread = sorted(set(tables) - _subscripts(new_source))
    lines.extend(f"  table {name}: not read by run.py" for name in unread)
    return lines


def _subscripts(source):
    """The table names run.py reads as `_B["NAME"]`."""
    return {n.slice.value for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Subscript)
            and isinstance(n.value, ast.Name) and n.value.id == "_B" and isinstance(n.slice, ast.Constant)}
