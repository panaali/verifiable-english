"""English authoring of identity-bound definitions and document glossaries.

Two sentence forms, both regular English (VISION: zero-training English):

* a definition, "By definition, for every person, that person is lead exactly
  when both that person is boss and that person is senior.";
* a glossary of synonyms, "In this document, staff, employees and personnel
  mean the same thing." Each later word becomes an alias definition of the
  first (W3, conservative); documents keep the author's word choice because
  every word stays its own predicate.

Neither form is a new statement grammar. A definition sentence is split at its
only "exactly when" into a head and a body sharing the same "for every"
binders; each part is then parsed as an ordinary closed English statement, so
each passes the complete all-derivations check. The split points are unique
because no declared wording may contain them (checked). The sentences change
the vocabulary, so they produce a new environment version (a new
environment_id); documents pin that version.
"""
from __future__ import annotations

from copy import deepcopy
import re

from .. import ast
from ..ast import Document
from ..definitions import Definition, _atom, compile_definitions, premise
from ..english import EnglishTraversal, EnglishVocabulary, _max_scope, parse_english, render_english
from ..environment import Environment
from ..errors import VEError
from ..printer import print_document

DEFINITION_PREFIX = "By definition, "
EXACTLY = " exactly when "
GLOSSARY_PREFIX = "In this document, "
GLOSSARY_SUFFIX = " mean the same thing."


def _outside_quotes(text: str, needle: str) -> list[int]:
    """Start offsets of `needle` outside double-quoted symbol names."""
    masked = re.sub(r'"(?:[^"\\]|\\.)*"', lambda m: "\0" * len(m[0]), text)
    return [m.start() for m in re.finditer(re.escape(needle), masked)]


def _quantified(arguments, body):
    for sort in reversed(arguments):
        body = ast.Forall(sort, body)
    return body


def _check_wordings(words: EnglishVocabulary, separators) -> None:
    """The sentence split points are unique only if no wording contains them."""
    for name, template in [*words.predicates.items(), *words.negatives.items()]:
        for separator in separators:
            if separator in template:
                raise VEError(f"The wording of {name!r} contains {separator.strip()!r}; "
                              "definition sentences need wordings without it")


def render_definition(env: Environment, definition: Definition) -> str:
    """The definition sentence: shared binders, the defined atom, then the body."""
    words = EnglishVocabulary(env)
    traversal = EnglishTraversal(env, words)
    traversal.maximum = _max_scope(_quantified(definition.arguments, definition.body))
    scope, prefix = (), ""
    for sort in definition.arguments:
        binding, noun = traversal.binding(sort, scope)
        scope = (binding, *scope)
        prefix += "for every " + noun + ", "
    head = traversal.formula(_atom(definition.name, len(definition.arguments)), scope)
    body = traversal.formula(definition.body, scope)
    return DEFINITION_PREFIX + prefix + head + EXACTLY + body + ".\n"


def parse_definition(env: Environment, sentence: str) -> Definition:
    """One definition sentence over `env`, which declares the defined predicate
    (with or without a body yet). The result is checked when adopted."""
    words = EnglishVocabulary(env)
    _check_wordings(words, ("exactly when", ", "))
    text = sentence.strip()
    if not text.startswith(DEFINITION_PREFIX) or not text.endswith("."):
        raise VEError(f"A definition sentence starts with {DEFINITION_PREFIX.strip()!r} and ends with a period")
    text = text[len(DEFINITION_PREFIX):-1]
    splits = _outside_quotes(text, EXACTLY)
    if len(splits) != 1:
        raise VEError("A definition sentence contains 'exactly when' exactly once")
    left, body_text = text[:splits[0]], text[splits[0] + len(EXACTLY):]
    cut = left.rfind(", ")
    if not left.startswith("for every ") or cut < 0:
        raise VEError("A definition sentence introduces its arguments with 'for every'")
    prefix, head_text = left[:cut + 2], left[cut + 2:]
    head_doc = parse_english(env, prefix + head_text + ".")
    body_doc = parse_english(env, prefix + body_text + ".")
    if len(head_doc.formulas) != 1 or len(body_doc.formulas) != 1:
        raise VEError("A definition sentence has exactly one head and one body statement")
    head, body = head_doc.formulas[0], body_doc.formulas[0]
    arguments = []
    while type(head) is ast.Forall and type(body) is ast.Forall and head.sort == body.sort:
        arguments.append(head.sort)
        head, body = head.body, body.body
    if type(head) not in (ast.Unary, ast.Binary) or len(arguments) not in (1, 2):
        raise VEError("The part before 'exactly when' must be one defined atom over the "
                      "'for every' arguments")
    definition = Definition(head.predicate, tuple(arguments), body)
    if head != _atom(definition.name, len(arguments)) or env.predicates.get(
            definition.name) is None or env.predicates[definition.name].arguments != tuple(arguments):
        raise VEError("The defined atom must apply the predicate to the 'for every' arguments in order")
    return definition


def _phrases(env: Environment, words: EnglishVocabulary) -> dict[str, set[str]]:
    """Glossary words for each predicate: its identifier, its quoted name and
    its wording without the subject slot, the verb 'is' and an article."""
    phrases: dict[str, set[str]] = {}
    for name, template in words.predicates.items():
        options = {name, '"' + name + '"'}
        phrase = template.removeprefix("{0} ").removesuffix(" {1}")
        options.add(phrase)
        bare = re.sub(r"^is (?:an? )?", "", phrase)
        options.add(bare)
        for word in (bare, name):  # "employees" for "is an employee" or `employee`
            if re.fullmatch(r"[a-z]+", word):
                options.add(word + ("es" if word.endswith(("s", "x", "ch", "sh")) else "s"))
        for option in options:
            phrases.setdefault(option, set()).add(name)
    return phrases


