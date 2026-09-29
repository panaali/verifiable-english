"""An independent reading of the policy, written from PLAN section 3.3 only.

It does not import `ve`. It reads the emitted facts from `emit_log.py` and
evaluates each rule with three-valued logic: a missing fact is unknown (None),
never false. Rules 1-24 and the obligation rule 25 use the plan's numbering.
Its verdicts are compared with the harness (PLAN metric M8), not with the key.
"""
from __future__ import annotations

from emit_log import ACTIONS, FILES, HOSTS, PEOPLE, REPORTED


def AND(*values):
    if any(v is False for v in values):
        return False
    return True if all(v is True for v in values) else None


def OR(*values):
    if any(v is True for v in values):
        return True
    return False if all(v is False for v in values) else None


def NOT(value):
    return None if value is None else not value


def SOME(items, test):
    return OR(*(test(x) for x in items)) if items else False


def inside(f):
    return FILES[f][1]


def credential(f):
    return FILES[f][2]


def tracked(f):
    return FILES[f][3]


def guards(a):
    """Guard and carve-out of each rule, as (guard, unless) truth values."""
    tool = lambda t: a["tool"] == t
    c = a["confirmed"]
    shell_readonly = a["readonly"] if tool("shell") else False
    over_limit = NOT(a["affordable"]) if tool("purchase") else False
    return {
        1: (SOME(a["reads"], inside), False),
        2: (AND(c, bool(a["reads"])), False),
        3: (SOME(a["writes"], inside), False),
        4: (SOME(a["deletes"], inside), False),
        5: (AND(tool("shell"), shell_readonly), False),
        6: (AND(tool("shell"), c), False),
        7: (SOME(a["contacts"], lambda h: HOSTS[h][1]), False),
        8: (AND(c, bool(a["contacts"])), False),
        9: (SOME(a["messages"], lambda p: PEOPLE[p][1]), False),
        10: (AND(tool("purchase"), c), False),
        11: (AND(tool("get_secret"), c), False),
        12: (AND(c, SOME(a["reads"], credential)), False),
        13: (SOME(a["reads"], lambda f: NOT(inside(f))), c),
        14: (SOME(a["writes"], lambda f: NOT(inside(f))), False),
        15: (SOME(a["deletes"], lambda f: NOT(inside(f))), False),
        16: (SOME(a["deletes"], lambda f: NOT(tracked(f))), c),
        17: (AND(tool("shell"), NOT(shell_readonly) if tool("shell") else False), c),
        18: (SOME(a["contacts"], lambda h: not HOSTS[h][1]), c),
        19: (SOME(a["messages"], lambda p: not PEOPLE[p][1]), c),
        20: (tool("purchase"), c),
        21: (over_limit, False),
        22: (a["privileged"], False),
        23: (bool(a["discloses"]), False),
        24: (SOME(a["reads"], credential), False),
        25: (OR(bool(a["deletes"]), tool("purchase")), False),
    }


POSITIVE = range(1, 13)
NEGATIVE = range(13, 25)


def overrides(negative, positive):
    """Rules 13-24 take precedence over rules 1-12, except rule 14 over rule 3 (D1)."""
    return not (negative == 14 and positive == 3)


def selection(a):
    applies = {n: AND(g, NOT(u)) for n, (g, u) in guards(a).items()}
    selected = {}
    for n in POSITIVE:
        selected[n] = AND(applies[n], *(NOT(applies[m]) for m in NEGATIVE if overrides(m, n)))
    for n in NEGATIVE:
        selected[n] = applies[n]
    selected[25] = applies[25]
    return selected


def verdict(a):
    s = selection(a)
    pos = {n for n in POSITIVE if s[n] is True}
    neg = {n for n in NEGATIVE if s[n] is True}
    unknown = {n for n in (*POSITIVE, *NEGATIVE) if s[n] is None}
    if pos and neg:
        v = "CONFLICT"
    elif pos and not neg and not unknown & set(NEGATIVE):
        v = "APPROVED"
    elif neg and not pos and not unknown & set(POSITIVE):
        v = "REJECTED"
    elif not (pos or neg or unknown):
        v = "NOT-COVERED"
    else:
        v = "UNDETERMINED"
    report = {True: "required", False: "not covered"}.get(s[25], "undetermined")
    return {"verdict": v, "positive": sorted(pos), "negative": sorted(neg), "open": sorted(unknown),
            "report": report, "reported": a["reported"] if "reported" in a else None}


def verdicts():
    out = {}
    for name, a in ACTIONS.items():
        out[name] = verdict(a)
        out[name]["reported"] = name in REPORTED
    return out


if __name__ == "__main__":
    for name, result in verdicts().items():
        print(name, result)
