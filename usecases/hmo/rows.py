"""HMO England (statute corpus law 3): the translation's formulas, one pass with today's language. SAME-FAMILY (Opus 5.5).

Written from usecases/hmo/source/hmo-england.txt ONLY (sha256 29fd379a...f6e8481a7), after the question set was sealed
(manage-agents reviews/spare/statute-corpus/hmo/ISOLATION.md, 11:01Z) and BEFORE the encoder's file was opened: no question
was read when these rows were written (commit order: this file first, cases.py later).

Vocabulary: three sorts. person (the people a case names), place (the premises asked about = constant `premises`, the units of
living accommodation it consists of, the other flats of its block), amenity (toilet, washing, cooking and one non-basic
facility, so that "basic amenities" is a real restriction). Every rule is a closed formula of relational first-order logic
over this vocabulary (ve.core@0.2, relational-fol@0); translation.py grounds it over a case's named people and places.

`AtLeast(k, sort, body)` is an ABBREVIATION, not a new construct: it stands for
"exists x1 ... exists xk, pairwise different, with body(xi) for each i", a formula of the same logic (translation.py expands
it either way and checks that both give the same ground formula on small domains: test_translation.py).

Each row: n -> (category, formula, note, units) where units are the unit numbers n of
manage-agents reviews/spare/statute-corpus/hmo/units.jsonl that the row writes (the ledger's link).
Categories: RULE (a formula), NAME (a term defined by another Act: a stated fact), NOT (not written: see the ledger).

READINGS chosen by the translator (each is listed in RESULT.md as translator judgement):
 J1 s.258(2)(a) "all members of the same family" is read PAIRWISE: a group forms a single household exactly when every two of
    its members are of the same family (or within regs 3-4). "Two or more separate households" (art. 4(b), s.254(2)(f),
    Sch. 14 para 7) = some two occupants not of one household.
 J2 Sch. 14 para 6 needs at least one occupier with the freehold or a long lease (the "(a) one or more persons"), and "member
    of the household" in para 6(1)(b) is read with s.258 (same household).
 J3 s.254(2)(f) "share": two people of different households share a basic amenity when each of them shares that amenity
    (one shared facility of that kind in the premises); "lacking" = some basic amenity is not available to the premises'
    occupants at all.
 J4 s.254(4)(c)-(f): "the living accommodation" = the units that are not self-contained flats; its occupiers are those who
    live in such a unit.
 J5 reg. 3(2)(c) "does not pay any rent or other consideration" = no rent or consideration other than the work is payable for
    person A's occupation.
 J6 reg. 3(2)(a) "exclusively domestic": a stated fact, or all of A's work for B being work of a kind listed in reg. 3(3).
"""
from __future__ import annotations

PERSONS = tuple(f"person{i}" for i in range(1, 17))
PLACES = ("premises",) + tuple(f"unit{i}" for i in range(1, 13)) + tuple(f"flat{i}" for i in range(1, 9))
AMENITIES = {"toilet": "a toilet", "washing": "personal washing facilities", "cooking": "cooking facilities",
             "other_facility": "a facility that is not one of the three basic amenities (a lounge, a garden, ...)"}
P = "premises"

