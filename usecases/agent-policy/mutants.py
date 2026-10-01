"""The six seeded mutants of PLAN section 11, as exact text edits.

Each edit must apply exactly once to the committed `policy.ve` or `log.ve`.
A policy mutant is parsed without the manifest; its rules keep the committed
names, and m2's new rule (called M in the plan) is `message-others-confirmed`.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NEW_RULE = "message-others-confirmed"
ALL = "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12"
WITHOUT_3 = "1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12"
M2_RULE = ("Rule 27. Every action may be performed, if there is a person such that both that action "
           "messages that person and that person is not principal, unless that action is not confirmed.")


def _once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"mutant edit does not apply exactly once: {old!r}")
    return text.replace(old, new)


def m1(policy, log):
    """Add rule 3 to rule 14's exception list (the fix for D1)."""
    return _once(policy, f"Rule 14 (exception to rules {WITHOUT_3}).", f"Rule 14 (exception to rules {ALL})."), log


def m2(policy, log):
    """Add rule M for confirmed messages to non-users, overridden by all 12 negative rules."""
    lines = policy.split("\n")
    for number in range(13, 25):
        line = lines[number - 1]
        head = f"Rule {number} (exception to rules "
        if not line.startswith(head):
            raise ValueError(f"rule {number} has no exception list")
        close = line.index(").")
        lines[number - 1] = line[:close] + ", 27" + line[close:]
    return "\n".join(lines + [M2_RULE]), log


def m3(policy, log):
    """Shorten rule 2's guard to the confirmation alone (the exception-does-not-inherit trap)."""
    return _once(policy, "Rule 2. Every action may be performed, if there is a file such that both that "
                 "action reads that file and that action is confirmed.",
                 "Rule 2. Every action may be performed, if that action is confirmed."), log


def m4(policy, log):
    """Delete the closure sentence for `reads` from a01's record."""
    return policy, _once(log, 'For every file that "a01" reads, that file is the same as "f_main".\n', "")


def m5(policy, log):
    """Remove rule 12 from rule 24's exception list."""
    return _once(policy, f"Rule 24 (exception to rules {ALL}).",
                 "Rule 24 (exception to rules 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)."), log


def m6(policy, log):
    """State that a36 is confirmed, replacing the negative fact."""
    return policy, _once(log, '"a36" is not confirmed.', '"a36" is confirmed.')


MUTANTS = {"m1": m1, "m2": m2, "m3": m3, "m4": m4, "m5": m5, "m6": m6}


def names():
    """Rule names by display number, for parsing a mutant policy without the manifest."""
    blocks = json.loads((HERE / "policy.manifest.json").read_text())["blocks"]
    return [b["name"] for b in blocks] + [NEW_RULE]
