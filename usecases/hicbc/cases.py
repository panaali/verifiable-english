"""HICBC: the encoder's transcription of questions-enc.jsonl (manage-agents reviews/spare/statute-corpus/hicbc, sha256
a30a1bec...cff07e; id, scope, tax_year, subject, people, facts only). Encoder: dri-statute-corpus-hicbc-1123 (Opus 5.5), who
also wrote rules.py (committed before this file was started) and never opened the sealed answers. SAME-FAMILY.

What is transcribed (and nothing else): each person's stated adjusted net income; each stated child benefit entitlement
(claimant, child, weekly amount, the weeks as stated, its stated basis: "a" = s.143(1)(a) because the child lives with the
claimant, "b" = s.143(1)(b) contributing, "145a" = by virtue of s.145A; any s.13A election and its weeks); each stated
"has the child living with them for the purposes of s.143(1)(a)" period; each stated relationship fact with its dates
(married_or_cp, sep_court, sep_permanent [stated judgement], as_if_married [stated judgement]). Facts stated as never
holding are simply absent (closed facts). Every child named is stated to be a child or a qualifying young person within
s.142 SSCBA 1992 (is_child true). Week and day arithmetic is the bridge's (bridge/bridges.py), never done here.
ENCODER JUDGEMENT (beyond the stated facts and the bridge) is listed per case in "judgement".
"""

S = "2025-04-07", "2026-03-30"     # the stated week range of 2025-26 (first and last Monday)
S24 = "2024-04-08", "2025-03-31"   # 2024-25
S26 = "2026-04-06", "2027-04-05"   # 2026-27


def cb(claimant, child, weekly, frm, to, basis="a", election=None):
    return {"claimant": claimant, "child": child, "weekly": weekly, "from": frm, "to": to, "basis": basis,
            "election": election}


def rel(a, b, kind, frm, to=None):
    return {"pair": [a, b], "kind": kind, "from": frm, "to": to}


def lw(person, child, frm, to):
    return {"person": person, "child": child, "from": frm, "to": to}


SEP_NOT_PERMANENT = ("separated, no court order, 'the separation is not likely to be permanent': no 681G(2)(a) or (b) fact, "
                     "so the marriage fact alone stands (a reading of the stated facts, not of the Act)")

