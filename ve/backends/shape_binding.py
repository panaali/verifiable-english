"""The generic binding checker: what the Lean shapes bind in an answer, leaf by leaf (ADR 0001).

The response shapes are written once in Lean (`lean/ResponseShape/Schemas/`) and rendered to
`lean_service_schema/*.json`; `service_schema` checks an answer against them. This module reads the same
files and says, for every string and integer leaf of a mode's row, which of ADR 0001's classes the shape
puts it in:

* **bound**: a relation to the request (`echoes`, `equals`, `counts`, `measures`, `indexes`, `references`,
  `is bounded by`), named by the keyword that states it, at the leaf or at an ancestor that points to it
  (`x-references`, `x-count-where`, `x-count-presence`, `x-claim-nodes`, `x-source-span`, `x-reading-plan`);
* **closed domain**: `const`, `enum`, or the tag of an `x-tagged` grammar;
* **none**: anything else. `pattern`, `minLength` and `maxLength` check a format and put a leaf in no class;
  they are reported as `format`.

`leaves(mode)` is the static census of a mode's row: every leaf path of every branch. `classify(mode,
case, row)` places each leaf of one answer, following only the branches the answer takes. `check(mode,
case, row)` is the generic checker of one answer: the shape check `service_schema.check_row` (the one
validator; nothing here re-validates) and the classification of every leaf it checked.

Paths are patterns: an object member by name, `*` for any array element, a `prefixItems` position by
number, `{}` for the value and `@key` for the key of a map (`additionalProperties`), and `~grammar:tag`
for a tagged-grammar node, whose nested nodes of the same grammar share the pattern; `~grammar/tag` is
the tag itself. A `$ref` to another mode's row (a delegated case) is not expanded: that mode's census
holds it (`Delegation`).

Nothing here is semantic: which branch an answer takes is decided by `service_schema`'s compiled
validators, and the meaning of each keyword is the dialect README's.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path

from .service_schema import DIRECTORY, MODES, Compiler, Context, Invalid, _MISSING, _resolve, check_row

# ADR 0001's relation of each keyword that binds the leaf it stands on.
LEAF_RELATIONS = {
    "x-echo": "echoes", "x-digest": "echoes", "x-equals": "equals", "x-count": "counts",
    "x-index": "indexes", "x-max-steps": "is bounded by", "x-background-bound": "is bounded by",
}
# Keywords that bind an array's length to the request (a dropped or duplicated element is refused).
LENGTH_KEYWORDS = ("x-length", "x-zip", "x-zip-or-empty", "x-rows")
# Keywords that bind its elements to the request element at the same position.
POSITIONAL_KEYWORDS = ("x-zip", "x-zip-or-empty", "x-rows")
FORMAT_KEYWORDS = ("pattern", "minLength", "maxLength", "minimum")
CLASSES = ("bound", "closed domain", "none")
_STRENGTH = {"none": 0, "closed domain": 1, "bound": 2}


@dataclass(frozen=True)
class Binding:
    """How a leaf is bound: its class, the keyword (and the schema site carrying it) and its relation."""
    cls: str = "none"
    keyword: str | None = None
    relation: str | None = None
    at: str | None = None  # the site of the keyword when an ancestor states it
    of: str | None = None  # for a counter (`x-count-where`): the pattern of the array it counts, if all its elements

    def stronger(self, other: "Binding") -> "Binding":
        return other if _STRENGTH[other.cls] > _STRENGTH[self.cls] else self


@dataclass(frozen=True)
class Leaf:
    """One string, integer or map-key leaf of a mode's row."""
    path: str
    kind: str              # string | integer | key
    site: str              # file#pointer of the leaf's schema
    binding: Binding
    format: tuple = ()     # (keyword, value) of the format keywords on the leaf
    branch: tuple = ()     # the anyOf / x-select / if branches taken to reach it
    domain: tuple | None = None  # the values of a closed domain


