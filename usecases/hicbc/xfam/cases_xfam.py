"""HICBC: TEMPLATE for the cross-family encoder: the build's record format, helpers and conventions, records removed.

What is transcribed (and nothing else): each person's stated adjusted net income; each stated child benefit entitlement
(claimant, child, weekly amount, the weeks as stated, its stated basis: "a" = s.143(1)(a) because the child lives with the
claimant, "b" = s.143(1)(b) contributing, "145a" = by virtue of s.145A; any s.13A election and its weeks); each stated
"has the child living with them for the purposes of s.143(1)(a)" period; each stated relationship fact with its dates
(married_or_cp, sep_court, sep_permanent [stated judgement], as_if_married [stated judgement]). Facts stated as never
holding are simply absent (closed facts). Every child named is stated to be a child or a qualifying young person within
s.142 SSCBA 1992 (is_child true). Week and day arithmetic is the bridge's (bridge/bridges.py), never done here.
ENCODER JUDGEMENT (beyond the stated facts and the bridge) is listed per case in "judgement".
Record: {"id", "tax_year", "subject", "people", "ani": {person: "pounds"}, "cb": [cb(...)], "lives": [lw(...)] (optional),
"rel": [rel(...)], "judgement": [...]} (optional "unstated_dates_ok": [dates the bridge's quote check may skip, each
with its reason in "judgement"]).
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


CASES = [
    {"id": "H001", "tax_year": "2025-26", "subject": "Anna", "people": ["Anna", "Ivy"],
     "ani": {"Anna": "59999", "Ivy": "0"},
     "cb": [cb("Anna", "Ivy", "25.65", "2025-04-07", "2025-04-07")],
     "lives": [lw("Anna", "Ivy", "2025-04-07", "2025-04-07")],
     "rel": [], "judgement": []},
    {"id": "H002", "tax_year": "2025-26", "subject": "Beth", "people": ["Beth", "Ivy"],
     "ani": {"Beth": "60000", "Ivy": "0"},
     "cb": [cb("Beth", "Ivy", "25.65", *S)],
     "lives": [lw("Beth", "Ivy", *S)],
     "rel": [], "judgement": []},
    {"id": "H003", "tax_year": "2025-26", "subject": "Cara", "people": ["Cara", "Ivy"],
     "ani": {"Cara": "60001", "Ivy": "0"},
     "cb": [cb("Cara", "Ivy", "25.65", *S)],
     "lives": [lw("Cara", "Ivy", *S)],
     "rel": [], "judgement": []},
    {"id": "H004", "tax_year": "2025-26", "subject": "Dana", "people": ["Dana", "Ivy"],
     "ani": {"Dana": "64350", "Ivy": "0"},
     "cb": [cb("Dana", "Ivy", "25.65", *S)],
     "lives": [lw("Dana", "Ivy", *S)],
     "rel": [], "judgement": []},
    {"id": "H005", "tax_year": "2025-26", "subject": "Ella", "people": ["Ella", "Ivy"],
     "ani": {"Ella": "79999", "Ivy": "0"},
     "cb": [cb("Ella", "Ivy", "25.65", *S)],
     "lives": [lw("Ella", "Ivy", *S)],
     "rel": [], "judgement": []},
    {"id": "H006", "tax_year": "2025-26", "subject": "Faye", "people": ["Faye", "Ivy"],
     "ani": {"Faye": "80000", "Ivy": "0"},
     "cb": [cb("Faye", "Ivy", "25.65", *S)],
     "lives": [lw("Faye", "Ivy", *S)],
     "rel": [], "judgement": []},
    {"id": "H007", "tax_year": "2026-27", "subject": "Gina", "people": ["Gina", "Ivy"],
     "ani": {"Gina": "80001", "Ivy": "0"},
     "cb": [cb("Gina", "Ivy", "25.65", *S26)],
     "lives": [lw("Gina", "Ivy", *S26)],
     "rel": [], "judgement": []},
    {"id": "H008", "tax_year": "2025-26", "subject": "Ivan", "people": ["Hana", "Ivan", "Ivy"],
     "ani": {"Hana": "30000", "Ivan": "70000", "Ivy": "0"},
     "cb": [cb("Hana", "Ivy", "26.05", *S)],
     "lives": [lw("Hana", "Ivy", *S)],
     "rel": [rel("Hana", "Ivan", "married_or_cp", "2018-05-12")], "judgement": []},
    {"id": "H009", "tax_year": "2025-26", "subject": "Karl", "people": ["Julia", "Karl", "Ivy"],
     "ani": {"Julia": "72000", "Karl": "66000", "Ivy": "0"},
     "cb": [cb("Julia", "Ivy", "25", "2025-04-07", "2025-04-28")],
     "lives": [lw("Julia", "Ivy", "2025-04-07", "2025-04-28")],
     "rel": [rel("Julia", "Karl", "married_or_cp", "2018-05-12")], "judgement": []},
    {"id": "H010", "tax_year": "2025-26", "subject": "Lena", "people": ["Lena", "Mark", "Nina", "Owen"],
     "ani": {"Lena": "68000", "Mark": "68000", "Nina": "0", "Owen": "0"},
     "cb": [cb("Lena", "Nina", "20", "2025-04-07", "2025-04-14"), cb("Mark", "Owen", "30", "2025-04-07", "2025-04-14")],
     "lives": [lw("Lena", "Nina", "2025-04-07", "2025-04-14"), lw("Mark", "Owen", "2025-04-07", "2025-04-14")],
     "rel": [rel("Lena", "Mark", "married_or_cp", "2018-05-12")], "judgement": []},
    {"id": "H011", "tax_year": "2025-26", "subject": "Quinn", "people": ["Paula", "Quinn", "Rose"],
     "ani": {"Paula": "68000", "Quinn": "68000", "Rose": "0"},
     "cb": [cb("Paula", "Rose", "25", "2025-04-07", "2025-04-07")],
     "lives": [lw("Paula", "Rose", "2025-04-07", "2025-04-07")],
     "rel": [rel("Paula", "Quinn", "married_or_cp", "2018-05-12")], "judgement": []},
    {"id": "H012", "tax_year": "2025-26", "subject": "Sara", "people": ["Sara", "Tony", "Ivy"],
     "ani": {"Sara": "66000", "Tony": "74000", "Ivy": "0"},
     "cb": [cb("Sara", "Ivy", "25.75", "2025-06-02", "2025-06-16")],
     "lives": [lw("Sara", "Ivy", "2025-06-02", "2025-06-16")],
     "rel": [rel("Sara", "Tony", "married_or_cp", "2025-06-04")], "judgement": []},
    {"id": "H013", "tax_year": "2025-26", "subject": "Victor", "people": ["Uma", "Victor", "Ivy"],
     "ani": {"Uma": "66000", "Victor": "74000", "Ivy": "0"},
     "cb": [cb("Uma", "Ivy", "25.75", "2025-06-09", "2025-06-23")],
     "lives": [lw("Uma", "Ivy", "2025-06-09", "2025-06-23")],
     "rel": [rel("Uma", "Victor", "married_or_cp", "2018-05-12"), rel("Uma", "Victor", "sep_court", "2025-06-18")],
     "judgement": []},
    {"id": "H014", "tax_year": "2025-26", "subject": "Willa", "people": ["Willa", "Xavier", "Ivy"],
     "ani": {"Willa": "64000", "Xavier": "78000", "Ivy": "0"},
     "cb": [cb("Willa", "Ivy", "30.40", "2025-07-21", "2025-08-04")],
     "lives": [lw("Willa", "Ivy", "2025-07-21", "2025-08-04")],
     "rel": [rel("Willa", "Xavier", "married_or_cp", "2018-05-12"), rel("Willa", "Xavier", "sep_permanent", "2025-08-03")],
     "judgement": []},
    {"id": "H015", "tax_year": "2025-26", "subject": "Zane", "people": ["Yara", "Zane", "Ivy"],
     "ani": {"Yara": "64000", "Zane": "76000", "Ivy": "0"},
     "cb": [cb("Yara", "Ivy", "30.40", "2025-05-26", "2025-06-09")],
     "lives": [lw("Yara", "Ivy", "2025-05-26", "2025-06-09")],
     "rel": [rel("Yara", "Zane", "as_if_married", "2025-01-01", "2025-06-04")],
     "judgement": ["'until they stopped living together on 4 June 2025': living together recorded through 4 June 2025 inclusive (the stated end date)"]},
    {"id": "H016", "tax_year": "2025-26", "subject": "Bea", "people": ["Alice", "Bea", "Ivy"],
     "ani": {"Alice": "64000", "Bea": "76000", "Ivy": "0"},
     "cb": [cb("Alice", "Ivy", "25.75", "2025-04-07", "2025-04-14")],
     "lives": [lw("Alice", "Ivy", "2025-04-07", "2025-04-14")],
     "rel": [rel("Alice", "Bea", "married_or_cp", "2020-01-01"), rel("Alice", "Bea", "sep_court", "2025-03-14")],
     "judgement": []},
    {"id": "H017", "tax_year": "2025-26", "subject": "David", "people": ["Clara", "David", "Ivy"],
     "ani": {"Clara": "30000", "David": "82000", "Ivy": "0"},
     "cb": [cb("Clara", "Ivy", "25.65", "2025-04-07", "2025-04-28", election="all")],
     "lives": [lw("Clara", "Ivy", "2025-04-07", "2025-04-28")],
     "rel": [rel("Clara", "David", "married_or_cp", "2018-05-12")], "judgement": []},
    {"id": "H018", "tax_year": "2025-26", "subject": "Edith", "people": ["Edith", "Ivy"],
     "ani": {"Edith": "66000", "Ivy": "0"},
     "cb": [cb("Edith", "Ivy", "25.65", "2025-04-07", "2025-04-28", election=["2025-04-14", "2025-04-21"])],
     "lives": [lw("Edith", "Ivy", "2025-04-07", "2025-04-28")],
     "rel": [], "judgement": []},
    {"id": "H019", "tax_year": "2025-26", "subject": "Flora", "people": ["Flora", "Ivy"],
     "ani": {"Flora": "70000", "Ivy": "0"},
     "cb": [cb("Flora", "Ivy", "25.65", "2025-04-07", "2025-04-07"),
            cb("Flora", "Ivy", "25.65", "2025-04-14", "2025-04-28", basis="145a")],
     "lives": [lw("Flora", "Ivy", "2025-04-07", "2025-04-07")],
     "rel": [],
     "judgement": ["the s.145A amounts after Ivy's death carry is_child true by the build's convention (every item); they are stated as s.145A entitlements"]},
    {"id": "H020", "tax_year": "2024-25", "subject": "Grace", "people": ["Grace", "Ivy"],
     "ani": {"Grace": "70000", "Ivy": "0"},
     "cb": [cb("Grace", "Ivy", "25.65", d, d) for d in ("2024-04-01", "2024-04-08", "2025-03-31", "2025-04-07")],
     "lives": [lw("Grace", "Ivy", d, d) for d in ("2024-04-01", "2024-04-08", "2025-03-31", "2025-04-07")],
     "rel": [], "judgement": []},
    {"id": "H021", "tax_year": "2025-26", "subject": "Jules", "people": ["Hugo", "Ines", "Jules", "Kira"],
     "ani": {"Hugo": "30000", "Ines": "70000", "Jules": "74000", "Kira": "0"},
     "cb": [cb("Hugo", "Kira", "30.25", "2025-06-02", "2025-06-09", basis="b")],
     "lives": [lw("Ines", "Kira", "2025-06-02", "2025-06-09"), lw("Jules", "Kira", "2025-06-02", "2025-06-09")],
     "rel": [], "judgement": []},
    {"id": "H022", "tax_year": "2025-26", "subject": "Nora", "people": ["Leo", "Mona", "Nora", "Owen"],
     "ani": {"Leo": "30000", "Mona": "62000", "Nora": "80000", "Owen": "0"},
     "cb": [cb("Leo", "Owen", "25", "2025-06-02", "2025-06-02", basis="b")],
     "lives": [lw("Nora", "Owen", "2025-06-02", "2025-06-02")],
     "rel": [rel("Leo", "Mona", "married_or_cp", "2018-05-12")], "judgement": []},
    {"id": "H023", "tax_year": "2025-26", "subject": "Ruth", "people": ["Paul", "Ruth", "Seth"],
     "ani": {"Paul": "30000", "Ruth": "80000", "Seth": "0"},
     "cb": [cb("Paul", "Seth", "30.25", *S, basis="b"),
            cb("Paul", "Seth", "30.25", "2025-03-31", "2025-03-31"),
            cb("Paul", "Seth", "30.25", "2026-04-06", "2026-04-06")],
     "lives": [lw("Ruth", "Seth", *S), lw("Paul", "Seth", "2025-03-31", "2025-03-31"),
               lw("Paul", "Seth", "2026-04-06", "2026-04-06")],
     "rel": [], "judgement": []},
    {"id": "H024", "tax_year": "2025-26", "subject": "Vera", "people": ["Tom", "Vera", "Will"],
     "ani": {"Tom": "30000", "Vera": "80000", "Will": "0"},
     "cb": [cb("Tom", "Will", "30.25", "2025-03-31", "2026-03-30", basis="b"),
            cb("Tom", "Will", "30.25", "2025-03-24", "2025-03-24"),
            cb("Tom", "Will", "30.25", "2026-04-06", "2026-04-06")],
     "lives": [lw("Vera", "Will", "2025-03-31", "2026-03-30"), lw("Tom", "Will", "2025-03-24", "2025-03-24"),
               lw("Tom", "Will", "2026-04-06", "2026-04-06")],
     "rel": [], "judgement": []},
    {"id": "H025", "tax_year": "2025-26", "subject": "Adam", "people": ["Tara", "Adam", "Ben", "Cleo"],
     "ani": {"Tara": "30000", "Adam": "72000", "Ben": "76000", "Cleo": "0"},
     "cb": [cb("Tara", "Cleo", "25.65", "2025-04-07", "2025-04-14")],
     "lives": [lw("Tara", "Cleo", "2025-04-07", "2025-04-14")],
     "rel": [rel("Tara", "Adam", "married_or_cp", "2018-05-12"), rel("Tara", "Ben", "as_if_married", "2025-01-01")],
     "judgement": []},
]

# out-of-scope probes (scope "out" in the question file): VE answers UNSUPPORTED, reported apart
PROBES = ("H026", "H027", "H028", "H029", "H030", "H031", "H032")  # the ids of every out-of-scope household (and any in-scope one the vocabulary cannot state)
