"""Environment-specific CFGs for canonical VE, without decoding dependencies.

Full mode enumerates finite binding contexts; syntax mode forgets variable scope
and sorts. Both retain predicate arity, constant sorts, and preorder binder names.
See docs/constrained-authoring.md for bounds, backend usage, and guarantees.
"""
from __future__ import annotations

from collections import deque
import json

from .environment import Environment
from .errors import ResourceLimit
from .limits import MAX_DEPTH, MAX_NODES
from .ast import INT_SORT


def _integer(name: str, value: int, maximum: int) -> None:
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(f"{name} must be an integer between 0 and {maximum}")


class _Grammar:
    def __init__(self, env, mode, depth, binders, max_rules, wrapper):
        self.env, self.mode = env, mode
        self.depth, self.binders = depth, binders
        self.max_rules, self.wrapper = max_rules, wrapper
        self.rules: dict[str, list[str]] = {}
        self.states = {}
        self.pending = deque()
        self.terms = {}
        self.productions = 0
        self.sorts = tuple(sorted(env.sorts))
        self.int_terms = {}

    def literal(self, value):
        # A VE newline must become the two JSON-string characters \\n inside
        # the wrapper. Then quote that terminal for the grammar metalanguage.
        if self.wrapper:
            value = json.dumps(value, ensure_ascii=True)[1:-1]
        return json.dumps(value, ensure_ascii=True)

    def add(self, name, *symbols):
        if self.productions >= self.max_rules:
            raise ResourceLimit(
                f"Grammar exceeds {self.max_rules} productions; lower binder bounds "
                "or use mode='syntax'")
        self.rules.setdefault(name, []).append(" ".join(symbols))
        self.productions += 1

    def state(self, context, depth, begin, end):
        # At maximum nesting, only formulas consuming zero new binders exist.
        if begin < end and (not self.sorts or depth >= self.depth):
            return None
        key = (context if self.mode == "full" else depth, begin, end)
        if key not in self.states:
            if len(self.states) >= self.max_rules:
                raise ResourceLimit("Grammar binding-context budget exceeded")
            name = f"f{len(self.states)}"
            self.states[key] = name
            self.pending.append((name, context, depth, begin, end))
        return self.states[key]

    def term(self, context, sort):
        if sort == INT_SORT and self.env.order:
            return self.integer_term(context)
        key = (context if self.mode == "full" else (), sort)
        if key in self.terms:
            return self.terms[key]
        values = ["@" + name for name, decl in sorted(self.env.constants.items())
                  if decl.sort == sort]
        if self.mode == "full":
            values += [f"x{i}" for i, bound_sort in context if bound_sort == sort]
        else:
            values += [f"x{i}" for i in range(self.binders)]
        name = f"t{len(self.terms)}" if values else None
        self.terms[key] = name
        for value in values:
            self.add(name, self.literal(value))
        return name

    def integer_term(self, context):
        key = context if self.mode == "full" else ()
        if key in self.int_terms:
            return self.int_terms[key]
        name = f"i{len(self.int_terms)}"
        self.int_terms[key] = name
        other = name + "o"
        plus = name + "p"
        self.add(name, "numeral")
        self.add(name, other)
        for constant, decl in sorted(self.env.constants.items()):
            if decl.sort == INT_SORT:
                self.add(other, self.literal("@" + constant))
                self.add(plus, self.literal("@" + constant))
        indices = (i for i, sort in context if sort == INT_SORT) if self.mode == "full" else range(self.binders)
        for index in indices:
            self.add(other, self.literal(f"x{index}"))
            self.add(plus, self.literal(f"x{index}"))
        # Keep direct negation and [-1 * numeral] apart: the former may not
        # precede a numeral, while the latter is its canonical AST spelling.
        self.add(other, self.literal("-"), other)
        self.add(other, self.literal("["), "coefficient", self.literal(" * "), name, self.literal("]"))
        self.add(other, self.literal("[-1 * "), "numeral", self.literal("]"))
        self.add(other, self.literal("["), name, self.literal(" + "), plus, self.literal("]"))
        self.add(other, self.literal("["), name, self.literal(" - "), name, self.literal("]"))
        self.add(plus, "numeral")
        self.add(plus, self.literal("["), "coefficient", self.literal(" * "), name, self.literal("]"))
        self.add(plus, self.literal("["), name, self.literal(" + "), plus, self.literal("]"))
        self.add(plus, self.literal("["), name, self.literal(" - "), name, self.literal("]"))
        return name

    def formula(self, name, context, depth, begin, end):
        q = self.literal
        if begin == end:
            self.add(name, q("true"))
            self.add(name, q("false"))
            terms = {sort: self.term(context, sort) for sort in self.sorts}
            if self.env.order:
                terms[INT_SORT] = self.term(context, INT_SORT)
            for pred, decl in sorted(self.env.predicates.items()):
                args = [terms[sort] for sort in decl.arguments]
                if any(term is None for term in args):
                    continue
                if len(args) == 1:
                    self.add(name, args[0], q(f" is {pred}"))
                else:
                    self.add(name, args[0], q(f" {pred} "), args[1])
                    if self.env.closure and decl.arguments[0] == decl.arguments[1]:
                        for op in ("tc", "rtc"):
                            self.add(name, q(f"{op}[{pred}]("), args[0], q(", "), args[1], q(")"))
            for term in terms.values():
                if term is not None:
                    self.add(name, term, q(" equals "), term)
            if self.env.order:
                integer = terms[INT_SORT]
                self.add(name, integer, q(" < "), integer)
                self.add(name, integer, q(" <= "), integer)
        self.add(name, q("not ("), name, q(")"))
        for middle in range(begin, end + 1):
            left = self.state(context, depth, begin, middle)
            right = self.state(context, depth, middle, end)
            if left is not None and right is not None:
                self.add(name, q("("), left, q(") and ("), right, q(")"))
                self.add(name, q("("), left, q(") or ("), right, q(")"))
                self.add(name, q("if ("), left, q("), then ("), right, q(")"))
        if self.env.closure and begin + 2 <= end and depth + 2 <= self.depth:
            for sort in self.sorts:
                endpoint = self.term(context, sort)
                nested = context + ((begin, sort), (begin + 1, sort)) if self.mode == "full" else ()
                body = self.state(nested, depth + 2, begin + 2, end)
                if endpoint is not None and body is not None:
                    for op in ("tc", "rtc"):
                        self.add(name, q(f"{op}[{sort} x{begin}, x{begin + 1} | ("), body,
                                 q(")]("), endpoint, q(", "), endpoint, q(")"))
        if begin < end:
            for sort in self.sorts:
                nested = context + ((begin, sort),) if self.mode == "full" else ()
                body = self.state(nested, depth + 1, begin + 1, end)
                if body is not None:
                    for keyword in ("for every", "there exists"):
                        self.add(name, q(f"{keyword} {sort} x{begin}, ("), body, q(")"))

    def build(self):
        self.add("document", "statement", "document")
        self.add("document", "statement")
        for end in range(self.binders + 1):
            formula = self.state((), 0, 0, end)
            if formula is not None:
                self.add("statement", formula, self.literal(".\n"))
        while self.pending:
            self.formula(*self.pending.popleft())

    def render(self, dialect):
        root, separator = ("start", ":") if dialect == "lark" else ("root", "::=")
        q = json.dumps  # Wrapper punctuation is not itself JSON-string escaped.
        if self.wrapper:
            entry = " ".join((q('{"ve": "'), "document",
                              q('\", "explanation": '), "jsonstring", q("}")))
        else:
            entry = "document"
        lines = [f"{root} {separator} {entry}"]
        lines += [f"{name} {separator} " + " | ".join(alts)
                  for name, alts in self.rules.items()]
        if self.env.order:
            if dialect == "lark":
                number = r'/0|[1-9][0-9]*|-[1-9][0-9]*/'
                coefficient = r'/0|[1-9][0-9]*|-(?:[1-9][0-9]+|[2-9])/'
            else:
                number = r'"0" | [1-9] [0-9]* | "-" [1-9] [0-9]*'
                coefficient = r'"0" | [1-9] [0-9]* | "-" ([2-9] | [1-9] [0-9]+)'
            lines.append(f"numeral {separator} {number}")
            lines.append(f"coefficient {separator} {coefficient}")
        if self.wrapper:
            # Same JSON string language in each dialect. No implicit whitespace.
            char = r'/[^"\\\x00-\x1f]/' if dialect == "lark" else r'[^"\\\x00-\x1f]'
            escaped = r'/["\\\/bfnrt]/' if dialect == "lark" else r'["\\/bfnrt]'
            hexdigit = r'/[0-9a-fA-F]/' if dialect == "lark" else r'[0-9a-fA-F]'
            lines += [f'jsonstring {separator} {q(chr(34))} jsonchars {q(chr(34))}',
                      f'jsonchars {separator} jsonchar*',
                      f'jsonchar {separator} {char} | {q(chr(92))} {escaped} | '
                      f'{q(chr(92) + "u")} hex hex hex hex',
                      f'hex {separator} {hexdigit}']
        return "\n".join(lines) + "\n"