@dataclass(frozen=True)
class ArrayNode:
    """An array of a mode's row: whether the shape binds its length and its elements' positions."""
    path: str
    site: str
    length: str | None     # the keyword binding its length to the request, or None
    positional: str | None  # the keyword binding element i to request element i, or None
    fixed: bool = False    # a tuple (`prefixItems`): its positions are its shape
    branch: tuple = ()
    items: tuple = (None, None)  # its minItems and maxItems


@dataclass(frozen=True)
class Delegation:
    """A branch answered by another mode's row."""
    path: str
    mode: str
    site: str


@dataclass
class Census:
    leaves: list = field(default_factory=list)
    arrays: list = field(default_factory=list)
    delegations: list = field(default_factory=list)


def render(path: tuple) -> str:
    return "/" + "/".join(str(step) for step in path) if path else "/"


def _steps(pointer: str) -> tuple:
    return tuple(t.replace("~1", "/").replace("~0", "~") for t in pointer.split("/")[1:]) if pointer else ()


def _types(schema: dict) -> set:
    names = schema.get("type")
    found = set([names] if isinstance(names, str) else names or ())
    for value in ([schema["const"]] if "const" in schema else []) + list(schema.get("enum", ())):
        if type(value) is str:
            found.add("string")
        elif type(value) is int:
            found.add("integer")
    if "pattern" in schema or "minLength" in schema or "maxLength" in schema:
        found.add("string")
    if "minimum" in schema:
        found.add("integer")
    return found & {"string", "integer"}


class _Pending:
    """Bindings an ancestor states for the leaves at relative paths (pattern steps; `**` any descendant)."""

    def __init__(self, items=()):
        self.items = tuple(items)

    def add(self, steps: tuple, binding: Binding) -> "_Pending":
        return _Pending(self.items + ((steps, binding),))

    def step(self, step) -> "_Pending":
        out = []
        for steps, binding in self.items:
            if steps and steps[0] == "**":
                out.append((steps, binding))
            elif steps and (steps[0] == step or steps[0] == "*" and step == "*"):
                out.append((steps[1:], binding))
        return _Pending(out)

    def here(self) -> Binding:
        found = Binding()
        for steps, binding in self.items:
            if not steps or steps == ("**",):
                found = found.stronger(binding)
        return found


