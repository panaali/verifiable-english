"""Admit English only after the complete Earley derivation check."""
from functools import lru_cache
import re

from ..errors import ResourceLimit, SyntaxError
from ..limits import MAX_NODES


@lru_cache(maxsize=32)
def _parser(grammar):
    from lark import Lark
    return Lark(grammar, parser="earley", lexer="dynamic_complete", ambiguity="explicit")


def require_unique_derivation(env, source, **options) -> None:
    from ..english import english_lark_grammar
    if len(source) > MAX_NODES:
        raise ResourceLimit(f"English derivation budget MAX_NODES ({MAX_NODES}) exhausted")
    grammar = english_lark_grammar(env, **options)
    # The handwritten parser folds the first letter of every sentence before
    # matching; the independent grammar must see the same lexical input.
    text = re.sub(r"(^|(?<=\.)\s+)([A-Z])", lambda match: match[1] + match[2].lower(), source)
    try:
        tree = _parser(grammar).parse(text)
    except Exception as exc:
        raise SyntaxError(f"English all-derivations check failed: {exc}") from exc
    stack = [tree]
    count = 0
    while stack:
        node = stack.pop()
        count += 1
        if count > MAX_NODES:
            raise ResourceLimit(f"English derivation budget MAX_NODES ({MAX_NODES}) exhausted")
        if getattr(node, "data", None) == "_ambig":
            first, second = node.children[:2]
            raise SyntaxError("English has two derivations:\n" + first.pretty()[:1000]
                              + "\n---\n" + second.pretty()[:1000])
        stack.extend(getattr(node, "children", ()))
