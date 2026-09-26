"""Deterministic, read-only surfaces of one checked AST."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import product
import json
from pathlib import Path
import re
from typing import Any, Iterable
import unicodedata

from . import ast
from .errors import ResourceLimit
from .limits import MAX_NODES, MAX_SOURCE_BYTES

VIEWS = ("fol_symbols", "fol_keywords", "ve_strict", "ve_explicit", "ve_fluent")
# VIEWS is the frozen five-view experimental comparison cohort.
RENDERING_VIEWS = (*VIEWS, "ve_natural", "ve_english")
NATURAL_RENDERER = "ve.natural-audited"
NATURAL_RENDERER_VERSION = "3"
NAMING_POLICIES = ("per_statement", "per_document")
LEGEND_STYLES = ("compact", "json")

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
    "ve_explicit": {
        ast.Top: "true", ast.Bottom: "false", ast.Eq: "{left} is equal to {right}",
        ast.Not: "it is not the case that {body}", ast.And: "{left} and {right}",
        ast.Or: "{left} or {right}, or both", ast.Implies: "if {left}, then {right}",
        ast.Forall: "for every {sort} {name}: {body}",
        ast.Exists: "there is a {sort} {name} such that {body}",
    },
}

# order@0 arithmetic terms (frozen canonical forms, see docs/spec/order-implementation.md):
# numerals are canonical decimals (a leading minus is part of the numeral);
# Scale(-1, t) prints as -t unless t is a numeral; Add(t, Scale(-1, u)) prints
# as [t - u]; every other sum or scaling is bracketed. No term is normalised.
_COMPARISONS = {
    "fol_symbols": ("{left} < {right}", "{left} ≤ {right}"),
    "fol_keywords": ("{left} < {right}", "{left} <= {right}"),
    "ve_strict": ("{left} < {right}", "{left} <= {right}"),
    "ve_explicit": ("{left} is less than {right}", "{left} is at most {right}"),
}


def render_int_term(value, leaf, brackets="[]"):
    """Render an order@0 term; ``leaf`` renders variables and constants."""
    open_, close = brackets
    kind = type(value)
    if kind is ast.Num:
        return str(value.value)
    if kind is ast.Scale:
        if value.coefficient == -1 and type(value.term) is not ast.Num:
            return "-" + render_int_term(value.term, leaf, brackets)
        return f"{open_}{value.coefficient} * {render_int_term(value.term, leaf, brackets)}{close}"
    if kind is ast.Add:
        left = render_int_term(value.left, leaf, brackets)
        if type(value.right) is ast.Scale and value.right.coefficient == -1:
            return f"{open_}{left} - {render_int_term(value.right.term, leaf, brackets)}{close}"
        return f"{open_}{left} + {render_int_term(value.right, leaf, brackets)}{close}"
    return leaf(value)


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
    eight nine ten a an the lacks nothing nobody everything everybody just solely
    many several another but plus few might""".split())
_AUXILIARIES = frozenset("is are was were be been being gets got".split())
_CONVERSE_ENDINGS = frozenset("by to of from with for".split())
_TOKENS = re.compile(r"[A-Za-z][A-Za-z0-9_]*(?:-[A-Za-z]+)?", re.ASCII)
_VARIABLE = re.compile(r"(?:x[0-9]*|[A-Z]+[0-9]*)\Z", re.ASCII)
MAX_TEMPLATE_CHARS = 80
MAX_TEMPLATE_WORDS = 8

# Exceptions to regular third-person spelling, including ambiguous -es/-ies.
# This is a lexical convention, not proof of an English verb's meaning.
_IRREGULAR_VERBS = {
    "has": "have", "does": "do", "goes": "go", "says": "say",
    "dies": "die", "lies": "lie", "ties": "tie", "unties": "untie", "vies": "vie",
    "quizzes": "quiz", "gases": "gas", "biases": "bias",
    "buses": "bus", "focuses": "focus", "echoes": "echo", "vetoes": "veto",
    "aches": "ache", "caches": "cache", "niches": "niche", "axes": "axe",
    "shoes": "shoe", "toes": "toe", "tiptoes": "tiptoe",
}