# ---- base predicates: facts a case states (closed: every one gets true or false) ----------------------------------------
PLACE1 = {
    "within": "is a unit of living accommodation of which the premises consist (the premises itself when it is one unit)",
    "separate_set": "is a separate set of premises (whether or not on the same floor)",
    "part_of_building": "forms part of a building (is not a whole building)",
    "above_below": "the whole or a material part of it lies above or below some other part of the building",
    "created_since": "was created as a unit of living accommodation since the building or part was constructed",
    "in_block": "is a self-standing flat of the block in which the premises (a flat) is situated, the premises included",
    "is_part": "is a part of a building (the premises asked about is not a whole building)",
    "only_use": "the occupation of its living accommodation by its occupiers is the only use of that accommodation",
    "purpose_built": "is a purpose-built flat",
    "decl": "an HMO declaration is in force in respect of it under section 255",
    "s257": "is a converted block of flats to which section 257 applies",
    "vol_org": "is managed by a voluntary organisation",
    "abuse_refuge_use": "is used wholly or mainly for the temporary accommodation of persons who have left their homes as a "
                        "result of physical violence, mental abuse or threats of them from persons who are or were their "
                        "spouses or civil partners or with whom they are or were co-habiting",
    "mgr_lha": "the person managing or having control of it is a local housing authority",
    "mgr_nprp": "... is a non-profit registered provider of social housing",
    "mgr_rsl": "... is a body registered as a social landlord under Part 1 of the Housing Act 1996",
    "mgr_pcc": "... is a police and crime commissioner",
    "mgr_mopac": "... is the Mayor's Office for Policing and Crime",
    "mgr_fra": "... is a fire and rescue authority under the Fire and Rescue Services Act 2004",
    "mgr_hsb": "... is a health service body within section 9 of the National Health Service Act 2006",
    "mgr_prp": "... is a profit-making registered provider of social housing",
    "social_housing": "is social housing within the meaning of Part 2 of the Housing and Regeneration Act 2008",
    "mgr_coop_body": "the person managing or having control of it is a body registered as a co-operative society under the "
                     "2014 Act, or a pre-commencement society meeting the condition in s.2(2)(a)(i) of that Act",
    "coop_rule_a": "the manager's rules secure that membership is restricted to occupiers or prospective occupiers of its buildings",
    "coop_rule_b": "the manager's rules secure that all management decisions are made by the members at a general meeting "
                   "all members are entitled to, and invited to, attend",
    "coop_rule_c": "the manager's rules secure that each member has equal voting rights at such a meeting",
    "coop_rule_d": "the manager's rules secure that a non-member occupier occupies only by sharing with a member at the "
                   "member's invitation",
    "religious": "is occupied principally for the purposes of a religious community whose principal occupation is prayer, "
                 "contemplation, education or the relief of suffering (stated judgment)",
}
PLACE_AMENITY = {
    "excl_amenity": "the amenity is available in the place for the exclusive use of the place's occupants",
    "has_amenity": "the amenity is available to the place's occupants (for their exclusive use or shared)",
}
PERSON1 = {
    "main_res": "occupies the place where they live as their only or main residence",
    "ft_student": "occupies it as their residence for the purpose of undertaking a full-time course of further or higher education",
    "rent_payable": "rent is payable or other consideration (other than work within reg. 3) is to be provided in respect of "
                    "the person's occupation",
    "res_scheme_employed": "has leave to enter or remain granted by virtue of residence scheme immigration rules and has taken "
                           "up activity in the UK as an employed person",
    "work_permit": "has a permit indicating, under the immigration rules, eligibility (not a British citizen) for entry to "
                   "the UK to take employment",
    "frontier_worker": "is a frontier worker within reg. 3 of the Citizens' Rights (Frontier Workers) (EU Exit) Regs 2020",
    "seasonal_emp": "carries out for an employer employment of a seasonal character whose nature depends on the cycle of the "
                    "seasons and recurs automatically each year",
    "le_8_months": "that seasonal employment's duration cannot exceed eight months",
    "consid_employment": "the person's occupation is made partly in consideration of their employment within the UK",
    "employer_provided": "the building or part is provided by, or on behalf of, the person's employer or an agent or employee of it",
    "asylum": "is an asylum seeker (s.94 IAA 1999) or a dependant of one",
    "s95": "has been provided with this accommodation under section 95 of the Immigration and Asylum Act 1999",
    "nass": "that accommodation is funded partly or wholly by the National Asylum Support Service",
    "listed_work": "all the work or service the person carries out (for the person they work for) is work usually carried out "
                   "by an au pair, nanny, nurse, carer, governess, servant (maid, butler, cook, cleaner), chauffeur, "
                   "gardener, secretary or personal assistant",
    "excl_domestic": "the work or service the person carries out is of an exclusively domestic nature (stated judgment)",
    "apc": "is an adult placement carer approved under the Adult Placement Schemes (England) Regulations 2004",
    "le3_users": "provides care in that accommodation for not more than three service users under a permitted scheme",
    "freehold": "has the freehold estate in the whole or a part of the premises",
    "long_lease": "has a leasehold interest in the whole or a part of the premises granted for a term of more than 21 years",
    "occ_ast": "occupies premises in the building by virtue of an assured, a secure or a protected tenancy",
}
PERSON2 = {
    "married": "the two are married to each other",
    "civil_partners": "the two are civil partners of each other",
    "living_as": "the two live together as if they were a married couple or civil partners",
    "parent_of": "the first is a parent of the second",
    "step_parent_of": "the second is the first's stepchild",
    "grandparent_of": "the first is a grandparent of the second",
    "sibling_of": "the two are brother or sister of the whole blood",
    "half_sibling_of": "the two are brother or sister of the half-blood",
    "uncle_aunt_of": "the first is an uncle or aunt (whole blood) of the second",
    "half_uncle_aunt_of": "the first is an uncle or aunt of the half-blood of the second",
    "cousin_of": "the two are cousins",
    "works_for": "the first carries out work or performs a service for the second",
    "supplied_by": "the first's living accommodation is supplied by the second as part of the consideration for the work",
    "receives_care": "the first receives care from the second (the carer) in living accommodation in the same building or part",
    "fostered_with": "the first is placed with the second, the foster parent, under the Fostering Services Regulations 2002",
}
PERSON_PLACE = {"lives_in": "the person occupies the place (a unit of living accommodation)"}
PERSON_AMENITY = {"shares": "the person shares the amenity with other occupiers of the premises (one such facility of that kind)"}

