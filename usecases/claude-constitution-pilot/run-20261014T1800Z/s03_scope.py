"""u0165.s03, “Create cyberweapons or malicious code that could cause significant damage if deployed.” (run 20261014T1800Z).

The relative clause “that could cause significant damage if deployed” can follow the whole coordination or only “malicious code”
(audit 20261013T0600Z: the single reading did not represent both). The category of the rule is therefore a reading set of two candidates, each a full rule:

    wide    ( (creating_a_cyberweapon or creating_malicious_code) and could_cause_significant_damage_if_deployed )
    narrow  ( creating_a_cyberweapon or ( creating_malicious_code and could_cause_significant_damage_if_deployed ) )

and the guard is the same as the other six hard constraints: ( CATEGORY(s) and knowingly_engages_3(c, s) ) or thinks_quite_likely_3(c, s).
This module is the one owner of the two guards; `repair_20261014T1800Z.py`, `nd.py` and the probes read them from here.
"""
CYBERWEAPON = "creating_a_cyberweapon"
MALICIOUS_CODE = "creating_malicious_code"
DAMAGE = "could_cause_significant_damage_if_deployed"
ATOMS = [CYBERWEAPON, MALICIOUS_CODE, DAMAGE]
SET_ID = "scope-u0165-s03"
UNIT = "u0165.s03"
READINGS = ["wide", "narrow"]
KNOWING, THINKING = "knowingly_engages_3", "thinks_quite_likely_3"


def un(name):
    return ["unary", name, ["var", 0]]


def category(reading):
    if reading == "wide":
        return ["and", ["or", un(CYBERWEAPON), un(MALICIOUS_CODE)], un(DAMAGE)]
    assert reading == "narrow"
    return ["or", un(CYBERWEAPON), ["and", un(MALICIOUS_CODE), un(DAMAGE)]]


def guard(reading):
    return ["or", ["and", category(reading), ["binary", KNOWING, ["var", 1], ["var", 0]]], ["binary", THINKING, ["var", 1], ["var", 0]]]


def with_reading(content, reading):
    """The unit's norm content with this reading's guard (name, predicate, sign and unless are the unit's own)."""
    out = {**content, "norm": {**content["norm"], "guard": guard(reading)}}
    return out
