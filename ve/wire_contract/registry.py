"""Registry of test-only wire contract hooks used by legacy profile contracts."""

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Callable

# The values of the input read during one run of the engine (`one_run`), as `Hooks.*.hooksFor` builds them in Lean.
_RUN = ContextVar("wire_contract_run", default=None)


@contextmanager
def one_run():
    """One run of the engine: `once` evaluates each value of the run's input at most once inside it."""
    token = _RUN.set({})
    try:
        yield
    finally:
        _RUN.reset(token)


def once(name, root, compute):
    """`compute(root)`, evaluated once per run for the root object `root` and kept, with what it raised, for the
    rest of the run (ap-1bfb review F2: 4.7 decoded the environment at every rule). Outside a run it is evaluated at
    each call. The root is held with its value, so its identity is not reused during the run."""
    memo = _RUN.get()
    if memo is None:
        return compute(root)
    hit = memo.get((name, id(root)))
    if hit is None or hit[0] is not root:
        try:
            hit = (root, compute(root), None)
        except Exception as exc:  # kept, so the run sees the same refusal at each read
            hit = (root, None, exc)
        memo[(name, id(root))] = hit
    if hit[2] is not None:
        raise hit[2]
    return hit[1]

@dataclass
class Registry:
    hooks: dict[str, Callable]
    classifiers: dict[str, Callable]
    views: dict[str, Callable]
    adapters: dict[str, Callable]

    def __init__(self):
        self.hooks, self.classifiers, self.views, self.adapters = {}, {}, {}, {}

    def register(self, *, hooks=None, classifiers=None, views=None, adapters=None):
        for attr, entries in (("hooks", hooks), ("classifiers", classifiers),
                              ("views", views), ("adapters", adapters)):
            if entries:
                getattr(self, attr).update(entries)
        return self
