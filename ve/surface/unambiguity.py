"""Admit English only after the complete Earley derivation check."""
from functools import lru_cache
import re
import inspect
import signal
import sys
import threading
import time

from lark.exceptions import LarkError

from ..errors import ResourceLimit, SyntaxError
from ..limits import MAX_NODES

EARLEY_SECONDS = 30


@lru_cache(maxsize=32)
def _parser(grammar):
    from lark import Lark
    return Lark(grammar, parser="earley", lexer="dynamic_complete", ambiguity="explicit",
                propagate_positions=True)


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
    # Leave an existing host alarm alone. A trace can enforce our deadline
    # while the host's timer and handler retain their original schedule.
    use_signal = (threading.current_thread() is threading.main_thread()
                  and signal.getitimer(signal.ITIMER_REAL)[0] == 0)
    if use_signal:
        previous = signal.getsignal(signal.SIGALRM)
        signal.signal(signal.SIGALRM, timeout)
        old_timer = signal.setitimer(signal.ITIMER_REAL, EARLEY_SECONDS)
    else:
        previous_trace = sys.gettrace()
        started = time.monotonic()
        def trace(_frame, _event, _arg):
            if time.monotonic() - started > EARLEY_SECONDS:
                raise ResourceLimit("English Earley time budget exhausted")
            return trace
        sys.settrace(trace)
    try:
        tree = _parser(grammar).parse(text)
    except ResourceLimit:
        raise
    # A host SIGALRM handler may raise an ordinary Exception. Let it escape.
    except LarkError as exc:
        raise SyntaxError(f"English all-derivations check failed: {exc}") from exc
    finally:
        if use_signal:
            signal.setitimer(signal.ITIMER_REAL, *old_timer)
            signal.signal(signal.SIGALRM, previous)
        else:
            sys.settrace(previous_trace)
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


def require_correspondence(tree, readings, env, words, source=None) -> None:
    """Each extension result must match the grammar rule at its source span."""
    if not readings:
        return
    derived = []
    stack = [tree]
    records = list({reading[0].wire_tag: reading[0] for reading in readings}.values())
    while stack:
        node = stack.pop()
        for record in records:
            if getattr(node, "data", None) == record.grammar_production:
                meta = getattr(node, "meta", None)
                hook = record.derivation_hook
                value = (hook(node, env, words, source)
                         if len(inspect.signature(hook).parameters) == 4
                         else hook(node, env, words))
                derived.append((record, value,
                                getattr(meta, "start_pos", None), getattr(meta, "end_pos", None)))
        stack.extend(getattr(node, "children", ()))
    for reading in readings:
        if reading not in derived:
            raise SyntaxError("English parser reading has no matching grammar derivation")
        derived.remove(reading)
