"""Independent structural decoder for the four fully grouped test surfaces."""
import re

from ve import ast
from ve.printer import _NaturalVocabulary
from ve.surface.registry import by_tag


def parse_explicit(env, text, view, scope=()):
    """Decode grouping/operators directly; share only the vocabulary codebook."""
    natural = _NaturalVocabulary(env)

    def term(value):
        return ast.Const(value[1:]) if value.startswith("@") else ast.Var(scope.index(value))

    def child(value):
        assert value[0] == "(" and value[-1] == ")", value
        return parse_explicit(env, value[1:-1], view, scope)

    def first_group(value):
        assert value.startswith("("), value
        depth = 0
        for i, char in enumerate(value):
            depth += (char == "(") - (char == ")")
            if depth == 0:
                return value[:i + 1], value[i + 1:]
        raise AssertionError(value)

    symbols = view == "fol_symbols"
    if text == ("⊤" if symbols else "true"):
        return ast.Top()
    if text == ("⊥" if symbols else "false"):
        return ast.Bottom()
    negative = "¬ " if symbols else "it is not the case that " if view == "ve_natural" else "not "
    if text.startswith(negative):
        return ast.Not(child(text[len(negative):]))
    for sort in env.sorts:
        noun = natural.sorts[sort]
        for kind in (by_tag("forall").node_type, by_tag("exists").node_type):
            if symbols:
                pattern = ("∀" if kind is ast.Forall else "∃") + r" (x\d+):" + sort + r", \((.*)\)"
            elif view == "fol_keywords":
                pattern = ("forall" if kind is ast.Forall else "exists") + r" (x\d+):" + sort + r", \((.*)\)"
            elif view == "ve_strict":
                pattern = ("for every" if kind is ast.Forall else "there exists") + " " + sort + r" (x\d+), \((.*)\)"
            elif kind is ast.Forall:
                pattern = "for every " + re.escape(noun) + r" (x\d+): \((.*)\)"
            else:
                pattern = "there is an? " + re.escape(noun) + r" (x\d+) such that \((.*)\)"
            match = re.fullmatch(pattern, text)
            if match:
                return kind(sort, parse_explicit(env, match[2], view, (match[1], *scope)))
    token = r"(@[a-z][a-z0-9_]*|x[0-9]+)"
    if view in ("ve_strict", "fol_keywords"):
        m = re.fullmatch(r"(tc|rtc)\[([a-z][a-z0-9_]*)\]\(" + token + ", " + token + r"\)", text)
        if m:
            return ast.Reach("plus" if m[1] == "tc" else "star", ast.Named(m[2]), term(m[3]), term(m[4]))
        m = re.fullmatch(r"(tc|rtc)\[([a-z][a-z0-9_]*) (x\d+), (x\d+) \| \((.*)\)\]\(" + token + ", " + token + r"\)", text)
        if m:
            body = parse_explicit(env, m[5], view, (m[4], m[3], *scope))
            return ast.Reach("plus" if m[1] == "tc" else "star", ast.Body(m[2], body), term(m[6]), term(m[7]))
    elif symbols:
        m = re.fullmatch(r"([a-z][a-z0-9_]*)(⁺|\*)\(" + token + ", " + token + r"\)", text)
        if m:
            return ast.Reach("plus" if m[2] == "⁺" else "star", ast.Named(m[1]), term(m[3]), term(m[4]))
        m = re.fullmatch(r"\((TC|RTC) (x\d+):([a-z][a-z0-9_]*),(x\d+):([a-z][a-z0-9_]*)\.\((.*)\)\)\(" + token + ", " + token + r"\)", text)
        if m:
            assert m[3] == m[5]
            body = parse_explicit(env, m[6], view, (m[4], m[2], *scope))
            return ast.Reach("plus" if m[1] == "TC" else "star", ast.Body(m[3], body), term(m[7]), term(m[8]))
    elif view == "ve_natural":
        m = re.fullmatch(token + " is reachable from " + token + r" by (one|zero) or more ([a-z][a-z0-9_]*) steps", text)
        if m:
            return ast.Reach("plus" if m[3] == "one" else "star", ast.Named(m[4]), term(m[2]), term(m[1]))
        for sort in env.sorts:
            m = re.fullmatch(token + " is reachable from " + token + r" by (one|zero) or more steps satisfying \[" + re.escape(natural.sorts[sort]) + r" (x\d+), (x\d+) \| \((.*)\)\]", text)
            if m:
                body = parse_explicit(env, m[6], view, (m[5], m[4], *scope))
                return ast.Reach("plus" if m[3] == "one" else "star", ast.Body(sort, body), term(m[2]), term(m[1]))
    if text.startswith("if "):
        left, rest = first_group(text[3:])
        assert rest.startswith(", then ")
        return ast.Implies(child(left), child(rest[7:]))
    if text.startswith("("):
        left, rest = first_group(text)
        separators = {" ∧ ": by_tag("and").node_type, " ∨ ": by_tag("or").node_type,
                      " → ": by_tag("implies").node_type} if symbols else {
            " and ": by_tag("and").node_type, " or ": by_tag("or").node_type,
            " implies ": by_tag("implies").node_type}
        for separator, constructor in separators.items():
            if rest.startswith(separator):
                right = rest[len(separator):]
                if view == "ve_natural" and constructor is ast.Or:
                    assert right.endswith(", or both")
                    right = right[:-9]
                return constructor(child(left), child(right))
        raise AssertionError(rest)
    token = r"(@[a-z][a-z0-9_]*|x[0-9]+)"
    equality = " = " if view.startswith("fol_") else " is equal to " if view == "ve_natural" else " equals "
    match = re.fullmatch(token + equality + token, text)
    if match:
        return ast.Eq(term(match[1]), term(match[2]))
    candidates = []
    for name, declaration in env.predicates.items():
        arity = len(declaration.arguments)
        if view.startswith("fol_"):
            pattern = name + r"\(" + token + (", " + token if arity == 2 else "") + r"\)"
        else:
            template = (natural.predicates[name] if view == "ve_natural" else
                        "{0} is " + name if arity == 1 else "{0} " + name + " {1}")
            pattern = re.escape(template)
            for i in range(arity):
                pattern = pattern.replace(re.escape("{" + str(i) + "}"), token)
        match = re.fullmatch(pattern, text)
        if match:
            candidates.append((ast.Unary if arity == 1 else ast.Binary)(name, *(term(t) for t in match.groups())))
    assert len(candidates) == 1, (view, text, candidates)
    return candidates[0]