class _Walker:
    """One walk over a mode's row schema, statically (every branch) or along one answer (`value` given)."""

    def __init__(self, compiler: Compiler):
        self.compiler = compiler
        self.checks: dict = {}

    # Schema access

    def document(self, name: str):
        return self.compiler.document(name)

    def target(self, base: str, reference: str):
        name, _, pointer = reference.partition("#")
        name = name or base
        return name, pointer, _resolve(self.document(name), pointer)

    def valid(self, schema, base: str, value, ctx) -> bool:
        key = (base, id(schema))
        check = self.checks.get(key)
        if check is None:
            check = self.checks[key] = (schema, self.compiler.compile(schema, base))
        try:
            check[1](value, ctx, {})
            return True
        except Invalid:
            return False

    # The walk

    def walk(self, schema, base: str, pointer: str, path: tuple, pending: _Pending, branch: tuple, out: Census,
             value=_MISSING, ctx=None, concrete: tuple = (), stack: tuple = (), grammars: dict | None = None,
             found: list | None = None):
        """Record the leaves, arrays and delegations of `schema` at `path`. With `value`, follow the answer and
        append (concrete path, value, Leaf) to `found`."""
        if not isinstance(schema, dict):
            return
        static = value is _MISSING
        site = f"{base}#{pointer}"
        if "x-tagged" in schema:
            self.grammar(schema, base, pointer, path, pending, branch, out, value, ctx, concrete, stack,
                         grammars or {}, found)
            return
        # Bindings this node and its `allOf` conjuncts state for the leaves below it. A relation keyword on an
        # array or object (`x-equals` of a whole list) binds every leaf below it.
        pending = self.bindings(schema, site, pending, path)
        for i, sub in enumerate(schema.get("allOf", ())):
            if isinstance(sub, dict):
                pending = self.bindings(sub, f"{site}/allOf/{i}", pending, path)
        for keyword, relation in LEAF_RELATIONS.items():
            if keyword in schema:
                pending = pending.add(("**",), Binding("bound", keyword, relation))
        if "$ref" in schema:
            name, target_pointer, target = self.target(base, schema["$ref"])
            if target_pointer == "/row" and name != base and name.removesuffix(".json") in MODES:
                out.delegations.append(Delegation(render(path), name.removesuffix(".json"), site))
            elif target is not _MISSING and (not static or (name, target_pointer) not in stack):
                self.walk(target, name, target_pointer, path, pending, branch, out, value, ctx, concrete,
                          stack + ((name, target_pointer),), grammars, found)
        here = pending.here()
        domain = None
        if "const" in schema or "enum" in schema:
            here = here.stronger(Binding("closed domain", "const" if "const" in schema else "enum"))
            domain = (schema["const"],) if "const" in schema else tuple(schema["enum"])
        kinds = _types(schema)
        if not kinds and set(schema) & set(LEAF_RELATIONS):
            # A property overlay that binds a leaf whose type its `$ref`'d sibling states (`bound_report`).
            kinds = {"overlay"} if static else {"string", "integer"}
        if kinds:
            if static:
                for kind in sorted(kinds):
                    out.leaves.append(Leaf(render(path), kind, site, here, self.formats(schema), branch, domain))
            elif type(value) is str and "string" in kinds or type(value) is int and "integer" in kinds:
                leaf = Leaf(render(path), "string" if type(value) is str else "integer", site, here,
                            self.formats(schema), branch, domain)
                out.leaves.append(leaf)
                found.append((concrete, value, leaf))
        # Composition.
        for keyword in ("allOf",):
            for i, sub in enumerate(schema.get(keyword, ())):
                self.walk(sub, base, f"{pointer}/{keyword}/{i}", path, pending, branch, out, value, ctx, concrete,
                          stack, grammars, found)
        if "anyOf" in schema:
            taken = [i for i, sub in enumerate(schema["anyOf"]) if static or self.valid(sub, base, value, ctx)]
            # Several valid branches are alternatives: a mutant need pass only one of them (`classify`).
            mark = "?" if len(taken) > 1 and not static else ""
            for i in taken:
                self.walk(schema["anyOf"][i], base, f"{pointer}/anyOf/{i}", path, pending,
                          branch + (f"{site}/anyOf/{i}{mark}",), out, value, ctx, concrete, stack, grammars, found)
        if "if" in schema:
            chosen = ("then", "else") if static else (("then",) if self.valid(schema["if"], base, value, ctx)
                                                       else ("else",))
            for keyword in chosen:
                if keyword in schema:
                    self.walk(schema[keyword], base, f"{pointer}/{keyword}", path, pending,
                              branch + (f"{site}/{keyword}",), out, value, ctx, concrete, stack, grammars, found)
        if "x-select" in schema:
            for i, entry in enumerate(schema["x-select"]):
                if static or self.valid(entry["when"], base, ctx.value, ctx):
                    self.walk(entry["then"], base, f"{pointer}/x-select/{i}/then", path, pending,
                              branch + (f"{site}/x-select/{i}",), out, value, ctx, concrete, stack, grammars, found)
                    if not static:
                        break
        # Structure.
        if "properties" in schema:
            for name, sub in schema["properties"].items():
                if static or isinstance(value, dict) and name in value:
                    self.walk(sub, base, f"{pointer}/properties/{_escape(name)}", path + (name,), pending.step(name),
                              branch, out, _MISSING if static else value[name], ctx, concrete + (name,), stack,
                              grammars, found)
        extra = schema.get("additionalProperties")
        if isinstance(extra, dict):
            key_leaf = Leaf(render(path + ("@key",)), "key", f"{site}/additionalProperties", pending.step("@key").here(),
                            (), branch)
            if static:
                out.leaves.append(key_leaf)
                self.walk(extra, base, f"{pointer}/additionalProperties", path + ("{}",), pending.step("{}"), branch,
                          out, stack=stack, grammars=grammars)
            elif isinstance(value, dict):
                known = set(schema.get("properties", ()))
                for name, item in value.items():
                    if name in known:
                        continue
                    out.leaves.append(key_leaf)
                    found.append((concrete + (_Key(name),), name, key_leaf))
                    self.walk(extra, base, f"{pointer}/additionalProperties", path + ("{}",), pending.step("{}"),
                              branch, out, item, ctx, concrete + (name,), stack, grammars, found)
        if {"items", "prefixItems", "minItems", "maxItems", *LENGTH_KEYWORDS} & set(schema):
            self.array(schema, base, pointer, path, pending, branch, out, value, ctx, concrete, stack, grammars, found)

    def array(self, schema, base, pointer, path, pending, branch, out, value, ctx, concrete, stack, grammars, found):
        static = value is _MISSING
        site = f"{base}#{pointer}"
        whole = pending.here()
        exact = whole.keyword if whole.cls == "bound" and whole.relation in ("echoes", "equals") else None
        length = next((k for k in LENGTH_KEYWORDS if k in schema), None) or exact
        positional = next((k for k in POSITIONAL_KEYWORDS if k in schema), None) or exact
        prefix = schema.get("prefixItems", ())
        if static or isinstance(value, list):
            out.arrays.append(ArrayNode(render(path), site, length, positional, bool(prefix), branch,
                                        (schema.get("minItems"), schema.get("maxItems"))))
        for i, sub in enumerate(prefix):
            if static or isinstance(value, list) and i < len(value):
                self.walk(sub, base, f"{pointer}/prefixItems/{i}", path + (str(i),), pending.step(str(i)), branch, out,
                          _MISSING if static else value[i], ctx, concrete + (i,), stack, grammars, found)
        zipped = schema.get("x-zip") or schema.get("x-zip-or-empty")
        items, items_pointer = (zipped["items"], f"{pointer}/{positional}/items") if zipped else (
            schema.get("items"), f"{pointer}/items")
        if items is None:
            return
        if static:
            self.walk(items, base, items_pointer, path + ("*",), pending.step("*"), branch, out, stack=stack,
                      grammars=grammars)
            return
        if not isinstance(value, list):
            return
        contexts = _resolve(ctx.value, zipped["of"]) if zipped else _MISSING
        for i in range(len(prefix), len(value)):
            element_ctx = Context(contexts[i], i) if zipped and isinstance(contexts, list) and i < len(contexts) \
                else ctx
            self.walk(items, base, items_pointer, path + ("*",), pending.step("*"), branch, out, value[i],
                      element_ctx, concrete + (i,), stack, grammars, found)

    def bindings(self, schema: dict, site: str, pending: _Pending, path: tuple = ()) -> _Pending:
        """The bindings `schema`'s keywords state for leaves below it (dialect README)."""
        rule = schema.get("x-references")
        if rule:
            pending = pending.add(_steps(rule["array"]) + ("*", rule["field"]),
                                  Binding("bound", "x-references", "references", site))
        for rule in ([schema["x-count-where"]] if "x-count-where" in schema else []):
            counted = render(path + _steps(rule["array"]))
            pending = pending.add(_steps(rule["equals"]), Binding("bound", "x-count-where", "counts", site,
                                                                  counted if rule["where"] is True else None))
        rule = schema.get("x-count-presence")
        if rule:
            pending = pending.add(_steps(rule["equals"]), Binding("bound", "x-count-presence", "counts", site))
        for pointer in schema.get("x-claim-nodes", ()):
            claim = Binding("bound", "x-claim-nodes", "references", site)
            for prefix in (_steps(pointer), _steps(pointer) + ("*",)):
                pending = pending.add(prefix + ("name",), claim).add(prefix + ("label",), claim)
                pending = pending.add(prefix + ("ast", "**"), claim)
        if "x-source-span" in schema:
            for name, relation in (("start", "is bounded by"), ("end", "is bounded by"), ("line", "equals"),
                                   ("column", "equals")):
                pending = pending.add((name,), Binding("bound", "x-source-span", relation, site))
        if schema.get("x-reading-plan"):
            for steps, relation in ((("choices", "*", "*"), "is bounded by"), (("conditional_on", "*"), "equals"),
                                    (("budget", "max_choices"), "equals"), (("choice_count",), "is bounded by"),
                                    (("units", "*"), "references")):
                pending = pending.add(steps, Binding("bound", "x-reading-plan", relation, site))
        return pending

    @staticmethod
    def formats(schema: dict) -> tuple:
        return tuple((k, schema[k]) for k in FORMAT_KEYWORDS if k in schema)

    def grammar(self, schema, base, pointer, path, pending, branch, out, value, ctx, concrete, stack, grammars, found):
        """A tagged grammar: the tag is closed; each slot is walked under `~name:tag/<slot>`. A slot that is the
        same grammar again shares the pattern, so nested formulas of any depth are walked without recursion."""
        name = _grammar_name(base, pointer)
        site = f"{base}#{pointer}"
        tag_path = path + (f"~{name}", "tag")
        table = schema["x-tagged"]
        tag_leaf = Leaf(render(tag_path), "string", site, Binding("closed domain", "x-tagged"), (), branch,
                        tuple(table))
        if value is _MISSING:
            if site in (grammars or {}):
                return
            grammars = {**(grammars or {}), site: True}
            out.leaves.append(tag_leaf)
            for tag, slots in table.items():
                for i, sub in enumerate(slots, 1):
                    self.slot(sub, base, f"{pointer}/x-tagged/{_escape(tag)}/{i - 1}", path + (f"~{name}:{tag}", str(i)),
                              pending, branch, out, _MISSING, ctx, (), stack, grammars, None, site)
            return
        pending_nodes = [(value, concrete)]
        while pending_nodes:
            node, where = pending_nodes.pop()
            if not isinstance(node, list) or not node or type(node[0]) is not str or node[0] not in table:
                continue
            out.leaves.append(tag_leaf)
            found.append((where + (0,), node[0], tag_leaf))
            for i, sub in enumerate(table[node[0]], 1):
                if i >= len(node):
                    break
                if self.same_grammar(sub, base, site):
                    pending_nodes.append((node[i], where + (i,)))
                    continue
                self.slot(sub, base, f"{pointer}/x-tagged/{_escape(node[0])}/{i - 1}",
                          path + (f"~{name}:{node[0]}", str(i)), pending, branch, out, node[i], ctx, where + (i,),
                          stack, grammars, found, site)

    def same_grammar(self, sub, base, site) -> bool:
        if isinstance(sub, dict) and set(sub) - {"$comment"} == {"$ref"}:
            name, pointer, _ = self.target(base, sub["$ref"])
            return f"{name}#{pointer}" == site
        return False

    def slot(self, sub, base, pointer, path, pending, branch, out, value, ctx, concrete, stack, grammars, found, site):
        if self.same_grammar(sub, base, site):
            return
        self.walk(sub, base, pointer, path, pending, branch, out, value, ctx, concrete, stack, grammars, found)


