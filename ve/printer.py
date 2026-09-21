"""Four deterministic surfaces of one checked AST and one scope traversal."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re
from typing import Any

from . import ast
from .errors import ResourceLimit
from .limits import MAX_PACKAGE_BYTES, MAX_SOURCE_BYTES

VIEWS = ("fol_symbols", "fol_keywords", "ve_strict", "ve_natural")
NATURAL_RENDERER = "ve.ace-explicit"
NATURAL_RENDERER_VERSION = "1"

# These tables contain surface vocabulary only. Children arrive already grouped
# by the ONE traversal below; no surface can change scope, names, or child order.
_SURFACES = {
    "fol_symbols": {
        ast.Top: "⊤", ast.Bottom: "⊥", ast.Unary: "{predicate}({left})",
        ast.Binary: "{predicate}({left}, {right})", ast.Eq: "{left} = {right}",
        ast.Not: "¬ {body}", ast.And: "{left} ∧ {right}",
        ast.Or: "{left} ∨ {right}", ast.Implies: "{left} → {right}",
        ast.Forall: "∀ {name}:{sort}, {body}", ast.Exists: "∃ {name}:{sort}, {body}",
    },
    "fol_keywords": {
        ast.Top: "true", ast.Bottom: "false", ast.Unary: "{predicate}({left})",
        ast.Binary: "{predicate}({left}, {right})", ast.Eq: "{left} = {right}",
        ast.Not: "not {body}", ast.And: "{left} and {right}",
        ast.Or: "{left} or {right}", ast.Implies: "{left} implies {right}",
        ast.Forall: "forall {name}:{sort}, {body}", ast.Exists: "exists {name}:{sort}, {body}",
    },
    "ve_strict": {
        ast.Top: "true", ast.Bottom: "false", ast.Unary: "{left} is {predicate}",
        ast.Binary: "{left} {predicate} {right}", ast.Eq: "{left} equals {right}",
        ast.Not: "not {body}", ast.And: "{left} and {right}",
        ast.Or: "{left} or {right}", ast.Implies: "if {left}, then {right}",
        ast.Forall: "for every {sort} {name}, {body}", ast.Exists: "there exists {sort} {name}, {body}",
    },
    "ve_natural": {
        ast.Top: "true", ast.Bottom: "false", ast.Eq: "{left} is equal to {right}",
        ast.Not: "it is not the case that {body}", ast.And: "{left} and {right}",
        ast.Or: "{left} or {right}, or both", ast.Implies: "if {left}, then {right}",
        ast.Forall: "for every {sort} {name}: {body}",
        ast.Exists: "there is a {sort} {name} such that {body}",
    },
}

# Templates are deliberately a small positive atomic grammar. Logical language,
# punctuation, variable-looking words, missing/repeated arguments and format
# expressions are excluded. Unsupported strings remain in the environment but
# cause strict fallback; they are never interpreted with Python str.format.
_WORDS = re.compile(r"[a-z]+(?: [a-z]+)*\Z", re.ASCII)
_LOGICAL_WORDS = frozenset("""all any every some no none not never neither nor
    and or both either if then unless except without only exists forall implies
    true false equal equals there such that case condition for at least most
    exactly does do must may can cannot should shall will would whenever when
    implies iff otherwise always sometimes one two three four five six seven
    eight nine ten a an the""".split())


def _phrase(value: str) -> bool:
    return bool(_WORDS.fullmatch(value)) and not _LOGICAL_WORDS.intersection(value.split())


def _predicate_template(value: str | None, arity: int) -> str | None:
    if value is None or not value.startswith("{0} "):
        return None
    phrase = value[4:]
    if arity == 2:
        if not phrase.endswith(" {1}"):
            return None
        phrase = phrase[:-4]
    if not _phrase(phrase):
        return None
    if arity == 1 and (not phrase.startswith("is ") or len(phrase.split()) < 2):
        return None
    if arity == 2:
        words = phrase.split()
        if not words[0].endswith("s") or phrase == "is":
            return None
    return value


class _NaturalVocabulary:
    """Select collision-free lexical templates against the entire vocabulary."""
    def __init__(self, env):
        strict = {name: "{0} is " + name if len(p.arguments) == 1
                  else "{0} " + name + " {1}" for name, p in env.predicates.items()}
        candidates = {name: _predicate_template(p.verbalisation, len(p.arguments))
                      for name, p in env.predicates.items()}
        counts = Counter(v for v in candidates.values() if v is not None)
        canonical_owner = {template: name for name, template in strict.items()}
        self.predicates = {}
        for name, candidate in candidates.items():
            safe = (candidate is not None and counts[candidate] == 1
                    and canonical_owner.get(candidate, name) == name)
            self.predicates[name] = candidate if safe else strict[name]
        nouns = {name: p.verbalisation.singular if p.verbalisation is not None
                 and _phrase(p.verbalisation.singular) else name
                 for name, p in env.sorts.items()}
        counts = Counter(nouns.values())
        self.sorts = {name: noun if counts[noun] == 1 and (noun not in env.sorts or noun == name)
                      else name for name, noun in nouns.items()}

    def atom(self, predicate, terms):
        # Literal replacement only. Terms cannot contain braces, and every safe
        # template contains each positional placeholder exactly once in order.
        text = self.predicates[predicate]
        for index, term in enumerate(terms):
            text = text.replace("{" + str(index) + "}", term)
        return text


class _Traversal:
    def __init__(self, env, view):
        self.next_name = 0
        self.surface = _SURFACES[view]
        self.natural = _NaturalVocabulary(env) if view == "ve_natural" else None

    @staticmethod
    def term(value, scope):
        if isinstance(value, ast.Var):
            return scope[value.index]
        return "@" + value.name

    def child(self, value, scope):
        # Every immediate formula operand is grouped in EVERY view, even atoms.
        # Predicate application parentheses in FOL are lexical argument lists.
        return "(" + self.formula(value, scope) + ")"

    def formula(self, value, scope):
        kind = type(value)
        fields = {}
        if kind in (ast.Unary, ast.Binary, ast.Eq):
            terms = (value.term,) if kind is ast.Unary else (value.left, value.right)
            rendered = tuple(self.term(term, scope) for term in terms)
            fields["left"] = rendered[0]
            if len(rendered) == 2:
                fields["right"] = rendered[1]
            if kind in (ast.Unary, ast.Binary):
                if self.natural is not None:
                    return self.natural.atom(value.predicate, rendered)
                fields["predicate"] = value.predicate
        elif kind is ast.Not:
            fields["body"] = self.child(value.body, scope)
        elif kind in (ast.And, ast.Or, ast.Implies):
            fields["left"] = self.child(value.left, scope)
            fields["right"] = self.child(value.right, scope)
        elif kind in (ast.Forall, ast.Exists):
            name = f"x{self.next_name}"
            self.next_name += 1
            fields.update(name=name, sort=(self.natural.sorts[value.sort] if self.natural else value.sort))
            fields["body"] = self.child(value.body, (name, *scope))
            if kind is ast.Exists and self.natural and fields["sort"][0] in "aeiou":
                # The article is display vocabulary; it makes no cardinality claim.
                return "there is an {sort} {name} such that {body}".format_map(fields)
        return self.surface[kind].format_map(fields)


def render(value: ast.Document | ast.Formula, env: Any, view: str = "ve_strict") -> str:
    """Render a checked AST with shared preorder names and formula grouping.

    A formula has no final punctuation; documents have a period and LF for each
    statement. Natural documents capitalize the first letter of each statement.
    The counter resets per statement. No view rewrites or normalizes the AST.
    """
    if view not in VIEWS:
        raise ValueError(f"view must be one of {VIEWS}")
    if isinstance(value, ast.Document):
        ast.check_document(env, value)
        lines = []
        for formula in value.formulas:
            line = _Traversal(env, view).formula(formula, ())
            if view == "ve_natural":
                line = line[0].upper() + line[1:]
            lines.append(line + ".\n")
        text = "".join(lines)
    else:
        ast.check_formula(env, value)
        text = _Traversal(env, view).formula(value, ())
    limit = MAX_SOURCE_BYTES if view == "ve_strict" else MAX_PACKAGE_BYTES
    if len(text.encode("utf-8")) + (0 if isinstance(value, ast.Document) else 2) > limit:
        raise ResourceLimit(f"Rendered {view} text exceeds its {limit}-byte limit")
    return text


def print_formula(env: Any, formula: Any) -> str:
    """Print one closed formula without statement punctuation."""
    ast.check_formula(env, formula)
    return render(formula, env, "ve_strict")


def print_document(env: Any, document: ast.Document) -> str:
    """Return the sole canonical VE v0 serialization of *document*."""
    ast.check_document(env, document)
    return render(document, env, "ve_strict")


@dataclass(frozen=True, slots=True)
class NaturalView:
    text: str
    environment_id: str
    meaning_id: str
    renderer: str = NATURAL_RENDERER
    version: str = NATURAL_RENDERER_VERSION

    def to_dict(self) -> dict[str, str]:
        return {"text": self.text, "environment_id": self.environment_id,
                "meaning_id": self.meaning_id, "renderer": self.renderer,
                "version": self.version}


def natural_document(env: Any, document: ast.Document) -> NaturalView:
    """Render a validated read-only view with explicit scope and dependencies."""
    ast.check_document(env, document)
    from .identity import meaning_id
    return NaturalView(render(document, env, "ve_natural"), env.environment_id,
                       meaning_id(env, document))


def natural_formula(env: Any, formula: Any) -> NaturalView:
    ast.check_formula(env, formula)
    from .identity import meaning_id
    return NaturalView(render(formula, env, "ve_natural") + ".", env.environment_id,
                       meaning_id(env, formula))
