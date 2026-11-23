"""Sea and inland waterway passenger compensation, Regulation (EU) No 1177/2010 Arts 2(1)-(2), 3 (13 used definitions), 19(1),
(3), (4), (6), 20(1), (2), (4) (statute corpus batch 3, law eu-sea-passengers): the VE translation, one pass with today's
language. SAME-FAMILY (Opus writer, Opus translator).

Row statute-corpus-eu-sea-passengers (dri-statute-corpus-eu-sea-passengers-1123, Opus 5.5). Written from the pinned source
only (manage-agents reviews/spare/statute-corpus/stock/eu-sea-passengers/source.txt, sha256 31a4ed9d...7bb000a49) and the
answer forms of WRITER-BRIEF.md, BEFORE the encoder's question file was opened. Evidence branch: nothing here is a Lean
kernel line, a profile, a refuses pair or a lint change; nothing merges.

UNITS maps each in-scope unit n of stock/eu-sea-passengers/units.jsonl to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one case;
  ("PART", builder, cause, note) written except the part named in the note (stated / refused / not written);
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2).
Items of a case: p (the passenger and the journey), c (the party the transport contract names as carrier: the fixed facts
of the test say it may also be a tour operator, travel agent or ticket vendor), e (the port of embarkation), d (the port
of disembarkation). No number from a case's facts is ever put into a rule as a coefficient: every coefficient and limit
below is a literal of the pinned text (12, 3, 500 metres, 36, 1965, two overnight stays, 4 / 8 / 24 hours, 1 / 2 / 3 / 6
hours, "double", 25 %, 50 %, "half", EUR 6).
Durations (scheduled journey, delay in arrival) are pairs (whole hours, minutes beyond them, 0-59), as the facts state
them ("in hours and minutes"): "at least N hours" = h >= N; "more than N hours" = h > N or (h = N and m > 0); "up to /
not exceeding N hours" = not more than N hours. "Double the time" is written as scale 2 of the literal hours.

TRANSLATOR READINGS (fixed here, before any question was read; each is either the text's plain words or a refusal):
R1 Art 2(1) is the whole positive scope: a passenger in none of (a)-(c) is one the Regulation does not apply to.
R2 Art 19(1): the passenger "may request compensation" when the delay reaches the minimum-level threshold of (a)-(d) for
   the scheduled journey (the minimum level is set "for a delay of at least ..."); below it there is no Art 19 right.
R3 Art 2(2)(d): REFUSED where its two readings differ: (i) "ships not propelled by mechanical means" OR (historical ships,
   designed before 1965, original materials, certified up to 36); (ii) "certified to carry up to 36 passengers" also
   limiting the ships not propelled by mechanical means. Both readings agree -> written; they differ -> no derivation.
R4 Art 19(6): a carrier threshold above EUR 6 ("shall not exceed EUR 6"): capped at 6 or void are two readings; they give
   the same payment unless the compensation is below EUR 6: then refused. A compensation below a valid threshold is not
   paid (the amount the carrier must pay is 0.00); whether the passenger then still "may request compensation" (Q2) is
   two readings ("may request" in 19(1) vs "will not be paid" in 19(6)): Q2 refused there.
R5 Art 19 "request compensation from the carrier" and Art 2(1)(b) "operated by a Union carrier": the party the contract
   names is taken as the carrier only when it is a "carrier" (Art 3(d)); a contract with a tour operator, travel agent or
   ticket vendor and no carrier: the Art 19 right and 2(1)(b) are refused, never denied.
R6 Art 2(1)(c) "However, Articles ... 19 and 20(1) and (4) shall not apply to those passengers": "those passengers" are
   the passengers of (c) (a cruise embarking in a Member State).
"""
from __future__ import annotations

import hashlib
import json

EUR, HOURS, MINS, PERSONS, METRES, NIGHTS, YEAR = ("eur_cent", "hour_count", "minute_count", "person_count",
                                                   "metre_count", "night_count", "calendar_year")
