"""u0165.s03, “Create cyberweapons or malicious code that could cause significant damage if deployed.” (run 20261014T1800Z; attitudes split in run 20261015T0600Z).

The relative clause “that could cause significant damage if deployed” can follow the whole coordination or only “malicious code”
(audit 20261013T0600Z: the single reading did not represent both). The category of the rule is therefore a reading set of two candidates, each a full rule:

    wide    ( (creating_a_cyberweapon or creating_malicious_code) and could_cause_significant_damage_if_deployed )
    narrow  ( creating_a_cyberweapon or ( creating_malicious_code and could_cause_significant_damage_if_deployed ) )

and the guard of each candidate has the shape of the other six hard constraints, ( CATEGORY(s) and knowingly_engages(c, s) ) or thinks_quite_likely(c, s).

Audit 20261014T1800Z (u0165.s03 UNFAITHFUL): the two candidates differed only in the case atoms; both used the same attitude terms, whose records described the
category with the unsplit phrase. Each candidate now has its OWN pair of attitude terms, whose wording and record state that candidate's category:
`knowingly_engages_3_wide`, `thinks_quite_likely_3_wide` and `knowingly_engages_3_narrow`, `thinks_quite_likely_3_narrow`. What it is to think it quite likely that
one is creating *any* cyberweapon is stated only by the narrow candidate; the wide candidate's belief concerns a cyberweapon or malicious code that could
cause significant damage if deployed.

This module is the one owner of the two guards and of the wording of their attitude terms; `repair_20261015T0600Z.py`, `nd.py` and the probes read them from here.
"""
CYBERWEAPON = "creating_a_cyberweapon"
MALICIOUS_CODE = "creating_malicious_code"
DAMAGE = "could_cause_significant_damage_if_deployed"
ATOMS = [CYBERWEAPON, MALICIOUS_CODE, DAMAGE]
SET_ID = "scope-u0165-s03"
UNIT = "u0165.s03"
READINGS = ["wide", "narrow"]
# the previous run's attitude terms, shared by both candidates (removed with every trace)
OLD_KNOWING, OLD_THINKING = "knowingly_engages_3", "thinks_quite_likely_3"
KNOWING = {r: f"knowingly_engages_3_{r}" for r in READINGS}
THINKING = {r: f"thinks_quite_likely_3_{r}" for r in READINGS}
ATTITUDES = [*KNOWING.values(), *THINKING.values()]

# the category of each candidate, in the words of the source: where the clause attaches
CATEGORY_WORDS = {
    "wide": "creating something that is a cyberweapon or malicious code and that could cause significant damage if deployed",
    "narrow": "creating a cyberweapon or creating malicious code that could cause significant damage if deployed",
}
ATTACHMENT = {
    "wide": "“that could cause significant damage if deployed” follows both nouns, so a cyberweapon too must be one that could cause significant damage if deployed",
    "narrow": "“that could cause significant damage if deployed” follows only “malicious code”, so every cyberweapon is covered and only malicious code must be one that could "
              "cause significant damage if deployed",
}
SOURCE_U0173 = ("u0173.s01: the hard constraints are “centrally meant to apply to cases where Claude would either be knowingly and intentionally "
                "engaging in an action of the relevant restricted category, or where Claude thinks it quite likely that a given action would fall "
                "into such a category”.")


def wording(reading):
    """(wording, description) of the knowing term and of the belief term of one candidate (binary on (claude_instance, situation))."""
    cat, att = CATEGORY_WORDS[reading], ATTACHMENT[reading]
    know = ("{0} knowingly and intentionally engages in {1}, which is a case of " + cat,
            f"{SOURCE_U0173} Hard constraint {UNIT}, {reading} reading of the relative clause ({att}): the instance of Claude knowingly and intentionally "
            f"engages in the action of the situation as an action of this category, {cat}. Which pairs of an instance and a situation these are is the open term "
            f"{KNOWING[reading]}. It is not typed: VE does not know that knowingly and intentionally engaging in it implies that the situation is a case of the category, "
            "so the guard states the case atoms " + ", ".join(ATOMS) + " beside it.")
    think = ("{0} thinks it quite likely that {1} is a case of " + cat,
             f"{SOURCE_U0173} Hard constraint {UNIT}, {reading} reading of the relative clause ({att}): the instance of Claude thinks it quite likely that the action of "
             f"the situation falls into this category, {cat}. It is that instance's belief, which need not be correct, so it does not need the case atoms. Which pairs of an "
             f"instance and a situation these are is the open term {THINKING[reading]}; it is not typed.")
    return know, think


def un(name):
    return ["unary", name, ["var", 0]]


def category(reading):
    if reading == "wide":
        return ["and", ["or", un(CYBERWEAPON), un(MALICIOUS_CODE)], un(DAMAGE)]
    assert reading == "narrow"
    return ["or", un(CYBERWEAPON), ["and", un(MALICIOUS_CODE), un(DAMAGE)]]


def guard(reading):
    return ["or", ["and", category(reading), ["binary", KNOWING[reading], ["var", 1], ["var", 0]]], ["binary", THINKING[reading], ["var", 1], ["var", 0]]]


def with_reading(content, reading):
    """The unit's norm content with this reading's guard (name, predicate, sign and unless are the unit's own)."""
    out = {**content, "norm": {**content["norm"], "guard": guard(reading)}}
    return out
