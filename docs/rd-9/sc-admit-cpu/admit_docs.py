"""sc-admit-cpu: the soft-chain documents of docs/rd-9/sc-11/w13-cpu.md and docs/rd-9/sc-11w/cpu.md as readings@1
requests (environment and document JSON), for `admit_bench.lean`'s `admitSD` timing (docs/rd-9/sc-admit-cpu/cpu.md).

Each case restates a Lean `NDoc` of `docs/rd-9/sc-11w/cpu_bench.lean` (`NSDbig n g`, `withRules n m g`) on the wire:
the environment is `tests/test_readings_sd_lean.py`'s `env4()` (the vocabulary of `frame4`, `y_permitted` unspecified),
the units and reading sets are those of `D4`/`doc4` widened as `NSDbig` widens them. The bench decodes each request and
checks that the admitted document's items, chain and unspecified predicates equal the Lean `NDoc` it restates, so a
drift here is reported, not timed. Usage: `python3 admit_docs.py <out-dir> [R<n>_<m>_<e> ...]` writes `<out-dir>/<case>.json`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROFILES = ["norm-defaults@0", "norms@0", "readings@1", "relational-fol@0", "soft-norms@0"]


def environment():
    def regulated(role, default, act, **extra):
        return {"arguments": ["assistant"], "description": "obligation" if role == "obligation" else "permission",
                "regulated": {"role": role, "default": default, "act": act, **extra}}
    return {"language": "ve.core@0.2", "profiles": PROFILES, "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"assistant": {"description": "assistant"}}, "predicates": {
                "x_required": regulated("obligation", "deny", "{0} do x", permission="x_permitted"),
                "x_permitted": regulated("permission", "deny", "{0} do x"),
                "y_permitted": regulated("permission", "unspecified", "{0} do y"),
                "c": {"arguments": ["assistant"], "description": "c"}}, "constants": {}}}


def wide(e):
    """cpu_bench.lean's `wide e`: `c(x)` conjoined with itself to depth `e`."""
    return ["unary", "c", ["var", 0]] if e == 0 else ["and", wide(e - 1), wide(e - 1)]


def sized(n):
    """SoftSupWireExamples' `sized n`: a balanced formula of exactly `n >= 1` AST nodes."""
    if n <= 1:
        return ["top"]
    if n == 2:
        return ["unary", "c", ["var", 0]]
    k = n - 1
    return ["and", sized(k // 2), sized(k - k // 2)]


def norm(name, pred, sign, guard=("top",), default=False, sufficient=()):
    body = {"name": name, "predicate": pred, "sign": sign, "guard": list(guard), "unless": [], "over": []}
    if default:
        body.update({"mode": "default", "exception": {"decided_by": "unstated", "sufficient": list(sufficient),
                                                      "necessary": [], "factors": []}})
    return {"norm": body}


def reading(rid, content):
    return {"id": rid, "kind": "norm", "content": content, "meaning_id": "m",
            "admission": {"who": "w", "why": "y", "distinguishing_models": {}}}


def nsd_big(n, guard=("top",), rules=0, rule_guard=("top",)):
    """`NSDbig n guard` (set 0's strict guard is `guard`), then `withRules`' `rules` fixed strict rules (`rule_guard`,
    or `rule_guard(i)` when it is a function)."""
    y, c = ["unary", "y_permitted", ["var", 0]], ["unary", "c", ["var", 0]]
    units = [{"id": "u0", "kind": "norm", "content": norm("need-not-x", "x_required", False, default=True)}]
    sets = []
    for k in range(n):
        units.append({"id": f"u{k + 1}"})
        strict = norm(f"must-x-{k}", "x_required", True, guard if k == 0 else ("top",))
        default = norm(f"must-x-{k}", "x_required", True, y, default=True, sufficient=[c])
        sets.append({"id": f"rs{k}", "unit": f"u{k + 1}", "version": 1, "status": "open",
                     "readings": [reading("strict", strict), reading("default", default)], "situations": {}})
    preds = ["x_required", "x_permitted", "y_permitted"]
    units += [{"id": f"g{i}", "kind": "norm", "content": norm(f"guarded-{i}", preds[i % 3], True,
                                                           rule_guard(i) if callable(rule_guard) else rule_guard)}
              for i in range(rules)]
    return {"units": units, "reading_sets": sets}


# name -> document; the names are cpu_bench.lean's `cases` (and `NSDbig6`, w13-cpu.md's row 1 at 6 sets)
CASES = {
    "NSDbig6": lambda: nsd_big(6),
    "wideGuard767": lambda: nsd_big(8, wide(8)),
    "wideGuard3071": lambda: nsd_big(6, wide(10)),
    "wideGuard191": lambda: nsd_big(8, wide(6)),
    "NSDbig8": lambda: nsd_big(8),
    "NSDheavy": lambda: nsd_big(6, rules=10, rule_guard=wide(4)),
    "heavyIn": lambda: nsd_big(6, rules=9, rule_guard=wide(4)),
    # SoftWireExamples' `NSDlimit r`: 13 rules, the first r of 3 nodes, the rest of 2; work 131,072 (r = 1), 133,120
    "atLimit": lambda: nsd_big(6, rules=13, rule_guard=lambda i: sized(3 if i < 1 else 2)),
    "overLimit": lambda: nsd_big(6, rules=13, rule_guard=lambda i: sized(3 if i < 2 else 2)),
    # scaling: `rules<m>` is `withRules 6 m (wide 4)`, `guard<e>` is `withRules 6 9 (wide e)`
    **{f"rules{m}": (lambda m=m: nsd_big(6, rules=m, rule_guard=wide(4))) for m in (0, 1, 2, 4, 8, 16)},
    **{f"guard{e}": (lambda e=e: nsd_big(6, rules=9, rule_guard=wide(e))) for e in (0, 2, 6)},
    # `top<m>` is `withRules 6 m (fun _ => .top)`: many rules, few nodes
    **{f"top{m}": (lambda m=m: nsd_big(6, rules=m)) for m in (3, 9, 16, 32)},
    # `few<n>x<m>` is `withRules n m (fun _ => .top)`: few choices, many rules
    **{f"few{n}x{m}": (lambda n=n, m=m: nsd_big(n, rules=m)) for n, m in ((1, 32), (1, 64), (1, 128), (3, 32), (3, 64))},
}


def generic(name):
    """`R<n>_<m>_<e>` is `withRules n m` with guard `wide e` (`t`: `.top`), for cases the command line names."""
    n, m, e = name[1:].split("_")
    return nsd_big(int(n), rules=int(m), rule_guard=("top",) if e == "t" else wide(int(e)))


def main(out, extra=()):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for name, build in [*CASES.items(), *((x, lambda x=x: generic(x)) for x in extra)]:
        (out / f"{name}.json").write_text(json.dumps({"case": name, "environment": environment(),
                                                     "document": build()}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