INT_UNITS = {  # per-case integer constants on the journey item p: base name -> (unit, words)
    "cap": (PERSONS, "the number of passengers the ship is certified to carry"),
    "crew": (PERSONS, "the number of persons in the crew responsible for the operation of the ship"),
    "dist": (METRES, "the distance of the overall passenger service, one way, in metres"),
    "nights": (NIGHTS, "the number of overnight stays on board"),
    "dyear": (YEAR, "the year the historical passenger ship (the original, for a replica) was designed"),
    "sch_h": (HOURS, "the whole hours of the scheduled journey"),
    "sch_m": (MINS, "the minutes beyond those whole hours of the scheduled journey"),
    "del_h": (HOURS, "the whole hours of the delay in arrival at the final destination as set out in the transport "
                     "contract"),
    "del_m": (MINS, "the minutes beyond those whole hours of the delay in arrival"),
    "price": (EUR, "the price the passenger actually paid for the delayed passenger service (a single journey)"),
    "rprice": (EUR, "the price paid for the transport by that passenger service, both legs (a return journey)"),
    "thr": (EUR, "the minimum threshold under which the carrier's conditions say payments for compensation will not be "
                 "paid"),
    "base": (EUR, "the price compensation is calculated in relation to (Art 19(3), (4))"),
    "comp": (EUR, "the minimum level of compensation under Art 19(1)"),
    "pay": (EUR, "the minimum compensation the carrier must pay under Art 19 (after Art 19(6) and the exemptions)"),
}
STEP_CONSTANTS = ("base", "comp", "pay")
T19 = [("a", None, 4, 1), ("b", 4, 8, 2), ("c", 8, 24, 3), ("d", 24, None, 6)]  # 19(1): point, more than, not
# exceeding (hours of the scheduled journey), the delay of at least (hours)