# ---- derived predicates (each fixed by one rule below) --------------------------------------------------------------------
DERIVED_PLACE1 = {
    "scf": "is a self-contained flat (s.254(8))",
    "converted": "is a converted building (s.254(8))",
    "refuge": "is a refuge (s.259(3))",
    "units_non_scf": "s.254(2)(a): consists of one or more units of living accommodation none of which is a self-contained flat",
    "some_non_scf": "s.254(4)(b): contains a unit of living accommodation that is not a self-contained flat",
    "not_single": "its occupiers do not form a single household (s.254(2)(b), art. 4(b))",
    "not_single_n": "the occupiers of its non-flat units do not form a single household (s.254(4)(c))",
    "residence_all": "s.254(2)(c): every occupier occupies as only or main residence or is treated as so occupying",
    "residence_all_n": "s.254(4)(d): the same, for the occupiers of its non-flat units",
    "rent_one": "s.254(2)(e): rent or other consideration is payable for at least one occupier",
    "rent_one_n": "s.254(4)(f): the same, for the occupiers of its non-flat units",
    "lacks": "its living accommodation lacks one or more basic amenities",
    "shared_between": "two or more of its households share one or more basic amenities",
    "standard": "meets the standard test (s.254(2))",
    "scf_test": "meets the self-contained flat test (s.254(3))",
    "converted_test": "meets the converted building test (s.254(4))",
    "within_254_1": "is within s.254(1)",
    "sch14_2": "is listed in Sch. 14 para 2", "sch14_2a": "is listed in Sch. 14 para 2A",
    "sch14_2b": "is listed in Sch. 14 para 2B", "sch14_5": "is listed in Sch. 14 para 5",
    "sch14_6": "is listed in Sch. 14 para 6", "sch14_7": "is listed in Sch. 14 para 7",
    "sch14": "is listed in Schedule 14",
    "hmo": "is a house in multiple occupation for the purposes of the Act other than Part 1",
    "five_plus": "is occupied by five or more persons",
    "block3": "is situated in a block comprising three or more self-contained flats",
    "prescribed": "is an HMO of the prescribed description in art. 4 of SI 2018/221",
}
DERIVED_PERSON1 = {
    "occ": "occupies a unit of living accommodation of the premises",
    "occ_n": "occupies a unit of the premises that is not a self-contained flat",
    "migrant": "is a migrant worker (reg. 5(2)(a))",
    "seasonal": "is a seasonal worker (reg. 5(2)(d))",
    "treated_main": "is treated as occupying as only or main residence (s.259(2), reg. 5)",
    "residence_ok": "occupies as only or main residence or is treated as so occupying",
    "excl_dom": "the work is of an exclusively domestic nature (reg. 3(2)(a), (3))",
    "owner": "occupies and has the freehold or a lease granted for more than 21 years (Sch. 14 para 6(1)(a))",
    "owner_hh": "occupies and is a member of the household of an occupier within para 6(1)(a) (para 6(1)(b))",
    "other6": "occupies and is neither within para 6(1)(a) nor (b)",
}
DERIVED_PERSON2 = {
    "couple": "the two are a couple (s.258(4)(a))",
    "parent_rel": "the first is a parent of the second, a stepchild counted as a child (s.258(4)(d))",
    "sib_rel": "the two are brother or sister, the half-blood counted as the whole blood (s.258(4)(c))",
    "unc_rel": "the first is uncle or aunt of the second, the half-blood counted as the whole blood (s.258(4)(c))",
    "relative": "one is a relative of the other (s.258(4)(b))",
    "family": "the two are members of the same family (s.258(3))",
    "dom_worker": "the first is a domestic worker of the second within reg. 3(2)",
    "reg3_hh": "the two are regarded as one household under reg. 3(1), (4)",
    "reg4_hh": "the two are regarded as one household under reg. 4(1) or (2)",
    "same_hh": "the two form a single household (s.258(2))",
    "with_family": "the first is the second, or an occupier who is a member of the second's family",
}


