"""Test-only recursive-descent inverse, not a new VE source language.

Only the environment's lexical codebook is shared with the renderer. Parsing
does not call render, inspect a source AST, enumerate formulas, or use a cache.
"""
import re

from ve import ast
from ve.fluent import _FluentVocabulary


TERM = r"(?:[A-Z][0-9]*|@[a-z][a-z0-9_]*)"
BOUNDARY = r"(?=$|\)|,| and | or | then )"


class Inverse:
    def __init__(self, env, text):
        self.env = env
        self.words = _FluentVocabulary(env)
        self.text = text
        self.pos = 0
        self.binders = []
        self.nouns = sorted(((noun, sort) for sort, noun in self.words.sorts.items()),
                            key=lambda pair: -len(pair[0]))
        self.atoms = []
        for negative, templates in ((False, self.words.predicates), (True, self.words.negatives)):
            for name, template in templates.items():
                pattern = re.escape(template)
                for i in range(len(env.predicates[name].arguments)):
                    pattern = pattern.replace(re.escape("{" + str(i) + "}"), "(" + TERM + ")")
                self.atoms.append((name, negative, re.compile(pattern + BOUNDARY)))

    def take(self, literal):
        if self.text.startswith(literal, self.pos):
            self.pos += len(literal)
            return True
        return False

    def need(self, literal):
        assert self.take(literal), (literal, self.text[self.pos:])

    def term(self, text, scope):
        if text.startswith("@"):
            assert text[1:] in self.env.constants
            return ast.Const(text[1:])
        return ast.Var(tuple(name for name, _ in scope).index(text))

    def noun(self):
        for noun, sort in self.nouns:
            if self.text.startswith(noun, self.pos):
                end = self.pos + len(noun)
                if end == len(self.text) or self.text[end] in " ,)":
                    self.pos = end
                    return sort
        raise AssertionError(("noun", self.text[self.pos:]))

    def binder(self, kind):
        sort = self.noun()
        match = re.match(r" ([A-Z][0-9]*)(?= |,)", self.text[self.pos:])
        name = None
        if match:
            name = match[1]
            self.pos += match.end()
        self.binders.append((kind, sort, name))
        return name, sort

    def atom(self, scope):
        for word, constructor in (("true", ast.Top), ("false", ast.Bottom)):
            match = re.match(word + BOUNDARY, self.text[self.pos:])
            if match:
                self.pos += match.end()
                return constructor()
        candidates = []
        for name, negative, pattern in self.atoms:
            match = pattern.match(self.text, self.pos)
            if match:
                terms = tuple(self.term(t, scope) for t in match.groups())
                constructor = ast.Unary if len(terms) == 1 else ast.Binary
                atom = constructor(name, *terms)
                candidates.append((match.end(), ast.Not(atom) if negative else atom))
        for noun, sort in self.nouns:
            pattern = ("(" + TERM + r") is (not )?the same " + re.escape(noun)
                       + " as (" + TERM + ")" + BOUNDARY)
            match = re.compile(pattern).match(self.text, self.pos)
            if match:
                left, right = self.term(match[1], scope), self.term(match[3], scope)
                actual = scope[left.index][1] if type(left) is ast.Var else self.env.constants[left.name].sort
                assert actual == sort
                value = ast.Eq(left, right)
                candidates.append((match.end(), ast.Not(value) if match[2] else value))
        assert len(candidates) == 1, (self.text[self.pos:], candidates)
        self.pos, value = candidates[0]
        return value

    def relative(self, scope):
        self.need("that ")
        # Restore the syntactically elided subject, then use the atomic lexer.
        prefix = scope[0][0] + " "
        original, start = self.text, self.pos
        self.text, self.pos = prefix + original[start:], 0
        value = self.atom(scope)
        consumed = self.pos - len(prefix)
        self.text, self.pos = original, start + consumed
        return value

    def unit(self, scope):
        if self.take("("):
            value = self.formula(scope)
            self.need(")")
            return value
        return self.atom(scope)

    def formula(self, scope=()):
        if self.take("for every "):
            declarations = [self.binder(ast.Forall)]
            while self.take(" and every "):
                declarations.append(self.binder(ast.Forall))
            inner = tuple(reversed(declarations)) + scope
            guard = None
            if self.take(" "):
                if self.take("such that "):
                    guard = self.unit(inner)
                else:
                    guard = self.relative(inner)
                    if self.take(" and "):
                        guard = ast.And(guard, self.relative(inner))
            self.need(", ")
            value = self.formula(inner)
            if guard is not None:
                value = ast.Implies(guard, value)
            for _, sort in reversed(declarations):
                value = ast.Forall(sort, value)
            return value
        if self.take("there is "):
            if not self.take("an "):
                self.need("a ")
            binding = self.binder(ast.Exists)
            self.need(" such that ")
            return ast.Exists(binding[1], self.formula((binding, *scope)))
        if self.take("it is false that "):
            return ast.Not(self.unit(scope))
        for prefix, separator, suffix, constructor in (
                ("both ", " and ", "", ast.And),
                ("either ", " or ", ", or both", ast.Or),
                ("if ", " then ", "", ast.Implies)):
            if self.take(prefix):
                left = self.unit(scope)
                self.need(separator)
                right = self.unit(scope)
                self.need(suffix)
                return constructor(left, right)
        return self.atom(scope)

    def parse(self):
        value = self.formula()
        assert self.pos == len(self.text), self.text[self.pos:]
        ast.check_formula(self.env, value)
        return value


def parse_fluent(env, text):
    return Inverse(env, text).parse()
