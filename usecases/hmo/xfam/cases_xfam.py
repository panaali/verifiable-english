"""HMO England: the ENCODER's file for a CROSS-FAMILY question set. Copy this file to /work/out/cases_xfam.py and fill CASES
and PROBES from /work/questions-enc.jsonl ONLY (id, scope, premises, facts).

The record format and the conventions below are the frozen build's (its own encoder file uses them unchanged; only the
examples in brackets were made generic). encode.py turns each record into closed facts; rows.py holds the vocabulary.

ENCODING CONVENTIONS (every case; counted as encoder judgement in the result):
 C1 Domain closure (prompt F4): the case names everyone who occupies the premises; people are person1.. in the order named;
    places are `premises` and, where the premises consist of several units or sit in a block, unit1.. / flat1...
 C2 Relations between people are those the facts state; relations not stated do not exist (the facts describe the
    occupants' relations), EXCEPT a relation the facts imply only through the law's own deemings (s.258(4)(c), (d)): that is
    VE's to derive; where the facts state a kinship chain VE's vocabulary cannot compose (a step-grandchild), the base relation
    is left UNKNOWN (no literal), so VE refuses what turns on it. Plain kinship consequences of stated facts (the son of
    X's sister is X's nephew) are encoded and listed per case.
 C3 A whole building let as one dwelling is one unit: the premises itself (within(premises)); a building of flats or bedsits
    has one place per unit. "Has its own front door / a separate set of rooms" = separate_set.
 C4 An HMO declaration (s.255) or a s.257 status the facts do not mention is not in force / does not apply.
 C5 "They share the kitchen and bathroom(s)" = each named sharer shares cooking, toilet and personal washing facilities.
 C6 Rent: rent_payable(p) when rent or other consideration (a charge, a contribution, a payment by a funder) is payable for
    p's occupation, whoever pays it; a domestic worker's work is not counted (reg. 3(2)(c)).
 C7 A number stated in the facts compared with a number in the text (a lease's stated term against "more than 21 years"; a
    stated number of service users against "not more than three") is compared by the encoder: listed per case.
 C8 A status the facts do not state and nothing settles (only or main residence where unstated) is left UNKNOWN.
Per-case judgement beyond C1-C8 is in "judgement".

RECORD FORMAT (one dict per in-scope case; encode.facts(record) must accept it):
  "id":       the case id, e.g. "H001"
  "people":   the occupants' names in the order the facts name them (C1); at most 16
  "places":   ["premises"] plus any "unit1".."unit12" / "flat1".."flat8" the case needs (C1, C3)
  "place":    {place: [PLACE1 predicate names true of that place]}   (rows.PLACE1; every other PLACE1 literal is false)
  "amen":     {place: {"has": [amenities available], "excl": [amenities for the exclusive use of its occupants]}}
              amenities: "toilet", "washing", "cooking", "other_facility" (rows.AMENITIES)
  "lives":    {person: place}                                       (lives_in)
  "all":      [PERSON1 predicate names true of every person]
  "person":   {person: [PERSON1 predicate names true of that person]}
  "rel":      [(person_a, person_b, PERSON2 predicate name)]       (as rows.PERSON2 words it: first, second)
  "shares":   {person: [amenities that person shares with other occupiers]}
  "unknown":  [("unary", pred, name) | ("binary", pred, name1, name2)]: literals left out (C2, C8): VE refuses what turns on them
  "judgement": [one short line per reading beyond copying a stated fact]
Every literal not listed as true is FALSE (closed facts), except those in "unknown".
PROBES: {id: "one line: why the case is out of scope"} for every case whose scope is "out" (nothing is encoded for them).
"""

ALL3 = ["toilet", "washing", "cooking"]
SCF = ["separate_set", "part_of_building", "above_below"]


def house(cid, people, *, all_facts=(), person=None, rel=(), shares=ALL3, place=(), unknown=(), judgement=(),
          only_use=True):
    """A whole building let as one dwelling (C3), all named people living in it."""
    return {"id": cid, "people": list(people), "places": ["premises"],
            "place": {"premises": ["within"] + (["only_use"] if only_use else []) + list(place)},
            "amen": {"premises": {"has": ALL3, "excl": ALL3}},
            "lives": {p: "premises" for p in people},
            "all": list(all_facts), "person": person or {}, "rel": list(rel),
            "shares": {p: list(shares) for p in people}, "unknown": list(unknown), "judgement": list(judgement)}