FACTS = {  # name -> (item, words); the encoder states each true or false
    "commercial": ("p", "the transport service is commercial"),
    "pax_transport": ("p", "the service is a passenger transport service"),
    "by_sea": ("p", "the service is by sea"),
    "inland": ("p", "the service is on a natural or artificial navigable inland body of water, or system of "
                    "interconnected bodies of water"),
    "water_used": ("p", "that body of water (or system) is used for transport"),
    "timetable": ("p", "the service is operated according to a published timetable"),
    "pleasure": ("p", "the service is operated exclusively for the purpose of pleasure or recreation"),
    "accomm": ("p", "the service is supplemented by accommodation and other facilities"),
    "excursion": ("p", "the passenger is travelling on an excursion or sightseeing tour"),
    "vessel": ("p", "the passenger travels on a vessel"),
    "not_mech": ("p", "the ship is not propelled by mechanical means"),
    "hist": ("p", "the ship is an original, or an individual replica, of a historical passenger ship"),
    "orig_mat": ("p", "the ship is built predominantly with the original materials"),
    "contract": ("p", "the passenger has a contract of carriage with c for the journey"),
    "doc": ("p", "the passenger holds a valid document or other evidence of that contract"),
    "ret": ("p", "the transport is for a return journey"),
    "open_t": ("p", "the passenger holds an open ticket"),
    "dep_spec": ("p", "the time of departure is specified"),
    "pass_t": ("p", "the passenger holds a travel pass or a season ticket"),
    "informed": ("p", "the passenger was informed of the delay before the purchase of the ticket"),
    "fault": ("p", "the delay is caused by the fault of the passenger"),
    "weather": ("p", "the carrier proves that the delay is caused by weather conditions endangering the safe operation "
                     "of the ship (stated judgment)"),
    "extraord": ("p", "the carrier proves that the delay is caused by extraordinary circumstances hindering the "
                      "performance of the passenger service which could not have been avoided even if all reasonable "
                      "measures had been taken (stated judgment)"),
    "has_thr": ("p", "the carrier's conditions state a minimum threshold under which payments for compensation will "
                     "not be paid"),
    "person": ("c", "c is a natural or legal person"),
    "offers_public": ("c", "c offers transport by passenger services or cruises to the general public"),
    "tour_op": ("c", "c is an organiser or retailer within the meaning of Article 2(2) and (3) of Directive 90/314/EEC, "
                     "other than a carrier (a tour operator: stated, Art 3(q) defines by reference)"),
    "retailer": ("c", "c is a retailer"),
    "for_carrier": ("c", "c concludes transport contracts on behalf of a carrier"),
    "for_pax": ("c", "c acts on behalf of a passenger or a tour operator for the conclusion of transport contracts"),
    "est_ms": ("c", "c is established within the territory of a Member State"),
    "other_ms": ("c", "c offers transport by passenger services operated to or from the territory of a Member State "
                      "(other than the case's own service)"),
    "in_ms_e": ("e", "the port of embarkation is situated in the territory of a Member State (TFEU Art 355: stated)"),
    "works_e": ("e", "the place of embarkation has improvement works and facilities permitting the reception of ships"),
    "regular_e": ("e", "passengers regularly embark or disembark there"),
    "in_ms_d": ("d", "the port of disembarkation is situated in the territory of a Member State (stated)"),
    "works_d": ("d", "the place of disembarkation has improvement works and facilities permitting the reception of "
                     "ships"),
    "regular_d": ("d", "passengers regularly embark or disembark there"),
}
STATED = ("weather", "extraord")  # the brief's stated judgments (Art 20(4))
DERIVED_UNARY = {
    "iww": ("p", "the service is on an inland waterway (Art 3(i))"),
    "ship": ("p", "the passenger travels on a ship (Art 3(l))"),
    "ps": ("p", "the passenger travels on a passenger service (Art 3(f))"),
    "cruise": ("p", "the passenger travels on a cruise (Art 3(t))"),
    "port_e": ("e", "the place of embarkation is a port (Art 3(j))"),
    "port_d": ("d", "the place of disembarkation is a port (Art 3(j))"),
    "tv": ("c", "c is a ticket vendor (Art 3(o))"),
    "ta": ("c", "c is a travel agent (Art 3(p))"),
    "carrier": ("c", "c is a carrier (Art 3(d))"),
    "ucarrier": ("c", "c is a Union carrier (Art 3(e))"),
    "tc": ("p", "the passenger's contract is a transport contract (Art 3(m))"),
    "ticket": ("p", "the passenger holds a ticket (Art 3(n))"),
    "a21a": ("p", "Art 2(1)(a) holds"), "a21b": ("p", "Art 2(1)(b) holds"), "a21c": ("p", "Art 2(1)(c) holds"),
    "in21": ("p", "the passenger is one Art 2(1) names"),
    "x22a": ("p", "Art 2(2)(a) holds"), "x22b": ("p", "Art 2(2)(b) holds"), "x22c": ("p", "Art 2(2)(c) holds"),
    "hist_ok": ("p", "the ship is an original or individual replica of a historical passenger ship designed before "
                     "1965, built predominantly with the original materials"),
    "x22d": ("p", "Art 2(2)(d) holds"),
    "ex22": ("p", "the passenger is one Art 2(2) names"),
    "applies": ("p", "the Regulation applies in respect of the passenger on this journey (Art 2(1), (2))"),
    "x20_1": ("p", "Art 20(1) exempts Art 19"), "x20_2": ("p", "Art 20(2) exempts Art 19"),
    "x20_4": ("p", "Art 20(4) exempts Art 19"),
    **{f"band_{r}": ("p", f"the scheduled journey is one of Art 19(1)({r})") for r, *_ in T19},
    "meets": ("p", "the delay is at least the time Art 19(1) sets for the scheduled journey"),
    "dbl": ("p", "the delay exceeds double the time set out in Art 19(1)(a) to (d)"),
    "core": ("p", "every condition of the Art 19 right other than the carrier holds"),
    "right19": ("p", "the passenger may request compensation from the carrier under Art 19 for this delay"),
    "thr_ok": ("p", "the carrier's threshold does not exceed EUR 6"),
    "thr_over": ("p", "the carrier's threshold exceeds EUR 6"),
    "unpaid": ("p", "the compensation is under the carrier's threshold (Art 19(6): not paid)"),
    "doubt6": ("p", "a threshold above EUR 6 and a compensation below EUR 6 (R4: two readings)"),
}


# --- formula helpers (the ve-quantity@1 wire shapes; fwa_australia / council_tax conventions) -----------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def eur(v): return ["decimal", EUR, v]
def hrs(v): return ["decimal", HOURS, str(v)]
def mins(v): return ["decimal", MINS, str(v)]
def num(unit, v): return ["decimal", unit, str(v)]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def scale(tag, n, t): return ["scale", tag, str(n), t]
TRUE, FALSE = ["top"], ["bottom"]


