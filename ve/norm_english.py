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

from .assurance import semantic_entry
from . import ast
from .english import EnglishParser, EnglishTraversal, EnglishVocabulary, _max_scope, english_lark_grammar
from .surface.unambiguity import require_unique_derivation
from .errors import SyntaxError, VEError
from .norms import Norm, NormDocument
from .surface import norms as _registered_surface  # noqa: F401
from .surface import softnorms as _soft_surface


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
    traversal = EnglishTraversal(env, words, word_markers=env.alternatives is not None)
    initial = tuple(sort for sort, _ in scope)
    traversal.maximum = _max_scope(formula, initial, Counter(initial))
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


def _mentions_outcome(formula, predicate):
    """Find a deontic self-edge at any tuple, including another action."""
    if isinstance(formula, (ast.Unary, ast.Binary)):
        return formula.predicate == predicate
    if isinstance(formula, (ast.Forall, ast.Exists)):
        return _mentions_outcome(formula.body, predicate)
    if isinstance(formula, ast.Not):
        return _mentions_outcome(formula.body, predicate)
    if isinstance(formula, (ast.And, ast.Or, ast.Implies)):
        return (_mentions_outcome(formula.left, predicate) or
                _mentions_outcome(formula.right, predicate))
    return False


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


def default_sentence(env, predicate, completion=None):
    """The legend sentence of `predicate`'s completion (the declared one unless
    `completion` names another, as the legend grammar's alternatives do)."""
    decl = env.predicates[predicate]
    reg = decl.regulated
    if reg is None:
        raise VEError(f"UnknownSymbol: regulated predicate {predicate}")
    default = reg.default if completion is None else completion
    words = _words(env)
    nouns = [words.sorts[s] for s in decl.arguments]
    article = lambda noun: ("an " if noun[0].lower() in "aeiou" else "a ") + noun
    if default == "unspecified":
        # norm-defaults 4.1: one reading, "neither answer follows" where nothing
        # else in the text (no rule, `By default` or pair sentence) settles it.
        return UNSPECIFIED_KEYWORD + "the text does not say whether " + unspecified_clause(env, predicate) + "."
    if reg.role == "plain":
        template = (words.predicates[predicate] if default == "allow" else
                    words.negatives.get(predicate) or "it is not the case that " + words.predicates[predicate])
        return "By default, " + template.format(*(article(n) for n in nouns)) + "."
    modal = ("may" if default == "allow" else "must not") if reg.role == "permission" else (
        "must" if default == "allow" else "need not")
    template = reg.act.replace("{0} ", "{0} " + modal + " ", 1)
    return "By default, " + template.format(*(article(n) for n in nouns)) + "."


UNSPECIFIED_KEYWORD = "When nothing else in the text decides, "


def unspecified_clause(env, predicate, arguments=None):
    """`a <noun> may <act>`, `a <noun> must <act>` or the plain verbalisation,
    with indefinite arguments unless `arguments` names them."""
    decl = env.predicates[predicate]
    reg = decl.regulated
    words = _words(env)
    if arguments is None:
        arguments = [("an " if n[0].lower() in "aeiou" else "a ") + n
                     for n in (words.sorts[s] for s in decl.arguments)]
    if reg.role == "plain":
        return words.predicates[predicate].format(*arguments)
    modal = "may" if reg.role == "permission" else "must"
    return reg.act.replace("{0} ", "{0} " + modal + " ", 1).format(*arguments)


def pair_sentence(env, required):
    """norm-defaults 4.1: the profile premise of a declared pair, render-only."""
    decl = env.predicates[required]
    reg = decl.regulated
    if reg is None or reg.permission is None:
        raise VEError(f"UnknownSymbol: declared pair {required}")
    words = _words(env)
    scope, nouns = _bindings(decl, words)
    refs = [scope[len(scope) - i - 1][1] for i in range(len(nouns))]
    first = [("an " if n[0].lower() in "aeiou" else "a ") + n for n in nouns]
    must = reg.act.replace("{0} ", "{0} must ", 1).format(*first)
    may = reg.act.replace("{0} ", "{0} may ", 1).format("it", *refs[1:])
    return "Whenever " + must + ", " + may + "."


