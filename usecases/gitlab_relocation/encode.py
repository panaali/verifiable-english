"""The encoder's helper for the GitLab relocation translation (statute corpus batch 5): a sub-case spec (cases.py,
smoke_cases.py) -> the translation's Ctx and the stated facts. CROSS-FAMILY questions, Opus encoder. Written with the
translation, BEFORE any question existed (ISOLATION.md D-row of 2026-11-25).

A Sub lists the items one question needs (the team member p is always there), each item's parent, and the stated facts:
yes/no facts (fact) and stated values (val: dates YYYY-MM-DD). Nothing is computed here: every sum, comparison and date step
is a rule of translation.py (Lean checks it). The one exception is bridge/bridge.py's anniversary, entered as a fact marked
"bridge". Conventions the encoder applies (fixed now, before the questions; listed as encoder judgement on a case where used):
E1 the year asked about is entered by its name: 1 January of the year and of the next year (year());
E2 a place is entered by its name: the name facts of translation.NAMES are set for every listed name (true for its own name
   only); a place the text does not name gets the case's stated U.S. embargoed list membership (place());
E3 a yes/no fact the writer brief's FIXED FACTS say a case states where it matters (DESTINATION, PERSON, APPROVALS) and the
   case does not mention is entered as false, and listed as encoder judgement on the question;
E4 a fact the case states only for another question is not entered.
E5 (added AFTER the frozen run, row statute-corpus-gitlab-relocation-wrong-r035; the frozen encoder dropped R035's stated lack
   of written VP/PBP pre-approval as "not entered" and VE answered yes): a fact the case states that has no predicate here
   is entered with nopred(unit, text, turns_on), naming the unit it is about and whether that unit's stated outcome turns
   on it (turns_on: the same case with the fact the other way could get another outcome from the unit; when in doubt,
   true). A question whose answer is covered by that unit (the unit's rules are among the rules its answer turns on:
   covered_units) is REFUSED when turns_on is true, never answered with the fact dropped. A fact on a unit the answer does
   not turn on (a unit the translation does not write, or another question's unit), or one that is only the thing the
   outcome is about, leaves the answer as it is (recorded, not used). Only this law's encoder
   (usecases/gitlab_relocation/encode.py) has the rule.
"""
from __future__ import annotations

import sys
from pathlib import Path

import translation as T

sys.path.insert(0, str(Path(__file__).resolve().parent / "bridge"))
import bridge as B  # noqa: E402

LIT = {T.DAY: lambda v: ["date", v], T.NDAYS: lambda v: T.nd(v)}


class Sub:
    def __init__(self, judgement=()):
        self.items = [("p", "person")]
        self.parent = {}
        self.facts = []
        self.judgement = list(judgement)
        self.unentered = []      # E5: [(unit, the stated fact)] with no predicate

    def item(self, x, kind, parent=None):
        assert "_" not in x and x not in dict(self.items), x
        self.items.append((x, kind))
        if parent is not None:
            self.parent[x] = parent
        return self

    def fact(self, pred, x="p", val=True):
        assert pred in T.FACTS, pred
        f = T.U(pred, x)
        self._add(f if val else T.Not(f))
        return self

    def val(self, base, x, v, bridge=False):
        assert base in T.STATED_BASES, base
        self._add(T.Eq(T.k(base, x), LIT[T.UNIT_OF[base]](v)), bridge)
        return self

    def year(self, y, x="y"):
        """E1."""
        self.item(x, "year")
        return self.val("ya", x, f"{int(y):04d}-01-01").val("yb", x, f"{int(y) + 1:04d}-01-01")

    def place(self, x, name=None, onlist=None):
        """E2: name is a key of translation.NAMES or None (a place the text does not name)."""
        self.item(x, "place")
        assert name is None or name in T.NAMES, name
        for n in T.NAMES:
            self.fact(T.is_name(n), x, n == name)
        if onlist is not None:
            self.fact("onlist", x, onlist)
        return self

    def stay(self, x, place, first, last):
        self.item(x, "stay", place)
        return self.val("sf", x, first).val("sl", x, last)

    def start(self, day):
        """The start date and its bridged first anniversary (D8; a 29 February start raises: the question is refused)."""
        self.val("sd", "p", day)
        return self.val("an", "p", B.anniversary(day), bridge=True)

    def nopred(self, unit, text, turns_on=True):
        """E5: a stated fact with no predicate in the translation, the unit of units.jsonl it is about, and whether that
        unit's outcome turns on it."""
        assert unit is None or unit in T.UNITS, unit
        assert text and isinstance(text, str), text
        self.unentered.append((unit, text, bool(turns_on)))
        return self

    def _add(self, f, bridge=False):
        self.facts.append({"id": f"f{len(self.facts)}", "formula": f, **({"bridge": True} if bridge else {})})


def build(spec):
    return T.Ctx(spec.items, spec.parent), spec.facts, {}


def covered_units(ground, roots):
    """The units whose ground rules (translation.ground_by_unit) the answer at roots (atom keys / constant names,
    run.roots_for's) turns on: the rules that define a root, then every rule that defines an atom or constant those rules
    read, to a fixed point. A formula two units ground counts for both."""
    by_target = {}
    for n, f, t in ground:
        if t is not None:
            by_target.setdefault(t, []).append({"unit": n, "formula": f})
    seen, todo, units = set(), list(roots), set()
    while todo:
        t = todo.pop()
        if t in seen:
            continue
        seen.add(t)
        for r in by_target.get(t, ()):
            units.add(r["unit"])
            atoms, consts = set(), set()
            T.atoms_in(r["formula"], atoms, consts)
            todo += [a for a in atoms if a not in seen] + [x for x in consts if x not in seen]
    return units


def nopred_refusal(spec, ctx, roots, mutant=None):
    """E5: the refusal reason when a stated fact with no predicate bears on a unit the answer turns on, else None."""
    if not any(on for _, _, on in spec.unentered):
        return None
    units = covered_units(T.ground_by_unit(ctx, mutant), roots)
    hit = [(u, t) for u, t, on in spec.unentered if on and u in units]
    if not hit:
        return None
    return "stated fact with no predicate on a covered unit (encoder rule E5): " + "; ".join(
        f"unit {u}: {t}" for u, t in hit)