def And(*fs):
    fs = [f for f in fs if f is not None]
    if not fs:
        return TRUE
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["and", f, r]
    return r


def Or(*fs):
    fs = [f for f in fs if f is not None]
    if not fs:
        return FALSE
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["or", f, r]
    return r


def k(base):
    """Per-case integer constant (on the journey item p)."""
    return ["const", INT_UNITS[base][0], f"{base}_p"]


def F(name):
    """A stated or derived unary atom on its item."""
    item = (FACTS.get(name) or DERIVED_UNARY[name])[0]
    return U(name, item)


def iff(name, body): return Iff(F(name), body)


# --- durations as (whole hours, minutes beyond them) -------------------------------------------------------------

def dur_more_than(n_term, h, m):
    """'more than N hours' for a duration of h whole hours and m minutes (N a literal term in hours)."""
    return Or(Lt(n_term, h), And(Eq(h, n_term), Lt(mins(0), m)))


def dur_at_least(n_term, h, m):
    return Le(n_term, h)


def sched(): return k("sch_h"), k("sch_m")
def delay(): return k("del_h"), k("del_m")


# --- the case context --------------------------------------------------------------------------------------------

class Ctx:
    items = ["p", "c", "e", "d"]


def one(fn):
    return lambda ctx: fn()


# --- Art 3 definitions -------------------------------------------------------------------------------------------

def _d_iww(): return [iff("iww", And(F("inland"), F("water_used")))]
def _d_ship(): return [iff("ship", And(F("vessel"), Or(F("by_sea"), F("iww"))))]
def _d_ps(): return [iff("ps", And(F("commercial"), F("pax_transport"), Or(F("by_sea"), F("iww")), F("timetable")))]


def _d_cruise():
    return [iff("cruise", And(Or(F("by_sea"), F("iww")), F("pleasure"), F("accomm"), Lt(num(NIGHTS, 2), k("nights"))))]


def _d_port():
    return [iff("port_e", And(F("works_e"), F("regular_e"))), iff("port_d", And(F("works_d"), F("regular_d")))]


def _d_tv(): return [iff("tv", And(F("retailer"), F("for_carrier")))]
def _d_ta(): return [iff("ta", And(F("retailer"), F("for_pax")))]


def _d_carrier():
    return [iff("carrier", And(F("person"), F("offers_public"), Not(F("tour_op")), Not(F("ta")), Not(F("tv"))))]


def _d_ucarrier():
    """Art 3(e): established in a Member State, or offering transport by passenger services operated to or from the
    territory of a Member State: the case's own service counts when it is a passenger service with a port of
    embarkation or disembarkation in a Member State (c offers it: the contract names c)."""
    own = And(F("ps"), Or(F("in_ms_e"), F("in_ms_d")))
    return [iff("ucarrier", And(F("carrier"), Or(F("est_ms"), F("other_ms"), own)))]


def _d_tc(): return [iff("tc", And(F("contract"), F("carrier"), Or(F("ps"), F("cruise"))))]
def _d_ticket(): return [iff("ticket", And(F("doc"), F("tc")))]


# --- Art 2 -------------------------------------------------------------------------------------------------------

def _a2_1():
    b_geo = And(F("ps"), F("port_e"), Not(F("in_ms_e")), F("port_d"), F("in_ms_d"))
    return [iff("a21a", And(F("ps"), F("port_e"), F("in_ms_e"))),
            # (b) R5: decided only when c is a carrier, or when the ports / service already rule (b) out
            Implies(Not(b_geo), Not(F("a21b"))),
            Implies(F("carrier"), Iff(F("a21b"), And(b_geo, F("ucarrier")))),
            iff("a21c", And(F("cruise"), F("port_e"), F("in_ms_e"))),
            iff("in21", Or(F("a21a"), F("a21b"), F("a21c")))]


