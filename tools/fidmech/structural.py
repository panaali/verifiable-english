"""Structural mutants of one document's rule blocks, made on the parsed rule and written back as VE English (plan 5.1).

Each rule block's line is parsed by VE (`ve.norm_english.parse_english`, which asks Lean); an op edits the parsed rule
(its guard, its unless clauses or its force) and VE's own renderer (`render_rule_sentence`) writes it back, so a guard
names the rule's own bound variable by its sort ("that proposal", "that threshold"), never a fixed "that situation".
The written line is parsed again: a line that does not parse, or parses to another rule than the edit made, is
`stillborn` (counted and listed, never scored).

| op | edit |
|---|---|
| drop-conjunct | each leaf of the guard's top conjunction, alone (a guard of one condition: the rule becomes unconditional) |
| drop-unless | each unless clause, alone |
| drop-disjunct | each leaf of a disjunction that is the guard, a top conjunct of the guard or an unless clause, alone |
| drop-exception | each PRECEDENCE pair, alone (the translation module's literal); each rule whose header calls it an exception to another gets the always-false guard |
| flip-force | the rule's mode: strict <-> default (must <-> should, must not <-> should not, may <-> generally may, need not <-> generally need not) |
| add-guard-true | the guard gains a unary base predicate of the subject's sort that holds in the case-model atoms of an item selecting the rule and that the rule uses nowhere (so never `A and A`) |
| rule-drop | the always-false guard ("if this is impossible"): rule coverage, not guard detection |
| widen-quantifier | for a rule over a second variable, every top conjunct of the guard that restricts that variable alone, dropped together |

A predicate's role (obligation or permission) is fixed by its vocabulary entry, so the parsed form has no may <-> must
or need not <-> must not flip (VE refuses such a line: the role-crossing pairs would always be stillborn). A mutant
whose edits equal another's is kept once, under the narrower op (KEEP_FIRST), and the other is counted as a duplicate.
A plain predicate (no obligation or permission act) has no force to flip.

`syntactic(original, mutant)` compares two parsed rules through `SoftRule.to_dict` (never `Norm.to_dict`, which drops
the mode, so force stays in the comparison) after sorting the operands of every and/or chain, recursively; `over` is
kept. A structural mutant is `syntactic` only when it changes the rule file alone.
"""
from __future__ import annotations

import ast as pyast
import json
import re
from dataclasses import dataclass, replace

from ve import ast
from ve.errors import CheckerUnavailable

GENERATOR = "fidmech/1"
OPS = ("drop-conjunct", "drop-unless", "drop-disjunct", "drop-exception", "flip-force", "add-guard-true",
       "rule-drop", "widen-quantifier")
# Which op keeps a mutant whose edits equal another's: the narrower name first (a widen that drops the one
# restricting conjunct is also a drop-conjunct; a header-declared exception's drop is also a rule-drop).
KEEP_FIRST = ("drop-exception", "widen-quantifier", "drop-unless", "drop-disjunct", "drop-conjunct", "flip-force",
              "add-guard-true", "rule-drop")
RULES, ENVIRONMENT, FACTS, BINDINGS = "rules.d1.ve", "environment.d1.json", "facts.d1.ve", "fidmech/bindings.json"
EXCEPTION_HEADER = re.compile(r"\bexception to\b", re.I)
# What VE's parse or render may raise for a line it does not take: a refusal (VEError is a ValueError), or no answer
# (CheckerUnavailable: the parse is undecided). Anything else is a bug here and propagates.
REFUSED = (ValueError, CheckerUnavailable)
RULE_LINE = re.compile(r"(Rule [1-9][0-9]*\. )(.*)\Z", re.S)


@dataclass(frozen=True)
class Block:
    """A rule block: its id, its header line and its one rule line."""
    id: str
    header: str
    text: str


def rule_blocks(text):
    """The rule blocks of a rules file: `## <id> | ...` header lines, each followed by its block's one line; a block
    whose line is no numbered rule (an item's own premise) is skipped."""
    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines):
        head = re.match(r"## (\S+) \|", line)
        if head and i + 1 < len(lines) and RULE_LINE.match(lines[i + 1]):
            out.append(Block(head.group(1), line, lines[i + 1]))
    return out