def _negative_template(positive: str, arity: int) -> str | None:
    """Mechanically negate an already accepted positive lexical template."""
    if arity == 1:
        return positive.replace("{0} is ", "{0} is not ", 1)
    words = positive.split()
    verb = words[1]
    if verb in _IRREGULAR_VERBS:
        base = _IRREGULAR_VERBS[verb]
    elif len(verb) > 3 and verb.endswith("ies") and verb[-4] not in "aeiou":
        base = verb[:-3] + "y"
    elif verb.endswith(("ches", "shes", "sses", "xes", "zzes")):
        base = verb[:-2]
    elif len(verb) > 2 and verb.endswith("s") and not verb.endswith(("ss", "us", "is", "ous", "oes")):
        base = verb[:-1]
    else:
        return None
    return "{0} does not " + base + " " + " ".join(words[2:])


def _fluent_variable_letters(sorts, env):
    """Stable distinct letters; digits only count occurrences, never encode sorts.

    More than 23 sorts (or reserved identifiers) can exhaust single letters.
    In that case use alphabetic codes BB, BC, ... in the same fixed order.
    Avoid case-insensitive identifier collisions, including suffixed names.
    """
    alphabet = "BCDEFGHJKLMNPQRSTUVWXYZ"
    reserved = {re.sub(r"[0-9]+$", "", name.upper())
                for declarations in (env.sorts, env.predicates, env.constants)
                for name in declarations}
    used = set(reserved)
    result = {}
    for sort, noun in sorted(sorts.items()):
        candidates = [noun[0].upper()]
        candidates += [letter for letter in noun.upper() if letter in alphabet and letter not in "EU"]
        candidates += list(alphabet)
        letter = next((c for c in candidates if c in alphabet and c not in used), None)
        width = 2
        while letter is None:
            letter = next(("".join(code) for code in product(alphabet, repeat=width)
                           if "".join(code) not in used), None)
            width += 1
        result[sort] = letter
        used.add(letter)
    return result


@dataclass(frozen=True, slots=True)
class VocabularyLint:
    """A stable diagnostic code at a vocabulary JSON path; rendering falls back."""
    path: str
    code: str

    def to_dict(self) -> dict[str, Any]:
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

        def template_checks(value, path):
            # Placeholders count as words, and all template characters count.
            if len(value) > MAX_TEMPLATE_CHARS or len(value.split()) > MAX_TEMPLATE_WORDS:
                report(path, "TEMPLATE_LENGTH")
            words = _TOKENS.findall(value)
            for noun in nouns:
                tokens = _TOKENS.findall(noun)
                if tokens and any(words[i:i + len(tokens)] == tokens
                                  for i in range(len(words) - len(tokens) + 1)):
                    report(path, "SORT_NOUN")

        def phrase_checks(name, phrase, path):
            words = _TOKENS.findall(phrase)
            if not _WORDS.fullmatch(phrase):
                report(path, "PHRASE_SYNTAX")
            if (_LOGICAL_WORDS | (frozenset("reachable reachability steps satisfying zero more from".split()) if env.closure else frozenset())).intersection(words):
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
        accepted = set()
        for name, p in env.predicates.items():
            value = p.verbalisation
            self.predicates[name] = strict[name]
            if value is None:
                continue
            path = f"/vocabulary/predicates/{name}/verbalisation"
            before = len(issues)
            template_checks(value, path)
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
                accepted.add(name)

        self.negatives = {}
        for name, p in env.predicates.items():
            value = p.negative_verbalisation
            if value is None:
                continue
            path = f"/vocabulary/predicates/{name}/negative_verbalisation"
            before = len(issues)
            template_checks(value, path)
            if name not in accepted:
                report(path, "NEGATIVE_WITHOUT_POSITIVE")
            elif value != _negative_template(self.predicates[name], len(p.arguments)):
                report(path, "NEGATIVE_NOT_NEGATION")
            if len(issues) == before:
                self.negatives[name] = value

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

    def atom(self, predicate, terms, *, negative=False):
        # Literal replacement only. Terms cannot contain braces, and every safe
        # template contains each positional placeholder exactly once in order.
        text = (self.negatives if negative else self.predicates)[predicate]
        for index, term in enumerate(terms):
            text = text.replace("{" + str(index) + "}", term)
        return text