def _a2_2():
    r1 = Or(F("not_mech"), And(F("hist_ok"), Le(k("cap"), num(PERSONS, 36))))
    r2 = And(Or(F("not_mech"), F("hist_ok")), Le(k("cap"), num(PERSONS, 36)))
    return [iff("x22a", And(F("ship"), Le(k("cap"), num(PERSONS, 12)))),
            iff("x22b", Or(And(F("ship"), Le(k("crew"), num(PERSONS, 3))), Lt(k("dist"), num(METRES, 500)))),
            iff("x22c", And(F("excursion"), Not(F("cruise")))),
            iff("hist_ok", And(F("hist"), Lt(k("dyear"), num(YEAR, 1965)), F("orig_mat"))),
            # R3: written where the two readings agree; refused where they differ
            Implies(And(F("ship"), r1, r2), F("x22d")),
            Implies(Or(Not(F("ship")), And(Not(r1), Not(r2))), Not(F("x22d"))),
            iff("ex22", Or(F("x22a"), F("x22b"), F("x22c"), F("x22d"))),
            iff("applies", And(F("in21"), Not(F("ex22"))))]


# --- Art 19 and Art 20 -------------------------------------------------------------------------------------------

def _a19_1():
    sh, sm = sched()
    dh, dm = delay()
    out = []
    for r, lo, hi, t in T19:
        out.append(iff(f"band_{r}", And(dur_more_than(hrs(lo), sh, sm) if lo is not None else None,
                                        Not(dur_more_than(hrs(hi), sh, sm)) if hi is not None else None)))
    out.append(iff("meets", Or(*[And(F(f"band_{r}"), dur_at_least(hrs(t), dh, dm)) for r, lo, hi, t in T19])))
    out.append(iff("dbl", Or(*[And(F(f"band_{r}"), dur_more_than(scale(HOURS, 2, hrs(t)), dh, dm))
                               for r, lo, hi, t in T19])))
    core = And(F("applies"), Not(F("a21c")), Not(F("x20_1")), Not(F("x20_2")), Not(F("x20_4")), F("meets"))
    out += [iff("core", core),
            Implies(Not(F("core")), Not(F("right19"))),
            Implies(And(F("core"), F("tc")), F("right19")),  # R5: core without a carrier's contract -> refused
            Implies(And(F("meets"), Not(F("dbl"))), Eq(scale(EUR, 100, k("comp")), scale(EUR, 25, k("base")))),
            Implies(F("dbl"), Eq(scale(EUR, 100, k("comp")), scale(EUR, 50, k("base"))))]
    return out


def _a19_3(): return [Implies(Not(F("ret")), Eq(k("base"), k("price")))]
def _a19_4(): return [Implies(F("ret"), Eq(scale(EUR, 2, k("base")), k("rprice")))]


def _a19_6():
    """Not reduced by transaction costs: no rule subtracts anything. The threshold (R4)."""
    six = eur("6.00")
    return [iff("thr_ok", And(F("has_thr"), Le(k("thr"), six))),
            iff("thr_over", And(F("has_thr"), Lt(six, k("thr")))),
            iff("unpaid", And(F("thr_ok"), Lt(k("comp"), k("thr")))),
            iff("doubt6", And(F("thr_over"), Lt(k("comp"), six))),
            Implies(Not(F("right19")), Eq(k("pay"), eur("0.00"))),
            Implies(And(F("right19"), F("unpaid")), Eq(k("pay"), eur("0.00"))),
            Implies(And(F("right19"), Not(F("unpaid")), Not(F("doubt6"))), Eq(k("pay"), k("comp")))]


def _a20_1(): return [iff("x20_1", And(F("open_t"), Not(F("dep_spec")), Not(F("pass_t"))))]
def _a20_2(): return [iff("x20_2", Or(F("informed"), F("fault")))]
def _a20_4(): return [iff("x20_4", Or(F("weather"), F("extraord")))]