CASES = [
    {"id": "H001", "tax_year": "2025-26", "subject": "Alice", "people": ["Alice", "Ella"], "ani": {"Alice": "64350"},
     "cb": [cb("Alice", "Ella", "26.05", *S)], "rel": [], "judgement": []},
    {"id": "H002", "tax_year": "2025-26", "subject": "Ben", "people": ["Ben", "Leo"], "ani": {"Ben": "60000"},
     "cb": [cb("Ben", "Leo", "26.05", *S)], "rel": [], "judgement": []},
    {"id": "H003", "tax_year": "2025-26", "subject": "Cara", "people": ["Cara", "Noah"], "ani": {"Cara": "60001"},
     "cb": [cb("Cara", "Noah", "26.05", *S)], "rel": [], "judgement": []},
    {"id": "H004", "tax_year": "2024-25", "subject": "Dan", "people": ["Dan", "Erin", "Finn", "Gus"],
     "ani": {"Dan": "79999", "Erin": "30000"},
     "cb": [cb("Erin", "Finn", "25.60", *S24), cb("Erin", "Gus", "16.95", *S24)],
     "rel": [rel("Dan", "Erin", "married_or_cp", "2018-05-12")], "judgement": []},
    {"id": "H005", "tax_year": "2026-27", "subject": "Fay", "people": ["Fay", "Hana"], "ani": {"Fay": "80001"},
     "cb": [cb("Fay", "Hana", "26.75", *S26)], "rel": [], "judgement": []},
    {"id": "H006", "tax_year": "2025-26", "subject": "Hugo", "people": ["Gail", "Hugo", "Iris"],
     "ani": {"Gail": "70000", "Hugo": "70000"},
     "cb": [cb("Gail", "Iris", "26.05", *S)], "rel": [rel("Gail", "Hugo", "married_or_cp", "2010-06-04")], "judgement": []},
    {"id": "H007", "tax_year": "2025-26", "subject": "Jane", "people": ["Ian", "Jane", "Kai"],
     "ani": {"Ian": "90000", "Jane": "65000"},
     "cb": [cb("Jane", "Kai", "26.05", *S)], "rel": [rel("Ian", "Jane", "married_or_cp", "2013-09-21")], "judgement": []},
    {"id": "H008", "tax_year": "2025-26", "subject": "Leon", "people": ["Kate", "Leon", "Mila"],
     "ani": {"Kate": "45000", "Leon": "72500"},
     "cb": [cb("Kate", "Mila", "26.05", *S)], "rel": [rel("Kate", "Leon", "married_or_cp", "2025-09-10")], "judgement": []},
    {"id": "H009", "tax_year": "2024-25", "subject": "Mark", "people": ["Mark", "Nina", "Oscar"],
     "ani": {"Mark": "68000", "Nina": "20000"},
     "cb": [cb("Nina", "Oscar", "25.60", *S24)],
     "rel": [rel("Mark", "Nina", "married_or_cp", "2012-08-18"), rel("Mark", "Nina", "sep_court", "2024-11-14")],
     "judgement": ["the court order 'made on 14 November 2024' separates them from that day (stated: 'separated under that "
                   "court order since 14 November 2024')"]},
    {"id": "H010", "tax_year": "2025-26", "subject": "Paul", "people": ["Olga", "Paul", "Ruby"],
     "ani": {"Olga": "35000", "Paul": "61500"},
     "cb": [cb("Olga", "Ruby", "26.05", *S)],
     "rel": [rel("Olga", "Paul", "married_or_cp", "2014-05-03"), rel("Olga", "Paul", "sep_permanent", "2025-03-12")],
     "judgement": []},
    {"id": "H011", "tax_year": "2026-27", "subject": "Quinn", "people": ["Quinn", "Rosa", "Sid", "Tom"],
     "ani": {"Quinn": "66666", "Rosa": "41000"},
     "cb": [cb("Rosa", "Sid", "26.75", *S26), cb("Rosa", "Tom", "17.75", *S26)],
     "rel": [rel("Quinn", "Rosa", "as_if_married", "2019-06-01")], "judgement": []},
    {"id": "H012", "tax_year": "2025-26", "subject": "Sven", "people": ["Alfie", "Bella", "Sven", "Tara"],
     "ani": {"Sven": "100000", "Tara": "25000"},
     "cb": [cb("Tara", "Alfie", "26.05", *S), cb("Tara", "Bella", "17.25", *S)],
     "rel": [rel("Sven", "Tara", "as_if_married", "2026-01-04")], "judgement": []},
    {"id": "H013", "tax_year": "2024-25", "subject": "Uma", "people": ["Cody", "Uma"], "ani": {"Uma": "70050"},
     "cb": [cb("Uma", "Cody", "25.60", "2025-03-03", None)], "rel": [], "judgement": []},
    {"id": "H014", "tax_year": "2026-27", "subject": "Will", "people": ["Ada", "Vera", "Will"],
     "ani": {"Vera": "59000", "Will": "61234"},
     "cb": [cb("Vera", "Ada", "26.75", "2027-03-29", None)], "rel": [rel("Vera", "Will", "married_or_cp", "2020-07-25")],
     "judgement": []},
    {"id": "H015", "tax_year": "2025-26", "subject": "Amy", "people": ["Amy", "Bob", "Zoe"],
     "ani": {"Amy": "75000", "Bob": "48000"},
     "cb": [cb("Bob", "Zoe", "26.05", "2022-01-03", S[1], basis="b")], "lives": [lw("Amy", "Zoe", *S)], "rel": [],
     "judgement": ["the two stated periods of Bob's s.143(1)(b) entitlement ('since the week beginning Monday 3 January 2022' "
                   "and the year's weeks) joined as one period ending with the last stated week"]},
    {"id": "H016", "tax_year": "2025-26", "subject": "Cleo", "people": ["Cleo", "Drew", "Finn"],
     "ani": {"Cleo": "90000", "Drew": "62000"},
     "cb": [cb("Drew", "Finn", "26.05", "2021-09-06", S[1], basis="b")], "lives": [lw("Cleo", "Finn", *S)], "rel": [],
     "judgement": ["Drew's s.143(1)(b) periods joined as in H015"]},
    {"id": "H017", "tax_year": "2024-25", "subject": "Fern", "people": ["Eli", "Fern", "Gwen", "Hal"],
     "ani": {"Fern": "61000", "Gwen": "64000", "Hal": "30000"},
     "cb": [cb("Hal", "Eli", "16.95", "2019-09-02", S24[1], basis="b")],
     "lives": [lw("Fern", "Eli", *S24), lw("Gwen", "Eli", *S24)], "rel": [],
     "judgement": ["Hal's s.143(1)(b) periods joined as in H015"]},
    {"id": "H018", "tax_year": "2024-25", "subject": "Ken", "people": ["Ida", "Jack", "Ken"],
     "ani": {"Ida": "52000", "Ken": "85000"},
     "cb": [cb("Ida", "Jack", "25.60", "2024-04-08", "2024-06-03"), cb("Ida", "Jack", "25.60", "2024-06-10", "2024-08-26", basis="b"),
            cb("Ida", "Jack", "25.60", "2024-09-02", S24[1])],
     "lives": [lw("Ken", "Jack", "2024-06-10", "2024-08-26")], "rel": [], "judgement": []},
    {"id": "H019", "tax_year": "2025-26", "subject": "Omar", "people": ["Lena", "Maya", "Nell", "Omar"],
     "ani": {"Lena": "40000", "Nell": "50000", "Omar": "70500"},
     "cb": [cb("Lena", "Maya", "26.05", "2025-04-07", "2025-09-29"), cb("Lena", "Maya", "26.05", "2025-10-06", "2026-11-02", basis="b"),
            cb("Lena", "Maya", "26.05", "2026-11-09", None)],
     "lives": [lw("Nell", "Maya", "2025-10-06", "2026-11-02")], "rel": [rel("Nell", "Omar", "married_or_cp", "2015-05-09")],
     "judgement": []},
    {"id": "H020", "tax_year": "2025-26", "subject": "Pia", "people": ["Ned", "Opal", "Pia"], "ani": {"Pia": "70000"},
     "cb": [cb("Pia", "Ned", "26.05", *S, election=["2025-10-06", None]), cb("Pia", "Opal", "17.25", *S, election=["2025-10-06", None])],
     "rel": [], "judgement": []},
    {"id": "H021", "tax_year": "2024-25", "subject": "Sam", "people": ["Owen", "Rhys", "Sam"],
     "ani": {"Rhys": "58000", "Sam": "95000"},
     "cb": [cb("Rhys", "Owen", "25.60", *S24, election="all")], "rel": [rel("Rhys", "Sam", "married_or_cp", "2016-04-30")],
     "judgement": []},
    {"id": "H022", "tax_year": "2026-27", "subject": "Tia", "people": ["Ivy", "Tia"], "ani": {"Tia": "68000"},
     "cb": [cb("Tia", "Ivy", "26.75", "2026-04-06", "2026-10-05"), cb("Tia", "Ivy", "26.75", "2026-10-12", "2026-11-30", basis="145a")],
     "rel": [], "judgement": []},
    {"id": "H023", "tax_year": "2025-26", "subject": "Vic", "people": ["Kit", "Uri", "Vic", "Wes"],
     "ani": {"Uri": "20000", "Vic": "75000", "Wes": "82000"},
     "cb": [cb("Uri", "Kit", "17.25", *S)],
     "rel": [rel("Uri", "Vic", "married_or_cp", "2011-07-02"), rel("Uri", "Wes", "as_if_married", "2024-03-01")],
     "judgement": [SEP_NOT_PERMANENT]},
    {"id": "H024", "tax_year": "2024-25", "subject": "Yann", "people": ["Rory", "Xena", "Yann", "Zack"],
     "ani": {"Xena": "30000", "Yann": "70000", "Zack": "90000"},
     "cb": [cb("Xena", "Rory", "25.60", *S24)],
     "rel": [rel("Xena", "Yann", "married_or_cp", "2010-04-17"), rel("Xena", "Zack", "as_if_married", "2024-10-03")],
     "judgement": [SEP_NOT_PERMANENT]},
    {"id": "H025", "tax_year": "2026-27", "subject": "Bea", "people": ["Ali", "Bea", "Cal", "Dee"],
     "ani": {"Ali": "65000", "Bea": "75555"},
     "cb": [cb("Ali", "Cal", "26.75", *S26), cb("Bea", "Dee", "17.75", *S26)],
     "rel": [rel("Ali", "Bea", "married_or_cp", "2011-09-10")], "judgement": []},
]

# out-of-scope probes (scope "out" in the question file): VE answers UNSUPPORTED, reported apart
PROBES = ("H026", "H027", "H028", "H029", "H030", "H031", "H032", "H033")
