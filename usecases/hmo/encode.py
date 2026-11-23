"""HMO England: turn the encoder's records (cases.py) into VE facts. Mechanical; every reading is in cases.py.

Closed facts: every base predicate gets a literal (true or false) for every tuple of the case's names (people in order ->
person1.., places, the four amenities), except the tuples the record lists as unknown (C2, C8), so VE can prove negatives
and refuses what turns on an unknown."""
from __future__ import annotations

import itertools

import rows as R


def names(case):
    people = {n: f"person{i}" for i, n in enumerate(case["people"], 1)}
    return people


def domains(case):
    return {"person": list(names(case).values()), "place": list(case["places"]), "amenity": list(R.AMENITIES)}


def facts(case):
    pm = names(case)
    dom = domains(case)
    true = set()
    for place, preds in case["place"].items():
        for pr in preds:
            true.add(("unary", pr, place))
    for place, am in case.get("amen", {}).items():
        for a in am.get("has", []):
            true.add(("binary", "has_amenity", place, a))
        for a in am.get("excl", []):
            true.add(("binary", "excl_amenity", place, a))
    for person, place in case["lives"].items():
        true.add(("binary", "lives_in", pm[person], place))
    for pr in case.get("all", []):
        for p in pm.values():
            true.add(("unary", pr, p))
    for person, preds in case.get("person", {}).items():
        for pr in preds:
            true.add(("unary", pr, pm[person]))
    for a, b, pr in case.get("rel", []):
        true.add(("binary", pr, pm[a], pm[b]))
    for person, ams in case.get("shares", {}).items():
        for a in ams:
            true.add(("binary", "shares", pm[person], a))
    unknown = set()
    for u in case.get("unknown", []):
        kind, pr, *args = u
        if kind in ("unary", "binary") and pr in R.PLACE1 | R.PERSON1 | R.PERSON2 | R.PLACE_AMENITY | R.PERSON_PLACE | R.PERSON_AMENITY:
            unknown.add((kind, pr, *[pm.get(x, x) for x in args]))
        else:  # ("excl_amenity", place, amenity) shorthand
            unknown.add(("binary", kind, pr, args[0]))
    for t in true:
        if t[1] not in (R.PLACE1 | R.PERSON1 | R.PERSON2 | R.PLACE_AMENITY | R.PERSON_PLACE | R.PERSON_AMENITY):
            raise ValueError(f"{case['id']}: not a base predicate: {t}")
        for x in t[2:]:
            if x not in dom["person"] + dom["place"] + dom["amenity"]:
                raise ValueError(f"{case['id']}: name outside the case's domain: {t}")
    tables = ((R.PLACE1, ["place"]), (R.PLACE_AMENITY, ["place", "amenity"]), (R.PERSON1, ["person"]),
              (R.PERSON2, ["person", "person"]), (R.PERSON_PLACE, ["person", "place"]),
              (R.PERSON_AMENITY, ["person", "amenity"]))
    out, left_out = [], []
    for table, args in tables:
        for pr in sorted(table):
            for tup in itertools.product(*(dom[a] for a in args)):
                atom = ("unary" if len(args) == 1 else "binary", pr, *tup)
                if atom in unknown:
                    left_out.append(" ".join(atom[1:]))
                    continue
                f = [atom[0], pr, *(["const", x] for x in tup)]
                out.append({"id": f"{pr}({','.join(tup)})", "formula": f if atom in true else ["not", f]})
    missing = [u for u in unknown if " ".join(u[1:]) not in left_out]
    if missing:
        raise ValueError(f"{case['id']}: unknown names no fact: {missing}")
    return out, left_out