def translation_name(files):
    """The translation module's file name among a case's files (the one holding PRECEDENCE)."""
    names = sorted(n for n in files if n.endswith("translation.py"))
    if len(names) != 1:
        raise ValueError(f"expected one *translation.py, found {names}")
    return names[0]


def _precedence_node(source):
    for node in pyast.parse(source).body:
        if (isinstance(node, pyast.Assign) and len(node.targets) == 1
                and getattr(node.targets[0], "id", None) == "PRECEDENCE"):
            return node.value
    raise ValueError("no PRECEDENCE assignment")


def precedence(source):
    """{rule: (rules it takes precedence over)} of a translation module's source (its literal, never imported)."""
    return pyast.literal_eval(_precedence_node(source))


def render_precedence(value):
    return "{" + ", ".join(json.dumps(k) + ": (" + "".join(json.dumps(v) + ", " for v in vs).rstrip(" ") + ")"
                           for k, vs in value.items()) + "}"


# ---- the parsed form ---------------------------------------------------------------------------------------------

def leaves(formula, kind):
    """Paths (tuples of 0/1) to the leaves of the `kind` (ast.And or ast.Or) tree at the top of `formula`."""
    if isinstance(formula, kind):
        return [(0, *p) for p in leaves(formula.left, kind)] + [(1, *p) for p in leaves(formula.right, kind)]
    return [()]


def leaf(formula, path):
    for step in path:
        formula = formula.right if step else formula.left
    return formula


def drop(formula, path):
    """`formula` with the leaf at `path` taken out of its tree (its parent replaced by the sibling); a leaf at the
    root leaves ast.Top."""
    if not path:
        return ast.Top()
    if len(path) == 1:
        return formula.left if path[0] else formula.right
    if path[0]:
        return replace(formula, right=drop(formula.right, path[1:]))
    return replace(formula, left=drop(formula.left, path[1:]))


def predicates(formula):
    """Every predicate a formula names, at any depth."""
    if isinstance(formula, (ast.Unary, ast.Binary, ast.Atom)):
        return {formula.predicate}
    found = set()
    for name in getattr(formula, "__slots__", ()):
        value = getattr(formula, name)
        for v in value if isinstance(value, tuple) else (value,):
            if _is_formula(v):
                found |= predicates(v)
    return found


def _is_formula(value):
    return type(value).__module__ == ast.__name__ and not isinstance(value, (ast.Var, ast.Const))


def free_vars(formula, depth=0):
    """The free de Bruijn indices of a formula (an index under k binders counts as index - k)."""
    if isinstance(formula, ast.Var):
        return {formula.index - depth} if formula.index >= depth else set()
    found = set()
    inner = depth + isinstance(formula, (ast.Forall, ast.Exists))
    for name in getattr(formula, "__slots__", ()):
        value = getattr(formula, name)
        for v in value if isinstance(value, tuple) else (value,):
            if _is_formula(v) or isinstance(v, ast.Var):
                found |= free_vars(v, inner)
    return found


# ---- ops on one parsed rule --------------------------------------------------------------------------------------

def _edit(rule, **core):
    """A copy of a parsed SoftRule with core fields and the mode replaced."""
    mode = core.pop("mode", rule.mode)
    return replace(rule, core=replace(rule.core, **core), mode=mode)