def export_grammar(env: Environment, *, dialect: str = "lark", mode: str = "full",
                   max_binder_depth: int = 3, max_binders: int | None = None,
                   max_rules: int = 20_000, wrapper: bool = False) -> str:
    """Export strict VE as Lark, llama.cpp GBNF, or XGrammar EBNF.

    ``max_binders`` limits *total* binders per statement, not nesting, because
    canonical preorder names are globally fresh within a statement. It defaults
    to ``max_binder_depth``; increasing it permits more sibling binders. Full mode
    enforces active scope and sort. Syntax mode permits ill-scoped/typed variables.

    ``max_rules`` caps production alternatives to stop exponential expansion.
    Runtime source/node/formula-depth limits still require the VE checker.
    ``wrapper=True`` generates a JSON object with a grammar-constrained ``ve``
    string and an unconstrained JSON ``explanation`` string, in that key order.
    """
    if not isinstance(env, Environment):
        raise TypeError("env must be a validated Environment")
    if dialect not in ("lark", "gbnf", "ebnf"):
        raise ValueError("dialect must be 'lark', 'gbnf', or 'ebnf'")
    if mode not in ("full", "syntax"):
        raise ValueError("mode must be 'full' or 'syntax'")
    _integer("max_binder_depth", max_binder_depth, MAX_DEPTH - 1)
    if max_binders is None:
        max_binders = max_binder_depth
    _integer("max_binders", max_binders, MAX_NODES)
    if type(max_rules) is not int or max_rules < 1:
        raise ValueError("max_rules must be a positive integer")
    if type(wrapper) is not bool:
        raise ValueError("wrapper must be Boolean")
    grammar = _Grammar(env, mode, max_binder_depth, max_binders, max_rules, wrapper)
    grammar.build()
    from .surface.registry import records
    for record in records():
        if record.strict_grammar_hook is not None:
            record.strict_grammar_hook(grammar)
    return grammar.render(dialect)