def render_rule_sentence(rule, env, words=None):
    """Render the content of one rule, including quoted rules outside a layer."""
    words = _words(env) if words is None else words
    core = getattr(rule, "core", rule)
    consequence, scope = (_soft_consequence(rule, env, words)
                          if getattr(rule, "mode", "strict") == "default" else
                          _consequence(core, env, words))
    sentence = consequence
    if not isinstance(core.guard, ast.Top):
        sentence += ", if " + _guard_text(core.guard, env, words, scope)
    if len(core.unless) == 1:
        sentence += ", unless " + _guard_text(core.unless[0], env, words, scope)
    sentence += "."
    if len(core.unless) > 1:
        sentence += " " + " ".join("Except when " + _guard_text(u, env, words, scope) + "."
                                   for u in core.unless)
    return sentence


def render_english(document: NormDocument, *, handles=None, _w1=False):
    if not _w1 and _soft_surface.SOFT_PROFILE in document.env.profiles:
        return _render_soft_english(document, handles=handles)
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


@semantic_entry("english.statement")
def parse_english(env, source, manifest=None, *, existing_names=(), _w1=False):
    if not _w1 and _soft_surface.SOFT_PROFILE in env.profiles:
        return _parse_soft_english(env, source, manifest, existing_names=existing_names)
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
            precedence.setdefault(ast.numeral_value(standalone[1]), []).append(ast.numeral_value(standalone[2]))
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
        if m is None or ast.numeral_value(m[1]) != index:
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
        refs = tuple(ast.numeral_value(x) for x in re.findall(r"[0-9]+", m[2] or "")) + tuple(precedence.get(index, ()))
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
    try:
        document = NormDocument(env, rules)
    except VEError as exc:
        if (env.alternatives is not None and str(exc).startswith("DependencyCycle: ") and
                any(_mentions_outcome(formula, rule.predicate)
                    for rule in rules for formula in (rule.guard, *rule.unless))):
            raise VEError(f"{exc}; GuardOnOwnOutcome: A condition on this rule's own "
                          "predicate creates a cycle. An author may instead select a factual guard "
                          "like Rule 9: there is a robot such that that action is available to "
                          "that robot and every other action available to that robot injures a human being or "
                          "allows a harm to a human being to happen. This changes the rule's "
                          "meaning and does not track later rules that forbid those actions "
                          "for other reasons.") from exc
        raise
    if manifest is not None and manifest.get("document_hash") != document.document_hash:
        raise VEError("IdentityMetadataMismatch: norm document hash")
    return document


_SOFT_NOTE = re.compile(
    r"Rule ([1-9][0-9]*) (serves ([a-z][a-z0-9_]*)|is excepted (only )?when (.+))\.")
_SOFT_DECIDER = re.compile(r"The exception to rule ([1-9][0-9]*) is decided by (.+)\.", re.S)
_SOFT_FACTORS = re.compile(r"The exception to rule ([1-9][0-9]*) takes account of (.+)\.", re.S)
_SOFT_HEADER = re.compile(r"Rule ([1-9][0-9]*)(?: \(([^()]*)\))?\. (.*)\Z", re.S)


def _soft_consequence(rule, env, words):
    core = getattr(rule, "core", rule)
    strict, scope = _consequence(core, env, words)
    reg = env.predicates[core.predicate].regulated
    if getattr(rule, "mode", "strict") != "default":
        return strict, scope
    if reg.role == "plain":
        raise SyntaxError("A default rule needs a declared obligation or permission act")
    modal = ("should" if core.sign else "generally need not") if reg.role == "obligation" else (
        "generally may" if core.sign else "should not")
    strict_modal = ("must" if core.sign else "need not") if reg.role == "obligation" else (
        "may" if core.sign else "must not")
    return strict.replace(" " + strict_modal + " ", " " + modal + " ", 1), scope


