"""An independent reading of the Asimov rules and the authored additions, for one robot.

It is written from the plain meaning of PLAN.md sections 4.1 and 4.2, not from
VE's elaboration: the four laws as in v2's `source_reading`, then the
additions. They are this project's, not Asimov's: a severity order on harms,
a precaution against possible harm when a candidate action has a less severe
worst case, a least-severe-worst-case permission when every action breaks a
law, and precedence between competing orders. Every action of a record is
available to its one robot, so "competes with" always holds.
"""
from __future__ import annotations

from cases import HUMAN, HUMANITY, SELF

RANK = {"catastrophic": 3, "fatal": 2, "injuring": 1, "damaging": 0}
CLASS = {"humanity_harm": "catastrophic", "death_1": "fatal", "death_2": "fatal", "death_3": "fatal",
         "injury_1": "injuring", "property_damage": "damaging", "robot_destroyed": "damaging",
         "robot_damaged": "damaging"}


def read(spec, extended=True, rank=None):
    """Permitted, required and clear actions, and the dilemma kind when nothing is clear."""
    rank = RANK if rank is None else rank
    actions = spec["actions"]
    cell = spec["cells"]
    facts = spec["facts"]
    marked = lambda name: {row[0] for row in facts[name]}  # noqa: E731
    pairs = lambda name: {tuple(row) for row in facts[name]}  # noqa: E731
    leads = lambda a, h: cell[(a, h)] == "leads"  # noqa: E731
    might = lambda a, h: cell[(a, h)] in ("leads", "might")  # noqa: E731
    others = lambda a: [b for b in actions if b != a]  # noqa: E731
    allows = lambda a, h: leads(a, h) and any(not leads(b, h) for b in others(a))  # noqa: E731
    prevents = lambda a, h: not leads(a, h) and any(leads(b, h) for b in others(a))  # noqa: E731

    first = {a for a in actions if a in marked("injures_human") or any(allows(a, h) for h in HUMAN)}
    zeroth = {a for a in actions if a in marked("injures_humanity") or any(allows(a, h) for h in HUMANITY)}
    lawful = {a for a in actions if a not in first | zeroth}
    excused = {a for a in actions if any(prevents(a, h) for h in HUMANITY) and not lawful}
    ordered = marked("ordered")

    if not extended:
        permitted = [a for a in actions if a not in zeroth and (a not in first or a in excused)]
        required = [a for a in permitted if a in ordered]
    else:
        # A candidate breaks no law; when no action is lawful, every action that keeps the Zeroth Law is one.
        candidates = {a for a in actions if a in lawful or (not lawful and a not in zeroth)}

        def worst(a):
            return max((rank[CLASS[h]] for h in CLASS if might(a, h)), default=-1)

        beaten = {a for a in actions if any(b in candidates and worst(a) > worst(b) for b in others(a))}
        possibly_harmful = {a for a in actions if any(might(a, h) for h in HUMAN)
                            or (a not in ordered and any(might(a, h) for h in SELF))}
        precaution = possibly_harmful & beaten
        least_severe = candidates - beaten - zeroth
        permitted = [a for a in actions if a not in zeroth and a not in precaution
                     and (a not in first or a in excused or a in least_severe)]
        valid = {a for a in ordered if a in lawful and a not in precaution}
        outranks, before = pairs("outranks"), pairs("ordered_before")
        prevails = lambda b, a: (b, a) in outranks or ((b, a) in before and (a, b) not in outranks)  # noqa: E731
        overridden = {a for a in actions if any(b in valid and prevails(b, a) for b in actions)}
        required = [a for a in permitted if a in ordered and a not in overridden]

    threats = [h for h in SELF if any(not leads(a, h) for a in permitted)]
    jointly = any(all(not leads(a, h) for h in threats) for a in permitted)
    duties = [h for h in threats if jointly and all(prevents(a, h) for a in required)]
    clear = [a for a in permitted if set(required) <= {a} and all(not leads(a, h) for h in duties)]
    if clear:
        dilemma = None
    elif not permitted:
        dilemma = "NONE-PERMITTED"
    elif len(required) > 1:
        dilemma = "OVER-REQUIRED"
    else:
        dilemma = "OTHER"
    return {"permitted": permitted, "required": required, "clear": clear, "dilemma": dilemma}