def structured_output_spec(env: Environment, *, dialect: str = "lark",
                           mode: str = "full", max_binder_depth: int = 3,
                           max_binders: int | None = None,
                           max_rules: int = 20_000) -> dict:
    """Return an adapter spec, not a provider request or standard JSON Schema.

    ``json_schema`` describes the object shape. Its ``x-ve-grammar`` annotation
    is informative: ordinary JSON Schema validators do not enforce it. Pass the
    sibling ``grammar`` (covering the complete JSON object) to a CFG backend.
    """
    options = dict(dialect=dialect, mode=mode, max_binder_depth=max_binder_depth,
                   max_binders=max_binders, max_rules=max_rules)
    raw = export_grammar(env, **options)
    return {
        "environment_id": env.environment_id,
        "dialect": dialect,
        "mode": mode,
        "max_binder_depth": max_binder_depth,
        "max_binders": max_binder_depth if max_binders is None else max_binders,
        "json_schema": {
            "type": "object",
            "properties": {
                "ve": {"type": "string", "x-ve-grammar": {"dialect": dialect, "grammar": raw}},
                "explanation": {"type": "string"},
            },
            "required": ["ve", "explanation"],
            "additionalProperties": False,
        },
        "grammar": export_grammar(env, wrapper=True, **options),
    }
