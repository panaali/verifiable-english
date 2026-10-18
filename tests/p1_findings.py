"""The P1 items' reference findings, checked several at a time, once per process.

`experiments/p1.py` (frozen with the P1 preregistration) checks an item's argument the first time a test renders
or requests it (`p1.finding`), and keeps the finding for the process (`p1._finding`, an `lru_cache` holding exactly
the 200 items). Each item's check is independent of every other item's: its reference replay, its witness and its
record, each failing with `PreflightError`. Those checks were nearly all of the heavy P1 tests' time: the first
test in a process that requests every item (`p1.known_answer()`, the token-bound fixtures) ran 200 of them one
after another, 98% of `known_answer`'s time.

`warm` runs the same checks through the same function and cache, `THREADS` items at a time, so the tests that
follow read exactly the findings they read before (an item whose check fails raises its error here, as it would
there). The concurrency is the checks' own: each waits on the pooled Lean services, the Rust checker pool and
the one-shot Lean runs, all of which serve concurrent callers.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import contextvars

from experiments import p1

THREADS = 4


def items(*splits: str) -> list[dict]:
    """The items of `splits` (both when none is named), in `p1.materials` order."""
    return [item for split in splits or ("dev", "scored") for item in p1.materials(split)]


def warm(*splits: str) -> None:
    """Check every item of `splits` (both when none is named) into `p1`'s per-process cache."""
    todo = items(*splits)
    # One copy of this thread's context per item: an authority the test pinned holds in every check.
    contexts = [contextvars.copy_context() for _ in todo]
    with ThreadPoolExecutor(THREADS) as pool:
        for _ in pool.map(lambda context, item: context.run(p1.finding, item), contexts, todo):
            pass
