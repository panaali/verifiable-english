"""Canonical W1 rule-block view with an identity-bound export manifest.

Rule blocks are document units, rather than FOL formulas, so this surface has
its own entry point. Guards use the ordinary English formula parser with the
deontic atom templates added from regulated declarations.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import re

from . import ast
from .english import EnglishParser, EnglishTraversal, EnglishVocabulary, english_lark_grammar
from .surface.unambiguity import require_unique_derivation
from .errors import SyntaxError, VEError
from .norms import Norm, NormDocument
from .surface import norms as _registered_surface  # noqa: F401


def _words(env):
    return EnglishVocabulary(env)


def _bindings(decl, words):
    counts = Counter(decl.arguments)
    scope = []
    nouns = []
    for sort in decl.arguments:
        noun = words.sorts[sort]
        index = sum(s == sort for s, _ in scope)
        if counts[sort] == 1:
            ref, display = "that " + noun, noun
        elif counts[sort] == 2:
            display = ("first " if index == 0 else "second ") + noun
            ref = "the " + display
        else:
            raise VEError("ResourceLimit: English rule surface supports at most two same-sort arguments")
        scope.insert(0, (sort, ref))
        nouns.append(display)
    return tuple(scope), tuple(nouns)


def _guard_text(formula, env, words, scope):
    traversal = EnglishTraversal(env, words)
    traversal.maximum = Counter(sort for sort, _ in scope)
    return traversal.formula(formula, scope)


def _parse_guard(source, env, words, scope):
    parser = EnglishParser(env, source, words)
    formula = parser.formula(scope)
    if parser.i != len(source):
        raise SyntaxError("The condition has more than one reading or trailing words")
    ast._Checker(env).formula(formula, tuple(sort for sort, _ in scope))
    # Close the situation variables with explicit English binders so the P0
    # independent Earley grammar checks every derivation of this condition.
    bound = list(reversed(scope))
    prefixes = []
    counts = Counter(sort for sort, _ in bound)
    seen = Counter()
    for sort, _ in bound:
        noun = words.sorts[sort]
        if counts[sort] == 2:
            noun = ("first " if seen[sort] == 0 else "second ") + noun
        seen[sort] += 1
        prefixes.append("for every " + noun + ", ")
    require_unique_derivation(env, "".join(prefixes) + source + ".")
    return formula


def _consequence(rule, env, words):
    decl = env.predicates[rule.predicate]
    reg = decl.regulated
    scope, nouns = _bindings(decl, words)
    if reg.role == "plain":
        template = (words.negatives.get(rule.predicate) if not rule.sign else None) or words.predicates[rule.predicate]
    else:
        if reg.role == "permission":
            modal = "may" if rule.sign else "must not"
        else:
            modal = "must" if rule.sign else "need not"
        template = reg.act.replace("{0} ", "{0} " + modal + " ", 1)
    args = ["Every " + nouns[0]] + ["each " + noun for noun in nouns[1:]]
    text = template.format(*args)
    if reg.role == "plain" and not rule.sign and rule.predicate not in words.negatives:
        refs = [scope[len(scope) - i - 1][1] for i in range(len(nouns))]
        body = template.format(*refs)
        binders = ", ".join(["for every " + nouns[0]] + ["for each " + noun for noun in nouns[1:]])
        text = binders.capitalize() + ", it is not the case that " + body
    return text, scope


def default_sentence(env, predicate):
    decl = env.predicates[predicate]
    reg = decl.regulated
    if reg is None:
        raise VEError(f"UnknownSymbol: regulated predicate {predicate}")
    words = _words(env)
    nouns = [words.sorts[s] for s in decl.arguments]
    article = lambda noun: ("an " if noun[0].lower() in "aeiou" else "a ") + noun
    if reg.role == "plain":
        template = (words.predicates[predicate] if reg.default == "allow" else
                    words.negatives.get(predicate) or "it is not the case that " + words.predicates[predicate])
        return "By default, " + template.format(*(article(n) for n in nouns)) + "."
    modal = ("may" if reg.default == "allow" else "must not") if reg.role == "permission" else (
        "must" if reg.default == "allow" else "need not")
    template = reg.act.replace("{0} ", "{0} " + modal + " ", 1)
    return "By default, " + template.format(*(article(n) for n in nouns)) + "."


def render_rule_sentence(rule, env, words=None):
    """Render the content of one rule, including quoted rules outside a layer."""
    words = _words(env) if words is None else words
    consequence, scope = _consequence(rule, env, words)
    sentence = consequence
    if not isinstance(rule.guard, ast.Top):
        sentence += ", if " + _guard_text(rule.guard, env, words, scope)
    if len(rule.unless) == 1:
        sentence += ", unless " + _guard_text(rule.unless[0], env, words, scope)
    sentence += "."
    if len(rule.unless) > 1:
        sentence += " " + " ".join("Except when " + _guard_text(u, env, words, scope) + "."
                                   for u in rule.unless)
    return sentence


def render_english(document: NormDocument, *, handles=None):
    env = document.env
    if handles is not None and (set(handles) != {r.name for r in document.rules}
                                or len(set(handles.values())) != len(handles)
                                or any(type(h) is not str or not h for h in handles.values())):
        raise VEError("IdentityMetadataMismatch: invalid editor handles")
    words = _words(env)
    numbers = {r.name: i for i, r in enumerate(document.rules, 1)}
    lines = []
    entries = []
    for i, rule in enumerate(document.rules, 1):
        if rule.over:
            refs = ", ".join(str(numbers[name]) for name in rule.over)
            header = (f"Rule {i} (exception to rule {refs})." if len(rule.over) == 1 else
                      f"Rule {i} (exception to rules {refs}).")
        else:
            header = f"Rule {i}."
        block = header + " " + render_rule_sentence(rule, env, words)
        start = sum(len(line) + 1 for line in lines)
        lines.append(block)
        entries.append({"handle": handles[rule.name] if handles is not None else f"handle-{rule.name}",
                        "name": rule.name,
                        "number": i, "span": [start, start + len(block)]})
    text = "\n".join(lines)
    manifest = {"environment_id": env.environment_id,
                "document_hash": document.document_hash,
                "text_digest": hashlib.sha256(text.encode()).hexdigest(),
                "blocks": entries}
    return text, manifest


_HEADER = re.compile(r"Rule ([1-9][0-9]*)(?: \(exception to rules? ([0-9, and]+)\))?\. (.*)\Z", re.S)


def _block_grammar(env, words):
    """Audit the complete rule syntax with P0's independent formula grammar.

    Consequences are declared phrases, never a catch-all terminal. The guard
    and carve-out positions use the same unrestricted formula productions as
    ordinary English, so punctuation and connective ambiguity remain visible.
    """
    base = english_lark_grammar(env)
    clauses = []
    for name, decl in env.predicates.items():
        if decl.regulated is None:
            continue
        for sign in (True, False):
            wording, _ = _consequence(Norm("candidate", name, sign, ast.Top()), env, words)
            _, nouns = _bindings(decl, words)
            variants = [wording]
            if len(nouns) == 2:
                variants.append(wording.replace("each " + nouns[1], "any " + nouns[1]))
            if decl.regulated.role == "permission" and not sign:
                variants.append(wording.replace("Every " + nouns[0] + " must not ",
                                                "No " + nouns[0] + " may ", 1))
            clauses.extend(json.dumps(v) + "i" for v in dict.fromkeys(variants))
    if not clauses:
        clauses = ["IMPOSSIBLE"]
    lines = base.splitlines()
    lines[0] = ('start: rule_block | precedence_sentence\n'
                'rule_block: "Rule"i RULE_NUMBER header? "." consequence condition* "." carveout*\n'
                'header: "(" "exception to rule"i RULE_NUMBER ")" '
                '| "(" "exception to rules"i rule_refs ")"\n'
                'rule_refs: RULE_NUMBER ("," RULE_NUMBER | "and"i RULE_NUMBER)*\n'
                'precedence_sentence: "Rule"i RULE_NUMBER "takes precedence over rule"i RULE_NUMBER "."\n'
                'condition: ", if" formula | ", unless" formula | ", except when"i formula\n'
                'carveout: "Except when"i formula "."\n'
                'consequence: ' + ' | '.join(dict.fromkeys(clauses)) + '\n'
                'RULE_NUMBER: /[1-9][0-9]*/')
    return "\n".join(lines) + "\n"


def _parse_consequence(text, env, words):
    matches = []
    for name, decl in env.predicates.items():
        if decl.regulated is None:
            continue
        for sign in (True, False):
            dummy = Norm("candidate", name, sign, ast.Top())
            wording, scope = _consequence(dummy, env, words)
            _, nouns = _bindings(decl, words)
            alternatives = [wording]
            if len(nouns) == 2:
                alternatives.append(wording.replace("each " + nouns[1], "any " + nouns[1]))
            if decl.regulated.role == "permission" and not sign:
                alternatives.append(wording.replace("Every " + nouns[0] + " must not ",
                                                    "No " + nouns[0] + " may ", 1))
            for candidate in dict.fromkeys(alternatives):
                if text.casefold() == candidate.casefold():
                    matches.append((name, sign, scope))
    if len(matches) != 1:
        raise SyntaxError("Norm consequence has no single declared reading; use Every, each, and a declared act phrase")
    return matches[0]


def parse_english(env, source, manifest=None, *, existing_names=()):
    if type(source) is not str:
        raise SyntaxError("Norm English must be text")
    if manifest is not None:
        if (type(manifest) is not dict or manifest.get("environment_id") != env.environment_id
                or manifest.get("text_digest") != hashlib.sha256(source.encode()).hexdigest()):
            raise VEError("IdentityMetadataMismatch: stale English export")
    words = _words(env)
    grammar = _block_grammar(env, words)
    lines = source.split("\n") if source else []
    precedence = {}
    blocks = []
    for line in lines:
        standalone = re.fullmatch(r"Rule ([1-9][0-9]*) takes precedence over rule ([1-9][0-9]*)\.", line)
        if standalone:
            require_unique_derivation(env, line, grammar=grammar)
            precedence.setdefault(int(standalone[1]), []).append(int(standalone[2]))
        else:
            blocks.append(line)
    if any(source_ref < 1 or source_ref > len(blocks) or
           target_ref < 1 or target_ref > len(blocks)
           for source_ref, targets in precedence.items() for target_ref in targets):
        raise VEError("UnknownRule: display reference")
    if manifest is not None and len(manifest.get("blocks", [])) != len(blocks):
        raise VEError("IdentityMetadataMismatch: block count")
    parsed = []
    reserved = set(existing_names)
    seen_handles = set()
    for index, block in enumerate(blocks, 1):
        m = _HEADER.fullmatch(block)
        if m is None or int(m[1]) != index:
            raise SyntaxError(f"Expected Rule {index} with its own block")
        if manifest is None:
            candidate = index
            while f"rule-{candidate}" in reserved:
                candidate += 1
            name = f"rule-{candidate}"
            reserved.add(name)
        else:
            entry = manifest["blocks"][index - 1]
            start = sum(len(b) + 1 for b in blocks[:index - 1])
            handle = entry.get("handle")
            if (entry.get("number") != index or entry.get("span") != [start, start + len(block)]
                    or type(handle) is not str or not handle or handle in seen_handles
                    or entry.get("name") in reserved):
                raise VEError("IdentityMetadataMismatch: block mapping")
            seen_handles.add(handle)
            name = entry["name"]
            reserved.add(name)
        refs = tuple(int(x) for x in re.findall(r"[0-9]+", m[2] or "")) + tuple(precedence.get(index, ()))
        clauses = m[3].split(" Except when ")
        if not clauses[0].endswith("."):
            raise SyntaxError("Expected a complete rule sentence")
        first = clauses[0][:-1]
        extra = [x[:-1] if x.endswith(".") else x for x in clauses[1:]]
        unless = []
        carve = re.search(r", (?:unless|except when) ", first, re.I)
        if carve:
            u = first[carve.end():]
            first = first[:carve.start()]
            unless.append(u)
        guard_text = None
        if ", if " in first:
            first, guard_text = first.split(", if ", 1)
        predicate, sign, scope = _parse_consequence(first, env, words)
        guard = _parse_guard(guard_text, env, words, scope) if guard_text else ast.Top()
        carveouts = tuple(_parse_guard(x, env, words, scope) for x in (*unless, *extra))
        require_unique_derivation(env, block, grammar=grammar)
        parsed.append((name, predicate, sign, guard, carveouts, refs))
    names = [x[0] for x in parsed]
    rules = []
    for name, predicate, sign, guard, carveouts, refs in parsed:
        if any(ref < 1 or ref > len(names) for ref in refs):
            raise VEError("UnknownRule: display reference")
        rules.append(Norm(name, predicate, sign, guard, carveouts,
                          tuple(names[ref - 1] for ref in refs)))
    document = NormDocument(env, rules)
    if manifest is not None and manifest.get("document_hash") != document.document_hash:
        raise VEError("IdentityMetadataMismatch: norm document hash")
    return document
