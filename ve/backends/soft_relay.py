"""Lean's soft route at the Python boundary."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import threading
import weakref

from ..errors import CheckerUnavailable, VEError
from .relay import _pool_for, decide, decide_once

# The quoted rules Lean accepted, per pool and per lower soft source (docs/LEAN-FIRST-PLAN.md, batch 6).
# A rule check is a pure function of the source and the rule, and `soft-rules` checks each rule on its
# own, so a rule accepted once under a source is accepted by every later request for it. Readings and
# rights rebuild the same document once per candidate; each rebuild sends only the rules no earlier
# request has checked. A rejected rule is never kept. Another pool (another build) starts empty.
_accepted: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()
_accepted_lock = threading.Lock()
ACCEPTED_SOURCES = 64


def _text(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def wire(value):
    """The restricted Lean wire spells optional null fields by omission."""
    if type(value) is dict:
        return {key: wire(item) for key, item in value.items() if item is not None}
    if type(value) is list:
        return [wire(item) for item in value]
    return value


def run(case):
    """Return a Lean soft row, retaining its diagnostic on a rejection."""
    try:
        if case.get("kind") in ("soft-elaborate", "soft-rule", "soft-rules"):
            # Both are pure source checks. Repeated rights correlation sends the
            # same large source and rules many times; keep Lean's bound answer,
            # and give each caller an independent display row.
            return deepcopy(decide_once("soft-norms", case))
        return decide("soft-norms", [case])[0]
    except VEError as error:
        if case.get("kind") in ("soft-elaborate", "admission"):
            diagnosed = decide("diagnose", [{**case, "unit": "soft-norms@0"}])[0]
            if diagnosed.get("outcome") == "fault":
                error.diagnostic = diagnosed["diagnostic"]
        raise


def _accepted_for(source_text: str) -> set:
    digest = hashlib.sha256(source_text.encode()).hexdigest()
    with _accepted_lock:
        sources = _accepted.setdefault(_pool_for(None), {})
        if digest not in sources and len(sources) >= ACCEPTED_SOURCES:
            sources.clear()
        return sources.setdefault(digest, set())


def check_rule(source, norm) -> None:
    """Lean's `soft-rule` check of `norm` under the lower soft `source`, or its raised diagnostic.
    A rule Lean already accepted under the same source is not sent again."""
    accepted = _accepted_for(_text(source))
    key = _text(norm)
    with _accepted_lock:
        if key in accepted:
            return
    run({"id": "soft-rule", "kind": "soft-rule", "environment": source, "norm": norm})
    with _accepted_lock:
        accepted.add(key)


def check_rules(source, norms) -> list:
    """Lean's `soft-rules` results for `norms` under `source`, in order: one request for the rules
    not yet accepted under the source, none when every rule was. A request that Lean rejects as a
    whole is sent again with every rule, so the raised diagnostic is the full request's."""
    norms = list(norms)
    accepted = _accepted_for(_text(source))
    keys = [_text(norm) for norm in norms]
    with _accepted_lock:
        missing = [i for i, key in enumerate(keys) if key not in accepted]
    results = [{"status": "ok"} for _ in norms]
    if not missing:
        return results
    try:
        row = run({"id": "soft-rules", "kind": "soft-rules", "environment": source,
                   "norms": [norms[i] for i in missing]})
    except VEError:
        if len(missing) == len(norms):
            raise
        row = run({"id": "soft-rules", "kind": "soft-rules", "environment": source, "norms": norms})
        missing = list(range(len(norms)))
    answers = row["results"]
    if type(answers) is not list or len(answers) != len(missing):
        raise CheckerUnavailable("CheckerUnavailable: Lean soft rule count differs from the request")
    for i, answer in zip(missing, answers):
        results[i] = answer
    with _accepted_lock:
        accepted.update(keys[i] for i, answer in zip(missing, answers)
                        if type(answer) is dict and answer.get("status") == "ok")
    return results