def environment():
    consts = {}
    for n in PERSONS:
        consts[n] = {"sort": "person", "description": f"A person the case names ({n}).", "verbalisation": n}
    for n in PLACES:
        consts[n] = {"sort": "place", "description": f"A place the case names ({n}).", "verbalisation": n}
    for n, w in AMENITIES.items():
        consts[n] = {"sort": "amenity", "description": w[0].upper() + w[1:] + ".", "verbalisation": w}
    preds = {}
    for table, args in ((PLACE1, ["place"]), (DERIVED_PLACE1, ["place"]), (PLACE_AMENITY, ["place", "amenity"]),
                        (PERSON1, ["person"]), (DERIVED_PERSON1, ["person"]), (PERSON2, ["person", "person"]),
                        (DERIVED_PERSON2, ["person", "person"]), (PERSON_PLACE, ["person", "place"]),
                       (PERSON_AMENITY, ["person", "amenity"])):
        for n, d in table.items():
            preds[n] = {"arguments": args, "description": d[0].upper() + d[1:] + "."}
    preds["basic_amenity"] = {"arguments": ["amenity"], "description": "Is a basic amenity (s.254(8))."}
    sorts = {s: {"description": f"A {s}."} for s in ("person", "place", "amenity")}
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": sorts, "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1", "units": {"day": {"scale": "1", "display": {"kind": "iso_date"}}}}


# ---- formula helpers (the same JSON formulas as usecases/pawhp/rows_v2.py) -------------------------------------------------
def c(n): return ["const", n]
def t(x): return c(x) if isinstance(x, str) else x
def U(p, x): return ["unary", p, t(x)]
def B(p, x, y): return ["binary", p, t(x), t(y)]
def Not(f): return ["not", f]
def V(i): return ["var", i]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def All(sort, f): return ["forall", sort, f]
def Ex(sort, f): return ["exists", sort, f]
def Eq(a, b): return ["eq", t(a), t(b)]
def AtLeast(k, sort, body): return ["atleast", k, sort, body]  # abbreviation; body uses V(0) for the counted variable


def And(*fs):
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["and", f, r]
    return r


def Or(*fs):
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["or", f, r]
    return r


def PL(body):  # forall place x. body(x)
    return All("place", body(V(0)))


def P1(body):
    return All("person", body(V(0)))


def P2(body):  # forall person p, q: p = V(1), q = V(0)
    return All("person", All("person", body(V(1), V(0))))


def some_basic(f):  # exists amenity a: basic(a) and f(a); a = V(0) at the place of use
    return Ex("amenity", And(U("basic_amenity", V(0)), f(V(0))))


