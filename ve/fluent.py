"""Read-only English surface: explicit scope, reversible local contractions.

The four fully parenthesized views live in printer.py. This visitor follows the
same binder/operand preorder, but uses a prefix grammar and groups only complex
operands. It never normalizes, reassociates, or exchanges AST nodes.
"""
from collections import Counter

from . import ast
from .printer import _NaturalVocabulary, _fluent_variable_letters, _check_naming, render_int_term


FLUENT_RENDERER = "ve.fluent"
FLUENT_RENDERER_VERSION = "3"


# Every view's legend and both English visitors use exactly one lexical policy.
_FluentVocabulary = _NaturalVocabulary


def _references(value, index=0):
    """Occurrences of one binder, including under intervening binders."""
    kind = type(value)
    if kind is ast.Unary:
        return int(value.term == ast.Var(index))
    if kind in (ast.Binary, ast.Eq, ast.Lt, ast.Le):
        return int(value.left == ast.Var(index)) + int(value.right == ast.Var(index))
    if kind is ast.Reach:
        endpoints = int(value.left == ast.Var(index)) + int(value.right == ast.Var(index))
        return endpoints + (_references(value.edge.formula, index + 2) if type(value.edge) is ast.Body else 0)
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
        self.letters = _fluent_variable_letters(self.words.sorts, env)
        self.stats = Counter()

    def binder(self, value):
        noun = self.words.sorts[value.sort]
        name = None
        # A declaration is the first mention. A body reference is a subsequent
        # mention; vacuous binders alone can omit their names in global syntax.
        if _references(value.body):
            self.names[value.sort] += 1
            count = self.names[value.sort]
            name = self.letters[value.sort] + (str(count) if count > 1 else "")
        return (name, value.sort), noun + (" " + name if name else "")

    @staticmethod
    def term(value, scope):
        def leaf(value):
            if type(value) is ast.Var:
                name = scope[value.index][0]
                assert name is not None
                return name
            return "@" + value.name
        return render_int_term(value, leaf)

    def equality(self, value, scope, negative=False):
        sort = (scope[value.left.index][1] if type(value.left) is ast.Var
                else self.env.constants[value.left.name].sort if type(value.left) is ast.Const
                else ast.INT_SORT)
        noun = "integer" if sort == ast.INT_SORT else self.words.sorts[sort]
        return (self.term(value.left, scope) + " is " + ("not " if negative else "")
                + "the same " + noun + " as " + self.term(value.right, scope))

    def unit(self, value, scope):
        text = self.formula(value, scope)
        if type(value) in (ast.Top, ast.Bottom, ast.Unary, ast.Binary, ast.Eq, ast.Lt, ast.Le):
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
            self.stats["relative_guards"] += 1
            return relative
        if type(value) is ast.And:
            left, right = self.relative(value.left, scope), self.relative(value.right, scope)
            if left is not None and right is not None:
                self.stats["relative_guards"] += 1
                return left + " and " + right
        self.stats["structural_guards"] += 1
        self.stats["structural_both_guards"] += int(type(value) is ast.And)
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
        if kind is ast.Reach:
            left, right = self.term(value.left, scope), self.term(value.right, scope)
            count = "one or more" if value.kind == "plus" else "zero or more"
            prefix = f"{right} is reachable from {left} by {count} "
            if type(value.edge) is ast.Named:
                return prefix + value.edge.relation + " steps"
            sort = value.edge.sort
            self.names[sort] += 1
            n = self.names[sort]
            src = self.letters[sort] + (str(n) if n > 1 else "")
            self.names[sort] += 1
            dst = self.letters[sort] + str(self.names[sort])
            body = self.formula(value.edge.formula, ((dst, sort), (src, sort), *scope))
            return prefix + f"steps satisfying [{self.words.sorts[sort]} {src}, {dst} | ({body})]"
        if kind is ast.Eq:
            return self.equality(value, scope)
        if kind in (ast.Lt, ast.Le):
            relation = " is less than " if kind is ast.Lt else " is at most "
            return self.term(value.left, scope) + relation + self.term(value.right, scope)
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
            self.stats["universal_groups"] += 1
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


def contraction_stats(items, env, naming="per_statement"):
    """Count emitted guard forms and negations over checked formulas/documents.

    One guard is one universal group with an implication antecedent. Structural
    guards include single object-position literals; structural_both_guards is
    the subset spelled 'such that (both ...)'. Negation counts visit AST Not
    occurrences once, including those in relative guards and nested negations.
    Whitelisted means a declared negative passed the mechanical lexical check;
    typed inequalities are reported separately. Empty denominators yield 0.0.
    """
    _check_naming(naming)
    from .printer import render
    keys = ("items", "statements", "universal_groups", "relative_guards",
            "structural_guards", "structural_both_guards", "negations",
            "predicate_negations", "whitelisted_negations", "equality_negations",
            "fallback_negations")
    counts = Counter(dict.fromkeys(keys, 0))
    for item in items:
        # Apply the same validation and output limits as the public renderer.
        render(item, env, "ve_fluent", naming)
        visitor = FluentTraversal(env)
        formulas = item.formulas if isinstance(item, ast.Document) else (item,)
        counts["items"] += 1
        counts["statements"] += len(formulas)
        for formula in formulas:
            if naming == "per_statement":
                visitor.names.clear()
            visitor.formula(formula)
            stack = [formula]
            while stack:
                node = stack.pop()
                if type(node) is ast.Not:
                    counts["negations"] += 1
                    if type(node.body) in (ast.Unary, ast.Binary):
                        counts["predicate_negations"] += 1
                        key = ("whitelisted_negations" if node.body.predicate in visitor.words.negatives
                               else "fallback_negations")
                    else:
                        key = "equality_negations" if type(node.body) is ast.Eq else "fallback_negations"
                    counts[key] += 1
                if type(node) in (ast.Not, ast.Forall, ast.Exists):
                    stack.append(node.body)
                elif type(node) is ast.Reach and type(node.edge) is ast.Body:
                    stack.append(node.edge.formula)
                elif type(node) in (ast.And, ast.Or, ast.Implies):
                    stack.extend((node.right, node.left))
        counts.update(visitor.stats)
    result = dict(counts)
    guards = counts["relative_guards"] + counts["structural_guards"]
    result["guards"] = guards
    result["uncontracted_universal_groups"] = counts["universal_groups"] - guards
    for key in ("relative_guards", "structural_guards", "structural_both_guards"):
        result[key + "_share"] = counts[key] / guards if guards else 0.0
    for key in ("whitelisted_negations", "fallback_negations", "equality_negations"):
        result[key + "_share"] = counts[key] / counts["negations"] if counts["negations"] else 0.0
    result["whitelisted_predicate_negations_share"] = (
        counts["whitelisted_negations"] / counts["predicate_negations"]
        if counts["predicate_negations"] else 0.0)
    return result
