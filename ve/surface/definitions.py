"""One-reading English previews of identity-bound definitions."""
from __future__ import annotations

from ..ast import Document
from ..definitions import compile_definitions, premise
from ..english import parse_english, render_english
from ..environment import Environment
from ..errors import VEError
from ..printer import print_document


def wordings(env: Environment) -> tuple[dict, ...]:
    """Render each definition's biconditional and verify unique English parsing."""
    if not env.definition_entries:
        return ()
    result = []
    for definition in compile_definitions(env, env.definition_entries, version=env.environment_id):
        document = Document((premise(definition),))
        english = render_english(document, env)
        if parse_english(env, english) != document:
            raise VEError(f"English definition wording has another reading: {definition.name}")
        result.append({"predicate": definition.name, "english": english,
                       "strict": print_document(env, document)})
    return tuple(result)