class _Key(str):
    """A concrete path step naming a map key itself (not its value)."""


def _grammar_name(base: str, pointer: str) -> str:
    """A grammar's name: its definition, and the position inside it of an inline grammar (`q_term.anyOf.0`)."""
    head, _, rest = pointer.rpartition("/$defs/")
    return rest.replace("/", ".") if head or rest else base.removesuffix(".json")


def _escape(name: str) -> str:
    return name.replace("~", "~0").replace("/", "~1")


_compiler = Compiler(DIRECTORY)


def _row(mode: str):
    if mode not in MODES:
        raise KeyError(mode)
    return f"{mode}.json", "/row", _resolve(_compiler.document(f"{mode}.json"), "/row")


def census(mode: str, directory: Path | None = None) -> Census:
    """Every leaf, array and delegation of every branch of `mode`'s row."""
    compiler = _compiler if directory is None else Compiler(directory)
    walker = _Walker(compiler)
    name, pointer = f"{mode}.json", "/row"
    out = Census()
    walker.walk(_resolve(compiler.document(name), pointer), name, pointer, (), _Pending(), (), out,
                stack=((name, pointer),))
    return out


def leaves(mode: str) -> list[Leaf]:
    """The static census of `mode`'s row: one entry per leaf path, kind, class and branch set."""
    merged: dict = {}
    found = census(mode).leaves
    overlays = [leaf for leaf in found if leaf.kind == "overlay"]
    for leaf in found:
        if leaf.kind == "overlay":
            continue
        for overlay in overlays:
            if overlay.path == leaf.path and overlay.branch == leaf.branch:
                leaf = replace(leaf, binding=leaf.binding.stronger(overlay.binding))
        key = (leaf.path, leaf.kind, leaf.branch)
        merged[key] = replace(leaf, binding=merged[key].binding.stronger(leaf.binding)) if key in merged else leaf
    out: dict = {}
    for leaf in merged.values():
        key = (leaf.path, leaf.kind, leaf.binding, leaf.format)
        if key in out:
            out[key] = replace(out[key], branch=out[key].branch + leaf.branch)
        else:
            out[key] = leaf
    return sorted(out.values(), key=lambda leaf: (leaf.path, leaf.kind, CLASSES.index(leaf.binding.cls),
                                                  str(leaf.binding.keyword)))