def occ_some(pred_unit, p):
    """the person p (a term one level out) lives in a unit of the premises (satisfying pred_unit, if given)."""
    parts = [U("within", V(0))] + ([pred_unit(V(0))] if pred_unit else []) + [["binary", "lives_in", shift(p), V(0)]]
    return Ex("place", And(*parts))


def shift(term, by=1):
    if term[0] == "var":
        return ["var", term[1] + by]
    return term


def not_single(occ_pred):
    # some two occupiers (by occ_pred) do not form a single household (J1)
    return Ex("person", Ex("person", And(U(occ_pred, V(1)), U(occ_pred, V(0)), Not(B("same_hh", V(1), V(0))))))


T = {
    # ---- SI 2018/221 art. 4 (unit 1) ----
    1: ("RULE", Iff(U("five_plus", P), AtLeast(5, "person", U("occ", V(0)))), "art. 4(a)", [1]),
    2: ("RULE", Iff(U("block3", P), AtLeast(3, "place", And(U("in_block", V(0)), U("scf", V(0))))),
        "art. 4(c)(ii): a block comprising three or more self-contained flats", [1]),
    3: ("RULE", Iff(U("prescribed", P),
                    And(U("hmo", P), U("five_plus", P), U("not_single", P),
                        Or(U("standard", P), And(U("scf_test", P), Not(And(U("purpose_built", P), U("block3", P)))),
                           U("converted_test", P)))),
        "art. 4: an HMO (for the Act's purposes other than Part 1: Part 2 is one) of the prescribed description; (b) two or "
        "more separate households = not_single (J1)", [1]),
    # ---- s.254(1), (5) (units 2, 6) ----
    4: ("RULE", Iff(U("within_254_1", P), Or(U("standard", P), U("scf_test", P), U("converted_test", P), U("decl", P),
                                             U("s257", P))), "s.254(1)(a)-(e)", [2]),
    5: ("RULE", Iff(U("hmo", P), And(U("within_254_1", P), Not(U("sch14", P)))), "s.254(5)", [6]),
    # ---- s.254(2) standard test (unit 3) ----
    6: ("RULE", P1(lambda p: Iff(U("occ", p), occ_some(None, p))),
        "an occupier of the premises' living accommodation", [3]),
    7: ("RULE", Iff(U("units_non_scf", P), And(Ex("place", U("within", V(0))),
                                               All("place", Implies(U("within", V(0)), Not(U("scf", V(0))))))),
        "s.254(2)(a)", [3]),
    8: ("RULE", Iff(U("not_single", P), not_single("occ")), "s.254(2)(b), J1", [3]),
    9: ("RULE", Iff(U("residence_all", P), P1(lambda p: Implies(U("occ", p), U("residence_ok", p)))), "s.254(2)(c)", [3]),
    10: ("RULE", Iff(U("rent_one", P), Ex("person", And(U("occ", V(0)), U("rent_payable", V(0))))), "s.254(2)(e)", [3]),
    11: ("RULE", Iff(U("lacks", P), some_basic(lambda a: Not(["binary", "has_amenity", c(P), a]))), "s.254(2)(f) second limb, J3", [3]),
    12: ("RULE", Iff(U("shared_between", P),
                     Ex("person", Ex("person", And(U("occ", V(1)), U("occ", V(0)), Not(B("same_hh", V(1), V(0))),
                                                   Ex("amenity", And(U("basic_amenity", V(0)),
                                                                     ["binary", "shares", V(2), V(0)],
                                                                     ["binary", "shares", V(1), V(0)])))))),
         "s.254(2)(f) first limb, J3", [3]),
    13: ("RULE", Iff(U("standard", P), And(U("units_non_scf", P), U("not_single", P), U("residence_all", P),
                                          U("only_use", P), U("rent_one", P),
                                          Or(U("shared_between", P), U("lacks", P)))), "s.254(2)(a)-(f)", [3]),
    # ---- s.254(3) (unit 4) ----
    14: ("RULE", Iff(U("scf_test", P), And(U("is_part", P), U("scf", P), U("not_single", P), U("residence_all", P),
                                          U("only_use", P), U("rent_one", P),
                                          Or(U("shared_between", P), U("lacks", P)))),
         "s.254(3): (a) it consists of a self-contained flat; (b) (2)(b)-(f) read for the flat (the premises is the flat)", [4]),
    # ---- s.254(4) (unit 5) ----
    15: ("RULE", P1(lambda p: Iff(U("occ_n", p), occ_some(lambda u: Not(["unary", "scf", u]), p))), "J4", [5]),
    16: ("RULE", Iff(U("some_non_scf", P), Ex("place", And(U("within", V(0)), Not(U("scf", V(0)))))), "s.254(4)(b)", [5]),
    17: ("RULE", Iff(U("not_single_n", P), not_single("occ_n")), "s.254(4)(c), J1, J4", [5]),
    18: ("RULE", Iff(U("residence_all_n", P), P1(lambda p: Implies(U("occ_n", p), U("residence_ok", p)))), "s.254(4)(d)", [5]),
    19: ("RULE", Iff(U("rent_one_n", P), Ex("person", And(U("occ_n", V(0)), U("rent_payable", V(0))))), "s.254(4)(f)", [5]),
    20: ("RULE", Iff(U("converted_test", P), And(U("converted", P), U("some_non_scf", P), U("not_single_n", P),
                                                U("residence_all_n", P), U("only_use", P), U("rent_one_n", P))),
         "s.254(4)(a)-(f); (e) only use: the premises' fact", [5]),
    # ---- s.254(8) (units 7, 8, 10) ----
    21: ("RULE", And(U("basic_amenity", "toilet"), U("basic_amenity", "washing"), U("basic_amenity", "cooking"),
                     Not(U("basic_amenity", "other_facility"))), "basic amenities: (a)-(c), a closed list", [7]),
    22: ("RULE", Iff(U("converted", P), Ex("place", And(U("within", V(0)), U("created_since", V(0))))),
         "converted building: living accommodation in which one or more units have been created since construction", [8]),
    23: ("NOT", None, "\"enactment\": used only by s.254(6)-(7) (powers, out of scope); no question can turn on it", [9]),
    24: ("RULE", PL(lambda x: Iff(U("scf", x), And(U("separate_set", x), U("part_of_building", x), U("above_below", x),
                                                  All("amenity", Implies(U("basic_amenity", V(0)),
                                                                         ["binary", "excl_amenity", shift(x), V(0)]))))),
         "self-contained flat (a)-(c); 'a material part' is a stated fact (judgment)", [10]),
    # ---- s.258 (units 11-13) ----
    25: ("RULE", P2(lambda p, q: Iff(B("couple", p, q), And(Not(Eq(p, q)), Or(B("married", p, q), B("married", q, p),
                                                                              B("civil_partners", p, q), B("civil_partners", q, p),
                                                                              B("living_as", p, q), B("living_as", q, p))))),
         "s.258(3)(a) with (4)(a)", [12, 13]),
    26: ("RULE", P2(lambda p, q: Iff(B("parent_rel", p, q), Or(B("parent_of", p, q), B("step_parent_of", p, q)))),
         "s.258(4)(d): a stepchild is a child", [13]),
    27: ("RULE", P2(lambda p, q: Iff(B("sib_rel", p, q), Or(B("sibling_of", p, q), B("sibling_of", q, p),
                                                           B("half_sibling_of", p, q), B("half_sibling_of", q, p)))),
         "s.258(4)(c): half-blood as whole blood (brothers and sisters)", [13]),
    28: ("RULE", P2(lambda p, q: Iff(B("unc_rel", p, q), Or(B("uncle_aunt_of", p, q), B("half_uncle_aunt_of", p, q)))),
         "s.258(4)(c): half-blood as whole blood (uncles and aunts; nephews and nieces are the converse)", [13]),
    29: ("RULE", P2(lambda p, q: Iff(B("relative", p, q), And(Not(Eq(p, q)), Or(
        B("parent_rel", p, q), B("parent_rel", q, p), B("grandparent_of", p, q), B("grandparent_of", q, p),
        B("sib_rel", p, q), B("unc_rel", p, q), B("unc_rel", q, p), B("cousin_of", p, q), B("cousin_of", q, p))))),
         "s.258(4)(b): parent, grandparent, child, grandchild, brother, sister, uncle, aunt, nephew, niece, cousin", [13]),
    30: ("RULE", P2(lambda p, q: Iff(B("family", p, q), Or(
        B("couple", p, q), B("relative", p, q),
        # (c): one of them is, or is a relative of, one member of a couple and the other is a relative of the other member
        Ex("person", Ex("person", And(B("couple", V(1), V(0)),
                                      Or(Eq(shift(p, 2), V(1)), B("relative", shift(p, 2), V(1))),
                                      B("relative", shift(q, 2), V(0))))),
        Ex("person", Ex("person", And(B("couple", V(1), V(0)),
                                      Or(Eq(shift(q, 2), V(1)), B("relative", shift(q, 2), V(1))),
                                      B("relative", shift(p, 2), V(0)))))))),
         "s.258(3)(a)-(c)", [12]),
    31: ("RULE", P2(lambda p, q: Iff(B("same_hh", p, q), Or(Eq(p, q), B("family", p, q), B("reg3_hh", p, q),
                                                           B("reg3_hh", q, p), B("reg4_hh", p, q), B("reg4_hh", q, p)))),
         "s.258(2)(a) and (b) (regs 3, 4), J1", [11]),
    # ---- s.259 (units 14, 15) ----
    32: ("RULE", Iff(U("refuge", P), And(U("vol_org", P), U("abuse_refuge_use", P))), "s.259(3)", [15]),
    33: ("RULE", P1(lambda p: Iff(U("treated_main", p), Or(U("ft_student", p), And(U("occ", p), U("refuge", P)),
                                                           And(Or(U("migrant", p), U("seasonal", p)),
                                                               U("consid_employment", p), U("employer_provided", p)),
                                                           And(U("asylum", p), U("s95", p), U("nass", p))))),
         "s.259(2)(a)-(c) with SI 2006/373 reg. 5(1)", [14, 23]),
    34: ("RULE", P1(lambda p: Iff(U("residence_ok", p), Or(U("main_res", p), U("treated_main", p)))),
         "s.254(2)(c): only or main residence or treated as so occupying", [3, 14]),
    # ---- SI 2006/373 reg. 3 (units 16-19) ----
    35: ("RULE", P1(lambda p: Iff(U("excl_dom", p), Or(U("excl_domestic", p), U("listed_work", p)))),
         "reg. 3(2)(a) with (3), J6", [17, 18]),
    36: ("RULE", P2(lambda a, b: Iff(B("dom_worker", a, b), And(Not(Eq(a, b)), B("works_for", a, b), U("excl_dom", a),
                                                               B("supplied_by", a, b), Not(U("rent_payable", a))))),
         "reg. 3(2)(a)-(c), J5 (work for a member of B's family: B is that member, whose family joins by rule 37)", [17]),
    37: ("RULE", P2(lambda x, y: Iff(B("reg3_hh", x, y), Ex("person", Ex("person", And(
        B("dom_worker", V(1), V(0)), U("occ", V(1)), U("occ", V(0)),
        B("with_family", shift(x, 2), V(1)), B("with_family", shift(y, 2), V(0))))))),
         "reg. 3(1) and (4): A with his occupying family, B with his family living with him", [16, 19]),
    53: ("RULE", P2(lambda x, a: Iff(B("with_family", x, a), Or(Eq(x, a), And(U("occ", x), B("family", x, a))))),
         "reg. 3(1)(b), (4): a person, or an occupier of the same family (a step of rule 37)", [16, 19]),
    # ---- reg. 4 (units 20-22) ----
    38: ("RULE", P2(lambda p, q: Iff(B("reg4_hh", p, q), Or(And(B("receives_care", p, q), U("apc", q), U("le3_users", q)),
                                                           B("fostered_with", p, q)))),
         "reg. 4(1), (2); 'adult placement carer', 'service users' (4(3)) are stated facts", [20, 21]),
    39: ("NAME", None, "reg. 4(3): adult placement carer and service users take their meanings from SI 2004/2071: stated facts", [22]),
    # ---- reg. 5 (units 23, 24) ----
    40: ("RULE", P1(lambda p: Iff(U("migrant", p), Or(U("res_scheme_employed", p), U("work_permit", p), U("frontier_worker", p)))),
         "reg. 5(2)(a)(i)-(iii); the immigration-rule statuses are stated facts", [24]),
    41: ("RULE", P1(lambda p: Iff(U("seasonal", p), And(U("seasonal_emp", p), U("le_8_months", p)))), "reg. 5(2)(d)", [24]),
    # ---- reg. 6(2) with Sch. 14 para 6 (units 25, 36) ----
    42: ("RULE", P1(lambda p: Iff(U("owner", p), And(U("occ", p), Or(U("freehold", p), U("long_lease", p))))),
         "para 6(1)(a); 'more than 21 years' compared by the encoder on the stated term (listed)", [36]),
    43: ("RULE", P1(lambda p: Iff(U("owner_hh", p), And(U("occ", p), Not(U("owner", p)),
                                                        Ex("person", And(U("owner", V(0)), B("same_hh", shift(p), V(0)))))))
         , "para 6(1)(b), J2", [36]),
    44: ("RULE", P1(lambda p: Iff(U("other6", p), And(U("occ", p), Not(U("owner", p)), Not(U("owner_hh", p))))),
         "para 6(1)(c)", [36]),
    45: ("RULE", Iff(U("sch14_6", P), And(Ex("person", U("owner", V(0))), Not(AtLeast(3, "person", U("other6", V(0)))),
                                         Not(U("s257", P)))),
         "para 6(1) with reg. 6(2) (no more than two others); 6(2): not for a s.257 block itself (a flat in one is not the "
         "block, so the exception is met), J2", [25, 36, 37]),
    # ---- Sch. 14 paras 1, 2, 2A, 2B, 5, 7 (units 26-35) ----
    46: ("RULE", Iff(U("sch14_2", P), Or(U("mgr_lha", P), U("mgr_nprp", P), U("mgr_rsl", P), U("mgr_pcc", P),
                                         U("mgr_mopac", P), U("mgr_fra", P), U("mgr_hsb", P))),
         "para 2(1)(a)-(f) with (aa); para 1(2): a 'building' includes a part (every rule speaks of the premises)", [26, 27, 28]),
    47: ("RULE", Iff(U("sch14_2a", P), And(U("social_housing", P), U("mgr_prp", P))), "para 2A", [29]),
    48: ("RULE", Iff(U("sch14_2b", P), And(U("mgr_coop_body", P), Not(U("mgr_nprp", P)), Not(U("mgr_rsl", P)),
                                          U("coop_rule_a", P), U("coop_rule_b", P), U("coop_rule_c", P), U("coop_rule_d", P),
                                          Not(Ex("person", U("occ_ast", V(0)))))),
         "para 2B(1)-(3); the tenancy kinds of (4) are stated facts", [30, 31, 32]),
    49: ("NAME", None, "para 2B(4): assured / protected / secure tenancy by reference to other Acts: stated facts", [33, 34]),
    50: ("RULE", Iff(U("sch14_5", P), And(U("religious", P), Not(U("s257", P)))), "para 5(1), (2); 'principally' stated", [35, 36]),
    51: ("RULE", Iff(U("sch14_7", P), And(AtLeast(2, "person", U("occ", V(0))), Not(AtLeast(3, "person", U("occ", V(0)))),
                                         U("not_single", P))), "para 7 (not a unit of units.jsonl), J1", []),
    52: ("RULE", Iff(U("sch14", P), Or(U("sch14_2", P), U("sch14_2a", P), U("sch14_2b", P), U("sch14_5", P),
                                       U("sch14_6", P), U("sch14_7", P))), "s.254(5) with Sch. 14 para 1(1)", [6]),
}