UNITS = {
    1: ("RULE", one(_a2_1), "Art 2(1)(a)-(c) written over the ports (Art 3(j)), the passenger service (3(f)), the cruise "
        "(3(t)) and the Union carrier (3(e)); 'However, Articles ... 19 and 20(1) and (4) shall not apply to those "
        "passengers' written for Art 19 (R6; 16(2), 18 out of scope); R1 (the whole positive scope); R5 for (b)"),
    2: ("PART", one(_a2_2), "other:two readings", "Art 2(2)(a)-(c) written ('up to 12', 'not more than three', 'less "
        "than 500 metres, one way', 'other than cruises'); (d) written where its two readings agree, REFUSED where they "
        "differ (R3: whether 'certified to carry up to 36 passengers' also limits ships not propelled by mechanical "
        "means); 'designed before 1965' compared in Lean with the stated design year"),
    3: ("NOT", None, "definition by reference", "Art 3(b) 'territory of a Member State': a territory to which the TFEU "
        "applies under its Article 355 (not pinned): whether each port is situated in it is a stated fact (fixed facts "
        "of the test)"),
    4: ("RULE", one(_d_carrier), "Art 3(d): a natural or legal person offering transport by passenger services or "
        "cruises to the general public, other than a tour operator (stated, unit 14), travel agent (unit 13) or ticket "
        "vendor (unit 12)"),
    5: ("RULE", one(_d_ucarrier), "Art 3(e): established in a Member State, or offering transport by passenger "
        "services operated to or from the territory of a Member State (the case's own service, or another stated)"),
    6: ("RULE", one(_d_ps), "Art 3(f): commercial, passenger transport, by sea or inland waterways (unit 7), published "
        "timetable (each a stated fact of the operation)"),
    7: ("RULE", one(_d_iww), "Art 3(i): a natural or artificial navigable inland body of water (or system) used for "
        "transport"),
    8: ("RULE", one(_d_port), "Art 3(j): a place with improvement works and facilities permitting the reception of "
        "ships, from which passengers regularly embark or disembark (both ports)"),
    9: ("RULE", one(_d_ship), "Art 3(l): a vessel used for navigation at sea or on inland waterways"),
    10: ("RULE", one(_d_tc), "Art 3(m): a contract of carriage between a carrier and the passenger for passenger "
         "services or cruises (used by the Art 19 right, R5)"),
    11: ("RULE", one(_d_ticket), "Art 3(n): a valid document or other evidence of a transport contract (written; no "
         "in-scope rule turns on it beyond the stated ticket type)"),
    12: ("RULE", one(_d_tv), "Art 3(o): a retailer concluding transport contracts on behalf of a carrier"),
    13: ("RULE", one(_d_ta), "Art 3(p): a retailer acting on behalf of a passenger or a tour operator for the "
         "conclusion of transport contracts"),
    14: ("NOT", None, "definition by reference", "Art 3(q) 'tour operator': an organiser or retailer 'within the "
         "meaning of Article 2(2) and (3) of Directive 90/314/EEC' (not pinned): a stated fact"),
    15: ("RULE", one(_d_cruise), "Art 3(t): by sea or inland waterway, exclusively for pleasure or recreation, "
         "accommodation and other facilities, exceeding two overnight stays on board (compared in Lean)"),
    16: ("RULE", one(_a19_1), "Art 19(1): the four journey bands and their delays (R2), 'exceeds double the time' "
         "(scale 2 of the literal), 25 % / 50 % of the ticket price (100 x comp = 25 / 50 x price: LIN by literals); "
         "the right read with Art 2(1)(c), 20(1), (2), (4) and the carrier (R5)"),
    17: ("RULE", one(_a19_3), "Art 19(3): calculated in relation to the price actually paid for the delayed service"),
    18: ("RULE", one(_a19_4), "Art 19(4): a return journey: half of the price paid for the transport by that passenger "
         "service (2 x base = the return price: PROD by a literal)"),
    19: ("PART", one(_a19_6), "other:two readings", "Art 19(6): not reduced by transaction costs (no rule subtracts "
         "anything); a compensation under the carrier's threshold is not paid (0.00); a threshold above EUR 6 with a "
         "compensation below EUR 6, and Q2 for a compensation under the threshold, REFUSED (R4: two readings)"),
    20: ("RULE", one(_a20_1), "Art 20(1): open ticket while the time of departure is not specified, except a travel "
         "pass or season ticket (Art 19 only; 17, 18 out of scope)"),
    21: ("PART", one(_a20_2), "other:judgment standard", "Art 20(2): written; 'informed ... before the purchase of the "
         "ticket' a stated fact; 'caused by the fault of the passenger' a stated fact (the brief's fixed facts; an "
         "evaluative standard, not a stated judgment of the brief)"),
    22: ("PART", one(_a20_4), "other:judgment standard", "Art 20(4): written; 'weather conditions endangering the safe "
         "operation of the ship' and 'extraordinary circumstances ... which could not have been avoided even if all "
         "reasonable measures had been taken' (and that the carrier proves them) are stated judgments"),
}