def classify(mode: str, case: object, row: object, index: int = 0) -> tuple[list, Census]:
    """[(concrete path, value, Leaf)] for every leaf of `row` (an answer to `case`), along the branches it
    takes; a leaf reached by several valid branches gets the weakest binding of them (a mutant need pass only
    one). Concrete paths step through object members (a `_Key` step names the key itself) and list positions."""
    name, pointer, schema = _row(mode)
    walker = _Walker(_compiler)
    out, found = Census(), []
    walker.walk(schema, name, pointer, (), _Pending(), (), out, row, Context(case, index), (),
                ((name, pointer),), None, found)
    by_path: dict = {}
    for concrete, value, leaf in found:
        key = (concrete, type(concrete[-1]) if concrete else None)
        by_path.setdefault(key, []).append((concrete, value, leaf))
    placed = []
    for entries in by_path.values():
        # Conjuncts on one branch: the strongest binding holds. Alternatives (several valid anyOf branches,
        # marked `?`): the weakest of their strongest holds.
        per_branch: dict = {}
        for entry in entries:
            leaf = entry[2]
            alternative = tuple(step for step in leaf.branch if step.endswith("?"))
            best = per_branch.get(alternative)
            if best is None:
                per_branch[alternative] = entry
                continue
            # Conjuncts: the strongest binding, every format, and the closed domain if either has one.
            strong, weak = (entry, best) if _STRENGTH[leaf.binding.cls] > _STRENGTH[best[2].binding.cls] else (best, entry)
            merged = replace(strong[2], format=tuple(dict.fromkeys(strong[2].format + weak[2].format)),
                             domain=strong[2].domain if strong[2].domain is not None else weak[2].domain)
            per_branch[alternative] = (strong[0], strong[1], merged)
        ambiguous = [entry for key, entry in per_branch.items() if key]
        choice = min(ambiguous, key=lambda entry: _STRENGTH[entry[2].binding.cls]) if ambiguous else per_branch[()]
        unconditional = per_branch.get(())
        if ambiguous and unconditional is not None:
            choice = choice if _STRENGTH[choice[2].binding.cls] >= _STRENGTH[unconditional[2].binding.cls] \
                else unconditional
        placed.append(choice)
    return placed, out


def check(mode: str, case: object, row: object, index: int = 0) -> list:
    """The generic checker of one answer: `row` passes the mode's Lean shape for `case` at `index`
    (`service_schema.check_row`, raising `Invalid` otherwise), and its leaves are classified (`classify`)."""
    check_row(mode, row, case, index)
    return classify(mode, case, row, index)[0]