def _soft_rewrite_consequence(sentence, env, words):
    """Find exactly one declared deontic reading and its W1 equivalent."""
    matches = []
    for name, decl in env.predicates.items():
        if decl.regulated is None:
            continue
        for sign in (True, False):
            base = Norm("candidate", name, sign, ast.Top())
            strict, _ = _consequence(base, env, words)
            candidates = [(strict, "strict")]
            _, nouns = _bindings(decl, words)
            if len(nouns) == 2:
                candidates.append((strict.replace("each " + nouns[1], "any " + nouns[1]), "strict"))
            if decl.regulated.role == "permission" and not sign:
                candidates.append((strict.replace("Every " + nouns[0] + " must not ",
                                                  "No " + nouns[0] + " may ", 1), "strict"))
            if decl.regulated.role != "plain":
                soft, _ = _soft_consequence(_soft_surface.SoftNorm(
                    "candidate", name, sign, ast.Top(), mode="default"), env, words)
                candidates.append((soft, "default"))
                if len(nouns) == 2:
                    candidates.append((soft.replace("each " + nouns[1], "any " + nouns[1]), "default"))
                if " should not " in soft:
                    candidates.append((soft.replace(" should not ", " generally must not ", 1), "default"))
                elif " should " in soft:
                    candidates.append((soft.replace(" should ", " generally must ", 1), "default"))
            for wording, mode in candidates:
                if sentence.casefold().startswith(wording.casefold()) and (
                    len(sentence) == len(wording) or sentence[len(wording):].startswith(", ")):
                    matches.append((name, sign, mode, wording, strict))
    if len(matches) != 1:
        if re.search(r"\b(?:normally|typically|usually|as a rule)\b", sentence, re.I):
            raise SyntaxError("Frequency wording has two readings; choose a default rule or a frequency claim")
        raise SyntaxError("Norm consequence has no single declared reading; use a declared act phrase")
    name, sign, mode, wording, strict = matches[0]
    return name, sign, mode, strict + sentence[len(wording):]


def _soft_note_parts(tail, number):
    """Separate W1 carve-outs from the soft annotations in one rule block."""
    markers = (" Rule ", " The exception to rule ")
    pos = min((tail.find(x) for x in markers if x in tail), default=-1)
    if pos < 0:
        return tail, ""
    return tail[:pos], tail[pos + 1:]


def _parse_soft_notes(notes, number, env, words, scope):
    result = {"rank": None, "decided_by": None, "sufficient": [], "necessary": [], "factors": []}
    if not notes:
        return result
    remaining = notes
    while remaining:
        quoted = escaped = False
        point = -1
        for index, char in enumerate(remaining):
            if escaped:
                escaped = False
            elif quoted and char == "\\":
                escaped = True
            elif char == '"':
                quoted = not quoted
            elif not quoted and remaining.startswith(". ", index):
                point = index
                break
        statement = remaining if point < 0 else remaining[:point + 1]
        remaining = "" if point < 0 else remaining[point + 2:]
        m = _SOFT_NOTE.fullmatch(statement)
        if m:
            if ast.numeral_value(m[1]) != number:
                raise SyntaxError("Soft annotation names another rule")
            if m[3] is not None:
                if result["rank"] is not None:
                    raise SyntaxError("Duplicate rank attribution")
                result["rank"] = m[3]
            else:
                key = "necessary" if m[4] else "sufficient"
                result[key].append(_parse_guard(m[5], env, words, scope))
            continue
        m = _SOFT_DECIDER.fullmatch(statement)
        if m and ast.numeral_value(m[1]) == number:
            if result["decided_by"] is not None:
                raise SyntaxError("Duplicate exception decider")
            if m[2].startswith('"'):
                try:
                    result["decided_by"] = json.loads(m[2])
                except ValueError as exc:
                    raise SyntaxError("Invalid quoted exception decider") from exc
                if type(result["decided_by"]) is not str:
                    raise SyntaxError("Invalid quoted exception decider")
            else:
                result["decided_by"] = m[2]
            continue
        m = _SOFT_FACTORS.fullmatch(statement)
        if m and ast.numeral_value(m[1]) == number:
            if result["factors"]:
                raise SyntaxError("Duplicate exception factors")
            # Canonical output quotes each factor, preserving embedded commas.
            # The source's natural list spelling is accepted for authoring.
            if m[2].startswith('"'):
                try:
                    result["factors"] = json.loads("[" + m[2] + "]")
                except (ValueError, TypeError) as exc:
                    raise SyntaxError("Invalid quoted exception factors") from exc
                if (type(result["factors"]) is not list or
                        any(type(factor) is not str for factor in result["factors"])):
                    raise SyntaxError("Invalid quoted exception factors")
            else:
                result["factors"] = [piece.strip() for piece in
                                     re.split(r", (?:and )?| and ", m[2])]
            continue
        raise SyntaxError(f"Unknown soft annotation {statement!r}")
    return result


