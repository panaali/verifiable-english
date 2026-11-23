"""The encoder's facts for one case (cases.py). SAME-FAMILY.

Conventions (stated, the same for every case; fixed with the translation, before the encoder's questions were read):
C1 closed world over translation.FACTS: a fact the case record does not list as true is stated false; the encoder lists
   every true fact it reads in the question's facts;
C2 integer constants only where the question gives them: the ship's certified passengers and crew, the one-way distance
   (metres; a distance stated in kilometres is written in metres, x 1000, exact), the overnight stays, the design year,
   the scheduled journey and the delay as (whole hours, minutes 0-59) exactly as stated (a duration stated in minutes
   only is written as its whole hours and the minutes left), the prices and the threshold in EUR;
C3 a stated judgment enters as the stated fact (translation.STATED), never decided by the encoder;
C4 fixed facts of the test (WRITER-BRIEF): a place the facts name as a port of embarkation / disembarkation is a place
   with improvement works and facilities permitting the reception of ships from which passengers regularly embark or
   disembark (works_*, regular_*) unless the facts say otherwise; the passenger travels on a vessel and holds a contract of
   carriage with the named party and a valid document or evidence of it unless the facts say otherwise; a passenger
   transport service is what the facts describe as transporting passengers; a named lake, river or canal the service
   runs on is a navigable inland body of water used for transport (the words of Art 3(i)) unless the facts say otherwise.
"""
from __future__ import annotations

import translation as T


def literal(name, value):
    unit = T.INT_UNITS[name.rsplit("_", 1)[0]][0]
    term = ["const", unit, name]
    if unit == T.EUR:
        return ["eq", term, ["decimal", unit, str(value)]]
    return ["eq", term, ["decimal", unit, str(int(value))]]


def ctx_of(case):
    return T.Ctx()


def facts(case):
    out = []
    mine = set(case.get("facts", ()))
    bad = mine - set(T.FACTS)
    if bad:
        raise ValueError(f"{case['id']}: unknown facts {sorted(bad)}")
    for p, (item, _) in T.FACTS.items():
        f = T.U(p, item)
        out.append({"id": f"{item}.{p}", "formula": f if p in mine else ["not", f]})
    ints = dict(case.get("ints", {}))
    for name, value in ints.items():
        base = name.rsplit("_", 1)[0]
        if base not in T.INT_UNITS or not name.endswith("_p"):
            raise ValueError(f"{case['id']}: unknown constant {name}")
        if base in T.STEP_CONSTANTS:
            raise ValueError(f"{case['id']}: a derived amount typed by the encoder ({name})")
        if base in ("sch_m", "del_m") and not 0 <= int(value) <= 59:
            raise ValueError(f"{case['id']}: minutes beyond whole hours must be 0-59 ({name}={value})")
    for name, value in sorted(ints.items()):
        out.append({"id": name, "formula": literal(name, value)})
    return out