def units_table(mutant=None):
    t = dict(UNITS)
    if mutant is not None:
        t = MUTANTS[mutant][1](t)
    return t


def rules(ctx, mutant=None):
    """Ground rules for a case: [{"id", "unit", "formula", "defines"}]."""
    out = []
    table = units_table(mutant)
    entries = [(n, e[1]) for n, e in sorted(table.items()) if e[1] is not None]
    for n, builder in entries:
        for i, f in enumerate(builder(ctx)):
            for j, part in enumerate(conjuncts(f)):
                out.append({"id": f"u{n}.{i}.{j}", "unit": n, "formula": part, "defines": defines(part)})
    return out


# --- structure helpers (fwa_australia / council_tax translation.py conventions) --------------------------------

def key(formula):
    return json.dumps(formula, sort_keys=True, separators=(",", ":"))


def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def is_iff(f):
    return (type(f) is list and f and f[0] == "and" and type(f[1]) is list and type(f[2]) is list
            and f[1][:1] == ["implies"] and f[2][:1] == ["implies"] and f[1][1] == f[2][2] and f[1][2] == f[2][1])


def conjuncts(f):
    if is_iff(f) or type(f) is not list or f[0] != "and":
        return [f]
    return conjuncts(f[1]) + conjuncts(f[2])


def atoms_in(f, atoms, constants):
    if type(f) is not list or not f:
        return
    if f[0] in ("unary", "binary"):
        atoms.add(key(f))
        return
    if f[0] == "const" and len(f) == 3:
        constants.add(f[2])
        return
    for part in f[1:]:
        atoms_in(part, atoms, constants)


def defines(f):
    """The atoms / integer constants a ground rule fixes."""
    if is_iff(f):
        lhs = f[1][1]
        if lhs[0] in ("unary", "binary"):
            return [key(lhs)]
        raise ValueError(f"iff with a non-atom left side: {f}")
    if f[0] == "implies":
        return defines(f[2])
    if f[0] in ("unary", "binary"):
        return [key(f)]
    if f[0] == "not" and f[1][0] in ("unary", "binary"):
        return [key(f[1])]
    if f[0] == "eq" and f[1][0] == "const" and len(f[1]) == 3:
        return [f[1][2]]
    if f[0] == "eq" and f[1][0] == "scale" and f[1][3][0] == "const" and len(f[1][3]) == 3:
        return [f[1][3][2]]
    raise ValueError(f"no defined target: {f}")


# --- the environment for one case -----------------------------------------------------------------------------

UNIT_DECL = {
    EUR: {"scale": "100", "display": {"kind": "money", "currency": "EUR", "input_symbol": "€"}},
    HOURS: {"scale": "1", "display": {"kind": "decimal", "label": "hours"}},
    MINS: {"scale": "1", "display": {"kind": "decimal", "label": "minutes"}},
    PERSONS: {"scale": "1", "display": {"kind": "decimal", "label": "persons"}},
    METRES: {"scale": "1", "display": {"kind": "decimal", "label": "metres"}},
    NIGHTS: {"scale": "1", "display": {"kind": "decimal", "label": "overnight stays"}},
    YEAR: {"scale": "1", "display": {"kind": "decimal", "label": "year"}},
}
ITEM_WORDS = {"p": "the passenger and the journey", "c": "the party the transport contract names as carrier",
              "e": "the place (port) of embarkation", "d": "the place (port) of disembarkation"}


def environment(ctx):
    consts = {}
    for x in ctx.items:
        consts[x] = {"sort": "item", "description": f"The case's {ITEM_WORDS[x]}.", "verbalisation": ITEM_WORDS[x]}
    for base, (u, w) in INT_UNITS.items():
        consts[f"{base}_p"] = {"sort": "$int", "unit": u, "description": f"{w[0].upper() + w[1:]}.",
                               "verbalisation": w}
    preds = {n: {"arguments": ["item"], "description": d[1][0].upper() + d[1][1:] + "."}
             for n, d in {**FACTS, **DERIVED_UNARY}.items()}
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "The passenger, the carrier party and the two ports."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1", "units": UNIT_DECL}


# --- planted errors (run.py --mutants): each must change the answer of at least one question --------------------

def _swap(n, fn):
    def apply(t):
        t = dict(t)
        e = t[n]
        t[n] = (e[0], fn(e[1]), *e[2:])
        return t
    return apply


