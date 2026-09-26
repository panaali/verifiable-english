"""Canonical W1 rule-block view with an identity-bound export manifest.

Rule blocks are document units, rather than FOL formulas, so this surface has
its own entry point. Guards use the ordinary English formula parser with the
deontic atom templates added from regulated declarations.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import re

from . import ast
from .english import EnglishParser, EnglishTraversal, EnglishVocabulary
from .errors import SyntaxError, VEError
from .norms import Norm, NormDocument
from .surface import norms as _registered_surface  # noqa: F401


def _words(env):
    words = EnglishVocabulary(env)
    for name, decl in env.predicates.items():
        reg = decl.regulated
        if reg is not None and reg.role != "plain":
            modal = "may" if reg.role == "permission" else "must"
            words.predicates[name] = reg.act.replace("{0} ", "{0} " + modal + " ", 1)
            words.negatives.pop(name, None)
    return words


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
    return formula


def _consequence(rule, env, words):
    decl = env.predicates[rule.predicate]
    reg = decl.regulated
    scope, nouns = _bindings(decl, words)
    if reg.role == "plain":
        template = words.predicates[rule.predicate]
    else:
        if reg.role == "permission":
            modal = "may" if rule.sign else "must not"
        else:
            modal = "must" if rule.sign else "need not"
        template = reg.act.replace("{0} ", "{0} " + modal + " ", 1)
    args = ["Every " + nouns[0]] + ["each " + noun for noun in nouns[1:]]
    text = template.format(*args)
    if reg.role == "plain" and not rule.sign:
        text = "It is not the case that " + text
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
                    "it is not the case that " + words.predicates[predicate])
        return "By default, " + template.format(*(article(n) for n in nouns)) + "."
    modal = ("may" if reg.default == "allow" else "must not") if reg.role == "permission" else (
        "must" if reg.default == "allow" else "need not")
    template = reg.act.replace("{0} ", "{0} " + modal + " ", 1)
    return "By default, " + template.format(*(article(n) for n in nouns)) + "."


def render_english(document: NormDocument):
    env = document.env
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
        block = header + " " + sentence
        start = sum(len(line) + 1 for line in lines)
        lines.append(block)
        entries.append({"handle": f"norm-{i}", "name": rule.name,
                        "number": i, "span": [start, start + len(block)]})
    text = "\n".join(lines)
    manifest = {"environment_id": env.environment_id,
                "document_hash": document.document_hash,
                "text_digest": hashlib.sha256(text.encode()).hexdigest(),
                "blocks": entries}
    return text, manifest


_HEADER = re.compile(r"Rule ([1-9][0-9]*)(?: \(exception to rules? ([0-9, and]+)\))?\. (.*)\Z", re.S)


def _parse_consequence(text, env, words):
    matches = []
    for name, decl in env.predicates.items():
        if decl.regulated is None:
            continue
        for sign in (True, False):
            dummy = Norm("candidate", name, sign, ast.Top())
            wording, scope = _consequence(dummy, env, words)
            nouns = [words.sorts[s] for s in decl.arguments]
            alternatives = [wording]
            if len(nouns) == 2:
                alternatives.append(wording.replace("each " + nouns[1], "any " + nouns[1]))
            if decl.regulated.role == "permission" and not sign:
                alternatives.append(wording.replace("Every " + nouns[0] + " must not ",
                                                    "No " + nouns[0] + " may ", 1))
            for candidate in alternatives:
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
    blocks = source.split("\n") if source else []
    if manifest is not None and len(manifest.get("blocks", [])) != len(blocks):
        raise VEError("IdentityMetadataMismatch: block count")
    words = _words(env)
    parsed = []
    reserved = set(existing_names)
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
            if (entry.get("number") != index or entry.get("span") != [start, start + len(block)]
                    or entry.get("handle") != f"norm-{index}" or entry.get("name") in reserved):
                raise VEError("IdentityMetadataMismatch: block mapping")
            name = entry["name"]
            reserved.add(name)
        refs = tuple(int(x) for x in re.findall(r"[0-9]+", m[2] or ""))
        clauses = m[3].split(" Except when ")
        if not clauses[0].endswith("."):
            raise SyntaxError("Expected a complete rule sentence")
        first = clauses[0][:-1]
        extra = [x[:-1] if x.endswith(".") else x for x in clauses[1:]]
        unless = []
        if ", unless " in first:
            first, u = first.split(", unless ", 1)
            unless.append(u)
        guard_text = None
        if ", if " in first:
            first, guard_text = first.split(", if ", 1)
        predicate, sign, scope = _parse_consequence(first, env, words)
        guard = _parse_guard(guard_text, env, words, scope) if guard_text else ast.Top()
        carveouts = tuple(_parse_guard(x, env, words, scope) for x in (*unless, *extra))
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
