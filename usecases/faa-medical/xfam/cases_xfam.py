"""14 CFR 61.23: the ENCODER's file for the CROSS-FAMILY question set (questions-enc.jsonl in /work). TEMPLATE: the
helpers below are the frozen build's own (cases.py of the build, its case records removed). Fill CASES and PROBES.
(The build's conventions, as written in its cases.py:)

Dates: every date below is transcribed from the case's facts; bridge/bridges.py refuses any date the facts do not state and
computes every derived date (ages, 60th birthday, month ends, windows, which date is later): bridge/bridges.jsonl.

ENCODING CONVENTIONS (apply to every case; counted as encoder judgement in RESULT.md):
 C1 Domain closure: the case names every medical certificate and every application the facts state; quantifiers range
    over them. A certificate the person held was issued on an application found eligible (one application per stated
    certificate, unless the facts state more).
 C2 Closed facts: a status the facts do not state is false (e.g. 61.113(i) not mentioned -> not under 61.113(i)); a status
    the facts say "must be decided from these circumstances" is unknown.
 C3 Pilot in command of a part 121 operation, or second in command of one, serves as a required pilot flightcrew member.
 C4 A solo flight is flown as pilot in command.
 C5 An application's date, where two applications must be ordered, is the stated examination date of the certificate issued
    on it.
Per-case judgement beyond C1-C5 is in `judgement`.
"""

BRIDGES_SHA256 = None  # the operator fills it after running the bridge script on your dates

ALL_CERTS = ("cert1", "cert2", "cert3", "cert4")


def C(cid, flight_day, true, birth=None, certs=None, apps=None, course=None, bexam=None, unknown=(), judgement=()):
    certs = certs or {}
    apps = apps or {}
    dates = {"birth": birth, "flight_day": flight_day, "certs": {k: v[0] for k, v in certs.items()},
             "apps": {k: v["date"] for k, v in apps.items() if v.get("date")},
             "course_day": course, "basic_exam_day": bexam}
    return {"id": cid, "dates": dates, "true": list(true), "unknown": list(unknown),
            "certs": {k: {"class": v[1], "suspended": v[2]} for k, v in certs.items()},
            "apps": {k: {"eligible": v.get("eligible"), "denied": v.get("denied")} for k, v in apps.items()},
            "judgement": list(judgement)}


ISSUED = {"eligible": True, "denied": False}
DL113 = ["holds_dl", "dl_med_complied", "course_done", "basic_exam_done"]

