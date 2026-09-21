"""Five deterministic, read-only surfaces of one checked AST."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import json
import re
from typing import Any, Iterable

from . import ast
from .errors import ResourceLimit
from .limits import MAX_SOURCE_BYTES

VIEWS = ("fol_symbols", "fol_keywords", "ve_strict", "ve_natural", "ve_fluent")
NATURAL_RENDERER = "ve.ace-explicit"
NATURAL_RENDERER_VERSION = "2"

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
_LOGICAL_WORDS = frozenset("""all any every some each no none not never neither nor
    and or both either if then unless except without only exists forall implies
    true false equal equals there such that case condition for at least most
    exactly does do must may can cannot should shall will would whenever when
    implies iff otherwise always sometimes one two three four five six seven
    eight nine ten a an the lacks""".split())
_AUXILIARIES = frozenset("is are was were be been being gets got".split())
_CONVERSE_ENDINGS = frozenset("by to of from with for".split())
_TOKENS = re.compile(r"[A-Za-z][A-Za-z0-9_]*(?:-[A-Za-z]+)?", re.ASCII)
_VARIABLE = re.compile(r"(?:x[0-9]*|[A-Z])\Z", re.ASCII)


@dataclass(frozen=True, slots=True)
class VocabularyLint:
    """A stable diagnostic code at a vocabulary JSON path; rendering falls back."""
    path: str
    code: str

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "code": self.code}


def _template_head(value: str, arity: int) -> str | None:
    words = _TOKENS.findall(value)
    if arity == 1 and words[:1] == ["is"]:
        words = words[1:]
    return words[0] if words else None


class _NaturalVocabulary:
    """One conservative lexical policy shared by rendering and public linting.

    This is a heuristic over trusted declarations, not an English meaning proof.
    Inspect all declarations, including unusable templates and unused symbols.
    """
    def __init__(self, env):
        strict = {name: "{0} is " + name if len(p.arguments) == 1
                  else "{0} " + name + " {1}" for name, p in env.predicates.items()}
        owners = defaultdict(set)
        predicate_heads = set(env.predicates)
        for declarations in (env.sorts, env.predicates, env.constants):
            for name in declarations:
                owners[name].add(name)
        for name, p in env.predicates.items():
            head = _template_head(p.verbalisation or strict[name], len(p.arguments))
            if head:
                owners[head].add(name)
                predicate_heads.add(head)
        nouns = defaultdict(set)
        for name, s in env.sorts.items():
            nouns[name].add(name)
            if s.verbalisation is not None:
                for noun in (s.verbalisation.singular, s.verbalisation.plural):
                    nouns[noun].add(name)
                    words = _TOKENS.findall(noun)
                    if words:
                        owners[words[-1]].add(name)
        negated_heads = {prefix + head for prefix in ("un", "non", "un-", "non-")
                         for head in predicate_heads}

        issues = set()

        def report(path, code):
            issues.add(VocabularyLint(path, code))

        def phrase_checks(name, phrase, path):
            words = _TOKENS.findall(phrase)
            if not _WORDS.fullmatch(phrase):
                report(path, "PHRASE_SYNTAX")
            if _LOGICAL_WORDS.intersection(words):
                report(path, "LOGICAL_WORD")
            if any(_VARIABLE.fullmatch(word) for word in words):
                report(path, "VARIABLE_TOKEN")
            if any(owners[word] - {name} for word in words):
                report(path, "SYMBOL_COLLISION")
            if negated_heads.intersection(words):
                report(path, "NEGATED_HEAD")

        counts = Counter(p.verbalisation for p in env.predicates.values()
                         if p.verbalisation is not None)
        self.predicates = {}
        for name, p in env.predicates.items():
            value = p.verbalisation
            self.predicates[name] = strict[name]
            if value is None:
                continue
            path = f"/vocabulary/predicates/{name}/verbalisation"
            before = len(issues)
            if counts[value] > 1:
                report(path, "DUPLICATE_TEMPLATE")
            arity = len(p.arguments)
            # Anchors and the positive phrase grammar also exclude repeated,
            # reordered, missing, converted, or attribute-access placeholders.
            shape = (r"\{0\} (.+)" if arity == 1 else r"\{0\} (.+) \{1\}")
            match = re.fullmatch(shape, value)
            if match is None:
                report(path, "TEMPLATE_SHAPE")
            else:
                phrase = match[1]
                phrase_checks(name, phrase, path)
                words = phrase.split()
                if arity == 1:
                    if not words or words[0] != "is" or len(words) < 2:
                        report(path, "TEMPLATE_SHAPE")
                    elif len(words) != 2:
                        # A single complement head; no post-head adverbs or
                        # other modifiers such as "reviewed already".
                        report(path, "UNARY_MODIFIER")
                elif words:
                    if words[0] in _AUXILIARIES:
                        report(path, "BINARY_AUXILIARY")
                    if words[-1] in _CONVERSE_ENDINGS:
                        report(path, "BINARY_CONVERSE")
                    if not words[0].endswith("s"):
                        report(path, "BINARY_VERB")
            if len(issues) == before:
                self.predicates[name] = value

        self.sorts = {}
        for name, s in env.sorts.items():
            self.sorts[name] = name
            if s.verbalisation is None:
                continue
            before = len(issues)
            for field in ("singular", "plural"):
                noun = getattr(s.verbalisation, field)
                path = f"/vocabulary/sorts/{name}/verbalisation/{field}"
                phrase_checks(name, noun, path)
                if nouns[noun] - {name}:
                    report(path, "SORT_COLLISION")
            if len(issues) == before:
                self.sorts[name] = s.verbalisation.singular
        self.issues = tuple(sorted(issues, key=lambda issue: (issue.path, issue.code)))

    def atom(self, predicate, terms):
        # Literal replacement only. Terms cannot contain braces, and every safe
        # template contains each positional placeholder exactly once in order.
        text = self.predicates[predicate]
        for index, term in enumerate(terms):
            text = text.replace("{" + str(index) + "}", term)
        return text


def lint_vocabulary(env: Any) -> tuple[VocabularyLint, ...]:
    """Report rejected display metadata in stable path/code order.

    Missing metadata is supported strict fallback, not a lint failure. Even an
    empty report is not evidence that English phrases match their declarations.
    """
    return _NaturalVocabulary(env).issues


def _check_view(view: str) -> None:
    if view not in VIEWS:
        raise ValueError(f"view must be one of {VIEWS}")


def render_vocabulary(env: Any, view: str = "ve_strict") -> str:
    """Return the identical, deterministic identity/argument-order legend in every view.

    Raw metadata is JSON-quoted data. Both declared and selected templates are
    shown so a judge can inspect rejected metadata as well as the actual display.
    """
    _check_view(view)
    selected = _NaturalVocabulary(env)
    legend = {
        "format": "ve.vocabulary-legend@1", "environment_id": env.environment_id,
        "sorts": [{"identifier": name, "description": s.description,
                   "verbalisation": None if s.verbalisation is None else {
                       "singular": s.verbalisation.singular, "plural": s.verbalisation.plural},
                   "rendered_noun": selected.sorts[name]}
                  for name, s in sorted(env.sorts.items())],
        "predicates": [{"identifier": name, "arguments": list(p.arguments),
                        "description": p.description, "verbalisation": p.verbalisation,
                        "rendered_template": selected.predicates[name]}
                       for name, p in sorted(env.predicates.items())],
        "constants": [{"identifier": name, "sort": c.sort, "description": c.description}
                      for name, c in sorted(env.constants.items())],
        "lint": [issue.to_dict() for issue in selected.issues],
    }
    return json.dumps(legend, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


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
    """Render a checked AST with shared binder and operand preorder.

    A formula has no final punctuation; documents have a period and LF for each
    statement. All views preserve lexical case without sentence capitalization.
    The counter resets per statement. No view rewrites or normalizes the AST.
    """
    _check_view(view)

    def render_one(formula):
        if view == "ve_fluent":
            from .fluent import FluentTraversal
            return FluentTraversal(env).formula(formula)
        return _Traversal(env, view).formula(formula, ())

    if isinstance(value, ast.Document):
        ast.check_document(env, value)
        lines = []
        for formula in value.formulas:
            line = render_one(formula)
            lines.append(line + ".\n")
        text = "".join(lines)
    else:
        ast.check_formula(env, value)
        text = render_one(value)
    limit = MAX_SOURCE_BYTES
    if len(text.encode("utf-8")) + (0 if isinstance(value, ast.Document) else 2) > limit:
        raise ResourceLimit(f"Rendered {view} text exceeds its {limit}-byte limit")
    return text


def measure_view_lengths(items: Iterable[ast.Document | ast.Formula], env: Any, *,
                         include_vocabulary: bool = False) -> list[dict[str, Any]]:
    r"""Measure each item/view's Unicode characters and word-or-symbol tokens.

    The Unicode regex ``\w+|[^\w\s]`` treats each non-whitespace punctuation or
    logic symbol as one token. These are reproducible covariates, not model/BPE
    token counts. Optional legend bytes are exactly those shown to every judge.
    """
    legend = render_vocabulary(env) if include_vocabulary else ""
    rows = []
    for index, item in enumerate(items):
        for view in VIEWS:
            text = legend + render(item, env, view)
            rows.append({"item_index": index, "view": view, "characters": len(text),
                         "tokenish": len(re.findall(r"\w+|[^\w\s]", text)),
                         "includes_vocabulary": include_vocabulary})
    return rows


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
    return NaturalView(render(formula, env, "ve_natural"), env.environment_id,
                       meaning_id(env, formula))