def units(cid, people, unit_of, unit_place, *, premises=("only_use",), prem_has=ALL3, prem_excl=(), unit_amen=None,
          all_facts=(), person=None, rel=(), shares=None, extra_places=None, judgement=()):
    """A building (or flat) whose living accommodation is the listed units; unit_of: person -> place."""
    places = ["premises"] + list(unit_place) + list(extra_places or {})
    place = {"premises": list(premises)}
    place.update({u: list(v) for u, v in unit_place.items()})
    place.update({u: list(v) for u, v in (extra_places or {}).items()})
    amen = {"premises": {"has": list(prem_has), "excl": list(prem_excl)}}
    for u in list(unit_place) + list(extra_places or {}):
        has, excl = (unit_amen or {}).get(u, (ALL3, ALL3))
        amen[u] = {"has": list(has), "excl": list(excl)}
    return {"id": cid, "people": list(people), "places": places, "place": place, "amen": amen,
            "lives": dict(unit_of), "all": list(all_facts), "person": person or {}, "rel": list(rel),
            "shares": shares or {}, "unknown": [], "judgement": list(judgement)}


AB5 = ["Anna", "Ben", "Clara", "David", "Eva"]
MR_RENT = ["main_res", "rent_payable"]
OFFICE5 = {f"unit{i}": ["within", "created_since"] for i in range(1, 6)}
J_OFFICE = "bedsitting rooms = unit1..unit5 (one per occupant, in the order named), created_since; separate set / above or below not stated: false"
J_SHAREDFAC = "units: the shared toilet, bathroom and kitchen are available to (not exclusive to) each room's occupant"