def ops_of(rule, env, *, exception=False, true_atoms=()):
    """[(op, where, edited SoftRule)] of one parsed rule. `true_atoms`: the unary base predicates of the subject's sort
    that hold in an item selecting the rule, most items first; `exception`: its header calls it an exception."""
    core = rule.core
    out = []
    if not isinstance(core.guard, ast.Top):
        out += [("drop-conjunct", "rule", _edit(rule, guard=drop(core.guard, p))) for p in leaves(core.guard, ast.And)]
    out += [("drop-unless", "unless", _edit(rule, unless=core.unless[:i] + core.unless[i + 1:]))
            for i in range(len(core.unless))]
    tops = [((), core.guard)] + [(p, leaf(core.guard, p)) for p in leaves(core.guard, ast.And) if p]
    for conj, formula in tops:
        if isinstance(formula, ast.Or):
            for p in leaves(formula, ast.Or):
                guard = drop(formula, p) if not conj else _put(core.guard, conj, drop(formula, p))
                out.append(("drop-disjunct", "rule", _edit(rule, guard=guard)))
    for i, formula in enumerate(core.unless):
        for p in leaves(formula, ast.Or) if isinstance(formula, ast.Or) else ():
            unless = core.unless[:i] + (drop(formula, p),) + core.unless[i + 1:]
            out.append(("drop-disjunct", "unless", _edit(rule, unless=unless)))
    if exception:
        out.append(("drop-exception", "rule", _edit(rule, guard=ast.Bottom())))
    if env.predicates[core.predicate].regulated.role != "plain":  # a plain predicate carries no force
        out.append(("flip-force", "rule", _edit(rule, mode="strict" if rule.mode == "default" else "default")))
    used = predicates(core.guard) | {p for u in core.unless for p in predicates(u)} | {core.predicate}
    arguments = env.predicates[core.predicate].arguments
    for name in true_atoms:
        if name not in used:
            new = ast.Unary(name, ast.Var(len(arguments) - 1))  # the subject: first argument, de Bruijn len - 1
            guard = new if isinstance(core.guard, ast.Top) else ast.And(core.guard, new)
            out.append(("add-guard-true", "rule", _edit(rule, guard=guard)))
            break
    out.append(("rule-drop", "rule", _edit(rule, guard=ast.Bottom())))
    if len(arguments) == 2 and not isinstance(core.guard, ast.Top):
        guard, restricting = core.guard, [p for p in leaves(core.guard, ast.And)
                                          if free_vars(leaf(core.guard, p)) == {0}]
        for p in sorted(restricting, reverse=True):  # deepest right first, so earlier paths stay valid
            guard = drop(guard, p)
        if restricting:
            out.append(("widen-quantifier", "rule", _edit(rule, guard=guard)))
    return out


def _put(formula, path, value):
    if not path:
        return value
    if path[0]:
        return replace(formula, right=_put(formula.right, path[1:], value))
    return replace(formula, left=_put(formula.left, path[1:], value))


def guard_candidates(env, rule_id, subject_sort, selected, atoms):
    """The unary base predicates of `subject_sort` true in the case-model atoms of an item that selects `rule_id`,
    most items first (then by name). `selected` {item: rule ids} and `atoms` {item: atoms} are the adapter's
    (tools/fidmech/adapters.py)."""
    counts = {}
    for item, rules in selected.items():
        if rule_id not in rules:
            continue
        for name in {a[0] for a in atoms.get(item, ()) if len(a) == 2}:
            decl = env.predicates.get(name)
            if decl is not None and decl.regulated is None and tuple(decl.arguments) == (subject_sort,):
                counts[name] = counts.get(name, 0) + 1
    return [n for n, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]


# ---- writing back, parsing, equivalence --------------------------------------------------------------------------

def render(rule, env, prefix="Rule 1. "):
    """The VE English line of a parsed (or edited) rule, on one line as the rules files hold it."""
    from ve.norm_english import render_rule_sentence
    return re.sub(r"\n\s*", " ", prefix + render_rule_sentence(rule, env))


def parse(env, line):
    """The parsed SoftRule of one rule line (VE's one-reading parse, Lean)."""
    from ve.norm_english import parse_english
    rules = parse_english(env, line).rules
    if len(rules) != 1:
        raise ValueError(f"{len(rules)} rules in one block")
    return rules[0]


def canonical_rule(rule):
    """SoftRule.to_dict() with every and/or chain flattened and its operands sorted, recursively."""
    def canon(node):
        if isinstance(node, list) and node and node[0] in ("and", "or"):
            flat = []

            def walk(n):
                if isinstance(n, list) and n and n[0] == node[0]:
                    walk(n[1])
                    walk(n[2])
                else:
                    flat.append(canon(n))
            walk(node)
            return [node[0], sorted(flat, key=lambda x: json.dumps(x, sort_keys=True))]
        if isinstance(node, list):
            return [canon(x) for x in node]
        if isinstance(node, dict):
            return {k: canon(v) for k, v in node.items()}
        return node
    return canon(json.loads(json.dumps(rule.to_dict())))


def syntactic(original, mutant):
    """Whether two parsed rules are equal after canonicalisation (force, mode and `over` kept)."""
    return canonical_rule(original) == canonical_rule(mutant)


def same_edit(expected, parsed):
    """Whether a re-parsed line is the edited rule: its core and its mode."""
    return expected.core.to_dict()["norm"] | {"name": None} == parsed.core.to_dict()["norm"] | {"name": None} \
        and expected.mode == parsed.mode