def parse_glossary(env: Environment, sentence: str) -> tuple[str, ...]:
    """The predicates a glossary sentence names, first the reference word."""
    text = sentence.strip()
    if not text.startswith(GLOSSARY_PREFIX) or not text.endswith(GLOSSARY_SUFFIX):
        raise VEError("A glossary sentence reads 'In this document, A, B and C mean the same thing.'")
    listed = text[len(GLOSSARY_PREFIX):-len(GLOSSARY_SUFFIX)]
    parts = re.split(r", and |, | and ", listed)
    phrases = _phrases(env, EnglishVocabulary(env))
    for phrase in phrases:
        if (", " in phrase or " and " in phrase) and phrase in parts:
            raise VEError(f"The wording {phrase!r} contains a list separator")
    names = []
    for part in parts:
        found = phrases.get(part, set())
        if len(found) != 1:
            raise VEError(f"Glossary word {part!r} names {'no' if not found else 'more than one'} "
                          "declared predicate")
        names.append(next(iter(found)))
    if len(names) < 2 or len(set(names)) != len(names):
        raise VEError("A glossary sentence lists at least two different words")
    signatures = {env.predicates[name].arguments for name in names}
    if len(signatures) != 1:
        raise VEError("Glossary words must have the same argument sorts")
    return tuple(names)


def _check_lemma_names(names) -> None:
    for name in names:
        if type(name) is not str or re.fullmatch(r"[A-Za-z0-9_.-]+", name) is None or not name[0].isalnum():
            raise VEError(f"Lemma name {name!r} cannot be cited in English")


def render_citation(env: Environment, cited, conclusion) -> str:
    """'By T7a and T7b, <the conclusion>.' The conclusion is one ordinary
    English statement; lemmas are cited by their stable names."""
    cited = list(cited)
    _check_lemma_names(cited)
    statement = render_english(Document((conclusion,)), env)
    if not cited:
        return statement
    names = cited[0] if len(cited) == 1 else ", ".join(cited[:-1]) + " and " + cited[-1]
    return "By " + names + ", " + statement[0].lower() + statement[1:]


def parse_citation(env: Environment, sentence: str, lemma_names) -> tuple[tuple[str, ...], ast.Formula]:
    """The cited lemma names and the conclusion of a citation sentence. The
    names end at the comma before the conclusion, and the
    conclusion passes the complete all-derivations check."""
    _check_lemma_names(lemma_names)
    text = sentence.strip()
    cited: tuple[str, ...] = ()
    if text.startswith("By "):
        names = set(lemma_names)
        match = re.match(r"By ([A-Za-z0-9_.-]+(?:, [A-Za-z0-9_.-]+)* and [A-Za-z0-9_.-]+|[A-Za-z0-9_.-]+), ", text)
        if match is None:
            raise VEError("A citation reads 'By T1 and T2, <statement>.'")
        cited = tuple(re.split(r", | and ", match[1]))
        unknown = [name for name in cited if name not in names]
        if unknown:
            raise VEError(f"Citation names an unknown lemma: {unknown[0]}")
        text = text[match.end():]
    document = parse_english(env, text)
    if len(document.formulas) != 1:
        raise VEError("A citation sentence has one conclusion")
    return cited, document.formulas[0]


def _sentences(text: str) -> list[str]:
    chunks = re.split(r"(?m)^(?=By definition, |In this document, )", text)
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def adopt(env_json: dict, text: str) -> dict:
    """A new environment version with the sentences' definitions bound into the
    vocabulary (`definitions@0` added). The result is re-checked: every body is
    typed below its symbol, the DAG is acyclic, and every definition renders
    back to a sentence with one reading."""
    raw = deepcopy(env_json)
    if "definitions@0" not in raw["profiles"]:
        raw["profiles"] = sorted({*raw["profiles"], "definitions@0"})
    env = Environment(raw)
    predicates = raw["vocabulary"]["predicates"]
    for sentence in _sentences(text):
        if sentence.startswith(GLOSSARY_PREFIX):
            names = parse_glossary(env, sentence)
            reference, aliases = names[0], names[1:]
            arity = len(env.predicates[reference].arguments)
            definitions = [Definition(alias, env.predicates[alias].arguments, _atom(reference, arity))
                           for alias in aliases]
        else:
            definitions = [parse_definition(env, sentence)]
        for definition in definitions:
            entry = predicates[definition.name]
            if "defined" in entry:
                raise VEError(f"{definition.name!r} is already defined in this vocabulary version")
            entry["defined"] = {"arguments": list(definition.arguments),
                                "body": ast._to_data(definition.body)}
        env = Environment(raw)
    wordings(env)
    return raw


def wordings(env: Environment) -> tuple[dict, ...]:
    """Render each definition as a sentence and verify it reads back uniquely."""
    if not env.definition_entries:
        return ()
    result = []
    for definition in compile_definitions(env, env.definition_entries, version=env.environment_id):
        english = render_definition(env, definition)
        if parse_definition(env, english) != definition:
            raise VEError(f"English definition wording has another reading: {definition.name}")
        document = Document((premise(definition),))
        result.append({"predicate": definition.name, "english": english,
                       "biconditional": render_english(document, env),
                       "strict": print_document(env, document)})
    return tuple(result)
