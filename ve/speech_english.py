"""Deliberately narrow, single-reading English for experimental speech acts."""
from __future__ import annotations

import re

from .ast import _Checker, _Decoder, _to_data
from .backends.english_lean import QUESTION_CALLERS, SPEECH_CALLER, read_command, read_question
from .english import EnglishVocabulary, parse_english
from .environment import RESERVED
from .errors import VEError
from .speech_acts import ascii_fold, ascii_wording, wording_text


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


# The beginnings of the wordings Lean reads for the speech-acts caller, as its contract's `callers` lists them
# (`VE.Question.Run.speechPrefixes`): `Is it the case that ` (F1), `Must ` and `Can ` (refused with `ModalQuestion`)
# and F2's fronted `Is `.
_LEAN_PREFIXES = QUESTION_CALLERS[SPEECH_CALLER]


def _polar(env, text):
    """A polar question (F1 or F2), or a `Must` or `Can` wording, as Lean's `english.question` reads it for the
    speech-acts caller (docs/spec/question-answering-PLAN.md Q1.4): its formula, or Lean's refusal raised as Lean
    gives it."""
    from .english import EnglishVocabulary
    answer = read_question(env, text, EnglishVocabulary(env, _defer_overlay_refusals=True), {}, caller=SPEECH_CALLER)
    return {"mode": "polar", "body": answer["ast"]}, "question"


def parse_speech(env, source, scope, *, query=None, reading_set=None, warnings=None, unit="command", queries=()):
    """Return a typed wire content object and its kind; reject other wordings.

    A wording of no question form is a command, read by Lean (`read_command`, commands-imperatives CI-2) as the
    command `unit` of a document with the query records `queries`. Advisory lints (`OpaqueWording`) are appended to
    `warnings` when given.
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
    if text.startswith(_LEAN_PREFIXES):
        return _polar(env, text)
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
    if text.startswith("Which "):
        raise VEError("OpenDomainWhich: list the named alternatives")
    words = EnglishVocabulary(env, _defer_overlay_refusals=True)
    return read_command(env, text, words, {}, unit=unit, queries=list(queries))["reading"]["command"], "instruction"


def legend(env, lines):
    """The scope sentences as Lean wrote them (`VE.SpeechActs.Run.legend`, relayed in the source report), then
    norms' W1 default sentences."""
    from .norm_english import default_sentence
    return "\n".join([*lines, *(default_sentence(env, p) for p, d in env.predicates.items() if d.regulated is not None)])