def lint_vocabulary(env: Any, *, surface: str = "strict") -> tuple[VocabularyLint, ...]:
    """Report rejected display metadata in stable path/code order.

    Missing metadata is supported strict fallback, not a lint failure. Even an
    empty report is not evidence that English phrases match their declarations.
    """
    if surface == "english":
        from .english import lint_english_vocabulary
        return lint_english_vocabulary(env)
    if surface != "strict":
        raise ValueError("surface must be strict or english")
    return _NaturalVocabulary(env).issues


def _check_view(view: str) -> None:
    if view not in RENDERING_VIEWS:
        raise ValueError(f"view must be one of {RENDERING_VIEWS}")


def _check_naming(naming: str) -> None:
    if naming not in NAMING_POLICIES:
        raise ValueError(f"naming must be one of {NAMING_POLICIES}")


def _check_legend_style(style: str) -> None:
    if style not in LEGEND_STYLES:
        raise ValueError(f"style must be one of {LEGEND_STYLES}")


def _legend_quote(value: str) -> str:
    """Quote data on one physical/display line, including Unicode controls.

    JSON already escapes quotes, backslashes and C0 controls. Escape C1,
    bidi/format controls and Unicode line/paragraph separators as well, so raw
    rejected metadata and descriptions cannot forge or reorder legend lines.
    """
    return "".join(json.dumps(char, ensure_ascii=True)[1:-1]
                   if unicodedata.category(char) in ("Cc", "Cf", "Zl", "Zp") else char
                   for char in json.dumps(value, ensure_ascii=False))


def _compact_vocabulary(legend: dict[str, Any]) -> str:
    """Present the same legend fields without JSON keys or repeated metadata."""
    quote = _legend_quote
    lines = [f"Vocabulary: {legend['format']}; environment: {legend['environment_id']}"]
    lines.append("Sorts:" if legend["sorts"] else "Sorts: none")
    for entry in legend["sorts"]:
        raw, noun = entry["verbalisation"], entry["rendered_noun"]
        nouns = quote(noun)
        if raw is None:
            nouns += "; declared: none"
        elif raw["singular"] == noun:
            nouns += "/" + quote(raw["plural"])
        else:
            nouns += f"; declared: {quote(raw['singular'])}/{quote(raw['plural'])}"
        lines.append(f"  {entry['identifier']} (noun: {nouns}) — {quote(entry['description'])}")
    lines.append("Constants:" if legend["constants"] else "Constants: none")
    for entry in legend["constants"]:
        lines.append(f"  @{entry['identifier']} : {entry['sort']} — {quote(entry['description'])}")
    lines.append("Predicates:" if legend["predicates"] else "Predicates: none")
    for entry in legend["predicates"]:
        template = quote(entry["rendered_template"])
        raw = entry["verbalisation"]
        if raw != entry["rendered_template"]:
            template += f" (strict fallback; declared: {quote(raw) if raw is not None else 'none'})"
        line = (f"  {entry['identifier']}({', '.join(entry['arguments'])}) — "
                f"{template} — {quote(entry['description'])}")
        negative, raw_negative = entry["rendered_negative_template"], entry["negative_verbalisation"]
        if negative is not None or raw_negative is not None:
            line += "; negative: " + (quote(negative) if negative is not None else "none")
            if raw_negative != negative:
                line += f" (declared: {quote(raw_negative)})"
        lines.append(line)
    fluent = legend["fluent_variables"]
    letters = ", ".join(f"{sort} = {letter}" for sort, letter in fluent["letters_by_sort"].items())
    lines.append("Fluent variable letters: " + (letters or "none"))
    lines.append("Fluent variable rule: " + fluent["rule"])
    lines.append(f"Naming: {legend['naming']} — {legend['naming_rule']}")
    lines.append("Lint:" if legend["lint"] else "Lint: none")
    for issue in legend["lint"]:
        lines.append(f"  {issue['path']}: {issue['code']}")
    if "closure" in legend:
        closure = legend["closure"]
        lines.append("Closure: " + closure["profile"])
        for kind, meaning in closure["kinds"].items():
            lines.append(f"  {kind}: {meaning}")
        for field in ("direction", "body", "cycles"):
            lines.append(f"  {field}: {closure[field]}")
        lines.append("  relations: " + (", ".join(closure["relations"]) or "none"))
    return "\n".join(lines) + "\n"


