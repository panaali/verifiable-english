"""Read-only English surface: explicit scope, reversible local contractions.

The four fully parenthesized views live in printer.py. This visitor follows the
same binder/operand preorder, but uses a prefix grammar and groups only complex
operands. It never normalizes, reassociates, or exchanges AST nodes.
"""
from collections import Counter

from . import ast
from .printer import _NaturalVocabulary, _fluent_variable_sequences


FLUENT_RENDERER = "ve.fluent"
FLUENT_RENDERER_VERSION = "2"


# Every view's legend and both English visitors use exactly one lexical policy.
_FluentVocabulary = _NaturalVocabulary


def _references(value, index=0):
    """Occurrences of one binder, including under intervening binders."""
    kind = type(value)
    if kind is ast.Unary:
        return int(value.term == ast.Var(index))
    if kind in (ast.Binary, ast.Eq):
        return int(value.left == ast.Var(index)) + int(value.right == ast.Var(index))
    if kind is ast.Not:
        return _references(value.body, index)
    if kind in (ast.And, ast.Or, ast.Implies):
        return _references(value.left, index) + _references(value.right, index)
    if kind in (ast.Forall, ast.Exists):
        return _references(value.body, index + 1)
    return 0


def _guard(value):
    """A tree of conjunctive literals, each mentioning the innermost binder."""
    if type(value) is ast.And:
        return _guard(value.left) and _guard(value.right)
    if type(value) is ast.Not:
        value = value.body
    return type(value) in (ast.Unary, ast.Binary, ast.Eq) and _references(value) > 0


class FluentTraversal:
    def __init__(self, env):
        self.env = env
        self.words = _FluentVocabulary(env)
        self.names = Counter()
        self.sequences = _fluent_variable_sequences(self.words.sorts)

    def binder(self, value):
        noun = self.words.sorts[value.sort]
        name = None
        # A declaration is the first mention. A body reference is a subsequent
        # mention; vacuous binders alone can omit their names in global syntax.
        if _references(value.body):
            sequence = self.sequences[value.sort]
            count = sequence["first_suffix"] + self.names[value.sort] * sequence["stride"]
            self.names[value.sort] += 1
            name = sequence["letter"] + (str(count) if count > 1 else "")
        return (name, value.sort), noun + (" " + name if name else "")

    @staticmethod
    def term(value, scope):
        if type(value) is ast.Var:
            name = scope[value.index][0]
            assert name is not None
            return name
        return "@" + value.name

    def equality(self, value, scope, negative=False):
        sort = (scope[value.left.index][1] if type(value.left) is ast.Var
                else self.env.constants[value.left.name].sort)
        return (self.term(value.left, scope) + " is " + ("not " if negative else "")
                + "the same " + self.words.sorts[sort] + " as " + self.term(value.right, scope))

    def unit(self, value, scope):
        text = self.formula(value, scope)
        if type(value) in (ast.Top, ast.Bottom, ast.Unary, ast.Binary, ast.Eq):
            return text
        if self.negative_atom(value):
            return text
        return "(" + text + ")"

    def relative(self, value, scope):
        """Only delete a literal's subject when it is exactly the guard binder."""
        atom = value.body if type(value) is ast.Not else value
        if type(atom) not in (ast.Unary, ast.Binary, ast.Eq):
            return None
        subject = atom.term if type(atom) is ast.Unary else atom.left
        if subject != ast.Var(0):
            return None
        if type(value) is ast.Not and not self.negative_atom(value):
            return None
        if type(atom) in (ast.Unary, ast.Binary):
            # Formal fallback names need not be grammatical relative verbs.
            declaration = self.env.predicates[atom.predicate]
            if self.words.predicates[atom.predicate] != declaration.verbalisation:
                return None
        text = self.formula(value, scope)
        return "that " + text[len(scope[0][0]) + 1:]

    def guard(self, value, scope):
        relative = self.relative(value, scope)
        if relative is not None:
            return relative
        if type(value) is ast.And:
            left, right = self.relative(value.left, scope), self.relative(value.right, scope)
            if left is not None and right is not None:
                return left + " and " + right
        return "such that " + self.unit(value, scope)

    def negative_atom(self, value):
        return (type(value) is ast.Not and
                (type(value.body) is ast.Eq or
                 (type(value.body) in (ast.Unary, ast.Binary) and
                  value.body.predicate in self.words.negatives)))

    def formula(self, value, scope=()):
        kind = type(value)
        if kind is ast.Top:
            return "true"
        if kind is ast.Bottom:
            return "false"
        if kind in (ast.Unary, ast.Binary):
            terms = (value.term,) if kind is ast.Unary else (value.left, value.right)
            return self.words.atom(value.predicate, tuple(self.term(t, scope) for t in terms))
        if kind is ast.Eq:
            return self.equality(value, scope)
        if kind is ast.Not:
            if type(value.body) is ast.Eq:
                return self.equality(value.body, scope, negative=True)
            if self.negative_atom(value):
                atom = value.body
                terms = (atom.term,) if type(atom) is ast.Unary else (atom.left, atom.right)
                return self.words.atom(atom.predicate, tuple(self.term(t, scope) for t in terms),
                                       negative=True)
            return "it is false that " + self.unit(value.body, scope)
        if kind in (ast.And, ast.Or, ast.Implies):
            left, right = self.unit(value.left, scope), self.unit(value.right, scope)
            if kind is ast.And:
                return "both " + left + " and " + right
            if kind is ast.Or:
                return "either " + left + " or " + right + ", or both"
            return "if " + left + " then " + right
        if kind is ast.Exists:
            binding, declaration = self.binder(value)
            article = "an" if declaration[0] in "aeiou" else "a"
            return ("there is " + article + " " + declaration + " such that "
                    + self.formula(value.body, (binding, *scope)))
        if kind is ast.Forall:
            declarations = []
            while type(value) is ast.Forall:
                binding, declaration = self.binder(value)
                declarations.append(declaration)
                scope = (binding, *scope)
                value = value.body
            prefix = "for every " + " and every ".join(declarations)
            if (len(declarations) == 1 and type(value) is ast.Implies and _guard(value.left)):
                return (prefix + " " + self.guard(value.left, scope) + ", "
                        + self.formula(value.right, scope))
            return prefix + ", " + self.formula(value, scope)
        raise TypeError("Unknown checked formula constructor")