def _parse_soft_english(env, source, manifest, *, existing_names):
    if type(source) is not str:
        raise SyntaxError("Norm English must be text")
    if manifest is not None and (type(manifest) is not dict or
                                 manifest.get("environment_id") != env.environment_id or
                                 manifest.get("text_digest") != hashlib.sha256(source.encode()).hexdigest()):
        raise VEError("IdentityMetadataMismatch: stale English export")
    words = _words(env)
    transformed = []
    metadata = []
    for line in source.split("\n") if source else []:
        if re.fullmatch(r"Rule [1-9][0-9]* takes precedence over rule [1-9][0-9]*\.", line):
            transformed.append(line)
            continue
        m = _SOFT_HEADER.fullmatch(line)
        if m is None:
            raise SyntaxError("Expected a numbered soft rule block")
        number = ast.numeral_value(m[1])
        refs, parties = _soft_surface.parse_header_options(m[2] or "")
        first, notes = _soft_note_parts(m[3], number)
        sentence_end = first.find(". ")
        consequence = first if sentence_end < 0 else first[:sentence_end + 1]
        carveouts = "" if sentence_end < 0 else first[sentence_end + 1:]
        if not consequence.endswith("."):
            raise SyntaxError("Expected a complete soft rule sentence")
        name, sign, mode, strict = _soft_rewrite_consequence(consequence[:-1], env, words)
        decl = env.predicates[name]
        scope, _ = _bindings(decl, words)
        fields = _parse_soft_notes(notes, number, env, words, scope)
        if mode == "strict" and (fields["decided_by"] is not None or fields["sufficient"] or
                                 fields["necessary"] or fields["factors"]):
            raise SyntaxError("A strict rule has no exception decision")
        header = ("Rule " + str(number) +
                  _soft_surface.render_header_options(refs, ()) + ". ")
        transformed.append(header + strict + "." + (" " + carveouts if carveouts else ""))
        metadata.append((mode, parties, fields))
    w1 = parse_english(env, "\n".join(transformed), None, existing_names=existing_names, _w1=True)
    if len(w1.rules) != len(metadata):
        raise SyntaxError("Soft annotation count does not match rule count")
    rules = []
    for rule, (mode, parties, fields) in zip(w1.rules, metadata):
        rules.append(_soft_surface.SoftNorm(
            rule.name, rule.predicate, rule.sign, rule.guard, rule.unless, rule.over,
            mode, fields["rank"], parties,
            (fields["decided_by"] or ("unstated" if mode == "default" and
             not getattr(env, "soft", {}).get("exception_decider") else None)),
            tuple(fields["sufficient"]), tuple(fields["necessary"]), tuple(fields["factors"])))
    if manifest is not None:
        blocks = [line for line in source.split("\n") if not re.fullmatch(
            r"Rule [1-9][0-9]* takes precedence over rule [1-9][0-9]*\.", line)]
        entries = manifest.get("blocks")
        if type(entries) is not list or len(entries) != len(rules):
            raise VEError("IdentityMetadataMismatch: block count")
        names = []
        handles = set()
        offset = 0
        for i, (block, entry) in enumerate(zip(blocks, entries), 1):
            if type(entry) is not dict or entry.get("number") != i or entry.get("span") != [offset, offset + len(block)]:
                raise VEError("IdentityMetadataMismatch: block mapping")
            handle = entry.get("handle")
            name = entry.get("name")
            if (type(handle) is not str or not handle or handle in handles or
                    type(name) is not str or name in names or name in existing_names):
                raise VEError("IdentityMetadataMismatch: block mapping")
            handles.add(handle)
            names.append(name)
            offset += len(block) + 1
        w1_positions = {rule.name: i for i, rule in enumerate(w1.rules)}
        restored = []
        for i, rule in enumerate(rules):
            restored.append(_soft_surface.SoftNorm(
                names[i], rule.predicate, rule.sign, rule.guard, rule.unless,
                tuple(names[w1_positions[parent]] for parent in rule.over),
                rule.mode, rule.rank, rule.alterable,
                rule.decided_by, rule.sufficient, rule.necessary, rule.factors,
                manifest["blocks"][i].get("hard", False) if manifest is not None else False))
        rules = restored
    from .softnorms import SoftEnvironment, SoftNormDocument
    soft_env = env if isinstance(env, SoftEnvironment) else SoftEnvironment(env.to_dict())
    try:
        document = SoftNormDocument(soft_env, [rule.to_dict() for rule in rules])
    except VEError as exc:
        if getattr(exc, "dual_guard_cycle", False):
            raise VEError(f"{exc}; DualGuardCycle: a soft decision introduces a guard dependency") from exc
        raise
    if manifest is not None and manifest.get("document_hash") != document.document_hash:
        raise VEError("IdentityMetadataMismatch: norm document hash")
    return document


