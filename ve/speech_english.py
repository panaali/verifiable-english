"""Deliberately narrow, single-reading English for experimental speech acts."""
from __future__ import annotations

from itertools import product
import re

from .ast import _Checker, _Decoder, _to_data
from .english import parse_english
from .environment import RESERVED
from .errors import VEError


def _formula(env, sentence):
    parsed = parse_english(env, sentence)
    if len(parsed.formulas) != 1:
        raise VEError("Speech wording requires one sentence")
    return parsed.formulas[0]


def _name(env, text):
    matches = [name for name in env.constants if name.casefold() == text.casefold()]
    if len(matches) != 1:
        raise VEError(f"UnknownAlternative: wording, {text}")
    return matches[0]


# Words that make a wording a sentence rather than one predicate: W1's reserved
# words (connectives, negation, quantifiers, modals) and the other quantifier and
# connective words of the English surface.
_SENTENCE_WORDS = RESERVED | {"some", "all", "each", "any", "only", "unless", "none", "nor", "but", "both",
                              "either", "neither", "nothing", "nobody", "everything", "without"}


def _opaque(env, rest):
    """The sentence a declared gloss would hide behind one predicate (6), if any.

    A copular gloss may only name a property: a connective, negation or
    quantifier word, a declared constant or a bound definite phrase inside it
    is a sentence the gloss would answer as one opaque atom.
    """
    words = [w.casefold() for w in re.findall(r"[A-Za-z0-9_']+", rest)][1:]  # after the copula "is"
    constants = {name.casefold() for name in env.constants}
    padded = " " + " ".join(words) + " "
    for word in words:
        if word in _SENTENCE_WORDS or word.endswith("n't") or word in constants:
            return word
    for phrase in (env.speech_acts or {}).get("definites", {}):
        if " " + phrase.casefold() + " " in padded:
            return phrase
    return None


def _copular(env, name, rest):
    """Match a declared unary copula without asking P0 to parse a question."""
    from .ast import Const, Unary
    matches = [Unary(predicate, Const(name)) for predicate, decl in env.predicates.items()
               if len(decl.arguments) == 1 and decl.arguments[0] == env.constants[name].sort
               and decl.verbalisation is not None
               and decl.verbalisation.casefold() == ("{0} " + rest).casefold()]
    if matches and (hidden := _opaque(env, rest)) is not None:
        raise VEError(f"OpaqueWording: '{rest}' is a sentence about '{hidden}', not one declared property")
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise VEError("AmbiguousDerivation: copular question")
    return _formula(env, f"@{name} {rest}.")


def _sentence(env, source):
    match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_]*) (is .+)\.", source)
    if match:
        try:
            return _copular(env, _name(env, match[1]), match[2])
        except VEError as exc:
            if str(exc).startswith("OpaqueWording"):
                raise
    return _formula(env, source)


def _body(env, alternative, rest):
    # Parse a complete existing English sentence first, then abstract exactly
    # the named alternative.  This retains P0's one-reading grammar check.
    formula = _copular(env, alternative, rest)
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
    names = [s.strip() for s in re.split(r", | and ", text)]
    if not 2 <= len(names) <= 16 or any(not name for name in names):
        raise VEError("OpenDomainWhich: name two to sixteen alternatives")
    return names


def _command_candidates(env, scope):
    """Enumerate declared act phrases with bound names and definite synonyms."""
    for predicate, decl in env.predicates.items():
        reg = decl.regulated
        if reg is None or reg.role not in ("obligation", "permission"):
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
            phrase = reg.act[4:].format(*display).strip()
            if phrase:
                phrase = phrase[0].upper() + phrase[1:]
            yield phrase, predicate, tuple(value for _, value in bindings), reg.role


def parse_speech(env, source, scope, *, query=None, reading_set=None):
    """Return a typed wire content object and its kind; reject other wordings."""
    if type(source) is not str:
        raise VEError("InvalidInput: speech wording")
    text = source.strip()
    if not text:
        raise VEError("InvalidInput: speech wording")
    if text == "Which reading did you mean?":
        if reading_set is None:
            raise VEError("InvalidInput: reading set required")
        return {"mode": "reading", "set": reading_set[0], "version": reading_set[1]}, "question"
    if text.startswith("Does it follow from these premises that ") and text.endswith("?"):
        if query is None:
            raise VEError("InvalidInput: query required")
        _sentence(env, text[len("Does it follow from these premises that "):-1] + ".")
        return {"mode": "follows", "query": query}, "question"
    if text.startswith("Is it the case that ") and text.endswith("?"):
        formula = _formula(env, text[len("Is it the case that "):-1] + ".")
        return {"mode": "polar", "body": _to_data(formula)}, "question"
    match = re.fullmatch(r"Is ([A-Za-z][A-Za-z0-9_]*) (.+)\?", text)
    if match:
        name = _name(env, match[1])
        return {"mode": "polar", "body": _to_data(_copular(env, name, "is " + match[2]))}, "question"
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
                    "body": _body(env, domain[0], rest)}, "question"
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
        _sentence(env, text[len("Prove that "):-len(" using these premises.")] + ".")
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
            plain = plain[:1].upper() + plain[1:]
        matches = []
        wrong_role = []
        for phrase, predicate, args, role in _command_candidates(env, scope):
            if plain.casefold() == phrase.casefold():
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
    for phrase, constant in scope.get("definites", {}).items():
        result.append(f"In this task, {phrase} is {constant}.")
    from .norm_english import default_sentence
    result.extend(default_sentence(env, p) for p, d in env.predicates.items() if d.regulated is not None)
    return "\n".join(result)
