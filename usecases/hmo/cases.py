"""HMO England: the ENCODER's file. Facts of the 26 in-scope cases, read from questions-enc.jsonl ONLY (id, scope, premises,
facts; sha256 a9ed25c2...0fae555), never questions.jsonl or the sealed answers. SAME-FAMILY (Opus 5.5 encoder = translator).

ENCODING CONVENTIONS (every case; counted as encoder judgement in RESULT.md):
 C1 Domain closure (prompt F4): the case names everyone who occupies the premises; people are person1.. in the order named;
    places are `premises` and, where the premises consist of several units or sit in a block, unit1.. / flat1...
 C2 Relations between people are those the facts state; relations not stated do not exist (the facts describe the
    occupants' relations), EXCEPT a relation the facts imply only through the law's own deemings (s.258(4)(c), (d)): that is
    VE's to derive; where the facts state a kinship chain VE's vocabulary cannot compose (a step-grandchild), the base relation
    is left UNKNOWN (no literal), so VE refuses what turns on it. Plain kinship consequences of stated facts (the son of
    Paul's sister is Paul's nephew) are encoded and listed per case.
 C3 A whole building let as one dwelling is one unit: the premises itself (within(premises)); a building of flats or bedsits
    has one place per unit. "Has its own front door / a separate set of rooms" = separate_set.
 C4 An HMO declaration (s.255) or a s.257 status the facts do not mention is not in force / does not apply.
 C5 "They share the kitchen and bathroom(s)" = each named sharer shares cooking, toilet and personal washing facilities.
 C6 Rent: rent_payable(p) when rent or other consideration (a charge, a contribution, a payment by a funder) is payable for
    p's occupation, whoever pays it; a domestic worker's work is not counted (reg. 3(2)(c)).
 C7 A number stated in the facts compared with a number in the text (a 125-year lease > 21 years; three service users <=
    three) is compared by the encoder: listed per case.
 C8 A status the facts do not state and nothing settles (only or main residence where unstated) is left UNKNOWN.
Per-case judgement beyond C1-C8 is in "judgement".
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


CASES = [
    house("H001", ["amy", "ben", "chloe", "dev", "ella"], all_facts=["ft_student", "rent_payable"]),
    house("H002", ["ben", "anna", "dan", "carol"], all_facts=["main_res", "rent_payable"],
          rel=[("ben", "anna", "married"), ("dan", "carol", "married"), ("ben", "dan", "sibling_of")],
          judgement=["'Ben's brother Dan': brothers of the whole blood (either blood gives a relative)"]),
    house("H003", ["paul", "quinn", "rita", "simon", "theo"], all_facts=["main_res", "rent_payable"],
          rel=[("paul", "quinn", "living_as"), ("rita", "quinn", "parent_of"), ("paul", "simon", "sibling_of"),
               ("paul", "theo", "uncle_aunt_of"), ("simon", "theo", "uncle_aunt_of")],
          judgement=["Theo, 'the son of Paul's and Simon's sister': Paul and Simon are his uncles (plain kinship, C2)",
                     "Paul and Simon brothers of the whole blood"]),
    house("H004", ["lena", "max", "olive", "nora"], all_facts=["main_res"], person={"lena": ["rent_payable"]},
          rel=[("lena", "max", "step_parent_of"), ("lena", "olive", "parent_of"), ("max", "olive", "half_sibling_of"),
               ("max", "nora", "parent_of"), ("olive", "nora", "half_uncle_aunt_of")],
          unknown=[("binary", "grandparent_of", "lena", "nora")],
          judgement=["Olive, half-sister of Nora's father: Nora's aunt of the half-blood (plain kinship, C2)",
                     "Lena-Nora: Nora is the daughter of Lena's stepson; whether that makes Lena a grandparent goes through "
                     "s.258(4)(d) applied to a chain: left UNKNOWN (C2)"]),
    house("H005", ["xena", "yusuf", "zara", "adam", "beth"], all_facts=["main_res"],
          person={"xena": ["rent_payable"], "yusuf": ["rent_payable"], "beth": ["listed_work"]},
          rel=[("xena", "yusuf", "married"), ("xena", "zara", "parent_of"), ("yusuf", "zara", "parent_of"),
               ("adam", "xena", "fostered_with"), ("adam", "yusuf", "fostered_with"),
               ("beth", "xena", "works_for"), ("beth", "yusuf", "works_for"),
               ("beth", "xena", "supplied_by"), ("beth", "yusuf", "supplied_by")],
          judgement=["Zara 'their daughter': daughter of both Xena and Yusuf",
                     "Beth works as a nanny for Xena and Yusuf (both employ her) and both supply her room"]),
    house("H006", ["craig", "donna", "eli", "finn", "gina"], all_facts=["main_res"],
          person={"craig": ["rent_payable"], "donna": ["rent_payable"], "gina": ["listed_work", "rent_payable"]},
          rel=[("craig", "donna", "married"), ("craig", "eli", "parent_of"), ("craig", "finn", "parent_of"),
               ("donna", "eli", "parent_of"), ("donna", "finn", "parent_of"), ("eli", "finn", "sibling_of"),
               ("gina", "craig", "works_for"), ("gina", "donna", "works_for"), ("gina", "donna", "supplied_by")],
          judgement=["'their two sons': sons of both Craig and Donna, brothers of the whole blood",
                     "Gina looks after the boys: work for their parents Craig and Donna",
                     "Gina pays Donna 40 pounds a week towards the room: rent payable for her occupation (C6)"]),
    house("H007", ["sam", "tina", "pablo", "rosa", "hugo"], all_facts=["main_res"],
          person={"sam": ["rent_payable"], "tina": ["rent_payable"], "pablo": ["listed_work"]},
          rel=[("sam", "tina", "married"), ("pablo", "rosa", "married"), ("pablo", "hugo", "parent_of"),
               ("rosa", "hugo", "parent_of"), ("pablo", "sam", "works_for"), ("pablo", "tina", "works_for"),
               ("pablo", "sam", "supplied_by")],
          judgement=["one unit: the whole house (Pablo's two rooms have no facilities of their own) (C3)",
                     "Pablo drives Sam and Tina: work for both; his rooms are supplied by Sam",
                     "'their son Hugo': son of Pablo and Rosa"]),
    house("H008", ["victor", "wendy", "yasmin", "zac"], all_facts=["main_res", "rent_payable"],
          person={"victor": ["apc", "le3_users"]},
          rel=[("wendy", "victor", "receives_care"), ("yasmin", "victor", "receives_care"),
               ("zac", "victor", "receives_care")],
          judgement=["three service users <= three (C7)",
                     "Victor pays the landlord; each service user pays Victor a sum for accommodation and care (C6)"]),
    house("H009", ["alan", "brian", "colin", "derek", "ed"], all_facts=["rent_payable"],
          judgement=["main residence elsewhere: main_res false; no student, refuge, reg. 5 or asylum facts"]),
    house("H010", ["petra", "radu", "sanna", "tom", "ursula"],
          all_facts=["rent_payable", "consid_employment", "employer_provided"],
          person={"petra": ["res_scheme_employed"], "radu": ["res_scheme_employed"], "sanna": ["res_scheme_employed"],
                  "tom": ["seasonal_emp", "le_8_months"], "ursula": ["seasonal_emp", "le_8_months"]},
          judgement=["the weekly charge deducted from wages: rent payable (C6)"]),
    house("H011", ["ahmed", "bella", "chidi", "dawit", "emil"], all_facts=["asylum", "s95", "nass", "rent_payable"],
          rel=[("ahmed", "bella", "parent_of")],
          unknown=[("unary", "main_res", p) for p in ["ahmed", "bella", "chidi", "dawit", "emil"]],
          judgement=["NASS pays the manager for each occupant's accommodation: consideration provided in respect of their "
                     "occupation (C6)", "only or main residence not stated (C8)"]),
    house("H012", ["carla", "kyle", "lily", "dina", "erin"], place=["vol_org", "abuse_refuge_use"],
          person={"carla": ["rent_payable"], "dina": ["rent_payable"], "erin": ["rent_payable"]},
          rel=[("carla", "kyle", "parent_of"), ("carla", "lily", "parent_of"), ("kyle", "lily", "sibling_of")],
          unknown=[("unary", "main_res", p) for p in ["carla", "kyle", "lily", "dina", "erin"]],
          judgement=["'her two children': brother and sister (whole blood assumed; either blood gives a relative)",
                     "only or main residence not stated (C8)",
                     "'uses the house wholly for the temporary accommodation of women ... who have left their homes as a "
                     "result of physical violence or threats ... from men who are or were their husbands or with whom they "
                     "were living': abuse_refuge_use"]),
    house("H013", ["vera", "wanda"], all_facts=["main_res", "rent_payable"]),
    house("H014", ["fay", "gus"], all_facts=["main_res"], person={"fay": ["freehold"], "gus": ["rent_payable"]}),
    house("H015", ["hana", "ivan", "jack", "kim", "liam"], all_facts=["main_res"],
          person={"hana": ["freehold"], "ivan": ["freehold"], "jack": ["rent_payable"], "kim": ["rent_payable"],
                  "liam": ["rent_payable"]},
          rel=[("hana", "ivan", "married")]),
    {"id": "H016", "people": ["kemal", "leah", "leo", "mia", "nico", "omar"],
     "places": ["premises", "unit1", "unit2", "unit3", "unit4", "unit5"],
     "place": {"premises": ["only_use"],
               "unit1": ["within", "created_since"] + SCF, "unit2": ["within", "created_since"] + SCF,
               "unit3": ["within", "created_since", "part_of_building", "above_below"],
               "unit4": ["within", "created_since", "part_of_building", "above_below"],
               "unit5": ["within", "created_since", "part_of_building", "above_below"]},
     "amen": {"premises": {"has": ALL3, "excl": []}, "unit1": {"has": ALL3, "excl": ALL3},
              "unit2": {"has": ALL3, "excl": ALL3}, "unit3": {"has": ALL3, "excl": ["cooking"]},
              "unit4": {"has": ALL3, "excl": ["cooking"]}, "unit5": {"has": ALL3, "excl": ["cooking"]}},
     "lives": {"kemal": "unit1", "leah": "unit1", "leo": "unit2", "mia": "unit3", "nico": "unit4", "omar": "unit5"},
     "all": ["main_res", "rent_payable"], "person": {}, "rel": [("kemal", "leah", "married")],
     "shares": {"mia": ["toilet", "washing"], "nico": ["toilet", "washing"], "omar": ["toilet", "washing"]},
     "unknown": [], "judgement": ["unit1, unit2 = Flats 1, 2; unit3-5 = the bedsitting rooms (created since built)",
                                  "a bedsitting room's sink is not personal washing facilities (its shower is shared)",
                                  "a bedsitting room is not encoded as a separate set of premises (it shares the bathroom)",
                                  "s.257 not mentioned: does not apply (C4)"]},
    {"id": "H017", "people": ["aaron", "basil", "cyril", "dominic", "edmund", "felix", "gareth", "hugh"],
     "places": ["premises", "unit1", "unit2", "unit3", "unit4"],
     "place": {"premises": ["only_use", "s257", "religious"],
               **{u: ["within", "created_since"] + SCF for u in ["unit1", "unit2", "unit3", "unit4"]}},
     "amen": {"premises": {"has": ALL3, "excl": []}, **{u: {"has": ALL3, "excl": ALL3} for u in ["unit1", "unit2", "unit3", "unit4"]}},
     "lives": {"aaron": "unit1", "basil": "unit1", "cyril": "unit2", "dominic": "unit2", "edmund": "unit3", "felix": "unit3",
               "gareth": "unit4", "hugh": "unit4"},
     "all": ["main_res", "rent_payable"], "person": {}, "rel": [], "shares": {}, "unknown": [],
     "judgement": ["the four flats were created by the conversion (created_since)",
                   "the monthly contribution for board and lodging is consideration (C6)",
                   "'occupied principally for the purposes of a religious community ...': stated judgment, encoded as given"]},
    {"id": "H018", "people": ["pia", "rhys", "saul", "tess", "umar"],
     "places": ["premises", "unit1", "unit2", "unit3", "unit4", "unit5"],
     "place": {"premises": ["only_use"],
               **{u: ["within", "created_since", "separate_set", "part_of_building"]
                  for u in ["unit1", "unit2", "unit3", "unit4", "unit5"]}},
     "amen": {"premises": {"has": ALL3, "excl": []}, **{u: {"has": ALL3, "excl": ALL3} for u in ["unit1", "unit2", "unit3", "unit4", "unit5"]}},
     "lives": {"pia": "unit1", "rhys": "unit2", "saul": "unit3", "tess": "unit4", "umar": "unit5"},
     "all": ["main_res", "rent_payable"], "person": {}, "rel": [], "shares": {}, "unknown": [],
     "judgement": ["each studio opening off the common hallway: a separate set of premises", "s.257 not mentioned (C4)"]},
    {"id": "H019", "people": ["ava", "bram", "cleo", "dara", "evan"], "places": ["premises", "flat1"],
     "place": {"premises": ["within", "only_use", "is_part", "purpose_built", "in_block"] + SCF, "flat1": ["in_block"]},
     "amen": {"premises": {"has": ALL3, "excl": ALL3}},
     "lives": {p: "premises" for p in ["ava", "bram", "cleo", "dara", "evan"]},
     "all": ["main_res", "rent_payable"], "person": {}, "rel": [], "shares": {p: ALL3 for p in ["ava", "bram", "cleo", "dara", "evan"]},
     "unknown": [(k, "flat1", a) for k in ("excl_amenity",) for a in ALL3] + [("unary", x, "flat1") for x in SCF],
     "judgement": ["'constructed as a shop on the ground floor with two flats above it': Flat 2 is a purpose-built flat",
                   "Flat 1's layout and facilities are not stated: left UNKNOWN (C8)"]},
    {"id": "H020", "people": ["faye", "gil", "hugo", "iris", "joel"],
     "places": ["premises", "flat1", "flat2", "flat3", "flat5", "flat6"],
     "place": {"premises": ["within", "only_use", "is_part", "purpose_built", "in_block"] + SCF,
               **{f: ["in_block"] + SCF for f in ["flat1", "flat2", "flat3", "flat5", "flat6"]}},
     "amen": {"premises": {"has": ALL3, "excl": ALL3}, **{f: {"has": ALL3, "excl": ALL3} for f in ["flat1", "flat2", "flat3", "flat5", "flat6"]}},
     "lives": {p: "premises" for p in ["faye", "gil", "hugo", "iris", "joel"]},
     "all": ["main_res", "rent_payable"], "person": {}, "rel": [], "shares": {p: ALL3 for p in ["faye", "gil", "hugo", "iris", "joel"]},
     "unknown": [], "judgement": ["'constructed as six flats ... not altered': each flat purpose-built; the other five flats "
                                  "each lie above or below another part (one on each floor)"]},
    house("H021", ["kate", "lara", "mona", "nell", "ola", "pam"], all_facts=["main_res", "rent_payable"], place=["mgr_hsb"]),
    house("H022", ["quentin", "rosa", "stan", "tara", "uri"], all_facts=["main_res", "rent_payable"],
          place=["social_housing", "mgr_prp"]),
    house("H023", ["vic", "will", "xia", "yves", "zoe", "amir"], all_facts=["main_res"],
          person={p: ["rent_payable"] for p in ["vic", "will", "xia", "yves", "zoe"]},
          place=["mgr_coop_body", "coop_rule_a", "coop_rule_b", "coop_rule_c", "coop_rule_d"],
          rel=[("zoe", "amir", "living_as")],
          judgement=["each member pays a weekly charge; Amir (not a member) pays nothing stated (C6)"]),
    house("H024", ["agnes", "bridget", "cecily", "dorothy", "edith", "frances"], all_facts=["main_res", "rent_payable"],
          place=["religious"],
          judgement=["'occupied principally for the purposes of a religious community ...': stated judgment, encoded as given",
                     "the monthly contribution for board and lodging is consideration (C6)"]),
    {"id": "H025", "people": ["ivy", "jon", "kara"], "places": ["premises"],
     "place": {"premises": ["within", "only_use", "is_part"] + SCF},
     "amen": {"premises": {"has": ALL3, "excl": ALL3}},
     "lives": {p: "premises" for p in ["ivy", "jon", "kara"]},
     "all": ["main_res"], "person": {"ivy": ["long_lease"], "jon": ["rent_payable"], "kara": ["rent_payable"]},
     "rel": [], "shares": {p: ALL3 for p in ["ivy", "jon", "kara"]}, "unknown": [],
     "judgement": ["a lease granted for 125 years: more than 21 years (C7)",
                   "s.257 applies to Riverside House, the block; the premises asked about is Flat 3, not the block: s257 "
                   "false for the premises"]},
    house("H026", ["bea", "cal", "dot", "ezra", "flo"], all_facts=["main_res", "rent_payable"], place=["decl"],
          only_use=False,
          judgement=["the living room shared with a hairdressing business: occupation is not the only use (stated)"]),
]

PROBES = {
    "H027": "a student block managed by a university: Sch. 14 para 3A (out of scope; F2 contradicted by the facts' doubt)",
    "H028": "a house in Wales: SI 2018/221 and SI 2006/373 are England instruments; Sch. 14 para 4 (out of scope)",
    "H029": "asks whether a licence is required or in force (s.61: not in the pinned text)",
    "H030": "asks whether an HMO declaration ought to be made (s.255: not in the pinned text)",
    "H031": "whether s.257 applies is not stated and turns on s.257 (not pinned)",
    "H032": "whether any tenancy is assured, secure or protected is not stated: Sch. 14 para 2B(1)(b) turns on other Acts",
    "H033": "asked for the purposes of Part 1 (s.254(5) and Sch. 14 do not apply; Part 1 not pinned)",
    "H034": "occupation regulated under another enactment: Sch. 14 para 3 with SI 2006/373 reg. 6(1) and its Schedule (out)",
}