CASES = [
    house("H001", ["Anna", "Ben", "Clara", "David"], all_facts=["ft_student", "rent_payable"],
          judgement=["'residence for undertaking a full-time course of higher education' = ft_student",
                     "main_res false: stated that none occupies as only or main residence"]),
    house("H002", ["Alice", "Beth", "Cora", "Dina", "Ella"], all_facts=["rent_payable"],
          place=["vol_org", "abuse_refuge_use"],
          judgement=["abuse_refuge_use: each occupant left home because of violence, abuse or threats from a (former) "
                     "spouse, civil partner or cohabitant and the house's entire accommodation use is their temporary accommodation",
                     "main_res false: stated that none occupies as only or main residence"]),
    house("H003", ["Amir", "Boris", "Carla", "Dora", "Elias"],
          person={"Amir": ["res_scheme_employed", "consid_employment", "employer_provided", "rent_payable"],
                  "Boris": ["work_permit", "consid_employment", "employer_provided", "rent_payable"],
                  "Carla": ["frontier_worker", "consid_employment", "employer_provided", "rent_payable"],
                  "Dora": ["seasonal_emp", "le_8_months", "consid_employment", "employer_provided", "rent_payable"],
                  "Elias": ["asylum", "s95", "nass"]},
          judgement=["'employer provides the accommodation partly in consideration of employment' = consid_employment and employer_provided",
                     "'accommodation charges' = other consideration: rent_payable (C6)",
                     "Dora: harvesting employment for an employer, seasonal and recurring, cannot exceed 8 months = seasonal_emp, le_8_months",
                     "main_res false: stated that none occupies as only or main residence"]),
    house("H004", ["Alice", "Ben", "Colin", "Dana", "Eva"], all_facts=MR_RENT,
          rel=[("Alice", "Ben", "civil_partners"), ("Colin", "Alice", "half_sibling_of"),
               ("Eva", "Alice", "cousin_of"), ("Eva", "Colin", "cousin_of"), ("Ben", "Dana", "step_parent_of")],
          judgement=["'Dana is Ben's stepchild' = step_parent_of(Ben, Dana); no relation of Dana to Alice stated"]),
    house("H005", ["Alan", "Beth", "Clara", "Daniel", "Edith"], all_facts=["main_res"], place=["decl"],
          person={"Alan": ["rent_payable"], "Clara": ["listed_work", "excl_domestic"]},
          rel=[("Alan", "Beth", "living_as"), ("Clara", "Daniel", "married"), ("Clara", "Edith", "parent_of"),
               ("Daniel", "Edith", "parent_of"), ("Clara", "Alan", "works_for"), ("Clara", "Beth", "works_for"),
               ("Clara", "Alan", "supplied_by")],
          judgement=["listed_work: every duty stated for Clara is work usually done by a reg. 3(3) worker (nanny, nurse, carer, "
                     "governess, servant, chauffeur, gardener, secretary, personal assistant)",
                     "'Alan supplies Clara's accommodation as part of her remuneration' = supplied_by(Clara, Alan) (consideration for the work)",
                     "rent_payable only Alan: his rent to the freeholder read as for his occupation; no rent stated for Beth"]),
    house("H006", ["Alan", "Beth", "Clara", "Daniel", "Edith"], all_facts=["main_res"],
          person={"Alan": ["freehold"], "Clara": ["listed_work", "excl_domestic", "rent_payable"]},
          rel=[("Alan", "Beth", "living_as"), ("Clara", "Daniel", "married"), ("Clara", "Edith", "parent_of"),
               ("Daniel", "Edith", "parent_of"), ("Clara", "Alan", "works_for"), ("Clara", "Beth", "works_for"),
               ("Clara", "Alan", "supplied_by")],
          judgement=["listed_work: every duty stated for Clara is work usually done by a reg. 3(3) worker",
                     "'Alan supplies Clara's accommodation as part of her remuneration' = supplied_by(Clara, Alan)",
                     "rent_payable only Clara: no rent stated for Alan (freeholder) or Beth; Daniel, Edith pay nothing"]),
    house("H007", ["Alice", "Ben"], all_facts=MR_RENT, person={"Alice": ["apc", "le3_users"]},
          rel=[("Ben", "Alice", "receives_care")],
          judgement=["C7: one service user (Ben) is not more than three: le3_users(Alice)"]),
    house("H008", ["Alice", "Ben", "Clara", "David", "Eva"], all_facts=MR_RENT, person={"Alice": ["apc"]},
          rel=[(p, "Alice", "receives_care") for p in ["Ben", "Clara", "David", "Eva"]],
          judgement=["C7: four service users is more than three: le3_users(Alice) false"]),
    house("H009", ["Alice", "Ben"], all_facts=MR_RENT, rel=[("Ben", "Alice", "fostered_with")], judgement=[]),
    house("H010", ["Anna", "Ben"], all_facts=["main_res"], person={"Anna": ["freehold"], "Ben": ["rent_payable"]},
          judgement=[]),
    house("H011", AB5, all_facts=["main_res"],
          person={"Anna": ["long_lease"], "David": ["rent_payable"], "Eva": ["rent_payable"]},
          rel=[("Anna", "Ben", "married"), ("Anna", "Clara", "parent_of"), ("Ben", "Clara", "parent_of")],
          judgement=["C7: lease term 22 years is more than 21: long_lease(Anna)",
                     "'Clara is their child' = parent_of(Anna, Clara), parent_of(Ben, Clara)"]),
    house("H012", ["Anna", "Ben", "Clara", "David"], all_facts=["main_res"],
          person={"Anna": ["freehold"], "Ben": ["rent_payable"], "Clara": ["rent_payable"], "David": ["rent_payable"]},
          judgement=[]),
    units("H013", AB5, {"Anna": "unit1", "Ben": "unit2", "Clara": "unit3", "David": "unit4", "Eva": "unit5"},
          {"unit1": ["within", "separate_set", "part_of_building", "created_since"],
           "unit2": ["within", "separate_set", "part_of_building", "created_since"],
           "unit3": ["within", "separate_set", "part_of_building", "created_since"],
           "unit4": ["within", "separate_set", "part_of_building", "above_below", "created_since"],
           "unit5": ["within", "separate_set", "part_of_building", "above_below", "created_since"]},
          all_facts=["main_res"], person={p: ["rent_payable"] for p in ["Ben", "Clara", "David", "Eva"]},
          judgement=["unit1-3 = the wings of Anna, Ben, Clara; unit4 = Flat 1 (David), unit5 = Flat 2 (Eva)",
                     "a wing / flat of the building forms part of it: part_of_building",
                     "Flat 2 lies below Flat 1: above_below for both; wings: no part above or below: false",
                     "C7: lease of exactly 21 years is not more than 21: long_lease(Anna) false",
                     "premises: amenities available to occupants (in their units), not exclusive at building level"]),
    units("H014", AB5, {p: "premises" for p in AB5},
          {}, premises=["within", "separate_set", "part_of_building", "above_below", "is_part", "only_use",
                        "purpose_built", "in_block"], prem_excl=ALL3,
          extra_places={"flat2": ["in_block", "separate_set", "part_of_building", "above_below"]},
          all_facts=MR_RENT, shares={p: ALL3 for p in AB5},
          judgement=["premises = Flat 1 as one unit (C3); flat2 = Flat 2, the other flat of the block",
                     "Fred (Flat 2 only) does not occupy the premises: not named (C1)",
                     "block built as two separate sets: Flat 1 is purpose-built",
                     "Flat 1 wholly above Flat 2: above_below for both; each flat part_of_building"]),
    units("H015", AB5, {p: "premises" for p in AB5},
          {}, premises=["within", "separate_set", "part_of_building", "above_below", "is_part", "only_use",
                        "purpose_built", "in_block"], prem_excl=ALL3,
          extra_places={"flat2": ["in_block", "separate_set", "part_of_building", "above_below"],
                        "flat3": ["in_block", "separate_set", "part_of_building", "above_below"]},
          all_facts=MR_RENT, shares={p: ALL3 for p in AB5},
          judgement=["premises = Flat 1 as one unit (C3); flat2, flat3 = Flats 2 and 3 of the block",
                     "Fred (Flat 2) and Grace (Flat 3) do not occupy the premises: not named (C1)",
                     "block built as three separate sets: Flat 1 is purpose-built",
                     "flats stacked wholly above one another: above_below for each; each part_of_building"]),
    units("H016", AB5, {p: f"unit{i}" for i, p in enumerate(AB5, 1)}, OFFICE5,
          premises=["only_use", "mgr_lha", "mgr_nprp", "mgr_rsl", "mgr_pcc", "mgr_mopac", "mgr_fra", "mgr_hsb"],
          unit_amen={u: (ALL3, []) for u in OFFICE5}, all_facts=MR_RENT, shares={p: ALL3 for p in AB5},
          judgement=[J_OFFICE, J_SHAREDFAC,
                     "each of the seven named bodies manages and controls the building: all seven mgr_ predicates true"]),
    house("H017", AB5, all_facts=MR_RENT, place=["social_housing", "mgr_prp"], judgement=[]),
    house("H018", AB5, all_facts=MR_RENT, place=["mgr_coop_body", "coop_rule_a", "coop_rule_b", "coop_rule_c", "coop_rule_d"],
          judgement=["the society's stated binding rules = coop_rule_a..d; who is a member (Eva not) has no predicate: not encoded"]),
    house("H019", AB5, all_facts=MR_RENT, person={"Anna": ["occ_ast"]},
          place=["mgr_coop_body", "coop_rule_a", "coop_rule_b", "coop_rule_c", "coop_rule_d"],
          judgement=["the society's stated binding rules = coop_rule_a..d; membership has no predicate: not encoded",
                     "C7: assured tenancy for one year is not more than 21 years: long_lease(Anna) false"]),
    house("H020", AB5, all_facts=MR_RENT, place=["religious"], judgement=[]),
    units("H021", AB5, {"Anna": "unit1", "Ben": "unit1", "Clara": "unit2", "David": "unit2", "Eva": "unit2"},
          {"unit1": ["within", "separate_set", "part_of_building", "above_below", "created_since"],
           "unit2": ["within", "separate_set", "part_of_building", "above_below", "created_since"]},
          premises=["only_use", "s257", "religious"], all_facts=["main_res"],
          person={"Anna": ["long_lease", "rent_payable"], "Clara": ["long_lease", "rent_payable"]},
          rel=[("Anna", "Ben", "married"), ("Clara", "David", "married"), ("Clara", "Eva", "parent_of"),
               ("David", "Eva", "parent_of")],
          judgement=["unit1 = Flat 1 (Anna, Ben), unit2 = Flat 2 (Clara, David, Eva)",
                     "C7: leases of 99 years are more than 21: long_lease(Anna), long_lease(Clara)",
                     "ground rent under their leases = rent payable for Anna's and Clara's occupation (C6); none stated for the others",
                     "'Eva is their child' = parent_of(Clara, Eva), parent_of(David, Eva)",
                     "shares false for all: the premises has one set of facilities per flat and none is shared between "
                     "flats; `shares` (one such facility in the premises) cannot state within-flat sharing",
                     "premises: amenities available to occupants (in their flats), not exclusive at building level"]),
    units("H022", ["Anna", "Ben", "Clara"], {p: "premises" for p in ["Anna", "Ben", "Clara"]},
          {}, premises=["within", "separate_set", "part_of_building", "above_below", "is_part", "only_use",
                        "created_since", "in_block"], prem_excl=ALL3,
          extra_places={"flat2": ["in_block", "separate_set", "part_of_building", "above_below", "created_since"]},
          all_facts=["main_res"], person={"Anna": ["long_lease"], "Ben": ["rent_payable"], "Clara": ["rent_payable"]},
          shares={p: ALL3 for p in ["Anna", "Ben", "Clara"]},
          judgement=["premises = Flat 1 as one unit (C3); flat2 = Flat 2, the other flat of the block",
                     "David (Flat 2 only) does not occupy the premises: not named (C1)",
                     "created by conversion of a warehouse: created_since, not purpose_built",
                     "s257(premises) false: Flat 1 itself is stated not to be a s.257 block; the whole block's s.257 status "
                     "has no place of its own here",
                     "C7: lease of 99 years is more than 21: long_lease(Anna)"]),
    units("H023", AB5, {p: f"unit{i}" for i, p in enumerate(AB5, 1)},
          {f"unit{i}": ["within", "separate_set", "part_of_building"] for i in range(1, 6)}, all_facts=MR_RENT,
          judgement=["sets = unit1..unit5 in the order named; a set of the building forms part of it: part_of_building",
                     "no part of the building above or below any set: above_below false",
                     "premises: amenities available to occupants (in their units), not exclusive at building level"]),
    units("H024", AB5, {p: f"unit{i}" for i, p in enumerate(AB5, 1)}, OFFICE5, premises=["only_use", "decl"],
          prem_has=["toilet", "washing"],
          unit_amen={u: (["toilet", "washing"], ["toilet", "washing"]) for u in OFFICE5}, all_facts=MR_RENT,
          judgement=[J_OFFICE, "'own toilet and shower' = toilet and washing; cooking facilities nowhere in the building"]),
    units("H025", AB5, {p: f"unit{i}" for i, p in enumerate(AB5, 1)}, OFFICE5, premises=[],
          unit_amen={u: (ALL3, []) for u in OFFICE5}, all_facts=MR_RENT, shares={p: ALL3 for p in AB5},
          judgement=[J_OFFICE, J_SHAREDFAC, "use of the same rooms and kitchen as a public cafe: only_use false"]),
    units("H026", AB5, {p: f"unit{i}" for i, p in enumerate(AB5, 1)}, OFFICE5,
          unit_amen={u: (ALL3, []) for u in OFFICE5}, shares={p: ALL3 for p in AB5},
          judgement=[J_OFFICE, J_SHAREDFAC,
                     "main_res false: stated that none occupies as only or main residence (leisure visit)",
                     "gratuitous licences, no consideration: rent_payable false"]),
]

PROBES = {
    "H027": "turns on Sch. 14 para 3A specifications not supplied and not in the encoded text",
    "H028": "turns on Sch. 14 para 3 / s.254(6) regulations not supplied",
    "H029": "asks whether a licence is required (Part 2 licensing), outside the encoded provisions",
    "H030": "asks whether an HMO declaration should be made; s.255 criteria not supplied",
    "H031": "s.257 status of the whole block not stated",
    "H032": "building in Wales; the encoded test set is England's",
    "H033": "asks about HMO status for Part 1, outside the encoded question",
    "H034": "asks the encoder to decide unstated immigration and accommodation statuses",
}
