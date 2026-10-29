"""Deliberately narrow, single-reading English for experimental speech acts."""
from __future__ import annotations

from itertools import product
import re

from .ast import _Checker, _Decoder, _to_data
from .english import parse_english
from .environment import RESERVED
from .errors import VEError
from .speech_acts import act_verb, ascii_fold, ascii_wording, wording_text


def _formula(env, sentence):
    # An embedded formula is ASCII (3.2): P0's English never sees a character it would normalise.
    parsed = parse_english(env, ascii_wording(sentence))
    if len(parsed.formulas) != 1:
        raise VEError("Speech wording requires one sentence")
    return parsed.formulas[0]


def _name(env, text):
    matches = [name for name in env.constants if ascii_fold(name) == ascii_fold(text)]
    if len(matches) != 1:
        raise VEError(f"UnknownAlternative: wording, {text}")
    return matches[0]


# Words that make a wording a sentence rather than one predicate: W1's reserved
# words (connectives, negation, quantifiers, modals) and the other quantifier,
# negation, contrast and connective words of English that a property never needs.
_SENTENCE_WORDS = RESERVED | {
    "some", "all", "each", "any", "only", "unless", "none", "nor", "but", "both", "either", "neither", "nothing",
    "nobody", "everything", "without", "never", "nowhere", "noone", "yet", "although", "though",
    "however", "whereas", "while", "whilst", "except", "also", "nevertheless", "nonetheless", "otherwise", "instead",
    "else", "whether", "iff", "because", "plus", "versus", "vs", "always", "sometimes", "ever", "everyone",
    "everybody", "someone", "somebody", "something", "anyone", "anybody", "anything", "most", "few", "many"}


def _property_words(gloss):
    """The words of a one-place gloss after its subject and copula, or None for another shape."""
    if not gloss.startswith("{0} ") or "{" in gloss[4:]:
        return None
    words = [w.casefold() for w in re.findall(r"[A-Za-z0-9_']+", gloss[4:])]
    return words[1:] if words[:1] == ["is"] else words


def _opaque(env, rest):
    """The advisory lint of 2.1: a word suggesting a declared gloss hides a sentence, if any.

    A declared gloss is author-declared vocabulary, one atom whose English VE
    does not and cannot check, so this is a warning and never a gate, and the
    list is closed (2.1): a connective, negation, contrast or quantifier
    word; sentence punctuation; a word said twice; another declared property
    as a proper part; a declared constant or a bound definite phrase.
    """
    words = [w.casefold() for w in re.findall(r"[A-Za-z0-9_']+", rest)][1:]  # after the copula "is"
    if (mark := re.search(r"[^A-Za-z0-9_' -]", rest)) is not None:
        return mark[0]
    constants = {name.casefold() for name in env.constants}
    padded = " " + " ".join(words) + " "
    for i, word in enumerate(words):
        if word in _SENTENCE_WORDS or word.endswith("n't") or word in constants or word in words[:i]:
            return word
    for decl in env.predicates.values():
        inner = _property_words(decl.verbalisation) if decl.verbalisation is not None else None
        if inner and inner != words and " " + " ".join(inner) + " " in padded:
            return " ".join(inner)
    for phrase in (env.speech_acts or {}).get("definites", {}):
        if " " + phrase.casefold() + " " in padded:
            return phrase
    return None


def _copular(env, name, rest, warnings=None):
    """Match a declared unary copula without asking P0 to parse a question.

    A matching gloss is read as its one declared predicate; the lint of
    `_opaque` only adds an `OpaqueWording` warning to `warnings`.
    """
    from .ast import Const, Unary
    matches = [Unary(predicate, Const(name)) for predicate, decl in env.predicates.items()
               if len(decl.arguments) == 1 and decl.arguments[0] == env.constants[name].sort
               and decl.verbalisation is not None
               and ascii_fold(decl.verbalisation) == ascii_fold("{0} " + rest)]
    if matches and warnings is not None and (hidden := _opaque(env, rest)) is not None:
        warnings.append(f"OpaqueWording: '{rest}' contains '{hidden}' and is read as one declared predicate")
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise VEError("AmbiguousDerivation: copular question")
    return _formula(env, f"@{name} {rest}.")


def _sentence(env, source, warnings=None):
    match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_]*) (is .+)\.", ascii_wording(source))
    if match:
        try:
            return _copular(env, _name(env, match[1]), match[2], warnings)
        except VEError:
            pass
    return _formula(env, source)


def _body(env, alternative, rest, warnings=None):
    # Parse a complete existing English sentence first, then abstract exactly
    # the named alternative.  This retains P0's one-reading grammar check.
    formula = _copular(env, alternative, rest, warnings)
    data = _to_data(formula)
    def abstract(node):
        if type(node) is list:
            if node == ["const", alternative]:
                return ["var", 0]
            return [abstract(x) for x in node]
        return node
    result = _Decoder().decode(abstract(data))
    _Checker(env).formula(result, (env.constants[alternative].sort,))
    return _to_data(result)


def _alternatives(text):
    names = [wording_text(s) for s in re.split(r", | and ", text)]
    if not 2 <= len(names) <= 16 or any(not name for name in names):
        raise VEError("OpenDomainWhich: name two to sixteen alternatives")
    return names


def _command_candidates(env, scope):
    """Enumerate declared act phrases with bound names and definite synonyms."""
    for predicate, decl in env.predicates.items():
        reg = decl.regulated
        # An imperative begins with its act's verb (3.2): an act whose first word after `{0}` is a slot has none.
        if reg is None or reg.role not in ("obligation", "permission") or act_verb(reg.act) is None:
            continue
        names = []
        for sort in decl.arguments[1:]:
            choices = []
            for name, constant in env.constants.items():
                if constant.sort == sort:
                    choices.append((name, name))
                    choices.extend((phrase, name) for phrase, bound in scope.get("definites", {}).items()
                                   if bound == name)
            names.append(choices)
        for bindings in product(*names):
            display = [None, *(label for label, _ in bindings)]
            phrase = reg.act[4:].format(*display)
            yield phrase, predicate, tuple(value for _, value in bindings), reg.role