def _wrap(walker):
    return lambda builder: (lambda ctx: [walker(f) for f in builder(ctx)])


def _json_sub(a, b):
    def walk(f):
        s = json.dumps(f)
        if a not in s:
            raise ValueError(f"mutant pattern not found: {a}")
        return json.loads(s.replace(a, b))
    return lambda f: walk(f) if a in json.dumps(f) else f


def _drop_scale2(f):
    """Mutant helper: ["scale", "hour_count", "2", t] -> t ('double the time' read as the time)."""
    if type(f) is list:
        if f[:3] == ["scale", HOURS, "2"]:
            return f[3]
        return [_drop_scale2(g) for g in f]
    return f


MUTANTS = {
    "M1": ("THRESHOLD: Art 19(1)(a) 'up to 4 hours' and (b) 'more than 4 hours' moved to 5 hours",
           _swap(16, _wrap(_json_sub('["decimal", "hour_count", "4"]', '["decimal", "hour_count", "5"]')))),
    "M2": ("ARITHMETIC: 'exceeds double the time' read as 'exceeds the time' (scale 2 dropped)",
           _swap(16, _wrap(_drop_scale2))),
    "M3": ("ARITHMETIC: 50 % read as 25 %",
           _swap(16, _wrap(_json_sub('"scale", "eur_cent", "50"', '"scale", "eur_cent", "25"')))),
    "M4": ("ARITHMETIC: Art 19(4) 'half of the price' dropped (a return calculated on the full return price)",
           _swap(18, _wrap(_json_sub('"scale", "eur_cent", "2"', '"scale", "eur_cent", "1"')))),
    "M5": ("DEFINITION: Art 3(t) 'exceeding two overnight stays' read as 'two or more'",
           _swap(15, _wrap(_json_sub('["lt", ["decimal", "night_count", "2"]', '["le", ["decimal", "night_count", "2"]')))),
    "M6": ("DEFINITION: Art 3(f) 'operated according to a published timetable' dropped",
           _swap(6, _wrap(_json_sub('["unary", "timetable", ["const", "p"]]', '["top"]')))),
    "M7": ("EXCLUSION: Art 2(2)(a) 'up to 12 passengers' read as 'fewer than 12'",
           _swap(2, _wrap(_json_sub('["le", ["const", "person_count", "cap_p"], ["decimal", "person_count", "12"]]',
                                    '["lt", ["const", "person_count", "cap_p"], ["decimal", "person_count", "12"]]')))),
    "M8": ("EXCEPTION: Art 20(1) 'except for passengers holding a travel pass or a season ticket' dropped",
           _swap(20, _wrap(_json_sub('["not", ["unary", "pass_t", ["const", "p"]]]', '["top"]')))),
    "M9": ("EXCEPTION: Art 2(1)(c) 'However, Articles ... 19 ... shall not apply to those passengers' dropped",
           _swap(16, _wrap(_json_sub('["not", ["unary", "a21c", ["const", "p"]]]', '["top"]')))),
    "M10": ("THRESHOLD: Art 19(6) 'under which' read as 'at or under which'",
            _swap(19, _wrap(_json_sub('["lt", ["const", "eur_cent", "comp_p"], ["const", "eur_cent", "thr_p"]]',
                                      '["le", ["const", "eur_cent", "comp_p"], ["const", "eur_cent", "thr_p"]]')))),
    "M11": ("DEFINITION: Art 3(e) 'offering transport by passenger services operated to or from the territory of a "
            "Member State' read as excluding the case's own service (only another stated service counts)",
            _swap(5, _wrap(_json_sub(json.dumps(And(F("ps"), Or(F("in_ms_e"), F("in_ms_d")))), '["bottom"]')))),
    "M12": ("EXCLUSION: Art 2(2)(b) 'less than 500 metres' read as '500 metres or less'",
            _swap(2, _wrap(_json_sub('["lt", ["const", "metre_count", "dist_p"]', '["le", ["const", "metre_count", "dist_p"]')))),
    "M13": ("EXEMPTION: Art 20(2) 'caused by the fault of the passenger' dropped",
            _swap(21, _wrap(_json_sub('["unary", "fault", ["const", "p"]]', '["bottom"]')))),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
