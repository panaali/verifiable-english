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
   of written VP/PBP pre-approval as "not entered" and VE answered yes; narrowed after the fix's review): a fact the case
   states that no predicate here can carry is entered with nopred(unit, text, turns_on, clause, about): the unit it is
   about, whether a clause of that unit that states an outcome depends on it (turns_on), the clause's exact words, and the
   item it is about ("team member", "request" or a place's name; None: any). A question is REFUSED, never answered with the
   fact dropped, when (1) turns_on, (2) the clause overlaps a clause the translation writes (translation.WRITTEN; clause
   None: every written clause of the unit), (3) the question's answer reads one of that clause's names for the fact's item
   (covered_targets), and (4) the answer does not still follow with the rules defining those targets removed (run.py
   run_sub). A turns_on fact on a clause the translation does not write refuses nothing and is reported (e5_unwritten):
   the translation's ledger, reviewed, says that clause has no outcome. (5) A turns_on fact with no unit, or on a WRITTEN
   clause whose unit has no rules in the table in use (only a planted error such as M17 makes that state: WRITTEN is fixed
   with the translation), refuses every question of the sub-case whose answer reads anything about the fact's item. It is
   NOT a guard against the R035 class. LIMIT (the R035 class): a clause the translator ledgers as having no outcome when it
   has one (unit 4 in the frozen build, which a WRITTEN made from that ledger would not list) is not caught by the
   encoder: the fact is only reported (e5_unwritten); the cover is the translation's own review; the fresh seats flag ledgered duties as turning on (126 flags in
   this set, unit 6's "contact the People Operations Team" and unit 3's "Discuss the proposed move"), so refusing on them
   would refuse almost every answer. Only this law's encoder has the rule.
"""
from __future__ import annotations

import difflib
import json
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

    def nopred(self, unit, text, turns_on=True, clause=None, about=None):
        """E5: a stated fact with no predicate in the translation: the unit of units.jsonl it is about, whether a clause of
        that unit that states an outcome depends on it, that clause's words (None: any written clause of the unit) and
        the item it is about ("team member", "request", a place's name; None: any)."""
        assert unit is None or unit in T.UNITS, unit
        assert text and isinstance(text, str), text
        assert type(turns_on) is bool, turns_on
        assert about in ABOUT_KINDS or (isinstance(about, str) and about), about
        self.unentered.append((unit, text, turns_on, clause, about))
        return self

    def _add(self, f, bridge=False):
        self.facts.append({"id": f"f{len(self.facts)}", "formula": f, **({"bridge": True} if bridge else {})})


def build(spec):
    return T.Ctx(spec.items, spec.parent), spec.facts, {}


def covered_targets(ground, roots):
    """Every target (atom key or constant name) the answer at roots (run.roots_for's) reads through the ground rules
    (translation.ground_by_unit, a formula two units ground listed for both), to a fixed point; and the units of those
    rules."""
    by_target = {}
    for n, f, t in ground:
        if t is not None:
            by_target.setdefault(t, []).append((n, f))
    seen, todo, units = set(), list(roots), set()
    while todo:
        t = todo.pop()
        if t in seen:
            continue
        seen.add(t)
        for n, f in by_target.get(t, ()):
            units.add(n)
            atoms, consts = set(), set()
            T.atoms_in(f, atoms, consts)
            todo += [a for a in atoms if a not in seen] + [x for x in consts if x not in seen]
    return seen, units


def covered_units(ground, roots):
    """The units whose ground rules the answer at roots turns on."""
    return covered_targets(ground, roots)[1]


def target_name_item(t):
    """(predicate or step base, item) of a target: an atom key or a constant name base_item."""
    if t.startswith("["):
        f = json.loads(t)
        return (f[1], f[2][1]) if f[0] == "unary" else (None, None)
    base, _, x = t.partition("_")
    return base, x


def _norm(text):
    return " ".join(text.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"').split()).lower()


def written_names(unit, clause):
    """The names of the translation's written clauses of the unit that the cited clause overlaps (30 characters or one
    inside the other); clause None: every written clause of the unit."""
    names = set()
    for u, w, ns in T.WRITTEN:
        if u != unit:
            continue
        if clause is None:
            names |= set(ns)
            continue
        a, b = _norm(clause), _norm(w)
        if a in b or b in a:
            names |= set(ns)
            continue
        m = difflib.SequenceMatcher(None, a, b, autojunk=False).find_longest_match(0, len(a), 0, len(b))
        if m.size >= 30:
            names |= set(ns)
    return names


ABOUT_KINDS = (None, "team member", "request")


def item_matches(ctx, about, x):
    """Does the target item x belong to the fact's item ("team member" / None: any item; "request": a request, its
    place and the person; a place's name: that place, its stays and plans; a name the sub-case has no place for: any
    place and its children; in a request sub-case the request's destination)."""
    if about in (None, "team member"):
        return True
    if about != "request" and PLACE_IDS.get(about) not in ctx.of("place"):
        return True      # a name this sub-case has no place for (or two names): every item (conservative)
    kinds = dict(ctx.items)
    if about == "request":
        reqs = ctx.of("req")
        return x == "p" or kinds.get(x) == "req" or x in {ctx.parent.get(r) for r in reqs}
    places = [PLACE_IDS[about]]
    return x in places or ctx.parent.get(x) in places


PLACE_IDS = {"Spain": "es", "Portugal": "pt", "France": "fr", "Italy": "it", "Germany": "de", "Belgium": "be",
             "Mexico": "mx", "Brazil": "br", "Kyiv": "kyiv"}


def e5_hits(spec, ctx, roots, mutant=None):
    """E5 (1)-(3): [(unit, fact, the hit targets)] for the turns_on facts whose written clause the answer reads for the
    fact's item; and the turns_on facts on clauses the translation does not write."""
    hits, unwritten = [], []
    on = [e for e in spec.unentered if e[2]]
    if not on:
        return hits, unwritten
    targets, _ = covered_targets(T.ground_by_unit(ctx, mutant), roots)
    table = T.units_table(mutant)
    for unit, text, _, clause, about in on:
        names = written_names(unit, clause) if unit is not None else set()
        if unit is not None and not names:
            unwritten.append((unit, text, clause))
            continue
        if unit is None or table[unit][1] is None:
            # (5) a translation gap: the answer refuses if it reads anything about the fact's item
            hit = {t for t in targets if item_matches(ctx, about, target_name_item(t)[1])}
        else:
            hit = {t for t in targets
                   if (lambda ni: ni[0] in names and item_matches(ctx, about, ni[1]))(target_name_item(t))}
        if hit:
            hits.append((unit, text, hit))
    return hits, unwritten


def e5_reason(hits):
    return "stated fact with no predicate on a written clause the answer reads (encoder rule E5): " + "; ".join(
        f"unit {u}: {t}" for u, t, _ in hits)
