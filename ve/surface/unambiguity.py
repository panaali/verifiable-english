"""Admit English only after the complete Earley derivation check."""
from functools import lru_cache
import re
import signal
import threading

from ..errors import ResourceLimit, SyntaxError
from ..limits import MAX_NODES


@lru_cache(maxsize=32)
def _parser(grammar):
    from lark import Lark
    return Lark(grammar, parser="earley", lexer="dynamic_complete", ambiguity="explicit")


def require_unique_derivation(env, source, **options):
    from ..english import english_lark_grammar
    if len(source) > MAX_NODES:
        raise ResourceLimit(f"English derivation budget MAX_NODES ({MAX_NODES}) exhausted")
    grammar = english_lark_grammar(env, **options)
    # The handwritten parser folds the first letter of every sentence before
    # matching; the independent grammar must see the same lexical input.
    text = re.sub(r"(^|(?<=\.)\s+)([A-Z])", lambda match: match[1] + match[2].lower(), source)
    def timeout(_signum, _frame):
        raise ResourceLimit("English Earley time budget exhausted")
    timed = threading.current_thread() is threading.main_thread()
    if timed:
        previous = signal.getsignal(signal.SIGALRM)
        old_timer = signal.setitimer(signal.ITIMER_REAL, 30)
        signal.signal(signal.SIGALRM, timeout)
    try:
        tree = _parser(grammar).parse(text)
    except ResourceLimit:
        raise
    except Exception as exc:
        raise SyntaxError(f"English all-derivations check failed: {exc}") from exc
    finally:
        if timed:
            signal.setitimer(signal.ITIMER_REAL, *old_timer)
            signal.signal(signal.SIGALRM, previous)
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
    return tree


def require_correspondence(tree, readings, env, words) -> None:
    """Each handwritten extension result must be decoded from its grammar rule."""
    if not readings:
        return
    derived = []
    stack = [tree]
    records = [record for record, _ in readings]
    while stack:
        node = stack.pop()
        for record in records:
            if getattr(node, "data", None) == record.grammar_production:
                derived.append((record, record.derivation_hook(node, env, words)))
        stack.extend(getattr(node, "children", ()))
    for reading in readings:
        if reading not in derived:
            raise SyntaxError("English parser reading has no matching grammar derivation")
        derived.remove(reading)
