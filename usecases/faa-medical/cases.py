"""14 CFR 61.23: the ENCODER's file. Facts of the 45 cases, read from questions-enc.jsonl ONLY (sha256 081edf17...1173: id,
facts, date, operation; never questions.jsonl, answers or the writer's "covers"/"scope"). SAME-FAMILY (Opus 5.5 encoder =
translation author). The translation (rows.py) was committed (ed835b6e5c) before this file was opened.

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

BRIDGES_SHA256 = "35e9252987ef53272e40e71fedd2728493495646765df0581e7f222dd11aa451"

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
    C("F001", "2027-06-10", ["atp", "acting_pic", "part121", "required_crew"], birth="1986-06-15",
      certs={"cert1": ("2026-06-14", 1, False)}, apps={"app1": ISSUED}),
    C("F002", "2027-04-01", ["atp", "serving_sic", "part121", "flag_supp_3plus", "required_crew"], birth="1986-09-22",
      certs={"cert1": ("2026-09-22", 1, False)}, apps={"app1": ISSUED}),
    C("F003", "2026-08-15", ["atp", "serving_sic", "required_crew", "part121"], birth="1966-03-20",
      certs={"cert1": ("2026-02-05", 1, False)}, apps={"app1": ISSUED}),
    C("F004", "2026-06-20", ["atp", "serving_sic", "required_crew", "part121"], birth="1966-07-03",
      certs={"cert1": ("2026-01-10", 2, False)}, apps={"app1": ISSUED}),
    C("F005", "2026-12-05", ["commercial", "acting_pic", "comp_hire"], birth="1975-08-01",
      certs={"cert1": ("2026-03-12", 1, False)}, apps={"app1": ISSUED}),
    C("F006", "2026-10-01", ["commercial", "balloon_rating", "in_balloon", "acting_pic", "comp_hire"], birth="1980-10-10",
      certs={"cert1": ("2025-09-07", 2, False)}, apps={"app1": ISSUED}),
    C("F007", "2026-04-10", ["commercial", "balloon_rating", "in_balloon", "acting_pic", "training_61_133",
                             "conducting_training", "comp_hire"], birth="1979-04-18",
      certs={"cert1": ("2023-03-03", 2, False)}, apps={"app1": ISSUED},
      judgement=["exercises the commercial pilot certificate only (the flight instructor certificate held is not stated "
                 "as exercised)"]),
    C("F008", "2026-10-31", ["private", "acting_pic", "holds_dl"], birth="1971-03-14",
      certs={"cert1": ("2024-10-09", 3, False)}, apps={"app1": ISSUED}),
    C("F009", "2027-02-02", ["student", "acting_pic"], birth="2004-02-02",
      certs={"cert1": ("2025-01-20", 1, False)}, apps={"app1": ISSUED}),
    C("F010", "2027-02-28", ["flight_instructor", "acting_pic", "conducting_training"], birth="1970-05-05",
      certs={"cert1": ("2025-02-17", 1, False)}, apps={"app1": ISSUED}),
    C("F011", "2028-01-15", ["taking_test_aircraft", "acting_pic"], birth="1985-12-09",
      certs={"cert1": ("2025-12-08", 2, False)}, apps={"app1": ISSUED},
      judgement=["the test taker is not stated to exercise student pilot privileges: student not set (no (d) row then)",
                 "an applicant flying the practical test acts as pilot in command"]),
    C("F012", "2025-11-12", ["examiner_aircraft", "examiner_admin", "holds_dl", "dl_complied"], birth="1970-03-02"),
    C("F013", "2025-05-20", ["student", "seeking_sport_gb", "seeking_sport", "in_balloon", "acting_pic"], birth="1998-06-30"),
    C("F014", "2026-08-08", ["taking_test_gbsf", "taking_test_aircraft", "seeking_gb_rating", "in_glider", "acting_pic"],
      birth="1990-11-11", certs={"cert1": ("2015-04-04", 3, False)}, apps={"app1": ISSUED},
      judgement=["a glider is an aircraft: the practical test is also one 'in an aircraft' ((a)(3)(iii))",
                 "the test taker is not stated to exercise student pilot privileges: student not set"]),
    C("F015", "2026-06-14", ["flight_instructor", "fi_sport_rating", "in_glider", "acting_pic", "conducting_training"],
      birth="1988-07-07"),
    C("F016", "2026-09-03", ["commercial", "flight_instructor", "glider_rating", "fi_glider_rating", "in_glider",
                             "acting_pic", "comp_hire", "conducting_training"], birth="1984-01-25",
      judgement=["the operation names both certificates as exercised: commercial and flight_instructor both set"]),
    C("F017", "2025-09-21", ["private", "balloon_rating", "in_balloon", "acting_pic", "examiner_gbsf", "examiner_aircraft",
                             "examiner_admin"], birth="1962-02-19",
      certs={"cert1": ("2016-05-12", 3, False)}, apps={"app1": ISSUED},
      judgement=["a balloon is an aircraft: the Examiner also performs duties 'in an aircraft' ((a)(3)(iv))"]),
    C("F018", "2025-03-03", ["flight_instructor", "conducting_training"], birth="1977-08-13",
      certs={"cert1": ("2017-06-06", 3, False)}, apps={"app1": ISSUED}),
    C("F019", "2026-01-09", ["ground_instructor"], birth="1958-12-01"),
    C("F020", "2025-07-04", ["military_evidence", "domestic_us", "private", "acting_pic"], birth="1992-04-16"),
    C("F021", "2026-04-15", ["private", "acting_pic", "special_med_test"], birth="1964-10-08",
      certs={"cert1": ("2019-03-14", 3, False)},
      apps={"app1": dict(ISSUED, date="2019-03-14"), "app2": {"eligible": None, "denied": False, "date": "2026-03-01"}}),
    C("F022", "2027-04-30", ["student", "seeking_sport", "meets_316", "acting_pic"], birth="1985-04-11",
      certs={"cert1": ("2025-04-11", 2, False)}, apps={"app1": ISSUED}),
    C("F023", "2026-05-17", ["sport", "meets_316", "acting_pic", "holds_dl", "dl_complied", "knows_condition"],
      birth="1972-05-29"),
    C("F024", "2026-09-12", ["sport", "night", "under_113i", "meets_316", "acting_pic", "dl_complied"] + DL113,
      birth="1975-06-06", certs={"cert1": ("2017-05-02", 3, False)},
      apps={"app1": dict(ISSUED, date="2017-05-02"), "app2": {"eligible": False, "denied": True, "date": "2026-01-15"}},
      course="2026-05-04", bexam="2025-06-02",
      judgement=["a completed and denied application: not found eligible on it ((c)(2)(ii))"]),
    C("F025", "2026-02-14", ["sport", "night", "under_113i", "in_glider", "acting_pic", "dl_complied",
                             "last_si_withdrawn"] + DL113,
      birth="1958-09-09", certs={"cert1": ("2021-08-06", 3, False)}, apps={"app1": ISSUED},
      course="2025-10-20", bexam="2025-09-15"),
    C("F026", "2029-05-05", ["flight_instructor", "fi_sport_rating", "acting_pic", "meets_316", "conducting_training"],
      birth="1987-01-27", certs={"cert1": ("2027-01-26", 3, False)}, apps={"app1": ISSUED},
      judgement=["instruction under the flight instructor certificate only: sport not set"]),
    C("F027", "2025-10-10", ["examiner_sport_test", "examiner_admin", "meets_316", "holds_dl", "dl_complied"],
      birth="1966-03-03"),
    C("F028", "2027-03-10", ["sport", "night", "under_113i", "in_balloon", "acting_pic", "dl_complied"] + DL113,
      birth="1960-06-03", certs={"cert1": ("2024-02-02", 3, False)}, apps={"app1": ISSUED},
      course="2026-05-04", bexam="2025-06-02"),
    C("F029", "2026-04-18", ["sport", "night", "under_113i", "meets_316", "acting_pic", "holds_dl", "course_done",
                             "basic_exam_done"],
      birth="1968-11-21", certs={"cert1": ("2019-05-13", 3, False)}, apps={"app1": ISSUED},
      course="2026-01-02", bexam="2025-12-09",
      judgement=["a corrective-lens restriction not complied with: dl_complied and dl_med_complied both false"]),
    C("F030", "2026-06-06", ["private", "under_113i", "acting_pic"] + DL113, birth="1980-12-12",
      course="2026-02-01", bexam="2025-11-11"),
    C("F031", "2027-03-15", ["private", "under_113i", "acting_pic"] + DL113, birth="1960-07-17",
      certs={"cert1": ("2018-06-05", 3, False)}, apps={"app1": ISSUED}, course="2025-02-28", bexam="2025-01-10"),
    C("F032", "2026-10-05", ["flight_instructor", "acting_pic", "under_113i", "conducting_training"] + DL113,
      birth="1955-04-04", certs={"cert1": ("2016-08-22", 3, False)}, apps={"app1": ISSUED},
      course="2026-01-12", bexam="2022-09-30"),
    C("F033", "2026-09-01", ["private", "under_113i", "acting_pic", "diagnosed_impact"] + DL113, birth="1962-10-30",
      certs={"cert1": ("2018-03-19", 3, False)}, apps={"app1": ISSUED}, course="2026-07-01", bexam="2025-08-15"),
    C("F034", "2026-07-07", ["examiner_admin", "examiner_aircraft", "acting_pic", "under_113i"] + DL113,
      birth="1963-02-14", certs={"cert1": ("2020-03-10", 2, True)}, apps={"app1": ISSUED},
      course="2026-04-02", bexam="2026-04-07",
      judgement=["revoked: suspended_or_revoked true"]),
    C("F035", "2026-12-20", ["private", "under_113i", "acting_pic", "diagnosed_impact", "physician_care"] + DL113,
      birth="1965-08-08", certs={"cert1": ("2019-11-14", 3, False)},
      apps={"app1": dict(ISSUED, date="2019-11-14"), "app2": {"eligible": None, "denied": False, "date": "2026-03-03"}},
      course="2024-12-01", bexam="2025-01-20",
      judgement=["a pending application: not completed and denied; whether found eligible is unknown"]),
    # F038, F039: encodable with the status the facts leave to be decided as UNKNOWN (C2); VE must refuse
    C("F038", "2026-06-10", ["private", "acting_pic", "holds_dl", "course_done", "basic_exam_done"], birth="1966-05-05",
      certs={"cert1": ("2016-06-03", 3, False)}, apps={"app1": ISSUED}, course="2026-03-01", bexam="2026-04-01",
      unknown=["under_113i", "dl_med_complied"],
      judgement=["comprehensive examination 'by a State-licensed physician under part 68' not stated: basic_exam_done set "
                 "as stated ('a comprehensive medical examination'); 113i and license compliance unknown"]),
    C("F039", "2026-03-21", ["sport", "holds_dl"], birth="1990-09-12", unknown=["meets_316", "dl_complied"]),
]

# Cases the vocabulary cannot state (UNSUPPORTED; the encoder's reason)
PROBES = {
    "F036": "foreign pilot licence and foreign medical certificate only: no U.S. certificate is exercised (no fact for it)",
    "F037": "a foreign medical certificate: whether it is a 'medical certificate' of 61.23 has no fact in the vocabulary",
    "F040": "remote pilot certificate: an operation the vocabulary has no fact for",
    "F041": "parachute rigger certificate: an operation the vocabulary has no fact for",
    "F042": "aircraft dispatcher certificate: an operation the vocabulary has no fact for",
    "F043": "the special issuance authorization's own time limit and the issuing decision: not in the vocabulary",
    "F044": "a flight leaving U.S. airspace on the driver's license route: no fact for the airspace of that route",
    "F045": "Canadian medical rules: not in the vocabulary",
}

MUTANT_TARGETS = {"M1": ["F002"], "M2": ["F008"], "M3": ["F025"], "M4": ["F008"], "M5": ["F031"], "M6": ["F004"]}