def _render_soft_english(document, *, handles=None):
    from .softnorms import SoftNormDocument
    soft_hash = document.document_hash if isinstance(document, SoftNormDocument) else None
    if isinstance(document, SoftNormDocument):
        from .ast import _Decoder
        rules = []
        for source_rule in document.rules:
            core = source_rule.core
            exception = source_rule.exception or {}
            rules.append(_soft_surface.SoftNorm(
                core.name, core.predicate, core.sign, core.guard, core.unless, core.over,
                source_rule.mode, source_rule.rank, source_rule.alterable,
                exception.get("decided_by"),
                tuple(_Decoder().decode(x) for x in exception.get("sufficient", ())),
                tuple(_Decoder().decode(x) for x in exception.get("necessary", ())),
                tuple(exception.get("factors", ())), source_rule.hard))
        document = NormDocument(document.env, rules)
    text, manifest = render_english(document, handles=handles, _w1=True)
    words = _words(document.env)
    lines = []
    numbers = {rule.name: i for i, rule in enumerate(document.rules, 1)}
    for i, (line, rule) in enumerate(zip(text.split("\n"), document.rules), 1):
        m = _SOFT_HEADER.fullmatch(line)
        if m is None:
            raise SyntaxError("Invalid W1 rule block in soft export")
        consequence, _ = _consequence(rule, document.env, words)
        soft, scope = _soft_consequence(rule, document.env, words)
        body = m[3].replace(consequence, soft, 1)
        header = ("Rule " + str(i) +
                  _soft_surface.render_header_options(tuple(numbers[n] for n in rule.over),
                                                       tuple(getattr(rule, "alterable", ()))) + ". ")
        annotations = []
        rank = getattr(rule, "rank", None)
        if rank:
            annotations.append(f"Rule {i} serves {rank}.")
        if getattr(rule, "mode", "strict") == "default":
            decider = getattr(rule, "decided_by", None)
            if decider and (decider != "unstated" or
                            getattr(document.env, "soft", {}).get("exception_decider")):
                annotations.append(f"The exception to rule {i} is decided by " +
                                   json.dumps(decider, ensure_ascii=False) + ".")
            for formula in getattr(rule, "sufficient", ()):
                annotations.append(f"Rule {i} is excepted when {_guard_text(formula, document.env, words, scope)}.")
            for formula in getattr(rule, "necessary", ()):
                annotations.append(f"Rule {i} is excepted only when {_guard_text(formula, document.env, words, scope)}.")
            factors = getattr(rule, "factors", ())
            if factors:
                annotations.append(f"The exception to rule {i} takes account of " +
                                   ", ".join(json.dumps(f, ensure_ascii=False) for f in factors) + ".")
        lines.append(header + body + (" " + " ".join(annotations) if annotations else ""))
    source = "\n".join(lines)
    start = 0
    for entry, line in zip(manifest["blocks"], lines):
        entry["span"] = [start, start + len(line)]
        rule = document.rules[entry["number"] - 1]
        if getattr(rule, "hard", False):
            entry["hard"] = True
        start += len(line) + 1
    manifest["text_digest"] = hashlib.sha256(source.encode()).hexdigest()
    if soft_hash is None:
        from .softnorms import SoftEnvironment
        soft_env = document.env if isinstance(document.env, SoftEnvironment) else SoftEnvironment(document.env.to_dict())
        soft_hash = SoftNormDocument(soft_env, [rule.to_dict() for rule in document.rules]).document_hash
    manifest["document_hash"] = soft_hash
    return source, manifest