def parse_speech(env, source, scope, *, query=None, reading_set=None, warnings=None):
    """Return a typed wire content object and its kind; reject other wordings.

    Advisory lints (`OpaqueWording`) are appended to `warnings` when given.
    """
    if type(source) is not str:
        raise VEError("InvalidInput: speech wording")
    text = wording_text(source)
    if not text:
        raise VEError("InvalidInput: speech wording")
    if text == "Which reading did you mean?":
        if reading_set is None:
            raise VEError("InvalidInput: reading set required")
        return {"mode": "reading", "set": reading_set[0], "version": reading_set[1]}, "question"
    if text.startswith("Does it follow from these premises that ") and text.endswith("?"):
        if query is None:
            raise VEError("InvalidInput: query required")
        _sentence(env, text[len("Does it follow from these premises that "):-1] + ".", warnings)
        return {"mode": "follows", "query": query}, "question"
    if text.startswith("Is it the case that ") and text.endswith("?"):
        formula = _formula(env, text[len("Is it the case that "):-1] + ".")
        return {"mode": "polar", "body": _to_data(formula)}, "question"
    match = re.fullmatch(r"Is ([A-Za-z][A-Za-z0-9_]*) (.+)\?", text)
    if match:
        name = _name(env, match[1])
        return {"mode": "polar", "body": _to_data(_copular(env, name, "is " + match[2], warnings))}, "question"
    for mode, pattern in (("which_one", r"Which one of (.+) is (.+)\?"),
                          ("which_all", r"Which of (.+) are (.+)\?")):
        match = re.fullmatch(pattern, text)
        if match:
            domain = [_name(env, name) for name in _alternatives(match[1])]
            sort = env.constants[domain[0]].sort
            if any(env.constants[name].sort != sort for name in domain):
                raise VEError("AlternativeSort: wording")
            rest = "is " + match[2]
            return {"mode": mode, "sort": sort, "domain": domain,
                    "body": _body(env, domain[0], rest, warnings)}, "question"
    if text.startswith("Must ") or text.startswith("Can "):
        raise VEError("ModalQuestion: choose an explicit question")
    if text.startswith("Which "):
        raise VEError("OpenDomainWhich: list the named alternatives")
    if text.startswith("You may "):
        raise VEError("PermissionNotCommand: use an equality-guarded W1 rule")
    if text.startswith("Please "):
        raise VEError("InvalidInput: please needs author approval")
    if " and " in text and not text.startswith("Do not "):
        # A conjunction may be inside a declared act. Check matching phrases
        # before issuing this diagnostic.
        coordinated = True
    else:
        coordinated = False
    if text.startswith("Prove that ") and text.endswith(" using these premises."):
        if query is None:
            raise VEError("InvalidInput: query required")
        _sentence(env, text[len("Prove that "):-len(" using these premises.")] + ".", warnings)
        from .speech_acts import PROOF_TASK_ACT
        candidates = [(name, decl) for name, decl in env.predicates.items()
                      if decl.regulated is not None and decl.regulated.role == "obligation"
                      and decl.regulated.act == PROOF_TASK_ACT and decl.arguments[1:] == ("query",)]
        if len(candidates) != 1:
            raise VEError(f"MissingObligationRole: {PROOF_TASK_ACT}")
        return {"force": "require", "act": candidates[0][0], "args": [query], "guard": ["top"]}, "instruction"
    if text.endswith("."):
        plain = text[:-1]
        condition = None
        if ", if " in plain:
            plain, condition = plain.rsplit(", if ", 1)
        forbidden = plain.startswith("Do not ")
        if forbidden:
            plain = plain[len("Do not "):]
        matches = []
        wrong_role = []
        for phrase, predicate, args, role in _command_candidates(env, scope):
            if ascii_fold(plain) == ascii_fold(phrase):
                if role == ("permission" if forbidden else "obligation"):
                    matches.append((predicate, args, role))
                else:
                    wrong_role.append(predicate)
        matches = list(dict.fromkeys(matches))
        if len(matches) == 1:
            predicate, args, role = matches[0]
            if role != ("permission" if forbidden else "obligation"):
                raise VEError(f"Missing{'Permission' if forbidden else 'Obligation'}Role: {env.predicates[predicate].regulated.act}")
            guard = _to_data(_formula(env, condition + ".")) if condition else ["top"]
            return {"force": "forbid" if forbidden else "require", "act": predicate,
                    "args": list(args), "guard": guard}, "instruction"
        if len(matches) > 1:
            raise VEError("AmbiguousDerivation: multiple declared acts match")
        if wrong_role:
            raise VEError(f"Missing{'Permission' if forbidden else 'Obligation'}Role: {env.predicates[wrong_role[0]].regulated.act}")
    if coordinated:
        raise VEError("CoordinatedActs: split into two commands")
    raise VEError("InvalidInput: no single speech-act reading")


def legend(env):
    scope = env.speech_acts
    result = [f"This document is task {scope['task']}."]
    if "addressee" in scope:
        result.append(f"In this task, you are {scope['addressee']['constant']}.")
    for phrase, constant in sorted(scope.get("definites", {}).items()):  # Lean's canonical order
        result.append(f"In this task, {phrase} is {constant}.")
    from .norm_english import default_sentence
    result.extend(default_sentence(env, p) for p, d in env.predicates.items() if d.regulated is not None)
    return "\n".join(result)