def render_vocabulary(env: Any, view: str = "ve_strict", naming: str = "per_statement",
                      style: str = "json", *, vocabulary=None, accept_suggested_vocabulary=False) -> str:
    """Return the identical, deterministic identity/argument-order legend in every view.

    JSON is the unchanged default; compact uses one line per entry. Both styles
    quote raw metadata and preserve declared and selected templates, so a judge
    can inspect rejected metadata as well as the actual display.
    """
    _check_view(view)
    _check_naming(naming)
    _check_legend_style(style)
    if view in ("ve_english", "ve_natural"):
        from .english import english_legend
        return english_legend(env, style, vocabulary=vocabulary, accept_suggested_vocabulary=accept_suggested_vocabulary)
    selected = _NaturalVocabulary(env)
    legend = {
        "format": "ve.vocabulary-legend@3", "environment_id": env.environment_id,
        "naming": naming,
        "fluent_variables": {
            "letters_by_sort": _fluent_variable_letters(selected.sorts, env),
            "rule": "Distinct sort letters exclude A/I/O and declared identifiers (case-insensitive). "
                    "Choose the noun initial, then its unused consonants, then BCDEFGHJKLMNPQRSTUVWXYZ; "
                    "on exhaustion use alphabetic codes BB, BC, ... . Within the naming scope, "
                    "each sort's named binders use suffixes 1, 2, ... in preorder; omit 1. "
                    "Constants have @; lexical words are lowercase.",
        },
        "naming_rule": "Allocate binders in preorder. " + (
            "Restart names in each statement." if naming == "per_statement" else
            "Continue numbering across statements in the document; reset for each render call."),
        "sorts": [{"identifier": name, "description": s.description,
                   "verbalisation": None if s.verbalisation is None else {
                       "singular": s.verbalisation.singular, "plural": s.verbalisation.plural},
                   "rendered_noun": selected.sorts[name]}
                  for name, s in sorted(env.sorts.items())],
        "predicates": [{"identifier": name, "arguments": list(p.arguments),
                        "description": p.description, "verbalisation": p.verbalisation,
                        "rendered_template": selected.predicates[name],
                        "negative_verbalisation": p.negative_verbalisation,
                        "rendered_negative_template": selected.negatives.get(name)}
                       for name, p in sorted(env.predicates.items())],
        "constants": [{"identifier": name, "sort": c.sort, "description": c.description}
                      for name, c in sorted(env.constants.items())],
        "lint": [issue.to_dict() for issue in selected.issues],
    }
    if env.closure:
        legend["closure"] = {
            "profile": "closure@0", "kinds": {"tc": "one or more steps", "rtc": "zero or more steps"},
            "direction": "u is reachable from t means a directed path from source t to destination u.",
            "body": "[s a, b | (body)] defines a step from a to b; outer parameters stay fixed. Both locals are always named.",
            "relations": [name for name, p in sorted(env.predicates.items())
                          if len(p.arguments) == 2 and p.arguments[0] == p.arguments[1]],
            "cycles": "Positive closure can contain (a,a) on a cycle; zero steps require star.",
        }
    if style == "compact":
        return _compact_vocabulary(legend)
    return json.dumps(legend, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


class _Traversal:
    def __init__(self, env, view):
        self.next_name = 0
        self.view = view
        self.surface = _SURFACES[view]
        self.natural = _NaturalVocabulary(env) if view == "ve_explicit" else None

    def term(self, value, scope):
        def leaf(value):
            if isinstance(value, ast.Var):
                return scope[value.index]
            return "@" + value.name
        return render_int_term(value, leaf, "()" if self.view.startswith("fol_") else "[]")

    def child(self, value, scope):
        # Every immediate operand is grouped in the four explicit views, even atoms.
        # Predicate application parentheses in FOL are lexical argument lists.
        return "(" + self.formula(value, scope) + ")"

    def formula(self, value, scope):
        kind = type(value)
        from .surface.registry import by_node
        record = by_node(value)
        if record is not None and record.printer_hook is not None:
            return record.printer_hook(self, value, scope)
        fields = {}
        if kind is ast.Reach:
            left, right = self.term(value.left, scope), self.term(value.right, scope)
            op = "tc" if value.kind == "plus" else "rtc"
            count = "one or more" if value.kind == "plus" else "zero or more"
            if type(value.edge) is ast.Named:
                relation = value.edge.relation
                if self.view == "fol_symbols":
                    return f"{relation}{'⁺' if value.kind == 'plus' else '*'}({left}, {right})"
                if self.view == "ve_explicit":
                    return f"{right} is reachable from {left} by {count} {relation} steps"
                return f"{op}[{relation}]({left}, {right})"
            src, dst = f"x{self.next_name}", f"x{self.next_name + 1}"
            self.next_name += 2
            body = self.formula(value.edge.formula, (dst, src, *scope))
            sort = value.edge.sort
            if self.view == "fol_symbols":
                return f"({op.upper()} {src}:{sort},{dst}:{sort}.({body}))({left}, {right})"
            if self.view == "ve_explicit":
                noun = self.natural.sorts[sort]
                return f"{right} is reachable from {left} by {count} steps satisfying [{noun} {src}, {dst} | ({body})]"
            return f"{op}[{sort} {src}, {dst} | ({body})]({left}, {right})"
        if kind in (ast.Lt, ast.Le):
            template = _COMPARISONS[self.view][kind is ast.Le]
            return template.format(left=self.term(value.left, scope), right=self.term(value.right, scope))
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


def render(value: ast.Document | ast.Formula, env: Any, view: str = "ve_strict",
           naming: str = "per_statement", *, vocabulary=None, accept_suggested_vocabulary=False,
           conclusions=(), conclusion_marker="Therefore", paragraph_breaks=()) -> str:
    """Render a checked AST in the selected display surface.

    A formula has no final punctuation. Natural documents join sentences into
    paragraphs; the historical views retain their line-oriented format.
    The historical views preserve lexical case without sentence capitalization.
    All views use the selected naming scope, defaulting to per-statement resets.
    No view changes the checked AST.
    """
    _check_view(view)
    _check_naming(naming)
    if view == "ve_natural":
        from .natural import render_natural_sentence
        if isinstance(value, ast.Document):
            return natural_document(env, value, vocabulary=vocabulary,
                                    accept_suggested_vocabulary=accept_suggested_vocabulary,
                                    conclusions=conclusions, conclusion_marker=conclusion_marker,
                                    paragraph_breaks=paragraph_breaks).text
        else:
            if conclusions or paragraph_breaks:
                raise ValueError('Conclusion roles and paragraph breaks require a document')
            ast.check_formula(env, value)
            text = render_natural_sentence(value, env, vocabulary=vocabulary,
                   accept_suggested_vocabulary=accept_suggested_vocabulary).text
        if len(text.encode('utf-8')) + (0 if isinstance(value, ast.Document) else 2) > MAX_SOURCE_BYTES:
            raise ResourceLimit(f'Rendered {view} text exceeds its {MAX_SOURCE_BYTES}-byte limit')
        if isinstance(value, ast.Document) and len(text) > MAX_NODES:
            raise ResourceLimit(f'Rendered {view} text exceeds the English derivation budget MAX_NODES ({MAX_NODES})')
        if isinstance(value, ast.Document):
            from .english import parse_english
            if parse_english(env, text, vocabulary=vocabulary,
                             accept_suggested_vocabulary=accept_suggested_vocabulary) != value:
                raise ValueError('Rendered ve_natural document has a different reading')
        return text
    if conclusions or paragraph_breaks:
        raise ValueError('Conclusion roles and paragraph breaks require the natural view')
    if view == "ve_english":
        from .english import render_english
        return render_english(value, env, vocabulary=vocabulary, accept_suggested_vocabulary=accept_suggested_vocabulary)
    if view == "ve_fluent":
        from .fluent import FluentTraversal
        traversal = FluentTraversal(env)
    else:
        traversal = _Traversal(env, view)

    def render_one(formula):
        if naming == "per_statement":
            if view == "ve_fluent":
                traversal.names.clear()
            else:
                traversal.next_name = 0
        return traversal.formula(formula, ())

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


def render_cell(value: ast.Document | ast.Formula, env: Any, view: str = "ve_strict",
                naming: str = "per_statement", style: str = "json", **options) -> str:
    """Render an experimental cell, ALWAYS including the identical view legend."""
    return render_vocabulary(env, view, naming, style, **options) + render(value, env, view, naming, **options)


def measure_view_lengths(items: Iterable[ast.Document | ast.Formula], env: Any, *,
                         include_vocabulary: bool = False,
                         naming: str = "per_statement", style: str = "json") -> list[dict[str, Any]]:
    r"""Measure each item/view's Unicode characters and word-or-symbol tokens.

    The Unicode regex ``\w+|[^\w\s]`` treats each non-whitespace punctuation or
    logic symbol as one token. These are reproducible covariates, not model/BPE
    token counts. Optional legend bytes are exactly those shown to every judge.
    """
    _check_naming(naming)
    _check_legend_style(style)
    legend = render_vocabulary(env, naming=naming, style=style) if include_vocabulary else ""
    rows = []
    for index, item in enumerate(items):
        for view in VIEWS:
            text = legend + render(item, env, view, naming)
            rows.append({"item_index": index, "view": view, "characters": len(text),
                         "tokenish": len(re.findall(r"\w+|[^\w\s]", text)),
                         "includes_vocabulary": include_vocabulary})
    return rows


def measure_jsonl_lengths(path: str | Path, env: Any, *, field: str = "ast",
                          source_format: str = "ast", include_vocabulary: bool = True,
                          naming: str = "per_statement", style: str = "json") -> list[dict[str, Any]]:
    """Measure actual JSONL records, preserving source line and optional item ID.

    Select a top-level field containing a tagged formula/document AST, or strict
    VE text with source_format='ve'. No invalid record is silently dropped.
    The environment must match the file; a present environment_id is checked.
    """
    from .parser import parse
    from .wire import _pairs, _invalid_number
    from .limits import MAX_PACKAGE_BYTES
    _check_naming(naming)
    _check_legend_style(style)
    if source_format not in ("ast", "ve"):
        raise ValueError("source_format must be ast or ve")
    rows = []
    with Path(path).open("rb") as stream:
        line_number = 0
        while line := stream.readline(MAX_PACKAGE_BYTES + 1):
            line_number += 1
            if len(line) > MAX_PACKAGE_BYTES:
                raise ResourceLimit(f"JSONL line {line_number} exceeds {MAX_PACKAGE_BYTES} bytes")
            # Item envelopes may contain ordinary JSON metadata (null/floats).
            # Only the selected AST/source field is subject to VE's wire rules.
            try:
                record = json.loads(line, object_pairs_hook=_pairs, parse_constant=_invalid_number)
            except RecursionError as exc:
                raise ResourceLimit(f"JSONL line {line_number} exceeds the nesting limit") from exc
            if not isinstance(record, dict) or field not in record:
                raise ValueError(f"JSONL line {line_number} requires field {field!r}")
            if record.get("environment_id", env.environment_id) != env.environment_id:
                raise ValueError(f"JSONL line {line_number} has a different environment_id")
            value = record[field]
            if source_format == "ve":
                item = parse(env, value)
            elif isinstance(value, list) and value and isinstance(value[0], str):
                item = ast.formula_from_data(env, value)
            else:
                item = ast.document_from_data(env, value)
            for row in measure_view_lengths([item], env, include_vocabulary=include_vocabulary,
                                            naming=naming, style=style):
                row.update(item_index=line_number - 1, line=line_number)
                if "id" in record:
                    row["item_id"] = record["id"]
                rows.append(row)
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
    sentences: tuple[dict[str, str | None], ...] = ()
    paragraphs: tuple[dict[str, int], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text, "sentences": list(self.sentences),
                "paragraphs": list(self.paragraphs),
                "environment_id": self.environment_id,
                "meaning_id": self.meaning_id, "renderer": self.renderer,
                "version": self.version}


def natural_document(env: Any, document: ast.Document, *, naming: str = "per_statement",
                     vocabulary=None, accept_suggested_vocabulary=False,
                     conclusions=(), conclusion_marker="Therefore",
                     paragraph_breaks=()) -> NaturalView:
    """Render a validated read-only view with explicit scope and dependencies."""
    ast.check_document(env, document)
    from .identity import meaning_id
    from .natural import render_natural_sentence
    results = tuple(render_natural_sentence(formula, env, vocabulary=vocabulary,
                    accept_suggested_vocabulary=accept_suggested_vocabulary)
                    for formula in document.formulas)
    conclusions = tuple(conclusions)
    if len(set(conclusions)) != len(conclusions) or any(type(i) is not int or not 0 <= i < len(results)
                                                      for i in conclusions):
        raise ValueError('Conclusion indices must identify distinct document statements')
    if conclusion_marker not in ('Therefore', 'So', 'Hence', 'It follows that'):
        raise ValueError('Unsupported conclusion marker')
    paragraph_breaks = tuple(paragraph_breaks)
    if (len(set(paragraph_breaks)) != len(paragraph_breaks)
            or any(type(i) is not int or not 0 < i < len(results) for i in paragraph_breaks)):
        raise ValueError('Paragraph breaks must identify distinct interior sentence boundaries')
    breaks = set(paragraph_breaks)
    marked = set(conclusions)
    display_texts = [result.text for result in results]
    from .english import EnglishVocabulary, _mentioned_constants
    names = EnglishVocabulary(env, vocabulary=vocabulary,
                              accept_suggested_vocabulary=accept_suggested_vocabulary).constants
    referents = set()
    for i, formula in enumerate(document.formulas):
        if (i not in marked and len(referents) == 1 and results[i].natural
                and type(formula) is ast.Unary and type(formula.term) is ast.Const
                and formula.term.name in referents):
            head = names[formula.term.name]
            head = head[0].upper() + head[1:]
            if display_texts[i].startswith(head + ' '):
                display_texts[i] = 'It' + display_texts[i][len(head):]
        referents.update(_mentioned_constants(formula))
    def clause(result, index):
        wording = display_texts[index]
        if index not in marked:
            return wording
        tail = wording
        if tail.startswith('The ') or tail.split(' ', 1)[0] in {
                'Every', 'Some', 'No', 'For', 'There', 'It', 'If', 'Both',
                'Either', 'Starting', 'All', 'At', 'This'}:
            tail = tail[0].lower() + tail[1:]
        return conclusion_marker + ' ' + tail
    def prose_text():
        return ''.join(('\n\n' if i in breaks else ' ' if i else '') + clause(result, i) + '.'
                       for i, result in enumerate(results))
    text = prose_text()
    if len(text.encode('utf-8')) > MAX_SOURCE_BYTES:
        raise ResourceLimit(f'Rendered ve_natural text exceeds its {MAX_SOURCE_BYTES}-byte limit')
    if len(text) > MAX_NODES:
        raise ResourceLimit(f'Rendered ve_natural text exceeds the English derivation budget MAX_NODES ({MAX_NODES})')
    from .english import _parse_english_document
    try:
        parsed, _, _, parsed_conclusions = _parse_english_document(
            env, text, vocabulary=vocabulary,
            accept_suggested_vocabulary=accept_suggested_vocabulary)
    except Exception:
        if display_texts == [result.text for result in results]:
            raise
        display_texts = [result.text for result in results]
        text = prose_text()
        parsed, _, _, parsed_conclusions = _parse_english_document(
            env, text, vocabulary=vocabulary,
            accept_suggested_vocabulary=accept_suggested_vocabulary)
    if parsed != document or parsed_conclusions != tuple(i for i in range(len(results)) if i in marked):
        raise ValueError('Rendered ve_natural document has a different reading')
    starts = (0, *sorted(breaks))
    ends = (*sorted(breaks), len(results))
    return NaturalView(text, env.environment_id, meaning_id(env, document),
                       sentences=tuple({'text': display_texts[i], 'form': result.form,
                                        'fallback_reason': result.reason,
                                        'role': 'conclusion' if i in marked else 'premise'}
                                       for i, result in enumerate(results)),
                       paragraphs=tuple({'start': start, 'end': end}
                                        for start, end in zip(starts, ends)))


def natural_formula(env: Any, formula: Any, *, naming: str = "per_statement",
                    vocabulary=None, accept_suggested_vocabulary=False) -> NaturalView:
    ast.check_formula(env, formula)
    from .identity import meaning_id
    from .natural import render_natural_sentence
    result = render_natural_sentence(formula, env, vocabulary=vocabulary,
                                     accept_suggested_vocabulary=accept_suggested_vocabulary)
    if len(result.text.encode('utf-8')) + 2 > MAX_SOURCE_BYTES:
        raise ResourceLimit(f'Rendered ve_natural text exceeds its {MAX_SOURCE_BYTES}-byte limit')
    return NaturalView(result.text, env.environment_id, meaning_id(env, formula),
                       sentences=({'text': result.text, 'form': result.form,
                                   'fallback_reason': result.reason, 'role': 'premise'},),
                       paragraphs=({'start': 0, 'end': 1},))