CASES = [
    C("F001", "2025-03-12", ["student", "acting_pic", "in_glider", "seeking_sport_gb"]),
    C("F002", "2025-04-09", ["sport", "acting_pic", "in_balloon"]),
    C("F003", "2025-05-14", ["private", "flight_instructor", "acting_pic", "in_glider", "glider_rating", "fi_glider_rating",
                             "fi_sport_rating", "conducting_training"]),
    C("F004", "2025-06-18", ["private", "balloon_rating", "in_balloon", "acting_pic"]),
    C("F005", "2025-07-21", ["commercial", "balloon_rating", "in_balloon", "acting_pic", "training_61_133",
                             "conducting_training", "comp_hire"]),
    C("F006", "2025-08-11", ["flight_instructor", "conducting_training"]),
    C("F007", "2025-09-17", ["ground_instructor"]),
    C("F008", "2025-10-13", ["examiner_gbsf", "examiner_admin", "examiner_aircraft", "in_balloon"],
      judgement=["a balloon is an aircraft: examiner_aircraft is true alongside examiner_gbsf"]),
    C("F009", "2025-11-19", ["student", "acting_pic", "in_glider", "seeking_gb_rating", "taking_test_gbsf",
                             "taking_test_aircraft"],
      judgement=["a glider is an aircraft: taking_test_aircraft is true alongside taking_test_gbsf"]),
    C("F010", "2025-12-08", ["private", "acting_pic", "military_evidence", "domestic_us"]),
    C("F011", "2026-01-14", ["student", "acting_pic", "special_med_test"]),
    C("F012", "2025-01-05", ["atp", "acting_pic"], birth="1985-01-05",
      certs={"cert1": ("2024-12-20", 1, False)}, apps={"app1": ISSUED}),
    C("F013", "2026-07-02", ["atp", "serving_sic", "required_crew", "part121", "flag_supp_3plus"], birth="1966-07-02",
      certs={"cert1": ("2026-01-10", 1, False)}, apps={"app1": ISSUED}),
    C("F014", "2026-04-30", ["commercial", "acting_pic", "comp_hire", "military_evidence", "domestic_us"],
      birth="1975-09-09", certs={"cert1": ("2025-04-05", 1, False)}, apps={"app1": ISSUED}),
    C("F015", "2029-06-30", ["private", "acting_pic"], birth="1984-06-16",
      certs={"cert1": ("2024-06-15", 1, False)}, apps={"app1": ISSUED}),
    C("F016", "2026-07-01", ["flight_instructor", "private", "acting_pic", "conducting_training"], birth="1984-06-16",
      certs={"cert1": ("2024-06-17", 1, False)}, apps={"app1": ISSUED}),
    C("F017", "2026-07-01", ["atp", "serving_sic", "required_crew", "part121"], birth="1966-07-02",
      certs={"cert1": ("2026-05-05", 2, False)}, apps={"app1": ISSUED}),
    C("F018", "2025-01-01", ["recreational", "acting_pic"], birth="1980-12-16",
      certs={"cert1": ("2019-12-15", 2, False)}, apps={"app1": ISSUED}),
    C("F019", "2026-06-30", ["private", "acting_pic", "taking_test_aircraft"], birth="1984-06-16",
      certs={"cert1": ("2024-06-17", 2, False)}, apps={"app1": ISSUED}),
    C("F020", "2025-01-31", ["student", "acting_pic"], birth="1980-01-16",
      certs={"cert1": ("2020-01-15", 3, False)}, apps={"app1": ISSUED}),
    C("F021", "2026-07-01", ["private", "acting_pic", "examiner_aircraft", "examiner_admin"], birth="1984-06-16",
      certs={"cert1": ("2024-06-17", 3, False)}, apps={"app1": ISSUED}),
    C("F022", "2027-04-30", ["commercial", "balloon_rating", "in_balloon", "acting_pic", "comp_hire"], birth="1970-08-08",
      certs={"cert1": ("2026-04-12", 2, False)}, apps={"app1": ISSUED}),
    C("F023", "2026-08-10", ["student", "acting_pic", "seeking_sport", "meets_316", "holds_dl"],
      judgement=["\"rely on their U.S. driver's license\" read as holds_dl"]),
    C("F024", "2026-08-10", ["sport", "acting_pic", "meets_316", "holds_dl", "dl_complied"], birth="1970-01-12",
      certs={"cert1": ("2015-05-08", 3, False)},
      apps={"app1": {**ISSUED, "date": "2015-05-08"}, "app2": {"eligible": False, "denied": True, "date": "2026-06-02"}}),
    C("F025", "2026-08-10", ["sport", "flight_instructor", "fi_sport_rating", "acting_pic", "conducting_training",
                             "meets_316", "holds_dl", "dl_complied", "last_si_withdrawn"], birth="1970-01-12",
      certs={"cert1": ("2015-05-08", 3, True)}, apps={"app1": ISSUED}),
    C("F026", "2026-08-10", ["sport", "acting_pic", "examiner_sport_test", "examiner_admin", "meets_316", "holds_dl",
                             "dl_complied", "knows_condition"]),
    C("F027", "2027-05-20", ["private", "acting_pic", "under_113i", "dl_complied", "diagnosed_impact", "physician_care",
                             *DL113], birth="1970-01-12", course="2026-05-10", bexam="2025-06-12",
      certs={"cert1": ("2015-05-08", 3, False)},
      apps={"app1": {**ISSUED, "date": "2015-05-08"}, "app2": {"eligible": False, "denied": False, "date": "2027-04-01"}},
      judgement=["pending application app2: not found eligible and not denied"]),
    C("F028", "2027-07-20", ["sport", "flight_instructor", "fi_sport_rating", "acting_pic", "conducting_training",
                             "in_glider", "night", "under_113i", "meets_316", "dl_complied", *DL113],
      birth="1970-01-12", course="2026-05-10", bexam="2023-08-12",
      certs={"cert1": ("2015-05-08", 3, False)}, apps={"app1": ISSUED}),
    C("F029", "2027-05-20", ["flight_instructor", "acting_pic", "conducting_training", "under_113i", "holds_dl",
                             "dl_complied", "course_done", "basic_exam_done"], birth="1970-01-12",
      course="2026-05-10", bexam="2025-06-12", certs={"cert1": ("2015-05-08", 3, False)}, apps={"app1": ISSUED},
      judgement=["the failed medical restriction of the license sets dl_med_complied false; dl_complied (other "
                 "restrictions, judicial orders) true"]),
    C("F030", "2027-05-20", ["private", "acting_pic", "examiner_aircraft", "examiner_admin", "under_113i", "dl_complied",
                             *DL113], birth="1970-01-12", course="2026-05-10", bexam="2025-06-12"),
    C("F031", "2027-05-20", ["private", "acting_pic", "under_113i", "dl_complied", "diagnosed_impact", *DL113],
      birth="1970-01-12", course="2026-05-10", bexam="2025-06-12",
      certs={"cert1": ("2015-05-08", 3, False)}, apps={"app1": ISSUED}),
    C("F032", "2027-06-01", ["private", "acting_pic", "under_113i", "holds_dl", "dl_complied", "dl_med_complied",
                             "basic_exam_done"], birth="1970-01-12", course="2025-05-10", bexam="2025-06-12",
      certs={"cert1": ("2015-05-08", 3, False)}, apps={"app1": ISSUED}),
    C("F033", "2027-09-01", ["private", "acting_pic", "under_113i", "dl_complied", *DL113], birth="1970-01-12",
      course="2026-05-10", bexam="2023-08-12", certs={"cert1": ("2015-05-08", 3, False)}, apps={"app1": ISSUED}),
    C("F034", "2027-05-20", ["private", "acting_pic", "under_113i", "dl_complied", "last_si_withdrawn", *DL113],
      birth="1970-01-12", course="2026-05-10", bexam="2025-06-12",
      certs={"cert1": ("2015-05-08", 3, True)}, apps={"app1": ISSUED}),
    C("F035", "2027-05-20", ["private", "acting_pic", "under_113i", "dl_complied", *DL113], birth="1970-01-12",
      course="2026-05-10", bexam="2025-06-12", certs={"cert1": ("2015-05-08", 3, False)},
      apps={"app1": {**ISSUED, "date": "2015-05-08"}, "app2": {"eligible": False, "denied": True, "date": "2027-04-01"}},
      judgement=["app2 dated by its stated submission day (1 April 2027), not its denial day"]),
    C("F037", "2027-05-20", ["private", "acting_pic", "dl_complied", *DL113], birth="1970-01-12",
      course="2026-05-10", bexam="2025-06-12", certs={"cert1": ("2015-05-08", 3, False)}, apps={"app1": ISSUED},
      unknown=["under_113i"]),
    C("F038", "2027-05-20", ["sport", "acting_pic", "holds_dl", "dl_complied"], unknown=["meets_316"]),
    C("F040", "2027-05-20", ["private", "acting_pic"], birth="1970-01-12", apps={"app1": {"eligible": False, "denied": False}},
      judgement=["pending application app1: not found eligible and not denied; the part 67 findings premise is not "
                 "encoded"]),
    C("F042", "2027-05-20", ["private", "acting_pic", "under_113i", "dl_complied", *DL113], birth="1970-01-12",
      course="2026-05-10", bexam="2025-06-12", certs={"cert1": ("2015-05-08", 3, False)}, apps={"app1": ISSUED},
      judgement=["flight outside U.S. airspace: domestic_us false; no other fact for it"]),
]

# Ids the vocabulary cannot state (UNSUPPORTED; the encoder's reason)
PROBES = {
    "F036": "foreign pilot licence and foreign medical certificate: no fact name for foreign credentials",
    "F039": "remote pilot certificate / unmanned aircraft: no fact name",
    "F041": "the special issuance authorization's own time limit: no fact name or date slot",
    "F043": "another country's medical rules: no fact name",
}
