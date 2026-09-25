"""Statement-initial surface dispatch, ordered by longest English keyword."""
from __future__ import annotations

from dataclasses import dataclass
from .. import ast


@dataclass(frozen=True, slots=True)
class SurfaceRecord:
    wire_tag: str
    strict_form: str
    english_keywords: tuple[str, ...]
    fluent_form: str
    grammar_production: str
    evaluator_hook: object = None
    traversal_hooks: object = None
    witness_renderer: object = None
    node_type: type | None = None
    wire_arity: int | None = None
    parser_hook: object = None
    strict_parser_hook: object = None
    printer_hook: object = None
    fluent_hook: object = None
    english_renderer: object = None
    grammar_hook: object = None
    strict_grammar_hook: object = None
    wire_encoder: object = None
    wire_decoder: object = None
    fol_import_hook: object = None
    fol_export_hook: object = None
    typecheck_hook: object = None
    profiles: tuple[str, ...] = ()


_records: dict[str, SurfaceRecord] = {}
_by_type: dict[type, SurfaceRecord] = {}
KEYWORDS: tuple[tuple[str, SurfaceRecord], ...] = ()


def register(record: SurfaceRecord) -> None:
    global KEYWORDS
    if not isinstance(record, SurfaceRecord):
        raise TypeError("expected a SurfaceRecord")
    if record.wire_tag in _records:
        raise ValueError(f"Duplicate wire tag {record.wire_tag}")
    if record.node_type is not None and record.node_type in _by_type:
        raise ValueError(f"Duplicate surface constructor {record.node_type.__name__}")
    if type(record.profiles) is not tuple or record.profiles != tuple(sorted(set(record.profiles))):
        raise ValueError("Surface profiles must be sorted and unique")
    if record.traversal_hooks is not None and type(record.traversal_hooks) is not dict:
        raise ValueError("Traversal hooks must be a mapping")
    for value in (record.evaluator_hook, record.witness_renderer, record.parser_hook,
                  record.strict_parser_hook, record.printer_hook, record.fluent_hook,
                  record.english_renderer, record.grammar_hook, record.strict_grammar_hook,
                  record.wire_encoder, record.wire_decoder, record.fol_import_hook,
                  record.fol_export_hook, record.typecheck_hook,
                  *((record.traversal_hooks or {}).values())):
        if value is not None and (not callable(value) or not value.__module__.startswith("ve.")):
            raise ValueError("Surface hooks must be callables from ve modules")
    keywords = {word for existing in _records.values() for word in existing.english_keywords}
    for keyword in record.english_keywords:
        if keyword in keywords or record.english_keywords.count(keyword) != 1:
            raise ValueError(f"Duplicate English keyword {keyword!r}")
    _records[record.wire_tag] = record
    if record.node_type is not None:
        _by_type[record.node_type] = record
    KEYWORDS = tuple(sorted(((keyword, item) for item in _records.values()
                             for keyword in item.english_keywords),
                            key=lambda item: (-len(item[0]), item[0])))


def records() -> tuple[SurfaceRecord, ...]:
    return tuple(_records.values())


def enabled(record: SurfaceRecord, env) -> bool:
    return all(profile in env.profiles for profile in record.profiles)


def by_tag(tag: str) -> SurfaceRecord | None:
    return _records.get(tag)


def by_node(node) -> SurfaceRecord | None:
    return _by_type.get(type(node))


def formula_arities() -> dict[str, int]:
    return {record.wire_tag: record.wire_arity for record in _records.values()
            if record.wire_arity is not None}


def keywords() -> tuple[tuple[str, SurfaceRecord], ...]:
    return KEYWORDS


def dispatch(source: str, env=None):
    return next(((keyword, record) for keyword, record in keywords()
                 if source.startswith(keyword) and (env is None or enabled(record, env))), None)


def strict_dispatch(source: str, env=None):
    candidates = ((record.strict_form, record) for record in _records.values()
                  if record.strict_parser_hook is not None and (env is None or enabled(record, env)))
    return next(((prefix, record) for prefix, record in sorted(candidates,
                 key=lambda item: (-len(item[0]), item[0])) if source.startswith(prefix)), None)


register(SurfaceRecord("not", "not", ("it is not the case that ",), "not", "negation",
                       node_type=ast.Not, wire_arity=2))
register(SurfaceRecord("and", "and", ("both of the following hold:", "all of the following hold:",
                                            "both "), "and", "listing | compact",
                       node_type=ast.And, wire_arity=3))
register(SurfaceRecord("or", "or", ("at least one of the following holds:", "either "),
                       "or", "listing | compact", node_type=ast.Or, wire_arity=3))
register(SurfaceRecord("implies", "if", ("if the following holds:", "if "),
                       "implies", "listing | compact", node_type=ast.Implies, wire_arity=3))
register(SurfaceRecord("forall", "for every", ("for every ", "every "),
                       "for every", "universal", node_type=ast.Forall, wire_arity=3))
register(SurfaceRecord("exists", "there exists", ("there is ",),
                       "there is", "existential", node_type=ast.Exists, wire_arity=3))
register(SurfaceRecord("reach", "tc/rtc", ("starting from ",),
                       "reachable", "reach", node_type=ast.Reach, wire_arity=5))

for tag, node_type, arity in (("top", ast.Top, 1), ("bottom", ast.Bottom, 1),
                              ("unary", ast.Unary, 3), ("binary", ast.Binary, 4),
                              ("eq", ast.Eq, 3), ("lt", ast.Lt, 3), ("le", ast.Le, 3)):
    register(SurfaceRecord(tag, tag, (), tag, "atom", node_type=node_type, wire_arity=arity))
